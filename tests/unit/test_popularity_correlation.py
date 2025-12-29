"""Unit tests for kenobase.analysis.popularity_correlation module (HYP-004)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from kenobase.analysis.popularity_correlation import (
    BIRTHDAY_NUMBERS,
    SCHOENE_ZAHLEN,
    PopularityResult,
    RollingCorrelationResult,
    aggregate_gq_to_number_popularity,
    analyze_correlation,
    analyze_rolling_correlation,
    calculate_draw_frequency,
    calculate_popularity_scores_heuristic,
    load_gq_popularity,
    run_hyp004_analysis,
)
from kenobase.core.data_loader import DrawResult, GameType


class TestPopularityConstants:
    """Tests for popularity constants."""

    def test_birthday_numbers_range(self):
        """Birthday numbers should be 1-31."""
        assert BIRTHDAY_NUMBERS == set(range(1, 32))
        assert 1 in BIRTHDAY_NUMBERS
        assert 31 in BIRTHDAY_NUMBERS
        assert 32 not in BIRTHDAY_NUMBERS

    def test_schoene_zahlen_defined(self):
        """Schoene Zahlen should be defined."""
        assert len(SCHOENE_ZAHLEN) > 0
        assert 7 in SCHOENE_ZAHLEN
        assert 42 in SCHOENE_ZAHLEN


class TestCalculatePopularityScoresHeuristic:
    """Tests for heuristic popularity calculation."""

    def test_birthday_numbers_get_boost(self):
        """Numbers 1-31 should have higher scores."""
        scores = calculate_popularity_scores_heuristic(range(1, 71))

        # Birthday numbers should have higher average
        birthday_avg = sum(scores[n] for n in BIRTHDAY_NUMBERS) / len(BIRTHDAY_NUMBERS)
        non_birthday_avg = sum(scores[n] for n in range(32, 71)) / (70 - 31)

        assert birthday_avg > non_birthday_avg

    def test_schoene_zahlen_get_boost(self):
        """Schoene Zahlen should have positive scores."""
        scores = calculate_popularity_scores_heuristic(range(1, 71))

        for n in SCHOENE_ZAHLEN:
            if n <= 70:
                assert scores[n] > 0

    def test_scores_normalized(self):
        """All scores should be between 0 and 1."""
        scores = calculate_popularity_scores_heuristic(range(1, 71))

        for score in scores.values():
            assert 0 <= score <= 1


class TestCalculateDrawFrequency:
    """Tests for draw frequency calculation."""

    @pytest.fixture
    def sample_draws(self) -> list[DrawResult]:
        """Create sample draws for testing."""
        return [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 2, 3, 10, 20, 30, 40, 50, 60, 70] + list(range(11, 21)),
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2024, 1, 2),
                numbers=[1, 2, 4, 11, 21, 31, 41, 51, 61, 69] + list(range(12, 22)),
                game_type=GameType.KENO,
            ),
        ]

    def test_empty_draws(self):
        """Empty draws should return empty dict."""
        result = calculate_draw_frequency([])
        assert result == {}

    def test_frequency_calculation(self, sample_draws):
        """Frequencies should be calculated correctly."""
        freq = calculate_draw_frequency(sample_draws)

        # Number 1 appears in both draws
        assert freq[1] == 1.0  # 2/2 = 1.0

        # Number 3 appears in one draw
        assert freq[3] == 0.5  # 1/2 = 0.5

    def test_all_numbers_in_range(self, sample_draws):
        """All numbers in range should be present."""
        freq = calculate_draw_frequency(sample_draws, number_range=(1, 70))

        assert len(freq) == 70
        for n in range(1, 71):
            assert n in freq


class TestAnalyzeCorrelation:
    """Tests for correlation analysis."""

    def test_perfect_negative_correlation(self):
        """Perfect negative correlation should return r close to -1."""
        # Need at least 10 data points
        popularity = {i: i / 20.0 for i in range(1, 21)}
        frequency = {i: 1 - (i / 20.0) for i in range(1, 21)}

        result = analyze_correlation(popularity, frequency)

        assert result.correlation < -0.9
        assert result.method == "spearman"

    def test_constant_input_handled(self):
        """Constant frequency should be handled gracefully."""
        popularity = {i: i / 70.0 for i in range(1, 71)}
        frequency = {i: 0.5 for i in range(1, 71)}  # All same frequency

        result = analyze_correlation(popularity, frequency)

        # Constant input should return method="constant_input"
        assert result.method == "constant_input"
        assert result.correlation == 0.0

    def test_insufficient_data(self):
        """Should handle insufficient data gracefully."""
        popularity = {1: 1.0, 2: 0.5}
        frequency = {1: 0.5, 2: 1.0}

        result = analyze_correlation(popularity, frequency)

        assert result.n_samples < 10
        assert result.method == "insufficient"

    def test_supports_hypothesis(self):
        """Should correctly identify when hypothesis is supported."""
        # Create data with strong negative correlation
        popularity = {i: i / 70.0 for i in range(1, 71)}
        frequency = {i: 1 - (i / 70.0) for i in range(1, 71)}

        result = analyze_correlation(popularity, frequency)

        if result.correlation < -0.2 and result.p_value < 0.05:
            assert result.supports_hypothesis


class TestRollingCorrelation:
    """Tests for rolling window correlation."""

    @pytest.fixture
    def many_draws(self) -> list[DrawResult]:
        """Create many draws for rolling window tests."""
        import random

        random.seed(42)
        draws = []
        for i in range(100):
            numbers = sorted(random.sample(range(1, 71), 20))
            draws.append(
                DrawResult(
                    date=datetime(2024, 1, 1 + i % 28, hour=i // 28),
                    numbers=numbers,
                    game_type=GameType.KENO,
                )
            )
        return draws

    def test_rolling_window_count(self, many_draws):
        """Should return correct number of windows."""
        popularity = calculate_popularity_scores_heuristic(range(1, 71))
        results = analyze_rolling_correlation(many_draws, popularity, window=30)

        expected_windows = len(many_draws) - 30 + 1
        assert len(results) == expected_windows

    def test_insufficient_data_for_window(self):
        """Should return empty list if not enough draws."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, i),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            )
            for i in range(1, 10)
        ]
        popularity = calculate_popularity_scores_heuristic(range(1, 71))

        results = analyze_rolling_correlation(draws, popularity, window=30)

        assert len(results) == 0

    def test_rolling_result_structure(self, many_draws):
        """Each result should have correct structure."""
        popularity = calculate_popularity_scores_heuristic(range(1, 71))
        results = analyze_rolling_correlation(many_draws, popularity, window=30)

        for r in results:
            assert isinstance(r, RollingCorrelationResult)
            assert isinstance(r.date, datetime)
            assert -1 <= r.correlation <= 1
            assert 0 <= r.p_value <= 1
            assert r.window_size == 30


