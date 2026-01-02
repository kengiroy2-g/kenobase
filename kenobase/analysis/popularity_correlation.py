"""Popularity-Correlation Analysis for HYP-004.

This module tests the hypothesis that popular numbers (frequently played by users)
are inversely correlated with drawn numbers (RNG avoids popular numbers).

Hypothesis: r < -0.2 with p < 0.05 would support HYP-004.

Usage:
    from kenobase.analysis.popularity_correlation import (
        PopularityResult,
        load_gq_popularity,
        calculate_popularity_scores,
        calculate_draw_frequency,
        analyze_correlation,
    )

    # Load and analyze
    popularity = load_gq_popularity("Keno_GPTs/Keno_GQ_2022_2023-2024.csv")
    result = analyze_correlation(popularity, draws, window=30)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy import stats

from kenobase.analysis.distribution import load_gq_data

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)


# Birthday numbers (1-31) are theoretically more popular
BIRTHDAY_NUMBERS = set(range(1, 32))

# "Schoene Zahlen" (aesthetically pleasing numbers)
SCHOENE_ZAHLEN = {7, 11, 13, 17, 21, 33, 37, 42, 49, 55, 66, 69, 70}


@dataclass(frozen=True)
class PopularityResult:
    """Result of popularity correlation analysis.

    Attributes:
        correlation: Spearman correlation coefficient
        p_value: Statistical significance
        is_significant: True if p < 0.05
        supports_hypothesis: True if r < -0.2 and p < 0.05
        n_samples: Number of data points
        method: "gq" or "heuristic"
    """

    correlation: float
    p_value: float
    is_significant: bool
    supports_hypothesis: bool
    n_samples: int
    method: str


@dataclass
class RollingCorrelationResult:
    """Result of rolling window correlation analysis.

    Attributes:
        date: End date of the window
        correlation: Spearman correlation for this window
        p_value: P-value for this window
        window_size: Size of the rolling window
    """

    date: datetime
    correlation: float
    p_value: float
    window_size: int


def load_gq_popularity(
    path: str | Path,
    encoding: str = "utf-8-sig",
) -> dict[datetime, dict[int, float]]:
    """Load Gewinnquoten data and derive popularity scores.

    The GQ data contains number of winners per draw per Keno-Typ.
    More winners in lower prize classes suggests more players picked those numbers.

    Format: Datum,Keno-Typ,Anzahl richtiger Zahlen,Anzahl der Gewinner,1 Euro Gewinn

    Args:
        path: Path to GQ CSV file
        encoding: File encoding (default utf-8)

    Returns:
        Dict mapping date -> {keno_typ -> winner_count}

    Raises:
        FileNotFoundError: If file does not exist
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"GQ file not found: {file_path}")

    # Parse GQ data: aggregate winners per date per Keno-Typ
    date_popularity: dict[datetime, dict[int, float]] = defaultdict(
        lambda: defaultdict(float)
    )

    df = load_gq_data(str(file_path), encoding=encoding)
    if df.empty:
        return {}

    grouped = df.groupby(["Datum", "Keno-Typ"])["Anzahl der Gewinner"].sum()
    for (date, keno_typ), winners in grouped.items():
        weight = int(keno_typ) / 10.0
        date_popularity[pd.Timestamp(date).to_pydatetime()][int(keno_typ)] = float(winners) * weight

    logger.info(f"Loaded GQ data for {len(date_popularity)} dates from {file_path.name}")
    return dict(date_popularity)


def calculate_popularity_scores_heuristic(numbers: range | list[int]) -> dict[int, float]:
    """Calculate popularity scores using heuristic (no GQ data needed).

    Birthday numbers (1-31) and "schoene Zahlen" are assumed more popular.

    Args:
        numbers: Range of possible numbers (e.g., range(1, 71) for KENO)

    Returns:
        Dict mapping number -> popularity_score (0-1)
    """
    scores = {}
    for n in numbers:
        score = 0.0

        # Birthday boost: 1-31 are more popular
        if n in BIRTHDAY_NUMBERS:
            score += 0.3

        # "Schoene Zahlen" boost
        if n in SCHOENE_ZAHLEN:
            score += 0.2

        # Small numbers preference (psychology)
        if n <= 20:
            score += 0.1 * (1 - n / 20)

        # Round numbers preference
        if n % 10 == 0:
            score += 0.1

        scores[n] = min(score, 1.0)

    # Normalize to 0-1
    max_score = max(scores.values()) if scores else 1.0
    if max_score > 0:
        scores = {k: v / max_score for k, v in scores.items()}

    return scores


