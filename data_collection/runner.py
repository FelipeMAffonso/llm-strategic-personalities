"""
Experiment runner: plays the trials of a design against the model APIs, in parallel, and writes one JSON file per
trial.

Each trial is written to the raw data folder (raw_data/ at the top of the repository, or the folder named by the
environment variable RAW_DATA_DIR) as <game>_<model>_vs_<opponent>_<condition>_t<trial>_<hash>.json, the format of
the published corpus; a trial whose file already exists is not run again. A one-line summary of each new trial is
appended to trials.csv in the same folder.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

from data_collection.api import call_model_with_retry, get_delay
from data_collection.conditions import get_condition
from games.engine import (
    GameEngine, MatchResult, StrategyPlayer, make_model_player,
    play_model_vs_strategy,
)
from games.definitions import GAME_REGISTRY
from games.strategies import get_strategies_for_game


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = Path(os.environ.get("RAW_DATA_DIR") or PROJECT_ROOT / "raw_data")
CSV_PATH = DATA_RAW / "trials.csv"

# Thread lock for CSV writes
_csv_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _trial_hash(game_id: str, model_key: str, opponent: str,
                condition: str, trial_num: int) -> str:
    """Deterministic hash for a trial configuration."""
    key = f"{game_id}|{model_key}|{opponent}|{condition}|{trial_num}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def _cache_path(game_id: str, model_key: str, opponent: str,
                condition: str, trial_num: int) -> Path:
    """Path for cached trial JSON."""
    h = _trial_hash(game_id, model_key, opponent, condition, trial_num)
    return DATA_RAW / f"{game_id}_{model_key}_vs_{opponent}_{condition}_t{trial_num}_{h}.json"


def _load_cached(path: Path) -> dict | None:
    """Load cached trial result if it exists."""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_cache(path: Path, data: dict):
    """Save trial result to cache."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

CSV_HEADERS = [
    "game_id", "game_name", "game_category", "game_type",
    "model_key", "opponent", "matchup_type", "condition",
    "trial_num", "num_rounds",
    "player0_id", "player1_id",
    "player0_total_payoff", "player1_total_payoff",
    "cooperation_rate", "joint_cooperation_rate",
    "mean_choice_p0", "mean_choice_p1",
    "input_tokens", "output_tokens",
    "cache_hit", "timestamp",
]


def _init_csv():
    """Initialise CSV with headers if it doesn't exist."""
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()


def _append_csv(row: dict):
    """Thread-safe CSV append."""
    with _csv_lock:
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerow(row)


# ---------------------------------------------------------------------------
# Metric extraction from MatchResult
# ---------------------------------------------------------------------------

def _extract_metrics(result: MatchResult, game_config: dict) -> dict:
    """Extract summary metrics from a match result."""
    metrics = {}
    options = game_config["options"]

    if game_config["type"] == "simultaneous" and len(options) == 2:
        # Binary cooperation metrics (PD, Stag Hunt, Chicken, etc.)
        coop_option = options[0]  # first option is conventionally "cooperative"

        p0_choices = [r.parsed_choices.get(0) for r in result.rounds]
        p1_choices = [r.parsed_choices.get(1) for r in result.rounds]

        p0_coop = sum(1 for c in p0_choices if c == coop_option) / len(p0_choices)
        p1_coop = sum(1 for c in p1_choices if c == coop_option) / len(p1_choices)

        joint_coop = sum(
            1 for c0, c1 in zip(p0_choices, p1_choices)
            if c0 == coop_option and c1 == coop_option
        ) / len(p0_choices)

        metrics["cooperation_rate"] = round((p0_coop + p1_coop) / 2, 4)
        metrics["joint_cooperation_rate"] = round(joint_coop, 4)
        metrics["mean_choice_p0"] = coop_option if p0_coop > 0.5 else options[1]
        metrics["mean_choice_p1"] = coop_option if p1_coop > 0.5 else options[1]
    else:
        metrics["cooperation_rate"] = None
        metrics["joint_cooperation_rate"] = None
        metrics["mean_choice_p0"] = None
        metrics["mean_choice_p1"] = None

    return metrics


# ---------------------------------------------------------------------------
# LLM-as-judge for parsing verification
# ---------------------------------------------------------------------------

# The judge that extracts the answer from an ambiguous response: Claude Haiku 4.5
# at temperature 0 (disable with ENABLE_JUDGE=0).
JUDGE_MODEL_KEY = "claude-haiku-4.5"
JUDGE_MODEL_CFG = {
    "provider": "anthropic",
    "model_id": "claude-haiku-4-5-20251001",
}
_JUDGE_ENABLED = os.environ.get("ENABLE_JUDGE", "1") == "1"


