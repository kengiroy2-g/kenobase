#!/usr/bin/env python3
"""HYP-003: Anti-Cluster Reset-Regel Analyse.

Dieses Script fuehrt die komplette HYP-003 Analyse durch:
1. Cluster-Erkennung (>= threshold aufeinanderfolgende Erscheinungen)
2. Reset-Wahrscheinlichkeit berechnen
3. Trading-Signale generieren

Kernhypothese: Nach einem Cluster ist die Wahrscheinlichkeit eines
"Resets" (Nicht-Erscheinen) erhoehlt (>= 60% Baseline-Annahme).

Usage:
    python scripts/analyze_hyp003.py \\
        --data-file data/KENO_Stats.csv \\
        --threshold 5 \\
        --output results/hyp003_cluster_reset.json

Output:
    JSON-Report mit allen Metriken und Acceptance Criteria Evaluation.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.cluster_reset import (
    analyze_reset_probability,
    detect_cluster_events,
    generate_cluster_reset_report,
    generate_trading_signals,
)
from kenobase.core.data_loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_cluster_detection(draws: list, threshold: int) -> dict[str, Any]:
    """Fuehrt Cluster-Erkennung durch.

    Args:
        draws: Liste von DrawResult-Objekten
        threshold: Mindest-Cluster-Laenge

    Returns:
        Dict mit Cluster-Statistiken
    """
    logger.info("=== Phase 1: Cluster Detection ===")

    clusters = detect_cluster_events(draws, threshold)

    # Statistiken berechnen
    cluster_lengths = [c.length for c in clusters]

    return {
        "total_clusters": len(clusters),
        "min_length": min(cluster_lengths) if cluster_lengths else 0,
        "max_length": max(cluster_lengths) if cluster_lengths else 0,
        "avg_length": sum(cluster_lengths) / len(cluster_lengths) if cluster_lengths else 0,
        "clusters_by_length": {
            length: sum(1 for c in clusters if c.length == length)
            for length in sorted(set(cluster_lengths))
        } if cluster_lengths else {},
        "top_clusters": [
            {
                "number": c.number,
                "length": c.length,
                "start_date": c.start_date.isoformat() if c.start_date else None,
                "end_date": c.end_date.isoformat() if c.end_date else None,
            }
            for c in sorted(clusters, key=lambda x: x.length, reverse=True)[:10]
        ],
    }


def run_reset_analysis(draws: list, threshold: int) -> dict[str, Any]:
    """Fuehrt Reset-Analyse durch.

    Args:
        draws: Liste von DrawResult-Objekten
        threshold: Mindest-Cluster-Laenge

    Returns:
        Dict mit Reset-Statistiken
    """
    logger.info("=== Phase 2: Reset Probability Analysis ===")

    result = analyze_reset_probability(draws, threshold)

    return {
        "total_clusters": result.total_clusters,
        "clusters_with_reset": result.clusters_with_reset,
        "reset_probability": result.reset_probability,
        "baseline_probability": result.baseline_probability,
        "lift": result.lift,
        "is_significant": result.is_significant,
        "clusters_by_reset_status": {
            "reset_occurred": sum(1 for c in result.cluster_events if c.reset_occurred is True),
            "no_reset": sum(1 for c in result.cluster_events if c.reset_occurred is False),
            "unknown": sum(1 for c in result.cluster_events if c.reset_occurred is None),
        },
    }


def run_signal_generation(draws: list, threshold: int) -> dict[str, Any]:
    """Generiert Trading-Signale.

    Args:
        draws: Liste von DrawResult-Objekten
        threshold: Mindest-Cluster-Laenge

    Returns:
        Dict mit Signal-Informationen
    """
    logger.info("=== Phase 3: Trading Signal Generation ===")

    signals = generate_trading_signals(draws, threshold)

    return {
        "total_signals": len(signals),
        "no_bet_numbers": [s.number for s in signals],
        "signals_detail": [
            {
                "number": s.number,
                "signal_type": s.signal_type,
                "cluster_length": s.cluster_length,
                "expected_reset_prob": s.expected_reset_prob,
            }
            for s in signals
        ],
    }


def evaluate_acceptance_criteria(
    cluster_detection: dict,
    reset_analysis: dict,
    signal_generation: dict,
) -> dict[str, Any]:
    """Evaluiert die Acceptance Criteria fuer HYP-003.

    Criteria:
    1. Cluster-Erkennung: >= 10 Cluster gefunden
    2. Reset-Wahrscheinlichkeit: berechenbar
    3. Lift > 1.0: Reset-Rate hoeher als Baseline
    4. Signale: generierbar

    Args:
        cluster_detection: Cluster-Ergebnisse
        reset_analysis: Reset-Ergebnisse
        signal_generation: Signal-Ergebnisse

    Returns:
        Dict mit Acceptance Criteria Evaluation
    """
    criteria = {
        "clusters_detected": {
            "target": ">= 10 clusters",
            "actual": cluster_detection["total_clusters"],
            "passed": cluster_detection["total_clusters"] >= 10,
        },
        "reset_probability_calculated": {
            "target": "probability > 0 or no clusters",
            "actual": reset_analysis["reset_probability"],
            "passed": reset_analysis["reset_probability"] > 0 or cluster_detection["total_clusters"] == 0,
        },
        "lift_above_baseline": {
            "target": "lift > 1.0 (indicates predictive value)",
            "actual": reset_analysis["lift"],
            "passed": reset_analysis["lift"] > 1.0,
        },
        "signals_generated": {
            "target": "signal generation works",
            "actual": signal_generation["total_signals"],
            "passed": True,  # Always passes if analysis ran
        },
        "hypothesis_testable": {
            "target": "enough data for statistical test",
            "actual": f"{cluster_detection['total_clusters']} clusters",
            "passed": cluster_detection["total_clusters"] >= 10,
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


def main():
    parser = argparse.ArgumentParser(
        description="HYP-003: Anti-Cluster Reset-Regel Analyse"
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=Path("data/KENO_Stats.csv"),
        help="Pfad zur KENO CSV-Datei",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Mindest-Cluster-Laenge (default: 5)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/hyp003_cluster_reset.json"),
        help="Pfad fuer Output-JSON",
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

    # Validate input file
    if not args.data_file.exists():
        logger.error(f"Data file not found: {args.data_file}")
        sys.exit(1)

    # Create output directory
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Load data
    logger.info(f"Starting HYP-003 Analysis")
    logger.info(f"  Data File: {args.data_file}")
    logger.info(f"  Threshold: {args.threshold}")
    logger.info(f"  Output: {args.output}")

    loader = DataLoader()
    draws = loader.load(str(args.data_file))
    logger.info(f"  Loaded {len(draws)} draws")

    # Run analyses
    cluster_detection = run_cluster_detection(draws, args.threshold)
    reset_analysis = run_reset_analysis(draws, args.threshold)
    signal_generation = run_signal_generation(draws, args.threshold)

    # Evaluate acceptance criteria
    acceptance = evaluate_acceptance_criteria(
        cluster_detection, reset_analysis, signal_generation
    )

    # Build report
    report = {
        "hypothesis": "HYP-003",
        "title": "Anti-Cluster Reset-Regel",
        "timestamp": datetime.now().isoformat(),
        "data_sources": {
            "data_file": str(args.data_file),
            "total_draws": len(draws),
        },
        "config": {
            "threshold": args.threshold,
        },
        "cluster_detection": cluster_detection,
        "reset_analysis": reset_analysis,
        "signal_generation": signal_generation,
        "acceptance_criteria": acceptance,
        "summary": {
            "hypothesis_supported": reset_analysis["is_significant"],
            "key_findings": [],
        },
    }

    # Add key findings
    if reset_analysis["is_significant"]:
        report["summary"]["key_findings"].append(
            f"Reset-Wahrscheinlichkeit ({reset_analysis['reset_probability']:.1%}) ist "
            f"{reset_analysis['lift']:.2f}x hoeher als Baseline ({reset_analysis['baseline_probability']:.1%})"
        )
    else:
        report["summary"]["key_findings"].append(
            f"Reset-Wahrscheinlichkeit ({reset_analysis['reset_probability']:.1%}) ist "
            f"nicht signifikant hoeher als Baseline"
        )

    if cluster_detection["total_clusters"] > 0:
        report["summary"]["key_findings"].append(
            f"{cluster_detection['total_clusters']} Cluster mit Laenge >= {args.threshold} gefunden"
        )
        report["summary"]["key_findings"].append(
            f"Laengster Cluster: {cluster_detection['max_length']} aufeinanderfolgende Erscheinungen"
        )

    if signal_generation["total_signals"] > 0:
        report["summary"]["key_findings"].append(
            f"{signal_generation['total_signals']} aktive NO-BET Signale: "
            f"Zahlen {signal_generation['no_bet_numbers'][:5]}{'...' if len(signal_generation['no_bet_numbers']) > 5 else ''}"
        )

    # Custom JSON encoder for numpy types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.bool_, np.integer)):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    # Write report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    logger.info(f"Report saved to: {args.output}")

    # Print summary
    print("\n" + "=" * 60)
    print("HYP-003 ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Threshold: >= {args.threshold} consecutive appearances")
    print(f"Total Clusters: {cluster_detection['total_clusters']}")
    print(f"Reset Probability: {reset_analysis['reset_probability']:.1%}")
    print(f"Baseline Probability: {reset_analysis['baseline_probability']:.1%}")
    print(f"Lift: {reset_analysis['lift']:.2f}x")
    print(f"Hypothesis Supported: {reset_analysis['is_significant']}")
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