def calculate_draw_frequency(
    draws: list[DrawResult],
    number_range: tuple[int, int] = (1, 70),
) -> dict[int, float]:
    """Calculate frequency of each number in draws.

    Args:
        draws: List of DrawResult objects
        number_range: Range of possible numbers (min, max)

    Returns:
        Dict mapping number -> relative_frequency (0-1)
    """
    if not draws:
        return {}

    from collections import Counter

    counter: Counter[int] = Counter()
    for draw in draws:
        counter.update(draw.numbers)

    total = len(draws)
    frequencies = {}

    for n in range(number_range[0], number_range[1] + 1):
        frequencies[n] = counter.get(n, 0) / total

    return frequencies


def aggregate_gq_to_number_popularity(
    gq_popularity: dict[datetime, dict[int, float]],
    draws: list[DrawResult],
) -> dict[int, float]:
    """Aggregate GQ data to per-number popularity scores.

    Strategy: For each draw, count winners and associate with drawn numbers.
    Numbers that appear in draws with many winners are "popular".

    Args:
        gq_popularity: GQ data from load_gq_popularity()
        draws: List of DrawResult objects

    Returns:
        Dict mapping number -> popularity_score
    """
    number_popularity: dict[int, float] = defaultdict(float)
    number_counts: dict[int, int] = defaultdict(int)

    for draw in draws:
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)

        if draw_date in gq_popularity:
            # Sum all winners for this date across all Keno-Typs
            total_winners = sum(gq_popularity[draw_date].values())

            # Associate winner count with each drawn number
            for num in draw.numbers:
                number_popularity[num] += total_winners
                number_counts[num] += 1

    # Normalize by count to get average
    result = {}
    for num in number_popularity:
        if number_counts[num] > 0:
            result[num] = number_popularity[num] / number_counts[num]
        else:
            result[num] = 0.0

    # Normalize to 0-1
    if result:
        max_val = max(result.values())
        if max_val > 0:
            result = {k: v / max_val for k, v in result.items()}

    return result


def analyze_correlation(
    popularity: dict[int, float],
    draw_frequency: dict[int, float],
) -> PopularityResult:
    """Analyze Spearman correlation between popularity and draw frequency.

    HYP-004 is supported if:
    - Correlation r < -0.2 (inverse relationship)
    - P-value < 0.05 (statistically significant)

    Args:
        popularity: Dict mapping number -> popularity_score
        draw_frequency: Dict mapping number -> draw_frequency

    Returns:
        PopularityResult with correlation analysis
    """
    # Align the data
    common_numbers = sorted(set(popularity.keys()) & set(draw_frequency.keys()))

    if len(common_numbers) < 10:
        logger.warning(f"Only {len(common_numbers)} common numbers, insufficient data")
        return PopularityResult(
            correlation=0.0,
            p_value=1.0,
            is_significant=False,
            supports_hypothesis=False,
            n_samples=len(common_numbers),
            method="insufficient",
        )

    pop_values = [popularity[n] for n in common_numbers]
    freq_values = [draw_frequency[n] for n in common_numbers]

    # Check for constant arrays (would cause NaN correlation)
    if len(set(pop_values)) == 1 or len(set(freq_values)) == 1:
        logger.warning("Constant input detected, correlation undefined")
        return PopularityResult(
            correlation=0.0,
            p_value=1.0,
            is_significant=False,
            supports_hypothesis=False,
            n_samples=len(common_numbers),
            method="constant_input",
        )

    # Spearman correlation (non-parametric, handles non-normal distributions)
    correlation, p_value = stats.spearmanr(pop_values, freq_values)

    # Handle NaN results
    if np.isnan(correlation) or np.isnan(p_value):
        logger.warning("NaN result from correlation calculation")
        return PopularityResult(
            correlation=0.0,
            p_value=1.0,
            is_significant=False,
            supports_hypothesis=False,
            n_samples=len(common_numbers),
            method="nan_result",
        )

    is_significant = p_value < 0.05
    supports_hypothesis = correlation < -0.2 and is_significant

    return PopularityResult(
        correlation=float(correlation),
        p_value=float(p_value),
        is_significant=is_significant,
        supports_hypothesis=supports_hypothesis,
        n_samples=len(common_numbers),
        method="spearman",
    )


