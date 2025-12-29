#!/usr/bin/env python3
"""Calendar feature extraction for HYP-002 Jackpot-Zyklen analysis.

Extracts calendar-based features from GK1 events:
- Weekday distribution (0=Monday, 6=Sunday)
- Month distribution
- Holiday proximity (German holidays)
- Payday proximity (end of month)

Usage:
    from kenobase.analysis.calendar_features import extract_calendar_features
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
from scipy import stats

# German public holidays (fixed dates, approximate)
GERMAN_HOLIDAYS_FIXED = [
    (1, 1),    # Neujahr
    (5, 1),    # Tag der Arbeit
    (10, 3),   # Tag der Deutschen Einheit
    (12, 25),  # 1. Weihnachtsfeiertag
    (12, 26),  # 2. Weihnachtsfeiertag
]

# Payday window: 25th-31st of month
PAYDAY_START_DAY = 25


@dataclass
class CalendarFeatures:
    """Calendar features for a single date."""

    weekday: int  # 0=Monday, 6=Sunday
    month: int  # 1-12
    is_near_holiday: bool  # Within 3 days of fixed holiday
    is_payday_window: bool  # 25th-31st of month
    day_of_month: int


@dataclass
class CalendarAnalysisResult:
    """Result of calendar correlation analysis."""

    n_events: int
    weekday_counts: list[int]  # Length 7
    weekday_chi2: float
    weekday_p_value: float
    weekday_interpretation: str

    month_counts: list[int]  # Length 12
    month_chi2: float
    month_p_value: float
    month_interpretation: str

    holiday_proximity_rate: float
    payday_window_rate: float

    # Expected rates for comparison
    expected_holiday_rate: float
    expected_payday_rate: float


def extract_calendar_features(date: datetime) -> CalendarFeatures:
    """Extract calendar features from a single date.

    Args:
        date: The date to analyze

    Returns:
        CalendarFeatures with weekday, month, holiday proximity, payday window
    """
    weekday = date.weekday()  # 0=Monday
    month = date.month
    day_of_month = date.day

    # Check holiday proximity (within 3 days of fixed holiday)
    is_near_holiday = False
    for h_month, h_day in GERMAN_HOLIDAYS_FIXED:
        try:
            holiday_date = datetime(date.year, h_month, h_day)
            days_diff = abs((date - holiday_date).days)
            if days_diff <= 3:
                is_near_holiday = True
                break
        except ValueError:
            continue

    # Check payday window (25th-31st)
    is_payday_window = day_of_month >= PAYDAY_START_DAY

    return CalendarFeatures(
        weekday=weekday,
        month=month,
        is_near_holiday=is_near_holiday,
        is_payday_window=is_payday_window,
        day_of_month=day_of_month,
    )


def analyze_calendar_correlation(dates: list[datetime]) -> CalendarAnalysisResult:
    """Analyze calendar patterns in GK1 event dates.

    Tests:
    1. Weekday distribution: Chi-square against uniform (Mon-Sun)
    2. Month distribution: Chi-square against uniform (Jan-Dec)
    3. Holiday proximity rate vs. expected
    4. Payday window rate vs. expected

    Args:
        dates: List of GK1 event dates

    Returns:
        CalendarAnalysisResult with all test results
    """
    if len(dates) < 5:
        return CalendarAnalysisResult(
            n_events=len(dates),
            weekday_counts=[0] * 7,
            weekday_chi2=0.0,
            weekday_p_value=1.0,
            weekday_interpretation="Insufficient data (< 5 events)",
            month_counts=[0] * 12,
            month_chi2=0.0,
            month_p_value=1.0,
            month_interpretation="Insufficient data (< 5 events)",
            holiday_proximity_rate=0.0,
            payday_window_rate=0.0,
            expected_holiday_rate=0.0,
            expected_payday_rate=0.0,
        )

    # Extract features for all dates
    features = [extract_calendar_features(d) for d in dates]

    # Weekday counts
    weekday_counts = [0] * 7
    for f in features:
        weekday_counts[f.weekday] += 1

    # Month counts
    month_counts = [0] * 12
    for f in features:
        month_counts[f.month - 1] += 1  # 0-indexed

    # Chi-square tests
    n = len(features)

    # Weekday: expected uniform distribution
    expected_weekday = [n / 7] * 7
    weekday_chi2, weekday_p = stats.chisquare(weekday_counts, expected_weekday)

    if weekday_p < 0.05:
        most_common_day = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][np.argmax(weekday_counts)]
        weekday_interp = f"Signifikante Wochentagsverteilung (p={weekday_p:.4f}). Haeufigster Tag: {most_common_day}"
    else:
        weekday_interp = f"Keine signifikante Wochentagspraeferenz (p={weekday_p:.4f})"

    # Month: expected uniform distribution
    expected_month = [n / 12] * 12
    month_chi2, month_p = stats.chisquare(month_counts, expected_month)

    if month_p < 0.05:
        months = ["Jan", "Feb", "Maerz", "Apr", "Mai", "Juni", "Juli", "Aug", "Sep", "Okt", "Nov", "Dez"]
        most_common_month = months[np.argmax(month_counts)]
        month_interp = f"Signifikante Monatsverteilung (p={month_p:.4f}). Haeufigster Monat: {most_common_month}"
    else:
        month_interp = f"Keine signifikante Monatspraeferenz (p={month_p:.4f})"

    # Holiday proximity rate
    holiday_count = sum(1 for f in features if f.is_near_holiday)
    holiday_rate = holiday_count / n

    # Expected holiday rate: 5 holidays * 7 days window / 365 days
    expected_holiday_rate = (5 * 7) / 365  # ~0.096

    # Payday window rate
    payday_count = sum(1 for f in features if f.is_payday_window)
    payday_rate = payday_count / n

    # Expected payday rate: 7 days / 30 days average month
    expected_payday_rate = 7 / 30  # ~0.233

    return CalendarAnalysisResult(
        n_events=n,
        weekday_counts=weekday_counts,
        weekday_chi2=float(weekday_chi2),
        weekday_p_value=float(weekday_p),
        weekday_interpretation=weekday_interp,
        month_counts=month_counts,
        month_chi2=float(month_chi2),
        month_p_value=float(month_p),
        month_interpretation=month_interp,
        holiday_proximity_rate=float(holiday_rate),
        payday_window_rate=float(payday_rate),
        expected_holiday_rate=float(expected_holiday_rate),
        expected_payday_rate=float(expected_payday_rate),
    )


def predict_next_gk1(
    intervals: list[int],
    last_event_date: datetime,
) -> dict[str, Any]:
    """Predict next GK1 event using Poisson model.

    Uses the mean interval to estimate probability distribution
    of next event.

    Args:
        intervals: Historical intervals in days between GK1 events
        last_event_date: Date of last GK1 event

    Returns:
        Dict with prediction statistics
    """
    if len(intervals) < 3:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "Need at least 3 intervals for prediction",
        }

    # Fit Poisson: lambda = mean interval
    intervals_arr = np.array(intervals, dtype=float)
    lambda_estimate = np.mean(intervals_arr)
    std_interval = np.std(intervals_arr)

    # Probability of event on each future day (exponential waiting time)
    # P(next event in k days) = (1/lambda) * exp(-k/lambda)
    days_forecast = 30
    daily_probs = []
    cumulative_prob = 0.0

    for k in range(1, days_forecast + 1):
        # Exponential distribution PDF
        prob = (1 / lambda_estimate) * np.exp(-k / lambda_estimate)
        cumulative_prob += prob
        daily_probs.append({
            "day": k,
            "probability": float(prob),
            "cumulative": float(cumulative_prob),
        })

    # Most likely day (mode of waiting time = 0, but we use median)
    median_wait = int(np.median(intervals_arr))

    # 80% confidence interval
    ci_low = int(np.percentile(intervals_arr, 10))
    ci_high = int(np.percentile(intervals_arr, 90))

    return {
        "status": "PREDICTED",
        "last_event_date": last_event_date.strftime("%d.%m.%Y"),
        "mean_interval_days": float(lambda_estimate),
        "std_interval_days": float(std_interval),
        "median_interval_days": int(median_wait),
        "confidence_interval_80": [ci_low, ci_high],
        "daily_forecast": daily_probs[:14],  # First 14 days
        "interpretation": (
            f"Basierend auf {len(intervals)} historischen Intervallen: "
            f"Naechster GK1 erwartet in ca. {median_wait} Tagen "
            f"(80% CI: {ci_low}-{ci_high} Tage)"
        ),
    }


def to_dict(result: CalendarAnalysisResult) -> dict[str, Any]:
    """Convert CalendarAnalysisResult to JSON-serializable dict."""
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    months = ["Januar", "Februar", "Maerz", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Dezember"]

    return {
        "n_events": result.n_events,
        "weekday_analysis": {
            "counts": dict(zip(weekdays, result.weekday_counts)),
            "chi2_statistic": result.weekday_chi2,
            "p_value": result.weekday_p_value,
            "interpretation": result.weekday_interpretation,
        },
        "month_analysis": {
            "counts": dict(zip(months, result.month_counts)),
            "chi2_statistic": result.month_chi2,
            "p_value": result.month_p_value,
            "interpretation": result.month_interpretation,
        },
        "holiday_analysis": {
            "observed_rate": result.holiday_proximity_rate,
            "expected_rate": result.expected_holiday_rate,
            "ratio": result.holiday_proximity_rate / result.expected_holiday_rate if result.expected_holiday_rate > 0 else 0,
        },
        "payday_analysis": {
            "observed_rate": result.payday_window_rate,
            "expected_rate": result.expected_payday_rate,
            "ratio": result.payday_window_rate / result.expected_payday_rate if result.expected_payday_rate > 0 else 0,
        },
    }
