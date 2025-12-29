"""Unit tests for HYP-014 multiweek_timing module."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pytest

from kenobase.analysis.multiweek_timing import (
    ABO_LENGTHS,
    N_POSITION_BINS,
    ChiSquareResult,
    MonteCarloComparison,
    MultiweekTimingResult,
    PositionDistribution,
    SimulationConfig,
    analyze_multiweek_timing,
    calculate_position_distribution,
    chi_square_uniformity_test,
    compare_to_monte_carlo,
    export_result_to_json,
    run_hyp014_analysis,
    simulate_random_abo_starts,
    to_dict,
)


class TestSimulationConfig:
    """Tests fuer SimulationConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SimulationConfig()
        assert config.n_simulations == 10000
        assert config.random_seed == 42
        assert config.abo_lengths == [7, 14, 28]

    def test_custom_config(self):
        """Test custom configuration."""
        config = SimulationConfig(
            n_simulations=5000,
            random_seed=123,
            abo_lengths=[7, 21],
        )
        assert config.n_simulations == 5000
        assert config.random_seed == 123
        assert config.abo_lengths == [7, 21]


class TestSimulateRandomAboStarts:
    """Tests fuer Monte-Carlo Simulation."""

    def test_reproducibility_with_same_seed(self):
        """Test that same seed produces same results."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i * 10) for i in range(20)]
        date_range = (dates[0], dates[-1])

        result1 = simulate_random_abo_starts(
            dates, date_range, abo_length=7, n_simulations=100, random_seed=42
        )
        result2 = simulate_random_abo_starts(
            dates, date_range, abo_length=7, n_simulations=100, random_seed=42
        )

        np.testing.assert_array_equal(result1, result2)

    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i * 10) for i in range(20)]
        date_range = (dates[0], dates[-1])

        result1 = simulate_random_abo_starts(
            dates, date_range, abo_length=7, n_simulations=100, random_seed=42
        )
        result2 = simulate_random_abo_starts(
            dates, date_range, abo_length=7, n_simulations=100, random_seed=123
        )

        assert not np.array_equal(result1, result2)

    def test_mean_ratio_around_half(self):
        """Test that mean position ratio is around 0.5 for uniform distribution."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(365)]
        date_range = (dates[0], dates[-1])

        result = simulate_random_abo_starts(
            dates, date_range, abo_length=7, n_simulations=1000, random_seed=42
        )

        # Mean should be close to 0.5 (uniform distribution)
        assert 0.4 < np.mean(result) < 0.6

    def test_empty_dates(self):
        """Test handling of empty date list."""
        date_range = (datetime(2024, 1, 1), datetime(2024, 12, 31))
        result = simulate_random_abo_starts(
            [], date_range, abo_length=7, n_simulations=100, random_seed=42
        )
        assert len(result) == 100
        assert all(r == 0.5 for r in result)


