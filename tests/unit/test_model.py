"""Unit Tests fuer kenobase.prediction.model.

Testet:
- ModelConfig Konvertierung
- KenoPredictor Training/Prediction
- Cross-Validation
- Feature Importance
- Metriken-Berechnung

TASK-P02 Acceptance Criteria:
- Unit-Tests fuer ML Model
"""

import pytest
import numpy as np
from datetime import date

# Skip tests if LightGBM not installed
pytest.importorskip("lightgbm")
pytest.importorskip("sklearn")


class TestModelConfig:
    """Tests fuer ModelConfig."""

    def test_default_values(self):
        """Test default config values."""
        from kenobase.prediction.model import ModelConfig

        config = ModelConfig()

        assert config.num_leaves == 31
        assert config.learning_rate == 0.05
        assert config.n_estimators == 100
        assert config.random_state == 42

    def test_to_lgb_params(self):
        """Test conversion to LightGBM params."""
        from kenobase.prediction.model import ModelConfig

        config = ModelConfig(
            num_leaves=15,
            learning_rate=0.1,
            max_depth=5,
        )
        params = config.to_lgb_params()

        assert params["boosting_type"] == "gbdt"
        assert params["objective"] == "binary"
        assert params["num_leaves"] == 15
        assert params["learning_rate"] == 0.1
        assert params["max_depth"] == 5
        assert params["verbose"] == -1

    def test_custom_config(self):
        """Test custom config values."""
        from kenobase.prediction.model import ModelConfig

        config = ModelConfig(
            num_leaves=63,
            max_depth=10,
            learning_rate=0.01,
            n_estimators=500,
            min_child_samples=50,
        )

        assert config.num_leaves == 63
        assert config.max_depth == 10
        assert config.learning_rate == 0.01
        assert config.n_estimators == 500
        assert config.min_child_samples == 50


class TestPredictionResult:
    """Tests fuer PredictionResult."""

    def test_creation(self):
        """Test PredictionResult creation."""
        from kenobase.prediction.model import PredictionResult

        result = PredictionResult(
            number=42,
            probability=0.75,
            prediction=1,
            confidence=0.5,
        )

        assert result.number == 42
        assert result.probability == 0.75
        assert result.prediction == 1
        assert result.confidence == 0.5

    def test_to_dict(self):
        """Test conversion to dict."""
        from kenobase.prediction.model import PredictionResult

        result = PredictionResult(
            number=7,
            probability=0.8234567,
            prediction=1,
            confidence=0.6234567,
            features={"freq_raw": 0.1234567},
        )

        d = result.to_dict()

        assert d["number"] == 7
        assert d["probability"] == 0.8235  # Rounded to 4 decimals
        assert d["prediction"] == 1
        assert d["confidence"] == 0.6235
        assert d["features"]["freq_raw"] == 0.1235


class TestModelMetrics:
    """Tests fuer ModelMetrics."""

    def test_creation(self):
        """Test ModelMetrics creation."""
        from kenobase.prediction.model import ModelMetrics

        metrics = ModelMetrics(
            precision=0.8,
            recall=0.7,
            f1=0.75,
            accuracy=0.85,
            auc_roc=0.9,
            n_samples=1000,
        )

        assert metrics.precision == 0.8
        assert metrics.recall == 0.7
        assert metrics.f1 == 0.75
        assert metrics.accuracy == 0.85
        assert metrics.auc_roc == 0.9
        assert metrics.n_samples == 1000

    def test_to_dict(self):
        """Test conversion to dict."""
        from kenobase.prediction.model import ModelMetrics

        metrics = ModelMetrics(
            precision=0.82345,
            recall=0.71234,
            f1=0.76543,
            accuracy=0.85678,
            auc_roc=0.91234,
            n_samples=500,
        )

        d = metrics.to_dict()

        assert d["precision"] == 0.8235
        assert d["recall"] == 0.7123
        assert d["f1"] == 0.7654
        assert d["accuracy"] == 0.8568
        assert d["auc_roc"] == 0.9123
        assert d["n_samples"] == 500


