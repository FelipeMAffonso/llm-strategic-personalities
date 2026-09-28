"""
Robustness check of the reasoning-text clustering: the sentence-transformer embedding (all-MiniLM-L6-v2).

Repeats the developer-separation statistics of reasoning_text_clustering.py with a neural sentence embedding in place
of TF-IDF reduced by singular value decomposition. Everything except the embedding is the clustering's own code: the
same loader, the same subsample (_subsample_traces, 50,000 cap, random_state 42), the same centroids and cosine
distances, and the same developer labels (get_provider, through compute_provider_separation). The script stops
unless:
  1. analysis/check_developer_labels.py passes, and PROVIDER_MAP below agrees with get_provider for every model in
     the subsample;
  2. the subsample has the size and per-agent counts of the clustering, and the lexical statistics recomputed on it
     reproduce summary_data/reasoning_text_clustering/hodoscope_summary.json, which shows that both embeddings read
     the same 41,520 texts.
It then computes the ratio without Anthropic for both embeddings from the same distance matrices, and repeats the
ratios over the 25 models alone (models_only), the basis of the ratios the paper reports.

Writes summary_data/reasoning_text_clustering/robustness_st.json (the source of the sentence-transformer column of
Supplementary Table S10) and st_centroid_distances.csv (the 34 by 34 cosine distances between the sentence-transformer
centroids). Needs sentence-transformers (with torch) and scikit-learn; reads the raw trial files from raw_data/ or
from the folder named by RAW_DATA_DIR. It takes about an hour on a CPU. Run from the top of the repository, after
reasoning_text_clustering.py:

    python analysis/reasoning_text_robustness.py
"""
import os

# four threads, as in the released run
for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS",
             "RAYON_NUM_THREADS", "RAYON_RS_NUM_CPUS"):
    os.environ.setdefault(_var, "4")

import argparse
import datetime
import gc
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from reasoning_text_clustering import (  # noqa: E402
    _embed_traces_tfidf,
    _subsample_traces,
    compute_centroid_distances,
    compute_model_centroids,
    compute_provider_separation,
    get_provider,
    load_reasoning_traces,
)
import check_developer_labels  # noqa: E402

# The developer of every model key, as get_provider returns it. The labels used below come from get_provider;
# check_developer_labels.py reads this table, and the script stops if the two disagree.
PROVIDER_MAP = {
    'claude-haiku-4.5': 'anthropic', 'claude-haiku-4.5-thinking': 'anthropic',
    'claude-sonnet-4.5': 'anthropic', 'claude-sonnet-4.6': 'anthropic',
    'claude-opus-4.5': 'anthropic', 'claude-opus-4.6': 'anthropic',
    'gpt-4o-mini': 'openai', 'gpt-4.1': 'openai', 'gpt-4.1-mini': 'openai',
    'gpt-4.1-nano': 'openai', 'gpt-5-mini': 'openai', 'gpt-5-nano': 'openai',
    'gpt-5.3': 'openai', 'gpt-5.4': 'openai',
    'gemini-2.0-flash': 'google', 'gemini-2.5-flash': 'google',
    'gemini-2.5-flash-thinking': 'google', 'gemini-3-flash': 'google',
    'gemini-3-pro': 'google', 'gemini-3.1-pro': 'google',
    'deepseek-v3': 'deepseek', 'deepseek-r1': 'deepseek',
    'llama-3.3-70b': 'meta', 'ministral-14b': 'mistral', 'qwen3.5-flash': 'alibaba',
}

MAX_TRACES = 50_000          # the cap the clustering passes to _subsample_traces
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
UNSCORED_GAMES = ("colonel_blotto", "multi_issue")
TOLERANCE = 2e-4             # the released lexical values are rounded to four decimals
CLUSTERING = ROOT / "summary_data" / "reasoning_text_clustering"
SUMMARY = CLUSTERING / "hodoscope_summary.json"
OUT = CLUSTERING / "robustness_st.json"


