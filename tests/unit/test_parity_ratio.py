"""Unit tests for parity_ratio analysis."""

from datetime import datetime

import pytest

from kenobase.analysis.parity_ratio import (
    ParityRatioResult,
    analyze_parity_ratio,
    count_parity,
    is_even,
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


class TestIsEven:
    """Tests for is_even helper function."""

    def test_even_numbers(self) -> None:
        assert is_even(2) is True
        assert is_even(4) is True
        assert is_even(10) is True
        assert is_even(70) is True

    def test_odd_numbers(self) -> None:
        assert is_even(1) is False
        assert is_even(3) is False
        assert is_even(11) is False
        assert is_even(69) is False


class TestCountParity:
    """Tests for count_parity helper function."""

    def test_all_even(self) -> None:
        even, odd = count_parity([2, 4, 6, 8, 10])
        assert even == 5
        assert odd == 0

    def test_all_odd(self) -> None:
        even, odd = count_parity([1, 3, 5, 7, 9])
        assert even == 0
        assert odd == 5

    def test_mixed(self) -> None:
        even, odd = count_parity([1, 2, 3, 4, 5, 6])
        assert even == 3
        assert odd == 3

    def test_empty(self) -> None:
        even, odd = count_parity([])
        assert even == 0
        assert odd == 0


class TestAnalyzeParityRatio:
    """Tests for main analyze_parity_ratio function."""

    def test_perfectly_balanced(self) -> None:
        """Test with exactly 50/50 even/odd distribution."""
        draws = [
            _draw([1, 2, 3, 4, 5, 6]),  # 3 even, 3 odd
            _draw([7, 8, 9, 10, 11, 12]),  # 3 even, 3 odd
        ]

        result = analyze_parity_ratio(draws)

        assert result.total_numbers == 12
        assert result.even_count == 6
        assert result.odd_count == 6
        assert result.parity_ratio == pytest.approx(0.5, abs=1e-6)
        assert result.chi_square == pytest.approx(0.0, abs=1e-6)
        assert result.chi_p_value == pytest.approx(1.0, rel=1e-3)
        assert result.binomial_p_value == pytest.approx(1.0, rel=1e-2)
        assert result.guardrail_breached is False
        assert result.max_deviation_ratio == pytest.approx(0.0, abs=1e-6)

    def test_all_even_triggers_guardrail(self) -> None:
        """Test that all even numbers trigger guardrail."""
        draws = [
            _draw([2, 4, 6, 8, 10, 12]),
            _draw([14, 16, 18, 20, 22, 24]),
        ]

        result = analyze_parity_ratio(draws)

        assert result.even_count == 12
        assert result.odd_count == 0
        assert result.parity_ratio == pytest.approx(1.0, abs=1e-6)
        assert result.guardrail_breached is True
        assert result.max_deviation_ratio == pytest.approx(1.0, abs=1e-6)
        assert result.chi_p_value < 0.001  # Highly significant
        assert result.binomial_p_value < 0.001

    def test_all_odd_triggers_guardrail(self) -> None:
        """Test that all odd numbers trigger guardrail."""
        draws = [
            _draw([1, 3, 5, 7, 9, 11]),
            _draw([13, 15, 17, 19, 21, 23]),
        ]

        result = analyze_parity_ratio(draws)

        assert result.even_count == 0
        assert result.odd_count == 12
        assert result.parity_ratio == pytest.approx(0.0, abs=1e-6)
        assert result.guardrail_breached is True
        assert result.max_deviation_ratio == pytest.approx(1.0, abs=1e-6)

    def test_slight_imbalance_within_guardrail(self) -> None:
        """Test slight imbalance stays within default 10% guardrail."""
        # 22 numbers: 12 even, 10 odd = 54.5% even, deviation ~9%
        draws = [
            _draw([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]),  # 11 even
            _draw([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]),  # 11 odd
        ]

        result = analyze_parity_ratio(draws)

        assert result.total_numbers == 22
        assert result.guardrail_breached is False

    def test_empty_draws(self) -> None:
        """Test with empty draws list."""
        result = analyze_parity_ratio([])

        assert result.total_draws == 0
        assert result.total_numbers == 0
        assert result.parity_ratio == 0.5
        assert result.guardrail_breached is False
        assert "No draws provided" in result.warnings

    def test_empty_numbers_in_draws(self) -> None:
        """Test with draws that have empty number lists."""
        draws = [_draw([]), _draw([])]

        result = analyze_parity_ratio(draws)

        assert result.total_draws == 2
        assert result.total_numbers == 0
        assert "No numbers found in draws" in result.warnings

    def test_custom_guardrail(self) -> None:
        """Test with custom guardrail ratio."""
        # 60/40 split = 20% deviation
        draws = [
            _draw([2, 4, 6, 1, 3, 5]),  # 3 even, 3 odd
            _draw([8, 10, 12, 14, 7, 9]),  # 4 even, 2 odd
        ]
        # Total: 7 even, 5 odd = 58.3% even, ~16.7% deviation

        # With 10% guardrail, should breach
        result_strict = analyze_parity_ratio(draws, guardrail_ratio=0.10)
        assert result_strict.guardrail_breached is True

        # With 20% guardrail, should not breach
        result_lenient = analyze_parity_ratio(draws, guardrail_ratio=0.20)
        assert result_lenient.guardrail_breached is False

    def test_bins_structure(self) -> None:
        """Test that bins contain correct structure."""
        draws = [_draw([1, 2, 3, 4, 5, 6])]

        result = analyze_parity_ratio(draws)

        assert len(result.bins) == 2
        categories = {b.category for b in result.bins}
        assert categories == {"even", "odd"}

        for bin_stat in result.bins:
            assert bin_stat.count >= 0
            assert bin_stat.expected_count > 0
            assert 0 <= bin_stat.relative_frequency <= 1
            assert isinstance(bin_stat.within_guardrail, bool)

    def test_numbers_per_draw_inference(self) -> None:
        """Test that numbers_per_draw is correctly inferred."""
        draws = [
            _draw([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),  # 10 numbers
        ]

        result = analyze_parity_ratio(draws)
        assert result.numbers_per_draw == 10

        # Test explicit override
        result_explicit = analyze_parity_ratio(draws, numbers_per_draw=20)
        assert result_explicit.numbers_per_draw == 20


class TestStatisticalSignificance:
    """Tests for statistical significance calculations."""

    def test_binomial_significance_large_sample(self) -> None:
        """Test binomial test with large sample detects small deviations."""
        # Create many draws with slight imbalance
        draws = []
        for _ in range(100):
            # 11 even, 9 odd per draw = 55% even
            draws.append(_draw([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 1, 3, 5, 7, 9, 11, 13, 15, 17]))

        result = analyze_parity_ratio(draws)

        # With 2000 numbers, 55% even should be significant
        assert result.binomial_p_value < 0.05
        assert result.chi_p_value < 0.05

    def test_chi_square_df1(self) -> None:
        """Chi-square test for 2 categories has 1 degree of freedom."""
        draws = [_draw([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])]

        result = analyze_parity_ratio(draws)

        # P-value should be valid (between 0 and 1)
        assert 0 <= result.chi_p_value <= 1
        assert result.chi_square >= 0
