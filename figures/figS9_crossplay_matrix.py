import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import figlib
from figlib import plt

from common import MODELS, DEVELOPER_ORDER

SUMMARY = Path(figlib.SUMMARY)
RAW = Path(figlib.RAW)

FIVE_MODELS = [
    "claude-haiku-4.5", "claude-haiku-4.5-thinking", "gpt-4o-mini",
    "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5-mini", "gpt-5-nano",
    "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-flash-thinking",
    "gemini-3-flash", "deepseek-v3", "deepseek-r1", "llama-3.3-70b",
    "ministral-14b", "qwen3.5-flash",
]
KEYS = sorted(FIVE_MODELS, key=lambda key: (DEVELOPER_ORDER.index(MODELS[key][1]), list(MODELS).index(key)))


def read_matrix():
    profiles = pd.read_csv(SUMMARY / "behavioral_profiles.csv", low_memory=False)
    selected = profiles.loc[profiles.game_id.eq("pd_canonical") & profiles.model_key.isin(KEYS) & profiles.opponent.isin(KEYS)]
    if not set(selected.matchup_type).issubset({"cross_play", "self_play"}):
        raise ValueError("Unexpected matchup type in the selected design.")
    print("Processed matchup types:", selected.matchup_type.value_counts().to_dict())
    observations = defaultdict(list)
    pair_counts = Counter()
    records = Counter()
    for source in sorted(RAW.glob("pd_canonical_*.json")):
        trial = json.loads(source.read_text(encoding="utf-8"))
        detail = trial["match_detail"]
        players = detail["players"]
        first, second = players["0"], players["1"]
        if first not in KEYS or second not in KEYS:
            continue
        if trial["game_id"] != "pd_canonical" or trial["matchup_type"] not in {"cross_play", "self_play"}:
            raise ValueError(f"Unexpected raw trial: {source.name}")
        rounds = detail["rounds"]
        if len(rounds) != 10 or sorted(row["round_num"] for row in rounds) != list(range(1, 11)):
            raise ValueError(f"Incomplete round sequence: {source.name}")
        pair_counts[tuple(sorted([first, second]))] += 1
        records[(trial["model_key"], trial["opponent"], trial["condition"], trial["trial_num"])] += 1
        for row in rounds:
            for seat, own, partner in [("0", first, second), ("1", second, first)]:
                choice = row["parsed_choices"][seat]
                if choice not in {"cooperate", "defect"}:
                    raise ValueError(f"Unrecognized parsed action: {source.name}")
                observations[(own, partner)].append(choice == "cooperate")
    expected_records = Counter(selected[["model_key", "opponent", "condition", "trial_num"]].itertuples(index=False, name=None))
    if records != expected_records:
        raise ValueError("Raw and processed trial coverage differ.")
    matrix = np.array([[100 * np.mean(observations[(own, partner)]) if observations[(own, partner)] else np.nan
                        for partner in KEYS] for own in KEYS])
    assert matrix.shape == (16, 16) and np.isfinite(matrix).sum() == 256, "Expected 256 filled cells."
    assert sum(first != second for first, second in pair_counts) == 120, "Expected 120 distinct pairs."
    print("PASS: 256 filled cells = 120 pairs in both directions + 16 self-play cells")
    print("Recorded files per unordered pair, including self-play:", dict(sorted(Counter(pair_counts.values()).items())))
    return matrix, pair_counts


def build():
    figlib.style()
    matrix, pair_counts = read_matrix()
    fig = plt.figure(figsize=(7.2, 7.6))
    axis = fig.add_axes([0.28, 0.23, 0.69, 0.50])
    cmap = LinearSegmentedColormap.from_list("cooperation", ["white", figlib.color("Google"), figlib.color("Alibaba")])
    image = axis.imshow(matrix, vmin=0, vmax=100, cmap=cmap, aspect="auto", interpolation="none")
    labels = [MODELS[key][0] for key in KEYS]
    axis.set_xticks(range(16), labels, rotation=90, ha="center", va="bottom", fontsize=6)
    axis.xaxis.tick_top()
    axis.set_yticks(range(16), labels, fontsize=7)
    axis.tick_params(length=0, pad=5)
    axis.set_xlabel("Partner", labelpad=9)
    axis.set_ylabel("Model", labelpad=7)
    for ticks in [axis.get_xticklabels(), axis.get_yticklabels()]:
        for tick, key in zip(ticks, KEYS):
            tick.set_color(figlib.color(MODELS[key][1]))
    for row, column in np.ndindex(matrix.shape):
        value = matrix[row, column]
        axis.text(column, row, f"{value:.1f}", ha="center", va="center", fontsize=6,
                  color="white" if value >= 50 else figlib.PALETTE["ink"])
    for position in range(15):
        if MODELS[KEYS[position]][1] != MODELS[KEYS[position + 1]][1]:
            axis.axhline(position + 0.5, color=figlib.PALETTE["separator"], linewidth=0.7)
            axis.axvline(position + 0.5, color=figlib.PALETTE["separator"], linewidth=0.7)
    for spine in axis.spines.values():
        spine.set_visible(False)
    color_axis = fig.add_axes([0.28, 0.115, 0.69, 0.018])
    colorbar = fig.colorbar(image, cax=color_axis, orientation="horizontal", ticks=[0, 25, 50, 75, 100])
    colorbar.set_label("Cooperation (%)", labelpad=5)
    colorbar.outline.set_visible(False)
    fig.text(0.5, 0.035, "Recorded trials; both player slots; replication counts vary", ha="center", fontsize=6,
             color=figlib.PALETTE["benchmark"])
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS9_crossplay_matrix")
