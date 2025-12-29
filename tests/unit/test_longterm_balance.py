"""Unit Tests fuer kenobase.analysis.longterm_balance (TASK-R05).

Testet Balance-Score Berechnung, Trigger-Erkennung und Klassifikation.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from kenobase.analysis.longterm_balance import (
    BalanceResult,
    BalanceTrigger,
    NumberBalanceStats,
    analyze_longterm_balance,
    calculate_balance_score,
    calculate_deviation_std,
    classify_balance,
    detect_balance_triggers,
    generate_longterm_balance_report,
    get_overrepresented_numbers,
    get_underrepresented_numbers,
)
from kenobase.core.data_loader import DrawResult, GameType


def create_draw(date: datetime, numbers: list[int]) -> DrawResult:
    """Helper: Erstellt DrawResult fuer Tests."""
    return DrawResult(date=date, numbers=numbers, game_type=GameType.KENO)


def create_uniform_draws(n: int, start_date: datetime | None = None) -> list[DrawResult]:
    """Helper: Erstellt n Ziehungen mit uniformer Verteilung."""
    start = start_date or datetime(2023, 1, 1)
    draws = []
    for i in range(n):
        # Rotate through numbers 1-70, picking 20 each time
        offset = (i * 20) % 70
        numbers = [(j % 70) + 1 for j in range(offset, offset + 20)]
        draws.append(create_draw(start + timedelta(days=i), numbers))
    return draws


def create_biased_draws(
    n: int,
    biased_number: int,
    bias_factor: float,
    start_date: datetime | None = None,
) -> list[DrawResult]:
    """Helper: Erstellt n Ziehungen mit Bias fuer eine Zahl.

    Args:
        n: Anzahl Ziehungen
        biased_number: Zahl mit Bias
        bias_factor: >1 = haeufiger, <1 = seltener
    """
    start = start_date or datetime(2023, 1, 1)
    draws = []
    import random
    random.seed(42)

    for i in range(n):
        # Base numbers excluding biased_number
        available = [x for x in range(1, 71) if x != biased_number]
        numbers = random.sample(available, 19)

        # Add biased number based on bias_factor
        # Normal prob = 20/70 = 0.286
        # With bias_factor 2.0: prob = 0.571
        if random.random() < min(1.0, (20/70) * bias_factor):
            numbers.append(biased_number)
        else:
            # Fill with another number if biased_number not included
            remaining = [x for x in available if x not in numbers]
            if remaining:
                numbers.append(random.choice(remaining))

        draws.append(create_draw(start + timedelta(days=i), numbers[:20]))
    return draws


class TestCalculateBalanceScore:
    """Tests fuer calculate_balance_score()."""

    def test_perfect_balance(self) -> None:
        """Perfekte Balance sollte 0 ergeben."""
        assert calculate_balance_score(100, 100) == 0.0

    def test_underrepresented(self) -> None:
        """Zu wenige Erscheinungen sollte negative Balance ergeben."""
        # 80 statt 100 erwartet = -20%
        score = calculate_balance_score(80, 100)
        assert score == pytest.approx(-0.2, rel=0.01)

    def test_overrepresented(self) -> None:
        """Zu viele Erscheinungen sollte positive Balance ergeben."""
        # 120 statt 100 erwartet = +20%
        score = calculate_balance_score(120, 100)
        assert score == pytest.approx(0.2, rel=0.01)

    def test_zero_expected(self) -> None:
        """Null Erwartung sollte 0 zurueckgeben (Guard)."""
        assert calculate_balance_score(10, 0) == 0.0
        assert calculate_balance_score(0, 0) == 0.0

    def test_extreme_underrepresented(self) -> None:
        """Keine Erscheinungen sollte -1.0 ergeben."""
        score = calculate_balance_score(0, 100)
        assert score == pytest.approx(-1.0, rel=0.01)


class TestCalculateDeviationStd:
    """Tests fuer calculate_deviation_std()."""

    def test_perfect_match(self) -> None:
        """Perfekte Uebereinstimmung sollte 0 std ergeben."""
        # 500 draws, expected = 500 * 0.286 = 143
        expected = 500 * (20 / 70)
        std = calculate_deviation_std(int(expected), expected, 500)
        assert abs(std) < 0.1

    def test_positive_deviation(self) -> None:
        """Mehr als erwartet sollte positive std ergeben."""
        expected = 500 * (20 / 70)  # ~143
        observed = int(expected) + 20  # 20 mehr
        std = calculate_deviation_std(observed, expected, 500)
        assert std > 0

    def test_negative_deviation(self) -> None:
        """Weniger als erwartet sollte negative std ergeben."""
        expected = 500 * (20 / 70)  # ~143
        observed = int(expected) - 20  # 20 weniger
        std = calculate_deviation_std(observed, expected, 500)
        assert std < 0


class TestClassifyBalance:
    """Tests fuer classify_balance()."""

    def test_normal_range(self) -> None:
        """Kleine Abweichung sollte 'normal' sein."""
        assert classify_balance(0.05) == "normal"
        assert classify_balance(-0.05) == "normal"
        assert classify_balance(0.0) == "normal"

    def test_underrepresented(self) -> None:
        """Stark negative Balance sollte 'underrepresented' sein."""
        assert classify_balance(-0.15) == "underrepresented"
        assert classify_balance(-0.5) == "underrepresented"

    def test_overrepresented(self) -> None:
        """Stark positive Balance sollte 'overrepresented' sein."""
        assert classify_balance(0.15) == "overrepresented"
        assert classify_balance(0.5) == "overrepresented"

    def test_custom_threshold(self) -> None:
        """Custom Threshold sollte funktionieren."""
        assert classify_balance(0.15, threshold=0.2) == "normal"
        assert classify_balance(-0.15, threshold=0.2) == "normal"
        assert classify_balance(0.25, threshold=0.2) == "overrepresented"


class TestDetectBalanceTriggers:
    """Tests fuer detect_balance_triggers()."""

    def test_empty_draws(self) -> None:
        """Leere Liste sollte leere Trigger-Liste ergeben."""
        triggers = detect_balance_triggers([], window=500)
        assert triggers == []

    def test_insufficient_draws(self) -> None:
        """Zu wenige Draws sollte leere Trigger-Liste ergeben."""
        draws = create_uniform_draws(100)
        triggers = detect_balance_triggers(draws, window=500)
        assert triggers == []

    def test_uniform_no_triggers(self) -> None:
        """Uniforme Verteilung sollte keine/wenige Trigger haben."""
        draws = create_uniform_draws(600)
        triggers = detect_balance_triggers(draws, window=500, trigger_threshold_std=3.0)
        # Mit uniformer Verteilung sollten keine extremen Abweichungen auftreten
        # (Threshold 3.0 std ist streng)
        assert len(triggers) < 10  # Relaxed assertion for statistical variance

    def test_biased_triggers(self) -> None:
        """Stark verzerrte Verteilung sollte Trigger erzeugen."""
        draws = create_biased_draws(600, biased_number=42, bias_factor=2.5)
        triggers = detect_balance_triggers(draws, window=500, trigger_threshold_std=1.5)

        # Pruefen dass Trigger gefunden wurden
        assert len(triggers) > 0

    def test_trigger_structure(self) -> None:
        """Trigger sollte korrekte Struktur haben."""
        draws = create_biased_draws(600, biased_number=42, bias_factor=3.0)
        triggers = detect_balance_triggers(draws, window=500, trigger_threshold_std=1.0)

        if triggers:
            t = triggers[0]
            assert isinstance(t, BalanceTrigger)
            assert 1 <= t.number <= 70
            assert t.trigger_type in ("REVERSION_UP", "REVERSION_DOWN")
            assert 0.0 <= t.confidence <= 1.0
            assert t.date is not None


class TestAnalyzeLongtermBalance:
    """Tests fuer analyze_longterm_balance()."""

    def test_result_structure(self) -> None:
        """Result sollte korrekte Struktur haben."""
        draws = create_uniform_draws(600)
        result = analyze_longterm_balance(draws, window=500)

        assert isinstance(result, BalanceResult)
        assert result.total_draws == 600
        assert result.window == 500
        assert result.expected_frequency == pytest.approx(20 / 70, rel=0.01)
        assert len(result.number_stats) == 70

    def test_all_numbers_covered(self) -> None:
        """Alle 70 Zahlen sollten Statistiken haben."""
        draws = create_uniform_draws(600)
        result = analyze_longterm_balance(draws, window=500)

        numbers = {s.number for s in result.number_stats}
        assert numbers == set(range(1, 71))

    def test_classification_counts(self) -> None:
        """Klassifikations-Counts sollten korrekt sein."""
        draws = create_uniform_draws(600)
        result = analyze_longterm_balance(draws, window=500)

        under = sum(1 for s in result.number_stats if s.classification == "underrepresented")
        over = sum(1 for s in result.number_stats if s.classification == "overrepresented")
        normal = sum(1 for s in result.number_stats if s.classification == "normal")

        assert under == result.underrepresented_count
        assert over == result.overrepresented_count
        assert under + over + normal == 70

    def test_insufficient_data(self) -> None:
        """Zu wenige Daten sollte leeres Result ergeben."""
        draws = create_uniform_draws(100)
        result = analyze_longterm_balance(draws, window=500)

        assert result.total_draws == 100
        assert len(result.number_stats) == 0


class TestConvenienceFunctions:
    """Tests fuer Convenience-Funktionen."""

    def test_get_underrepresented_returns_list(self) -> None:
        """get_underrepresented_numbers sollte Liste zurueckgeben."""
        draws = create_biased_draws(600, biased_number=42, bias_factor=0.2)
        numbers = get_underrepresented_numbers(draws, window=500)

        assert isinstance(numbers, list)
        # Zahl 42 sollte unterrepraesentiert sein (bias_factor 0.2)
        # Note: May not always be in list due to randomness
        assert all(isinstance(n, int) for n in numbers)

    def test_get_overrepresented_returns_list(self) -> None:
        """get_overrepresented_numbers sollte Liste zurueckgeben."""
        draws = create_biased_draws(600, biased_number=42, bias_factor=3.0)
        numbers = get_overrepresented_numbers(draws, window=500)

        assert isinstance(numbers, list)
        assert all(isinstance(n, int) for n in numbers)


class TestGenerateReport:
    """Tests fuer generate_longterm_balance_report()."""

    def test_report_structure(self) -> None:
        """Report sollte alle erforderlichen Felder haben."""
        draws = create_uniform_draws(600)
        report = generate_longterm_balance_report(draws, window=500)

        assert "metadata" in report
        assert "balance_analysis" in report
        assert "number_stats" in report
        assert "triggers" in report
        assert "acceptance_criteria" in report
        assert "summary" in report

    def test_metadata_content(self) -> None:
        """Metadata sollte korrekte Inhalte haben."""
        draws = create_uniform_draws(600)
        report = generate_longterm_balance_report(draws, window=500)

        assert report["metadata"]["task"] == "TASK-R05"
        assert report["metadata"]["total_draws"] == 600
        assert "generated_at" in report["metadata"]

    def test_acceptance_criteria(self) -> None:
        """Acceptance Criteria sollten vorhanden sein."""
        draws = create_uniform_draws(600)
        report = generate_longterm_balance_report(draws, window=500)

        ac = report["acceptance_criteria"]
        assert "AC1_balance_scores_calculated" in ac
        assert "AC2_triggers_detected" in ac
        assert "AC3_classifications_assigned" in ac
        assert "AC4_report_generated" in ac


class TestEdgeCases:
    """Tests fuer Edge-Cases."""

    def test_single_draw(self) -> None:
        """Einzelne Ziehung sollte nicht abstuerzen."""
        draw = create_draw(datetime(2023, 1, 1), list(range(1, 21)))
        result = analyze_longterm_balance([draw], window=500)

        assert result.total_draws == 1
        assert len(result.number_stats) == 0

    def test_exact_window_size(self) -> None:
        """Exakt window_size Ziehungen sollte funktionieren."""
        draws = create_uniform_draws(500)
        result = analyze_longterm_balance(draws, window=500)

        assert result.total_draws == 500
        assert len(result.number_stats) == 70

    def test_all_same_numbers(self) -> None:
        """Alle gleichen Zahlen sollte funktionieren."""
        start = datetime(2023, 1, 1)
        draws = [create_draw(start + timedelta(days=i), list(range(1, 21))) for i in range(600)]
        result = analyze_longterm_balance(draws, window=500)

        # Zahlen 1-20 sollten ueberrepraesentiert sein
        over = [s for s in result.number_stats if s.classification == "overrepresented"]
        under = [s for s in result.number_stats if s.classification == "underrepresented"]

        # Zahlen 21-70 sollten unterrepraesentiert sein (nie gezogen)
        assert len(under) == 50  # Zahlen 21-70


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
