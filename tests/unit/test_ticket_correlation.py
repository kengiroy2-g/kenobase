"""Unit tests for ticket_correlation module.

Tests 5 scenarios:
1. No overlap between tickets
2. Full overlap (identical tickets)
3. Partial overlap
4. Insufficient data handling
5. Diversification score calculation

Author: EXECUTOR (TASK_034)
Date: 2025-12-30
"""

import pytest
import numpy as np

from kenobase.analysis.ticket_correlation import (
    TicketPair,
    OverlapResult,
    SyncResult,
    TimingResult,
    PairCorrelation,
    TicketCorrelationResult,
    calculate_overlap,
    calculate_roi_sync,
    calculate_timing,
    calculate_diversification_score,
    analyze_ticket_pair,
    analyze_ticket_correlation,
)


class TestCalculateOverlap:
    """Tests for calculate_overlap function."""

    def test_no_overlap(self) -> None:
        """Test Jaccard = 0 when no shared numbers."""
        numbers_a = [1, 2, 3]
        numbers_b = [4, 5, 6]

        result = calculate_overlap(numbers_a, numbers_b)

        assert result.jaccard_index == 0.0
        assert result.overlap_count == 0
        assert result.union_count == 6

    def test_full_overlap(self) -> None:
        """Test Jaccard = 1 when identical tickets."""
        numbers = [1, 2, 3, 4, 5]

        result = calculate_overlap(numbers, numbers)

        assert result.jaccard_index == 1.0
        assert result.overlap_count == 5
        assert result.union_count == 5

    def test_partial_overlap(self) -> None:
        """Test Jaccard for partial overlap."""
        numbers_a = [1, 2, 3, 4]  # 4 numbers
        numbers_b = [3, 4, 5, 6]  # 4 numbers, 2 shared

        result = calculate_overlap(numbers_a, numbers_b)

        # Intersection: {3, 4} = 2, Union: {1,2,3,4,5,6} = 6
        # Jaccard = 2/6 = 0.333...
        assert result.jaccard_index == pytest.approx(2 / 6)
        assert result.overlap_count == 2
        assert result.union_count == 6

    def test_subset_overlap(self) -> None:
        """Test when one ticket is subset of other."""
        numbers_a = [1, 2]
        numbers_b = [1, 2, 3, 4]

        result = calculate_overlap(numbers_a, numbers_b)

        # Intersection: {1, 2} = 2, Union: {1,2,3,4} = 4
        # Jaccard = 2/4 = 0.5
        assert result.jaccard_index == 0.5
        assert result.overlap_count == 2
        assert result.union_count == 4


class TestCalculateRoiSync:
    """Tests for calculate_roi_sync function."""

    def test_insufficient_data(self) -> None:
        """Test returns None with insufficient observations."""
        roi_a = [0.1, 0.2, 0.3]  # Only 3 observations
        roi_b = [0.1, 0.2, 0.3]

        result = calculate_roi_sync(roi_a, roi_b, min_observations=10)

        assert result is None

    def test_perfect_positive_correlation(self) -> None:
        """Test Spearman r = 1 for perfect positive correlation."""
        roi_a = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        roi_b = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

        result = calculate_roi_sync(roi_a, roi_b, min_observations=5)

        assert result is not None
        assert result.spearman_r == pytest.approx(1.0)
        assert result.n_observations == 10
        assert result.is_significant

    def test_negative_correlation(self) -> None:
        """Test Spearman r < 0 for negative correlation."""
        roi_a = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        roi_b = [10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]  # Reversed

        result = calculate_roi_sync(roi_a, roi_b, min_observations=5)

        assert result is not None
        assert result.spearman_r == pytest.approx(-1.0)
        assert result.is_significant

    def test_constant_array(self) -> None:
        """Test handles constant arrays gracefully."""
        roi_a = [1.0] * 20  # Constant
        roi_b = [1.0, 2.0, 3.0, 4.0, 5.0] * 4

        result = calculate_roi_sync(roi_a, roi_b, min_observations=5)

        assert result is not None
        assert result.spearman_r == 0.0
        assert result.spearman_p == 1.0
        assert not result.is_significant


class TestCalculateTiming:
    """Tests for calculate_timing function."""

    def test_insufficient_draws(self) -> None:
        """Test returns None with insufficient draws."""
        wins_a = [True, False, True]
        wins_b = [True, True, False]

        result = calculate_timing(wins_a, wins_b, min_draws=10)

        assert result is None

    def test_perfect_cooccurrence(self) -> None:
        """Test lift > 1 when tickets always win together."""
        # Both win on same draws
        wins_a = [True, False, True, False, True, False, True, False, True, False]
        wins_b = [True, False, True, False, True, False, True, False, True, False]

        result = calculate_timing(wins_a, wins_b, min_draws=5)

        assert result is not None
        assert result.cooccurrence_ratio == 0.5  # 5/10 draws both win
        assert result.ticket_a_win_rate == 0.5
        assert result.ticket_b_win_rate == 0.5
        # Expected = 0.5 * 0.5 = 0.25, Actual = 0.5
        assert result.expected_cooccurrence == 0.25
        assert result.lift == pytest.approx(2.0)  # 0.5 / 0.25

    def test_anti_cooccurrence(self) -> None:
        """Test lift < 1 when tickets never win together."""
        # A wins when B loses and vice versa
        wins_a = [True, False, True, False, True, False, True, False, True, False]
        wins_b = [False, True, False, True, False, True, False, True, False, True]

        result = calculate_timing(wins_a, wins_b, min_draws=5)

        assert result is not None
        assert result.cooccurrence_ratio == 0.0  # Never win together
        assert result.ticket_a_win_rate == 0.5
        assert result.ticket_b_win_rate == 0.5
        assert result.lift == 0.0  # 0 / 0.25


