"""
Game Registry
==============
Imports all game category modules and builds a unified GAME_REGISTRY.
"""

from .cooperation import COOPERATION_GAMES
from .coordination import COORDINATION_GAMES
from .fairness import FAIRNESS_GAMES
from .depth import DEPTH_GAMES
from .trust import TRUST_GAMES
from .competition import COMPETITION_GAMES
from .negotiation import NEGOTIATION_GAMES
from .risk import RISK_GAMES

# Unified registry: game_id -> game_config
GAME_REGISTRY = {}
ALL_GAMES = []

for game_list in [
    COOPERATION_GAMES,
    COORDINATION_GAMES,
    FAIRNESS_GAMES,
    DEPTH_GAMES,
    TRUST_GAMES,
    COMPETITION_GAMES,
    NEGOTIATION_GAMES,
    RISK_GAMES,
]:
    for game in game_list:
        GAME_REGISTRY[game["game_id"]] = game
        ALL_GAMES.append(game)

# Category groupings
CATEGORIES = {
    "cooperation": COOPERATION_GAMES,
    "coordination": COORDINATION_GAMES,
    "fairness": FAIRNESS_GAMES,
    "depth": DEPTH_GAMES,
    "trust": TRUST_GAMES,
    "competition": COMPETITION_GAMES,
    "negotiation": NEGOTIATION_GAMES,
    "risk": RISK_GAMES,
}
