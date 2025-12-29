"""ML Model Wrapper - LightGBM Binary Classifier fuer Zahlenvorhersage.

Dieses Modul implementiert das ML-Modell fuer KENO-Zahlenvorhersage
basierend auf der TASK-P02 Spezifikation (ARCHITECT Handoff).

Modell: LightGBM Binary Classifier
- Pro Zahl (1-70) ein Modell: hit=1, miss=0
- Features: 20 aus FeatureExtractor
- CV: 5-Fold + Walk-Forward
- Ziel: F1 >= 0.50, Stability std <= 0.05

Hyperparameter-Ranges (Optuna):
- learning_rate: [0.01, 0.3]
- num_leaves: [15, 63]
- max_depth: [3, 12]
- min_child_samples: [10, 100]
- subsample: [0.6, 1.0]
- colsample_bytree: [0.6, 1.0]
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)

# Optional imports - graceful degradation if not installed
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    lgb = None
    HAS_LIGHTGBM = False
    logger.warning("LightGBM not installed. Install via: pip install lightgbm")

try:
    import optuna
    HAS_OPTUNA = True
except ImportError:
    optuna = None
    HAS_OPTUNA = False
    logger.warning("Optuna not installed. Hyperparameter tuning disabled.")


@dataclass
class ModelConfig:
    """Konfiguration fuer das LightGBM Modell.

    Attributes:
        num_leaves: Anzahl Blaetter pro Baum
        max_depth: Maximale Baumtiefe (-1 = unbegrenzt)
        learning_rate: Lernrate
        n_estimators: Anzahl Baeume
        min_child_samples: Minimale Samples pro Blatt
        subsample: Anteil Samples pro Baum
        colsample_bytree: Anteil Features pro Baum
        reg_alpha: L1 Regularisierung
        reg_lambda: L2 Regularisierung
        random_state: Seed fuer Reproduzierbarkeit
        class_weight: Gewichtung fuer unbalancierte Klassen
    """

    num_leaves: int = 31
    max_depth: int = -1
    learning_rate: float = 0.05
    n_estimators: int = 100
    min_child_samples: int = 20
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    reg_alpha: float = 0.0
    reg_lambda: float = 0.0
    random_state: int = 42
    class_weight: Optional[str] = "balanced"

    def to_lgb_params(self) -> dict[str, Any]:
        """Konvertiert zu LightGBM-Parametern."""
        return {
            "boosting_type": "gbdt",
            "objective": "binary",
            "metric": ["binary_logloss", "auc"],
            "num_leaves": self.num_leaves,
            "max_depth": self.max_depth,
            "learning_rate": self.learning_rate,
            "n_estimators": self.n_estimators,
            "min_child_samples": self.min_child_samples,
            "subsample": self.subsample,
            "colsample_bytree": self.colsample_bytree,
            "reg_alpha": self.reg_alpha,
            "reg_lambda": self.reg_lambda,
            "random_state": self.random_state,
            "class_weight": self.class_weight,
            "verbose": -1,
        }


@dataclass
class PredictionResult:
    """Ergebnis einer Vorhersage.

    Attributes:
        number: Die vorhergesagte Zahl
        probability: Wahrscheinlichkeit fuer hit (0-1)
        prediction: Binaere Vorhersage (0 oder 1)
        confidence: Konfidenz der Vorhersage
        features: Feature-Werte die zur Vorhersage gefuehrt haben
    """

    number: int
    probability: float
    prediction: int
    confidence: float = 0.5
    features: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "number": self.number,
            "probability": round(self.probability, 4),
            "prediction": self.prediction,
            "confidence": round(self.confidence, 4),
            "features": {k: round(v, 4) for k, v in self.features.items()},
        }


@dataclass
class ModelMetrics:
    """Metriken fuer Modell-Evaluation.

    Attributes:
        precision: Precision Score
        recall: Recall Score
        f1: F1 Score
        accuracy: Accuracy Score
        auc_roc: Area Under ROC Curve
        n_samples: Anzahl Samples
    """

    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    accuracy: float = 0.0
    auc_roc: float = 0.0
    n_samples: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "accuracy": round(self.accuracy, 4),
            "auc_roc": round(self.auc_roc, 4),
            "n_samples": self.n_samples,
        }


class KenoPredictor:
    """LightGBM-basierter Predictor fuer KENO-Zahlen.

    Trainiert ein Modell pro Zahl (1-70) zur Vorhersage ob die Zahl
    in der naechsten Ziehung erscheint.

    Verwendung:
        predictor = KenoPredictor()
        predictor.train(X_train, y_train)
        predictions = predictor.predict(X_test)

    Args:
        config: ModelConfig mit Hyperparametern
        numbers_range: Zahlenbereich (default KENO: 1-70)
    """

    FEATURE_NAMES = [
        # Frequency (4)
        "freq_raw", "freq_rolling", "freq_hot", "freq_cold",
        # Pattern (3)
        "duo_score", "trio_score", "quatro_score",
        # Temporal (3)
        "weekday_bias", "month_bias", "holiday_proximity",
        # Popularity (3)
        "is_birthday", "is_schoene", "is_safe",
        # Stake (2)
        "einsatz_score", "auszahlung_score",
        # Recurrence (2)
        "streak_length", "stability_score",
        # Stability (1)
        "law_a_score",
        # Cluster (2)
        "reset_probability", "cluster_signal",
    ]

    def __init__(
        self,
        config: Optional[ModelConfig] = None,
        numbers_range: tuple[int, int] = (1, 70),
    ):
        """Initialisiert den Predictor.

        Args:
            config: Optionale ModelConfig
            numbers_range: Zahlenbereich (min, max)
        """
        if not HAS_LIGHTGBM:
            raise ImportError(
                "LightGBM ist nicht installiert. "
                "Installiere via: pip install lightgbm"
            )

        self.config = config or ModelConfig()
        self.numbers_range = numbers_range
        self._models: dict[int, lgb.LGBMClassifier] = {}
        self._is_trained = False
        self._feature_importance: dict[str, float] = {}

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[list[str]] = None,
        eval_set: Optional[tuple[np.ndarray, np.ndarray]] = None,
    ) -> ModelMetrics:
        """Trainiert das Modell.

        Args:
            X: Feature-Matrix (n_samples, n_features)
            y: Target-Vektor (n_samples,) mit Werten 0 oder 1
            feature_names: Optionale Feature-Namen
            eval_set: Optionales Validierungs-Set (X_val, y_val)

        Returns:
            ModelMetrics mit Training-Metriken
        """
        feature_names = feature_names or self.FEATURE_NAMES

        # Single model approach (binary classification)
        params = self.config.to_lgb_params()
        model = lgb.LGBMClassifier(**params)

        callbacks = []
        if eval_set is not None:
            X_val, y_val = eval_set
            callbacks.append(lgb.early_stopping(stopping_rounds=10, verbose=False))
            model.fit(
                X, y,
                eval_set=[(X_val, y_val)],
                callbacks=callbacks,
            )
        else:
            model.fit(X, y)

        self._models[0] = model  # Single model stored at key 0
        self._is_trained = True

        # Calculate feature importance
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            for i, name in enumerate(feature_names[:len(importances)]):
                self._feature_importance[name] = float(importances[i])

        # Calculate training metrics
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1]

        return self._calculate_metrics(y, y_pred, y_proba)

    def predict(
        self,
        X: np.ndarray,
        threshold: float = 0.5,
    ) -> list[PredictionResult]:
        """Macht Vorhersagen fuer Feature-Vektoren.

        Args:
            X: Feature-Matrix (n_samples, n_features)
            threshold: Schwelle fuer binaere Klassifikation

        Returns:
            Liste von PredictionResult
        """
        if not self._is_trained:
            raise RuntimeError("Model muss zuerst trainiert werden.")

        model = self._models[0]
        probabilities = model.predict_proba(X)[:, 1]
        predictions = (probabilities >= threshold).astype(int)

        results = []
        for i, (prob, pred) in enumerate(zip(probabilities, predictions)):
            # Confidence: Distanz zur Entscheidungsgrenze
            confidence = abs(prob - threshold) / max(threshold, 1 - threshold)

            results.append(PredictionResult(
                number=i + self.numbers_range[0],
                probability=float(prob),
                prediction=int(pred),
                confidence=float(confidence),
            ))

        return results

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Gibt Wahrscheinlichkeiten zurueck.

        Args:
            X: Feature-Matrix

        Returns:
            Array mit Wahrscheinlichkeiten (n_samples,)
        """
        if not self._is_trained:
            raise RuntimeError("Model muss zuerst trainiert werden.")

        return self._models[0].predict_proba(X)[:, 1]

    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
    ) -> ModelMetrics:
        """Evaluiert das Modell auf Test-Daten.

        Args:
            X: Feature-Matrix
            y: Target-Vektor

        Returns:
            ModelMetrics
        """
        if not self._is_trained:
            raise RuntimeError("Model muss zuerst trainiert werden.")

        model = self._models[0]
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1]

        return self._calculate_metrics(y, y_pred, y_proba)

    def cross_validate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_folds: int = 5,
    ) -> tuple[ModelMetrics, float]:
        """Fuehrt k-Fold Cross-Validation durch.

        Args:
            X: Feature-Matrix
            y: Target-Vektor
            n_folds: Anzahl Folds

        Returns:
            Tuple aus (mittlere Metriken, F1 Standardabweichung)
        """
        from sklearn.model_selection import StratifiedKFold

        kfold = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

        f1_scores = []
        all_metrics = []

        for fold, (train_idx, val_idx) in enumerate(kfold.split(X, y)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            # Train fold model
            params = self.config.to_lgb_params()
            model = lgb.LGBMClassifier(**params)
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_val)
            y_proba = model.predict_proba(X_val)[:, 1]
            metrics = self._calculate_metrics(y_val, y_pred, y_proba)

            f1_scores.append(metrics.f1)
            all_metrics.append(metrics)

            logger.debug(f"Fold {fold + 1}/{n_folds}: F1={metrics.f1:.4f}")

        # Average metrics
        avg_metrics = ModelMetrics(
            precision=np.mean([m.precision for m in all_metrics]),
            recall=np.mean([m.recall for m in all_metrics]),
            f1=np.mean([m.f1 for m in all_metrics]),
            accuracy=np.mean([m.accuracy for m in all_metrics]),
            auc_roc=np.mean([m.auc_roc for m in all_metrics]),
            n_samples=len(y),
        )

        f1_std = float(np.std(f1_scores))
        logger.info(f"CV Results: F1={avg_metrics.f1:.4f} +/- {f1_std:.4f}")

        return avg_metrics, f1_std

    def tune_hyperparameters(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_trials: int = 50,
        n_folds: int = 5,
    ) -> ModelConfig:
        """Tuned Hyperparameter mit Optuna.

        Args:
            X: Feature-Matrix
            y: Target-Vektor
            n_trials: Anzahl Optuna Trials
            n_folds: Anzahl CV Folds

        Returns:
            Beste ModelConfig
        """
        if not HAS_OPTUNA:
            logger.warning("Optuna nicht installiert. Verwende Default-Config.")
            return self.config

        from sklearn.model_selection import cross_val_score

        def objective(trial: optuna.Trial) -> float:
            params = {
                "boosting_type": "gbdt",
                "objective": "binary",
                "metric": "binary_logloss",
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "num_leaves": trial.suggest_int("num_leaves", 15, 63),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 1.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 1.0, log=True),
                "random_state": 42,
                "verbose": -1,
                "n_estimators": 100,
            }

            model = lgb.LGBMClassifier(**params)
            scores = cross_val_score(
                model, X, y, cv=n_folds, scoring="f1", n_jobs=-1
            )
            return float(np.mean(scores))

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

        best_params = study.best_params
        logger.info(f"Best trial: F1={study.best_value:.4f}")
        logger.info(f"Best params: {best_params}")

        return ModelConfig(
            learning_rate=best_params["learning_rate"],
            num_leaves=best_params["num_leaves"],
            max_depth=best_params["max_depth"],
            min_child_samples=best_params["min_child_samples"],
            subsample=best_params["subsample"],
            colsample_bytree=best_params["colsample_bytree"],
            reg_alpha=best_params["reg_alpha"],
            reg_lambda=best_params["reg_lambda"],
        )

    def get_feature_importance(self) -> dict[str, float]:
        """Gibt Feature-Importance zurueck.

        Returns:
            Dict mit Feature-Name -> Importance
        """
        if not self._feature_importance:
            return {}

        # Normalize to sum to 1
        total = sum(self._feature_importance.values())
        if total > 0:
            return {k: v / total for k, v in self._feature_importance.items()}
        return self._feature_importance

    def save(self, path: Union[str, Path]) -> None:
        """Speichert das Modell.

        Args:
            path: Pfad zur Modell-Datei (ohne Extension)
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not self._is_trained:
            raise RuntimeError("Model muss zuerst trainiert werden.")

        # Save model
        model = self._models[0]
        model.booster_.save_model(str(path.with_suffix(".lgb")))

        # Save config and metadata
        metadata = {
            "config": {
                "num_leaves": self.config.num_leaves,
                "max_depth": self.config.max_depth,
                "learning_rate": self.config.learning_rate,
                "n_estimators": self.config.n_estimators,
                "min_child_samples": self.config.min_child_samples,
                "subsample": self.config.subsample,
                "colsample_bytree": self.config.colsample_bytree,
            },
            "numbers_range": list(self.numbers_range),
            "feature_importance": self._feature_importance,
            "feature_names": self.FEATURE_NAMES,
        }

        with open(path.with_suffix(".json"), "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Model saved to {path}")

    def load(self, path: Union[str, Path]) -> None:
        """Laedt ein gespeichertes Modell.

        Args:
            path: Pfad zur Modell-Datei (ohne Extension)
        """
        path = Path(path)

        # Load metadata
        with open(path.with_suffix(".json"), "r") as f:
            metadata = json.load(f)

        self.numbers_range = tuple(metadata["numbers_range"])
        self._feature_importance = metadata.get("feature_importance", {})

        # Load model - use Booster directly for prediction
        booster = lgb.Booster(model_file=str(path.with_suffix(".lgb")))

        # Create wrapper that uses booster directly
        class BoosterWrapper:
            """Wrapper to use Booster with sklearn-like API."""

            def __init__(self, booster):
                self._booster = booster

            def predict_proba(self, X):
                """Predict class probabilities."""
                raw_preds = self._booster.predict(X)
                # LightGBM returns probabilities for binary classification
                proba_1 = np.clip(raw_preds, 0, 1)
                proba_0 = 1 - proba_1
                return np.column_stack([proba_0, proba_1])

            def predict(self, X):
                """Predict class labels."""
                proba = self.predict_proba(X)
                return (proba[:, 1] >= 0.5).astype(int)

        self._models[0] = BoosterWrapper(booster)
        self._is_trained = True

        logger.info(f"Model loaded from {path}")

    def _calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: np.ndarray,
    ) -> ModelMetrics:
        """Berechnet Evaluations-Metriken.

        Args:
            y_true: Wahre Labels
            y_pred: Vorhergesagte Labels
            y_proba: Vorhergesagte Wahrscheinlichkeiten

        Returns:
            ModelMetrics
        """
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            roc_auc_score,
        )

        # Handle edge cases
        if len(np.unique(y_true)) < 2:
            logger.warning("Only one class in y_true. Metrics may be unreliable.")
            auc = 0.5
        else:
            try:
                auc = roc_auc_score(y_true, y_proba)
            except ValueError:
                auc = 0.5

        return ModelMetrics(
            precision=precision_score(y_true, y_pred, zero_division=0),
            recall=recall_score(y_true, y_pred, zero_division=0),
            f1=f1_score(y_true, y_pred, zero_division=0),
            accuracy=accuracy_score(y_true, y_pred),
            auc_roc=auc,
            n_samples=len(y_true),
        )


__all__ = [
    "ModelConfig",
    "ModelMetrics",
    "PredictionResult",
    "KenoPredictor",
    "HAS_LIGHTGBM",
    "HAS_OPTUNA",
]
