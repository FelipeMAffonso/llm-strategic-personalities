"""Supplementary Fig. 12: developer clustering of the reasoning text. Panel a, UMAP projection of the embedded
reasoning texts with a density contour per developer and each model's centroid; panel b, each model's silhouette
score with developer as the label.

Reads summary_data/reasoning_text_clustering/trace_umap.csv, centroid_umap.csv and hodoscope_summary.json, and writes
figures/out/figS12_developer_clustering.pdf and .png.

    python figures/figS12_developer_clustering.py
"""
import numpy as np
import matplotlib.colors as mcolors
from scipy.stats import gaussian_kde

from compact_style import C, CLUSTERING, DOUBLE, PROV_LABEL, PROV_ORDER, RC, _c, _lab, _llm, _prov, _s, _save, _sort, plt, read_clustering_summary, read_csv


def build():
    """Panel a: UMAP embedding with per-provider KDE density contours and
    centroid markers.  Panel b: per-model silhouette scores (horizontal bars).
    """
    print("Supplementary Fig. 12, developer clustering")

    hodo = {"summary": read_clustering_summary(),
            "centroid_umap": read_csv(CLUSTERING / "centroid_umap.csv")}
    traces = read_csv(CLUSTERING / "trace_umap.csv")

    with plt.rc_context(RC):
        fig, (ax1, ax2) = plt.subplots(
            1, 2, figsize=(DOUBLE, 3.2),
            gridspec_kw={"width_ratios": [1.4, 1]})

        # ── a: UMAP with density ──
        _lab(ax1, "a")

        centroids = hodo["centroid_umap"]
        prov_pts = {}  # provider -> list of (x, y) from centroids

        # KDE density contours from the individual reasoning texts
        if traces:
            prov_trace_pts = {}
            for t in traces:
                mk = t.get("model_key", "")
                p = _prov(mk) if mk else t.get("provider", "").lower()
                prov_trace_pts.setdefault(p, {"x": [], "y": []})
                prov_trace_pts[p]["x"].append(t["x"])
                prov_trace_pts[p]["y"].append(t["y"])

            # Use LLM-only traces for the density bounds (exclude strategy outliers)
            llm_tx = [t["x"] for t in traces if _llm(t.get("model_key", ""))]
            llm_ty = [t["y"] for t in traces if _llm(t.get("model_key", ""))]
            if llm_tx:
                pad = 0.15
                xmin = np.percentile(llm_tx, 1) - pad
                xmax = np.percentile(llm_tx, 99) + pad
                ymin = np.percentile(llm_ty, 1) - pad
                ymax = np.percentile(llm_ty, 99) + pad
            else:
                all_x = [t["x"] for t in traces]
                all_y = [t["y"] for t in traces]
                pad = 0.5
                xmin, xmax = min(all_x) - pad, max(all_x) + pad
                ymin, ymax = min(all_y) - pad, max(all_y) + pad
            xx, yy = np.mgrid[xmin:xmax:150j, ymin:ymax:150j]
            positions = np.vstack([xx.ravel(), yy.ravel()])

            for p in PROV_ORDER:
                if p not in prov_trace_pts or len(prov_trace_pts[p]["x"]) < 20:
                    continue
                col = C[p]
                rgb = mcolors.to_rgb(col)
                vals = np.vstack([prov_trace_pts[p]["x"],
                                  prov_trace_pts[p]["y"]])
                try:
                    kde = gaussian_kde(vals, bw_method=0.35)
                    zz = kde(positions).reshape(xx.shape)
                    zz_norm = zz / zz.max() if zz.max() > 0 else zz
                    cmap = mcolors.LinearSegmentedColormap.from_list(
                        f"kde6_{p}",
                        [(rgb[0], rgb[1], rgb[2], 0.0),
                         (rgb[0], rgb[1], rgb[2], 0.18)],
                        N=64)
                    ax1.contourf(xx, yy, zz_norm,
                                 levels=np.linspace(0.2, 1.0, 5),
                                 cmap=cmap, zorder=0)
                    ax1.contour(xx, yy, zz_norm,
                                levels=np.linspace(0.4, 0.9, 3),
                                colors=[col], linewidths=0.25,
                                alpha=0.3, zorder=0)
                except Exception:
                    pass

        for item in centroids:
            key = item["model_key"]
            x, y = item["x"], item["y"]
            p = _prov(key)

            if not _llm(key):
                ax1.plot(x, y, "D", color=C["strategy"], ms=3,
                         alpha=0.35, mew=0, zorder=1)
            else:
                col = C.get(p, C["strategy"])
                ax1.plot(x, y, "o", color=col, ms=5.5,
                         mec="white", mew=0.4, zorder=3)
                prov_pts.setdefault(p, []).append((x, y))

        # Zoom into LLM density region (exclude extreme strategy outliers)
        llm_cx = [item["x"] for item in centroids if _llm(item["model_key"])]
        llm_cy = [item["y"] for item in centroids if _llm(item["model_key"])]
        if llm_cx:
            margin = 0.18
            ax1.set_xlim(min(llm_cx) - margin, max(llm_cx) + margin)
            ax1.set_ylim(min(llm_cy) - margin, max(llm_cy) + margin)

        ax1.set_xlabel("UMAP 1")
        ax1.set_ylabel("UMAP 2")

        # Combined legend (providers + strategies)
        provs_present = [p for p in PROV_ORDER if p in prov_pts]
        hs = [ax1.plot([], [], "o", color=C[p], ms=3.5, ls="none",
                       label=PROV_LABEL[p])[0] for p in provs_present]
        hs.append(ax1.plot([], [], "D", color=C["strategy"], ms=3, ls="none",
                           alpha=0.5, label="Strategies")[0])
        ax1.legend(handles=hs, loc="lower left", fontsize=5, ncol=2)

        # ── b: Silhouette ──
        _lab(ax2, "b")

        sil = hodo["summary"]["provider_separation"]["per_model_silhouette"]
        llm_sil = {k: v for k, v in sil.items() if _llm(k)}
        sk = _sort(list(llm_sil.keys()))
        n = len(sk)

        vals   = [llm_sil[k] for k in sk]
        colors = [_c(k) for k in sk]

        ax2.barh(range(n), vals, color=colors, height=0.72,
                 edgecolor="white", linewidth=0.3, zorder=2)
        ax2.axvline(0, color="#444444", lw=0.4, zorder=1)

        ax2.set_yticks(range(n))
        ax2.set_yticklabels([_s(k) for k in sk], fontsize=5)
        ax2.set_xlabel("Silhouette score")
        ax2.invert_yaxis()

        for i, k in enumerate(sk):
            ax2.get_yticklabels()[i].set_color(_c(k))

        # Provider group separators
        prev = None
        for i, k in enumerate(sk):
            p = _prov(k)
            if prev is not None and p != prev:
                ax2.axhline(i - 0.5, color="#CCCCCC", lw=0.4)
            prev = p

        fig.tight_layout(w_pad=2.0)
        _save(fig, "figS12_developer_clustering")


if __name__ == "__main__":
    build()
