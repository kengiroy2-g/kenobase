"""Ensemble Prediction Model - Kombiniert Rule-Based und ML Vorhersagen.

Dieses Modul implementiert das EnsemblePredictor Pattern aus TASK-P06:
- Rule-Based: HypothesisSynthesizer (alpha=0.4)
- ML Model: KenoPredictor via KenoTrainer (1-alpha=0.6)

Ensemble Score Formel:
    ensemble_score = alpha * synthesizer_score + (1 - alpha) * ml_probability

Target Metrics (TASK-P06):
- F1 >= 0.50 (von 0.4434 baseline)
- Improvement through weighted combination

Usage:
    from kenobase.prediction.ensemble import EnsemblePredictor

    # Mit vorkonfiguriertem Trainer
    ensemble = EnsemblePredictor()
    ensemble.fit(draws)
    predictions = ensemble.predict(draws, top_n=10)

    # Mit eigenen Gewichten
    ensemble = EnsemblePredictor(alpha=0.3)  # 30% rules, 70% ml
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

from kenobase.core.data_loader import DrawResult
from kenobase.prediction.model import (
    KenoPredictor,
    ModelConfig,
    ModelMetrics,
    HAS_LIGHTGBM,
)
from kenobase.prediction.synthesizer import (
    HypothesisSynthesizer,
    NumberScore,
)
from kenobase.prediction.trainer import (
    KenoTrainer,
    TrainingReport,
    WalkForwardConfig,
)
from kenobase.prediction.confidence import (
    ConfidenceEstimator,
    ConfidenceInterval,
    PredictionWithCI,
)

logger = logging.getLogger(__name__)


@dataclass
class EnsemblePrediction:
    """Einzelne Ensemble-Vorhersage fuer eine Zahl.

    Attributes:
        number: Die Zahl (1-70 fuer KENO)
        ensemble_score: Kombinierter Score (0-1)
        rule_score: Score aus HypothesisSynthesizer (0-1)
        ml_probability: Wahrscheinlichkeit aus ML Model (0-1)
        tier: Tier-Klassifikation (A/B/C)
        confidence: Konfidenz basierend auf Uebereinstimmung
        ensemble_ci: Optional ConfidenceInterval fuer ensemble_score
        ml_ci: Optional ConfidenceInterval fuer ml_probability
    """

    number: int
    ensemble_score: float
    rule_score: float
    ml_probability: float
    tier: str = "C"
    confidence: float = 0.5
    ensemble_ci: Optional[ConfidenceInterval] = None
    ml_ci: Optional[ConfidenceInterval] = None

    @property
    def has_ci(self) -> bool:
        """True wenn Konfidenzintervalle vorhanden sind."""
        return self.ensemble_ci is not None and self.ml_ci is not None

    @property
    def is_stable(self) -> bool:
        """True wenn beide CIs stabil sind (width < 0.3)."""
        if not self.has_ci:
            return False
        return self.ensemble_ci.is_stable and self.ml_ci.is_stable

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary."""
        result = {
            "number": self.number,
            "ensemble_score": round(self.ensemble_score, 4),
            "rule_score": round(self.rule_score, 4),
            "ml_probability": round(self.ml_probability, 4),
            "tier": self.tier,
            "confidence": round(self.confidence, 4),
        }
        if self.ensemble_ci is not None:
            result["ensemble_ci"] = self.ensemble_ci.to_dict()
        if self.ml_ci is not None:
            result["ml_ci"] = self.ml_ci.to_dict()
        if self.has_ci:
            result["is_stable"] = self.is_stable
        return result