class TestDiversificationScore:
    """Tests for calculate_diversification_score function."""

    def test_maximum_diversification(self) -> None:
        """Test max score with no overlap, negative sync, low timing."""
        overlap = OverlapResult(jaccard_index=0.0, overlap_count=0, union_count=10)
        sync = SyncResult(
            spearman_r=-1.0, spearman_p=0.001, n_observations=100, is_significant=True
        )
        timing = TimingResult(
            cooccurrence_ratio=0.0,
            ticket_a_win_rate=0.5,
            ticket_b_win_rate=0.5,
            expected_cooccurrence=0.25,
            lift=0.0,
            n_draws=100,
        )

        score = calculate_diversification_score(overlap, sync, timing)

        # No overlap = 1.0, negative correlation = 1.0, lift=0 = 1.0
        assert score == pytest.approx(1.0)

    def test_minimum_diversification(self) -> None:
        """Test min score with full overlap, positive sync, high timing."""
        overlap = OverlapResult(jaccard_index=1.0, overlap_count=5, union_count=5)
        sync = SyncResult(
            spearman_r=1.0, spearman_p=0.001, n_observations=100, is_significant=True
        )
        timing = TimingResult(
            cooccurrence_ratio=0.5,
            ticket_a_win_rate=0.5,
            ticket_b_win_rate=0.5,
            expected_cooccurrence=0.25,
            lift=2.0,
            n_draws=100,
        )

        score = calculate_diversification_score(overlap, sync, timing)

        # Full overlap = 0.0, positive correlation = 0.0, lift=2 = 0.0
        assert score == pytest.approx(0.0)

    def test_neutral_score(self) -> None:
        """Test neutral score with partial overlap and no sync/timing."""
        overlap = OverlapResult(jaccard_index=0.5, overlap_count=2, union_count=4)

        score = calculate_diversification_score(overlap, None, None)

        # Overlap = 0.5, sync = 0.5 (neutral), timing = 0.5 (neutral)
        assert score == pytest.approx(0.5)


class TestAnalyzeTicketPair:
    """Tests for analyze_ticket_pair function."""

    def test_overlap_only(self) -> None:
        """Test analysis with overlap only (no ROI/timing data)."""
        pair = TicketPair(
            ticket_a_type=2,
            ticket_b_type=6,
            ticket_a_numbers=(9, 50),
            ticket_b_numbers=(3, 24, 40, 49, 51, 64),
        )

        result = analyze_ticket_pair(pair)

        assert result.pair == pair
        assert result.overlap.jaccard_index == 0.0  # No shared numbers
        assert result.sync is None
        assert result.timing is None
        assert 0.0 <= result.diversification_score <= 1.0


class TestAnalyzeTicketCorrelation:
    """Tests for analyze_ticket_correlation function."""

    def test_single_ticket_warning(self) -> None:
        """Test returns empty result with single ticket."""
        tickets = {2: (9, 50)}

        result = analyze_ticket_correlation(tickets)

        assert result.n_tickets == 1
        assert result.n_pairs == 0
        assert len(result.pair_correlations) == 0

    def test_four_tickets(self) -> None:
        """Test with 4 tickets (6 pairs)."""
        tickets = {
            2: (9, 50),
            6: (3, 24, 40, 49, 51, 64),
            8: (2, 3, 20, 24, 36, 49, 51, 64),
            10: (2, 3, 9, 24, 33, 36, 49, 50, 51, 64),
        }

        result = analyze_ticket_correlation(tickets)

        assert result.n_tickets == 4
        assert result.n_pairs == 6  # C(4,2) = 6
        assert len(result.pair_correlations) == 6
        assert result.best_diversification_pair is not None
        assert result.worst_diversification_pair is not None

    def test_to_dict_serialization(self) -> None:
        """Test result can be serialized to dict."""
        tickets = {
            2: (9, 50),
            6: (3, 24, 40, 49, 51, 64),
        }

        result = analyze_ticket_correlation(tickets)
        result_dict = result.to_dict()

        assert "generated_at" in result_dict
        assert "n_tickets" in result_dict
        assert "n_pairs" in result_dict
        assert "pair_correlations" in result_dict
        assert len(result_dict["pair_correlations"]) == 1


class TestTicketPairValidation:
    """Tests for TicketPair validation."""

    def test_empty_numbers_raises(self) -> None:
        """Test that empty numbers raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TicketPair(
                ticket_a_type=2,
                ticket_b_type=6,
                ticket_a_numbers=(),
                ticket_b_numbers=(1, 2, 3),
            )

    def test_valid_pair(self) -> None:
        """Test valid pair creation."""
        pair = TicketPair(
            ticket_a_type=2,
            ticket_b_type=6,
            ticket_a_numbers=(9, 50),
            ticket_b_numbers=(3, 24, 40, 49, 51, 64),
        )

        assert pair.ticket_a_type == 2
        assert pair.ticket_b_type == 6
        assert pair.ticket_a_numbers == (9, 50)
        assert pair.ticket_b_numbers == (3, 24, 40, 49, 51, 64)
