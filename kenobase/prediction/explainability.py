"""SHAP-basierte Model Explainability fuer Kenobase.

Dieses Modul implementiert SHAP (SHapley Additive exPlanations) fuer die
Erklaerbarkeit von LightGBM-Vorhersagen.

Hauptfunktionen:
- explain_single: SHAP-Werte fuer einzelne Vorhersage
- explain_batch: SHAP-Werte fuer mehrere Vorhersagen
- summary_plot: Visualisierung der wichtigsten Features
- force_plot: Visualisierung einer einzelnen Vorhersage

Referenz: TASK-P14 Model Explainability
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)

# Optional SHAP import - graceful degradation if not installed
try:
    import shap
    HAS_SHAP = True
except ImportError:
    shap = None  # type: ignore
    HAS_SHAP = False
    logger.warning("SHAP not installed. Install via: pip install shap>=0.44.0")


@dataclass
class SHAPExplanation:
    """Ergebnis einer SHAP-Erklaerung.

    Attributes:
        shap_values: SHAP-Werte pro Feature (Array oder Liste)
        base_value: Baseline-Vorhersage (expected value)
        feature_names: Namen der Features
        feature_values: Werte der Features fuer diese Vorhersage
        prediction: Finale Vorhersage (base_value + sum(shap_values))
    """

    shap_values: np.ndarray
    base_value: float
    feature_names: list[str]
    feature_values: np.ndarray
    prediction: float

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary fuer JSON-Serialisierung."""
        # Sortiere Features nach absolutem SHAP-Wert (absteigend)
        sorted_indices = np.argsort(np.abs(self.shap_values))[::-1]

        contributions = []
        for idx in sorted_indices:
            contributions.append({
                "feature": self.feature_names[idx],
                "value": round(float(self.feature_values[idx]), 4),
                "shap_value": round(float(self.shap_values[idx]), 6),
            })

        return {
            "base_value": round(self.base_value, 6),
            "prediction": round(self.prediction, 6),
            "contributions": contributions,
        }

    def get_top_features(self, n: int = 5) -> list[tuple[str, float, float]]:
        """Gibt die Top-N Features nach absolutem SHAP-Wert zurueck.

        Args:
            n: Anzahl Top-Features

        Returns:
            Liste von Tupeln (feature_name, feature_value, shap_value)
        """
        sorted_indices = np.argsort(np.abs(self.shap_values))[::-1][:n]
        return [
            (
                self.feature_names[idx],
                float(self.feature_values[idx]),
                float(self.shap_values[idx]),
            )
            for idx in sorted_indices
        ]


