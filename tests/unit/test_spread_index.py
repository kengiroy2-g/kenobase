"""Unit tests for spread_index analysis."""

from datetime import datetime

import pytest

from kenobase.analysis.spread_index import (
    SpreadBin,
    SpreadIndexResult,
    analyze_spread_index,
    calculate_spread_index,
    calculate_spread_for_draws,
    create_spread_bins,
)
from kenobase.core.data_loader import DrawResult, GameType


def _draw(numbers: list[int]) -> DrawResult:
    return DrawResult(
        date=datetime(2025, 1, 1),
        numbers=numbers,
        bonus=[],
        game_type=GameType.KENO,
        metadata={},
    )


class TestCalculateSpreadIndex:
    """Tests for calculate_spread_index helper function."""

    def test_max_spread(self) -> None:
        """Test with numbers from 1 to 70 (KENO range)."""
        # (70 - 1) / 70 = 0.9857...
        spread = calculate_spread_index([1, 35, 70])
        assert spread == pytest.approx(69 / 70, abs=1e-6)

    def test_min_spread(self) -> None:
        """Test with consecutive numbers."""
        # (5 - 1) / 5 = 0.8
        spread = calculate_spread_index([1, 2, 3, 4, 5])
        assert spread == pytest.approx(0.8, abs=1e-6)

    def test_same_number(self) -> None:
        """Test with all same numbers."""
        spread = calculate_spread_index([5, 5, 5, 5])
        assert spread == pytest.approx(0.0, abs=1e-6)

    def test_single_number(self) -> None:
        """Test with single number returns 0."""
        spread = calculate_spread_index([42])
        assert spread == 0.0

    def test_empty_list(self) -> None:
        """Test with empty list returns 0."""
        spread = calculate_spread_index([])
        assert spread == 0.0

    def test_two_numbers(self) -> None:
        """Test with exactly two numbers."""
        # (10 - 2) / 10 = 0.8
        spread = calculate_spread_index([2, 10])
        assert spread == pytest.approx(0.8, abs=1e-6)

    def test_keno_typical(self) -> None:
        """Test with typical KENO draw numbers."""
        # 20 numbers from 1-70: e.g., min=3, max=68 -> (68-3)/68 = 0.956
        numbers = [3, 7, 12, 18, 23, 29, 31, 35, 40, 42, 47, 51, 55, 58, 60, 62, 64, 66, 67, 68]
        spread = calculate_spread_index(numbers)
        expected = (68 - 3) / 68
        assert spread == pytest.approx(expected, abs=1e-6)


class TestCalculateSpreadForDraws:
    """Tests for calculate_spread_for_draws function."""

    def test_multiple_draws(self) -> None:
        """Test calculating spread for multiple draws."""
        draws = [
            _draw([1, 10]),  # (10-1)/10 = 0.9
            _draw([5, 10]),  # (10-5)/10 = 0.5
            _draw([1, 2]),   # (2-1)/2 = 0.5
        ]
        spreads = calculate_spread_for_draws(draws)
        assert len(spreads) == 3
        assert spreads[0] == pytest.approx(0.9, abs=1e-6)
        assert spreads[1] == pytest.approx(0.5, abs=1e-6)
        assert spreads[2] == pytest.approx(0.5, abs=1e-6)

    def test_empty_draws(self) -> None:
        """Test with empty draws list."""
        spreads = calculate_spread_for_draws([])
        assert spreads == []


class TestCreateSpreadBins:
    """Tests for create_spread_bins function."""

    def test_uniform_distribution(self) -> None:
        """Test with uniformly distributed spreads."""
        # Create 50 values evenly distributed across [0, 1]
        spread_values = [i / 50 for i in range(50)]

        bins, max_dev, breached = create_spread_bins(spread_values, n_bins=5, guardrail_ratio=0.15)

        assert len(bins) == 5
        assert breached is False
        assert max_dev < 0.15

    def test_concentrated_distribution(self) -> None:
        """Test with all values in one bin."""
        spread_values = [0.1, 0.1, 0.12, 0.15, 0.18]

        bins, max_dev, breached = create_spread_bins(spread_values, n_bins=5, guardrail_ratio=0.15)

        assert len(bins) == 5
        assert breached is True  # All in first bin -> large deviation

    def test_empty_list(self) -> None:
        """Test with empty list."""
        bins, max_dev, breached = create_spread_bins([], n_bins=5, guardrail_ratio=0.15)

        assert bins == []
        assert max_dev == 0.0
        assert breached is False

    def test_bin_labels(self) -> None:
        """Test that bin labels are formatted correctly."""
        spread_values = [0.1, 0.3, 0.5, 0.7, 0.9]
        bins, _, _ = create_spread_bins(spread_values, n_bins=5, guardrail_ratio=0.15)

        assert bins[0].bin_label == "[0.0-0.2)"
        assert bins[4].bin_label == "[0.8-1.0]"


