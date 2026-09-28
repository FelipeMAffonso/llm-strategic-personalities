"""The re-parsing check: every analysis repeated with the rule-based parser alone.

During data collection, the replies that the rule-based parsing steps could not read went to Claude Haiku 4.5 at
temperature 0, and its answer was stored (the "judge" in games/engine.py). This script asks what the paper's numbers
look like without that step.

1. Re-parse. Every model reply in the raw trial files is parsed again with the engine's own code (games/engine.py)
   and the judge switched off (GameEngine with judge_fn=None, which is what data_collection/runner.py does with
   ENABLE_JUDGE=0). A reply goes through the answer tag, the short-reply check and the pattern fallback, in the
   engine's order. When none of them finds a value, the engine would have stored a random option (choices) or 0
   (numbers); here that reply is dropped instead, and nothing is imputed. The 730 trials of 28 February, whose stored
   values came from an earlier first-number parser, get the same current parse as every other trial.

2. Trial-level measures. The measures are rebuilt exactly as analysis/behavioral_profiles.py builds them, reading the
   files in the order of their names in upper case. A trial with no dropped reply goes through the original measure
   functions, imported from that file. A trial with a dropped reply goes through copies that leave the dropped reply
   out: rounds that need it (and, for the measures that pair rounds or players, the pairs that need it) are skipped.
   Colonel Blotto and multi-issue negotiation are left out of the data, because their replies kept only one number.
   The payoff columns (player0_payoff, player1_payoff) keep the stored totals; none of the analyses reads them.

3. Rounds for the endgame analysis. analysis/endgame_by_opponent.py reads raw rounds, so the re-parsed prisoner's
   dilemma rounds are written as slim trial files (same file names, a dropped reply stored as null, which that script
   skips).

4. The analyses. Unmodified copies of same_opponent.py (A1), variance_decomposition.py (A2), category_tables.py (A4),
   mechanism_profiles.py (A6) and endgame_by_opponent.py (A3), with common.py and summary_data/A7_release_dates.csv,
   run in three copies of the analysis folder in a scratch folder:
     stored_full   the stored parse and every game. It must reproduce the released A1 to A6 results in summary_data/
                   cell for cell, which shows that the copies run the paper's analyses; the script stops if it does not.
     stored_excl   the stored parse without Colonel Blotto and multi-issue negotiation. The analyses already leave
                   those two games out of every result, so this run matches stored_full; it shows that leaving them
                   out of the data changes nothing before the re-parse is applied.
     judge_free    the re-parsed data, with the rule-based parser alone.

5. Results in summary_data/reparse_check/: the re-parsed trial-level data (behavioral_profiles.csv), the results of
   the five analyses on it (A1_*, A2_*, A3_*, A4_*, A6_*, named as in summary_data/), parse_summary.json (how many
   replies changed or were dropped, overall, in the four prisoner's dilemma variants and by game) and
   printed_numbers.csv (every number printed in the Abstract and Results of the paper beside its value in the three
   runs, and whether it changes at the precision printed).

Checks that stop the run when they fail:
  * the fixtures in selftest() (hand-computed measures for trials with a dropped reply, and the parse of four known
    replies);
  * with the stored values and every game kept, the rebuilt trial-level file equals summary_data/behavioral_profiles.csv
    byte for byte;
  * on every trial with nothing dropped, the drop-aware copies return exactly what the original functions return;
  * the stored_full copy reproduces the released A1, A2, A3, A4 and A6 results.

Run from the top of the repository after the main analyses (bash reproduce.sh --with-reparse-check runs it last):
    python analysis/reparse_check.py [--workers 4] [--scratch DIR]
    python analysis/reparse_check.py --selftest      (the fixtures only)
It takes about ten minutes with four worker processes. The raw trial files are read from raw_data/, or from the folder
named by RAW_DATA_DIR. Nothing in the repository is written except summary_data/reparse_check/; the three analysis
copies and a list of every changed or dropped reply (changed_or_dropped_decisions.csv) go to the scratch folder, by
default llm-games-reparse-check in the system's temporary folder.
"""
import argparse
import csv
import importlib.util
import json
import math
import os
import random as _random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from multiprocessing import Pool

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.environ.get("RAW_DATA_DIR") or os.path.join(ROOT, "raw_data")
SUMMARY = os.path.join(ROOT, "summary_data")
BANKED_PROFILES = os.path.join(SUMMARY, "behavioral_profiles.csv")
OUT = os.path.join(SUMMARY, "reparse_check")
EXCLUDED_GAMES = ("colonel_blotto", "multi_issue")
PD = ["pd_canonical", "pd_harsh", "pd_medium", "pd_mild"]
SCRIPTS = ["same_opponent.py", "variance_decomposition.py", "category_tables.py", "mechanism_profiles.py", "endgame_by_opponent.py"]
TREES = ("stored_full", "stored_excl", "judge_free")
BANKED_FILES = ["A1_same_opponent.csv", "A1_by_opponent.csv", "A1_summary.json", "A2_regression.csv", "A2_summary.json",
                "A2_variance_shares.csv", "A3_rounds_by_class.csv", "A3_round10.csv", "A3_summary.json",
                "A4_category_index.csv", "A4_category_summary.csv", "A4_competition_games.csv", "A4_summary.json",
                "A4_table1.csv", "A6_mechanism.csv", "A6_summary.json"]


# --------------------------------------------------------------------------------------------------------------
# The original measure functions, imported from the file that builds summary_data/behavioral_profiles.csv
# --------------------------------------------------------------------------------------------------------------

