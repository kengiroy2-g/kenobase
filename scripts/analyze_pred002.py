#!/usr/bin/env python
"""
PRED-002: Waiting Time Analysis for GK1 Events

Hypothesis: After long periods without GK1 events (>30-50 days),
the probability of a GK1 event should increase.

Analysis:
1. Calculate waiting times between all GK1 events
2. Analyze conditional probabilities:
   - P(GK1 in next 7 days | days since last GK1 < 20)
   - P(GK1 in next 7 days | days since last GK1 = 20-40)
   - P(GK1 in next 7 days | days since last GK1 > 40)
3. Test for trend: Does P(GK1) increase with waiting time?
4. Perform Chi-Square test
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def load_gk1_data(filepath: str) -> pd.DataFrame:
    """Load and parse GK1 data."""
    df = pd.read_csv(filepath)
    df.columns = ["Datum", "Keno_Typ", "Anzahl_Gewinner", "Tage_seit_letztem_GK1"]

    # Parse dates (German format: DD.MM.YYYY)
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    return df


def create_daily_series(df: pd.DataFrame) -> pd.DataFrame:
    """Create a daily time series with GK1 events marked."""
    start_date = df["Datum"].min()
    end_date = df["Datum"].max()

    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    daily_df = pd.DataFrame({"Datum": date_range})

    # Mark GK1 events
    gk1_dates = set(df["Datum"].dt.date)
    daily_df["is_gk1"] = daily_df["Datum"].dt.date.isin(gk1_dates).astype(int)

    # Calculate days since last GK1
    days_since_gk1 = []
    last_gk1_idx = -1

    for i, row in daily_df.iterrows():
        if row["is_gk1"] == 1:
            days_since_gk1.append(0)
            last_gk1_idx = i
        elif last_gk1_idx >= 0:
            days_since_gk1.append(i - last_gk1_idx)
        else:
            days_since_gk1.append(np.nan)

    daily_df["days_since_last_gk1"] = days_since_gk1

    # Check if GK1 occurs in next 7 days
    gk1_in_next_7 = []
    for i in range(len(daily_df)):
        window_end = min(i + 8, len(daily_df))  # +8 because we check next 7 days (days 1-7)
        has_gk1 = daily_df.iloc[i+1:window_end]["is_gk1"].sum() > 0 if i + 1 < len(daily_df) else False
        gk1_in_next_7.append(int(has_gk1))

    daily_df["gk1_in_next_7_days"] = gk1_in_next_7

    return daily_df


def analyze_conditional_probabilities(daily_df: pd.DataFrame) -> dict:
    """
    Calculate conditional probabilities for GK1 events based on waiting time.
    """
    # Filter out NaN values and days where GK1 occurred (we want days WAITING)
    valid_df = daily_df[
        (daily_df["days_since_last_gk1"].notna()) &
        (daily_df["days_since_last_gk1"] > 0)
    ].copy()

    # Define waiting time categories
    categories = {
        "short_wait_lt20": valid_df["days_since_last_gk1"] < 20,
        "medium_wait_20_40": (valid_df["days_since_last_gk1"] >= 20) & (valid_df["days_since_last_gk1"] <= 40),
        "long_wait_gt40": valid_df["days_since_last_gk1"] > 40
    }

    results = {}
    contingency_data = []

    for cat_name, mask in categories.items():
        cat_df = valid_df[mask]
        n_total = len(cat_df)
        n_gk1 = cat_df["gk1_in_next_7_days"].sum()

        if n_total > 0:
            p_gk1 = n_gk1 / n_total
            # Wilson confidence interval
            z = 1.96
            denominator = 1 + z**2 / n_total
            center = (p_gk1 + z**2 / (2 * n_total)) / denominator
            margin = z * np.sqrt((p_gk1 * (1 - p_gk1) + z**2 / (4 * n_total)) / n_total) / denominator
            ci_lower = max(0, center - margin)
            ci_upper = min(1, center + margin)
        else:
            p_gk1 = np.nan
            ci_lower = np.nan
            ci_upper = np.nan

        results[cat_name] = {
            "n_days": int(n_total),
            "n_gk1_events": int(n_gk1),
            "p_gk1_next_7_days": float(p_gk1) if not np.isnan(p_gk1) else None,
            "ci_95_lower": float(ci_lower) if not np.isnan(ci_lower) else None,
            "ci_95_upper": float(ci_upper) if not np.isnan(ci_upper) else None
        }

        # For contingency table
        contingency_data.append([int(n_gk1), int(n_total - n_gk1)])

    return results, np.array(contingency_data)


def perform_chi_square_test(contingency_table: np.ndarray) -> dict:
    """
    Perform Chi-Square test to check if probabilities differ across categories.
    """
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

    return {
        "chi2_statistic": float(chi2),
        "p_value": float(p_value),
        "degrees_of_freedom": int(dof),
        "expected_frequencies": expected.tolist()
    }


def test_trend(conditional_probs: dict) -> dict:
    """
    Test if P(GK1) increases with waiting time (Cochran-Armitage trend test approximation).
    """
    categories = ["short_wait_lt20", "medium_wait_20_40", "long_wait_gt40"]

    probs = []
    n_values = []

    for cat in categories:
        if conditional_probs[cat]["p_gk1_next_7_days"] is not None:
            probs.append(conditional_probs[cat]["p_gk1_next_7_days"])
            n_values.append(conditional_probs[cat]["n_days"])

    if len(probs) < 3:
        return {"trend_detected": False, "reason": "Insufficient data in categories"}

    # Simple linear regression on proportions
    x = np.array([1, 2, 3])  # Ordinal scores for categories
    y = np.array(probs)

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # Trend is increasing if slope > 0 and significant
    trend_increasing = slope > 0 and p_value < 0.05

    return {
        "slope": float(slope),
        "r_squared": float(r_value**2),
        "p_value_trend": float(p_value),
        "trend_direction": "increasing" if slope > 0 else "decreasing",
        "trend_significant": bool(p_value < 0.05),
        "hypothesis_supported": bool(trend_increasing)
    }


def calculate_waiting_time_statistics(df: pd.DataFrame) -> dict:
    """Calculate statistics on waiting times between GK1 events."""
    waiting_times = df["Tage_seit_letztem_GK1"].dropna().values
    waiting_times = waiting_times[waiting_times > 0]  # Exclude same-day events

    return {
        "n_events": int(len(df)),
        "n_waiting_periods": int(len(waiting_times)),
        "mean_waiting_days": float(np.mean(waiting_times)),
        "median_waiting_days": float(np.median(waiting_times)),
        "std_waiting_days": float(np.std(waiting_times)),
        "min_waiting_days": int(np.min(waiting_times)),
        "max_waiting_days": int(np.max(waiting_times)),
        "waiting_times": [int(w) for w in waiting_times]
    }


def main():
    """Main analysis function."""
    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    data_path = base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv"
    output_path = base_path / "results" / "pred002_waiting_time_analysis.json"

    print("=" * 60)
    print("PRED-002: Waiting Time Analysis for GK1 Events")
    print("=" * 60)

    # Load data
    print("\n1. Loading GK1 data...")
    df = load_gk1_data(data_path)
    print(f"   Loaded {len(df)} GK1 events from {df['Datum'].min().date()} to {df['Datum'].max().date()}")

    # Calculate waiting time statistics
    print("\n2. Calculating waiting time statistics...")
    waiting_stats = calculate_waiting_time_statistics(df)
    print(f"   Mean waiting time: {waiting_stats['mean_waiting_days']:.1f} days")
    print(f"   Median waiting time: {waiting_stats['median_waiting_days']:.1f} days")
    print(f"   Range: {waiting_stats['min_waiting_days']} - {waiting_stats['max_waiting_days']} days")

    # Create daily series
    print("\n3. Creating daily time series...")
    daily_df = create_daily_series(df)
    print(f"   Created series with {len(daily_df)} days")

    # Analyze conditional probabilities
    print("\n4. Analyzing conditional probabilities...")
    conditional_probs, contingency_table = analyze_conditional_probabilities(daily_df)

    for cat, stats_dict in conditional_probs.items():
        p = stats_dict["p_gk1_next_7_days"]
        n = stats_dict["n_days"]
        if p is not None:
            print(f"   {cat}: P(GK1|wait) = {p:.4f} (n={n})")

    # Chi-Square test
    print("\n5. Performing Chi-Square test...")
    chi_square_results = perform_chi_square_test(contingency_table)
    print(f"   Chi-Square = {chi_square_results['chi2_statistic']:.4f}")
    print(f"   p-value = {chi_square_results['p_value']:.4f}")

    # Trend test
    print("\n6. Testing for increasing trend...")
    trend_results = test_trend(conditional_probs)
    print(f"   Slope = {trend_results['slope']:.6f}")
    print(f"   Trend direction: {trend_results['trend_direction']}")
    print(f"   Trend significant (p<0.05): {trend_results['trend_significant']}")

    # Compile results
    alpha = 0.05
    hypothesis_confirmed = (
        trend_results.get("hypothesis_supported", False) and
        chi_square_results["p_value"] < alpha
    )

    result = {
        "hypothesis": "PRED-002",
        "description": "Long jackpot-free periods increase P(GK1)",
        "analysis_date": datetime.now().isoformat(),
        "data_period": {
            "start": df["Datum"].min().isoformat(),
            "end": df["Datum"].max().isoformat(),
            "total_gk1_events": int(len(df))
        },
        "waiting_time_statistics": waiting_stats,
        "conditional_probabilities": conditional_probs,
        "chi_square_test": chi_square_results,
        "trend_analysis": trend_results,
        "conclusion": {
            "hypothesis_confirmed": bool(hypothesis_confirmed),
            "alpha_level": alpha,
            "interpretation": (
                "The hypothesis is CONFIRMED: P(GK1) increases significantly with waiting time."
                if hypothesis_confirmed else
                "The hypothesis is FALSIFIED: P(GK1) does NOT significantly increase with waiting time. "
                "GK1 events appear to follow a memoryless (random) process."
            ),
            "evidence_summary": {
                "chi_square_p_value": chi_square_results["p_value"],
                "trend_p_value": trend_results.get("p_value_trend"),
                "trend_direction": trend_results.get("trend_direction"),
                "p_short_wait": conditional_probs["short_wait_lt20"]["p_gk1_next_7_days"],
                "p_medium_wait": conditional_probs["medium_wait_20_40"]["p_gk1_next_7_days"],
                "p_long_wait": conditional_probs["long_wait_gt40"]["p_gk1_next_7_days"]
            }
        }
    }

    # Print conclusion
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    status = "CONFIRMED" if hypothesis_confirmed else "FALSIFIED"
    print(f"\nPRED-002 Status: {status}")
    print(f"\n{result['conclusion']['interpretation']}")

    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nResults saved to: {output_path}")

    return result


if __name__ == "__main__":
    main()