class TestKenoPredictor:
    """Tests fuer KenoPredictor."""

    @pytest.fixture
    def sample_data(self):
        """Creates sample training data."""
        np.random.seed(42)
        n_samples = 500
        n_features = 20

        X = np.random.randn(n_samples, n_features).astype(np.float32)
        y = (np.random.rand(n_samples) > 0.7).astype(np.int32)

        return X, y

    @pytest.fixture
    def predictor(self):
        """Creates a KenoPredictor instance."""
        from kenobase.prediction.model import KenoPredictor, ModelConfig

        config = ModelConfig(
            n_estimators=10,  # Small for fast tests
            num_leaves=15,
        )
        return KenoPredictor(config=config)

    def test_creation(self, predictor):
        """Test predictor creation."""
        assert predictor.numbers_range == (1, 70)
        assert len(predictor.FEATURE_NAMES) == 20
        assert not predictor._is_trained

    def test_train(self, predictor, sample_data):
        """Test model training."""
        X, y = sample_data
        metrics = predictor.train(X, y)

        assert predictor._is_trained
        assert metrics.n_samples == len(y)
        assert 0 <= metrics.f1 <= 1
        assert 0 <= metrics.precision <= 1
        assert 0 <= metrics.recall <= 1

    def test_predict(self, predictor, sample_data):
        """Test predictions."""
        X, y = sample_data
        predictor.train(X, y)

        predictions = predictor.predict(X[:10])

        assert len(predictions) == 10
        for pred in predictions:
            assert 0 <= pred.probability <= 1
            assert pred.prediction in [0, 1]
            assert 0 <= pred.confidence <= 1

    def test_predict_proba(self, predictor, sample_data):
        """Test probability predictions."""
        X, y = sample_data
        predictor.train(X, y)

        proba = predictor.predict_proba(X)

        assert len(proba) == len(X)
        assert all(0 <= p <= 1 for p in proba)

    def test_evaluate(self, predictor, sample_data):
        """Test model evaluation."""
        X, y = sample_data
        X_train, X_test = X[:400], X[400:]
        y_train, y_test = y[:400], y[400:]

        predictor.train(X_train, y_train)
        metrics = predictor.evaluate(X_test, y_test)

        assert metrics.n_samples == len(y_test)
        assert 0 <= metrics.f1 <= 1
        assert 0 <= metrics.auc_roc <= 1

    def test_cross_validate(self, predictor, sample_data):
        """Test cross-validation."""
        X, y = sample_data

        avg_metrics, f1_std = predictor.cross_validate(X, y, n_folds=3)

        assert 0 <= avg_metrics.f1 <= 1
        assert f1_std >= 0
        assert avg_metrics.n_samples == len(y)

    def test_feature_importance(self, predictor, sample_data):
        """Test feature importance extraction."""
        X, y = sample_data
        predictor.train(X, y)

        importance = predictor.get_feature_importance()

        assert len(importance) > 0
        # Sum should be approximately 1 (normalized)
        total = sum(importance.values())
        assert 0.99 <= total <= 1.01

    def test_predict_before_training_raises(self, predictor, sample_data):
        """Test that predict raises if not trained."""
        X, _ = sample_data

        with pytest.raises(RuntimeError, match="trainiert"):
            predictor.predict(X)

    def test_train_with_eval_set(self, predictor, sample_data):
        """Test training with validation set (early stopping)."""
        X, y = sample_data
        X_train, X_val = X[:400], X[400:]
        y_train, y_val = y[:400], y[400:]

        metrics = predictor.train(
            X_train, y_train,
            eval_set=(X_val, y_val),
        )

        assert predictor._is_trained
        assert metrics.n_samples == len(y_train)


class TestKenoPredictorSaveLoad:
    """Tests fuer Model Save/Load."""

    @pytest.fixture
    def trained_predictor(self):
        """Creates and trains a predictor."""
        from kenobase.prediction.model import KenoPredictor, ModelConfig

        np.random.seed(42)
        X = np.random.randn(200, 20).astype(np.float32)
        y = (np.random.rand(200) > 0.7).astype(np.int32)

        config = ModelConfig(n_estimators=10)
        predictor = KenoPredictor(config=config)
        predictor.train(X, y)

        return predictor, X

    def test_save_and_load(self, trained_predictor, tmp_path):
        """Test saving and loading model."""
        from kenobase.prediction.model import KenoPredictor

        predictor, X = trained_predictor
        model_path = tmp_path / "test_model"

        # Save
        predictor.save(model_path)

        # Check files exist
        assert (model_path.with_suffix(".lgb")).exists()
        assert (model_path.with_suffix(".json")).exists()

        # Load into new predictor
        new_predictor = KenoPredictor()
        new_predictor.load(model_path)

        assert new_predictor._is_trained

        # Predictions should be similar
        orig_proba = predictor.predict_proba(X[:10])
        new_proba = new_predictor.predict_proba(X[:10])

        np.testing.assert_array_almost_equal(orig_proba, new_proba, decimal=5)

    def test_save_untrained_raises(self, tmp_path):
        """Test that saving untrained model raises."""
        from kenobase.prediction.model import KenoPredictor

        predictor = KenoPredictor()

        with pytest.raises(RuntimeError, match="trainiert"):
            predictor.save(tmp_path / "model")


class TestIntegration:
    """Integration tests with realistic data."""

    def test_full_workflow(self):
        """Test complete training workflow."""
        from kenobase.prediction.model import (
            KenoPredictor,
            ModelConfig,
        )

        # Simulate realistic data
        np.random.seed(42)
        n_samples = 1000
        n_features = 20

        X = np.random.randn(n_samples, n_features).astype(np.float32)
        # Imbalanced classes like real KENO (20/70 = 28.6% hits)
        y = (np.random.rand(n_samples) > 0.714).astype(np.int32)

        # Split
        split = int(0.8 * n_samples)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Train
        config = ModelConfig(
            n_estimators=50,
            num_leaves=31,
            learning_rate=0.1,
            class_weight="balanced",
        )
        predictor = KenoPredictor(config=config)

        train_metrics = predictor.train(
            X_train, y_train,
            eval_set=(X_test, y_test),
        )

        # Evaluate
        test_metrics = predictor.evaluate(X_test, y_test)

        # Predictions
        predictions = predictor.predict(X_test)

        # Assertions
        assert predictor._is_trained
        assert train_metrics.f1 > 0
        assert test_metrics.f1 > 0
        assert len(predictions) == len(X_test)

        # Cross-validation
        cv_metrics, cv_std = predictor.cross_validate(X, y, n_folds=3)
        assert cv_metrics.f1 > 0
        assert cv_std >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
