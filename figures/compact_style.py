"""Style and helpers shared by Supplementary Figs. 4, 8 and 11.

These three figures use their own compact style (the Okabe-Ito developer colors below, short model names, tight
bounding boxes), which differs from figlib.py. Each figure is written to figures/out/ as PDF and PNG at 600 dpi.
"""
from __future__ import annotations

import csv
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "summary_data"
CLUSTERING = SUMMARY / "reasoning_text_clustering"
OUT = Path(__file__).resolve().parent / "out"

RC = {
    "font.family":          "Arial",
    "font.size":            7,
    "axes.labelsize":       7,
    "axes.titlesize":       8,
    "xtick.labelsize":      6,
    "ytick.labelsize":      6,
    "legend.fontsize":      6,
    "figure.dpi":           150,
    "savefig.dpi":          600,
    "savefig.bbox":         "tight",
    "savefig.pad_inches":   0.04,
    "pdf.fonttype":         42,
    "ps.fonttype":          42,
    "axes.linewidth":       0.5,
    "xtick.major.width":    0.4,
    "ytick.major.width":    0.4,
    "xtick.major.size":     2.5,
    "ytick.major.size":     2.5,
    "lines.linewidth":      0.8,
    "axes.spines.top":      False,
    "axes.spines.right":    False,
    "legend.frameon":       False,
    "legend.handlelength":  1.0,
    "legend.handletextpad": 0.4,
    "legend.columnspacing": 0.8,
    "legend.borderpad":     0.3,
    "legend.labelspacing":  0.25,
}

# Column widths (inches)
SINGLE = 3.5          # 89 mm
DOUBLE = 7.2          # 183 mm

# Okabe-Ito colorblind-safe palette, one color per developer
C = {
    "anthropic":  "#D97706",
    "openai":     "#10A37F",
    "google":     "#4285F4",
    "deepseek":   "#E69F00",
    "meta":       "#CC79A7",
    "mistral":    "#8B5CF6",
    "alibaba":    "#332288",
    "strategy":   "#BBBBBB",
    "agg":        "#333333",
}

PROV_ORDER = ["anthropic", "openai", "google", "deepseek",
              "meta", "mistral", "alibaba"]
PROV_LABEL = {p: p.capitalize() for p in PROV_ORDER}
PROV_LABEL["openai"] = "OpenAI"
PROV_LABEL["deepseek"] = "DeepSeek"

SHORT = {
    "claude-haiku-4.5":          "Haiku 4.5",
    "claude-haiku-4.5-thinking": "Haiku 4.5 T",
    "claude-sonnet-4.5":         "Sonnet 4.5",
    "claude-sonnet-4.6":         "Sonnet 4.6",
    "claude-opus-4.5":           "Opus 4.5",
    "claude-opus-4.6":           "Opus 4.6",
    "gpt-4o-mini":               "GPT-4o Mini",
    "gpt-4.1":                   "GPT-4.1",
    "gpt-4.1-mini":              "GPT-4.1 Mini",
    "gpt-4.1-nano":              "GPT-4.1 Nano",
    "gpt-5-mini":                "GPT-5 Mini",
    "gpt-5-nano":                "GPT-5 Nano",
    "gpt-5.3":                   "GPT-5.3",
    "gpt-5.4":                   "GPT-5.4",
    "gemini-2.0-flash":          "Gem 2.0 Flash",
    "gemini-2.5-flash":          "Gem 2.5 Flash",
    "gemini-2.5-flash-thinking": "Gem 2.5 Flash T",
    "gemini-3-flash":            "Gem 3 Flash",
    "gemini-3-pro":              "Gem 3 Pro",
    "gemini-3.1-pro":            "Gem 3.1 Pro",
    "deepseek-v3":               "DS V3",
    "deepseek-r1":               "DS R1",
    "llama-3.3-70b":             "LLaMA 70B",
    "ministral-14b":             "Ministral 14B",
    "qwen3.5-flash":             "Qwen 3.5",
}

def _prov(k):
    lo = k.lower()
    if "claude" in lo:                                    return "anthropic"
    if any(x in lo for x in ("gpt-", "o1-", "o3-")):     return "openai"
    if "gemini" in lo:                                    return "google"
    if "deepseek" in lo:                                  return "deepseek"
    if "llama" in lo:                                     return "meta"
    if "ministral" in lo:                                 return "mistral"
    if "qwen" in lo:                                      return "alibaba"
    return "strategy"

def _c(k):       return C.get(_prov(k), C["strategy"])
def _s(k):       return SHORT.get(k, k)
def _llm(k):     return _prov(k) != "strategy"

def _sort(keys, coop=None):
    """Sort by developer order, then cooperation rate descending."""
    def key_fn(k):
        p = _prov(k)
        pi = PROV_ORDER.index(p) if p in PROV_ORDER else 99
        r = -(coop[k]["mean"] if coop and k in coop else 0)
        return (pi, r)
    return sorted(keys, key=key_fn)

def _save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", format=ext)
    plt.close(fig)
    print(f"  + {name}")

def _prov_legend(ax, provs=None, marker="o", ms=3.5, **kwargs):
    if provs is None:
        provs = PROV_ORDER
    hs = [ax.plot([], [], marker, color=C[p], ms=ms, ls="none",
                  label=PROV_LABEL.get(p, p))[0] for p in provs]
    ax.legend(handles=hs, **kwargs)


def read_csv(path: Path) -> list[dict]:
    """Read a CSV into a list of dicts, converting numeric fields (integral values become int)."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            converted = {}
            for k, v in row.items():
                if v == "" or v is None:
                    converted[k] = None
                else:
                    try:
                        converted[k] = float(v)
                        if converted[k] == int(converted[k]):
                            converted[k] = int(converted[k])
                    except (ValueError, OverflowError):
                        converted[k] = v
            rows.append(converted)
    return rows
