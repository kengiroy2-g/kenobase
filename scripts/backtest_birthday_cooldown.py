#!/usr/bin/env python3
"""
HYP_005: Birthday-Avoidance V2 im Post-Jackpot Cooldown

Testet ob V2 (Anti-Birthday) Tickets im Cooldown nach Jackpot
besser performen als V1 (Original) Tickets.

Hypothese: Birthday-Zahlen (1-31) sind bei Jackpots unterrepraesentiert,
daher sollte V2 (ohne Birthday-Zahlen) im Cooldown besser abschneiden.

Acceptance Criteria:
- p < 0.05 (Chi-Square Test)
- V2 ROI > V1 ROI im Cooldown

Autor: Kenobase V2.2 - HYP_005
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
from scipy import stats

from kenobase.core.keno_quotes import get_fixed_quote


# ============================================================================
# TICKET DEFINITIONS
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

# Cooldown period (days after jackpot)
COOLDOWN_DAYS = 30


# ============================================================================
# DATA LOADING
# ============================================================================

def load_data(keno_path: str, gk1_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Laedt KENO Ziehungen und GK1 Events."""
    # KENO Ziehungen
    keno_df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    keno_df["Datum"] = pd.to_datetime(keno_df["Datum"], format="%d.%m.%Y")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    keno_df["numbers_set"] = keno_df[pos_cols].apply(lambda row: set(row), axis=1)
    keno_df = keno_df.sort_values("Datum").reset_index(drop=True)

    # GK1 Events (Jackpots)
    gk1_df = pd.read_csv(gk1_path, encoding="utf-8")
    gk1_df["Datum"] = pd.to_datetime(gk1_df["Datum"], format="%d.%m.%Y")

    # Nur Typ 10 Jackpots
    gk1_typ10 = gk1_df[gk1_df["Keno-Typ"] == 10].copy()

    return keno_df, gk1_typ10


# ============================================================================
# SIMULATION
# ============================================================================

