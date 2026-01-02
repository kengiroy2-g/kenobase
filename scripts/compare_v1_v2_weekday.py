#!/usr/bin/env python3
"""
V1 vs V2 Weekday Comparison (TASK_039b)

Compares ROI per weekday for V1 (Original) vs V2 (Birthday-Avoidance) tickets.

V1 Tickets: Original OPTIMAL_TICKETS (includes birthday numbers)
V2 Tickets: Birthday-Avoidance (excludes birthday numbers 1-31 where possible)

Acceptance Criteria:
- Compare ROI difference V2-V1 per weekday for each Keno type
- Multiple-testing correction (BH) for 7 weekdays
- Nullmodell: weekday-preserving shuffle permutation test

Output: results/v1_v2_weekday_comparison.json
"""

import json
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from kenobase.core.keno_quotes import get_fixed_quote


# ============================================================================
# TICKET DEFINITIONS (from backtest_birthday_cooldown.py lines 37-52)
# ============================================================================

# V1: Original OPTIMAL_TICKETS (from backtest_post_jackpot.py)
V1_TICKETS = {
    6: [3, 9, 10, 32, 49, 64],
    7: [3, 24, 30, 49, 51, 59, 64],
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
}

# V2: Birthday-Avoidance Tickets (from super_model_synthesis.py)
V2_TICKETS = {
    6: [3, 36, 51, 58, 61, 64],
    7: [3, 36, 43, 51, 58, 61, 64],
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}

WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


# ============================================================================
# DATA LOADING
# ============================================================================

def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Load KENO data from CSV (2022-2025)."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(
        lambda row: set(row.dropna().astype(int)), axis=1
    )
    df["weekday"] = df["Datum"].dt.dayofweek

    return df.dropna(subset=["Datum"]).sort_values("Datum").reset_index(drop=True)


# ============================================================================
# SIMULATION
# ============================================================================

def simulate_ticket(ticket: list[int], keno_type: int, draw_set: set) -> float:
    """Simulate payout for a ticket against a draw."""
    hits = sum(1 for n in ticket if n in draw_set)
    return get_fixed_quote(keno_type, hits)


def compute_weekday_roi(
    df: pd.DataFrame, ticket: list[int], keno_type: int
) -> dict[str, dict]:
    """Compute ROI per weekday for a given ticket."""
    results = {}
    for wd in range(7):
        subset = df[df["weekday"] == wd]
        n = len(subset)
        if n < 5:
            results[WEEKDAYS_DE[wd]] = {
                "n": n, "roi_pct": None, "invested": n, "winnings": 0
            }
            continue

        winnings = sum(
            simulate_ticket(ticket, keno_type, row["numbers_set"])
            for _, row in subset.iterrows()
        )
        invested = n  # 1 EUR per draw
        roi_pct = ((winnings - invested) / invested) * 100 if invested > 0 else 0.0

        results[WEEKDAYS_DE[wd]] = {
            "n": n,
            "invested": invested,
            "winnings": round(winnings, 2),
            "roi_pct": round(roi_pct, 2),
        }

    return results


# ============================================================================
# NULLMODELL: WEEKDAY-PRESERVING SHUFFLE
# ============================================================================

