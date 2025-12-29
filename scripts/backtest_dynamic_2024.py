#!/usr/bin/env python3
"""
Backtest: Dynamisches Empfehlungssystem ueber 2024

Testet das komplette System inkl. Jackpot-Warnung:
1. Exclusion-Regeln
2. Inclusion-Boost
3. Korrelierte Absenzen
4. Jackpot-Warnung (NICHT SPIELEN 30 Tage nach Jackpot)

Vergleicht:
- MIT Jackpot-Warnung (Skip Post-Jackpot Perioden)
- OHNE Jackpot-Warnung (immer spielen)

Autor: Kenobase V2.2
Datum: 2025-12-29
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pandas as pd
import numpy as np

# Import from dynamic_recommendation
import sys
sys.path.insert(0, str(Path(__file__).parent))

from dynamic_recommendation import (
    OPTIMAL_TICKETS,
    MULTI_EXCLUSION_RULES,
    INCLUSION_RULES,
    CORRELATED_ABSENCES,
    HOT_NUMBERS,
    CORE_NUMBERS,
    JACKPOT_COOLDOWN_DAYS,
    apply_exclusion_rules,
    apply_inclusion_boost,
    apply_absence_correlations,
    generate_dynamic_ticket,
    load_jackpot_dates,
    check_jackpot_warning
)

# KENO Gewinnquoten
KENO_QUOTES = {
    2: {2: 6, 1: 0, 0: 0},
    3: {3: 16, 2: 1, 1: 0, 0: 0},
    4: {4: 22, 3: 2, 2: 1, 1: 0, 0: 0},
    5: {5: 100, 4: 7, 3: 2, 2: 0, 1: 0, 0: 0},
    6: {6: 500, 5: 15, 4: 5, 3: 1, 2: 0, 1: 0, 0: 0},
    7: {7: 1000, 6: 100, 5: 12, 4: 4, 3: 1, 2: 0, 1: 0, 0: 0},
    8: {8: 10000, 7: 1000, 6: 100, 5: 10, 4: 2, 3: 0, 2: 0, 1: 0, 0: 0},
    9: {9: 50000, 8: 5000, 7: 500, 6: 50, 5: 10, 4: 2, 3: 0, 2: 0, 1: 0, 0: 0},
    10: {10: 100000, 9: 10000, 8: 1000, 7: 100, 6: 15, 5: 5, 4: 0, 3: 0, 2: 0, 1: 0, 0: 2}
}


def load_keno_data(path: str) -> pd.DataFrame:
    """Laedt KENO Ziehungsdaten."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["positions"] = df[pos_cols].apply(lambda row: list(row), axis=1)
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row), axis=1)

    return df.sort_values("Datum").reset_index(drop=True)


