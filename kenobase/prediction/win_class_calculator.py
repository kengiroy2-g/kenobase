"""Gewinnklassen-Berechnung fuer V1 und V2 Tickets.

Dieses Modul stellt eine DRY-konforme Gewinnklassen-Berechnung bereit,
die parallel fuer mehrere Ticket-Strategien (V1: OPTIMAL_TICKETS_KI1,
V2: BIRTHDAY_AVOIDANCE_TICKETS_V2) angewendet werden kann.

Single Source of Truth fuer Quoten: kenobase/core/keno_quotes.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from kenobase.core.keno_quotes import KENO_FIXED_QUOTES_BY_TYPE, get_fixed_quote


# Gewinnklassen-Labels aus dem offiziellen Fixed-Quote-Table ableiten.
# GK1 = hoechste Treffer, GK2 = zweithoechste, usw.
GK_LABELS_BY_TYPE: dict[int, dict[int, str]] = {}
for _keno_type, _hits_to_quote in KENO_FIXED_QUOTES_BY_TYPE.items():
    ordered = sorted(_hits_to_quote.keys(), reverse=True)
    GK_LABELS_BY_TYPE[int(_keno_type)] = {int(h): f"GK{i+1}" for i, h in enumerate(ordered)}


@dataclass
class WinClassResult:
    """Ergebnis einer Gewinnklassen-Berechnung fuer ein Ticket."""

    keno_type: int
    hits: int
    gewinnklasse: str | None
    quote: float


@dataclass
class TicketEvaluation:
    """Aggregierte Auswertung eines Tickets ueber mehrere Ziehungen."""

    ticket_name: str
    keno_type: int
    numbers: list[int]
    total_draws: int = 0
    total_hits: int = 0
    hit_distribution: dict[int, int] = field(default_factory=dict)
    gewinnklassen_count: dict[str, int] = field(default_factory=dict)
    total_winnings: float = 0.0
    roi: float = 0.0


def get_gewinnklasse(keno_type: int, hits: int) -> WinClassResult:
    """Bestimmt Gewinnklasse und Quote fuer eine Treffer-Anzahl.

    Args:
        keno_type: KENO-Typ (2-10)
        hits: Anzahl der Treffer

    Returns:
        WinClassResult mit Gewinnklasse und Quote
    """
    keno_type = int(keno_type)
    hits = int(hits)

    quote = get_fixed_quote(keno_type, hits)
    gk_label = None

    if keno_type in GK_LABELS_BY_TYPE and quote > 0:
        gk_label = GK_LABELS_BY_TYPE[keno_type].get(hits)

    return WinClassResult(
        keno_type=keno_type,
        hits=hits,
        gewinnklasse=gk_label,
        quote=quote,
    )


def calculate_hits(ticket: Sequence[int], drawn: set[int]) -> int:
    """Berechnet Anzahl Treffer eines Tickets gegen eine Ziehung.

    Args:
        ticket: Ticket-Zahlen (Liste oder Set)
        drawn: Gezogene Zahlen (Set)

    Returns:
        Anzahl der Treffer
    """
    return len(set(ticket) & drawn)


def evaluate_ticket_single_draw(
    ticket: Sequence[int],
    drawn: set[int],
) -> WinClassResult:
    """Wertet ein Ticket gegen eine einzelne Ziehung aus.

    Args:
        ticket: Ticket-Zahlen
        drawn: Gezogene Zahlen

    Returns:
        WinClassResult mit Gewinnklasse und Quote
    """
    keno_type = len(ticket)
    hits = calculate_hits(ticket, drawn)
    return get_gewinnklasse(keno_type, hits)


def evaluate_ticket_parallel(
    tickets: Mapping[str, Sequence[int]],
    draws: Sequence[set[int]],
) -> dict[str, TicketEvaluation]:
    """Wertet mehrere Tickets parallel gegen mehrere Ziehungen aus.

    Args:
        tickets: Dict mit Ticket-Name -> Zahlen
        draws: Liste von Ziehungs-Sets

    Returns:
        Dict mit Ticket-Name -> TicketEvaluation
    """
    results: dict[str, TicketEvaluation] = {}

    for name, numbers in tickets.items():
        keno_type = len(numbers)
        evaluation = TicketEvaluation(
            ticket_name=name,
            keno_type=keno_type,
            numbers=list(numbers),
            total_draws=len(draws),
        )

        for drawn in draws:
            hits = calculate_hits(numbers, drawn)
            evaluation.total_hits += hits
            evaluation.hit_distribution[hits] = evaluation.hit_distribution.get(hits, 0) + 1

            wc = get_gewinnklasse(keno_type, hits)
            if wc.gewinnklasse:
                evaluation.gewinnklassen_count[wc.gewinnklasse] = (
                    evaluation.gewinnklassen_count.get(wc.gewinnklasse, 0) + 1
                )
                evaluation.total_winnings += wc.quote

        # ROI berechnen: (Gewinn - Einsatz) / Einsatz
        # Einsatz = 1 EUR pro Ziehung
        einsatz = float(evaluation.total_draws)
        if einsatz > 0:
            evaluation.roi = (evaluation.total_winnings - einsatz) / einsatz

        results[name] = evaluation

    return results


def evaluate_v1_v2_parallel(
    v1_tickets: Mapping[int, Sequence[int]],
    v2_tickets: Mapping[int, Sequence[int]],
    draws: Sequence[set[int]],
) -> dict[str, dict[str, TicketEvaluation]]:
    """Wertet V1 und V2 Tickets parallel aus.

    Args:
        v1_tickets: V1 Tickets (OPTIMAL_TICKETS_KI1), keno_type -> numbers
        v2_tickets: V2 Tickets (BIRTHDAY_AVOIDANCE_TICKETS_V2), keno_type -> numbers
        draws: Liste von Ziehungs-Sets

    Returns:
        Dict mit "v1" -> {typ_X: TicketEvaluation}, "v2" -> {typ_X: TicketEvaluation}
    """
    # V1 Tickets vorbereiten
    v1_named: dict[str, Sequence[int]] = {f"v1_typ{kt}": nums for kt, nums in v1_tickets.items()}

    # V2 Tickets vorbereiten
    v2_named: dict[str, Sequence[int]] = {f"v2_typ{kt}": nums for kt, nums in v2_tickets.items()}

    # Alle Tickets zusammenfuehren und parallel evaluieren
    all_tickets = {**v1_named, **v2_named}
    all_results = evaluate_ticket_parallel(all_tickets, draws)

    # Ergebnisse nach V1/V2 aufteilen
    v1_results = {k: v for k, v in all_results.items() if k.startswith("v1_")}
    v2_results = {k: v for k, v in all_results.items() if k.startswith("v2_")}

    return {"v1": v1_results, "v2": v2_results}


def format_evaluation_summary(evaluation: TicketEvaluation) -> dict:
    """Formatiert eine TicketEvaluation als JSON-serialisierbares Dict.

    Args:
        evaluation: TicketEvaluation Objekt

    Returns:
        Dict mit Summary-Daten
    """
    avg_hits = evaluation.total_hits / max(evaluation.total_draws, 1)
    return {
        "ticket_name": evaluation.ticket_name,
        "keno_type": evaluation.keno_type,
        "numbers": evaluation.numbers,
        "total_draws": evaluation.total_draws,
        "avg_hits": round(avg_hits, 3),
        "hit_distribution": evaluation.hit_distribution,
        "gewinnklassen": evaluation.gewinnklassen_count,
        "total_winnings_eur": round(evaluation.total_winnings, 2),
        "roi_percent": round(evaluation.roi * 100, 2),
    }


__all__ = [
    "GK_LABELS_BY_TYPE",
    "WinClassResult",
    "TicketEvaluation",
    "get_gewinnklasse",
    "calculate_hits",
    "evaluate_ticket_single_draw",
    "evaluate_ticket_parallel",
    "evaluate_v1_v2_parallel",
    "format_evaluation_summary",
]