def _create_judge_fn():
    """
    Create a judge callable for the engine.
    The judge extracts the correct answer from ambiguous model responses.
    Returns None if judging is disabled.
    """
    if not _JUDGE_ENABLED:
        return None

    from data_collection.api import call_model

    def judge_fn(prompt: str) -> str:
        """Call the judge model to extract the parsed value from a response."""
        try:
            result = call_model(
                JUDGE_MODEL_KEY,
                JUDGE_MODEL_CFG,
                system_prompt="You are a parsing assistant. Extract the exact answer from the player's response. Be precise and respond with ONLY the requested value.",
                user_message=prompt,
                max_tokens=32,
                temperature=0.0,
            )
            return result.get("text", "") if isinstance(result, dict) else str(result)
        except Exception as e:
            print(f"    [judge] failed: {e}")
            return ""

    return judge_fn


def _get_max_tokens(model_cfg: dict) -> int:
    """Get appropriate max_tokens for a model.

    Reference implementations:
    - Akata (2025): max_tokens=1 (single char forced choice)
    - GAMABench: max_tokens=1024
    - GameTheory: max_tokens=2000

    We use temp=1.0 (like GameTheory) which produces reasoning text,
    so we need sufficient tokens. Thinking/reasoning models need
    much more for their <think> blocks.
    """
    if model_cfg.get("thinking", False):
        return 16384  # thinking models need space for <think>...</think> + answer
    return 4096  # standard models: 2000 was too low, caused 5% truncation


# ---------------------------------------------------------------------------
# SCoT (Social Chain-of-Thought) wrapper
# ---------------------------------------------------------------------------

def _wrap_scot_player(model_player_fn, abstract_options):
    """
    Wrap a model player with SCoT two-step prompting (Akata et al. 2025).

    Each call to the wrapped function makes TWO API calls through the
    underlying model_player_fn:
      1. Prediction: "What will the other player do?"
      2. Resolution: "You predicted X. What do you choose?"

    Token usage is tracked on the underlying model_player_fn (which
    appends to its _token_usage list for each API call).
    """
    import re as _re
    from games.prompts import SCOT_PREDICTION_TEMPLATE, SCOT_RESOLUTION_TEMPLATE

    opt_a, opt_b = abstract_options[0], abstract_options[1]

    def scot_player(sys_prompt, user_msg):
        # Step 1: Prediction: replace Q: with the prediction question
        pred_msg = user_msg
        if "Q:" in pred_msg:
            parts = pred_msg.split("Q:", 1)
            pred_msg = parts[0] + SCOT_PREDICTION_TEMPLATE.format(
                opt_a=opt_a, opt_b=opt_b
            )

        pred_response = model_player_fn(sys_prompt, pred_msg)

        # Capture internal thinking from prediction call (thinking models)
        pred_thinking = getattr(model_player_fn, "_last_thinking", "") or ""

        # Extract predicted option (last mention of Option X in response)
        predicted = opt_a  # default
        for m in _re.finditer(
            rf'\bOption\s+({_re.escape(opt_a)}|{_re.escape(opt_b)})\b',
            pred_response, _re.IGNORECASE
        ):
            predicted = m.group(1).upper()

        # Step 2: Resolution: given the prediction, choose
        resolution = SCOT_RESOLUTION_TEMPLATE.format(
            predicted=predicted, opt_a=opt_a, opt_b=opt_b
        )
        # Include history context + prediction summary + resolution question
        if "Q:" in user_msg:
            history_part = user_msg.split("Q:", 1)[0]
            full_resolution = (
                history_part
                + f"Your prediction: {pred_response}\n\n"
                + resolution
            )
        else:
            full_resolution = f"Your prediction: {pred_response}\n\n" + resolution

        final_response = model_player_fn(sys_prompt, full_resolution)

        # Capture internal thinking from resolution call (thinking models)
        resolution_thinking = getattr(model_player_fn, "_last_thinking", "") or ""

        # Combine the SCoT text with the internal thinking from both calls.
        # For standard models, pred_thinking and resolution_thinking are empty.
        # For thinking models, they contain the model's internal chain-of-thought.
        text_parts = []
        if pred_thinking:
            text_parts.append(f"[Prediction Thinking] {pred_thinking}")
        text_parts.append(f"[SCoT Prediction] {pred_response}")
        text_parts.append(f"[Predicted: Option {predicted}]")
        if resolution_thinking:
            text_parts.append(f"[Resolution Thinking] {resolution_thinking}")
        text_parts.append(f"[SCoT Resolution] {final_response}")
        scot_player._last_thinking = "\n".join(text_parts)

        return final_response

    scot_player._last_thinking = ""
    scot_player.__name__ = getattr(model_player_fn, "__name__", "scot_player")

    return scot_player


