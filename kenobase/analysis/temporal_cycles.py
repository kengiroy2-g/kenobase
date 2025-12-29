#!/usr/bin/env python3
"""Temporal Cycles Analysis for HYP-011.

Analyzes temporal patterns in KENO draw numbers across multiple time dimensions:
- Weekday cycles (0=Monday to 6=Sunday)
- Month cycles (1-12)
- Year-over-year patterns
- Holiday proximity effects

Uses Chi-square tests to detect deviations from uniform distribution.

Usage:
    from kenobase.analysis.temporal_cycles import analyze_temporal_cycles
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np
from scipy import stats

# German public holidays (fixed dates)
GERMAN_HOLIDAYS = [
    (1, 1),    # Neujahr
    (5, 1),    # Tag der Arbeit
    (10, 3),   # Tag der Deutschen Einheit
    (12, 25),  # 1. Weihnachtsfeiertag
    (12, 26),  # 2. Weihnachtsfeiertag
]

# KENO-specific: draws happen daily
WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONTHS_DE = ["Januar", "Februar", "Maerz", "April", "Mai", "Juni",
             "Juli", "August", "September", "Oktober", "November", "Dezember"]


@dataclass
class TemporalDimensionResult:
    """Result for a single temporal dimension (weekday, month, etc.)."""

    dimension: str
    n_draws: int
    observed_counts: list[int]
    expected_counts: list[float]
    labels: list[str]
    chi2_statistic: float
    p_value: float
    degrees_of_freedom: int
    is_significant: bool  # p < 0.05
    interpretation: str
    most_common: str
    least_common: str


@dataclass
class NumberTemporalResult:
    """Temporal analysis for a specific number."""

    number: int
    weekday_result: TemporalDimensionResult
    month_result: TemporalDimensionResult
    is_weekday_biased: bool
    is_month_biased: bool


@dataclass
class TemporalCyclesResult:
    """Complete temporal cycles analysis result for HYP-011."""

    hypothesis_id: str = "HYP-011"
    n_draws: int = 0
    date_range_start: str = ""
    date_range_end: str = ""

    # Global temporal patterns (all numbers combined)
    weekday_analysis: TemporalDimensionResult | None = None
    month_analysis: TemporalDimensionResult | None = None
    year_analysis: TemporalDimensionResult | None = None
    holiday_analysis: dict[str, Any] = field(default_factory=dict)

    # Per-number temporal patterns (optional, for top deviations)
    number_analyses: list[NumberTemporalResult] = field(default_factory=list)

    # Summary
    significant_weekday_numbers: list[int] = field(default_factory=list)
    significant_month_numbers: list[int] = field(default_factory=list)

    # HYP-011 verdict
    verdict: str = ""
    confidence: float = 0.0


def analyze_dimension(
    dates: list[datetime],
    dimension: str,
    alpha: float = 0.05,
) -> TemporalDimensionResult:
    """Analyze a single temporal dimension.

    Args:
        dates: List of draw dates
        dimension: One of "weekday", "month", "year"
        alpha: Significance level (default 0.05)

    Returns:
        TemporalDimensionResult with Chi-square test results
    """
    n = len(dates)
    if n < 10:
        return TemporalDimensionResult(
            dimension=dimension,
            n_draws=n,
            observed_counts=[],
            expected_counts=[],
            labels=[],
            chi2_statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=0,
            is_significant=False,
            interpretation="Insufficient data (< 10 draws)",
            most_common="N/A",
            least_common="N/A",
        )

    if dimension == "weekday":
        values = [d.weekday() for d in dates]
        n_categories = 7
        labels = WEEKDAYS_DE
    elif dimension == "month":
        values = [d.month - 1 for d in dates]  # 0-indexed
        n_categories = 12
        labels = MONTHS_DE
    elif dimension == "year":
        years = sorted(set(d.year for d in dates))
        year_to_idx = {y: i for i, y in enumerate(years)}
        values = [year_to_idx[d.year] for d in dates]
        n_categories = len(years)
        labels = [str(y) for y in years]
    else:
        raise ValueError(f"Unknown dimension: {dimension}")

    # Count occurrences
    observed = [0] * n_categories
    for v in values:
        observed[v] += 1

    # Expected uniform distribution
    expected = [n / n_categories] * n_categories

    # Chi-square test
    # Filter out zero-expected categories (for year analysis with few years)
    valid_indices = [i for i in range(n_categories) if expected[i] >= 5]
    if len(valid_indices) < 2:
        return TemporalDimensionResult(
            dimension=dimension,
            n_draws=n,
            observed_counts=observed,
            expected_counts=expected,
            labels=labels,
            chi2_statistic=0.0,
            p_value=1.0,
            degrees_of_freedom=0,
            is_significant=False,
            interpretation="Insufficient expected counts for Chi-square test",
            most_common=labels[np.argmax(observed)],
            least_common=labels[np.argmin(observed)],
        )

    obs_valid = [observed[i] for i in valid_indices]
    exp_valid = [expected[i] for i in valid_indices]
    labels_valid = [labels[i] for i in valid_indices]

    chi2, p_value = stats.chisquare(obs_valid, exp_valid)
    df = len(obs_valid) - 1

    is_significant = p_value < alpha

    # Interpretation
    most_common_idx = np.argmax(obs_valid)
    least_common_idx = np.argmin(obs_valid)
    most_common = labels_valid[most_common_idx]
    least_common = labels_valid[least_common_idx]

    if is_significant:
        interpretation = (
            f"Signifikante Abweichung von Gleichverteilung (p={p_value:.4f}). "
            f"Haeufigster: {most_common} ({obs_valid[most_common_idx]}), "
            f"Seltenster: {least_common} ({obs_valid[least_common_idx]})"
        )
    else:
        interpretation = (
            f"Keine signifikante Abweichung von Gleichverteilung (p={p_value:.4f}). "
            f"Ziehungen sind gleichmaessig verteilt."
        )

    return TemporalDimensionResult(
        dimension=dimension,
        n_draws=n,
        observed_counts=observed,
        expected_counts=expected,
        labels=labels,
        chi2_statistic=float(chi2),
        p_value=float(p_value),
        degrees_of_freedom=df,
        is_significant=is_significant,
        interpretation=interpretation,
        most_common=most_common,
        least_common=least_common,
    )


def analyze_holiday_proximity(
    dates: list[datetime],
    window_days: int = 3,
) -> dict[str, Any]:
    """Analyze draw frequency around German holidays.

    Args:
        dates: List of draw dates
        window_days: Days before/after holiday to consider "near"

    Returns:
        Dict with holiday proximity analysis
    """
    n = len(dates)
    if n < 30:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "Need at least 30 draws for holiday analysis",
        }

    near_holiday_count = 0
    for d in dates:
        for h_month, h_day in GERMAN_HOLIDAYS:
            try:
                holiday = datetime(d.year, h_month, h_day)
                if abs((d - holiday).days) <= window_days:
                    near_holiday_count += 1
                    break
            except ValueError:
                continue

    # Expected rate: 5 holidays * (2*window+1) days / 365
    expected_rate = (len(GERMAN_HOLIDAYS) * (2 * window_days + 1)) / 365
    observed_rate = near_holiday_count / n

    # Binomial test
    # Under null: each draw has expected_rate probability of being near holiday
    # Using normal approximation for large n
    expected_count = n * expected_rate
    std_expected = np.sqrt(n * expected_rate * (1 - expected_rate))

    if std_expected > 0:
        z_score = (near_holiday_count - expected_count) / std_expected
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # two-tailed
    else:
        z_score = 0.0
        p_value = 1.0

    is_significant = p_value < 0.05

    return {
        "window_days": window_days,
        "n_draws": n,
        "near_holiday_count": near_holiday_count,
        "observed_rate": float(observed_rate),
        "expected_rate": float(expected_rate),
        "expected_count": float(expected_count),
        "z_score": float(z_score),
        "p_value": float(p_value),
        "is_significant": is_significant,
        "interpretation": (
            f"{'Signifikante' if is_significant else 'Keine signifikante'} Abweichung "
            f"bei Feiertags-Naehe (beobachtet: {observed_rate:.1%}, erwartet: {expected_rate:.1%})"
        ),
    }


def analyze_number_temporal(
    number: int,
    dates: list[datetime],
    numbers_per_draw: list[list[int]],
    alpha: float = 0.05,
) -> NumberTemporalResult:
    """Analyze temporal patterns for a specific number.

    Args:
        number: The KENO number to analyze (1-70)
        dates: List of draw dates
        numbers_per_draw: List of drawn numbers for each date
        alpha: Significance level

    Returns:
        NumberTemporalResult with weekday/month patterns
    """
    # Filter to dates where this number appeared
    appeared_dates = [
        d for d, nums in zip(dates, numbers_per_draw)
        if number in nums
    ]

    weekday_result = analyze_dimension(appeared_dates, "weekday", alpha)
    month_result = analyze_dimension(appeared_dates, "month", alpha)

    return NumberTemporalResult(
        number=number,
        weekday_result=weekday_result,
        month_result=month_result,
        is_weekday_biased=weekday_result.is_significant,
        is_month_biased=month_result.is_significant,
    )


def analyze_temporal_cycles(
    dates: list[datetime],
    numbers_per_draw: list[list[int]] | None = None,
    analyze_per_number: bool = False,
    numbers_to_analyze: list[int] | None = None,
    alpha: float = 0.05,
) -> TemporalCyclesResult:
    """Main function: analyze temporal cycles in KENO draws (HYP-011).

    Args:
        dates: List of draw dates (must be sorted ascending)
        numbers_per_draw: Optional list of drawn numbers for per-number analysis
        analyze_per_number: If True, analyze each number's temporal patterns
        numbers_to_analyze: Specific numbers to analyze (default: 1-70)
        alpha: Significance level for Chi-square tests

    Returns:
        TemporalCyclesResult with complete analysis
    """
    if not dates:
        return TemporalCyclesResult(
            verdict="INSUFFICIENT_DATA",
            confidence=0.0,
        )

    n = len(dates)
    dates_sorted = sorted(dates)

    result = TemporalCyclesResult(
        n_draws=n,
        date_range_start=dates_sorted[0].strftime("%d.%m.%Y"),
        date_range_end=dates_sorted[-1].strftime("%d.%m.%Y"),
    )

    # Global temporal analyses
    result.weekday_analysis = analyze_dimension(dates, "weekday", alpha)
    result.month_analysis = analyze_dimension(dates, "month", alpha)
    result.year_analysis = analyze_dimension(dates, "year", alpha)
    result.holiday_analysis = analyze_holiday_proximity(dates)

    # Per-number analysis (if requested)
    if analyze_per_number and numbers_per_draw is not None:
        numbers = numbers_to_analyze or list(range(1, 71))
        significant_weekday = []
        significant_month = []

        for num in numbers:
            num_result = analyze_number_temporal(num, dates, numbers_per_draw, alpha)
            result.number_analyses.append(num_result)

            if num_result.is_weekday_biased:
                significant_weekday.append(num)
            if num_result.is_month_biased:
                significant_month.append(num)

        result.significant_weekday_numbers = significant_weekday
        result.significant_month_numbers = significant_month

    # HYP-011 Verdict
    # Count significant findings
    sig_count = 0
    if result.weekday_analysis and result.weekday_analysis.is_significant:
        sig_count += 1
    if result.month_analysis and result.month_analysis.is_significant:
        sig_count += 1
    if result.year_analysis and result.year_analysis.is_significant:
        sig_count += 1
    if result.holiday_analysis.get("is_significant", False):
        sig_count += 1

    # Additional: per-number significance
    n_weekday_biased = len(result.significant_weekday_numbers)
    n_month_biased = len(result.significant_month_numbers)

    # Expected false positives at alpha=0.05: ~5% of 70 = 3.5
    expected_fp = 0.05 * 70

    if sig_count == 0 and n_weekday_biased <= expected_fp and n_month_biased <= expected_fp:
        result.verdict = "NICHT_BESTAETIGT"
        result.confidence = 0.95
    elif sig_count >= 2 or n_weekday_biased > 2 * expected_fp or n_month_biased > 2 * expected_fp:
        result.verdict = "BESTAETIGT"
        result.confidence = 0.8
    else:
        result.verdict = "UNKLAR"
        result.confidence = 0.5

    return result


def to_dict(result: TemporalCyclesResult) -> dict[str, Any]:
    """Convert TemporalCyclesResult to JSON-serializable dict."""

    def to_native(val: Any) -> Any:
        """Convert numpy types to native Python types."""
        if isinstance(val, (np.bool_, np.integer)):
            return int(val) if isinstance(val, np.integer) else bool(val)
        if isinstance(val, np.floating):
            return float(val)
        return val

    def dim_to_dict(dim: TemporalDimensionResult | None) -> dict[str, Any] | None:
        if dim is None:
            return None
        return {
            "dimension": dim.dimension,
            "n_draws": dim.n_draws,
            "observed_counts": dict(zip(dim.labels, dim.observed_counts)),
            "expected_per_category": dim.expected_counts[0] if dim.expected_counts else 0,
            "chi2_statistic": to_native(dim.chi2_statistic),
            "p_value": to_native(dim.p_value),
            "degrees_of_freedom": dim.degrees_of_freedom,
            "is_significant": to_native(dim.is_significant),
            "interpretation": dim.interpretation,
            "most_common": dim.most_common,
            "least_common": dim.least_common,
        }

    # Convert holiday_analysis values to native types
    holiday_dict = {}
    for k, v in result.holiday_analysis.items():
        holiday_dict[k] = to_native(v)

    output = {
        "hypothesis_id": result.hypothesis_id,
        "n_draws": result.n_draws,
        "date_range": {
            "start": result.date_range_start,
            "end": result.date_range_end,
        },
        "weekday_analysis": dim_to_dict(result.weekday_analysis),
        "month_analysis": dim_to_dict(result.month_analysis),
        "year_analysis": dim_to_dict(result.year_analysis),
        "holiday_analysis": holiday_dict,
        "verdict": result.verdict,
        "confidence": result.confidence,
    }

    # Add per-number summary if available
    if result.number_analyses:
        output["per_number_summary"] = {
            "n_weekday_biased": len(result.significant_weekday_numbers),
            "n_month_biased": len(result.significant_month_numbers),
            "weekday_biased_numbers": result.significant_weekday_numbers,
            "month_biased_numbers": result.significant_month_numbers,
            "expected_false_positives": 0.05 * 70,
        }

    return output


__all__ = [
    "TemporalCyclesResult",
    "TemporalDimensionResult",
    "NumberTemporalResult",
    "analyze_temporal_cycles",
    "analyze_dimension",
    "analyze_holiday_proximity",
    "analyze_number_temporal",
    "to_dict",
    "GERMAN_HOLIDAYS",
    "WEEKDAYS_DE",
    "MONTHS_DE",
]
