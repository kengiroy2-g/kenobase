#!/usr/bin/env python3
"""Analyze correlations between KENO ticket types for portfolio diversification.

This script analyzes the 4 tickets from SYSTEM_STATUS.json (Typ-2, -6, -8, -10)
and outputs correlation metrics to help with portfolio diversification decisions.

NOTE: All tickets have negative ROI (-43% to -67%). This analysis is for
diversification purposes only, not for finding profitable combinations.

Usage:
    python scripts/analyze_ticket_correlation.py
    python scripts/analyze_ticket_correlation.py --output results/ticket_correlation.json

Author: EXECUTOR (TASK_034)
Date: 2025-12-30
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.ticket_correlation import (
    TicketCorrelationResult,
    analyze_ticket_correlation,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Tickets from SYSTEM_STATUS.json
SYSTEM_STATUS_TICKETS: dict[int, tuple[int, ...]] = {
    2: (9, 50),
    6: (3, 24, 40, 49, 51, 64),
    8: (2, 3, 20, 24, 36, 49, 51, 64),
    10: (2, 3, 9, 24, 33, 36, 49, 50, 51, 64),
}


def analyze_tickets() -> TicketCorrelationResult:
    """Analyze correlations between SYSTEM_STATUS tickets.

    Returns:
        TicketCorrelationResult with all pair correlations
    """
    logger.info("Analyzing ticket correlations...")
    logger.info(f"Tickets: {list(SYSTEM_STATUS_TICKETS.keys())}")

    # For now, we only analyze overlap (no backtest data available)
    # Future: integrate with ticket_backtester.py results
    result = analyze_ticket_correlation(
        tickets=SYSTEM_STATUS_TICKETS,
        backtest_results=None,  # No ROI/timing data available yet
        apply_fdr=True,
        fdr_alpha=0.05,
    )

    return result


def print_summary(result: TicketCorrelationResult) -> None:
    """Print human-readable summary to stdout."""
    print("\n" + "=" * 60)
    print("TICKET CORRELATION ANALYSIS")
    print("=" * 60)
    print(f"Tickets analyzed: {result.n_tickets}")
    print(f"Pairs analyzed: {result.n_pairs}")
    print(f"Generated at: {result.generated_at}")
    print()

    print("--- OVERLAP ANALYSIS (Jaccard Similarity) ---")
    for pc in result.pair_correlations:
        pair_name = f"Typ-{pc.pair.ticket_a_type} vs Typ-{pc.pair.ticket_b_type}"
        shared = set(pc.pair.ticket_a_numbers) & set(pc.pair.ticket_b_numbers)
        print(
            f"  {pair_name}: Jaccard={pc.overlap.jaccard_index:.3f} "
            f"(shared: {sorted(shared) if shared else 'none'})"
        )
    print()

    print("--- DIVERSIFICATION SCORES ---")
    for pc in sorted(
        result.pair_correlations,
        key=lambda x: x.diversification_score,
        reverse=True,
    ):
        pair_name = f"Typ-{pc.pair.ticket_a_type} vs Typ-{pc.pair.ticket_b_type}"
        score = pc.diversification_score
        quality = "HIGH" if score >= 0.7 else "MEDIUM" if score >= 0.5 else "LOW"
        print(f"  {pair_name}: {score:.3f} ({quality})")
    print()

    if result.best_diversification_pair:
        print(
            f"Best diversification: Typ-{result.best_diversification_pair[0]} + "
            f"Typ-{result.best_diversification_pair[1]}"
        )
    if result.worst_diversification_pair:
        print(
            f"Most correlated: Typ-{result.worst_diversification_pair[0]} + "
            f"Typ-{result.worst_diversification_pair[1]}"
        )

    print()
    print("NOTE: All tickets have negative ROI. Analysis is for diversification only.")
    print("=" * 60)


def save_result(result: TicketCorrelationResult, output_path: Path) -> None:
    """Save result to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "analysis": "ticket_correlation",
        "description": "Correlation analysis for portfolio diversification",
        "note": "All tickets have negative ROI (-43% to -67%). Diversification only.",
        **result.to_dict(),
    }

    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(f"Saved result to {output_path}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze KENO ticket correlations for portfolio diversification"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "results" / "ticket_correlation.json",
        help="Output JSON path (default: results/ticket_correlation.json)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress summary output",
    )

    args = parser.parse_args()

    try:
        result = analyze_tickets()

        if not args.quiet:
            print_summary(result)

        save_result(result, args.output)

        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
