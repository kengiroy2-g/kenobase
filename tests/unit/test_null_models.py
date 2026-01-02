"""
Unit tests for null_models.py

Tests permutation-based null models for statistical testing:
- schedule_permutation: weekday-preserving shuffling
- block_permutation: block-based shuffling
- NullModelRunner: integrated test runner
- FDR correction: Benjamini-Hochberg procedure

Author: EXECUTOR (TASK NULL-001)
Date: 2025-12-30
"""

from datetime import datetime, timedelta

import numpy as np
import pytest
from numpy.random import default_rng

from kenobase.analysis.null_models import (
    NullModelRunner,
    NullModelTestResult,
    PermutationResult,
    FDRResult,
    benjamini_hochberg_fdr,
    block_permutation,
    calculate_empirical_p_value,
    iid_permutation,
    run_axiom_prediction_test,
    schedule_permutation,
)
from kenobase.core.axioms import NullModelType


class TestSchedulePermutation:
    """Tests for schedule_permutation function."""

    def test_preserves_weekday_structure(self):
        """Verify that weekday distribution is preserved after permutation."""
        # Create data spanning 3 weeks with known dates
        base_date = datetime(2024, 1, 1)  # Monday
        dates = [base_date + timedelta(days=i) for i in range(21)]
        data = np.arange(21, dtype=float)

        rng = default_rng(42)
        permuted = schedule_permutation(data, dates, rng)

        # Check that weekday groups still have same values (just shuffled within)
        for weekday in range(7):
            orig_indices = [i for i, d in enumerate(dates) if d.weekday() == weekday]
            orig_values = set(data[orig_indices])
            perm_values = set(permuted[orig_indices])
            assert orig_values == perm_values, f"Weekday {weekday} values changed"

    def test_raises_on_length_mismatch(self):
        """Verify error when data and dates have different lengths."""
        data = np.array([1, 2, 3])
        dates = [datetime(2024, 1, 1), datetime(2024, 1, 2)]

        with pytest.raises(ValueError, match="length"):
            schedule_permutation(data, dates)

    def test_reproducible_with_seed(self):
        """Verify permutation is reproducible with same seed."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(14)]
        data = np.arange(14, dtype=float)

        rng1 = default_rng(123)
        rng2 = default_rng(123)

        result1 = schedule_permutation(data, dates, rng1)
        result2 = schedule_permutation(data, dates, rng2)

        np.testing.assert_array_equal(result1, result2)

    def test_single_day_weekday(self):
        """Verify single-day weekdays are not shuffled."""
        # Only one Monday
        dates = [datetime(2024, 1, 1)]  # Monday
        data = np.array([42.0])

        permuted = schedule_permutation(data, dates)
        assert permuted[0] == 42.0


class TestBlockPermutation:
    """Tests for block_permutation function."""

    def test_preserves_block_structure(self):
        """Verify that within-block order is preserved."""
        # 3 complete weeks
        data = np.arange(21, dtype=float)
        rng = default_rng(42)

        permuted = block_permutation(data, block_size=7, rng=rng)

        # Extract blocks from permuted data
        blocks = [permuted[i * 7 : (i + 1) * 7] for i in range(3)]

        # Each block should be a complete week from original (check pattern)
        for block in blocks:
            # Block should have consecutive pattern (e.g., 0-6, 7-13, or 14-20)
            diffs = np.diff(block)
            assert np.all(diffs == 1), "Block internal structure not preserved"

    def test_handles_remainder(self):
        """Verify remainder handling when data length not divisible by block_size."""
        data = np.arange(10, dtype=float)  # 10 elements, block_size=7
        rng = default_rng(42)

        permuted = block_permutation(data, block_size=7, rng=rng)

        # Should have 10 elements
        assert len(permuted) == 10

        # Remainder (last 3) should be preserved
        # Note: remainder stays at end, not shuffled
        assert set(permuted[7:]) == {7, 8, 9}

    def test_reproducible_with_seed(self):
        """Verify block permutation is reproducible."""
        data = np.arange(28, dtype=float)

        rng1 = default_rng(456)
        rng2 = default_rng(456)

        result1 = block_permutation(data, block_size=7, rng=rng1)
        result2 = block_permutation(data, block_size=7, rng=rng2)

        np.testing.assert_array_equal(result1, result2)

    def test_empty_data(self):
        """Verify handling of empty data."""
        data = np.array([])
        permuted = block_permutation(data, block_size=7)
        assert len(permuted) == 0


class TestIidPermutation:
    """Tests for iid_permutation function."""

    def test_preserves_values(self):
        """Verify that all values are preserved after shuffle."""
        data = np.array([1, 2, 3, 4, 5])
        permuted = iid_permutation(data, rng=default_rng(42))

        assert set(permuted) == set(data)
        assert len(permuted) == len(data)

    def test_reproducible(self):
        """Verify reproducibility with seed."""
        data = np.arange(100)

        result1 = iid_permutation(data, rng=default_rng(789))
        result2 = iid_permutation(data, rng=default_rng(789))

        np.testing.assert_array_equal(result1, result2)


class TestEmpiricalPValue:
    """Tests for calculate_empirical_p_value function."""

    def test_less_direction(self):
        """Test p-value for 'less' direction."""
        observed = 2.0
        null = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        # P(X <= 2) = 2/5 values, corrected = (2+1)/(5+1) = 0.5
        p_value = calculate_empirical_p_value(observed, null, direction="less")
        assert p_value == pytest.approx(0.5, abs=0.01)

    def test_greater_direction(self):
        """Test p-value for 'greater' direction."""
        observed = 4.0
        null = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        # P(X >= 4) = 2/5 values, corrected = (2+1)/(5+1) = 0.5
        p_value = calculate_empirical_p_value(observed, null, direction="greater")
        assert p_value == pytest.approx(0.5, abs=0.01)

    def test_extreme_values(self):
        """Test p-value for extreme observations."""
        null = np.arange(100, dtype=float)

        # Very low value
        p_low = calculate_empirical_p_value(-10.0, null, direction="less")
        assert p_low < 0.02  # Should be very significant

        # Very high value
        p_high = calculate_empirical_p_value(110.0, null, direction="greater")
        assert p_high < 0.02


class TestBenjaminiHochbergFDR:
    """Tests for benjamini_hochberg_fdr function."""

    def test_single_significant(self):
        """Test FDR with one significant p-value."""
        p_values = [0.001, 0.5, 0.6, 0.9]
        result = benjamini_hochberg_fdr(p_values, alpha=0.05)

        assert result.n_tests == 4
        assert result.n_significant >= 1
        assert 0 in result.significant_indices  # First one should be significant

    def test_no_significant(self):
        """Test FDR when no tests are significant."""
        p_values = [0.5, 0.6, 0.7, 0.8]
        result = benjamini_hochberg_fdr(p_values, alpha=0.05)

        assert result.n_significant == 0
        assert result.significant_indices == []

    def test_all_significant(self):
        """Test FDR when all tests are significant."""
        p_values = [0.001, 0.002, 0.003, 0.004]
        result = benjamini_hochberg_fdr(p_values, alpha=0.05)

        assert result.n_significant == 4

    def test_empty_input(self):
        """Test FDR with empty input."""
        result = benjamini_hochberg_fdr([], alpha=0.05)

        assert result.n_tests == 0
        assert result.n_significant == 0
        assert result.q_values == []

    def test_q_values_ordering(self):
        """Verify q-values are properly ordered."""
        p_values = [0.01, 0.03, 0.02, 0.05]
        result = benjamini_hochberg_fdr(p_values, alpha=0.1)

        # q-values should be >= original p-values
        for p, q in zip(p_values, result.q_values):
            assert q >= p


class TestNullModelRunner:
    """Tests for NullModelRunner class."""

    def test_schedule_preserving_test(self):
        """Test running a SCHEDULE_PRESERVING null model."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(30)]
        data = np.random.default_rng(42).normal(0, 1, 30)

        runner = NullModelRunner(n_permutations=100, seed=42)
        result = runner.run_test(
            data=data,
            statistic_fn=np.mean,
            null_model_type=NullModelType.SCHEDULE_PRESERVING,
            dates=dates,
            direction="two-sided",
        )

        assert isinstance(result, PermutationResult)
        assert result.n_permutations == 100
        assert result.null_model_type == NullModelType.SCHEDULE_PRESERVING
        assert 0 <= result.p_value <= 1

    def test_block_permutation_test(self):
        """Test running a BLOCK_PERMUTATION null model."""
        data = np.random.default_rng(42).normal(0, 1, 28)

        runner = NullModelRunner(n_permutations=100, seed=42)
        result = runner.run_test(
            data=data,
            statistic_fn=np.std,
            null_model_type=NullModelType.BLOCK_PERMUTATION,
            block_size=7,
            direction="greater",
        )

        assert isinstance(result, PermutationResult)
        assert result.null_model_type == NullModelType.BLOCK_PERMUTATION

    def test_requires_dates_for_schedule(self):
        """Verify SCHEDULE_PRESERVING raises without dates."""
        data = np.arange(10, dtype=float)
        runner = NullModelRunner(n_permutations=10)

        with pytest.raises(ValueError, match="dates"):
            runner.run_test(
                data=data,
                statistic_fn=np.mean,
                null_model_type=NullModelType.SCHEDULE_PRESERVING,
            )

    def test_multiple_tests_with_fdr(self):
        """Test running multiple tests with FDR correction."""
        rng = np.random.default_rng(42)

        tests = [
            {
                "data": rng.normal(0, 1, 30),
                "statistic_fn": np.mean,
                "null_model_type": NullModelType.PERMUTATION,
                "direction": "two-sided",
            },
            {
                "data": rng.normal(3, 1, 30),  # Shifted mean - should be significant
                "statistic_fn": np.mean,
                "null_model_type": NullModelType.PERMUTATION,
                "direction": "greater",
            },
        ]

        runner = NullModelRunner(n_permutations=100, seed=42)
        results, fdr = runner.run_multiple_tests(tests, alpha=0.05)

        assert len(results) == 2
        assert isinstance(fdr, FDRResult)
        assert fdr.n_tests == 2


