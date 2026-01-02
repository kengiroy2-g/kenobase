"""Unit tests for decade_distribution analysis."""

from datetime import datetime

import pytest

from kenobase.analysis.decade_distribution import (
    analyze_decade_distribution,
    map_number_to_decade,
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


def test_map_number_to_decade_basic() -> None:
    assert map_number_to_decade(1) == 0
    assert map_number_to_decade(10) == 0
    assert map_number_to_decade(11) == 1
    assert map_number_to_decade(70) == 6

    with pytest.raises(ValueError):
        map_number_to_decade(0)


def test_uniform_decade_distribution() -> None:
    draws = [
        _draw([1, 11, 21, 31, 41, 51, 61]),
        _draw([10, 20, 30, 40, 50, 60, 70]),
    ]

    result = analyze_decade_distribution(draws, max_number=70, numbers_per_draw=7)

    assert result.total_numbers == 14
    assert result.guardrail_breached is False
    assert result.max_deviation_ratio == pytest.approx(0.0, abs=1e-6)
    assert result.chi_square == pytest.approx(0.0, abs=1e-6)
    assert result.p_value == pytest.approx(1.0, rel=1e-3)

    for bin_stat in result.bins:
        assert bin_stat.count == 2
        assert bin_stat.within_guardrail is True


def test_guardrail_flag_triggers_on_large_deviation() -> None:
    draws = [
        _draw([1, 2, 3, 4, 5, 6, 7]),
        _draw([1, 2, 3, 4, 5, 6, 7]),
    ]

    result = analyze_decade_distribution(draws, max_number=70, numbers_per_draw=7)

    assert result.guardrail_breached is True
    assert result.max_deviation_ratio > 0.20
    assert result.bins[0].count == 14
    assert result.bins[0].within_guardrail is False