class SHAPExplainer:
    """SHAP-Explainer fuer LightGBM-Modelle.

    Verwendet TreeExplainer fuer optimale Performance mit LightGBM.
    TreeExplainer nutzt die Baumstruktur direkt (O(n) statt O(2^n)).

    Usage:
        predictor = KenoPredictor()
        predictor.train(X_train, y_train)

        explainer = SHAPExplainer(predictor)
        explanation = explainer.explain_single(X_test[0])

        # Oder fuer Batch:
        explanations = explainer.explain_batch(X_test[:10])
    """

    def __init__(
        self,
        predictor: Any,
        feature_names: Optional[list[str]] = None,
        check_additivity: bool = True,
    ):
        """Initialisiert den SHAP-Explainer.

        Args:
            predictor: Trainierter KenoPredictor
            feature_names: Optionale Feature-Namen (sonst aus Predictor)
            check_additivity: SHAP additivity check (kann Performance reduzieren)

        Raises:
            ImportError: Wenn SHAP nicht installiert ist
            ValueError: Wenn Predictor nicht trainiert ist
        """
        if not HAS_SHAP:
            raise ImportError(
                "SHAP ist nicht installiert. "
                "Installiere via: pip install shap>=0.44.0"
            )

        if not predictor._is_trained:
            raise ValueError("Predictor muss zuerst trainiert werden.")

        self._predictor = predictor
        self._check_additivity = check_additivity

        # Feature-Namen aus Predictor oder explizit
        if feature_names is not None:
            self._feature_names = feature_names
        elif hasattr(predictor, "FEATURE_NAMES"):
            self._feature_names = predictor.FEATURE_NAMES
        else:
            self._feature_names = [f"feature_{i}" for i in range(20)]

        # Erstelle TreeExplainer fuer LightGBM
        model = predictor._models[0]

        # Pruefe ob es ein BoosterWrapper (nach load) oder LGBMClassifier ist
        if hasattr(model, "_booster"):
            # BoosterWrapper nach model.load()
            self._explainer = shap.TreeExplainer(model._booster)
        elif hasattr(model, "booster_"):
            # LGBMClassifier nach model.train()
            self._explainer = shap.TreeExplainer(model.booster_)
        else:
            # Fallback: versuche direkt
            self._explainer = shap.TreeExplainer(model)

        # Handle expected_value which may be scalar or array
        expected = self._explainer.expected_value
        if hasattr(expected, "__len__") and len(expected) > 0:
            # Array-like: take first element (for binary classification)
            self._base_value = float(expected[0]) if len(expected) == 1 else float(expected[1])
        else:
            self._base_value = float(expected)
        logger.debug(f"SHAP TreeExplainer initialisiert. Base value: {self._base_value:.4f}")

    @property
    def base_value(self) -> float:
        """Expected value (Baseline-Vorhersage)."""
        return self._base_value

    @property
    def feature_names(self) -> list[str]:
        """Feature-Namen."""
        return self._feature_names

    def explain_single(
        self,
        X: np.ndarray,
    ) -> SHAPExplanation:
        """Erklaert eine einzelne Vorhersage.

        Args:
            X: Feature-Vektor (1D array) oder (1, n_features)

        Returns:
            SHAPExplanation mit SHAP-Werten
        """
        # Stelle sicher dass X 2D ist
        if X.ndim == 1:
            X = X.reshape(1, -1)

        shap_values = self._explainer.shap_values(X, check_additivity=self._check_additivity)

        # LightGBM binary classifier: shap_values kann [neg_class, pos_class] sein
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]  # Positive Klasse

        shap_vals = shap_values[0]  # Erste (einzige) Vorhersage
        prediction = float(self._base_value + np.sum(shap_vals))

        return SHAPExplanation(
            shap_values=shap_vals,
            base_value=self._base_value,
            feature_names=self._feature_names[:len(shap_vals)],
            feature_values=X[0],
            prediction=prediction,
        )

    def explain_batch(
        self,
        X: np.ndarray,
    ) -> list[SHAPExplanation]:
        """Erklaert mehrere Vorhersagen.

        Args:
            X: Feature-Matrix (n_samples, n_features)

        Returns:
            Liste von SHAPExplanation
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        shap_values = self._explainer.shap_values(X, check_additivity=self._check_additivity)

        # LightGBM binary classifier handling
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]

        explanations = []
        for i in range(len(X)):
            shap_vals = shap_values[i]
            prediction = float(self._base_value + np.sum(shap_vals))

            explanations.append(SHAPExplanation(
                shap_values=shap_vals,
                base_value=self._base_value,
                feature_names=self._feature_names[:len(shap_vals)],
                feature_values=X[i],
                prediction=prediction,
            ))

        return explanations

    def get_mean_abs_shap(
        self,
        X: np.ndarray,
    ) -> dict[str, float]:
        """Berechnet mittlere absolute SHAP-Werte pro Feature.

        Dies gibt eine globale Feature-Importance aehnlich wie
        get_feature_importance() aus dem Predictor.

        Args:
            X: Feature-Matrix (n_samples, n_features)

        Returns:
            Dict mit Feature-Name -> mean(|SHAP|)
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        shap_values = self._explainer.shap_values(X, check_additivity=self._check_additivity)

        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]

        mean_abs = np.mean(np.abs(shap_values), axis=0)

        return {
            name: float(val)
            for name, val in zip(self._feature_names[:len(mean_abs)], mean_abs)
        }

    def compare_with_native_importance(
        self,
        X: np.ndarray,
    ) -> tuple[dict[str, float], float]:
        """Vergleicht SHAP-Importance mit nativer LightGBM-Importance.

        Args:
            X: Feature-Matrix fuer SHAP-Berechnung

        Returns:
            Tuple aus (importance_comparison, correlation)
            - importance_comparison: Dict mit Feature -> {shap, native, diff}
            - correlation: Spearman-Korrelation zwischen SHAP und native
        """
        from scipy.stats import spearmanr

        # SHAP-based importance
        shap_importance = self.get_mean_abs_shap(X)

        # Native LightGBM importance
        native_importance = self._predictor.get_feature_importance()

        # Normalisiere SHAP importance
        shap_total = sum(shap_importance.values())
        if shap_total > 0:
            shap_normalized = {k: v / shap_total for k, v in shap_importance.items()}
        else:
            shap_normalized = shap_importance

        # Erstelle Vergleich
        comparison = {}
        shap_vals = []
        native_vals = []

        for name in self._feature_names[:len(shap_importance)]:
            shap_val = shap_normalized.get(name, 0.0)
            native_val = native_importance.get(name, 0.0)

            comparison[name] = {
                "shap": round(shap_val, 4),
                "native": round(native_val, 4),
                "diff": round(shap_val - native_val, 4),
            }

            shap_vals.append(shap_val)
            native_vals.append(native_val)

        # Berechne Korrelation
        if len(shap_vals) > 1:
            correlation, _ = spearmanr(shap_vals, native_vals)
            correlation = float(correlation) if not np.isnan(correlation) else 0.0
        else:
            correlation = 0.0

        return comparison, correlation

    def summary_plot(
        self,
        X: np.ndarray,
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        max_display: int = 10,
    ) -> None:
        """Erstellt SHAP Summary Plot.

        Args:
            X: Feature-Matrix
            output_path: Optionaler Pfad zum Speichern (PNG)
            show: Plot anzeigen (default True)
            max_display: Maximale Anzahl Features im Plot
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("matplotlib nicht installiert. Summary plot nicht moeglich.")
            return

        if X.ndim == 1:
            X = X.reshape(1, -1)

        shap_values = self._explainer.shap_values(X, check_additivity=self._check_additivity)

        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]

        plt.figure(figsize=(10, 6))
        shap.summary_plot(
            shap_values,
            X,
            feature_names=self._feature_names[:X.shape[1]],
            max_display=max_display,
            show=False,
        )

        if output_path is not None:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
            logger.info(f"Summary plot gespeichert: {output_path}")

        if show:
            plt.show()
        plt.close()

    def force_plot(
        self,
        X: np.ndarray,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Optional[Any]:
        """Erstellt SHAP Force Plot fuer einzelne Vorhersage.

        Args:
            X: Feature-Vektor (1D oder 1 x n_features)
            output_path: Optionaler Pfad zum Speichern (HTML)

        Returns:
            SHAP Force Plot Objekt (fuer Jupyter Display)
        """
        if X.ndim == 1:
            X = X.reshape(1, -1)

        shap_values = self._explainer.shap_values(X, check_additivity=self._check_additivity)

        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]

        force = shap.force_plot(
            self._base_value,
            shap_values[0],
            X[0],
            feature_names=self._feature_names[:X.shape[1]],
        )

        if output_path is not None:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shap.save_html(str(output_path), force)
            logger.info(f"Force plot gespeichert: {output_path}")

        return force


def validate_shap_native_correlation(
    predictor: Any,
    X: np.ndarray,
    threshold: float = 0.7,
) -> tuple[bool, float, dict[str, Any]]:
    """Validiert dass SHAP-Importance mit nativer LightGBM-Importance korreliert.

    Dies ist ein Acceptance Test fuer TASK-P14:
    SHAP und native Importance sollten >= 0.7 korrelieren.

    Args:
        predictor: Trainierter KenoPredictor
        X: Feature-Matrix fuer SHAP-Berechnung
        threshold: Mindest-Korrelation (default 0.7)

    Returns:
        Tuple aus (passed, correlation, details)
    """
    if not HAS_SHAP:
        return False, 0.0, {"error": "SHAP not installed"}

    explainer = SHAPExplainer(predictor)
    comparison, correlation = explainer.compare_with_native_importance(X)

    passed = correlation >= threshold

    return passed, correlation, {
        "threshold": threshold,
        "correlation": correlation,
        "passed": passed,
        "feature_comparison": comparison,
    }


__all__ = [
    "SHAPExplanation",
    "SHAPExplainer",
    "HAS_SHAP",
    "validate_shap_native_correlation",
]