def refuse(message):
    print(f"\nSENTENCE-TRANSFORMER CHECK STOPPED: {message}")
    sys.exit(1)


def check_labels(summary, agents):
    bad = check_developer_labels.failures(get_provider, summary)
    bad += [f"PROVIDER_MAP {k}: {v!r}, get_provider {get_provider(k)!r}" for k, v in PROVIDER_MAP.items() if get_provider(k) != v]
    bad += [f"{a}: a model with no PROVIDER_MAP entry" for a in agents if get_provider(a) != "strategy" and a not in PROVIDER_MAP]
    if bad:
        refuse("developer labels disagree:\n  " + "\n  ".join(bad))


def separation(embeddings, sub):
    """The clustering's statistics on any embedding: centroids, cosine distances, developer separation, and the
    same separation with Anthropic's models removed (the other 28 agents, the strategies' group included)."""
    dist = compute_centroid_distances(compute_model_centroids(sub, embeddings))
    full = compute_provider_separation(dist)
    anthropic = [m for m in dist.index if get_provider(m) == "anthropic"]
    if len(anthropic) != 6:
        refuse(f"expected six Anthropic models, found {anthropic}")
    rest = dist.drop(index=anthropic, columns=anthropic)
    without = compute_provider_separation(rest)
    # The same ratios over the 25 models alone, the fixed strategies left out (the basis of the ratios the paper
    # reports). The top-level ratios count the strategies as a group as well; their texts sit close together.
    models = [m for m in dist.index if get_provider(m) != "strategy"]
    only = compute_provider_separation(dist.loc[models, models])
    no_ant = [m for m in models if m not in anthropic]
    only_without = compute_provider_separation(dist.loc[no_ant, no_ant])
    models_only = {
        "n_agents": len(models),
        "overall_silhouette": only["silhouette_score"],
        "mean_within_provider_distance": only["mean_within_provider_distance"],
        "mean_between_provider_distance": only["mean_between_provider_distance"],
        "provider_separation_ratio": only["provider_separation_ratio"],
        "provider_separation_ratio_without_anthropic": only_without["provider_separation_ratio"],
    }
    sils = full["per_model_silhouette"]
    by_dev = {}
    for m, s in sils.items():
        by_dev.setdefault(get_provider(m), []).append(s)
    return {
        "overall_silhouette": full["silhouette_score"],
        "mean_within_provider_distance": full["mean_within_provider_distance"],
        "mean_between_provider_distance": full["mean_between_provider_distance"],
        "provider_separation_ratio": full["provider_separation_ratio"],
        "provider_separation_ratio_without_anthropic": without["provider_separation_ratio"],
        "overall_silhouette_without_anthropic": without["silhouette_score"],
        "n_agents_without_anthropic": int(len(rest)),
        "models_only": models_only,
        "anthropic_mean_silhouette": float(np.mean(by_dev["anthropic"])),
        "anthropic_silhouette_range": [min(by_dev["anthropic"]), max(by_dev["anthropic"])],
        "openai_mean_silhouette": float(np.mean(by_dev["openai"])),
        "openai_silhouette_range": [min(by_dev["openai"]), max(by_dev["openai"])],
        "mean_silhouette_by_label": {d: float(np.mean(v)) for d, v in sorted(by_dev.items())},
        "per_model_silhouette": sils,
        "provider_labels": full["provider_labels"],
        "_distances": dist,
    }


