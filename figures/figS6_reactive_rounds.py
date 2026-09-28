import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import figlib
from figlib import plt
from fig2_categories import DATA, DEVELOPERS


def build():
    figlib.style()
    data = pd.read_csv(DATA / "A3_rounds_by_class.csv", index_col=["model_key", "opponent_class"])
    if data.index.duplicated().any():
        raise ValueError("Duplicate model and opponent-class rows.")
    reactive = data.xs("reactive", level="opponent_class")
    metadata = pd.read_csv(DATA / "A4_category_index.csv")
    models = metadata.loc[metadata.category.eq("coordination")].copy()
    models["developer_order"] = models.developer.map(DEVELOPERS.index)
    models = models.sort_values("developer_order", kind="stable")
    if len(models) != 25 or set(reactive.index) != set(models.model_key):
        raise ValueError("Expected the same 25 models as the main figures.")
    columns = [str(round_number) for round_number in range(1, 11)]
    values = reactive.loc[models.model_key, columns].to_numpy() * 100
    if not np.isfinite(values).all() or (values < 0).any() or (values > 100).any():
        raise ValueError("Reactive cooperation must contain finite percentages.")
    fig, axes = plt.subplots(5, 5, figsize=(7.2, 7.4), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.085, right=0.98, top=0.94, bottom=0.105, wspace=0.24, hspace=0.68)
    round_numbers = np.arange(1, 11)
    benchmark = np.r_[np.full(9, 100.0), 0.0]
    for index, (axis, (_, model)) in enumerate(zip(axes.flat, models.iterrows())):
        axis.plot(round_numbers, benchmark, color=figlib.PALETTE["benchmark"], linewidth=0.8,
                  linestyle=(0, (3, 2)), gid="benchmark")
        axis.plot(round_numbers, values[index], color=figlib.color(model.developer),
                  linewidth=1.1, marker="o", markersize=1.8, gid=f"model:{model.model_key}")
        axis.set_title(model.display.replace(" (Thinking)", "\n(Thinking)"), fontsize=6,
                       color=figlib.color(model.developer), pad=7)
        axis.set_xlim(0.7, 10.3)
        axis.set_ylim(-3, 103)
        axis.set_xticks(round_numbers)
        axis.set_yticks([0, 50, 100])
        axis.tick_params(axis="both", labelsize=6, length=2, pad=2)
        axis.tick_params(axis="x", labelbottom=True)
        axis.spines["left"].set_bounds(0, 100)
        axis.spines["bottom"].set_bounds(1, 10)
        if index % 5 == 0:
            axis.set_ylabel("Cooperation (%)", fontsize=7, labelpad=4)
        if index >= 20:
            axis.set_xlabel("Round", fontsize=7, labelpad=4)
    handles = [Line2D([], [], color=figlib.PALETTE["benchmark"], linewidth=0.8,
                      linestyle=(0, (3, 2)), label="Reactive benchmark")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.018), frameon=False)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS6_reactive_rounds")
