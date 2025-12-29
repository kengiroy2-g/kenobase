#!/usr/bin/env python
"""HYP-004 Analysis Script: Inverse Korrelation beliebte vs. gezogene Zahlen.

This script tests whether popular numbers (frequently played by users)
are inversely correlated with drawn numbers.

Hypothesis: If RNG avoids popular numbers, we expect r < -0.2 with p < 0.05.

Usage:
    python scripts/analyze_hyp004.py --window 30
    python scripts/analyze_hyp004.py --gq-path Keno_GPTs/Keno_GQ_2022_2023-2024.csv
    python scripts/analyze_hyp004.py --output data/results/hyp004_correlation.json
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

from kenobase.analysis.popularity_correlation import (
    PopularityResult,
    run_hyp004_analysis,
)
from kenobase.core.data_loader import DataLoader, GameType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Run HYP-004 analysis."""
    parser = argparse.ArgumentParser(
        description="HYP-004: Inverse Korrelation beliebte vs. gezogene Zahlen"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Path to KENO draw data",
    )
    parser.add_argument(
        "--gq-path",
        type=str,
        default="Keno_GPTs/Keno_GQ_2022_2023-2024.csv",
        help="Path to Gewinnquoten data (optional, uses heuristic if not found)",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=30,
        help="Rolling window size for walk-forward validation (default: 30)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/results/hyp004_correlation.json",
        help="Output path for results",
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
    gq_path = PROJECT_ROOT / args.gq_path if args.gq_path else None
    output_path = PROJECT_ROOT / args.output

    # Check data file exists
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        return 1

    # Load KENO data
    logger.info(f"Loading KENO data from {data_path}")
    loader = DataLoader()
    draws = loader.load(data_path, game_type=GameType.KENO)
    logger.info(f"Loaded {len(draws)} draws")

    # Sort by date
    draws = sorted(draws, key=lambda d: d.date)

    # Check GQ path
    if gq_path and not gq_path.exists():
        logger.warning(f"GQ file not found: {gq_path}, using heuristic")
        gq_path = None

    # Run analysis
    logger.info("Running HYP-004 analysis...")
    results = run_hyp004_analysis(
        draws=draws,
        gq_path=gq_path,
        window=args.window,
        number_range=(1, 70),
    )

    # Extract key results
    overall: PopularityResult = results["overall"]
    summary = results["summary"]

    # Print results
    print("\n" + "=" * 60)
    print("HYP-004 Analysis Results")
    print("=" * 60)
    print(f"\nMethod: {summary['method']}")
    print(f"Draws analyzed: {summary['n_draws']}")
    print(f"Window size: {summary['window_size']}")
    print(f"Rolling windows: {summary['n_windows']}")

    print("\n--- Overall Correlation ---")
    print(f"Spearman r: {overall.correlation:.4f}")
    print(f"P-value: {overall.p_value:.4f}")
    print(f"Significant (p < 0.05): {overall.is_significant}")
    print(f"Supports HYP-004 (r < -0.2, p < 0.05): {overall.supports_hypothesis}")

    if summary.get("n_windows", 0) > 0:
        print("\n--- Rolling Window Summary ---")
        print(f"Mean correlation: {summary['mean_correlation']:.4f}")
        print(f"Std correlation: {summary['std_correlation']:.4f}")
        print(f"Min correlation: {summary['min_correlation']:.4f}")
        print(f"Max correlation: {summary['max_correlation']:.4f}")
        print(f"Significant windows: {summary['significant_windows']}/{summary['n_windows']} ({summary['significant_ratio']:.1%})")
        print(f"Supporting windows: {summary['supporting_windows']}/{summary['n_windows']} ({summary['support_ratio']:.1%})")

    print("\n--- Conclusion ---")
    if overall.supports_hypothesis:
        print("EVIDENCE FOUND: HYP-004 is supported by the data.")
        print("There is a significant inverse correlation between popular and drawn numbers.")
    else:
        if overall.correlation < -0.2:
            print("WEAK EVIDENCE: Negative correlation found but not statistically significant.")
        elif overall.correlation > 0:
            print("NO EVIDENCE: Positive correlation found (opposite of hypothesis).")
        else:
            print("NO EVIDENCE: Correlation is near zero, no relationship detected.")

    print("=" * 60 + "\n")

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Helper to convert numpy types to native Python
    def to_json_serializable(obj):
        """Convert numpy types to native Python types."""
        import numpy as np
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            return float(obj)
        if isinstance(obj, dict):
            return {k: to_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_json_serializable(v) for v in obj]
        return obj

    # Convert results to JSON-serializable format
    output_data = {
        "hypothesis": "HYP-004",
        "description": "Inverse Korrelation beliebte vs. gezogene Zahlen",
        "acceptance_criteria": "r < -0.2 with p < 0.05",
        "timestamp": datetime.now().isoformat(),
        "overall": {
            "correlation": float(overall.correlation),
            "p_value": float(overall.p_value),
            "is_significant": bool(overall.is_significant),
            "supports_hypothesis": bool(overall.supports_hypothesis),
            "n_samples": int(overall.n_samples),
            "method": str(overall.method),
        },
        "summary": to_json_serializable(summary),
        "rolling_correlations": [
            {
                "date": r.date.isoformat(),
                "correlation": float(r.correlation),
                "p_value": float(r.p_value),
            }
            for r in results["rolling"]
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")

    return 0 if not overall.supports_hypothesis else 0  # Always success, just reporting


if __name__ == "__main__":
    sys.exit(main())
