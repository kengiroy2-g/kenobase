"""Unit tests for kenobase.analysis.odds_correlation module (HYP-010)."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pytest

from kenobase.analysis.odds_correlation import (
    NumberClassification,
    OddsAnalysisSummary,
    OddsCorrelationResult,
    aggregate_winners_by_date,
    analyze_odds_correlation,
    calculate_draw_frequency,
    calculate_number_winner_scores,
    classify_numbers_by_popularity,
)
from kenobase.core.data_loader import DrawResult, GameType


def make_draw(date: str, numbers: list[int]) -> DrawResult:
    """Create a DrawResult for testing."""
    return DrawResult(
        date=datetime.strptime(date, "%d.%m.%Y"),
        numbers=numbers,
        bonus=[],
        game_type=GameType.KENO,
    )


class TestAggregateWinnersByDate:
    """Tests for aggregate_winners_by_date function."""

    def test_simple_aggregation(self):
        """Test basic winner aggregation."""
        gq_data = {
            datetime(2024, 1, 1): {2: 100.0, 3: 50.0, 4: 25.0},
            datetime(2024, 1, 2): {2: 200.0, 5: 10.0},
        }

        result = aggregate_winners_by_date(gq_data, weight_by_keno_typ=False)

        assert result[datetime(2024, 1, 1)] == 175.0  # 100 + 50 + 25
        assert result[datetime(2024, 1, 2)] == 210.0  # 200 + 10

    def test_weighted_aggregation(self):
        """Test aggregation with Keno-Typ weighting."""
        gq_data = {
            datetime(2024, 1, 1): {2: 100.0, 10: 100.0},  # Same count, different weight
        }

        result = aggregate_winners_by_date(gq_data, weight_by_keno_typ=True)

        # 100 * 0.2 + 100 * 1.0 = 120
        assert result[datetime(2024, 1, 1)] == 120.0

    def test_empty_data(self):
        """Test with empty GQ data."""
        result = aggregate_winners_by_date({})
        assert result == {}


class TestCalculateNumberWinnerScores:
    """Tests for calculate_number_winner_scores function."""

    def test_basic_scores(self):
        """Test basic winner score calculation."""
        gq_data = {
            datetime(2024, 1, 1): {2: 100.0},
            datetime(2024, 1, 2): {2: 200.0},
        }

        draws = [
            make_draw("01.01.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
            make_draw("02.01.2024", [1, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                                     30, 31, 32, 33, 34, 35, 36, 37, 38, 39]),
        ]

        result = calculate_number_winner_scores(gq_data, draws, weight_by_keno_typ=False)

        # Number 1 appears in both draws
        avg_1, count_1 = result[1]
        assert count_1 == 2
        assert avg_1 == 150.0  # (100 + 200) / 2

        # Number 2 appears only in first draw
        avg_2, count_2 = result[2]
        assert count_2 == 1
        assert avg_2 == 100.0

    def test_no_overlap(self):
        """Test when draws don't overlap with GQ dates."""
        gq_data = {
            datetime(2024, 1, 1): {2: 100.0},
        }

        draws = [
            make_draw("01.06.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
        ]

        result = calculate_number_winner_scores(gq_data, draws)

        # No overlap, all counts should be 0
        for num in range(1, 71):
            assert result[num][1] == 0  # draw_count


class TestCalculateDrawFrequency:
    """Tests for calculate_draw_frequency function."""

    def test_basic_frequency(self):
        """Test basic frequency calculation."""
        draws = [
            make_draw("01.01.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
            make_draw("02.01.2024", [1, 2, 21, 22, 23, 24, 25, 26, 27, 28,
                                     29, 30, 31, 32, 33, 34, 35, 36, 37, 38]),
        ]

        result = calculate_draw_frequency(draws)

        # Numbers 1 and 2 appear in both draws
        assert result[1] == 1.0  # 2/2
        assert result[2] == 1.0  # 2/2

        # Number 3 appears in one draw
        assert result[3] == 0.5  # 1/2

        # Number 70 never appears
        assert result[70] == 0.0

    def test_date_filtering(self):
        """Test frequency with date filtering."""
        draws = [
            make_draw("01.01.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
            make_draw("01.06.2024", [21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                                     31, 32, 33, 34, 35, 36, 37, 38, 39, 40]),
        ]

        # Filter to January only
        result = calculate_draw_frequency(
            draws,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
        )

        # Only first draw included
        assert result[1] == 1.0
        assert result[21] == 0.0

    def test_empty_draws(self):
        """Test with empty draws list."""
        result = calculate_draw_frequency([])
        assert result == {}


class TestAnalyzeOddsCorrelation:
    """Tests for analyze_odds_correlation function."""

    def test_empty_gq_data(self):
        """Test with empty GQ data."""
        draws = [
            make_draw("01.01.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
        ]

        result = analyze_odds_correlation({}, draws)

        assert result.n_samples == 0
        assert not result.is_significant

    def test_insufficient_overlap(self):
        """Test with insufficient draw overlap."""
        gq_data = {
            datetime(2024, 6, 1): {2: 100.0},
        }

        draws = [
            make_draw("01.01.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
        ]

        result = analyze_odds_correlation(gq_data, draws)

        # No overlap
        assert result.n_draws == 0

    def test_result_structure(self):
        """Test that result has correct structure."""
        gq_data = {
            datetime(2024, 1, i): {2: float(100 + i * 10)}
            for i in range(1, 31)
        }

        draws = [
            make_draw(f"{i:02d}.01.2024", list(range(1, 21)))
            for i in range(1, 31)
        ]

        result = analyze_odds_correlation(gq_data, draws)

        assert isinstance(result, OddsCorrelationResult)
        assert hasattr(result, "pearson_r")
        assert hasattr(result, "pearson_p")
        assert hasattr(result, "spearman_r")
        assert hasattr(result, "spearman_p")
        assert hasattr(result, "is_significant")
        assert hasattr(result, "n_samples")


class TestClassifyNumbersByPopularity:
    """Tests for classify_numbers_by_popularity function."""

    def test_classification_output(self):
        """Test that classification produces correct output."""
        # Create data where some numbers have consistently high/low winners
        gq_data = {}
        draws = []

        for i in range(1, 31):
            date = datetime(2024, 1, i)
            gq_data[date] = {2: 100.0 + i}  # Varying winners

            # Numbers 1-10 always drawn
            draws.append(
                make_draw(f"{i:02d}.01.2024", list(range(1, 21)))
            )

        result = classify_numbers_by_popularity(gq_data, draws)

        assert len(result) == 70

        # Check structure
        for classification in result:
            assert isinstance(classification, NumberClassification)
            assert 1 <= classification.number <= 70
            assert classification.classification in ["safe", "neutral", "popular", "no_data"]

    def test_threshold_effect(self):
        """Test that threshold affects classification counts."""
        gq_data = {
            datetime(2024, 1, i): {2: float(np.random.uniform(50, 150))}
            for i in range(1, 31)
        }

        draws = [
            make_draw(f"{i:02d}.01.2024", list(range(1, 21)))
            for i in range(1, 31)
        ]

        # Lower threshold = more extreme classifications
        result_low = classify_numbers_by_popularity(gq_data, draws, threshold_std=0.5)
        result_high = classify_numbers_by_popularity(gq_data, draws, threshold_std=2.0)

        safe_low = sum(1 for c in result_low if c.classification == "safe")
        safe_high = sum(1 for c in result_high if c.classification == "safe")

        # Higher threshold should result in fewer extreme classifications
        assert safe_low >= safe_high


class TestOddsCorrelationResultDataclass:
    """Tests for OddsCorrelationResult dataclass."""

    def test_frozen(self):
        """Test that result is immutable."""
        result = OddsCorrelationResult(
            pearson_r=0.5,
            pearson_p=0.01,
            spearman_r=0.4,
            spearman_p=0.02,
            is_significant=True,
            n_samples=70,
            n_draws=100,
            n_gq_dates=90,
        )

        with pytest.raises(AttributeError):
            result.pearson_r = 0.9  # type: ignore

    def test_significance_flag(self):
        """Test is_significant reflects p-values correctly."""
        significant = OddsCorrelationResult(
            pearson_r=0.5,
            pearson_p=0.01,  # < 0.05
            spearman_r=0.4,
            spearman_p=0.02,
            is_significant=True,
            n_samples=70,
            n_draws=100,
            n_gq_dates=90,
        )

        not_significant = OddsCorrelationResult(
            pearson_r=0.1,
            pearson_p=0.5,  # >= 0.05
            spearman_r=0.05,
            spearman_p=0.7,
            is_significant=False,
            n_samples=70,
            n_draws=100,
            n_gq_dates=90,
        )

        assert significant.is_significant
        assert not not_significant.is_significant
