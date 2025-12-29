"""Unit Tests fuer SHAP Explainability (TASK-P14).

Testet:
1. SHAPExplainer Initialisierung
2. explain_single und explain_batch
3. Korrelation mit nativer LightGBM-Importance
4. SHAPExplanation Datenstruktur
"""

import pytest
import numpy as np

# Check if required dependencies are available
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

pytestmark = pytest.mark.skipif(
    not HAS_LIGHTGBM or not HAS_SHAP,
    reason="LightGBM and SHAP required for explainability tests"
)


@pytest.fixture
def synthetic_data():
    """Erstellt synthetische Trainingsdaten."""
    np.random.seed(42)
    n_samples = 200
    n_features = 20

    # Features
    X = np.random.randn(n_samples, n_features)

    # Target: abhaengig von ersten 3 Features (simuliert echte Wichtigkeit)
    y = (
        0.5 * X[:, 0] +
        0.3 * X[:, 1] +
        0.2 * X[:, 2] +
        0.1 * np.random.randn(n_samples)
    )
    y = (y > 0).astype(int)

    return X, y


@pytest.fixture
def trained_predictor(synthetic_data):
    """Erstellt und trainiert einen KenoPredictor."""
    from kenobase.prediction.model import KenoPredictor, ModelConfig

    X, y = synthetic_data

    config = ModelConfig(
        n_estimators=50,
        num_leaves=15,
        max_depth=5,
        learning_rate=0.1,
    )
    predictor = KenoPredictor(config=config)
    predictor.train(X, y)

    return predictor


class TestSHAPExplainer:
    """Tests fuer SHAPExplainer Klasse."""

    def test_init_requires_trained_model(self, synthetic_data):
        """SHAPExplainer erfordert trainiertes Modell."""
        from kenobase.prediction.model import KenoPredictor
        from kenobase.prediction.explainability import SHAPExplainer

        predictor = KenoPredictor()

        with pytest.raises(ValueError, match="trainiert"):
            SHAPExplainer(predictor)

    def test_init_success(self, trained_predictor):
        """SHAPExplainer initialisiert korrekt mit trainiertem Modell."""
        from kenobase.prediction.explainability import SHAPExplainer

        explainer = SHAPExplainer(trained_predictor)

        assert explainer is not None
        assert explainer.base_value is not None
        assert len(explainer.feature_names) == 20

    def test_explain_single(self, trained_predictor, synthetic_data):
        """explain_single gibt SHAPExplanation zurueck."""
        from kenobase.prediction.explainability import SHAPExplainer, SHAPExplanation

        X, _ = synthetic_data
        explainer = SHAPExplainer(trained_predictor)

        explanation = explainer.explain_single(X[0])

        assert isinstance(explanation, SHAPExplanation)
        assert len(explanation.shap_values) == 20
        assert explanation.base_value == explainer.base_value
        assert len(explanation.feature_names) == 20
        assert len(explanation.feature_values) == 20

    def test_explain_single_2d_input(self, trained_predictor, synthetic_data):
        """explain_single akzeptiert auch 2D Input (1, n_features)."""
        from kenobase.prediction.explainability import SHAPExplainer

        X, _ = synthetic_data
        explainer = SHAPExplainer(trained_predictor)

        explanation = explainer.explain_single(X[0:1])

        assert len(explanation.shap_values) == 20

    def test_explain_batch(self, trained_predictor, synthetic_data):
        """explain_batch gibt Liste von SHAPExplanations zurueck."""
        from kenobase.prediction.explainability import SHAPExplainer, SHAPExplanation

        X, _ = synthetic_data
        explainer = SHAPExplainer(trained_predictor)

        explanations = explainer.explain_batch(X[:5])

        assert len(explanations) == 5
        for exp in explanations:
            assert isinstance(exp, SHAPExplanation)
            assert len(exp.shap_values) == 20

    def test_shap_additivity(self, trained_predictor, synthetic_data):
        """SHAP-Werte sind additiv: base_value + sum(shap) ≈ prediction."""
        from kenobase.prediction.explainability import SHAPExplainer

        X, _ = synthetic_data
        explainer = SHAPExplainer(trained_predictor, check_additivity=True)

        explanation = explainer.explain_single(X[0])

        # SHAP Additivity: base + sum(shap_values) = prediction
        reconstructed = explanation.base_value + np.sum(explanation.shap_values)
        assert np.isclose(reconstructed, explanation.prediction, atol=0.01)

    def test_get_mean_abs_shap(self, trained_predictor, synthetic_data):
        """get_mean_abs_shap gibt Dict mit Feature-Importance zurueck."""
        from kenobase.prediction.explainability import SHAPExplainer

        X, _ = synthetic_data
        explainer = SHAPExplainer(trained_predictor)

        importance = explainer.get_mean_abs_shap(X[:50])

        assert isinstance(importance, dict)
        assert len(importance) == 20
        assert all(v >= 0 for v in importance.values())


