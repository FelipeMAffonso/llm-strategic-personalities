"""A6: fixed opponents separate preferences, beliefs, risk attitude and rules.

In the four prisoner's dilemma variants every model played the same fixed opponents. Three of them identify
what a choice can mean. Against always-cooperate the own-payoff best response is to defect every round, so
any cooperation there is other-regarding preference or a rule that ignores the opponent. Against
always-defect the best response is again to defect every round, so cooperation there is an unconditional
rule or a misreading of the game. Against tit-for-tat (and grim trigger) with a known last round, the best
response is to cooperate in rounds 1 to 9 and defect in round 10, so the trial-level cooperation rate of a
forward-looking own-payoff maximizer is 0.90; a rate above 0.90 is preference-driven final-round
cooperation, and a rate well below 0.90 is a failure to best-respond (or a rule).

Outside the prisoner's dilemma: the dictator share (preference with no strategic uncertainty), the trust
game send and return (trust and positive reciprocity), the stag choice in the risky stag hunt (payoff
dominance against risk dominance), the chicken risk-taking rate, and the beauty-contest depth (belief
depth). Writes summary_data/A6_mechanism.csv and summary_data/A6_summary.json.

    python analysis/mechanism_profiles.py
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from common import DEVELOPER_ORDER, MODELS, ORDER, OUT, PD, load_profiles

BEST_RESPONSE_TFT = 0.90


def rate(d, col):
    return d.groupby("model_key")[col].mean().reindex(ORDER)


def same_opponent_rate(df, game, col):
    """Strategy-play trials of one game against the fixed opponents every model faced, weighted equally per opponent.
    Every mechanism measure uses this one sampling basis so the components are comparable."""
    d = df[(df.game_id == game) & (df.matchup_type == "model_vs_strategy") & df[col].notna()]
    common = set.intersection(*[set(g.opponent) for _, g in d.groupby("model_key")]) if len(d) else set()
    d = d[d.opponent.isin(common)]
    return d.groupby(["model_key", "opponent"])[col].mean().groupby("model_key").mean().reindex(ORDER), len(common)


def main():
    df = load_profiles()
    pdd = df[df.game_id.isin(PD) & (df.matchup_type == "model_vs_strategy")]
    c_ac = rate(pdd[pdd.opponent == "always_cooperate"], "cooperation_rate")
    c_ad = rate(pdd[pdd.opponent == "always_defect"], "cooperation_rate")
    c_tft = rate(pdd[pdd.opponent == "tit_for_tat"], "cooperation_rate")
    c_grim = rate(pdd[pdd.opponent == "grim_trigger"], "cooperation_rate")
    dictator, n_dict = same_opponent_rate(df, "dictator", "offer_ratio")
    trust_send, n_trust = same_opponent_rate(df, "trust_berg", "trust_index")
    stag_risky, n_stag = same_opponent_rate(df, "stag_hunt_risky", "preferred_option_rate")
    stag_std, _ = same_opponent_rate(df, "stag_hunt_standard", "preferred_option_rate")
    chicken, n_chk = same_opponent_rate(df, "chicken", "risk_taking_rate")
    depth, n_bc = same_opponent_rate(df, "beauty_contest_23", "strategic_depth")
    out = pd.DataFrame({
        "display": [MODELS[k][0] for k in ORDER], "developer": [MODELS[k][1] for k in ORDER],
        "coop_vs_always_cooperate": c_ac, "coop_vs_always_defect": c_ad, "coop_vs_tit_for_tat": c_tft, "coop_vs_grim_trigger": c_grim,
        "best_response_gap_tft": c_tft - BEST_RESPONSE_TFT,
        "dictator_share": dictator, "trust_sent_share": trust_send,
        "stag_share_risky": stag_risky, "stag_share_standard": stag_std, "chicken_risky_share": chicken, "beauty_depth": depth,
    }, index=ORDER)
    sampling = {"dictator": n_dict, "trust_berg": n_trust, "stag_hunt_risky": n_stag, "chicken": n_chk, "beauty_contest_23": n_bc}
    # components
    out["preference_component"] = out[["coop_vs_always_cooperate", "dictator_share"]].mean(axis=1)
    out["rule_component"] = out["coop_vs_always_defect"]
    out["belief_component"] = out[["coop_vs_tit_for_tat", "beauty_depth"]].mean(axis=1)
    out["risk_component"] = out[["stag_share_risky", "chicken_risky_share"]].mean(axis=1)
    out = out.round(4)
    out.to_csv(os.path.join(OUT, "A6_mechanism.csv"))
    dev = pd.Series({k: MODELS[k][1] for k in ORDER})
    summary = {"best_response_rate_vs_tft": BEST_RESPONSE_TFT, "sampling_basis": "strategy-play against the fixed opponents every model faced, equal weight per opponent", "common_opponents_per_game": sampling, "developer_means": {}, "developer_tests": {}}
    for comp in ["preference_component", "rule_component", "belief_component", "risk_component", "coop_vs_always_cooperate", "coop_vs_always_defect", "coop_vs_tit_for_tat"]:
        dm = out[comp].groupby(dev).mean().reindex(DEVELOPER_ORDER).round(3)
        summary["developer_means"][comp] = {k: (None if np.isnan(v) else float(v)) for k, v in dm.items()}
        groups = [out.loc[dev == d, comp].dropna() for d in ["Anthropic", "OpenAI", "Google"]]
        kw = stats.kruskal(*groups)
        # share of between-model variance explained by developer (eta squared from one-way ANOVA on the three developers with 6+ models)
        sub = out.loc[dev.isin(["Anthropic", "OpenAI", "Google"]), comp].dropna()
        gm = sub.mean()
        ssb = sum(len(g) * (g.mean() - gm) ** 2 for g in groups)
        sst = ((sub - gm) ** 2).sum()
        summary["developer_tests"][comp] = {"kruskal_H": round(float(kw.statistic), 2), "p": round(float(kw.pvalue), 4), "eta_squared_between_developers": round(float(ssb / sst), 3) if sst > 0 else None}
    with open(os.path.join(OUT, "A6_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(out[["display", "coop_vs_always_cooperate", "coop_vs_always_defect", "coop_vs_tit_for_tat", "dictator_share", "stag_share_risky", "beauty_depth"]].to_string())
    print(json.dumps(summary["developer_tests"], indent=1))


if __name__ == "__main__":
    main()