class TestRunHyp004Analysis:
    """Tests for the complete HYP-004 analysis."""

    @pytest.fixture
    def sample_draws(self) -> list[DrawResult]:
        """Create sample draws."""
        import random

        random.seed(42)
        return [
            DrawResult(
                date=datetime(2024, 1, i % 28 + 1),
                numbers=sorted(random.sample(range(1, 71), 20)),
                game_type=GameType.KENO,
            )
            for i in range(50)
        ]

    def test_uses_heuristic_when_no_gq(self, sample_draws):
        """Should use heuristic when GQ path is None."""
        results = run_hyp004_analysis(sample_draws, gq_path=None, window=10)

        assert results["summary"]["method"] == "heuristic"
        assert "overall" in results
        assert "rolling" in results

    def test_result_structure(self, sample_draws):
        """Should return correct result structure."""
        results = run_hyp004_analysis(sample_draws, gq_path=None, window=10)

        assert "overall" in results
        assert "rolling" in results
        assert "summary" in results
        assert "popularity_scores" in results
        assert "draw_frequencies" in results

        assert isinstance(results["overall"], PopularityResult)
        assert isinstance(results["rolling"], list)
        assert isinstance(results["summary"], dict)

    def test_summary_contains_expected_keys(self, sample_draws):
        """Summary should contain expected statistics."""
        results = run_hyp004_analysis(sample_draws, gq_path=None, window=10)
        summary = results["summary"]

        expected_keys = ["method", "n_draws", "n_windows", "window_size"]
        for key in expected_keys:
            assert key in summary