def weekday_shuffle_test(
    df: pd.DataFrame,
    v1_ticket: list[int],
    v2_ticket: list[int],
    keno_type: int,
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict:
    """Nullmodell: Shuffle weekday assignments and compute V2-V1 difference spread.

    Tests whether observed V2-V1 ROI difference per weekday is significant.
    """
    random.seed(seed)
    np.random.seed(seed)

    # Observed ROI per weekday
    v1_roi = compute_weekday_roi(df, v1_ticket, keno_type)
    v2_roi = compute_weekday_roi(df, v2_ticket, keno_type)

    # Compute observed difference per weekday
    observed_diffs = []
    for wd in WEEKDAYS_DE:
        if v1_roi[wd]["roi_pct"] is not None and v2_roi[wd]["roi_pct"] is not None:
            observed_diffs.append(v2_roi[wd]["roi_pct"] - v1_roi[wd]["roi_pct"])

    if len(observed_diffs) < 2:
        return {"p_value": 1.0, "observed_spread": 0.0, "null_spreads": []}

    observed_spread = max(observed_diffs) - min(observed_diffs)
    observed_mean_diff = np.mean(observed_diffs)

    # Permutation test: shuffle weekday assignments
    null_spreads = []
    null_mean_diffs = []

    for _ in range(n_permutations):
        shuffled_df = df.copy()
        shuffled_weekdays = shuffled_df["weekday"].tolist()
        random.shuffle(shuffled_weekdays)
        shuffled_df["weekday"] = shuffled_weekdays

        # Compute ROI for shuffled data
        v1_shuffled = compute_weekday_roi(shuffled_df, v1_ticket, keno_type)
        v2_shuffled = compute_weekday_roi(shuffled_df, v2_ticket, keno_type)

        shuffled_diffs = []
        for wd in WEEKDAYS_DE:
            if (v1_shuffled[wd]["roi_pct"] is not None and
                    v2_shuffled[wd]["roi_pct"] is not None):
                shuffled_diffs.append(
                    v2_shuffled[wd]["roi_pct"] - v1_shuffled[wd]["roi_pct"]
                )

        if len(shuffled_diffs) >= 2:
            null_spreads.append(max(shuffled_diffs) - min(shuffled_diffs))
            null_mean_diffs.append(np.mean(shuffled_diffs))

    # P-value for spread
    p_value_spread = (
        sum(1 for ns in null_spreads if ns >= observed_spread) / len(null_spreads)
        if null_spreads else 1.0
    )

    # P-value for mean difference (two-sided)
    p_value_mean = (
        sum(1 for nd in null_mean_diffs if abs(nd) >= abs(observed_mean_diff))
        / len(null_mean_diffs)
        if null_mean_diffs else 1.0
    )

    return {
        "p_value_spread": round(p_value_spread, 4),
        "p_value_mean_diff": round(p_value_mean, 4),
        "observed_spread": round(observed_spread, 2),
        "observed_mean_diff": round(observed_mean_diff, 2),
        "n_permutations": n_permutations,
        "null_mean_spread": round(np.mean(null_spreads), 2) if null_spreads else 0.0,
        "null_std_spread": round(np.std(null_spreads), 2) if null_spreads else 0.0,
    }


# ============================================================================
# BENJAMINI-HOCHBERG CORRECTION
# ============================================================================

def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> list[bool]:
    """Apply Benjamini-Hochberg FDR correction to a list of p-values.

    Returns list of booleans indicating whether each test is significant.
    """
    n = len(p_values)
    if n == 0:
        return []

    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    significant = [False] * n

    for rank, (orig_idx, p) in enumerate(indexed, 1):
        threshold = (rank / n) * alpha
        if p <= threshold:
            significant[orig_idx] = True

    return significant


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("=" * 70)
    print("V1 vs V2 WEEKDAY COMPARISON (TASK_039b)")
    print("=" * 70)

    base_path = Path(__file__).parent.parent
    df = load_keno_data(base_path)
    n_draws = len(df)

    print(f"\nDaten: {n_draws} Ziehungen")
    print(f"Zeitraum: {df['Datum'].min().date()} bis {df['Datum'].max().date()}")
    print(f"\nV1 = Original OPTIMAL_TICKETS")
    print(f"V2 = Birthday-Avoidance Tickets")

    # Results container
    results = {
        "task": "TASK_039b",
        "analysis": "V1 vs V2 Weekday Comparison",
        "data": {
            "n_draws": n_draws,
            "date_range": {
                "start": str(df["Datum"].min().date()),
                "end": str(df["Datum"].max().date()),
            },
        },
        "v1_tickets": V1_TICKETS,
        "v2_tickets": V2_TICKETS,
        "weekday_labels": WEEKDAYS_DE,
        "by_type": {},
        "aggregated": {},
        "nullmodell_tests": {},
        "statistical_summary": {},
        "timestamp": datetime.now().isoformat(),
    }

    # Analyze each Keno type
    all_p_values = []  # For BH correction

    for keno_type in sorted(V1_TICKETS.keys()):
        print(f"\n{'=' * 70}")
        print(f"KENO TYP {keno_type}")
        print("=" * 70)

        v1_ticket = V1_TICKETS[keno_type]
        v2_ticket = V2_TICKETS[keno_type]

        print(f"  V1 Ticket: {v1_ticket}")
        print(f"  V2 Ticket: {v2_ticket}")

        # Compute ROI per weekday
        v1_roi = compute_weekday_roi(df, v1_ticket, keno_type)
        v2_roi = compute_weekday_roi(df, v2_ticket, keno_type)

        print(f"\n{'Wochentag':<10} {'V1 ROI':>10} {'V2 ROI':>10} {'Diff':>10}")
        print("-" * 45)

        weekday_data = {}
        diffs = []

        for wd in WEEKDAYS_DE:
            v1_val = v1_roi[wd]["roi_pct"]
            v2_val = v2_roi[wd]["roi_pct"]

            if v1_val is not None and v2_val is not None:
                diff = v2_val - v1_val
                diffs.append(diff)
                print(f"{wd:<10} {v1_val:>+9.1f}% {v2_val:>+9.1f}% {diff:>+9.1f}%")
            else:
                diff = None
                print(f"{wd:<10} {'N/A':>10} {'N/A':>10} {'N/A':>10}")

            weekday_data[wd] = {
                "v1": v1_roi[wd],
                "v2": v2_roi[wd],
                "diff_pct": round(diff, 2) if diff is not None else None,
            }

        # Summary for this type
        if diffs:
            avg_diff = np.mean(diffs)
            std_diff = np.std(diffs)
            best_diff = max(diffs)
            worst_diff = min(diffs)
            best_wd = [wd for wd in WEEKDAYS_DE if weekday_data[wd]["diff_pct"] == round(best_diff, 2)][0]
            worst_wd = [wd for wd in WEEKDAYS_DE if weekday_data[wd]["diff_pct"] == round(worst_diff, 2)][0]

            print(f"\n  Avg V2-V1 Diff: {avg_diff:+.2f}% (std: {std_diff:.2f}%)")
            print(f"  Best for V2: {best_wd} ({best_diff:+.1f}%)")
            print(f"  Worst for V2: {worst_wd} ({worst_diff:+.1f}%)")
        else:
            avg_diff = 0.0
            std_diff = 0.0
            best_diff = 0.0
            worst_diff = 0.0
            best_wd = "N/A"
            worst_wd = "N/A"

        # Nullmodell test
        print("\n  Nullmodell (weekday shuffle, 1000 permutations)...")
        null_result = weekday_shuffle_test(df, v1_ticket, v2_ticket, keno_type)
        print(f"    p-value (spread): {null_result['p_value_spread']:.4f}")
        print(f"    p-value (mean diff): {null_result['p_value_mean_diff']:.4f}")

        all_p_values.append(null_result["p_value_mean_diff"])

        # Store results
        results["by_type"][f"typ_{keno_type}"] = {
            "v1_ticket": v1_ticket,
            "v2_ticket": v2_ticket,
            "weekday_roi": weekday_data,
            "summary": {
                "avg_diff_pct": round(avg_diff, 2),
                "std_diff_pct": round(std_diff, 2),
                "best_day_for_v2": best_wd,
                "best_diff_pct": round(best_diff, 2),
                "worst_day_for_v2": worst_wd,
                "worst_diff_pct": round(worst_diff, 2),
                "v2_better_days": sum(1 for d in diffs if d > 0),
                "v1_better_days": sum(1 for d in diffs if d < 0),
            },
        }
        results["nullmodell_tests"][f"typ_{keno_type}"] = null_result

    # =========================================================================
    # BENJAMINI-HOCHBERG CORRECTION
    # =========================================================================
    print("\n" + "=" * 70)
    print("BENJAMINI-HOCHBERG KORREKTUR (5 Tests fuer 5 Keno-Typen)")
    print("=" * 70)

    bh_significant = benjamini_hochberg(all_p_values, alpha=0.05)

    for i, keno_type in enumerate(sorted(V1_TICKETS.keys())):
        typ_key = f"typ_{keno_type}"
        p_val = all_p_values[i]
        sig = bh_significant[i]
        results["nullmodell_tests"][typ_key]["bh_significant"] = sig
        print(f"  Typ {keno_type}: p={p_val:.4f} -> {'SIGNIFICANT' if sig else 'not significant'}")

    # =========================================================================
    # AGGREGATED SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("AGGREGIERTE ERGEBNISSE")
    print("=" * 70)

    # Aggregate across all types
    all_avg_diffs = [
        results["by_type"][f"typ_{kt}"]["summary"]["avg_diff_pct"]
        for kt in sorted(V1_TICKETS.keys())
    ]

    overall_avg_diff = np.mean(all_avg_diffs)
    overall_std_diff = np.std(all_avg_diffs)

    # Count how many types favor V2 on average
    v2_better_types = sum(1 for d in all_avg_diffs if d > 0)
    v1_better_types = sum(1 for d in all_avg_diffs if d < 0)

    # Count significant tests after BH correction
    significant_count = sum(bh_significant)

    print(f"\n  Overall Avg V2-V1 Diff: {overall_avg_diff:+.2f}% (std: {overall_std_diff:.2f}%)")
    print(f"  V2 better in {v2_better_types}/5 types (on average)")
    print(f"  V1 better in {v1_better_types}/5 types (on average)")
    print(f"  Significant tests (BH-corrected): {significant_count}/5")

    results["aggregated"] = {
        "overall_avg_diff_pct": round(overall_avg_diff, 2),
        "overall_std_diff_pct": round(overall_std_diff, 2),
        "v2_better_types": v2_better_types,
        "v1_better_types": v1_better_types,
        "significant_tests_bh": significant_count,
        "total_types": 5,
    }

    # =========================================================================
    # FINAL VERDICT
    # =========================================================================
    print("\n" + "=" * 70)
    print("FAZIT")
    print("=" * 70)

    if significant_count > 0:
        if overall_avg_diff > 0:
            verdict = "V2_SIGNIFICANTLY_BETTER"
            message = f"V2 signifikant besser in {significant_count}/5 Typen (Avg: {overall_avg_diff:+.2f}%)"
        else:
            verdict = "V1_SIGNIFICANTLY_BETTER"
            message = f"V1 signifikant besser in {significant_count}/5 Typen (Avg: {overall_avg_diff:+.2f}%)"
    elif overall_avg_diff > 5:
        verdict = "V2_TREND_BETTER"
        message = f"V2 tendenziell besser (Avg: {overall_avg_diff:+.2f}%), aber nicht signifikant"
    elif overall_avg_diff < -5:
        verdict = "V1_TREND_BETTER"
        message = f"V1 tendenziell besser (Avg: {overall_avg_diff:+.2f}%), aber nicht signifikant"
    else:
        verdict = "NO_CLEAR_DIFFERENCE"
        message = f"Kein klarer Unterschied (Avg: {overall_avg_diff:+.2f}%)"

    print(f"\n  Status: {verdict}")
    print(f"  {message}")

    results["verdict"] = {
        "status": verdict,
        "message": message,
        "interpretation": (
            "Die Weekday-Analyse vergleicht V1 (Original) mit V2 (Birthday-Avoidance) "
            "Tickets ueber 7 Wochentage und 5 Keno-Typen. "
            "Nullmodell: Weekday-Shuffle-Permutationstest. "
            "Multiple-Testing: Benjamini-Hochberg Korrektur."
        ),
    }

    # Save results
    output_path = base_path / "results" / "v1_v2_weekday_comparison.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {output_path}")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
