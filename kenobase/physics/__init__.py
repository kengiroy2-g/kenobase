"""Physics module - Model Laws A/B/C, Avalanche, Metrics.

Dieses Modul implementiert physik-inspirierte Konzepte fuer Kenobase V2.0.
"""

from kenobase.physics.avalanche import (
    THETA_MODERATE,
    THETA_SAFE,
    THETA_WARNING,
    AvalancheResult,
    AvalancheState,
    analyze_combination,
    calculate_expected_value,
    calculate_theta,
    get_avalanche_state,
    get_avalanche_state_with_thresholds,
    is_profitable,
    max_picks_for_theta,
)
from kenobase.physics.metrics import (
    calculate_autocorrelation,
    calculate_autocorrelation_series,
    calculate_coefficient_of_variation,
    calculate_hurst_exponent,
    calculate_stability_score,
    calculate_volatility,
    count_regime_peaks,
)
from kenobase.physics.model_laws import (
    PipelineConfig,
    calculate_criticality,
    calculate_criticality_from_config,
    calculate_pipeline_action,
    calculate_stability,
    is_law,
    select_best_pipeline,
)

__all__ = [
    # Model Laws (A/B/C)
    "is_law",
    "calculate_stability",
    "PipelineConfig",
    "calculate_pipeline_action",
    "select_best_pipeline",
    "calculate_criticality",
    "calculate_criticality_from_config",
    # Avalanche
    "AvalancheState",
    "AvalancheResult",
    "THETA_SAFE",
    "THETA_MODERATE",
    "THETA_WARNING",
    "calculate_theta",
    "get_avalanche_state",
    "get_avalanche_state_with_thresholds",
    "is_profitable",
    "calculate_expected_value",
    "analyze_combination",
    "max_picks_for_theta",
    # Metrics
    "calculate_hurst_exponent",
    "calculate_autocorrelation",
    "calculate_autocorrelation_series",
    "count_regime_peaks",
    "calculate_volatility",
    "calculate_coefficient_of_variation",
    "calculate_stability_score",
]
