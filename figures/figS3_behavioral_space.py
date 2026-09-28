from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.lines import Line2D
from scipy.stats import gaussian_kde

import figlib
from figlib import plt

from common import DEVELOPER_ORDER, MODELS


def build():
    figlib.style()
    source = Path(figlib.CLUSTERING)
    traces = pd.read_csv(source / "trace_umap.csv")
    centroids = pd.read_csv(source / "centroid_umap.csv")
    assert len(traces) == 10000 and centroids.model_key.is_unique
    traces["developer"] = traces.model_key.map(lambda key: MODELS[key][1] if key in MODELS else "Strategy")
    fig = plt.figure(figsize=(7.2, 7.2))
    axis = fig.add_axes([0.105, 0.11, 0.86, 0.77])
    horizontal, vertical = np.mgrid[traces.x.min() - 0.5:traces.x.max() + 0.5:200j,
                                  traces.y.min() - 0.5:traces.y.max() + 0.5:200j]
    positions = np.vstack([horizontal.ravel(), vertical.ravel()])
    for developer in DEVELOPER_ORDER:
        subset = traces.loc[traces.developer.eq(developer)]
        shade = figlib.color(developer)
        if len(subset) >= 20:
            density = gaussian_kde(subset[["x", "y"]].to_numpy().T, bw_method=0.3)(positions).reshape(horizontal.shape)
            density /= density.max()
            red, green, blue = to_rgb(shade)
            cmap = LinearSegmentedColormap.from_list(developer, [(red, green, blue, 0), (red, green, blue, 0.25)])
            axis.contourf(horizontal, vertical, density, levels=np.linspace(0.15, 1, 6), cmap=cmap, zorder=0)
            axis.contour(horizontal, vertical, density, levels=np.linspace(0.3, 0.9, 4), colors=[shade], linewidths=0.3, alpha=0.35, zorder=0)
        axis.scatter(subset.x, subset.y, s=1, color=shade, alpha=0.12, linewidths=0, rasterized=True, zorder=1)
    strategy_traces = traces.loc[traces.developer.eq("Strategy")]
    axis.scatter(strategy_traces.x, strategy_traces.y, s=1, color=figlib.PALETTE["strategy"], alpha=0.12, linewidths=0, rasterized=True)
    points = []
    for row in centroids.loc[centroids.model_key.isin(MODELS)].itertuples():
        shade = figlib.color(MODELS[row.model_key][1])
        axis.scatter(row.x, row.y, s=22, color=shade, edgecolor="white", linewidth=0.35, zorder=4)
        points.append((row.x, row.y, "", shade))
    strategies = centroids.loc[~centroids.model_key.isin(MODELS)].copy()
    strategies["group_x"] = strategies.x.round(10)
    strategies["group_y"] = strategies.y.round(10)
    for coordinates, group in strategies.groupby(["group_x", "group_y"], sort=False):
        horizontal_value, vertical_value = group[["x", "y"]].mean()
        names = " / ".join(key.replace("_", " ").capitalize() for key in group.model_key)
        axis.scatter(horizontal_value, vertical_value, marker="D", s=24, color=figlib.PALETTE["strategy"], edgecolor="white", linewidth=0.35, zorder=4)
        points.append((horizontal_value, vertical_value, names, figlib.PALETTE["benchmark"]))
    axis.set(xlim=(-0.43, 1.02), ylim=(-0.62, 0.74), xlabel="UMAP 1", ylabel="UMAP 2")
    axis.set_xticks(np.arange(-0.4, 1.01, 0.2))
    axis.set_yticks(np.arange(-0.6, 0.71, 0.2))
    handles = [Line2D([], [], marker="o", linestyle="none", color=figlib.color(developer), label=developer, markersize=4) for developer in DEVELOPER_ORDER]
    handles.append(Line2D([], [], marker="D", linestyle="none", color=figlib.PALETTE["strategy"], label="Fixed strategies", markersize=4))
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.52, 0.974), ncol=4, frameon=False, fontsize=7, columnspacing=1.5)
    line_count = len(axis.lines)
    figlib.label_points(axis, points, fontsize=6, avoid_leader_crossings=True)
    for line in list(axis.lines)[line_count:]:
        line.remove()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in axis.texts:
        horizontal_value, vertical_value = text.get_position()
        source_pixel = axis.transData.transform((horizontal_value, vertical_value))
        box = text.get_window_extent(renderer).padded(1)
        target_pixel = [np.clip(source_pixel[0], box.x0, box.x1), np.clip(source_pixel[1], box.y0, box.y1)]
        target = axis.transData.inverted().transform(target_pixel)
        axis.plot([horizontal_value, target[0]], [vertical_value, target[1]], color=figlib.PALETTE["benchmark"], linewidth=0.5, zorder=3)
    print(f"Traces: {len(traces)}; model centroids: {len(MODELS)}; strategy names: {len(strategies)}; joined labels: {len(axis.texts)}")
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS3_behavioral_space")
