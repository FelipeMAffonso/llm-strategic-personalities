"""A4: one number per category per model, with its interval, and the per-game measures behind it.

Writes summary_data/A4_category_index.csv (model by category: mean, 95 percent interval, number of trials),
summary_data/A4_category_summary.csv (per category: cross-model range, coefficient of variation, developer means,
Kruskal-Wallis test across the three developers with six or more models), summary_data/A4_competition_games.csv (the
three scored competition games separately, plus an empty Colonel Blotto row that supplementary_tables/build_tables.py
checks for and leaves out of Supplementary Table 4), summary_data/A4_table1.csv (the source of Table 1) and
summary_data/A4_summary.json. Where a game has fixed opponents, only strategy-play trials against the opponents every
model faced are used, so every model is measured against the same opponents; games without fixed opponents use all
trials.

How an index pools games: a model's index is the mean over the fixed opponents every model faced, each opponent
weighted equally, of the mean of all that model's trials against that opponent in the category's index games.
Trials are pooled across games within an opponent, so a game counts in proportion to its trials with that opponent,
and an opponent that appears in only some games brings only those games.

Colonel Blotto and multi-issue negotiation were played but are not scored: each answer needed several numbers and the
parser kept one, so their measures do not describe the models' play. They are removed from the trial-level data
before anything is computed, so they enter no index, range, coefficient of variation, developer mean, Kruskal-Wallis
test or interval. Table 1 still lists them, marked "not scored", and marks every other game played in a category but
outside its index "not in the index". The risk-taking index is the two chicken games only (see INDEX_GAMES).

    python analysis/category_tables.py
"""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

from common import CATEGORIES, DEVELOPER_ORDER, GAME_MEASURES, MODELS, ORDER, OUT, PD, load_profiles

UNSCORED = ("colonel_blotto", "multi_issue")

# Table 1 as written into A4_table1.csv: the games whose trials enter the index, the definition and the benchmark.
# The definitions name exactly those games; main() stops without writing the tables if the games that actually enter
# an index differ from the ones listed here.
TABLE1 = {
    "coordination": (
        ["bos_standard", "bos_transposed", "stag_hunt_standard", "stag_hunt_risky", "matching_pennies", "focal_point"],
        "Share of rounds in which the two players chose matching actions, pooled over the two battle-of-the-sexes "
        "games, the two stag hunts, matching pennies and the focal-point game",
        "A pure-strategy equilibrium requires matching; human pairs miscoordinate in a substantial share of rounds in "
        "battle-of-the-sexes experiments"),
    "depth": (
        ["beauty_contest_23", "beauty_contest_12", "eleven_twenty"],
        "One minus the mean number chosen divided by 50, pooled over the two beauty contests (a guess of 50 scores 0 "
        "and the equilibrium guess of 0 scores 1) and the 11 to 20 game (requests of 11 to 20 score 0.78 to 0.60)",
        "Nash equilibrium guess 0 in the beauty contests; first-round human guesses average about 37 in the "
        "two-thirds game"),
    "competition": (
        ["auction_first_price", "auction_vickrey", "auction_all_pay"],
        "Mean bid divided by the maximum allowed bid of 100, pooled over the first-price, Vickrey and all-pay auctions",
        "Risk-neutral bidders shade first-price bids below value; bidding true value is the dominant strategy in the "
        "Vickrey auction; in the all-pay auction for a prize of 50, equilibrium bids are spread evenly from 0 to 50"),
    "cooperation": (
        list(PD),
        "Share of rounds in which the model chose the cooperative action, pooled over the four prisoner's dilemma "
        "variants",
        "Stage-game equilibrium is mutual defection; one-shot human cooperation averages about 37 percent"),
    "trust": (
        ["trust_berg", "gift_exchange"],
        "Share of the largest possible transfer that the model sent as first mover, pooled over the Berg trust game "
        "(points sent out of 10) and gift exchange (wage offered out of 100)",
        "Subgame-perfect prediction is to send nothing and to offer a wage of 0; human senders in the trust game "
        "transfer about half"),
    "fairness": (
        ["ultimatum", "dictator", "third_party_punishment"],
        "Share of the 100-point endowment given to the other player, pooled over the ultimatum offer, the dictator "
        "gift and the allocator's transfer in third-party punishment",
        "Subgame-perfect offer is the smallest positive amount in the ultimatum game and 0 in the dictator and "
        "third-party punishment games; human ultimatum offers average 40 percent"),
    "negotiation": (
        ["nash_demand", "alternating_offers"],
        "Share of the 100-point surplus that the model demanded for itself, pooled over the Nash demand game and the "
        "proposer's demand in alternating offers",
        "In the Nash demand game any pair of demands summing to the surplus is an equilibrium, and the equal split is "
        "the focal outcome"),
    "risk": (
        ["chicken", "chicken_high_stakes"],
        "Share of rounds in which the model chose the risky action (going straight), pooled over standard and "
        "high-stakes chicken",
        "Mixed equilibrium of the standard chicken game is 2/13 straight"),
}


# Where the index uses fewer games than the category holds (common.CATEGORIES), for reasons other than a missing
# measure. Risk taking is the two chicken games only: the paper defines it as the share of chicken rounds going
# straight; in cheap talk the measure compares a numeric message with the label "action" and is 0 in every round, and
# the signaling share (sending no signal) is not a risk measure the paper defines.
INDEX_GAMES = {"cooperation": list(PD), "risk": ["chicken", "chicken_high_stakes"]}


def games_column(games, index_games):
    """Every game played in the category for Table 1, with the unscored games and the games outside the index marked."""
    def mark(g):
        if g in UNSCORED:
            return f"{g} (not scored)"
        return g if g in index_games else f"{g} (not in the index)"
    return ", ".join(mark(g) for g in games)


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
    df = df[~df.game_id.isin(UNSCORED)]
    rows, summ = [], []
    for cat, label, games, col, _definition, _bench in CATEGORIES:
        index_games, definition, bench = TABLE1[cat]
        gset = INDEX_GAMES.get(cat, games)
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
        # stop rather than write a Table 1 definition that names different games from the ones the index is computed on
        entered = set(use.game_id)
        if entered != set(index_games) or entered & set(UNSCORED):
            raise ValueError(f"{cat}: the index uses {sorted(entered)}, Table 1 names {sorted(index_games)}")
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
                     "games": games_column(games, index_games), "games_in_index": ", ".join(index_games), "n_models": int(pm.notna().sum()), "min": round(float(pm.min()), 4), "max": round(float(pm.max()), 4),
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
    # competition games separately. Colonel Blotto keeps an empty row, marked not scored, which
    # supplementary_tables/build_tables.py checks for before it leaves the row out of Supplementary Table 4.
    comp = []
    for g, (name, col, defn) in GAME_MEASURES.items():
        if g in UNSCORED:
            comp.append({"game": name, "measure": col, "definition": "not scored: the parser kept one of the several numbers each answer required",
                         "min": np.nan, "max": np.nan, "cv": np.nan, **{MODELS[k][0]: np.nan for k in ORDER}})
            continue
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
