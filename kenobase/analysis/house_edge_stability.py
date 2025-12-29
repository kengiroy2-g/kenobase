"""House-Edge Stability Analysis for HOUSE-003.

This module tests rolling stability of Restbetrag (house edge) over 7/14/30 day windows.
Coefficient of Variation (CV) < 15% indicates active payout control.

Hypothesis: If Keno payouts are actively managed, the Restbetrag will show
unusually low variance over rolling windows compared to random variance.

Data source: Keno_GPTs/Keno_Ziehung2023_+_Restbetrag_v2.CSV
Columns: Datum, z1-z20, Spieleinsatz, Total_Auszahlung, Restbetrag_nach_Auszahlung

Usage:
    from kenobase.analysis.house_edge_stability import (
        RollingWindowResult,
        HouseEdgeStabilityResult,
        calculate_rolling_cv,
        analyze_house_edge_stability,
        run_house003_analysis,
    )

    # Load and analyze
    result = run_house003_analysis("Keno_GPTs/Keno_Ziehung2023_+_Restbetrag_v2.CSV")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from kenobase.analysis.stake_correlation import StakeDrawRecord

logger = logging.getLogger(__name__)

# Default rolling windows (days)
DEFAULT_WINDOWS = [7, 14, 30]

# CV threshold for stability classification
CV_STABILITY_THRESHOLD = 0.15  # 15%


@dataclass(frozen=True)
class RollingWindowResult:
    """Result for a single rolling window analysis.

    Attributes:
        window_size: Window size in days
        n_windows: Number of rolling windows calculated
        cv_mean: Mean CV across all windows
        cv_std: Standard deviation of CV across windows
        cv_min: Minimum CV observed
        cv_max: Maximum CV observed
        cv_values: List of CV values for each window position
        is_stable: True if cv_mean < CV_STABILITY_THRESHOLD
    """

    window_size: int
    n_windows: int
    cv_mean: float
    cv_std: float
    cv_min: float
    cv_max: float
    cv_values: tuple[float, ...]
    is_stable: bool


@dataclass
class HouseEdgeStabilityResult:
    """Complete result of HOUSE-003 rolling stability analysis.

    Attributes:
        n_records: Total number of records analyzed
        date_range_start: First date in dataset
        date_range_end: Last date in dataset
        field_analyzed: Field used for analysis (restbetrag or total_auszahlung)
        windows: Dict mapping window_size -> RollingWindowResult
        stable_count: Number of windows with CV < threshold
        total_windows: Total number of window sizes tested
        hypothesis_supported: True if stable_count >= 2 (majority stable)
        cv_threshold: CV threshold used for classification
    """

    n_records: int
    date_range_start: datetime
    date_range_end: datetime
    field_analyzed: str
    windows: dict[int, RollingWindowResult] = field(default_factory=dict)
    stable_count: int = 0
    total_windows: int = 0
    hypothesis_supported: bool = False
    cv_threshold: float = CV_STABILITY_THRESHOLD


def calculate_rolling_cv(
    values: list[float],
    window_size: int,
) -> tuple[list[float], list[float], list[float]]:
    """Calculate rolling Coefficient of Variation.

    CV = std(window) / mean(window)

    Args:
        values: List of values to analyze
        window_size: Size of rolling window

    Returns:
        Tuple of (cv_values, mean_values, std_values) for each window position
    """
    if len(values) < window_size:
        logger.warning(f"Not enough data ({len(values)}) for window size {window_size}")
        return [], [], []

    cv_values = []
    mean_values = []
    std_values = []

    for i in range(len(values) - window_size + 1):
        window = values[i : i + window_size]
        window_mean = float(np.mean(window))
        window_std = float(np.std(window))

        # Avoid division by zero
        if window_mean > 0:
            cv = window_std / window_mean
        else:
            cv = 0.0

        cv_values.append(cv)
        mean_values.append(window_mean)
        std_values.append(window_std)

    return cv_values, mean_values, std_values


def analyze_single_window(
    values: list[float],
    window_size: int,
    cv_threshold: float = CV_STABILITY_THRESHOLD,
) -> RollingWindowResult:
    """Analyze stability for a single window size.

    Args:
        values: List of values to analyze
        window_size: Size of rolling window
        cv_threshold: Threshold for stability classification

    Returns:
        RollingWindowResult with CV statistics
    """
    cv_values, _, _ = calculate_rolling_cv(values, window_size)

    if not cv_values:
        return RollingWindowResult(
            window_size=window_size,
            n_windows=0,
            cv_mean=0.0,
            cv_std=0.0,
            cv_min=0.0,
            cv_max=0.0,
            cv_values=tuple(),
            is_stable=False,
        )

    cv_mean = float(np.mean(cv_values))
    cv_std = float(np.std(cv_values))
    cv_min = float(np.min(cv_values))
    cv_max = float(np.max(cv_values))

    return RollingWindowResult(
        window_size=window_size,
        n_windows=len(cv_values),
        cv_mean=cv_mean,
        cv_std=cv_std,
        cv_min=cv_min,
        cv_max=cv_max,
        cv_values=tuple(cv_values),
        is_stable=cv_mean < cv_threshold,
    )


def analyze_house_edge_stability(
    records: list[StakeDrawRecord],
    windows: list[int] | None = None,
    field: str = "restbetrag",
    cv_threshold: float = CV_STABILITY_THRESHOLD,
) -> HouseEdgeStabilityResult:
    """Analyze rolling stability of house edge (Restbetrag).

    Tests HOUSE-003: Does Restbetrag show suspiciously low variance
    over rolling windows, indicating active payout management?

    Args:
        records: List of StakeDrawRecord objects (sorted by date)
        windows: List of window sizes to test (default: [7, 14, 30])
        field: Field to analyze ("restbetrag" or "total_auszahlung")
        cv_threshold: CV threshold for stability classification

    Returns:
        HouseEdgeStabilityResult with analysis for all windows
    """
    if windows is None:
        windows = DEFAULT_WINDOWS

    if not records:
        logger.warning("No records provided for HOUSE-003 analysis")
        return HouseEdgeStabilityResult(
            n_records=0,
            date_range_start=datetime.min,
            date_range_end=datetime.min,
            field_analyzed=field,
            cv_threshold=cv_threshold,
        )

    # Sort by date
    sorted_records = sorted(records, key=lambda r: r.date)

    # Extract values based on field
    if field == "restbetrag":
        values = [r.restbetrag for r in sorted_records]
    elif field == "total_auszahlung":
        values = [r.total_auszahlung for r in sorted_records]
    else:
        logger.error(f"Unknown field: {field}")
        values = [r.restbetrag for r in sorted_records]

    # Analyze each window size
    window_results: dict[int, RollingWindowResult] = {}
    stable_count = 0

    for ws in windows:
        result = analyze_single_window(values, ws, cv_threshold)
        window_results[ws] = result
        if result.is_stable:
            stable_count += 1

    # Hypothesis is supported if at least 2 of 3 windows are stable
    hypothesis_supported = stable_count >= 2

    return HouseEdgeStabilityResult(
        n_records=len(records),
        date_range_start=sorted_records[0].date,
        date_range_end=sorted_records[-1].date,
        field_analyzed=field,
        windows=window_results,
        stable_count=stable_count,
        total_windows=len(windows),
        hypothesis_supported=hypothesis_supported,
        cv_threshold=cv_threshold,
    )


def run_house003_analysis(
    stake_path: str | Path,
    windows: list[int] | None = None,
    cv_threshold: float = CV_STABILITY_THRESHOLD,
) -> HouseEdgeStabilityResult:
    """Run complete HOUSE-003 analysis.

    Args:
        stake_path: Path to stake data file
        windows: List of window sizes to test (default: [7, 14, 30])
        cv_threshold: CV threshold for stability classification

    Returns:
        HouseEdgeStabilityResult with analysis for all windows
    """
    # Import here to avoid circular dependency
    from kenobase.analysis.stake_correlation import load_stake_data

    records = load_stake_data(stake_path)

    if not records:
        logger.error(f"Failed to load stake data from {stake_path}")
        return HouseEdgeStabilityResult(
            n_records=0,
            date_range_start=datetime.min,
            date_range_end=datetime.min,
            field_analyzed="restbetrag",
            cv_threshold=cv_threshold,
        )

    logger.info(f"Loaded {len(records)} records for HOUSE-003 analysis")

    return analyze_house_edge_stability(
        records=records,
        windows=windows,
        field="restbetrag",
        cv_threshold=cv_threshold,
    )


def result_to_dict(result: HouseEdgeStabilityResult) -> dict:
    """Convert HouseEdgeStabilityResult to JSON-serializable dict.

    Args:
        result: HouseEdgeStabilityResult object

    Returns:
        Dict suitable for JSON serialization
    """
    windows_dict = {}
    for ws, wr in result.windows.items():
        windows_dict[str(ws)] = {
            "window_size": wr.window_size,
            "n_windows": wr.n_windows,
            "cv_mean": round(wr.cv_mean, 6),
            "cv_std": round(wr.cv_std, 6),
            "cv_min": round(wr.cv_min, 6),
            "cv_max": round(wr.cv_max, 6),
            "is_stable": wr.is_stable,
            # Omit cv_values to keep output concise
        }

    return {
        "n_records": result.n_records,
        "date_range_start": result.date_range_start.isoformat()
        if result.date_range_start != datetime.min
        else None,
        "date_range_end": result.date_range_end.isoformat()
        if result.date_range_end != datetime.min
        else None,
        "field_analyzed": result.field_analyzed,
        "windows": windows_dict,
        "stable_count": result.stable_count,
        "total_windows": result.total_windows,
        "hypothesis_supported": result.hypothesis_supported,
        "cv_threshold": result.cv_threshold,
    }


__all__ = [
    "RollingWindowResult",
    "HouseEdgeStabilityResult",
    "CV_STABILITY_THRESHOLD",
    "DEFAULT_WINDOWS",
    "calculate_rolling_cv",
    "analyze_single_window",
    "analyze_house_edge_stability",
    "run_house003_analysis",
    "result_to_dict",
]
