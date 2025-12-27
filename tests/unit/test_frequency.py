"""Unit tests fuer kenobase.analysis.frequency.

Coverage-Ziel: >= 80%
Testfaelle:
- Leere Listen
- Einzelne Ziehung
- Mehrere Ziehungen
- Hot/Cold-Klassifikation
- Rolling Windows
- Edge Cases (Division by Zero, ungueltige Parameter)
"""

from datetime import datetime

import pytest

from kenobase.analysis.frequency import (
    FrequencyResult,
    PairFrequencyResult,
    calculate_frequency,
    calculate_pair_frequency,
    calculate_rolling_frequency,
    classify_numbers,
    classify_pairs,
    get_cold_numbers,
    get_hot_numbers,
)
from kenobase.core.data_loader import DrawResult, GameType


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def single_draw() -> list[DrawResult]:
    """Einzelne Ziehung mit Zahlen 1, 2, 3."""
    return [
        DrawResult(
            date=datetime(2024, 1, 1),
            numbers=[1, 2, 3],
            game_type=GameType.KENO,
        )
    ]


@pytest.fixture
def multiple_draws() -> list[DrawResult]:
    """Mehrere Ziehungen fuer Frequenztest.

    Zahl 1: 3x (100%)
    Zahl 2: 2x (66.7%)
    Zahl 3: 1x (33.3%)
    Zahl 4: 1x (33.3%)
    Zahl 5: 1x (33.3%)
    """
    return [
        DrawResult(
            date=datetime(2024, 1, 1),
            numbers=[1, 2, 3],
            game_type=GameType.KENO,
        ),
        DrawResult(
            date=datetime(2024, 1, 2),
            numbers=[1, 2, 4],
            game_type=GameType.KENO,
        ),
        DrawResult(
            date=datetime(2024, 1, 3),
            numbers=[1, 5, 6],
            game_type=GameType.KENO,
        ),
    ]


@pytest.fixture
def draws_for_rolling() -> list[DrawResult]:
    """5 Ziehungen fuer Rolling-Window-Test."""
    return [
        DrawResult(
            date=datetime(2024, 1, i + 1),
            numbers=[1, 2, 3] if i % 2 == 0 else [4, 5, 6],
            game_type=GameType.KENO,
        )
        for i in range(5)
    ]


# =============================================================================
# Test: calculate_frequency
# =============================================================================


class TestCalculateFrequency:
    """Tests fuer calculate_frequency."""

    def test_empty_list_returns_empty(self) -> None:
        """Leere Eingabe gibt leere Liste zurueck."""
        result = calculate_frequency([])
        assert result == []

    def test_single_draw_counts_correctly(self, single_draw: list[DrawResult]) -> None:
        """Einzelne Ziehung zaehlt alle Zahlen als 1."""
        results = calculate_frequency(single_draw)

        assert len(results) == 3
        for r in results:
            assert r.absolute_frequency == 1
            assert r.relative_frequency == 1.0

    def test_multiple_draws_counts_correctly(
        self, multiple_draws: list[DrawResult]
    ) -> None:
        """Mehrere Ziehungen werden korrekt gezaehlt."""
        results = calculate_frequency(multiple_draws)

        # Finde Zahl 1 (sollte 3x vorkommen)
        freq_1 = next(r for r in results if r.number == 1)
        assert freq_1.absolute_frequency == 3
        assert freq_1.relative_frequency == 1.0  # 3/3 = 100%

        # Finde Zahl 2 (sollte 2x vorkommen)
        freq_2 = next(r for r in results if r.number == 2)
        assert freq_2.absolute_frequency == 2
        assert abs(freq_2.relative_frequency - 2 / 3) < 0.001

    def test_results_sorted_by_number(
        self, multiple_draws: list[DrawResult]
    ) -> None:
        """Ergebnisse sind nach Zahl sortiert."""
        results = calculate_frequency(multiple_draws)
        numbers = [r.number for r in results]
        assert numbers == sorted(numbers)

    def test_with_number_range_initializes_zeros(self) -> None:
        """number_range initialisiert fehlende Zahlen mit 0."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 3, 5],
                game_type=GameType.KENO,
            )
        ]
        results = calculate_frequency(draws, number_range=(1, 5))

        assert len(results) == 5  # 1, 2, 3, 4, 5

        # Zahl 2 und 4 sollten 0 sein
        freq_2 = next(r for r in results if r.number == 2)
        assert freq_2.absolute_frequency == 0
        assert freq_2.relative_frequency == 0.0

    def test_invalid_number_range_raises(self) -> None:
        """Ungueltige number_range wirft ValueError."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 2, 3],
                game_type=GameType.KENO,
            )
        ]
        with pytest.raises(ValueError, match="Invalid number_range"):
            calculate_frequency(draws, number_range=(10, 5))


# =============================================================================
# Test: calculate_pair_frequency
# =============================================================================