# ---------------------------------------------------------------------------
# Single trial runner
# ---------------------------------------------------------------------------

def run_single_trial(
    game_id: str,
    model_key: str,
    model_cfg: dict,
    opponent: str,  # strategy name or model key
    condition: str,
    trial_num: int,
    opponent_cfg: dict | None = None,  # if opponent is a model
    temperature: float = 1.0,
    num_rounds: int | None = None,
    record_reasoning: bool = True,
    label_seed: int | None = None,
) -> dict:
    """
    Run a single game trial. If the trial's file already exists, returns it instead.

    Returns dict with match result and metadata.
    """
    cache_file = _cache_path(game_id, model_key, opponent, condition, trial_num)
    cached = _load_cached(cache_file)
    if cached:
        return {**cached, "cache_hit": True}

    game_config = GAME_REGISTRY[game_id]
    cond_cfg = get_condition(condition)
    temp = cond_cfg.get("temperature", temperature)

    # Set up label randomisation seed
    if label_seed is None:
        label_seed = hash(f"{game_id}|{model_key}|{trial_num}") % (2**31)

    # Create judge for parsing verification
    judge_fn = _create_judge_fn()

    # payoff_scale of the framing preset (1.0 unless a framing scales payoffs),
    # passed to GameEngine, which scales every payoff parameter consistently
    from games.prompts import FRAMING_PRESETS
    framing_key = cond_cfg.get("framing", "baseline")
    payoff_scale = FRAMING_PRESETS.get(framing_key, {}).get("payoff_scale", 1.0)

    engine = GameEngine(game_config, num_rounds=num_rounds,
                        label_seed=label_seed, judge_fn=judge_fn,
                        payoff_scale=payoff_scale)

    # Create model player (max_tokens depends on whether model uses thinking)
    max_tok = _get_max_tokens(model_cfg)
    model_delay = get_delay(model_cfg["provider"])
    model_player = make_model_player(
        model_key, model_cfg, call_model_with_retry,
        temperature=temp, max_tokens=max_tok, delay=model_delay,
    )

    # Wrap with SCoT two-step prompting if needed
    # Token tracking stays on the original model_player (SCoT wrapper
    # delegates API calls to it, which appends to _token_usage).
    use_scot = (framing_key == "scot" and len(engine.abstract_options) >= 2)
    engine_model_player = (
        _wrap_scot_player(model_player, engine.abstract_options)
        if use_scot else model_player
    )

    # Create opponent player
    num_game_players = game_config.get("num_players", 2)
    if opponent_cfg is not None:
        # Model vs model
        opp_max_tok = _get_max_tokens(opponent_cfg)
        opp_delay = get_delay(opponent_cfg["provider"])
        opponent_player = make_model_player(
            opponent, opponent_cfg, call_model_with_retry,
            temperature=temp, max_tokens=opp_max_tok, delay=opp_delay,
        )
        engine_opp_player = (
            _wrap_scot_player(opponent_player, engine.abstract_options)
            if use_scot else opponent_player
        )
        player_fns = {0: engine_model_player, 1: engine_opp_player}
        # For N-player cross-play, fill extra slots with random strategy
        if num_game_players > 2:
            from games.strategies import random_strategy
            for pid in range(2, num_game_players):
                player_fns[pid] = StrategyPlayer(random_strategy, pid, game_config, engine)
            engine._current_history = []
        result = engine.play_match(player_fns, framing=cond_cfg["framing"],
                                    record_reasoning=record_reasoning)
        matchup_type = "cross_play" if model_key != opponent else "self_play"
    else:
        # Model vs strategy
        strategies = get_strategies_for_game(game_config)
        if opponent not in strategies:
            raise ValueError(f"Unknown strategy '{opponent}' for game '{game_id}'")
        strategy_fn = strategies[opponent]
        result = play_model_vs_strategy(
            engine, engine_model_player, strategy_fn,
            model_player_id=0,
            framing=cond_cfg["framing"],
            record_reasoning=record_reasoning,
        )
        matchup_type = "model_vs_strategy"

    # Extract token usage from model player
    total_input = 0
    total_output = 0
    if hasattr(model_player, "_token_usage"):
        for usage in model_player._token_usage:
            total_input += usage["input_tokens"]
            total_output += usage["output_tokens"]

    if opponent_cfg and hasattr(opponent_player, "_token_usage"):
        for usage in opponent_player._token_usage:
            total_input += usage["input_tokens"]
            total_output += usage["output_tokens"]

    # Extract metrics
    metrics = _extract_metrics(result, game_config)

    # Build output
    output = {
        "game_id": game_id,
        "game_name": game_config["name"],
        "game_category": game_config["category"],
        "game_type": game_config["type"],
        "model_key": model_key,
        "opponent": opponent,
        "matchup_type": matchup_type,
        "condition": condition,
        "trial_num": trial_num,
        "num_rounds": result.num_rounds,
        "player0_id": result.players.get(0, model_key),
        "player1_id": result.players.get(1, opponent),
        "player0_total_payoff": result.total_payoffs.get(0, 0),
        "player1_total_payoff": result.total_payoffs.get(1, 0),
        "label_map": result.label_map,
        "input_tokens": total_input,
        "output_tokens": total_output,
        "cache_hit": False,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        **metrics,
        "match_detail": result.to_dict(),
    }

    # Cache result
    _save_cache(cache_file, output)

    # Append to CSV (without match_detail to keep CSV manageable)
    csv_row = {k: v for k, v in output.items()
               if k in CSV_HEADERS}
    _append_csv(csv_row)

    return output


