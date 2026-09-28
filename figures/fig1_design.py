"""Fig. 1: the design. Panel a, the three parts of the prompt and the message each was sent in, with excerpts from a
recorded trial; panel b, the eight categories with their number of games and measure; panel c, the matchup types and
the two sampling designs.

Every number is computed from the data: the models and developers from analysis/common.py, the games and categories
from summary_data/A4_category_summary.csv, the trials, rounds and model replies from
summary_data/behavioral_profiles.csv, and the prompt excerpts from a recorded trial in sample_data/, assembled by the
game engine (games/engine.py) exactly as in data collection.

    python figures/fig1_design.py
"""
import json
from pathlib import Path
import re
import sys
import textwrap

import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle

import figlib
from figlib import plt
from common import CATEGORIES, DEVELOPER_ORDER, FRONTIER_MODELS, MODELS

sys.path.insert(0, figlib.ROOT)

DATA = Path(figlib.SUMMARY)
PROMPT_TRIAL = Path(figlib.ROOT) / "sample_data" / "pd_canonical_claude-haiku-4.5-thinking_vs_always_cooperate_baseline_t1_5a5de013047b.json"
# In the dictator and third-party punishment games the second seat is a recipient who never replies, so in self-play
# and cross-play those seats hold no model reply: 13,040 of the 826,990 model seats. The re-parsing check
# (analysis/reparse_check.py) counts the replies in every raw trial file and finds the same 813,950.
RECIPIENT_SEAT_GAMES = {"dictator", "third_party_punishment"}
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


def corpus_scale(profiles):
    """The scale strip. Trials are rows of behavioral_profiles.csv (one per raw trial file); rounds are the sum of
    num_rounds. A model seat is one round for each seat a model held (seat 0 always, seat 1 too in self-play and
    cross-play): 826,990. Model replies leave out the recipient seats of the dictator and third-party punishment games
    in self-play and cross-play, where no model replied: 826,990 - 13,040 = 813,950."""
    seats = profiles.matchup_type.map({"model_vs_strategy": 1, "self_play": 2, "cross_play": 2})
    if seats.isna().any():
        raise ValueError("Unknown matchup type in behavioral_profiles.csv.")
    slots = int((profiles.num_rounds * seats).sum())
    recipient = int(profiles.num_rounds[(seats == 2) & profiles.game_id.isin(RECIPIENT_SEAT_GAMES)].sum())
    games = profiles.game_id.nunique()
    if games != sum(len(entry[2]) for entry in CATEGORIES):
        raise ValueError("Games in the data do not match the category lists.")
    developers = len({MODELS[key][1] for key in MODELS})
    if developers != len(DEVELOPER_ORDER):
        raise ValueError("Developer count differs from the developer order.")
    return {"models": profiles.model_key.nunique(), "developers": developers, "games": games,
            "categories": len(CATEGORIES), "trials": len(profiles), "rounds": int(profiles.num_rounds.sum()),
            "replies": slots - recipient}


def prompt_excerpts():
    """Round 2 of the trial above, assembled by the game engine exactly as in data collection.

    GameEngine.build_prompt returns (system prompt, user message); single-message mode was never switched on, so the
    rules block went out as the system message and the history and query blocks as the user message. The excerpts
    are checked against the message they are drawn from, so the labels in panel a follow the code."""
    from games.engine import GameEngine, RoundResult
    from games.definitions import GAME_REGISTRY

    trial = json.loads(PROMPT_TRIAL.read_text(encoding="utf-8"))
    engine = GameEngine(GAME_REGISTRY[trial["game_id"]], num_rounds=trial["num_rounds"], label_seed=0)
    if engine.single_message:
        raise ValueError("The engine default changed: single-message mode is on.")
    # the stored labels replace the engine's own draw, so the excerpt shows the letters this trial used
    engine.label_map = dict(trial["label_map"])
    engine.abstract_options = list(engine.label_map)
    engine.reverse_map = {action: label for label, action in engine.label_map.items()}
    stored = trial["match_detail"]["rounds"][0]
    first_round = RoundResult(round_num=int(stored["round_num"]),
                              choices={int(seat): reply for seat, reply in stored["choices"].items()},
                              parsed_choices={int(seat): choice for seat, choice in stored["parsed_choices"].items()},
                              payoffs={int(seat): payoff for seat, payoff in stored["payoffs"].items()})
    system, user = engine.build_prompt(0, 2, [first_round], framing=trial["condition"])
    rules = re.search(r"You will play \d+ rounds in total with the same player", system).group(0)
    history = re.search(r"In round 1, you chose Option \w and the other player chose Option \w\.", user).group(0)
    query = re.search(r"Which option do you choose, Option \w or Option \w\?", user).group(0)
    if rules in user or history in system or query in system:
        raise ValueError("A prompt excerpt appears in both messages.")
    return rules, history, query


