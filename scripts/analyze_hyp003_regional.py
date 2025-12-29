#!/usr/bin/env python3
"""HYP-003 Regional Distribution Analysis via Press Releases.

This script analyzes regional winner distribution from scraped press releases
and tests whether it deviates from population-based expectations.

Hypothesis: Winner distribution across German Bundeslaender matches
population distribution (null hypothesis for Chi-Quadrat test).

Usage:
    python scripts/analyze_hyp003_regional.py \\
        --scraped-dir data/scraped \\
        --output results/hyp003_regional_distribution.json

Output:
    JSON report with Chi-Quadrat test results and per-bundesland statistics.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.regional_affinity import (
    BUNDESLAND_POPULATION_SHARE,
    RegionalDistributionResult,
    calculate_distribution_chi2,
)
from kenobase.core.data_loader import DrawResult
from kenobase.scraper.converters import load_all_scraped_winners

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def analyze_regional_distribution(
    draws: list[DrawResult],
) -> dict[str, Any]:
    """Run Chi-Quadrat analysis on regional distribution.

    Args:
        draws: List of DrawResult objects with bundesland in metadata

    Returns:
        Analysis results dict
    """
    logger.info(f"Analyzing {len(draws)} winner records...")

    # Run Chi-Quadrat test
    chi2_result = calculate_distribution_chi2(draws)

    # Calculate per-bundesland summary
    bundesland_summary = {}
    for region in BUNDESLAND_POPULATION_SHARE:
        observed = chi2_result.observed.get(region, 0)
        expected = chi2_result.expected.get(region, 0)
        deviation = chi2_result.deviations.get(region, 0)

        bundesland_summary[region] = {
            "observed": observed,
            "expected": round(expected, 2) if expected else 0,
            "deviation_pct": round(deviation * 100, 1) if deviation else 0,
            "population_share_pct": round(
                BUNDESLAND_POPULATION_SHARE.get(region, 0) * 100, 1
            ),
        }

    return {
        "chi2_test": chi2_result.to_dict(),
        "bundesland_summary": bundesland_summary,
    }


def evaluate_acceptance_criteria(
    chi2_result: RegionalDistributionResult,
    n_draws: int,
) -> dict[str, Any]:
    """Evaluate acceptance criteria for HYP-003 Regional.

    Criteria:
    1. Data: >= 10 winners with bundesland info
    2. Coverage: >= 3 different Bundeslaender represented
    3. Chi2 Test: computable (df >= 1)
    4. Interpretation: clear result (significant or not)

    Args:
        chi2_result: Chi-Quadrat test result
        n_draws: Number of valid draw records

    Returns:
        Acceptance criteria evaluation
    """
    n_regions = len(chi2_result.observed)

    criteria = {
        "sufficient_data": {
            "target": ">= 10 winners with bundesland",
            "actual": chi2_result.n_total,
            "passed": chi2_result.n_total >= 10,
        },
        "regional_coverage": {
            "target": ">= 3 Bundeslaender represented",
            "actual": n_regions,
            "passed": n_regions >= 3,
        },
        "chi2_computable": {
            "target": "degrees of freedom >= 1",
            "actual": chi2_result.degrees_of_freedom,
            "passed": chi2_result.degrees_of_freedom >= 1,
        },
        "result_interpretable": {
            "target": "p-value computed",
            "actual": chi2_result.p_value,
            "passed": 0 <= chi2_result.p_value <= 1,
        },
    }

    n_passed = sum(1 for c in criteria.values() if c["passed"])
    n_total = len(criteria)

    return {
        "criteria": criteria,
        "passed": n_passed,
        "total": n_total,
        "all_passed": n_passed == n_total,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="HYP-003: Regional Distribution Analysis via Press Releases"
    )
    parser.add_argument(
        "--scraped-dir",
        type=Path,
        default=Path("data/scraped"),
        help="Directory containing scraped JSON files",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.3,
        help="Minimum extraction confidence (0.0-1.0)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/hyp003_regional_distribution.json"),
        help="Output JSON path",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input directory
    if not args.scraped_dir.is_dir():
        logger.error(f"Scraped directory not found: {args.scraped_dir}")
        print(f"\nError: Directory not found: {args.scraped_dir}")
        print("Run 'python scripts/scrape_press.py --all' first to collect data.")
        return 1

    # Create output directory
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Load scraped winners
    logger.info(f"Loading scraped winners from {args.scraped_dir}...")
    draws = load_all_scraped_winners(
        args.scraped_dir,
        min_confidence=args.min_confidence,
        deduplicate=True,
    )

    if not draws:
        logger.error("No valid winner records found")
        print("\nError: No valid winner records found.")
        print("Run 'python scripts/scrape_press.py --all' to collect data.")
        return 1

    logger.info(f"Loaded {len(draws)} valid winner records")

    # Run analysis
    analysis = analyze_regional_distribution(draws)
    chi2_result = calculate_distribution_chi2(draws)

    # Evaluate acceptance criteria
    acceptance = evaluate_acceptance_criteria(chi2_result, len(draws))

    # Build report
    report = {
        "hypothesis": "HYP-003",
        "variant": "regional_distribution",
        "title": "Regionale Gewinner-Verteilung vs. Bevoelkerungsanteil",
        "timestamp": datetime.now().isoformat(),
        "data_sources": {
            "scraped_dir": str(args.scraped_dir),
            "total_records_loaded": len(draws),
            "min_confidence": args.min_confidence,
        },
        "chi2_test": analysis["chi2_test"],
        "bundesland_summary": analysis["bundesland_summary"],
        "acceptance_criteria": acceptance,
        "summary": {
            "null_hypothesis": "Winner distribution matches population distribution",
            "result": "REJECTED" if chi2_result.is_significant else "NOT REJECTED",
            "interpretation": "",
            "key_findings": [],
        },
    }

    # Add interpretation
    if chi2_result.n_total < 10:
        report["summary"]["interpretation"] = (
            "Insufficient data for statistical test. "
            "Collect more press releases."
        )
    elif chi2_result.is_significant:
        report["summary"]["interpretation"] = (
            f"Significant deviation from population distribution "
            f"(Chi2={chi2_result.chi2_statistic:.2f}, p={chi2_result.p_value:.4f}). "
            f"Regional factors may influence winner distribution."
        )
    else:
        report["summary"]["interpretation"] = (
            f"No significant deviation from population distribution "
            f"(Chi2={chi2_result.chi2_statistic:.2f}, p={chi2_result.p_value:.4f}). "
            f"Winner distribution appears random across regions."
        )

    # Add key findings
    report["summary"]["key_findings"].append(
        f"{chi2_result.n_total} winners from {len(chi2_result.observed)} Bundeslaender"
    )

    if chi2_result.deviations:
        # Find largest deviations
        sorted_deviations = sorted(
            chi2_result.deviations.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )
        if sorted_deviations:
            region, dev = sorted_deviations[0]
            direction = "ueber" if dev > 0 else "unter"
            report["summary"]["key_findings"].append(
                f"Groesste Abweichung: {region} ({direction}repraesentiert um {abs(dev)*100:.1f}%)"
            )

    report["summary"]["key_findings"].append(
        f"Chi-Quadrat Statistik: {chi2_result.chi2_statistic:.2f} (df={chi2_result.degrees_of_freedom})"
    )
    report["summary"]["key_findings"].append(
        f"p-Wert: {chi2_result.p_value:.4f} ({'signifikant' if chi2_result.is_significant else 'nicht signifikant'})"
    )

    # Write report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Report saved to: {args.output}")

    # Print summary
    print("\n" + "=" * 60)
    print("HYP-003 REGIONAL DISTRIBUTION ANALYSIS")
    print("=" * 60)
    print(f"Data Source: {args.scraped_dir}")
    print(f"Winners Analyzed: {chi2_result.n_total}")
    print(f"Bundeslaender: {len(chi2_result.observed)}")
    print()
    print(f"Chi-Quadrat: {chi2_result.chi2_statistic:.4f}")
    print(f"Degrees of Freedom: {chi2_result.degrees_of_freedom}")
    print(f"p-Value: {chi2_result.p_value:.6f}")
    print(f"Significant (p < 0.05): {chi2_result.is_significant}")
    print()
    print(f"Null Hypothesis: {report['summary']['result']}")
    print()
    print("Interpretation:")
    print(f"  {report['summary']['interpretation']}")
    print()
    print(f"Acceptance Criteria: {acceptance['passed']}/{acceptance['total']} passed")
    print()
    print("Key Findings:")
    for finding in report["summary"]["key_findings"]:
        print(f"  - {finding}")
    print()

    # Print per-region breakdown if verbose
    if args.verbose and chi2_result.observed:
        print("-" * 60)
        print("Per-Bundesland Breakdown:")
        print()
        print(f"{'Bundesland':<25} {'Obs':>5} {'Exp':>7} {'Dev%':>8}")
        print("-" * 47)
        for region, stats in sorted(
            analysis["bundesland_summary"].items(),
            key=lambda x: x[1].get("observed", 0),
            reverse=True,
        ):
            if stats["observed"] > 0 or stats["expected"] > 0:
                print(
                    f"{region:<25} {stats['observed']:>5} "
                    f"{stats['expected']:>7.1f} {stats['deviation_pct']:>7.1f}%"
                )
        print()

    print(f"Full report: {args.output}")

    return 0 if acceptance["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
