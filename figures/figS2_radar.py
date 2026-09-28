from pathlib import Path

import numpy as np
import pandas as pd

import figlib
from figlib import plt

from common import CATEGORIES, DEVELOPER_ORDER, MODELS


def build():
    figlib.style()
    data = pd.read_csv(Path(figlib.SUMMARY) / "A4_category_index.csv")
    keys = sorted(MODELS, key=lambda key: DEVELOPER_ORDER.index(MODELS[key][1]))
    values = data.pivot(index="model_key", columns="category", values="mean").loc[keys, [item[0] for item in CATEGORIES]] * 100
    assert values.shape == (25, 8) and np.isfinite(values).all().all()
    angles = np.arange(8) * np.pi / 4
    labels = [item[1].replace("Strategic depth", "Strategic\ndepth").replace("Risk taking", "Risk\ntaking") for item in CATEGORIES]
    fig = plt.figure(figsize=(7.2, 8.8))
    for position, key in enumerate(keys):
        row, column = divmod(position, 5)
        center_x = 0.94 + column * 1.355
        center_y = 7.72 - row * 1.64
        axis = fig.add_axes([(center_x - 0.43) / 7.2, (center_y - 0.43) / 8.8, 0.86 / 7.2, 0.86 / 8.8], projection="polar")
        axis.set_theta_zero_location("N")
        axis.set_theta_direction(-1)
        axis.set_ylim(0, 100)
        axis.set_xticks(angles, labels if column == 0 else [""] * 8, fontsize=5)
        axis.tick_params(axis="x", pad=8)
        axis.set_yticks([25, 50, 75, 100], [])
        axis.tick_params(grid_color=figlib.PALETTE["separator"], grid_linewidth=0.5)
        axis.spines["polar"].set_color(figlib.PALETTE["separator"])
        shade = figlib.color(MODELS[key][1])
        polygon = np.r_[values.loc[key].to_numpy(), values.loc[key].iloc[0]]
        closed_angles = np.r_[angles, angles[0]]
        axis.fill(closed_angles, polygon, color=shade, alpha=0.16)
        axis.plot(closed_angles, polygon, color=shade, linewidth=0.9)
        title = MODELS[key][0].replace(" (Thinking)", "\n(Thinking)")
        fig.text(center_x / 7.2, (center_y + 0.81) / 8.8, title, ha="center", va="top", fontsize=6, color=shade)
    fig.text(0.5, 0.028, "Category indices: 0 at center, 100 at outer ring; rings every 25", ha="center", fontsize=6)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS2_radar")
