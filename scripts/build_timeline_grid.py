#!/usr/bin/env python
"""CLI Script: Build Multi-Game Timeline Grid.

Erstellt ein einheitliches Tages-Grid fuer KENO, Lotto und EuroJackpot.

Usage:
    python scripts/build_timeline_grid.py --output data/processed/timeline.parquet

    # Mit spezifischen Pfaden:
    python scripts/build_timeline_grid.py \
        --keno data/raw/keno/KENO_ab_2022_bereinigt.csv \
        --lotto data/raw/lotto/LOTTO_ab_2022_bereinigt.csv \
        --eurojackpot data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv \
        --output data/processed/timeline.parquet \
        --fill-strategy nan \
        --mode matrix
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kenobase.core.timeline import TimelineGrid, load_multi_game_grid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Default paths
DEFAULT_PATHS = {
    "keno": "data/raw/keno/KENO_ab_2022_bereinigt.csv",
    "lotto": "data/raw/lotto/LOTTO_ab_2022_bereinigt.csv",
    "eurojackpot": "data/raw/eurojackpot/EJ_ab_2022_bereinigt.csv",
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build multi-game timeline grid from lottery data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Input paths
    parser.add_argument(
        "--keno",
        type=str,
        default=None,
        help=f"Path to KENO CSV (default: {DEFAULT_PATHS['keno']})",
    )
    parser.add_argument(
        "--lotto",
        type=str,
        default=None,
        help=f"Path to Lotto CSV (default: {DEFAULT_PATHS['lotto']})",
    )
    parser.add_argument(
        "--eurojackpot",
        type=str,
        default=None,
        help=f"Path to EuroJackpot CSV (default: {DEFAULT_PATHS['eurojackpot']})",
    )
    parser.add_argument(
        "--use-defaults",
        action="store_true",
        help="Use default paths for all games",
    )

    # Output options
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="data/processed/timeline_grid.parquet",
        help="Output parquet path (default: data/processed/timeline_grid.parquet)",
    )
    parser.add_argument(
        "--mode",
        choices=["tuple", "matrix"],
        default="matrix",
        help="Export mode: 'tuple' (numbers as tuples) or 'matrix' (expanded columns)",
    )

    # Fill strategy
    parser.add_argument(
        "--fill-strategy",
        choices=["nan", "ffill"],
        default="nan",
        help="Strategy for non-draw days: 'nan' or 'ffill' (forward-fill)",
    )

    # Verbosity
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--json-summary",
        type=str,
        default=None,
        help="Path to save JSON summary (optional)",
    )

    return parser.parse_args()


def resolve_path(path: str | None, default: str, use_defaults: bool) -> str | None:
    """Resolve path with default fallback."""
    if path:
        return path
    if use_defaults:
        return default
    return None


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve paths
    keno_path = resolve_path(args.keno, DEFAULT_PATHS["keno"], args.use_defaults)
    lotto_path = resolve_path(args.lotto, DEFAULT_PATHS["lotto"], args.use_defaults)
    ej_path = resolve_path(
        args.eurojackpot, DEFAULT_PATHS["eurojackpot"], args.use_defaults
    )

    # Check that at least one game is specified
    if not any([keno_path, lotto_path, ej_path]):
        logger.error(
            "No game paths specified. Use --use-defaults or specify at least one path."
        )
        return 1

    # Validate paths exist
    for name, path in [("keno", keno_path), ("lotto", lotto_path), ("eurojackpot", ej_path)]:
        if path and not Path(path).exists():
            logger.error(f"{name.upper()} file not found: {path}")
            return 1

    # Load games
    logger.info("Building timeline grid...")
    logger.info(f"  Fill strategy: {args.fill_strategy}")
    logger.info(f"  Export mode: {args.mode}")

    try:
        grid = load_multi_game_grid(
            keno_path=keno_path,
            lotto_path=lotto_path,
            eurojackpot_path=ej_path,
            fill_strategy=args.fill_strategy,
        )
    except Exception as e:
        logger.error(f"Failed to load games: {e}")
        return 1

    # Print summary
    summary = grid.summary()
    logger.info(f"\nTimeline Grid Summary:")
    logger.info(f"  Date range: {summary['start_date']} to {summary['end_date']}")
    logger.info(f"  Total days: {summary['total_days']}")
    logger.info(f"  Games: {', '.join(summary['games'])}")

    # Print coverage
    coverage = grid.get_draw_coverage()
    logger.info(f"\nDraw Coverage:")
    for _, row in coverage.iterrows():
        logger.info(
            f"  {row['game']}: {row['draw_days']} draws "
            f"({row['coverage']:.1%} coverage, "
            f"{row['actual_weekly']:.1f}/week)"
        )

    # Export
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result_path = grid.to_parquet(output_path, mode=args.mode)
        logger.info(f"\nExported to: {result_path}")
    except Exception as e:
        logger.error(f"Failed to export: {e}")
        return 1

    # Optional JSON summary
    if args.json_summary:
        summary_path = Path(args.json_summary)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"Summary saved to: {summary_path}")

    logger.info("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
