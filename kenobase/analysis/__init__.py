"""Analysis module - Frequency, Pattern, Stability, Criticality."""

from kenobase.analysis.frequency import (
    FrequencyResult,
    PairFrequencyResult,
    calculate_frequency,
    calculate_pair_frequency,
    calculate_rolling_frequency,
    classify_numbers,
    classify_pairs,
    get_cold_numbers,
    get_hot_numbers,
)
from kenobase.analysis.pattern import (
    PatternResult,
    aggregate_patterns,
    extract_patterns,
    extract_patterns_from_draws,
)

__all__ = [
    # Frequency
    "FrequencyResult",
    "PairFrequencyResult",
    "calculate_frequency",
    "calculate_pair_frequency",
    "calculate_rolling_frequency",
    "classify_numbers",
    "classify_pairs",
    "get_hot_numbers",
    "get_cold_numbers",
    # Pattern
    "PatternResult",
    "extract_patterns",
    "extract_patterns_from_draws",
    "aggregate_patterns",
]