class TestLoadGQPopularity:
    """Tests for GQ data loading."""

    def test_file_not_found(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_gq_popularity("nonexistent_file.csv")


class TestAggregateGQToNumberPopularity:
    """Tests for GQ aggregation."""

    def test_empty_inputs(self):
        """Should handle empty inputs."""
        result = aggregate_gq_to_number_popularity({}, [])
        assert result == {}

    def test_no_matching_dates(self):
        """Should handle when no dates match."""
        gq_data = {datetime(2024, 1, 1): {10: 100.0}}
        draws = [
            DrawResult(
                date=datetime(2024, 2, 1),  # Different month
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            )
        ]

        result = aggregate_gq_to_number_popularity(gq_data, draws)
        assert all(v == 0.0 for v in result.values()) or len(result) == 0


class TestCalculateBirthdayScore:
    """Tests for birthday score calculation."""

    def test_all_birthday_numbers(self):
        """All numbers 1-31 should give score 1.0."""
        from kenobase.analysis.popularity_correlation import calculate_birthday_score

        numbers = list(range(1, 21))  # All < 31
        score = calculate_birthday_score(numbers)
        assert score == 1.0

    def test_no_birthday_numbers(self):
        """All numbers 32-70 should give score 0.0."""
        from kenobase.analysis.popularity_correlation import calculate_birthday_score

        numbers = list(range(50, 70))  # All >= 32
        score = calculate_birthday_score(numbers)
        assert score == 0.0

    def test_half_birthday_numbers(self):
        """Mixed numbers should give proportional score."""
        from kenobase.analysis.popularity_correlation import calculate_birthday_score

        numbers = [1, 2, 3, 4, 5, 50, 51, 52, 53, 54]  # 5 birthday, 5 non-birthday
        score = calculate_birthday_score(numbers)
        assert score == 0.5

    def test_empty_list(self):
        """Empty list should return 0.0."""
        from kenobase.analysis.popularity_correlation import calculate_birthday_score

        score = calculate_birthday_score([])
        assert score == 0.0

    def test_typical_keno_draw(self):
        """Typical KENO draw should have ~44% birthday numbers."""
        from kenobase.analysis.popularity_correlation import calculate_birthday_score

        # 20 numbers: 8 birthday (1-31), 12 non-birthday
        numbers = [1, 5, 10, 15, 20, 25, 30, 31, 40, 45, 50, 55, 60, 65, 66, 67, 68, 69, 70, 35]
        score = calculate_birthday_score(numbers)
        # 8 birthday numbers out of 20 = 0.4
        assert 0.3 <= score <= 0.5


class TestCorrelateBirthdayWithWinners:
    """Tests for birthday-winners correlation."""

    def test_empty_draws(self):
        """Should handle empty draws."""
        from kenobase.analysis.popularity_correlation import (
            BirthdayCorrelationResult,
            correlate_birthday_with_winners,
        )

        result = correlate_birthday_with_winners([], {})
        assert result["overall"].n_samples == 0
        assert "error" in result["summary"]

    def test_empty_gq_data(self):
        """Should handle empty GQ data."""
        from kenobase.analysis.popularity_correlation import correlate_birthday_with_winners

        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            )
        ]
        result = correlate_birthday_with_winners(draws, {})
        assert result["overall"].n_samples == 0

    def test_no_matching_dates(self):
        """Should handle when no dates match."""
        from kenobase.analysis.popularity_correlation import correlate_birthday_with_winners

        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            )
        ]
        gq_data = {datetime(2024, 2, 1): {10: 100.0}}

        result = correlate_birthday_with_winners(draws, gq_data)
        # No paired data should result in insufficient samples
        assert result["overall"].n_samples == 0

    def test_positive_correlation_detected(self):
        """Should detect positive correlation when present."""
        from kenobase.analysis.popularity_correlation import correlate_birthday_with_winners

        # Create synthetic data: high birthday score -> high winners
        draws = []
        gq_data = {}

        for i in range(50):
            date = datetime(2024, 1, 1 + i % 28, hour=i // 28)
            # Alternate between high and low birthday scores
            if i % 2 == 0:
                # High birthday score (all 1-20)
                numbers = list(range(1, 21))
                winners = 1000.0 + i * 10  # More winners
            else:
                # Low birthday score (all 50-69)
                numbers = list(range(50, 70))
                winners = 100.0 + i  # Fewer winners

            draws.append(
                DrawResult(
                    date=date,
                    numbers=numbers,
                    game_type=GameType.KENO,
                )
            )
            gq_data[date.replace(hour=0)] = {10: winners}

        result = correlate_birthday_with_winners(draws, gq_data, window=10)

        # Should have paired data
        assert result["overall"].n_samples >= 10
        # Correlation should be positive (high birthday -> high winners)
        assert result["overall"].correlation > 0

    def test_result_structure(self):
        """Should return correct result structure."""
        from kenobase.analysis.popularity_correlation import (
            BirthdayCorrelationResult,
            correlate_birthday_with_winners,
        )

        draws = [
            DrawResult(
                date=datetime(2024, 1, 1 + i % 28, hour=i // 28),
                numbers=list(range(1, 21)),
                game_type=GameType.KENO,
            )
            for i in range(50)
        ]
        gq_data = {datetime(2024, 1, 1 + i % 28): {10: 100.0 + i} for i in range(28)}

        result = correlate_birthday_with_winners(draws, gq_data, window=10)

        assert "overall" in result
        assert "rolling" in result
        assert "summary" in result
        assert isinstance(result["overall"], BirthdayCorrelationResult)
