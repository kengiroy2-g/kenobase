#!/usr/bin/env python3
"""HYP-007: Duo/Trio/Quatro Pattern Validation.

Dieses Script validiert die Hypothese, dass Duo/Trio/Quatro Patterns
vorhersagekraeftiger sind als der Zufall.

Methode (Walk-Forward Validation):
1. Training-Set: Erste 80% der Ziehungen
2. Test-Set: Letzte 20% der Ziehungen
3. Extrahiere haeufigste Patterns aus Training-Set
4. Zaehle Treffer dieser Patterns im Test-Set
5. Vergleiche mit Random Baseline (Monte Carlo, 1000 Iterationen)
6. Statistische Signifikanz via Permutationstest (p < 0.05)

Usage:
    python scripts/analyze_hyp007.py \
        --data data/raw/keno/KENO_ab_2018.csv \
        --output results/hyp007_pattern_validation.json

Output:
    JSON-Report mit Pattern-Metriken und Signifikanz-Test.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations
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
)
from kenobase.core.data_loader import DataLoader, DrawResult, GameType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class PatternValidationResult:
    """Ergebnis der Pattern-Validierung.

    Attributes:
        pattern_type: "duo", "trio", oder "quatro"
        top_n_patterns: Anzahl der getesteten Top-Patterns
        train_occurrences: Summe der Erscheinungen im Training-Set
        test_hits: Treffer der Patterns im Test-Set
        random_baseline_mean: Erwartungswert bei Zufall
        random_baseline_std: Standardabweichung bei Zufall
        z_score: (test_hits - baseline_mean) / baseline_std
        p_value: Permutationstest p-Wert
        is_significant: p < 0.05
        top_patterns: Liste der Top-Patterns mit Counts
    """

    pattern_type: str
    top_n_patterns: int
    train_occurrences: int
    test_hits: int
    random_baseline_mean: float
    random_baseline_std: float
    z_score: float
    p_value: float
    is_significant: bool
    top_patterns: list[tuple[tuple[int, ...], int]] = field(default_factory=list)


def generate_random_combination(pool_size: int = 70, combo_size: int = 6) -> list[int]:
    """Generiert eine zufaellige Kombination.

    Args:
        pool_size: Zahlenpool (KENO: 1-70)
        combo_size: Kombinationsgroesse

    Returns:
        Sortierte Liste von Zahlen
    """
    return sorted(random.sample(range(1, pool_size + 1), combo_size))


def extract_patterns_from_draw(draw_numbers: list[int]) -> dict[str, list[tuple]]:
    """Extrahiert alle moeglichen Patterns aus einer Ziehung.

    Da KENO 20 aus 70 zieht, extrahieren wir:
    - Alle C(20,2)=190 Duos
    - Alle C(20,3)=1140 Trios
    - Alle C(20,4)=4845 Quatros

    Args:
        draw_numbers: 20 gezogene KENO-Zahlen

    Returns:
        Dict mit "duos", "trios", "quatros" als Keys
    """
    draw_set = set(draw_numbers)
    return {
        "duos": [tuple(sorted(d)) for d in combinations(draw_set, 2)],
        "trios": [tuple(sorted(t)) for t in combinations(draw_set, 3)],
        "quatros": [tuple(sorted(q)) for q in combinations(draw_set, 4)],
    }


def count_pattern_hits(
    patterns: set[tuple],
    draw_numbers: list[int],
) -> int:
    """Zaehlt wie viele der Patterns in einer Ziehung vorkommen.

    Args:
        patterns: Menge der zu pruefenden Patterns
        draw_numbers: 20 gezogene Zahlen

    Returns:
        Anzahl der Treffer
    """
    draw_set = set(draw_numbers)
    hits = 0
    for pattern in patterns:
        if set(pattern).issubset(draw_set):
            hits += 1
    return hits


def calculate_random_baseline(
    top_patterns: set[tuple],
    test_draws: list[DrawResult],
    n_iterations: int = 1000,
) -> tuple[float, float, list[int]]:
    """Berechnet Random Baseline via Monte Carlo Simulation.

    Generiert n_iterations zufaellige Pattern-Sets gleicher Groesse
    und zaehlt deren Treffer im Test-Set.

    Args:
        top_patterns: Original Top-Patterns
        test_draws: Test-Ziehungen
        n_iterations: Anzahl Monte Carlo Iterationen

    Returns:
        (mean_hits, std_hits, all_hit_counts)
    """
    pattern_size = len(list(top_patterns)[0]) if top_patterns else 2
    n_patterns = len(top_patterns)

    random_hits = []

    for _ in range(n_iterations):
        # Generiere zufaellige Patterns gleicher Groesse
        random_patterns = set()
        while len(random_patterns) < n_patterns:
            nums = tuple(sorted(random.sample(range(1, 71), pattern_size)))
            random_patterns.add(nums)

        # Zaehle Treffer im Test-Set
        total_hits = sum(
            count_pattern_hits(random_patterns, draw.numbers) for draw in test_draws
        )
        random_hits.append(total_hits)

    return float(np.mean(random_hits)), float(np.std(random_hits)), random_hits


def validate_pattern_type(
    pattern_type: str,
    train_draws: list[DrawResult],
    test_draws: list[DrawResult],
    top_n: int = 50,
    n_monte_carlo: int = 1000,
) -> PatternValidationResult:
    """Validiert einen Pattern-Typ (duo/trio/quatro).

    Args:
        pattern_type: "duo", "trio", oder "quatro"
        train_draws: Training-Ziehungen
        test_draws: Test-Ziehungen
        top_n: Anzahl Top-Patterns zu testen
        n_monte_carlo: Anzahl Monte Carlo Iterationen

    Returns:
        PatternValidationResult mit Metriken
    """
    logger.info(f"Validating {pattern_type}s (top {top_n})...")

    # Extrahiere Patterns aus Training-Set
    pattern_key = f"{pattern_type}s"
    pattern_counter: Counter = Counter()

    for draw in train_draws:
        patterns = extract_patterns_from_draw(draw.numbers)
        pattern_counter.update(patterns[pattern_key])

    # Top-N Patterns
    top_patterns_list = pattern_counter.most_common(top_n)
    top_patterns_set = {p for p, _ in top_patterns_list}
    train_occurrences = sum(c for _, c in top_patterns_list)

    # Zaehle Treffer im Test-Set
    test_hits = sum(
        count_pattern_hits(top_patterns_set, draw.numbers) for draw in test_draws
    )

    # Random Baseline
    baseline_mean, baseline_std, random_hits = calculate_random_baseline(
        top_patterns_set, test_draws, n_monte_carlo
    )

    # Z-Score
    z_score = (
        (test_hits - baseline_mean) / baseline_std if baseline_std > 0 else 0.0
    )

    # P-Value (einseitiger Test: sind echte Patterns besser als Zufall?)
    p_value = sum(1 for h in random_hits if h >= test_hits) / len(random_hits)

    return PatternValidationResult(
        pattern_type=pattern_type,
        top_n_patterns=top_n,
        train_occurrences=train_occurrences,
        test_hits=test_hits,
        random_baseline_mean=baseline_mean,
        random_baseline_std=baseline_std,
        z_score=z_score,
        p_value=p_value,
        is_significant=p_value < 0.05,
        top_patterns=[(p, c) for p, c in top_patterns_list[:10]],  # Top 10 only
    )


def run_validation(
    draws: list[DrawResult],
    train_ratio: float = 0.8,
    top_n: int = 50,
    n_monte_carlo: int = 1000,
) -> dict[str, PatternValidationResult]:
    """Fuehrt komplette Pattern-Validierung durch.

    Args:
        draws: Alle Ziehungen (chronologisch sortiert)
        train_ratio: Anteil Training-Set (default 80%)
        top_n: Anzahl Top-Patterns pro Typ
        n_monte_carlo: Anzahl Monte Carlo Iterationen

    Returns:
        Dict mit Ergebnissen pro Pattern-Typ
    """
    # Split in Train/Test
    split_idx = int(len(draws) * train_ratio)
    train_draws = draws[:split_idx]
    test_draws = draws[split_idx:]

    logger.info(f"Train set: {len(train_draws)} draws")
    logger.info(f"Test set: {len(test_draws)} draws")
    logger.info(f"Train period: {train_draws[0].date} - {train_draws[-1].date}")
    logger.info(f"Test period: {test_draws[0].date} - {test_draws[-1].date}")

    results = {}
    for pattern_type in ["duo", "trio", "quatro"]:
        results[pattern_type] = validate_pattern_type(
            pattern_type,
            train_draws,
            test_draws,
            top_n=top_n,
            n_monte_carlo=n_monte_carlo,
        )

    return results


def evaluate_acceptance_criteria(
    results: dict[str, PatternValidationResult],
) -> dict[str, Any]:
    """Evaluiert Acceptance Criteria fuer HYP-007.

    Criteria:
    1. Mindestens ein Pattern-Typ signifikant besser als Zufall (p < 0.05)
    2. Z-Score > 1.65 (90% Konfidenz) fuer mindestens einen Typ
    3. Test-Hits > Random Baseline fuer alle Typen

    Args:
        results: Validierungs-Ergebnisse pro Pattern-Typ

    Returns:
        Dict mit Acceptance Criteria Evaluation
    """
    any_significant = any(r.is_significant for r in results.values())
    any_high_zscore = any(r.z_score > 1.65 for r in results.values())
    all_above_baseline = all(
        r.test_hits > r.random_baseline_mean for r in results.values()
    )

    criteria = {
        "any_pattern_significant": {
            "target": "p < 0.05 for at least one pattern type",
            "actual": [
                f"{k}: p={v.p_value:.4f}" for k, v in results.items() if v.is_significant
            ],
            "passed": any_significant,
        },
        "any_high_zscore": {
            "target": "z-score > 1.65 (90% confidence)",
            "actual": {k: round(v.z_score, 3) for k, v in results.items()},
            "passed": any_high_zscore,
        },
        "all_above_baseline": {
            "target": "test_hits > random baseline for all types",
            "actual": {
                k: f"{v.test_hits} vs {v.random_baseline_mean:.1f}"
                for k, v in results.items()
            },
            "passed": all_above_baseline,
        },
    }

    n_passed = sum(1 for c in criteria.values() if c["passed"])
    n_total = len(criteria)

    return {
        "criteria": criteria,
        "passed": n_passed,
        "total": n_total,
        "hypothesis_supported": any_significant,  # Main criterion
    }


def main():
    parser = argparse.ArgumentParser(
        description="HYP-007: Duo/Trio/Quatro Pattern Validation"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/raw/keno/KENO_ab_2018.csv"),
        help="Pfad zur KENO CSV-Datei",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/hyp007_pattern_validation.json"),
        help="Pfad fuer Output-JSON",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.8,
        help="Anteil Training-Set (default: 0.8)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=50,
        help="Anzahl Top-Patterns pro Typ (default: 50)",
    )
    parser.add_argument(
        "--monte-carlo",
        type=int,
        default=1000,
        help="Anzahl Monte Carlo Iterationen (default: 1000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed fuer Reproduzierbarkeit",
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

    # Set seed
    random.seed(args.seed)
    np.random.seed(args.seed)

    # Validate input
    if not args.data.exists():
        logger.error(f"Data file not found: {args.data}")
        sys.exit(1)

    # Create output directory
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Load data
    logger.info(f"Loading KENO data from {args.data}")
    loader = DataLoader()
    draws = loader.load(args.data, game_type=GameType.KENO)

    # Sort by date (chronological order)
    draws.sort(key=lambda d: d.date)
    logger.info(f"Loaded {len(draws)} draws ({draws[0].date} - {draws[-1].date})")

    # Run validation
    logger.info("Starting pattern validation...")
    results = run_validation(
        draws,
        train_ratio=args.train_ratio,
        top_n=args.top_n,
        n_monte_carlo=args.monte_carlo,
    )

    # Evaluate acceptance criteria
    acceptance = evaluate_acceptance_criteria(results)

    # Build report
    report = {
        "hypothesis": "HYP-007",
        "title": "Duo/Trio/Quatro Pattern Prediction",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "data_file": str(args.data),
            "n_draws": len(draws),
            "train_ratio": args.train_ratio,
            "top_n_patterns": args.top_n,
            "monte_carlo_iterations": args.monte_carlo,
            "random_seed": args.seed,
        },
        "results": {
            pattern_type: {
                "pattern_type": r.pattern_type,
                "top_n_patterns": r.top_n_patterns,
                "train_occurrences": r.train_occurrences,
                "test_hits": r.test_hits,
                "random_baseline_mean": round(r.random_baseline_mean, 2),
                "random_baseline_std": round(r.random_baseline_std, 2),
                "z_score": round(r.z_score, 4),
                "p_value": round(r.p_value, 4),
                "is_significant": r.is_significant,
                "top_10_patterns": [
                    {"pattern": list(p), "count": c} for p, c in r.top_patterns
                ],
            }
            for pattern_type, r in results.items()
        },
        "acceptance_criteria": acceptance,
        "summary": {
            "hypothesis_supported": acceptance["hypothesis_supported"],
            "key_findings": [],
        },
    }

    # Add key findings
    for ptype, r in results.items():
        if r.is_significant:
            report["summary"]["key_findings"].append(
                f"{ptype.capitalize()}s: Signifikant (p={r.p_value:.4f}, z={r.z_score:.2f})"
            )
        elif r.test_hits > r.random_baseline_mean:
            report["summary"]["key_findings"].append(
                f"{ptype.capitalize()}s: Ueber Baseline (+{r.test_hits - r.random_baseline_mean:.0f}), "
                f"aber nicht signifikant (p={r.p_value:.4f})"
            )
        else:
            report["summary"]["key_findings"].append(
                f"{ptype.capitalize()}s: Unter/gleich Baseline (p={r.p_value:.4f})"
            )

    # Write report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Report saved to: {args.output}")

    # Print summary
    print("\n" + "=" * 70)
    print("HYP-007: DUO/TRIO/QUATRO PATTERN VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Data: {len(draws)} KENO draws ({draws[0].date.date()} - {draws[-1].date.date()})")
    print(f"Split: {int(args.train_ratio*100)}% train / {int((1-args.train_ratio)*100)}% test")
    print()
    print("RESULTS:")
    print("-" * 70)
    print(f"{'Type':<10} {'Hits':<8} {'Baseline':<12} {'Z-Score':<10} {'P-Value':<10} {'Sig?':<6}")
    print("-" * 70)
    for ptype, r in results.items():
        sig_marker = "YES" if r.is_significant else "no"
        print(
            f"{ptype.capitalize():<10} {r.test_hits:<8} "
            f"{r.random_baseline_mean:>6.1f}+/-{r.random_baseline_std:>4.1f} "
            f"{r.z_score:>10.3f} {r.p_value:>10.4f} {sig_marker:<6}"
        )
    print("-" * 70)
    print()
    print(f"Acceptance Criteria: {acceptance['passed']}/{acceptance['total']} passed")
    print(f"Hypothesis Supported: {acceptance['hypothesis_supported']}")
    print()
    print("Key Findings:")
    for finding in report["summary"]["key_findings"]:
        print(f"  - {finding}")
    print()
    print(f"Full report: {args.output}")

    return 0 if acceptance["hypothesis_supported"] else 1


if __name__ == "__main__":
    sys.exit(main())
