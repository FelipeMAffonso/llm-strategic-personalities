"""Supplementary Fig. 16: standard and thinking configurations on the eight category indices.

The values are the category indices of Fig. 2 and Supplementary Fig. 1 (summary_data/A4_category_index.csv:
strategy-play against the common opponents of each category, opponents weighted equally, 95 percent bootstrap
intervals), so every bar here equals the matching cell of Supplementary Fig. 1.

The pairs are found from the model list in analysis/common.py, not typed: a model whose key is another model's key
plus "-thinking" (the same snapshot called with thinking on), and a product line holding exactly two models, one with
reasoning and one without (DeepSeek V3 and DeepSeek R1, which are two different models). The script stops if it finds
a number of pairs other than three.

    python figures/figS16_thinking_comparison.py
"""
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch

import figlib
from figlib import plt
from fig2_categories import DATA, CATEGORIES

from common import MODELS


def find_pairs():
    """(standard key, reasoning key, same_snapshot) for every standard and reasoning pair in the model list."""
    pairs = []
    for key, (_, _, _, _, reasoning) in MODELS.items():
        base = key[: -len("-thinking")] if key.endswith("-thinking") else None
        if reasoning and base in MODELS and not MODELS[base][4]:
            pairs.append((base, key, True))
    paired = {k for p in pairs for k in p[:2]}
    lines = {}
    for key, (_, _, line, _, reasoning) in MODELS.items():
        lines.setdefault(line, []).append((key, reasoning))
    for line, members in lines.items():
        if len(members) == 2 and sorted(r for _, r in members) == [False, True] and not paired & {k for k, _ in members}:
            standard = next(k for k, r in members if not r)
            thinking = next(k for k, r in members if r)
            pairs.append((standard, thinking, False))
    if len(pairs) != 3:
        raise ValueError(f"Expected three standard and reasoning pairs, found {pairs}")
    return pairs


def tint(hex_color, share):
    rgb = np.array(to_rgb(hex_color))
    return tuple(rgb + (1 - rgb) * share)


def build():
    figlib.style()
    data = pd.read_csv(DATA / "A4_category_index.csv")
    if data.duplicated(["model_key", "category"]).any():
        raise ValueError("Duplicate model-category estimates.")
    pairs = find_pairs()
    categories = [entry[0] for entry in CATEGORIES]
    names = [entry[1] for entry in CATEGORIES]
    table = data.set_index(["model_key", "category"])
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.55), sharey=True)
    fig.subplots_adjust(left=0.115, right=0.985, top=0.86, bottom=0.30, wspace=0.12)
    rows = np.arange(len(categories))
    height = 0.36
    for index, (panel, (standard, thinking, same_snapshot)) in enumerate(zip(axes, pairs)):
        developer = MODELS[standard][1]
        full = figlib.color(developer)
        light = tint(full, 0.55)
        if same_snapshot:
            title = MODELS[standard][0]
            labels = ("Standard", "Extended thinking" if developer == "Anthropic" else "Thinking")
        else:
            title = f"{MODELS[standard][0]} and {MODELS[thinking][0]}"
            labels = (f"{MODELS[standard][0]}, standard", f"{MODELS[thinking][0]}, reasoning")
        for offset, key, shade in ((-height / 2 - 0.02, standard, light), (height / 2 + 0.02, thinking, full)):
            cells = table.loc[[(key, c) for c in categories]]
            means, lo, hi = (cells[c].to_numpy() * 100 for c in ("mean", "ci_lo", "ci_hi"))
            if not (np.isfinite(means).all() and np.isfinite(lo).all() and np.isfinite(hi).all()):
                raise ValueError(f"Missing category estimates for {key}")
            positions = rows + offset
            panel.barh(positions, means, height=height, color=shade, edgecolor="none", zorder=2)
            panel.hlines(positions, lo, hi, color=figlib.PALETTE["ink"], linewidth=0.6, zorder=3)
            for y, value, right in zip(positions, means, hi):
                panel.text(right + 1.6, y, f"{value:.1f}", va="center", ha="left", fontsize=6,
                           color=figlib.PALETTE["ink"], gid=f"value:{key}")
        panel.set_ylim(len(categories) - 0.45, -0.55)
        panel.set_yticks(rows, names)
        panel.tick_params(axis="y", length=0, pad=4)
        panel.set_xlim(0, 112)
        panel.set_xticks([0, 25, 50, 75, 100])
        panel.spines["left"].set_visible(False)
        panel.set_title(title, fontsize=7, pad=10)
        panel.text(-0.02, 1.045, chr(ord("a") + index), transform=panel.transAxes, fontsize=8, weight="bold", va="bottom")
        panel.legend(handles=[Patch(color=light, label=labels[0]), Patch(color=full, label=labels[1])],
                     loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False,
                     handlelength=1.1, handletextpad=0.4, borderaxespad=0)
    axes[1].set_xlabel("Category index (0 to 100)", labelpad=4)
    fig.text(0.5, 0.035, "Bars, the category indices of Fig. 2 and Supplementary Fig. 1; lines, 95% intervals. "
             "Panels a and b switch thinking on in one model; panel c compares two models.",
             ha="center", fontsize=6.5, color=figlib.PALETTE["benchmark"])
    return fig, pairs


if __name__ == "__main__":
    fig, pairs = build()
    print("pairs:", pairs)
    figlib.save(fig, "figS16_thinking_comparison")
