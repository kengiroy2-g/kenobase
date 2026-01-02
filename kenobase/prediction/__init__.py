"""Kenobase Prediction Module - ML-basierte Zahlenvorhersage.

Dieses Modul kombiniert:
1. Hypothesen-Synthese: Kombiniert Ergebnisse aus HYP-Analysen
2. ML Prediction: LightGBM Binary Classifier fuer Zahlenvorhersage
3. Walk-Forward Validation: Robustes Backtesting

Hauptkomponenten:
- HypothesisSynthesizer: Kombiniert HYP-Ergebnisse zu Scores
- KenoPredictor: LightGBM-basierter Predictor
- KenoTrainer: Orchestriert Training + Validation

Usage:
    # Hypothesen-basiert
    from kenobase.prediction import HypothesisSynthesizer
    synthesizer = HypothesisSynthesizer(results_dir="results")
    scores = synthesizer.synthesize()

    # ML-basiert
    from kenobase.prediction import KenoTrainer
    trainer = KenoTrainer()
    report = trainer.train_and_evaluate(draws)
    predictions = trainer.predict(draws, top_n=10)
"""

from kenobase.prediction.synthesizer import HypothesisSynthesizer
from kenobase.prediction.recommendation import (
    generate_recommendations,
    Recommendation,
    RecommendationTier,
)
from kenobase.prediction.model import (
    KenoPredictor,
    ModelConfig,
    ModelMetrics,
    PredictionResult,
    HAS_LIGHTGBM,
    HAS_OPTUNA,
)
from kenobase.prediction.trainer import (
    KenoTrainer,
    TrainingReport,
    WalkForwardConfig,
    WalkForwardResult,
)
from kenobase.prediction.ensemble import (
    EnsemblePredictor,
    EnsemblePrediction,
    EnsembleReport,
)
from kenobase.prediction.storage import (
    Prediction,
    PredictionMetrics,
    PredictionStorage,
    generate_draw_id,
)
from kenobase.prediction.explainability import (
    SHAPExplainer,
    SHAPExplanation,
    HAS_SHAP,
    validate_shap_native_correlation,
)
from kenobase.prediction.state_aware import (
    StateAwarePredictor,
    StateAwarePrediction,
    StateAwareReport,
    DEFAULT_STATE_ALPHAS,
)
from kenobase.prediction.win_class_calculator import (
    GK_LABELS_BY_TYPE,
    WinClassResult,
    TicketEvaluation,
    get_gewinnklasse,
    calculate_hits,
    evaluate_ticket_single_draw,
    evaluate_ticket_parallel,
    evaluate_v1_v2_parallel,
    format_evaluation_summary,
)

__all__ = [
    # Synthesizer
    "HypothesisSynthesizer",
    # Recommendation
    "generate_recommendations",
    "Recommendation",
    "RecommendationTier",
    # Model
    "KenoPredictor",
    "ModelConfig",
    "ModelMetrics",
    "PredictionResult",
    "HAS_LIGHTGBM",
    "HAS_OPTUNA",
    # Trainer
    "KenoTrainer",
    "TrainingReport",
    "WalkForwardConfig",
    "WalkForwardResult",
    # Ensemble
    "EnsemblePredictor",
    "EnsemblePrediction",
    "EnsembleReport",
    # Storage
    "Prediction",
    "PredictionMetrics",
    "PredictionStorage",
    "generate_draw_id",
    # Explainability (TASK-P14)
    "SHAPExplainer",
    "SHAPExplanation",
    "HAS_SHAP",
    "validate_shap_native_correlation",
    # State-Aware (TASK_004)
    "StateAwarePredictor",
    "StateAwarePrediction",
    "StateAwareReport",
    "DEFAULT_STATE_ALPHAS",
    # Win Class Calculator (TASK_005)
    "GK_LABELS_BY_TYPE",
    "WinClassResult",
    "TicketEvaluation",
    "get_gewinnklasse",
    "calculate_hits",
    "evaluate_ticket_single_draw",
    "evaluate_ticket_parallel",
    "evaluate_v1_v2_parallel",
    "format_evaluation_summary",
]
