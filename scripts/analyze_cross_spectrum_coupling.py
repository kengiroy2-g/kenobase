#!/usr/bin/env python3
"""CLI for cross-spectrum coupling analysis between lottery games.

Usage:
    python scripts/analyze_cross_spectrum_coupling.py \
        --keno data/keno_draws.csv \
        --lotto data/lotto_draws.csv \
        --output results/cross_spectrum_coupling.json

This script performs spectral coupling analysis (CPSD, coherence, phase-locking)
between lottery games to detect inverse/periodic correlations.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.analysis.cross_lottery_coupling import GameDraws
from kenobase.analysis.cross_spectrum_coupling import (
    DEFAULT_BANDS,
    FrequencyBand,
    run_cross_spectrum_analysis,
    to_jsonable,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_game_from_csv(
    filepath: Path,
    name: str,
    pool_max: int,
    draw_size: int,
    date_col: str = "date",
    numbers_col: Optional[str] = None,
    number_cols: Optional[list[str]] = None,
) -> GameDraws:
    """Load game draws from CSV file.

    Args:
        filepath: Path to CSV file
        name: Game name
        pool_max: Maximum number in pool (e.g., 70 for KENO)
        draw_size: Number of drawn numbers per draw
        date_col: Name of date column
        numbers_col: Column containing comma-separated numbers (alternative)
        number_cols: List of columns containing individual numbers

    Returns:
        GameDraws object
    """
    df = pd.read_csv(filepath)

    # Parse dates
    df[date_col] = pd.to_datetime(df[date_col])
    dates = [d.date() for d in df[date_col]]

    # Build presence matrix
    n_draws = len(df)
    presence = np.zeros((n_draws, pool_max + 1), dtype=np.int8)

    ordered_numbers: Optional[list[list[int]]] = None

    if numbers_col and numbers_col in df.columns:
        # Numbers in single column as comma-separated
        for i, row in df.iterrows():
            nums_str = str(row[numbers_col])
            nums = [int(x.strip()) for x in nums_str.split(",") if x.strip().isdigit()]
            for n in nums:
                if 1 <= n <= pool_max:
                    presence[i, n] = 1
    elif number_cols:
        # Numbers in separate columns
        for i, row in df.iterrows():
            for col in number_cols:
                if col in df.columns:
                    try:
                        n = int(row[col])
                        if 1 <= n <= pool_max:
                            presence[i, n] = 1
                    except (ValueError, TypeError):
                        continue
    else:
        # Auto-detect: look for columns named z1-z20 or n1-n6 etc.
        num_cols = [c for c in df.columns if c.lower().startswith(("z", "n", "zahl"))]
        if num_cols:
            ordered: list[list[int]] = []
            for i, row in df.iterrows():
                draw_nums = []
                for col in sorted(num_cols):
                    try:
                        n = int(row[col])
                        if 1 <= n <= pool_max:
                            presence[i, n] = 1
                            draw_nums.append(n)
                    except (ValueError, TypeError):
                        continue
                ordered.append(draw_nums)
            ordered_numbers = ordered

    return GameDraws(
        name=name,
        pool_max=pool_max,
        draw_size=draw_size,
        dates=dates,
        presence=presence,
        ordered_numbers=ordered_numbers,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-spectrum coupling analysis between lottery games",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Data inputs
    parser.add_argument(
        "--keno",
        type=Path,
        help="Path to KENO draws CSV",
    )
    parser.add_argument(
        "--lotto",
        type=Path,
        help="Path to Lotto 6aus49 draws CSV",
    )
    parser.add_argument(
        "--eurojackpot",
        type=Path,
        help="Path to EuroJackpot draws CSV (negative control)",
    )

    # Output
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("results/cross_spectrum_coupling.json"),
        help="Output JSON path (default: results/cross_spectrum_coupling.json)",
    )

    # Analysis parameters
    parser.add_argument(
        "--representations",
        nargs="+",
        default=["centroid", "sum", "mean"],
        choices=["sum", "mean", "centroid", "presence_vector", "normalized_vector"],
        help="Time series representations to analyze",
    )
    parser.add_argument(
        "--n-surrogates",
        type=int,
        default=199,
        help="Number of surrogates for significance testing (default: 199)",
    )
    parser.add_argument(
        "--surrogate-type",
        choices=["phase", "block"],
        default="phase",
        help="Surrogate type for null distribution (default: phase)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="FDR significance threshold (default: 0.05)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    # Frequency bands
    parser.add_argument(
        "--band-weekly",
        action="store_true",
        default=True,
        help="Include weekly frequency band",
    )
    parser.add_argument(
        "--band-biweekly",
        action="store_true",
        default=True,
        help="Include biweekly frequency band",
    )
    parser.add_argument(
        "--band-monthly",
        action="store_true",
        default=True,
        help="Include monthly frequency band",
    )

    args = parser.parse_args()

    # Collect games
    games: list[GameDraws] = []

    if args.keno and args.keno.exists():
        logger.info(f"Loading KENO from {args.keno}")
        keno = load_game_from_csv(args.keno, "KENO", pool_max=70, draw_size=20)
        logger.info(f"  Loaded {len(keno.dates)} KENO draws")
        games.append(keno)

    if args.lotto and args.lotto.exists():
        logger.info(f"Loading Lotto from {args.lotto}")
        lotto = load_game_from_csv(args.lotto, "LOTTO", pool_max=49, draw_size=6)
        logger.info(f"  Loaded {len(lotto.dates)} Lotto draws")
        games.append(lotto)

    if args.eurojackpot and args.eurojackpot.exists():
        logger.info(f"Loading EuroJackpot from {args.eurojackpot}")
        ej = load_game_from_csv(args.eurojackpot, "EuroJackpot", pool_max=50, draw_size=5)
        logger.info(f"  Loaded {len(ej.dates)} EuroJackpot draws")
        games.append(ej)

    if len(games) < 2:
        logger.error("Need at least 2 games for coupling analysis")
        logger.info("Provide at least two of: --keno, --lotto, --eurojackpot")
        return 1

    # Build frequency bands
    bands = DEFAULT_BANDS  # Use default bands

    # Run analysis
    logger.info(f"Running cross-spectrum analysis...")
    logger.info(f"  Games: {[g.name for g in games]}")
    logger.info(f"  Representations: {args.representations}")
    logger.info(f"  Surrogates: {args.n_surrogates} ({args.surrogate_type})")
    logger.info(f"  Alpha FDR: {args.alpha}")

    summary = run_cross_spectrum_analysis(
        games=games,
        representations=args.representations,
        bands=bands,
        n_surrogates=args.n_surrogates,
        surrogate_type=args.surrogate_type,
        alpha_fdr=args.alpha,
        negative_control_games=["EuroJackpot"],
        seed=args.seed,
    )

    # Output summary
    logger.info(f"Analysis complete:")
    logger.info(f"  Total results: {len(summary.results)}")
    logger.info(f"  Significant (non-control): {summary.significant_count}")
    logger.info(f"  Negative control significant: {summary.negative_control_significant}")

    if summary.negative_control_significant > 0:
        logger.warning(
            f"  WARNING: {summary.negative_control_significant} negative control results "
            f"are significant - may indicate FDR issues"
        )

    # Save results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output_data = to_jsonable(summary)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, default=str)

    logger.info(f"Results saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
