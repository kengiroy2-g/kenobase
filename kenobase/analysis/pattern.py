"""Muster-Erkennung fuer Kombinationen in Ziehungen (Duos, Trios, Quatros).

Dieses Modul implementiert die Pattern-Extraktion fuer Kenobase V2.0.
Es erkennt alle Sub-Kombinationen wenn eine Spielkombination mit einer
Ziehung uebereinstimmt.

BUG-FIX: Behebt den exklusiven elif-Bug aus V9 (Zeilen 130-135).
Das alte Verhalten extrahierte bei 4 Treffern NUR das Quatro und verlor
die 4 Trios und 6 Duos. Jetzt werden ALLE Sub-Kombinationen erfasst.

Usage:
    from kenobase.analysis.pattern import (
        PatternResult,
        extract_patterns,
        extract_patterns_from_draws,
    )

    # Einzelne Ueberpruefung
    combination = [1, 5, 12, 23, 34, 45]
    draw_numbers = [1, 5, 12, 23, 7, 9, ...]  # 20 KENO-Zahlen
    result = extract_patterns(combination, draw_numbers)

    # Alle Muster aus DrawResults
    patterns = extract_patterns_from_draws(combination, draws)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult


@dataclass
class PatternResult:
    """Ergebnis der Muster-Extraktion fuer eine Kombination.

    Attributes:
        combination: Die analysierte Spielkombination (z.B. 6 Zahlen)
        match_count: Anzahl der Treffer (Uebereinstimmungen)
        matched_numbers: Die uebereinstimmenden Zahlen
        duos: Liste aller 2er-Kombinationen aus den Treffern
        trios: Liste aller 3er-Kombinationen aus den Treffern
        quatros: Liste aller 4er-Kombinationen aus den Treffern
    """

    combination: tuple[int, ...]
    match_count: int
    matched_numbers: frozenset[int]
    duos: list[tuple[int, int]] = field(default_factory=list)
    trios: list[tuple[int, int, int]] = field(default_factory=list)
    quatros: list[tuple[int, int, int, int]] = field(default_factory=list)

    @property
    def total_patterns(self) -> int:
        """Gesamtanzahl aller extrahierten Muster."""
        return len(self.duos) + len(self.trios) + len(self.quatros)


def extract_patterns(
    combination: list[int] | tuple[int, ...],
    draw_numbers: list[int] | tuple[int, ...] | set[int],
) -> PatternResult:
    """Extrahiert ALLE Sub-Muster aus der Uebereinstimmung.

    BUG-FIX: Verwendet parallele if-Statements statt exklusiver elif-Kette.
    Bei 4 Treffern werden jetzt korrekt extrahiert:
      - 1 Quatro: C(4,4) = 1
      - 4 Trios: C(4,3) = 4
      - 6 Duos: C(4,2) = 6
      - Gesamt: 11 Muster

    Bei 3 Treffern:
      - 1 Trio: C(3,3) = 1
      - 3 Duos: C(3,2) = 3
      - Gesamt: 4 Muster

    Bei 2 Treffern:
      - 1 Duo: C(2,2) = 1
      - Gesamt: 1 Muster

    Args:
        combination: Spielkombination (z.B. 6 Zahlen)
        draw_numbers: Gezogene Zahlen (z.B. 20 KENO-Zahlen)

    Returns:
        PatternResult mit allen extrahierten Mustern

    Example:
        >>> combi = [1, 5, 12, 23, 34, 45]
        >>> draw = [1, 5, 12, 23, 7, 9, 14, 18, 22, 28,
        ...         33, 41, 48, 52, 55, 61, 64, 67, 69, 70]
        >>> result = extract_patterns(combi, draw)
        >>> result.match_count
        4
        >>> len(result.quatros)  # C(4,4) = 1
        1
        >>> len(result.trios)    # C(4,3) = 4
        4
        >>> len(result.duos)     # C(4,2) = 6
        6
        >>> result.total_patterns
        11
    """
    combo_set = set(combination)
    draw_set = set(draw_numbers) if not isinstance(draw_numbers, set) else draw_numbers

    matched = combo_set.intersection(draw_set)
    match_count = len(matched)

    duos: list[tuple[int, int]] = []
    trios: list[tuple[int, int, int]] = []
    quatros: list[tuple[int, int, int, int]] = []

    # FIX: Parallel extraction - NOT exclusive elif!
    # Extract ALL sub-patterns from the matched numbers.

    if match_count >= 4:
        # Extract all 4-combinations from matched numbers
        quatros = [tuple(sorted(q)) for q in combinations(matched, 4)]

    if match_count >= 3:
        # Extract all 3-combinations from matched numbers
        trios = [tuple(sorted(t)) for t in combinations(matched, 3)]

    if match_count >= 2:
        # Extract all 2-combinations from matched numbers
        duos = [tuple(sorted(d)) for d in combinations(matched, 2)]

    return PatternResult(
        combination=tuple(sorted(combination)),
        match_count=match_count,
        matched_numbers=frozenset(matched),
        duos=duos,
        trios=trios,
        quatros=quatros,
    )


def extract_patterns_from_draws(
    combination: list[int] | tuple[int, ...],
    draws: list[DrawResult],
) -> list[PatternResult]:
    """Extrahiert Muster fuer eine Kombination ueber mehrere Ziehungen.

    Args:
        combination: Spielkombination (z.B. 6 Zahlen)
        draws: Liste von DrawResult-Objekten

    Returns:
        Liste von PatternResult (nur Ziehungen mit mind. 2 Treffern)

    Example:
        >>> from kenobase.core.data_loader import DataLoader
        >>> loader = DataLoader()
        >>> draws = loader.load("data/KENO_Stats.csv")
        >>> combi = [1, 5, 12, 23, 34, 45]
        >>> results = extract_patterns_from_draws(combi, draws)
        >>> len([r for r in results if r.match_count >= 4])
        3  # Anzahl Ziehungen mit 4+ Treffern
    """
    results = []
    for draw in draws:
        pattern = extract_patterns(combination, draw.numbers)
        # Only include draws with at least 2 matches (at least one duo)
        if pattern.match_count >= 2:
            results.append(pattern)
    return results


def aggregate_patterns(
    pattern_results: list[PatternResult],
) -> dict[str, dict[tuple[int, ...], int]]:
    """Aggregiert Muster-Haeufigkeiten ueber mehrere Ziehungen.

    Args:
        pattern_results: Liste von PatternResult-Objekten

    Returns:
        Dictionary mit Muster-Typ als Key und Haeufigkeits-Dict als Value.
        Beispiel:
        {
            "duos": {(1, 5): 3, (5, 12): 2, ...},
            "trios": {(1, 5, 12): 1, ...},
            "quatros": {...}
        }
    """
    from collections import Counter

    duo_counter: Counter[tuple[int, int]] = Counter()
    trio_counter: Counter[tuple[int, int, int]] = Counter()
    quatro_counter: Counter[tuple[int, int, int, int]] = Counter()

    for result in pattern_results:
        duo_counter.update(result.duos)
        trio_counter.update(result.trios)
        quatro_counter.update(result.quatros)

    return {
        "duos": dict(duo_counter),
        "trios": dict(trio_counter),
        "quatros": dict(quatro_counter),
    }


def calculate_pattern_lift(
    observed_freq: int,
    total_draws: int,
    pool_size: int,
    drawn_per_draw: int,
    pattern_size: int,
) -> tuple[float, float, float]:
    """Berechnet den Lift eines Patterns gegenueber Zufalls-Baseline.

    Lift = observed_rate / expected_rate
    - Lift > 1: Pattern erscheint haeufiger als zufaellig erwartet
    - Lift = 1: Pattern entspricht Zufall
    - Lift < 1: Pattern erscheint seltener als erwartet

    Args:
        observed_freq: Beobachtete Haeufigkeit des Patterns
        total_draws: Gesamtanzahl Ziehungen
        pool_size: Groesse des Zahlenpools (z.B. 70 bei KENO)
        drawn_per_draw: Anzahl gezogener Zahlen pro Ziehung (z.B. 20)
        pattern_size: Groesse des Patterns (2, 3, oder 4)

    Returns:
        Tuple aus (observed_rate, expected_rate, lift)

    Example:
        >>> # Duo erscheint 15 mal in 100 KENO-Ziehungen
        >>> obs, exp, lift = calculate_pattern_lift(15, 100, 70, 20, 2)
        >>> obs
        0.15
        >>> round(exp, 4)  # (20*19)/(70*69) approx 0.0788
        0.0788
        >>> round(lift, 2)  # 0.15 / 0.0788 approx 1.90
        1.9
    """
    if total_draws == 0:
        return 0.0, 0.0, 1.0

    observed_rate = observed_freq / total_draws

    # Berechne erwartete Wahrscheinlichkeit (hypergeometrisch approx)
    # P(alle k Zahlen gezogen) = product((drawn-i)/(pool-i)) fuer i in 0..k-1
    expected_rate = 1.0
    for i in range(pattern_size):
        expected_rate *= (drawn_per_draw - i) / (pool_size - i)

    # Berechne Lift
    lift = observed_rate / expected_rate if expected_rate > 0 else 1.0

    return observed_rate, expected_rate, lift


def calculate_feature_importance(
    pattern_frequencies: dict[tuple[int, ...], int],
    total_draws: int,
    pool_size: int = 70,
    drawn_per_draw: int = 20,
) -> list[dict]:
    """Berechnet Feature-Importance fuer alle Patterns.

    Sortiert Patterns nach Lift (absteigend). Patterns mit hohem Lift
    sind statistisch interessanter als erwarteter Zufall.

    Args:
        pattern_frequencies: Dict {pattern_tuple: frequency}
        total_draws: Gesamtanzahl Ziehungen
        pool_size: Groesse des Zahlenpools
        drawn_per_draw: Anzahl gezogener Zahlen pro Ziehung

    Returns:
        Liste von Dicts mit pattern, frequency, observed_rate, expected_rate, lift
        Sortiert nach Lift (hoechster zuerst)

    Example:
        >>> freqs = {(1, 5): 15, (12, 23): 8, (34, 45): 20}
        >>> importance = calculate_feature_importance(freqs, 100, 70, 20)
        >>> importance[0]["pattern"]  # Hoechster Lift
        (34, 45)
    """
    results = []

    for pattern, freq in pattern_frequencies.items():
        pattern_size = len(pattern)
        obs_rate, exp_rate, lift = calculate_pattern_lift(
            freq, total_draws, pool_size, drawn_per_draw, pattern_size
        )

        results.append({
            "pattern": pattern,
            "frequency": freq,
            "observed_rate": obs_rate,
            "expected_rate": exp_rate,
            "lift": lift,
            "pattern_size": pattern_size,
        })

    # Sortiere nach Lift (absteigend)
    results.sort(key=lambda x: x["lift"], reverse=True)

    return results


def get_significant_patterns(
    aggregated: dict[str, dict[tuple[int, ...], int]],
    total_draws: int,
    min_lift: float = 1.5,
    min_frequency: int = 3,
    pool_size: int = 70,
    drawn_per_draw: int = 20,
) -> dict[str, list[dict]]:
    """Filtert statistisch signifikante Patterns.

    Ein Pattern gilt als signifikant wenn:
    1. Lift >= min_lift (standardmaessig 1.5x ueber Zufall)
    2. Frequency >= min_frequency (mind. 3 Vorkommen)

    Args:
        aggregated: Aggregierte Patterns aus aggregate_patterns()
        total_draws: Gesamtanzahl Ziehungen
        min_lift: Minimaler Lift fuer Signifikanz
        min_frequency: Minimale Haeufigkeit
        pool_size: Groesse des Zahlenpools
        drawn_per_draw: Anzahl gezogener Zahlen pro Ziehung

    Returns:
        Dict mit Pattern-Typ als Key und Liste signifikanter Patterns

    Example:
        >>> from kenobase.analysis.pattern import aggregate_patterns
        >>> aggregated = aggregate_patterns(pattern_results)
        >>> significant = get_significant_patterns(aggregated, 100)
        >>> len(significant["duos"])  # Anzahl signifikanter Duos
        5
    """
    result = {}

    for ptype, patterns in aggregated.items():
        importance = calculate_feature_importance(
            patterns, total_draws, pool_size, drawn_per_draw
        )

        # Filtere nach Signifikanz-Kriterien
        significant = [
            p for p in importance
            if p["lift"] >= min_lift and p["frequency"] >= min_frequency
        ]

        result[ptype] = significant

    return result


__all__ = [
    "PatternResult",
    "extract_patterns",
    "extract_patterns_from_draws",
    "aggregate_patterns",
    "calculate_pattern_lift",
    "calculate_feature_importance",
    "get_significant_patterns",
]
