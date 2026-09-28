"""A2: what explains cooperation: developer, size tier, reasoning mode, release date, opponent and game.

Trial-level prisoner's dilemma cooperation on strategy-play trials against the 16 common fixed opponents (so every
model faces the same opponent mix). Three things are reported:

1. A linear probability model of the trial cooperation rate on developer, size tier, reasoning mode, release date
   (years since the earliest model, from summary_data/A7_release_dates.csv), opponent and game variant, with standard
   errors clustered by model; coefficients, P values, R squared.
2. A nested comparison: R squared with and without each factor, given the others, and the share of between-model
   variance in the model means explained by developer, size tier and reasoning (eta squared from one-way ANOVAs on
   the 25 model means, and a joint model), with a bootstrap over models for the ordering of the shares.
3. The same for the trust index, as a check that the pattern is not specific to the prisoner's dilemma.

Writes summary_data/A2_regression.csv, summary_data/A2_variance_shares.csv and summary_data/A2_summary.json.

    python analysis/variance_decomposition.py
"""
import json
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from common import MODELS, ORDER, OUT, PD, load_profiles, release_dates


def fit(d, y, factors):
    f = f"{y} ~ " + " + ".join(factors)
    m = smf.ols(f, data=d).fit(cov_type="cluster", cov_kwds={"groups": d["model_key"]})
    return m


def eta_sq(means, groups):
    gm = means.mean()
    sst = ((means - gm) ** 2).sum()
    ssb = sum(len(means[groups == g]) * (means[groups == g].mean() - gm) ** 2 for g in groups.unique())
    return float(ssb / sst) if sst > 0 else np.nan


