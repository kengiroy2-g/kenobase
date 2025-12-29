"""Jackpot-Correlation Analysis for HYP-015.

This module tests the hypothesis that jackpot height (proxied by GK1 events)
correlates with drawn number types - identifying if "birthday" numbers (1-31)
or "high" numbers (32-70) are drawn more often during jackpot events.

Hypothesis: Significant correlation (|r| > 0.2, p < 0.05, Chi-Quadrat p < 0.05)
between jackpot events and number type distribution indicates non-random patterns.

Number Types:
- Birthday: 1-31 (dates that can appear as day of month)
- High: 32-70 (numbers outside birthday range)
- Even/Odd distribution
- Decade distribution (0-9, 10-19, ..., 60-70)

Usage:
    from kenobase.analysis.jackpot_correlation import (
        JackpotCorrelationResult,
        NumberTypeStats,
        load_gk1_events,
        analyze_jackpot_correlation,
        run_hyp015_analysis,
    )

    # Load and analyze
    gk1_events = load_gk1_events("Keno_GPTs/10-9_KGDaten_gefiltert.csv")
    result = run_hyp015_analysis(draws, gk1_events)
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)

# Number type boundaries
BIRTHDAY_MIN = 1
BIRTHDAY_MAX = 31
HIGH_MIN = 32
HIGH_MAX = 70

# Decades for KENO (0-9, 10-19, ..., 60-70)
DECADES = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 70)]


@dataclass(frozen=True)
class NumberTypeStats:
    """Statistics for a single number type category.

    Attributes:
        category: Category name (birthday, high, even, odd, decade_X)
        jackpot_ratio: Ratio of this type in jackpot draws
        normal_ratio: Ratio of this type in normal draws
        difference: jackpot_ratio - normal_ratio
        z_score: Z-score of the difference
    """

    category: str
    jackpot_ratio: float
    normal_ratio: float
    difference: float
    z_score: float


@dataclass(frozen=True)
class JackpotCorrelationResult:
    """Result of jackpot-number type correlation analysis.

    Attributes:
        pearson_r: Pearson correlation coefficient (birthday ratio vs jackpot indicator)
        pearson_p: Pearson p-value
        spearman_r: Spearman correlation coefficient
        spearman_p: Spearman p-value
        chi_square_stat: Chi-square statistic for birthday/high distribution
        chi_square_p: Chi-square p-value
        chi_square_dof: Degrees of freedom
        is_significant: True if any test shows significance (p < 0.05)
        n_jackpot_draws: Number of draws on jackpot days
        n_normal_draws: Number of normal draws
        n_total_draws: Total draws analyzed
    """

    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float
    chi_square_stat: float
    chi_square_p: float
    chi_square_dof: int
    is_significant: bool
    n_jackpot_draws: int
    n_normal_draws: int
    n_total_draws: int


@dataclass
class JackpotAnalysisSummary:
    """Complete summary of HYP-015 analysis.

    Attributes:
        correlation: Main correlation result
        number_type_stats: Statistics per number type category
        jackpot_dates: List of jackpot event dates
        birthday_numbers: List of birthday numbers (1-31)
        high_numbers: List of high numbers (32-70)
        metadata: Additional analysis metadata
    """

    correlation: JackpotCorrelationResult
    number_type_stats: list[NumberTypeStats] = field(default_factory=list)
    jackpot_dates: list[datetime] = field(default_factory=list)
    birthday_numbers: list[int] = field(default_factory=list)
    high_numbers: list[int] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class GK1Event:
    """A Gewinnklasse 1 (jackpot) event.

    Attributes:
        datum: Date of the jackpot event
        keno_typ: Keno type (9 or 10)
        anzahl_gewinner: Number of winners
        vergangene_tage: Days since last GK1 event
    """

    datum: datetime
    keno_typ: int
    anzahl_gewinner: int
    vergangene_tage: int


def load_gk1_events(
    path: str | Path,
    encoding: str = "utf-8",
) -> list[GK1Event]:
    """Load GK1 events from 10-9_KGDaten_gefiltert.csv.

    The GK1 data contains jackpot events (when Keno-Typ 9 or 10 had winners).
    Fewer winners typically indicates a higher jackpot was won.

    Format: Datum,Keno-Typ,Anzahl der Gewinner,Vergangene Tage seit dem letzten Gewinnklasse 1

    Args:
        path: Path to GK1 CSV file
        encoding: File encoding (default utf-8)

    Returns:
        List of GK1Event objects

    Raises:
        FileNotFoundError: If file does not exist
    """
    import csv

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"GK1 file not found: {file_path}")

    events: list[GK1Event] = []

    with open(file_path, "r", encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter=",")

        for row_num, row in enumerate(reader, start=2):
            try:
                # Clean whitespace
                row = {k.strip(): v.strip() if v else "" for k, v in row.items() if k}

                date_str = row.get("Datum", "")
                if not date_str:
                    continue

                datum = datetime.strptime(date_str, "%d.%m.%Y")
                keno_typ = int(row.get("Keno-Typ", "0"))
                anzahl_gewinner = int(float(row.get("Anzahl der Gewinner", "0")))
                vergangene_tage = int(
                    float(
                        row.get("Vergangene Tage seit dem letzten Gewinnklasse 1", "0")
                    )
                )

                events.append(
                    GK1Event(
                        datum=datum,
                        keno_typ=keno_typ,
                        anzahl_gewinner=anzahl_gewinner,
                        vergangene_tage=vergangene_tage,
                    )
                )

            except (ValueError, KeyError) as e:
                logger.debug(f"Row {row_num}: Parse error - {e}")
                continue

    logger.info(f"Loaded {len(events)} GK1 events from {file_path.name}")
    return events


def get_jackpot_dates(gk1_events: list[GK1Event]) -> set[datetime]:
    """Extract unique jackpot dates from GK1 events.

    Args:
        gk1_events: List of GK1Event objects

    Returns:
        Set of datetime objects (normalized to midnight)
    """
    return {
        event.datum.replace(hour=0, minute=0, second=0, microsecond=0)
        for event in gk1_events
    }


def classify_number_type(number: int) -> dict[str, bool]:
    """Classify a number into various type categories.

    Args:
        number: KENO number (1-70)

    Returns:
        Dict with boolean flags for each category
    """
    return {
        "birthday": BIRTHDAY_MIN <= number <= BIRTHDAY_MAX,
        "high": HIGH_MIN <= number <= HIGH_MAX,
        "even": number % 2 == 0,
        "odd": number % 2 == 1,
    }


def get_decade(number: int) -> int:
    """Get the decade index for a number.

    Args:
        number: KENO number (1-70)

    Returns:
        Decade index (0-6)
    """
    if number <= 9:
        return 0
    elif number <= 19:
        return 1
    elif number <= 29:
        return 2
    elif number <= 39:
        return 3
    elif number <= 49:
        return 4
    elif number <= 59:
        return 5
    else:
        return 6


def calculate_type_ratios(
    draws: list["DrawResult"],
) -> dict[str, float]:
    """Calculate number type ratios for a set of draws.

    Args:
        draws: List of DrawResult objects

    Returns:
        Dict mapping category -> ratio (0.0 - 1.0)
    """
    if not draws:
        return {}

    total_numbers = 0
    type_counts: dict[str, int] = defaultdict(int)

    for draw in draws:
        for num in draw.numbers:
            total_numbers += 1
            classification = classify_number_type(num)

            for category, is_type in classification.items():
                if is_type:
                    type_counts[category] += 1

            # Count decade
            decade = get_decade(num)
            type_counts[f"decade_{decade}"] += 1

    if total_numbers == 0:
        return {}

    return {category: count / total_numbers for category, count in type_counts.items()}


def calculate_draw_type_features(
    draws: list["DrawResult"],
    jackpot_dates: set[datetime],
) -> tuple[list[float], list[int]]:
    """Calculate birthday ratio and jackpot indicator per draw.

    Args:
        draws: List of DrawResult objects
        jackpot_dates: Set of jackpot dates

    Returns:
        Tuple of (birthday_ratios, jackpot_indicators)
        - birthday_ratios: List of birthday number ratios per draw
        - jackpot_indicators: List of 0/1 for normal/jackpot draw
    """
    birthday_ratios = []
    jackpot_indicators = []

    for draw in draws:
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Calculate birthday ratio for this draw
        birthday_count = sum(
            1 for n in draw.numbers if BIRTHDAY_MIN <= n <= BIRTHDAY_MAX
        )
        birthday_ratio = birthday_count / len(draw.numbers) if draw.numbers else 0.0

        birthday_ratios.append(birthday_ratio)
        jackpot_indicators.append(1 if draw_date in jackpot_dates else 0)

    return birthday_ratios, jackpot_indicators


def chi_square_test(
    jackpot_draws: list["DrawResult"],
    normal_draws: list["DrawResult"],
) -> tuple[float, float, int]:
    """Perform Chi-square test on birthday/high distribution.

    Tests if the distribution of birthday vs high numbers differs
    significantly between jackpot and normal draws.

    Args:
        jackpot_draws: Draws on jackpot days
        normal_draws: Draws on normal days

    Returns:
        Tuple of (chi_square_stat, p_value, degrees_of_freedom)
    """
    # Count birthday and high numbers
    jackpot_birthday = sum(
        1 for d in jackpot_draws for n in d.numbers if BIRTHDAY_MIN <= n <= BIRTHDAY_MAX
    )
    jackpot_high = sum(
        1 for d in jackpot_draws for n in d.numbers if HIGH_MIN <= n <= HIGH_MAX
    )
    normal_birthday = sum(
        1 for d in normal_draws for n in d.numbers if BIRTHDAY_MIN <= n <= BIRTHDAY_MAX
    )
    normal_high = sum(
        1 for d in normal_draws for n in d.numbers if HIGH_MIN <= n <= HIGH_MAX
    )

    # Create contingency table
    # Rows: jackpot, normal
    # Cols: birthday, high
    observed = np.array([[jackpot_birthday, jackpot_high], [normal_birthday, normal_high]])

    # Check for valid table (no zero row/column totals)
    if observed.sum() == 0:
        return 0.0, 1.0, 1

    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)

    if 0 in row_totals or 0 in col_totals:
        logger.warning("Chi-square test: zero marginals detected")
        return 0.0, 1.0, 1

    # Perform chi-square test
    chi2, p, dof, _ = stats.chi2_contingency(observed)

    return float(chi2), float(p), int(dof)


def analyze_jackpot_correlation(
    draws: list["DrawResult"],
    jackpot_dates: set[datetime],
) -> JackpotCorrelationResult:
    """Analyze correlation between jackpot events and number types.

    Tests HYP-015: Do drawn number types correlate with jackpot events?
    - Positive correlation: birthday numbers more common during jackpots
    - Negative correlation: high numbers more common during jackpots

    Args:
        draws: List of DrawResult objects
        jackpot_dates: Set of jackpot dates

    Returns:
        JackpotCorrelationResult with Pearson, Spearman, and Chi-square results
    """
    if not draws or not jackpot_dates:
        logger.warning("No draws or jackpot dates provided")
        return JackpotCorrelationResult(
            pearson_r=0.0,
            pearson_p=1.0,
            spearman_r=0.0,
            spearman_p=1.0,
            chi_square_stat=0.0,
            chi_square_p=1.0,
            chi_square_dof=1,
            is_significant=False,
            n_jackpot_draws=0,
            n_normal_draws=0,
            n_total_draws=0,
        )

    # Split draws into jackpot and normal
    jackpot_draws = []
    normal_draws = []

    for draw in draws:
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)
        if draw_date in jackpot_dates:
            jackpot_draws.append(draw)
        else:
            normal_draws.append(draw)

    n_jackpot = len(jackpot_draws)
    n_normal = len(normal_draws)
    n_total = len(draws)

    logger.info(f"Analyzing {n_jackpot} jackpot draws, {n_normal} normal draws")

    if n_jackpot < 5:
        logger.warning(f"Only {n_jackpot} jackpot draws - results may be unreliable")

    # Calculate per-draw features for correlation
    birthday_ratios, jackpot_indicators = calculate_draw_type_features(
        draws, jackpot_dates
    )

    # Pearson and Spearman correlation
    if len(set(jackpot_indicators)) < 2:
        # All draws are same type (all jackpot or all normal)
        pearson_r, pearson_p = 0.0, 1.0
        spearman_r, spearman_p = 0.0, 1.0
    else:
        pearson_r, pearson_p = stats.pearsonr(birthday_ratios, jackpot_indicators)
        spearman_r, spearman_p = stats.spearmanr(birthday_ratios, jackpot_indicators)

    # Handle NaN
    if np.isnan(pearson_r):
        pearson_r, pearson_p = 0.0, 1.0
    if np.isnan(spearman_r):
        spearman_r, spearman_p = 0.0, 1.0

    # Chi-square test
    chi2_stat, chi2_p, chi2_dof = chi_square_test(jackpot_draws, normal_draws)

    # Determine significance
    is_significant = (
        (abs(pearson_r) > 0.2 and pearson_p < 0.05)
        or (abs(spearman_r) > 0.2 and spearman_p < 0.05)
        or chi2_p < 0.05
    )

    return JackpotCorrelationResult(
        pearson_r=float(pearson_r),
        pearson_p=float(pearson_p),
        spearman_r=float(spearman_r),
        spearman_p=float(spearman_p),
        chi_square_stat=chi2_stat,
        chi_square_p=chi2_p,
        chi_square_dof=chi2_dof,
        is_significant=is_significant,
        n_jackpot_draws=n_jackpot,
        n_normal_draws=n_normal,
        n_total_draws=n_total,
    )


def calculate_number_type_stats(
    jackpot_draws: list["DrawResult"],
    normal_draws: list["DrawResult"],
) -> list[NumberTypeStats]:
    """Calculate detailed statistics for each number type category.

    Args:
        jackpot_draws: Draws on jackpot days
        normal_draws: Draws on normal days

    Returns:
        List of NumberTypeStats for each category
    """
    jackpot_ratios = calculate_type_ratios(jackpot_draws)
    normal_ratios = calculate_type_ratios(normal_draws)

    # Get all categories
    all_categories = set(jackpot_ratios.keys()) | set(normal_ratios.keys())

    stats_list = []
    for category in sorted(all_categories):
        jp_ratio = jackpot_ratios.get(category, 0.0)
        nm_ratio = normal_ratios.get(category, 0.0)
        diff = jp_ratio - nm_ratio

        # Calculate Z-score (assuming binomial standard error)
        n_jp = len(jackpot_draws) * 20  # 20 numbers per KENO draw
        n_nm = len(normal_draws) * 20

        if n_jp > 0 and n_nm > 0:
            pooled_ratio = (jp_ratio * n_jp + nm_ratio * n_nm) / (n_jp + n_nm)
            if pooled_ratio > 0 and pooled_ratio < 1:
                se = np.sqrt(
                    pooled_ratio * (1 - pooled_ratio) * (1 / n_jp + 1 / n_nm)
                )
                z_score = diff / se if se > 0 else 0.0
            else:
                z_score = 0.0
        else:
            z_score = 0.0

        stats_list.append(
            NumberTypeStats(
                category=category,
                jackpot_ratio=jp_ratio,
                normal_ratio=nm_ratio,
                difference=diff,
                z_score=float(z_score),
            )
        )

    return stats_list


def run_hyp015_analysis(
    draws: list["DrawResult"],
    gk1_path: str | Path,
) -> JackpotAnalysisSummary:
    """Run complete HYP-015 jackpot correlation analysis.

    Args:
        draws: List of DrawResult objects
        gk1_path: Path to GK1 data file (10-9_KGDaten_gefiltert.csv)

    Returns:
        JackpotAnalysisSummary with correlation and statistics
    """
    # Load GK1 events
    gk1_events = load_gk1_events(gk1_path)

    if not gk1_events:
        logger.error(f"Failed to load GK1 data from {gk1_path}")
        return JackpotAnalysisSummary(
            correlation=JackpotCorrelationResult(
                pearson_r=0.0,
                pearson_p=1.0,
                spearman_r=0.0,
                spearman_p=1.0,
                chi_square_stat=0.0,
                chi_square_p=1.0,
                chi_square_dof=1,
                is_significant=False,
                n_jackpot_draws=0,
                n_normal_draws=0,
                n_total_draws=0,
            ),
        )

    # Get jackpot dates
    jackpot_dates = get_jackpot_dates(gk1_events)

    # Find date range overlap
    if draws:
        draw_dates = [d.date for d in draws]
        min_draw = min(draw_dates)
        max_draw = max(draw_dates)
        min_jp = min(jackpot_dates)
        max_jp = max(jackpot_dates)

        overlap_start = max(min_draw, min_jp)
        overlap_end = min(max_draw, max_jp)

        # Filter draws to overlap period
        filtered_draws = [
            d
            for d in draws
            if overlap_start
            <= d.date.replace(hour=0, minute=0, second=0, microsecond=0)
            <= overlap_end
        ]
    else:
        filtered_draws = []

    logger.info(
        f"Overlap period contains {len(filtered_draws)} draws and {len(jackpot_dates)} jackpot dates"
    )

    # Run correlation analysis
    correlation = analyze_jackpot_correlation(filtered_draws, jackpot_dates)

    # Split draws for detailed stats
    jackpot_draws = []
    normal_draws = []
    for draw in filtered_draws:
        draw_date = draw.date.replace(hour=0, minute=0, second=0, microsecond=0)
        if draw_date in jackpot_dates:
            jackpot_draws.append(draw)
        else:
            normal_draws.append(draw)

    # Calculate number type statistics
    type_stats = calculate_number_type_stats(jackpot_draws, normal_draws)

    # Build metadata
    metadata = {
        "gk1_source": str(gk1_path),
        "n_gk1_events": len(gk1_events),
        "keno_typ_distribution": {},
        "avg_vergangene_tage": 0.0,
    }

    if gk1_events:
        keno_typ_counts: dict[int, int] = defaultdict(int)
        for event in gk1_events:
            keno_typ_counts[event.keno_typ] += 1
        metadata["keno_typ_distribution"] = dict(keno_typ_counts)
        metadata["avg_vergangene_tage"] = float(
            np.mean([e.vergangene_tage for e in gk1_events])
        )

    return JackpotAnalysisSummary(
        correlation=correlation,
        number_type_stats=type_stats,
        jackpot_dates=sorted(jackpot_dates),
        birthday_numbers=list(range(BIRTHDAY_MIN, BIRTHDAY_MAX + 1)),
        high_numbers=list(range(HIGH_MIN, HIGH_MAX + 1)),
        metadata=metadata,
    )


def export_result_to_json(
    result: JackpotAnalysisSummary,
    output_path: str | Path,
) -> None:
    """Export analysis result to JSON file.

    Args:
        result: JackpotAnalysisSummary to export
        output_path: Path for output JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "hypothesis": "HYP-015",
        "description": "Jackpot-Hoehe vs. Zahlentyp Korrelation",
        "correlation": {
            "pearson_r": result.correlation.pearson_r,
            "pearson_p": result.correlation.pearson_p,
            "spearman_r": result.correlation.spearman_r,
            "spearman_p": result.correlation.spearman_p,
            "chi_square_stat": result.correlation.chi_square_stat,
            "chi_square_p": result.correlation.chi_square_p,
            "chi_square_dof": result.correlation.chi_square_dof,
            "is_significant": result.correlation.is_significant,
            "n_jackpot_draws": result.correlation.n_jackpot_draws,
            "n_normal_draws": result.correlation.n_normal_draws,
            "n_total_draws": result.correlation.n_total_draws,
        },
        "number_type_stats": [
            {
                "category": s.category,
                "jackpot_ratio": s.jackpot_ratio,
                "normal_ratio": s.normal_ratio,
                "difference": s.difference,
                "z_score": s.z_score,
            }
            for s in result.number_type_stats
        ],
        "jackpot_dates": [d.isoformat() for d in result.jackpot_dates],
        "birthday_numbers": result.birthday_numbers,
        "high_numbers": result.high_numbers,
        "metadata": result.metadata,
        "acceptance_criteria": {
            "pearson_r_threshold": 0.2,
            "p_value_threshold": 0.05,
            "pearson_r_met": abs(result.correlation.pearson_r) > 0.2,
            "pearson_p_met": result.correlation.pearson_p < 0.05,
            "chi_square_p_met": result.correlation.chi_square_p < 0.05,
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Exported result to {output_path}")


__all__ = [
    "GK1Event",
    "NumberTypeStats",
    "JackpotCorrelationResult",
    "JackpotAnalysisSummary",
    "BIRTHDAY_MIN",
    "BIRTHDAY_MAX",
    "HIGH_MIN",
    "HIGH_MAX",
    "DECADES",
    "load_gk1_events",
    "get_jackpot_dates",
    "classify_number_type",
    "get_decade",
    "calculate_type_ratios",
    "calculate_draw_type_features",
    "chi_square_test",
    "analyze_jackpot_correlation",
    "calculate_number_type_stats",
    "run_hyp015_analysis",
    "export_result_to_json",
]
