"""A3: play in the last rounds by opponent class, with the applicable benchmark.

Reads the raw trial files of the four prisoner's dilemma variants (ten rounds each), finds the model's own choice in
each round, and reports round-by-round cooperation per model per opponent class:

  fixed_defect      always-defect: the best response is to defect every round (benchmark 0 in every round)
  fixed_cooperate   always-cooperate: the best response is to defect every round (benchmark 0)
  reactive          tit-for-tat, grim trigger, hard tit-for-tat, mirror and suspicious tit-for-tat: with a known
                    last round the best response cooperates in rounds 1 to 9 and defects in round 10 (benchmark 1,
                    then 0)
  reactive_lenient  tit-for-two-tats, Pavlov, false defector, defect once, noise 10 and noise 20: defect in round
                    10; before it, an earlier defection can go unpunished
  self_play         the model against itself: the subgame-perfect prediction is defection throughout
  cross_play        another model: the same prediction

The types are then stated in these terms: sustained cooperators keep cooperating in round 10 against reactive
opponents (they forgo a sure gain); horizon-conditioned models defect only in round 10 (the best response);
unconditional defectors defect throughout (they forgo the gains of rounds 1 to 9 against reactive opponents).
Writes summary_data/A3_rounds_by_class.csv, summary_data/A3_round10.csv and summary_data/A3_summary.json.

The raw trial files are read from raw_data/ (the corpus from Zenodo, 10.5281/zenodo.19896196), or from the folder
named by the environment variable RAW_DATA_DIR:

    python analysis/endgame_by_opponent.py
"""
import glob
import json
import os
import re
from collections import defaultdict

import numpy as np
import pandas as pd

from common import MODELS, ORDER, OUT, PD, RAW

# The benchmark "cooperate through round 9, defect in round 10" holds exactly for the copy-last-move family
# (tit-for-tat, grim trigger, hard tit-for-tat, mirror, suspicious tit-for-tat): any defection before round 10 is
# answered in the next round and costs more than it gains under the study's payoffs. For tit-for-two-tats, Pavlov,
# the noisy variants, false defector and defect-once, an earlier defection can go unpunished, so the exact best
# response differs; they form a second reactive class reported beside the first.
CLASSES = {
    "always_defect": "fixed_defect", "always_cooperate": "fixed_cooperate",
    "tit_for_tat": "reactive", "grim_trigger": "reactive", "hard_tft": "reactive", "mirror": "reactive", "suspicious_tft": "reactive",
    "pavlov": "reactive_lenient", "tit_for_two_tats": "reactive_lenient", "false_defector": "reactive_lenient", "defect_once": "reactive_lenient", "noise_10": "reactive_lenient", "noise_20": "reactive_lenient",
    "reverse_tft": "other", "anti_mirror": "other", "random": "other",
}
COOP_WORDS = {"cooperate", "c", "cooperation", "contribute"}
GAMES_SORTED = sorted(PD, key=len, reverse=True)


def model_of(fname):
    for g in GAMES_SORTED:
        if fname.startswith(g + "_"):
            rest = fname[len(g) + 1:]
            m = re.match(r"^(.+?)_vs_(.+?)_(baseline|[a-z_0-9]+?)_t(\d+)_[0-9a-f]{12}\.json$", rest)
            if m:
                return g, m.group(1), m.group(2)
    return None, None, None


def is_coop(choice):
    if choice is None:
        return None
    c = str(choice).strip().lower()
    return c in COOP_WORDS or c.startswith("cooperat")


