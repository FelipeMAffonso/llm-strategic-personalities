"""Supplementary Fig. 12: reasoning-text centroids and per-model silhouette scores (lexical embedding).

Reads summary_data/reasoning_text_clustering/, as written by analysis/reasoning_text_clustering.py: centroid_pca.csv
for panel a (each model's centroid; the fixed strategies' centroids that fall inside the panel are drawn in gray),
hodoscope_summary.json for panel b. The two-dimensional coordinates are the first two principal components of the
384-dimensional text vectors (the files named umap hold the clustering's PCA fallback, because umap-learn was not
installed when they were computed; centroid_umap.csv equals centroid_pca.csv). The silhouette uses developer as the
label, with the nine fixed strategies as a group of their own; the labels are checked by
analysis/check_developer_labels.py.

    python figures/figS12_developer_clustering.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import figlib
from figlib import plt

from common import DEVELOPER_ORDER, MODELS, ORDER

SOURCE = Path(figlib.CLUSTERING)


def build():
    figlib.style()
    summary = json.load(open(SOURCE / "hodoscope_summary.json", encoding="utf-8"))
    separation = summary["provider_separation"]
    labels = separation["provider_labels"]
    for key in ORDER:
        if labels.get(key) != MODELS[key][1].lower():
            raise ValueError(f"{key} is labelled {labels.get(key)!r} in the clustering, not {MODELS[key][1]}")
    silhouettes = separation["per_model_silhouette"]
    centroids = pd.read_csv(SOURCE / "centroid_pca.csv")

    fig = plt.figure(figsize=(7.2, 4.0))
    panel_a = fig.add_axes([0.075, 0.26, 0.47, 0.67])
    panel_b = fig.add_axes([0.745, 0.26, 0.235, 0.67])

    llm = centroids.loc[centroids.model_key.isin(MODELS)]
    margin = 0.08
    x_lim = (llm.x.min() - margin, llm.x.max() + margin)
    y_lim = (llm.y.min() - margin, llm.y.max() + margin)
    # panel a shows the centroids only: a density of the individual texts would be cut at this window
    strategies_drawn = 0
    for row in centroids.itertuples():
        if row.model_key in MODELS:
            panel_a.scatter(row.x, row.y, s=26, color=figlib.color(MODELS[row.model_key][1]), edgecolor="white", linewidth=0.4, zorder=3)
        elif x_lim[0] <= row.x <= x_lim[1] and y_lim[0] <= row.y <= y_lim[1]:
            panel_a.scatter(row.x, row.y, marker="D", s=18, color=figlib.PALETTE["strategy"], edgecolor="white", linewidth=0.3, zorder=2)
            strategies_drawn += 1
    panel_a.set(xlim=x_lim, ylim=y_lim, xlabel="Principal component 1", ylabel="Principal component 2")
    # ticks strictly inside the limits, so the corner labels of the two axes never meet
    panel_a.set_xticks([t for t in np.arange(-0.4, 0.41, 0.1) if x_lim[0] + 0.02 < t < x_lim[1]])
    panel_a.set_yticks([t for t in np.arange(-0.4, 0.41, 0.05) if y_lim[0] + 0.02 < t < y_lim[1]])
    panel_a.text(-0.01, 1.03, "a", transform=panel_a.transAxes, fontsize=8, weight="bold", va="bottom")
    handles = [Line2D([], [], marker="o", linestyle="none", color=figlib.color(d), label=d, markersize=4) for d in DEVELOPER_ORDER]
    if strategies_drawn:
        handles.append(Line2D([], [], marker="D", linestyle="none", color=figlib.PALETTE["strategy"], label="Fixed strategies", markersize=3.5))
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.06, 0.06), ncol=4, frameon=False, columnspacing=1.2, handletextpad=0.3)

    keys = sorted(ORDER, key=lambda k: (DEVELOPER_ORDER.index(MODELS[k][1]), ORDER.index(k)))
    values = [silhouettes[k] for k in keys]
    rows = np.arange(len(keys))
    panel_b.barh(rows, values, height=0.72, color=[figlib.color(MODELS[k][1]) for k in keys], edgecolor="none", zorder=2)
    panel_b.axvline(0, color=figlib.PALETTE["ink"], linewidth=0.5, zorder=3)
    panel_b.set_ylim(len(keys) - 0.4, -0.6)
    panel_b.set_yticks(rows, [MODELS[k][0] for k in keys], fontsize=6)
    panel_b.tick_params(axis="y", length=0, pad=3)
    for tick, key in zip(panel_b.get_yticklabels(), keys):
        tick.set_color(figlib.color(MODELS[key][1]))
    developers = [MODELS[k][1] for k in keys]
    for i in range(1, len(keys)):
        if developers[i] != developers[i - 1]:
            panel_b.axhline(i - 0.5, color=figlib.PALETTE["separator"], linewidth=0.6, zorder=1)
    panel_b.set_xlim(-0.8, 0.8)
    panel_b.set_xticks([-0.8, -0.4, 0, 0.4, 0.8])
    panel_b.set_xlabel("Silhouette score")
    panel_b.spines["left"].set_visible(False)
    panel_b.text(-0.75, 1.03, "b", transform=panel_b.transAxes, fontsize=8, weight="bold", va="bottom")
    fig.text(0.5, 0.012, f"Developer as the group label, fixed strategies as their own group; overall silhouette {separation['silhouette_score']:.4f}.\n"
             "LLaMA 3.3 70B, Ministral 14B and Qwen 3.5 Flash are their developers' only models, so each scores 0.",
             ha="center", va="bottom", fontsize=6, color=figlib.PALETTE["benchmark"], linespacing=1.4)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS12_developer_clustering")
