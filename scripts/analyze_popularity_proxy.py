#!/usr/bin/env python3
"""Popularity Proxy Analysis - Birthday Score vs Winner Count.

This script tests the hypothesis that draws with more birthday numbers (1-31)
have more winners, because more players pick these numbers.

Hypothesis: Positive correlation (r > 0.3) between birthday-score and winner count.

Usage:
    python scripts/analyze_popularity_proxy.py \
        --draws data/raw/keno/KENO_ab_2018.csv \
        --gq-dir data/raw/keno \
        --output results/popularity_proxy.json

Output:
    JSON report with correlation analysis and per-window statistics.
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

from kenobase.analysis.popularity_correlation import (
    BirthdayCorrelationResult,
    calculate_birthday_score,
    correlate_birthday_with_winners,
    load_gq_popularity,
)
from kenobase.core.data_loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def find_gq_files(gq_dir: Path) -> list[Path]:
    """Find all GQ CSV files in directory.

    Args:
        gq_dir: Directory to search

    Returns:
        List of paths to GQ CSV files
    """
    patterns = ["*GQ*.csv", "*gq*.csv", "*Gewinnquoten*.csv", "*gewinnquoten*.csv"]
    files = []
    for pattern in patterns:
        files.extend(gq_dir.glob(pattern))
    return list(set(files))


def merge_gq_data(gq_files: list[Path]) -> dict[datetime, dict[int, float]]:
    """Merge GQ data from multiple files.

    Args:
        gq_files: List of GQ CSV file paths

    Returns:
        Merged GQ data dict
    """
    merged = {}
    for gq_file in gq_files:
        try:
            data = load_gq_popularity(gq_file)
            for date, values in data.items():
                if date not in merged:
                    merged[date] = {}
                merged[date].update(values)
            logger.info(f"Loaded {len(data)} dates from {gq_file.name}")
        except Exception as e:
            logger.warning(f"Failed to load {gq_file}: {e}")
    return merged


def evaluate_acceptance_criteria(
    result: BirthdayCorrelationResult,
    summary: dict,
) -> dict[str, Any]:
    """Evaluate acceptance criteria for Popularity Proxy hypothesis.

    Criteria:
    1. Data: >= 30 paired samples
    2. Correlation: r > 0.3 (positive)
    3. Significance: p < 0.05
    4. Stability: >= 50% of rolling windows support hypothesis

    Args:
        result: Overall correlation result
        summary: Summary statistics

    Returns:
        Acceptance criteria evaluation
    """
    n_paired = summary.get("n_paired", 0)
    support_ratio = summary.get("support_ratio", 0)

    criteria = {
        "sufficient_data": {
            "target": ">= 30 paired samples",
            "actual": n_paired,
            "passed": n_paired >= 30,
        },
        "positive_correlation": {
            "target": "r > 0.3",
            "actual": round(result.correlation, 4),
            "passed": result.correlation > 0.3,
        },
        "statistical_significance": {
            "target": "p < 0.05",
            "actual": round(result.p_value, 6),
            "passed": result.p_value < 0.05,
        },
        "rolling_stability": {
            "target": ">= 50% windows support hypothesis",
            "actual": f"{support_ratio * 100:.1f}%",
            "passed": support_ratio >= 0.5,
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
        description="Popularity Proxy Analysis: Birthday Score vs Winner Count"
    )
    parser.add_argument(
        "--draws",
        type=Path,
        default=Path("data/raw/keno/KENO_ab_2018.csv"),
        help="Path to draws CSV file",
    )
    parser.add_argument(
        "--gq-dir",
        type=Path,
        default=Path("data/raw/keno"),
        help="Directory containing GQ CSV files",
    )
    parser.add_argument(
        "--gq-file",
        type=Path,
        default=None,
        help="Specific GQ file to use (overrides --gq-dir)",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=30,
        help="Rolling window size for stability test (default: 30)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/popularity_proxy.json"),
        help="Output JSON path",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate inputs
    if not args.draws.exists():
        logger.error(f"Draws file not found: {args.draws}")
        print(f"\nError: Draws file not found: {args.draws}")
        return 1

    # Load draws
    logger.info(f"Loading draws from {args.draws}...")
    try:
        loader = DataLoader()
        draws = loader.load(args.draws)
        logger.info(f"Loaded {len(draws)} draws")
    except Exception as e:
        logger.error(f"Failed to load draws: {e}")
        print(f"\nError: Failed to load draws: {e}")
        return 1

    if not draws:
        logger.error("No draws loaded")
        print("\nError: No draws loaded from file")
        return 1

    # Load GQ data
    if args.gq_file:
        gq_files = [args.gq_file] if args.gq_file.exists() else []
    else:
        gq_files = find_gq_files(args.gq_dir)

    if not gq_files:
        logger.warning("No GQ files found - analysis cannot proceed")
        print("\nWarning: No GQ files found in specified directory")
        print("The Popularity Proxy analysis requires Gewinnquoten data.")
        print("\nExpected file pattern: *GQ*.csv or *Gewinnquoten*.csv")
        print(f"Searched directory: {args.gq_dir}")

        # Create empty report
        report = {
            "hypothesis": "POPULARITY_PROXY",
            "title": "Birthday Score vs Winner Count Correlation",
            "timestamp": datetime.now().isoformat(),
            "status": "NO_DATA",
            "error": "No Gewinnquoten (GQ) files found",
            "data_sources": {
                "draws_file": str(args.draws),
                "gq_dir": str(args.gq_dir),
                "gq_files_found": 0,
            },
            "summary": {
                "result": "INCONCLUSIVE",
                "interpretation": "Cannot test hypothesis without GQ data",
            },
        }

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nEmpty report saved to: {args.output}")
        return 1

    logger.info(f"Found {len(gq_files)} GQ files")
    gq_data = merge_gq_data(gq_files)
    logger.info(f"Merged GQ data for {len(gq_data)} dates")

    if not gq_data:
        logger.error("No valid GQ data loaded")
        print("\nError: Failed to load any GQ data")
        return 1

    # Run correlation analysis
    logger.info("Running popularity proxy correlation analysis...")
    results = correlate_birthday_with_winners(draws, gq_data, window=args.window)

    overall = results["overall"]
    rolling = results["rolling"]
    summary = results["summary"]

    # Evaluate acceptance criteria
    acceptance = evaluate_acceptance_criteria(overall, summary)

    # Build report
    report = {
        "hypothesis": "POPULARITY_PROXY",
        "title": "Birthday Score vs Winner Count Correlation",
        "timestamp": datetime.now().isoformat(),
        "data_sources": {
            "draws_file": str(args.draws),
            "n_draws": len(draws),
            "gq_files": [str(f) for f in gq_files],
            "n_gq_dates": len(gq_data),
        },
        "overall_result": {
            "correlation": overall.correlation,
            "p_value": overall.p_value,
            "is_significant": overall.is_significant,
            "supports_hypothesis": overall.supports_hypothesis,
            "n_paired_samples": overall.n_samples,
            "mean_birthday_score": round(overall.mean_birthday_score, 4),
            "mean_winners": round(overall.mean_winners, 2),
        },
        "rolling_analysis": {
            "window_size": args.window,
            "n_windows": len(rolling),
            "mean_correlation": summary.get("mean_rolling_correlation", 0),
            "std_correlation": summary.get("std_rolling_correlation", 0),
            "supporting_windows": summary.get("supporting_windows", 0),
            "support_ratio": summary.get("support_ratio", 0),
        },
        "acceptance_criteria": acceptance,
        "summary": {
            "result": "SUPPORTED" if overall.supports_hypothesis else "NOT SUPPORTED",
            "interpretation": "",
            "key_findings": [],
        },
    }

    # Add interpretation
    if overall.n_samples < 10:
        report["summary"]["interpretation"] = (
            "Insufficient data for statistical test. "
            "Need more paired draw-GQ samples."
        )
    elif overall.supports_hypothesis:
        report["summary"]["interpretation"] = (
            f"Hypothesis SUPPORTED: Birthday score positively correlates with winner count "
            f"(r={overall.correlation:.3f}, p={overall.p_value:.4f}). "
            f"Draws with more birthday numbers (1-31) tend to have more winners."
        )
    elif overall.correlation > 0:
        report["summary"]["interpretation"] = (
            f"Weak positive correlation found (r={overall.correlation:.3f}) "
            f"but either not significant (p={overall.p_value:.4f}) or too weak (< 0.3). "
            f"Some evidence for popularity effect, but not conclusive."
        )
    else:
        report["summary"]["interpretation"] = (
            f"No positive correlation found (r={overall.correlation:.3f}). "
            f"Birthday-score does not predict winner count in this dataset."
        )

    # Add key findings
    report["summary"]["key_findings"].append(
        f"{overall.n_samples} paired draw-GQ samples analyzed"
    )
    report["summary"]["key_findings"].append(
        f"Mean birthday score: {overall.mean_birthday_score:.1%} "
        f"(expected: {31/70:.1%} = 44.3%)"
    )
    report["summary"]["key_findings"].append(
        f"Correlation: r = {overall.correlation:.3f} "
        f"({'positive' if overall.correlation > 0 else 'negative'})"
    )
    report["summary"]["key_findings"].append(
        f"Statistical significance: p = {overall.p_value:.4f} "
        f"({'significant' if overall.is_significant else 'not significant'})"
    )

    if rolling:
        support_pct = summary.get("support_ratio", 0) * 100
        report["summary"]["key_findings"].append(
            f"Rolling stability: {support_pct:.1f}% of windows support hypothesis"
        )

    # Create output directory
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Write report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Report saved to: {args.output}")

    # Print summary
    print("\n" + "=" * 60)
    print("POPULARITY PROXY ANALYSIS")
    print("Birthday Score vs Winner Count Correlation")
    print("=" * 60)
    print(f"Draws: {len(draws)}")
    print(f"GQ Dates: {len(gq_data)}")
    print(f"Paired Samples: {overall.n_samples}")
    print()
    print(f"Correlation (Spearman): r = {overall.correlation:.4f}")
    print(f"P-Value: {overall.p_value:.6f}")
    print(f"Significant (p < 0.05): {overall.is_significant}")
    print(f"Supports Hypothesis (r > 0.3): {overall.supports_hypothesis}")
    print()
    print(f"Mean Birthday Score: {overall.mean_birthday_score:.2%}")
    print(f"Mean Winners per Draw: {overall.mean_winners:.1f}")
    print()

    if rolling:
        print(f"Rolling Windows ({args.window}): {len(rolling)}")
        print(f"Mean Rolling Correlation: {summary.get('mean_rolling_correlation', 0):.4f}")
        print(f"Supporting Windows: {summary.get('supporting_windows', 0)}/{len(rolling)}")
        print()

    print(f"Result: {report['summary']['result']}")
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
    print(f"Full report: {args.output}")

    return 0 if acceptance["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
