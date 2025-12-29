"""Odds-Correlation Analysis for HYP-010.

This module tests the hypothesis that winner counts (Gewinnquoten) correlate
with drawn numbers - identifying "safe" (low winners) vs "popular" (high winners) numbers.

Hypothesis: Significant correlation (|r| > 0.2, p < 0.05) between draw frequency
and aggregated winner counts indicates non-random player behavior patterns.

Usage:
    from kenobase.analysis.odds_correlation import (
        OddsCorrelationResult,
        load_gq_winner_data,
        aggregate_winners_by_date,
        calculate_number_winner_scores,
        analyze_odds_correlation,
        classify_numbers_by_popularity,
    )

    # Load and analyze
    gq_data = load_gq_winner_data("Keno_GPTs/Keno_GQ_2022_2023-2024.csv")
    result = analyze_odds_correlation(gq_data, draws)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy import stats

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OddsCorrelationResult:
    """Result of odds-winner correlation analysis.

    Attributes:
        pearson_r: Pearson correlation coefficient
        pearson_p: Pearson p-value
        spearman_r: Spearman correlation coefficient
        spearman_p: Spearman p-value
        is_significant: True if either p < 0.05
        n_samples: Number of numbers analyzed (typically 70 for KENO)
        n_draws: Number of draws analyzed
        n_gq_dates: Number of GQ dates with data
    """

    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float
    is_significant: bool
    n_samples: int
    n_draws: int
    n_gq_dates: int


@dataclass
class NumberClassification:
    """Classification of a number based on winner counts.

    Attributes:
        number: The lottery number (1-70)
        avg_winners: Average winner count when this number was drawn
        draw_count: Number of times this number was drawn in the overlap period
        classification: "safe" (low winners), "neutral", or "popular" (high winners)
        z_score: Standard deviations from median
    """

    number: int
    avg_winners: float
    draw_count: int
    classification: str
    z_score: float


@dataclass
class OddsAnalysisSummary:
    """Complete summary of HYP-010 analysis.

    Attributes:
        correlation: Main correlation result
        safe_numbers: Numbers with below-average winners (fewer players picked them)
        popular_numbers: Numbers with above-average winners (more players picked them)
        classification_stats: Statistics about the classification
    """

    correlation: OddsCorrelationResult
    safe_numbers: list[int] = field(default_factory=list)
    popular_numbers: list[int] = field(default_factory=list)
    classification_stats: dict = field(default_factory=dict)


def load_gq_winner_data(
    path: str | Path,
    encoding: str = "utf-8",
) -> dict[datetime, dict[int, float]]:
    """Load Gewinnquoten data and extract winner counts per date per Keno-Typ.

    The GQ data contains number of winners per draw per Keno-Typ.
    More winners suggests more players picked similar number combinations.

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
    date_winners: dict[datetime, dict[int, float]] = defaultdict(
        lambda: defaultdict(float)
    )

    df = pd.read_csv(file_path, encoding=encoding)

    # Normalize column names
    df.columns = df.columns.str.strip()

    # Expected columns: Datum, Keno-Typ, Anzahl richtiger Zahlen, Anzahl der Gewinner
    required = ["Datum", "Keno-Typ", "Anzahl der Gewinner"]
    for col in required:
        if col not in df.columns:
            logger.warning(f"Missing column: {col} in {file_path}")
            return {}

    for _, row in df.iterrows():
        try:
            date_str = str(row["Datum"]).strip()
            date = datetime.strptime(date_str, "%d.%m.%Y")

            keno_typ = int(row["Keno-Typ"])
            winners = row["Anzahl der Gewinner"]

            # Handle German number format (3.462 = 3462, 1.443 = 1443)
            if isinstance(winners, str):
                winners = winners.replace(".", "").replace(",", ".")
            winners = float(winners)

            date_winners[date][keno_typ] = winners

        except (ValueError, KeyError) as e:
            logger.debug(f"Skipping row: {e}")
            continue

    logger.info(f"Loaded GQ winner data for {len(date_winners)} dates from {file_path.name}")
    return dict(date_winners)


def aggregate_winners_by_date(
    gq_data: dict[datetime, dict[int, float]],
    weight_by_keno_typ: bool = True,
) -> dict[datetime, float]:
    """Aggregate winner counts per date across all Keno-Typs.

    Args:
        gq_data: GQ data from load_gq_winner_data()
        weight_by_keno_typ: If True, weight winners by Keno-Typ (higher types = more informative)

    Returns:
        Dict mapping date -> total_winners (optionally weighted)
    """
    result = {}

    for date, keno_winners in gq_data.items():
        if weight_by_keno_typ:
            # Weight by Keno-Typ: higher types picked more numbers, more informative
            total = sum(
                winners * (keno_typ / 10.0)
                for keno_typ, winners in keno_winners.items()
            )
        else:
            total = sum(keno_winners.values())

        result[date] = total

    return result