class TestRunAxiomPredictionTest:
    """Tests for run_axiom_prediction_test convenience function."""

    def test_p13_block_permutation(self):
        """Test P1.3 prediction with BLOCK_PERMUTATION null model."""
        # Simulate ROI data
        data = np.random.default_rng(42).normal(-0.5, 0.03, 90)

        result = run_axiom_prediction_test(
            prediction_id="P1.3",
            data=data,
            statistic_fn=lambda x: np.std(x),
            null_model_type=NullModelType.BLOCK_PERMUTATION,
            block_size=7,
            direction="less",
            n_permutations=100,
            seed=42,
        )

        assert isinstance(result, NullModelTestResult)
        assert result.prediction_id == "P1.3"
        assert isinstance(result.is_significant, bool)

    def test_p43_schedule_preserving(self):
        """Test P4.3 prediction with SCHEDULE_PRESERVING null model."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(60)]
        data = np.random.default_rng(42).random(60)

        result = run_axiom_prediction_test(
            prediction_id="P4.3",
            data=data,
            statistic_fn=lambda x: np.corrcoef(x[:-1], x[1:])[0, 1],
            null_model_type=NullModelType.SCHEDULE_PRESERVING,
            dates=dates,
            direction="greater",
            n_permutations=100,
            seed=42,
        )

        assert result.prediction_id == "P4.3"
        assert result.permutation_result.null_model_type == NullModelType.SCHEDULE_PRESERVING

    def test_result_serialization(self):
        """Test that results can be serialized to dict."""
        data = np.arange(20, dtype=float)

        result = run_axiom_prediction_test(
            prediction_id="P6.3",
            data=data,
            statistic_fn=np.mean,
            null_model_type=NullModelType.BLOCK_PERMUTATION,
            n_permutations=50,
            seed=42,
        )

        result_dict = result.to_dict()

        assert "prediction_id" in result_dict
        assert "permutation" in result_dict
        assert "is_significant" in result_dict
        assert result_dict["prediction_id"] == "P6.3"


class TestIntegrationWithAxioms:
    """Integration tests verifying compatibility with axioms.py."""

    def test_all_null_model_types_supported(self):
        """Verify runner handles all NullModelType values."""
        data = np.arange(28, dtype=float)
        dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(28)]
        runner = NullModelRunner(n_permutations=10, seed=42)

        # Test each type that should work
        for null_type in [
            NullModelType.IID,
            NullModelType.PERMUTATION,
            NullModelType.BLOCK_PERMUTATION,
        ]:
            result = runner.run_test(
                data=data,
                statistic_fn=np.mean,
                null_model_type=null_type,
            )
            assert result.null_model_type == null_type

        # SCHEDULE_PRESERVING requires dates
        result = runner.run_test(
            data=data,
            statistic_fn=np.mean,
            null_model_type=NullModelType.SCHEDULE_PRESERVING,
            dates=dates,
        )
        assert result.null_model_type == NullModelType.SCHEDULE_PRESERVING

    def test_predictions_requiring_block_permutation(self):
        """Test predictions P1.3 that requires BLOCK_PERMUTATION."""
        # P1.3: House-Edge variance < 5% between quarters
        quarterly_roi = np.array([-0.48, -0.51, -0.49, -0.52])

        result = run_axiom_prediction_test(
            prediction_id="P1.3",
            data=quarterly_roi,
            statistic_fn=np.std,
            null_model_type=NullModelType.BLOCK_PERMUTATION,
            block_size=1,  # Each quarter is a block
            direction="less",
            n_permutations=100,
            seed=42,
        )

        assert result.prediction_id == "P1.3"
        # Observed std should be low (~0.017)
        assert result.permutation_result.observed_statistic < 0.05
