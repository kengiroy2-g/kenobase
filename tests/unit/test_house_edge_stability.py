"""Unit tests for HOUSE-003: House-Edge Stability Analysis."""

from __future__ import annotations

from datetime import datetime

import pytest

from kenobase.analysis.house_edge_stability import (
    CV_STABILITY_THRESHOLD,
    DEFAULT_WINDOWS,
    HouseEdgeStabilityResult,
    RollingWindowResult,
    analyze_house_edge_stability,
    analyze_single_window,
    calculate_rolling_cv,
    result_to_dict,
)
from kenobase.analysis.stake_correlation import StakeDrawRecord


def make_record(
    date: datetime,
    restbetrag: float,
    total_auszahlung: float = 100000.0,
) -> StakeDrawRecord:
    """Create a StakeDrawRecord for testing."""
    return StakeDrawRecord(
        date=date,
        numbers=list(range(1, 21)),
        spieleinsatz=500000.0,
        total_gewinner=1000,
        total_auszahlung=total_auszahlung,
        restbetrag=restbetrag,
        kasse=1000000.0,
    )


class TestCalculateRollingCV:
    """Tests for calculate_rolling_cv function."""

    def test_basic_cv_calculation(self) -> None:
        """Test basic CV calculation with known values."""
        # Constant values should have CV = 0
        values = [100.0, 100.0, 100.0, 100.0, 100.0]
        cv_values, mean_values, std_values = calculate_rolling_cv(values, 3)

        assert len(cv_values) == 3  # 5 - 3 + 1 = 3 windows
        for cv in cv_values:
            assert cv == pytest.approx(0.0, abs=1e-10)

    def test_variable_values(self) -> None:
        """Test CV calculation with variable values."""
        # Values with known variance
        values = [100.0, 200.0, 100.0, 200.0, 100.0]
        cv_values, mean_values, std_values = calculate_rolling_cv(values, 3)

        assert len(cv_values) == 3
        # Each window has values like [100, 200, 100] with mean=133.33 and std~47.14
        # CV = 47.14/133.33 = 0.353
        for cv in cv_values:
            assert cv > 0.0

    def test_insufficient_data(self) -> None:
        """Test handling of insufficient data."""
        values = [100.0, 200.0]
        cv_values, mean_values, std_values = calculate_rolling_cv(values, 5)

        assert cv_values == []
        assert mean_values == []
        assert std_values == []

    def test_window_count(self) -> None:
        """Test correct number of windows produced."""
        values = [float(i) for i in range(10)]

        for window_size in [3, 5, 7]:
            cv_values, _, _ = calculate_rolling_cv(values, window_size)
            expected_count = len(values) - window_size + 1
            assert len(cv_values) == expected_count


class TestAnalyzeSingleWindow:
    """Tests for analyze_single_window function."""

    def test_stable_window(self) -> None:
        """Test detection of stable (low CV) window."""
        # Low variance values - CV should be < 15%
        values = [1000.0 + i * 10 for i in range(30)]  # Linear increase, low relative variance
        result = analyze_single_window(values, 7)

        assert result.window_size == 7
        assert result.n_windows == 24  # 30 - 7 + 1
        assert result.cv_mean < CV_STABILITY_THRESHOLD  # Should be stable
        assert result.is_stable is True

    def test_unstable_window(self) -> None:
        """Test detection of unstable (high CV) window."""
        # High variance values alternating between low and high
        values = []
        for i in range(30):
            values.append(100.0 if i % 2 == 0 else 1000.0)

        result = analyze_single_window(values, 7)

        assert result.window_size == 7
        assert result.cv_mean > CV_STABILITY_THRESHOLD  # Should be unstable
        assert result.is_stable is False

    def test_empty_values(self) -> None:
        """Test handling of empty values."""
        result = analyze_single_window([], 7)

        assert result.n_windows == 0
        assert result.is_stable is False


class TestAnalyzeHouseEdgeStability:
    """Tests for analyze_house_edge_stability function."""

    def test_basic_analysis(self) -> None:
        """Test basic analysis with sample records."""
        # Create 50 records with stable restbetrag
        records = []
        base_date = datetime(2023, 1, 1)
        for i in range(50):
            date = datetime(2023, 1, 1 + i % 28, 12, 0, 0)
            if i >= 28:
                date = datetime(2023, 2, 1 + (i - 28) % 28, 12, 0, 0)
            # Stable values with small variation
            restbetrag = 150000.0 + (i % 5) * 1000
            records.append(make_record(date, restbetrag))

        result = analyze_house_edge_stability(records, windows=[7, 14])

        assert result.n_records == 50
        assert result.field_analyzed == "restbetrag"
        assert 7 in result.windows
        assert 14 in result.windows

    def test_empty_records(self) -> None:
        """Test handling of empty records list."""
        result = analyze_house_edge_stability([])

        assert result.n_records == 0
        assert result.hypothesis_supported is False

    def test_hypothesis_support_logic(self) -> None:
        """Test that hypothesis is supported when >= 2 windows are stable."""
        # Create records with very stable values (constant)
        records = []
        for i in range(100):
            date = datetime(2023, 1, 1) if i == 0 else datetime(2023, 4, 10)
            # Use different dates to avoid duplicates
            date = datetime(2023, 1 + i // 30, 1 + i % 28)
            records.append(make_record(date, 150000.0))  # Constant value

        result = analyze_house_edge_stability(records, windows=[7, 14, 30])

        # All windows should be stable (CV = 0 for constant values)
        assert result.stable_count == 3
        assert result.hypothesis_supported is True


class TestResultToDict:
    """Tests for result_to_dict function."""

    def test_basic_conversion(self) -> None:
        """Test basic dict conversion."""
        result = HouseEdgeStabilityResult(
            n_records=100,
            date_range_start=datetime(2023, 1, 1),
            date_range_end=datetime(2023, 12, 31),
            field_analyzed="restbetrag",
            windows={
                7: RollingWindowResult(
                    window_size=7,
                    n_windows=94,
                    cv_mean=0.12,
                    cv_std=0.02,
                    cv_min=0.08,
                    cv_max=0.18,
                    cv_values=tuple(),
                    is_stable=True,
                )
            },
            stable_count=1,
            total_windows=1,
            hypothesis_supported=False,
            cv_threshold=0.15,
        )

        d = result_to_dict(result)

        assert d["n_records"] == 100
        assert d["field_analyzed"] == "restbetrag"
        assert "7" in d["windows"]
        assert d["windows"]["7"]["cv_mean"] == 0.12
        assert d["windows"]["7"]["is_stable"] is True

    def test_datetime_serialization(self) -> None:
        """Test datetime fields are properly serialized."""
        result = HouseEdgeStabilityResult(
            n_records=10,
            date_range_start=datetime(2023, 6, 15, 14, 30, 0),
            date_range_end=datetime(2023, 6, 25, 16, 45, 0),
            field_analyzed="restbetrag",
        )

        d = result_to_dict(result)

        assert "2023-06-15" in d["date_range_start"]
        assert "2023-06-25" in d["date_range_end"]


class TestDefaultConstants:
    """Tests for module constants."""

    def test_default_windows(self) -> None:
        """Test DEFAULT_WINDOWS contains expected values."""
        assert 7 in DEFAULT_WINDOWS
        assert 14 in DEFAULT_WINDOWS
        assert 30 in DEFAULT_WINDOWS

    def test_cv_threshold(self) -> None:
        """Test CV_STABILITY_THRESHOLD is 15%."""
        assert CV_STABILITY_THRESHOLD == 0.15
