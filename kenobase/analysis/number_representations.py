"""Number representations for cross-lottery time-series analysis.

This module provides different representations of lottery draws as numerical
time-series, enabling alternative coupling analysis methods like Granger
causality, Transfer Entropy, and DTW.

Representations:
- sum: Sum of drawn numbers (single scalar per draw)
- mean: Mean of drawn numbers (single scalar per draw)
- centroid: Normalized centroid position in [0,1]
- presence_vector: Binary vector indicating which numbers were drawn
- normalized_vector: Vector of normalized number positions

All representations support cross-game comparison via normalization.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal, Optional, Sequence

import numpy as np
import pandas as pd

from kenobase.analysis.cross_lottery_coupling import GameDraws
from kenobase.core.normalizer import GAME_RANGES

RepresentationType = Literal["sum", "mean", "centroid", "presence_vector", "normalized_vector"]


@dataclass
class GameTimeSeries:
    """Time-series representation of a lottery game's draws.

    Attributes:
        name: Game name (e.g., "KENO", "LOTTO")
        dates: List of draw dates
        values: NumPy array of representation values
            - For scalar representations: shape (n_draws,)
            - For vector representations: shape (n_draws, dim)
        representation: Type of representation used
        pool_max: Maximum number in the game's pool
    """

    name: str
    dates: list[date]
    values: np.ndarray
    representation: RepresentationType
    pool_max: int


def _get_game_range(name: str) -> tuple[int, int]:
    """Get the number range for a game by name."""
    name_lower = name.lower()
    if name_lower in GAME_RANGES:
        return GAME_RANGES[name_lower]
    # Fallbacks for common names
    if "keno" in name_lower:
        return (1, 70)
    if "lotto" in name_lower or "auswahlwette" in name_lower:
        return (1, 49)
    if "eurojackpot" in name_lower or "ej" in name_lower:
        return (1, 50)
    return (1, 70)  # Default to KENO range


def draws_to_sum_series(game: GameDraws) -> GameTimeSeries:
    """Convert draws to sum-of-numbers time-series.

    Args:
        game: GameDraws object with presence matrix

    Returns:
        GameTimeSeries with sum values (shape: n_draws,)
    """
    n_draws = game.presence.shape[0]
    sums = np.zeros(n_draws, dtype=np.float64)

    for i in range(n_draws):
        # Get drawn numbers from presence matrix
        drawn = np.where(game.presence[i] == 1)[0]
        sums[i] = np.sum(drawn)

    return GameTimeSeries(
        name=game.name,
        dates=game.dates,
        values=sums,
        representation="sum",
        pool_max=game.pool_max,
    )


def draws_to_mean_series(game: GameDraws) -> GameTimeSeries:
    """Convert draws to mean-of-numbers time-series.

    Args:
        game: GameDraws object with presence matrix

    Returns:
        GameTimeSeries with mean values (shape: n_draws,)
    """
    n_draws = game.presence.shape[0]
    means = np.zeros(n_draws, dtype=np.float64)

    for i in range(n_draws):
        drawn = np.where(game.presence[i] == 1)[0]
        if len(drawn) > 0:
            means[i] = np.mean(drawn)
        else:
            means[i] = 0.0

    return GameTimeSeries(
        name=game.name,
        dates=game.dates,
        values=means,
        representation="mean",
        pool_max=game.pool_max,
    )


def draws_to_centroid_series(game: GameDraws) -> GameTimeSeries:
    """Convert draws to normalized centroid time-series.

    The centroid is the mean of drawn numbers, normalized to [0, 1]
    based on the game's number range.

    Args:
        game: GameDraws object with presence matrix

    Returns:
        GameTimeSeries with centroid values in [0, 1] (shape: n_draws,)
    """
    n_draws = game.presence.shape[0]
    centroids = np.zeros(n_draws, dtype=np.float64)

    min_val, max_val = _get_game_range(game.name)
    range_size = max_val - min_val

    for i in range(n_draws):
        drawn = np.where(game.presence[i] == 1)[0]
        if len(drawn) > 0:
            mean_val = np.mean(drawn)
            centroids[i] = (mean_val - min_val) / range_size if range_size > 0 else 0.5
        else:
            centroids[i] = 0.5

    return GameTimeSeries(
        name=game.name,
        dates=game.dates,
        values=centroids,
        representation="centroid",
        pool_max=game.pool_max,
    )


def draws_to_presence_vector_series(game: GameDraws) -> GameTimeSeries:
    """Convert draws to binary presence vector time-series.

    Args:
        game: GameDraws object with presence matrix

    Returns:
        GameTimeSeries with presence vectors (shape: n_draws, pool_max+1)
    """
    return GameTimeSeries(
        name=game.name,
        dates=game.dates,
        values=game.presence.astype(np.float64),
        representation="presence_vector",
        pool_max=game.pool_max,
    )


def draws_to_normalized_vector_series(
    game: GameDraws,
    target_dim: int = 70,
) -> GameTimeSeries:
    """Convert draws to normalized vector time-series.

    Each draw is represented as a vector of sorted normalized positions.
    This enables cross-game comparison by mapping all games to [0, 1].

    Args:
        game: GameDraws object with presence matrix
        target_dim: Target dimension for output vectors (default: 70)

    Returns:
        GameTimeSeries with normalized vectors (shape: n_draws, target_dim)
    """
    n_draws = game.presence.shape[0]
    vectors = np.zeros((n_draws, target_dim), dtype=np.float64)

    min_val, max_val = _get_game_range(game.name)
    range_size = max_val - min_val

    for i in range(n_draws):
        drawn = np.where(game.presence[i] == 1)[0]
        if len(drawn) > 0:
            # Normalize to [0, 1]
            normalized = [(n - min_val) / range_size if range_size > 0 else 0.5 for n in drawn]
            normalized_sorted = sorted(normalized)
            # Pad or truncate to target_dim
            for j, val in enumerate(normalized_sorted[:target_dim]):
                vectors[i, j] = val

    return GameTimeSeries(
        name=game.name,
        dates=game.dates,
        values=vectors,
        representation="normalized_vector",
        pool_max=game.pool_max,
    )


def game_to_time_series(
    game: GameDraws,
    representation: RepresentationType = "centroid",
    target_dim: int = 70,
) -> GameTimeSeries:
    """Convert a GameDraws to the specified time-series representation.

    Args:
        game: GameDraws object
        representation: Type of representation
        target_dim: Target dimension for vector representations

    Returns:
        GameTimeSeries with the specified representation
    """
    if representation == "sum":
        return draws_to_sum_series(game)
    elif representation == "mean":
        return draws_to_mean_series(game)
    elif representation == "centroid":
        return draws_to_centroid_series(game)
    elif representation == "presence_vector":
        return draws_to_presence_vector_series(game)
    elif representation == "normalized_vector":
        return draws_to_normalized_vector_series(game, target_dim)
    else:
        raise ValueError(f"Unknown representation: {representation}")


def align_time_series(
    series_list: list[GameTimeSeries],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> pd.DataFrame:
    """Align multiple time-series to a common date index.

    For scalar representations, creates columns named by game.
    For vector representations, flattens to columns named game_0, game_1, etc.

    Args:
        series_list: List of GameTimeSeries to align
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        DataFrame with date index and aligned series values
    """
    if not series_list:
        return pd.DataFrame()

    # Build DataFrames for each series
    dfs = []
    for ts in series_list:
        if ts.values.ndim == 1:
            # Scalar representation
            df = pd.DataFrame({
                "date": ts.dates,
                ts.name: ts.values,
            })
        else:
            # Vector representation - flatten
            cols = {f"{ts.name}_{i}": ts.values[:, i] for i in range(ts.values.shape[1])}
            cols["date"] = ts.dates
            df = pd.DataFrame(cols)

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        dfs.append(df)

    # Join all DataFrames
    result = dfs[0]
    for df in dfs[1:]:
        result = result.join(df, how="outer")

    # Apply date filters
    if start_date:
        result = result[result.index >= pd.Timestamp(start_date)]
    if end_date:
        result = result[result.index <= pd.Timestamp(end_date)]

    return result.sort_index()


def get_train_test_split(
    df: pd.DataFrame,
    split_date: str = "2024-01-01",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split aligned time-series into train and test sets.

    Args:
        df: Aligned DataFrame with date index
        split_date: Date string for train/test split (exclusive for test)

    Returns:
        Tuple of (train_df, test_df)
    """
    split_ts = pd.Timestamp(split_date)
    train = df[df.index < split_ts].copy()
    test = df[df.index >= split_ts].copy()
    return train, test


__all__ = [
    "GameTimeSeries",
    "RepresentationType",
    "draws_to_sum_series",
    "draws_to_mean_series",
    "draws_to_centroid_series",
    "draws_to_presence_vector_series",
    "draws_to_normalized_vector_series",
    "game_to_time_series",
    "align_time_series",
    "get_train_test_split",
]
