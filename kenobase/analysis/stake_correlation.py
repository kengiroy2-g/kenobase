"""Stake-Correlation Analysis for HYP-012.

This module tests the hypothesis that Spieleinsatz (stake) correlates
with drawn numbers - identifying patterns where certain numbers appear
more often in high-stake or low-stake draws.

Hypothesis: Significant correlation (|r| > 0.2, p < 0.05) between draw frequency
and aggregated stake amounts indicates non-random stake-number relationships.

Data source: Keno_GPTs/Keno_Ziehung2023_+_Restbetrag_v2.CSV
Columns: Datum, z1-z20, Spieleinsatz, Total_gewinner, Total_Auszahlung,
         Eur_pro_Spieler, Restbetrag_nach_Auszahlung, Kasse

Usage:
    from kenobase.analysis.stake_correlation import (
        StakeCorrelationResult,
        load_stake_data,
        aggregate_stake_by_date,
        calculate_number_stake_scores,
        analyze_stake_correlation,
        classify_numbers_by_stake,
    )

    # Load and analyze
    stake_data = load_stake_data("Keno_GPTs/Keno_Ziehung2023_+_Restbetrag_v2.CSV")
    result = analyze_stake_correlation(stake_data)
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
    pass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StakeCorrelationResult:
    """Result of stake-number correlation analysis.

    Attributes:
        pearson_r: Pearson correlation coefficient
        pearson_p: Pearson p-value
        spearman_r: Spearman correlation coefficient
        spearman_p: Spearman p-value
        is_significant: True if either p < 0.05
        n_samples: Number of numbers analyzed (typically 70 for KENO)
        n_draws: Number of draws analyzed
    """

    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float
    is_significant: bool
    n_samples: int
    n_draws: int


@dataclass
class NumberStakeClassification:
    """Classification of a number based on stake correlation.

    Attributes:
        number: The lottery number (1-70)
        avg_stake: Average stake when this number was drawn
        draw_count: Number of times this number was drawn
        classification: "low_stake" (below avg), "neutral", or "high_stake" (above avg)
        z_score: Standard deviations from median
    """

    number: int
    avg_stake: float
    draw_count: int
    classification: str
    z_score: float


@dataclass
class StakeAnalysisSummary:
    """Complete summary of HYP-012 analysis.

    Attributes:
        correlation: Main correlation result
        low_stake_numbers: Numbers associated with below-average stakes
        high_stake_numbers: Numbers associated with above-average stakes
        classification_stats: Statistics about the classification
        auszahlung_correlation: Optional correlation with Total_Auszahlung
        restbetrag_correlation: Optional correlation with Restbetrag
    """

    correlation: StakeCorrelationResult
    low_stake_numbers: list[int] = field(default_factory=list)
    high_stake_numbers: list[int] = field(default_factory=list)
    classification_stats: dict = field(default_factory=dict)
    auszahlung_correlation: StakeCorrelationResult | None = None
    restbetrag_correlation: StakeCorrelationResult | None = None


@dataclass
class StakeDrawRecord:
    """Single draw record with stake data.

    Attributes:
        date: Draw date
        numbers: List of 20 drawn numbers
        spieleinsatz: Stake amount
        total_gewinner: Total winners
        total_auszahlung: Total payout
        restbetrag: Remaining amount after payout
        kasse: Running total
    """

    date: datetime
    numbers: list[int]
    spieleinsatz: float
    total_gewinner: int
    total_auszahlung: float
    restbetrag: float
    kasse: float


def load_stake_data(
    path: str | Path,
    encoding: str = "utf-8",
) -> list[StakeDrawRecord]:
    """Load stake data from Keno_Ziehung CSV with financial columns.

    Format: Datum;z1;z2;...;z20;Plus-5;Spieleinsatz;Total_gewinner;
            Total_Auszahlung;Eur_pro_Spieler;Restbetrag_nach_Auszahlung;Kasse

    Args:
        path: Path to CSV file
        encoding: File encoding (default utf-8)

    Returns:
        List of StakeDrawRecord objects

    Raises:
        FileNotFoundError: If file does not exist
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Stake data file not found: {file_path}")

    records: list[StakeDrawRecord] = []

    df = pd.read_csv(file_path, sep=";", encoding=encoding)

    # Normalize column names
    df.columns = df.columns.str.strip()

    # Check required columns
    required = ["Datum", "Spieleinsatz"]
    number_cols = [f"z{i}" for i in range(1, 21)]
    required.extend(number_cols)

    for col in required:
        if col not in df.columns:
            logger.warning(f"Missing required column: {col} in {file_path}")
            return []

    for _, row in df.iterrows():
        try:
            date_str = str(row["Datum"]).strip()
            date = datetime.strptime(date_str, "%d.%m.%Y")

            # Extract drawn numbers
            numbers = []
            for i in range(1, 21):
                col = f"z{i}"
                if col in row and pd.notna(row[col]):
                    numbers.append(int(row[col]))

            # Parse stake (German format: 342.774 = 342774)
            spieleinsatz = _parse_german_number(row.get("Spieleinsatz", 0))
            total_gewinner = int(_parse_german_number(row.get("Total_gewinner", 0)))
            total_auszahlung = _parse_german_number(row.get("Total_Auszahlung", 0))
            restbetrag = _parse_german_number(
                row.get("Restbetrag_nach_Auszahlung", 0)
            )
            kasse = _parse_german_number(row.get("Kasse", 0))

            records.append(
                StakeDrawRecord(
                    date=date,
                    numbers=numbers,
                    spieleinsatz=spieleinsatz,
                    total_gewinner=total_gewinner,
                    total_auszahlung=total_auszahlung,
                    restbetrag=restbetrag,
                    kasse=kasse,
                )
            )

        except (ValueError, KeyError) as e:
            logger.debug(f"Skipping row: {e}")
            continue

    logger.info(f"Loaded {len(records)} stake records from {file_path.name}")
    return records


