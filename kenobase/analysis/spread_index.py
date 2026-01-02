"""Spread-Index Analyse fuer Lotterieziehungen.

Dieses Modul analysiert die Spreizung (Range) von gezogenen Zahlen
pro Ziehung und testet gegen eine erwartete Gleichverteilung.

Spread-Index = (Max - Min) / Max
Normalisiert auf [0, 1], wobei 1 maximale Spreizung bedeutet.

Kernausgaben:
- Spread-Index pro Ziehung
- Aggregierte Statistiken (Mittelwert, Std, Min, Max)
- Chi-Quadrat-Test fuer Spreizungs-Verteilung
- Guardrail: maximal zulaessige Abweichung von 15% (konfigurierbar)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from scipy import stats

from kenobase.core.data_loader import DrawResult


@dataclass(frozen=True)
class SpreadBin:
    """Aggregierte Metriken fuer einen Spread-Bereich."""

    bin_label: str  # z.B. "[0.0-0.2)", "[0.2-0.4)", etc.
    bin_min: float
    bin_max: float
    count: int
    expected_count: float
    relative_frequency: float
    deviation_ratio: float
    within_guardrail: bool


@dataclass(frozen=True)
class SpreadIndexResult:
    """Gesamtresultat der Spread-Index-Analyse."""

    total_draws: int
    numbers_per_draw: int
    spread_values: List[float]  # Individual spread per draw
    mean_spread: float
    std_spread: float
    min_spread: float
    max_spread: float
    chi_square: float
    chi_p_value: float
    max_deviation_ratio: float
    guardrail_breached: bool
    bins: List[SpreadBin]
    warnings: list[str]


def calculate_spread_index(numbers: list[int]) -> float:
    """Berechnet den Spread-Index einer Zahlenliste.

    SpreadIndex = (Max - Min) / Max

    Args:
        numbers: Liste von Zahlen

    Returns:
        Spread-Index im Bereich [0, 1].
        Gibt 0.0 zurueck wenn weniger als 2 Zahlen oder Max == 0.
    """
    if len(numbers) < 2:
        return 0.0

    min_val = min(numbers)
    max_val = max(numbers)

    if max_val == 0:
        return 0.0

    return (max_val - min_val) / max_val


def calculate_spread_for_draws(draws: list[DrawResult]) -> list[float]:
    """Berechnet Spread-Index fuer alle Ziehungen.

    Args:
        draws: Liste von Ziehungsergebnissen

    Returns:
        Liste von Spread-Index-Werten
    """
    return [calculate_spread_index(draw.numbers) for draw in draws]


def create_spread_bins(
    spread_values: list[float],
    n_bins: int = 5,
    guardrail_ratio: float = 0.15,
) -> tuple[list[SpreadBin], float, bool]:
    """Erstellt Bins fuer die Spread-Verteilung.

    Args:
        spread_values: Liste von Spread-Index-Werten
        n_bins: Anzahl der Bins (default 5)
        guardrail_ratio: Maximal erlaubte Abweichung (default 15%)

    Returns:
        Tuple (bins, max_deviation, guardrail_breached)
    """
    if not spread_values:
        return [], 0.0, False

    n = len(spread_values)
    expected_per_bin = n / n_bins

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bins_list: list[SpreadBin] = []
    max_dev = 0.0

    for i in range(n_bins):
        bin_min = bin_edges[i]
        bin_max = bin_edges[i + 1]

        # Count values in this bin (inclusive of lower, exclusive of upper, except last)
        if i == n_bins - 1:
            count = sum(1 for v in spread_values if bin_min <= v <= bin_max)
        else:
            count = sum(1 for v in spread_values if bin_min <= v < bin_max)

        rel_freq = count / n if n > 0 else 0.0
        deviation = (count - expected_per_bin) / expected_per_bin if expected_per_bin > 0 else 0.0
        within_guardrail = abs(deviation) <= guardrail_ratio

        if abs(deviation) > max_dev:
            max_dev = abs(deviation)

        label = f"[{bin_min:.1f}-{bin_max:.1f})"
        if i == n_bins - 1:
            label = f"[{bin_min:.1f}-{bin_max:.1f}]"

        bins_list.append(
            SpreadBin(
                bin_label=label,
                bin_min=bin_min,
                bin_max=bin_max,
                count=count,
                expected_count=expected_per_bin,
                relative_frequency=rel_freq,
                deviation_ratio=deviation,
                within_guardrail=within_guardrail,
            )
        )

    guardrail_breached = max_dev > guardrail_ratio
    return bins_list, max_dev, guardrail_breached


def analyze_spread_index(
    draws: list[DrawResult],
    numbers_per_draw: Optional[int] = None,
    n_bins: int = 5,
    guardrail_ratio: float = 0.15,
) -> SpreadIndexResult:
    """Berechnet Spread-Index-Verteilung und statistische Tests.

    Args:
        draws: Liste von Ziehungsergebnissen
        numbers_per_draw: Optionale Anzahl Zahlen pro Ziehung (inferiert wenn None)
        n_bins: Anzahl der Bins fuer Chi-Square-Test (default 5)
        guardrail_ratio: Maximal erlaubte Abweichung von Gleichverteilung (default 15%)

    Returns:
        SpreadIndexResult mit allen Metriken
    """
    warnings: list[str] = []

    if not draws:
        return SpreadIndexResult(
            total_draws=0,
            numbers_per_draw=0,
            spread_values=[],
            mean_spread=0.0,
            std_spread=0.0,
            min_spread=0.0,
            max_spread=0.0,
            chi_square=0.0,
            chi_p_value=1.0,
            max_deviation_ratio=0.0,
            guardrail_breached=False,
            bins=[],
            warnings=["No draws provided"],
        )

    # Calculate spread for each draw
    spread_values = calculate_spread_for_draws(draws)

    # Filter out draws with insufficient numbers
    valid_spreads = [s for s in spread_values if s > 0.0 or any(len(d.numbers) >= 2 for d in draws)]

    if not valid_spreads:
        return SpreadIndexResult(
            total_draws=len(draws),
            numbers_per_draw=numbers_per_draw or 0,
            spread_values=[],
            mean_spread=0.0,
            std_spread=0.0,
            min_spread=0.0,
            max_spread=0.0,
            chi_square=0.0,
            chi_p_value=1.0,
            max_deviation_ratio=0.0,
            guardrail_breached=False,
            bins=[],
            warnings=warnings + ["No valid spread values calculated"],
        )

    # Statistics
    mean_spread = float(np.mean(spread_values))
    std_spread = float(np.std(spread_values))
    min_spread = float(min(spread_values))
    max_spread = float(max(spread_values))

    # Create bins for chi-square test
    bins, max_dev, guardrail_breached = create_spread_bins(
        spread_values, n_bins=n_bins, guardrail_ratio=guardrail_ratio
    )

    # Chi-Square Test against uniform distribution
    if bins:
        observed = np.array([b.count for b in bins])
        expected = np.array([b.expected_count for b in bins])

        # Avoid division by zero
        if np.all(expected > 0):
            chi_square, chi_p_value = stats.chisquare(f_obs=observed, f_exp=expected)
            chi_square = float(chi_square)
            chi_p_value = float(chi_p_value)
        else:
            chi_square = 0.0
            chi_p_value = 1.0
            warnings.append("Chi-square test skipped due to zero expected values")
    else:
        chi_square = 0.0
        chi_p_value = 1.0

    # Infer numbers_per_draw if not specified
    inferred_npd = numbers_per_draw
    if inferred_npd is None and draws:
        inferred_npd = len(draws[0].numbers)

    return SpreadIndexResult(
        total_draws=len(draws),
        numbers_per_draw=inferred_npd or 0,
        spread_values=spread_values,
        mean_spread=mean_spread,
        std_spread=std_spread,
        min_spread=min_spread,
        max_spread=max_spread,
        chi_square=chi_square,
        chi_p_value=chi_p_value,
        max_deviation_ratio=float(max_dev),
        guardrail_breached=guardrail_breached,
        bins=bins,
        warnings=warnings,
    )


__all__ = [
    "SpreadBin",
    "SpreadIndexResult",
    "analyze_spread_index",
    "calculate_spread_index",
    "calculate_spread_for_draws",
    "create_spread_bins",
]
