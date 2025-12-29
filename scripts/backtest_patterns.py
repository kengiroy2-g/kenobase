#!/usr/bin/env python3
"""Pattern Backtest: Walk-Forward Validierung von Duo/Trio/Quatro Patterns.

Dieses Script fuehrt einen Walk-Forward Backtest durch um die Vorhersagekraft
von Pattern-Kombinationen (Duo/Trio/Quatro) zu validieren.

Methodik:
1. Trainings-Fenster: Letzte N Ziehungen analysieren
2. Pattern-Extraktion: Top-K haeufigste Patterns ermitteln
3. Test-Fenster: Naechste M Ziehungen vorhersagen
4. Metriken: Precision, Recall, Lift vs. Zufalls-Baseline

Usage:
    python scripts/backtest_patterns.py \
        --data data/raw/keno/KENO_ab_2018.csv \
        --train-window 100 \
        --test-window 20 \
        --output AI_COLLABORATION/ARTIFACTS/pattern_backtest.json

Output:
    JSON-Report mit Walk-Forward Metriken und Acceptance Criteria.

References:
    - ADR-002: Pattern Bug-Fix
    - ISSUE-004: Korrelations-Analysen
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from kenobase.analysis.pattern import (
    PatternResult,
    aggregate_patterns,
    extract_patterns,
    extract_patterns_from_draws,
)
from kenobase.core.data_loader import DataLoader, DrawResult, GameType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class PatternMetrics:
    """Metriken fuer Pattern-Validierung.

    Attributes:
        pattern_type: 'duo', 'trio', oder 'quatro'
        n_patterns_tested: Anzahl getesteter Patterns
        precision: Anteil korrekter Vorhersagen
        recall: Anteil gefundener Patterns
        lift: Verbesserung gegenueber Zufalls-Baseline
        baseline_rate: Erwartete Zufalls-Trefferquote
    """

    pattern_type: str
    n_patterns_tested: int
    precision: float
    recall: float
    lift: float
    baseline_rate: float
    hits: int = 0
    total_predictions: int = 0
    total_actual: int = 0


@dataclass
class BacktestResult:
    """Ergebnis eines Walk-Forward Backtest-Laufs.

    Attributes:
        fold_id: Index des Folds
        train_start: Start-Index Training
        train_end: End-Index Training
        test_start: Start-Index Test
        test_end: End-Index Test
        metrics: Dict mit Metriken pro Pattern-Typ
    """

    fold_id: int
    train_start: int
    train_end: int
    test_start: int
    test_end: int
    n_train_draws: int
    n_test_draws: int
    metrics: dict[str, PatternMetrics] = field(default_factory=dict)


def calculate_baseline_rate(
    game_type: GameType,
    pattern_size: int,
) -> float:
    """Berechnet die erwartete Zufalls-Trefferquote fuer ein Pattern.

    Args:
        game_type: KENO, LOTTO oder EUROJACKPOT
        pattern_size: 2 (Duo), 3 (Trio), oder 4 (Quatro)

    Returns:
        Wahrscheinlichkeit dass Pattern zufaellig erscheint
    """
    # Konfiguration pro Spieltyp
    game_configs = {
        GameType.KENO: {"pool": 70, "drawn": 20},
        GameType.LOTTO: {"pool": 49, "drawn": 6},
        GameType.EUROJACKPOT: {"pool": 50, "drawn": 5},
    }

    config = game_configs.get(game_type, game_configs[GameType.KENO])
    pool = config["pool"]
    drawn = config["drawn"]

    # Hypergeometrische Wahrscheinlichkeit: k aus n Erfolge bei N draws aus M pool
    # P(alle k Zahlen gezogen) = C(k,k) * C(M-k, N-k) / C(M, N)
    # Vereinfacht fuer kleine k: approx (drawn/pool)^k

    # Exact calculation: product of conditional probabilities
    prob = 1.0
    for i in range(pattern_size):
        prob *= (drawn - i) / (pool - i)

    return prob


def extract_top_patterns(
    pattern_results: list[PatternResult],
    top_k: int = 10,
) -> dict[str, list[tuple[tuple[int, ...], int]]]:
    """Extrahiert die Top-K haeufigsten Patterns pro Typ.

    Args:
        pattern_results: Liste von PatternResult aus Trainings-Daten
        top_k: Anzahl Top-Patterns pro Typ

    Returns:
        Dict mit Pattern-Typ als Key und Liste von (pattern, count) Tupeln
    """
    aggregated = aggregate_patterns(pattern_results)

    result = {}
    for ptype, patterns in aggregated.items():
        # Sortiere nach Haeufigkeit (absteigend)
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        result[ptype] = sorted_patterns[:top_k]

    return result


def evaluate_predictions(
    top_patterns: dict[str, list[tuple[tuple[int, ...], int]]],
    test_draws: list[DrawResult],
    game_type: GameType,
) -> dict[str, PatternMetrics]:
    """Evaluiert Vorhersagen auf Test-Daten.

    Args:
        top_patterns: Top-K Patterns pro Typ aus Training
        test_draws: Test-Ziehungen
        game_type: Spieltyp fuer Baseline-Berechnung

    Returns:
        Dict mit Metriken pro Pattern-Typ
    """
    metrics = {}

    for ptype, patterns in top_patterns.items():
        if not patterns:
            continue

        pattern_size = len(patterns[0][0]) if patterns else 2
        baseline = calculate_baseline_rate(game_type, pattern_size)

        # Erstelle Set der vorhergesagten Patterns
        predicted_set = {p[0] for p in patterns}
        n_predictions = len(predicted_set)

        # Zaehle Treffer in Test-Daten
        hits = 0
        total_actual = 0

        for draw in test_draws:
            draw_set = set(draw.numbers)

            # Pruefe alle vorhergesagten Patterns
            for pattern in predicted_set:
                if set(pattern).issubset(draw_set):
                    hits += 1

            # Zaehle tatsaechliche Patterns im Draw (fuer Recall)
            # Vereinfacht: Anzahl moeglicher k-Kombinationen aus gezogenen Zahlen
            from itertools import combinations

            n_drawn = len(draw.numbers)
            if n_drawn >= pattern_size:
                total_actual += len(list(combinations(draw.numbers, pattern_size)))

        # Berechne Metriken
        n_tests = len(test_draws) * n_predictions  # Anzahl Tests
        precision = hits / n_tests if n_tests > 0 else 0.0
        recall = hits / total_actual if total_actual > 0 else 0.0
        lift = precision / baseline if baseline > 0 else 1.0

        metrics[ptype] = PatternMetrics(
            pattern_type=ptype,
            n_patterns_tested=n_predictions,
            precision=precision,
            recall=recall,
            lift=lift,
            baseline_rate=baseline,
            hits=hits,
            total_predictions=n_tests,
            total_actual=total_actual,
        )

    return metrics


def run_walk_forward_backtest(
    draws: list[DrawResult],
    train_window: int = 100,
    test_window: int = 20,
    top_k: int = 10,
    test_combination: list[int] | None = None,
) -> list[BacktestResult]:
    """Fuehrt Walk-Forward Backtest durch.

    Args:
        draws: Sortierte Liste aller Ziehungen (aelteste zuerst)
        train_window: Groesse des Trainings-Fensters
        test_window: Groesse des Test-Fensters
        top_k: Anzahl Top-Patterns pro Typ
        test_combination: Optionale Test-Kombination (default: [1-6])

    Returns:
        Liste von BacktestResult fuer jeden Fold
    """
    if test_combination is None:
        # Default: Erste 6 Zahlen (fuer Demo)
        test_combination = [1, 2, 3, 4, 5, 6]

    results = []
    n_draws = len(draws)

    # Bestimme Spieltyp
    game_type = draws[0].game_type if draws else GameType.KENO

    fold_id = 0
    train_start = 0

    while train_start + train_window + test_window <= n_draws:
        train_end = train_start + train_window
        test_start = train_end
        test_end = test_start + test_window

        # Extrahiere Trainings- und Test-Daten
        train_draws = draws[train_start:train_end]
        test_draws = draws[test_start:test_end]

        # Extrahiere Patterns aus Training
        pattern_results = extract_patterns_from_draws(test_combination, train_draws)
        top_patterns = extract_top_patterns(pattern_results, top_k)

        # Evaluiere auf Test-Daten
        metrics = evaluate_predictions(top_patterns, test_draws, game_type)

        results.append(
            BacktestResult(
                fold_id=fold_id,
                train_start=train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end,
                n_train_draws=len(train_draws),
                n_test_draws=len(test_draws),
                metrics=metrics,
            )
        )

        # Slide forward
        train_start += test_window
        fold_id += 1

    return results


def aggregate_backtest_results(
    results: list[BacktestResult],
) -> dict[str, dict[str, float]]:
    """Aggregiert Metriken ueber alle Folds.

    Args:
        results: Liste von BacktestResult

    Returns:
        Dict mit aggregierten Metriken pro Pattern-Typ
    """
    aggregated: dict[str, dict[str, list[float]]] = {}

    for result in results:
        for ptype, metrics in result.metrics.items():
            if ptype not in aggregated:
                aggregated[ptype] = {
                    "precision": [],
                    "recall": [],
                    "lift": [],
                    "baseline_rate": [],
                }
            aggregated[ptype]["precision"].append(metrics.precision)
            aggregated[ptype]["recall"].append(metrics.recall)
            aggregated[ptype]["lift"].append(metrics.lift)
            aggregated[ptype]["baseline_rate"].append(metrics.baseline_rate)

    # Berechne Mittelwerte und Std
    summary: dict[str, dict[str, float]] = {}
    for ptype, vals in aggregated.items():
        summary[ptype] = {
            "mean_precision": float(np.mean(vals["precision"])),
            "std_precision": float(np.std(vals["precision"])),
            "mean_recall": float(np.mean(vals["recall"])),
            "std_recall": float(np.std(vals["recall"])),
            "mean_lift": float(np.mean(vals["lift"])),
            "std_lift": float(np.std(vals["lift"])),
            "baseline_rate": float(np.mean(vals["baseline_rate"])),
            "n_folds": len(vals["precision"]),
        }

    return summary


def evaluate_acceptance_criteria(
    summary: dict[str, dict[str, float]],
) -> dict[str, Any]:
    """Evaluiert die Acceptance Criteria fuer Pattern-Backtest.

    Criteria:
    1. Lift > 1.0 fuer mindestens einen Pattern-Typ (besser als Zufall)
    2. Precision stabil (CV < 0.5)
    3. Mindestens 3 Folds durchgefuehrt

    Args:
        summary: Aggregierte Metriken

    Returns:
        Dict mit Acceptance Criteria Evaluation
    """
    # Check if any pattern type has lift > 1
    any_lift_above_baseline = any(
        m.get("mean_lift", 0) > 1.0 for m in summary.values()
    )

    # Check precision stability (CV = std/mean < 0.5)
    precision_stable = all(
        (m.get("std_precision", 1) / max(m.get("mean_precision", 0.001), 0.001)) < 0.5
        for m in summary.values()
        if m.get("mean_precision", 0) > 0
    )

    # Check sufficient folds
    min_folds = min(m.get("n_folds", 0) for m in summary.values()) if summary else 0

    criteria = {
        "lift_above_baseline": {
            "target": "at least one pattern type with lift > 1.0",
            "actual": {p: m.get("mean_lift", 0) for p, m in summary.items()},
            "passed": any_lift_above_baseline,
        },
        "precision_stability": {
            "target": "CV < 0.5 for all pattern types",
            "actual": {
                p: (m.get("std_precision", 0) / max(m.get("mean_precision", 0.001), 0.001))
                for p, m in summary.items()
            },
            "passed": precision_stable,
        },
        "sufficient_folds": {
            "target": ">= 3 folds",
            "actual": min_folds,
            "passed": min_folds >= 3,
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
        description="Pattern Backtest: Walk-Forward Validierung von Duo/Trio/Quatro Patterns"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/raw/keno/KENO_ab_2018.csv"),
        help="Pfad zur Ziehungs-CSV",
    )
    parser.add_argument(
        "--train-window",
        type=int,
        default=100,
        help="Groesse des Trainings-Fensters (Anzahl Ziehungen)",
    )
    parser.add_argument(
        "--test-window",
        type=int,
        default=20,
        help="Groesse des Test-Fensters (Anzahl Ziehungen)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Anzahl Top-Patterns pro Typ",
    )
    parser.add_argument(
        "--combination",
        type=str,
        default="1,5,12,23,34,45",
        help="Test-Kombination (komma-separiert)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("AI_COLLABORATION/ARTIFACTS/pattern_backtest.json"),
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

    # Validate input
    if not args.data.exists():
        logger.error(f"Data file not found: {args.data}")
        sys.exit(1)

    # Parse combination
    test_combination = [int(x.strip()) for x in args.combination.split(",")]

    # Create output directory
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Load data
    logger.info(f"Loading data from {args.data}")
    loader = DataLoader()
    draws = loader.load(args.data)
    logger.info(f"Loaded {len(draws)} draws")

    # Sort by date (oldest first for walk-forward)
    draws.sort(key=lambda d: d.date)

    # Run backtest
    logger.info(
        f"Running walk-forward backtest (train={args.train_window}, test={args.test_window})"
    )
    results = run_walk_forward_backtest(
        draws,
        train_window=args.train_window,
        test_window=args.test_window,
        top_k=args.top_k,
        test_combination=test_combination,
    )
    logger.info(f"Completed {len(results)} folds")

    # Aggregate results
    summary = aggregate_backtest_results(results)

    # Evaluate acceptance criteria
    acceptance = evaluate_acceptance_criteria(summary)

    # Build report
    report = {
        "task": "ISSUE-004",
        "script": "backtest_patterns.py",
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "data_file": str(args.data),
            "train_window": args.train_window,
            "test_window": args.test_window,
            "top_k": args.top_k,
            "test_combination": test_combination,
        },
        "data_stats": {
            "n_draws": len(draws),
            "n_folds": len(results),
            "date_range": {
                "start": draws[0].date.isoformat() if draws else None,
                "end": draws[-1].date.isoformat() if draws else None,
            },
        },
        "summary": summary,
        "fold_details": [
            {
                "fold_id": r.fold_id,
                "train_range": [r.train_start, r.train_end],
                "test_range": [r.test_start, r.test_end],
                "n_train": r.n_train_draws,
                "n_test": r.n_test_draws,
                "metrics": {
                    ptype: {
                        "precision": m.precision,
                        "recall": m.recall,
                        "lift": m.lift,
                        "hits": m.hits,
                    }
                    for ptype, m in r.metrics.items()
                },
            }
            for r in results
        ],
        "acceptance_criteria": acceptance,
    }

    # Write report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Report saved to: {args.output}")

    # Print summary
    print("\n" + "=" * 60)
    print("PATTERN BACKTEST COMPLETE")
    print("=" * 60)
    print(f"Folds: {len(results)}")
    print(f"Train Window: {args.train_window}")
    print(f"Test Window: {args.test_window}")
    print()
    print("Aggregated Metrics:")
    for ptype, metrics in summary.items():
        print(f"  {ptype}:")
        print(f"    Precision: {metrics['mean_precision']:.4f} +/- {metrics['std_precision']:.4f}")
        print(f"    Recall:    {metrics['mean_recall']:.6f} +/- {metrics['std_recall']:.6f}")
        print(f"    Lift:      {metrics['mean_lift']:.2f} +/- {metrics['std_lift']:.2f}")
        print(f"    Baseline:  {metrics['baseline_rate']:.6f}")
    print()
    print(f"Acceptance Criteria: {acceptance['passed']}/{acceptance['total']} passed")
    print(f"All Passed: {acceptance['all_passed']}")
    print()
    print(f"Full report: {args.output}")

    return 0 if acceptance["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
