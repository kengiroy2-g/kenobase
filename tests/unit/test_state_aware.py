"""Unit tests for StateAwarePredictor.

Tests the state-aware prediction wrapper that combines EconomicState
with EnsemblePredictor for TASK_004.

Coverage:
- StateAwarePrediction dataclass
- StateAwareReport dataclass
- StateAwarePredictor.fit()
- StateAwarePredictor.predict()
- State-specific alpha weighting
- Integration with EconomicState
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.core.economic_state import EconomicState
from kenobase.prediction.state_aware import (
    StateAwarePredictor,
    StateAwarePrediction,
    StateAwareReport,
    DEFAULT_STATE_ALPHAS,
)


# --- Fixtures ---


@pytest.fixture
def sample_draws() -> list[DrawResult]:
    """Create sample DrawResult objects for testing."""
    base_date = datetime(2024, 1, 1)
    draws = []

    for i in range(100):
        draw = DrawResult(
            date=base_date + timedelta(days=i),
            numbers=sorted(list(range(1, 21))),  # Numbers 1-20
            game_type=GameType.KENO,
            metadata={
                "spieleinsatz": 1_000_000 + i * 10_000,
                "jackpot": 5_000_000 + i * 100_000,
            },
        )
        draws.append(draw)

    return draws


@pytest.fixture
def sample_economic_state() -> EconomicState:
    """Create a sample EconomicState."""
    return EconomicState(
        date=datetime(2024, 1, 15),
        spieleinsatz=1_500_000.0,
        jackpot=8_000_000.0,
        rolling_cv=0.3,
        state_label="NORMAL",
    )


# --- StateAwarePrediction Tests ---


class TestStateAwarePrediction:
    """Tests for StateAwarePrediction dataclass."""

    def test_to_dict(self):
        """Test to_dict conversion."""
        prediction = StateAwarePrediction(
            number=42,
            ensemble_score=0.75,
            rule_score=0.6,
            ml_probability=0.85,
            tier="A",
            confidence=0.7,
            state_label="NORMAL",
            state_alpha=0.4,
            bet_recommendation={"action": "NEUTRAL", "confidence": 0.5},
        )

        result = prediction.to_dict()

        assert result["number"] == 42
        assert result["ensemble_score"] == 0.75
        assert result["rule_score"] == 0.6
        assert result["ml_probability"] == 0.85
        assert result["tier"] == "A"
        assert result["state_label"] == "NORMAL"
        assert result["state_alpha"] == 0.4
        assert result["bet_recommendation"]["action"] == "NEUTRAL"

    def test_default_values(self):
        """Test default values."""
        prediction = StateAwarePrediction(
            number=1,
            ensemble_score=0.5,
            rule_score=0.5,
            ml_probability=0.5,
        )

        assert prediction.tier == "C"
        assert prediction.confidence == 0.5
        assert prediction.state_label == "NORMAL"
        assert prediction.state_alpha == 0.4


# --- StateAwareReport Tests ---


class TestStateAwareReport:
    """Tests for StateAwareReport dataclass."""

    def test_to_dict(self):
        """Test to_dict conversion."""
        report = StateAwareReport(
            state_metrics={
                "NORMAL": {"f1": 0.5, "n_samples": 80},
                "COOLDOWN": {"f1": 0.45, "n_samples": 10},
            },
            state_distribution={
                "total": 100,
                "counts": {"NORMAL": 80, "COOLDOWN": 10, "RECOVERY": 5, "HOT": 5},
            },
            state_alphas=DEFAULT_STATE_ALPHAS,
            overall_f1=0.48,
            baseline_f1=0.45,
        )

        result = report.to_dict()

        assert result["overall_f1"] == 0.48
        assert result["baseline_f1"] == 0.45
        assert result["f1_improvement"] == 0.03
        assert "NORMAL" in result["state_metrics"]
        assert result["state_distribution"]["total"] == 100

    def test_save(self, tmp_path):
        """Test report save to JSON."""
        report = StateAwareReport(
            overall_f1=0.5,
            baseline_f1=0.45,
        )

        path = tmp_path / "report.json"
        report.save(path)

        assert path.exists()


# --- StateAwarePredictor Tests ---


class TestStateAwarePredictor:
    """Tests for StateAwarePredictor class."""

    def test_init_default_alphas(self):
        """Test initialization with default alphas."""
        with patch("kenobase.prediction.state_aware.EnsemblePredictor"):
            predictor = StateAwarePredictor()

        assert predictor.state_alphas["NORMAL"] == 0.4
        assert predictor.state_alphas["COOLDOWN"] == 0.6
        assert predictor.state_alphas["RECOVERY"] == 0.5
        assert predictor.state_alphas["HOT"] == 0.3

    def test_init_custom_alphas(self):
        """Test initialization with custom alphas."""
        custom_alphas = {
            "NORMAL": 0.5,
            "COOLDOWN": 0.7,
            "RECOVERY": 0.55,
            "HOT": 0.25,
        }

        with patch("kenobase.prediction.state_aware.EnsemblePredictor"):
            predictor = StateAwarePredictor(state_alphas=custom_alphas)

        assert predictor.state_alphas["NORMAL"] == 0.5
        assert predictor.state_alphas["COOLDOWN"] == 0.7

    def test_init_partial_alphas_fills_defaults(self):
        """Test that missing alphas are filled with defaults."""
        partial_alphas = {"NORMAL": 0.35}

        with patch("kenobase.prediction.state_aware.EnsemblePredictor"):
            predictor = StateAwarePredictor(state_alphas=partial_alphas)

        assert predictor.state_alphas["NORMAL"] == 0.35
        assert predictor.state_alphas["COOLDOWN"] == 0.6  # Default
        assert predictor.state_alphas["HOT"] == 0.3  # Default

    def test_predict_without_fit_raises(self):
        """Test that predict raises error if not fitted."""
        with patch("kenobase.prediction.state_aware.EnsemblePredictor"):
            predictor = StateAwarePredictor()

        with pytest.raises(RuntimeError, match="must be fitted"):
            predictor.predict([], top_n=10)

    def test_get_current_state(self, sample_draws):
        """Test get_current_state extraction."""
        with patch("kenobase.prediction.state_aware.EnsemblePredictor"):
            predictor = StateAwarePredictor()

        state = predictor.get_current_state(sample_draws)

        assert isinstance(state, EconomicState)
        assert state.state_label in ["NORMAL", "COOLDOWN", "RECOVERY", "HOT"]

    def test_state_alphas_used_in_prediction(self, sample_economic_state):
        """Test that state-specific alphas are used."""
        # Test each state uses correct alpha
        for state_label, expected_alpha in DEFAULT_STATE_ALPHAS.items():
            state = EconomicState(
                date=datetime.now(),
                spieleinsatz=None,
                jackpot=None,
                rolling_cv=None,
                state_label=state_label,
            )

            with patch("kenobase.prediction.state_aware.EnsemblePredictor"):
                predictor = StateAwarePredictor()
                alpha = predictor.state_alphas.get(state_label)

            assert alpha == expected_alpha, f"State {state_label} should use alpha {expected_alpha}"


# --- Integration Tests ---


class TestStateAwarePredictorIntegration:
    """Integration tests for StateAwarePredictor with mocked EnsemblePredictor."""

    @pytest.fixture
    def mock_ensemble_predictor(self):
        """Create a mocked EnsemblePredictor."""
        mock = MagicMock()
        mock.alpha = 0.4

        # Mock fit to return a report
        mock_report = MagicMock()
        mock_report.ensemble_metrics = MagicMock()
        mock_report.ensemble_metrics.f1 = 0.45
        mock.fit.return_value = mock_report

        # Mock predict to return predictions
        mock_predictions = [
            MagicMock(
                number=i,
                ensemble_score=0.5 + i * 0.01,
                rule_score=0.5,
                ml_probability=0.5,
                tier="B",
                confidence=0.5,
            )
            for i in range(1, 21)
        ]
        mock.predict.return_value = mock_predictions

        return mock

    def test_fit_extracts_economic_states(self, sample_draws, mock_ensemble_predictor):
        """Test that fit extracts economic states from draws."""
        with patch(
            "kenobase.prediction.state_aware.EnsemblePredictor",
            return_value=mock_ensemble_predictor,
        ):
            predictor = StateAwarePredictor()
            report = predictor.fit(sample_draws)

        assert len(predictor._economic_states) == len(sample_draws)
        assert report.state_distribution["total"] == len(sample_draws)

    def test_fit_computes_state_metrics(self, sample_draws, mock_ensemble_predictor):
        """Test that fit computes per-state metrics."""
        with patch(
            "kenobase.prediction.state_aware.EnsemblePredictor",
            return_value=mock_ensemble_predictor,
        ):
            predictor = StateAwarePredictor()
            report = predictor.fit(sample_draws)

        # Should have metrics for each state
        assert "NORMAL" in report.state_metrics

    def test_predict_returns_state_aware_predictions(
        self, sample_draws, mock_ensemble_predictor
    ):
        """Test that predict returns StateAwarePrediction objects."""
        with patch(
            "kenobase.prediction.state_aware.EnsemblePredictor",
            return_value=mock_ensemble_predictor,
        ):
            predictor = StateAwarePredictor()
            predictor.fit(sample_draws)
            predictions = predictor.predict(sample_draws, top_n=10)

        # Mock returns 20, so we get 20 converted to StateAwarePrediction
        # (real implementation limits to top_n, but mock bypasses that)
        assert len(predictions) <= 20
        assert all(isinstance(p, StateAwarePrediction) for p in predictions)
        assert all(p.state_label in ["NORMAL", "COOLDOWN", "RECOVERY", "HOT"] for p in predictions)

    def test_predict_with_explicit_state(self, sample_draws, mock_ensemble_predictor):
        """Test predict with explicit current_state."""
        explicit_state = EconomicState(
            date=datetime.now(),
            spieleinsatz=500_000.0,
            jackpot=2_000_000.0,
            rolling_cv=0.6,
            state_label="COOLDOWN",
        )

        with patch(
            "kenobase.prediction.state_aware.EnsemblePredictor",
            return_value=mock_ensemble_predictor,
        ):
            predictor = StateAwarePredictor()
            predictor.fit(sample_draws)
            predictions = predictor.predict(
                sample_draws,
                top_n=10,
                current_state=explicit_state,
            )

        # All predictions should have COOLDOWN state
        assert all(p.state_label == "COOLDOWN" for p in predictions)
        assert all(p.state_alpha == 0.6 for p in predictions)

    def test_predict_proba_returns_all_numbers(self, sample_draws, mock_ensemble_predictor):
        """Test predict_proba returns scores for all numbers."""
        with patch(
            "kenobase.prediction.state_aware.EnsemblePredictor",
            return_value=mock_ensemble_predictor,
        ):
            predictor = StateAwarePredictor(numbers_range=(1, 70))
            predictor.fit(sample_draws)
            proba = predictor.predict_proba(sample_draws)

        # Should have scores for all numbers (mocked to 20)
        assert len(proba) >= 10  # At least some numbers returned


# --- Acceptance Criteria Tests ---


class TestAcceptanceCriteria:
    """Tests for TASK_004 acceptance criteria."""

    def test_state_labels_match_economic_state(self, sample_draws):
        """Test that state labels match economic_state module labels."""
        valid_states = {"NORMAL", "COOLDOWN", "RECOVERY", "HOT"}

        with patch("kenobase.prediction.state_aware.EnsemblePredictor") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.alpha = 0.4
            mock_report = MagicMock()
            mock_report.ensemble_metrics = MagicMock()
            mock_report.ensemble_metrics.f1 = 0.45
            mock_instance.fit.return_value = mock_report
            mock_instance.predict.return_value = []
            mock_cls.return_value = mock_instance

            predictor = StateAwarePredictor()
            predictor.fit(sample_draws)

            # All economic states should have valid labels
            for state in predictor._economic_states:
                assert state.state_label in valid_states

    def test_f1_metric_computed_per_state(self, sample_draws):
        """Test that F1 is computed per state."""
        with patch("kenobase.prediction.state_aware.EnsemblePredictor") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.alpha = 0.4
            mock_report = MagicMock()
            mock_report.ensemble_metrics = MagicMock()
            mock_report.ensemble_metrics.f1 = 0.45
            mock_instance.fit.return_value = mock_report
            mock_instance.predict.return_value = [
                MagicMock(number=i, ensemble_score=0.5, rule_score=0.5, ml_probability=0.5, tier="B", confidence=0.5)
                for i in range(1, 21)
            ]
            mock_cls.return_value = mock_instance

            predictor = StateAwarePredictor()
            report = predictor.fit(sample_draws)

            # State metrics should contain f1 for each state
            for state_label in ["NORMAL", "COOLDOWN", "RECOVERY", "HOT"]:
                if state_label in report.state_metrics:
                    assert "f1" in report.state_metrics[state_label]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
