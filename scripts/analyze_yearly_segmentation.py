"""Yearly Segmented Near-Miss Analysis.

Analyzes HOUSE-004 anomaly (Near-Miss patterns) segmented by year.
Tests whether the 70x difference between jackpot and normal periods
exists in all years or only in specific years.
"""

from __future__ import annotations

import json
import logging
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        return super().default(obj)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class YearlyNearMissResult:
    """Near-Miss analysis result for a specific year."""

    year: int
    keno_type: int
    n_draws: int
    max_winners: int
    near_miss_winners: int
    near_miss_ratio: float
    expected_ratio: float
    ratio_deviation: float  # observed / expected
    chi2_stat: float
    p_value: float
    is_significant: bool


@dataclass
class YearlyGK1Stats:
    """GK1 statistics for a specific year."""

    year: int
    n_gk1_events: int
    n_gk1_typ9: int
    n_gk1_typ10: int
    avg_waiting_days: float
    min_waiting_days: int
    max_waiting_days: int
    total_winners: int


@dataclass
class HouseAnomalyYearly:
    """HOUSE-004 anomaly comparison between jackpot and normal periods per year."""

    year: int
    keno_type: int
    jackpot_near_miss_ratio: float
    normal_near_miss_ratio: float
    ratio_difference: float
    is_anomaly: bool  # True if difference > 10x


def _keno_match_probability(
    keno_type: int,
    matches: int,
    *,
    numbers_range: int = 70,
    numbers_drawn: int = 20,
) -> float:
    """Hypergeometric probability for exactly `matches` hits."""
    if matches < 0 or matches > keno_type:
        return 0.0
    misses = numbers_drawn - matches
    if misses < 0:
        return 0.0
    if misses > (numbers_range - keno_type):
        return 0.0
    denom = math.comb(numbers_range, numbers_drawn)
    return (
        math.comb(keno_type, matches)
        * math.comb(numbers_range - keno_type, misses)
        / denom
    )


def calculate_expected_ratio(keno_type: int) -> float:
    """Calculate expected near-miss to max ratio based on hypergeometric distribution."""
    max_matches = keno_type
    near_miss = keno_type - 1

    p_max = _keno_match_probability(keno_type, max_matches)
    p_near = _keno_match_probability(keno_type, near_miss)

    return p_near / p_max if p_max > 0 else 1.0


def load_and_prepare_data(gq_path: str) -> pd.DataFrame:
    """Load and prepare GQ data with proper date parsing."""
    df = pd.read_csv(gq_path, encoding='utf-8-sig')

    # Parse dates (German format: DD.MM.YYYY)
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    # Extract year
    df['Year'] = df['Datum'].dt.year

    # Convert winner counts (handle German number format with dots)
    df['Anzahl der Gewinner'] = df['Anzahl der Gewinner'].apply(
        lambda x: float(str(x).replace('.', '')) if pd.notna(x) else 0
    )

    return df


def load_gk1_data(gk1_path: str) -> pd.DataFrame:
    """Load GK1 (jackpot) events data."""
    df = pd.read_csv(gk1_path, encoding='utf-8-sig')
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    df['Year'] = df['Datum'].dt.year
    return df


