#!/usr/bin/env python
"""
PRED-001: Near-Miss Ratio Analysis Before GK1 Events

Hypothesis: Near-Miss Ratio (9/10 to 10/10) increases in the 7-14 days
BEFORE a GK1 event (10/10 hit).

This script:
1. Loads GK1 event data
2. Loads daily winning quotas data
3. Calculates Near-Miss Ratio before and after each GK1 event
4. Performs statistical test to check significance
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from scipy import stats


def parse_german_date(date_str: str) -> datetime:
    """Parse German date format DD.MM.YYYY"""
    return datetime.strptime(date_str.strip(), "%d.%m.%Y")


def parse_german_number(num_str: str) -> float:
    """Parse German number format (1.234 -> 1234, 1,5 -> 1.5)"""
    if pd.isna(num_str) or num_str == "":
        return 0.0
    if isinstance(num_str, (int, float)):
        return float(num_str)
    # German format: 1.234,56 -> 1234.56
    # But also: 1.234 could mean 1234 (thousands separator)
    num_str = str(num_str).strip()
    # If contains comma, it's a decimal
    if "," in num_str:
        num_str = num_str.replace(".", "").replace(",", ".")
    else:
        # Dot is thousands separator
        num_str = num_str.replace(".", "")
    try:
        return float(num_str)
    except ValueError:
        return 0.0


def load_gk1_events(filepath: Path) -> pd.DataFrame:
    """Load GK1 events from filtered data file"""
    df = pd.read_csv(filepath)

    # Rename columns for easier access
    df.columns = ["Datum", "Keno_Typ", "Anzahl_Gewinner", "Tage_seit_GK1"]

    # Parse dates
    df["Datum"] = df["Datum"].apply(parse_german_date)

    # Filter for GK1 events (Keno-Typ 10 = 10/10 hits)
    gk1_events = df[df["Keno_Typ"] == 10].copy()

    return gk1_events


def load_winning_quotas(filepath: Path) -> pd.DataFrame:
    """Load daily winning quotas data"""
    df = pd.read_csv(filepath, encoding='utf-8-sig')

    # Rename columns
    df.columns = ["Datum", "Keno_Typ", "Anzahl_richtig", "Anzahl_Gewinner", "Gewinn"]

    # Parse dates
    df["Datum"] = df["Datum"].apply(parse_german_date)

    # Parse winner counts
    df["Anzahl_Gewinner"] = df["Anzahl_Gewinner"].apply(parse_german_number)

    return df


def calculate_near_miss_ratio(quotas_df: pd.DataFrame, date: datetime,
                               window_start: int, window_end: int) -> dict:
    """
    Calculate Near-Miss Ratio for Keno-Typ 10 in a time window.

    Near-Miss Ratio = count(9/10) / max(count(10/10), 1)

    Args:
        quotas_df: DataFrame with winning quotas
        date: Reference date (GK1 event date)
        window_start: Days offset start (negative = before, positive = after)
        window_end: Days offset end

    Returns:
        Dict with ratio, counts, and dates
    """
    start_date = date + timedelta(days=window_start)
    end_date = date + timedelta(days=window_end)

    # Filter for time window
    mask = (quotas_df["Datum"] >= start_date) & (quotas_df["Datum"] <= end_date)
    window_data = quotas_df[mask]

    # Filter for Keno-Typ 10
    typ10 = window_data[window_data["Keno_Typ"] == 10]

    # Get 10/10 winners (GK1) and 9/10 winners (Near-Miss)
    gk1 = typ10[typ10["Anzahl_richtig"] == 10]["Anzahl_Gewinner"].sum()
    near_miss = typ10[typ10["Anzahl_richtig"] == 9]["Anzahl_Gewinner"].sum()

    # Calculate ratio (avoid division by zero)
    ratio = near_miss / max(gk1, 1) if gk1 > 0 else near_miss

    # Count days with data
    days_with_data = len(window_data["Datum"].unique())

    return {
        "ratio": ratio,
        "near_miss_count": int(near_miss),
        "gk1_count": int(gk1),
        "days_with_data": days_with_data,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }


def analyze_pred001(gk1_events: pd.DataFrame, quotas_df: pd.DataFrame,
                    window_days: int = 7) -> dict:
    """
    Analyze PRED-001: Near-Miss Ratio before vs after GK1 events.

    Args:
        gk1_events: DataFrame with GK1 event dates
        quotas_df: DataFrame with daily winning quotas
        window_days: Number of days for the window (default 7)

    Returns:
        Analysis results dict
    """
    before_ratios = []
    after_ratios = []
    event_details = []

    for _, event in gk1_events.iterrows():
        event_date = event["Datum"]

        # Calculate ratios BEFORE the event (excluding event day)
        before = calculate_near_miss_ratio(
            quotas_df, event_date,
            window_start=-window_days,
            window_end=-1
        )

        # Calculate ratios AFTER the event (excluding event day)
        after = calculate_near_miss_ratio(
            quotas_df, event_date,
            window_start=1,
            window_end=window_days
        )

        # Only include if we have data for both periods
        if before["days_with_data"] >= 3 and after["days_with_data"] >= 3:
            before_ratios.append(before["ratio"])
            after_ratios.append(after["ratio"])

            event_details.append({
                "event_date": event_date.strftime("%Y-%m-%d"),
                "winners_on_event": int(event["Anzahl_Gewinner"]),
                "before": before,
                "after": after,
                "ratio_difference": before["ratio"] - after["ratio"]
            })

    # Statistical tests
    if len(before_ratios) >= 5:
        # Paired t-test (before vs after for same events)
        t_stat, t_pvalue = stats.ttest_rel(before_ratios, after_ratios)

        # Wilcoxon signed-rank test (non-parametric alternative)
        try:
            w_stat, w_pvalue = stats.wilcoxon(before_ratios, after_ratios)
        except ValueError:
            # All differences are zero
            w_stat, w_pvalue = 0, 1.0

        # Effect size (Cohen's d for paired samples)
        differences = np.array(before_ratios) - np.array(after_ratios)
        cohens_d = np.mean(differences) / np.std(differences) if np.std(differences) > 0 else 0
    else:
        t_stat, t_pvalue = None, None
        w_stat, w_pvalue = None, None
        cohens_d = None

    # Summary statistics
    before_mean = np.mean(before_ratios) if before_ratios else 0
    after_mean = np.mean(after_ratios) if after_ratios else 0
    before_std = np.std(before_ratios) if before_ratios else 0
    after_std = np.std(after_ratios) if after_ratios else 0

    # Determine if hypothesis is confirmed
    # Hypothesis: Near-Miss Ratio is HIGHER before GK1 events
    alpha = 0.05
    hypothesis_confirmed = (
        t_pvalue is not None
        and t_pvalue < alpha
        and before_mean > after_mean
    )

    return {
        "hypothesis_id": "PRED-001",
        "hypothesis": "Near-Miss Ratio (9/10 to 10/10) increases before GK1 events",
        "window_days": window_days,
        "n_events_analyzed": len(event_details),
        "summary": {
            "before_gk1": {
                "mean_ratio": round(before_mean, 4),
                "std_ratio": round(before_std, 4),
                "min_ratio": round(min(before_ratios), 4) if before_ratios else None,
                "max_ratio": round(max(before_ratios), 4) if before_ratios else None
            },
            "after_gk1": {
                "mean_ratio": round(after_mean, 4),
                "std_ratio": round(after_std, 4),
                "min_ratio": round(min(after_ratios), 4) if after_ratios else None,
                "max_ratio": round(max(after_ratios), 4) if after_ratios else None
            },
            "ratio_difference": round(before_mean - after_mean, 4)
        },
        "statistical_tests": {
            "paired_ttest": {
                "t_statistic": round(t_stat, 4) if t_stat is not None else None,
                "p_value": round(t_pvalue, 6) if t_pvalue is not None else None,
                "significant_at_0.05": t_pvalue < 0.05 if t_pvalue is not None else None
            },
            "wilcoxon_test": {
                "w_statistic": round(w_stat, 4) if w_stat is not None else None,
                "p_value": round(w_pvalue, 6) if w_pvalue is not None else None,
                "significant_at_0.05": w_pvalue < 0.05 if w_pvalue is not None else None
            },
            "effect_size": {
                "cohens_d": round(cohens_d, 4) if cohens_d is not None else None,
                "interpretation": interpret_cohens_d(cohens_d) if cohens_d is not None else None
            }
        },
        "conclusion": {
            "hypothesis_confirmed": hypothesis_confirmed,
            "interpretation": generate_interpretation(
                before_mean, after_mean, t_pvalue, hypothesis_confirmed
            )
        },
        "event_details": event_details,
        "methodology": {
            "near_miss_ratio_formula": "count(9/10 winners) / max(count(10/10 winners), 1)",
            "statistical_tests_used": ["Paired t-test", "Wilcoxon signed-rank test"],
            "significance_level": 0.05,
            "data_sources": [
                "Keno_GPTs/10-9_KGDaten_gefiltert.csv",
                "Keno_GPTs/Keno_GQ_2022_2023-2024.csv"
            ]
        }
    }


def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d effect size"""
    d = abs(d)
    if d < 0.2:
        return "negligible"
    elif d < 0.5:
        return "small"
    elif d < 0.8:
        return "medium"
    else:
        return "large"


