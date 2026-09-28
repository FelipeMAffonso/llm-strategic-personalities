import numpy as np
from matplotlib.lines import Line2D

import figlib
from figlib import plt
from figS9_crossplay_matrix import read_matrix, KEYS, MODELS, DEVELOPER_ORDER


def build():
    figlib.style()
    matrix, pair_counts = read_matrix()
    self_play = np.diag(matrix)
    cross_play = (matrix.sum(axis=1) - self_play) / 15
    # Axes fit the observed range with a margin so the sixteen points and their labels have room;
    # the identity line and the two annotations are placed relative to that range.
    top = min(100.0, 10.0 * np.ceil((max(self_play.max(), cross_play.max()) + 12.0) / 10.0))
    fig = plt.figure(figsize=(5, 5))
    axis = fig.add_axes([0.14, 0.13, 0.80, 0.76])
    axis.plot([0, top], [0, top], linestyle="--", color=figlib.PALETTE["benchmark"], linewidth=0.7, zorder=0)
    points = []
    for key, horizontal, vertical in zip(KEYS, self_play, cross_play):
        shade = figlib.color(MODELS[key][1])
        axis.scatter(horizontal, vertical, s=20, color=shade, edgecolor="white", linewidth=0.4, zorder=4)
        label = MODELS[key][0].replace(" (Thinking)", "\n(Thinking)")
        points.append((horizontal, vertical, label, shade))
        print(f"{MODELS[key][0]} | {horizontal:.6f} | {vertical:.6f}")
    # A margin below zero leaves room for the labels of the models near the origin; ticks stay at 0 to top.
    axis.set(xlim=(-0.09 * top, 1.04 * top), ylim=(-0.09 * top, 1.04 * top),
             xlabel="Self-play cooperation (%)", ylabel="Mean cross-play cooperation (%)")
    ticks = list(np.arange(0, top + 0.1, 10 if top <= 60 else 20))
    axis.set_xticks(ticks)
    axis.set_yticks(ticks)
    axis.text(0.04 * top, 0.92 * top, "More cooperative with others", fontsize=6, color=figlib.PALETTE["benchmark"])
    axis.text(0.56 * top, 0.06 * top, "Less cooperative with others", fontsize=6, color=figlib.PALETTE["benchmark"])
    handles = [Line2D([], [], marker="o", linestyle="none", color=figlib.color(developer), markersize=4, label=developer) for developer in DEVELOPER_ORDER]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.52, 0.997), ncol=4, fontsize=6, frameon=False,
               columnspacing=1, handletextpad=0.3)
    text_count = len(axis.texts)
    line_count = len(axis.lines)
    figlib.label_points(axis, sorted(points, key=lambda point: point[1]), fontsize=6, avoid_leader_crossings=True)
    for line in list(axis.lines)[line_count:]:
        line.remove()
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in list(axis.texts)[text_count:]:
        horizontal, vertical = text.get_position()
        source = axis.transData.transform((horizontal, vertical))
        box = text.get_window_extent(renderer).padded(1)
        target = axis.transData.inverted().transform([np.clip(source[0], box.x0, box.x1), np.clip(source[1], box.y0, box.y1)])
        axis.plot([horizontal, target[0]], [vertical, target[1]], color=text.get_color(), linewidth=0.5, zorder=2)
    return fig


if __name__ == "__main__":
    fig = build()
    figlib.save(fig, "figS15_crossplay_effects")
