"""State-Aware Predictor - Combines EconomicState with EnsemblePredictor.

This module implements TASK_004: StateAwarePredictor wrapper that provides
state-conditional predictions based on economic state (A7 axiom).

Key Features:
- State-tagged predictions with economic state labels
- State-based alpha weighting (different weights per economic state)
- Bet recommendations based on economic state
- F1 metric per state for granular evaluation

Integration:
- Uses EconomicState from kenobase.core.economic_state (4 states)
- Wraps EnsemblePredictor from kenobase.prediction.ensemble
- Acceptance: State-aware F1 >= EnsemblePredictor baseline F1

Usage:
    from kenobase.prediction.state_aware import StateAwarePredictor

    predictor = StateAwarePredictor()
    predictor.fit(draws)
    predictions = predictor.predict(draws)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

from kenobase.core.data_loader import DrawResult
from kenobase.core.economic_state import (
    EconomicState,
    extract_economic_states,
    get_bet_recommendation,
    compute_state_distribution,
)
from kenobase.prediction.ensemble import (
    EnsemblePredictor,
    EnsemblePrediction,
    EnsembleReport,
)
from kenobase.prediction.model import ModelConfig, ModelMetrics

logger = logging.getLogger(__name__)


# State-specific alpha weights (Axiom A7: Reset-Zyklen)
# COOLDOWN: More conservative, rely more on rules (higher alpha)
# HOT: More aggressive, rely more on ML (lower alpha)
DEFAULT_STATE_ALPHAS = {
    "NORMAL": 0.4,      # Default EnsemblePredictor alpha
    "COOLDOWN": 0.6,    # More rules-based (conservative after jackpot)
    "RECOVERY": 0.5,    # Balanced during transition
    "HOT": 0.3,         # More ML-based (high activity)
}


@dataclass
class StateAwarePrediction:
    """Prediction with economic state context.

    Attributes:
        number: The number (1-70 for KENO)
        ensemble_score: Combined score (0-1)
        rule_score: Score from HypothesisSynthesizer (0-1)
        ml_probability: Probability from ML Model (0-1)
        tier: Tier classification (A/B/C)
        confidence: Confidence based on agreement
        state_label: Economic state at prediction time
        state_alpha: Alpha weight used for this state
        bet_recommendation: Bet recommendation based on state
    """

    number: int
    ensemble_score: float
    rule_score: float
    ml_probability: float
    tier: str = "C"
    confidence: float = 0.5
    state_label: str = "NORMAL"
    state_alpha: float = 0.4
    bet_recommendation: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "number": self.number,
            "ensemble_score": round(self.ensemble_score, 4),
            "rule_score": round(self.rule_score, 4),
            "ml_probability": round(self.ml_probability, 4),
            "tier": self.tier,
            "confidence": round(self.confidence, 4),
            "state_label": self.state_label,
            "state_alpha": round(self.state_alpha, 4),
            "bet_recommendation": self.bet_recommendation,
        }


@dataclass
class StateAwareReport:
    """Report for StateAwarePredictor training and evaluation.

    Attributes:
        base_report: EnsembleReport from base predictor
        state_metrics: F1 and metrics per economic state
        state_distribution: Distribution of states in training data
        state_alphas: Alpha weights per state
        overall_f1: Overall F1 across all states
    """

    base_report: Optional[EnsembleReport] = None
    state_metrics: dict[str, dict[str, float]] = field(default_factory=dict)
    state_distribution: dict[str, Any] = field(default_factory=dict)
    state_alphas: dict[str, float] = field(default_factory=dict)
    overall_f1: float = 0.0
    baseline_f1: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "base_report": self.base_report.to_dict() if self.base_report else None,
            "state_metrics": self.state_metrics,
            "state_distribution": self.state_distribution,
            "state_alphas": self.state_alphas,
            "overall_f1": round(self.overall_f1, 4),
            "baseline_f1": round(self.baseline_f1, 4),
            "f1_improvement": round(self.overall_f1 - self.baseline_f1, 4),
        }

    def save(self, path: Union[str, Path]) -> None:
        """Save report as JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"StateAwareReport saved to {path}")


