"""
Play one full match between two programmed strategies, with no model and no API call.

The engine builds the same prompts it sends to a model (rules, history and query), parses the <answer> tag each
strategy returns, applies the payoffs and records the match in the format of the raw trial files. By default,
tit-for-tat plays suspicious tit-for-tat in the canonical prisoner's dilemma (ten rounds):

    python games/example_match.py
    python games/example_match.py --game trust_berg --first trust_full --second trust_proportional
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from games.definitions import GAME_REGISTRY  # noqa: E402
from games.engine import GameEngine, StrategyPlayer, play_model_vs_strategy  # noqa: E402
from games.strategies import get_strategies_for_game  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--game", default="pd_canonical")
    parser.add_argument("--first", default="tit_for_tat", help="strategy in the first player position")
    parser.add_argument("--second", default="suspicious_tft", help="strategy in the second player position")
    parser.add_argument("--seed", type=int, default=1, help="seed of the option labels")
    parser.add_argument("--show-prompt", action="store_true", help="print the prompt of the last round")
    args = parser.parse_args()

    game = GAME_REGISTRY[args.game]
    strategies = get_strategies_for_game(game)
    engine = GameEngine(game, label_seed=args.seed)
    first = StrategyPlayer(strategies[args.first], 0, game, engine)
    result = play_model_vs_strategy(engine, first, strategies[args.second], model_player_id=0)
    result.players[0] = args.first

    print(f"{result.game_name}: {args.first} against {args.second}, {result.num_rounds} rounds")
    print(f"option labels: {json.dumps(result.label_map)}")
    for r in result.rounds:
        print(f"  round {r.round_num:2d}: {r.parsed_choices[0]:>10s} {r.parsed_choices[1]:>10s}   "
              f"payoffs {r.payoffs[0]:g}, {r.payoffs[1]:g}")
    print(f"total payoffs: {result.total_payoffs[0]:g}, {result.total_payoffs[1]:g}")
    if args.show_prompt:
        system_prompt, user_message = engine.build_prompt(0, result.num_rounds, result.rounds[:-1])
        print("\n" + system_prompt + "\n\n" + user_message)


if __name__ == "__main__":
    main()
