"""Gerade/Ungerade (Even/Odd) Ratio Analyse fuer Lotterieziehungen.

Dieses Modul analysiert die Verteilung von geraden und ungeraden Zahlen
in Ziehungen und testet gegen eine 50/50 Erwartung.

Kernausgaben:
- Counts fuer gerade und ungerade Zahlen
- Binomial-Test gegen 50/50 Erwartung
- Chi-Quadrat-Test fuer Verteilungsvergleich
- Guardrail: maximal zulaessige Abweichung von 10% (konfigurierbar)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from scipy import stats

from kenobase.core.data_loader import DrawResult


@dataclass(frozen=True)
class ParityBin:
    """Aggregierte Metriken fuer gerade oder ungerade Zahlen."""

    category: str  # "even" or "odd"
    count: int
    expected_count: float
    relative_frequency: float
    deviation_ratio: float
    within_guardrail: bool


@dataclass(frozen=True)
class ParityRatioResult:
    """Gesamtresultat der Paritaets-Analyse."""

    total_draws: int
    numbers_per_draw: int
    total_numbers: int
    even_count: int
    odd_count: int
    parity_ratio: float  # even / (even + odd)
    chi_square: float
    chi_p_value: float
    binomial_p_value: float
    max_deviation_ratio: float
    guardrail_breached: bool
    bins: List[ParityBin]
    warnings: list[str]


def is_even(number: int) -> bool:
    """Prueft ob eine Zahl gerade ist."""
    return number % 2 == 0


def count_parity(numbers: list[int]) -> tuple[int, int]:
    """Zaehlt gerade und ungerade Zahlen in einer Liste.

    Args:
        numbers: Liste von Zahlen

    Returns:
        Tuple (even_count, odd_count)
    """
    even = sum(1 for n in numbers if is_even(n))
    odd = len(numbers) - even
    return even, odd


def analyze_parity_ratio(
    draws: list[DrawResult],
    numbers_per_draw: Optional[int] = None,
    guardrail_ratio: float = 0.10,
) -> ParityRatioResult:
    """Berechnet Paritaets-Verteilung und statistische Tests gegen 50/50.

    Args:
        draws: Liste von Ziehungsergebnissen
        numbers_per_draw: Optionale Anzahl Zahlen pro Ziehung (inferiert wenn None)
        guardrail_ratio: Maximal erlaubte Abweichung von 50% (default 10%)

    Returns:
        ParityRatioResult mit allen Metriken
    """
    warnings: list[str] = []

    if not draws:
        return ParityRatioResult(
            total_draws=0,
            numbers_per_draw=0,
            total_numbers=0,
            even_count=0,
            odd_count=0,
            parity_ratio=0.5,
            chi_square=0.0,
            chi_p_value=1.0,
            binomial_p_value=1.0,
            max_deviation_ratio=0.0,
            guardrail_breached=False,
            bins=[],
            warnings=["No draws provided"],
        )

    # Sammle alle Zahlen
    total_even = 0
    total_odd = 0

    for draw in draws:
        e, o = count_parity(draw.numbers)
        total_even += e
        total_odd += o

    total_numbers = total_even + total_odd

    if total_numbers == 0:
        return ParityRatioResult(
            total_draws=len(draws),
            numbers_per_draw=numbers_per_draw or 0,
            total_numbers=0,
            even_count=0,
            odd_count=0,
            parity_ratio=0.5,
            chi_square=0.0,
            chi_p_value=1.0,
            binomial_p_value=1.0,
            max_deviation_ratio=0.0,
            guardrail_breached=False,
            bins=[],
            warnings=warnings + ["No numbers found in draws"],
        )

    # Erwartete Counts bei 50/50
    expected_count = total_numbers / 2.0

    # Parity Ratio (Anteil gerade)
    parity_ratio = total_even / total_numbers

    # Deviation Ratios
    even_deviation = (total_even - expected_count) / expected_count
    odd_deviation = (total_odd - expected_count) / expected_count

    max_dev = max(abs(even_deviation), abs(odd_deviation))
    guardrail_breached = max_dev > guardrail_ratio

    # Chi-Quadrat Test gegen 50/50
    observed = np.array([total_even, total_odd])
    expected = np.array([expected_count, expected_count])
    chi_square, chi_p_value = stats.chisquare(f_obs=observed, f_exp=expected)

    # Binomial Test: Ist die Abweichung von 50% signifikant?
    # Test ob even_count signifikant von total/2 abweicht
    binomial_result = stats.binomtest(
        k=total_even,
        n=total_numbers,
        p=0.5,
        alternative="two-sided",
    )
    binomial_p_value = binomial_result.pvalue

    # Erzeuge Bins
    bins = [
        ParityBin(
            category="even",
            count=total_even,
            expected_count=expected_count,
            relative_frequency=total_even / total_numbers,
            deviation_ratio=even_deviation,
            within_guardrail=abs(even_deviation) <= guardrail_ratio,
        ),
        ParityBin(
            category="odd",
            count=total_odd,
            expected_count=expected_count,
            relative_frequency=total_odd / total_numbers,
            deviation_ratio=odd_deviation,
            within_guardrail=abs(odd_deviation) <= guardrail_ratio,
        ),
    ]

    # Inferiere numbers_per_draw wenn nicht angegeben
    inferred_npd = numbers_per_draw
    if inferred_npd is None and draws:
        inferred_npd = len(draws[0].numbers)

    return ParityRatioResult(
        total_draws=len(draws),
        numbers_per_draw=inferred_npd or 0,
        total_numbers=total_numbers,
        even_count=total_even,
        odd_count=total_odd,
        parity_ratio=float(parity_ratio),
        chi_square=float(chi_square),
        chi_p_value=float(chi_p_value),
        binomial_p_value=float(binomial_p_value),
        max_deviation_ratio=float(max_dev),
        guardrail_breached=guardrail_breached,
        bins=bins,
        warnings=warnings,
    )


__all__ = [
    "ParityBin",
    "ParityRatioResult",
    "analyze_parity_ratio",
    "count_parity",
    "is_even",
]
