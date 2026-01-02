"""Core module - Config, Data Loading, Number Pool, Combination Engine."""

from kenobase.core.config import (
    KenobaseConfig,
    GameConfig,
    PhysicsConfig,
    AnalysisConfig,
    PipelineConfig,
    PathsConfig,
    LegacyConfig,
    LoggingConfig,
    SummenSignaturConfig,
    load_config,
    save_config,
    get_config,
    set_config,
)
from kenobase.core.data_loader import (
    DataLoader,
    DrawResult,
    GameType,
    FormatInfo,
)
from kenobase.core.number_pool import (
    NumberPoolGenerator,
    PeriodAnalysis,
)
from kenobase.core.combination_engine import (
    CombinationEngine,
    CombinationResult,
)
from kenobase.core.axioms import (
    Axiom,
    Prediction,
    Direction,
    NullModelType,
    ALL_AXIOMS,
    ALL_PREDICTIONS,
    get_axiom,
    get_prediction,
    get_predictions_for_axiom,
    get_predictions_requiring_data,
    get_predictions_by_null_model,
    export_all_axioms,
    get_train_test_split,
    get_eurojackpot_control_config,
)
from kenobase.core.normalizer import (
    GAME_RANGES,
    EUROJACKPOT_BONUS_RANGE,
    LOTTO_BONUS_RANGE,
    get_game_range,
    normalize_number,
    denormalize_number,
    normalize_numbers,
    denormalize_numbers,
    normalize_draw,
    normalize_draws,
    cross_game_distance,
)
from kenobase.core.economic_state import (
    EconomicState,
    parse_spieleinsatz,
    parse_jackpot,
    compute_rolling_cv,
    classify_economic_state,
    extract_economic_states,
    get_bet_recommendation,
    compute_state_distribution,
)

__all__ = [
    # Config
    "KenobaseConfig",
    "GameConfig",
    "PhysicsConfig",
    "AnalysisConfig",
    "SummenSignaturConfig",
    "PipelineConfig",
    "PathsConfig",
    "LegacyConfig",
    "LoggingConfig",
    "load_config",
    "save_config",
    "get_config",
    "set_config",
    # Data Loader
    "DataLoader",
    "DrawResult",
    "GameType",
    "FormatInfo",
    # Number Pool
    "NumberPoolGenerator",
    "PeriodAnalysis",
    # Combination Engine
    "CombinationEngine",
    "CombinationResult",
    # Axioms
    "Axiom",
    "Prediction",
    "Direction",
    "NullModelType",
    "ALL_AXIOMS",
    "ALL_PREDICTIONS",
    "get_axiom",
    "get_prediction",
    "get_predictions_for_axiom",
    "get_predictions_requiring_data",
    "get_predictions_by_null_model",
    "export_all_axioms",
    "get_train_test_split",
    "get_eurojackpot_control_config",
    # Normalizer
    "GAME_RANGES",
    "EUROJACKPOT_BONUS_RANGE",
    "LOTTO_BONUS_RANGE",
    "get_game_range",
    "normalize_number",
    "denormalize_number",
    "normalize_numbers",
    "denormalize_numbers",
    "normalize_draw",
    "normalize_draws",
    "cross_game_distance",
    # Economic State
    "EconomicState",
    "parse_spieleinsatz",
    "parse_jackpot",
    "compute_rolling_cv",
    "classify_economic_state",
    "extract_economic_states",
    "get_bet_recommendation",
    "compute_state_distribution",
]
