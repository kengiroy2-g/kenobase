"""Confidence Interval Module - Bootstrap-basierte Konfidenzintervalle.

Dieses Modul implementiert statistische Konfidenzintervalle fuer Vorhersagen
basierend auf der TASK-P11 Spezifikation.

Methode: Percentile-Bootstrap (1000 Resamples)
- 95% CI fuer ensemble_score und ml_probability
- CI coverage test zur Validierung
- Stabile Vorhersagen: CI width < 0.3

Usage:
    from kenobase.prediction.confidence import ConfidenceEstimator

    estimator = ConfidenceEstimator()
    ci = estimator.calculate_ci(scores, confidence_level=0.95)
    print(f"CI: [{ci.lower:.4f}, {ci.upper:.4f}], width={ci.width:.4f}")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceInterval:
    """Konfidenzintervall fuer eine Vorhersage.

    Attributes:
        lower: Untere Grenze des Intervalls
        upper: Obere Grenze des Intervalls
        point_estimate: Punktschaetzer (Median der Bootstrap-Verteilung)
        confidence_level: Konfidenzniveau (z.B. 0.95 fuer 95% CI)
        n_bootstrap: Anzahl Bootstrap-Resamples
    """

    lower: float
    upper: float
    point_estimate: float
    confidence_level: float = 0.95
    n_bootstrap: int = 1000

    @property
    def width(self) -> float:
        """Breite des Konfidenzintervalls."""
        return self.upper - self.lower

    @property
    def is_stable(self) -> bool:
        """True wenn CI width < 0.3 (stabile Vorhersage)."""
        return self.width < 0.3

    def contains(self, value: float) -> bool:
        """Prueft ob ein Wert im Intervall liegt."""
        return self.lower <= value <= self.upper

    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary."""
        return {
            "ci_lower": round(self.lower, 4),
            "ci_upper": round(self.upper, 4),
            "ci_width": round(self.width, 4),
            "point_estimate": round(self.point_estimate, 4),
            "confidence_level": self.confidence_level,
            "is_stable": self.is_stable,
        }


