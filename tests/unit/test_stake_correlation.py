"""Unit tests for kenobase.analysis.stake_correlation module (HYP-012)."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pytest

from kenobase.analysis.stake_correlation import (
    HighStakePopularityResult,
    NumberStakeClassification,
    StakeAnalysisSummary,
    StakeCorrelationResult,
    StakeDrawRecord,
    aggregate_stake_by_date,
    analyze_high_stake_popularity_bias,
    analyze_stake_correlation,
    calculate_draw_frequency_from_records,
    calculate_number_stake_scores,
    classify_numbers_by_stake,
)


def make_stake_record(
    date: str,
    numbers: list[int],
    spieleinsatz: float = 100000.0,
    total_auszahlung: float = 50000.0,
    restbetrag: float = 50000.0,
) -> StakeDrawRecord:
    """Create a StakeDrawRecord for testing."""
    return StakeDrawRecord(
        date=datetime.strptime(date, "%d.%m.%Y"),
        numbers=numbers,
        spieleinsatz=spieleinsatz,
        total_gewinner=100,
        total_auszahlung=total_auszahlung,
        restbetrag=restbetrag,
        kasse=restbetrag,
    )


class TestAggregateStakeByDate:
    """Tests for aggregate_stake_by_date function."""

    def test_simple_aggregation(self):
        """Test basic stake aggregation by date."""
        records = [
            make_stake_record("01.01.2024", [1, 2, 3], spieleinsatz=100000.0),
            make_stake_record("02.01.2024", [4, 5, 6], spieleinsatz=200000.0),
        ]

        result = aggregate_stake_by_date(records)

        assert result[datetime(2024, 1, 1)] == 100000.0
        assert result[datetime(2024, 1, 2)] == 200000.0

    def test_empty_records(self):
        """Test with empty records list."""
        result = aggregate_stake_by_date([])
        assert result == {}


class TestCalculateNumberStakeScores:
    """Tests for calculate_number_stake_scores function."""

    def test_basic_scores(self):
        """Test basic stake score calculation."""
        records = [
            make_stake_record(
                "01.01.2024",
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                spieleinsatz=100000.0,
            ),
            make_stake_record(
                "02.01.2024",
                [1, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
                spieleinsatz=200000.0,
            ),
        ]

        result = calculate_number_stake_scores(records)

        # Number 1 appears in both draws
        avg_1, count_1 = result[1]
        assert count_1 == 2
        assert avg_1 == 150000.0  # (100000 + 200000) / 2

        # Number 2 appears only in first draw
        avg_2, count_2 = result[2]
        assert count_2 == 1
        assert avg_2 == 100000.0

    def test_number_not_drawn(self):
        """Test numbers that were never drawn."""
        records = [
            make_stake_record("01.01.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                             11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
        ]

        result = calculate_number_stake_scores(records)

        # Number 70 was never drawn
        avg_70, count_70 = result[70]
        assert count_70 == 0
        assert avg_70 == 0.0


class TestCalculateDrawFrequencyFromRecords:
    """Tests for calculate_draw_frequency_from_records function."""

    def test_basic_frequency(self):
        """Test basic frequency calculation."""
        records = [
            make_stake_record("01.01.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                             11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
            make_stake_record("02.01.2024", [1, 2, 21, 22, 23, 24, 25, 26, 27, 28,
                                             29, 30, 31, 32, 33, 34, 35, 36, 37, 38]),
        ]

        result = calculate_draw_frequency_from_records(records)

        # Numbers 1 and 2 appear in both draws
        assert result[1] == 1.0  # 2/2
        assert result[2] == 1.0  # 2/2

        # Number 3 appears in one draw
        assert result[3] == 0.5  # 1/2

        # Number 70 never appears
        assert result[70] == 0.0

    def test_empty_records(self):
        """Test with empty records list."""
        result = calculate_draw_frequency_from_records([])
        assert result == {}


class TestAnalyzeStakeCorrelation:
    """Tests for analyze_stake_correlation function."""

    def test_empty_records(self):
        """Test with empty records."""
        result = analyze_stake_correlation([])

        assert result.n_samples == 0
        assert not result.is_significant

    def test_insufficient_records(self):
        """Test with insufficient records."""
        records = [
            make_stake_record("01.01.2024", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                                             11, 12, 13, 14, 15, 16, 17, 18, 19, 20]),
        ]

        result = analyze_stake_correlation(records)

        # Only 1 record
        assert result.n_draws == 1

    def test_result_structure(self):
        """Test that result has correct structure."""
        records = [
            make_stake_record(
                f"{i:02d}.01.2024",
                list(range(1, 21)),
                spieleinsatz=float(100000 + i * 1000),
            )
            for i in range(1, 31)
        ]

        result = analyze_stake_correlation(records)

        assert isinstance(result, StakeCorrelationResult)
        assert hasattr(result, "pearson_r")
        assert hasattr(result, "pearson_p")
        assert hasattr(result, "spearman_r")
        assert hasattr(result, "spearman_p")
        assert hasattr(result, "is_significant")
        assert hasattr(result, "n_samples")
        assert hasattr(result, "n_draws")


class TestClassifyNumbersByStake:
    """Tests for classify_numbers_by_stake function."""

    def test_classification_output(self):
        """Test that classification produces correct output."""
        records = [
            make_stake_record(
                f"{i:02d}.01.2024",
                list(range(1, 21)),
                spieleinsatz=float(100000 + i * 1000),
            )
            for i in range(1, 31)
        ]

        result = classify_numbers_by_stake(records)

        assert len(result) == 70

        # Check structure
        for classification in result:
            assert isinstance(classification, NumberStakeClassification)
            assert 1 <= classification.number <= 70
            assert classification.classification in [
                "low_stake", "neutral", "high_stake", "no_data"
            ]

    def test_threshold_effect(self):
        """Test that threshold affects classification counts."""
        records = [
            make_stake_record(
                f"{i:02d}.01.2024",
                list(range(1, 21)),
                spieleinsatz=float(np.random.uniform(50000, 150000)),
            )
            for i in range(1, 31)
        ]

        # Lower threshold = more extreme classifications
        result_low = classify_numbers_by_stake(records, threshold_std=0.5)
        result_high = classify_numbers_by_stake(records, threshold_std=2.0)

        low_stake_low = sum(
            1 for c in result_low if c.classification == "low_stake"
        )
        low_stake_high = sum(
            1 for c in result_high if c.classification == "low_stake"
        )

        # Higher threshold should result in fewer extreme classifications
        assert low_stake_low >= low_stake_high

    def test_empty_records(self):
        """Test with empty records."""
        result = classify_numbers_by_stake([])
        assert result == []


class TestStakeCorrelationResultDataclass:
    """Tests for StakeCorrelationResult dataclass."""

    def test_frozen(self):
        """Test that result is immutable."""
        result = StakeCorrelationResult(
            pearson_r=0.5,
            pearson_p=0.01,
            spearman_r=0.4,
            spearman_p=0.02,
            is_significant=True,
            n_samples=70,
            n_draws=100,
        )

        with pytest.raises(AttributeError):
            result.pearson_r = 0.9  # type: ignore

    def test_significance_flag(self):
        """Test is_significant reflects p-values correctly."""
        significant = StakeCorrelationResult(
            pearson_r=0.5,
            pearson_p=0.01,  # < 0.05
            spearman_r=0.4,
            spearman_p=0.02,
            is_significant=True,
            n_samples=70,
            n_draws=100,
        )

        not_significant = StakeCorrelationResult(
            pearson_r=0.1,
            pearson_p=0.5,  # >= 0.05
            spearman_r=0.05,
            spearman_p=0.7,
            is_significant=False,
            n_samples=70,
            n_draws=100,
        )

        assert significant.is_significant
        assert not not_significant.is_significant


class TestStakeDrawRecord:
    """Tests for StakeDrawRecord dataclass."""

    def test_creation(self):
        """Test creating a StakeDrawRecord."""
        record = StakeDrawRecord(
            date=datetime(2024, 1, 1),
            numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            spieleinsatz=342774.0,
            total_gewinner=55533,
            total_auszahlung=173458.0,
            restbetrag=169316.0,
            kasse=169316.0,
        )

        assert record.date == datetime(2024, 1, 1)
        assert len(record.numbers) == 20
        assert record.spieleinsatz == 342774.0
        assert record.total_gewinner == 55533


class TestAnalyzeHighStakePopularityBias:
    """Tests for analyze_high_stake_popularity_bias function (HOUSE-002)."""

    def test_empty_records(self):
        """Test with empty records returns zero result."""
        result = analyze_high_stake_popularity_bias([])

        assert isinstance(result, HighStakePopularityResult)
        assert result.n_draws == 0
        assert result.spearman_r == 0.0
        assert result.spearman_p == 1.0
        assert not result.is_significant
        assert not result.supports_hypothesis

    def test_insufficient_records(self):
        """Test with insufficient records (< 20) returns zero result."""
        records = [
            make_stake_record(
                f"{i:02d}.01.2024",
                list(range(1, 21)),
                spieleinsatz=float(100000 + i * 1000),
            )
            for i in range(1, 10)  # Only 9 records
        ]

        result = analyze_high_stake_popularity_bias(records)

        assert result.n_draws == 9
        assert not result.is_significant

    def test_result_structure(self):
        """Test that result has correct structure."""
        records = [
            make_stake_record(
                f"{i:02d}.01.2024",
                list(range(1, 21)),
                spieleinsatz=float(100000 + i * 1000),
            )
            for i in range(1, 31)  # 30 records
        ]

        result = analyze_high_stake_popularity_bias(records)

        assert isinstance(result, HighStakePopularityResult)
        assert hasattr(result, "spearman_r")
        assert hasattr(result, "spearman_p")
        assert hasattr(result, "is_significant")
        assert hasattr(result, "supports_hypothesis")
        assert hasattr(result, "n_draws")
        assert hasattr(result, "n_high_stake")
        assert hasattr(result, "high_stake_threshold")
        assert hasattr(result, "mean_unpopular_ratio_high")
        assert hasattr(result, "mean_unpopular_ratio_low")

        assert result.n_draws == 30
        # Top 25% of 30 = ~8 records
        assert result.n_high_stake > 0

    def test_high_stake_threshold_percentile(self):
        """Test that high-stake threshold is correctly calculated."""
        # Create records with distinct stakes
        records = [
            make_stake_record(
                f"{i:02d}.01.2024",
                list(range(1, 21)),
                spieleinsatz=float(i * 10000),  # 10000, 20000, ..., 300000
            )
            for i in range(1, 31)
        ]

        result = analyze_high_stake_popularity_bias(
            records, high_stake_percentile=0.75
        )

        # 75th percentile of 10000..300000 should be around 230000
        assert result.high_stake_threshold > 200000
        assert result.high_stake_threshold < 250000

    def test_custom_popularity_scores(self):
        """Test with custom popularity scores."""
        records = [
            make_stake_record(
                f"{i:02d}.01.2024",
                list(range(1, 21)),
                spieleinsatz=float(100000 + i * 1000),
            )
            for i in range(1, 31)
        ]

        # Custom popularity: numbers 1-35 are popular, 36-70 unpopular
        custom_popularity = {n: 1.0 if n <= 35 else 0.0 for n in range(1, 71)}

        result = analyze_high_stake_popularity_bias(
            records, popularity_scores=custom_popularity
        )

        assert isinstance(result, HighStakePopularityResult)
        # With numbers 1-20 drawn, all are "popular", so unpopular ratio = 0
        assert result.mean_unpopular_ratio_high == 0.0
        assert result.mean_unpopular_ratio_low == 0.0

    def test_correlation_threshold_effect(self):
        """Test that correlation threshold affects hypothesis support."""
        # Generate dates across multiple months to avoid invalid dates
        records = []
        for month in range(1, 5):  # 4 months
            for day in range(1, 26):  # 25 days per month = 100 records
                idx = (month - 1) * 25 + day
                records.append(
                    make_stake_record(
                        f"{day:02d}.{month:02d}.2024",
                        list(range(1, 21)),
                        spieleinsatz=float(100000 + idx * 1000),
                    )
                )

        # With strict threshold, less likely to support
        result_strict = analyze_high_stake_popularity_bias(
            records, correlation_threshold=0.5
        )

        # With loose threshold, more likely to support
        result_loose = analyze_high_stake_popularity_bias(
            records, correlation_threshold=0.01
        )

        # Strict threshold requires stronger correlation
        # If correlation is weak, strict will reject, loose might accept
        if result_loose.is_significant and abs(result_loose.spearman_r) < 0.5:
            assert not result_strict.supports_hypothesis or result_loose.supports_hypothesis

    def test_result_frozen(self):
        """Test that result is immutable."""
        result = HighStakePopularityResult(
            spearman_r=0.2,
            spearman_p=0.01,
            is_significant=True,
            supports_hypothesis=True,
            n_draws=100,
            n_high_stake=25,
            high_stake_threshold=200000.0,
            mean_unpopular_ratio_high=0.55,
            mean_unpopular_ratio_low=0.45,
        )

        with pytest.raises(AttributeError):
            result.spearman_r = 0.9  # type: ignore
