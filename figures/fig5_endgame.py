import json
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import figlib
from figlib import plt


DATA = Path(figlib.SUMMARY)
CLASSES = [
    ("reactive", "Reactive opponents"),
    ("fixed_cooperate", "Always-cooperate"),
    ("self_play", "Self-play"),
    ("cross_play", "Cross-play"),
]
HIGHLIGHTS = [
    ("claude-opus-4.6", "sustained cooperator", "o"),
    ("gemini-3-pro", "horizon-conditioned", "D"),
    ("gpt-5-nano", "unconditional defector", "s"),
]
CROSS_PLAY_MODELS = [
    "claude-haiku-4.5", "claude-haiku-4.5-thinking", "gpt-4o-mini",
    "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5-mini", "gpt-5-nano",
    "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-flash-thinking",
    "gemini-3-flash", "deepseek-v3", "deepseek-r1", "llama-3.3-70b",
    "ministral-14b", "qwen3.5-flash",
]
BENCHMARKS = {
    "reactive": "cooperate rounds 1 to 9, defect round 10",
    "fixed_cooperate": "defect every round",
    "self_play": "defect throughout (subgame perfect)",
    "cross_play": "defect throughout (subgame perfect)",
}


def read_sources():
    rounds = pd.read_csv(DATA / "A3_rounds_by_class.csv", index_col=["model_key", "opponent_class"])
    endings = pd.read_csv(DATA / "A3_round10.csv", index_col=["model_key", "opponent_class"])
    summary = json.loads((DATA / "A3_summary.json").read_text(encoding="utf-8"))
    columns = [str(round_number) for round_number in range(1, 11)]
    if rounds.index.duplicated().any() or endings.index.duplicated().any():
        raise ValueError("Expected one row per model and opponent class.")
    if not rounds.index.sort_values().equals(endings.index.sort_values()):
        raise ValueError("Round tables have different model or opponent-class coverage.")
    values = rounds[columns].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
        raise ValueError("Round estimates must be finite shares within the unit interval.")
    endings = endings.loc[rounds.index]
    if not np.allclose(rounds["9"], endings.round9) or not np.allclose(rounds["10"], endings.round10):
        raise ValueError("Final-round estimates differ across the supplied tables.")
    if not np.allclose(rounds["9"] - rounds["10"], endings.drop_9_to_10):
        raise ValueError("Final-round changes differ across the supplied tables.")
    for opponent_class, expected in BENCHMARKS.items():
        if not str(summary["benchmarks"][opponent_class]).startswith(expected):  # the class list may follow the benchmark text
            raise ValueError(f"Benchmark changed for {opponent_class}; review the figure specification.")
    for model, expected_type, marker in HIGHLIGHTS:
        entry = summary["types_vs_reactive"][model]
        if entry["type"] != expected_type:
            raise ValueError(f"Reactive classification changed for {model}.")
        row = endings.loc[(model, "reactive")]
        if row.display != entry["display"] or row.developer != entry["developer"]:
            raise ValueError(f"Model metadata differ across sources for {model}.")
        if not np.allclose([row.round9, row.round10],
                           [entry["round9_reactive"], entry["round10_reactive"]], atol=0.00051, rtol=0):
            raise ValueError(f"Reactive summary differs from round estimates for {model}.")
    return rounds[columns], summary


def build():
    figlib.style()
    rounds, summary = read_sources()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.085, right=0.977, top=0.928, bottom=0.115, wspace=0.16, hspace=0.40)
    round_numbers = np.arange(1, 11)
    for index, (axis, (opponent_class, title)) in enumerate(zip(axes.flat, CLASSES)):
        subset = rounds.xs(opponent_class, level="opponent_class")
        if opponent_class == "cross_play":
            subset = subset.loc[CROSS_PLAY_MODELS]
        for model, row in subset.iterrows():
            axis.plot(round_numbers, row.to_numpy() * 100, color=figlib.PALETTE["strategy"],
                      linewidth=0.55, alpha=0.45, zorder=1, gid=f"context:{model}")
        benchmark = np.r_[np.full(9, 100.0), 0.0] if opponent_class == "reactive" else np.zeros(10)
        axis.plot(round_numbers, benchmark, color=figlib.PALETTE["benchmark"], linewidth=1.0,
                  linestyle=(0, (3, 2)), zorder=2, gid="benchmark")
        missing = []
        for model, model_type, marker in HIGHLIGHTS:
            if model not in subset.index:
                missing.append(model_type)
                continue
            shade = figlib.color(summary["types_vs_reactive"][model]["developer"])
            axis.plot(round_numbers, subset.loc[model].to_numpy() * 100, color=shade,
                      marker=marker, markersize=4.4 if marker == "D" else 2.8,
                      markerfacecolor="none" if marker == "D" else shade,
                      markeredgewidth=0.75, linewidth=1.2,
                      linestyle=(0, (4, 2)) if marker == "D" else "-",
                      zorder=4, gid=f"highlight:{model}")
        axis.set_xlim(0.8, 10.2)
        axis.set_ylim(-5, 136)
        axis.set_xticks(round_numbers)
        axis.set_yticks([0, 25, 50, 75, 100])
        axis.tick_params(axis="x", labelbottom=True)
        axis.set_xlabel("Round", labelpad=4)
        if index % 2 == 0:
            axis.set_ylabel("Cooperation (%)", labelpad=5)
        else:
            axis.tick_params(axis="y", left=False)
        axis.spines["left"].set_bounds(0, 100)
        axis.spines["bottom"].set_bounds(1, 10)
        axis.text(-0.025, 1.075, chr(ord("a") + index), transform=axis.transAxes,
                  fontsize=8, weight="bold", va="bottom")
        axis.set_title(title, fontsize=7, pad=14)
        if index == 0:
            handles = []
            for model, model_type, marker in HIGHLIGHTS:
                entry = summary["types_vs_reactive"][model]
                shade = figlib.color(entry["developer"])
                handles.append(Line2D([], [], color=shade, marker=marker,
                                      markersize=4.4 if marker == "D" else 2.8,
                                      markerfacecolor="none" if marker == "D" else shade,
                                      markeredgewidth=0.75, linewidth=1.2,
                                      linestyle=(0, (4, 2)) if marker == "D" else "-",
                                      label=entry["display"]))
            handles.append(Line2D([], [], color=figlib.PALETTE["benchmark"], linewidth=1.0,
                                  linestyle=(0, (3, 2)), label="Class benchmark"))
            axis.legend(handles=handles, loc="upper center", ncol=2, frameon=False,
                        handlelength=2.0, columnspacing=1.0, handletextpad=0.5,
                        borderaxespad=0.15, labelspacing=0.5)
        else:
            axis.text(0.5, 0.945, f"{len(subset)} models with data", transform=axis.transAxes,
                      fontsize=6, ha="center", color=figlib.PALETTE["benchmark"])
        if missing:
            missing_label = "Sustained cooperator and horizon-conditioned\nhighlight not in this design"
            axis.text(0.5, 0.825, missing_label, transform=axis.transAxes, fontsize=6,
                      ha="center", color=figlib.PALETTE["benchmark"])
            print(f"{opponent_class}: unavailable highlight types: {', '.join(missing)}")
    fig.text(0.5, 0.035, "Thin gray lines show models in each displayed design", ha="center",
             fontsize=7, color=figlib.PALETTE["benchmark"])
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "fig5_endgame")
