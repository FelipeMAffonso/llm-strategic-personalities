"""Supplementary Fig. 5: Jensen-Shannon distances between the models' choice distributions, averaged over the 36
scored games (a), the cooperation games (b) and the three scored competition games (c).

Colonel Blotto and multi-issue negotiation are left out: each answer needed several numbers and the parser kept one,
so their choice distributions do not describe the models' play. The script first checks that averaging all 38
per-game matrices reproduces the stored aggregate (summary_data/reasoning_text_clustering/aggregate_jsd.csv).

    python figures/figS5_jsd_matrices.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import figlib
from figlib import plt

from common import CATEGORIES, DEVELOPER_ORDER, MODELS

SOURCE = Path(figlib.CLUSTERING)
UNSCORED = {"colonel_blotto", "multi_issue"}


def per_game():
    matrices = {path.name[:-len("_jsd.csv")]: pd.read_csv(path, index_col=0) for path in sorted(SOURCE.glob("jsd_per_game/*_jsd.csv"))}
    assert all(matrix.notna().all().all() for matrix in matrices.values())
    return matrices


def average(matrices, games, labels):
    """Mean over the games in which both agents of a pair appear, as compute_aggregate_jsd in
    analysis/reasoning_text_clustering.py builds aggregate_jsd.csv: per cell, the sum over available games divided by
    their number; a pair that never shares a game gets 0 there (only fixed strategies, never two models)."""
    parts = np.array([matrices[game].reindex(index=labels, columns=labels).to_numpy() for game in games])
    counts = np.isfinite(parts).sum(axis=0)
    return np.nansum(parts, axis=0) / np.maximum(counts, 1), counts


def build():
    figlib.style()
    keys = sorted(MODELS, key=lambda key: DEVELOPER_ORDER.index(MODELS[key][1]))
    games = per_game()
    # the averaging reproduces the stored 38-game aggregate before the two unscored games are dropped
    aggregate = pd.read_csv(SOURCE / "aggregate_jsd.csv", index_col=0)
    assert len(games) == 38
    reproduced, _ = average(games, sorted(games), list(aggregate.index))
    assert np.abs(reproduced - aggregate.to_numpy()).max() < 1e-12
    scored = [game for game in sorted(games) if game not in UNSCORED]
    panels = [("all", scored, f"All {len(scored)} games")]
    for category in ["cooperation", "competition"]:
        members = [game for game in next(entry[2] for entry in CATEGORIES if entry[0] == category) if game not in UNSCORED]
        panels.append((category, members, f"{category.capitalize()} games ({len(members)})"))
    matrices, titles, notes = [], [], []
    for name, members, title in panels:
        matrix, counts = average(games, members, keys)
        assert counts.min() > 0  # every pair of models shares at least one game in the panel
        matrices.append(matrix)
        titles.append(title)
        notes.append(f"{'all games' if name == 'all' else name} {counts.min()} to {counts.max()}")
        print(f"{title}: {len(members)} game matrices; available games per cell {counts.min()} to {counts.max()}")
    for matrix in matrices:
        assert matrix.shape == (25, 25) and np.isfinite(matrix).all()
        assert np.allclose(matrix, matrix.T) and np.allclose(np.diag(matrix), 0)
    maximum = max(matrix.max() for matrix in matrices)
    fig = plt.figure(figsize=(7.2, 11.2))
    cmap = LinearSegmentedColormap.from_list("distance", ["white", figlib.color("Google"), figlib.color("Alibaba")])
    labels = [MODELS[key][0] for key in keys]
    for position, (matrix, title, bottom) in enumerate(zip(matrices, titles, [0.735, 0.475, 0.215])):
        axis = fig.add_axes([0.265, bottom, 0.70, 0.225])
        image = axis.imshow(matrix, cmap=cmap, vmin=0, vmax=maximum, aspect="auto", interpolation="none")
        axis.set_yticks(range(25), labels, fontsize=6)
        axis.set_xticks(range(25), labels if position == 2 else [""] * 25, rotation=90, fontsize=6)
        axis.tick_params(length=0, pad=4)
        for ticks in [axis.get_xticklabels(), axis.get_yticklabels()]:
            for tick, key in zip(ticks, keys):
                tick.set_color(figlib.color(MODELS[key][1]))
        for boundary in range(24):
            if MODELS[keys[boundary]][1] != MODELS[keys[boundary + 1]][1]:
                axis.axhline(boundary + 0.5, color=figlib.PALETTE["separator"], linewidth=0.6)
                axis.axvline(boundary + 0.5, color=figlib.PALETTE["separator"], linewidth=0.6)
        for spine in axis.spines.values():
            spine.set_visible(False)
        fig.text(0.025, bottom + 0.236, "abc"[position], fontsize=8, fontweight="bold", va="bottom")
        fig.text(0.265, bottom + 0.236, title, fontsize=7, va="bottom")
    color_axis = fig.add_axes([0.265, 0.052, 0.70, 0.012])
    colorbar = fig.colorbar(image, cax=color_axis, orientation="horizontal")
    colorbar.set_ticks(np.arange(0, maximum + 0.001, 0.1))
    colorbar.set_label("Jensen-Shannon distance", labelpad=5)
    colorbar.outline.set_visible(False)
    fig.text(0.5, 0.012, "Available-game means: " + "; ".join(notes) + " games per cell", ha="center", fontsize=6,
             color=figlib.PALETTE["benchmark"])
    print("Shared maximum:", maximum)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS5_jsd_matrices")
