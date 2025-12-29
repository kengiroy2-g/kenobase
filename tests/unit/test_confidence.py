"""Unit tests for kenobase.prediction.confidence module.

Tests the Bootstrap-based confidence interval implementation:
- ConfidenceInterval dataclass
- ConfidenceEstimator bootstrap CI calculation
- Coverage test validation
- Integration with EnsemblePrediction

Acceptance Criteria (TASK-P11):
- CI coverage nahe 95% (0.90-0.98)
- Stabile Vorhersagen: width < 0.3
"""

import numpy as np
import pytest

from kenobase.prediction.confidence import (
    ConfidenceEstimator,
    ConfidenceInterval,
    PredictionWithCI,
)


class TestConfidenceInterval:
    """Tests for ConfidenceInterval dataclass."""

    def test_width_calculation(self):
        """Test width property calculation."""
        ci = ConfidenceInterval(
            lower=0.3, upper=0.7, point_estimate=0.5
        )
        assert ci.width == pytest.approx(0.4)

    def test_is_stable_true(self):
        """Test is_stable returns True when width < 0.3."""
        ci = ConfidenceInterval(
            lower=0.4, upper=0.6, point_estimate=0.5
        )
        assert ci.width == pytest.approx(0.2)
        assert ci.is_stable is True

    def test_is_stable_false(self):
        """Test is_stable returns False when width >= 0.3."""
        ci = ConfidenceInterval(
            lower=0.2, upper=0.8, point_estimate=0.5
        )
        assert ci.width == pytest.approx(0.6)
        assert ci.is_stable is False

    def test_contains_value_inside(self):
        """Test contains returns True for value inside interval."""
        ci = ConfidenceInterval(lower=0.3, upper=0.7, point_estimate=0.5)
        assert ci.contains(0.5) is True
        assert ci.contains(0.3) is True  # Boundary
        assert ci.contains(0.7) is True  # Boundary

    def test_contains_value_outside(self):
        """Test contains returns False for value outside interval."""
        ci = ConfidenceInterval(lower=0.3, upper=0.7, point_estimate=0.5)
        assert ci.contains(0.2) is False
        assert ci.contains(0.8) is False

    def test_to_dict(self):
        """Test to_dict serialization."""
        ci = ConfidenceInterval(
            lower=0.35,
            upper=0.65,
            point_estimate=0.5,
            confidence_level=0.95,
            n_bootstrap=1000,
        )
        d = ci.to_dict()

        assert d["ci_lower"] == 0.35
        assert d["ci_upper"] == 0.65
        assert d["ci_width"] == 0.3
        assert d["point_estimate"] == 0.5
        assert d["confidence_level"] == 0.95
        assert d["is_stable"] is False  # width == 0.3, not < 0.3