def main():
    files = glob.glob(os.path.join(RAW, "*.json"))
    files = [f for f in files if os.path.basename(f).startswith("pd_")]
    if not files:
        raise SystemExit(f"no prisoner's dilemma files under {RAW}; unpack the raw corpus from Zenodo "
                         "(10.5281/zenodo.19896196) into raw_data/ or set RAW_DATA_DIR")
    rec = []  # model_key, opponent_class, opponent, round, coop
    skipped = 0
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            skipped += 1
            continue
        md = d.get("match_detail") or {}
        rounds = md.get("rounds") or d.get("rounds") or []
        players = md.get("players") or {"0": d.get("model_key"), "1": d.get("opponent")}
        if not rounds or d.get("game_id") not in PD:
            skipped += 1
            continue
        # every seat held by a model is an observation; the other seat is its opponent
        seats = []
        for seat in ("0", "1"):
            mk = players.get(seat)
            opp = players.get("1" if seat == "0" else "0")
            if mk in MODELS:
                seats.append((seat, mk, opp))
        for seat, mk, opp in seats:
            if opp in CLASSES:
                cls = CLASSES[opp]
            elif opp == mk:
                cls = "self_play"
            elif opp in MODELS:
                cls = "cross_play"
            else:
                cls = "other"
            for r in rounds:
                rn = r.get("round_num") or r.get("round")
                pc = (r.get("parsed_choices") or {}).get(seat)
                cv = is_coop(pc)
                if rn is None or cv is None:
                    continue
                rec.append((mk, cls, opp, int(rn), int(cv)))
    df = pd.DataFrame(rec, columns=["model_key", "opponent_class", "opponent", "round", "coop"])
    df = df[df["round"].between(1, 10)]
    # equal weight per opponent within a class, then mean
    per_opp = df.groupby(["model_key", "opponent_class", "opponent", "round"]).coop.mean().reset_index()
    by_class = per_opp.groupby(["model_key", "opponent_class", "round"]).coop.mean().unstack("round")
    by_class = by_class.reindex(columns=range(1, 11))
    by_class.to_csv(os.path.join(OUT, "A3_rounds_by_class.csv"))
    r10 = by_class[[9, 10]].copy()
    r10.columns = ["round9", "round10"]
    r10["drop_9_to_10"] = r10.round9 - r10.round10
    r10 = r10.reset_index()
    r10["display"] = r10.model_key.map(lambda k: MODELS[k][0])
    r10["developer"] = r10.model_key.map(lambda k: MODELS[k][1])
    r10.to_csv(os.path.join(OUT, "A3_round10.csv"), index=False)
    # types against reactive opponents
    react = r10[r10.opponent_class == "reactive"].set_index("model_key")
    early = by_class.xs("reactive", level=1)[list(range(1, 10))].mean(axis=1) if "reactive" in by_class.index.get_level_values(1) else pd.Series(dtype=float)
    types = {}
    for k in ORDER:
        if k not in react.index:
            continue
        r9, r10v = react.loc[k, "round9"], react.loc[k, "round10"]
        e = float(early.get(k, np.nan))
        if r10v >= 0.5:
            t = "sustained cooperator"
        elif r9 >= 0.25 and r10v < 0.10 and (r9 - r10v) >= 0.25:
            t = "horizon-conditioned"
        elif e < 0.20 and r10v < 0.20:
            # unconditional means low in every round, not only in the last two
            t = "unconditional defector"
        else:
            t = "intermediate"
        types[k] = {"display": MODELS[k][0], "developer": MODELS[k][1], "rounds1to9_reactive": round(e, 3), "round9_reactive": round(float(r9), 3), "round10_reactive": round(float(r10v), 3), "type": t,
                    "round10_fixed_cooperate": round(float(r10[(r10.model_key == k) & (r10.opponent_class == "fixed_cooperate")].round10.iloc[0]), 3) if ((r10.model_key == k) & (r10.opponent_class == "fixed_cooperate")).any() else None}
    summary = {"n_files": len(files), "n_skipped": skipped, "n_round_observations": int(len(df)),
               "classes": sorted(df.opponent_class.unique().tolist()),
               "benchmarks": {"fixed_defect": "defect every round", "fixed_cooperate": "defect every round", "reactive": "cooperate rounds 1 to 9, defect round 10 (copy-last-move family: tit-for-tat, grim trigger, hard tit-for-tat, mirror, suspicious tit-for-tat)", "reactive_lenient": "defect in round 10; before it, cooperation is not always the exact best response because a defection can go unpunished (tit-for-two-tats, Pavlov, noise 10 and 20, false defector, defect once)", "self_play": "defect throughout (subgame perfect)", "cross_play": "defect throughout (subgame perfect)"},
               "type_rule": "types use the copy-last-move reactive class: sustained = round 10 at or above 50 percent; horizon-conditioned = round 9 at or above 25 percent, round 10 below 10 percent, drop at least 25 points; unconditional = mean of rounds 1 to 9 below 20 percent and round 10 below 20 percent; the rest intermediate",
               "types_vs_reactive": types,
               "type_counts": pd.Series([v["type"] for v in types.values()]).value_counts().to_dict()}
    with open(os.path.join(OUT, "A3_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "types_vs_reactive"}, indent=1))
    print(pd.DataFrame(types).T.to_string())


if __name__ == "__main__":
    main()
