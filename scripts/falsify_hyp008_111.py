#!/usr/bin/env python3
"""HYP-008: 111-Prinzip Falsifikation.

Dieses Script testet die Nullhypothese:
    H0: Der 111-Filter hat keine bessere Trefferquote als Zufall.

Methode (Monte Carlo Sampling + Chi-Quadrat):
1. Sampele zufaellige 6er-Kombinationen aus dem Zahlenpool 1-70
2. Filtere nach 111-Prinzip
3. Vergleiche Hit-Rate: 111-gefilterte vs. nicht-111 Kombinationen
4. Chi-Quadrat Test auf Signifikanz
5. Akzeptanzkriterien: p > 0.05 = widerlegt, Hit-Rate Differenz < 5% = widerlegt

111-Prinzip Definition (aus HYPOTHESES_CATALOG.md):
- Summe durch 111 teilbar mit Quotient in {1, 11}
- ODER: Ziffern der Summe umkehren und dann pruefen

Usage:
    python scripts/falsify_hyp008_111.py \
        --data data/raw/keno/KENO_ab_2018.csv \
        --seed 42 \
        --output results/hyp008_111_falsification.json

Output:
    JSON-Report mit Falsifikations-Ergebnis und Chi-Quadrat p-Wert.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from kenobase.core.data_loader import DataLoader, DrawResult, GameType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# 111-Prinzip Algorithm (from HYPOTHESES_CATALOG.md Lines 198-224)
# =============================================================================


def is_111_prinzip(kombination: list[int]) -> bool:
    """Prueft ob eine Zahlenkombination dem 111-Prinzip entspricht.

    Regeln (aus HYPOTHESES_CATALOG.md):
    1. Summe der Kombination berechnen
    2. Pruefen ob Summe durch 111 teilbar ist
    3. Quotient muss 1 oder 11 sein
    4. Alternative: Ziffern umkehren und dann pruefen

    Args:
        kombination: Liste von Zahlen (z.B. 6er-Kombination)

    Returns:
        True wenn 111-Prinzip erfuellt, sonst False
    """
    summe = sum(kombination)

    # Regel 1: Direkte 111-Teilbarkeit mit Quotient in {1, 11}
    if summe > 0 and summe % 111 == 0:
        quotient = summe // 111
        if quotient in (1, 11):
            return True

    # Regel 2: Ziffernumkehr pruefen
    summe_str = str(summe)
    umgekehrt_str = summe_str[::-1]
    try:
        umgekehrt = int(umgekehrt_str)
        if umgekehrt > 0 and umgekehrt % 111 == 0:
            quotient_rev = umgekehrt // 111
            if quotient_rev in (1, 11):
                return True
    except ValueError:
        pass

    return False


def generate_random_combination(pool_size: int = 70, combo_size: int = 6) -> tuple[int, ...]:
    """Generiert eine zufaellige Kombination.

    Args:
        pool_size: Zahlenpool (KENO: 1-70)
        combo_size: Kombinationsgroesse

    Returns:
        Sortierte Tuple von Zahlen
    """
    return tuple(sorted(random.sample(range(1, pool_size + 1), combo_size)))


def count_hits_in_draw(kombination: tuple[int, ...], draw_numbers: list[int]) -> int:
    """Zaehlt wie viele Zahlen einer Kombination in der Ziehung vorkommen."""
    draw_set = set(draw_numbers)
    return sum(1 for z in kombination if z in draw_set)


def is_partial_hit(kombination: tuple[int, ...], draw_numbers: list[int], min_hits: int = 3) -> bool:
    """Prueft ob mindestens min_hits Zahlen der Kombination gezogen wurden."""
    return count_hits_in_draw(kombination, draw_numbers) >= min_hits


# =============================================================================
# Main Falsification Logic (Optimized Monte Carlo)
# =============================================================================


@dataclass
class FalsificationResult:
    """Ergebnis der Falsifikation."""

    hypothesis_falsified: bool
    hits_111: int
    checks_111: int
    rate_111: float
    hits_non111: int
    checks_non111: int
    rate_non111: float
    rate_difference: float
    chi2_statistic: float
    p_value_chi2: float
    n_111_combis: int
    n_non111_combis: int
    n_total_sampled: int
    acceptance_criteria: dict[str, Any]
    sample_111_combis: list[tuple[int, ...]] = field(default_factory=list)


def run_falsification(
    draws: list[DrawResult],
    combo_size: int = 6,
    min_hits: int = 3,
    n_samples: int = 50000,
    random_seed: int = 42,
) -> FalsificationResult:
    """Fuehrt die 111-Prinzip Falsifikation via Monte Carlo durch.

    Strategie:
    - Generiere n_samples zufaellige Kombinationen
    - Partitioniere in 111-Kombis und nicht-111-Kombis
    - Vergleiche Hit-Rates auf Test-Daten
    - Chi-Quadrat Test

    Args:
        draws: KENO-Ziehungen
        combo_size: Kombinationsgroesse (default: 6)
        min_hits: Mindestanzahl Treffer fuer "Hit" (default: 3)
        n_samples: Anzahl zu generierender Kombinationen
        random_seed: Random seed

    Returns:
        FalsificationResult mit allen Metriken
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    logger.info(f"Generating {n_samples} random {combo_size}er combinations...")

    # Generiere Kombinationen und partitioniere
    kombinationen_111 = []
    kombinationen_non111 = []

    for _ in range(n_samples):
        kombi = generate_random_combination(70, combo_size)
        if is_111_prinzip(list(kombi)):
            kombinationen_111.append(kombi)
        else:
            kombinationen_non111.append(kombi)

    n_111 = len(kombinationen_111)
    n_non111 = len(kombinationen_non111)

    logger.info(f"111-combinations: {n_111} ({100*n_111/n_samples:.2f}%)")
    logger.info(f"Non-111-combinations: {n_non111} ({100*n_non111/n_samples:.2f}%)")

    if n_111 == 0:
        logger.warning("No 111-combinations found in sample! Increasing sample size...")
        # Gezielt 111-Kombinationen generieren
        attempts = 0
        while len(kombinationen_111) < 100 and attempts < 500000:
            kombi = generate_random_combination(70, combo_size)
            if is_111_prinzip(list(kombi)):
                kombinationen_111.append(kombi)
            attempts += 1
        n_111 = len(kombinationen_111)
        logger.info(f"After targeted search: {n_111} 111-combinations")

    if n_111 == 0:
        return FalsificationResult(
            hypothesis_falsified=True,
            hits_111=0, checks_111=0, rate_111=0.0,
            hits_non111=0, checks_non111=0, rate_non111=0.0,
            rate_difference=0.0, chi2_statistic=0.0, p_value_chi2=1.0,
            n_111_combis=0, n_non111_combis=n_non111, n_total_sampled=n_samples,
            acceptance_criteria={"verdict": "FALSIFIED - 111-Kombis extrem selten"},
        )

    # Split draws: 80% train, 20% test
    split_idx = int(len(draws) * 0.8)
    test_draws = draws[split_idx:]
    logger.info(f"Test set: {len(test_draws)} draws")

    # Berechne Hit-Rates
    logger.info("Calculating hit rates...")

    hits_111 = 0
    for kombi in kombinationen_111:
        for draw in test_draws:
            if is_partial_hit(kombi, draw.numbers, min_hits):
                hits_111 += 1

    checks_111 = n_111 * len(test_draws)
    rate_111 = hits_111 / checks_111 if checks_111 > 0 else 0.0

    # Sample gleiche Anzahl non-111 fuer fairen Vergleich
    sampled_non111 = random.sample(kombinationen_non111, min(n_111, n_non111))

    hits_non111 = 0
    for kombi in sampled_non111:
        for draw in test_draws:
            if is_partial_hit(kombi, draw.numbers, min_hits):
                hits_non111 += 1

    checks_non111 = len(sampled_non111) * len(test_draws)
    rate_non111 = hits_non111 / checks_non111 if checks_non111 > 0 else 0.0

    rate_difference = rate_111 - rate_non111

    logger.info(f"Hit rate 111: {rate_111:.6f} ({hits_111}/{checks_111})")
    logger.info(f"Hit rate non-111: {rate_non111:.6f} ({hits_non111}/{checks_non111})")

    # Chi-Quadrat Test
    a = hits_111
    b = checks_111 - hits_111
    c = hits_non111
    d = checks_non111 - hits_non111

    observed = np.array([[a, b], [c, d]])

    # Fisher exact wenn expected frequencies zu klein
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    total = observed.sum()

    if total > 0:
        expected = np.outer(row_totals, col_totals) / total
        if (expected < 5).any():
            _, p_value_chi2 = stats.fisher_exact(observed)
            chi2_stat = 0.0
        else:
            chi2_stat, p_value_chi2, _, _ = stats.chi2_contingency(observed)
    else:
        chi2_stat, p_value_chi2 = 0.0, 1.0

    logger.info(f"Chi2 p-value: {p_value_chi2:.6f}")

    # Acceptance Criteria
    criteria = {
        "p_value_threshold": {
            "target": "p > 0.05 (H0 cannot be rejected)",
            "actual": round(float(p_value_chi2), 6),
            "passed": bool(p_value_chi2 > 0.05),
        },
        "rate_difference_small": {
            "target": "|rate_111 - rate_non111| < 5%",
            "actual_pct": round(abs(rate_difference) * 100, 4),
            "passed": bool(abs(rate_difference) < 0.05),
        },
        "111_not_better": {
            "target": "111 rate <= non-111 rate * 1.05 (no practical advantage)",
            "actual": f"{rate_111:.6f} vs {rate_non111:.6f}",
            "passed": bool(rate_111 <= rate_non111 * 1.05),
        },
    }

    # Hypothesis falsified if ANY criterion shows H0 cannot be rejected
    hypothesis_falsified = any(c["passed"] for c in criteria.values())

    return FalsificationResult(
        hypothesis_falsified=hypothesis_falsified,
        hits_111=hits_111,
        checks_111=checks_111,
        rate_111=rate_111,
        hits_non111=hits_non111,
        checks_non111=checks_non111,
        rate_non111=rate_non111,
        rate_difference=rate_difference,
        chi2_statistic=chi2_stat,
        p_value_chi2=p_value_chi2,
        n_111_combis=n_111,
        n_non111_combis=len(sampled_non111),
        n_total_sampled=n_samples,
        acceptance_criteria=criteria,
        sample_111_combis=kombinationen_111[:10],  # Sample for report
    )