def analyze_near_miss_by_year(df: pd.DataFrame, keno_type: int = 10) -> list[YearlyNearMissResult]:
    """Analyze near-miss patterns for a specific Keno type by year."""
    results = []

    max_matches = keno_type
    near_miss_matches = keno_type - 1
    expected_ratio = calculate_expected_ratio(keno_type)

    for year in sorted(df['Year'].unique()):
        year_data = df[(df['Year'] == year) & (df['Keno-Typ'] == keno_type)]

        if len(year_data) == 0:
            continue

        # Get unique draws
        n_draws = year_data['Datum'].nunique()

        # Sum winners
        max_data = year_data[year_data['Anzahl richtiger Zahlen'] == max_matches]
        near_data = year_data[year_data['Anzahl richtiger Zahlen'] == near_miss_matches]

        max_winners = int(max_data['Anzahl der Gewinner'].sum()) if len(max_data) > 0 else 0
        near_winners = int(near_data['Anzahl der Gewinner'].sum()) if len(near_data) > 0 else 0

        # Calculate ratio
        observed_ratio = near_winners / max_winners if max_winners > 0 else 0.0
        ratio_deviation = observed_ratio / expected_ratio if expected_ratio > 0 else 0.0

        # Chi-square test
        if max_winners > 0 and near_winners > 0:
            total = max_winners + near_winners
            p_max = 1 / (1 + expected_ratio)
            p_near = expected_ratio / (1 + expected_ratio)

            expected_vals = np.array([total * p_max, total * p_near])
            observed_vals = np.array([max_winners, near_winners])

            chi2, p_value = stats.chisquare(observed_vals, expected_vals)
        else:
            chi2, p_value = 0.0, 1.0

        results.append(YearlyNearMissResult(
            year=int(year),
            keno_type=keno_type,
            n_draws=n_draws,
            max_winners=max_winners,
            near_miss_winners=near_winners,
            near_miss_ratio=round(observed_ratio, 4),
            expected_ratio=round(expected_ratio, 4),
            ratio_deviation=round(ratio_deviation, 4),
            chi2_stat=round(float(chi2), 4),
            p_value=round(float(p_value), 6),
            is_significant=float(p_value) < 0.05,
        ))

    return results


def analyze_gk1_by_year(gk1_df: pd.DataFrame) -> list[YearlyGK1Stats]:
    """Analyze GK1 events by year."""
    results = []

    for year in sorted(gk1_df['Year'].unique()):
        year_data = gk1_df[gk1_df['Year'] == year]

        n_typ9 = len(year_data[year_data['Keno-Typ'] == 9])
        n_typ10 = len(year_data[year_data['Keno-Typ'] == 10])

        waiting_days = year_data['Vergangene Tage seit dem letzten Gewinnklasse 1'].values
        waiting_days = [d for d in waiting_days if d > 0]  # Exclude 0 (same day events)

        total_winners = int(year_data['Anzahl der Gewinner'].sum())

        results.append(YearlyGK1Stats(
            year=int(year),
            n_gk1_events=len(year_data),
            n_gk1_typ9=n_typ9,
            n_gk1_typ10=n_typ10,
            avg_waiting_days=round(np.mean(waiting_days), 2) if waiting_days else 0.0,
            min_waiting_days=int(min(waiting_days)) if waiting_days else 0,
            max_waiting_days=int(max(waiting_days)) if waiting_days else 0,
            total_winners=total_winners,
        ))

    return results


