#!/usr/bin/env python3
"""
Backtest: 1 Monat nach Jackpot (GK10_10)

Testet Performance der optimalen Tickets im Monat nach einem Jackpot.
Hypothese WL-003: Nach Reset-Zyklus (Jackpot) aendert sich das Systemverhalten.
Hypothese HYP_002: High-Wins (>=100 EUR) sind im Cooldown unterdrueckt.

Autor: Kenobase V2.2
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

# High-Win threshold (EUR)
HIGH_WIN_THRESHOLD = 100


# KENO Gewinnquoten (fixed per 1 EUR Einsatz): `kenobase.core.keno_quotes.get_fixed_quote`

# Optimale Tickets
OPTIMAL_TICKETS = {
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
    7: [3, 24, 30, 49, 51, 59, 64],
    6: [3, 9, 10, 32, 49, 64],
}


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


def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> int:
    """Simuliert ein Ticket und gibt Gewinn zurueck."""
    hits = sum(1 for n in ticket if n in draw_set)
    return int(get_fixed_quote(keno_type, hits))


def backtest_period(
    keno_df: pd.DataFrame,
    start_date: datetime,
    days: int,
    tickets: Dict[int, List[int]]
) -> Dict:
    """Fuehrt Backtest fuer eine Periode durch."""
    end_date = start_date + timedelta(days=days)

    period_df = keno_df[
        (keno_df["Datum"] > start_date) &
        (keno_df["Datum"] <= end_date)
    ]

    results = {
        "start": str(start_date.date()),
        "end": str(end_date.date()),
        "draws": len(period_df),
        "by_type": {}
    }

    for keno_type, ticket in tickets.items():
        invested = 0
        won = 0
        wins_by_hits = defaultdict(int)
        daily_results = []
        high_wins_count = 0  # HYP_002: Count wins >= HIGH_WIN_THRESHOLD

        for _, row in period_df.iterrows():
            draw_set = row["numbers_set"]
            win = simulate_ticket(ticket, keno_type, draw_set)
            hits = sum(1 for n in ticket if n in draw_set)

            invested += 1
            won += win
            wins_by_hits[hits] += 1
            if win >= HIGH_WIN_THRESHOLD:
                high_wins_count += 1
            daily_results.append({
                "date": str(row["Datum"].date()),
                "hits": hits,
                "win": win
            })

        roi = (won - invested) / invested if invested > 0 else 0

        results["by_type"][f"typ_{keno_type}"] = {
            "ticket": ticket,
            "invested": invested,
            "won": won,
            "roi": round(roi * 100, 2),
            "avg_hits": round(np.mean([d["hits"] for d in daily_results]), 2) if daily_results else 0,
            "max_hits": max([d["hits"] for d in daily_results]) if daily_results else 0,
            "wins_by_hits": dict(wins_by_hits),
            "best_day": max(daily_results, key=lambda x: x["win"]) if daily_results else None,
            "high_wins_count": high_wins_count,  # HYP_002
            "high_wins_rate": round(high_wins_count / len(period_df) * 100, 2) if len(period_df) > 0 else 0
        }

    return results


def analyze_post_jackpot(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    days_after: int = 30
) -> Dict:
    """Analysiert Performance im Monat nach jedem Jackpot."""

    all_results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "jackpots_analyzed": len(jackpot_dates),
            "days_after_jackpot": days_after
        },
        "jackpot_periods": [],
        "aggregated": {}
    }

    # Fuer jeden Jackpot
    for jp_date in jackpot_dates:
        print(f"\nJackpot: {jp_date.date()}")

        period_result = backtest_period(
            keno_df,
            jp_date,
            days_after,
            OPTIMAL_TICKETS
        )
        period_result["jackpot_date"] = str(jp_date.date())

        all_results["jackpot_periods"].append(period_result)

        # Zeige ROI pro Typ
        for typ, data in period_result["by_type"].items():
            print(f"  {typ}: ROI {data['roi']:+.1f}%, Max Hits: {data['max_hits']}")

    # Aggregiere ueber alle Jackpot-Perioden
    print("\n" + "=" * 70)
    print("AGGREGIERTE ERGEBNISSE (alle Post-Jackpot Perioden)")
    print("=" * 70)

    for keno_type in OPTIMAL_TICKETS.keys():
        typ_key = f"typ_{keno_type}"

        total_invested = sum(p["by_type"][typ_key]["invested"] for p in all_results["jackpot_periods"])
        total_won = sum(p["by_type"][typ_key]["won"] for p in all_results["jackpot_periods"])

        rois = [p["by_type"][typ_key]["roi"] for p in all_results["jackpot_periods"]]
        avg_hits = [p["by_type"][typ_key]["avg_hits"] for p in all_results["jackpot_periods"]]
        max_hits = [p["by_type"][typ_key]["max_hits"] for p in all_results["jackpot_periods"]]

        overall_roi = (total_won - total_invested) / total_invested * 100 if total_invested > 0 else 0

        # HYP_002: High-Wins aggregation
        total_high_wins = sum(
            p["by_type"][typ_key]["high_wins_count"]
            for p in all_results["jackpot_periods"]
        )
        high_wins_rates = [
            p["by_type"][typ_key]["high_wins_rate"]
            for p in all_results["jackpot_periods"]
        ]

        all_results["aggregated"][typ_key] = {
            "ticket": OPTIMAL_TICKETS[keno_type],
            "total_invested": total_invested,
            "total_won": total_won,
            "overall_roi": round(overall_roi, 2),
            "avg_roi_per_period": round(np.mean(rois), 2),
            "std_roi": round(np.std(rois), 2),
            "avg_hits": round(np.mean(avg_hits), 2),
            "max_hits_ever": max(max_hits),
            "periods_positive": sum(1 for r in rois if r > 0),
            "total_periods": len(rois),
            # HYP_002 fields
            "total_high_wins": total_high_wins,
            "avg_high_wins_rate": round(np.mean(high_wins_rates), 2),
        }

        print(f"\nTYP {keno_type}:")
        print(f"  Ticket: {OPTIMAL_TICKETS[keno_type]}")
        print(f"  Gesamt ROI: {overall_roi:+.1f}%")
        print(f"  Durchschn. ROI pro Periode: {np.mean(rois):+.1f}% (+/- {np.std(rois):.1f}%)")
        print(f"  Positive Perioden: {sum(1 for r in rois if r > 0)}/{len(rois)}")
        print(f"  Durchschn. Treffer: {np.mean(avg_hits):.2f}")
        print(f"  Max Treffer: {max(max_hits)}")

    return all_results


def compare_to_normal_periods(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    days: int = 30
) -> Dict:
    """Vergleicht Post-Jackpot mit normalen Perioden."""

    # Finde normale Perioden (nicht im Monat nach Jackpot)
    all_dates = set(keno_df["Datum"].dt.date)
    post_jp_dates = set()

    for jp_date in jackpot_dates:
        for d in range(1, days + 1):
            post_jp_dates.add((jp_date + timedelta(days=d)).date())

    normal_dates = all_dates - post_jp_dates

    # Sample normale Perioden
    normal_starts = []
    sorted_normal = sorted(normal_dates)

    # Nehme jeden 30. Tag als Start einer normalen Periode
    for i in range(0, len(sorted_normal) - days, 30):
        start = pd.Timestamp(sorted_normal[i])
        # Pruefe ob die naechsten 30 Tage alle normal sind
        valid = True
        for d in range(days):
            check_date = (start + timedelta(days=d)).date()
            if check_date in post_jp_dates:
                valid = False
                break
        if valid:
            normal_starts.append(start)

    print(f"\nVergleiche {len(jackpot_dates)} Post-Jackpot vs {len(normal_starts)} normale Perioden")

    # Backtest normale Perioden
    normal_results = []
    for start in normal_starts[:len(jackpot_dates)]:  # Gleiche Anzahl
        result = backtest_period(keno_df, start, days, OPTIMAL_TICKETS)
        normal_results.append(result)

    # Vergleich
    comparison = {}

    for keno_type in OPTIMAL_TICKETS.keys():
        typ_key = f"typ_{keno_type}"

        # Post-Jackpot (bereits berechnet)
        # Normal
        normal_rois = [r["by_type"][typ_key]["roi"] for r in normal_results]

        # HYP_002: High-Wins comparison
        normal_high_wins = sum(
            r["by_type"][typ_key]["high_wins_count"]
            for r in normal_results
        )
        normal_draws = sum(r["draws"] for r in normal_results)
        normal_high_wins_rate = (
            round(normal_high_wins / normal_draws * 100, 2)
            if normal_draws > 0 else 0
        )

        comparison[typ_key] = {
            "normal_avg_roi": round(np.mean(normal_rois), 2),
            "normal_std": round(np.std(normal_rois), 2),
            # HYP_002 fields
            "normal_high_wins": normal_high_wins,
            "normal_draws": normal_draws,
            "normal_high_wins_rate": normal_high_wins_rate,
        }

    return comparison, normal_results


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("BACKTEST: 1 MONAT NACH JACKPOT (GK10_10)")
    print("=" * 70)

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

    if not keno_path or not gk1_path.exists():
        print("FEHLER: Datendateien nicht gefunden!")
        return

    print(f"\nLade Daten...")
    keno_df, gk1_df = load_data(str(keno_path), str(gk1_path))

    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  GK10_10 Jackpots: {len(gk1_df)}")

    jackpot_dates = gk1_df["Datum"].tolist()
    print(f"\nJackpot-Daten:")
    for jp in jackpot_dates:
        winners = gk1_df[gk1_df["Datum"] == jp]["Anzahl der Gewinner"].values[0]
        print(f"  {jp.date()} - {int(winners)} Gewinner")

    # Post-Jackpot Analyse
    print("\n" + "=" * 70)
    print("ANALYSE: 30 TAGE NACH JEDEM JACKPOT")
    print("=" * 70)

    results = analyze_post_jackpot(keno_df, jackpot_dates, days_after=30)

    # Vergleich mit normalen Perioden
    print("\n" + "=" * 70)
    print("VERGLEICH: POST-JACKPOT VS NORMALE PERIODEN")
    print("=" * 70)

    comparison, normal_results = compare_to_normal_periods(keno_df, jackpot_dates, days=30)

    print("\n" + "-" * 70)
    print(f"{'Typ':<8} {'Post-JP ROI':>15} {'Normal ROI':>15} {'Differenz':>15}")
    print("-" * 70)

    for keno_type in OPTIMAL_TICKETS.keys():
        typ_key = f"typ_{keno_type}"
        post_jp_roi = results["aggregated"][typ_key]["avg_roi_per_period"]
        normal_roi = comparison[typ_key]["normal_avg_roi"]
        diff = post_jp_roi - normal_roi

        print(f"Typ {keno_type:<4} {post_jp_roi:>+14.1f}% {normal_roi:>+14.1f}% {diff:>+14.1f}%")

        results["aggregated"][typ_key]["normal_avg_roi"] = normal_roi
        results["aggregated"][typ_key]["difference"] = round(diff, 2)

    # =========================================================================
    # HYP_002: HIGH-WINS COOLDOWN ANALYSIS
    # =========================================================================
    print("\n" + "=" * 70)
    print("HYP_002: HIGH-WINS (>=100 EUR) COOLDOWN ANALYSE")
    print("=" * 70)

    hyp002_results = {
        "hypothesis": "HYP_002",
        "description": "High-Wins (>=100 EUR) sind im Post-Jackpot Cooldown unterdrueckt",
        "threshold_eur": HIGH_WIN_THRESHOLD,
        "by_type": {},
        "overall": {}
    }

    print(f"\nHigh-Win Schwelle: >= {HIGH_WIN_THRESHOLD} EUR")
    print("\n" + "-" * 70)
    print(f"{'Typ':<8} {'Cooldown HW':>12} {'Normal HW':>12} {'CD Rate':>10} {'N Rate':>10} {'Chi2':>8} {'p-Wert':>10}")
    print("-" * 70)

    total_cooldown_hw = 0
    total_normal_hw = 0
    total_cooldown_draws = 0
    total_normal_draws = 0

    for keno_type in OPTIMAL_TICKETS.keys():
        typ_key = f"typ_{keno_type}"

        # Cooldown (post-jackpot) high-wins
        cooldown_hw = results["aggregated"][typ_key]["total_high_wins"]
        cooldown_draws = results["aggregated"][typ_key]["total_invested"]
        cooldown_rate = cooldown_hw / cooldown_draws * 100 if cooldown_draws > 0 else 0

        # Normal period high-wins
        normal_hw = comparison[typ_key]["normal_high_wins"]
        normal_draws = comparison[typ_key]["normal_draws"]
        normal_rate = normal_hw / normal_draws * 100 if normal_draws > 0 else 0

        # Chi-square test: 2x2 contingency table
        # [cooldown_hw, cooldown_no_hw], [normal_hw, normal_no_hw]
        contingency = [
            [cooldown_hw, cooldown_draws - cooldown_hw],
            [normal_hw, normal_draws - normal_hw]
        ]

        # Only run chi-square if we have sufficient data
        if cooldown_hw + normal_hw >= 5:
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        else:
            chi2, p_value = 0.0, 1.0  # Insufficient data

        print(f"Typ {keno_type:<4} {cooldown_hw:>12} {normal_hw:>12} {cooldown_rate:>9.2f}% {normal_rate:>9.2f}% {chi2:>8.2f} {p_value:>10.4f}")

        # Store results
        hyp002_results["by_type"][typ_key] = {
            "cooldown_high_wins": cooldown_hw,
            "cooldown_draws": cooldown_draws,
            "cooldown_rate_pct": round(cooldown_rate, 2),
            "normal_high_wins": normal_hw,
            "normal_draws": normal_draws,
            "normal_rate_pct": round(normal_rate, 2),
            "chi2": round(chi2, 4),
            "p_value": round(p_value, 4),
            "significant": p_value < 0.05,
            "direction": "SUPPRESSED" if cooldown_rate < normal_rate else "NOT_SUPPRESSED"
        }

        # Update in aggregated results
        results["aggregated"][typ_key]["normal_high_wins"] = normal_hw
        results["aggregated"][typ_key]["normal_high_wins_rate"] = round(normal_rate, 2)
        results["aggregated"][typ_key]["hyp002_chi2"] = round(chi2, 4)
        results["aggregated"][typ_key]["hyp002_p_value"] = round(p_value, 4)

        # Accumulate totals
        total_cooldown_hw += cooldown_hw
        total_normal_hw += normal_hw
        total_cooldown_draws += cooldown_draws
        total_normal_draws += normal_draws

    # Overall chi-square test
    overall_contingency = [
        [total_cooldown_hw, total_cooldown_draws - total_cooldown_hw],
        [total_normal_hw, total_normal_draws - total_normal_hw]
    ]

    if total_cooldown_hw + total_normal_hw >= 5:
        overall_chi2, overall_p, _, _ = stats.chi2_contingency(overall_contingency)
    else:
        overall_chi2, overall_p = 0.0, 1.0

    overall_cooldown_rate = total_cooldown_hw / total_cooldown_draws * 100 if total_cooldown_draws > 0 else 0
    overall_normal_rate = total_normal_hw / total_normal_draws * 100 if total_normal_draws > 0 else 0

    print("-" * 70)
    print(f"{'GESAMT':<8} {total_cooldown_hw:>12} {total_normal_hw:>12} {overall_cooldown_rate:>9.2f}% {overall_normal_rate:>9.2f}% {overall_chi2:>8.2f} {overall_p:>10.4f}")

    hyp002_results["overall"] = {
        "cooldown_high_wins": total_cooldown_hw,
        "cooldown_draws": total_cooldown_draws,
        "cooldown_rate_pct": round(overall_cooldown_rate, 2),
        "normal_high_wins": total_normal_hw,
        "normal_draws": total_normal_draws,
        "normal_rate_pct": round(overall_normal_rate, 2),
        "chi2": round(overall_chi2, 4),
        "p_value": round(overall_p, 4),
        "significant": overall_p < 0.05,
        "direction": "SUPPRESSED" if overall_cooldown_rate < overall_normal_rate else "NOT_SUPPRESSED"
    }

    # Add HYP_002 to results
    results["hyp002"] = hyp002_results

    # HYP_002 Conclusion
    print("\n" + "-" * 70)
    print("HYP_002 ERGEBNIS:")
    if overall_p < 0.05:
        if overall_cooldown_rate < overall_normal_rate:
            print(f"  BESTAETIGT: High-Wins im Cooldown signifikant UNTERDRUECKT")
            print(f"  Cooldown: {overall_cooldown_rate:.2f}% vs Normal: {overall_normal_rate:.2f}%")
            print(f"  Chi2={overall_chi2:.2f}, p={overall_p:.4f}")
            hyp002_results["conclusion"] = "CONFIRMED"
        else:
            print(f"  WIDERLEGT: High-Wins im Cooldown signifikant ERHOET")
            hyp002_results["conclusion"] = "FALSIFIED_INVERSE"
    else:
        print(f"  NICHT SIGNIFIKANT: p={overall_p:.4f} > 0.05")
        print(f"  Cooldown: {overall_cooldown_rate:.2f}% vs Normal: {overall_normal_rate:.2f}%")
        print(f"  Hinweis: Geringe Sample Size (HW={total_cooldown_hw + total_normal_hw})")
        hyp002_results["conclusion"] = "NOT_SIGNIFICANT"

    # Speichern
    output_path = base_path / "results" / "post_jackpot_backtest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    # Finde besten Typ nach Jackpot
    best_type = max(
        results["aggregated"].items(),
        key=lambda x: x[1]["avg_roi_per_period"]
    )

    print(f"""
