"""Unit tests fuer win_class_calculator.py.

Testet Gewinnklassen-Berechnung fuer V1 und V2 Tickets.
"""

from __future__ import annotations

import pytest

from kenobase.prediction.win_class_calculator import (
    GK_LABELS_BY_TYPE,
    WinClassResult,
    TicketEvaluation,
    get_gewinnklasse,
    calculate_hits,
    evaluate_ticket_single_draw,
    evaluate_ticket_parallel,
    evaluate_v1_v2_parallel,
    format_evaluation_summary,
)


class TestGKLabels:
    """Tests fuer GK_LABELS_BY_TYPE Mapping."""

    def test_gk_labels_exist_for_all_keno_types(self):
        """GK Labels existieren fuer Typ 2-10."""
        for keno_type in range(2, 11):
            assert keno_type in GK_LABELS_BY_TYPE

    def test_gk1_is_highest_hits(self):
        """GK1 entspricht der hoechsten Treffer-Anzahl."""
        # Typ 10: GK1 = 10 Treffer
        assert GK_LABELS_BY_TYPE[10][10] == "GK1"
        # Typ 9: GK1 = 9 Treffer
        assert GK_LABELS_BY_TYPE[9][9] == "GK1"
        # Typ 8: GK1 = 8 Treffer
        assert GK_LABELS_BY_TYPE[8][8] == "GK1"

    def test_gk_labels_typ8_includes_zero_hits(self):
        """Typ 8 hat GK fuer 0 Treffer (Trostpreis)."""
        assert 0 in GK_LABELS_BY_TYPE[8]


class TestGetGewinnklasse:
    """Tests fuer get_gewinnklasse Funktion."""

    def test_typ10_full_match(self):
        """10/10 Treffer = GK1, Quote 100000."""
        result = get_gewinnklasse(10, 10)
        assert result.gewinnklasse == "GK1"
        assert result.quote == 100000.0

    def test_typ10_zero_hits(self):
        """0/10 Treffer = GK7, Quote 2."""
        result = get_gewinnklasse(10, 0)
        assert result.gewinnklasse is not None
        assert result.quote == 2.0

    def test_typ9_full_match(self):
        """9/9 Treffer = GK1, Quote 50000."""
        result = get_gewinnklasse(9, 9)
        assert result.gewinnklasse == "GK1"
        assert result.quote == 50000.0

    def test_no_win_no_gk(self):
        """Treffer ohne Gewinn -> keine GK."""
        result = get_gewinnklasse(10, 3)
        assert result.gewinnklasse is None
        assert result.quote == 0.0

    def test_invalid_keno_type(self):
        """Ungueltiger Typ -> keine GK."""
        result = get_gewinnklasse(99, 5)
        assert result.gewinnklasse is None
        assert result.quote == 0.0


class TestCalculateHits:
    """Tests fuer calculate_hits Funktion."""

    def test_no_match(self):
        """Keine Treffer."""
        ticket = [1, 2, 3, 4, 5, 6]
        drawn = {11, 12, 13, 14, 15, 16, 17, 18, 19, 20}
        assert calculate_hits(ticket, drawn) == 0

    def test_partial_match(self):
        """Teilweise Treffer."""
        ticket = [1, 2, 3, 4, 5, 6]
        drawn = {1, 2, 10, 11, 12, 13, 14, 15, 16, 17}
        assert calculate_hits(ticket, drawn) == 2

    def test_full_match(self):
        """Alle Treffer."""
        ticket = [1, 2, 3, 4, 5, 6]
        drawn = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
        assert calculate_hits(ticket, drawn) == 6


class TestEvaluateTicketSingleDraw:
    """Tests fuer evaluate_ticket_single_draw Funktion."""

    def test_typ9_with_5_hits(self):
        """Typ 9 mit 5 Treffern = GK5, Quote 2."""
        ticket = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        drawn = {1, 2, 3, 4, 5, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34}
        result = evaluate_ticket_single_draw(ticket, drawn)
        assert result.keno_type == 9
        assert result.hits == 5
        assert result.gewinnklasse == "GK5"
        assert result.quote == 2.0

    def test_typ8_with_zero_hits(self):
        """Typ 8 mit 0 Treffern = Trostpreis."""
        ticket = [1, 2, 3, 4, 5, 6, 7, 8]
        drawn = {20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39}
        result = evaluate_ticket_single_draw(ticket, drawn)
        assert result.keno_type == 8
        assert result.hits == 0
        assert result.gewinnklasse is not None
        assert result.quote == 1.0


