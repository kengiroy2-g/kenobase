#!/usr/bin/env python
"""DIST-005: Distribution Pattern Synthesis CLI.

Synthesizes results from DIST-001/002/003/004 into a unified report.

Usage:
    python scripts/analyze_dist005.py
    python scripts/analyze_dist005.py --results-dir results/
    python scripts/analyze_dist005.py --output results/dist005_synthesis.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.analysis.distribution_synthesis import (
    export_synthesis_report,
    report_to_dict,
    run_synthesis,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Run the distribution synthesis analysis."""
    parser = argparse.ArgumentParser(
        description="DIST-005: Synthesize distribution pattern analysis results"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("results"),
        help="Directory containing DIST-001/002/003/004 results (default: results/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/dist005_synthesis.json"),
        help="Output path for synthesis report (default: results/dist005_synthesis.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    results_dir = args.results_dir
    if not results_dir.exists():
        logger.error(f"Results directory not found: {results_dir}")
        return 1

    logger.info(f"Running DIST-005 synthesis from {results_dir}")

    # Run synthesis
    report = run_synthesis(results_dir)

    # Export report
    export_synthesis_report(report, args.output)

    # Print summary
    print("\n" + "=" * 60)
    print("DIST-005: Distribution Pattern Synthesis")
    print("=" * 60)
    print(f"\nData Sources: {report.n_available}/{report.n_total} available")
    print("-" * 40)

    for src in report.sources:
        status = "OK" if src.available else "NO_DATA"
        score_str = f"{src.evidence_score:.2f}" if src.available else "N/A"
        print(f"  {src.source_id}: [{status}] score={score_str}")
        print(f"    {src.description}")

    print("-" * 40)
    print(f"\nOverall Evidence Score: {report.overall_evidence_score:.4f}")
    print(f"Verdict: {report.distribution_verdict}")
    print(f"\nOutput: {args.output}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
