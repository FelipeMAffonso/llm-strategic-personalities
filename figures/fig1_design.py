"""Fig. 1: the design. Panel a, the three parts of the prompt, with excerpts from a recorded trial; panel b, the
eight categories with their number of games and measure; panel c, the matchup types and the two sampling designs.

Every number is computed from the data: the models and developers from analysis/common.py, the games and categories
from summary_data/A4_category_summary.csv, the trials, rounds and model decisions from
summary_data/behavioral_profiles.csv, and the prompt excerpts from a recorded trial in sample_data/.

    python figures/fig1_design.py
"""
import json
from pathlib import Path
import textwrap

import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle

import figlib
from figlib import plt
from common import CATEGORIES, DEVELOPER_ORDER, FRONTIER_MODELS, MODELS


DATA = Path(figlib.SUMMARY)
PROMPT_TRIAL = Path(figlib.ROOT) / "sample_data" / "pd_canonical_claude-haiku-4.5-thinking_vs_always_cooperate_baseline_t1_5a5de013047b.json"
MEASURES = {
    "coordination": "Matching-action\nshare",
    "depth": "One minus mean\nguess over 50",
    "competition": "Bid / maximum\nbid",
    "cooperation": "Cooperation\nshare",
    "trust": "Endowment\nsent share",
    "fairness": "Endowment\noffered share",
    "negotiation": "Surplus\ndemanded share",
    "risk": "Risky-action\nshare",
}


def read_sources():
    profiles = pd.read_csv(DATA / "behavioral_profiles.csv", low_memory=False)
    models = len(MODELS)
    developers = len({MODELS[key][1] for key in MODELS})
    if developers != len(DEVELOPER_ORDER):
        raise ValueError("Developer count differs from the developer order.")
    games = sum(len(entry[2]) for entry in CATEGORIES)
    categories = len(CATEGORIES)
    trials = f"{len(profiles):,}"
    rounds = f"{int(profiles.num_rounds.sum()):,}"
    # a round is one decision in strategy-play and two (one per seat) in self-play and cross-play
    seats = profiles.matchup_type.map({"model_vs_strategy": 1, "self_play": 2, "cross_play": 2})
    decisions = f"{int((profiles.num_rounds * seats).sum()):,}"
    frontier_models = len(FRONTIER_MODELS)
    standard_models = models - frontier_models
    pairs = standard_models * (standard_models - 1) // 2
    # trials per cell: the most common number of trials per model, game and fixed opponent in each design
    cells = (profiles[(profiles.matchup_type == "model_vs_strategy") & (profiles.condition == "baseline")]
             .groupby(["model_key", "game_id", "opponent"]).size().reset_index(name="n"))
    frontier_cells = cells.model_key.isin(FRONTIER_MODELS)
    standard_trials = int(cells.loc[~frontier_cells, "n"].mode().iloc[0])
    frontier_trials = int(cells.loc[frontier_cells, "n"].mode().iloc[0])
    trial = json.loads(PROMPT_TRIAL.read_text(encoding="utf-8"))
    # the first sentence of the rules block, as the game engine writes it (games/engine.py)
    rules = f"You will play {trial['num_rounds']} rounds in total with the same player"
    first_round = trial["match_detail"]["rounds"][0]
    reverse_map = {action: label for label, action in trial["label_map"].items()}
    own = reverse_map[first_round["parsed_choices"]["0"]]
    other = reverse_map[first_round["parsed_choices"]["1"]]
    history = (f"In round {first_round['round_num']}, you chose Option {own} and "
               f"the other player chose Option {other}.")
    labels = list(trial["label_map"])
    query = f"Which option do you choose, Option {labels[0]} or Option {labels[1]}?"
    summary = pd.read_csv(DATA / "A4_category_summary.csv").set_index("category").loc[list(MEASURES)]
    summary["game_count"] = summary.games.str.split(",").map(len)
    if summary.game_count.sum() != games or len(summary) != categories:
        raise ValueError("Category game counts do not match the game list.")
    scale = (models, developers, games, categories, trials, rounds, decisions)
    cohorts = (standard_models, standard_trials, pairs, frontier_models, frontier_trials)
    return summary, (rules, history, query), scale, cohorts