def corpus_counts(traces):
    """What the loader extracted: visible reply text (the reasoning field, never the thinking field) of at least
    30 characters after trimming, one text per seat per round, every trial, every game."""
    is_model = traces["model_key"].isin(PROVIDER_MAP)
    return {
        "definition": "visible reply text (round reasoning field, not the thinking field) of at least 30 characters "
                      "after trimming whitespace, one per seat per round, all trials, all 38 games; "
                      "analysis.reasoning_text_clustering.load_reasoning_traces",
        "n_texts": int(len(traces)),
        "n_texts_models": int(is_model.sum()),
        "n_texts_fixed_strategies": int((~is_model).sum()),
        "n_texts_by_matchup": {k: int(v) for k, v in sorted(Counter(traces["matchup_type"]).items())},
        "n_texts_unscored_games": {g: int((traces["game_id"] == g).sum()) for g in UNSCORED_GAMES},
        "n_agents": int(traces["model_key"].nunique()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu", help="cpu (default, four threads) or cuda")
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--out", type=Path, default=OUT, help="where to write the results (default: the released file)")
    args = ap.parse_args()

    summary = json.load(open(SUMMARY, encoding="utf-8"))
    released = summary["provider_separation"]

    print("[1/6] Loading reasoning texts (the clustering's loader)...")
    traces = load_reasoning_traces()
    corpus = corpus_counts(traces)
    print(f"  {corpus['n_texts']:,} texts: {corpus['n_texts_models']:,} from models, "
          f"{corpus['n_texts_fixed_strategies']:,} from fixed strategies")

    print(f"[2/6] Subsampling as the clustering does (_subsample_traces, cap {MAX_TRACES:,}, random_state 42)...")
    sub = _subsample_traces(traces, MAX_TRACES)
    del traces  # the full table is several gigabytes; only the subsample is needed from here
    gc.collect()
    counts = sub["model_key"].value_counts().to_dict()
    released_counts = {m: v["n_traces"] for m, v in summary["per_model_stats"].items()}
    if len(sub) != summary["n_traces"] or counts != released_counts:
        refuse(f"subsample {len(sub):,} texts differs from the clustering's {summary['n_traces']:,} "
               f"or its per-agent counts: {sorted(set(counts.items()) ^ set(released_counts.items()))}")
    check_labels(summary, counts)
    digest = hashlib.sha256("\x1e".join(f"{m}\x1f{t}" for m, t in zip(sub["model_key"], sub["reasoning_trace"].fillna("")))
                            .encode("utf-8")).hexdigest()
    print(f"  {len(sub):,} texts across {len(counts)} agents; sha256 {digest[:16]}; labels checked")

    print("[3/6] Recomputing the lexical statistics on this subsample (TF-IDF, 5,000 terms, SVD to 384)...")
    lexical = separation(_embed_traces_tfidf(sub), sub)
    drift = {"overall_silhouette": abs(lexical["overall_silhouette"] - released["silhouette_score"]),
             "provider_separation_ratio": abs(lexical["provider_separation_ratio"] - released["provider_separation_ratio"])}
    drift.update({m: abs(s - released["per_model_silhouette"][m]) for m, s in lexical["per_model_silhouette"].items()})
    worst = max(drift, key=drift.get)
    if drift[worst] > TOLERANCE or lexical["provider_labels"] != released["provider_labels"]:
        refuse(f"the lexical statistics on this subsample do not reproduce hodoscope_summary.json "
               f"(largest gap {drift[worst]:.2e} at {worst}); the two embeddings would not read the same texts")
    print(f"  reproduced the released lexical results (largest gap {drift[worst]:.1e}): silhouette "
          f"{lexical['overall_silhouette']}, ratio {lexical['provider_separation_ratio']}, "
          f"without Anthropic {lexical['provider_separation_ratio_without_anthropic']}")

    print(f"[4/6] Encoding with {EMBEDDING_MODEL}...")
    import torch
    torch.set_num_threads(4)
    import sentence_transformers
    from sentence_transformers import SentenceTransformer
    device = args.device
    model = SentenceTransformer(EMBEDDING_MODEL, device=device)
    texts = sub["reasoning_trace"].fillna("").tolist()
    # token lengths in chunks of 1,000 texts, which keeps the memory small
    n_tokens = np.concatenate([[len(ids) for ids in model.tokenizer(texts[i:i + 1000], add_special_tokens=True,
                                                                    truncation=False)["input_ids"]]
                               for i in range(0, len(texts), 1000)])
    embeddings = np.asarray(model.encode(texts, batch_size=args.batch_size, show_progress_bar=True,
                                         normalize_embeddings=True, convert_to_numpy=True))
    try:
        from huggingface_hub import snapshot_download
        revision = Path(snapshot_download(EMBEDDING_MODEL, local_files_only=True)).name
    except Exception:  # the revision is recorded for reference only
        revision = None
    print(f"  embeddings {embeddings.shape} on {device}; {int((n_tokens > model.max_seq_length).sum()):,} texts "
          f"longer than the model's {model.max_seq_length}-token window were truncated")

    print("[5/6] Developer separation on the sentence-transformer embedding...")
    semantic = separation(embeddings, sub)
    if semantic["provider_labels"] != lexical["provider_labels"]:
        refuse("the two embeddings were scored with different labels")
    print(f"  silhouette {semantic['overall_silhouette']}, ratio {semantic['provider_separation_ratio']}, "
          f"without Anthropic {semantic['provider_separation_ratio_without_anthropic']}, Anthropic mean "
          f"{semantic['anthropic_mean_silhouette']:.4f}, OpenAI mean {semantic['openai_mean_silhouette']:.4f}")

    print("[6/6] Saving...")
    lexical.pop("_distances")
    # the 34 by 34 cosine distances between the sentence-transformer centroids, so every statistic above can be
    # recomputed by hand, as centroid_distances.csv allows for the lexical embedding
    distances_path = args.out.with_name("st_centroid_distances.csv")
    semantic.pop("_distances").to_csv(distances_path)
    shared = {
        "n_texts_loaded": corpus["n_texts"],
        "n_traces_subsampled": int(len(sub)),
        "n_agents": int(len(counts)),
        "subsample": {"function": "analysis.reasoning_text_clustering._subsample_traces", "cap": MAX_TRACES,
                      "random_state": 42, "per_agent_counts": dict(sorted(counts.items())),
                      "sha256_of_texts_in_order": digest},
        "label_function": "analysis.reasoning_text_clustering.get_provider (fixed strategies labelled 'strategy')",
        "without_anthropic": "the six Anthropic models removed; the other 28 agents, the fixed strategies' group included",
        "basis": "top-level statistics use all 34 agents with the fixed strategies as one group, as hodoscope_summary.json "
                 "does; models_only repeats the ratios over the 25 models, the strategies left out",
    }
    result = {
        "run": {"date": datetime.date.today().isoformat(), "script": "analysis/reasoning_text_robustness.py",
                "device": device, "torch": torch.__version__, "sentence_transformers": sentence_transformers.__version__,
                "embedding_model_revision": revision},
        "corpus": corpus,
        "shared": shared,
        "tfidf_baseline": {
            "embedding_model": "TF-IDF (5000 features) + TruncatedSVD (384 dim)",
            "reproduces": "summary_data/reasoning_text_clustering/hodoscope_summary.json",
            "largest_gap_to_banked": float(drift[worst]),
            **{k: v for k, v in lexical.items() if k != "provider_labels"},
        },
        "sentence_transformer_robustness": {
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dim": int(embeddings.shape[1]),
            "max_seq_length": int(model.max_seq_length),
            "n_texts_truncated": int((n_tokens > model.max_seq_length).sum()),
            "n_traces_subsampled": int(len(sub)),
            "n_agents": int(len(counts)),
            **semantic,
        },
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2)
    print(f"  saved {args.out} and {distances_path}")
    print(f"\n{'':32s} {'lexical':>10s} {'sentence transformer':>22s}")
    for key in ("overall_silhouette", "provider_separation_ratio", "provider_separation_ratio_without_anthropic",
                "anthropic_mean_silhouette", "openai_mean_silhouette"):
        print(f"{key:44s} {lexical[key]:>10.4f} {semantic[key]:>10.4f}")
    for key in ("provider_separation_ratio", "provider_separation_ratio_without_anthropic"):
        print(f"{key + ', 25 models':44s} {lexical['models_only'][key]:>10.4f} {semantic['models_only'][key]:>10.4f}")


if __name__ == "__main__":
    main()