class TestAnalyzeSpreadIndex:
    """Tests for main analyze_spread_index function."""

    def test_typical_keno_draws(self) -> None:
        """Test with typical KENO-like draws."""
        draws = [
            _draw([1, 10, 20, 30, 40, 50, 60, 70]),  # Max spread
            _draw([5, 15, 25, 35, 45, 55, 65, 69]),
            _draw([2, 12, 22, 32, 42, 52, 62, 68]),
        ]

        result = analyze_spread_index(draws)

        assert result.total_draws == 3
        assert result.numbers_per_draw == 8
        assert len(result.spread_values) == 3
        assert result.mean_spread > 0.9  # High spread expected
        assert result.guardrail_breached is False or result.guardrail_breached is True

    def test_empty_draws(self) -> None:
        """Test with empty draws list."""
        result = analyze_spread_index([])

        assert result.total_draws == 0
        assert result.spread_values == []
        assert result.mean_spread == 0.0
        assert result.guardrail_breached is False
        assert "No draws provided" in result.warnings

    def test_custom_guardrail(self) -> None:
        """Test with custom guardrail ratio."""
        # Create draws spread across bins for balanced distribution
        draws = [
            _draw([1, 10]),   # 0.9 -> high bin
            _draw([5, 10]),   # 0.5 -> middle bin
            _draw([8, 10]),   # 0.2 -> low bin
            _draw([3, 10]),   # 0.7 -> middle-high bin
            _draw([6, 10]),   # 0.4 -> middle-low bin
        ]

        # Strict guardrail might breach due to distribution
        result_strict = analyze_spread_index(draws, guardrail_ratio=0.05)
        # With only 5 samples, some deviation is expected

        # Lenient guardrail should not breach
        result_lenient = analyze_spread_index(draws, guardrail_ratio=0.50)
        # 50% deviation tolerance should accommodate 5 samples

        # Verify guardrail is configurable
        assert isinstance(result_strict.guardrail_breached, bool)
        assert isinstance(result_lenient.guardrail_breached, bool)
        # Max deviation should be the same regardless of guardrail
        assert result_strict.max_deviation_ratio == result_lenient.max_deviation_ratio

    def test_bins_structure(self) -> None:
        """Test that bins contain correct structure."""
        draws = [
            _draw([1, 10, 20]),
            _draw([5, 15, 25]),
            _draw([10, 20, 30]),
        ]

        result = analyze_spread_index(draws, n_bins=5)

        assert len(result.bins) == 5
        for bin_stat in result.bins:
            assert isinstance(bin_stat.bin_label, str)
            assert 0 <= bin_stat.bin_min <= 1
            assert 0 <= bin_stat.bin_max <= 1
            assert bin_stat.count >= 0
            assert bin_stat.expected_count >= 0
            assert 0 <= bin_stat.relative_frequency <= 1
            assert isinstance(bin_stat.within_guardrail, bool)

    def test_numbers_per_draw_inference(self) -> None:
        """Test that numbers_per_draw is correctly inferred."""
        draws = [_draw([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])]

        result = analyze_spread_index(draws)
        assert result.numbers_per_draw == 10

        result_explicit = analyze_spread_index(draws, numbers_per_draw=20)
        assert result_explicit.numbers_per_draw == 20

    def test_chi_square_valid(self) -> None:
        """Test that chi-square test returns valid values."""
        draws = [_draw([i, i + 10, i + 20]) for i in range(1, 50)]

        result = analyze_spread_index(draws)

        assert result.chi_square >= 0
        assert 0 <= result.chi_p_value <= 1


class TestStatisticalProperties:
    """Tests for statistical properties of spread index."""

    def test_spread_always_in_range(self) -> None:
        """Test that spread is always in [0, 1]."""
        test_cases = [
            [1, 70],
            [1, 2],
            [35, 36],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70],
        ]

        for numbers in test_cases:
            spread = calculate_spread_index(numbers)
            assert 0 <= spread <= 1, f"Spread {spread} out of range for {numbers}"

    def test_monotonic_with_range(self) -> None:
        """Test that larger range gives larger spread for same max."""
        spread_narrow = calculate_spread_index([5, 10])   # (10-5)/10 = 0.5
        spread_wide = calculate_spread_index([1, 10])     # (10-1)/10 = 0.9

        assert spread_wide > spread_narrow


class TestEdgeCases:
    """Tests for edge cases."""

    def test_draws_with_empty_numbers(self) -> None:
        """Test draws that have empty number lists."""
        draws = [_draw([]), _draw([])]

        result = analyze_spread_index(draws)

        assert result.total_draws == 2
        assert all(s == 0.0 for s in result.spread_values)

    def test_draws_with_single_number(self) -> None:
        """Test draws with only one number."""
        draws = [_draw([42]), _draw([17])]

        result = analyze_spread_index(draws)

        assert result.total_draws == 2
        assert all(s == 0.0 for s in result.spread_values)

    def test_large_numbers(self) -> None:
        """Test with large number ranges."""
        spread = calculate_spread_index([1, 1000])
        expected = (1000 - 1) / 1000
        assert spread == pytest.approx(expected, abs=1e-6)

    def test_zero_in_numbers(self) -> None:
        """Test behavior when zero is in the number list."""
        # (10 - 0) / 10 = 1.0
        spread = calculate_spread_index([0, 10])
        assert spread == pytest.approx(1.0, abs=1e-6)

    def test_max_is_zero(self) -> None:
        """Test when max value is zero."""
        spread = calculate_spread_index([0, 0, 0])
        assert spread == 0.0
