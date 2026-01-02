#!/usr/bin/env python3
"""
Weekday-ROI Analysis (TASK_013)

Tests whether ROI varies significantly by day of week for V2-Tickets.

Acceptance criteria:
- ROI_diff >= 20% between best/worst weekday OR
- p < 0.05 Chi-square for draw frequency

Nullmodell: Weekday-preserving shuffle (compare shuffled draws within same weekday)

Output: results/weekday_roi_analysis.json
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

from kenobase.analysis.temporal_cycles import analyze_dimension
from kenobase.core.keno_quotes import get_fixed_quote


# V2 Birthday-Avoidance Ticket Type 9 (standard recommendation)
TICKET_V2_TYPE9 = [3, 7, 36, 43, 48, 51, 58, 61, 64]

WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Load KENO data from CSV."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(
        lambda row: set(row.dropna().astype(int)), axis=1
    )
    df["weekday"] = df["Datum"].dt.dayofweek

    return df.dropna(subset=["Datum"]).sort_values("Datum").reset_index(drop=True)


def simulate_ticket(ticket: list[int], keno_type: int, draw_set: set) -> float:
    """Simulate payout for a ticket against a draw."""
    hits = sum(1 for n in ticket if n in draw_set)
    return get_fixed_quote(keno_type, hits)


def compute_weekday_roi(df: pd.DataFrame, ticket: list[int], keno_type: int) -> dict:
    """Compute ROI per weekday for a given ticket."""
    results = {}
    for wd in range(7):
        subset = df[df["weekday"] == wd]
        n = len(subset)
        if n < 5:
            results[WEEKDAYS_DE[wd]] = {"n": n, "roi_pct": None, "invested": n, "winnings": 0}
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


def weekday_shuffle_test(
    df: pd.DataFrame,
    ticket: list[int],
    keno_type: int,
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict:
    """Nullmodell: Shuffle weekday assignments.

    Randomly reassigns weekdays to draws (breaking weekday-ROI correlation)
    while preserving overall draw distribution.

    Returns p-value for observed ROI spread being due to chance.
    """
    random.seed(seed)
    np.random.seed(seed)

    # Observed ROI per weekday
    observed_roi = compute_weekday_roi(df, ticket, keno_type)
    observed_values = [
        v["roi_pct"] for v in observed_roi.values() if v["roi_pct"] is not None
    ]
    if len(observed_values) < 2:
        return {"p_value": 1.0, "observed_spread": 0.0, "null_spreads": []}

    observed_spread = max(observed_values) - min(observed_values)

    # Permutation test: shuffle weekday assignments across all draws
    null_spreads = []
    for _ in range(n_permutations):
        # Shuffle weekday column (breaks weekday-draw correlation)
        shuffled_df = df.copy()
        shuffled_weekdays = shuffled_df["weekday"].tolist()
        random.shuffle(shuffled_weekdays)
        shuffled_df["weekday"] = shuffled_weekdays

        # Compute ROI spread for shuffled data
        shuffled_roi = compute_weekday_roi(shuffled_df, ticket, keno_type)
        shuffled_values = [
            v["roi_pct"] for v in shuffled_roi.values() if v["roi_pct"] is not None
        ]
        if len(shuffled_values) >= 2:
            null_spreads.append(max(shuffled_values) - min(shuffled_values))

    # P-value: proportion of null spreads >= observed spread
    p_value = (
        sum(1 for ns in null_spreads if ns >= observed_spread) / len(null_spreads)
        if null_spreads
        else 1.0
    )

    return {
        "p_value": round(p_value, 4),
        "observed_spread": round(observed_spread, 2),
        "n_permutations": n_permutations,
        "null_mean_spread": round(np.mean(null_spreads), 2) if null_spreads else 0.0,
        "null_std_spread": round(np.std(null_spreads), 2) if null_spreads else 0.0,
    }


def main():
    print("=" * 70)
    print("WEEKDAY-ROI ANALYSIS (TASK_013)")
    print("=" * 70)

    base_path = Path(__file__).parent.parent
    df = load_keno_data(base_path)
    n_draws = len(df)

    print(f"\nDaten: {n_draws} Ziehungen")
    print(f"Zeitraum: {df['Datum'].min().date()} bis {df['Datum'].max().date()}")

    # 1. Chi-square test for draw frequency per weekday
    print("\n1. CHI-SQUARE: Ziehungsverteilung nach Wochentag")
    print("-" * 50)

    dates = df["Datum"].tolist()
    chi_result = analyze_dimension(dates, "weekday", alpha=0.05)

    print(f"   Chi-square: {chi_result.chi2_statistic:.3f}")
    print(f"   p-value: {chi_result.p_value:.4f}")
    print(f"   Signifikant: {chi_result.is_significant}")
    print(f"   {chi_result.interpretation}")

    # 2. ROI per weekday for V2-Ticket Type 9
    print("\n2. ROI PRO WOCHENTAG (V2-Ticket Typ 9)")
    print("-" * 50)

    weekday_roi = compute_weekday_roi(df, TICKET_V2_TYPE9, keno_type=9)

    print(f"{'Wochentag':<10} {'N':>6} {'Invested':>10} {'Winnings':>10} {'ROI':>10}")
    print("-" * 50)

    roi_values = []
    for wd_name, stats_dict in weekday_roi.items():
        if stats_dict["roi_pct"] is not None:
            roi_values.append(stats_dict["roi_pct"])
            print(
                f"{wd_name:<10} {stats_dict['n']:>6} "
                f"{stats_dict['invested']:>10} {stats_dict['winnings']:>10.2f} "
                f"{stats_dict['roi_pct']:>+9.1f}%"
            )
        else:
            print(f"{wd_name:<10} {stats_dict['n']:>6} {'---':>10} {'---':>10} {'N/A':>10}")

    # Best/worst weekday
    if roi_values:
        best_roi = max(roi_values)
        worst_roi = min(roi_values)
        roi_spread = best_roi - worst_roi

        best_day = [k for k, v in weekday_roi.items() if v["roi_pct"] == best_roi][0]
        worst_day = [k for k, v in weekday_roi.items() if v["roi_pct"] == worst_roi][0]

        print(f"\n   Bester Tag: {best_day} ({best_roi:+.1f}%)")
        print(f"   Schlechtester Tag: {worst_day} ({worst_roi:+.1f}%)")
        print(f"   ROI-Spread: {roi_spread:.1f}%")
    else:
        roi_spread = 0.0
        best_day = "N/A"
        worst_day = "N/A"

    # 3. Nullmodell: Weekday-preserving shuffle
    print("\n3. NULLMODELL: Weekday-Preserving Shuffle (1000 Permutationen)")
    print("-" * 50)

    shuffle_result = weekday_shuffle_test(df, TICKET_V2_TYPE9, keno_type=9)

    print(f"   Beobachteter ROI-Spread: {shuffle_result['observed_spread']:.1f}%")
    print(f"   Null-Modell Spread (mean): {shuffle_result['null_mean_spread']:.1f}%")
    print(f"   Null-Modell Spread (std): {shuffle_result['null_std_spread']:.1f}%")
    print(f"   Permutations-p-value: {shuffle_result['p_value']:.4f}")

    # 4. Acceptance criteria
    print("\n4. ACCEPTANCE CRITERIA")
    print("-" * 50)

    criterion_roi = roi_spread >= 20.0
    criterion_chi = chi_result.p_value < 0.05
    criterion_null = shuffle_result["p_value"] < 0.05

    print(f"   ROI-Spread >= 20%: {roi_spread:.1f}% -> {'PASS' if criterion_roi else 'FAIL'}")
    print(f"   Chi-square p < 0.05: {chi_result.p_value:.4f} -> {'PASS' if criterion_chi else 'FAIL'}")
    print(f"   Nullmodell p < 0.05: {shuffle_result['p_value']:.4f} -> {'PASS' if criterion_null else 'FAIL'}")

    # Final verdict
    if criterion_roi or criterion_chi:
        verdict = "CONFIRMED"
        confidence = "HIGH" if criterion_roi and criterion_chi else "MEDIUM"
    else:
        verdict = "NOT_CONFIRMED"
        confidence = "LOW"

    if criterion_null:
        verdict_null = "SIGNIFICANT"
    else:
        verdict_null = "NOT_SIGNIFICANT"

    print(f"\n   VERDICT: {verdict} (Confidence: {confidence})")
    print(f"   Nullmodell-Verdict: Weekday-Effekt ist {verdict_null}")

    # Build result object
    result = {
        "task": "TASK_013",
        "analysis": "Weekday-ROI Analysis",
        "data": {
            "n_draws": n_draws,
            "date_range": {
                "start": str(df["Datum"].min().date()),
                "end": str(df["Datum"].max().date()),
            },
            "ticket": TICKET_V2_TYPE9,
            "keno_type": 9,
        },
        "chi_square_test": {
            "dimension": chi_result.dimension,
            "chi2_statistic": float(chi_result.chi2_statistic),
            "p_value": float(chi_result.p_value),
            "degrees_of_freedom": int(chi_result.degrees_of_freedom),
            "is_significant": bool(chi_result.is_significant),
            "interpretation": chi_result.interpretation,
            "observed_counts": [int(c) for c in chi_result.observed_counts],
            "expected_counts": [round(float(e), 2) for e in chi_result.expected_counts],
            "labels": chi_result.labels,
        },
        "weekday_roi": weekday_roi,
        "roi_summary": {
            "best_day": best_day,
            "worst_day": worst_day,
            "roi_spread_pct": round(roi_spread, 2),
        },
        "nullmodell": shuffle_result,
        "acceptance": {
            "roi_spread_criterion": {
                "threshold": 20.0,
                "observed": round(roi_spread, 2),
                "passed": bool(criterion_roi),
            },
            "chi_square_criterion": {
                "threshold": 0.05,
                "observed": float(chi_result.p_value),
                "passed": bool(criterion_chi),
            },
            "nullmodell_criterion": {
                "threshold": 0.05,
                "observed": float(shuffle_result["p_value"]),
                "passed": bool(criterion_null),
            },
        },
        "verdict": {
            "weekday_effect": verdict,
            "confidence": confidence,
            "nullmodell_verdict": verdict_null,
        },
        "timestamp": datetime.now().isoformat(),
    }

    # Save results
    output_path = base_path / "results" / "weekday_roi_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n   Output: {output_path}")
    print("=" * 70)

    return result


if __name__ == "__main__":
    main()
