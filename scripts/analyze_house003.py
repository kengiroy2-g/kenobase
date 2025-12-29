#!/usr/bin/env python
"""HOUSE-003 Analysis Script: Rolling House-Edge Stability.

Tests the hypothesis that Keno Restbetrag (house edge) shows suspiciously low
variance over rolling windows, indicating active payout management.

Hypothesis: CV (Coefficient of Variation) < 15% on at least 2 of 3 windows
(7/14/30 days) indicates active payout control.

Acceptance Criteria:
- CV < 15% on at least 2 of 3 windows indicates SUPPORTED

Usage:
    python scripts/analyze_house003.py
    python scripts/analyze_house003.py --output results/custom_output.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.house_edge_stability import (
    CV_STABILITY_THRESHOLD,
    DEFAULT_WINDOWS,
    result_to_dict,
    run_house003_analysis,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> int:
    """Run HOUSE-003 analysis."""
    parser = argparse.ArgumentParser(
        description="HOUSE-003: Rolling House-Edge Stability Analysis"
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
        default="results/house003_rolling_stability.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--cv-threshold",
        type=float,
        default=CV_STABILITY_THRESHOLD,
        help=f"CV threshold for stability (default: {CV_STABILITY_THRESHOLD})",
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
    logger.info("HOUSE-003: Rolling House-Edge Stability Analysis")
    logger.info("=" * 60)

    # Check input file exists
    if not stake_path.exists():
        logger.error(f"Stake file not found: {stake_path}")
        return 1

    # Run analysis
    logger.info(f"Loading stake data from: {stake_path}")
    result = run_house003_analysis(
        stake_path=stake_path,
        windows=DEFAULT_WINDOWS,
        cv_threshold=args.cv_threshold,
    )

    if result.n_records == 0:
        logger.error("Failed to load or analyze stake data")
        return 1

    logger.info(f"Analyzed {result.n_records} records")

    # Build output
    output = {
        "hypothesis": "HOUSE-003",
        "description": "Rolling House-Edge Stability via CV over 7/14/30 day windows",
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "stake_file": str(stake_path),
            "windows": DEFAULT_WINDOWS,
            "cv_threshold": args.cv_threshold,
        },
        "result": result_to_dict(result),
        "acceptance_criteria": {
            "cv_threshold": f"CV < {args.cv_threshold * 100:.0f}%",
            "minimum_stable_windows": "2 of 3",
        },
        "verdict": {
            "stable_count": result.stable_count,
            "total_windows": result.total_windows,
            "hypothesis_supported": result.hypothesis_supported,
            "conclusion": (
                "SUPPORTED: Low variance in Restbetrag indicates active payout control"
                if result.hypothesis_supported
                else "NOT SUPPORTED: Variance is within expected random range"
            ),
        },
    }

    # Print summary
    print("\n" + "=" * 60)
    print("HOUSE-003 ANALYSIS RESULTS")
    print("=" * 60)
    print(f"Data source: {stake_path.name}")
    print(f"Records analyzed: {result.n_records}")
    print(
        f"Date range: {result.date_range_start.strftime('%Y-%m-%d')} to "
        f"{result.date_range_end.strftime('%Y-%m-%d')}"
    )
    print(f"Field analyzed: {result.field_analyzed}")
    print()
    print(f"CV Threshold: {args.cv_threshold * 100:.0f}%")
    print()
    print("ROLLING WINDOW RESULTS:")
    for ws in sorted(result.windows.keys()):
        wr = result.windows[ws]
        status = "STABLE" if wr.is_stable else "UNSTABLE"
        print(f"  {ws:2d}-day window:")
        print(f"    CV mean: {wr.cv_mean * 100:6.2f}%")
        print(f"    CV std:  {wr.cv_std * 100:6.2f}%")
        print(f"    CV range: [{wr.cv_min * 100:.2f}%, {wr.cv_max * 100:.2f}%]")
        print(f"    N windows: {wr.n_windows}")
        print(f"    Status: [{status}]")
        print()
    print("VERDICT:")
    print(f"  Stable windows: {result.stable_count}/{result.total_windows}")
    if result.hypothesis_supported:
        print("  [SUPPORTED] Low variance indicates active payout control")
    else:
        print("  [NOT SUPPORTED] Variance is within expected random range")
    print("=" * 60)

    # Save output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
