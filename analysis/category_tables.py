"""A4: one number per category per model, with its interval, and the per-game measures behind it.

Writes summary_data/A4_category_index.csv (model by category: mean, 95 percent interval, number of trials),
summary_data/A4_category_summary.csv (per category: cross-model range, coefficient of variation, developer means,
Kruskal-Wallis test across the three developers with six or more models), summary_data/A4_competition_games.csv (the
four competition games separately), summary_data/A4_table1.csv (the source of Table 1) and summary_data/A4_summary.json.
Where a game has fixed opponents, only strategy-play trials against the opponents every model faced are used, so
every model is measured against the same opponents; games without fixed opponents use all trials.

    python analysis/category_tables.py
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from common import CATEGORIES, DEVELOPER_ORDER, GAME_MEASURES, MODELS, ORDER, OUT, PD, load_profiles


def tci(x):
    x = pd.Series(x).dropna()
    n = len(x)
    if n < 2:
        return (np.nan, np.nan, n)
    m = x.mean()
    h = stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)
    return (m - h, m + h, n)


def boot_ci(d, col, reps=2000, seed=7):
    """95 percent percentile bootstrap interval for the equal-weight-per-opponent mean: trials are resampled
    within each opponent (stratified), the per-opponent means are averaged with equal weight, repeated.
    This matches the estimand the point estimate uses."""
    rng = np.random.default_rng(seed)
    groups = [g[col].dropna().to_numpy() for _, g in d.groupby("opponent")]
    groups = [g for g in groups if len(g)]
    if not groups:
        return (np.nan, np.nan)
    if all(len(g) == 1 for g in groups):
        # one trial per opponent (the frontier protocol): resample opponents instead
        vals = np.array([g[0] for g in groups])
        if len(vals) < 2:
            return (np.nan, np.nan)
        means = [rng.choice(vals, size=len(vals), replace=True).mean() for _ in range(reps)]
    else:
        means = [np.mean([rng.choice(g, size=len(g), replace=True).mean() for g in groups]) for _ in range(reps)]
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def main():
    df = load_profiles()
    rows, summ = [], []
    for cat, label, games, col, definition, bench in CATEGORIES:
        gset = PD if cat == "cooperation" else games
        d = df[df.game_id.isin(gset) & df[col].notna()]
        # equal weighting across opponents within strategy-play when fixed opponents exist for all models
        strat = d[d.matchup_type == "model_vs_strategy"]
        common = set.intersection(*[set(g.opponent) for _, g in strat.groupby("model_key")]) if len(strat) else set()
        if common and all(k in set(strat.model_key) for k in MODELS):
            use = strat[strat.opponent.isin(common)]
            policy = f"strategy-play, {len(common)} common opponents, equal weight"
            per_model = use.groupby(["model_key", "opponent"])[col].mean().groupby("model_key").mean()
        else:
            use = d
            policy = "all trials"
            per_model = use.groupby("model_key")[col].mean()
        for k in ORDER:
            vals = use[use.model_key == k][col]
            n = int(vals.notna().sum())
            if policy.startswith("strategy-play"):
                lo, hi = boot_ci(use[use.model_key == k], col)
            else:
                lo, hi, _ = tci(vals)
                lo, hi = max(0.0, lo), min(1.0, hi)
            rows.append({"category": cat, "label": label, "model_key": k, "display": MODELS[k][0], "developer": MODELS[k][1],
                         "mean": round(float(per_model.get(k, np.nan)), 4), "ci_lo": round(lo, 4) if n else np.nan, "ci_hi": round(hi, 4) if n else np.nan,
                         "n_trials": int(n), "policy": policy})
        pm = per_model.reindex(ORDER)
        dev = pd.Series({k: MODELS[k][1] for k in ORDER})
        dm = pm.groupby(dev).mean().reindex(DEVELOPER_ORDER)
        summ.append({"category": cat, "label": label, "measure": col, "definition": definition, "benchmark": bench,
                     "games": ", ".join(games), "n_models": int(pm.notna().sum()), "min": round(float(pm.min()), 4), "max": round(float(pm.max()), 4),
                     "min_model": MODELS[pm.idxmin()][0], "max_model": MODELS[pm.idxmax()][0],
                     "cv": round(float(pm.std(ddof=1) / pm.mean()), 3), "fold": round(float(pm.max() / pm.min()), 1) if pm.min() > 0 else np.nan,
                     **{f"dev_{dd}": round(float(dm[dd]), 4) for dd in DEVELOPER_ORDER},
                     "kruskal_p": round(float(stats.kruskal(*[pm[dev == dd].dropna() for dd in ["Anthropic", "OpenAI", "Google"]]).pvalue), 4),
                     # the H statistic beside P (two degrees of freedom, three developers)
                     "kruskal_H": round(float(stats.kruskal(*[pm[dev == dd].dropna() for dd in ["Anthropic", "OpenAI", "Google"]]).statistic), 2),
                     "policy": policy})
    idx = pd.DataFrame(rows)
    idx.to_csv(os.path.join(OUT, "A4_category_index.csv"), index=False)
    S = pd.DataFrame(summ)
    S.to_csv(os.path.join(OUT, "A4_category_summary.csv"), index=False)
    S[["label", "games", "measure", "definition", "benchmark"]].to_csv(os.path.join(OUT, "A4_table1.csv"), index=False)
    # competition games separately
    comp = []
    for g, (name, col, defn) in GAME_MEASURES.items():
        d = df[(df.game_id == g) & df[col].notna()]
        pm = d.groupby("model_key")[col].mean().reindex(ORDER)
        comp.append({"game": name, "measure": col, "definition": defn, "min": round(float(pm.min()), 3), "max": round(float(pm.max()), 3),
                     "cv": round(float(pm.std(ddof=1) / pm.mean()), 3), **{MODELS[k][0]: round(float(pm[k]), 3) for k in ORDER}})
    pd.DataFrame(comp).to_csv(os.path.join(OUT, "A4_competition_games.csv"), index=False)
    print(S[["label", "measure", "min", "max", "cv", "fold", "kruskal_p", "policy"]].to_string(index=False))
    print("\ncompetition games:\n", pd.DataFrame(comp)[["game", "measure", "min", "max", "cv"]].to_string(index=False))
    with open(os.path.join(OUT, "A4_summary.json"), "w", encoding="utf-8") as f:
        json.dump({r["category"]: {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in r.items()} for r in summ}, f, indent=2, default=str)


if __name__ == "__main__":
    main()
