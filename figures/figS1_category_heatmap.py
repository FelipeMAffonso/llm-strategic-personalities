import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import figlib
from figlib import plt
from fig2_categories import DATA, DEVELOPERS, CATEGORIES


def build():
    figlib.style()
    data = pd.read_csv(DATA / "A4_category_index.csv")
    if data.duplicated(["model_key", "category"]).any():
        raise ValueError("Duplicate model-category estimates.")
    models = data.loc[data.category.eq("coordination")].copy()
    models["developer_order"] = models.developer.map(DEVELOPERS.index)
    models = models.sort_values("developer_order", kind="stable")
    categories = [entry[0] for entry in CATEGORIES]
    matrix = data.pivot(index="model_key", columns="category", values="mean").loc[models.model_key, categories] * 100
    values = matrix.to_numpy()
    if values.shape != (25, 8) or not np.isfinite(values).all() or (values < 0).any() or (values > 100).any():
        raise ValueError("Expected 25 by 8 complete category indices between 0 and 100.")
    fig = plt.figure(figsize=(7.2, 6.6))
    axis = fig.add_axes([0.255, 0.18, 0.72, 0.72])
    shades = LinearSegmentedColormap.from_list("category_index", ["#ffffff", figlib.color("Google"), figlib.color("Alibaba")])
    image = axis.imshow(values, vmin=0, vmax=100, cmap=shades, aspect="auto", interpolation="none")
    labels = [entry[1].replace("Strategic depth", "Strategic\ndepth").replace("Risk taking", "Risk\ntaking") for entry in CATEGORIES]
    axis.set_xticks(np.arange(8), labels)
    axis.xaxis.tick_top()
    axis.tick_params(axis="x", length=0, pad=8)
    axis.set_yticks(np.arange(25), models.display)
    axis.tick_params(axis="y", length=0, pad=5)
    for tick, developer in zip(axis.get_yticklabels(), models.developer):
        tick.set_color(figlib.color(developer))
    for row, column in np.ndindex(values.shape):
        value = values[row, column]
        axis.text(column, row, f"{value:.1f}", ha="center", va="center", fontsize=7,
                  color="white" if value >= 50 else figlib.PALETTE["ink"], gid=f"cell:{row}:{column}")
    separators = np.flatnonzero(models.developer.to_numpy()[:-1] != models.developer.to_numpy()[1:]) + 0.5
    for separator in separators:
        axis.axhline(separator, color=figlib.PALETTE["separator"], linewidth=0.8)
    for spine in axis.spines.values():
        spine.set_visible(False)
    color_axis = fig.add_axes([0.255, 0.085, 0.72, 0.018])
    colorbar = fig.colorbar(image, cax=color_axis, orientation="horizontal", ticks=[0, 25, 50, 75, 100])
    colorbar.set_label("Category index (0 to 100)", labelpad=5)
    colorbar.outline.set_visible(False)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS1_category_heatmap")