class TestCalculatePairFrequency:
    """Tests fuer calculate_pair_frequency."""

    def test_empty_list_returns_empty(self) -> None:
        """Leere Eingabe gibt leere Liste zurueck."""
        result = calculate_pair_frequency([])
        assert result == []

    def test_single_draw_creates_all_pairs(
        self, single_draw: list[DrawResult]
    ) -> None:
        """Einzelne Ziehung [1,2,3] erstellt Paare (1,2), (1,3), (2,3)."""
        results = calculate_pair_frequency(single_draw)

        assert len(results) == 3
        pairs = {r.pair for r in results}
        assert pairs == {(1, 2), (1, 3), (2, 3)}

    def test_multiple_draws_counts_correctly(
        self, multiple_draws: list[DrawResult]
    ) -> None:
        """Paar (1,2) erscheint in 2 von 3 Ziehungen."""
        results = calculate_pair_frequency(multiple_draws)

        # Finde Paar (1, 2) - kommt in Draw 1 und 2 vor
        pair_12 = next(r for r in results if r.pair == (1, 2))
        assert pair_12.absolute_frequency == 2
        assert abs(pair_12.relative_frequency - 2 / 3) < 0.001

    def test_results_sorted_by_frequency_descending(
        self, multiple_draws: list[DrawResult]
    ) -> None:
        """Ergebnisse sind nach Frequenz (absteigend) sortiert."""
        results = calculate_pair_frequency(multiple_draws)
        frequencies = [r.absolute_frequency for r in results]
        assert frequencies == sorted(frequencies, reverse=True)

    def test_pairs_are_sorted_internally(self) -> None:
        """Paare sind intern sortiert (kleinere Zahl zuerst)."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[5, 2, 8],  # Nicht sortiert
                game_type=GameType.KENO,
            )
        ]
        results = calculate_pair_frequency(draws)

        for r in results:
            assert r.pair[0] < r.pair[1]


# =============================================================================
# Test: classify_numbers
# =============================================================================


class TestClassifyNumbers:
    """Tests fuer classify_numbers."""

    def test_hot_classification(self) -> None:
        """Zahlen >= hot_threshold werden als 'hot' klassifiziert."""
        freq_results = [
            FrequencyResult(number=1, absolute_frequency=10, relative_frequency=0.25, classification="normal"),
        ]
        classified = classify_numbers(freq_results, hot_threshold=0.20, cold_threshold=0.05)

        assert classified[0].classification == "hot"

    def test_cold_classification(self) -> None:
        """Zahlen <= cold_threshold werden als 'cold' klassifiziert."""
        freq_results = [
            FrequencyResult(number=1, absolute_frequency=1, relative_frequency=0.03, classification="normal"),
        ]
        classified = classify_numbers(freq_results, hot_threshold=0.20, cold_threshold=0.05)

        assert classified[0].classification == "cold"

    def test_normal_classification(self) -> None:
        """Zahlen zwischen Thresholds werden als 'normal' klassifiziert."""
        freq_results = [
            FrequencyResult(number=1, absolute_frequency=5, relative_frequency=0.10, classification="normal"),
        ]
        classified = classify_numbers(freq_results, hot_threshold=0.20, cold_threshold=0.05)

        assert classified[0].classification == "normal"

    def test_invalid_thresholds_raises(self) -> None:
        """hot_threshold <= cold_threshold wirft ValueError."""
        freq_results = [
            FrequencyResult(number=1, absolute_frequency=5, relative_frequency=0.10, classification="normal"),
        ]
        with pytest.raises(ValueError, match="hot_threshold"):
            classify_numbers(freq_results, hot_threshold=0.05, cold_threshold=0.10)

    def test_returns_new_list(self) -> None:
        """classify_numbers gibt neue Liste zurueck, aendert Original nicht."""
        freq_results = [
            FrequencyResult(number=1, absolute_frequency=10, relative_frequency=0.25, classification="normal"),
        ]
        classified = classify_numbers(freq_results, hot_threshold=0.20, cold_threshold=0.05)

        assert classified is not freq_results
        assert freq_results[0].classification == "normal"
        assert classified[0].classification == "hot"


# =============================================================================
# Test: classify_pairs
# =============================================================================


class TestClassifyPairs:
    """Tests fuer classify_pairs."""

    def test_hot_pair_classification(self) -> None:
        """Paare >= hot_threshold werden als 'hot' klassifiziert."""
        pair_results = [
            PairFrequencyResult(pair=(1, 2), absolute_frequency=5, relative_frequency=0.15, classification="normal"),
        ]
        classified = classify_pairs(pair_results, hot_threshold=0.10, cold_threshold=0.01)

        assert classified[0].classification == "hot"

    def test_cold_pair_classification(self) -> None:
        """Paare <= cold_threshold werden als 'cold' klassifiziert."""
        pair_results = [
            PairFrequencyResult(pair=(1, 2), absolute_frequency=1, relative_frequency=0.005, classification="normal"),
        ]
        classified = classify_pairs(pair_results, hot_threshold=0.10, cold_threshold=0.01)

        assert classified[0].classification == "cold"

    def test_invalid_thresholds_raises(self) -> None:
        """hot_threshold <= cold_threshold wirft ValueError."""
        pair_results = [
            PairFrequencyResult(pair=(1, 2), absolute_frequency=5, relative_frequency=0.05, classification="normal"),
        ]
        with pytest.raises(ValueError, match="hot_threshold"):
            classify_pairs(pair_results, hot_threshold=0.01, cold_threshold=0.10)


# =============================================================================
# Test: calculate_rolling_frequency
# =============================================================================


class TestCalculateRollingFrequency:
    """Tests fuer calculate_rolling_frequency."""

    def test_empty_list_returns_empty(self) -> None:
        """Leere Eingabe gibt leere Liste zurueck."""
        result = calculate_rolling_frequency([], window=5, number=1)
        assert result == []

    def test_window_larger_than_draws_returns_empty(
        self, single_draw: list[DrawResult]
    ) -> None:
        """Window groesser als Anzahl Ziehungen gibt leere Liste."""
        result = calculate_rolling_frequency(single_draw, window=10, number=1)
        assert result == []

    def test_invalid_window_raises(self, single_draw: list[DrawResult]) -> None:
        """Window < 1 wirft ValueError."""
        with pytest.raises(ValueError, match="window must be >= 1"):
            calculate_rolling_frequency(single_draw, window=0, number=1)

    def test_rolling_calculation(
        self, draws_for_rolling: list[DrawResult]
    ) -> None:
        """Rolling-Frequenz wird korrekt berechnet.

        draws_for_rolling: [1,2,3], [4,5,6], [1,2,3], [4,5,6], [1,2,3]
        Window=3 fuer Zahl 1:
        - [0:3] -> 2/3 = 0.667 (Zahl 1 in Index 0, 2)
        - [1:4] -> 1/3 = 0.333 (Zahl 1 in Index 2)
        - [2:5] -> 2/3 = 0.667 (Zahl 1 in Index 2, 4)
        """
        freqs = calculate_rolling_frequency(draws_for_rolling, window=3, number=1)

        assert len(freqs) == 3  # 5 - 3 + 1 = 3
        assert abs(freqs[0] - 2 / 3) < 0.001
        assert abs(freqs[1] - 1 / 3) < 0.001
        assert abs(freqs[2] - 2 / 3) < 0.001

    def test_number_not_in_any_draw(
        self, draws_for_rolling: list[DrawResult]
    ) -> None:
        """Zahl die nie vorkommt hat Frequenz 0."""
        freqs = calculate_rolling_frequency(draws_for_rolling, window=3, number=99)

        assert all(f == 0.0 for f in freqs)


# =============================================================================
# Test: Convenience Functions
# =============================================================================


class TestConvenienceFunctions:
    """Tests fuer get_hot_numbers und get_cold_numbers."""

    def test_get_hot_numbers(self, multiple_draws: list[DrawResult]) -> None:
        """get_hot_numbers gibt nur hot Zahlen zurueck."""
        # Zahl 1 hat 100% Frequenz, sollte hot sein bei Threshold 0.20
        hot = get_hot_numbers(multiple_draws, hot_threshold=0.20, cold_threshold=0.05)

        assert 1 in hot
        assert len(hot) >= 1

    def test_get_cold_numbers(self) -> None:
        """get_cold_numbers gibt nur cold Zahlen zurueck."""
        from datetime import timedelta

        base_date = datetime(2024, 1, 1)
        draws = [
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=[1, 2, 3],
                game_type=GameType.KENO,
            )
            for i in range(100)
        ]
        # Mit number_range (1, 10) haben 4-10 Frequenz 0
        cold = get_cold_numbers(
            draws,
            hot_threshold=0.20,
            cold_threshold=0.05,
            number_range=(1, 10),
        )

        assert 4 in cold
        assert 10 in cold
        assert 1 not in cold  # 1 hat 100% Frequenz


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests fuer Randfaelle."""

    def test_single_number_draw(self) -> None:
        """Ziehung mit nur einer Zahl."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[42],
                game_type=GameType.KENO,
            )
        ]
        freq_results = calculate_frequency(draws)
        pair_results = calculate_pair_frequency(draws)

        assert len(freq_results) == 1
        assert freq_results[0].number == 42
        assert len(pair_results) == 0  # Keine Paare bei einzelner Zahl

    def test_duplicate_numbers_in_draw(self) -> None:
        """Ziehung mit duplizierten Zahlen (sollte nicht vorkommen, aber robust sein).

        DrawResult.numbers wird vom Validator sortiert, Duplikate bleiben erhalten.
        """
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 1, 2],  # Duplikat
                game_type=GameType.KENO,
            )
        ]
        freq_results = calculate_frequency(draws)

        # Zahl 1 wird 2x gezaehlt
        freq_1 = next(r for r in freq_results if r.number == 1)
        assert freq_1.absolute_frequency == 2

    def test_large_number_range(self) -> None:
        """Grosser Zahlenbereich (1-70 fuer KENO)."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=list(range(1, 21)),  # 20 Zahlen
                game_type=GameType.KENO,
            )
        ]
        freq_results = calculate_frequency(draws, number_range=(1, 70))

        assert len(freq_results) == 70
        # Zahlen 21-70 haben Frequenz 0
        freq_50 = next(r for r in freq_results if r.number == 50)
        assert freq_50.absolute_frequency == 0
