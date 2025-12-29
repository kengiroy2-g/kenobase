"""ML Trainer - Training + Cross-Validation Logic fuer KENO Predictor.

Dieses Modul orchestriert das Training des LightGBM Modells mit:
- Walk-Forward Validation (Train 6 Monate, Test 1 Monat)
- 5-Fold Cross-Validation
- Hyperparameter-Tuning via Optuna
- Stabilitaets-Analyse ueber alle Perioden

TASK-P02 Acceptance Criteria:
- F1 >= 0.50
- Stability std <= 0.05
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np
import pandas as pd

from kenobase.core.data_loader import DrawResult, DataLoader
from kenobase.features import FeatureExtractor, FeatureVector
from kenobase.prediction.model import (
    KenoPredictor,
    ModelConfig,
    ModelMetrics,
    HAS_LIGHTGBM,
)

logger = logging.getLogger(__name__)


@dataclass
class WalkForwardConfig:
    """Konfiguration fuer Walk-Forward Validation.

    Attributes:
        train_months: Anzahl Trainings-Monate
        test_months: Anzahl Test-Monate
        step_months: Schrittweite in Monaten
        min_train_samples: Minimale Trainings-Samples
    """

    train_months: int = 6
    test_months: int = 1
    step_months: int = 1
    min_train_samples: int = 100


@dataclass
class WalkForwardResult:
    """Ergebnis einer Walk-Forward Periode.

    Attributes:
        period_idx: Index der Periode
        train_start: Startdatum Training
        train_end: Enddatum Training
        test_start: Startdatum Test
        test_end: Enddatum Test
        metrics: Metriken fuer diese Periode
        n_train: Anzahl Trainings-Samples
        n_test: Anzahl Test-Samples
    """

    period_idx: int
    train_start: date
    train_end: date
    test_start: date
    test_end: date
    metrics: ModelMetrics
    n_train: int = 0
    n_test: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "period_idx": self.period_idx,
            "train_start": str(self.train_start),
            "train_end": str(self.train_end),
            "test_start": str(self.test_start),
            "test_end": str(self.test_end),
            "metrics": self.metrics.to_dict(),
            "n_train": self.n_train,
            "n_test": self.n_test,
        }


@dataclass
class TrainingReport:
    """Vollstaendiger Training-Report.

    Attributes:
        model_type: Typ des Modells (z.B. "LightGBM")
        config: Verwendete ModelConfig
        cv_metrics: Cross-Validation Metriken
        cv_f1_std: F1 Standardabweichung in CV
        wf_results: Walk-Forward Ergebnisse pro Periode
        wf_metrics: Aggregierte Walk-Forward Metriken
        wf_f1_std: F1 Standardabweichung in Walk-Forward
        feature_importance: Feature-Importance Ranking
        acceptance_passed: Ob Acceptance Criteria erfuellt
    """

    model_type: str = "LightGBM"
    config: Optional[ModelConfig] = None
    cv_metrics: Optional[ModelMetrics] = None
    cv_f1_std: float = 0.0
    wf_results: list[WalkForwardResult] = field(default_factory=list)
    wf_metrics: Optional[ModelMetrics] = None
    wf_f1_std: float = 0.0
    feature_importance: dict[str, float] = field(default_factory=dict)
    acceptance_passed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "model_type": self.model_type,
            "config": {
                "num_leaves": self.config.num_leaves if self.config else None,
                "learning_rate": self.config.learning_rate if self.config else None,
                "max_depth": self.config.max_depth if self.config else None,
            },
            "cv_metrics": self.cv_metrics.to_dict() if self.cv_metrics else None,
            "cv_f1_std": round(self.cv_f1_std, 4),
            "wf_results": [r.to_dict() for r in self.wf_results],
            "wf_metrics": self.wf_metrics.to_dict() if self.wf_metrics else None,
            "wf_f1_std": round(self.wf_f1_std, 4),
            "feature_importance": {
                k: round(v, 4) for k, v in self.feature_importance.items()
            },
            "acceptance_passed": self.acceptance_passed,
            "acceptance_criteria": {
                "f1_target": 0.50,
                "f1_actual": round(self.wf_metrics.f1, 4) if self.wf_metrics else 0,
                "stability_target": 0.05,
                "stability_actual": round(self.wf_f1_std, 4),
            },
        }

    def save(self, path: Union[str, Path]) -> None:
        """Speichert den Report als JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to {path}")