def _parse_german_number(value) -> float:
    """Parse German number format (dot as thousand separator).

    Examples:
        342.774 -> 342774.0
        1.443 -> 1443.0
        173458 -> 173458.0
    """
    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()
    if not s:
        return 0.0

    # German format: dot = thousand separator, comma = decimal
    # But our data seems to use dot as thousand separator only
    # Check if likely thousand-separator (digit.digit{3})
    if "." in s and "," not in s:
        # Assume German thousand separator
        s = s.replace(".", "")

    if "," in s:
        s = s.replace(",", ".")

    return float(s)


def aggregate_stake_by_date(
    records: list[StakeDrawRecord],
) -> dict[datetime, float]:
    """Aggregate stake per date.

    Args:
        records: List of StakeDrawRecord objects

    Returns:
        Dict mapping date -> spieleinsatz
    """
    result = {}
    for rec in records:
        result[rec.date] = rec.spieleinsatz
    return result


def calculate_number_stake_scores(
    records: list[StakeDrawRecord],
) -> dict[int, tuple[float, int]]:
    """Calculate average stake associated with each drawn number.

    For each number, sum the stakes from draws when that number appeared,
    then average by draw count.

    Args:
        records: List of StakeDrawRecord objects

    Returns:
        Dict mapping number -> (avg_stake, draw_count)
    """
    number_stakes: dict[int, float] = defaultdict(float)
    number_counts: dict[int, int] = defaultdict(int)

    for rec in records:
        for num in rec.numbers:
            number_stakes[num] += rec.spieleinsatz
            number_counts[num] += 1

    # Calculate average
    result = {}
    for num in range(1, 71):  # KENO uses 1-70
        if number_counts[num] > 0:
            avg = number_stakes[num] / number_counts[num]
            result[num] = (avg, number_counts[num])
        else:
            result[num] = (0.0, 0)

    return result


def calculate_draw_frequency_from_records(
    records: list[StakeDrawRecord],
) -> dict[int, float]:
    """Calculate draw frequency for each number from stake records.

    Args:
        records: List of StakeDrawRecord objects

    Returns:
        Dict mapping number -> relative_frequency (0-1)
    """
    if not records:
        return {}

    from collections import Counter

    counter: Counter[int] = Counter()
    for rec in records:
        counter.update(rec.numbers)

    total = len(records)
    frequencies = {}

    for n in range(1, 71):  # KENO uses 1-70
        frequencies[n] = counter.get(n, 0) / total

    return frequencies


