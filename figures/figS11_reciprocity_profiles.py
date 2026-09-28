"""Supplementary Fig. 11: each model's probability of cooperating after the other player cooperated, P(C|C),
against its probability of cooperating after the other player defected, P(C|D), in the prisoner's dilemma.

Reads summary_data/reciprocity.csv (written by analysis/reciprocity.py) and writes
figures/out/figS11_reciprocity_profiles.pdf and .png.

    python figures/figS11_reciprocity_profiles.py
"""
import numpy as np

from compact_style import SINGLE, SUMMARY, RC, _c, _prov_legend, _s, _save, plt, read_csv


def build():
    """P(C|C) vs P(C|D) scatter with shaded quadrant regions
    and selectively labelled extreme models.
    """
    print("Supplementary Fig. 11, reciprocity profiles")

    recip = {row["model_key"]: row for row in read_csv(SUMMARY / "reciprocity.csv")}

    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(SINGLE, 3.5))

        xs, ys, ks = [], [], []
        for k, d in recip.items():
            x = d["p_coop_after_coop"] * 100
            y = d["p_coop_after_defect"] * 100
            xs.append(x); ys.append(y); ks.append(k)

        y_max = max(ys) + 6 if ys else 35

        # Quadrant shading
        ax.fill_between([55, 102], -3, 15, color="#E8F5E9", alpha=0.30, zorder=0)
        ax.fill_between([-3, 22],  -3, 15, color="#FFEBEE", alpha=0.30, zorder=0)
        ax.fill_between([-3, 22],  15, y_max, color="#FFF8E1", alpha=0.30, zorder=0)

        # Quadrant labels (positioned to avoid data points)
        ax.text(98, 14, "Strict\nreciprocators", ha="right", va="top",
                fontsize=5.5, color="#2E7D32", style="italic")
        ax.text(3, -2, "Unconditional defectors", ha="left", va="top",
                fontsize=5.5, color="#C62828", style="italic")
        ax.text(3, y_max - 1, "Anti-\nreciprocators", ha="left", va="top",
                fontsize=5.5, color="#E65100", style="italic")

        # Diagonal reference
        ax.plot([-5, 105], [-5, 105], ":", color="#E0E0E0", lw=0.4, zorder=0)

        # All dots
        for i in range(len(xs)):
            ax.plot(xs[i], ys[i], "o", color=_c(ks[i]), ms=5,
                    mec="white", mew=0.3, zorder=3)

        # Label only the single most extreme model per region
        labels_to_place = {}

        # Highest P(C|C): top strict reciprocator
        by_x = sorted(range(len(xs)), key=lambda i: xs[i], reverse=True)
        labels_to_place[by_x[0]] = (-5, -8, "right")

        # Lowest P(C|C): most extreme unconditional defector
        by_x_lo = sorted(range(len(xs)), key=lambda i: xs[i])
        labels_to_place[by_x_lo[0]] = (4, 5, "left")

        # Highest P(C|D): top anti-reciprocator
        by_y = sorted(range(len(ys)), key=lambda i: ys[i], reverse=True)
        labels_to_place[by_y[0]] = (4, 3, "left")

        # Highest endgame drop (P(C|C) high but P(C|D) low and far from diagonal)
        # = most responsive model
        gaps = [(i, xs[i] - ys[i]) for i in range(len(xs))]
        biggest_gap = sorted(gaps, key=lambda x: x[1], reverse=True)
        for idx, _ in biggest_gap[:1]:
            if idx not in labels_to_place:
                labels_to_place[idx] = (-5, 5, "right")

        for i, (dx, dy, ha) in labels_to_place.items():
            ax.annotate(_s(ks[i]), (xs[i], ys[i]),
                        xytext=(dx, dy), textcoords="offset points",
                        fontsize=4.5, color=_c(ks[i]), ha=ha, zorder=4)

        ax.set_xlabel("P(cooperate | opponent cooperated) (%)")
        ax.set_ylabel("P(cooperate | opponent defected) (%)")
        ax.set_xlim(-3, 102)
        ax.set_ylim(-3, y_max)

        _prov_legend(ax, loc="upper right", ncol=2)

        fig.tight_layout()
        _save(fig, "figS11_reciprocity_profiles")


if __name__ == "__main__":
    build()
