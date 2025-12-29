#!/usr/bin/env python3
"""HYP-011: Temporal Cycles Analysis for KENO Draws.

Tests whether KENO draw numbers show temporal patterns:
- Weekday bias (certain numbers appear more on specific weekdays)
- Month bias (seasonal patterns)
- Year-over-year trends
- Holiday proximity effects

Methodology: Chi-square tests against uniform distribution.

Usage:
    python scripts/analyze_hyp011.py --data data/raw/keno/KENO_ab_2018.csv
    python scripts/analyze_hyp011.py --data data/raw/keno/KENO_ab_2018.csv --per-number
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

from kenobase.core.data_loader import DataLoader
from kenobase.analysis.temporal_cycles import (
    analyze_temporal_cycles,
    to_dict,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Run HYP-011 temporal cycles analysis."""
    parser = argparse.ArgumentParser(
        description="HYP-011: Temporal Cycles Analysis for KENO"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Path to KENO data CSV",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/hyp011_temporal_cycles.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--per-number",
        action="store_true",
        help="Analyze each number individually (slower)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level (default: 0.05)",
    )

    args = parser.parse_args()

    # Load data
    data_path = Path(args.data)
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        return 1

    logger.info(f"Loading KENO data from {data_path}")
    loader = DataLoader()
    draws = loader.load(data_path)

    if not draws:
        logger.error("No draws loaded from data file")
        return 1

    logger.info(f"Loaded {len(draws)} KENO draws")

    # Extract dates and numbers
    dates = [draw.date for draw in draws]
    numbers_per_draw = [draw.numbers for draw in draws]

    # Run analysis
    logger.info("Running temporal cycles analysis...")
    result = analyze_temporal_cycles(
        dates=dates,
        numbers_per_draw=numbers_per_draw,
        analyze_per_number=args.per_number,
        alpha=args.alpha,
    )

    # Convert to dict for JSON output
    output_dict = to_dict(result)
    output_dict["analysis_timestamp"] = datetime.now().isoformat()
    output_dict["data_source"] = str(data_path)
    output_dict["parameters"] = {
        "alpha": args.alpha,
        "per_number_analysis": args.per_number,
    }

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_dict, f, indent=2, ensure_ascii=False)

    logger.info(f"Results written to {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("HYP-011: TEMPORAL CYCLES ANALYSIS - SUMMARY")
    print("=" * 60)
    print(f"Data: {data_path.name}")
    print(f"Draws analyzed: {result.n_draws}")
    print(f"Date range: {result.date_range_start} - {result.date_range_end}")
    print()

    # Weekday analysis
    if result.weekday_analysis:
        wa = result.weekday_analysis
        print(f"WEEKDAY DISTRIBUTION:")
        print(f"  Chi2 = {wa.chi2_statistic:.2f}, p = {wa.p_value:.4f}")
        print(f"  Significant: {'JA' if wa.is_significant else 'NEIN'}")
        print(f"  {wa.interpretation}")
        print()

    # Month analysis
    if result.month_analysis:
        ma = result.month_analysis
        print(f"MONTH DISTRIBUTION:")
        print(f"  Chi2 = {ma.chi2_statistic:.2f}, p = {ma.p_value:.4f}")
        print(f"  Significant: {'JA' if ma.is_significant else 'NEIN'}")
        print(f"  {ma.interpretation}")
        print()

    # Year analysis
    if result.year_analysis:
        ya = result.year_analysis
        print(f"YEAR DISTRIBUTION:")
        print(f"  Chi2 = {ya.chi2_statistic:.2f}, p = {ya.p_value:.4f}")
        print(f"  Significant: {'JA' if ya.is_significant else 'NEIN'}")
        print(f"  {ya.interpretation}")
        print()

    # Holiday analysis
    if result.holiday_analysis:
        ha = result.holiday_analysis
        if ha.get("status") != "INSUFFICIENT_DATA":
            print(f"HOLIDAY PROXIMITY:")
            print(f"  Observed rate: {ha['observed_rate']:.1%}")
            print(f"  Expected rate: {ha['expected_rate']:.1%}")
            print(f"  p = {ha['p_value']:.4f}")
            print(f"  {ha['interpretation']}")
            print()

    # Per-number summary
    if args.per_number and result.number_analyses:
        n_wd = len(result.significant_weekday_numbers)
        n_mo = len(result.significant_month_numbers)
        print(f"PER-NUMBER ANALYSIS:")
        print(f"  Numbers with weekday bias: {n_wd} (expected FP: ~3.5)")
        print(f"  Numbers with month bias: {n_mo} (expected FP: ~3.5)")
        if result.significant_weekday_numbers:
            print(f"  Weekday-biased numbers: {result.significant_weekday_numbers}")
        if result.significant_month_numbers:
            print(f"  Month-biased numbers: {result.significant_month_numbers}")
        print()

    # Final verdict
    print("=" * 60)
    print(f"HYP-011 VERDICT: {result.verdict}")
    print(f"Confidence: {result.confidence:.0%}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