class StateAwarePredictor:
    """Predictor that combines EconomicState with EnsemblePredictor.

    Uses economic state (NORMAL/COOLDOWN/RECOVERY/HOT) to adjust
    prediction weights according to Axiom A7 (Reset-Zyklen).

    Key insight: After a jackpot (COOLDOWN), the system needs to recover,
    so we rely more on rule-based predictions. During high activity (HOT),
    we can rely more on ML predictions.

    Attributes:
        state_alphas: Dict mapping state label to alpha weight
        numbers_range: Range of numbers (default KENO: 1-70)
        cv_window: Window size for rolling CV computation

    Usage:
        predictor = StateAwarePredictor()
        predictor.fit(draws)
        predictions = predictor.predict(draws)
    """

    def __init__(
        self,
        state_alphas: Optional[dict[str, float]] = None,
        numbers_range: tuple[int, int] = (1, 70),
        numbers_to_draw: int = 20,
        results_dir: str = "results",
        model_config: Optional[ModelConfig] = None,
        cv_window: int = 30,
        jackpot_high_threshold: float = 10_000_000.0,
        cv_high_threshold: float = 0.5,
    ):
        """Initialize the StateAwarePredictor.

        Args:
            state_alphas: Optional dict of state -> alpha weights
            numbers_range: Range of numbers (min, max)
            numbers_to_draw: Number of numbers drawn per draw
            results_dir: Path to HYP result files
            model_config: Optional ModelConfig for ML
            cv_window: Window for rolling CV computation
            jackpot_high_threshold: Threshold for "high" jackpot
            cv_high_threshold: Threshold for "high" CV
        """
        self.state_alphas = state_alphas or DEFAULT_STATE_ALPHAS.copy()
        self.numbers_range = numbers_range
        self.numbers_to_draw = numbers_to_draw
        self.results_dir = results_dir
        self.cv_window = cv_window
        self.jackpot_high_threshold = jackpot_high_threshold
        self.cv_high_threshold = cv_high_threshold

        # Validate state_alphas
        for state in ["NORMAL", "COOLDOWN", "RECOVERY", "HOT"]:
            if state not in self.state_alphas:
                self.state_alphas[state] = DEFAULT_STATE_ALPHAS[state]

        # Base ensemble predictor (will be fitted multiple times or once)
        self._base_predictor = EnsemblePredictor(
            alpha=self.state_alphas["NORMAL"],
            numbers_range=numbers_range,
            numbers_to_draw=numbers_to_draw,
            results_dir=results_dir,
            model_config=model_config,
        )

        # State
        self._is_fitted = False
        self._report: Optional[StateAwareReport] = None
        self._economic_states: list[EconomicState] = []
        self._draws: list[DrawResult] = []

    def fit(
        self,
        draws: list[DrawResult],
        tune_hyperparameters: bool = False,
        n_cv_folds: int = 5,
    ) -> StateAwareReport:
        """Train the StateAwarePredictor.

        1. Extract economic states from draws
        2. Train base EnsemblePredictor
        3. Compute per-state metrics

        Args:
            draws: List of DrawResult objects
            tune_hyperparameters: Whether to tune ML hyperparameters
            n_cv_folds: Number of CV folds

        Returns:
            StateAwareReport with all metrics
        """
        logger.info("Fitting StateAwarePredictor...")

        # Store draws for prediction
        self._draws = sorted(draws, key=lambda d: d.date)

        # 1. Extract economic states
        logger.info("Extracting economic states...")
        self._economic_states = extract_economic_states(
            draws=self._draws,
            window=self.cv_window,
            numbers_range=self.numbers_range,
            jackpot_high_threshold=self.jackpot_high_threshold,
            cv_high_threshold=self.cv_high_threshold,
        )

        # 2. Train base predictor
        logger.info("Training base EnsemblePredictor...")
        base_report = self._base_predictor.fit(
            draws,
            tune_hyperparameters=tune_hyperparameters,
            n_cv_folds=n_cv_folds,
        )

        # 3. Compute per-state metrics
        logger.info("Computing per-state metrics...")
        state_metrics = self._compute_state_metrics(draws)

        # 4. Build report
        state_distribution = compute_state_distribution(self._economic_states)

        # Calculate overall F1 as weighted average by state counts
        overall_f1 = 0.0
        total_samples = 0
        for state_label, metrics in state_metrics.items():
            count = state_distribution["counts"].get(state_label, 0)
            overall_f1 += metrics.get("f1", 0.0) * count
            total_samples += count

        if total_samples > 0:
            overall_f1 /= total_samples

        # Baseline F1 from base predictor
        baseline_f1 = (
            base_report.ensemble_metrics.f1
            if base_report.ensemble_metrics
            else 0.0
        )

        report = StateAwareReport(
            base_report=base_report,
            state_metrics=state_metrics,
            state_distribution=state_distribution,
            state_alphas=self.state_alphas,
            overall_f1=overall_f1,
            baseline_f1=baseline_f1,
        )

        self._is_fitted = True
        self._report = report

        logger.info(
            f"StateAwarePredictor training complete. "
            f"Overall F1={overall_f1:.4f}, Baseline F1={baseline_f1:.4f}"
        )

        return report

    def _compute_state_metrics(
        self,
        draws: list[DrawResult],
    ) -> dict[str, dict[str, float]]:
        """Compute metrics per economic state.

        For each state, we evaluate predictions made with that state's alpha.

        Args:
            draws: List of DrawResult objects

        Returns:
            Dict mapping state_label to metrics dict
        """
        # Group draws by state
        state_draws: dict[str, list[tuple[DrawResult, EconomicState]]] = {
            "NORMAL": [],
            "COOLDOWN": [],
            "RECOVERY": [],
            "HOT": [],
        }

        for draw, state in zip(self._draws, self._economic_states):
            if state.state_label in state_draws:
                state_draws[state.state_label].append((draw, state))

        # Compute metrics per state
        state_metrics: dict[str, dict[str, float]] = {}

        for state_label, items in state_draws.items():
            if len(items) < 10:  # Need minimum samples
                state_metrics[state_label] = {
                    "f1": 0.0,
                    "n_samples": len(items),
                    "note": "insufficient_samples",
                }
                continue

            # Get predictions using state-specific alpha
            alpha = self.state_alphas[state_label]

            # Calculate metrics based on hit rate
            hits = 0
            total_predictions = 0

            for draw, _ in items:
                # Get top predictions
                predictions = self._predict_with_alpha(
                    [d for d, _ in items],
                    alpha,
                    top_n=self.numbers_to_draw,
                )

                predicted_numbers = {p.number for p in predictions}
                actual_numbers = set(draw.numbers)

                # Count hits
                hits += len(predicted_numbers & actual_numbers)
                total_predictions += len(predicted_numbers)

            # Calculate precision as proxy for F1
            precision = hits / total_predictions if total_predictions > 0 else 0.0
            recall = hits / (len(items) * self.numbers_to_draw) if items else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )

            state_metrics[state_label] = {
                "f1": f1,
                "precision": precision,
                "recall": recall,
                "n_samples": len(items),
                "alpha": alpha,
            }

        return state_metrics

    def _predict_with_alpha(
        self,
        draws: list[DrawResult],
        alpha: float,
        top_n: int = 10,
    ) -> list[EnsemblePrediction]:
        """Make predictions with a specific alpha weight.

        Args:
            draws: Draws for feature computation
            alpha: Alpha weight to use
            top_n: Number of predictions to return

        Returns:
            List of EnsemblePrediction
        """
        # Temporarily override alpha
        old_alpha = self._base_predictor.alpha
        self._base_predictor.alpha = alpha

        predictions = self._base_predictor.predict(draws, top_n=top_n)

        # Restore alpha
        self._base_predictor.alpha = old_alpha

        return predictions

    def predict(
        self,
        draws: list[DrawResult],
        top_n: int = 10,
        current_state: Optional[EconomicState] = None,
    ) -> list[StateAwarePrediction]:
        """Generate state-aware predictions.

        Uses the current economic state to select appropriate alpha weight.

        Args:
            draws: Previous draws for feature computation
            top_n: Number of predictions to return
            current_state: Optional current economic state (auto-detected if None)

        Returns:
            List of StateAwarePrediction, sorted by ensemble_score
        """
        if not self._is_fitted:
            raise RuntimeError("Predictor must be fitted first with fit()")

        # Determine current state
        if current_state is None:
            if self._economic_states:
                current_state = self._economic_states[-1]
            else:
                # Extract state from latest draws
                states = extract_economic_states(
                    draws=sorted(draws, key=lambda d: d.date)[-self.cv_window:],
                    window=self.cv_window,
                    numbers_range=self.numbers_range,
                    jackpot_high_threshold=self.jackpot_high_threshold,
                    cv_high_threshold=self.cv_high_threshold,
                )
                current_state = states[-1] if states else EconomicState(
                    date=datetime.now(),
                    spieleinsatz=None,
                    jackpot=None,
                    rolling_cv=None,
                    state_label="NORMAL",
                )

        # Get state-specific alpha
        state_label = current_state.state_label
        alpha = self.state_alphas.get(state_label, DEFAULT_STATE_ALPHAS["NORMAL"])

        # Get base predictions with state-specific alpha
        base_predictions = self._predict_with_alpha(draws, alpha, top_n=top_n)

        # Get bet recommendation
        bet_rec = get_bet_recommendation(current_state)

        # Convert to StateAwarePrediction
        predictions: list[StateAwarePrediction] = []

        for pred in base_predictions:
            predictions.append(StateAwarePrediction(
                number=pred.number,
                ensemble_score=pred.ensemble_score,
                rule_score=pred.rule_score,
                ml_probability=pred.ml_probability,
                tier=pred.tier,
                confidence=pred.confidence,
                state_label=state_label,
                state_alpha=alpha,
                bet_recommendation=bet_rec,
            ))

        return predictions

    def predict_proba(
        self,
        draws: list[DrawResult],
        current_state: Optional[EconomicState] = None,
    ) -> dict[int, float]:
        """Return ensemble scores for all numbers.

        Args:
            draws: Previous draws
            current_state: Optional current economic state

        Returns:
            Dict with number -> ensemble_score
        """
        predictions = self.predict(
            draws,
            top_n=self.numbers_range[1] - self.numbers_range[0] + 1,
            current_state=current_state,
        )
        return {p.number: p.ensemble_score for p in predictions}

    def get_current_state(
        self,
        draws: list[DrawResult],
    ) -> EconomicState:
        """Get the current economic state from draws.

        Args:
            draws: List of DrawResult objects

        Returns:
            Current EconomicState
        """
        states = extract_economic_states(
            draws=sorted(draws, key=lambda d: d.date),
            window=self.cv_window,
            numbers_range=self.numbers_range,
            jackpot_high_threshold=self.jackpot_high_threshold,
            cv_high_threshold=self.cv_high_threshold,
        )
        return states[-1] if states else EconomicState(
            date=datetime.now(),
            spieleinsatz=None,
            jackpot=None,
            rolling_cv=None,
            state_label="NORMAL",
        )

    def get_report(self) -> Optional[StateAwareReport]:
        """Return the last training report.

        Returns:
            StateAwareReport or None if not trained
        """
        return self._report

    def save(self, path: Union[str, Path]) -> None:
        """Save the trained predictor.

        Args:
            path: Base path (without extension)
        """
        if not self._is_fitted:
            raise RuntimeError("Predictor must be trained first.")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save base predictor
        self._base_predictor.save(path)

        # Save state-aware config
        config = {
            "state_alphas": self.state_alphas,
            "numbers_range": list(self.numbers_range),
            "numbers_to_draw": self.numbers_to_draw,
            "cv_window": self.cv_window,
            "jackpot_high_threshold": self.jackpot_high_threshold,
            "cv_high_threshold": self.cv_high_threshold,
        }

        with open(path.with_suffix(".state_aware.json"), "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"StateAwarePredictor saved to {path}")

    def load(self, path: Union[str, Path]) -> None:
        """Load a saved predictor.

        Args:
            path: Base path (without extension)
        """
        path = Path(path)

        # Load base predictor
        self._base_predictor.load(path)

        # Load state-aware config
        with open(path.with_suffix(".state_aware.json"), "r") as f:
            config = json.load(f)

        self.state_alphas = config["state_alphas"]
        self.numbers_range = tuple(config["numbers_range"])
        self.numbers_to_draw = config["numbers_to_draw"]
        self.cv_window = config["cv_window"]
        self.jackpot_high_threshold = config["jackpot_high_threshold"]
        self.cv_high_threshold = config["cv_high_threshold"]

        self._is_fitted = True
        logger.info(f"StateAwarePredictor loaded from {path}")


__all__ = [
    "StateAwarePredictor",
    "StateAwarePrediction",
    "StateAwareReport",
    "DEFAULT_STATE_ALPHAS",
]
