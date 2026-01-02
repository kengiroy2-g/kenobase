#!/usr/bin/env python3
"""Analyze Cross-Game Timing - CLI Script.

This script implements STRAT-001: Cross-Game Timing Analysis
Based on TRANS-005 finding: Pattern->Timing paradigm shift validated.

Key Insight from Ecosystem Graph:
- Only 1 robust edge: KENO->AUSWAHLWETTE lag=7, lift=2.41
- Number-to-number couplings too weak for strategies
- Timing signals (WHEN to play) is the valid approach

Usage:
    python scripts/analyze_cross_game_timing.py \\
        --keno-file data/raw/keno/KENO_ab_2022_bereinigt.csv \\
        --output results/cross_game_timing.json

    python scripts/analyze_cross_game_timing.py --help
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

import numpy as np

from kenobase.core.data_loader import DataLoader
from kenobase.analysis.cross_game_timing import (
    run_cross_game_timing_analysis,
    compute_timing_signals,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def compute_keno_hits(draws: list, hit_threshold: int = 3) -> list[int]:
    """Compute binary hit indicator for KENO draws.

    A "hit" is defined as matching >= hit_threshold numbers with a
    reference pattern. For simplicity, we use consecutive appearance
    of numbers in top-20 as a proxy (stability indicator).

    Args:
        draws: List of DrawResult objects
        hit_threshold: Minimum matches to count as hit

    Returns:
        List of binary hit indicators (1=hit, 0=no hit)
    """
    hits = []
    prev_numbers = None

    for draw in draws:
        numbers = set(draw.numbers)
        if prev_numbers is not None:
            # Count overlap with previous draw
            overlap = len(numbers.intersection(prev_numbers))
            # Higher overlap indicates "stability" - potentially favorable
            hits.append(1 if overlap >= hit_threshold else 0)
        else:
            hits.append(0)
        prev_numbers = numbers

    return hits


def print_summary(result: dict) -> None:
    """Print human-readable summary."""
    print("\n" + "=" * 70)
    print("CROSS-GAME TIMING ANALYSIS - SUMMARY")
    print("=" * 70)

    print(f"\nTarget Game: {result['target_game']}")
    print(f"Total Dates Analyzed: {result['n_dates']}")
    print(f"Signals Tested: {result['signals_tested']}")
    print(f"Significant Signals: {result['significant_signals']}")
    print(f"Alpha Level: {result['alpha']}")
    print(f"Permutation Test: {'Yes' if result['permutation_test_used'] else 'No'}")

    print("\n--- AXIOM BASIS ---")
    for key, value in result.get("axiom_basis", {}).items():
        print(f"  {key}: {value}")

    print("\n--- TIMING SIGNAL RESULTS ---")
    for res in result.get("results", []):
        sig_name = res.get("signal_name", "unknown")
        improvement = res.get("hit_rate_improvement_pct", 0)
        p_value = res.get("p_value")
        is_sig = res.get("is_significant", False)
        is_sig_perm = res.get("is_significant_permutation", False)

        status = "***" if (is_sig or is_sig_perm) else ""

        print(f"\n  {sig_name} {status}")
        print(f"    Favorable days: {res.get('n_draws_favorable', 0)}")
        print(f"    Unfavorable days: {res.get('n_draws_unfavorable', 0)}")
        print(f"    Hit rate (favorable): {res.get('hit_rate_favorable', 0):.3f}")
        print(f"    Hit rate (unfavorable): {res.get('hit_rate_unfavorable', 0):.3f}")
        print(f"    Improvement: {improvement:+.1f}%")
        if p_value is not None:
            print(f"    Fisher p-value: {p_value:.4f}")

        perm = res.get("permutation_test")
        if perm:
            print(f"    Permutation p-value: {perm.get('p_value', 'N/A'):.4f}")
            print(f"    Observed diff: {perm.get('observed_stat', 0):.4f}")
            print(f"    Null mean: {perm.get('null_mean', 0):.4f} +/- {perm.get('null_std', 0):.4f}")

    # Highlight key finding from ecosystem graph
    aw_results = [r for r in result.get("results", [])
                  if "auswahlwette" in r.get("signal_name", "").lower()]

    if aw_results:
        print("\n" + "-" * 70)
        print("KEY FINDING (from Ecosystem Graph: KENO->AUSWAHLWETTE lag=7):")
        for aw in aw_results:
            print(f"  Signal: {aw.get('signal_name')}")
            print(f"  Hit Rate Improvement: {aw.get('hit_rate_improvement_pct', 0):+.1f}%")
            if aw.get("is_significant_permutation"):
                print("  Status: SIGNIFICANT (validated by permutation test)")
            else:
                print("  Status: Not significant at alpha=0.05")

    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cross-Game Timing Analysis (STRAT-001)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Based on TRANS-005 / Ecosystem Graph finding:
- Only 1 robust cross-game edge: KENO->AUSWAHLWETTE lag=7, lift=2.41
- Pattern-based strategies failed FDR validation (delta_mean_hits=0.0)
- Timing-based approach (WHEN to play) is the validated paradigm

Examples:
    python scripts/analyze_cross_game_timing.py \\
        -k data/raw/keno/KENO_ab_2022_bereinigt.csv

    python scripts/analyze_cross_game_timing.py \\
        -k data/raw/keno/KENO_ab_2022_bereinigt.csv \\
        -o results/cross_game_timing.json \\
        --permutations 2000
        """,
    )
    parser.add_argument(
        "-k", "--keno-file",
        required=True,
        help="Path to KENO CSV file",
    )
    parser.add_argument(
        "-o", "--output",
        default="results/cross_game_timing.json",
        help="Output JSON file (default: results/cross_game_timing.json)",
    )
    parser.add_argument(
        "--hit-threshold",
        type=int,
        default=6,
        help="Overlap threshold for 'hit' definition (default: 6)",
    )
    parser.add_argument(
        "--permutations",
        type=int,
        default=1000,
        help="Number of permutations for null model (default: 1000)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level (default: 0.05)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load KENO data
    logger.info(f"Loading KENO data from {args.keno_file}")
    loader = DataLoader()
    draws = loader.load(args.keno_file)
    logger.info(f"Loaded {len(draws)} draws")

    # Sort by date
    draws = sorted(draws, key=lambda d: d.date)

    # Extract dates and compute hits
    dates = [d.date.date() if hasattr(d.date, 'date') else d.date for d in draws]
    hits = compute_keno_hits(draws, hit_threshold=args.hit_threshold)

    logger.info(f"Computed hits: {sum(hits)}/{len(hits)} ({sum(hits)/len(hits)*100:.1f}%)")

    # Run analysis
    logger.info("Running cross-game timing analysis...")
    result = run_cross_game_timing_analysis(
        keno_dates=dates,
        keno_hits=hits,
        signal_names=None,  # Use defaults
        use_permutation_test=True,
        n_permutations=args.permutations,
        alpha=args.alpha,
        seed=args.seed,
    )

    # Add metadata
    result["generated_at"] = datetime.now().isoformat()
    result["keno_file"] = str(args.keno_file)
    result["hit_threshold"] = args.hit_threshold
    result["seed"] = args.seed

    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    logger.info(f"Results saved to {args.output}")

    # Print summary
    print_summary(result)

    # Return for programmatic use
    return result


if __name__ == "__main__":
    main()