def analyze_stake_correlation(
    records: list[StakeDrawRecord],
) -> StakeCorrelationResult:
    """Analyze correlation between draw frequency and stake amounts.

    Tests HYP-012: Do drawn numbers correlate with stake amounts?
    - Positive correlation: numbers in high-stake draws appear more often
    - Negative correlation: numbers in low-stake draws appear more often

    Args:
        records: List of StakeDrawRecord objects

    Returns:
        StakeCorrelationResult with Pearson and Spearman correlations
    """
    if not records:
        logger.warning("No stake records provided")
        return StakeCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=0,
            n_draws=0,
        )

    if len(records) < 10:
        logger.warning(f"Only {len(records)} stake records available")
        return StakeCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=0,
            n_draws=len(records),
        )

    # Calculate stake scores per number
    stake_scores = calculate_number_stake_scores(records)

    # Calculate draw frequency
    draw_freq = calculate_draw_frequency_from_records(records)

    # Prepare arrays for correlation
    numbers = sorted(set(stake_scores.keys()) & set(draw_freq.keys()))

    if len(numbers) < 10:
        logger.warning(f"Only {len(numbers)} numbers with data")
        return StakeCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=len(numbers),
            n_draws=len(records),
        )

    stake_values = [stake_scores[n][0] for n in numbers]  # avg_stake
    freq_values = [draw_freq[n] for n in numbers]

    # Check for constant arrays
    if len(set(stake_values)) == 1 or len(set(freq_values)) == 1:
        logger.warning("Constant input detected, correlation undefined")
        return StakeCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=len(numbers),
            n_draws=len(records),
        )

    # Calculate correlations
    pearson_r, pearson_p = stats.pearsonr(stake_values, freq_values)
    spearman_r, spearman_p = stats.spearmanr(stake_values, freq_values)

    # Handle NaN
    if np.isnan(pearson_r):
        pearson_r, pearson_p = 0.0, 1.0
    if np.isnan(spearman_r):
        spearman_r, spearman_p = 0.0, 1.0

    is_significant = pearson_p < 0.05 or spearman_p < 0.05

    return StakeCorrelationResult(
        pearson_r=float(pearson_r),
        pearson_p=float(pearson_p),
        spearman_r=float(spearman_r),
        spearman_p=float(spearman_p),
        is_significant=is_significant,
        n_samples=len(numbers),
        n_draws=len(records),
    )


def analyze_auszahlung_correlation(
    records: list[StakeDrawRecord],
) -> StakeCorrelationResult:
    """Analyze correlation between draw frequency and Total_Auszahlung.

    Args:
        records: List of StakeDrawRecord objects

    Returns:
        StakeCorrelationResult for Total_Auszahlung correlation
    """
    if not records or len(records) < 10:
        return StakeCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=0,
            n_draws=len(records) if records else 0,
        )

    # Calculate auszahlung scores per number
    number_auszahlung: dict[int, float] = defaultdict(float)
    number_counts: dict[int, int] = defaultdict(int)

    for rec in records:
        for num in rec.numbers:
            number_auszahlung[num] += rec.total_auszahlung
            number_counts[num] += 1

    auszahlung_scores = {}
    for num in range(1, 71):
        if number_counts[num] > 0:
            auszahlung_scores[num] = number_auszahlung[num] / number_counts[num]
        else:
            auszahlung_scores[num] = 0.0

    draw_freq = calculate_draw_frequency_from_records(records)

    numbers = sorted(set(auszahlung_scores.keys()) & set(draw_freq.keys()))
    auszahlung_values = [auszahlung_scores[n] for n in numbers]
    freq_values = [draw_freq[n] for n in numbers]

    if len(set(auszahlung_values)) == 1 or len(set(freq_values)) == 1:
        return StakeCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=len(numbers),
            n_draws=len(records),
        )

    pearson_r, pearson_p = stats.pearsonr(auszahlung_values, freq_values)
    spearman_r, spearman_p = stats.spearmanr(auszahlung_values, freq_values)

    if np.isnan(pearson_r):
        pearson_r, pearson_p = 0.0, 1.0
    if np.isnan(spearman_r):
        spearman_r, spearman_p = 0.0, 1.0

    return StakeCorrelationResult(
        pearson_r=float(pearson_r),
        pearson_p=float(pearson_p),
        spearman_r=float(spearman_r),
        spearman_p=float(spearman_p),
        is_significant=pearson_p < 0.05 or spearman_p < 0.05,
        n_samples=len(numbers),
        n_draws=len(records),
    )


