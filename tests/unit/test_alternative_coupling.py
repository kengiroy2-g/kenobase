"""Unit tests for alternative_coupling module."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from kenobase.analysis.alternative_coupling import (
    CouplingResult,
    apply_fdr_correction,
    dtw_distance,
    granger_causality_test,
    mutual_information_lagged,
    run_all_methods,
    transfer_entropy,
)


@pytest.fixture
def correlated_series() -> tuple[np.ndarray, np.ndarray]:
    """Create correlated time series for testing."""
    np.random.seed(42)
    n = 200

    # X causes Y with lag 1
    x = np.random.randn(n)
    noise = np.random.randn(n) * 0.5
    y = np.zeros(n)
    y[1:] = 0.7 * x[:-1] + noise[1:]

    return x, y


@pytest.fixture
def uncorrelated_series() -> tuple[np.ndarray, np.ndarray]:
    """Create uncorrelated time series for testing."""
    np.random.seed(123)
    n = 200

    x = np.random.randn(n)
    y = np.random.randn(n)

    return x, y


class TestTransferEntropy:
    """Tests for transfer_entropy function."""

    def test_correlated_series_has_higher_te(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that correlated series have higher TE."""
        x, y = correlated_series

        result = transfer_entropy(x, y, lag=1, n_permutations=30, k_neighbors=4)

        assert isinstance(result, CouplingResult)
        assert result.method == "transfer_entropy"
        # TE should be positive for causal relationship
        assert result.statistic >= 0
        assert result.n_samples > 0

    def test_uncorrelated_series_low_te(
        self, uncorrelated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that uncorrelated series have low TE."""
        x, y = uncorrelated_series

        result = transfer_entropy(x, y, lag=1, n_permutations=30, k_neighbors=4)

        # TE should resemble null (high p-value)
        assert result.p_value >= 0.05

    def test_short_series_handling(self) -> None:
        """Test handling of too-short series."""
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])

        result = transfer_entropy(x, y, lag=1, k_history_target=3, n_permutations=10)

        # Should return valid result with p_value=1.0
        assert result.p_value == 1.0

    def test_result_attributes(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that result has all required attributes."""
        x, y = correlated_series

        result = transfer_entropy(x, y, lag=2, n_permutations=20, k_neighbors=4)

        assert hasattr(result, "source")
        assert hasattr(result, "target")
        assert hasattr(result, "method")
        assert hasattr(result, "statistic")
        assert hasattr(result, "p_value")
        assert hasattr(result, "q_value")
        assert hasattr(result, "lag")
        assert hasattr(result, "n_samples")
        assert result.lag == 2
        assert result.k_history_target >= 1

    def test_directionality_te_forward_vs_reverse(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Forward direction should have higher TE than reverse for causal data."""
        x, y = correlated_series

        forward = transfer_entropy(x, y, lag=1, n_permutations=25, k_neighbors=4)
        reverse = transfer_entropy(y, x, lag=1, n_permutations=25, k_neighbors=4)

        assert forward.statistic >= reverse.statistic
        assert 0 <= forward.p_value <= 1
        assert 0 <= reverse.p_value <= 1


class TestMutualInformationLagged:
    """Tests for mutual_information_lagged function."""

    def test_correlated_series_has_higher_mi(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that correlated series have higher MI."""
        x, y = correlated_series

        result = mutual_information_lagged(x, y, lag=1, n_permutations=30, k_neighbors=4)

        assert isinstance(result, CouplingResult)
        assert result.method == "mutual_information"
        assert result.statistic >= 0

    def test_uncorrelated_series_low_mi(
        self, uncorrelated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that uncorrelated series have low MI."""
        x, y = uncorrelated_series

        result = mutual_information_lagged(x, y, lag=1, n_permutations=30, k_neighbors=4)

        # MI should be close to null for independent series (high p-value)
        assert result.p_value >= 0.05

    def test_different_bin_sizes(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test with different neighbor settings."""
        x, y = correlated_series

        result_5 = mutual_information_lagged(x, y, lag=1, k_neighbors=3, n_permutations=15)
        result_20 = mutual_information_lagged(x, y, lag=1, k_neighbors=8, n_permutations=15)

        # Both should return valid results
        assert result_5.statistic >= 0
        assert result_20.statistic >= 0

    def test_directionality_cmi_forward_vs_reverse(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Forward CMI should exceed reverse on causal synthetic data."""
        x, y = correlated_series

        forward = mutual_information_lagged(
            x, y, lag=1, k_neighbors=4, n_permutations=25, k_history_target=1
        )
        reverse = mutual_information_lagged(
            y, x, lag=1, k_neighbors=4, n_permutations=25, k_history_target=1
        )

        assert forward.statistic >= reverse.statistic


class TestDTWDistance:
    """Tests for dtw_distance function."""

    def test_identical_series(self) -> None:
        """Test that identical series have minimal DTW distance."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = x.copy()

        result = dtw_distance(x, y, window_size=20, n_permutations=30)

        assert isinstance(result, CouplingResult)
        assert result.method == "dtw"
        # Negative distance (higher = more similar)
        assert result.statistic <= 0  # DTW=0 for identical -> -0

    def test_different_series(
        self, uncorrelated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that different series have larger DTW distance."""
        x, y = uncorrelated_series

        result = dtw_distance(x, y, window_size=30, n_permutations=30)

        # Should have some negative distance
        assert result.statistic != 0

    def test_short_series_handling(self) -> None:
        """Test handling of too-short series."""
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])

        result = dtw_distance(x, y, window_size=10, n_permutations=10)

        # Should return valid result
        assert result.p_value == 1.0

    def test_sakoe_chiba_band_constraint(self) -> None:
        """Test that Sakoe-Chiba band produces valid results and updates method name."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)

        # Without band (full O(n²))
        result_no_band = dtw_distance(x, y, window_size=20, n_permutations=20)

        # With band (O(n*band))
        result_with_band = dtw_distance(
            x, y, window_size=20, n_permutations=20, sakoe_chiba_band=5
        )

        # Both should produce valid results
        assert isinstance(result_no_band, CouplingResult)
        assert isinstance(result_with_band, CouplingResult)
        assert result_no_band.method == "dtw"
        assert result_with_band.method == "dtw_band5"
        assert 0 <= result_no_band.p_value <= 1
        assert 0 <= result_with_band.p_value <= 1

    def test_sakoe_chiba_band_identical_series(self) -> None:
        """Test that Sakoe-Chiba band still detects identical series."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = x.copy()

        result = dtw_distance(
            x, y, window_size=20, n_permutations=30, sakoe_chiba_band=3
        )

        # Identical series should still have near-zero distance
        assert result.method == "dtw_band3"
        assert result.statistic <= 0  # Negative (closer to 0 = more similar)

    def test_multiscale_windows(self) -> None:
        """Test DTW with multiscale windows."""
        np.random.seed(42)
        x = np.random.randn(200)
        y = np.random.randn(200)

        result = dtw_distance(
            x, y,
            window_size=30,  # default fallback
            n_permutations=20,
            multiscale_windows=[20, 40, 60],
        )

        assert isinstance(result, CouplingResult)
        assert 0 <= result.p_value <= 1
        # n_samples should reflect actual data used
        assert result.n_samples == 200

    def test_multiscale_with_band(self) -> None:
        """Test combining multiscale windows with Sakoe-Chiba band."""
        np.random.seed(42)
        x = np.random.randn(150)
        y = np.random.randn(150)

        result = dtw_distance(
            x, y,
            window_size=25,
            n_permutations=15,
            sakoe_chiba_band=4,
            multiscale_windows=[15, 30, 50],
        )

        assert isinstance(result, CouplingResult)
        assert result.method == "dtw_band4"
        assert 0 <= result.p_value <= 1

    def test_sakoe_chiba_beats_null_on_coupled_series(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that DTW with band detects coupled series (acceptance criterion)."""
        x, y = correlated_series

        result = dtw_distance(
            x, y, window_size=30, n_permutations=100, sakoe_chiba_band=5
        )

        # For correlated series, p-value should be low (significant coupling)
        # Acceptance criterion: p < 0.05 on known-coupled series
        assert result.p_value < 0.05, f"Expected p < 0.05, got {result.p_value}"
        assert result.is_significant  # Use truthiness check for numpy bool compatibility


class TestGrangerCausality:
    """Tests for granger_causality_test function."""

    def test_result_structure(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that Granger test returns valid result structure."""
        x, y = correlated_series

        result = granger_causality_test(x, y, max_lag=2, n_permutations=20)

        assert isinstance(result, CouplingResult)
        assert result.method == "granger"
        # Result should have valid attributes
        assert 0 <= result.p_value <= 1

    def test_short_series_handling(self) -> None:
        """Test handling of too-short series."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([6, 7, 8, 9, 10])

        result = granger_causality_test(x, y, max_lag=3, n_permutations=10)

        # Should return result without crashing
        assert isinstance(result, CouplingResult)


class TestRunAllMethods:
    """Tests for run_all_methods function."""

    def test_runs_all_methods(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that all methods are run."""
        x, y = correlated_series

        results = run_all_methods(
            x, y,
            source_name="X",
            target_name="Y",
            lag=1,
            n_permutations=20,
        )

        assert len(results) == 4  # granger, te, mi, dtw
        methods = {r.method for r in results}
        assert "granger" in methods
        assert "transfer_entropy" in methods
        assert "mutual_information" in methods
        assert "dtw" in methods

    def test_preserves_names(
        self, correlated_series: tuple[np.ndarray, np.ndarray]
    ) -> None:
        """Test that source/target names are preserved."""
        x, y = correlated_series

        results = run_all_methods(
            x, y,
            source_name="KENO",
            target_name="LOTTO",
            lag=1,
            n_permutations=10,
        )

        for r in results:
            assert r.source == "KENO"
            assert r.target == "LOTTO"


class TestApplyFDRCorrection:
    """Tests for apply_fdr_correction function."""

    def test_empty_results(self) -> None:
        """Test with empty results list."""
        corrected = apply_fdr_correction([])
        assert corrected == []

    def test_single_result(self) -> None:
        """Test with single result."""
        result = CouplingResult(
            source="X",
            target="Y",
            method="test",
            statistic=1.0,
            p_value=0.01,
            q_value=0.01,
            lag=1,
            n_samples=100,
            null_mean=0.0,
            null_std=1.0,
            is_significant=True,
        )

        corrected = apply_fdr_correction([result])

        assert len(corrected) == 1
        assert corrected[0].p_value == 0.01
        # Single test: q_value == p_value
        assert corrected[0].q_value == 0.01

    def test_multiple_results_correction(self) -> None:
        """Test FDR correction with multiple results."""
        results = [
            CouplingResult(
                source="X",
                target="Y",
                method="test",
                statistic=1.0,
                p_value=0.01,  # Significant
                q_value=0.01,
                lag=1,
                n_samples=100,
                null_mean=0.0,
                null_std=1.0,
                is_significant=True,
            ),
            CouplingResult(
                source="X",
                target="Y",
                method="test2",
                statistic=0.5,
                p_value=0.04,  # Borderline
                q_value=0.04,
                lag=1,
                n_samples=100,
                null_mean=0.0,
                null_std=1.0,
                is_significant=True,
            ),
            CouplingResult(
                source="X",
                target="Y",
                method="test3",
                statistic=0.1,
                p_value=0.50,  # Not significant
                q_value=0.50,
                lag=1,
                n_samples=100,
                null_mean=0.0,
                null_std=1.0,
                is_significant=False,
            ),
        ]

        corrected = apply_fdr_correction(results, alpha=0.05)

        assert len(corrected) == 3
        # q-values should be >= p-values after BH correction
        for orig, corr in zip(results, corrected):
            assert corr.q_value >= orig.p_value
        # Least significant p-value has q_value = p_value (max)
        assert corrected[2].q_value <= 1.0


class TestCliSmoke:
    """Smoke tests for the CLI wrapper."""

    def test_cli_runs_with_synthetic_data(self, tmp_path: Path) -> None:
        """CLI should run end-to-end on synthetic draws."""
        output_path = tmp_path / "alternative_coupling.json"
        cmd = [
            sys.executable,
            "scripts/analyze_alternative_methods.py",
            "--method",
            "te",
            "--lags",
            "1",
            "--n-permutations",
            "3",
            "--k-neighbors",
            "3",
            "--use-synthetic",
            "--output",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert output_path.exists()
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert payload["config"]["synthetic"] is True
        assert payload["summary"]["total_tests"] >= 1
