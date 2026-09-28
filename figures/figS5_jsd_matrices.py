from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import figlib
from figlib import plt

from common import CATEGORIES, DEVELOPER_ORDER, MODELS


def build():
    figlib.style()
    source = Path(figlib.CLUSTERING)
    keys = sorted(MODELS, key=lambda key: DEVELOPER_ORDER.index(MODELS[key][1]))
    matrices = [pd.read_csv(source / "aggregate_jsd.csv", index_col=0).loc[keys, keys].to_numpy()]
    for category in ["cooperation", "competition"]:
        games = next(entry[2] for entry in CATEGORIES if entry[0] == category)
        parts = np.array([pd.read_csv(source / f"jsd_per_game/{game}_jsd.csv", index_col=0).reindex(index=keys, columns=keys).to_numpy() for game in games])
        counts = np.isfinite(parts).sum(axis=0)
        assert counts.min() > 0
        matrices.append(np.nanmean(parts, axis=0))
        print(f"{category}: {len(games)} game matrices; available games per cell {counts.min()} to {counts.max()}")
    for matrix in matrices:
        assert matrix.shape == (25, 25) and np.isfinite(matrix).all()
        assert np.allclose(matrix, matrix.T) and np.allclose(np.diag(matrix), 0)
    maximum = max(matrix.max() for matrix in matrices)
    fig = plt.figure(figsize=(7.2, 11.2))
    cmap = LinearSegmentedColormap.from_list("distance", ["white", figlib.color("Google"), figlib.color("Alibaba")])
    titles = ["All 38 games", "Cooperation games", "Competition games"]
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
    fig.text(0.5, 0.012, "Available-game means: cooperation 2 to 10; competition 1 to 4 games per cell", ha="center", fontsize=6,
             color=figlib.PALETTE["benchmark"])
    print("Shared maximum:", maximum)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS5_jsd_matrices")
