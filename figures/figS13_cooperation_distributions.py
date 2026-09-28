"""Supplementary Fig. 13: every model's game-level cooperation rates, shown as points.

One row per model, one dot per cooperation game with a cooperation measure (the mean cooperation rate over the
model's trials in that game), a black tick at the model's median; developer colors match the main figures.

    python figures/figS13_cooperation_distributions.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

import figlib
from figlib import plt
from fig2_categories import DATA, DEVELOPERS

# The six cooperation games whose processed data carry a cooperation rate. The three public-goods games and the
# commons dilemma store 0 in every trial (no cooperation measure is extracted for them), so plotting them would show
# four constant zeros per model.
GAMES = ["pd_canonical", "pd_harsh", "pd_medium", "pd_mild", "diners_dilemma", "el_farol_bar"]
# fixed vertical offsets so the dots of one row do not sit on top of each other
OFFSETS = np.linspace(-0.27, 0.27, len(GAMES))


def build():
    figlib.style()
    metadata = pd.read_csv(DATA / "A4_category_index.csv")
    models = metadata.loc[metadata.category.eq("coordination")].copy()
    models["developer_order"] = models.developer.map(DEVELOPERS.index)
    models = models.sort_values("developer_order", kind="stable").reset_index(drop=True)
    profiles = pd.read_csv(DATA / "behavioral_profiles.csv", low_memory=False,
                           usecols=["model_key", "game_id", "cooperation_rate"])
    rates = (profiles[profiles.game_id.isin(GAMES)].groupby(["model_key", "game_id"]).cooperation_rate.mean()
             .unstack().reindex(index=models.model_key, columns=GAMES) * 100)
    if rates.shape != (25, len(GAMES)) or not np.isfinite(rates.to_numpy()).all():
        missing = [(m, g) for m in rates.index for g in rates.columns if not np.isfinite(rates.loc[m, g])]
        raise ValueError(f"Expected 25 models by 6 cooperation games, all present; missing {missing[:5]}")
    fig = plt.figure(figsize=(7.2, 7.0))
    axis = fig.add_axes([0.24, 0.1, 0.72, 0.86])
    for row, (key, developer) in enumerate(zip(models.model_key, models.developer)):
        values = rates.loc[key].to_numpy()
        axis.scatter(values, row + OFFSETS, s=9, color=figlib.color(developer), alpha=0.85, linewidths=0, zorder=3)
        median = float(np.median(values))
        axis.plot([median, median], [row - 0.36, row + 0.36], color=figlib.PALETTE["ink"], linewidth=1.1, zorder=4)
    axis.set_yticks(np.arange(len(models)), models.display)
    axis.tick_params(axis="y", length=0, pad=5)
    for tick, developer in zip(axis.get_yticklabels(), models.developer):
        tick.set_color(figlib.color(developer))
    separators = np.flatnonzero(models.developer.to_numpy()[:-1] != models.developer.to_numpy()[1:]) + 0.5
    for separator in separators:
        axis.axhline(separator, color=figlib.PALETTE["separator"], linewidth=0.8, zorder=1)
    axis.set_ylim(len(models) - 0.5, -0.5)
    axis.set_xlim(-2, 102)
    axis.set_xticks([0, 25, 50, 75, 100])
    axis.set_xlabel("Cooperation (%), one point per cooperation game; black tick, model median")
    axis.spines["left"].set_visible(False)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS13_cooperation_distributions")