def build():
    figlib.style()
    summary, excerpts, scale, cohorts = read_sources()
    models, developers, games, categories, trials, rounds, decisions = scale
    standard_models, standard_trials, pairs, frontier_models, frontier_trials = cohorts
    fig = plt.figure(figsize=(7.2, 4.9))
    prompt = fig.add_axes([0.035, 0.23, 0.25, 0.65])
    table = fig.add_axes([0.323, 0.23, 0.365, 0.65])
    matchups = fig.add_axes([0.735, 0.23, 0.235, 0.65])
    for axis in [prompt, table, matchups]:
        axis.set_xlim(0, 1)
        axis.set_ylim(0, 1)
        axis.set_axis_off()
    for letter, left, heading in [("a", 0.035, "Prompt structure"), ("b", 0.323, "Categories and measures"),
                                  ("c", 0.735, "Matchup types")]:
        fig.text(left, 0.955, letter, fontsize=8, weight="bold")
        fig.text(left, 0.919, heading, fontsize=7)
    shade = figlib.PALETTE["benchmark"]
    for bottom, title, excerpt in zip([0.70, 0.36, 0.02], ["Rules", "History", "Query"], excerpts):
        prompt.add_patch(Rectangle((0, bottom), 1, 0.27, facecolor="#f5f3ee",
                                   edgecolor=figlib.PALETTE["separator"], linewidth=0.7))
        prompt.text(0.06, bottom + 0.225, title, fontsize=7, color=shade, va="top")
        wrapped = textwrap.fill(excerpt.replace("Option ", "Option_"), width=33).replace("Option_", "Option ")
        prompt.text(0.06, bottom + 0.159, wrapped, fontsize=7,
                    va="top", linespacing=1.35)
    for top, bottom in [(0.70, 0.63), (0.36, 0.29)]:
        prompt.add_patch(FancyArrowPatch((0.5, top - 0.008), (0.5, bottom + 0.008), arrowstyle="-|>",
                                         mutation_scale=7, color=shade, linewidth=0.7))
    table.text(0, 0.97, "Category", fontsize=7, va="top")
    table.text(0.49, 0.97, "Games", fontsize=7, ha="center", va="top")
    table.text(0.625, 0.97, "Measure", fontsize=7, va="top")
    table.plot([0, 1], [0.915, 0.915], color=shade, linewidth=0.6)
    for index, (category, row) in enumerate(summary.iterrows()):
        vertical = 0.855 - 0.105 * index
        table.text(0, vertical, row.label, fontsize=7, va="center")
        table.text(0.49, vertical, str(row.game_count), fontsize=7, ha="center", va="center")
        table.text(0.625, vertical, MEASURES[category], fontsize=7, va="center", linespacing=1.2)
        table.plot([0, 1], [vertical - 0.051, vertical - 0.051], color=figlib.PALETTE["separator"], linewidth=0.5)
    for vertical, title, description in [
        (0.96, "Fixed opponents", "Model vs. fixed strategy"),
        (0.79, "Self-play", "Model vs. itself"),
        (0.62, "Cross-play", "Model vs. another model"),
    ]:
        matchups.text(0, vertical, title, fontsize=7, va="top")
        matchups.text(0, vertical - 0.065, description, fontsize=7, va="top", color=shade)
        matchups.plot([0, 1], [vertical - 0.132, vertical - 0.132], color=figlib.PALETTE["separator"], linewidth=0.6)
    matchups.text(0, 0.425, "Sampling design", fontsize=7, color=shade, va="top")
    matchups.text(0, 0.345, f"{standard_models} models, {standard_trials} trials per cell", fontsize=7, va="top")
    matchups.text(0, 0.28, f"Full cross-play ({pairs} pairs)", fontsize=7, va="top")
    matchups.text(0, 0.18, f"{frontier_models} frontier models\n{frontier_trials} trial per cell", fontsize=7,
                  va="top", linespacing=1.35)
    matchups.text(0, 0.055, "Fixed opponents and self-play", fontsize=6, va="top", color=shade)
    fig.text(0.035, 0.166, "Recorded option letters; presentation order randomized", fontsize=6, color=shade)
    fig.text(0.5, 0.105, f"{models} models    |    {developers} developers    |    {games} games    |    {categories} categories",
             ha="center", fontsize=7)
    fig.text(0.5, 0.052, f"{trials} trials    |    {rounds} rounds    |    {decisions} model decisions",
             ha="center", fontsize=7)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "fig1_design")