def generate_interpretation(before_mean: float, after_mean: float,
                            p_value: float, confirmed: bool) -> str:
    """Generate human-readable interpretation"""
    if confirmed:
        return (
            f"CONFIRMED: Near-Miss Ratio is significantly higher before GK1 events "
            f"(before: {before_mean:.2f} vs after: {after_mean:.2f}, p={p_value:.4f}). "
            f"This supports the hypothesis that near-misses increase before big wins."
        )
    elif p_value is not None and p_value < 0.1:
        return (
            f"TREND: There is a trend suggesting higher Near-Miss Ratio before GK1 events "
            f"(before: {before_mean:.2f} vs after: {after_mean:.2f}, p={p_value:.4f}), "
            f"but it does not reach statistical significance at alpha=0.05."
        )
    else:
        p_str = f"{p_value:.4f}" if p_value is not None else "N/A"
        return (
            f"FALSIFIED: No significant difference in Near-Miss Ratio before vs after GK1 events "
            f"(before: {before_mean:.2f} vs after: {after_mean:.2f}, p={p_str}). "
            f"The hypothesis is not supported by the data."
        )


def main():
    """Main analysis function"""
    base_path = Path(__file__).parent.parent

    # Load data
    print("Loading GK1 events...")
    gk1_events = load_gk1_events(base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv")
    print(f"  Found {len(gk1_events)} GK1 events")

    print("Loading winning quotas...")
    quotas_df = load_winning_quotas(base_path / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv")
    print(f"  Loaded {len(quotas_df)} records")
    print(f"  Date range: {quotas_df['Datum'].min()} to {quotas_df['Datum'].max()}")

    # Run analysis with 7-day window
    print("\nAnalyzing PRED-001 with 7-day window...")
    results_7d = analyze_pred001(gk1_events, quotas_df, window_days=7)

    # Also run with 14-day window for comparison
    print("Analyzing PRED-001 with 14-day window...")
    results_14d = analyze_pred001(gk1_events, quotas_df, window_days=14)

    # Combine results
    final_results = {
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "primary_analysis_7d": results_7d,
        "sensitivity_analysis_14d": results_14d,
        "overall_conclusion": {
            "hypothesis_id": "PRED-001",
            "status": "CONFIRMED" if results_7d["conclusion"]["hypothesis_confirmed"] else "FALSIFIED",
            "robustness": "Both 7d and 14d windows show consistent results"
                if results_7d["conclusion"]["hypothesis_confirmed"] == results_14d["conclusion"]["hypothesis_confirmed"]
                else "Results vary by window size - inconclusive"
        }
    }

    # Save results
    output_path = base_path / "results" / "pred001_pre_gk1_analysis.json"

    # Custom JSON encoder for numpy types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

    print(f"\nResults saved to: {output_path}")
    print(f"\n{'='*60}")
    print(f"PRED-001 Analysis Summary")
    print(f"{'='*60}")
    print(f"Events analyzed: {results_7d['n_events_analyzed']}")
    print(f"7-day window:")
    print(f"  Before GK1: {results_7d['summary']['before_gk1']['mean_ratio']:.4f}")
    print(f"  After GK1:  {results_7d['summary']['after_gk1']['mean_ratio']:.4f}")
    print(f"  p-value:    {results_7d['statistical_tests']['paired_ttest']['p_value']}")
    print(f"  Status:     {final_results['overall_conclusion']['status']}")
    print(f"{'='*60}")

    return final_results


if __name__ == "__main__":
    main()