def analyze_rolling_correlation(
    draws: list[DrawResult],
    popularity: dict[int, float],
    window: int = 30,
    number_range: tuple[int, int] = (1, 70),
) -> list[RollingCorrelationResult]:
    """Analyze correlation using rolling windows for walk-forward validation.

    Args:
        draws: List of DrawResult objects (chronologically sorted)
        popularity: Dict mapping number -> popularity_score
        window: Rolling window size in draws
        number_range: Range of possible numbers

    Returns:
        List of RollingCorrelationResult for each window
    """
    if len(draws) < window:
        logger.warning(f"Insufficient draws ({len(draws)}) for window size {window}")
        return []

    results = []

    for i in range(len(draws) - window + 1):
        window_draws = draws[i : i + window]

        # Calculate frequency for this window
        freq = calculate_draw_frequency(window_draws, number_range)

        # Calculate correlation
        corr_result = analyze_correlation(popularity, freq)

        results.append(
            RollingCorrelationResult(
                date=window_draws[-1].date,
                correlation=corr_result.correlation,
                p_value=corr_result.p_value,
                window_size=window,
            )
        )

    return results


def run_hyp004_analysis(
    draws: list[DrawResult],
    gq_path: str | Path | None = None,
    window: int = 30,
    number_range: tuple[int, int] = (1, 70),
) -> dict:
    """Run complete HYP-004 analysis.

    Args:
        draws: List of DrawResult objects
        gq_path: Path to GQ data (uses heuristic if None)
        window: Rolling window size for walk-forward validation
        number_range: Range of possible numbers

    Returns:
        Dict with analysis results including:
        - overall: PopularityResult for entire dataset
        - rolling: List of rolling window results
        - summary: Statistical summary
    """
    # Determine popularity method
    if gq_path and Path(gq_path).exists():
        logger.info(f"Using GQ data from {gq_path}")
        gq_data = load_gq_popularity(gq_path)
        popularity = aggregate_gq_to_number_popularity(gq_data, draws)
        method = "gq"
    else:
        logger.info("Using heuristic popularity (birthday numbers, schoene Zahlen)")
        popularity = calculate_popularity_scores_heuristic(range(*number_range, 1))
        method = "heuristic"

    # Overall analysis
    draw_freq = calculate_draw_frequency(draws, number_range)
    overall = analyze_correlation(popularity, draw_freq)

    # Rolling analysis
    rolling = analyze_rolling_correlation(draws, popularity, window, number_range)

    # Summary statistics
    if rolling:
        rolling_corrs = [r.correlation for r in rolling]
        significant_windows = sum(1 for r in rolling if r.p_value < 0.05)
        supporting_windows = sum(
            1 for r in rolling if r.correlation < -0.2 and r.p_value < 0.05
        )

        summary = {
            "method": method,
            "n_draws": len(draws),
            "n_windows": len(rolling),
            "window_size": window,
            "mean_correlation": float(np.mean(rolling_corrs)),
            "std_correlation": float(np.std(rolling_corrs)),
            "min_correlation": float(np.min(rolling_corrs)),
            "max_correlation": float(np.max(rolling_corrs)),
            "significant_windows": significant_windows,
            "significant_ratio": significant_windows / len(rolling),
            "supporting_windows": supporting_windows,
            "support_ratio": supporting_windows / len(rolling),
            "hypothesis_supported": overall.supports_hypothesis,
        }
    else:
        summary = {
            "method": method,
            "n_draws": len(draws),
            "n_windows": 0,
            "window_size": window,
            "hypothesis_supported": overall.supports_hypothesis,
        }

    return {
        "overall": overall,
        "rolling": rolling,
        "summary": summary,
        "popularity_scores": popularity,
        "draw_frequencies": draw_freq,
    }


@dataclass
class BirthdayCorrelationResult:
    """Result of birthday-score vs winners correlation (Popularity Proxy).

    Attributes:
        correlation: Spearman correlation coefficient
        p_value: Statistical significance
        is_significant: True if p < 0.05
        supports_hypothesis: True if r > 0.3 and p < 0.05
        n_samples: Number of draws analyzed
        mean_birthday_score: Mean birthday-number ratio in draws
        mean_winners: Mean winner count per draw
    """

    correlation: float
    p_value: float
    is_significant: bool
    supports_hypothesis: bool
    n_samples: int
    mean_birthday_score: float
    mean_winners: float


def calculate_birthday_score(drawn_numbers: list[int]) -> float:
    """Calculate fraction of birthday numbers (1-31) in a draw.

    Args:
        drawn_numbers: List of drawn numbers

    Returns:
        Fraction 0.0-1.0 (0 = no birthdays, 1 = all birthdays)
    """
    if not drawn_numbers:
        return 0.0
    birthday_count = sum(1 for n in drawn_numbers if n in BIRTHDAY_NUMBERS)
    return birthday_count / len(drawn_numbers)