# ---------------------------------------------------------------------------
# Parallel experiment runner
# ---------------------------------------------------------------------------

def run_experiment_parallel(
    matchups: list[dict],
    max_workers: int = 4,
    progress_interval: int = 10,
) -> list[dict]:
    """
    Run a list of matchup configurations in parallel.

    Each matchup dict should have:
        - model_key, model_cfg, game_id, condition, num_trials
        - strategy_name (for model_vs_strategy) or model_key_p1, model_cfg_p1 (for cross/self play)
    """
    _init_csv()
    results = []
    completed = 0
    total = sum(m.get("num_trials", 1) for m in matchups)

    print(f"Running {total} trials across {len(matchups)} matchup configurations...")
    print(f"  Workers: {max_workers}")

    def _run_matchup_trial(matchup: dict, trial_num: int) -> dict:
        mtype = matchup.get("matchup_type", "model_vs_strategy")

        if mtype == "model_vs_strategy":
            return run_single_trial(
                game_id=matchup["game_id"],
                model_key=matchup["model_key"],
                model_cfg=matchup["model_cfg"],
                opponent=matchup["strategy_name"],
                condition=matchup["condition"],
                trial_num=trial_num,
            )
        elif mtype in ("self_play", "cross_play"):
            return run_single_trial(
                game_id=matchup["game_id"],
                model_key=matchup["model_key_p0"],
                model_cfg=matchup["model_cfg_p0"],
                opponent=matchup["model_key_p1"],
                condition=matchup["condition"],
                trial_num=trial_num,
                opponent_cfg=matchup["model_cfg_p1"],
            )
        else:
            raise ValueError(f"Unknown matchup type: {mtype}")

    # Build flat task list and shuffle for broad game coverage early.
    # Without shuffling, tasks are ordered by game (all PD first, then BoS,
    # etc.), so you don't see data for later games until hours in.
    # Shuffling ensures every game gets trials early, enabling early auditing.
    tasks = []
    for matchup in matchups:
        n_trials = matchup.get("num_trials", 1)
        for t in range(1, n_trials + 1):
            tasks.append((matchup, t))

    random.seed(42)  # reproducible shuffle
    random.shuffle(tasks)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_run_matchup_trial, m, t): (m, t)
            for m, t in tasks
        }

        for future in as_completed(futures):
            matchup, trial = futures[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1

                if completed % progress_interval == 0 or completed == total:
                    cached = sum(1 for r in results if r.get("cache_hit"))
                    print(f"  [{completed}/{total}] "
                          f"({cached} cached, {completed - cached} new)")

            except Exception as e:
                mtype = matchup.get("matchup_type", "?")
                model = matchup.get("model_key", matchup.get("model_key_p0", "?"))
                game = matchup.get("game_id", "?")
                print(f"  ERROR [{model} / {game} / t{trial}]: {type(e).__name__}: {e}")
                completed += 1

    return results
