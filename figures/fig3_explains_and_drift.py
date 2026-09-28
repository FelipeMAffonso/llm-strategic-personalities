from pathlib import Path

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

import figlib
from figlib import plt


DATA = Path(figlib.SUMMARY)
FACTORS = [("developer", "Developer"), ("size_tier", "Size tier"),
           ("release_years", "Release date"), ("reasoning", "Reasoning mode")]


def build():
    figlib.style()
    shares = pd.read_csv(DATA / "A2_variance_shares.csv").set_index("outcome")
    releases = pd.read_csv(DATA / "A7_release_dates.csv", parse_dates=["release_date"])
    cooperation = pd.read_csv(DATA / "A1_same_opponent.csv")
    names = pd.read_csv(DATA / "A4_category_index.csv").drop_duplicates("model_key").set_index("model_key").display
    models = releases.merge(cooperation, on="model_key", validate="one_to_one", how="outer", indicator=True)
    models["display_name"] = models.model_key.map(names)
    if not models._merge.eq("both").all() or models.release_date.isna().any():
        raise ValueError("Every model requires a release date and same-opponent estimate.")
    fig = plt.figure(figsize=(5.0, 9.0))
    variance = fig.add_axes([0.25, 0.775, 0.69, 0.182])
    dark = figlib.PALETTE["ink"]
    light = "#a9a49b"
    background = "#eeeae3"
    positions = np.arange(len(FACTORS))
    joint = shares.loc[["pd_cooperation", "trust_index"], "joint_r2"]
    for outcome, offset in [("pd_cooperation", -0.17), ("trust_index", 0.17)]:
        if pd.notna(joint[outcome]):
            variance.barh(positions + offset, joint[outcome], height=0.29, color=background, zorder=0)
    for position, (factor, label) in enumerate(FACTORS):
        for outcome, offset, shade in [("pd_cooperation", -0.17, dark), ("trust_index", 0.17, light)]:
            value = shares.loc[outcome, factor]
            if pd.isna(value):
                variance.text(0.012, position + offset, "Not estimated", va="center", fontsize=6, color=light)
            else:
                variance.barh(position + offset, value, height=0.25, color=shade)
                variance.text(value + 0.009, position + offset, f"{value:.3f}", va="center", fontsize=6, color=dark)
    variance.set_yticks(positions, [label for factor, label in FACTORS])
    variance.set_ylim(3.55, -0.55)
    variance.set_xlim(0, 0.64)
    variance.set_xticks([0, 0.2, 0.4, 0.6])
    variance.set_xlabel("Share of between-model variance", labelpad=4)
    variance.tick_params(axis="y", length=0, pad=6)
    variance.spines["left"].set_visible(False)
    fig.text(0.045, 0.97, "a", fontsize=8, weight="bold")
    fig.legend(handles=[Patch(facecolor=dark, label="Cooperation"), Patch(facecolor=light, label="Trust"),
                        Patch(facecolor=background, label="Joint fit")],
               loc="center", bbox_to_anchor=(0.52, 0.711), ncol=3, frameon=False,
               handlelength=1.2, columnspacing=1.0, handletextpad=0.4)
    joint_labels = [f"{label} {joint[outcome]:.3f}" if pd.notna(joint[outcome]) else f"{label} not estimated"
                    for outcome, label in [("pd_cooperation", "cooperation"), ("trust_index", "trust")]]
    fig.text(0.52, 0.688, "Separate-factor fits; joint shares: " + ", ".join(joint_labels), ha="center", fontsize=6,
             color=figlib.PALETTE["benchmark"])
    fig.text(0.045, 0.649, "b", fontsize=8, weight="bold")
    fig.text(0.94, 0.648, "Open circles, thinking mode", ha="right", fontsize=6,
             color=figlib.PALETTE["benchmark"])
    developers = ["Anthropic", "OpenAI", "Google"]
    bounds = [(0.479, 0.148), (0.273, 0.148), (0.067, 0.148)]
    start = pd.Timestamp("2024-05-01")
    end = pd.Timestamp("2026-09-01")
    ticks = pd.to_datetime(["2024-07-01", "2025-01-01", "2025-07-01", "2026-01-01", "2026-07-01"])
    for developer, (bottom, height) in zip(developers, bounds):
        axis = fig.add_axes([0.17, bottom, 0.77, height])
        subset = models.loc[models.developer.eq(developer)].sort_values("release_date", kind="stable")
        shade = figlib.color(developer)
        for product_index, (product_line, lineage) in enumerate(subset.groupby("product_line", sort=False)):
            centers = lineage.groupby("release_date", sort=True).same_opponent_rate.mean()
            axis.plot(mdates.date2num(centers.index), centers.to_numpy(), color=shade,
                      linewidth=0.9, linestyle=["-", "--", ":"][product_index % 3], alpha=0.7, zorder=1)
        for _, row in subset.iterrows():
            axis.plot(mdates.date2num(row.release_date), row.same_opponent_rate, "o",
                      markersize=5.5 if row.reasoning_mode == "yes" else 2.8,
                      markerfacecolor="none" if row.reasoning_mode == "yes" else shade,
                      markeredgecolor=shade, markeredgewidth=0.8, zorder=3)
        axis.set_xlim(mdates.date2num(start), mdates.date2num(end))
        axis.set_ylim(-8, 106)
        axis.set_yticks([0, 40, 80])
        axis.set_xticks(mdates.date2num(ticks))
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        axis.tick_params(axis="x", labelsize=6)
        axis.set_title(developer, loc="left", fontsize=7, pad=6, color=shade)
        if developer == "OpenAI":
            axis.set_ylabel("Cooperation, same opponents (%)", labelpad=6)
        if developer == "Google":
            axis.set_xlabel("Release date", labelpad=4)
        labels = [(mdates.date2num(row.release_date), row.same_opponent_rate,
                   row.display_name.replace(" (Thinking)", "\n(Thinking)"), shade)
                  for _, row in subset.iterrows()]
        figlib.label_points(axis, labels)
    fig.text(0.52, 0.008, "Lines join product-line date means; dots show individual models", ha="center", fontsize=6,
             color=figlib.PALETTE["benchmark"])
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "fig3_explains_and_drift")
