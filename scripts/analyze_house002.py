#!/usr/bin/env python
"""HOUSE-002 Analysis Script: High-Stake Draws and Unpopular Numbers.

Tests the hypothesis that high-stake draws favor unpopular numbers (numbers
that are less frequently chosen by players).

Hypothesis: When Spieleinsatz is high (top 25%), the RNG systematically draws
more unpopular numbers (below-median popularity).

Acceptance Criteria:
- Spearman |r| > 0.15 with p < 0.05 for high-stake subset

Usage:
    python scripts/analyze_house002.py
    python scripts/analyze_house002.py --output results/custom_output.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.popularity_correlation import (
    calculate_popularity_scores_heuristic,
)
from kenobase.analysis.stake_correlation import (
    analyze_high_stake_popularity_bias,
    load_stake_data,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> int:
    """Run HOUSE-002 analysis."""
    parser = argparse.ArgumentParser(
        description="HOUSE-002: High-stake draws vs unpopular numbers analysis"
    )
    parser.add_argument(
        "--stake-file",
        type=str,
        default="Keno_GPTs/Keno_Ziehung2023_+_Restbetrag_v2.CSV",
        help="Path to stake data file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/house002_stake_popularity.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--percentile",
        type=float,
        default=0.75,
        help="Percentile threshold for high-stake (default: 0.75 = top 25%%)",
    )
    parser.add_argument(
        "--correlation-threshold",
        type=float,
        default=0.15,
        help="Minimum |r| for hypothesis support (default: 0.15)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Resolve paths
    stake_path = project_root / args.stake_file
    output_path = project_root / args.output

    logger.info("=" * 60)
    logger.info("HOUSE-002: High-Stake Draws vs Unpopular Numbers")
    logger.info("=" * 60)

    # Check input file exists
    if not stake_path.exists():
        logger.error(f"Stake file not found: {stake_path}")
        return 1

    # Load stake data
    logger.info(f"Loading stake data from: {stake_path}")
    stake_records = load_stake_data(stake_path)

    if not stake_records:
        logger.error("Failed to load stake data")
        return 1

    logger.info(f"Loaded {len(stake_records)} stake records")

    # Calculate popularity scores (heuristic method)
    logger.info("Calculating popularity scores (heuristic: birthday + schoene Zahlen)")
    popularity_scores = calculate_popularity_scores_heuristic(range(1, 71))

    # Run HOUSE-002 analysis
    logger.info(
        f"Running analysis (percentile={args.percentile}, "
        f"threshold={args.correlation_threshold})"
    )
    result = analyze_high_stake_popularity_bias(
        stake_records=stake_records,
        popularity_scores=popularity_scores,
        high_stake_percentile=args.percentile,
        correlation_threshold=args.correlation_threshold,
    )

    # Build output (ensure all values are JSON-serializable)
    result_dict = asdict(result)
    # Convert numpy/bool types to Python native types
    for key, value in result_dict.items():
        if hasattr(value, "item"):  # numpy scalar
            result_dict[key] = value.item()
        elif isinstance(value, bool):
            result_dict[key] = bool(value)

    output = {
        "hypothesis": "HOUSE-002",
        "description": "High-stake draws favor unpopular numbers",
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "stake_file": str(stake_path),
            "high_stake_percentile": args.percentile,
            "correlation_threshold": args.correlation_threshold,
        },
        "result": result_dict,
        "acceptance_criteria": {
            "required_r": f"|r| > {args.correlation_threshold}",
            "required_p": "p < 0.05",
        },
        "verdict": {
            "is_significant": bool(result.is_significant),
            "supports_hypothesis": bool(result.supports_hypothesis),
            "conclusion": (
                "SUPPORTED: High-stake draws show significant correlation with unpopular numbers"
                if result.supports_hypothesis
                else "NOT SUPPORTED: No significant correlation detected"
            ),
        },
    }

    # Print summary
    print("\n" + "=" * 60)
    print("HOUSE-002 ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Data source: {stake_path.name}")
    print(f"Records analyzed: {result.n_draws}")
    print(f"High-stake draws (top 25%): {result.n_high_stake}")
    print(f"High-stake threshold: {result.high_stake_threshold:,.0f} EUR")
    print()
    print("CORRELATION RESULTS:")
    print(f"  Spearman r: {result.spearman_r:.4f}")
    print(f"  p-value: {result.spearman_p:.4f}")
    print(f"  Significant (p < 0.05): {result.is_significant}")
    print()
    print("UNPOPULAR NUMBER RATIOS:")
    print(f"  High-stake draws: {result.mean_unpopular_ratio_high:.3f}")
    print(f"  Low-stake draws: {result.mean_unpopular_ratio_low:.3f}")
    print(f"  Difference: {result.mean_unpopular_ratio_high - result.mean_unpopular_ratio_low:+.3f}")
    print()
    print("VERDICT:")
    if result.supports_hypothesis:
        print("  [SUPPORTED] High-stake draws favor unpopular numbers")
        print(f"  Correlation |r|={abs(result.spearman_r):.4f} > {args.correlation_threshold}")
    else:
        print("  [NOT SUPPORTED] No significant correlation detected")
        if not result.is_significant:
            print(f"  p-value {result.spearman_p:.4f} >= 0.05 (not significant)")
        else:
            print(f"  |r|={abs(result.spearman_r):.4f} <= {args.correlation_threshold} (weak effect)")
    print("=" * 60)

    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