def analyze_restbetrag_correlation(
    records: list[StakeDrawRecord],
) -> StakeCorrelationResult:
    """Analyze correlation between draw frequency and Restbetrag.

    Args:
        records: List of StakeDrawRecord objects

    Returns:
        StakeCorrelationResult for Restbetrag correlation
    """
    if not records or len(records) < 10:
        return StakeCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=0,
            n_draws=len(records) if records else 0,
        )

    # Calculate restbetrag scores per number
    number_restbetrag: dict[int, float] = defaultdict(float)
    number_counts: dict[int, int] = defaultdict(int)

    for rec in records:
        for num in rec.numbers:
            number_restbetrag[num] += rec.restbetrag
            number_counts[num] += 1

    restbetrag_scores = {}
    for num in range(1, 71):
        if number_counts[num] > 0:
            restbetrag_scores[num] = number_restbetrag[num] / number_counts[num]
        else:
            restbetrag_scores[num] = 0.0

    draw_freq = calculate_draw_frequency_from_records(records)

    numbers = sorted(set(restbetrag_scores.keys()) & set(draw_freq.keys()))
    restbetrag_values = [restbetrag_scores[n] for n in numbers]
    freq_values = [draw_freq[n] for n in numbers]

    if len(set(restbetrag_values)) == 1 or len(set(freq_values)) == 1:
        return StakeCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            n_samples=len(numbers),
            n_draws=len(records),
        )

    pearson_r, pearson_p = stats.pearsonr(restbetrag_values, freq_values)
    spearman_r, spearman_p = stats.spearmanr(restbetrag_values, freq_values)

    if np.isnan(pearson_r):
        pearson_r, pearson_p = 0.0, 1.0
    if np.isnan(spearman_r):
        spearman_r, spearman_p = 0.0, 1.0

    return StakeCorrelationResult(
        pearson_r=float(pearson_r),
        pearson_p=float(pearson_p),
        spearman_r=float(spearman_r),
        spearman_p=float(spearman_p),
        is_significant=pearson_p < 0.05 or spearman_p < 0.05,
        n_samples=len(numbers),
        n_draws=len(records),
    )


def classify_numbers_by_stake(
    records: list[StakeDrawRecord],
    threshold_std: float = 1.0,
) -> list[NumberStakeClassification]:
    """Classify numbers as low_stake, neutral, or high_stake based on correlation.

    low_stake numbers: below median - 1*std (appear more in low-stake draws)
    high_stake numbers: above median + 1*std (appear more in high-stake draws)

    Args:
        records: List of StakeDrawRecord objects
        threshold_std: Number of standard deviations for classification (default 1.0)

    Returns:
        List of NumberStakeClassification for all 70 numbers
    """
    stake_scores = calculate_number_stake_scores(records)

    # Extract avg_stakes for numbers with data
    values = [score[0] for score in stake_scores.values() if score[1] > 0]

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
        avg_stake, draw_count = stake_scores.get(num, (0.0, 0))

        if draw_count == 0:
            z_score = 0.0
            classification = "no_data"
        else:
            z_score = (avg_stake - median) / std
            if avg_stake < low_threshold:
                classification = "low_stake"
            elif avg_stake > high_threshold:
                classification = "high_stake"
            else:
                classification = "neutral"

        classifications.append(
            NumberStakeClassification(
                number=num,
                avg_stake=avg_stake,
                draw_count=draw_count,
                classification=classification,
                z_score=z_score,
            )
        )

    return classifications


