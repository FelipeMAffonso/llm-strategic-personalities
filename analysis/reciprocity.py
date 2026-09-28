"""Reciprocity: how often each model cooperates after the other player cooperated and after it defected.

Reads the raw trial files of the four prisoner's dilemma variants. For every round after the first, the model's
choice (the model in the first player position of the trial) is classed by the other player's choice in the previous
round, giving P(C|C), the probability of cooperating after the other player cooperated, and P(C|D), after it
defected, pooled over every opponent. Models with fewer than 20 rounds in both conditions are left out. Writes
summary_data/reciprocity.csv, the data of Supplementary Fig. 11 and Supplementary Table S9.

The raw trial files are read from raw_data/, or from the folder named by the environment variable RAW_DATA_DIR:

    python analysis/reciprocity.py
"""
import csv
import glob
import json
import os
from collections import defaultdict

from common import OUT, RAW


def main():
    files = sorted(glob.glob(os.path.join(RAW, "pd_*.json")), key=lambda path: os.path.basename(path).upper())
    if not files:
        raise SystemExit(f"no prisoner's dilemma files under {RAW}; unpack the raw corpus from Zenodo "
                         "(10.5281/zenodo.19896196) into raw_data/ or set RAW_DATA_DIR")
    counts = defaultdict(lambda: {"coop_after_coop": 0, "total_after_coop": 0,
                                  "coop_after_defect": 0, "total_after_defect": 0})
    for path in files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not data.get("game_id", "").startswith("pd_"):
            continue
        match_detail = data.get("match_detail", {})
        if not isinstance(match_detail, dict):
            continue
        rounds = match_detail.get("rounds", [])
        model = data.get("model_key", "")
        for i, rnd in enumerate(rounds):
            if i == 0:
                continue
            is_coop = rnd.get("parsed_choices", {}).get("0", "").lower() == "cooperate"
            previous_other = rounds[i - 1].get("parsed_choices", {}).get("1", "").lower()
            if previous_other == "cooperate":
                counts[model]["total_after_coop"] += 1
                counts[model]["coop_after_coop"] += is_coop
            elif previous_other == "defect":
                counts[model]["total_after_defect"] += 1
                counts[model]["coop_after_defect"] += is_coop
    rows = []
    for model, s in counts.items():
        if s["total_after_coop"] < 20 and s["total_after_defect"] < 20:
            continue
        rows.append({"model_key": model,
                     "p_coop_after_coop": round(s["coop_after_coop"] / max(1, s["total_after_coop"]), 4),
                     "p_coop_after_defect": round(s["coop_after_defect"] / max(1, s["total_after_defect"]), 4),
                     "n_after_coop": s["total_after_coop"], "n_after_defect": s["total_after_defect"]})
    with open(os.path.join(OUT, "reciprocity.csv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(files)} files, {len(rows)} models; wrote {os.path.join(OUT, 'reciprocity.csv')}")


if __name__ == "__main__":
    main()
