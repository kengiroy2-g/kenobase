"""Number Index System - Index-Berechnung seit letztem GK1-Event.

Dieses Modul implementiert das Zahlen-Index-System fuer HYP-005:
- Index = Haeufigkeit einer Zahl seit letztem Gewinnklasse-1-Event
- Reset bei jedem GK1-Event (Keno-Typ 9 oder 10)
- Korrelationsanalyse zwischen Index und Erscheinen in naechster Ziehung

Usage:
    from kenobase.analysis.number_index import (
        NumberIndex,
        IndexResult,
        calculate_index_table,
        calculate_index_correlation,
    )

    # Berechne Index-Tabelle
    index_result = calculate_index_table(draws, gk1_dates, number_range=70)

    # Korrelationsanalyse
    correlation = calculate_index_correlation(draws, gk1_dates)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np
from scipy import stats


@dataclass
class NumberIndex:
    """Index-Wert fuer eine einzelne Zahl.

    Attributes:
        number: Die Zahl (1-70)
        current_index: Aktuelle Haeufigkeit seit letztem Reset
        last_seen: Datum der letzten Erscheinung
        total_appearances: Gesamtzahl Erscheinungen seit Reset
    """

    number: int
    current_index: int
    last_seen: datetime | None
    total_appearances: int


@dataclass
class IndexResult:
    """Ergebnis der Index-Berechnung.

    Attributes:
        indices: Dict von Zahl -> NumberIndex
        last_reset_date: Datum des letzten GK1-Events
        draws_since_reset: Anzahl Ziehungen seit Reset
        gk1_event_type: Typ des letzten GK1-Events (9 oder 10)
    """

    indices: dict[int, NumberIndex]
    last_reset_date: datetime | None
    draws_since_reset: int
    gk1_event_type: int | None


@dataclass
class CorrelationResult:
    """Ergebnis der Korrelationsanalyse.

    Attributes:
        correlation: Pearson-Korrelation zwischen Index und Trefferrate
        p_value: Statistische Signifikanz
        mean_hits_high_index: Durchschnittliche Treffer fuer hohe Index-Zahlen
        mean_hits_low_index: Durchschnittliche Treffer fuer niedrige Index-Zahlen
        effect_size: Cohen's d
        interpretation: Textuelle Interpretation
    """

    correlation: float
    p_value: float
    mean_hits_high_index: float
    mean_hits_low_index: float
    effect_size: float
    interpretation: str
    n_segments: int = 0
    segment_details: list[dict[str, Any]] = field(default_factory=list)


def calculate_index_table(
    draws: list[tuple[datetime, list[int]]],
    gk1_events: list[tuple[datetime, int]],
    number_range: int = 70,
) -> IndexResult:
    """Berechnet die aktuelle Index-Tabelle fuer alle Zahlen.

    Index = Anzahl Erscheinungen einer Zahl seit letztem GK1-Event.

    Args:
        draws: Liste von (datum, zahlen) Tupeln, chronologisch sortiert
        gk1_events: Liste von (datum, keno_typ) Tupeln fuer GK1-Events
        number_range: Maximale Zahl (default: 70)

    Returns:
        IndexResult mit Index-Werten fuer alle Zahlen
    """
    # Initialisiere Index fuer alle Zahlen
    indices: dict[int, NumberIndex] = {}
    for num in range(1, number_range + 1):
        indices[num] = NumberIndex(
            number=num,
            current_index=0,
            last_seen=None,
            total_appearances=0,
        )

    if not draws:
        return IndexResult(
            indices=indices,
            last_reset_date=None,
            draws_since_reset=0,
            gk1_event_type=None,
        )

    # Sortiere GK1-Events nach Datum
    gk1_sorted = sorted(gk1_events, key=lambda x: x[0])

    # Finde letztes GK1-Event vor oder am letzten Draw-Datum
    last_draw_date = draws[-1][0]
    last_reset_date = None
    last_gk1_type = None

    for gk1_date, gk1_type in reversed(gk1_sorted):
        if gk1_date <= last_draw_date:
            last_reset_date = gk1_date
            last_gk1_type = gk1_type
            break

    # Zaehle Erscheinungen seit letztem Reset
    draws_since_reset = 0
    for draw_date, numbers in draws:
        # Nur Ziehungen nach dem letzten Reset zaehlen
        if last_reset_date is not None and draw_date < last_reset_date:
            continue

        draws_since_reset += 1

        for num in numbers:
            if 1 <= num <= number_range:
                idx = indices[num]
                indices[num] = NumberIndex(
                    number=num,
                    current_index=idx.current_index + 1,
                    last_seen=draw_date,
                    total_appearances=idx.total_appearances + 1,
                )

    return IndexResult(
        indices=indices,
        last_reset_date=last_reset_date,
        draws_since_reset=draws_since_reset,
        gk1_event_type=last_gk1_type,
    )


def calculate_index_correlation(
    draws: list[tuple[datetime, list[int]]],
    gk1_events: list[tuple[datetime, int]],
    number_range: int = 70,
    top_n: int = 11,
) -> CorrelationResult:
    """Berechnet die Korrelation zwischen Index und Trefferwahrscheinlichkeit.

    Methode:
    1. Fuer jedes GK1-Segment (zwischen zwei GK1-Events):
       - Berechne rolling Index fuer jede Ziehung
       - Identifiziere Top-N Zahlen nach Index
       - Pruefe wie viele davon in naechster Ziehung erscheinen
    2. Korreliere Index-Rang mit Trefferquote

    Args:
        draws: Liste von (datum, zahlen) Tupeln, chronologisch sortiert
        gk1_events: Liste von (datum, keno_typ) Tupeln fuer GK1-Events
        number_range: Maximale Zahl (default: 70)
        top_n: Anzahl Top-Zahlen fuer Vorhersage (default: 11)

    Returns:
        CorrelationResult mit Korrelation und Statistiken
    """
    if len(draws) < 20:
        return CorrelationResult(
            correlation=0.0,
            p_value=1.0,
            mean_hits_high_index=0.0,
            mean_hits_low_index=0.0,
            effect_size=0.0,
            interpretation="Insufficient data (< 20 draws)",
        )

    # Sortiere Events
    gk1_sorted = sorted(gk1_events, key=lambda x: x[0])
    draws_sorted = sorted(draws, key=lambda x: x[0])

    # Erstelle Segmente zwischen GK1-Events
    segments: list[list[tuple[datetime, list[int]]]] = []
    current_segment: list[tuple[datetime, list[int]]] = []
    gk1_idx = 0

    for draw_date, numbers in draws_sorted:
        # Pruefe ob wir ein GK1-Event erreicht haben
        while gk1_idx < len(gk1_sorted) and gk1_sorted[gk1_idx][0] <= draw_date:
            if current_segment:
                segments.append(current_segment)
                current_segment = []
            gk1_idx += 1

        current_segment.append((draw_date, numbers))

    # Letztes Segment hinzufuegen
    if current_segment:
        segments.append(current_segment)

    # Analysiere jeden Segment
    all_hits_high: list[int] = []
    all_hits_low: list[int] = []
    segment_details: list[dict[str, Any]] = []

    for seg_idx, segment in enumerate(segments):
        if len(segment) < 10:
            continue

        # Rolling Index innerhalb des Segments
        for i in range(5, len(segment) - 1):
            # Berechne Index basierend auf bisherigen Ziehungen im Segment
            index_counts: dict[int, int] = {n: 0 for n in range(1, number_range + 1)}
            for j in range(i):
                for num in segment[j][1]:
                    if 1 <= num <= number_range:
                        index_counts[num] += 1

            # Top-N Zahlen nach Index
            sorted_by_index = sorted(
                index_counts.items(), key=lambda x: x[1], reverse=True
            )
            top_numbers = {num for num, _ in sorted_by_index[:top_n]}
            bottom_numbers = {num for num, _ in sorted_by_index[-top_n:]}

            # Pruefe naechste Ziehung
            next_draw = set(segment[i + 1][1])

            hits_high = len(next_draw & top_numbers)
            hits_low = len(next_draw & bottom_numbers)

            all_hits_high.append(hits_high)
            all_hits_low.append(hits_low)

        segment_details.append({
            "segment": seg_idx,
            "n_draws": len(segment),
            "mean_hits_high": np.mean(all_hits_high[-len(segment):]) if all_hits_high else 0,
        })

    if not all_hits_high:
        return CorrelationResult(
            correlation=0.0,
            p_value=1.0,
            mean_hits_high_index=0.0,
            mean_hits_low_index=0.0,
            effect_size=0.0,
            interpretation="No valid segments found",
            n_segments=len(segments),
        )

    # Berechne Statistiken
    mean_high = float(np.mean(all_hits_high))
    mean_low = float(np.mean(all_hits_low))
    std_high = float(np.std(all_hits_high))
    std_low = float(np.std(all_hits_low))

    # t-Test: High-Index vs. Low-Index
    if len(all_hits_high) > 1 and len(all_hits_low) > 1:
        t_stat, p_value = stats.ttest_ind(all_hits_high, all_hits_low)
        p_value = float(p_value)
    else:
        t_stat, p_value = 0.0, 1.0

    # Korrelation zwischen Position und Hits
    # (vereinfacht: nutze t-Statistik als Proxy)
    correlation = float(t_stat / np.sqrt(len(all_hits_high) + t_stat**2)) if len(all_hits_high) > 0 else 0.0

    # Effect Size (Cohen's d)
    pooled_std = np.sqrt((std_high**2 + std_low**2) / 2) if (std_high + std_low) > 0 else 1
    effect_size = (mean_high - mean_low) / pooled_std if pooled_std > 0 else 0.0

    # Erwartung bei Zufall: top_n / number_range * 20 (20 Zahlen pro Ziehung)
    expected_random = top_n / number_range * 20

    # Interpretation
    if p_value < 0.05 and mean_high > mean_low:
        interpretation = (
            f"Signifikanter Unterschied: Top-{top_n} Index-Zahlen treffen haeufiger "
            f"({mean_high:.2f} vs. {mean_low:.2f}, p={p_value:.4f}). "
            f"Erwartet bei Zufall: {expected_random:.2f}. "
            f"Effect Size (Cohen's d): {effect_size:.2f}"
        )
    elif mean_high > expected_random * 1.1:
        interpretation = (
            f"Trend erkennbar: Top-{top_n} treffen ueber Zufall "
            f"({mean_high:.2f} vs. erwartet {expected_random:.2f}), "
            f"aber nicht signifikant (p={p_value:.4f})."
        )
    else:
        interpretation = (
            f"Kein signifikanter Unterschied zwischen High- und Low-Index "
            f"({mean_high:.2f} vs. {mean_low:.2f}, p={p_value:.4f}). "
            f"Index-System zeigt keine Vorhersagekraft."
        )

    return CorrelationResult(
        correlation=correlation,
        p_value=p_value,
        mean_hits_high_index=mean_high,
        mean_hits_low_index=mean_low,
        effect_size=float(effect_size),
        interpretation=interpretation,
        n_segments=len(segments),
        segment_details=segment_details,
    )


def export_index_table(
    index_result: IndexResult,
    output_path: str,
) -> None:
    """Exportiert Index-Tabelle als JSON.

    Args:
        index_result: IndexResult von calculate_index_table
        output_path: Pfad zur Ausgabedatei
    """
    import json
    from pathlib import Path

    data = {
        "last_reset_date": (
            index_result.last_reset_date.isoformat()
            if index_result.last_reset_date
            else None
        ),
        "draws_since_reset": index_result.draws_since_reset,
        "gk1_event_type": index_result.gk1_event_type,
        "indices": [
            {
                "number": idx.number,
                "current_index": idx.current_index,
                "last_seen": idx.last_seen.isoformat() if idx.last_seen else None,
                "total_appearances": idx.total_appearances,
            }
            for idx in sorted(index_result.indices.values(), key=lambda x: x.number)
        ],
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


__all__ = [
    "NumberIndex",
    "IndexResult",
    "CorrelationResult",
    "calculate_index_table",
    "calculate_index_correlation",
    "export_index_table",
]