class TestCalculatePositionDistribution:
    """Tests fuer Position-Verteilungs-Berechnung."""

    def test_uniform_distribution(self):
        """Test with dates evenly spread across abo period."""
        # Create dates at each day of a 7-day period over multiple weeks
        dates = []
        for week in range(10):
            for day in range(7):
                dates.append(datetime(2024, 1, 1) + timedelta(days=week * 7 + day))

        date_range = (dates[0], dates[-1])
        dist = calculate_position_distribution(dates, date_range, abo_length=7)

        assert dist.abo_length == 7
        assert dist.n_jackpots == 70
        assert len(dist.position_counts) == N_POSITION_BINS
        assert sum(dist.position_counts) == 70

    def test_empty_dates(self):
        """Test with empty date list."""
        date_range = (datetime(2024, 1, 1), datetime(2024, 12, 31))
        dist = calculate_position_distribution([], date_range, abo_length=7)

        assert dist.n_jackpots == 0
        assert dist.mean_position_ratio == 0.5
        assert dist.std_position_ratio == 0.0

    def test_position_labels_created(self):
        """Test that position labels are created correctly."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i * 3) for i in range(10)]
        date_range = (dates[0], dates[-1])
        dist = calculate_position_distribution(dates, date_range, abo_length=28)

        assert len(dist.position_labels) == N_POSITION_BINS
        assert "Tag" in dist.position_labels[0]


class TestChiSquareUniformityTest:
    """Tests fuer Chi-Quadrat Test."""

    def test_uniform_distribution_passes(self):
        """Test that uniform distribution passes the test."""
        dist = PositionDistribution(
            abo_length=7,
            n_jackpots=100,
            position_counts=[25, 25, 25, 25],  # Perfect uniform
            position_labels=["Q1", "Q2", "Q3", "Q4"],
            mean_position_ratio=0.5,
            std_position_ratio=0.25,
        )

        result = chi_square_uniformity_test(dist)

        assert result.is_uniform == True  # noqa: E712 - use == for numpy bool
        assert result.p_value > 0.05

    def test_skewed_distribution_fails(self):
        """Test that heavily skewed distribution fails the test."""
        dist = PositionDistribution(
            abo_length=7,
            n_jackpots=100,
            position_counts=[70, 10, 10, 10],  # Very skewed
            position_labels=["Q1", "Q2", "Q3", "Q4"],
            mean_position_ratio=0.2,
            std_position_ratio=0.3,
        )

        result = chi_square_uniformity_test(dist)

        assert result.is_uniform == False  # noqa: E712 - use == for numpy bool
        assert result.p_value < 0.05

    def test_insufficient_data(self):
        """Test handling of insufficient data."""
        dist = PositionDistribution(
            abo_length=7,
            n_jackpots=15,  # Less than 20
            position_counts=[4, 4, 4, 3],
            position_labels=["Q1", "Q2", "Q3", "Q4"],
            mean_position_ratio=0.5,
            std_position_ratio=0.25,
        )

        result = chi_square_uniformity_test(dist)

        assert result.is_uniform is True
        assert result.p_value == 1.0
        assert "Zu wenige Daten" in result.interpretation


class TestCompareToMonteCarlo:
    """Tests fuer Monte-Carlo Vergleich."""

    def test_similar_distribution_not_significant(self):
        """Test that similar distributions are not significant."""
        dist = PositionDistribution(
            abo_length=7,
            n_jackpots=100,
            position_counts=[25, 25, 25, 25],
            position_labels=["Q1", "Q2", "Q3", "Q4"],
            mean_position_ratio=0.5,
            std_position_ratio=0.25,
        )

        # Simulate ratios around 0.5
        simulated = np.random.default_rng(42).normal(0.5, 0.1, 1000)

        result = compare_to_monte_carlo(dist, simulated)

        assert abs(result.z_score) < 2.0
        assert not result.is_significant

    def test_extreme_distribution_is_significant(self):
        """Test that extreme distributions are significant."""
        dist = PositionDistribution(
            abo_length=7,
            n_jackpots=100,
            position_counts=[70, 10, 10, 10],
            position_labels=["Q1", "Q2", "Q3", "Q4"],
            mean_position_ratio=0.1,  # Very early in period
            std_position_ratio=0.2,
        )

        # Simulate ratios around 0.5
        simulated = np.random.default_rng(42).normal(0.5, 0.05, 1000)

        result = compare_to_monte_carlo(dist, simulated)

        assert abs(result.z_score) > 2.0
        assert result.is_significant


class TestAnalyzeMultiweekTiming:
    """Tests fuer Haupt-Analysefunktion."""

    def test_with_uniform_dates(self):
        """Test analysis with uniformly distributed dates."""
        # Create dates spread evenly over a year
        dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(365)]

        config = SimulationConfig(n_simulations=100, random_seed=42)
        result = analyze_multiweek_timing(dates, config)

        assert result.hypothesis_id == "HYP-014"
        assert result.n_jackpots == 365
        assert len(result.distributions) == len(config.abo_lengths)
        assert len(result.chi2_results) == len(config.abo_lengths)
        assert len(result.mc_comparisons) == len(config.abo_lengths)
        assert result.verdict in ["BESTAETIGT", "NICHT_BESTAETIGT", "UNKLAR"]

    def test_empty_dates(self):
        """Test handling of empty date list."""
        result = analyze_multiweek_timing([])

        assert result.verdict == "INSUFFICIENT_DATA"
        assert result.n_jackpots == 0
        assert result.acceptance_criteria_met is True

    def test_verdict_nicht_bestaetigt_for_random_data(self):
        """Test that random data results in NICHT_BESTAETIGT."""
        # Generate truly random dates
        rng = np.random.default_rng(42)
        base = datetime(2024, 1, 1)
        dates = [base + timedelta(days=int(d)) for d in rng.integers(0, 365, 200)]

        config = SimulationConfig(n_simulations=1000, random_seed=42)
        result = analyze_multiweek_timing(dates, config)

        # With random data, we expect no significant findings
        assert result.verdict in ["NICHT_BESTAETIGT", "UNKLAR"]


class TestToDict:
    """Tests fuer JSON-Konvertierung."""

    def test_to_dict_complete(self):
        """Test that to_dict produces complete JSON structure."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i * 5) for i in range(50)]
        config = SimulationConfig(n_simulations=100, random_seed=42)
        result = analyze_multiweek_timing(dates, config)

        d = to_dict(result)

        assert "hypothesis_id" in d
        assert "analysis_date" in d
        assert "n_jackpots" in d
        assert "date_range" in d
        assert "simulation_config" in d
        assert "distributions" in d
        assert "chi2_results" in d
        assert "mc_comparisons" in d
        assert "verdict" in d
        assert "confidence" in d
        assert "acceptance_criteria_met" in d


class TestExportResultToJson:
    """Tests fuer JSON-Export."""

    def test_export_creates_file(self, tmp_path):
        """Test that export creates JSON file."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i * 5) for i in range(30)]
        config = SimulationConfig(n_simulations=100, random_seed=42)
        result = analyze_multiweek_timing(dates, config)

        output_path = tmp_path / "test_result.json"
        export_result_to_json(result, output_path)

        assert output_path.exists()

        # Verify it's valid JSON
        import json
        with open(output_path) as f:
            data = json.load(f)
        assert data["hypothesis_id"] == "HYP-014"


class TestRunHyp014Analysis:
    """Tests fuer Convenience-Funktion."""

    def test_run_with_output(self, tmp_path):
        """Test convenience function with output file."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i * 5) for i in range(30)]
        output_path = tmp_path / "hyp014_result.json"

        result = run_hyp014_analysis(
            dates,
            output_path=output_path,
            n_simulations=100,
            random_seed=42,
        )

        assert result.hypothesis_id == "HYP-014"
        assert output_path.exists()

    def test_run_without_output(self):
        """Test convenience function without output file."""
        dates = [datetime(2024, 1, 1) + timedelta(days=i * 5) for i in range(30)]

        result = run_hyp014_analysis(
            dates,
            n_simulations=100,
            random_seed=42,
        )

        assert result.hypothesis_id == "HYP-014"
        assert result.n_jackpots == 30