def main():
    df = load_profiles()
    rel = release_dates()
    pdd = df[df.game_id.isin(PD) & (df.matchup_type == "model_vs_strategy")].copy()
    common = set.intersection(*[set(g.opponent) for _, g in pdd.groupby("model_key")])
    pdd = pdd[pdd.opponent.isin(common)].copy()
    pdd["reasoning"] = pdd["reasoning"].astype(int)
    has_rel = rel is not None and rel.notna().all()
    if has_rel:
        pdd["release_years"] = (pdd.model_key.map(rel) - rel.min()).dt.days / 365.25
    base = ["C(opponent)", "C(game_id)"]
    # OpenAI is the reference developer (eight models); single-model developers (Meta, Mistral, Alibaba) have a
    # coefficient identified by one model each, so the developer test the paper reports is the between-model
    # share below and the three-developer comparison, not those single-model coefficients.
    factors = {"developer": "C(developer, Treatment(reference='OpenAI'))", "size_tier": "C(size_tier, Treatment(reference='small'))", "reasoning": "reasoning"}
    if has_rel:
        factors["release_years"] = "release_years"
    full = fit(pdd, "cooperation_rate", base + list(factors.values()))
    rows = []
    for name, term in factors.items():
        without = fit(pdd, "cooperation_rate", base + [t for k, t in factors.items() if k != name])
        alone = fit(pdd, "cooperation_rate", base + [term])
        rows.append({"factor": name, "r2_full": round(full.rsquared, 4), "r2_without": round(without.rsquared, 4), "r2_drop": round(full.rsquared - without.rsquared, 4), "r2_alone_with_controls": round(alone.rsquared, 4)})
    r2 = pd.DataFrame(rows)
    # coefficient table for developer (reference OpenAI) etc.
    coefs = pd.DataFrame({"coef": full.params, "se": full.bse, "p": full.pvalues}).round(4)
    coefs.to_csv(os.path.join(OUT, "A2_regression.csv"))
    # between-model shares on the 25 model means
    means = pdd.groupby("model_key").cooperation_rate.mean().reindex(ORDER)
    dev = pd.Series({k: MODELS[k][1] for k in ORDER})
    size = pd.Series({k: MODELS[k][3] for k in ORDER})
    reas = pd.Series({k: int(MODELS[k][4]) for k in ORDER})
    shares = {"developer": eta_sq(means, dev), "size_tier": eta_sq(means, size), "reasoning": eta_sq(means, reas.astype(str))}
    mm = pd.DataFrame({"y": means, "developer": dev, "size_tier": size, "reasoning": reas})
    if has_rel:
        mm["release_years"] = (rel.reindex(ORDER) - rel.min()).dt.days / 365.25
        shares["release_years"] = float(smf.ols("y ~ release_years", data=mm).fit().rsquared)
    joint = smf.ols("y ~ C(developer) + C(size_tier) + reasoning" + (" + release_years" if has_rel else ""), data=mm).fit()
    shares["joint_r2"] = float(joint.rsquared)
    # uncertainty on the ordering: resample the 25 models with replacement and recompute the between-model
    # shares; report how often developer stays ahead of each other factor
    rng = np.random.default_rng(11)
    wins = {"size_tier": 0, "reasoning": 0, "release_years": 0}
    reps = 2000
    for _ in range(reps):
        idx = rng.choice(len(ORDER), size=len(ORDER), replace=True)
        mb = means.iloc[idx]
        db, sb, rb = dev.iloc[idx], size.iloc[idx], reas.iloc[idx].astype(str)
        d_share = eta_sq(mb, db)
        if d_share > eta_sq(mb, sb):
            wins["size_tier"] += 1
        if d_share > eta_sq(mb, rb):
            wins["reasoning"] += 1
        if has_rel:
            rel_b = mm["release_years"].iloc[idx]
            rr = float(smf.ols("y ~ x", data=pd.DataFrame({"y": mb.values, "x": rel_b.values})).fit().rsquared)
            if d_share > rr:
                wins["release_years"] += 1
    shares["bootstrap_developer_ahead_of"] = {k: round(v / reps, 3) for k, v in wins.items() if has_rel or k != "release_years"}
    # developer given the others
    others = smf.ols("y ~ C(size_tier) + reasoning" + (" + release_years" if has_rel else ""), data=mm).fit()
    shares["developer_given_others"] = float(joint.rsquared - others.rsquared)
    # trust index check
    tr = df[(df.game_id == "trust_berg") & df.trust_index.notna()]
    tmeans = tr.groupby("model_key").trust_index.mean().reindex(ORDER)
    tshares = {"developer": eta_sq(tmeans, dev), "size_tier": eta_sq(tmeans, size), "reasoning": eta_sq(tmeans, reas.astype(str))}
    tm = pd.DataFrame({"y": tmeans, "developer": dev, "size_tier": size, "reasoning": reas})
    if has_rel:
        tm["release_years"] = mm["release_years"]
        tshares["release_years"] = float(smf.ols("y ~ release_years", data=tm).fit().rsquared)
    tjoint = smf.ols("y ~ C(developer) + C(size_tier) + reasoning" + (" + release_years" if has_rel else ""), data=tm).fit()
    tshares["joint_r2"] = float(tjoint.rsquared)
    tshares["developer_given_others"] = float(tjoint.rsquared - smf.ols("y ~ C(size_tier) + reasoning" + (" + release_years" if has_rel else ""), data=tm).fit().rsquared)
    flat = lambda d: {k: round(v, 3) for k, v in d.items() if isinstance(v, float)}
    pd.DataFrame([{"outcome": "pd_cooperation", **flat(shares)}, {"outcome": "trust_index", **flat(tshares)}]).to_csv(os.path.join(OUT, "A2_variance_shares.csv"), index=False)
    dev_terms = {k: v for k, v in full.params.items() if "developer" in k}
    summary = {"n_trials": int(len(pdd)), "n_models": int(pdd.model_key.nunique()), "n_common_opponents": len(common), "release_dates_used": bool(has_rel),
               "trial_level": {"r2_full": round(full.rsquared, 4), "r2_drop_by_factor": {r["factor"]: r["r2_drop"] for r in rows},
                               "developer_coefficients_vs_reference": {k: round(float(v), 4) for k, v in dev_terms.items()},
                               "developer_p_values": {k: round(float(full.pvalues[k]), 6) for k in dev_terms},
                               "reference_developer": "OpenAI"},
               "between_model_shares_pd": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in shares.items()},
               "between_model_shares_trust": {k: round(v, 3) for k, v in tshares.items()}}
    with open(os.path.join(OUT, "A2_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=1))
    print(r2.to_string(index=False))


if __name__ == "__main__":
    main()
