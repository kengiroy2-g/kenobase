"""Unit tests for stable_numbers.py - Core Stable Numbers Analysis (Model Law A).

Tests the stability calculation and analysis functions.
Stability formula: stability_score = 1 - (std / mean)
A number is stable if stability_score >= threshold (default 0.90)
"""

from datetime import datetime, timedelta

import pytest

from kenobase.analysis.stable_numbers import (
    StableNumberResult,
    analyze_stable_numbers,
    calculate_stability_score,
    get_stable_numbers,
)
from kenobase.core.data_loader import DrawResult, GameType


def create_draw(date: datetime, numbers: list[int]) -> DrawResult:
    """Helper to create DrawResult for testing."""
    return DrawResult(
        date=date,
        numbers=numbers,
        bonus=[],
        game_type=GameType.KENO,
        metadata={},
    )


class TestCalculateStabilityScore:
    """Tests for calculate_stability_score function."""

    def test_perfect_stability(self):
        """Constant frequencies should yield stability = 1.0."""
        freqs = [0.25, 0.25, 0.25, 0.25, 0.25]
        score, mean, std = calculate_stability_score(freqs)
        assert score == 1.0
        assert mean == 0.25
        assert std == 0.0

    def test_high_stability(self):
        """Low variance should yield high stability."""
        freqs = [0.25, 0.26, 0.24, 0.25, 0.25]
        score, mean, std = calculate_stability_score(freqs)
        assert score > 0.9
        assert 0.24 < mean < 0.26

    def test_low_stability(self):
        """High variance should yield low stability."""
        freqs = [0.1, 0.5, 0.1, 0.5, 0.1]
        score, mean, std = calculate_stability_score(freqs)
        assert score < 0.5

    def test_zero_mean(self):
        """Zero mean (number never appears) should yield stability = 0."""
        freqs = [0.0, 0.0, 0.0, 0.0, 0.0]
        score, mean, std = calculate_stability_score(freqs)
        assert score == 0.0
        assert mean == 0.0

    def test_empty_input(self):
        """Empty input should yield stability = 0."""
        score, mean, std = calculate_stability_score([])
        assert score == 0.0
        assert mean == 0.0
        assert std == 0.0

    def test_single_value(self):
        """Single value should yield stability = 1.0 (no variance)."""
        freqs = [0.3]
        score, mean, std = calculate_stability_score(freqs)
        assert score == 1.0
        assert mean == 0.3

    def test_stability_clamped_to_0_1(self):
        """Stability should be clamped to [0, 1] range."""
        # Very high variance relative to mean could theoretically give negative
        freqs = [0.01, 0.99, 0.01, 0.99]
        score, mean, std = calculate_stability_score(freqs)
        assert 0.0 <= score <= 1.0