def load_original_extractors():
    spec = importlib.util.spec_from_file_location("behavioral_profiles", os.path.join(HERE, "behavioral_profiles.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.METRIC_EXTRACTORS


# --------------------------------------------------------------------------------------------------------------
# Drop-aware copies: a dropped reply is None in parsed_choices
# --------------------------------------------------------------------------------------------------------------

def _p(r, pid, default=None):
    return (r.get("parsed_choices") or {}).get(pid, default)


def _only_player0_present(rounds):
    """Keep the rounds whose player-0 reply was not dropped (a missing key is kept, as the originals read it)."""
    return [r for r in rounds if _p(r, "0", "absent") is not None]


def make_drop_aware(orig):
    """Copies of the measure functions that leave dropped replies out. Measures that read only the model's own choice
    in each round (depth, competition, negotiation, risk) call the original on the rounds that keep that choice; the
    others are rewritten so that a pair of rounds or players is used only when both replies are present."""

    def cooperation(rounds, cfg):
        coop = cfg["options"][0]
        n = len(rounds)
        if n == 0:
            return {}
        c0 = [None if _p(r, "0") is None else (1 if _p(r, "0") == coop else 0) for r in rounds]
        c1 = [None if _p(r, "1") is None else (1 if _p(r, "1") == coop else 0) for r in rounds]
        own = [c for c in c0 if c is not None]
        rate = np.mean(own) if own else np.nan
        pairs = [(a, b) for a, b in zip(c0, c1) if a is not None and b is not None]
        joint = np.mean([a and b for a, b in pairs]) if pairs else np.nan
        events = total = 0
        for i in range(1, n):
            if c1[i - 1] is None or c0[i] is None:
                continue
            if c1[i - 1] == 0:
                total += 1
                if c0[i] == 1:
                    events += 1
        if total == 0:
            forgiveness = retaliation = np.nan
        else:
            forgiveness = events / total
            retaliation = 1 - forgiveness
        return {"cooperation_rate": round(rate, 4), "joint_cooperation": round(joint, 4),
                "forgiveness_rate": round(forgiveness, 4), "retaliation_rate": round(retaliation, 4),
                "distance_to_equilibrium": round(rate, 4)}

    def coordination(rounds, cfg):
        n = len(rounds)
        if n == 0:
            return {}
        p0 = [_p(r, "0") for r in rounds]
        p1 = [_p(r, "1") for r in rounds]
        pairs = [(a, b) for a, b in zip(p0, p1) if a is not None and b is not None]
        coord = np.mean([a == b for a, b in pairs]) if pairs else np.nan
        preferred = cfg["options"][0]
        own = [c for c in p0 if c is not None]
        pref = np.mean([c == preferred for c in own]) if own else np.nan
        alternations = steps = 0
        for i in range(1, n):
            if p0[i] is None or p0[i - 1] is None:
                continue
            steps += 1
            if p0[i] != p0[i - 1]:
                alternations += 1
        return {"coordination_rate": round(coord, 4), "preferred_option_rate": round(pref, 4),
                "alternation_rate": round(alternations / max(1, steps), 4)}

    def fairness(rounds, cfg):
        if not rounds:
            return {}
        offers, rejections, responses = [], 0, 0
        for r in rounds:
            c0 = _p(r, "0", "0")
            if c0 is not None:
                try:
                    offers.append(float(c0))
                except (ValueError, TypeError):
                    pass
            c1 = _p(r, "1", "accept")
            if c1 is not None:
                responses += 1
                if "reject" in str(c1).lower():
                    rejections += 1
        if not offers:
            return {}
        endowment = cfg.get("endowment", 100)
        mean_offer = np.mean(offers)
        return {"offer_amount": round(mean_offer, 2), "offer_ratio": round(mean_offer / endowment, 4),
                "offer_std": round(np.std(offers), 2),
                "rejection_rate": round(rejections / responses, 4) if responses else np.nan}

    def trust(rounds, cfg):
        if not rounds:
            return {}
        sent, returned = [], []
        for r in rounds:
            s, t = _p(r, "0", "0"), _p(r, "1", "0")
            if s is not None:
                try:
                    sent.append(float(s))
                except (ValueError, TypeError):
                    pass
            if t is not None:
                try:
                    returned.append(float(t))
                except (ValueError, TypeError):
                    pass
        if not sent:
            return {}
        endowment = cfg.get("endowment", cfg.get("max_val", 10))
        index = min(1.0, max(0.0, np.mean(sent) / max(endowment, 1)))
        return {"amount_sent": round(np.mean(sent), 2), "trust_index": round(index, 4),
                "amount_returned": round(np.mean(returned), 2) if returned else None}

    def own_choice_only(category):
        return lambda rounds, cfg: orig[category](_only_player0_present(rounds), cfg)

    return {"cooperation": cooperation, "coordination": coordination, "fairness": fairness, "trust": trust,
            "depth": own_choice_only("depth"), "competition": own_choice_only("competition"),
            "negotiation": own_choice_only("negotiation"), "risk": own_choice_only("risk")}


def metrics_equal(a, b):
    if set(a) != set(b):
        return False
    for k in a:
        x, y = a[k], b[k]
        if x is None or y is None:
            if not (x is None and y is None):
                return False
            continue
        if isinstance(x, str) or isinstance(y, str):
            if x != y:
                return False
            continue
        if math.isnan(x) and math.isnan(y):
            continue
        if x != y:
            return False
    return True


# --------------------------------------------------------------------------------------------------------------
# The re-parse, with the engine's own parsing steps and the judge off
# --------------------------------------------------------------------------------------------------------------

class RandomRecorder:
    """Stands in for the engine module's `random`. It records any call to random.choice (the engine's last resort)
    so that the reply can be dropped; everything else goes to the real module."""

    def __init__(self):
        self.used = False

    def choice(self, seq):
        self.used = True
        return seq[0]

    def __getattr__(self, name):
        return getattr(_random, name)


def new_engine(E, cfg, label_map):
    eng = E.GameEngine(cfg, label_seed=0, judge_fn=None)
    eng.label_map = dict(label_map)
    eng.abstract_options = list(eng.label_map.keys())
    eng.reverse_map = {v: k for k, v in eng.label_map.items()}
    return eng


def reparse(E, rec, eng, cfg, pid, reply):
    """Parse one reply as the engine's round loop would with no judge. Returns (value, is_numeric); value is None
    when the engine would have fallen back to a random option or to 0."""
    gtype = cfg["type"]
    if gtype == "simultaneous":
        return _choice(E, rec, eng, reply, list(eng.canonical_options), None), False
    if gtype == "sequential":
        numeric_players = cfg.get("numeric_players")
        use_numeric = (pid in numeric_players) if numeric_players is not None else cfg.get("numeric_response", False)
        if use_numeric:
            return _numeric(eng, reply, cfg.get("min_val", 0), cfg.get("max_val", 100)), True
        options_map = cfg.get("player_options", {})
        valid = options_map[pid] if pid in options_map else eng.canonical_options
        override = valid if pid in options_map else None
        return _choice(E, rec, eng, reply, valid, override), False
    if gtype == "auction":
        return _numeric(eng, reply, cfg.get("min_bid", 0), cfg.get("max_bid", 100)), True
    if gtype == "allocation":
        return _numeric(eng, reply, 0, cfg.get("endowment", 10)), True
    raise ValueError(f"unknown game type {gtype}")


def _choice(E, rec, eng, reply, valid, override):
    rec.used = False
    parsed = eng._parse_choice_pipeline(reply, "", valid_options=override)
    if parsed not in valid:  # the engine's validation step in the round loop
        for canonical in valid:
            if re.search(rf'\b{re.escape(canonical)}\b', reply, re.IGNORECASE):
                parsed = canonical
                break
        else:
            parsed = E.random.choice(valid)
    return None if rec.used else parsed


def _numeric(eng, reply, lo, hi):
    # the parsing steps fall to their default 0 exactly when parse_numeric (answer tag, bare number, bold, "A:", last
    # number, any number) finds nothing, since its first two steps are the same as theirs
    if eng.parse_numeric(reply, min_val=lo, max_val=hi) is None:
        return None
    return float(eng._parse_numeric_pipeline(reply, "", lo, hi))


def same_value(stored, new, numeric):
    if numeric:
        try:
            return abs(float(stored) - new) < 1e-6
        except (TypeError, ValueError):
            return False
    return stored == new


# --------------------------------------------------------------------------------------------------------------
# Worker
# --------------------------------------------------------------------------------------------------------------

_W = {}


def _init_worker(slim_dirs):
    sys.path.insert(0, ROOT)
    import games.engine as E
    from games.definitions import GAME_REGISTRY
    rec = RandomRecorder()
    E.random = rec
    orig = load_original_extractors()
    _W.update(E=E, rec=rec, reg=GAME_REGISTRY, orig=orig, drop=make_drop_aware(orig), slim=slim_dirs)


def _row(trial, metrics):
    return {"model_key": trial.get("model_key"), "game_id": trial.get("game_id", "unknown"),
            "game_name": trial.get("game_name"), "game_category": trial.get("game_category", "unknown"),
            "condition": trial.get("condition"), "opponent": trial.get("opponent"),
            "matchup_type": trial.get("matchup_type"), "trial_num": trial.get("trial_num"),
            "num_rounds": trial.get("num_rounds"), "player0_payoff": trial.get("player0_total_payoff"),
            "player1_payoff": trial.get("player1_total_payoff"), "input_tokens": trial.get("input_tokens"),
            "output_tokens": trial.get("output_tokens"), "cost_usd": trial.get("cost_usd"), **metrics}


def _slim(trial, rounds):
    md = trial.get("match_detail", {})
    return {"game_id": trial.get("game_id"), "model_key": trial.get("model_key"), "opponent": trial.get("opponent"),
            "matchup_type": trial.get("matchup_type"),
            "match_detail": {"players": md.get("players"),
                             "rounds": [{"round_num": r.get("round_num"), "parsed_choices": r.get("parsed_choices")} for r in rounds]}}


def process_file(path):
    E, rec, reg, orig, drop = _W["E"], _W["rec"], _W["reg"], _W["orig"], _W["drop"]
    fn = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            trial = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None  # analysis/behavioral_profiles.py skips unreadable files the same way
    gid = trial.get("game_id", "unknown")
    cat = trial.get("game_category", "unknown")
    cfg = reg.get(gid, {})
    md = trial.get("match_detail", {})
    rounds = md.get("rounds", [])
    extractor = orig.get(cat)
    stored_metrics = extractor(rounds, cfg) if extractor else {}

    label_map = md.get("label_map") or trial.get("label_map")
    eng = new_engine(E, cfg, label_map)
    seats = ["0", "1"] if trial.get("matchup_type") in ("self_play", "cross_play") else ["0"]
    stats = Counter()
    changes = []
    new_rounds = []
    for r in rounds:
        pc = dict(r.get("parsed_choices") or {})
        for pid in seats:
            reply = (r.get("choices") or {}).get(pid)
            if reply is None:
                stats["no_reply_slots"] += 1
                continue
            value, numeric = reparse(E, rec, eng, cfg, int(pid), reply)
            stored = pc.get(pid)
            stats["replies"] += 1
            if value is None:
                stats["dropped"] += 1
                pc[pid] = None
                changes.append((fn, pid, r.get("round_num"), "dropped", str(stored), ""))
            elif same_value(stored, value, numeric):
                stats["unchanged"] += 1
            else:
                stats["changed"] += 1
                pc[pid] = str(value) if numeric else value
                changes.append((fn, pid, r.get("round_num"), "changed", str(stored), pc[pid]))
        nr = dict(r)
        nr["parsed_choices"] = pc
        new_rounds.append(nr)

    equivalence_failure = False
    if not extractor:
        jf_metrics = {}
    elif stats["dropped"]:
        jf_metrics = drop[cat](new_rounds, cfg)
    else:
        jf_metrics = extractor(new_rounds, cfg)
        # the drop-aware copy must return exactly the original's measures when nothing is dropped
        equivalence_failure = not metrics_equal(drop[cat](new_rounds, cfg), jf_metrics)

    if gid in PD:
        for tree, rr in (("stored_full", rounds), ("stored_excl", rounds), ("judge_free", new_rounds)):
            with open(os.path.join(_W["slim"][tree], fn), "w", encoding="utf-8") as f:
                json.dump(_slim(trial, rr), f)

    date = (trial.get("timestamp") or "")[:10]
    return {"file": fn, "game_id": gid, "category": cat, "date": date, "n_rounds": len(rounds),
            "stored_row": _row(trial, stored_metrics), "jf_row": _row(trial, jf_metrics), "stats": dict(stats),
            "changes": changes, "equivalence_failure": equivalence_failure}


# --------------------------------------------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------------------------------------------

def selftest():
    sys.path.insert(0, ROOT)
    import games.engine as E
    from games.definitions import GAME_REGISTRY
    orig = load_original_extractors()
    drop = make_drop_aware(orig)
    fails = []
    n_checks = [0]

    def check(name, got, want):
        n_checks[0] += 1
        ok = (isinstance(want, float) and got is not None and abs(got - want) < 1e-9) or got == want
        if not ok:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    pd_cfg = GAME_REGISTRY["pd_canonical"]
    C, D = pd_cfg["options"][0], pd_cfg["options"][1]
    rounds = [{"parsed_choices": {"0": C, "1": D}}, {"parsed_choices": {"0": None, "1": D}},
              {"parsed_choices": {"0": C, "1": D}}, {"parsed_choices": {"0": D, "1": C}}]
    m = drop["cooperation"](rounds, pd_cfg)
    check("cooperation rate over the three kept rounds", m["cooperation_rate"], 0.6667)
    check("joint cooperation over the three complete rounds", m["joint_cooperation"], 0.0)
    check("forgiveness over the two usable round pairs", m["forgiveness_rate"], 0.5)
    co = GAME_REGISTRY["bos_standard"]
    A_, B_ = co["options"][0], co["options"][1]
    m = drop["coordination"]([{"parsed_choices": {"0": A_, "1": A_}}, {"parsed_choices": {"0": None, "1": A_}},
                              {"parsed_choices": {"0": B_, "1": A_}}, {"parsed_choices": {"0": A_, "1": B_}}], co)
    check("coordination over the three complete rounds", m["coordination_rate"], 0.3333)
    check("preferred option over the three kept choices", m["preferred_option_rate"], 0.6667)
    check("alternation over the one usable pair of rounds", m["alternation_rate"], 1.0)
    full = [{"parsed_choices": {"0": C, "1": C}}, {"parsed_choices": {"0": D, "1": D}}, {"parsed_choices": {"0": C, "1": D}}]
    check("cooperation copy equals the original with nothing dropped", metrics_equal(drop["cooperation"](full, pd_cfg), orig["cooperation"](full, pd_cfg)), True)
    ult = GAME_REGISTRY["ultimatum"]
    m = drop["fairness"]([{"parsed_choices": {"0": "40.0", "1": "accept"}}, {"parsed_choices": {"0": None, "1": "reject"}},
                          {"parsed_choices": {"0": "60.0", "1": None}}], ult)
    check("offer ratio over the two kept offers", m["offer_ratio"], round(50.0 / ult.get("endowment", 100), 4))
    check("rejection rate over the two kept responses", m["rejection_rate"], 0.5)
    tb = GAME_REGISTRY["trust_berg"]
    m = drop["trust"]([{"parsed_choices": {"0": "5.0", "1": None}}, {"parsed_choices": {"0": None, "1": "6.0"}}], tb)
    check("amount sent over the kept send", m["amount_sent"], 5.0)
    check("amount returned over the kept return", m["amount_returned"], 6.0)
    ch = GAME_REGISTRY["chicken"]
    m = drop["risk"]([{"parsed_choices": {"0": ch["options"][1]}}, {"parsed_choices": {"0": None}}], ch)
    check("risk taking over the kept round", m["risk_taking_rate"], 1.0)

    rec = RandomRecorder()
    E.random = rec
    letters = list(E.randomise_labels(pd_cfg["options"], seed=3).items())
    lm = dict(letters)
    eng = new_engine(E, pd_cfg, lm)
    first_letter, first_canonical = letters[0]
    other_letters = set("".join(k for k, _ in letters))
    unsure = "".join(ch_ for ch_ in "I am unsure what to do here." if ch_.upper() not in other_letters)
    check("answer tag parses", reparse(E, rec, eng, pd_cfg, 0, f"<answer>Option {first_letter}</answer>")[0], first_canonical)
    check("no label anywhere is dropped", reparse(E, rec, eng, pd_cfg, 0, unsure)[0], None)
    fp = GAME_REGISTRY["auction_first_price"]
    eng2 = new_engine(E, fp, E.randomise_labels(fp["options"], seed=1) if fp.get("options") else {})
    check("numeric answer tag parses", reparse(E, rec, eng2, fp, 0, "I bid <answer>30</answer>")[0], 30.0)
    check("a reply with no number is dropped, not stored as 0", reparse(E, rec, eng2, fp, 0, "I will not bid this round.")[0], None)
    if fails:
        raise SystemExit("SELFTEST FAILED\n  " + "\n  ".join(fails))
    print(f"selftest: {n_checks[0]} fixtures pass")


# --------------------------------------------------------------------------------------------------------------
# The three analysis copies, their runs and the comparison
# --------------------------------------------------------------------------------------------------------------

def _flat(o, pre=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(_flat(v, f"{pre}.{k}" if pre else str(k)))
    elif isinstance(o, list):
        out[pre] = json.dumps(o)
    else:
        out[pre] = o
    return out


def _cells(path):
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            return {k: str(v) for k, v in _flat(json.load(f)).items()}
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    out = {}
    for i, row in df.iterrows():
        for c in df.columns:
            out[f"{i}|{c}"] = row[c]
    return out


def compare_outputs(dir_a, dir_b, files):
    diffs = {}
    for f in files:
        a, b = _cells(os.path.join(dir_a, f)), _cells(os.path.join(dir_b, f))
        d = [(k, a.get(k), b.get(k)) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
        if d:
            diffs[f] = d
    return diffs


def tree_paths(scratch, name):
    t = os.path.join(scratch, "trees", name)
    return {"root": t, "analysis": os.path.join(t, "analysis"), "out": os.path.join(t, "summary_data"),
            "raw": os.path.join(t, "raw_data"), "profiles": os.path.join(t, "summary_data", "behavioral_profiles.csv")}


def prepare_tree(scratch, name):
    p = tree_paths(scratch, name)
    if os.path.isdir(p["root"]):
        shutil.rmtree(p["root"])  # the scratch copy only, rebuilt on every run
    for d in (p["analysis"], p["out"], p["raw"]):
        os.makedirs(d, exist_ok=True)
    for s in ["common.py"] + SCRIPTS:
        shutil.copy2(os.path.join(HERE, s), p["analysis"])
    shutil.copy2(os.path.join(SUMMARY, "A7_release_dates.csv"), p["out"])
    return p


def refresh_tree(p):
    """For --analyses-only: copy the current analysis scripts and summary_data/A7_release_dates.csv into an existing
    copy, keeping its trial-level data and raw rounds, so that a changed script or release date reaches the results."""
    if not os.path.isfile(p["profiles"]):
        raise SystemExit(f"--analyses-only needs the copies of an earlier full run; missing {p['profiles']}")
    for s in ["common.py"] + SCRIPTS:
        shutil.copy2(os.path.join(HERE, s), p["analysis"])
    shutil.copy2(os.path.join(SUMMARY, "A7_release_dates.csv"), p["out"])
    return p


def run_tree(p):
    env = dict(os.environ, RAW_DATA_DIR=p["raw"])  # the copy reads its own re-parsed prisoner's dilemma rounds
    for s in SCRIPTS:
        res = subprocess.run([sys.executable, os.path.join(p["analysis"], s)], cwd=p["root"], env=env,
                             capture_output=True, text=True)
        with open(os.path.join(p["out"], s.replace(".py", ".log")), "w", encoding="utf-8") as f:
            f.write(res.stdout + "\n" + res.stderr)
        if res.returncode != 0:
            raise SystemExit(f"{s} failed in {p['root']}:\n{res.stderr[-3000:]}")


# --------------------------------------------------------------------------------------------------------------
# Every number printed in the Abstract and Results of the paper, and where each comes from
# --------------------------------------------------------------------------------------------------------------

DEV3 = ["Anthropic", "OpenAI", "Google"]


class Run:
    def __init__(self, out):
        j = lambda f: json.load(open(os.path.join(out, f), encoding="utf-8"))
        self.a1 = pd.read_csv(os.path.join(out, "A1_same_opponent.csv"), index_col=0)
        self.a1s, self.a2, self.a4, self.a6, self.a3 = j("A1_summary.json"), j("A2_summary.json"), j("A4_summary.json"), j("A6_summary.json"), j("A3_summary.json")
        self.a4g = pd.read_csv(os.path.join(out, "A4_competition_games.csv"), index_col="game")
        self.a4i = pd.read_csv(os.path.join(out, "A4_category_index.csv"))
        self.a3r = pd.read_csv(os.path.join(out, "A3_round10.csv"))


def number_specs():
    """(id, section, quantity, printed, getter). Getters return a float (or a string for names and lists)."""
    S = []
    add = lambda *a: S.append(a)
    DEVKEY = "C(developer, Treatment(reference='OpenAI'))[T.{}]"
    spec = importlib.util.spec_from_file_location("analysis_common", os.path.join(HERE, "common.py"))
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    name = lambda k: common.MODELS[k][0]
    # Abstract
    add("abs.coop.min", "Abstract", "Lowest same-opponent cooperation (percent)", "1.4", lambda R: R.a1s["min_rate"])
    add("abs.coop.max", "Abstract", "Highest same-opponent cooperation (percent)", "69.3", lambda R: R.a1s["max_rate"])
    add("abs.coop.fold", "Abstract", "Same-opponent fold spread", "49.5", lambda R: R.a1s["fold_spread_same_opponent"])
    for cat, lo, hi in (("coordination", "61", "85"), ("competition", "21", "41"), ("negotiation", "42", "51")):
        add(f"abs.{cat}.min", "Abstract", f"{cat.capitalize()} index, lowest model (percent)", lo, lambda R, c=cat: R.a4[c]["min"] * 100)
        add(f"abs.{cat}.max", "Abstract", f"{cat.capitalize()} index, highest model (percent)", hi, lambda R, c=cat: R.a4[c]["max"] * 100)
    add("abs.dev_share", "Abstract", "Developer share of between-model cooperation variance", "0.39", lambda R: R.a2["between_model_shares_pd"]["developer"])
    # Convergence
    add("conv.cv.min", "Results: convergence", "Lowest coefficient of variation of the three convergent indices", "0.070",
        lambda R: min(R.a4[c]["cv"] for c in ("coordination", "depth", "competition")))
    add("conv.cv.max", "Results: convergence", "Highest coefficient of variation of the three convergent indices", "0.148",
        lambda R: max(R.a4[c]["cv"] for c in ("coordination", "depth", "competition")))
    cats = [("coordination", "Coordination", "0.612", "LLaMA 3.3 70B", "0.850", "Gemini 3 Pro", "0.070", ("0.801", "0.770", "0.783"), "4.63", "0.0989"),
            ("depth", "Strategic depth", "0.527", "Ministral 14B", "0.889", "Gemini 3 Pro", "0.107", ("0.811", "0.838", "0.853"), "4.19", "0.123"),
            ("competition", "Competition", "0.209", "Gemini 3.1 Pro", "0.415", "Gemini 2.5 Flash", "0.148", ("0.368", "0.323", "0.326"), "2.90", "0.2351"),
            ("cooperation", "Cooperation index", None, None, None, None, "0.499", ("0.593", "0.305", "0.356"), "7.24", "0.0268"),
            ("trust", "Trust", "0.041", "GPT-5 Nano", "0.677", "Claude Opus 4.5", "0.298", ("0.599", "0.405", "0.427"), "8.34", "0.0154"),
            ("fairness", "Fairness", "0.125", "GPT-5 Nano", "0.494", "Qwen 3.5 Flash", "0.178", ("0.474", "0.408", "0.401"), "8.22", "0.0164"),
            ("negotiation", "Negotiation", "0.424", "GPT-4.1 Nano", "0.513", "Ministral 14B", "0.056", ("0.467", "0.462", "0.448"), "2.06", "0.3577"),
            ("risk", "Risk taking", "0.023", "Gemini 3 Flash", "0.469", "Ministral 14B", "0.819", ("0.074", "0.144", "0.119"), "3.44", "0.1793")]
    for cat, label, mn, mnm, mx, mxm, cv, devs, H, P in cats:
        sec = "Results: convergence" if cat in ("coordination", "depth", "competition") else "Results: divergence"
        if mn is not None:
            add(f"{cat}.min", sec, f"{label}: lowest model index", mn, lambda R, c=cat: R.a4[c]["min"])
            add(f"{cat}.min_model", sec, f"{label}: lowest model", mnm, lambda R, c=cat: R.a4[c]["min_model"])
            add(f"{cat}.max", sec, f"{label}: highest model index", mx, lambda R, c=cat: R.a4[c]["max"])
            add(f"{cat}.max_model", sec, f"{label}: highest model", mxm, lambda R, c=cat: R.a4[c]["max_model"])
        add(f"{cat}.cv", sec, f"{label}: coefficient of variation", cv, lambda R, c=cat: R.a4[c]["cv"])
        for dev, val in zip(DEV3, devs):
            add(f"{cat}.dev.{dev}", sec, f"{label}: {dev} mean", val, lambda R, c=cat, d=dev: R.a4[c][f"dev_{d}"])
        add(f"{cat}.H", sec, f"{label}: Kruskal-Wallis H", H, lambda R, c=cat: R.a4[c]["kruskal_H"])
        add(f"{cat}.P", sec, f"{label}: Kruskal-Wallis P", P, lambda R, c=cat: R.a4[c]["kruskal_p"])
        add(f"{cat}.policy", sec, f"{label}: sampling basis", {"coordination": "21 common opponents", "cooperation": "16 common opponents",
            "trust": "6 common opponents", "fairness": "6 common opponents", "negotiation": "6 common opponents", "risk": "18 common opponents"}.get(cat, "as released"),
            lambda R, c=cat: R.a4[c]["policy"])
    for game, lo, hi, cv in (("First-price auction", "0.249", "0.426", "0.164"), ("All-pay auction", "0.012", "0.297", "0.370"), ("Vickrey auction", "0.474", "0.513", "0.022")):
        key = game.split()[0].lower().replace("-", "")
        add(f"game.{key}.min", "Results: convergence", f"{game}: lowest model ratio", lo, lambda R, g=game: R.a4g.loc[g, "min"])
        add(f"game.{key}.max", "Results: convergence", f"{game}: highest model ratio", hi, lambda R, g=game: R.a4g.loc[g, "max"])
        add(f"game.{key}.cv", "Results: convergence", f"{game}: coefficient of variation", cv, lambda R, g=game: R.a4g.loc[g, "cv"])
    # Cooperation headline (A1)
    add("coop.min", "Results: divergence", "Lowest same-opponent cooperation (percent)", "1.4", lambda R: R.a1s["min_rate"])
    add("coop.min_model", "Results: divergence", "Lowest same-opponent model", "GPT-5 Nano", lambda R: name(R.a1s["min_model"]))
    add("coop.max", "Results: divergence", "Highest same-opponent cooperation (percent)", "69.3", lambda R: R.a1s["max_rate"])
    add("coop.max_model", "Results: divergence", "Highest same-opponent model", "Claude Opus 4.6", lambda R: name(R.a1s["max_model"]))
    add("coop.fold", "Results: divergence", "Same-opponent fold spread", "49.5", lambda R: R.a1s["fold_spread_same_opponent"])
    add("coop.fold_pooled", "Results: divergence", "Pooled fold spread", "47.7", lambda R: R.a1s["fold_spread_pooled"])
    add("coop.spearman", "Results: divergence", "Spearman, same-opponent vs pooled ranking", "0.995", lambda R: R.a1s["spearman_same_vs_pooled"])
    add("coop.n_opp", "Results: divergence", "Common opponents in the prisoner's dilemma", "16", lambda R: R.a1s["n_common_opponents"])
    # A2
    tl = lambda R: R.a2["trial_level"]
    add("a2.n", "Results: developer identity", "Strategy-play trials in the trial model", "5,318", lambda R: R.a2["n_trials"])
    add("a2.models", "Results: developer identity", "Models in the trial model", "25", lambda R: R.a2["n_models"])
    # Printed values as the corrected manuscript prints them (after the DeepSeek V3 date correction, 2026-09-28).
    add("a2.r2", "Results: developer identity", "Trial-level R squared", "0.2705", lambda R: tl(R)["r2_full"])
    add("a2.anthropic", "Results: developer identity", "Anthropic vs OpenAI (pp)", "26.1", lambda R: tl(R)["developer_coefficients_vs_reference"][DEVKEY.format("Anthropic")] * 100)
    add("a2.anthropic_p", "Results: developer identity", "Anthropic vs OpenAI, P", "0.0137", lambda R: tl(R)["developer_p_values"][DEVKEY.format("Anthropic")])
    for dev, val in (("Meta", "-24.5"), ("Mistral", "20.6"), ("Alibaba", "17.1"), ("DeepSeek", "-17.1"), ("Google", "-6.6")):
        add(f"a2.{dev}", "Results: developer identity", f"{dev} vs OpenAI (pp)", val, lambda R, d=dev: tl(R)["developer_coefficients_vs_reference"][DEVKEY.format(d)] * 100)
    for dev, val in (("DeepSeek", "0.282"), ("Google", "0.642")):
        add(f"a2.{dev}_p", "Results: developer identity", f"{dev} vs OpenAI, P", val,
            lambda R, d=dev: tl(R)["developer_p_values"][DEVKEY.format(d)])
    add("a2.Meta_p", "Results: developer identity", "Meta vs OpenAI, P (text: reported without a test, one model)", "without a test",
        lambda R: tl(R)["developer_p_values"][DEVKEY.format("Meta")])
    for f, val in (("developer", "0.0745"), ("size_tier", "0.0327"), ("release_years", "0.0066"), ("reasoning", "0.0001")):
        add(f"a2.drop.{f}", "Results: developer identity", f"R squared drop without {f.replace('_', ' ')}", val, lambda R, f=f: tl(R)["r2_drop_by_factor"][f])
    bm = lambda R: R.a2["between_model_shares_pd"]
    for f, val in (("developer", "0.390"), ("size_tier", "0.119"), ("release_years", "0.126"), ("reasoning", "0.000")):
        add(f"a2.share.{f}", "Results: developer identity", f"Between-model cooperation share: {f.replace('_', ' ')}", val, lambda R, f=f: bm(R)[f])
    for f, val in (("size_tier", "0.961"), ("reasoning", "1.000"), ("release_years", "0.955")):
        add(f"a2.boot.{f}", "Results: developer identity", f"Bootstrap share with developer ahead of {f.replace('_', ' ')}", val, lambda R, f=f: bm(R)["bootstrap_developer_ahead_of"][f])
    add("a2.joint", "Results: developer identity", "All characteristics jointly, between-model share", "0.571", lambda R: bm(R)["joint_r2"])
    add("a2.unique", "Results: developer identity", "Developer given the others", "0.373", lambda R: bm(R)["developer_given_others"])
    bt = lambda R: R.a2["between_model_shares_trust"]
    for f, val in (("size_tier", "0.212"), ("developer", "0.188"), ("reasoning", "0.007"), ("release_years", "0.032"), ("joint_r2", "0.402"), ("developer_given_others", "0.182")):
        add(f"a2.trust.{f}", "Results: developer identity", f"Trust between-model share: {f.replace('_', ' ')}", val, lambda R, f=f: bt(R)[f])
    # Generations (A1 same-opponent rates)
    for key, val in (("gpt-4o-mini", "53.2"), ("gpt-5-nano", "1.4"), ("gpt-4.1-mini", "41.9"), ("gpt-4.1-nano", "17.3"), ("gpt-5-mini", "6.7"),
                     ("gpt-4.1", "52.5"), ("gpt-5.3", "23.8"), ("gpt-5.4", "46.8"), ("gemini-2.0-flash", "8.3"), ("gemini-2.5-flash", "29.2"),
                     ("gemini-2.5-flash-thinking", "28.5"), ("gemini-3-flash", "59.7"), ("gemini-3-pro", "55.7"), ("gemini-3.1-pro", "32.0"),
                     ("claude-haiku-4.5", "42.2"), ("claude-haiku-4.5-thinking", "42.5"), ("claude-sonnet-4.6", "65.9"), ("claude-opus-4.6", "69.3")):
        add(f"gen.{key}", "Results: generations", f"Same-opponent cooperation, {name(key)} (percent)", val, lambda R, k=key: R.a1.loc[k, "same_opponent_rate"])
    r = lambda R, k: R.a1.loc[k, "same_opponent_rate"]
    add("gen.small_drop", "Results: generations", "GPT-4o Mini minus GPT-5 Nano (pp)", "exceeding 50", lambda R: r(R, "gpt-4o-mini") - r(R, "gpt-5-nano"))
    add("gen.frontier_fall", "Results: generations", "GPT-4.1 minus GPT-5.3 (pp)", "more than 25", lambda R: r(R, "gpt-4.1") - r(R, "gpt-5.3"))
    add("gen.frontier_recover", "Results: generations", "GPT-5.4 minus GPT-5.3 (pp)", "more than 20", lambda R: r(R, "gpt-5.4") - r(R, "gpt-5.3"))
    add("gen.flash_rise", "Results: generations", "Gemini 3 Flash minus Gemini 2.0 Flash (pp)", "exceeding 50", lambda R: r(R, "gemini-3-flash") - r(R, "gemini-2.0-flash"))
    add("gen.sonnet_opus_min", "Results: generations", "Sonnet and Opus, lowest (percent)", "65.9",
        lambda R: min(r(R, k) for k in ("claude-sonnet-4.5", "claude-sonnet-4.6", "claude-opus-4.5", "claude-opus-4.6")))
    add("gen.sonnet_opus_max", "Results: generations", "Sonnet and Opus, highest (percent)", "69.3",
        lambda R: max(r(R, k) for k in ("claude-sonnet-4.5", "claude-sonnet-4.6", "claude-opus-4.5", "claude-opus-4.6")))
    add("gen.tier_gap", "Results: generations", "Sonnet and Opus mean minus Haiku mean (pp)", "about 25",
        lambda R: np.mean([r(R, k) for k in ("claude-sonnet-4.5", "claude-sonnet-4.6", "claude-opus-4.5", "claude-opus-4.6")]) - np.mean([r(R, k) for k in ("claude-haiku-4.5", "claude-haiku-4.5-thinking")]))
    # Mechanisms (A6)
    dm = lambda R, comp, d: R.a6["developer_means"][comp][d]
    dt = lambda R, comp, k: R.a6["developer_tests"][comp][k]
    for comp, label, vals, H, P, eta in (("coop_vs_always_cooperate", "Against always-cooperate", ("0.875", "0.369", "0.580"), "8.32", "0.0156", "0.425"),
                                         ("coop_vs_always_defect", "Against always-defect", ("0.099", "0.087", "0.069"), "2.13", "0.3445", "0.064"),
                                         ("coop_vs_tit_for_tat", "Against tit-for-tat", ("0.881", "0.394", "0.526"), "8.58", "0.0137", "0.357"),
                                         ("preference_component", "Preference component", ("0.683", "0.370", "0.434"), "8.15", "0.017", "0.392"),
                                         ("belief_component", "Belief component", ("0.856", "0.660", "0.733"), "5.46", "0.0654", "0.268"),
                                         ("risk_component", "Risk component", ("0.381", "0.367", "0.388"), "0.18", "0.9134", "0.031"),
                                         ("rule_component", "Rule component", (None, None, None), "2.13", "0.3445", "0.064")):
        for dev, val in zip(DEV3, vals):
            if val is not None:
                add(f"a6.{comp}.{dev}", "Results: mechanisms", f"{label}: {dev} mean", val, lambda R, c=comp, d=dev: dm(R, c, d))
        add(f"a6.{comp}.H", "Results: mechanisms", f"{label}: H", H, lambda R, c=comp: dt(R, c, "kruskal_H"))
        add(f"a6.{comp}.P", "Results: mechanisms", f"{label}: P", P, lambda R, c=comp: dt(R, c, "p"))
        add(f"a6.{comp}.eta", "Results: mechanisms", f"{label}: eta squared", eta, lambda R, c=comp: dt(R, c, "eta_squared_between_developers"))
    # Endgame (A3)
    ty = lambda R: R.a3["types_vs_reactive"]
    members = lambda R, t: ", ".join(v["display"] for v in ty(R).values() if v["type"] == t)
    add("a3.files", "Results: endgame", "Prisoner's dilemma trial files", "7,668", lambda R: R.a3["n_files"])
    add("a3.obs", "Results: endgame", "Model-round observations", "100,180", lambda R: R.a3["n_round_observations"])
    for t, val, names in (("sustained cooperator", "5", "Claude Sonnet 4.6, Claude Opus 4.5, Claude Opus 4.6, GPT-4o Mini, GPT-5.4"),
                          ("horizon-conditioned", "5", "GPT-4.1, Gemini 3 Pro, Gemini 3.1 Pro, DeepSeek R1, Qwen 3.5 Flash"),
                          ("unconditional defector", "4", "(not named in the text)"), ("intermediate", "11", "(not named in the text)")):
        add(f"a3.count.{t}", "Results: endgame", f"Models classed as {t}", val, lambda R, t=t: R.a3["type_counts"].get(t, 0))
        add(f"a3.members.{t}", "Results: endgame", f"Members: {t}", names, lambda R, t=t: members(R, t))
    for key, val in (("claude-sonnet-4.6", "80.0"), ("claude-opus-4.5", "100.0"), ("claude-opus-4.6", "91.7"), ("gpt-4o-mini", "56.1"), ("gpt-5.4", "58.3")):
        add(f"a3.r10.{key}", "Results: endgame", f"Round-10 cooperation vs reactive opponents, {name(key)} (percent)", val, lambda R, k=key: ty(R)[k]["round10_reactive"] * 100)
    horizon = ("gpt-4.1", "gemini-3-pro", "gemini-3.1-pro", "deepseek-r1", "qwen3.5-flash")
    add("a3.h.r10.min", "Results: endgame", "Horizon-conditioned (named five): lowest round-10 rate", "0.0", lambda R: min(ty(R)[k]["round10_reactive"] for k in horizon) * 100)
    add("a3.h.r10.max", "Results: endgame", "Horizon-conditioned (named five): highest round-10 rate", "8.3", lambda R: max(ty(R)[k]["round10_reactive"] for k in horizon) * 100)
    add("a3.h.r9.min", "Results: endgame", "Horizon-conditioned (named five): lowest round-9 rate", "43.8", lambda R: min(ty(R)[k]["round9_reactive"] for k in horizon) * 100)
    add("a3.h.r9.max", "Results: endgame", "Horizon-conditioned (named five): highest round-9 rate", "91.7", lambda R: max(ty(R)[k]["round9_reactive"] for k in horizon) * 100)
    for key, v9, v10 in (("claude-haiku-4.5", "60.0", "48.3"), ("gpt-4.1-mini", "50.2", "29.9"), ("gemini-3-flash", "81.7", "13.3"), ("claude-sonnet-4.5", "86.7", "40.0")):
        add(f"a3.i.{key}.r9", "Results: endgame", f"{name(key)}: round 9 vs reactive (percent)", v9, lambda R, k=key: ty(R)[k]["round9_reactive"] * 100)
        add(f"a3.i.{key}.r10", "Results: endgame", f"{name(key)}: round 10 vs reactive (percent)", v10, lambda R, k=key: ty(R)[k]["round10_reactive"] * 100)
    cls = lambda R, c, k: float(R.a3r[(R.a3r.opponent_class == c) & (R.a3r.model_key == k)].round10.iloc[0]) * 100
    for key in ("claude-sonnet-4.6", "claude-opus-4.5", "claude-opus-4.6"):
        add(f"a3.ac.{key}", "Results: endgame", f"Final round vs always-cooperate, {name(key)} (percent)", "100.0", lambda R, k=key: cls(R, "fixed_cooperate", k))
        add(f"a3.sp.{key}", "Results: endgame", f"Final round in self-play, {name(key)} (percent)", "100.0", lambda R, k=key: cls(R, "self_play", k))
    add("a3.sp.zero", "Results: endgame", "Self-play final round at 0.0: OpenAI and Google models (text: several)", "several",
        lambda R: ", ".join(sorted(R.a3r[(R.a3r.opponent_class == "self_play") & (R.a3r.round10 == 0) & R.a3r.developer.isin(["OpenAI", "Google"])].display)))
    complete_design = sorted(set(common.MODELS) - set(common.FRONTIER_MODELS))
    xp = lambda R: R.a3r[(R.a3r.opponent_class == "cross_play") & R.a3r.model_key.isin(complete_design)].round10 * 100
    add("a3.xp.min", "Results: endgame", "Cross-play final round, 16 models: lowest (percent)", "0.0", lambda R: float(xp(R).min()))
    add("a3.xp.max", "Results: endgame", "Cross-play final round, 16 models: highest (percent)", "30.9", lambda R: float(xp(R).max()))
    return S


def _decimals(printed):
    s = printed.replace(",", "")
    try:
        float(s)
    except ValueError:
        return None
    return len(s.split(".")[1]) if "." in s else 0


def fmt(value, printed):
    if isinstance(value, str):
        return value
    d = _decimals(printed)
    if d is None:
        return f"{value:.4g}" if isinstance(value, float) else str(value)
    out = f"{float(value):,.{d}f}" if "," in printed else f"{float(value):.{d}f}"
    return "0.0" if out in ("-0.0",) else out


def numbers_table(scratch):
    runs = {name: Run(tree_paths(scratch, name)["out"]) for name in TREES}
    rows = []
    for nid, sec, what, printed, get in number_specs():
        row = {"id": nid, "section": sec, "quantity": what, "printed": printed}
        for name in TREES:
            try:
                v = get(runs[name])
                v = v.item() if hasattr(v, "item") else v
            except Exception as e:  # a missing model or class shows as an error, never as a number
                v = f"ERROR {type(e).__name__}"
            row[f"{name}_raw"] = v
            row[name] = fmt(v, printed) if not (isinstance(v, str) and v.startswith("ERROR")) else v
        row["changes_at_printed_precision"] = row["judge_free"] != row["stored_full"]
        # where the paper prints a number, the released result must print the same at that precision
        row["printed_matches_banked"] = (row["stored_full"] == printed) if _decimals(printed) is not None else ""
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scratch", default=os.path.join(tempfile.gettempdir(), "llm-games-reparse-check"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--analyses-only", action="store_true", help="reuse the copies of the last run and rerun the analyses and tables")
    a = ap.parse_args()
    selftest()
    if a.selftest:
        return
    scratch = a.scratch
    os.makedirs(scratch, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    trees = {name: tree_paths(scratch, name) for name in TREES}
    if a.analyses_only:
        trees = {name: refresh_tree(p) for name, p in trees.items()}

    if not a.analyses_only:
        trees = {name: prepare_tree(scratch, name) for name in TREES}
        if not os.path.isdir(RAW):
            raise SystemExit(f"no raw trial files in {RAW}; unpack the raw corpus from Zenodo (10.5281/zenodo.19896196) "
                             "into raw_data/ or set RAW_DATA_DIR")
        files = sorted([os.path.join(RAW, f) for f in os.listdir(RAW) if f.endswith(".json")], key=lambda p: os.path.basename(p).upper())
        print(f"re-parsing {len(files)} trial files with {a.workers} workers", flush=True)
        results = []
        with Pool(a.workers, initializer=_init_worker, initargs=({n: trees[n]["raw"] for n in TREES},)) as pool:
            for i, res in enumerate(pool.imap(process_file, files, chunksize=32), 1):
                if res is not None:
                    results.append(res)
                if i % 5000 == 0:
                    print(f"  {i}", flush=True)

        # 1. identity: the stored values and every game rebuild the released trial-level file byte for byte
        stored_all = pd.DataFrame([r["stored_row"] for r in results])
        stored_all.to_csv(trees["stored_full"]["profiles"], index=False)
        with open(trees["stored_full"]["profiles"], "rb") as f1, open(BANKED_PROFILES, "rb") as f2:
            if f1.read() != f2.read():
                raise SystemExit("the rebuilt trial-level file differs from summary_data/behavioral_profiles.csv; stopping")
        print("check: the stored parse rebuilds summary_data/behavioral_profiles.csv byte for byte", flush=True)
        n_equiv_fail = sum(r["equivalence_failure"] for r in results)
        if n_equiv_fail:
            raise SystemExit(f"{n_equiv_fail} trials: the drop-aware copies disagree with the originals with nothing dropped; stopping")
        print("check: the drop-aware copies equal the originals on every trial with nothing dropped", flush=True)
        cols = list(stored_all.columns)
        keep = [r["game_id"] not in EXCLUDED_GAMES for r in results]
        stored_all[keep].to_csv(trees["stored_excl"]["profiles"], index=False)
        jf = pd.DataFrame([r["jf_row"] for r, k in zip(results, keep) if k]).reindex(columns=cols)
        jf.to_csv(trees["judge_free"]["profiles"], index=False)
        shutil.copy2(trees["judge_free"]["profiles"], os.path.join(OUT, "behavioral_profiles.csv"))

        # parse summary
        def tally(rs):
            c = Counter()
            for r in rs:
                c.update(r["stats"])
                c["trials"] += 1
                c["rounds"] += r["n_rounds"]
                c["trials_with_a_change"] += int(bool(r["stats"].get("changed")))
                c["trials_with_a_drop"] += int(bool(r["stats"].get("dropped")))
            c["decision_slots"] = c["replies"] + c["no_reply_slots"]
            c["decisions_kept"] = c["replies"] - c["dropped"]
            return {k: int(c[k]) for k in ("trials", "rounds", "decision_slots", "no_reply_slots", "replies", "unchanged", "changed", "dropped",
                                            "decisions_kept", "trials_with_a_change", "trials_with_a_drop")}
        in_set = [r for r in results if r["game_id"] not in EXCLUDED_GAMES]
        summary = {
            "what": "Judge-free re-parse of every model reply: unchanged = equals the stored parse; changed = a different value; dropped = no deterministic parse (the engine would have used a random option or 0).",
            "all_38_games": tally(results),
            "robustness_dataset_36_games": tally(in_set),
            "prisoners_dilemma_4_variants": tally([r for r in results if r["game_id"] in PD]),
            "blotto_and_multi_issue_left_out": tally([r for r in results if r["game_id"] in EXCLUDED_GAMES]),
            "trials_28_february": tally([r for r in results if r["date"] == "2026-02-28"]),
            "trials_28_february_in_dataset": tally([r for r in in_set if r["date"] == "2026-02-28"]),
            "by_game": {g: tally([r for r in results if r["game_id"] == g]) for g in sorted({r["game_id"] for r in results})},
            "trials_in_robustness_dataset_with_no_measure": {c: int(jf[jf.game_category == c][m].isna().sum() - stored_all[keep][stored_all[keep].game_category == c][m].isna().sum())
                                                              for c, m in (("cooperation", "cooperation_rate"), ("coordination", "coordination_rate"), ("fairness", "offer_ratio"),
                                                                           ("trust", "trust_index"), ("depth", "mean_guess"), ("competition", "bid_ratio"),
                                                                           ("negotiation", "demand_ratio"), ("risk", "risk_taking_rate"))},
            "payoffs": "player0_payoff and player1_payoff in reparse_check/behavioral_profiles.csv are the stored totals; A1, A2, A3, A4 and A6 do not read payoffs, so none was recomputed.",
        }
        with open(os.path.join(OUT, "parse_summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        with open(os.path.join(scratch, "changed_or_dropped_decisions.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["file", "pid", "round", "kind", "stored", "judge_free"])
            for r in results:
                w.writerows(r["changes"])
        print(json.dumps({k: summary[k] for k in ("all_38_games", "robustness_dataset_36_games", "prisoners_dilemma_4_variants")}, indent=1), flush=True)
        del results

    # 2. the analyses in the three copies
    for name in TREES:
        print(f"running the analyses on {name}", flush=True)
        run_tree(trees[name])
    diffs = compare_outputs(SUMMARY, trees["stored_full"]["out"], BANKED_FILES)
    if diffs:
        report = "\n".join(f"  {f}: {len(d)} cells, first {d[:3]}" for f, d in diffs.items())
        raise SystemExit(f"the stored_full copy does not reproduce the released results:\n{report}")
    print("check: the stored_full copy reproduces all 16 released A1 to A6 result files cell for cell", flush=True)
    for f in BANKED_FILES:
        shutil.copy2(os.path.join(trees["judge_free"]["out"], f), os.path.join(OUT, f))
    table = numbers_table(scratch)
    table.to_csv(os.path.join(OUT, "printed_numbers.csv"), index=False)
    ch = table[table.changes_at_printed_precision]
    print(f"{len(table)} printed numbers; {len(ch)} change at printed precision in the re-parsed run")
    print(ch[["id", "printed", "stored_full", "stored_excl", "judge_free"]].to_string(index=False))


if __name__ == "__main__":
    main()
