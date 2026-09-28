from pathlib import Path

import numpy as np
import pandas as pd

import figlib
from figlib import plt
from matplotlib.lines import Line2D


DATA = Path(figlib.SUMMARY)
DEVELOPERS = list(figlib.PALETTE["developer"])
CATEGORIES = [
    ("coordination", "Coordination", "Share of rounds\nwith matching actions", 1.0),
    ("depth", "Strategic depth", "One minus mean\nguess over 50", 1.0),
    ("competition", "Competition", "Bid over\nmaximum bid", None),
    ("cooperation", "Cooperation", "Share of rounds\ncooperating", 0.37),
    ("trust", "Trust", "Share of\nendowment sent", 0.50),
    ("fairness", "Fairness", "Share of\nendowment offered", 0.40),
    ("negotiation", "Negotiation", "Share of\nsurplus demanded", 0.50),
    ("risk", "Risk taking", "Share of rounds\nchoosing risky action", 2 / 13),
]


def build():
    figlib.style()
    data = pd.read_csv(DATA / "A4_category_index.csv")
    summary = pd.read_csv(DATA / "A4_category_summary.csv").set_index("category")
    models = data.loc[data.category.eq("coordination")].copy()
    models["developer_order"] = models.developer.map(DEVELOPERS.index)
    models = models.sort_values("developer_order", kind="stable")
    keys = models.model_key.tolist()
    if len(keys) != 25 or data.duplicated(["category", "model_key"]).any():
        raise ValueError("Expected one estimate per model and category.")
    fig, axes = plt.subplots(2, 4, figsize=(7.2, 9.2), sharey=True)
    fig.subplots_adjust(left=0.255, right=0.978, top=0.956, bottom=0.12, wspace=0.19, hspace=0.23)
    positions = np.arange(len(keys))
    separators = np.flatnonzero(models.developer.to_numpy()[:-1] != models.developer.to_numpy()[1:]) + 0.5
    for panel, (category, title, label, benchmark) in zip(axes.flat, CATEGORIES):
        subset = data.loc[data.category.eq(category)].set_index("model_key").loc[keys]
        if subset[["mean", "ci_lo", "ci_hi"]].isna().any().any():
            raise ValueError(f"Missing category estimates: {category}")
        if summary.loc[category, "n_models"] != len(subset):
            raise ValueError(f"Model count differs from summary: {category}")
        for position, (_, row) in zip(positions, subset.iterrows()):
            shade = figlib.color(row.developer)
            panel.plot([row.ci_lo, row.ci_hi], [position, position], color=shade, linewidth=0.85)
            panel.plot(row["mean"], position, "o", color=shade, markersize=3.0)
        for separator in separators:
            panel.axhline(separator, color=figlib.PALETTE["separator"], linewidth=0.55, zorder=0)
        lower = min(0.0, subset.ci_lo.min())
        upper = max(subset.ci_hi.max(), benchmark if benchmark is not None else 0)
        span = upper - lower
        panel.set_xlim(lower - 0.045 * span, upper + 0.045 * span)
        if benchmark is not None:
            panel.axvline(benchmark, ymin=0.025, ymax=0.975, color=figlib.PALETTE["benchmark"],
                          linewidth=0.7, linestyle=(0, (2, 3)), zorder=0)
        panel.set_ylim(len(keys) - 0.4, -0.6)
        panel.set_yticks(positions, models.display)
        panel.tick_params(axis="y", length=0, pad=5)
        panel.set_xticks([0, 0.5, 1] if upper > 0.8 else [0, 0.2, 0.4] if upper < 0.5 else [0, 0.25, 0.5])
        panel.set_xlabel(label, labelpad=5, fontsize=7)
        panel.set_title(title, fontsize=7, pad=12)
        panel.spines["left"].set_visible(False)
    for index, panel in enumerate(axes.flat):
        panel.text(-0.01, 1.035, chr(ord("a") + index), transform=panel.transAxes,
                   fontsize=8, weight="bold", va="bottom")
        if index % 4 == 0:
            for tick, developer in zip(panel.get_yticklabels(), models.developer):
                tick.set_color(figlib.color(developer))
    handles = [Line2D([], [], color=figlib.color(developer), marker="o", linestyle="none", markersize=3,
                      label=developer) for developer in DEVELOPERS]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.037), ncol=7,
               frameon=False, handletextpad=0.35, columnspacing=1.1)
    fig.text(0.5, 0.02, "Dots, category means; horizontal lines, 95% intervals; dashed lines, reference values",
             ha="center", fontsize=7, color=figlib.PALETTE["benchmark"])
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "fig2_categories")