class TestAnalyzeStableNumbers:
    """Tests for analyze_stable_numbers function."""

    def test_empty_draws(self):
        """Empty draws should return empty results."""
        results = analyze_stable_numbers([], window=10)
        assert results == []

    def test_insufficient_draws(self):
        """Fewer draws than window should return empty results."""
        draws = [create_draw(datetime(2024, 1, i + 1), [1, 2, 3]) for i in range(5)]
        results = analyze_stable_numbers(draws, window=10)
        assert results == []

    def test_invalid_window(self):
        """Window < 1 should raise ValueError."""
        draws = [create_draw(datetime(2024, 1, i + 1), [1, 2, 3]) for i in range(10)]
        with pytest.raises(ValueError, match="window must be >= 1"):
            analyze_stable_numbers(draws, window=0)

    def test_invalid_threshold(self):
        """Threshold outside [0, 1] should raise ValueError."""
        draws = [create_draw(datetime(2024, 1, i + 1), [1, 2, 3]) for i in range(10)]
        with pytest.raises(ValueError, match="stability_threshold must be in"):
            analyze_stable_numbers(draws, window=5, stability_threshold=1.5)

    def test_basic_analysis(self):
        """Test basic analysis with consistent number appearances."""
        # Create draws where number 1 appears consistently
        base_date = datetime(2024, 1, 1)
        draws = []
        for i in range(100):
            # Number 1 appears in every draw (stable)
            # Number 2 appears randomly (less stable)
            numbers = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
            if i % 3 == 0:
                numbers[1] = 2  # Replace 3 with 2 sometimes
            draws.append(create_draw(base_date + timedelta(days=i), numbers))

        results = analyze_stable_numbers(
            draws,
            window=20,
            stability_threshold=0.90,
            number_range=(1, 21),
        )

        assert len(results) == 21
        # Results should be sorted by stability (descending)
        assert results[0].stability_score >= results[-1].stability_score

        # Number 1 appears in every draw - should be very stable
        num1_result = next(r for r in results if r.number == 1)
        assert num1_result.stability_score >= 0.90
        assert num1_result.is_stable is True

    def test_number_range_inferred(self):
        """Number range should be inferred from data if not provided."""
        base_date = datetime(2024, 1, 1)
        draws = [
            create_draw(base_date + timedelta(days=i), [5, 10, 15, 20, 25])
            for i in range(50)
        ]

        results = analyze_stable_numbers(draws, window=10)

        # Should only analyze numbers that appeared
        numbers_analyzed = {r.number for r in results}
        assert 5 in numbers_analyzed
        assert 25 in numbers_analyzed
        # Should not analyze 1, 2, 3, 4 since they never appeared
        assert 1 not in numbers_analyzed

    def test_results_sorted_by_stability(self):
        """Results should be sorted by stability_score descending."""
        base_date = datetime(2024, 1, 1)
        draws = []
        for i in range(50):
            numbers = list(range(1, 21))
            draws.append(create_draw(base_date + timedelta(days=i), numbers))

        results = analyze_stable_numbers(draws, window=10, number_range=(1, 20))

        for i in range(len(results) - 1):
            assert results[i].stability_score >= results[i + 1].stability_score

    def test_stable_number_result_fields(self):
        """Test that StableNumberResult has all expected fields."""
        base_date = datetime(2024, 1, 1)
        draws = [
            create_draw(base_date + timedelta(days=i), list(range(1, 21)))
            for i in range(50)
        ]

        results = analyze_stable_numbers(draws, window=10, number_range=(1, 20))

        assert len(results) > 0
        result = results[0]
        assert isinstance(result, StableNumberResult)
        assert isinstance(result.number, int)
        assert isinstance(result.stability_score, float)
        assert isinstance(result.is_stable, bool)
        assert isinstance(result.avg_frequency, float)
        assert isinstance(result.std_frequency, float)
        assert isinstance(result.window, int)
        assert isinstance(result.data_points, int)


class TestGetStableNumbers:
    """Tests for get_stable_numbers convenience function."""

    def test_returns_only_stable(self):
        """Should return only numbers that are stable."""
        base_date = datetime(2024, 1, 1)
        draws = [
            create_draw(base_date + timedelta(days=i), list(range(1, 21)))
            for i in range(50)
        ]

        stable = get_stable_numbers(draws, window=10, stability_threshold=0.90)

        # All returned numbers should be stable
        assert isinstance(stable, list)
        for num in stable:
            assert isinstance(num, int)

    def test_empty_on_no_data(self):
        """Should return empty list when no data."""
        stable = get_stable_numbers([], window=10)
        assert stable == []


class TestStabilityThreshold:
    """Test different stability threshold behaviors."""

    def test_high_threshold_fewer_stable(self):
        """Higher threshold should result in fewer stable numbers."""
        base_date = datetime(2024, 1, 1)
        draws = [
            create_draw(base_date + timedelta(days=i), list(range(1, 21)))
            for i in range(100)
        ]

        results_high = analyze_stable_numbers(draws, window=20, stability_threshold=0.95)
        results_low = analyze_stable_numbers(draws, window=20, stability_threshold=0.80)

        stable_high = len([r for r in results_high if r.is_stable])
        stable_low = len([r for r in results_low if r.is_stable])

        assert stable_high <= stable_low

    def test_threshold_at_boundary(self):
        """Test behavior at exact threshold boundary."""
        base_date = datetime(2024, 1, 1)
        draws = [
            create_draw(base_date + timedelta(days=i), list(range(1, 21)))
            for i in range(50)
        ]

        results = analyze_stable_numbers(draws, window=10)

        for r in results:
            if r.stability_score >= 0.90:
                assert r.is_stable is True
            else:
                assert r.is_stable is False