def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simuliert ein Ticket und gibt (Gewinn, Treffer) zurueck."""
    hits = sum(1 for n in ticket if n in draw_set)
    win = KENO_QUOTES.get(keno_type, {}).get(hits, 0)
    return win, hits


def backtest_month(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    year: int,
    month: int,
    use_jackpot_warning: bool = True
) -> Dict:
    """Fuehrt Backtest fuer einen Monat durch."""

    # Filter auf Monat
    month_df = keno_df[
        (keno_df["Datum"].dt.year == year) &
        (keno_df["Datum"].dt.month == month)
    ].copy()

    if len(month_df) < 2:
        return None

    results = {
        "year": year,
        "month": month,
        "draws": len(month_df) - 1,  # -1 weil wir Tag vorher brauchen
        "use_jackpot_warning": use_jackpot_warning,
        "skipped_days": 0,
        "played_days": 0,
        "by_type": {}
    }

    # Fuer jeden Typ
    for keno_type in [9, 8, 10, 7, 6]:
        invested = 0
        won = 0
        wins_by_hits = defaultdict(int)
        daily_results = []
        skipped = 0

        # Iteriere ueber Tage (ab Tag 2, weil wir Tag vorher brauchen)
        for i in range(1, len(month_df)):
            prev_row = month_df.iloc[i - 1]
            curr_row = month_df.iloc[i]

            today_date = curr_row["Datum"]

            # Pruefe Jackpot-Warnung
            if use_jackpot_warning:
                jp_warning = check_jackpot_warning(today_date, jackpot_dates)
                if jp_warning["in_cooldown"]:
                    skipped += 1
                    continue

            # Generiere dynamisches Ticket basierend auf Vortag
            prev_positions = prev_row["positions"]
            prev_set = prev_row["numbers_set"]
            prev_absent = set(range(1, 71)) - prev_set

            exclude = apply_exclusion_rules(prev_positions)
            boost = apply_inclusion_boost(prev_positions)
            likely_absent = apply_absence_correlations(prev_absent)

            ticket = generate_dynamic_ticket(keno_type, exclude, boost, likely_absent)

            # Simuliere gegen heutige Ziehung
            draw_set = curr_row["numbers_set"]
            win, hits = simulate_ticket(ticket, keno_type, draw_set)

            invested += 1
            won += win
            wins_by_hits[hits] += 1

            daily_results.append({
                "date": str(today_date.date()),
                "ticket": ticket,
                "hits": hits,
                "win": win,
                "exclusions": sorted(exclude),
                "boosts": boost
            })

        if keno_type == 9:
            results["skipped_days"] = skipped
            results["played_days"] = len(daily_results)

        roi = (won - invested) / invested * 100 if invested > 0 else 0

        results["by_type"][f"typ_{keno_type}"] = {
            "invested": invested,
            "won": won,
            "roi": round(roi, 2),
            "avg_hits": round(np.mean([d["hits"] for d in daily_results]), 2) if daily_results else 0,
            "max_hits": max([d["hits"] for d in daily_results]) if daily_results else 0,
            "wins_by_hits": dict(wins_by_hits),
            "best_day": max(daily_results, key=lambda x: x["win"]) if daily_results else None
        }

    return results


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("BACKTEST: DYNAMISCHES EMPFEHLUNGSSYSTEM 2024")
    print("=" * 70)
    print()

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
        print("FEHLER: Keine KENO-Datendatei gefunden!")
        return

    print(f"Lade KENO-Daten: {keno_path}")
    keno_df = load_keno_data(str(keno_path))
    print(f"  Ziehungen: {len(keno_df)}")

    # Jackpot-Daten
    jackpot_dates = []
    if gk1_path.exists():
        jackpot_dates = load_jackpot_dates(str(gk1_path))
        print(f"  Jackpots: {len(jackpot_dates)}")

    # Monate in 2024
    months_2024 = []
    for m in range(1, 13):
        month_data = keno_df[
            (keno_df["Datum"].dt.year == 2024) &
            (keno_df["Datum"].dt.month == m)
        ]
        if len(month_data) >= 2:
            months_2024.append(m)

    print(f"\nVerfuegbare Monate in 2024: {months_2024}")

    # Backtest MIT Jackpot-Warnung
    print("\n" + "=" * 70)
    print("BACKTEST MIT JACKPOT-WARNUNG")
    print("=" * 70)

    results_with_warning = {
        "mode": "MIT Jackpot-Warnung",
        "months": [],
        "totals": {}
    }

    for month in months_2024:
        result = backtest_month(keno_df, jackpot_dates, 2024, month, use_jackpot_warning=True)
        if result:
            results_with_warning["months"].append(result)
            print(f"\n{month:02d}/2024: {result['played_days']} Tage gespielt, {result['skipped_days']} uebersprungen")
            for typ, data in result["by_type"].items():
                print(f"  {typ}: ROI {data['roi']:+.1f}%, Max {data['max_hits']} Treffer")

    # Backtest OHNE Jackpot-Warnung
    print("\n" + "=" * 70)
    print("BACKTEST OHNE JACKPOT-WARNUNG (immer spielen)")
    print("=" * 70)

    results_without_warning = {
        "mode": "OHNE Jackpot-Warnung",
        "months": [],
        "totals": {}
    }

    for month in months_2024:
        result = backtest_month(keno_df, jackpot_dates, 2024, month, use_jackpot_warning=False)
        if result:
            results_without_warning["months"].append(result)
            print(f"\n{month:02d}/2024: {result['played_days']} Tage gespielt")
            for typ, data in result["by_type"].items():
                print(f"  {typ}: ROI {data['roi']:+.1f}%, Max {data['max_hits']} Treffer")

    # Aggregierte Ergebnisse
    print("\n" + "=" * 70)
    print("VERGLEICH: MIT vs OHNE JACKPOT-WARNUNG")
    print("=" * 70)

    comparison = {}

    for keno_type in [9, 8, 10, 7, 6]:
        typ_key = f"typ_{keno_type}"

        # MIT Warnung
        with_invested = sum(m["by_type"][typ_key]["invested"] for m in results_with_warning["months"])
        with_won = sum(m["by_type"][typ_key]["won"] for m in results_with_warning["months"])
        with_roi = (with_won - with_invested) / with_invested * 100 if with_invested > 0 else 0

        # OHNE Warnung
        without_invested = sum(m["by_type"][typ_key]["invested"] for m in results_without_warning["months"])
        without_won = sum(m["by_type"][typ_key]["won"] for m in results_without_warning["months"])
        without_roi = (without_won - without_invested) / without_invested * 100 if without_invested > 0 else 0

        diff = with_roi - without_roi

        comparison[typ_key] = {
            "with_warning": {
                "invested": with_invested,
                "won": with_won,
                "roi": round(with_roi, 2)
            },
            "without_warning": {
                "invested": without_invested,
                "won": without_won,
                "roi": round(without_roi, 2)
            },
            "difference": round(diff, 2)
        }

        results_with_warning["totals"][typ_key] = comparison[typ_key]["with_warning"]
        results_without_warning["totals"][typ_key] = comparison[typ_key]["without_warning"]

    # Ausgabe
    print("\n" + "-" * 70)
    print(f"{'Typ':<8} {'MIT Warnung':>15} {'OHNE Warnung':>15} {'Differenz':>15}")
    print("-" * 70)

    for keno_type in [9, 8, 10, 7, 6]:
        typ_key = f"typ_{keno_type}"
        c = comparison[typ_key]
        print(f"Typ {keno_type:<4} {c['with_warning']['roi']:>+14.1f}% {c['without_warning']['roi']:>+14.1f}% {c['difference']:>+14.1f}%")

    # Statistik
    total_skipped = sum(m["skipped_days"] for m in results_with_warning["months"])
    total_played_with = sum(m["played_days"] for m in results_with_warning["months"])
    total_played_without = sum(m["played_days"] for m in results_without_warning["months"])

    print("\n" + "-" * 70)
    print(f"Tage gespielt MIT Warnung:   {total_played_with}")
    print(f"Tage uebersprungen:          {total_skipped}")
    print(f"Tage gespielt OHNE Warnung:  {total_played_without}")

    # Speichern
    output = {
        "analysis_date": datetime.now().isoformat(),
        "year": 2024,
        "months_analyzed": months_2024,
        "comparison": comparison,
        "with_warning": results_with_warning,
        "without_warning": results_without_warning,
        "statistics": {
            "days_played_with_warning": total_played_with,
            "days_skipped": total_skipped,
            "days_played_without_warning": total_played_without
        }
    }

    output_path = base_path / "results" / "dynamic_backtest_2024.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    avg_diff = np.mean([c["difference"] for c in comparison.values()])
    best_type_with = max(comparison.items(), key=lambda x: x[1]["with_warning"]["roi"])
    best_type_without = max(comparison.items(), key=lambda x: x[1]["without_warning"]["roi"])

    print(f"""
ERGEBNIS JACKPOT-WARNUNG 2024:

Durchschnittliche ROI-Verbesserung: {avg_diff:+.1f}%

MIT JACKPOT-WARNUNG:
  Bester Typ: {best_type_with[0].upper()}
  ROI: {best_type_with[1]['with_warning']['roi']:+.1f}%
  Einsatz: {best_type_with[1]['with_warning']['invested']} EUR
  Gewinn: {best_type_with[1]['with_warning']['won']} EUR

OHNE JACKPOT-WARNUNG:
  Bester Typ: {best_type_without[0].upper()}
  ROI: {best_type_without[1]['without_warning']['roi']:+.1f}%
  Einsatz: {best_type_without[1]['without_warning']['invested']} EUR
  Gewinn: {best_type_without[1]['without_warning']['won']} EUR
""")

    if avg_diff > 0:
        print(f"FAZIT: Jackpot-Warnung VERBESSERT Performance um {avg_diff:.1f}%!")
        print("       -> System mit Jackpot-Warnung verwenden")
    else:
        print(f"FAZIT: Jackpot-Warnung VERSCHLECHTERT Performance um {abs(avg_diff):.1f}%")
        print("       -> Weitere Analyse noetig")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
