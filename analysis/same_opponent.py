"""A1: cooperation against the same opponents, weighted equally.

Restricts every model to the fixed-strategy opponents that all 25 models faced in the four prisoner's dilemma
variants, weights each opponent equally, and compares the result with the pooled rate over every matchup the model
played (with a 95 percent t-distribution interval on the trial-level pooled rates). Writes
summary_data/A1_same_opponent.csv, summary_data/A1_by_opponent.csv and summary_data/A1_summary.json.

    python analysis/same_opponent.py
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from common import OUT, PD, PROFILES


def main():
    df = pd.read_csv(PROFILES, low_memory=False)
    pdd = df[df.game_id.isin(PD)].copy()
    strat = pdd[pdd.matchup_type == "model_vs_strategy"]
    common = set.intersection(*[set(g.opponent) for _, g in strat.groupby("model_key")])
    strat = strat[strat.opponent.isin(common)]
    by_opp = strat.groupby(["model_key", "opponent"]).cooperation_rate.agg(["mean", "count"]).reset_index()
    same = by_opp.groupby("model_key")["mean"].mean().rename("same_opponent_rate")
    n_same = strat.groupby("model_key").size().rename("n_trials_same_opponent")
    pooled = pdd.groupby("model_key").cooperation_rate.mean().rename("pooled_rate")
    n_pooled = pdd.groupby("model_key").size().rename("n_trials_pooled")
    # 95 percent t-distribution interval on the trial-level pooled rates, clipped to the unit range (Supplementary
    # Table S2)
    def t_interval(x):
        x = x.dropna()
        if len(x) < 2:
            return pd.Series({"pooled_ci_lo": float("nan"), "pooled_ci_hi": float("nan")})
        half = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
        return pd.Series({"pooled_ci_lo": max(0.0, x.mean() - half), "pooled_ci_hi": min(1.0, x.mean() + half)})
    ci = pdd.groupby("model_key").cooperation_rate.apply(t_interval).unstack()
    out = pd.concat([same, n_same, pooled, n_pooled, ci], axis=1).sort_values("same_opponent_rate")
    cols = ["same_opponent_rate", "pooled_rate", "pooled_ci_lo", "pooled_ci_hi"]
    out[cols] = (out[cols] * 100).round(1)
    out.to_csv(os.path.join(OUT, "A1_same_opponent.csv"))
    piv = by_opp.pivot(index="model_key", columns="opponent", values="mean").mul(100).round(1)
    piv.to_csv(os.path.join(OUT, "A1_by_opponent.csv"))
    summary = {
        "n_common_opponents": len(common),
        "common_opponents": sorted(common),
        "fold_spread_same_opponent": round(float(out.same_opponent_rate.max() / out.same_opponent_rate.min()), 1),
        "fold_spread_pooled": round(float(out.pooled_rate.max() / out.pooled_rate.min()), 1),
        "min_model": out.same_opponent_rate.idxmin(), "min_rate": float(out.same_opponent_rate.min()),
        "max_model": out.same_opponent_rate.idxmax(), "max_rate": float(out.same_opponent_rate.max()),
        "spearman_same_vs_pooled": round(float(out[["same_opponent_rate", "pooled_rate"]].corr(method="spearman").iloc[0, 1]), 3),
    }
    with open(os.path.join(OUT, "A1_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print(out.to_string())


if __name__ == "__main__":
    main()