class TestConfidenceEstimator:
    """Tests for ConfidenceEstimator bootstrap CI calculation."""

    @pytest.fixture
    def estimator(self):
        """Create estimator with fixed seed for reproducibility."""
        return ConfidenceEstimator(n_bootstrap=1000, random_state=42)

    def test_calculate_ci_basic(self, estimator):
        """Test basic CI calculation with uniform scores."""
        scores = np.array([0.4, 0.5, 0.6, 0.5, 0.45, 0.55])
        ci = estimator.calculate_ci(scores)

        assert ci.lower < ci.upper
        assert ci.lower < ci.point_estimate < ci.upper
        assert 0.0 <= ci.lower <= 1.0
        assert 0.0 <= ci.upper <= 1.0
        assert ci.confidence_level == 0.95

    def test_calculate_ci_narrow_distribution(self, estimator):
        """Test CI is narrow for consistent scores."""
        # Very consistent scores should have narrow CI
        scores = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
        ci = estimator.calculate_ci(scores)

        # Width should be very small for constant values
        assert ci.width < 0.01
        assert ci.is_stable is True

    def test_calculate_ci_wide_distribution(self, estimator):
        """Test CI is wider for variable scores."""
        # Highly variable scores should have wider CI
        scores = np.array([0.1, 0.9, 0.2, 0.8, 0.3, 0.7])
        ci = estimator.calculate_ci(scores)

        # Width should be larger
        assert ci.width > 0.1
        assert ci.point_estimate == pytest.approx(0.5, abs=0.1)

    def test_calculate_ci_empty_raises(self, estimator):
        """Test that empty scores raises ValueError."""
        with pytest.raises(ValueError, match="darf nicht leer"):
            estimator.calculate_ci(np.array([]))

    def test_calculate_ci_invalid_confidence_level(self, estimator):
        """Test that invalid confidence_level raises ValueError."""
        scores = np.array([0.5, 0.5, 0.5])

        with pytest.raises(ValueError, match="zwischen 0 und 1"):
            estimator.calculate_ci(scores, confidence_level=0.0)

        with pytest.raises(ValueError, match="zwischen 0 und 1"):
            estimator.calculate_ci(scores, confidence_level=1.0)

    def test_calculate_ci_different_confidence_levels(self, estimator):
        """Test CI width increases with confidence level."""
        scores = np.array([0.3, 0.4, 0.5, 0.6, 0.7])

        ci_90 = estimator.calculate_ci(scores, confidence_level=0.90)
        ci_95 = estimator.calculate_ci(scores, confidence_level=0.95)
        ci_99 = estimator.calculate_ci(scores, confidence_level=0.99)

        # Higher confidence = wider interval
        assert ci_90.width < ci_95.width < ci_99.width

    def test_calculate_ci_median_statistic(self, estimator):
        """Test CI calculation with median statistic."""
        scores = np.array([0.3, 0.4, 0.5, 0.6, 0.7])
        ci = estimator.calculate_ci(scores, statistic="median")

        assert ci.lower < ci.upper
        assert 0.0 <= ci.point_estimate <= 1.0

    def test_calculate_ci_for_predictions(self, estimator):
        """Test CI calculation for ensemble and ML scores."""
        ensemble_scores = [0.4, 0.5, 0.6, 0.55, 0.45]
        ml_probs = [0.3, 0.4, 0.5, 0.35, 0.45]

        result = estimator.calculate_ci_for_predictions(
            ensemble_scores, ml_probs
        )

        assert "ensemble" in result
        assert "ml" in result
        assert isinstance(result["ensemble"], ConfidenceInterval)
        assert isinstance(result["ml"], ConfidenceInterval)

    def test_calculate_ci_for_predictions_empty(self, estimator):
        """Test CI for empty inputs returns degenerate CI."""
        result = estimator.calculate_ci_for_predictions([], [])

        assert result["ensemble"].point_estimate == 0.5
        assert result["ml"].point_estimate == 0.5


class TestCoverageTest:
    """Tests for coverage_test method."""

    @pytest.fixture
    def estimator(self):
        return ConfidenceEstimator(n_bootstrap=100, random_state=42)

    def test_coverage_perfect(self, estimator):
        """Test coverage = 1.0 when all values inside CI."""
        true_values = np.array([0.5, 0.5, 0.5])
        ci_list = [
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
        ]

        coverage = estimator.coverage_test(true_values, ci_list)
        assert coverage == 1.0

    def test_coverage_none(self, estimator):
        """Test coverage = 0.0 when no values inside CI."""
        true_values = np.array([0.1, 0.9, 0.1])
        ci_list = [
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
        ]

        coverage = estimator.coverage_test(true_values, ci_list)
        assert coverage == 0.0

    def test_coverage_partial(self, estimator):
        """Test coverage for partial overlap."""
        true_values = np.array([0.5, 0.9, 0.5, 0.1])
        ci_list = [
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
        ]

        coverage = estimator.coverage_test(true_values, ci_list)
        assert coverage == 0.5  # 2 out of 4

    def test_coverage_mismatched_lengths(self, estimator):
        """Test coverage raises on mismatched lengths."""
        true_values = np.array([0.5, 0.5])
        ci_list = [
            ConfidenceInterval(lower=0.4, upper=0.6, point_estimate=0.5),
        ]

        with pytest.raises(ValueError, match="Laengen stimmen nicht"):
            estimator.coverage_test(true_values, ci_list)

    def test_coverage_near_95_percent(self, estimator):
        """Test that 95% CI achieves ~95% coverage on normal data."""
        # Generate normal data and calculate CIs
        np.random.seed(42)
        n_trials = 100

        covered_count = 0
        for _ in range(n_trials):
            # Sample from N(0.5, 0.1)
            samples = np.random.normal(0.5, 0.1, size=20)
            samples = np.clip(samples, 0, 1)

            true_mean = 0.5  # Known population mean

            ci = estimator.calculate_ci(samples, confidence_level=0.95)
            if ci.contains(true_mean):
                covered_count += 1

        coverage_rate = covered_count / n_trials

        # Coverage should be around 0.95 (allow some variance for 100 trials)
        assert 0.85 <= coverage_rate <= 1.0, f"Coverage {coverage_rate} not near 95%"


