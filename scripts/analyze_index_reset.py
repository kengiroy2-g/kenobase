#!/usr/bin/env python
"""HYP-005 Index-Reset Analysis Script: Index-Vorhersagekraft nach GK1.

This script tests whether the Index (appearance frequency since last GK1)
has predictive power for future draws.

Hypothesis: Numbers with high Index (frequent appearances since GK1)
appear more often in subsequent draws than low-Index numbers.
Acceptance Criteria: t-Test p < 0.05

Usage:
    python scripts/analyze_index_reset.py
    python scripts/analyze_index_reset.py --data-path data/raw/keno/KENO_ab_2018.csv
    python scripts/analyze_index_reset.py --gk1-path Keno_GPTs/10-9_KGDaten_gefiltert.csv
    python scripts/analyze_index_reset.py --output results/hyp005_index_reset.json
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

from kenobase.analysis.number_index import (
    CorrelationResult,
    calculate_index_correlation,
    calculate_index_table,
    export_index_table,
)
from kenobase.core.data_loader import DataLoader, GameType, GK1Summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Run HYP-005 Index-Reset analysis."""
    parser = argparse.ArgumentParser(
        description="HYP-005: Index-Reset nach GK1 - Vorhersagekraft-Analyse"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Path to KENO draw data",
    )
    parser.add_argument(
        "--gk1-path",
        type=str,
        default="Keno_GPTs/10-9_KGDaten_gefiltert.csv",
        help="Path to GK1 events data",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/hyp005_index_reset.json",
        help="Output path for results",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level (default: 0.05)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=11,
        help="Number of top-index numbers to track (default: 11)",
    )
    parser.add_argument(
        "--export-index-table",
        type=str,
        default=None,
        help="Optional: Export current index table to JSON",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Resolve paths relative to project root
    data_path = PROJECT_ROOT / args.data_path
    gk1_path = PROJECT_ROOT / args.gk1_path
    output_path = PROJECT_ROOT / args.output

    # Check data files exist
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        return 1

    if not gk1_path.exists():
        logger.error(f"GK1 file not found: {gk1_path}")
        return 1

    # Load KENO data
    logger.info(f"Loading KENO data from {data_path}")
    loader = DataLoader()
    draws = loader.load(data_path, game_type=GameType.KENO)
    logger.info(f"Loaded {len(draws)} draws")

    # Load GK1 events
    logger.info(f"Loading GK1 events from {gk1_path}")
    gk1_records: list[GK1Summary] = loader.load(gk1_path, game_type=GameType.GK1_SUMMARY)
    logger.info(f"Loaded {len(gk1_records)} GK1 events")

    if not gk1_records:
        logger.error("No GK1 events found - cannot perform analysis")
        return 1

    # Convert to format expected by number_index module
    # draws: list[tuple[datetime, list[int]]]
    draws_tuples: list[tuple[datetime, list[int]]] = [
        (d.date, d.numbers) for d in sorted(draws, key=lambda x: x.date)
    ]

    # gk1_events: list[tuple[datetime, int]]  (date, keno_typ)
    gk1_events: list[tuple[datetime, int]] = [
        (g.datum, g.keno_typ) for g in sorted(gk1_records, key=lambda x: x.datum)
    ]

    # Run correlation analysis
    logger.info(f"Running Index-Reset correlation analysis (top_n={args.top_n})...")
    correlation_result = calculate_index_correlation(
        draws=draws_tuples,
        gk1_events=gk1_events,
        number_range=70,
        top_n=args.top_n,
    )

    # Calculate current index table (for reference)
    index_result = calculate_index_table(
        draws=draws_tuples,
        gk1_events=gk1_events,
        number_range=70,
    )

    # Print report
    print("\n" + "=" * 70)
    print("HYP-005: Index-Reset nach GK1 - Vorhersagekraft-Analyse")
    print("=" * 70)
    print(f"\nDaten:")
    print(f"  - KENO-Ziehungen: {len(draws_tuples)}")
    print(f"  - GK1-Events: {len(gk1_events)}")
    print(f"  - Analysierte Segmente: {correlation_result.n_segments}")
    print(f"  - Top-N Parameter: {args.top_n}")

    print(f"\nAktueller Index-Status:")
    print(f"  - Letzter GK1-Reset: {index_result.last_reset_date}")
    print(f"  - Ziehungen seit Reset: {index_result.draws_since_reset}")
    print(f"  - GK1-Typ: Keno-{index_result.gk1_event_type}")

    # Top 10 current index
    sorted_indices = sorted(
        index_result.indices.values(),
        key=lambda x: x.current_index,
        reverse=True
    )[:10]
    print(f"\nTop 10 aktuelle Index-Zahlen:")
    for idx in sorted_indices:
        print(f"    Zahl {idx.number:2d}: Index = {idx.current_index}")

    print(f"\nStatistische Ergebnisse:")
    print(f"  - Korrelation: {correlation_result.correlation:.4f}")
    print(f"  - p-Value: {correlation_result.p_value:.6f}")
    print(f"  - Mean Hits (High-Index): {correlation_result.mean_hits_high_index:.3f}")
    print(f"  - Mean Hits (Low-Index): {correlation_result.mean_hits_low_index:.3f}")
    print(f"  - Effect Size (Cohen's d): {correlation_result.effect_size:.3f}")

    # Significance check
    is_significant = correlation_result.p_value < args.alpha
    has_effect = correlation_result.mean_hits_high_index > correlation_result.mean_hits_low_index

    print(f"\n--- Interpretation ---")
    print(correlation_result.interpretation)

    print(f"\n--- Conclusion ---")
    if is_significant and has_effect:
        print(f"EVIDENCE FOUND: p = {correlation_result.p_value:.6f} < {args.alpha}")
        print("Index has significant predictive power.")
        print("High-Index numbers appear more often than low-Index numbers.")
        verdict = "SUPPORTED"
    elif has_effect:
        print(f"WEAK TREND: p = {correlation_result.p_value:.6f} >= {args.alpha}")
        print("Trend visible but not statistically significant.")
        verdict = "INCONCLUSIVE"
    else:
        print(f"NO EVIDENCE: p = {correlation_result.p_value:.6f}")
        print("Index shows no predictive power.")
        print("Numbers appear randomly regardless of Index.")
        verdict = "NOT_SUPPORTED"

    print("=" * 70 + "\n")

    # Prepare output
    output_data = {
        "hypothesis": "HYP-005-INDEX",
        "description": "Index-Reset nach GK1 - Vorhersagekraft",
        "acceptance_criteria": f"t-Test p < {args.alpha}",
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "data_path": str(args.data_path),
            "gk1_path": str(args.gk1_path),
            "alpha": args.alpha,
            "top_n": args.top_n,
        },
        "data_summary": {
            "n_draws": len(draws_tuples),
            "n_gk1_events": len(gk1_events),
            "n_segments_analyzed": correlation_result.n_segments,
            "date_range": {
                "start": draws_tuples[0][0].isoformat() if draws_tuples else None,
                "end": draws_tuples[-1][0].isoformat() if draws_tuples else None,
            },
        },
        "current_index_status": {
            "last_reset_date": (
                index_result.last_reset_date.isoformat()
                if index_result.last_reset_date
                else None
            ),
            "draws_since_reset": index_result.draws_since_reset,
            "gk1_event_type": index_result.gk1_event_type,
            "top_10_indices": [
                {"number": idx.number, "index": idx.current_index}
                for idx in sorted_indices
            ],
        },
        "statistical_results": {
            "correlation": float(correlation_result.correlation),
            "p_value": float(correlation_result.p_value),
            "mean_hits_high_index": float(correlation_result.mean_hits_high_index),
            "mean_hits_low_index": float(correlation_result.mean_hits_low_index),
            "effect_size_cohens_d": float(correlation_result.effect_size),
            "is_significant": bool(is_significant),
        },
        "verdict": verdict,
        "interpretation": correlation_result.interpretation,
        "segment_details": correlation_result.segment_details,
    }

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Results saved to {output_path}")

    # Optionally export index table
    if args.export_index_table:
        index_table_path = PROJECT_ROOT / args.export_index_table
        export_index_table(index_result, str(index_table_path))
        logger.info(f"Index table exported to {index_table_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