def calculate_number_winner_scores(
    gq_data: dict[datetime, dict[int, float]],
    draws: list[DrawResult],
    weight_by_keno_typ: bool = True,
) -> dict[int, tuple[float, int]]:
    """Calculate average winner count associated with each drawn number.

    For each number, sum the winner counts from dates when that number was drawn,
    then average by draw count.

    Args:
        gq_data: GQ data from load_gq_winner_data()
        draws: List of DrawResult objects
        weight_by_keno_typ: If True, weight winners by Keno-Typ

    Returns:
        Dict mapping number -> (avg_winners, draw_count)
    """
    # First aggregate winners per date
    date_totals = aggregate_winners_by_date(gq_data, weight_by_keno_typ)

    # Track total winners and count per number
    number_winners: dict[int, float] = defaultdict(float)
    number_counts: dict[int, int] = defaultdict(int)

    overlap_draws = 0
    for draw in draws:
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)

        if draw_date in date_totals:
            overlap_draws += 1
            total_winners = date_totals[draw_date]

            for num in draw.numbers:
                number_winners[num] += total_winners
                number_counts[num] += 1

    logger.info(f"Found {overlap_draws} draws with matching GQ data")

    # Calculate average
    result = {}
    for num in range(1, 71):  # KENO uses 1-70
        if number_counts[num] > 0:
            avg = number_winners[num] / number_counts[num]
            result[num] = (avg, number_counts[num])
        else:
            result[num] = (0.0, 0)

    return result


def calculate_draw_frequency(
    draws: list[DrawResult],
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict[int, float]:
    """Calculate draw frequency for each number within date range.

    Args:
        draws: List of DrawResult objects
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        Dict mapping number -> relative_frequency (0-1)
    """
    if not draws:
        return {}

    # Filter by date range
    filtered = draws
    if start_date:
        filtered = [d for d in filtered if d.date >= start_date]
    if end_date:
        filtered = [d for d in filtered if d.date <= end_date]

    if not filtered:
        return {}

    from collections import Counter

    counter: Counter[int] = Counter()
    for draw in filtered:
        counter.update(draw.numbers)

    total = len(filtered)
    frequencies = {}

    for n in range(1, 71):  # KENO uses 1-70
        frequencies[n] = counter.get(n, 0) / total

    return frequencies


def analyze_odds_correlation(
    gq_data: dict[datetime, dict[int, float]],
    draws: list[DrawResult],
    weight_by_keno_typ: bool = True,
) -> OddsCorrelationResult:
    """Analyze correlation between draw frequency and winner counts.

    Tests HYP-010: Do drawn numbers correlate with winner counts?
    - Positive correlation: popular numbers are drawn more often
    - Negative correlation: popular numbers are drawn less often (manipulation?)

    Args:
        gq_data: GQ data from load_gq_winner_data()
        draws: List of DrawResult objects
        weight_by_keno_typ: If True, weight winners by Keno-Typ

    Returns:
        OddsCorrelationResult with Pearson and Spearman correlations
    """
    # Get date range of GQ data
    if not gq_data:
        logger.warning("No GQ data provided")
        return OddsCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=0,
            n_draws=0,
            n_gq_dates=0,
        )

    gq_dates = sorted(gq_data.keys())
    start_date = gq_dates[0]
    end_date = gq_dates[-1]

    # Filter draws to overlap period
    overlap_draws = [
        d for d in draws
        if start_date <= d.date.replace(hour=0, minute=0, second=0, microsecond=0) <= end_date
    ]

    if len(overlap_draws) < 10:
        logger.warning(f"Only {len(overlap_draws)} draws overlap with GQ data")
        return OddsCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=0,
            n_draws=len(overlap_draws),
            n_gq_dates=len(gq_dates),
        )

    # Calculate winner scores per number
    winner_scores = calculate_number_winner_scores(gq_data, overlap_draws, weight_by_keno_typ)

    # Calculate draw frequency in overlap period
    draw_freq = calculate_draw_frequency(overlap_draws)

    # Prepare arrays for correlation
    numbers = sorted(set(winner_scores.keys()) & set(draw_freq.keys()))

    if len(numbers) < 10:
        logger.warning(f"Only {len(numbers)} numbers with data")
        return OddsCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=len(numbers),
            n_draws=len(overlap_draws),
            n_gq_dates=len(gq_dates),
        )

    winner_values = [winner_scores[n][0] for n in numbers]  # avg_winners
    freq_values = [draw_freq[n] for n in numbers]

    # Check for constant arrays
    if len(set(winner_values)) == 1 or len(set(freq_values)) == 1:
        logger.warning("Constant input detected, correlation undefined")
        return OddsCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=len(numbers),
            n_draws=len(overlap_draws),
            n_gq_dates=len(gq_dates),
        )

    # Calculate correlations
    pearson_r, pearson_p = stats.pearsonr(winner_values, freq_values)
    spearman_r, spearman_p = stats.spearmanr(winner_values, freq_values)

    # Handle NaN
    if np.isnan(pearson_r):
        pearson_r, pearson_p = 0.0, 1.0
    if np.isnan(spearman_r):
        spearman_r, spearman_p = 0.0, 1.0

    is_significant = pearson_p < 0.05 or spearman_p < 0.05

    return OddsCorrelationResult(
        pearson_r=float(pearson_r),
        pearson_p=float(pearson_p),
        spearman_r=float(spearman_r),
        spearman_p=float(spearman_p),
        is_significant=is_significant,
        n_samples=len(numbers),
        n_draws=len(overlap_draws),
        n_gq_dates=len(gq_dates),
    )


