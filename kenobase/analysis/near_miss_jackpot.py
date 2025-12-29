"""HOUSE-004: Near-Miss Analysis during High Jackpot Periods.

Combines near_miss.py (HYP-001) and jackpot_correlation.py (HYP-015) to test
whether Near-Miss frequency differs between high-jackpot and normal periods.

Hypothesis: Near-Miss occurrences may be elevated during jackpot periods
as a player retention strategy ("almost won" feeling encourages continued play).

Methodology:
1. Load GK1 events (jackpot dates) from jackpot_correlation module
2. Segment GQ data into jackpot vs normal periods
3. Calculate near_miss_ratio for each segment per Keno-Typ
4. Compare distributions using Chi-square test

Acceptance Criteria:
- Chi-square p < 0.05 for at least 3 Keno-Typen indicates SUPPORTED
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy import stats

from kenobase.analysis.jackpot_correlation import (
    GK1Event,
    get_jackpot_dates,
    load_gk1_events,
)
from kenobase.analysis.near_miss import (
    KENO_PROBABILITIES,
    NearMissResult,
    analyze_near_miss,
    calculate_expected_ratio,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# Significance threshold for Chi-square test
P_VALUE_THRESHOLD = 0.05

# Minimum number of significant Keno-Typen to support hypothesis
MIN_SIGNIFICANT_TYPES = 3


@dataclass
class NearMissJackpotResult:
    """Result of Near-Miss analysis comparing jackpot vs normal periods.

    Attributes:
        keno_type: Keno-Typ (2-10)
        jackpot_near_miss_ratio: Near-miss ratio during jackpot periods
        normal_near_miss_ratio: Near-miss ratio during normal periods
        expected_ratio: Theoretical expected ratio
        ratio_difference: jackpot_ratio - normal_ratio
        chi2_stat: Chi-square statistic comparing distributions
        p_value: p-value of Chi-square test
        is_significant: True if p < 0.05
        n_jackpot_draws: Number of draws on jackpot days
        n_normal_draws: Number of draws on normal days
        jackpot_max_winners: Total max winners during jackpot periods
        jackpot_near_winners: Total near-miss winners during jackpot periods
        normal_max_winners: Total max winners during normal periods
        normal_near_winners: Total near-miss winners during normal periods
    """

    keno_type: int
    jackpot_near_miss_ratio: float
    normal_near_miss_ratio: float
    expected_ratio: float
    ratio_difference: float
    chi2_stat: float
    p_value: float
    is_significant: bool
    n_jackpot_draws: int
    n_normal_draws: int
    jackpot_max_winners: int
    jackpot_near_winners: int
    normal_max_winners: int
    normal_near_winners: int


@dataclass
class House004AnalysisSummary:
    """Complete summary of HOUSE-004 analysis.

    Attributes:
        results: Per-Keno-Typ comparison results
        n_significant: Number of Keno-Typen with significant difference
        hypothesis_supported: True if n_significant >= MIN_SIGNIFICANT_TYPES
        n_gk1_events: Number of GK1 (jackpot) events loaded
        date_range_start: Start of analysis period
        date_range_end: End of analysis period
        gk1_source: Path to GK1 data file
        gq_source: Path to GQ data file
    """

    results: list[NearMissJackpotResult] = field(default_factory=list)
    n_significant: int = 0
    hypothesis_supported: bool = False
    n_gk1_events: int = 0
    date_range_start: datetime | None = None
    date_range_end: datetime | None = None
    gk1_source: str = ""
    gq_source: str = ""


def split_by_jackpot_dates(
    df: pd.DataFrame,
    jackpot_dates: set[datetime],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split GQ DataFrame into jackpot and normal periods.

    Args:
        df: DataFrame with GQ data (must have 'Datum' column)
        jackpot_dates: Set of jackpot dates (normalized to midnight)

    Returns:
        Tuple of (jackpot_df, normal_df)
    """
    if "Datum" not in df.columns:
        logger.error("DataFrame missing 'Datum' column")
        return pd.DataFrame(), df.copy()

    # Normalize dates in DataFrame
    df = df.copy()
    if df["Datum"].dtype == object:
        df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True)

    # Create normalized date column for comparison
    df["_normalized_date"] = df["Datum"].dt.normalize()

    # Convert jackpot_dates to pandas Timestamps for comparison
    jackpot_timestamps = {pd.Timestamp(d) for d in jackpot_dates}

    jackpot_mask = df["_normalized_date"].isin(jackpot_timestamps)

    jackpot_df = df[jackpot_mask].drop(columns=["_normalized_date"])
    normal_df = df[~jackpot_mask].drop(columns=["_normalized_date"])

    logger.info(
        f"Split GQ data: {len(jackpot_df)} jackpot records, {len(normal_df)} normal records"
    )

    return jackpot_df, normal_df


