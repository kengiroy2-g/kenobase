#!/usr/bin/env python3
"""Unit tests for kenobase.analysis.temporal_cycles module (HYP-011)."""

from datetime import datetime

import pytest

from kenobase.analysis.temporal_cycles import (
    TemporalCyclesResult,
    TemporalDimensionResult,
    analyze_dimension,
    analyze_holiday_proximity,
    analyze_number_temporal,
    analyze_temporal_cycles,
    to_dict,
)


class TestAnalyzeDimension:
    """Tests for analyze_dimension function."""

    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        dates = [datetime(2024, 1, i) for i in range(1, 5)]  # Only 4 dates
        result = analyze_dimension(dates, "weekday")
        assert result.n_draws == 4
        assert not result.is_significant
        assert "Insufficient data" in result.interpretation

    def test_weekday_uniform(self):
        """Test uniform weekday distribution."""
        # Create 7 weeks of dates using timedelta
        from datetime import timedelta
        base = datetime(2024, 1, 1)
        dates = [base + timedelta(days=i) for i in range(49)]  # 7 full weeks
        result = analyze_dimension(dates, "weekday")
        assert result.n_draws == 49
        assert result.dimension == "weekday"
        assert len(result.observed_counts) == 7
        # Should not be significant (uniform distribution)
        assert result.p_value > 0.05
        assert not result.is_significant

    def test_weekday_biased(self):
        """Test biased weekday distribution (need >5 expected per category)."""
        # Need enough data: 7 categories * 5 expected = 35 minimum
        # Create 42 Mondays (6 per category expected if uniform, but all Monday)
        from datetime import timedelta
        base = datetime(2024, 1, 1)  # Monday
        dates = [base + timedelta(weeks=i) for i in range(42)]
        result = analyze_dimension(dates, "weekday")
        assert result.n_draws == 42
        assert result.observed_counts[0] == 42  # All Monday
        # Chi-square test should detect this
        assert result.is_significant
        assert result.most_common == "Montag"

    def test_month_uniform(self):
        """Test month distribution over full year."""
        # One draw per day for a full year
        dates = []
        for month in range(1, 13):
            for day in range(1, 28):  # Use 27 days per month for simplicity
                dates.append(datetime(2024, month, day))
        result = analyze_dimension(dates, "month")
        assert result.dimension == "month"
        assert len(result.observed_counts) == 12
        # Should be uniform
        assert result.p_value > 0.05

    def test_year_analysis(self):
        """Test year dimension analysis."""
        dates = []
        # 100 draws in 2022, 100 in 2023, 50 in 2024
        for i in range(100):
            dates.append(datetime(2022, 1, (i % 28) + 1))
            dates.append(datetime(2023, 1, (i % 28) + 1))
        for i in range(50):
            dates.append(datetime(2024, 1, (i % 28) + 1))
        result = analyze_dimension(dates, "year")
        assert result.dimension == "year"
        assert len(result.labels) == 3
        assert "2022" in result.labels
        assert result.is_significant  # Unequal distribution


class TestAnalyzeHolidayProximity:
    """Tests for analyze_holiday_proximity function."""

    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        dates = [datetime(2024, 1, i) for i in range(1, 10)]
        result = analyze_holiday_proximity(dates)
        assert result["status"] == "INSUFFICIENT_DATA"

    def test_normal_distribution(self):
        """Test with normal distribution of dates."""
        # Full year of daily draws
        dates = []
        for month in range(1, 13):
            for day in range(1, 28):
                dates.append(datetime(2024, month, day))
        result = analyze_holiday_proximity(dates, window_days=3)
        assert result["n_draws"] == len(dates)
        assert "observed_rate" in result
        assert "expected_rate" in result
        assert result["window_days"] == 3

    def test_holiday_heavy(self):
        """Test with dates concentrated near holidays."""
        # All dates near Neujahr (Jan 1)
        dates = [datetime(2024, 1, i) for i in range(1, 32)]  # Jan 1-31
        result = analyze_holiday_proximity(dates, window_days=3)
        # Most dates are NOT near holiday (only Jan 1-4 are)
        assert result["near_holiday_count"] == 4  # Jan 1,2,3,4


class TestAnalyzeTemporalCycles:
    """Tests for main analyze_temporal_cycles function."""

    def test_empty_dates(self):
        """Test with empty date list."""
        result = analyze_temporal_cycles([])
        assert result.verdict == "INSUFFICIENT_DATA"
        assert result.confidence == 0.0

    def test_basic_analysis(self):
        """Test basic analysis without per-number."""
        # 100 days of draws
        dates = [datetime(2024, 1, 1) + __import__("datetime").timedelta(days=i)
                 for i in range(100)]
        result = analyze_temporal_cycles(dates)
        assert result.n_draws == 100
        assert result.weekday_analysis is not None
        assert result.month_analysis is not None
        assert result.verdict in ["BESTAETIGT", "NICHT_BESTAETIGT", "UNKLAR"]

    def test_per_number_analysis(self):
        """Test with per-number analysis enabled."""
        dates = [datetime(2024, 1, 1) + __import__("datetime").timedelta(days=i)
                 for i in range(100)]
        # Simulate: each draw has numbers 1-20
        numbers_per_draw = [list(range(1, 21)) for _ in dates]
        result = analyze_temporal_cycles(
            dates,
            numbers_per_draw=numbers_per_draw,
            analyze_per_number=True,
            numbers_to_analyze=[1, 2, 3],  # Only analyze 3 numbers
        )
        assert len(result.number_analyses) == 3


class TestToDict:
    """Tests for to_dict serialization."""

    def test_serialization(self):
        """Test that result can be serialized to dict."""
        dates = [datetime(2024, 1, 1) + __import__("datetime").timedelta(days=i)
                 for i in range(50)]
        result = analyze_temporal_cycles(dates)
        output = to_dict(result)
        assert isinstance(output, dict)
        assert output["hypothesis_id"] == "HYP-011"
        assert "weekday_analysis" in output
        assert "verdict" in output

    def test_json_serializable(self):
        """Test that output is JSON-serializable."""
        import json
        dates = [datetime(2024, 1, 1) + __import__("datetime").timedelta(days=i)
                 for i in range(50)]
        result = analyze_temporal_cycles(dates)
        output = to_dict(result)
        # Should not raise
        json_str = json.dumps(output)
        assert isinstance(json_str, str)
