"""Zehnergruppen-Paar-Affinitaet Analyse (HYP-005).

Dieses Modul analysiert, ob bestimmte Dekaden-Paare (Zehnergruppen)
haeufiger gemeinsam in Ziehungen erscheinen als erwartet.

Eine Dekade ist eine Zehnergruppe von Zahlen:
- Dekade 0: 1-10
- Dekade 1: 11-20
- Dekade 2: 21-30
- Dekade 3: 31-40
- Dekade 4: 41-50
- Dekade 5: 51-60
- Dekade 6: 61-70

Chi-Quadrat-Test gegen Zufalls-Baseline wird verwendet um signifikante
Affinitaeten zu identifizieren.

Usage:
    from kenobase.analysis.decade_affinity import (
        DecadeAffinityResult,
        analyze_decade_affinity,
        get_top_affinity_pairs,
    )

    results = analyze_decade_affinity(draws)
    top_pairs = get_top_affinity_pairs(results, n=5)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import TYPE_CHECKING

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult


# Dekaden-Definition fuer KENO (1-70)
NUM_DECADES = 7
DECADES = {
    0: range(1, 11),   # 1-10
    1: range(11, 21),  # 11-20
    2: range(21, 31),  # 21-30
    3: range(31, 41),  # 31-40
    4: range(41, 51),  # 41-50
    5: range(51, 61),  # 51-60
    6: range(61, 71),  # 61-70
}


@dataclass(frozen=True)
class DecadeAffinityResult:
    """Ergebnis der Dekaden-Paar-Affinitaetsanalyse.

    Attributes:
        pair: Tuple der beiden Dekaden-Indizes (0-6)
        observed: Beobachtete Anzahl gemeinsamer Vorkommen
        expected: Erwartete Anzahl unter Zufallsannahme
        affinity_score: (observed - expected) / expected, positiv = Affinitaet
        p_value: P-Wert des Chi-Quadrat-Tests
        is_significant: True wenn p_value < 0.05
    """

    pair: tuple[int, int]
    observed: int
    expected: float
    affinity_score: float
    p_value: float
    is_significant: bool


def get_decade(number: int) -> int:
    """Bestimmt die Dekade einer Zahl.

    Args:
        number: Zahl zwischen 1 und 70

    Returns:
        Dekaden-Index (0-6)

    Raises:
        ValueError: Wenn Zahl ausserhalb des Bereichs
    """
    if number < 1 or number > 70:
        raise ValueError(f"Number {number} out of range [1, 70]")

    return (number - 1) // 10


def count_decade_occurrences(
    draws: list[DrawResult],
) -> tuple[Counter[int], Counter[tuple[int, int]]]:
    """Zaehlt Dekaden-Einzelvorkommen und Paar-Vorkommen.

    Args:
        draws: Liste von DrawResult-Objekten

    Returns:
        Tuple aus:
        - Counter fuer Einzeldekaden (wie oft jede Dekade in Ziehungen vorkommt)
        - Counter fuer Dekaden-Paare (wie oft beide Dekaden gemeinsam vorkommen)
    """
    single_counts: Counter[int] = Counter()
    pair_counts: Counter[tuple[int, int]] = Counter()

    for draw in draws:
        # Dekaden in dieser Ziehung
        decades_in_draw = set()
        for number in draw.numbers:
            if 1 <= number <= 70:
                decades_in_draw.add(get_decade(number))

        # Einzelzaehlung
        single_counts.update(decades_in_draw)

        # Paarzaehlung
        for pair in combinations(sorted(decades_in_draw), 2):
            pair_counts[pair] += 1

    return single_counts, pair_counts


def calculate_expected_pair_frequency(
    single_counts: Counter[int],
    n_draws: int,
    decade_a: int,
    decade_b: int,
) -> float:
    """Berechnet die erwartete Paar-Frequenz unter Unabhaengigkeit.

    Unter der Annahme, dass Dekaden unabhaengig gezogen werden:
    P(A und B) = P(A) * P(B)
    Expected = N * P(A) * P(B)

    Args:
        single_counts: Zaehler fuer Einzeldekaden
        n_draws: Gesamtzahl der Ziehungen
        decade_a: Erste Dekade
        decade_b: Zweite Dekade

    Returns:
        Erwartete Anzahl gemeinsamer Vorkommen
    """
    if n_draws == 0:
        return 0.0

    p_a = single_counts[decade_a] / n_draws
    p_b = single_counts[decade_b] / n_draws

    return n_draws * p_a * p_b


def chi_square_test_single_pair(
    observed: int,
    expected: float,
) -> tuple[float, float]:
    """Chi-Quadrat-Test fuer ein einzelnes Dekaden-Paar.

    Args:
        observed: Beobachtete Anzahl
        expected: Erwartete Anzahl

    Returns:
        Tuple aus (chi2_statistic, p_value)
    """
    if expected < 5:
        # Zu wenige erwartete Beobachtungen fuer Chi-Quadrat
        return 0.0, 1.0

    # Chi-Quadrat = (O - E)^2 / E
    chi2 = (observed - expected) ** 2 / expected

    # Einfreiheitsgrad (df=1 fuer einzelnes Paar)
    p_value = 1 - stats.chi2.cdf(chi2, df=1)

    return chi2, p_value


def analyze_decade_affinity(
    draws: list[DrawResult],
    alpha: float = 0.05,
) -> list[DecadeAffinityResult]:
    """Analysiert Dekaden-Paar-Affinitaeten in Ziehungsdaten.

    Berechnet fuer jedes moegliche Dekaden-Paar:
    - Beobachtete gemeinsame Vorkommen
    - Erwartete Vorkommen unter Unabhaengigkeit
    - Affinitaets-Score und statistische Signifikanz

    Args:
        draws: Liste von DrawResult-Objekten
        alpha: Signifikanzniveau (default: 0.05)

    Returns:
        Liste von DecadeAffinityResult, sortiert nach affinity_score (absteigend)
    """
    if not draws:
        return []

    n_draws = len(draws)
    single_counts, pair_counts = count_decade_occurrences(draws)

    results = []

    # Alle moeglichen Dekaden-Paare
    for decade_a, decade_b in combinations(range(NUM_DECADES), 2):
        pair = (decade_a, decade_b)
        observed = pair_counts[pair]
        expected = calculate_expected_pair_frequency(
            single_counts, n_draws, decade_a, decade_b
        )

        # Affinitaets-Score berechnen
        if expected > 0:
            affinity_score = (observed - expected) / expected
        else:
            affinity_score = 0.0

        # Chi-Quadrat-Test
        _, p_value = chi_square_test_single_pair(observed, expected)

        results.append(
            DecadeAffinityResult(
                pair=pair,
                observed=observed,
                expected=expected,
                affinity_score=affinity_score,
                p_value=float(p_value),
                is_significant=bool(p_value < alpha),
            )
        )

    # Sortiere nach Affinitaets-Score (absteigend)
    results.sort(key=lambda r: r.affinity_score, reverse=True)

    return results


def get_top_affinity_pairs(
    results: list[DecadeAffinityResult],
    n: int = 5,
    only_significant: bool = False,
) -> list[DecadeAffinityResult]:
    """Gibt die Top-N Paare nach Affinitaets-Score zurueck.

    Args:
        results: Liste von DecadeAffinityResult
        n: Anzahl der Top-Paare (default: 5)
        only_significant: Nur signifikante Paare (default: False)

    Returns:
        Liste der Top-N DecadeAffinityResult
    """
    if only_significant:
        filtered = [r for r in results if r.is_significant]
    else:
        filtered = results

    return filtered[:n]


def get_anti_affinity_pairs(
    results: list[DecadeAffinityResult],
    n: int = 5,
    only_significant: bool = False,
) -> list[DecadeAffinityResult]:
    """Gibt die N Paare mit niedrigster Affinitaet (Anti-Affinitaet) zurueck.

    Args:
        results: Liste von DecadeAffinityResult
        n: Anzahl der Anti-Affinitaets-Paare (default: 5)
        only_significant: Nur signifikante Paare (default: False)

    Returns:
        Liste der N Paare mit niedrigster Affinitaet
    """
    if only_significant:
        filtered = [r for r in results if r.is_significant]
    else:
        filtered = results

    # Sortiere aufsteigend nach affinity_score
    sorted_results = sorted(filtered, key=lambda r: r.affinity_score)
    return sorted_results[:n]


def decade_pair_to_name(pair: tuple[int, int]) -> str:
    """Konvertiert Dekaden-Indizes zu lesbarem Namen.

    Args:
        pair: Tuple von Dekaden-Indizes

    Returns:
        Lesbarer Name, z.B. "(1-10, 21-30)"
    """
    def decade_range(d: int) -> str:
        start = d * 10 + 1
        end = d * 10 + 10
        return f"{start}-{end}"

    return f"({decade_range(pair[0])}, {decade_range(pair[1])})"


def generate_affinity_report(
    results: list[DecadeAffinityResult],
    n_draws: int,
) -> str:
    """Generiert einen lesbaren Report der Dekaden-Affinitaetsanalyse.

    Args:
        results: Liste von DecadeAffinityResult
        n_draws: Anzahl der analysierten Ziehungen

    Returns:
        Formatierter Report als String
    """
    lines = [
        "=" * 60,
        "HYP-005: Zehnergruppen-Paar-Affinitaet",
        "=" * 60,
        f"\nAnalysierte Ziehungen: {n_draws}",
        f"Anzahl Dekaden-Paare: {len(results)}",
    ]

    # Signifikante Paare zaehlen
    sig_count = sum(1 for r in results if r.is_significant)
    lines.append(f"Signifikante Paare (p < 0.05): {sig_count}")

    # Top-5 Affinitaeten
    lines.extend([
        "\n--- Top-5 Affinitaets-Paare ---",
    ])

    top_5 = get_top_affinity_pairs(results, n=5)
    for i, r in enumerate(top_5, 1):
        sig_marker = "*" if r.is_significant else ""
        lines.append(
            f"{i}. {decade_pair_to_name(r.pair)}: "
            f"score={r.affinity_score:+.3f}, "
            f"obs={r.observed}, exp={r.expected:.1f}, "
            f"p={r.p_value:.4f}{sig_marker}"
        )

    # Top-5 Anti-Affinitaeten
    lines.extend([
        "\n--- Top-5 Anti-Affinitaets-Paare ---",
    ])

    anti_5 = get_anti_affinity_pairs(results, n=5)
    for i, r in enumerate(anti_5, 1):
        sig_marker = "*" if r.is_significant else ""
        lines.append(
            f"{i}. {decade_pair_to_name(r.pair)}: "
            f"score={r.affinity_score:+.3f}, "
            f"obs={r.observed}, exp={r.expected:.1f}, "
            f"p={r.p_value:.4f}{sig_marker}"
        )

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def run_hyp005_analysis(
    draws: list[DrawResult],
    alpha: float = 0.05,
) -> dict:
    """Fuehrt die vollstaendige HYP-005 Analyse durch.

    Args:
        draws: Liste von DrawResult-Objekten
        alpha: Signifikanzniveau (default: 0.05)

    Returns:
        Dictionary mit:
        - results: Liste aller DecadeAffinityResult
        - top_pairs: Top-5 Affinitaets-Paare
        - anti_pairs: Top-5 Anti-Affinitaets-Paare
        - summary: Zusammenfassende Statistiken
    """
    results = analyze_decade_affinity(draws, alpha=alpha)

    top_pairs = get_top_affinity_pairs(results, n=5)
    anti_pairs = get_anti_affinity_pairs(results, n=5)

    sig_results = [r for r in results if r.is_significant]

    summary = {
        "n_draws": len(draws),
        "n_pairs_total": len(results),
        "n_pairs_significant": len(sig_results),
        "alpha": alpha,
        "mean_affinity_score": float(np.mean([r.affinity_score for r in results])) if results else 0.0,
        "std_affinity_score": float(np.std([r.affinity_score for r in results])) if results else 0.0,
        "max_affinity_score": float(max(r.affinity_score for r in results)) if results else 0.0,
        "min_affinity_score": float(min(r.affinity_score for r in results)) if results else 0.0,
    }

    return {
        "results": results,
        "top_pairs": top_pairs,
        "anti_pairs": anti_pairs,
        "summary": summary,
    }


__all__ = [
    "DecadeAffinityResult",
    "NUM_DECADES",
    "DECADES",
    "get_decade",
    "count_decade_occurrences",
    "calculate_expected_pair_frequency",
    "chi_square_test_single_pair",
    "analyze_decade_affinity",
    "get_top_affinity_pairs",
    "get_anti_affinity_pairs",
    "decade_pair_to_name",
    "generate_affinity_report",
    "run_hyp005_analysis",
]
