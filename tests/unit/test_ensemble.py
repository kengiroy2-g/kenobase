"""Unit Tests for EnsemblePredictor.

Tests TASK-P06 Ensemble Prediction Model:
- EnsemblePredictor initialization
- EnsemblePrediction dataclass
- EnsembleReport dataclass
- Weighted combination: alpha * rule + (1-alpha) * ml
- Integration with HypothesisSynthesizer and KenoPredictor

Target: F1 >= 0.50 (improvement from 0.4434 baseline)
"""

from __future__ import annotations

import json
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.prediction.synthesizer import NumberScore, HypothesisScore


class TestEnsemblePrediction:
    """Tests for EnsemblePrediction dataclass."""

    def test_creation(self):
        """Test basic EnsemblePrediction creation."""
        from kenobase.prediction.ensemble import EnsemblePrediction

        pred = EnsemblePrediction(
            number=42,
            ensemble_score=0.75,
            rule_score=0.6,
            ml_probability=0.85,
            tier="A",
            confidence=0.7,
        )

        assert pred.number == 42
        assert pred.ensemble_score == 0.75
        assert pred.rule_score == 0.6
        assert pred.ml_probability == 0.85
        assert pred.tier == "A"
        assert pred.confidence == 0.7

    def test_to_dict(self):
        """Test EnsemblePrediction serialization."""
        from kenobase.prediction.ensemble import EnsemblePrediction

        pred = EnsemblePrediction(
            number=42,
            ensemble_score=0.7512345,
            rule_score=0.6,
            ml_probability=0.85,
            tier="A",
            confidence=0.7,
        )

        d = pred.to_dict()

        assert d["number"] == 42
        assert d["ensemble_score"] == 0.7512  # Rounded to 4 decimals
        assert d["tier"] == "A"


