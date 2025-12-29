#!/usr/bin/env python3
"""HYP-010 Analysis Script: Odds-Winner Correlation.

Tests hypothesis that winner counts correlate with drawn numbers,
identifying "safe" vs "popular" numbers.

Usage:
    python scripts/analyze_hyp010.py
    python scripts/analyze_hyp010.py --gq-file path/to/gq.csv --draws-file path/to/draws.csv
    python scripts/analyze_hyp010.py --output results/hyp010_custom.json
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

from kenobase.analysis.odds_correlation import (
    OddsAnalysisSummary,
    run_hyp010_analysis,
)
from kenobase.core.data_loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def format_result(summary: OddsAnalysisSummary) -> dict:
    """Format analysis result for JSON output.

    Args:
        summary: Analysis summary

    Returns:
        JSON-serializable dict
    """
    corr = summary.correlation

    return {
        "hypothesis": "HYP-010",
        "description": "Odds-Winner Correlation Analysis",
        "timestamp": datetime.now().isoformat(),
        "correlation": {
            "pearson_r": round(corr.pearson_r, 4),
            "pearson_p": round(corr.pearson_p, 4),
            "spearman_r": round(corr.spearman_r, 4),
            "spearman_p": round(corr.spearman_p, 4),
            "is_significant": bool(corr.is_significant),
        },
        "data_summary": {
            "n_numbers": int(corr.n_samples),
            "n_draws": int(corr.n_draws),
            "n_gq_dates": int(corr.n_gq_dates),
        },
        "classification": {
            "safe_numbers": [int(n) for n in summary.safe_numbers],
            "popular_numbers": [int(n) for n in summary.popular_numbers],
            "stats": {k: float(v) if isinstance(v, (int, float)) else v
                      for k, v in summary.classification_stats.items()},
        },
        "interpretation": interpret_result(summary),
    }


def interpret_result(summary: OddsAnalysisSummary) -> dict:
    """Generate interpretation of results.

    Args:
        summary: Analysis summary

    Returns:
        Dict with interpretation text
    """
    corr = summary.correlation

    # Determine significance and direction
    if not corr.is_significant:
        significance = "NOT_SIGNIFICANT"
        verdict = "No significant correlation found between draw frequency and winner counts."
    else:
        if corr.spearman_r > 0.2:
            significance = "POSITIVE_CORRELATION"
            verdict = (
                "Positive correlation: Numbers drawn more often have higher winner counts. "
                "This suggests popular numbers are drawn more frequently (or players pick hot numbers)."
            )
        elif corr.spearman_r < -0.2:
            significance = "NEGATIVE_CORRELATION"
            verdict = (
                "Negative correlation: Numbers drawn more often have LOWER winner counts. "
                "This could indicate the RNG avoids popular numbers (supports HYP-004)."
            )
        else:
            significance = "WEAK_CORRELATION"
            verdict = (
                "Weak but statistically significant correlation. "
                "Effect size is small, likely no practical significance."
            )

    return {
        "significance": significance,
        "verdict": verdict,
        "safe_count": len(summary.safe_numbers),
        "popular_count": len(summary.popular_numbers),
        "recommendation": (
            f"Safe numbers (low winners): {summary.safe_numbers[:10]}..."
            if len(summary.safe_numbers) > 10
            else f"Safe numbers: {summary.safe_numbers}"
        ),
    }


def main() -> int:
    """Run HYP-010 analysis.

    Returns:
        Exit code (0 = success)
    """
    parser = argparse.ArgumentParser(
        description="HYP-010: Analyze odds-winner correlation"
    )
    parser.add_argument(
        "--gq-file",
        type=str,
        default="Keno_GPTs/Keno_GQ_2022_2023-2024.csv",
        help="Path to Gewinnquoten CSV file",
    )
    parser.add_argument(
        "--draws-file",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Path to KENO draws CSV file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/hyp010_odds_correlation.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--no-weight",
        action="store_true",
        help="Disable weighting by Keno-Typ",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.0,
        help="Standard deviation threshold for classification (default: 1.0)",
    )

    args = parser.parse_args()

    # Resolve paths
    gq_path = project_root / args.gq_file
    draws_path = project_root / args.draws_file
    output_path = project_root / args.output

    # Check files exist
    if not gq_path.exists():
        logger.error(f"GQ file not found: {gq_path}")
        return 1

    if not draws_path.exists():
        logger.error(f"Draws file not found: {draws_path}")
        return 1

    # Load draws
    logger.info(f"Loading draws from {draws_path}")
    loader = DataLoader()
    draws = loader.load(draws_path)
    logger.info(f"Loaded {len(draws)} draws")

    # Run analysis
    logger.info(f"Running HYP-010 analysis with GQ data from {gq_path}")
    summary = run_hyp010_analysis(
        draws=draws,
        gq_path=gq_path,
        weight_by_keno_typ=not args.no_weight,
        classification_threshold=args.threshold,
    )

    # Format and display results
    result = format_result(summary)

    print("\n" + "=" * 60)
    print("HYP-010: ODDS-WINNER CORRELATION ANALYSIS")
    print("=" * 60)
    print(f"\nData: {result['data_summary']['n_draws']} draws, "
          f"{result['data_summary']['n_gq_dates']} GQ dates")
    print(f"\nCorrelation Results:")
    print(f"  Pearson:  r={result['correlation']['pearson_r']:.4f}, "
          f"p={result['correlation']['pearson_p']:.4f}")
    print(f"  Spearman: r={result['correlation']['spearman_r']:.4f}, "
          f"p={result['correlation']['spearman_p']:.4f}")
    print(f"  Significant: {result['correlation']['is_significant']}")
    print(f"\nClassification:")
    print(f"  Safe numbers ({len(summary.safe_numbers)}): {summary.safe_numbers}")
    print(f"  Popular numbers ({len(summary.popular_numbers)}): {summary.popular_numbers}")
    print(f"\nInterpretation: {result['interpretation']['significance']}")
    print(f"  {result['interpretation']['verdict']}")
    print("=" * 60)

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
