"""Cycle Phase Analysis - Zyklus-Phasen basierend auf Jackpot-Events.

Dieses Modul markiert jede KENO-Ziehung mit einer Phase basierend auf
der Anzahl Tage seit dem letzten Jackpot-Event:

- COOLDOWN: 0-30 Tage nach Jackpot (System spart, reduzierte ROI)
- GROWTH: 31-60 Tage nach Jackpot (Uebergangsphase)
- HOT: >60 Tage nach Jackpot (hohe Jackpot-Wahrscheinlichkeit)
- UNKNOWN: Vor dem ersten Jackpot im Datensatz

Basiert auf Axiom A7 (Reset-Zyklen) und WL-003 Jackpot-Cooldown Erkenntnissen.

Usage:
    from kenobase.analysis.cycle_phases import (
        Phase,
        PhaseLabel,
        label_phases,
        get_phase_for_date,
    )

    # Mit GK1-Daten
    from kenobase.analysis.jackpot_correlation import load_gk1_events, get_jackpot_dates

    gk1_events = load_gk1_events("Keno_GPTs/10-9_KGDaten_gefiltert.csv")
    jackpot_dates = get_jackpot_dates(gk1_events)
    labels = label_phases(draws, jackpot_dates)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)

# Phase boundaries in days
COOLDOWN_MAX_DAYS = 30
GROWTH_MAX_DAYS = 60

# Sub-cooldown phase boundaries (within COOLDOWN)
FRUEH_MAX_DAYS = 14
SPAET_MAX_DAYS = 30


class SubCooldownPhase(str, Enum):
    """Sub-Phase innerhalb der COOLDOWN-Periode (0-30 Tage).

    Attributes:
        FRUEH: 1-14 Tage nach Jackpot (fruehe Cooldown-Phase)
        SPAET: 15-30 Tage nach Jackpot (spaete Cooldown-Phase)
        NORMAL: >30 Tage nach Jackpot (keine Cooldown)
        UNKNOWN: Vor erstem Jackpot im Datensatz
    """

    FRUEH = "FRUEH"
    SPAET = "SPAET"
    NORMAL = "NORMAL"
    UNKNOWN = "UNKNOWN"


class Phase(str, Enum):
    """Zyklus-Phase basierend auf Tagen seit letztem Jackpot.

    Attributes:
        COOLDOWN: 0-30 Tage nach Jackpot (System spart)
        GROWTH: 31-60 Tage nach Jackpot (Uebergangsphase)
        HOT: >60 Tage nach Jackpot (hohe Jackpot-Wahrscheinlichkeit)
        UNKNOWN: Vor erstem Jackpot im Datensatz
    """

    COOLDOWN = "COOLDOWN"
    GROWTH = "GROWTH"
    HOT = "HOT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class PhaseLabel:
    """Label fuer eine einzelne Ziehung mit Phase und Tage seit Jackpot.

    Attributes:
        date: Datum der Ziehung
        phase: Zyklus-Phase
        days_since_jackpot: Tage seit letztem Jackpot (None wenn UNKNOWN)
        last_jackpot_date: Datum des letzten Jackpots (None wenn UNKNOWN)
    """

    date: datetime
    phase: Phase
    days_since_jackpot: int | None
    last_jackpot_date: datetime | None


def get_sub_cooldown_phase(days_since_jackpot: int | None) -> SubCooldownPhase:
    """Bestimme Sub-Cooldown-Phase basierend auf Tagen seit Jackpot.

    Args:
        days_since_jackpot: Anzahl Tage seit letztem Jackpot (None = vor erstem)

    Returns:
        SubCooldownPhase enum Wert:
        - FRUEH: 1-14 Tage (fruehe Cooldown-Phase)
        - SPAET: 15-30 Tage (spaete Cooldown-Phase)
        - NORMAL: >30 Tage (keine Cooldown)
        - UNKNOWN: Kein vorheriger Jackpot
    """
    if days_since_jackpot is None:
        return SubCooldownPhase.UNKNOWN
    if days_since_jackpot <= 0:
        # Day 0 = Jackpot-Tag selbst, zaehlt als FRUEH
        return SubCooldownPhase.FRUEH
    if days_since_jackpot <= FRUEH_MAX_DAYS:
        return SubCooldownPhase.FRUEH
    if days_since_jackpot <= SPAET_MAX_DAYS:
        return SubCooldownPhase.SPAET
    return SubCooldownPhase.NORMAL


def get_phase_for_days(days_since_jackpot: int | None) -> Phase:
    """Bestimme Phase basierend auf Tagen seit Jackpot.

    Args:
        days_since_jackpot: Anzahl Tage seit letztem Jackpot (None = vor erstem)

    Returns:
        Phase enum Wert
    """
    if days_since_jackpot is None:
        return Phase.UNKNOWN
    if days_since_jackpot <= COOLDOWN_MAX_DAYS:
        return Phase.COOLDOWN
    if days_since_jackpot <= GROWTH_MAX_DAYS:
        return Phase.GROWTH
    return Phase.HOT


def get_phase_for_date(
    target_date: datetime,
    jackpot_dates: set[datetime],
) -> PhaseLabel:
    """Bestimme Phase fuer ein einzelnes Datum.

    Args:
        target_date: Datum fuer das Phase bestimmt werden soll
        jackpot_dates: Set von Jackpot-Datumswerten (normalisiert auf Mitternacht)

    Returns:
        PhaseLabel mit Phase und Tagen seit Jackpot
    """
    # Normalize target date to midnight
    target_normalized = target_date.replace(hour=0, minute=0, second=0, microsecond=0)

    if not jackpot_dates:
        return PhaseLabel(
            date=target_date,
            phase=Phase.UNKNOWN,
            days_since_jackpot=None,
            last_jackpot_date=None,
        )

    # Find most recent jackpot before or on target_date
    past_jackpots = [jp for jp in jackpot_dates if jp <= target_normalized]

    if not past_jackpots:
        # Target date is before all jackpots
        return PhaseLabel(
            date=target_date,
            phase=Phase.UNKNOWN,
            days_since_jackpot=None,
            last_jackpot_date=None,
        )

    last_jackpot = max(past_jackpots)
    days_since = (target_normalized - last_jackpot).days
    phase = get_phase_for_days(days_since)

    return PhaseLabel(
        date=target_date,
        phase=phase,
        days_since_jackpot=days_since,
        last_jackpot_date=last_jackpot,
    )


def label_phases(
    draws: list["DrawResult"],
    jackpot_dates: set[datetime],
) -> dict[datetime, PhaseLabel]:
    """Label alle Ziehungen mit Zyklus-Phasen.

    Args:
        draws: Liste von DrawResult Objekten
        jackpot_dates: Set von Jackpot-Datumswerten (normalisiert auf Mitternacht)

    Returns:
        Dict mapping Ziehungsdatum -> PhaseLabel
    """
    if not draws:
        return {}

    labels: dict[datetime, PhaseLabel] = {}

    # Sort jackpot dates for efficient lookup
    sorted_jackpots = sorted(jackpot_dates) if jackpot_dates else []

    for draw in draws:
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)

        if not sorted_jackpots:
            labels[draw_date] = PhaseLabel(
                date=draw.date,
                phase=Phase.UNKNOWN,
                days_since_jackpot=None,
                last_jackpot_date=None,
            )
            continue

        # Binary search for most recent jackpot <= draw_date
        last_jackpot = None
        for jp in sorted_jackpots:
            if jp <= draw_date:
                last_jackpot = jp
            else:
                break

        if last_jackpot is None:
            labels[draw_date] = PhaseLabel(
                date=draw.date,
                phase=Phase.UNKNOWN,
                days_since_jackpot=None,
                last_jackpot_date=None,
            )
        else:
            days_since = (draw_date - last_jackpot).days
            phase = get_phase_for_days(days_since)
            labels[draw_date] = PhaseLabel(
                date=draw.date,
                phase=phase,
                days_since_jackpot=days_since,
                last_jackpot_date=last_jackpot,
            )

    # Log statistics
    phase_counts = {p: 0 for p in Phase}
    for label in labels.values():
        phase_counts[label.phase] += 1

    logger.info(
        f"Labeled {len(labels)} draws: "
        f"COOLDOWN={phase_counts[Phase.COOLDOWN]}, "
        f"GROWTH={phase_counts[Phase.GROWTH]}, "
        f"HOT={phase_counts[Phase.HOT]}, "
        f"UNKNOWN={phase_counts[Phase.UNKNOWN]}"
    )

    return labels


def filter_draws_by_phase(
    draws: list["DrawResult"],
    labels: dict[datetime, PhaseLabel],
    phase: Phase,
) -> list["DrawResult"]:
    """Filtere Ziehungen nach Phase.

    Args:
        draws: Liste von DrawResult Objekten
        labels: Phase-Labels von label_phases()
        phase: Gewuenschte Phase

    Returns:
        Liste von Ziehungen mit der angegebenen Phase
    """
    result = []
    for draw in draws:
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)
        label = labels.get(draw_date)
        if label and label.phase == phase:
            result.append(draw)
    return result


def get_phase_statistics(
    labels: dict[datetime, PhaseLabel],
) -> dict[str, any]:
    """Berechne Statistiken ueber Phase-Verteilung.

    Args:
        labels: Phase-Labels von label_phases()

    Returns:
        Dict mit Statistiken pro Phase
    """
    phase_counts = {p.value: 0 for p in Phase}
    phase_days_sum = {p.value: 0 for p in Phase}
    phase_days_count = {p.value: 0 for p in Phase}

    for label in labels.values():
        phase_counts[label.phase.value] += 1
        if label.days_since_jackpot is not None:
            phase_days_sum[label.phase.value] += label.days_since_jackpot
            phase_days_count[label.phase.value] += 1

    total = len(labels)
    stats = {
        "total_draws": total,
        "phase_distribution": {},
    }

    for phase in Phase:
        count = phase_counts[phase.value]
        days_count = phase_days_count[phase.value]
        stats["phase_distribution"][phase.value] = {
            "count": count,
            "ratio": count / total if total > 0 else 0.0,
            "avg_days_since_jackpot": (
                phase_days_sum[phase.value] / days_count if days_count > 0 else None
            ),
        }

    return stats


__all__ = [
    "Phase",
    "PhaseLabel",
    "SubCooldownPhase",
    "COOLDOWN_MAX_DAYS",
    "GROWTH_MAX_DAYS",
    "FRUEH_MAX_DAYS",
    "SPAET_MAX_DAYS",
    "get_phase_for_days",
    "get_phase_for_date",
    "get_sub_cooldown_phase",
    "label_phases",
    "filter_draws_by_phase",
    "get_phase_statistics",
]
