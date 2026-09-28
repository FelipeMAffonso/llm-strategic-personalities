from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import figlib
from figlib import plt


DATA = Path(figlib.SUMMARY)
DEVELOPERS = list(figlib.PALETTE["developer"])


def build():
    figlib.style()
    data = pd.read_csv(DATA / "A6_mechanism.csv", index_col=0)
    categories = pd.read_csv(DATA / "A4_category_index.csv")
    models = categories.loc[categories.category.eq("coordination")].copy()
    models["developer_order"] = models.developer.map(DEVELOPERS.index)
    models = models.sort_values("developer_order", kind="stable")
    if set(models.model_key) != set(data.index) or data.index.duplicated().any():
        raise ValueError("Mechanism and category figures require identical model coverage.")
    data = data.loc[models.model_key]
    required = ["coop_vs_always_cooperate", "coop_vs_tit_for_tat", "coop_vs_always_defect",
                "preference_component", "belief_component"]
    if data[required].isna().any().any():
        raise ValueError("Missing mechanism estimates.")
    fig = plt.figure(figsize=(7.2, 7.1))
    opponents = fig.add_axes([0.25, 0.14, 0.285, 0.79])
    components = fig.add_axes([0.635, 0.23, 0.342, 0.64])
    positions = np.arange(len(data))
    for position, (_, row) in zip(positions, data.iterrows()):
        shade = figlib.color(row.developer)
        opponents.plot(row.coop_vs_tit_for_tat, position, "o", markerfacecolor="none",
                       markeredgecolor=shade, markersize=5.5, markeredgewidth=0.9, zorder=2)
        opponents.plot(row.coop_vs_always_cooperate, position, "o", color=shade, markersize=2.8, zorder=3)
        opponents.plot(row.coop_vs_always_defect, position, "s", color=shade, markersize=2.2, zorder=4)
    separators = np.flatnonzero(data.developer.to_numpy()[:-1] != data.developer.to_numpy()[1:]) + 0.5
    for separator in separators:
        opponents.axhline(separator, color=figlib.PALETTE["separator"], linewidth=0.55, zorder=0)
    for reference in [0, 0.9]:
        opponents.vlines(reference, -0.6, 24.6, color=figlib.PALETTE["benchmark"],
                         linewidth=0.7, linestyle=(0, (2, 3)), zorder=0)
    opponents.text(0.9, -1.25, "best response against tit-for-tat", fontsize=6,
                   ha="right", va="bottom", color=figlib.PALETTE["benchmark"])
    opponents.set_xlim(-0.045, 1.045)
    opponents.set_ylim(29, -2.7)
    opponents.set_yticks(positions, data.display)
    opponents.tick_params(axis="y", length=0, pad=5)
    opponents.set_xticks([0, 0.5, 0.9, 1], ["0", "0.5", "0.9", "1"])
    opponents.set_xlabel("Share of rounds cooperating", labelpad=5)
    opponents.spines["left"].set_visible(False)
    for label, developer in zip(opponents.get_yticklabels(), data.developer):
        label.set_color(figlib.color(developer))
    shade = figlib.PALETTE["benchmark"]
    opponents.legend(handles=[
        Line2D([], [], marker="o", linestyle="none", color=shade, markersize=3, label="Always-cooperate"),
        Line2D([], [], marker="o", linestyle="none", markerfacecolor="none", markeredgecolor=shade,
               markersize=5.5, label="Tit-for-tat"),
        Line2D([], [], marker="s", linestyle="none", color=shade, markersize=2.5, label="Always-defect"),
    ], loc="lower left", frameon=False, fontsize=6, borderaxespad=0.3,
        handletextpad=0.5, labelspacing=0.6)
    labels = []
    for _, row in data.iterrows():
        shade = figlib.color(row.developer)
        components.plot(row.preference_component, row.belief_component, "o", color=shade, markersize=3, zorder=3)
        labels.append((row.preference_component, row.belief_component,
                       row.display.replace(" (Thinking)", "\n(Thinking)"), shade))
    centroids = data.groupby("developer", sort=False)[["preference_component", "belief_component"]].mean()
    for developer, row in centroids.iterrows():
        shade = figlib.color(developer)
        components.plot(row.preference_component, row.belief_component, "D", markerfacecolor="none",
                        markeredgecolor=shade, markersize=7.5, markeredgewidth=1, zorder=4)
        labels.append((row.preference_component, row.belief_component, "", shade))
    components.set_xlim(-0.04, 1.22)
    components.set_ylim(0.26, 1.12)
    components.set_xticks([0, 0.25, 0.5, 0.75, 1])
    components.set_yticks([0.4, 0.6, 0.8, 1.0])
    components.set_xlabel("Preference component", labelpad=6)
    components.set_ylabel("Belief component", labelpad=5)
    components.legend(handles=[Line2D([], [], marker="D", linestyle="none", markerfacecolor="none",
                                     markeredgecolor=figlib.PALETTE["benchmark"], markersize=7.5,
                                     label="Developer centroid")],
                      loc="lower center", bbox_to_anchor=(0.5, -0.21), frameon=False, fontsize=6)
    fig.text(0.25, 0.964, "a", fontsize=8, weight="bold")
    fig.text(0.635, 0.964, "b", fontsize=8, weight="bold")
    fig.text(0.25, 0.94, "Opponent responses", fontsize=7)
    fig.text(0.635, 0.94, "Preference and belief components", fontsize=7)
    handles = [Line2D([], [], color=figlib.color(developer), marker="o", linestyle="none", markersize=3,
                      label=developer) for developer in DEVELOPERS]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.062), ncol=7,
               frameon=False, handletextpad=0.35, columnspacing=1.1)
    fig.text(0.5, 0.046, "Preference: cooperation against always-cooperate and dictator share", ha="center", fontsize=7)
    fig.text(0.5, 0.025, "Belief: cooperation against tit-for-tat and beauty-contest depth", ha="center", fontsize=7)
    figlib.label_points(components, sorted(labels, key=lambda point: (-point[0], -point[1])),
                        avoid_leader_crossings=True)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "fig4_mechanism")