def analyze_house004_by_year(
    gq_df: pd.DataFrame,
    gk1_df: pd.DataFrame,
    keno_type: int = 10,
    window_days: int = 7,
) -> list[HouseAnomalyYearly]:
    """Analyze HOUSE-004 anomaly (jackpot vs normal periods) by year."""
    results = []

    max_matches = keno_type
    near_miss_matches = keno_type - 1

    # Get jackpot dates
    jackpot_dates = set(gk1_df['Datum'].values)

    # Create jackpot window (7 days around each jackpot)
    jackpot_windows = set()
    for jd in jackpot_dates:
        jd_dt = pd.Timestamp(jd)
        for delta in range(-window_days, window_days + 1):
            jackpot_windows.add(jd_dt + pd.Timedelta(days=delta))

    for year in sorted(gq_df['Year'].unique()):
        year_data = gq_df[(gq_df['Year'] == year) & (gq_df['Keno-Typ'] == keno_type)]

        if len(year_data) == 0:
            continue

        # Split into jackpot and normal periods
        year_data = year_data.copy()
        year_data['is_jackpot_period'] = year_data['Datum'].isin(jackpot_windows)

        jackpot_data = year_data[year_data['is_jackpot_period']]
        normal_data = year_data[~year_data['is_jackpot_period']]

        # Calculate ratios for jackpot periods
        jp_max = jackpot_data[jackpot_data['Anzahl richtiger Zahlen'] == max_matches]
        jp_near = jackpot_data[jackpot_data['Anzahl richtiger Zahlen'] == near_miss_matches]
        jp_max_winners = jp_max['Anzahl der Gewinner'].sum() if len(jp_max) > 0 else 0
        jp_near_winners = jp_near['Anzahl der Gewinner'].sum() if len(jp_near) > 0 else 0
        jp_ratio = jp_near_winners / jp_max_winners if jp_max_winners > 0 else 0.0

        # Calculate ratios for normal periods
        nm_max = normal_data[normal_data['Anzahl richtiger Zahlen'] == max_matches]
        nm_near = normal_data[normal_data['Anzahl richtiger Zahlen'] == near_miss_matches]
        nm_max_winners = nm_max['Anzahl der Gewinner'].sum() if len(nm_max) > 0 else 0
        nm_near_winners = nm_near['Anzahl der Gewinner'].sum() if len(nm_near) > 0 else 0
        nm_ratio = nm_near_winners / nm_max_winners if nm_max_winners > 0 else 0.0

        ratio_diff = nm_ratio / jp_ratio if jp_ratio > 0 else 0.0

        results.append(HouseAnomalyYearly(
            year=int(year),
            keno_type=keno_type,
            jackpot_near_miss_ratio=round(jp_ratio, 4),
            normal_near_miss_ratio=round(nm_ratio, 4),
            ratio_difference=round(ratio_diff, 4),
            is_anomaly=ratio_diff > 10,  # >10x difference is anomalous
        ))

    return results


