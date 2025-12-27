"""Unit tests for NumberPoolGenerator.

Tests fuer kenobase/core/number_pool.py.
Prueft Zahlenpool-Generierung mit synthetischen Testdaten.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

import pytest

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.core.number_pool import NumberPoolGenerator, PeriodAnalysis


def create_test_draw(
    numbers: list[int],
    days_offset: int = 0,
) -> DrawResult:
    """Erstellt Test-DrawResult.

    Args:
        numbers: Liste von Zahlen (werden sortiert)
        days_offset: Tage relativ zu Basisdatum

    Returns:
        DrawResult-Objekt
    """
    base_date = datetime(2024, 1, 1)
    return DrawResult(
        date=base_date + timedelta(days=days_offset),
        numbers=numbers,
        bonus=[],
        game_type=GameType.KENO,
    )


def create_test_draws(n_draws: int, pattern: str = "sequential") -> list[DrawResult]:
    """Erstellt Liste von Test-Ziehungen.

    Args:
        n_draws: Anzahl Ziehungen
        pattern: "sequential" (1-20, 2-21, ...) oder "fixed" (immer 1-20)

    Returns:
        Liste von DrawResult-Objekten
    """
    draws = []
    for i in range(n_draws):
        if pattern == "sequential":
            # Jede Ziehung: 20 aufeinanderfolgende Zahlen, verschoben
            start = (i % 51) + 1  # 1-51 damit max 70 nicht ueberschritten
            numbers = list(range(start, start + 20))
        else:  # fixed
            numbers = list(range(1, 21))

        draws.append(create_test_draw(numbers, days_offset=i))
    return draws


class TestNumberPoolGeneratorInit:
    """Tests fuer NumberPoolGenerator Initialisierung."""

    def test_default_parameters(self):
        """Test Standard-Parameter."""
        generator = NumberPoolGenerator()

        assert generator.n_periods == 3
        assert generator.draws_per_period == 10
        assert generator.top_n_per_period == 11
        assert generator.top_n_total == 20

    def test_custom_parameters(self):
        """Test benutzerdefinierte Parameter."""
        generator = NumberPoolGenerator(
            n_periods=5,
            draws_per_period=8,
            top_n_per_period=15,
            top_n_total=30,
        )

        assert generator.n_periods == 5
        assert generator.draws_per_period == 8
        assert generator.top_n_per_period == 15
        assert generator.top_n_total == 30


class TestNumberPoolGeneratorGenerate:
    """Tests fuer generate() Methode."""

    def test_generate_returns_set(self):
        """Test dass generate() ein Set zurueckgibt."""
        draws = create_test_draws(30, pattern="fixed")
        generator = NumberPoolGenerator()

        pool = generator.generate(draws)

        assert isinstance(pool, set)
        assert all(isinstance(n, int) for n in pool)

    def test_generate_insufficient_draws_raises(self):
        """Test dass bei zu wenig Ziehungen ValueError geworfen wird."""
        draws = create_test_draws(20)  # Braucht 30
        generator = NumberPoolGenerator()

        with pytest.raises(ValueError, match="Need at least 30 draws"):
            generator.generate(draws)

    def test_generate_with_fixed_pattern(self):
        """Test mit fixen Zahlen (alle Ziehungen gleich)."""
        # Alle Ziehungen haben Zahlen 1-20
        draws = create_test_draws(30, pattern="fixed")
        generator = NumberPoolGenerator()

        pool = generator.generate(draws)

        # Bei gleichen Zahlen sollten alle Top-11 identisch sein
        # und die Schnittmenge sollte diese enthalten
        assert len(pool) > 0
        # Die haeufigsten Zahlen sind 1-20 (alle gleich haeufig)
        # Top-11 wuerden 11 davon sein (je nach Sortierung)

    def test_generate_pool_contains_frequent_numbers(self):
        """Test dass Pool haeufige Zahlen enthaelt."""
        # Konstruiere Ziehungen wo bestimmte Zahlen sehr haeufig sind
        draws = []
        for i in range(30):
            # Zahlen 1-10 erscheinen in jeder Ziehung
            # Zahlen 11-20 nur in manchen
            if i < 15:
                numbers = list(range(1, 21))
            else:
                numbers = list(range(1, 11)) + list(range(21, 31))
            draws.append(create_test_draw(numbers, days_offset=i))

        generator = NumberPoolGenerator()
        pool = generator.generate(draws)

        # Zahlen 1-10 sollten im Pool sein (sehr haeufig)
        for num in range(1, 11):
            assert num in pool, f"Zahl {num} sollte im Pool sein"


class TestGetTopN:
    """Tests fuer get_top_n() Methode."""

    def test_get_top_n_returns_correct_count(self):
        """Test dass korrekte Anzahl Top-Zahlen zurueckgegeben wird."""
        draws = create_test_draws(30, pattern="fixed")
        generator = NumberPoolGenerator()

        top_10 = generator.get_top_n(draws, 10)

        assert len(top_10) == 10

    def test_get_top_n_returns_most_frequent(self):
        """Test dass haeufigste Zahlen zurueckgegeben werden."""
        # Erstelle Ziehungen wo 1,2,3 am haeufigsten sind
        draws = []
        for i in range(10):
            # 1,2,3 in jeder Ziehung, andere variieren
            numbers = [1, 2, 3] + list(range(4 + i, 21 + i))
            numbers = [n for n in numbers if n <= 70][:20]
            draws.append(create_test_draw(numbers, days_offset=i))

        generator = NumberPoolGenerator()
        top_5 = generator.get_top_n(draws, 5)

        # 1, 2, 3 sollten enthalten sein
        assert 1 in top_5
        assert 2 in top_5
        assert 3 in top_5


class TestGetIntersections:
    """Tests fuer get_intersections() Methode."""

    def test_intersections_empty_for_disjoint_sets(self):
        """Test leere Schnittmenge bei disjunkten Sets."""
        generator = NumberPoolGenerator()
        sets = [{1, 2, 3}, {4, 5, 6}, {7, 8, 9}]

        result = generator.get_intersections(sets)

        assert result == set()

    def test_intersections_correct_for_overlapping_sets(self):
        """Test korrekte Schnittmenge bei ueberlappenden Sets."""
        generator = NumberPoolGenerator()
        sets = [{1, 2, 3}, {2, 3, 4}, {3, 4, 5}]

        result = generator.get_intersections(sets)

        # Paarweise: {1,2,3}&{2,3,4}={2,3}, {1,2,3}&{3,4,5}={3}, {2,3,4}&{3,4,5}={3,4}
        # Union: {2,3,4}
        assert result == {2, 3, 4}

    def test_intersections_single_set_returns_empty(self):
        """Test leere Rueckgabe bei nur einem Set."""
        generator = NumberPoolGenerator()

        result = generator.get_intersections([{1, 2, 3}])

        assert result == set()

    def test_intersections_empty_input(self):
        """Test leere Eingabe."""
        generator = NumberPoolGenerator()

        result = generator.get_intersections([])

        assert result == set()


class TestFromDraws:
    """Tests fuer from_draws() Factory-Methode."""

    def test_from_draws_produces_same_as_generate(self):
        """Test dass from_draws() gleiches Ergebnis wie generate() liefert."""
        draws = create_test_draws(30, pattern="fixed")

        # Via generate
        generator = NumberPoolGenerator()
        pool1 = generator.generate(draws)

        # Via from_draws
        pool2 = NumberPoolGenerator.from_draws(draws)

        assert pool1 == pool2

    def test_from_draws_with_custom_parameters(self):
        """Test from_draws() mit benutzerdefinierten Parametern."""
        draws = create_test_draws(50, pattern="fixed")

        pool = NumberPoolGenerator.from_draws(
            draws,
            n_periods=5,
            draws_per_period=10,
            top_n_per_period=8,
            top_n_total=15,
        )

        assert isinstance(pool, set)


class TestPeriodAnalysis:
    """Tests fuer PeriodAnalysis Dataclass."""

    def test_period_analysis_creation(self):
        """Test PeriodAnalysis Erstellung."""
        counts = Counter({1: 10, 2: 8, 3: 5})
        analysis = PeriodAnalysis(
            period_name="Test",
            frequency_counts=counts,
            top_n={1, 2, 3},
        )

        assert analysis.period_name == "Test"
        assert analysis.frequency_counts[1] == 10
        assert analysis.top_n == {1, 2, 3}


class TestEdgeCases:
    """Tests fuer Randfaelle."""

    def test_minimum_draws_exactly(self):
        """Test mit exakt der Mindestzahl an Ziehungen."""
        draws = create_test_draws(30, pattern="fixed")  # Exakt 3*10
        generator = NumberPoolGenerator()

        pool = generator.generate(draws)

        assert isinstance(pool, set)

    def test_more_draws_than_needed(self):
        """Test mit mehr Ziehungen als benoetigt."""
        draws = create_test_draws(100, pattern="sequential")
        generator = NumberPoolGenerator()

        pool = generator.generate(draws)

        # Nur die ersten 30 werden verwendet
        assert isinstance(pool, set)
        assert len(pool) > 0

    def test_all_same_number_in_pool(self):
        """Test wenn eine Zahl in allen Ziehungen vorkommt."""
        draws = []
        for i in range(30):
            # Zahl 42 immer dabei, andere Zahlen variieren
            # So ist 42 haeufiger als die meisten anderen
            base_numbers = [42]
            # Variierende Zahlen: i mod sorgt fuer Variation
            varying = list(range(1 + (i % 10), 20 + (i % 10)))
            numbers = base_numbers + varying[:19]
            draws.append(create_test_draw(numbers, days_offset=i))

        generator = NumberPoolGenerator()
        pool = generator.generate(draws)

        # 42 sollte definitiv im Pool sein (erscheint 30x, andere weniger)
        assert 42 in pool