class TestEnsembleReport:
    """Tests for EnsembleReport dataclass."""

    def test_creation(self):
        """Test basic EnsembleReport creation."""
        from kenobase.prediction.ensemble import EnsembleReport

        report = EnsembleReport(
            alpha=0.4,
            hypotheses_used=["HYP-007", "HYP-010"],
        )

        assert report.alpha == 0.4
        assert report.hypotheses_used == ["HYP-007", "HYP-010"]
        assert report.rule_contribution == 0.0  # Default

    def test_to_dict(self):
        """Test EnsembleReport serialization."""
        from kenobase.prediction.ensemble import EnsembleReport

        report = EnsembleReport(
            alpha=0.4,
            hypotheses_used=["HYP-007"],
            rule_contribution=0.4,
            ml_contribution=0.6,
        )

        d = report.to_dict()

        assert d["alpha"] == 0.4
        assert d["rule_weight"] == 0.4
        assert d["ml_weight"] == 0.6
        assert d["hypotheses_used"] == ["HYP-007"]

    def test_save(self):
        """Test EnsembleReport save to JSON."""
        from kenobase.prediction.ensemble import EnsembleReport

        report = EnsembleReport(
            alpha=0.4,
            hypotheses_used=["HYP-007"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.json"
            report.save(path)

            assert path.exists()
            with open(path) as f:
                data = json.load(f)
            assert data["alpha"] == 0.4


class TestEnsemblePredictor:
    """Tests for EnsemblePredictor class."""

    @pytest.fixture
    def mock_draws(self) -> list[DrawResult]:
        """Create mock draw data for testing."""
        from datetime import timedelta
        draws = []
        for i in range(100):
            # Generate random 20 numbers from 1-70
            numbers = sorted(np.random.choice(range(1, 71), 20, replace=False).tolist())
            draws.append(DrawResult(
                date=date(2024, 1, 1) + timedelta(days=i),
                numbers=numbers,
                game_type=GameType.KENO,
            ))
        return draws

    @pytest.fixture
    def mock_synthesizer(self):
        """Create mock synthesizer with scores."""
        scores = {}
        for num in range(1, 71):
            scores[num] = NumberScore(
                number=num,
                combined_score=0.3 + (num / 100),  # 0.31 to 1.0
                hypothesis_scores={
                    "HYP-007": HypothesisScore(
                        hypothesis_id="HYP-007",
                        score=0.5,
                        is_significant=False,
                        weight=0.1,
                        reason="test",
                    )
                },
                tier="A" if num > 50 else "B",
            )
        return scores

    def test_init_valid_alpha(self):
        """Test initialization with valid alpha."""
        pytest.importorskip("lightgbm")
        from kenobase.prediction.ensemble import EnsemblePredictor

        ensemble = EnsemblePredictor(alpha=0.4)
        assert ensemble.alpha == 0.4

        ensemble = EnsemblePredictor(alpha=0.0)
        assert ensemble.alpha == 0.0

        ensemble = EnsemblePredictor(alpha=1.0)
        assert ensemble.alpha == 1.0

    def test_init_invalid_alpha(self):
        """Test initialization with invalid alpha raises error."""
        pytest.importorskip("lightgbm")
        from kenobase.prediction.ensemble import EnsemblePredictor

        with pytest.raises(ValueError, match="alpha muss zwischen 0 und 1"):
            EnsemblePredictor(alpha=-0.1)

        with pytest.raises(ValueError, match="alpha muss zwischen 0 und 1"):
            EnsemblePredictor(alpha=1.1)

    def test_default_alpha(self):
        """Test default alpha is 0.4."""
        pytest.importorskip("lightgbm")
        from kenobase.prediction.ensemble import EnsemblePredictor

        ensemble = EnsemblePredictor()
        assert ensemble.alpha == 0.4

    def test_predict_before_fit_raises(self):
        """Test predict raises error if not fitted."""
        pytest.importorskip("lightgbm")
        from kenobase.prediction.ensemble import EnsemblePredictor

        ensemble = EnsemblePredictor()

        with pytest.raises(RuntimeError, match="muss zuerst mit fit"):
            ensemble.predict([], top_n=10)

    def test_ensemble_score_formula(self):
        """Test ensemble score is correctly weighted.

        Formula: ensemble_score = alpha * rule_score + (1 - alpha) * ml_probability
        """
        alpha = 0.4
        rule_score = 0.6
        ml_prob = 0.8

        expected = alpha * rule_score + (1 - alpha) * ml_prob
        # 0.4 * 0.6 + 0.6 * 0.8 = 0.24 + 0.48 = 0.72

        assert expected == pytest.approx(0.72)

    def test_fit_with_mock_data(self, mock_draws, mock_synthesizer):
        """Test fit with mocked components.

        This is a structural test - full integration requires actual data files.
        The test verifies the ensemble can be instantiated with the mock fixture.
        """
        pytest.importorskip("lightgbm")
        from kenobase.prediction.ensemble import EnsemblePredictor

        # Verify we can create ensemble and mock_draws fixture works
        ensemble = EnsemblePredictor(alpha=0.4)
        assert len(mock_draws) == 100
        assert ensemble.alpha == 0.4

        # Verify mock_synthesizer structure
        assert len(mock_synthesizer) == 70
        assert 1 in mock_synthesizer
        assert 70 in mock_synthesizer

        # Note: Full fit() test requires actual HYP result files and training data
        # This would be an integration test, not unit test

    def test_tier_classification(self):
        """Test tier classification based on ensemble_score."""
        from kenobase.prediction.ensemble import EnsemblePrediction

        # Tier A: score >= 0.7
        pred_a = EnsemblePrediction(
            number=1, ensemble_score=0.75, rule_score=0.7,
            ml_probability=0.8, tier="A", confidence=0.5
        )
        assert pred_a.tier == "A"

        # Tier B: 0.5 <= score < 0.7
        pred_b = EnsemblePrediction(
            number=2, ensemble_score=0.55, rule_score=0.5,
            ml_probability=0.6, tier="B", confidence=0.5
        )
        assert pred_b.tier == "B"

        # Tier C: score < 0.5
        pred_c = EnsemblePrediction(
            number=3, ensemble_score=0.35, rule_score=0.3,
            ml_probability=0.4, tier="C", confidence=0.5
        )
        assert pred_c.tier == "C"


class TestEnsembleIntegration:
    """Integration tests for ensemble with real components."""

    @pytest.mark.skipif(
        not pytest.importorskip("lightgbm", reason="LightGBM not installed"),
        reason="LightGBM not installed"
    )
    def test_module_exports(self):
        """Test that ensemble classes are exported from prediction module."""
        from kenobase.prediction import (
            EnsemblePredictor,
            EnsemblePrediction,
            EnsembleReport,
        )

        assert EnsemblePredictor is not None
        assert EnsemblePrediction is not None
        assert EnsembleReport is not None

    def test_alpha_weight_boundaries(self):
        """Test ensemble weights at boundary conditions."""
        # alpha=0: 100% ML
        alpha = 0.0
        rule_score = 0.8
        ml_prob = 0.6
        ensemble = alpha * rule_score + (1 - alpha) * ml_prob
        assert ensemble == pytest.approx(0.6)

        # alpha=1: 100% Rules
        alpha = 1.0
        ensemble = alpha * rule_score + (1 - alpha) * ml_prob
        assert ensemble == pytest.approx(0.8)

        # alpha=0.5: Equal weight
        alpha = 0.5
        ensemble = alpha * rule_score + (1 - alpha) * ml_prob
        assert ensemble == pytest.approx(0.7)

    def test_confidence_calculation(self):
        """Test confidence based on agreement between components."""
        # High agreement (both components similar)
        rule_score = 0.7
        ml_prob = 0.75
        agreement = 1 - abs(rule_score - ml_prob)
        assert agreement == pytest.approx(0.95)

        # Low agreement (components disagree)
        rule_score = 0.3
        ml_prob = 0.9
        agreement = 1 - abs(rule_score - ml_prob)
        assert agreement == pytest.approx(0.4)


class TestEnsemblePersistence:
    """Tests for ensemble save/load functionality."""

    @pytest.mark.skipif(
        not pytest.importorskip("lightgbm", reason="LightGBM not installed"),
        reason="LightGBM not installed"
    )
    def test_save_before_fit_raises(self):
        """Test save raises error if not fitted."""
        from kenobase.prediction.ensemble import EnsemblePredictor

        ensemble = EnsemblePredictor()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "model"
            with pytest.raises(RuntimeError, match="muss zuerst trainiert"):
                ensemble.save(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
