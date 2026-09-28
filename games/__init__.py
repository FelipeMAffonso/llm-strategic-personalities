"""
The game engine, the prompts, the programmed strategies and the 38 games.

    engine.py       GameEngine: rules, history and query blocks; response parsing; payoffs; match play
    prompts.py      the prompt structure and the framing presets
    strategies.py   the programmed opponents (always-cooperate, tit-for-tat, grim trigger and the rest)
    definitions/    the 38 games, one module per category
"""

from .engine import (
    GameEngine,
    MatchResult,
    RoundResult,
    make_model_player,
    make_strategy_player,
    StrategyPlayer,
    play_model_vs_strategy,
    randomise_labels,
)
from .definitions import GAME_REGISTRY, ALL_GAMES, CATEGORIES
