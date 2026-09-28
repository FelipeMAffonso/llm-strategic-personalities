"""
The two designs of the study.

  complete  16 models (COMPLETE_DESIGN_MODELS), all 38 games, five trials per cell: strategy-play against every
            programmed opponent of each game, self-play, and cross-play between every pair of the 16 models
            (120 pairs). Labelled F in Supplementary Table S1.
  frontier  9 frontier models (FRONTIER_DESIGN_MODELS), all 38 games, one trial per cell: strategy-play and
            self-play. Labelled G in Supplementary Table S1.

A cell is one model (or pair of models), one game and one opponent.

    python data_collection/run.py --design complete --dry-run    # the matchups and trial counts
    python data_collection/run.py --design complete              # run it
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from itertools import combinations

from data_collection.models import get_model_set
from games.definitions import ALL_GAMES
from games.strategies import get_strategies_for_game


@dataclass
class ExperimentDesign:
    """Full specification of an experiment run."""
    name: str
    description: str

    model_set: str                     # key into MODEL_SETS (data_collection/models.py)

    # Trial counts per matchup cell
    strategy_trials: int = 5
    self_play_trials: int = 5
    cross_play_trials: int = 5

    # Matchup types to run
    include_strategy: bool = True
    include_self_play: bool = True
    include_cross_play: bool = True

    # Conditions (data_collection/conditions.py)
    conditions: list[str] = field(default_factory=lambda: ["baseline"])

    def resolve_models(self) -> dict:
        return get_model_set(self.model_set)

    def resolve_games(self) -> list:
        return ALL_GAMES


DESIGNS = {
    "complete": ExperimentDesign(
        name="Complete design",
        description="16 models, all 38 games, five trials per cell: strategy-play, self-play and full cross-play.",
        model_set="complete",
        strategy_trials=5,
        self_play_trials=5,
        cross_play_trials=5,
        include_strategy=True,
        include_self_play=True,
        include_cross_play=True,
        conditions=["baseline"],
    ),

    "frontier": ExperimentDesign(
        name="Frontier design",
        description="9 frontier models, all 38 games, one trial per cell: strategy-play and self-play.",
        model_set="frontier",
        strategy_trials=1,
        self_play_trials=1,
        cross_play_trials=0,
        include_strategy=True,
        include_self_play=True,
        include_cross_play=False,
        conditions=["baseline"],
    ),
}


def get_design(name: str) -> ExperimentDesign:
    """Get one of the two designs."""
    if name not in DESIGNS:
        raise ValueError(f"Unknown design: {name}. "
                         f"Available: {list(DESIGNS.keys())}")
    return copy.deepcopy(DESIGNS[name])


def count_trials(design: ExperimentDesign) -> dict:
    """Number of matchups and trials of each matchup type in a design."""
    models = design.resolve_models()
    games = design.resolve_games()
    n_conditions = len(design.conditions)
    counts = {"n_models": len(models), "n_games": len(games)}
    total = 0
    if design.include_strategy:
        matchups = sum(len(models) * len(get_strategies_for_game(g)) for g in games)
        counts["strategy_matchups"] = matchups
        counts["strategy_trials"] = matchups * design.strategy_trials * n_conditions
        total += counts["strategy_trials"]
    if design.include_self_play:
        matchups = len(models) * len(games)
        counts["self_play_matchups"] = matchups
        counts["self_play_trials"] = matchups * design.self_play_trials * n_conditions
        total += counts["self_play_trials"]
    if design.include_cross_play:
        pairs = len(models) * (len(models) - 1) // 2
        counts["cross_play_pairs"] = pairs
        counts["cross_play_matchups"] = pairs * len(games)
        counts["cross_play_trials"] = pairs * len(games) * design.cross_play_trials * n_conditions
        total += counts["cross_play_trials"]
    counts["total_trials"] = total
    return counts


def print_design(design: ExperimentDesign):
    """Print a design and its trial counts."""
    c = count_trials(design)
    print(f"\n{'=' * 60}")
    print(f"  {design.name}")
    print(f"  {design.description}")
    print(f"{'=' * 60}")
    print(f"  Models:     {c['n_models']} ({design.model_set})")
    print(f"  Games:      {c['n_games']}")
    print(f"  Conditions: {design.conditions}")
    print()
    if "strategy_trials" in c:
        print(f"  Strategy-play:  {c['strategy_matchups']:>8,} matchups "
              f"x {design.strategy_trials} trials = {c['strategy_trials']:>10,} trials")
    if "self_play_trials" in c:
        print(f"  Self-play:      {c['self_play_matchups']:>8,} matchups "
              f"x {design.self_play_trials} trials = {c['self_play_trials']:>10,} trials")
    if "cross_play_trials" in c:
        print(f"  Cross-play:     {c['cross_play_pairs']:>8,} pairs x {c['n_games']} games "
              f"x {design.cross_play_trials} trials = {c['cross_play_trials']:>10,} trials")
    print(f"\n  TOTAL TRIALS:   {c['total_trials']:>10,}")


def design_to_matchups(design: ExperimentDesign) -> list[dict]:
    """
    Generate the full list of matchup dicts from an ExperimentDesign.
    Each matchup dict has all info needed by the runner.
    """
    models = design.resolve_models()
    games = design.resolve_games()
    matchups = []

    for condition in design.conditions:
        # Strategy-play
        if design.include_strategy:
            for game in games:
                game_id = game["game_id"]
                strategies = get_strategies_for_game(game)
                for model_key, model_cfg in models.items():
                    for strat_name in strategies:
                        matchups.append({
                            "matchup_type": "model_vs_strategy",
                            "model_key": model_key,
                            "model_cfg": model_cfg,
                            "game_id": game_id,
                            "strategy_name": strat_name,
                            "condition": condition,
                            "num_trials": design.strategy_trials,
                        })

        # Self-play
        if design.include_self_play:
            for game in games:
                game_id = game["game_id"]
                for model_key, model_cfg in models.items():
                    matchups.append({
                        "matchup_type": "self_play",
                        "model_key_p0": model_key,
                        "model_cfg_p0": model_cfg,
                        "model_key_p1": model_key,
                        "model_cfg_p1": model_cfg,
                        "game_id": game_id,
                        "condition": condition,
                        "num_trials": design.self_play_trials,
                    })

        # Cross-play: every pair of models, each pair once
        if design.include_cross_play:
            pair_list = list(combinations(list(models), 2))
            for game in games:
                game_id = game["game_id"]
                for key_a, key_b in pair_list:
                    matchups.append({
                        "matchup_type": "cross_play",
                        "model_key_p0": key_a,
                        "model_cfg_p0": models[key_a],
                        "model_key_p1": key_b,
                        "model_cfg_p1": models[key_b],
                        "game_id": game_id,
                        "condition": condition,
                        "num_trials": design.cross_play_trials,
                    })

    return matchups