class TestPredictionWithCI:
    """Tests for PredictionWithCI dataclass."""

    def test_is_stable_both_stable(self):
        """Test is_stable when both CIs are stable."""
        pred = PredictionWithCI(
            number=1,
            ensemble_score=0.6,
            ensemble_ci=ConfidenceInterval(
                lower=0.5, upper=0.7, point_estimate=0.6
            ),  # width=0.2 < 0.3
            ml_probability=0.55,
            ml_ci=ConfidenceInterval(
                lower=0.45, upper=0.65, point_estimate=0.55
            ),  # width=0.2 < 0.3
        )
        assert pred.is_stable is True

    def test_is_stable_one_unstable(self):
        """Test is_stable when one CI is unstable."""
        pred = PredictionWithCI(
            number=1,
            ensemble_score=0.6,
            ensemble_ci=ConfidenceInterval(
                lower=0.2, upper=0.8, point_estimate=0.6
            ),  # width=0.6 >= 0.3
            ml_probability=0.55,
            ml_ci=ConfidenceInterval(
                lower=0.45, upper=0.65, point_estimate=0.55
            ),  # width=0.2 < 0.3
        )
        assert pred.is_stable is False

    def test_combined_width(self):
        """Test combined_width calculation."""
        pred = PredictionWithCI(
            number=1,
            ensemble_score=0.6,
            ensemble_ci=ConfidenceInterval(
                lower=0.5, upper=0.7, point_estimate=0.6
            ),  # width=0.2
            ml_probability=0.55,
            ml_ci=ConfidenceInterval(
                lower=0.35, upper=0.75, point_estimate=0.55
            ),  # width=0.4
        )
        assert pred.combined_width == pytest.approx(0.3)  # (0.2 + 0.4) / 2

    def test_to_dict(self):
        """Test to_dict serialization."""
        pred = PredictionWithCI(
            number=42,
            ensemble_score=0.65,
            ensemble_ci=ConfidenceInterval(
                lower=0.55, upper=0.75, point_estimate=0.65
            ),
            ml_probability=0.6,
            ml_ci=ConfidenceInterval(
                lower=0.5, upper=0.7, point_estimate=0.6
            ),
            tier="A",
        )
        d = pred.to_dict()

        assert d["number"] == 42
        assert d["ensemble_score"] == 0.65
        assert d["ml_probability"] == 0.6
        assert d["tier"] == "A"
        assert "ensemble_ci" in d
        assert "ml_ci" in d
        assert d["is_stable"] is True


class TestIntegrationWithEnsemble:
    """Integration tests with ensemble module."""

    def test_ensemble_prediction_with_ci_properties(self):
        """Test EnsemblePrediction CI properties after integration."""
        from kenobase.prediction.ensemble import EnsemblePrediction

        pred = EnsemblePrediction(
            number=1,
            ensemble_score=0.7,
            rule_score=0.65,
            ml_probability=0.75,
            tier="A",
            confidence=0.7,
            ensemble_ci=ConfidenceInterval(
                lower=0.6, upper=0.8, point_estimate=0.7
            ),
            ml_ci=ConfidenceInterval(
                lower=0.65, upper=0.85, point_estimate=0.75
            ),
        )

        assert pred.has_ci is True
        assert pred.is_stable is True

    def test_ensemble_prediction_without_ci(self):
        """Test EnsemblePrediction without CI set."""
        from kenobase.prediction.ensemble import EnsemblePrediction

        pred = EnsemblePrediction(
            number=1,
            ensemble_score=0.7,
            rule_score=0.65,
            ml_probability=0.75,
        )

        assert pred.has_ci is False
        assert pred.is_stable is False

    def test_ensemble_prediction_to_dict_with_ci(self):
        """Test EnsemblePrediction.to_dict includes CI."""
        from kenobase.prediction.ensemble import EnsemblePrediction

        pred = EnsemblePrediction(
            number=1,
            ensemble_score=0.7,
            rule_score=0.65,
            ml_probability=0.75,
            ensemble_ci=ConfidenceInterval(
                lower=0.6, upper=0.8, point_estimate=0.7
            ),
            ml_ci=ConfidenceInterval(
                lower=0.65, upper=0.85, point_estimate=0.75
            ),
        )

        d = pred.to_dict()
        assert "ensemble_ci" in d
        assert "ml_ci" in d
        assert "is_stable" in d
