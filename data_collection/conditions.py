"""
Conditions: the prompt framing and the sampling temperature of a trial.

Both designs of the study ran the baseline condition (the neutral framing at temperature 1.0). The raw corpus also
holds 17 trials under five other conditions: three goal framings (maximise your points, beat the other player, reach
fair outcomes), social chain-of-thought, and temperature 0. They are defined here so that every condition in the data
has its definition; the framings themselves are in games/prompts.py (FRAMING_PRESETS).
"""

from __future__ import annotations

CONDITION_REGISTRY = {
    "baseline": {
        "framing": "baseline",
        "temperature": 1.0,
        "description": "Default neutral framing, temperature 1.0",
    },
    "goal_maximise": {
        "framing": "goal_maximise",
        "temperature": 1.0,
        "description": "Explicit goal: maximise your points",
    },
    "goal_win": {
        "framing": "goal_win",
        "temperature": 1.0,
        "description": "Explicit goal: beat the other player",
    },
    "goal_fair": {
        "framing": "goal_fair",
        "temperature": 1.0,
        "description": "Explicit goal: reach fair outcomes",
    },
    "scot": {
        "framing": "scot",
        "temperature": 1.0,
        "description": "Social chain-of-thought (predict the other player's choice, then decide)",
    },
    "temp_0": {
        "framing": "baseline",
        "temperature": 0.0,
        "description": "Temperature 0",
    },
}


def get_condition(name: str) -> dict:
    """Get condition config by name."""
    if name not in CONDITION_REGISTRY:
        raise ValueError(f"Unknown condition: {name}. "
                         f"Available: {list(CONDITION_REGISTRY.keys())}")
    return CONDITION_REGISTRY[name]
