#!/usr/bin/env python
"""A6 Axiom Validation: Regional Distribution Testing.

This script validates predictions P6.1, P6.2, P6.3 from Axiom A6 (Regionale Verteilung)
using scraped press release data from Landeslotterien.

Usage:
    python scripts/validate_a6_regional.py --scraped-dir data/scraped --output results/a6_validation.json
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from scipy import stats

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.core.axioms import AXIOM_A6, Direction
from kenobase.core.regions import normalize_region, GERMAN_REGIONS
from kenobase.scraper.converters import load_all_scraped_winners

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# German Bundesland population (millions, 2023 estimate)
# Source: Statistisches Bundesamt
BUNDESLAND_POPULATION = {
    "nordrhein-westfalen": 17.9,
    "bayern": 13.2,
    "baden-wuerttemberg": 11.1,
    "niedersachsen": 8.0,
    "hessen": 6.3,
    "rheinland-pfalz": 4.1,
    "sachsen": 4.0,
    "berlin": 3.8,
    "schleswig-holstein": 2.9,
    "brandenburg": 2.5,
    "sachsen-anhalt": 2.2,
    "thueringen": 2.1,
    "hamburg": 1.9,
    "mecklenburg-vorpommern": 1.6,
    "saarland": 1.0,
    "bremen": 0.7,
}


def count_wins_by_bundesland(draw_results: list) -> dict[str, int]:
    """Count wins per Bundesland from DrawResults."""
    counts: dict[str, int] = {bl: 0 for bl in GERMAN_REGIONS}

    for dr in draw_results:
        bundesland = dr.metadata.get("bundesland")
        if bundesland:
            normalized = normalize_region(bundesland)
            if normalized and normalized in counts:
                counts[normalized] += 1
            else:
                logger.warning(f"Unknown Bundesland: {bundesland}")

    return counts


def validate_p61_population_correlation(
    wins_by_bl: dict[str, int]
) -> dict:
    """P6.1: Wins per Bundesland correlate with population (r > 0.5)."""
    prediction = AXIOM_A6.predictions[0]  # P6.1

    # Build aligned arrays
    bundeslaender = list(BUNDESLAND_POPULATION.keys())
    populations = [BUNDESLAND_POPULATION[bl] for bl in bundeslaender]
    wins = [wins_by_bl.get(bl, 0) for bl in bundeslaender]

    # Calculate correlation
    correlation, p_value = stats.pearsonr(populations, wins)

    # Check against threshold
    passed = correlation > prediction.threshold

    return {
        "prediction_id": prediction.id,
        "description": prediction.description,
        "metric": prediction.metric,
        "threshold": prediction.threshold,
        "direction": prediction.direction.value,
        "observed_value": round(correlation, 4),
        "p_value": round(p_value, 6),
        "passed": passed,
        "n_bundeslaender": len(bundeslaender),
        "total_wins": sum(wins),
        "detail": {
            "bundesland_wins": {bl: wins_by_bl.get(bl, 0) for bl in bundeslaender},
            "bundesland_population": BUNDESLAND_POPULATION,
        },
    }


def validate_p62_jackpot_per_capita(
    wins_by_bl: dict[str, int],
    min_amount: float = 50000.0,
    draw_results: list = None,
) -> dict:
    """P6.2: No region has significantly more jackpots per capita (chi2 p > 0.05)."""
    prediction = AXIOM_A6.predictions[1]  # P6.2

    # Filter to large wins (jackpots) if draw_results provided
    jackpots_by_bl: dict[str, int] = {bl: 0 for bl in GERMAN_REGIONS}

    if draw_results:
        for dr in draw_results:
            amount = dr.metadata.get("amount_eur", 0)
            if amount >= min_amount:
                bundesland = dr.metadata.get("bundesland")
                if bundesland:
                    normalized = normalize_region(bundesland)
                    if normalized and normalized in jackpots_by_bl:
                        jackpots_by_bl[normalized] += 1
    else:
        jackpots_by_bl = wins_by_bl.copy()

    # Calculate expected wins based on population proportion
    total_population = sum(BUNDESLAND_POPULATION.values())
    total_jackpots = sum(jackpots_by_bl.values())

    if total_jackpots == 0:
        return {
            "prediction_id": prediction.id,
            "description": prediction.description,
            "passed": None,
            "reason": "No jackpot data available",
        }

    expected = [
        (BUNDESLAND_POPULATION[bl] / total_population) * total_jackpots
        for bl in BUNDESLAND_POPULATION.keys()
    ]
    observed = [jackpots_by_bl.get(bl, 0) for bl in BUNDESLAND_POPULATION.keys()]

    # Chi-square test
    # Only include regions with expected > 0
    valid_idx = [i for i, e in enumerate(expected) if e >= 1.0]

    if len(valid_idx) < 3:
        return {
            "prediction_id": prediction.id,
            "description": prediction.description,
            "passed": None,
            "reason": "Insufficient data for chi-square test",
        }

    obs_valid = [observed[i] for i in valid_idx]
    exp_valid = [expected[i] for i in valid_idx]

    chi2, p_value = stats.chisquare(obs_valid, exp_valid)

    # P6.2: p-value should be > 0.05 (no significant deviation)
    passed = p_value > prediction.threshold

    return {
        "prediction_id": prediction.id,
        "description": prediction.description,
        "metric": prediction.metric,
        "threshold": prediction.threshold,
        "direction": prediction.direction.value,
        "observed_value": round(p_value, 6),
        "chi2_statistic": round(chi2, 4),
        "passed": passed,
        "interpretation": (
            "Distribution matches population expectation"
            if passed
            else "Significant deviation from population expectation"
        ),
        "n_jackpots": total_jackpots,
        "min_amount": min_amount,
    }


def validate_p63_temporal_uniformity(
    draw_results: list,
) -> dict:
    """P6.3: Large wins are evenly distributed over time (KS p > 0.1)."""
    prediction = AXIOM_A6.predictions[2]  # P6.3

    # Extract dates from draw results
    dates = []
    for dr in draw_results:
        if dr.date:
            dates.append(dr.date)

    if len(dates) < 10:
        return {
            "prediction_id": prediction.id,
            "description": prediction.description,
            "passed": None,
            "reason": f"Insufficient temporal data (n={len(dates)})",
        }

    # Convert to day-of-year (0-365) for uniformity test
    day_of_year = [d.timetuple().tm_yday for d in dates]

    # Kolmogorov-Smirnov test against uniform distribution
    ks_statistic, p_value = stats.kstest(
        day_of_year,
        stats.uniform(loc=1, scale=365).cdf,
    )

    # P6.3: p-value should be > 0.1 (uniform distribution)
    passed = p_value > prediction.threshold

    return {
        "prediction_id": prediction.id,
        "description": prediction.description,
        "metric": prediction.metric,
        "threshold": prediction.threshold,
        "direction": prediction.direction.value,
        "observed_value": round(p_value, 6),
        "ks_statistic": round(ks_statistic, 4),
        "passed": passed,
        "interpretation": (
            "Wins are evenly distributed over time"
            if passed
            else "Temporal clustering detected"
        ),
        "n_dates": len(dates),
    }


def run_a6_validation(
    scraped_dir: Path,
    min_confidence: float = 0.3,
    output_path: Optional[Path] = None,
) -> dict:
    """Run full A6 axiom validation.

    Args:
        scraped_dir: Directory with scraped JSON files
        min_confidence: Minimum extraction confidence
        output_path: Optional path to save results

    Returns:
        Dictionary with validation results
    """
    logger.info(f"Loading scraped data from {scraped_dir}")

    # Load all scraped winners
    draw_results = load_all_scraped_winners(
        scraped_dir,
        min_confidence=min_confidence,
    )

    if not draw_results:
        logger.warning("No scraped data found")
        return {
            "status": "NO_DATA",
            "message": "No scraped data available for A6 validation",
            "recommendation": (
                "Run: python scripts/scrape_press.py --all --output data/scraped"
            ),
        }

    logger.info(f"Loaded {len(draw_results)} winner records")

    # Count wins by Bundesland
    wins_by_bl = count_wins_by_bundesland(draw_results)
    total_wins = sum(wins_by_bl.values())

    logger.info(f"Total wins across Bundeslaender: {total_wins}")

    # Run all P6.x validations
    results = {
        "axiom": {
            "id": AXIOM_A6.id,
            "name": AXIOM_A6.name,
            "description": AXIOM_A6.description,
        },
        "data_summary": {
            "total_records": len(draw_results),
            "min_confidence": min_confidence,
            "bundeslaender_with_data": sum(1 for v in wins_by_bl.values() if v > 0),
            "wins_by_bundesland": wins_by_bl,
        },
        "predictions": [],
        "timestamp": datetime.now().isoformat(),
    }

    # P6.1: Population correlation
    p61_result = validate_p61_population_correlation(wins_by_bl)
    results["predictions"].append(p61_result)
    logger.info(
        f"P6.1 (Population Correlation): "
        f"r={p61_result.get('observed_value', 'N/A')}, "
        f"passed={p61_result.get('passed')}"
    )

    # P6.2: Jackpot per capita
    p62_result = validate_p62_jackpot_per_capita(
        wins_by_bl,
        min_amount=50000.0,
        draw_results=draw_results,
    )
    results["predictions"].append(p62_result)
    logger.info(
        f"P6.2 (Jackpot Per Capita): "
        f"p={p62_result.get('observed_value', 'N/A')}, "
        f"passed={p62_result.get('passed')}"
    )

    # P6.3: Temporal uniformity
    p63_result = validate_p63_temporal_uniformity(draw_results)
    results["predictions"].append(p63_result)
    logger.info(
        f"P6.3 (Temporal Uniformity): "
        f"p={p63_result.get('observed_value', 'N/A')}, "
        f"passed={p63_result.get('passed')}"
    )

    # Calculate overall status
    prediction_results = [
        p.get("passed") for p in results["predictions"]
        if p.get("passed") is not None
    ]

    if not prediction_results:
        results["overall_status"] = "INSUFFICIENT_DATA"
    elif all(prediction_results):
        results["overall_status"] = "ALL_PASSED"
    elif any(prediction_results):
        results["overall_status"] = "PARTIAL"
    else:
        results["overall_status"] = "ALL_FAILED"

    # Save if output path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Results saved to {output_path}")

    return results


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate A6 Axiom (Regional Distribution) using scraped data",
    )
    parser.add_argument(
        "--scraped-dir",
        type=Path,
        default=Path("data/scraped"),
        help="Directory with scraped JSON files",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("results/a6_validation.json"),
        help="Output path for results",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.3,
        help="Minimum extraction confidence (0.0-1.0)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run validation
    results = run_a6_validation(
        scraped_dir=args.scraped_dir,
        min_confidence=args.min_confidence,
        output_path=args.output,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("A6 AXIOM VALIDATION RESULTS")
    print("=" * 60)
    print(f"Total Records: {results.get('data_summary', {}).get('total_records', 0)}")
    print(f"Overall Status: {results.get('overall_status', 'UNKNOWN')}")
    print("-" * 60)

    for pred in results.get("predictions", []):
        status = "PASS" if pred.get("passed") else "FAIL" if pred.get("passed") is False else "N/A"
        print(f"  {pred.get('prediction_id', '?')}: {status}")
        print(f"     {pred.get('description', '')[:50]}...")
        if pred.get("observed_value") is not None:
            print(f"     Observed: {pred.get('observed_value')} (threshold: {pred.get('threshold')})")

    print("=" * 60)
    print(f"Results saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