class TestEvaluateTicketParallel:
    """Tests fuer evaluate_ticket_parallel Funktion."""

    def test_multiple_tickets_multiple_draws(self):
        """Mehrere Tickets gegen mehrere Ziehungen."""
        tickets = {
            "ticket_a": [1, 2, 3, 4, 5, 6],  # Typ 6
            "ticket_b": [10, 20, 30, 40, 50, 60, 70, 80],  # Typ 8
        }
        draws = [
            {1, 2, 3, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27},
            {4, 5, 6, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27},
        ]
        results = evaluate_ticket_parallel(tickets, draws)

        assert "ticket_a" in results
        assert "ticket_b" in results
        assert results["ticket_a"].total_draws == 2
        assert results["ticket_b"].total_draws == 2

    def test_empty_draws(self):
        """Keine Ziehungen."""
        tickets = {"ticket_a": [1, 2, 3, 4, 5, 6]}
        draws: list[set[int]] = []
        results = evaluate_ticket_parallel(tickets, draws)

        assert results["ticket_a"].total_draws == 0
        assert results["ticket_a"].roi == 0.0


class TestEvaluateV1V2Parallel:
    """Tests fuer evaluate_v1_v2_parallel Funktion."""

    def test_v1_v2_separation(self):
        """V1 und V2 Ergebnisse werden getrennt."""
        v1_tickets = {9: [1, 2, 3, 4, 5, 6, 7, 8, 9]}
        v2_tickets = {9: [10, 20, 30, 40, 50, 60, 70, 61, 62]}
        draws = [
            {1, 2, 3, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26}
        ]
        results = evaluate_v1_v2_parallel(v1_tickets, v2_tickets, draws)

        assert "v1" in results
        assert "v2" in results
        assert "v1_typ9" in results["v1"]
        assert "v2_typ9" in results["v2"]


class TestFormatEvaluationSummary:
    """Tests fuer format_evaluation_summary Funktion."""

    def test_summary_format(self):
        """Summary enthaelt alle erwarteten Felder."""
        evaluation = TicketEvaluation(
            ticket_name="test_ticket",
            keno_type=9,
            numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9],
            total_draws=10,
            total_hits=30,
            hit_distribution={3: 5, 4: 3, 5: 2},
            gewinnklassen_count={"GK5": 2, "GK4": 1},
            total_winnings=15.0,
            roi=0.5,
        )
        summary = format_evaluation_summary(evaluation)

        assert summary["ticket_name"] == "test_ticket"
        assert summary["keno_type"] == 9
        assert summary["total_draws"] == 10
        assert summary["avg_hits"] == 3.0
        assert summary["roi_percent"] == 50.0
        assert summary["total_winnings_eur"] == 15.0


class TestIntegrationWithRealTickets:
    """Integration Tests mit echten V1/V2 Ticket-Definitionen."""

    def test_v1_ticket_typ9_structure(self):
        """V1 Typ 9 Ticket hat korrekte Struktur."""
        # Aus super_model_synthesis.py
        v1_typ9 = [3, 9, 10, 20, 24, 36, 49, 51, 64]
        assert len(v1_typ9) == 9
        assert all(1 <= n <= 70 for n in v1_typ9)

    def test_v2_ticket_typ9_structure(self):
        """V2 Typ 9 Ticket hat korrekte Struktur."""
        # Aus super_model_synthesis.py
        v2_typ9 = [3, 7, 36, 43, 48, 51, 58, 61, 64]
        assert len(v2_typ9) == 9
        assert all(1 <= n <= 70 for n in v2_typ9)

    def test_v1_v2_evaluation_against_mock_draws(self):
        """V1 und V2 Tickets gegen Mock-Ziehungen."""
        from scripts.super_model_synthesis import (
            OPTIMAL_TICKETS_KI1,
            BIRTHDAY_AVOIDANCE_TICKETS_V2,
        )

        # Mock-Ziehungen
        draws = [
            {3, 7, 10, 20, 36, 49, 51, 58, 61, 64, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21},
            {1, 2, 4, 5, 6, 8, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35},
        ]

        results = evaluate_v1_v2_parallel(OPTIMAL_TICKETS_KI1, BIRTHDAY_AVOIDANCE_TICKETS_V2, draws)

        # Beide Strategien wurden evaluiert
        assert len(results["v1"]) > 0
        assert len(results["v2"]) > 0
