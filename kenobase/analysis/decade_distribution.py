"""Dekaden-Verteilungsanalyse fuer KENO-Ziehungen.

Dieses Modul analysiert die Verteilung der gezogenen Zahlen ueber Zehner-Dekaden
und testet gegen eine uniforme Erwartung. Eine Dekade ist definiert als
(number - 1) // decade_size, default decade_size=10 fuer Zahlen 1-70.

Kernausgaben:
- Counts pro Dekade, erwartete Counts basierend auf gleichverteilten Zahlen
- Relative Frequenzen und Abweichungen
- Chi-Quadrat-Test gegen Uniformitaet
- Guardrail: maximal zulässige Abweichung von 20% (configurierbar)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

import numpy as np
from scipy import stats

from kenobase.core.data_loader import DrawResult


@dataclass(frozen=True)
class DecadeBin:
    """Aggregierte Metriken fuer eine Dekade."""

    decade: int
    start: int
    end: int
    count: int
    expected_count: float
    relative_frequency: float
    deviation_ratio: float
    within_guardrail: bool


@dataclass(frozen=True)
class DecadeDistributionResult:
    """Gesamtresultat der Dekaden-Verteilung."""

    total_draws: int
    numbers_per_draw: int
    total_numbers: int
    decade_size: int
    max_number: int
    chi_square: float
    p_value: float
    max_deviation_ratio: float
    guardrail_breached: bool
    bins: List[DecadeBin]
    warnings: list[str]


def map_number_to_decade(number: int, decade_size: int = 10, max_number: int = 70) -> int:
    """Mappt eine Zahl auf die Dekade (0-basiert)."""
    if number < 1 or number > max_number:
        raise ValueError(f"Number {number} out of range [1, {max_number}]")
    return (number - 1) // decade_size


def _build_decade_bins(max_number: int, decade_size: int) -> list[tuple[int, int]]:
    """Erzeugt (start, end) Paare fuer alle Dekaden bis max_number."""
    bins = []
    start = 1
    while start <= max_number:
        end = min(start + decade_size - 1, max_number)
        bins.append((start, end))
        start = end + 1
    return bins


def _collect_numbers(draws: Iterable[DrawResult]) -> list[int]:
    """Extrahiert alle Hauptzahlen aus Ziehungen."""
    numbers: list[int] = []
    for draw in draws:
        numbers.extend(draw.numbers)
    return numbers


def analyze_decade_distribution(
    draws: list[DrawResult],
    max_number: Optional[int] = None,
    numbers_per_draw: Optional[int] = None,
    decade_size: int = 10,
    guardrail_ratio: float = 0.20,
) -> DecadeDistributionResult:
    """Berechnet Dekaden-Verteilung und Chi-Quadrat-Test gegen Uniformitaet."""
    warnings: list[str] = []

    if not draws:
        return DecadeDistributionResult(
            total_draws=0,
            numbers_per_draw=0,
            total_numbers=0,
            decade_size=decade_size,
            max_number=max_number or 70,
            chi_square=0.0,
            p_value=1.0,
            max_deviation_ratio=0.0,
            guardrail_breached=False,
            bins=[],
            warnings=["No draws provided"],
        )

    inferred_max = max((max(d.numbers) if d.numbers else 0 for d in draws), default=0)
    max_val = max_number or inferred_max or 70

    bins = _build_decade_bins(max_val, decade_size)
    counts = np.zeros(len(bins), dtype=int)
    total_numbers = 0

    for draw in draws:
        for number in draw.numbers:
            try:
                idx = map_number_to_decade(number, decade_size=decade_size, max_number=max_val)
            except ValueError:
                warnings.append(f"Number {number} out of expected range 1-{max_val}, skipped")
                continue
            counts[idx] += 1
            total_numbers += 1

    if total_numbers == 0:
        return DecadeDistributionResult(
            total_draws=len(draws),
            numbers_per_draw=numbers_per_draw or 0,
            total_numbers=0,
            decade_size=decade_size,
            max_number=max_val,
            chi_square=0.0,
            p_value=1.0,
            max_deviation_ratio=0.0,
            guardrail_breached=False,
            bins=[],
            warnings=warnings + ["No numbers found in draws"],
        )

    expected_counts = []
    decade_bins: list[DecadeBin] = []
    deviation_ratios: list[float] = []

    for idx, (start, end) in enumerate(bins):
        bucket_size = end - start + 1
        expected = total_numbers * (bucket_size / max_val)
        expected_counts.append(expected)

        relative_frequency = counts[idx] / total_numbers
        deviation_ratio = (counts[idx] - expected) / expected if expected > 0 else 0.0
        deviation_ratios.append(deviation_ratio)

        decade_bins.append(
            DecadeBin(
                decade=idx,
                start=start,
                end=end,
                count=int(counts[idx]),
                expected_count=float(expected),
                relative_frequency=float(relative_frequency),
                deviation_ratio=float(deviation_ratio),
                within_guardrail=bool(abs(deviation_ratio) <= guardrail_ratio),
            )
        )

    chi_square = 0.0
    p_value = 1.0
    if all(exp > 0 for exp in expected_counts):
        chi_square, p_value = stats.chisquare(f_obs=counts, f_exp=expected_counts)

    max_dev = float(max(abs(float(r)) for r in deviation_ratios)) if deviation_ratios else 0.0
    guardrail_breached = bool(max_dev > guardrail_ratio)

    return DecadeDistributionResult(
        total_draws=len(draws),
        numbers_per_draw=numbers_per_draw or len(draws[0].numbers),
        total_numbers=total_numbers,
        decade_size=decade_size,
        max_number=max_val,
        chi_square=float(chi_square),
        p_value=float(p_value),
        max_deviation_ratio=float(max_dev),
        guardrail_breached=guardrail_breached,
        bins=decade_bins,
        warnings=warnings,
    )


__all__ = [
    "DecadeBin",
    "DecadeDistributionResult",
    "analyze_decade_distribution",
    "map_number_to_decade",
]