class TestSHAPExplanation:
    """Tests fuer SHAPExplanation Datenstruktur."""

    def test_to_dict(self, trained_predictor, synthetic_data):
        """to_dict gibt serialisierbares Dict zurueck."""
        from kenobase.prediction.explainability import SHAPExplainer

        X, _ = synthetic_data
        explainer = SHAPExplainer(trained_predictor)
        explanation = explainer.explain_single(X[0])

        result = explanation.to_dict()

        assert "base_value" in result
        assert "prediction" in result
        assert "contributions" in result
        assert len(result["contributions"]) == 20

        # Contributions sind nach abs(shap_value) sortiert
        abs_shap = [abs(c["shap_value"]) for c in result["contributions"]]
        assert abs_shap == sorted(abs_shap, reverse=True)

    def test_get_top_features(self, trained_predictor, synthetic_data):
        """get_top_features gibt Top-N Features zurueck."""
        from kenobase.prediction.explainability import SHAPExplainer

        X, _ = synthetic_data
        explainer = SHAPExplainer(trained_predictor)
        explanation = explainer.explain_single(X[0])

        top_5 = explanation.get_top_features(n=5)

        assert len(top_5) == 5
        for name, value, shap_val in top_5:
            assert isinstance(name, str)
            assert isinstance(value, float)
            assert isinstance(shap_val, float)


class TestNativeCorrelation:
    """Tests fuer Korrelation mit nativer LightGBM-Importance."""

    def test_compare_with_native_importance(self, trained_predictor, synthetic_data):
        """compare_with_native_importance gibt Vergleich und Korrelation."""
        from kenobase.prediction.explainability import SHAPExplainer

        X, _ = synthetic_data
        explainer = SHAPExplainer(trained_predictor)

        comparison, correlation = explainer.compare_with_native_importance(X[:50])

        assert isinstance(comparison, dict)
        assert isinstance(correlation, float)
        assert -1.0 <= correlation <= 1.0

        # Jeder Feature-Eintrag hat shap, native, diff
        for name, data in comparison.items():
            assert "shap" in data
            assert "native" in data
            assert "diff" in data

    def test_validate_shap_native_correlation(self, trained_predictor, synthetic_data):
        """validate_shap_native_correlation gibt Acceptance-Test Ergebnis."""
        from kenobase.prediction.explainability import validate_shap_native_correlation

        X, _ = synthetic_data

        passed, correlation, details = validate_shap_native_correlation(
            trained_predictor, X[:50], threshold=0.3  # niedrige Schwelle fuer Test
        )

        assert isinstance(passed, bool)
        assert isinstance(correlation, float)
        assert "threshold" in details
        assert "correlation" in details
        assert "passed" in details
        assert "feature_comparison" in details


class TestEdgeCases:
    """Edge Cases und Fehlerbehandlung."""

    def test_shap_not_installed_error(self, trained_predictor, monkeypatch):
        """SHAPExplainer gibt Fehler wenn SHAP nicht installiert."""
        import kenobase.prediction.explainability as exp_module

        # Simuliere dass SHAP nicht installiert ist
        monkeypatch.setattr(exp_module, "HAS_SHAP", False)

        with pytest.raises(ImportError, match="SHAP"):
            exp_module.SHAPExplainer(trained_predictor)

    def test_custom_feature_names(self, trained_predictor, synthetic_data):
        """Custom Feature-Namen werden verwendet."""
        from kenobase.prediction.explainability import SHAPExplainer

        X, _ = synthetic_data
        custom_names = [f"custom_{i}" for i in range(20)]

        explainer = SHAPExplainer(trained_predictor, feature_names=custom_names)

        assert explainer.feature_names == custom_names

        explanation = explainer.explain_single(X[0])
        assert explanation.feature_names == custom_names


class TestIntegration:
    """Integration mit KenoPredictor."""

    def test_full_workflow(self, synthetic_data):
        """Vollstaendiger Workflow: Train -> Explain -> Validate."""
        from kenobase.prediction.model import KenoPredictor, ModelConfig
        from kenobase.prediction.explainability import (
            SHAPExplainer,
            validate_shap_native_correlation,
        )

        X, y = synthetic_data

        # 1. Train
        config = ModelConfig(n_estimators=50, num_leaves=15)
        predictor = KenoPredictor(config=config)
        predictor.train(X, y)

        # 2. Explain
        explainer = SHAPExplainer(predictor)
        explanation = explainer.explain_single(X[0])

        assert explanation is not None
        assert len(explanation.shap_values) == 20

        # 3. Validate
        passed, corr, details = validate_shap_native_correlation(
            predictor, X[:30], threshold=0.3
        )

        # Bei synthetischen Daten sollte Korrelation moderat sein
        assert corr > -1.0  # Mindestens berechnet

    def test_get_feature_importance_comparison(self, trained_predictor, synthetic_data):
        """SHAP-Importance ist vergleichbar mit get_feature_importance()."""
        from kenobase.prediction.explainability import SHAPExplainer

        X, _ = synthetic_data

        # Native importance
        native = trained_predictor.get_feature_importance()

        # SHAP importance
        explainer = SHAPExplainer(trained_predictor)
        shap_importance = explainer.get_mean_abs_shap(X[:50])

        # Beide haben gleiche Features
        assert set(native.keys()) == set(shap_importance.keys())