def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simuliert ein Ticket und gibt (Gewinn, Hits) zurueck."""
    hits = sum(1 for n in ticket if n in draw_set)
    win = int(get_fixed_quote(keno_type, hits))
    return win, hits


def backtest_strategy(
    keno_df: pd.DataFrame,
    start_date: datetime,
    days: int,
    tickets: Dict[int, List[int]],
    strategy_name: str
) -> Dict:
    """Fuehrt Backtest fuer eine Strategie/Periode durch."""
    end_date = start_date + timedelta(days=days)

    period_df = keno_df[
        (keno_df["Datum"] > start_date) &
        (keno_df["Datum"] <= end_date)
    ]

    results = {
        "strategy": strategy_name,
        "start": str(start_date.date()),
        "end": str(end_date.date()),
        "draws": len(period_df),
        "by_type": {}
    }

    for keno_type, ticket in tickets.items():
        invested = 0
        won = 0
        wins_by_hits = defaultdict(int)
        daily_wins = []

        for _, row in period_df.iterrows():
            draw_set = row["numbers_set"]
            win, hits = simulate_ticket(ticket, keno_type, draw_set)

            invested += 1
            won += win
            wins_by_hits[hits] += 1
            daily_wins.append(win)

        roi = (won - invested) / invested if invested > 0 else 0

        results["by_type"][f"typ_{keno_type}"] = {
            "ticket": ticket,
            "invested": invested,
            "won": won,
            "roi_pct": round(roi * 100, 2),
            "wins_by_hits": dict(wins_by_hits),
            "daily_wins": daily_wins
        }

    return results


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_birthday_cooldown(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime]
) -> Dict:
    """Vergleicht V1 vs V2 im Post-Jackpot Cooldown."""

    all_results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "hypothesis": "HYP_005",
            "description": "Birthday-Avoidance V2 vs V1 im Post-Jackpot Cooldown",
            "acceptance_criteria": "p<0.05 AND V2_ROI > V1_ROI",
            "jackpots_analyzed": len(jackpot_dates),
            "cooldown_days": COOLDOWN_DAYS
        },
        "v1_tickets": V1_TICKETS,
        "v2_tickets": V2_TICKETS,
        "jackpot_periods": [],
        "aggregated": {},
        "statistical_tests": {}
    }

    print("=" * 70)
    print("HYP_005: BIRTHDAY-AVOIDANCE V2 IM POST-JACKPOT COOLDOWN")
    print("=" * 70)
    print(f"\nJackpots analysiert: {len(jackpot_dates)}")
    print(f"Cooldown-Periode: {COOLDOWN_DAYS} Tage")

    # Fuer jeden Jackpot
    for jp_date in jackpot_dates:
        print(f"\n  Jackpot: {jp_date.date()}")

        v1_result = backtest_strategy(
            keno_df, jp_date, COOLDOWN_DAYS, V1_TICKETS, "V1_Original"
        )
        v2_result = backtest_strategy(
            keno_df, jp_date, COOLDOWN_DAYS, V2_TICKETS, "V2_Birthday_Avoidance"
        )

        period_data = {
            "jackpot_date": str(jp_date.date()),
            "v1": v1_result,
            "v2": v2_result
        }

        all_results["jackpot_periods"].append(period_data)

        # Zeige ROI pro Typ
        for keno_type in sorted(V1_TICKETS.keys()):
            typ_key = f"typ_{keno_type}"
            v1_roi = v1_result["by_type"][typ_key]["roi_pct"]
            v2_roi = v2_result["by_type"][typ_key]["roi_pct"]
            diff = v2_roi - v1_roi
            print(f"    Typ {keno_type}: V1={v1_roi:+.1f}%, V2={v2_roi:+.1f}%, Diff={diff:+.1f}%")

    # =========================================================================
    # AGGREGATION
    # =========================================================================
    print("\n" + "=" * 70)
    print("AGGREGIERTE ERGEBNISSE")
    print("=" * 70)

    for keno_type in sorted(V1_TICKETS.keys()):
        typ_key = f"typ_{keno_type}"

        # V1 aggregation
        v1_total_invested = sum(
            p["v1"]["by_type"][typ_key]["invested"]
            for p in all_results["jackpot_periods"]
        )
        v1_total_won = sum(
            p["v1"]["by_type"][typ_key]["won"]
            for p in all_results["jackpot_periods"]
        )
        v1_rois = [
            p["v1"]["by_type"][typ_key]["roi_pct"]
            for p in all_results["jackpot_periods"]
        ]
        v1_daily_wins = []
        for p in all_results["jackpot_periods"]:
            v1_daily_wins.extend(p["v1"]["by_type"][typ_key]["daily_wins"])

        # V2 aggregation
        v2_total_invested = sum(
            p["v2"]["by_type"][typ_key]["invested"]
            for p in all_results["jackpot_periods"]
        )
        v2_total_won = sum(
            p["v2"]["by_type"][typ_key]["won"]
            for p in all_results["jackpot_periods"]
        )
        v2_rois = [
            p["v2"]["by_type"][typ_key]["roi_pct"]
            for p in all_results["jackpot_periods"]
        ]
        v2_daily_wins = []
        for p in all_results["jackpot_periods"]:
            v2_daily_wins.extend(p["v2"]["by_type"][typ_key]["daily_wins"])

        # Calculate overall ROI
        v1_overall_roi = (v1_total_won - v1_total_invested) / v1_total_invested * 100 if v1_total_invested > 0 else 0
        v2_overall_roi = (v2_total_won - v2_total_invested) / v2_total_invested * 100 if v2_total_invested > 0 else 0

        all_results["aggregated"][typ_key] = {
            "v1": {
                "ticket": V1_TICKETS[keno_type],
                "total_invested": v1_total_invested,
                "total_won": v1_total_won,
                "overall_roi_pct": round(v1_overall_roi, 2),
                "avg_roi_per_period": round(np.mean(v1_rois), 2),
                "std_roi": round(np.std(v1_rois), 2),
            },
            "v2": {
                "ticket": V2_TICKETS[keno_type],
                "total_invested": v2_total_invested,
                "total_won": v2_total_won,
                "overall_roi_pct": round(v2_overall_roi, 2),
                "avg_roi_per_period": round(np.mean(v2_rois), 2),
                "std_roi": round(np.std(v2_rois), 2),
            },
            "roi_difference_pct": round(v2_overall_roi - v1_overall_roi, 2),
            "v2_better": v2_overall_roi > v1_overall_roi
        }

        print(f"\nTYP {keno_type}:")
        print(f"  V1 Ticket: {V1_TICKETS[keno_type]}")
        print(f"  V1 ROI: {v1_overall_roi:+.2f}%")
        print(f"  V2 Ticket: {V2_TICKETS[keno_type]}")
        print(f"  V2 ROI: {v2_overall_roi:+.2f}%")
        print(f"  Differenz (V2-V1): {v2_overall_roi - v1_overall_roi:+.2f}%")

        # =====================================================================
        # STATISTICAL TEST: Mann-Whitney U (non-parametric) for daily wins
        # =====================================================================
        if len(v1_daily_wins) >= 5 and len(v2_daily_wins) >= 5:
            # Mann-Whitney U test (non-parametric alternative to t-test)
            u_stat, p_value_mw = stats.mannwhitneyu(
                v2_daily_wins, v1_daily_wins, alternative='greater'
            )

            # Also Welch's t-test for comparison
            t_stat, p_value_t = stats.ttest_ind(
                v2_daily_wins, v1_daily_wins, equal_var=False
            )
            # One-sided p-value
            p_value_t_onesided = p_value_t / 2 if t_stat > 0 else 1 - p_value_t / 2

            all_results["statistical_tests"][typ_key] = {
                "mann_whitney": {
                    "u_statistic": round(u_stat, 2),
                    "p_value": round(p_value_mw, 6),
                    "significant": p_value_mw < 0.05,
                    "alternative": "V2 > V1"
                },
                "welch_t_test": {
                    "t_statistic": round(t_stat, 2),
                    "p_value_onesided": round(p_value_t_onesided, 6),
                    "significant": p_value_t_onesided < 0.05
                },
                "n_v1": len(v1_daily_wins),
                "n_v2": len(v2_daily_wins),
                "v1_mean_win": round(np.mean(v1_daily_wins), 2),
                "v2_mean_win": round(np.mean(v2_daily_wins), 2)
            }

            print(f"  Mann-Whitney U: p={p_value_mw:.4f} {'*' if p_value_mw < 0.05 else ''}")
        else:
            all_results["statistical_tests"][typ_key] = {
                "error": "Insufficient data for statistical test",
                "n_v1": len(v1_daily_wins),
                "n_v2": len(v2_daily_wins)
            }
            print(f"  WARNUNG: Zu wenig Daten fuer statistischen Test")

    # =========================================================================
    # OVERALL CONCLUSION
    # =========================================================================
    print("\n" + "=" * 70)
    print("HYP_005 GESAMTERGEBNIS")
    print("=" * 70)

    # Count how many types show V2 > V1
    v2_wins = sum(
        1 for typ_key in all_results["aggregated"]
        if all_results["aggregated"][typ_key]["v2_better"]
    )
    total_types = len(all_results["aggregated"])

    # Count significant tests
    significant_tests = sum(
        1 for typ_key in all_results["statistical_tests"]
        if all_results["statistical_tests"][typ_key].get("mann_whitney", {}).get("significant", False)
    )

    # Average ROI difference
    avg_roi_diff = np.mean([
        all_results["aggregated"][typ_key]["roi_difference_pct"]
        for typ_key in all_results["aggregated"]
    ])

    # Conclusion
    if significant_tests > 0 and avg_roi_diff > 0:
        conclusion = "CONFIRMED"
        message = f"V2 signifikant besser in {significant_tests}/{total_types} Typen, Avg Diff: {avg_roi_diff:+.2f}%"
    elif avg_roi_diff > 0:
        conclusion = "TREND_V2_BETTER"
        message = f"V2 besser in {v2_wins}/{total_types} Typen, aber nicht signifikant (p>=0.05)"
    elif avg_roi_diff < 0:
        conclusion = "FALSIFIED"
        message = f"V1 besser als V2, Avg Diff: {avg_roi_diff:+.2f}%"
    else:
        conclusion = "INCONCLUSIVE"
        message = "Kein klarer Unterschied zwischen V1 und V2"

    all_results["conclusion"] = {
        "status": conclusion,
        "message": message,
        "v2_better_types": v2_wins,
        "total_types": total_types,
        "significant_tests": significant_tests,
        "avg_roi_difference_pct": round(avg_roi_diff, 2),
        "acceptance_met": conclusion == "CONFIRMED"
    }

    print(f"\nStatus: {conclusion}")
    print(f"Ergebnis: {message}")
    print(f"V2 besser in: {v2_wins}/{total_types} Typen")
    print(f"Signifikante Tests (p<0.05): {significant_tests}/{total_types}")
    print(f"Durchschnittliche ROI-Differenz: {avg_roi_diff:+.2f}%")

    return all_results


def main():
    """Hauptfunktion."""
    base_path = Path(__file__).parent.parent

    # Datenpfade
    keno_paths = [
        base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    ]
    gk1_path = base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv"

    keno_path = None
    for p in keno_paths:
        if p.exists():
            keno_path = p
            break

    if not keno_path:
        print("FEHLER: KENO Datendatei nicht gefunden!")
        print(f"  Gesucht: {keno_paths}")
        return

    if not gk1_path.exists():
        print(f"FEHLER: GK1 Datendatei nicht gefunden: {gk1_path}")
        return

    print(f"Lade Daten...")
    print(f"  KENO: {keno_path}")
    print(f"  GK1: {gk1_path}")

    keno_df, gk1_df = load_data(str(keno_path), str(gk1_path))

    print(f"\n  KENO Ziehungen: {len(keno_df)}")
    print(f"  GK10_10 Jackpots: {len(gk1_df)}")

    jackpot_dates = gk1_df["Datum"].tolist()

    # Run analysis
    results = analyze_birthday_cooldown(keno_df, jackpot_dates)

    # Save results
    output_path = base_path / "results" / "hyp005_birthday_cooldown.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
