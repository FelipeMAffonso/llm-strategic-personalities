"""Supplementary Fig. 16: the three pairs of models with and without a reasoning mode, compared on the eight
category measures (the mean over all of a model's trials in the category's games).

Reads summary_data/behavioral_profiles.csv and writes figures/out/figS16_thinking_comparison.pdf and .png.

    python figures/figS16_thinking_comparison.py
"""
import numpy as np

from compact_style import CAT_LABEL, DOUBLE, RC, SUMMARY, _c, _hide_spines, _lab, _save, plt, read_csv

# The measure of each category: the mean of this column over all of a model's trials in the category's games.
CATEGORY_MEASURES = {
    "cooperation": "cooperation_rate", "coordination": "coordination_rate", "fairness": "offer_ratio",
    "depth": "strategic_depth", "trust": "trust_index", "competition": "bid_ratio",
    "negotiation": "demand_ratio", "risk": "risk_taking_rate",
}


def category_means():
    """{model: {"radar": {category: {"value": mean}}}} from the trial-level data, rounded to four decimals."""
    trials = {}
    for row in read_csv(SUMMARY / "behavioral_profiles.csv"):
        trials.setdefault(row["model_key"], []).append(row)
    models = {}
    for model, rows in trials.items():
        by_cat = {}
        for t in rows:
            if t.get("game_category"):
                by_cat.setdefault(t["game_category"], []).append(t)
        radar = {}
        for cat, metric in CATEGORY_MEASURES.items():
            vals = [t[metric] for t in by_cat.get(cat, []) if t.get(metric) is not None]
            radar[cat] = {"value": round(sum(vals) / len(vals), 4) if vals else None}
        models[model] = {"radar": radar}
    return models


def build():
    """Paired comparison of thinking vs non-thinking models."""
    print("Supplementary Fig. 16, thinking comparison")

    models_j = category_means()

    # Thinking pairs
    pairs = [
        ("claude-haiku-4.5", "claude-haiku-4.5-thinking"),
        ("gemini-2.5-flash", "gemini-2.5-flash-thinking"),
        ("deepseek-v3",      "deepseek-r1"),
    ]
    pair_labels = [
        "Claude Haiku 4.5",
        "Gemini 2.5 Flash",
        "DeepSeek V3 / R1",
    ]

    # Dimensions to compare
    dims = ["cooperation", "coordination", "fairness", "depth",
            "trust", "competition", "negotiation", "risk"]
    dim_labels = [CAT_LABEL.get(d, d) for d in dims]

    with plt.rc_context(RC):
        fig, axes = plt.subplots(1, 3, figsize=(DOUBLE, 2.4), sharey=True)

        bar_width = 0.35
        x = np.arange(len(dims))

        for pidx, (base, think) in enumerate(pairs):
            ax = axes[pidx]

            base_vals = []
            think_vals = []
            for d in dims:
                bv = models_j.get(base, {}).get("radar", {}).get(d, {})
                tv = models_j.get(think, {}).get("radar", {}).get(d, {})
                base_vals.append(bv.get("value", 0) * 100)
                think_vals.append(tv.get("value", 0) * 100)

            bars1 = ax.barh(x + bar_width / 2, base_vals,
                            bar_width, color=_c(base), alpha=0.6,
                            edgecolor="white", linewidth=0.3,
                            label="Standard")
            bars2 = ax.barh(x - bar_width / 2, think_vals,
                            bar_width, color=_c(think), alpha=0.9,
                            edgecolor="white", linewidth=0.3,
                            label="Thinking")

            ax.set_title(pair_labels[pidx], fontsize=7, fontweight="bold")
            ax.set_xlim(0, 105)
            ax.set_yticks(x)
            if pidx == 0:
                ax.set_yticklabels(dim_labels, fontsize=5.5)
            ax.invert_yaxis()
            _hide_spines(ax)

            if pidx == 0:
                ax.legend(fontsize=5, loc="lower right")

            _lab(ax, chr(97 + pidx))

        axes[1].set_xlabel("Score (%)")
        fig.tight_layout(w_pad=0.8)
        _save(fig, "figS16_thinking_comparison")


if __name__ == "__main__":
    build()