def run_hyp012_analysis(
    stake_path: str | Path,
    classification_threshold: float = 1.0,
) -> StakeAnalysisSummary:
    """Run complete HYP-012 analysis.

    Args:
        stake_path: Path to stake data file
        classification_threshold: Std threshold for low/high classification

    Returns:
        StakeAnalysisSummary with correlation and classification results
    """
    # Load stake data
    records = load_stake_data(stake_path)

    if not records:
        logger.error(f"Failed to load stake data from {stake_path}")
        return StakeAnalysisSummary(
            correlation=StakeCorrelationResult(
                pearson_r=0.0,
                pearson_p=1.0,
                spearman_r=0.0,
                spearman_p=1.0,
                is_significant=False,
                n_samples=0,
                n_draws=0,
            ),
        )

    # Run main stake correlation analysis
    correlation = analyze_stake_correlation(records)

    # Run additional correlations
    auszahlung_corr = analyze_auszahlung_correlation(records)
    restbetrag_corr = analyze_restbetrag_correlation(records)

    # Classify numbers
    classifications = classify_numbers_by_stake(records, classification_threshold)

    low_stake_numbers = [c.number for c in classifications if c.classification == "low_stake"]
    high_stake_numbers = [c.number for c in classifications if c.classification == "high_stake"]
    neutral_numbers = [c.number for c in classifications if c.classification == "neutral"]

    # Calculate classification stats
    all_avg_stakes = [c.avg_stake for c in classifications if c.draw_count > 0]
    classification_stats = {
        "n_low_stake": len(low_stake_numbers),
        "n_high_stake": len(high_stake_numbers),
        "n_neutral": len(neutral_numbers),
        "mean_stake": float(np.mean(all_avg_stakes)) if all_avg_stakes else 0.0,
        "std_stake": float(np.std(all_avg_stakes)) if all_avg_stakes else 0.0,
        "median_stake": float(np.median(all_avg_stakes)) if all_avg_stakes else 0.0,
        "threshold_std": classification_threshold,
    }

    return StakeAnalysisSummary(
        correlation=correlation,
        low_stake_numbers=low_stake_numbers,
        high_stake_numbers=high_stake_numbers,
        classification_stats=classification_stats,
        auszahlung_correlation=auszahlung_corr,
        restbetrag_correlation=restbetrag_corr,
    )


@dataclass(frozen=True)
class HighStakePopularityResult:
    """Result of HOUSE-002 analysis: high-stake draws vs unpopular numbers.

    Attributes:
        spearman_r: Spearman correlation between stake and unpopular-number ratio
        spearman_p: P-value for Spearman correlation
        is_significant: True if p < 0.05
        supports_hypothesis: True if |r| > 0.15 and p < 0.05
        n_draws: Total number of draws analyzed
        n_high_stake: Number of draws in high-stake subset (top 25%)
        high_stake_threshold: Stake threshold for high-stake classification
        mean_unpopular_ratio_high: Mean unpopular ratio in high-stake draws
        mean_unpopular_ratio_low: Mean unpopular ratio in low-stake draws
    """

    spearman_r: float
    spearman_p: float
    is_significant: bool
    supports_hypothesis: bool
    n_draws: int
    n_high_stake: int
    high_stake_threshold: float
    mean_unpopular_ratio_high: float
    mean_unpopular_ratio_low: float