class ConfidenceEstimator:
    """Bootstrap-basierter Konfidenzintervall-Schaetzer.

    Verwendet Percentile-Bootstrap zur Berechnung von Konfidenzintervallen
    fuer Vorhersage-Scores.

    Attributes:
        n_bootstrap: Anzahl Bootstrap-Resamples (default: 1000)
        random_state: Seed fuer Reproduzierbarkeit
    """

    DEFAULT_N_BOOTSTRAP = 1000
    DEFAULT_CONFIDENCE_LEVEL = 0.95

    def __init__(
        self,
        n_bootstrap: int = DEFAULT_N_BOOTSTRAP,
        random_state: Optional[int] = 42,
    ):
        """Initialisiert den ConfidenceEstimator.

        Args:
            n_bootstrap: Anzahl Bootstrap-Resamples
            random_state: Seed fuer Reproduzierbarkeit (None fuer random)
        """
        self.n_bootstrap = n_bootstrap
        self.random_state = random_state
        self._rng = np.random.default_rng(random_state)

    def calculate_ci(
        self,
        scores: np.ndarray,
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
        statistic: str = "mean",
    ) -> ConfidenceInterval:
        """Berechnet Konfidenzintervall via Percentile-Bootstrap.

        Args:
            scores: Array von Scores (z.B. aus mehreren Walk-Forward Perioden)
            confidence_level: Konfidenzniveau (0.0-1.0)
            statistic: Statistik fuer Aggregation ("mean" oder "median")

        Returns:
            ConfidenceInterval mit lower, upper, width

        Raises:
            ValueError: Wenn scores leer oder confidence_level ungueltig
        """
        scores = np.asarray(scores).flatten()

        if len(scores) == 0:
            raise ValueError("scores darf nicht leer sein")
        if not 0.0 < confidence_level < 1.0:
            raise ValueError(f"confidence_level muss zwischen 0 und 1 liegen: {confidence_level}")

        # Aggregation function
        if statistic == "mean":
            agg_func = np.mean
        elif statistic == "median":
            agg_func = np.median
        else:
            raise ValueError(f"Unbekannte Statistik: {statistic}")

        # Bootstrap resampling
        bootstrap_stats = np.zeros(self.n_bootstrap)
        n = len(scores)

        for i in range(self.n_bootstrap):
            # Resample with replacement
            resample_idx = self._rng.integers(0, n, size=n)
            bootstrap_sample = scores[resample_idx]
            bootstrap_stats[i] = agg_func(bootstrap_sample)

        # Percentile method
        alpha = 1 - confidence_level
        lower_percentile = alpha / 2 * 100
        upper_percentile = (1 - alpha / 2) * 100

        ci_lower = float(np.percentile(bootstrap_stats, lower_percentile))
        ci_upper = float(np.percentile(bootstrap_stats, upper_percentile))
        point_estimate = float(np.median(bootstrap_stats))

        return ConfidenceInterval(
            lower=ci_lower,
            upper=ci_upper,
            point_estimate=point_estimate,
            confidence_level=confidence_level,
            n_bootstrap=self.n_bootstrap,
        )

    def calculate_ci_for_predictions(
        self,
        ensemble_scores: list[float],
        ml_probabilities: list[float],
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    ) -> dict[str, ConfidenceInterval]:
        """Berechnet CIs fuer Ensemble und ML Scores.

        Args:
            ensemble_scores: Liste von ensemble_score Werten
            ml_probabilities: Liste von ml_probability Werten
            confidence_level: Konfidenzniveau

        Returns:
            Dict mit "ensemble" und "ml" ConfidenceIntervals
        """
        result = {}

        if ensemble_scores:
            result["ensemble"] = self.calculate_ci(
                np.array(ensemble_scores),
                confidence_level=confidence_level,
            )
        else:
            # Return degenerate CI for empty input
            result["ensemble"] = ConfidenceInterval(
                lower=0.5, upper=0.5, point_estimate=0.5,
                confidence_level=confidence_level, n_bootstrap=0,
            )

        if ml_probabilities:
            result["ml"] = self.calculate_ci(
                np.array(ml_probabilities),
                confidence_level=confidence_level,
            )
        else:
            result["ml"] = ConfidenceInterval(
                lower=0.5, upper=0.5, point_estimate=0.5,
                confidence_level=confidence_level, n_bootstrap=0,
            )

        return result

    def coverage_test(
        self,
        true_values: np.ndarray,
        ci_list: list[ConfidenceInterval],
    ) -> float:
        """Testet die Coverage eines CI-Schemas.

        Berechnet den Anteil der wahren Werte, die in ihren
        entsprechenden Konfidenzintervallen liegen.

        Args:
            true_values: Array der wahren Werte
            ci_list: Liste der entsprechenden ConfidenceIntervals

        Returns:
            Coverage-Rate (0.0-1.0)

        Raises:
            ValueError: Wenn Laengen nicht uebereinstimmen
        """
        true_values = np.asarray(true_values).flatten()

        if len(true_values) != len(ci_list):
            raise ValueError(
                f"Laengen stimmen nicht ueberein: "
                f"{len(true_values)} vs {len(ci_list)}"
            )

        if len(true_values) == 0:
            return 1.0  # Trivial case

        covered = sum(
            ci.contains(value)
            for value, ci in zip(true_values, ci_list)
        )

        return covered / len(true_values)


@dataclass
class PredictionWithCI:
    """Vorhersage mit Konfidenzintervallen.

    Erweitert eine Basis-Vorhersage um statistische Konfidenzintervalle.

    Attributes:
        number: Die Zahl (1-70 fuer KENO)
        ensemble_score: Kombinierter Score (0-1)
        ensemble_ci: Konfidenzintervall fuer ensemble_score
        ml_probability: ML-Wahrscheinlichkeit (0-1)
        ml_ci: Konfidenzintervall fuer ml_probability
        tier: Tier-Klassifikation (A/B/C)
    """

    number: int
    ensemble_score: float
    ensemble_ci: ConfidenceInterval
    ml_probability: float
    ml_ci: ConfidenceInterval
    tier: str = "C"

    @property
    def is_stable(self) -> bool:
        """True wenn beide CIs stabil sind (width < 0.3)."""
        return self.ensemble_ci.is_stable and self.ml_ci.is_stable

    @property
    def combined_width(self) -> float:
        """Durchschnittliche CI-Breite."""
        return (self.ensemble_ci.width + self.ml_ci.width) / 2

    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary."""
        return {
            "number": self.number,
            "ensemble_score": round(self.ensemble_score, 4),
            "ensemble_ci": self.ensemble_ci.to_dict(),
            "ml_probability": round(self.ml_probability, 4),
            "ml_ci": self.ml_ci.to_dict(),
            "tier": self.tier,
            "is_stable": self.is_stable,
            "combined_ci_width": round(self.combined_width, 4),
        }


__all__ = [
    "ConfidenceInterval",
    "ConfidenceEstimator",
    "PredictionWithCI",
]