def classify_numbers_by_popularity(
    gq_data: dict[datetime, dict[int, float]],
    draws: list[DrawResult],
    threshold_std: float = 1.0,
    weight_by_keno_typ: bool = True,
) -> list[NumberClassification]:
    """Classify numbers as safe, neutral, or popular based on winner counts.

    Safe numbers: below median - 1*std (fewer players pick these)
    Popular numbers: above median + 1*std (more players pick these)

    Args:
        gq_data: GQ data from load_gq_winner_data()
        draws: List of DrawResult objects
        threshold_std: Number of standard deviations for classification (default 1.0)
        weight_by_keno_typ: If True, weight winners by Keno-Typ

    Returns:
        List of NumberClassification for all 70 numbers
    """
    # Get winner scores
    winner_scores = calculate_number_winner_scores(gq_data, draws, weight_by_keno_typ)

    # Extract avg_winners for numbers with data
    values = [score[0] for score in winner_scores.values() if score[1] > 0]

    if not values:
        return []

    median = float(np.median(values))
    std = float(np.std(values))

    if std == 0:
        std = 1.0  # Avoid division by zero

    low_threshold = median - threshold_std * std
    high_threshold = median + threshold_std * std

    classifications = []
    for num in range(1, 71):
        avg_winners, draw_count = winner_scores.get(num, (0.0, 0))

        if draw_count == 0:
            z_score = 0.0
            classification = "no_data"
        else:
            z_score = (avg_winners - median) / std
            if avg_winners < low_threshold:
                classification = "safe"
            elif avg_winners > high_threshold:
                classification = "popular"
            else:
                classification = "neutral"

        classifications.append(
            NumberClassification(
                number=num,
                avg_winners=avg_winners,
                draw_count=draw_count,
                classification=classification,
                z_score=z_score,
            )
        )

    return classifications


def run_hyp010_analysis(
    draws: list[DrawResult],
    gq_path: str | Path,
    weight_by_keno_typ: bool = True,
    classification_threshold: float = 1.0,
) -> OddsAnalysisSummary:
    """Run complete HYP-010 analysis.

    Args:
        draws: List of DrawResult objects
        gq_path: Path to GQ data file
        weight_by_keno_typ: If True, weight winners by Keno-Typ
        classification_threshold: Std threshold for safe/popular classification

    Returns:
        OddsAnalysisSummary with correlation and classification results
    """
    # Load GQ data
    gq_data = load_gq_winner_data(gq_path)

    if not gq_data:
        logger.error(f"Failed to load GQ data from {gq_path}")
        return OddsAnalysisSummary(
            correlation=OddsCorrelationResult(
                pearson_r=0.0,
                pearson_p=1.0,
                spearman_r=0.0,
                spearman_p=1.0,
                is_significant=False,
                n_samples=0,
                n_draws=0,
                n_gq_dates=0,
            ),
        )

    # Run correlation analysis
    correlation = analyze_odds_correlation(gq_data, draws, weight_by_keno_typ)

    # Classify numbers
    classifications = classify_numbers_by_popularity(
        gq_data, draws, classification_threshold, weight_by_keno_typ
    )

    safe_numbers = [c.number for c in classifications if c.classification == "safe"]
    popular_numbers = [c.number for c in classifications if c.classification == "popular"]
    neutral_numbers = [c.number for c in classifications if c.classification == "neutral"]

    # Calculate classification stats
    all_avg_winners = [c.avg_winners for c in classifications if c.draw_count > 0]
    classification_stats = {
        "n_safe": len(safe_numbers),
        "n_popular": len(popular_numbers),
        "n_neutral": len(neutral_numbers),
        "mean_winners": float(np.mean(all_avg_winners)) if all_avg_winners else 0.0,
        "std_winners": float(np.std(all_avg_winners)) if all_avg_winners else 0.0,
        "median_winners": float(np.median(all_avg_winners)) if all_avg_winners else 0.0,
        "threshold_std": classification_threshold,
    }

    return OddsAnalysisSummary(
        correlation=correlation,
        safe_numbers=safe_numbers,
        popular_numbers=popular_numbers,
        classification_stats=classification_stats,
    )


__all__ = [
    "OddsCorrelationResult",
    "NumberClassification",
    "OddsAnalysisSummary",
    "load_gq_winner_data",
    "aggregate_winners_by_date",
    "calculate_number_winner_scores",
    "calculate_draw_frequency",
    "analyze_odds_correlation",
    "classify_numbers_by_popularity",
    "run_hyp010_analysis",
]
