"""Core Stable Numbers Analysis Module - Model Law A Implementation.

Identifiziert Zahlen mit hoher Stabilitaet ueber Zeitfenster basierend auf
Model Law A (Stabilitaetspruefung). Eine Zahl gilt als "stabil" wenn ihre
Rolling Frequency ueber Zeit wenig variiert.

Formel: stability_score = 1 - (std(rolling_freq) / mean(rolling_freq))
Kriterium: is_stable = stability_score >= threshold (default 0.90)

Usage:
    from kenobase.analysis.stable_numbers import (
        StableNumberResult,
        analyze_stable_numbers,
    )

    from kenobase.core.data_loader import DataLoader

    loader = DataLoader()
    draws = loader.load("data/raw/keno/KENO.csv")
    results = analyze_stable_numbers(draws, window=50, threshold=0.90)
    stable = [r for r in results if r.is_stable]
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from kenobase.analysis.frequency import calculate_rolling_frequency

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult


@dataclass(frozen=True)
class StableNumberResult:
    """Ergebnis der Stabilitaetsanalyse fuer eine einzelne Zahl.

    Attributes:
        number: Die analysierte Zahl
        stability_score: Stabilitaetswert (0.0 - 1.0)
        is_stable: True wenn stability_score >= threshold
        avg_frequency: Durchschnittliche relative Frequenz ueber alle Fenster
        std_frequency: Standardabweichung der Rolling Frequency
        window: Verwendete Fenstergroesse
        data_points: Anzahl Rolling-Frequency-Datenpunkte
    """

    number: int
    stability_score: float
    is_stable: bool
    avg_frequency: float
    std_frequency: float
    window: int
    data_points: int


def calculate_stability_score(rolling_frequencies: list[float]) -> tuple[float, float, float]:
    """Berechnet den Stabilitaetsscore aus Rolling-Frequencies.

    Formel: stability_score = 1 - (std / mean)
    - Bei mean = 0: stability_score = 0.0 (keine Frequenz = instabil)
    - Bei std = 0: stability_score = 1.0 (perfekt stabil)

    Args:
        rolling_frequencies: Liste von relativen Frequenzen

    Returns:
        Tuple (stability_score, mean, std)

    Example:
        >>> freqs = [0.25, 0.26, 0.24, 0.25, 0.25]
        >>> score, mean, std = calculate_stability_score(freqs)
        >>> score > 0.9
        True
    """
    if not rolling_frequencies:
        return 0.0, 0.0, 0.0

    arr = np.array(rolling_frequencies)
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))

    if mean_val == 0:
        # Zahl kommt nie vor -> als instabil werten
        return 0.0, mean_val, std_val

    stability = 1.0 - (std_val / mean_val)
    # Clamp to [0, 1]
    stability = max(0.0, min(1.0, stability))

    return stability, mean_val, std_val


def analyze_stable_numbers(
    draws: list[DrawResult],
    window: int = 50,
    stability_threshold: float = 0.90,
    number_range: tuple[int, int] | None = None,
) -> list[StableNumberResult]:
    """Analysiert alle Zahlen auf Stabilitaet basierend auf Model Law A.

    Fuer jede Zahl im Bereich:
    1. Berechne Rolling Frequency ueber das Fenster
    2. Berechne stability_score = 1 - (std / mean)
    3. Klassifiziere als stabil wenn score >= threshold

    Args:
        draws: Liste von DrawResult-Objekten (chronologisch sortiert)
        window: Fenstergroesse fuer Rolling-Frequency (default 50)
        stability_threshold: Schwellwert fuer "stabil" (default 0.90)
        number_range: Zahlenbereich (min, max). Wenn None, wird aus draws abgeleitet.

    Returns:
        Liste von StableNumberResult sortiert nach stability_score (absteigend).
        Bei leerer Eingabe oder zu wenig Daten: leere Liste.

    Raises:
        ValueError: Wenn window < 1 oder stability_threshold nicht in [0, 1]

    Example:
        >>> results = analyze_stable_numbers(draws, window=50, stability_threshold=0.90)
        >>> stable_numbers = [r.number for r in results if r.is_stable]
        >>> len(stable_numbers)
        12
    """
    if window < 1:
        raise ValueError(f"window must be >= 1, got {window}")
    if not 0.0 <= stability_threshold <= 1.0:
        raise ValueError(f"stability_threshold must be in [0, 1], got {stability_threshold}")

    if not draws:
        return []

    if len(draws) < window:
        # Nicht genug Daten fuer Rolling-Berechnung
        return []

    # Determine number range
    if number_range is None:
        # Infer from data
        all_numbers = set()
        for draw in draws:
            all_numbers.update(draw.numbers)
        if not all_numbers:
            return []
        min_num = min(all_numbers)
        max_num = max(all_numbers)
    else:
        min_num, max_num = number_range

    results: list[StableNumberResult] = []

    for number in range(min_num, max_num + 1):
        # Calculate rolling frequency for this number
        rolling_freqs = calculate_rolling_frequency(draws, window, number)

        if not rolling_freqs:
            # Nicht genug Daten
            results.append(
                StableNumberResult(
                    number=number,
                    stability_score=0.0,
                    is_stable=False,
                    avg_frequency=0.0,
                    std_frequency=0.0,
                    window=window,
                    data_points=0,
                )
            )
            continue

        stability, avg_freq, std_freq = calculate_stability_score(rolling_freqs)

        results.append(
            StableNumberResult(
                number=number,
                stability_score=stability,
                is_stable=stability >= stability_threshold,
                avg_frequency=avg_freq,
                std_frequency=std_freq,
                window=window,
                data_points=len(rolling_freqs),
            )
        )

    # Sort by stability_score descending
    results.sort(key=lambda r: r.stability_score, reverse=True)

    return results


def get_stable_numbers(
    draws: list[DrawResult],
    window: int = 50,
    stability_threshold: float = 0.90,
    number_range: tuple[int, int] | None = None,
) -> list[int]:
    """Convenience-Funktion: Gibt nur die stabilen Zahlen zurueck.

    Args:
        draws: Liste von DrawResult-Objekten
        window: Fenstergroesse fuer Rolling-Frequency
        stability_threshold: Schwellwert fuer "stabil"
        number_range: Optionaler Zahlenbereich

    Returns:
        Liste der als stabil klassifizierten Zahlen (sortiert nach stability_score).
    """
    results = analyze_stable_numbers(draws, window, stability_threshold, number_range)
    return [r.number for r in results if r.is_stable]


def export_stable_numbers(
    results: list[StableNumberResult],
    output_path: str | Path,
    include_all: bool = False,
) -> None:
    """Exportiert Stable Numbers Ergebnisse als JSON.

    Args:
        results: Liste von StableNumberResult
        output_path: Pfad zur Ausgabedatei
        include_all: Wenn False, nur stabile Zahlen exportieren

    Example:
        >>> export_stable_numbers(results, "results/stable_numbers_keno.json")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    export_results = results if include_all else [r for r in results if r.is_stable]

    data = {
        "analysis": "stable_numbers",
        "count_total": len(results),
        "count_stable": len([r for r in results if r.is_stable]),
        "parameters": {
            "window": results[0].window if results else 0,
        },
        "results": [
            {
                "number": r.number,
                "stability_score": round(r.stability_score, 4),
                "is_stable": r.is_stable,
                "avg_frequency": round(r.avg_frequency, 4),
                "std_frequency": round(r.std_frequency, 4),
                "data_points": r.data_points,
            }
            for r in export_results
        ],
    }

    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


__all__ = [
    "StableNumberResult",
    "calculate_stability_score",
    "analyze_stable_numbers",
    "get_stable_numbers",
    "export_stable_numbers",
]
