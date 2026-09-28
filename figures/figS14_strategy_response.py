import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import figlib
from figlib import plt
from fig2_categories import DATA, DEVELOPERS


OPPONENTS = [
    "always_cooperate", "tit_for_tat", "tit_for_two_tats", "pavlov",
    "grim_trigger", "hard_tft", "suspicious_tft", "mirror",
    "false_defector", "defect_once", "noise_10", "noise_20",
    "reverse_tft", "anti_mirror", "random", "always_defect",
]
LABELS = [
    "Always-cooperate", "Tit-for-tat", "Tit-for-two-tats", "Pavlov",
    "Grim trigger", "Hard tit-for-tat", "Suspicious tit-for-tat", "Mirror",
    "False defector", "Defect once", "Noise 10%", "Noise 20%",
    "Reverse tit-for-tat", "Anti-mirror", "Random", "Always-defect",
]


def build():
    figlib.style()
    data = pd.read_csv(DATA / "A1_by_opponent.csv", index_col="model_key")
    metadata = pd.read_csv(DATA / "A4_category_index.csv")
    models = metadata.loc[metadata.category.eq("coordination")].copy()
    models["developer_order"] = models.developer.map(DEVELOPERS.index)
    models = models.sort_values("developer_order", kind="stable")
    if data.index.duplicated().any() or set(data.index) != set(models.model_key):
        raise ValueError("Opponent estimates must contain exactly the category model set.")
    values = data.loc[models.model_key, OPPONENTS].to_numpy()
    if values.shape != (25, 16) or not np.isfinite(values).all() or (values < 0).any() or (values > 100).any():
        raise ValueError("Expected 25 by 16 complete cooperation percentages.")
    fig = plt.figure(figsize=(7.2, 7.2))
    axis = fig.add_axes([0.255, 0.16, 0.72, 0.64])
    shades = LinearSegmentedColormap.from_list("cooperation", ["#ffffff", figlib.color("Google"), figlib.color("Alibaba")])
    image = axis.imshow(values, vmin=0, vmax=100, cmap=shades, aspect="auto", interpolation="none")
    axis.set_xticks(np.arange(16), LABELS, rotation=90, ha="center", va="bottom")
    axis.xaxis.tick_top()
    axis.tick_params(axis="x", length=0, pad=6)
    axis.set_yticks(np.arange(25), models.display)
    axis.tick_params(axis="y", length=0, pad=5)
    for tick, developer in zip(axis.get_yticklabels(), models.developer):
        tick.set_color(figlib.color(developer))
    for row, column in np.ndindex(values.shape):
        value = values[row, column]
        axis.text(column, row, f"{value:.1f}", ha="center", va="center", fontsize=6,
                  color="white" if value >= 50 else figlib.PALETTE["ink"], gid=f"cell:{row}:{column}")
    separators = np.flatnonzero(models.developer.to_numpy()[:-1] != models.developer.to_numpy()[1:]) + 0.5
    for separator in separators:
        axis.axhline(separator, color=figlib.PALETTE["separator"], linewidth=0.8)
    for spine in axis.spines.values():
        spine.set_visible(False)
    color_axis = fig.add_axes([0.255, 0.08, 0.72, 0.018])
    colorbar = fig.colorbar(image, cax=color_axis, orientation="horizontal", ticks=[0, 25, 50, 75, 100])
    colorbar.set_label("Cooperation (%)", labelpad=5)
    colorbar.outline.set_visible(False)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS14_strategy_response")
