"""Unit tests fuer calculate_frequency_per_year()."""

from __future__ import annotations

from datetime import datetime

import pytest

from kenobase.analysis.frequency import (
    YearlyFrequencyResult,
    calculate_frequency_per_year,
)
from kenobase.core.data_loader import DrawResult, GameType


class TestCalculateFrequencyPerYear:
    """Tests fuer calculate_frequency_per_year Funktion."""

    def test_empty_draws_returns_empty_dict(self) -> None:
        """Leere Eingabe gibt leeres Dict zurueck."""
        result = calculate_frequency_per_year([])
        assert result == {}

    def test_single_year_single_draw(self) -> None:
        """Einzelne Ziehung in einem Jahr."""
        draws = [
            DrawResult(
                date=datetime(2023, 5, 15),
                numbers=[1, 2, 3],
                game_type=GameType.KENO,
            ),
        ]
        result = calculate_frequency_per_year(draws)

        assert 2023 in result
        assert len(result) == 1

        year_results = result[2023]
        # Nur 3 Zahlen erschienen
        assert len(year_results) == 3
        assert all(r.year == 2023 for r in year_results)
        assert all(r.total_draws == 1 for r in year_results)
        assert all(r.absolute_frequency == 1 for r in year_results)
        assert all(r.relative_frequency == 1.0 for r in year_results)

    def test_multiple_years(self) -> None:
        """Ziehungen ueber mehrere Jahre."""
        draws = [
            DrawResult(
                date=datetime(2022, 1, 1),
                numbers=[1, 2, 3],
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=[4, 5, 6],
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[7, 8, 9],
                game_type=GameType.KENO,
            ),
        ]
        result = calculate_frequency_per_year(draws)

        assert len(result) == 3
        assert 2022 in result
        assert 2023 in result
        assert 2024 in result

    def test_multiple_draws_same_year(self) -> None:
        """Mehrere Ziehungen im selben Jahr."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=[1, 2, 3],
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2023, 6, 15),
                numbers=[1, 4, 5],
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2023, 12, 31),
                numbers=[1, 6, 7],
                game_type=GameType.KENO,
            ),
        ]
        result = calculate_frequency_per_year(draws)

        assert len(result) == 1
        assert 2023 in result

        year_results = result[2023]
        assert all(r.total_draws == 3 for r in year_results)

        # Zahl 1 erscheint 3x
        num_1 = next(r for r in year_results if r.number == 1)
        assert num_1.absolute_frequency == 3
        assert num_1.relative_frequency == 1.0

        # Andere Zahlen erscheinen je 1x
        for r in year_results:
            if r.number != 1:
                assert r.absolute_frequency == 1
                assert r.relative_frequency == pytest.approx(1 / 3)

    def test_with_number_range(self) -> None:
        """Mit number_range werden alle Zahlen initialisiert."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=[1, 2, 3],
                game_type=GameType.KENO,
            ),
        ]
        result = calculate_frequency_per_year(draws, number_range=(1, 10))

        year_results = result[2023]
        assert len(year_results) == 10  # Zahlen 1-10

        # Zahlen 1,2,3 haben freq 1
        for r in year_results:
            if r.number in [1, 2, 3]:
                assert r.absolute_frequency == 1
            else:
                assert r.absolute_frequency == 0

    def test_invalid_number_range_raises(self) -> None:
        """Ungueltiger number_range wirft ValueError."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=[1, 2, 3],
                game_type=GameType.KENO,
            ),
        ]
        with pytest.raises(ValueError, match="Invalid number_range"):
            calculate_frequency_per_year(draws, number_range=(10, 5))

    def test_keno_full_range(self) -> None:
        """KENO-Bereich 1-70 mit number_range."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=list(range(1, 21)),  # 20 Zahlen
                game_type=GameType.KENO,
            ),
        ]
        result = calculate_frequency_per_year(draws, number_range=(1, 70))

        year_results = result[2023]
        assert len(year_results) == 70

    def test_total_counts_consistency(self) -> None:
        """Summe der Counts muss = total_draws * numbers_per_draw sein."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=list(range(1, 21)),  # 20 Zahlen
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2023, 6, 15),
                numbers=list(range(21, 41)),  # 20 andere Zahlen
                game_type=GameType.KENO,
            ),
        ]
        result = calculate_frequency_per_year(draws, number_range=(1, 70))

        year_results = result[2023]
        total_counts = sum(r.absolute_frequency for r in year_results)
        expected = 2 * 20  # 2 draws * 20 numbers

        assert total_counts == expected

    def test_sorted_by_number(self) -> None:
        """Ergebnisse sind nach Zahl sortiert."""
        draws = [
            DrawResult(
                date=datetime(2023, 1, 1),
                numbers=[70, 1, 35],
                game_type=GameType.KENO,
            ),
        ]
        result = calculate_frequency_per_year(draws)

        year_results = result[2023]
        numbers = [r.number for r in year_results]
        assert numbers == sorted(numbers)


class TestYearlyFrequencyResult:
    """Tests fuer YearlyFrequencyResult dataclass."""

    def test_dataclass_frozen(self) -> None:
        """YearlyFrequencyResult ist immutable."""
        r = YearlyFrequencyResult(
            year=2023,
            number=7,
            absolute_frequency=100,
            relative_frequency=0.5,
            total_draws=200,
        )
        with pytest.raises(AttributeError):
            r.year = 2024  # type: ignore

    def test_dataclass_fields(self) -> None:
        """Alle Felder sind korrekt gesetzt."""
        r = YearlyFrequencyResult(
            year=2023,
            number=7,
            absolute_frequency=100,
            relative_frequency=0.5,
            total_draws=200,
        )
        assert r.year == 2023
        assert r.number == 7
        assert r.absolute_frequency == 100
        assert r.relative_frequency == 0.5
        assert r.total_draws == 200
