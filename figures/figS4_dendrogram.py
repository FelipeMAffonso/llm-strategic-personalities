"""Supplementary Fig. 4: average-linkage clustering of the models' reasoning-text centroids.

Reads summary_data/reasoning_text_clustering/centroid_distances.csv (the cosine distances between the models'
embedding centroids) and writes figures/out/figS4_dendrogram.pdf and .png.

    python figures/figS4_dendrogram.py
"""
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform

from compact_style import CLUSTERING, DOUBLE, RC, _c, _s, _save, plt, read_csv


def build():
    """Average-linkage dendrogram from centroid distances, with
    developer-coloured leaf labels.
    """
    print("Supplementary Fig. 4, dendrogram")

    cd   = read_csv(CLUSTERING / "centroid_distances.csv")
    if not cd:
        print("       (no centroid_distances data)")
        return

    # Build symmetric distance matrix
    # Each item is a dict row: {"": model_key, model_key_1: dist, ...}
    row_keys = []
    for row in cd:
        rk = row.get("", row.get("model_key", ""))
        row_keys.append(rk)

    n = len(row_keys)
    dist_mat = np.zeros((n, n))
    for i, row in enumerate(cd):
        for j, k in enumerate(row_keys):
            dist_mat[i, j] = float(row.get(k, 0))

    # Symmetrise
    dist_mat = (dist_mat + dist_mat.T) / 2
    np.fill_diagonal(dist_mat, 0)

    # Convert to condensed form for linkage
    condensed = squareform(dist_mat, checks=False)
    Z = linkage(condensed, method="average")

    with plt.rc_context(RC):
        fig, ax = plt.subplots(figsize=(DOUBLE, 4.5))

        dend = dendrogram(Z, labels=row_keys, ax=ax,
                          leaf_rotation=90, leaf_font_size=5,
                          color_threshold=0, above_threshold_color="#999999")

        # Colour leaf labels by provider
        xlabels = ax.get_xticklabels()
        for lbl in xlabels:
            mk = lbl.get_text()
            lbl.set_text(_s(mk))
            lbl.set_color(_c(mk))
            lbl.set_fontsize(4.5)

        ax.set_xticklabels([lbl.get_text() for lbl in xlabels])
        # Recolor after text update
        for lbl in ax.get_xticklabels():
            # Match back to original key
            short_name = lbl.get_text()
            for k in row_keys:
                if _s(k) == short_name:
                    lbl.set_color(_c(k))
                    break

        ax.set_ylabel("Distance")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()
        _save(fig, "figS4_dendrogram")


if __name__ == "__main__":
    build()