def analyze_high_stake_popularity_bias(
    stake_records: list[StakeDrawRecord],
    popularity_scores: dict[int, float] | None = None,
    high_stake_percentile: float = 0.75,
    correlation_threshold: float = 0.15,
) -> HighStakePopularityResult:
    """Analyze HOUSE-002: Do high-stake draws favor unpopular numbers?

    Tests the hypothesis that when stakes are high, the RNG favors numbers
    that are less popular (less frequently played by users).

    Strategy:
    1. Classify each draw as high-stake (top 25%) or low-stake
    2. For each draw, calculate unpopular-number ratio (numbers below median popularity)
    3. Compute Spearman correlation between stake and unpopular-ratio

    Args:
        stake_records: List of StakeDrawRecord objects with stake and numbers
        popularity_scores: Dict mapping number -> popularity (0-1). If None, uses
            heuristic based on birthday numbers and "schoene Zahlen".
        high_stake_percentile: Percentile threshold for high-stake classification
            (default 0.75 = top 25%)
        correlation_threshold: Minimum |r| to support hypothesis (default 0.15)

    Returns:
        HighStakePopularityResult with correlation analysis
    """
    if not stake_records:
        logger.warning("No stake records provided for HOUSE-002 analysis")
        return HighStakePopularityResult(
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            supports_hypothesis=False,
            n_draws=0,
            n_high_stake=0,
            high_stake_threshold=0.0,
            mean_unpopular_ratio_high=0.0,
            mean_unpopular_ratio_low=0.0,
        )

    if len(stake_records) < 20:
        logger.warning(f"Only {len(stake_records)} records, need >= 20 for analysis")
        return HighStakePopularityResult(
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            supports_hypothesis=False,
            n_draws=len(stake_records),
            n_high_stake=0,
            high_stake_threshold=0.0,
            mean_unpopular_ratio_high=0.0,
            mean_unpopular_ratio_low=0.0,
        )

    # Use heuristic popularity if not provided
    if popularity_scores is None:
        # Import here to avoid circular dependency
        from kenobase.analysis.popularity_correlation import (
            calculate_popularity_scores_heuristic,
        )
        popularity_scores = calculate_popularity_scores_heuristic(range(1, 71))

    # Calculate median popularity for threshold
    pop_values = list(popularity_scores.values())
    median_popularity = float(np.median(pop_values))

    # Identify unpopular numbers (below median)
    unpopular_numbers = {
        n for n, score in popularity_scores.items() if score < median_popularity
    }

    # Calculate stake threshold for high-stake classification
    all_stakes = [rec.spieleinsatz for rec in stake_records]
    high_stake_threshold = float(np.percentile(all_stakes, high_stake_percentile * 100))

    # For each draw, calculate unpopular-ratio and stake
    stakes = []
    unpopular_ratios = []
    high_stake_ratios = []
    low_stake_ratios = []

    for rec in stake_records:
        stake = rec.spieleinsatz
        n_unpopular = sum(1 for n in rec.numbers if n in unpopular_numbers)
        unpopular_ratio = n_unpopular / len(rec.numbers) if rec.numbers else 0.0

        stakes.append(stake)
        unpopular_ratios.append(unpopular_ratio)

        if stake >= high_stake_threshold:
            high_stake_ratios.append(unpopular_ratio)
        else:
            low_stake_ratios.append(unpopular_ratio)

    # Calculate Spearman correlation
    if len(set(stakes)) < 2 or len(set(unpopular_ratios)) < 2:
        logger.warning("Constant values detected, correlation undefined")
        return HighStakePopularityResult(
            spearman_r=0.0,
            spearman_p=1.0,
            is_significant=False,
            supports_hypothesis=False,
            n_draws=len(stake_records),
            n_high_stake=len(high_stake_ratios),
            high_stake_threshold=high_stake_threshold,
            mean_unpopular_ratio_high=float(np.mean(high_stake_ratios))
            if high_stake_ratios
            else 0.0,
            mean_unpopular_ratio_low=float(np.mean(low_stake_ratios))
            if low_stake_ratios
            else 0.0,
        )

    spearman_r, spearman_p = stats.spearmanr(stakes, unpopular_ratios)

    # Handle NaN
    if np.isnan(spearman_r) or np.isnan(spearman_p):
        spearman_r, spearman_p = 0.0, 1.0

    is_significant = spearman_p < 0.05
    supports_hypothesis = abs(spearman_r) > correlation_threshold and is_significant

    mean_unpopular_high = (
        float(np.mean(high_stake_ratios)) if high_stake_ratios else 0.0
    )
    mean_unpopular_low = float(np.mean(low_stake_ratios)) if low_stake_ratios else 0.0

    logger.info(
        f"HOUSE-002: r={spearman_r:.4f}, p={spearman_p:.4f}, "
        f"high-stake ratio={mean_unpopular_high:.3f}, low-stake ratio={mean_unpopular_low:.3f}"
    )

    return HighStakePopularityResult(
        spearman_r=float(spearman_r),
        spearman_p=float(spearman_p),
        is_significant=is_significant,
        supports_hypothesis=supports_hypothesis,
        n_draws=len(stake_records),
        n_high_stake=len(high_stake_ratios),
        high_stake_threshold=high_stake_threshold,
        mean_unpopular_ratio_high=mean_unpopular_high,
        mean_unpopular_ratio_low=mean_unpopular_low,
    )


__all__ = [
    "StakeCorrelationResult",
    "NumberStakeClassification",
    "StakeAnalysisSummary",
    "StakeDrawRecord",
    "HighStakePopularityResult",
    "load_stake_data",
    "aggregate_stake_by_date",
    "calculate_number_stake_scores",
    "calculate_draw_frequency_from_records",
    "analyze_stake_correlation",
    "analyze_auszahlung_correlation",
    "analyze_restbetrag_correlation",
    "classify_numbers_by_stake",
    "run_hyp012_analysis",
    "analyze_high_stake_popularity_bias",
]
