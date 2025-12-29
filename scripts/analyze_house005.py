#!/usr/bin/env python
"""HOUSE-005 Analysis Script: House-Edge Manipulation Synthesis.

Synthesizes results from HOUSE-001/002/003/004 into a unified report with
an overall evidence score for house-edge manipulation.

Dependencies:
- results/hyp015_jackpot_correlation.json (HOUSE-001)
- results/house002_stake_popularity.json (HOUSE-002)
- results/house003_rolling_stability.json (HOUSE-003)
- results/house004_near_miss_jackpot.json (HOUSE-004)

Usage:
    python scripts/analyze_house005.py
    python scripts/analyze_house005.py --results-dir path/to/results
    python scripts/analyze_house005.py --output results/custom_output.json
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.house_edge_synthesis import (
    DEFAULT_WEIGHTS,
    export_synthesis_report,
    run_synthesis,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> int:
    """Run HOUSE-005 synthesis."""
    parser = argparse.ArgumentParser(
        description="HOUSE-005: House-Edge Manipulation Synthesis"
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Path to results directory containing hypothesis JSON files",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/house005_synthesis_report.json",
        help="Output JSON file path",
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
    results_dir = project_root / args.results_dir
    output_path = project_root / args.output

    logger.info("=" * 70)
    logger.info("HOUSE-005: House-Edge Manipulation Synthesis")
    logger.info("=" * 70)

    # Check results directory exists
    if not results_dir.exists():
        logger.error(f"Results directory not found: {results_dir}")
        return 1

    # Check for required input files
    required_files = [
        "hyp015_jackpot_correlation.json",
        "house002_stake_popularity.json",
        "house003_rolling_stability.json",
        "house004_near_miss_jackpot.json",
    ]

    missing = []
    for fname in required_files:
        if not (results_dir / fname).exists():
            missing.append(fname)
            logger.warning(f"Missing: {fname}")

    if missing:
        logger.warning(f"Missing {len(missing)} input files - synthesis may be incomplete")

    # Run synthesis
    logger.info(f"Loading results from: {results_dir}")
    report = run_synthesis(results_dir)

    if not report.hypotheses:
        logger.error("No hypothesis results could be loaded")
        return 1

    # Print summary
    print("\n" + "=" * 70)
    print("HOUSE-005 SYNTHESIS REPORT")
    print("=" * 70)
    print(f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Hypotheses loaded: {report.n_total}")
    print(f"Hypotheses supported: {report.n_supported}")
    print()
    print("INDIVIDUAL RESULTS:")
    print("-" * 70)
    print(f"{'Hypothesis':<12} {'Description':<40} {'Supported':<10} {'Score':<8}")
    print("-" * 70)

    for hyp in report.hypotheses:
        status = "YES" if hyp.supported else "NO"
        print(f"{hyp.hypothesis_id:<12} {hyp.description:<40} {status:<10} {hyp.evidence_score:<8.4f}")

    print("-" * 70)
    print()
    print("WEIGHTS APPLIED:")
    for hyp_id, weight in DEFAULT_WEIGHTS.items():
        print(f"  {hyp_id}: {weight:.0%}")
    print()
    print("OVERALL EVIDENCE SCORE:")
    print(f"  Score: {report.overall_evidence_score:.4f}")
    print()
    print("VERDICT:")
    print(f"  {report.manipulation_verdict}")
    print()

    # Interpretation
    print("INTERPRETATION:")
    print("-" * 70)
    if report.overall_evidence_score >= 0.5:
        print("  The data shows indicators that warrant further investigation.")
        print("  However, this is NOT proof of manipulation - only statistical anomalies.")
    else:
        print("  The data is consistent with fair random draws.")
        print("  No significant evidence of systematic manipulation detected.")
    print("=" * 70)

    # Export report
    export_synthesis_report(report, output_path)
    logger.info(f"Synthesis report saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
