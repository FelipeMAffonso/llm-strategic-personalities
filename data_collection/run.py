#!/usr/bin/env python3
"""
Run the data collection of one of the two designs, or list the games, the models and the designs.

Usage (from the top of the repository):
    python data_collection/run.py --list-designs                   # the two designs and their trial counts
    python data_collection/run.py --list-games                     # the 38 games by category
    python data_collection/run.py --list-models                    # the 25 models
    python data_collection/run.py --design complete --dry-run      # the matchups of a design, without running it
    python data_collection/run.py --design complete                # run the complete design (16 models)
    python data_collection/run.py --design frontier                # run the frontier design (9 models)

Running a design calls the model APIs and needs the keys listed in data_collection/api.py. Trials are written to
raw_data/ (or the folder named by RAW_DATA_DIR); a trial whose file already exists is skipped, so an interrupted run
continues where it stopped.
"""

import argparse
import sys
from pathlib import Path

# The top of the repository on the path, for the games and data_collection packages
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def cmd_list_designs(args):
    """Show the two designs with their trial counts."""
    from data_collection.designs import DESIGNS, print_design
    for design in DESIGNS.values():
        print_design(design)
    print()


def cmd_design_dry_run(args):
    """Show one design and its trial counts without running it."""
    from data_collection.designs import design_to_matchups, get_design, print_design
    design = get_design(args.design)
    print_design(design)
    matchups = design_to_matchups(design)
    print(f"\n{len(matchups):,} matchup configurations.")


def cmd_design_run(args):
    """Run a design."""
    from data_collection.api import load_env
    from data_collection.designs import design_to_matchups, get_design, print_design
    from data_collection.runner import run_experiment_parallel
    load_env()

    design = get_design(args.design)
    print_design(design)

    matchups = design_to_matchups(design)
    print(f"\nGenerated {len(matchups):,} matchup configurations.")

    results = run_experiment_parallel(matchups, max_workers=args.workers)
    print(f"\nExperiment complete: {len(results)} trials")


def cmd_list_games(args):
    """List all registered games."""
    from games.definitions import ALL_GAMES, CATEGORIES

    print(f"{'=' * 60}")
    print(f"REGISTERED GAMES ({len(ALL_GAMES)} total)")
    print(f"{'=' * 60}")

    for category, games in CATEGORIES.items():
        print(f"\n  {category.upper()} ({len(games)} games):")
        for g in games:
            print(f"    {g['game_id']:30s}  {g['name']}")
            print(f"      Type: {g['type']}, Rounds: {g.get('num_rounds', '?')}, "
                  f"Players: {g.get('num_players', 2)}")


def cmd_list_models(args):
    """List all registered models."""
    from data_collection.models import ALL_MODELS, MODEL_SETS

    print(f"{'=' * 60}")
    print(f"REGISTERED MODELS ({len(ALL_MODELS)} total)")
    print(f"{'=' * 60}")

    providers = {}
    for key, cfg in ALL_MODELS.items():
        providers.setdefault(cfg["provider"], []).append((key, cfg))

    for provider, models in sorted(providers.items()):
        print(f"\n  {provider.upper()} ({len(models)} models):")
        for key, cfg in models:
            thinking = " [thinking]" if cfg.get("thinking") else ""
            print(f"    {key:35s}  {cfg['model_id']}{thinking}")

    print(f"\n{'=' * 60}")
    print("MODEL SETS:")
    for name, ms in MODEL_SETS.items():
        print(f"  {name:15s} ({len(ms)} models): {', '.join(ms)}")


def main():
    parser = argparse.ArgumentParser(
        description="Language models in repeated economic games: data collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--design", type=str, default=None, choices=["complete", "frontier"],
                        help="The design to run: complete (16 models) or frontier (9 models)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show the design and its trial counts without running it")
    parser.add_argument("--workers", type=int, default=80,
                        help="Trials run in parallel (default 80)")
    parser.add_argument("--list-games", action="store_true",
                        help="List the 38 games")
    parser.add_argument("--list-models", action="store_true",
                        help="List the 25 models and the two model sets")
    parser.add_argument("--list-designs", action="store_true",
                        help="List the two designs")

    args = parser.parse_args()

    if args.list_designs:
        cmd_list_designs(args)
    elif args.list_games:
        cmd_list_games(args)
    elif args.list_models:
        cmd_list_models(args)
    elif args.design and args.dry_run:
        cmd_design_dry_run(args)
    elif args.design:
        cmd_design_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
