"""Shared figure code: palette, style, paths, point labelling and the text collision check every figure passes
before it is saved.

Usage in a figure script:
    import figlib
    from figlib import plt
    figlib.style()
    fig, ax = plt.subplots(...)
    ...
    figlib.save(fig, "fig2_categories")   # stops if any text collides or is clipped; writes PDF and PNG

The collision check: every visible text is rendered and its extent taken, and (1) any pair of texts whose extents
overlap by more than 15 percent of the smaller one, or (2) any text whose extent leaves the figure canvas, is a
violation. Tick labels of one axis are not checked against each other (matplotlib spaced them), but they are checked
against titles, legends and annotations. Violations are printed and save() stops, so a figure is never written with
overlapping or clipped text.
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SUMMARY = os.path.join(ROOT, "summary_data")
CLUSTERING = os.path.join(SUMMARY, "reasoning_text_clustering")
RAW = os.environ.get("RAW_DATA_DIR") or os.path.join(ROOT, "raw_data")
sys.path.insert(0, os.path.join(ROOT, "analysis"))
PALETTE = json.load(open(os.path.join(HERE, "palette.json"), encoding="utf-8"))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)


def style():
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": [PALETTE["font"], "Liberation Sans", "DejaVu Sans"],
        "font.size": PALETTE["font_size_pt"], "axes.titlesize": PALETTE["panel_label_pt"], "axes.labelsize": PALETTE["font_size_pt"],
        "xtick.labelsize": PALETTE["font_size_pt"], "ytick.labelsize": PALETTE["font_size_pt"], "legend.fontsize": PALETTE["font_size_pt"],
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": PALETTE["ink"], "axes.linewidth": 0.6,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.dpi": PALETTE["dpi"],
        "figure.dpi": 150,
    })


def color(developer):
    return PALETTE["developer"].get(developer, PALETTE["benchmark"])


def label_points(ax, points, fontsize=6, avoid_leader_crossings=False):
    from matplotlib.path import Path as LinePath
    from matplotlib.transforms import Bbox, offset_copy

    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    occupied = [box.expanded(1.025, 1.08) for text, box in _extents(fig)]
    radius = 4 * fig.dpi / 72
    point_boxes = []
    for horizontal, vertical, label, shade in points:
        pixel_x, pixel_y = ax.transData.transform((horizontal, vertical))
        point_boxes.append(Bbox.from_extents(pixel_x - radius, pixel_y - radius,
                                            pixel_x + radius, pixel_y + radius))
    boundary = ax.get_window_extent().padded(-3)
    offsets = [(0, 6, "center", "bottom"), (0, -6, "center", "top"),
               (7, 0, "left", "center"), (-7, 0, "right", "center")]
    for distance in range(13, 119, 7):
        offsets.extend([(0, distance, "center", "bottom"), (0, -distance, "center", "top"),
                        (distance, 0, "left", "center"), (-distance, 0, "right", "center")])
        for shift in (-distance, distance):
            offsets.extend([(shift, distance, "center", "bottom"),
                            (shift, -distance, "center", "top")])
    for horizontal, vertical, label, shade in points:
        if not label:
            continue
        text = ax.text(horizontal, vertical, label, fontsize=fontsize, color=shade, zorder=5,
                       bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.2})
        for offset_x, offset_y, align_x, align_y in offsets:
            text.set_transform(offset_copy(ax.transData, fig=fig, x=offset_x, y=offset_y, units="points"))
            text.set_ha(align_x)
            text.set_va(align_y)
            box = text.get_window_extent(renderer).padded(1.5)
            if not boundary.contains(box.x0, box.y0) or not boundary.contains(box.x1, box.y1):
                continue
            if any(box.overlaps(other) for other in occupied + point_boxes):
                continue
            if max(abs(offset_x), abs(offset_y)) > 7:
                source_x, source_y = ax.transData.transform((horizontal, vertical))
                target_x = min(max(source_x, box.x0), box.x1)
                target_y = min(max(source_y, box.y0), box.y1)
                connection = LinePath([(source_x, source_y), (target_x, target_y)])
                obstacles = [other for other in point_boxes if not other.contains(source_x, source_y)]
                if avoid_leader_crossings and any(connection.intersects_bbox(other, filled=False) for other in obstacles):
                    continue
                target = ax.transData.inverted().transform((target_x, target_y))
                ax.plot([horizontal, target[0]], [vertical, target[1]], color=shade,
                        linewidth=0.45, alpha=0.55, zorder=1)
            occupied.append(box)
            break
        else:
            raise ValueError(f"No collision-free label position: {label}")


def _extents(fig):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    items = []
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        try:
            bb = t.get_window_extent(renderer=r)
        except Exception:
            continue
        if bb.width <= 0 or bb.height <= 0:
            continue
        items.append((t, bb))
    return items


def _same_axis_ticklabels(a, b):
    ax_a, ax_b = a.axes, b.axes
    if ax_a is None or ax_b is None or ax_a is not ax_b:
        return False
    ticks = set(ax_a.get_xticklabels() + ax_a.get_yticklabels())
    return a in ticks and b in ticks


def check(fig, name):
    items = _extents(fig)
    W, H = fig.canvas.get_width_height()
    violations = []
    for t, bb in items:
        if bb.x0 < -1 or bb.y0 < -1 or bb.x1 > W + 1 or bb.y1 > H + 1:
            violations.append(f"clipped: '{t.get_text()[:40]}' extent {bb.x0:.0f},{bb.y0:.0f},{bb.x1:.0f},{bb.y1:.0f} vs canvas {W}x{H}")
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, ba = items[i]
            b, bbb = items[j]
            if _same_axis_ticklabels(a, b):
                continue
            ix = max(0, min(ba.x1, bbb.x1) - max(ba.x0, bbb.x0))
            iy = max(0, min(ba.y1, bbb.y1) - max(ba.y0, bbb.y0))
            inter = ix * iy
            if inter <= 0:
                continue
            smaller = min(ba.width * ba.height, bbb.width * bbb.height)
            if smaller > 0 and inter / smaller > 0.15:
                violations.append(f"overlap {inter/smaller:.0%}: '{a.get_text()[:30]}' with '{b.get_text()[:30]}'")
    return violations


def save(fig, name, strict=True):
    v = check(fig, name)
    if v:
        print(f"Text collision check failed for {name}:")
        for x in v:
            print("  ", x)
        if strict:
            raise SystemExit(2)
    fig.savefig(os.path.join(OUT, f"{name}.pdf"), bbox_inches=None)
    fig.savefig(os.path.join(OUT, f"{name}.png"), bbox_inches=None, dpi=PALETTE["dpi"])
    print(f"saved {name} ({len(v)} violations)")
    return v