def analyze_near_miss_jackpot(
    df: pd.DataFrame,
    jackpot_dates: set[datetime],
    keno_type: int,
) -> NearMissJackpotResult:
    """Analyze near-miss distribution comparing jackpot vs normal periods.

    Args:
        df: DataFrame with GQ data
        jackpot_dates: Set of jackpot dates
        keno_type: Keno-Typ to analyze (2-10)

    Returns:
        NearMissJackpotResult with comparison metrics
    """
    # Split data by jackpot dates
    jackpot_df, normal_df = split_by_jackpot_dates(df, jackpot_dates)

    # Filter to this Keno-Typ
    jp_data = jackpot_df[jackpot_df["Keno-Typ"] == keno_type].copy()
    nm_data = normal_df[normal_df["Keno-Typ"] == keno_type].copy()

    max_matches = keno_type
    near_miss_matches = keno_type - 1

    # Count winners in each segment
    # Jackpot period
    jp_max = jp_data[jp_data["Anzahl richtiger Zahlen"] == max_matches]
    jp_near = jp_data[jp_data["Anzahl richtiger Zahlen"] == near_miss_matches]

    jackpot_max_winners = int(jp_max["Anzahl der Gewinner"].sum()) if len(jp_max) > 0 else 0
    jackpot_near_winners = int(jp_near["Anzahl der Gewinner"].sum()) if len(jp_near) > 0 else 0

    # Normal period
    nm_max = nm_data[nm_data["Anzahl richtiger Zahlen"] == max_matches]
    nm_near = nm_data[nm_data["Anzahl richtiger Zahlen"] == near_miss_matches]

    normal_max_winners = int(nm_max["Anzahl der Gewinner"].sum()) if len(nm_max) > 0 else 0
    normal_near_winners = int(nm_near["Anzahl der Gewinner"].sum()) if len(nm_near) > 0 else 0

    # Calculate ratios
    jackpot_ratio = (
        jackpot_near_winners / jackpot_max_winners if jackpot_max_winners > 0 else 0.0
    )
    normal_ratio = (
        normal_near_winners / normal_max_winners if normal_max_winners > 0 else 0.0
    )
    expected_ratio = calculate_expected_ratio(keno_type)

    # Count unique draws
    n_jackpot_draws = len(jp_data.groupby("Datum")) if len(jp_data) > 0 else 0
    n_normal_draws = len(nm_data.groupby("Datum")) if len(nm_data) > 0 else 0

    # Chi-square test comparing jackpot vs normal near-miss proportions
    # Contingency table:
    # Rows: jackpot, normal
    # Cols: near_miss_winners, max_winners
    observed = np.array([
        [jackpot_near_winners, jackpot_max_winners],
        [normal_near_winners, normal_max_winners],
    ])

    # Check for valid table
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)

    if observed.sum() == 0 or 0 in row_totals or 0 in col_totals:
        logger.warning(f"Keno-Typ {keno_type}: insufficient data for Chi-square test")
        chi2, p_value = 0.0, 1.0
    else:
        try:
            chi2, p_value, _, _ = stats.chi2_contingency(observed)
        except ValueError as e:
            logger.warning(f"Keno-Typ {keno_type}: Chi-square failed - {e}")
            chi2, p_value = 0.0, 1.0

    return NearMissJackpotResult(
        keno_type=keno_type,
        jackpot_near_miss_ratio=round(jackpot_ratio, 4),
        normal_near_miss_ratio=round(normal_ratio, 4),
        expected_ratio=round(expected_ratio, 4),
        ratio_difference=round(jackpot_ratio - normal_ratio, 4),
        chi2_stat=round(float(chi2), 4),
        p_value=round(float(p_value), 6),
        is_significant=float(p_value) < P_VALUE_THRESHOLD,
        n_jackpot_draws=n_jackpot_draws,
        n_normal_draws=n_normal_draws,
        jackpot_max_winners=jackpot_max_winners,
        jackpot_near_winners=jackpot_near_winners,
        normal_max_winners=normal_max_winners,
        normal_near_winners=normal_near_winners,
    )


