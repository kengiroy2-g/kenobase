"""Haeufigkeitsanalyse fuer Lottozahlen.

Dieses Modul implementiert die Frequenzanalyse fuer Kenobase V2.0.
Es berechnet absolute und relative Haeufigkeiten einzelner Zahlen
sowie Zahlenpaare (Duos) mit Hot/Cold/Normal-Klassifikation.

Usage:
    from kenobase.analysis.frequency import (
        FrequencyResult,
        PairFrequencyResult,
        calculate_frequency,
        calculate_pair_frequency,
        classify_numbers,
    )

    from kenobase.core.data_loader import DrawResult

    # Einzelne Zahlen-Frequenzen
    results = calculate_frequency(draws)
    hot_numbers = [r.number for r in results if r.classification == "hot"]

    # Paar-Frequenzen (Duos)
    pair_results = calculate_pair_frequency(draws)
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult


@dataclass(frozen=True)
class FrequencyResult:
    """Ergebnis der Frequenzanalyse fuer eine einzelne Zahl.

    Attributes:
        number: Die analysierte Zahl
        absolute_frequency: Absolute Anzahl der Vorkommen
        relative_frequency: Relativer Anteil (0.0 - 1.0)
        classification: "hot", "cold", oder "normal"
    """

    number: int
    absolute_frequency: int
    relative_frequency: float
    classification: str


@dataclass(frozen=True)
class PairFrequencyResult:
    """Ergebnis der Paar-Frequenzanalyse (Duo).

    Attributes:
        pair: Tuple der beiden Zahlen (kleinere zuerst)
        absolute_frequency: Absolute Anzahl gemeinsamer Vorkommen
        relative_frequency: Relativer Anteil (0.0 - 1.0)
        classification: "hot", "cold", oder "normal"
    """

    pair: tuple[int, int]
    absolute_frequency: int
    relative_frequency: float
    classification: str


def calculate_frequency(
    draws: list[DrawResult],
    number_range: tuple[int, int] | None = None,
) -> list[FrequencyResult]:
    """Berechnet die Haeufigkeit jeder Zahl in den Ziehungen.

    Args:
        draws: Liste von DrawResult-Objekten
        number_range: Optionaler Zahlenbereich (min, max) fuer Initialisierung.
                      Wenn None, werden nur vorkommende Zahlen gezaehlt.

    Returns:
        Liste von FrequencyResult sortiert nach Zahl.
        Bei leerer Eingabe: leere Liste.

    Raises:
        ValueError: Wenn number_range ungueltig ist (min > max).

    Example:
        >>> from kenobase.core.data_loader import DrawResult, GameType
        >>> from datetime import datetime
        >>> draws = [
        ...     DrawResult(date=datetime.now(), numbers=[1, 2, 3], game_type=GameType.KENO),
        ...     DrawResult(date=datetime.now(), numbers=[1, 4, 5], game_type=GameType.KENO),
        ... ]
        >>> results = calculate_frequency(draws)
        >>> results[0].number  # 1 kommt 2x vor
        1
        >>> results[0].absolute_frequency
        2
    """
    if not draws:
        return []

    if number_range is not None:
        min_num, max_num = number_range
        if min_num > max_num:
            raise ValueError(f"Invalid number_range: min ({min_num}) > max ({max_num})")

    # Zaehle alle Zahlen
    counter: Counter[int] = Counter()
    for draw in draws:
        counter.update(draw.numbers)

    total_draws = len(draws)

    # Initialisiere mit Null-Frequenzen wenn Bereich angegeben
    if number_range is not None:
        min_num, max_num = number_range
        for num in range(min_num, max_num + 1):
            if num not in counter:
                counter[num] = 0

    # Berechne relative Frequenzen (Guard gegen Division by Zero)
    results = []
    for number in sorted(counter.keys()):
        abs_freq = counter[number]
        rel_freq = abs_freq / total_draws if total_draws > 0 else 0.0
        results.append(
            FrequencyResult(
                number=number,
                absolute_frequency=abs_freq,
                relative_frequency=rel_freq,
                classification="normal",  # Wird spaeter durch classify_numbers gesetzt
            )
        )

    return results


def calculate_pair_frequency(
    draws: list[DrawResult],
) -> list[PairFrequencyResult]:
    """Berechnet die Haeufigkeit von Zahlenpaaren (Duos).

    Zaehlt wie oft zwei Zahlen gemeinsam in einer Ziehung erscheinen.

    Args:
        draws: Liste von DrawResult-Objekten

    Returns:
        Liste von PairFrequencyResult sortiert nach absoluter Frequenz (absteigend).
        Bei leerer Eingabe: leere Liste.

    Example:
        >>> from kenobase.core.data_loader import DrawResult, GameType
        >>> from datetime import datetime
        >>> draws = [
        ...     DrawResult(date=datetime.now(), numbers=[1, 2, 3], game_type=GameType.KENO),
        ...     DrawResult(date=datetime.now(), numbers=[1, 2, 4], game_type=GameType.KENO),
        ... ]
        >>> results = calculate_pair_frequency(draws)
        >>> results[0].pair  # (1, 2) kommt 2x vor
        (1, 2)
        >>> results[0].absolute_frequency
        2
    """
    if not draws:
        return []

    # Zaehle alle Paare
    counter: Counter[tuple[int, int]] = Counter()
    for draw in draws:
        # Erstelle alle 2er-Kombinationen (sortiert)
        for pair in combinations(sorted(draw.numbers), 2):
            counter[pair] += 1

    total_draws = len(draws)

    # Erstelle Ergebnisse sortiert nach Frequenz (absteigend)
    results = []
    for pair, abs_freq in counter.most_common():
        rel_freq = abs_freq / total_draws if total_draws > 0 else 0.0
        results.append(
            PairFrequencyResult(
                pair=pair,
                absolute_frequency=abs_freq,
                relative_frequency=rel_freq,
                classification="normal",
            )
        )

    return results


def classify_numbers(
    frequency_results: list[FrequencyResult],
    hot_threshold: float = 0.20,
    cold_threshold: float = 0.05,
) -> list[FrequencyResult]:
    """Klassifiziert Zahlen als hot/cold/normal basierend auf Frequenz.

    - hot: relative_frequency >= hot_threshold
    - cold: relative_frequency <= cold_threshold
    - normal: dazwischen

    Args:
        frequency_results: Liste von FrequencyResult (von calculate_frequency)
        hot_threshold: Schwellwert fuer "hot" (default: 0.20)
        cold_threshold: Schwellwert fuer "cold" (default: 0.05)

    Returns:
        Neue Liste mit aktualisierten Klassifikationen.

    Raises:
        ValueError: Wenn hot_threshold <= cold_threshold.

    Example:
        >>> results = calculate_frequency(draws)
        >>> classified = classify_numbers(results, hot_threshold=0.15, cold_threshold=0.05)
        >>> hot_nums = [r.number for r in classified if r.classification == "hot"]
    """
    if hot_threshold <= cold_threshold:
        raise ValueError(
            f"hot_threshold ({hot_threshold}) must be > cold_threshold ({cold_threshold})"
        )

    classified = []
    for result in frequency_results:
        if result.relative_frequency >= hot_threshold:
            classification = "hot"
        elif result.relative_frequency <= cold_threshold:
            classification = "cold"
        else:
            classification = "normal"

        classified.append(
            FrequencyResult(
                number=result.number,
                absolute_frequency=result.absolute_frequency,
                relative_frequency=result.relative_frequency,
                classification=classification,
            )
        )

    return classified


def classify_pairs(
    pair_results: list[PairFrequencyResult],
    hot_threshold: float = 0.10,
    cold_threshold: float = 0.01,
) -> list[PairFrequencyResult]:
    """Klassifiziert Zahlenpaare als hot/cold/normal basierend auf Frequenz.

    Args:
        pair_results: Liste von PairFrequencyResult (von calculate_pair_frequency)
        hot_threshold: Schwellwert fuer "hot" (default: 0.10)
        cold_threshold: Schwellwert fuer "cold" (default: 0.01)

    Returns:
        Neue Liste mit aktualisierten Klassifikationen.

    Raises:
        ValueError: Wenn hot_threshold <= cold_threshold.
    """
    if hot_threshold <= cold_threshold:
        raise ValueError(
            f"hot_threshold ({hot_threshold}) must be > cold_threshold ({cold_threshold})"
        )

    classified = []
    for result in pair_results:
        if result.relative_frequency >= hot_threshold:
            classification = "hot"
        elif result.relative_frequency <= cold_threshold:
            classification = "cold"
        else:
            classification = "normal"

        classified.append(
            PairFrequencyResult(
                pair=result.pair,
                absolute_frequency=result.absolute_frequency,
                relative_frequency=result.relative_frequency,
                classification=classification,
            )
        )

    return classified


def calculate_rolling_frequency(
    draws: list[DrawResult],
    window: int,
    number: int,
) -> list[float]:
    """Berechnet Rolling-Frequenz einer Zahl ueber ein Fenster.

    Fuer jeden Draw ab Position `window` wird die relative Frequenz
    der letzten `window` Ziehungen berechnet.

    Args:
        draws: Liste von DrawResult-Objekten (chronologisch sortiert)
        window: Fenstergroesse (Anzahl Ziehungen)
        number: Die zu analysierende Zahl

    Returns:
        Liste von relativen Frequenzen.
        Laenge = max(0, len(draws) - window + 1)

    Raises:
        ValueError: Wenn window < 1.

    Example:
        >>> freqs = calculate_rolling_frequency(draws, window=10, number=7)
        >>> len(freqs)  # len(draws) - 10 + 1
        91
    """
    if window < 1:
        raise ValueError(f"window must be >= 1, got {window}")

    if len(draws) < window:
        return []

    results = []
    for i in range(len(draws) - window + 1):
        window_draws = draws[i : i + window]
        count = sum(1 for d in window_draws if number in d.numbers)
        results.append(count / window)

    return results


def get_hot_numbers(
    draws: list[DrawResult],
    hot_threshold: float = 0.20,
    cold_threshold: float = 0.05,
    number_range: tuple[int, int] | None = None,
) -> list[int]:
    """Convenience-Funktion: Gibt nur die "hot" Zahlen zurueck.

    Args:
        draws: Liste von DrawResult-Objekten
        hot_threshold: Schwellwert fuer "hot"
        cold_threshold: Schwellwert fuer "cold"
        number_range: Optionaler Zahlenbereich

    Returns:
        Liste der als "hot" klassifizierten Zahlen.
    """
    freq_results = calculate_frequency(draws, number_range)
    classified = classify_numbers(freq_results, hot_threshold, cold_threshold)
    return [r.number for r in classified if r.classification == "hot"]


def get_cold_numbers(
    draws: list[DrawResult],
    hot_threshold: float = 0.20,
    cold_threshold: float = 0.05,
    number_range: tuple[int, int] | None = None,
) -> list[int]:
    """Convenience-Funktion: Gibt nur die "cold" Zahlen zurueck.

    Args:
        draws: Liste von DrawResult-Objekten
        hot_threshold: Schwellwert fuer "hot"
        cold_threshold: Schwellwert fuer "cold"
        number_range: Optionaler Zahlenbereich

    Returns:
        Liste der als "cold" klassifizierten Zahlen.
    """
    freq_results = calculate_frequency(draws, number_range)
    classified = classify_numbers(freq_results, hot_threshold, cold_threshold)
    return [r.number for r in classified if r.classification == "cold"]


@dataclass(frozen=True)
class YearlyFrequencyResult:
    """Ergebnis der Frequenzanalyse pro Jahr.

    Attributes:
        year: Das analysierte Jahr
        number: Die analysierte Zahl
        absolute_frequency: Absolute Anzahl der Vorkommen in diesem Jahr
        relative_frequency: Relativer Anteil (0.0 - 1.0) bezogen auf Ziehungen im Jahr
        total_draws: Anzahl Ziehungen in diesem Jahr
    """

    year: int
    number: int
    absolute_frequency: int
    relative_frequency: float
    total_draws: int


def calculate_frequency_per_year(
    draws: list[DrawResult],
    number_range: tuple[int, int] | None = None,
) -> dict[int, list[YearlyFrequencyResult]]:
    """Berechnet die Haeufigkeit jeder Zahl pro Jahr.

    Gruppiert Ziehungen nach Jahr (draw.date.year) und berechnet
    Frequenzen separat fuer jedes Jahr. Ermoeglicht Year-over-Year
    Stabilitaetsanalyse (Axiom A5).

    Args:
        draws: Liste von DrawResult-Objekten
        number_range: Optionaler Zahlenbereich (min, max) fuer KENO: (1, 70).
                      Wenn None, werden nur vorkommende Zahlen gezaehlt.

    Returns:
        Dict mit Jahr als Key und Liste von YearlyFrequencyResult als Value.
        Bei leerer Eingabe: leeres Dict.

    Raises:
        ValueError: Wenn number_range ungueltig ist (min > max).

    Example:
        >>> from kenobase.core.data_loader import DrawResult, GameType
        >>> from datetime import datetime
        >>> draws = [
        ...     DrawResult(date=datetime(2023, 1, 1), numbers=[1, 2, 3], game_type=GameType.KENO),
        ...     DrawResult(date=datetime(2024, 1, 1), numbers=[1, 4, 5], game_type=GameType.KENO),
        ... ]
        >>> results = calculate_frequency_per_year(draws)
        >>> 2023 in results
        True
        >>> 2024 in results
        True
    """
    if not draws:
        return {}

    if number_range is not None:
        min_num, max_num = number_range
        if min_num > max_num:
            raise ValueError(f"Invalid number_range: min ({min_num}) > max ({max_num})")

    # Gruppiere Ziehungen nach Jahr
    draws_by_year: dict[int, list[DrawResult]] = {}
    for draw in draws:
        year = draw.date.year
        if year not in draws_by_year:
            draws_by_year[year] = []
        draws_by_year[year].append(draw)

    # Berechne Frequenzen pro Jahr
    results: dict[int, list[YearlyFrequencyResult]] = {}

    for year, year_draws in sorted(draws_by_year.items()):
        counter: Counter[int] = Counter()
        for draw in year_draws:
            counter.update(draw.numbers)

        total_draws = len(year_draws)

        # Initialisiere mit Null-Frequenzen wenn Bereich angegeben
        if number_range is not None:
            min_num, max_num = number_range
            for num in range(min_num, max_num + 1):
                if num not in counter:
                    counter[num] = 0

        # Erstelle Ergebnisse fuer dieses Jahr
        year_results = []
        for number in sorted(counter.keys()):
            abs_freq = counter[number]
            rel_freq = abs_freq / total_draws if total_draws > 0 else 0.0
            year_results.append(
                YearlyFrequencyResult(
                    year=year,
                    number=number,
                    absolute_frequency=abs_freq,
                    relative_frequency=rel_freq,
                    total_draws=total_draws,
                )
            )

        results[year] = year_results

    return results


__all__ = [
    "FrequencyResult",
    "PairFrequencyResult",
    "YearlyFrequencyResult",
    "calculate_frequency",
    "calculate_frequency_per_year",
    "calculate_pair_frequency",
    "classify_numbers",
    "classify_pairs",
    "calculate_rolling_frequency",
    "get_hot_numbers",
    "get_cold_numbers",
]
