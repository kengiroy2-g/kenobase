#!/usr/bin/env python
"""DIST-003: Analyse-Script fuer Payout-Inference.

Fuehrt Reverse Engineering von Zahlen-Popularitaet aus Auszahlungsdaten durch.

Usage:
    python scripts/analyze_payout_inference.py --data Keno_GPTs/KENO_Quote_details_2023.csv
    python scripts/analyze_payout_inference.py --data Keno_GPTs/KENO_Quote_details_2023.csv \
        --draws data/raw/keno/KENO_ab_2018.csv --output results/payout_inference.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.analysis.payout_inference import (
    PayoutInferenceSummary,
    run_payout_inference,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def serialize_summary(summary: PayoutInferenceSummary) -> dict:
    """Serialisiert PayoutInferenceSummary zu JSON-kompatiblem Dict."""
    return {
        "n_draws": summary.n_draws,
        "low_popularity_count": summary.low_popularity_count,
        "high_popularity_count": summary.high_popularity_count,
        "normal_count": summary.normal_count,
        "anomaly_threshold": summary.anomaly_threshold,
        "low_popularity_rate": round(
            summary.low_popularity_count / summary.n_draws if summary.n_draws > 0 else 0, 4
        ),
        "high_popularity_rate": round(
            summary.high_popularity_count / summary.n_draws if summary.n_draws > 0 else 0, 4
        ),
        "number_rankings": [
            asdict(r) for r in summary.number_rankings[:20]  # Top 20
        ],
        "sample_low_popularity": [
            asdict(r) for r in summary.results if r.popularity_class == "LOW_POPULARITY"
        ][:10],
        "sample_high_popularity": [
            asdict(r) for r in summary.results if r.popularity_class == "HIGH_POPULARITY"
        ][:10],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Payout Inference Analysis")
    parser.add_argument(
        "--data",
        required=True,
        help="Path to KENO_Quote_details CSV",
    )
    parser.add_argument(
        "--draws",
        default=None,
        help="Optional: Path to KENO draws CSV for number aggregation",
    )
    parser.add_argument(
        "--output",
        default="results/payout_inference.json",
        help="Output path for results JSON",
    )
    parser.add_argument(
        "--anomaly-threshold",
        type=float,
        default=0.1,
        help="Anomaly threshold (relative deviation, default 0.1 = 10%%)",
    )
    parser.add_argument(
        "--z-threshold",
        type=float,
        default=-1.5,
        help="Z-score threshold for LOW_POPULARITY (default -1.5)",
    )

    args = parser.parse_args()

    # Verify input exists
    if not Path(args.data).exists():
        logger.error(f"Input file not found: {args.data}")
        return 1

    # Run analysis
    logger.info(f"Running payout inference on {args.data}")
    summary = run_payout_inference(
        quote_path=args.data,
        draws_path=args.draws,
        anomaly_threshold=args.anomaly_threshold,
        z_threshold=args.z_threshold,
    )

    # Print summary
    print("\n=== Payout Inference Summary ===")
    print(f"Total records analyzed: {summary.n_draws}")
    print(f"LOW_POPULARITY: {summary.low_popularity_count} ({100*summary.low_popularity_count/summary.n_draws:.1f}%)")
    print(f"HIGH_POPULARITY: {summary.high_popularity_count} ({100*summary.high_popularity_count/summary.n_draws:.1f}%)")
    print(f"NORMAL: {summary.normal_count} ({100*summary.normal_count/summary.n_draws:.1f}%)")

    if summary.number_rankings:
        print("\n=== Top 10 Unpopular Numbers ===")
        for i, nr in enumerate(summary.number_rankings[:10], 1):
            print(f"{i:2}. Number {nr.number:2}: ratio={nr.unpopularity_ratio:.4f} ({nr.low_popularity_count}/{nr.total_count})")

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serialize_summary(summary), f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
