"""Supplementary Fig. 8: frequency of six strategy terms in each model's reasoning text.

Reads the lexical features (lex_*) of summary_data/reasoning_text_clustering/behavioral_signatures.csv and writes
figures/out/figS8_lexical_features.pdf and .png.

    python figures/figS8_lexical_features.py
"""
import numpy as np

from compact_style import CLUSTERING, DOUBLE, RC, _c, _llm, _s, _save, _sort, plt, read_csv


def build():
    """Horizontal bar chart of strategy-relevant term frequencies,
    one sub-panel per term.
    """
    print("Supplementary Fig. 8, lexical features")

    sigs = read_csv(CLUSTERING / "behavioral_signatures.csv")
    if not sigs:
        print("       (no data)")
        return

    terms = {
        "lex_cooperation": "cooperate",
        "lex_defection":   "defect",
        "lex_fairness":    "fairness",
        "lex_trust":       "trust",
        "lex_equilibrium": "equilibrium",
        "lex_exploit":     "exploit",
    }

    md = {}
    for item in sigs:
        k = item.get("model_key", "")
        if not _llm(k):
            continue
        feats = {lab: item.get(lk, 0) for lk, lab in terms.items()
                 if lk in item}
        if feats:
            md[k] = feats

    if not md:
        print("       (no data)")
        return

    # Keep terms with at least some nonzero values
    active = [t for t in terms.values()
              if any(md[k].get(t, 0) > 0 for k in md)]
    if not active:
        print("       (no data)")
        return

    sk = _sort(list(md.keys()))
    nm = len(sk)
    nt = len(active)

    with plt.rc_context(RC):
        fig, axes = plt.subplots(1, nt, figsize=(DOUBLE, 0.19 * nm + 0.8),
                                 sharey=False)
        if nt == 1:
            axes = [axes]

        for j, term in enumerate(active):
            ax = axes[j]
            vs = [md[k].get(term, 0) for k in sk]
            cs = [_c(k) for k in sk]
            ax.barh(range(nm), vs, color=cs, height=0.72,
                    edgecolor="white", linewidth=0.2)
            ax.set_title(f'"{term}"', fontsize=6, style="italic")

            if j == 0:
                ax.set_yticks(range(nm))
                ax.set_yticklabels([_s(k) for k in sk], fontsize=4.5)
                for i, k in enumerate(sk):
                    ax.get_yticklabels()[i].set_color(_c(k))
            else:
                ax.set_yticks([])
            ax.invert_yaxis()

        fig.supxlabel("Frequency per 1 000 words", fontsize=6, y=0.01)
        fig.subplots_adjust(left=0.18, right=0.98, wspace=0.15)
        _save(fig, "figS8_lexical_features")


if __name__ == "__main__":
    build()