def read_sources():
    profiles = pd.read_csv(DATA / "behavioral_profiles.csv", low_memory=False)
    profiles = profiles.loc[profiles.model_key.isin(MODELS)]
    counts = corpus_scale(profiles)
    frontier_models = len(FRONTIER_MODELS)
    standard_models = len(MODELS) - frontier_models
    pairs = standard_models * (standard_models - 1) // 2
    # trials per cell (one model, one game, one fixed opponent) as the two designs ask for them
    # (data_collection/designs.py), checked against the most common count in the data
    from data_collection.designs import DESIGNS
    standard_trials = DESIGNS["complete"].strategy_trials
    frontier_trials = DESIGNS["frontier"].strategy_trials
    cells = (profiles[(profiles.matchup_type == "model_vs_strategy") & (profiles.condition == "baseline")]
             .groupby(["model_key", "game_id", "opponent"]).size().reset_index(name="n"))
    frontier_cells = cells.model_key.isin(FRONTIER_MODELS)
    if (int(cells.loc[~frontier_cells, "n"].mode().iloc[0]) != standard_trials
            or int(cells.loc[frontier_cells, "n"].mode().iloc[0]) != frontier_trials):
        raise ValueError("The most common number of trials per cell differs from the design.")
    summary = pd.read_csv(DATA / "A4_category_summary.csv").set_index("category").loc[list(MEASURES)]
    summary["game_count"] = summary.games.str.split(",").map(len)
    if summary.game_count.sum() != counts["games"] or len(summary) != counts["categories"]:
        raise ValueError("Category game counts do not match the data.")
    scale = tuple(f"{counts[key]:,}" for key in ["models", "developers", "games", "categories", "trials", "rounds", "replies"])
    cohorts = (standard_models, standard_trials, pairs, frontier_models, frontier_trials)
    return summary, prompt_excerpts(), scale, cohorts


def build():
    figlib.style()
    summary, excerpts, scale, cohorts = read_sources()
    models, developers, games, categories, trials, rounds, replies = scale
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
    width = 0.86  # the blocks leave room on the right for the two message brackets
    for bottom, title, excerpt in zip([0.70, 0.36, 0.02], ["Rules", "History", "Query"], excerpts):
        prompt.add_patch(Rectangle((0, bottom), width, 0.27, facecolor="#f5f3ee",
                                   edgecolor=figlib.PALETTE["separator"], linewidth=0.7))
        prompt.text(0.06, bottom + 0.225, title, fontsize=7, color=shade, va="top")
        wrapped = textwrap.fill(excerpt.replace("Option ", "Option_"), width=31).replace("Option_", "Option ")
        prompt.text(0.06, bottom + 0.159, wrapped, fontsize=7,
                    va="top", linespacing=1.35)
    for top, bottom in [(0.70, 0.63), (0.36, 0.29)]:
        prompt.add_patch(FancyArrowPatch((width / 2, top - 0.008), (width / 2, bottom + 0.008), arrowstyle="-|>",
                                         mutation_scale=7, color=shade, linewidth=0.7))
    # which message each block was sent in (GameEngine.build_prompt: rules = system, history + query = user)
    for top, bottom, message in [(0.97, 0.70, "System message"), (0.63, 0.02, "User message")]:
        prompt.plot([width + 0.035, width + 0.06, width + 0.06, width + 0.035], [top, top, bottom, bottom],
                    color=shade, linewidth=0.6, solid_joinstyle="miter")
        prompt.text(width + 0.1, (top + bottom) / 2, message, fontsize=6, color=shade,
                    rotation=90, ha="center", va="center")
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
    matchups.text(0, 0.345, f"{standard_models} models, {standard_trials} trials in most cells", fontsize=7, va="top")
    matchups.text(0, 0.28, f"Full cross-play ({pairs} pairs)", fontsize=7, va="top")
    matchups.text(0, 0.18, f"{frontier_models} frontier models\n{frontier_trials} trial in most cells", fontsize=7,
                  va="top", linespacing=1.35)
    matchups.text(0, 0.055, "Fixed opponents and self-play", fontsize=6, va="top", color=shade)
    fig.text(0.035, 0.166, "Recorded option letters; presentation order randomized", fontsize=6, color=shade)
    fig.text(0.5, 0.105, f"{models} models    |    {developers} developers    |    {games} games    |    {categories} categories",
             ha="center", fontsize=7)
    fig.text(0.5, 0.052, f"{trials} trials    |    {rounds} rounds    |    {replies} model replies",
             ha="center", fontsize=7)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "fig1_design")