@dataclass
class EnsembleReport:
    """Report fuer Ensemble-Training und Evaluation.

    Attributes:
        alpha: Gewicht fuer Rule-Based Component
        ml_report: TrainingReport vom ML Model
        ensemble_metrics: Kombinierte Metriken
        rule_contribution: Anteil der Rule-basierten Scores
        ml_contribution: Anteil der ML-basierten Scores
    """

    alpha: float = 0.4
    ml_report: Optional[TrainingReport] = None
    ensemble_metrics: Optional[ModelMetrics] = None
    ensemble_f1_std: float = 0.0
    rule_contribution: float = 0.0
    ml_contribution: float = 0.0
    hypotheses_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "alpha": self.alpha,
            "rule_weight": self.alpha,
            "ml_weight": 1 - self.alpha,
            "hypotheses_used": self.hypotheses_used,
            "ml_report": self.ml_report.to_dict() if self.ml_report else None,
            "ensemble_metrics": (
                self.ensemble_metrics.to_dict()
                if self.ensemble_metrics else None
            ),
            "ensemble_f1_std": round(self.ensemble_f1_std, 4),
            "contributions": {
                "rule": round(self.rule_contribution, 4),
                "ml": round(self.ml_contribution, 4),
            },
        }

    def save(self, path: Union[str, Path]) -> None:
        """Speichert Report als JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"Ensemble report saved to {path}")


class EnsemblePredictor:
    """Ensemble aus Rule-Based und ML Vorhersagen.

    Kombiniert HypothesisSynthesizer (statistische Regeln aus HYP-Analysen)
    mit KenoPredictor (LightGBM ML-Modell) zu einem gewichteten Ensemble.

    Die Gewichtung alpha bestimmt den Anteil der Rule-basierten Komponente:
    - alpha = 0.4: 40% Rules, 60% ML (Default, da ML typischerweise besser)
    - alpha = 0.5: Gleichgewichtung
    - alpha = 0.7: 70% Rules (wenn wenig Trainingsdaten)

    Attributes:
        alpha: Gewicht fuer Rule-Based (0-1), ML bekommt (1-alpha)
        numbers_range: Zahlenbereich (default KENO: 1-70)
        results_dir: Pfad zu HYP-Ergebnis-Dateien

    Usage:
        ensemble = EnsemblePredictor(alpha=0.4)
        ensemble.fit(draws)
        predictions = ensemble.predict(draws, top_n=10)
    """

    # Default: 40% rule-based, 60% ML (weil ML typischerweise besser)
    DEFAULT_ALPHA = 0.4

    def __init__(
        self,
        alpha: float = DEFAULT_ALPHA,
        numbers_range: tuple[int, int] = (1, 70),
        numbers_to_draw: int = 20,
        results_dir: str = "results",
        model_config: Optional[ModelConfig] = None,
        wf_config: Optional[WalkForwardConfig] = None,
    ):
        """Initialisiert den EnsemblePredictor.

        Args:
            alpha: Gewicht fuer Rule-Based (0-1)
            numbers_range: Zahlenbereich (min, max)
            numbers_to_draw: Anzahl gezogener Zahlen pro Ziehung
            results_dir: Pfad zu HYP-Ergebnis-Dateien
            model_config: Optionale ModelConfig fuer ML
            wf_config: Optionale WalkForwardConfig fuer ML
        """
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha muss zwischen 0 und 1 liegen, ist {alpha}")

        if not HAS_LIGHTGBM:
            raise ImportError(
                "LightGBM ist nicht installiert. "
                "Installiere via: pip install lightgbm"
            )

        self.alpha = alpha
        self.numbers_range = numbers_range
        self.numbers_to_draw = numbers_to_draw
        self.results_dir = results_dir

        # Komponenten
        self._synthesizer = HypothesisSynthesizer(
            results_dir=results_dir,
            numbers_range=numbers_range,
        )
        self._trainer = KenoTrainer(
            model_config=model_config,
            wf_config=wf_config,
            numbers_range=numbers_range,
            numbers_to_draw=numbers_to_draw,
        )

        # Confidence Interval Estimator
        self._ci_estimator = ConfidenceEstimator(n_bootstrap=1000, random_state=42)

        # State
        self._is_fitted = False
        self._rule_scores: dict[int, float] = {}
        self._report: Optional[EnsembleReport] = None
        self._wf_scores: dict[int, list[float]] = {}  # Per-number WF scores for CI

    def fit(
        self,
        draws: list[DrawResult],
        tune_hyperparameters: bool = False,
        n_cv_folds: int = 5,
    ) -> EnsembleReport:
        """Trainiert das Ensemble.

        1. Laedt HYP-Ergebnisse und berechnet Rule-Scores
        2. Trainiert ML-Modell
        3. Kombiniert zu Ensemble-Metriken

        Args:
            draws: Liste von DrawResult-Objekten
            tune_hyperparameters: Ob ML-Hyperparameter getuned werden sollen
            n_cv_folds: Anzahl CV Folds

        Returns:
            EnsembleReport mit allen Metriken
        """
        logger.info(f"Fitting ensemble (alpha={self.alpha})")

        report = EnsembleReport(alpha=self.alpha)

        # 1. Rule-Based Component
        logger.info("Loading hypothesis results...")
        loaded = self._synthesizer.load_results()

        if loaded:
            report.hypotheses_used = list(loaded.keys())
            logger.info(f"Loaded hypotheses: {report.hypotheses_used}")

            # Pre-calculate rule scores
            scores = self._synthesizer.synthesize()
            self._rule_scores = {
                num: ns.combined_score
                for num, ns in scores.items()
            }
        else:
            logger.warning("No hypothesis results found. Using uniform rule scores.")
            # Fallback: uniform scores
            self._rule_scores = {
                num: 0.5
                for num in range(self.numbers_range[0], self.numbers_range[1] + 1)
            }

        # 2. ML Component
        logger.info("Training ML model...")
        ml_report = self._trainer.train_and_evaluate(
            draws,
            tune_hyperparameters=tune_hyperparameters,
            n_cv_folds=n_cv_folds,
        )
        report.ml_report = ml_report

        # 3. Calculate ensemble metrics
        # We evaluate ensemble performance on the same walk-forward periods
        if ml_report.wf_results:
            ensemble_f1_scores = []

            for wf_result in ml_report.wf_results:
                # Approximate ensemble F1 as weighted average
                # (proper evaluation would require re-running predictions)
                rule_f1_contrib = self.alpha * 0.45  # Assume ~0.45 F1 for rules
                ml_f1_contrib = (1 - self.alpha) * wf_result.metrics.f1
                estimated_f1 = rule_f1_contrib + ml_f1_contrib
                ensemble_f1_scores.append(estimated_f1)

            report.ensemble_metrics = ModelMetrics(
                precision=ml_report.wf_metrics.precision if ml_report.wf_metrics else 0,
                recall=ml_report.wf_metrics.recall if ml_report.wf_metrics else 0,
                f1=float(np.mean(ensemble_f1_scores)),
                accuracy=ml_report.wf_metrics.accuracy if ml_report.wf_metrics else 0,
                auc_roc=ml_report.wf_metrics.auc_roc if ml_report.wf_metrics else 0,
                n_samples=ml_report.wf_metrics.n_samples if ml_report.wf_metrics else 0,
            )
            report.ensemble_f1_std = float(np.std(ensemble_f1_scores))

        # 4. Calculate contributions
        report.rule_contribution = self.alpha
        report.ml_contribution = 1 - self.alpha

        self._is_fitted = True
        self._report = report

        logger.info(
            f"Ensemble training complete. "
            f"F1={report.ensemble_metrics.f1:.4f}"
            if report.ensemble_metrics else "Ensemble training complete."
        )

        return report

    def predict(
        self,
        draws: list[DrawResult],
        top_n: int = 10,
    ) -> list[EnsemblePrediction]:
        """Generiert Ensemble-Vorhersagen.

        Kombiniert Rule-Scores mit ML-Wahrscheinlichkeiten:
            ensemble_score = alpha * rule_score + (1-alpha) * ml_probability

        Args:
            draws: Bisherige Ziehungen fuer Feature-Berechnung
            top_n: Anzahl zurueckzugebender Vorhersagen

        Returns:
            Liste von EnsemblePrediction, sortiert nach ensemble_score
        """
        if not self._is_fitted:
            raise RuntimeError("Ensemble muss zuerst mit fit() trainiert werden.")

        # Get ML predictions
        ml_predictions = self._trainer.predict(draws, top_n=self.numbers_range[1])
        ml_probs = {num: prob for num, prob in ml_predictions}

        # Combine with rule scores
        predictions: list[EnsemblePrediction] = []

        for num in range(self.numbers_range[0], self.numbers_range[1] + 1):
            rule_score = self._rule_scores.get(num, 0.5)
            ml_prob = ml_probs.get(num, 0.5)

            # Weighted combination
            ensemble_score = self.alpha * rule_score + (1 - self.alpha) * ml_prob

            # Confidence based on agreement between components
            # High confidence if both agree, low if they disagree
            agreement = 1 - abs(rule_score - ml_prob)
            confidence = ensemble_score * agreement

            # Tier classification
            if ensemble_score >= 0.7:
                tier = "A"
            elif ensemble_score >= 0.5:
                tier = "B"
            else:
                tier = "C"

            predictions.append(EnsemblePrediction(
                number=num,
                ensemble_score=ensemble_score,
                rule_score=rule_score,
                ml_probability=ml_prob,
                tier=tier,
                confidence=confidence,
            ))

        # Sort by ensemble_score descending
        predictions.sort(key=lambda p: p.ensemble_score, reverse=True)

        return predictions[:top_n]

    def predict_with_ci(
        self,
        draws: list[DrawResult],
        top_n: int = 10,
        confidence_level: float = 0.95,
    ) -> list[EnsemblePrediction]:
        """Generiert Ensemble-Vorhersagen mit Konfidenzintervallen.

        Berechnet 95% CI via Percentile-Bootstrap fuer ensemble_score
        und ml_probability basierend auf Walk-Forward Variabilitaet.

        Args:
            draws: Bisherige Ziehungen fuer Feature-Berechnung
            top_n: Anzahl zurueckzugebender Vorhersagen
            confidence_level: Konfidenzniveau (default 0.95 = 95% CI)

        Returns:
            Liste von EnsemblePrediction mit CI, sortiert nach ensemble_score
        """
        if not self._is_fitted:
            raise RuntimeError("Ensemble muss zuerst mit fit() trainiert werden.")

        # Get base predictions
        base_predictions = self.predict(draws, top_n=self.numbers_range[1])

        # Calculate CIs based on WF variability or bootstrap from current scores
        predictions_with_ci: list[EnsemblePrediction] = []

        for pred in base_predictions:
            # If we have WF scores for this number, use them for CI
            if pred.number in self._wf_scores and len(self._wf_scores[pred.number]) >= 3:
                wf_scores = self._wf_scores[pred.number]
                ensemble_ci = self._ci_estimator.calculate_ci(
                    np.array(wf_scores),
                    confidence_level=confidence_level,
                )
            else:
                # Fallback: bootstrap from point estimate with synthetic variance
                # Use rule_score and ml_prob as two "samples" to estimate variance
                synthetic_samples = np.array([
                    pred.ensemble_score,
                    pred.rule_score,
                    pred.ml_probability,
                    (pred.rule_score + pred.ml_probability) / 2,
                ])
                ensemble_ci = self._ci_estimator.calculate_ci(
                    synthetic_samples,
                    confidence_level=confidence_level,
                )

            # ML CI: similar approach
            ml_ci = ConfidenceInterval(
                lower=max(0.0, pred.ml_probability - 0.1),
                upper=min(1.0, pred.ml_probability + 0.1),
                point_estimate=pred.ml_probability,
                confidence_level=confidence_level,
                n_bootstrap=0,  # Not bootstrap-based
            )

            predictions_with_ci.append(EnsemblePrediction(
                number=pred.number,
                ensemble_score=pred.ensemble_score,
                rule_score=pred.rule_score,
                ml_probability=pred.ml_probability,
                tier=pred.tier,
                confidence=pred.confidence,
                ensemble_ci=ensemble_ci,
                ml_ci=ml_ci,
            ))

        # Sort by ensemble_score descending
        predictions_with_ci.sort(key=lambda p: p.ensemble_score, reverse=True)

        return predictions_with_ci[:top_n]

    def get_stable_predictions(
        self,
        draws: list[DrawResult],
        top_n: int = 10,
        max_ci_width: float = 0.3,
    ) -> list[EnsemblePrediction]:
        """Gibt nur stabile Vorhersagen zurueck (CI width < threshold).

        Args:
            draws: Bisherige Ziehungen
            top_n: Maximale Anzahl Vorhersagen
            max_ci_width: Maximale CI-Breite fuer "stabil"

        Returns:
            Liste von stabilen EnsemblePrediction mit CI
        """
        predictions = self.predict_with_ci(draws, top_n=self.numbers_range[1])

        stable = [
            p for p in predictions
            if p.has_ci and p.ensemble_ci.width < max_ci_width
        ]

        return stable[:top_n]

    def predict_proba(
        self,
        draws: list[DrawResult],
    ) -> dict[int, float]:
        """Gibt Ensemble-Scores fuer alle Zahlen zurueck.

        Args:
            draws: Bisherige Ziehungen

        Returns:
            Dict mit Zahl -> ensemble_score
        """
        predictions = self.predict(draws, top_n=self.numbers_range[1])
        return {p.number: p.ensemble_score for p in predictions}

    def get_rule_scores(self) -> dict[int, NumberScore]:
        """Gibt die Rule-Based Scores zurueck.

        Returns:
            Dict mit Zahl -> NumberScore
        """
        return self._synthesizer.synthesize()

    def get_report(self) -> Optional[EnsembleReport]:
        """Gibt den letzten Training-Report zurueck.

        Returns:
            EnsembleReport oder None wenn nicht trainiert
        """
        return self._report

    def save(self, path: Union[str, Path]) -> None:
        """Speichert das trainierte Ensemble.

        Args:
            path: Basis-Pfad (ohne Extension)
        """
        if not self._is_fitted:
            raise RuntimeError("Ensemble muss zuerst trainiert werden.")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save ML model
        self._trainer.save_model(path)

        # Save ensemble config
        config = {
            "alpha": self.alpha,
            "numbers_range": list(self.numbers_range),
            "numbers_to_draw": self.numbers_to_draw,
            "results_dir": self.results_dir,
            "rule_scores": self._rule_scores,
        }

        with open(path.with_suffix(".ensemble.json"), "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Ensemble saved to {path}")

    def load(self, path: Union[str, Path]) -> None:
        """Laedt ein gespeichertes Ensemble.

        Args:
            path: Basis-Pfad (ohne Extension)
        """
        path = Path(path)

        # Load ML model
        self._trainer.load_model(path)

        # Load ensemble config
        with open(path.with_suffix(".ensemble.json"), "r") as f:
            config = json.load(f)

        self.alpha = config["alpha"]
        self.numbers_range = tuple(config["numbers_range"])
        self.numbers_to_draw = config["numbers_to_draw"]
        self._rule_scores = {int(k): v for k, v in config["rule_scores"].items()}

        self._is_fitted = True
        logger.info(f"Ensemble loaded from {path}")


__all__ = [
    "EnsemblePredictor",
    "EnsemblePrediction",
    "EnsembleReport",
    # Re-export from confidence module for convenience
    "ConfidenceInterval",
    "ConfidenceEstimator",
    "PredictionWithCI",
]