def main():
    """Run yearly segmented analysis."""
    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    gq_path = base_path / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
    gk1_path = base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv"
    output_path = base_path / "results" / "yearly_segmentation.json"

    logger.info("Loading data...")
    gq_df = load_and_prepare_data(str(gq_path))
    gk1_df = load_gk1_data(str(gk1_path))

    logger.info(f"GQ data: {len(gq_df)} rows, years: {sorted(gq_df['Year'].unique())}")
    logger.info(f"GK1 data: {len(gk1_df)} events")

    # Analyze Near-Miss for Keno Type 10 by year
    logger.info("\n=== Near-Miss Analysis (Keno Typ 10) by Year ===")
    near_miss_results_10 = analyze_near_miss_by_year(gq_df, keno_type=10)
    for r in near_miss_results_10:
        sig = "SIGNIFICANT" if r.is_significant else ""
        logger.info(
            f"  {r.year}: ratio={r.near_miss_ratio:.2f} (expected={r.expected_ratio:.2f}), "
            f"deviation={r.ratio_deviation:.1f}x, p={r.p_value:.4f} {sig}"
        )

    # Analyze Near-Miss for Keno Type 9 by year
    logger.info("\n=== Near-Miss Analysis (Keno Typ 9) by Year ===")
    near_miss_results_9 = analyze_near_miss_by_year(gq_df, keno_type=9)
    for r in near_miss_results_9:
        sig = "SIGNIFICANT" if r.is_significant else ""
        logger.info(
            f"  {r.year}: ratio={r.near_miss_ratio:.2f} (expected={r.expected_ratio:.2f}), "
            f"deviation={r.ratio_deviation:.1f}x, p={r.p_value:.4f} {sig}"
        )

    # Analyze GK1 events by year
    logger.info("\n=== GK1 Events by Year ===")
    gk1_results = analyze_gk1_by_year(gk1_df)
    for r in gk1_results:
        logger.info(
            f"  {r.year}: {r.n_gk1_events} events (Typ9={r.n_gk1_typ9}, Typ10={r.n_gk1_typ10}), "
            f"avg_wait={r.avg_waiting_days:.1f} days, winners={r.total_winners}"
        )

    # Analyze HOUSE-004 anomaly by year
    logger.info("\n=== HOUSE-004 Anomaly (Jackpot vs Normal) by Year - Keno Typ 10 ===")
    house004_10 = analyze_house004_by_year(gq_df, gk1_df, keno_type=10)
    for r in house004_10:
        anomaly = "ANOMALY" if r.is_anomaly else ""
        logger.info(
            f"  {r.year}: jackpot_ratio={r.jackpot_near_miss_ratio:.2f}, "
            f"normal_ratio={r.normal_near_miss_ratio:.2f}, "
            f"diff={r.ratio_difference:.1f}x {anomaly}"
        )

    logger.info("\n=== HOUSE-004 Anomaly (Jackpot vs Normal) by Year - Keno Typ 9 ===")
    house004_9 = analyze_house004_by_year(gq_df, gk1_df, keno_type=9)
    for r in house004_9:
        anomaly = "ANOMALY" if r.is_anomaly else ""
        logger.info(
            f"  {r.year}: jackpot_ratio={r.jackpot_near_miss_ratio:.2f}, "
            f"normal_ratio={r.normal_near_miss_ratio:.2f}, "
            f"diff={r.ratio_difference:.1f}x {anomaly}"
        )

    # Compile results
    results = {
        "analysis": "yearly_segmentation",
        "description": "Near-Miss Patterns segmented by year to test HOUSE-004 anomaly consistency",
        "timestamp": datetime.now().isoformat(),
        "data_sources": {
            "gq_file": str(gq_path),
            "gk1_file": str(gk1_path),
        },
        "near_miss_keno_typ_10": [asdict(r) for r in near_miss_results_10],
        "near_miss_keno_typ_9": [asdict(r) for r in near_miss_results_9],
        "gk1_events_by_year": [asdict(r) for r in gk1_results],
        "house004_keno_typ_10": [asdict(r) for r in house004_10],
        "house004_keno_typ_9": [asdict(r) for r in house004_9],
        "summary": {
            "years_analyzed": [int(y) for y in sorted(gq_df['Year'].unique().tolist())],
            "total_draws": int(gq_df['Datum'].nunique()),
            "total_gk1_events": int(len(gk1_df)),
            "house004_anomaly_by_year": {
                "keno_typ_10": {
                    str(r.year): bool(r.is_anomaly) for r in house004_10
                },
                "keno_typ_9": {
                    str(r.year): bool(r.is_anomaly) for r in house004_9
                },
            },
            "conclusion": "",
        },
    }

    # Generate conclusion
    anomaly_years_10 = [int(r.year) for r in house004_10 if r.is_anomaly]
    anomaly_years_9 = [int(r.year) for r in house004_9 if r.is_anomaly]

    if len(anomaly_years_10) == len(house004_10):
        conclusion_10 = f"Keno Typ 10: HOUSE-004 anomaly present in ALL years ({anomaly_years_10})"
    elif len(anomaly_years_10) > 0:
        conclusion_10 = f"Keno Typ 10: HOUSE-004 anomaly present in SOME years ({anomaly_years_10})"
    else:
        conclusion_10 = "Keno Typ 10: HOUSE-004 anomaly NOT present in any year"

    if len(anomaly_years_9) == len(house004_9):
        conclusion_9 = f"Keno Typ 9: HOUSE-004 anomaly present in ALL years ({anomaly_years_9})"
    elif len(anomaly_years_9) > 0:
        conclusion_9 = f"Keno Typ 9: HOUSE-004 anomaly present in SOME years ({anomaly_years_9})"
    else:
        conclusion_9 = "Keno Typ 9: HOUSE-004 anomaly NOT present in any year"

    results["summary"]["conclusion"] = f"{conclusion_10}. {conclusion_9}."

    logger.info(f"\n=== CONCLUSION ===")
    logger.info(results["summary"]["conclusion"])

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    logger.info(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
