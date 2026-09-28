"""Check that the reasoning-text clustering labels every agent by its developer.

The lexical embedding (analysis/reasoning_text_clustering.py, get_provider) and the sentence-transformer check
(analysis/reasoning_text_robustness.py, PROVIDER_MAP) must use the same developer labels. The script stops (exit 1)
when:
  1. get_provider disagrees with the developer in analysis/common.py (MODELS) for any of the 25 models;
  2. a fixed strategy in summary_data/reasoning_text_clustering/hodoscope_summary.json is not labelled "strategy";
  3. the provider labels saved in hodoscope_summary.json differ from get_provider;
  4. the two embeddings group the 34 agents differently (the label names may differ, the groups may not).
It also runs a planted fault, a rule that misses "ministral" (the key of Ministral 14B does not contain "mistral"),
and stops if the checks do not catch it.

Run from the top of the repository: python analysis/check_developer_labels.py
"""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from common import MODELS  # noqa: E402
from reasoning_text_clustering import get_provider  # noqa: E402

SUMMARY = os.path.join(ROOT, "summary_data", "reasoning_text_clustering", "hodoscope_summary.json")
ST_SCRIPT = os.path.join(HERE, "reasoning_text_robustness.py")


def st_provider_map():
    tree = ast.parse(open(ST_SCRIPT, encoding="utf-8").read())
    return next(ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "PROVIDER_MAP")


def partition(labels):
    groups = {}
    for agent, label in labels.items():
        groups.setdefault(label, set()).add(agent)
    return {frozenset(g) for g in groups.values()}


def failures(provider_fn, summary):
    out = []
    for key, (_, developer, *_rest) in MODELS.items():
        if provider_fn(key) != developer.lower():
            out.append(f"{key}: {provider_fn(key)!r}, developer {developer}")
    agents = summary["models"]
    for agent in agents:
        if agent not in MODELS and provider_fn(agent) != "strategy":
            out.append(f"strategy {agent}: {provider_fn(agent)!r}")
    lexical = {a: provider_fn(a) for a in agents}
    st_map = st_provider_map()
    semantic = {a: st_map.get(a, "other") for a in agents}
    if partition(lexical) != partition(semantic):
        out.append("the lexical and sentence-transformer runs group the agents differently")
    return out


def rule_without_ministral(key):
    """The planted fault: the same rule without "ministral", and every unmatched key labelled "other"."""
    mk = key.lower()
    for tags, label in ((("claude",), "anthropic"), (("gpt", "o1-", "o3-", "o4-"), "openai"), (("gemini", "gemma"), "google"),
                        (("deepseek",), "deepseek"), (("llama",), "meta"), (("qwen",), "alibaba"), (("kimi",), "moonshot"),
                        (("mistral", "mixtral"), "mistral")):
        if any(t in mk for t in tags):
            return label
    return "other"


def main():
    summary = json.load(open(SUMMARY, encoding="utf-8"))
    bad = failures(get_provider, summary)
    saved = summary["provider_separation"]["provider_labels"]
    bad += [f"saved label {a}: {saved[a]!r}, code {get_provider(a)!r}" for a in saved if saved[a] != get_provider(a)]
    planted = failures(rule_without_ministral, summary)
    if not any(p.startswith("ministral-14b") for p in planted) or not any("group the agents differently" in p for p in planted):
        bad.append(f"the planted fault (a rule without \"ministral\") was not caught: {planted}")
    if bad:
        print("DEVELOPER LABEL CHECK FAILED:\n  " + "\n  ".join(bad))
        sys.exit(1)
    print(f"developer labels: {len(MODELS)} models and {len(summary['models']) - len(MODELS)} strategies labelled as expected; "
          f"saved labels match the code; the two embeddings group the {len(summary['models'])} agents identically; "
          f"planted fault caught ({len(planted)} failures)")


if __name__ == "__main__":
    main()