ERKENNTNIS - POST-JACKPOT PERFORMANCE:

Bester Typ nach Jackpot: {best_type[0].upper()}
  Ticket: {best_type[1]['ticket']}
  Durchschn. ROI: {best_type[1]['avg_roi_per_period']:+.1f}%
  vs Normal: {best_type[1].get('difference', 0):+.1f}% Unterschied

Positive Perioden: {best_type[1]['periods_positive']}/{best_type[1]['total_periods']}

RESET-ZYKLUS HYPOTHESE:
""")

    # Pruefe ob Post-Jackpot besser oder schlechter ist
    avg_diff = np.mean([
        results["aggregated"][f"typ_{t}"].get("difference", 0)
        for t in OPTIMAL_TICKETS.keys()
    ])

    if avg_diff > 5:
        print(f"  BESTAETIGT: Post-Jackpot ist {avg_diff:.1f}% BESSER als normal!")
        print("  -> System scheint nach Reset 'grosszuegiger' zu sein")
    elif avg_diff < -5:
        print(f"  BESTAETIGT: Post-Jackpot ist {abs(avg_diff):.1f}% SCHLECHTER als normal!")
        print("  -> System scheint nach Jackpot 'sparsamer' zu sein")
    else:
        print(f"  NICHT SIGNIFIKANT: Nur {avg_diff:.1f}% Unterschied")
        print("  -> Kein klarer Reset-Effekt erkennbar")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