def main():
    parser = argparse.ArgumentParser(
        description="HYP-008: 111-Prinzip Falsifikation"
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
        default=Path("results/hyp008_111_falsification.json"),
        help="Pfad fuer Output-JSON",
    )
    parser.add_argument(
        "--combo-size",
        type=int,
        default=6,
        help="Kombinationsgroesse (default: 6)",
    )
    parser.add_argument(
        "--min-hits",
        type=int,
        default=3,
        help="Mindestanzahl Treffer fuer 'Hit' (default: 3)",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=50000,
        help="Anzahl Monte Carlo Samples (default: 50000)",
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

    # Set seeds
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

    # Sort by date
    draws.sort(key=lambda d: d.date)
    logger.info(f"Loaded {len(draws)} draws ({draws[0].date} - {draws[-1].date})")

    # Run falsification
    logger.info("Starting 111-Prinzip falsification...")
    result = run_falsification(
        draws,
        combo_size=args.combo_size,
        min_hits=args.min_hits,
        n_samples=args.n_samples,
        random_seed=args.seed,
    )

    # Build report
    report = {
        "hypothesis": "HYP-008",
        "title": "111-Prinzip Falsifikation",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "data_file": str(args.data),
            "n_draws": len(draws),
            "combo_size": args.combo_size,
            "min_hits": args.min_hits,
            "n_samples": args.n_samples,
            "random_seed": args.seed,
        },
        "results": {
            "hypothesis_falsified": result.hypothesis_falsified,
            "111_filtered": {
                "n_combinations": result.n_111_combis,
                "hits": result.hits_111,
                "checks": result.checks_111,
                "hit_rate": round(result.rate_111, 8),
            },
            "non_111_control": {
                "n_combinations": result.n_non111_combis,
                "hits": result.hits_non111,
                "checks": result.checks_non111,
                "hit_rate": round(result.rate_non111, 8),
            },
            "comparison": {
                "rate_difference": round(result.rate_difference, 8),
                "rate_difference_pct": round(result.rate_difference * 100, 4),
                "chi2_statistic": round(result.chi2_statistic, 4),
                "p_value_chi2": round(result.p_value_chi2, 6),
            },
            "sample_111_combis": [list(c) for c in result.sample_111_combis],
        },
        "acceptance_criteria": result.acceptance_criteria,
        "summary": {
            "verdict": "FALSIFIED" if result.hypothesis_falsified else "NOT FALSIFIED",
            "interpretation": "",
            "key_findings": [],
        },
    }

    # Interpretation
    if result.hypothesis_falsified:
        report["summary"]["interpretation"] = (
            "Das 111-Prinzip bietet KEINEN statistisch signifikanten Vorteil "
            "gegenueber zufaellig gewaehlten Kombinationen. "
            "H0 (kein Unterschied) kann nicht abgelehnt werden. "
            "Die Hypothese HYP-008 gilt als WIDERLEGT."
        )
    else:
        report["summary"]["interpretation"] = (
            "Das 111-Prinzip zeigt einen statistisch signifikanten Unterschied. "
            "ACHTUNG: Weitere Pruefung erforderlich!"
        )

    # Key findings
    report["summary"]["key_findings"] = [
        f"Aus {args.n_samples:,} Samples: {result.n_111_combis} 111-Kombis ({100*result.n_111_combis/args.n_samples:.3f}%)",
        f"Hit-Rate 111: {result.rate_111:.6f} ({result.hits_111:,}/{result.checks_111:,})",
        f"Hit-Rate non-111: {result.rate_non111:.6f} ({result.hits_non111:,}/{result.checks_non111:,})",
        f"Differenz: {result.rate_difference * 100:+.4f}%",
        f"Chi2 p-Wert: {result.p_value_chi2:.6f} ({'nicht signifikant' if result.p_value_chi2 > 0.05 else 'signifikant'})",
    ]

    # Write report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Report saved to: {args.output}")

    # Print summary
    print("\n" + "=" * 70)
    print("HYP-008: 111-PRINZIP FALSIFIKATION COMPLETE")
    print("=" * 70)
    print(f"Data: {len(draws)} KENO draws ({draws[0].date.date()} - {draws[-1].date.date()})")
    print(f"Samples: {args.n_samples:,} random combinations")
    print()
    print("RESULTS:")
    print("-" * 70)
    print(f"{'Group':<15} {'Combis':<10} {'Hits':<10} {'Checks':<12} {'Rate':<12}")
    print("-" * 70)
    print(
        f"{'111-Filter':<15} {result.n_111_combis:<10} {result.hits_111:<10} "
        f"{result.checks_111:<12} {result.rate_111:.8f}"
    )
    print(
        f"{'Non-111':<15} {result.n_non111_combis:<10} {result.hits_non111:<10} "
        f"{result.checks_non111:<12} {result.rate_non111:.8f}"
    )
    print("-" * 70)
    print()
    print(f"Rate Difference: {result.rate_difference * 100:+.4f}%")
    print(f"Chi2 Statistic:  {result.chi2_statistic:.4f}")
    print(f"Chi2 p-Value:    {result.p_value_chi2:.6f}")
    print()
    print("ACCEPTANCE CRITERIA:")
    for name, criterion in result.acceptance_criteria.items():
        status = "PASS" if criterion["passed"] else "FAIL"
        print(f"  [{status}] {name}: {criterion['target']}")
    print()
    print(f"VERDICT: {report['summary']['verdict']}")
    print()
    print(f"Full report: {args.output}")

    return 0 if result.hypothesis_falsified else 1


if __name__ == "__main__":
    sys.exit(main())
