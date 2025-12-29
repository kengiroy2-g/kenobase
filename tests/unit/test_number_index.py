"""Unit tests for kenobase.analysis.number_index module.

Tests Index-Reset functionality for HYP-005:
- Index calculation since last GK1-Event
- Correlation analysis between Index and hit rate
- Edge cases and data validation
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from kenobase.analysis.number_index import (
    CorrelationResult,
    IndexResult,
    NumberIndex,
    calculate_index_correlation,
    calculate_index_table,
)


class TestNumberIndex:
    """Tests for NumberIndex dataclass."""

    def test_number_index_creation(self) -> None:
        """Test basic NumberIndex creation."""
        idx = NumberIndex(
            number=42,
            current_index=5,
            last_seen=datetime(2024, 1, 15),
            total_appearances=5,
        )
        assert idx.number == 42
        assert idx.current_index == 5
        assert idx.last_seen == datetime(2024, 1, 15)
        assert idx.total_appearances == 5

    def test_number_index_none_last_seen(self) -> None:
        """Test NumberIndex with no appearances."""
        idx = NumberIndex(
            number=1,
            current_index=0,
            last_seen=None,
            total_appearances=0,
        )
        assert idx.last_seen is None
        assert idx.current_index == 0


class TestCalculateIndexTable:
    """Tests for calculate_index_table function."""

    def test_empty_draws(self) -> None:
        """Test with no draws."""
        result = calculate_index_table(draws=[], gk1_events=[], number_range=70)

        assert isinstance(result, IndexResult)
        assert len(result.indices) == 70
        assert result.draws_since_reset == 0
        assert result.last_reset_date is None
        assert all(idx.current_index == 0 for idx in result.indices.values())

    def test_no_gk1_events(self) -> None:
        """Test with draws but no GK1 events."""
        base_date = datetime(2024, 1, 1)
        draws: list[tuple[datetime, list[int]]] = [
            (base_date + timedelta(days=i), [1, 2, 3, 4, 5])
            for i in range(10)
        ]

        result = calculate_index_table(draws=draws, gk1_events=[], number_range=70)

        assert result.last_reset_date is None
        # All draws counted since no reset
        assert result.draws_since_reset == 10
        # Numbers 1-5 should each have index=10
        for num in range(1, 6):
            assert result.indices[num].current_index == 10
        # Numbers 6-70 should have index=0
        for num in range(6, 71):
            assert result.indices[num].current_index == 0

    def test_single_gk1_event(self) -> None:
        """Test index reset after single GK1 event."""
        base_date = datetime(2024, 1, 1)
        gk1_date = datetime(2024, 1, 5)

        draws: list[tuple[datetime, list[int]]] = []
        # 4 draws before GK1 (1, 2, 3, 4)
        for i in range(4):
            draws.append((base_date + timedelta(days=i), [10, 20, 30]))
        # 6 draws after GK1 (5, 6, 7, 8, 9, 10)
        for i in range(4, 10):
            draws.append((base_date + timedelta(days=i), [1, 2, 3]))

        gk1_events: list[tuple[datetime, int]] = [(gk1_date, 10)]

        result = calculate_index_table(draws=draws, gk1_events=gk1_events, number_range=70)

        # Reset should be on GK1 date
        assert result.last_reset_date == gk1_date
        assert result.gk1_event_type == 10
        # Only draws after GK1 should be counted (days 5-10 = 6 draws)
        assert result.draws_since_reset == 6
        # Numbers 1, 2, 3 appear in each of 6 draws after reset
        assert result.indices[1].current_index == 6
        assert result.indices[2].current_index == 6
        assert result.indices[3].current_index == 6
        # Numbers 10, 20, 30 only appeared before reset
        assert result.indices[10].current_index == 0
        assert result.indices[20].current_index == 0
        assert result.indices[30].current_index == 0

    def test_multiple_gk1_events(self) -> None:
        """Test that only the last GK1 event is used for reset."""
        base_date = datetime(2024, 1, 1)
        gk1_early = datetime(2024, 1, 3)
        gk1_late = datetime(2024, 1, 7)

        draws: list[tuple[datetime, list[int]]] = [
            (base_date + timedelta(days=i), [i + 1])
            for i in range(10)
        ]

        gk1_events: list[tuple[datetime, int]] = [
            (gk1_early, 9),
            (gk1_late, 10),
        ]

        result = calculate_index_table(draws=draws, gk1_events=gk1_events, number_range=70)

        # Should use the later GK1 event
        assert result.last_reset_date == gk1_late
        assert result.gk1_event_type == 10
        # Draws on days 7, 8, 9, 10 (4 draws including GK1 date; >= semantics)
        # Day 0=1/1, Day 6=1/7(GK1), Day 7=1/8, Day 8=1/9, Day 9=1/10
        assert result.draws_since_reset == 4

    def test_custom_number_range(self) -> None:
        """Test with custom number range."""
        result = calculate_index_table(draws=[], gk1_events=[], number_range=10)
        assert len(result.indices) == 10
        assert 10 in result.indices
        assert 11 not in result.indices


class TestCalculateIndexCorrelation:
    """Tests for calculate_index_correlation function."""

    def test_insufficient_data(self) -> None:
        """Test with insufficient draws."""
        draws: list[tuple[datetime, list[int]]] = [
            (datetime(2024, 1, i), list(range(1, 21)))
            for i in range(1, 10)  # Only 9 draws
        ]
        gk1_events: list[tuple[datetime, int]] = []

        result = calculate_index_correlation(draws, gk1_events)

        assert isinstance(result, CorrelationResult)
        assert result.p_value == 1.0
        assert "Insufficient data" in result.interpretation

    def test_no_valid_segments(self) -> None:
        """Test when no segments have enough draws."""
        base_date = datetime(2024, 1, 1)
        # Create draws but with GK1 events causing too-short segments
        draws: list[tuple[datetime, list[int]]] = [
            (base_date + timedelta(days=i), list(range(1, 21)))
            for i in range(30)
        ]
        # GK1 events every 3 days = segments too short
        gk1_events: list[tuple[datetime, int]] = [
            (base_date + timedelta(days=i), 10)
            for i in range(3, 30, 3)
        ]

        result = calculate_index_correlation(draws, gk1_events)

        # Should return result even if no valid segments
        assert isinstance(result, CorrelationResult)
        assert result.n_segments > 0

    def test_basic_correlation_structure(self) -> None:
        """Test that correlation result has correct structure."""
        base_date = datetime(2024, 1, 1)

        # Create 100 draws
        draws: list[tuple[datetime, list[int]]] = [
            (base_date + timedelta(days=i), list(range(1, 21)))
            for i in range(100)
        ]
        # Single GK1 at day 50
        gk1_events: list[tuple[datetime, int]] = [(base_date + timedelta(days=50), 10)]

        result = calculate_index_correlation(draws, gk1_events, top_n=11)

        assert isinstance(result, CorrelationResult)
        assert hasattr(result, "correlation")
        assert hasattr(result, "p_value")
        assert hasattr(result, "mean_hits_high_index")
        assert hasattr(result, "mean_hits_low_index")
        assert hasattr(result, "effect_size")
        assert hasattr(result, "interpretation")
        assert hasattr(result, "n_segments")
        assert hasattr(result, "segment_details")

        # p_value should be between 0 and 1
        assert 0 <= result.p_value <= 1

    def test_correlation_with_biased_data(self) -> None:
        """Test correlation with artificially biased data.

        Create draws where high-index numbers consistently appear.
        """
        base_date = datetime(2024, 1, 1)

        # Build draws where certain numbers always appear
        # Numbers 1-10 appear in every draw, 11-20 never
        draws: list[tuple[datetime, list[int]]] = []
        for i in range(50):
            numbers = list(range(1, 11)) + list(range(21, 31))  # 1-10 + 21-30
            draws.append((base_date + timedelta(days=i), numbers))

        # No GK1 events = entire range is one segment
        gk1_events: list[tuple[datetime, int]] = []

        result = calculate_index_correlation(draws, gk1_events, top_n=11)

        # With consistent data, we should see some structure
        assert result.n_segments >= 1
        # Mean hits for high-index should be >= 0
        assert result.mean_hits_high_index >= 0

    def test_correlation_top_n_parameter(self) -> None:
        """Test different top_n values."""
        base_date = datetime(2024, 1, 1)
        draws: list[tuple[datetime, list[int]]] = [
            (base_date + timedelta(days=i), list(range(1, 21)))
            for i in range(50)
        ]
        gk1_events: list[tuple[datetime, int]] = []

        result_5 = calculate_index_correlation(draws, gk1_events, top_n=5)
        result_15 = calculate_index_correlation(draws, gk1_events, top_n=15)

        # Both should return valid results
        assert isinstance(result_5, CorrelationResult)
        assert isinstance(result_15, CorrelationResult)

    def test_segment_details_populated(self) -> None:
        """Test that segment_details is populated."""
        base_date = datetime(2024, 1, 1)

        draws: list[tuple[datetime, list[int]]] = [
            (base_date + timedelta(days=i), list(range(1, 21)))
            for i in range(100)
        ]
        # Two GK1 events create 3 segments
        gk1_events: list[tuple[datetime, int]] = [
            (base_date + timedelta(days=30), 9),
            (base_date + timedelta(days=60), 10),
        ]

        result = calculate_index_correlation(draws, gk1_events)

        # Should have analyzed multiple segments
        assert result.n_segments >= 2
        assert isinstance(result.segment_details, list)


class TestIndexResultExport:
    """Tests for IndexResult structure and export compatibility."""

    def test_index_result_structure(self) -> None:
        """Test IndexResult has expected attributes."""
        result = calculate_index_table([], [], number_range=70)

        assert hasattr(result, "indices")
        assert hasattr(result, "last_reset_date")
        assert hasattr(result, "draws_since_reset")
        assert hasattr(result, "gk1_event_type")

    def test_indices_dict_structure(self) -> None:
        """Test indices dictionary structure."""
        result = calculate_index_table([], [], number_range=70)

        assert isinstance(result.indices, dict)
        assert len(result.indices) == 70

        for num in range(1, 71):
            assert num in result.indices
            idx = result.indices[num]
            assert isinstance(idx, NumberIndex)
            assert idx.number == num


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_gk1_event_on_draw_date(self) -> None:
        """Test when GK1 event date matches a draw date."""
        base_date = datetime(2024, 1, 1)
        gk1_date = datetime(2024, 1, 5)

        draws: list[tuple[datetime, list[int]]] = [
            (base_date + timedelta(days=i), [1])
            for i in range(10)
        ]
        gk1_events: list[tuple[datetime, int]] = [(gk1_date, 10)]

        result = calculate_index_table(draws, gk1_events)

        # GK1 on day 5, draws from day 5 onwards should be counted (>= semantics)
        assert result.last_reset_date == gk1_date
        # Day 4=1/5 (GK1), Day 5=1/6, ..., Day 9=1/10 = 6 draws total
        assert result.draws_since_reset == 6

    def test_gk1_event_after_all_draws(self) -> None:
        """Test when GK1 event is after all draws."""
        base_date = datetime(2024, 1, 1)
        gk1_date = datetime(2024, 2, 1)  # After all draws

        draws: list[tuple[datetime, list[int]]] = [
            (base_date + timedelta(days=i), [1])
            for i in range(10)
        ]
        gk1_events: list[tuple[datetime, int]] = [(gk1_date, 10)]

        result = calculate_index_table(draws, gk1_events)

        # GK1 is in future, so no reset applies to these draws
        assert result.last_reset_date is None
        assert result.draws_since_reset == 10

    def test_numbers_outside_range_ignored(self) -> None:
        """Test that numbers outside range are ignored."""
        draws: list[tuple[datetime, list[int]]] = [
            (datetime(2024, 1, 1), [1, 71, 100, -1, 0])  # Only 1 is valid
        ]

        result = calculate_index_table(draws, [], number_range=70)

        assert result.indices[1].current_index == 1
        # Invalid numbers should not cause errors
        assert 71 not in result.indices
        assert 0 not in result.indices