def analyze_all_near_miss_jackpot(
    df: pd.DataFrame,
    jackpot_dates: set[datetime],
) -> list[NearMissJackpotResult]:
    """Analyze near-miss for all Keno-Typen comparing jackpot vs normal.

    Args:
        df: DataFrame with GQ data
        jackpot_dates: Set of jackpot dates

    Returns:
        List of NearMissJackpotResult for each Keno-Typ
    """
    results = []

    for keno_type in range(2, 11):
        if keno_type in df["Keno-Typ"].values:
            result = analyze_near_miss_jackpot(df, jackpot_dates, keno_type)
            results.append(result)

            status = "SIGNIFICANT" if result.is_significant else "normal"
            logger.info(
                f"Keno-Typ {keno_type}: jp_ratio={result.jackpot_near_miss_ratio:.2f}, "
                f"nm_ratio={result.normal_near_miss_ratio:.2f}, "
                f"diff={result.ratio_difference:+.2f}, p={result.p_value:.4f} [{status}]"
            )

    return results


def run_house004_analysis(
    gq_path: str | Path,
    gk1_path: str | Path,
) -> House004AnalysisSummary:
    """Run complete HOUSE-004 analysis.

    Args:
        gq_path: Path to GQ data file (CSV with winner statistics)
        gk1_path: Path to GK1 data file (jackpot events)

    Returns:
        House004AnalysisSummary with all results
    """
    gq_path = Path(gq_path)
    gk1_path = Path(gk1_path)

    # Load GK1 events
    try:
        gk1_events = load_gk1_events(gk1_path)
    except FileNotFoundError as e:
        logger.error(f"GK1 file not found: {e}")
        return House004AnalysisSummary(gk1_source=str(gk1_path), gq_source=str(gq_path))

    if not gk1_events:
        logger.error("No GK1 events loaded")
        return House004AnalysisSummary(gk1_source=str(gk1_path), gq_source=str(gq_path))

    jackpot_dates = get_jackpot_dates(gk1_events)
    logger.info(f"Loaded {len(gk1_events)} GK1 events ({len(jackpot_dates)} unique dates)")

    # Load GQ data
    if not gq_path.exists():
        logger.error(f"GQ file not found: {gq_path}")
        return House004AnalysisSummary(
            n_gk1_events=len(gk1_events),
            gk1_source=str(gk1_path),
            gq_source=str(gq_path),
        )

    try:
        # Try different encodings (utf-8-sig handles BOM)
        for encoding in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
            try:
                df = pd.read_csv(gq_path, encoding=encoding, sep=None, engine="python")
                break
            except UnicodeDecodeError:
                continue
        else:
            logger.error(f"Could not decode GQ file: {gq_path}")
            return House004AnalysisSummary(
                n_gk1_events=len(gk1_events),
                gk1_source=str(gk1_path),
                gq_source=str(gq_path),
            )
        # Strip BOM from column names if present
        df.columns = [c.lstrip("\ufeff") for c in df.columns]
    except Exception as e:
        logger.error(f"Failed to load GQ data: {e}")
        return House004AnalysisSummary(
            n_gk1_events=len(gk1_events),
            gk1_source=str(gk1_path),
            gq_source=str(gq_path),
        )

    logger.info(f"Loaded GQ data: {len(df)} records")

    # Ensure required columns exist
    required_cols = ["Datum", "Keno-Typ", "Anzahl richtiger Zahlen", "Anzahl der Gewinner"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        logger.error(f"GQ data missing columns: {missing_cols}")
        return House004AnalysisSummary(
            n_gk1_events=len(gk1_events),
            gk1_source=str(gk1_path),
            gq_source=str(gq_path),
        )

    # Parse dates
    df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Datum"])

    # Determine date range
    date_range_start = df["Datum"].min()
    date_range_end = df["Datum"].max()

    # Run analysis
    results = analyze_all_near_miss_jackpot(df, jackpot_dates)

    # Count significant results
    n_significant = sum(1 for r in results if r.is_significant)
    hypothesis_supported = n_significant >= MIN_SIGNIFICANT_TYPES

    return House004AnalysisSummary(
        results=results,
        n_significant=n_significant,
        hypothesis_supported=hypothesis_supported,
        n_gk1_events=len(gk1_events),
        date_range_start=date_range_start.to_pydatetime() if pd.notna(date_range_start) else None,
        date_range_end=date_range_end.to_pydatetime() if pd.notna(date_range_end) else None,
        gk1_source=str(gk1_path),
        gq_source=str(gq_path),
    )


def result_to_dict(result: NearMissJackpotResult) -> dict:
    """Convert NearMissJackpotResult to dictionary.

    Args:
        result: NearMissJackpotResult instance

    Returns:
        Dictionary representation
    """
    return {
        "keno_type": result.keno_type,
        "jackpot_near_miss_ratio": result.jackpot_near_miss_ratio,
        "normal_near_miss_ratio": result.normal_near_miss_ratio,
        "expected_ratio": result.expected_ratio,
        "ratio_difference": result.ratio_difference,
        "chi2_stat": result.chi2_stat,
        "p_value": result.p_value,
        "is_significant": result.is_significant,
        "n_jackpot_draws": result.n_jackpot_draws,
        "n_normal_draws": result.n_normal_draws,
        "jackpot_max_winners": result.jackpot_max_winners,
        "jackpot_near_winners": result.jackpot_near_winners,
        "normal_max_winners": result.normal_max_winners,
        "normal_near_winners": result.normal_near_winners,
    }


def summary_to_dict(summary: House004AnalysisSummary) -> dict:
    """Convert House004AnalysisSummary to dictionary.

    Args:
        summary: House004AnalysisSummary instance

    Returns:
        Dictionary representation for JSON export
    """
    return {
        "results": [result_to_dict(r) for r in summary.results],
        "n_significant": summary.n_significant,
        "hypothesis_supported": summary.hypothesis_supported,
        "n_gk1_events": summary.n_gk1_events,
        "date_range_start": (
            summary.date_range_start.isoformat() if summary.date_range_start else None
        ),
        "date_range_end": (
            summary.date_range_end.isoformat() if summary.date_range_end else None
        ),
        "gk1_source": summary.gk1_source,
        "gq_source": summary.gq_source,
    }


def export_result_to_json(
    summary: House004AnalysisSummary,
    output_path: str | Path,
) -> None:
    """Export analysis result to JSON file.

    Args:
        summary: House004AnalysisSummary to export
        output_path: Path for output JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "hypothesis": "HOUSE-004",
        "description": "Near-Miss Analyse bei hohem Jackpot",
        "timestamp": datetime.now().isoformat(),
        "summary": summary_to_dict(summary),
        "acceptance_criteria": {
            "p_value_threshold": P_VALUE_THRESHOLD,
            "min_significant_types": MIN_SIGNIFICANT_TYPES,
            "significance_met": summary.n_significant,
            "hypothesis_supported": summary.hypothesis_supported,
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Exported result to {output_path}")


__all__ = [
    "NearMissJackpotResult",
    "House004AnalysisSummary",
    "P_VALUE_THRESHOLD",
    "MIN_SIGNIFICANT_TYPES",
    "split_by_jackpot_dates",
    "analyze_near_miss_jackpot",
    "analyze_all_near_miss_jackpot",
    "run_house004_analysis",
    "result_to_dict",
    "summary_to_dict",
    "export_result_to_json",
]