class KenoTrainer:
    """Trainer fuer KENO Prediction Model.

    Orchestriert Training, Cross-Validation und Walk-Forward Testing.

    Verwendung:
        trainer = KenoTrainer()
        report = trainer.train_and_evaluate(draws)
        trainer.save_model("models/keno_predictor")
    """

    # Target: F1 >= 0.50, Stability std <= 0.05
    F1_TARGET = 0.50
    STABILITY_TARGET = 0.05

    def __init__(
        self,
        model_config: Optional[ModelConfig] = None,
        wf_config: Optional[WalkForwardConfig] = None,
        numbers_range: tuple[int, int] = (1, 70),
        numbers_to_draw: int = 20,
    ):
        """Initialisiert den Trainer.

        Args:
            model_config: Optionale ModelConfig
            wf_config: Optionale WalkForwardConfig
            numbers_range: Zahlenbereich
            numbers_to_draw: Anzahl gezogener Zahlen
        """
        if not HAS_LIGHTGBM:
            raise ImportError("LightGBM required. Install via: pip install lightgbm")

        self.model_config = model_config or ModelConfig()
        self.wf_config = wf_config or WalkForwardConfig()
        self.numbers_range = numbers_range
        self.numbers_to_draw = numbers_to_draw

        self._predictor: Optional[KenoPredictor] = None
        self._extractor = FeatureExtractor(
            numbers_range=numbers_range,
            numbers_to_draw=numbers_to_draw,
        )

    def train_and_evaluate(
        self,
        draws: list[DrawResult],
        tune_hyperparameters: bool = False,
        n_cv_folds: int = 5,
    ) -> TrainingReport:
        """Trainiert und evaluiert das Modell.

        Fuehrt folgende Schritte durch:
        1. Feature-Extraktion
        2. Optional: Hyperparameter-Tuning
        3. Cross-Validation
        4. Walk-Forward Validation
        5. Finales Training

        Args:
            draws: Liste von DrawResult-Objekten
            tune_hyperparameters: Ob Hyperparameter getuned werden sollen
            n_cv_folds: Anzahl CV Folds

        Returns:
            TrainingReport mit allen Metriken
        """
        logger.info(f"Starting training with {len(draws)} draws")

        report = TrainingReport(config=self.model_config)

        # Prepare data
        X, y = self._prepare_training_data(draws)
        logger.info(f"Prepared {len(X)} samples with {X.shape[1]} features")

        # Optional: Hyperparameter tuning
        if tune_hyperparameters:
            logger.info("Tuning hyperparameters...")
            predictor = KenoPredictor(config=self.model_config)
            self.model_config = predictor.tune_hyperparameters(X, y, n_trials=50)
            report.config = self.model_config

        # Cross-Validation
        logger.info(f"Running {n_cv_folds}-fold cross-validation...")
        predictor = KenoPredictor(config=self.model_config)
        cv_metrics, cv_f1_std = predictor.cross_validate(X, y, n_folds=n_cv_folds)
        report.cv_metrics = cv_metrics
        report.cv_f1_std = cv_f1_std

        logger.info(f"CV F1: {cv_metrics.f1:.4f} +/- {cv_f1_std:.4f}")

        # Walk-Forward Validation
        logger.info("Running walk-forward validation...")
        wf_results = self._walk_forward_validation(draws)
        report.wf_results = wf_results

        if wf_results:
            f1_scores = [r.metrics.f1 for r in wf_results]
            report.wf_metrics = ModelMetrics(
                precision=np.mean([r.metrics.precision for r in wf_results]),
                recall=np.mean([r.metrics.recall for r in wf_results]),
                f1=np.mean(f1_scores),
                accuracy=np.mean([r.metrics.accuracy for r in wf_results]),
                auc_roc=np.mean([r.metrics.auc_roc for r in wf_results]),
                n_samples=sum(r.n_test for r in wf_results),
            )
            report.wf_f1_std = float(np.std(f1_scores))

            logger.info(
                f"Walk-Forward F1: {report.wf_metrics.f1:.4f} "
                f"+/- {report.wf_f1_std:.4f}"
            )

        # Final training on all data
        logger.info("Training final model on all data...")
        self._predictor = KenoPredictor(config=self.model_config)
        self._predictor.train(X, y)
        report.feature_importance = self._predictor.get_feature_importance()

        # Check acceptance criteria
        if report.wf_metrics:
            f1_passed = report.wf_metrics.f1 >= self.F1_TARGET
            stability_passed = report.wf_f1_std <= self.STABILITY_TARGET
            report.acceptance_passed = f1_passed and stability_passed

            logger.info(
                f"Acceptance: F1 >= {self.F1_TARGET}: "
                f"{'PASS' if f1_passed else 'FAIL'} ({report.wf_metrics.f1:.4f})"
            )
            logger.info(
                f"Acceptance: Stability <= {self.STABILITY_TARGET}: "
                f"{'PASS' if stability_passed else 'FAIL'} ({report.wf_f1_std:.4f})"
            )

        return report

    def _prepare_training_data(
        self,
        draws: list[DrawResult],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Bereitet Trainings-Daten vor.

        Extrahiert Features und erstellt Labels (hit/miss).

        Args:
            draws: Liste von DrawResult-Objekten

        Returns:
            Tuple aus (X, y) - Feature-Matrix und Labels
        """
        if len(draws) < 2:
            raise ValueError("Mindestens 2 Ziehungen erforderlich")

        # Extract features for each draw (using previous draws as context)
        X_list = []
        y_list = []

        for i in range(1, len(draws)):
            # Features based on previous draws
            context_draws = draws[:i]
            vectors = self._extractor.extract(context_draws)

            # Target: which numbers appeared in this draw
            target_numbers = set(draws[i].numbers)

            for num in range(self.numbers_range[0], self.numbers_range[1] + 1):
                vec = vectors.get(num)
                if vec is None:
                    continue

                # Feature vector
                feature_values = [
                    vec.features.get(name, 0.0)
                    for name in KenoPredictor.FEATURE_NAMES
                ]
                X_list.append(feature_values)

                # Label: 1 if number appeared, 0 otherwise
                y_list.append(1 if num in target_numbers else 0)

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int32)

        return X, y

    def _walk_forward_validation(
        self,
        draws: list[DrawResult],
    ) -> list[WalkForwardResult]:
        """Fuehrt Walk-Forward Validation durch.

        Schema: Train 6 Monate -> Test 1 Monat -> Shift -> Repeat

        Args:
            draws: Liste von DrawResult-Objekten

        Returns:
            Liste von WalkForwardResult
        """
        results = []

        if not draws:
            return results

        # Sort by date
        sorted_draws = sorted(draws, key=lambda d: d.date)
        min_date = sorted_draws[0].date
        max_date = sorted_draws[-1].date

        period_idx = 0
        current_train_start = min_date

        while True:
            # Calculate period dates
            train_end = self._add_months(current_train_start, self.wf_config.train_months)
            test_start = train_end
            test_end = self._add_months(test_start, self.wf_config.test_months)

            # Check if we have enough data
            if test_end > max_date:
                break

            # Filter draws for train and test periods
            train_draws = [
                d for d in sorted_draws
                if current_train_start <= d.date < train_end
            ]
            test_draws = [
                d for d in sorted_draws
                if test_start <= d.date < test_end
            ]

            # Check minimum samples
            if len(train_draws) < self.wf_config.min_train_samples:
                logger.warning(
                    f"Period {period_idx}: Not enough training samples "
                    f"({len(train_draws)} < {self.wf_config.min_train_samples})"
                )
                current_train_start = self._add_months(
                    current_train_start, self.wf_config.step_months
                )
                continue

            if len(test_draws) < 10:
                logger.warning(
                    f"Period {period_idx}: Not enough test samples ({len(test_draws)})"
                )
                current_train_start = self._add_months(
                    current_train_start, self.wf_config.step_months
                )
                continue

            # Prepare data
            try:
                X_train, y_train = self._prepare_training_data(train_draws)
                X_test, y_test = self._prepare_training_data(test_draws)
            except ValueError as e:
                logger.warning(f"Period {period_idx}: Data preparation failed: {e}")
                current_train_start = self._add_months(
                    current_train_start, self.wf_config.step_months
                )
                continue

            # Train and evaluate
            predictor = KenoPredictor(config=self.model_config)
            predictor.train(X_train, y_train)
            metrics = predictor.evaluate(X_test, y_test)

            result = WalkForwardResult(
                period_idx=period_idx,
                train_start=current_train_start,
                train_end=train_end,
                test_start=test_start,
                test_end=test_end,
                metrics=metrics,
                n_train=len(X_train),
                n_test=len(X_test),
            )
            results.append(result)

            logger.debug(
                f"Period {period_idx}: "
                f"{current_train_start} - {test_end}, "
                f"F1={metrics.f1:.4f}"
            )

            # Move to next period
            current_train_start = self._add_months(
                current_train_start, self.wf_config.step_months
            )
            period_idx += 1

        return results

    def _add_months(self, d: date, months: int) -> date:
        """Addiert Monate zu einem Datum.

        Args:
            d: Ausgangsdatum
            months: Anzahl Monate

        Returns:
            Neues Datum
        """
        month = d.month + months
        year = d.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        # Handle day overflow
        try:
            return d.replace(year=year, month=month)
        except ValueError:
            # Day doesn't exist in target month (e.g., Feb 30)
            return d.replace(year=year, month=month, day=28)

    def save_model(self, path: Union[str, Path]) -> None:
        """Speichert das trainierte Modell.

        Args:
            path: Pfad (ohne Extension)
        """
        if self._predictor is None:
            raise RuntimeError("Kein trainiertes Modell vorhanden")

        self._predictor.save(path)

    def load_model(self, path: Union[str, Path]) -> None:
        """Laedt ein gespeichertes Modell.

        Args:
            path: Pfad (ohne Extension)
        """
        self._predictor = KenoPredictor(config=self.model_config)
        self._predictor.load(path)

    def predict(
        self,
        draws: list[DrawResult],
        top_n: int = 10,
    ) -> list[tuple[int, float]]:
        """Macht Vorhersagen basierend auf bisherigen Ziehungen.

        Args:
            draws: Bisherige Ziehungen
            top_n: Anzahl Top-Zahlen

        Returns:
            Liste von (Zahl, Wahrscheinlichkeit) Tupeln
        """
        if self._predictor is None:
            raise RuntimeError("Kein trainiertes Modell vorhanden")

        # Extract features
        vectors = self._extractor.extract(draws)

        # Prepare feature matrix
        X = []
        numbers = []
        for num in range(self.numbers_range[0], self.numbers_range[1] + 1):
            vec = vectors.get(num)
            if vec is None:
                continue

            feature_values = [
                vec.features.get(name, 0.0)
                for name in KenoPredictor.FEATURE_NAMES
            ]
            X.append(feature_values)
            numbers.append(num)

        X = np.array(X, dtype=np.float32)

        # Get predictions
        probabilities = self._predictor.predict_proba(X)

        # Sort by probability
        scored = list(zip(numbers, probabilities))
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored[:top_n]


__all__ = [
    "WalkForwardConfig",
    "WalkForwardResult",
    "TrainingReport",
    "KenoTrainer",
]