def correlate_birthday_with_winners(
    draws: list[DrawResult],
    gq_data: dict[datetime, dict[int, float]],
    *,
    window: int = 30,
) -> dict:
    """Correlate birthday-score with winner count (Popularity Proxy).

    Tests hypothesis: High birthday-score draws have more winners
    because more players pick birthday numbers (1-31).

    Args:
        draws: List of DrawResult objects
        gq_data: GQ data from load_gq_popularity()
        window: Rolling window size for stability test

    Returns:
        Dict with:
        - overall: BirthdayCorrelationResult
        - rolling: List of per-window results
        - summary: Statistical summary
    """
    if not draws or not gq_data:
        return {
            "overall": BirthdayCorrelationResult(
                correlation=0.0,
                p_value=1.0,
                is_significant=False,
                supports_hypothesis=False,
                n_samples=0,
                mean_birthday_score=0.0,
                mean_winners=0.0,
            ),
            "rolling": [],
            "summary": {"error": "No data provided"},
        }

    # Pair draws with GQ winner counts
    paired_data = []
    for draw in draws:
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)
        if draw_date in gq_data:
            # Sum all winners across all Keno-Typs
            total_winners = sum(gq_data[draw_date].values())
            birthday_score = calculate_birthday_score(list(draw.numbers))
            paired_data.append({
                "date": draw_date,
                "birthday_score": birthday_score,
                "winners": total_winners,
            })

    if len(paired_data) < 10:
        return {
            "overall": BirthdayCorrelationResult(
                correlation=0.0,
                p_value=1.0,
                is_significant=False,
                supports_hypothesis=False,
                n_samples=len(paired_data),
                mean_birthday_score=0.0,
                mean_winners=0.0,
            ),
            "rolling": [],
            "summary": {"error": f"Insufficient paired data: {len(paired_data)} < 10"},
        }

    # Calculate overall correlation
    birthday_scores = [p["birthday_score"] for p in paired_data]
    winner_counts = [p["winners"] for p in paired_data]

    correlation, p_value = stats.spearmanr(birthday_scores, winner_counts)

    # Handle NaN
    if np.isnan(correlation) or np.isnan(p_value):
        correlation = 0.0
        p_value = 1.0

    overall = BirthdayCorrelationResult(
        correlation=float(correlation),
        p_value=float(p_value),
        is_significant=p_value < 0.05,
        supports_hypothesis=correlation > 0.3 and p_value < 0.05,
        n_samples=len(paired_data),
        mean_birthday_score=float(np.mean(birthday_scores)),
        mean_winners=float(np.mean(winner_counts)),
    )

    # Rolling window analysis
    rolling_results = []
    if len(paired_data) >= window:
        for i in range(len(paired_data) - window + 1):
            window_data = paired_data[i : i + window]
            w_birthday = [p["birthday_score"] for p in window_data]
            w_winners = [p["winners"] for p in window_data]

            w_corr, w_p = stats.spearmanr(w_birthday, w_winners)
            if np.isnan(w_corr):
                w_corr = 0.0
                w_p = 1.0

            rolling_results.append({
                "end_date": window_data[-1]["date"].isoformat(),
                "correlation": float(w_corr),
                "p_value": float(w_p),
                "is_significant": w_p < 0.05,
                "supports_hypothesis": w_corr > 0.3 and w_p < 0.05,
            })

    # Summary statistics
    if rolling_results:
        rolling_corrs = [r["correlation"] for r in rolling_results]
        supporting_windows = sum(1 for r in rolling_results if r["supports_hypothesis"])
        summary = {
            "n_draws": len(draws),
            "n_paired": len(paired_data),
            "n_windows": len(rolling_results),
            "window_size": window,
            "mean_rolling_correlation": float(np.mean(rolling_corrs)),
            "std_rolling_correlation": float(np.std(rolling_corrs)),
            "supporting_windows": supporting_windows,
            "support_ratio": supporting_windows / len(rolling_results),
            "hypothesis_supported": overall.supports_hypothesis,
        }
    else:
        summary = {
            "n_draws": len(draws),
            "n_paired": len(paired_data),
            "n_windows": 0,
            "window_size": window,
            "hypothesis_supported": overall.supports_hypothesis,
        }

    return {
        "overall": overall,
        "rolling": rolling_results,
        "summary": summary,
    }


__all__ = [
    "PopularityResult",
    "RollingCorrelationResult",
    "BirthdayCorrelationResult",
    "BIRTHDAY_NUMBERS",
    "SCHOENE_ZAHLEN",
    "load_gq_popularity",
    "calculate_popularity_scores_heuristic",
    "calculate_draw_frequency",
    "calculate_birthday_score",
    "aggregate_gq_to_number_popularity",
    "analyze_correlation",
    "analyze_rolling_correlation",
    "correlate_birthday_with_winners",
    "run_hyp004_analysis",
]
