#!/usr/bin/env python3
"""
Backtest: Paar-Gewinn-Frequenz (WL-005)

Testet die Hypothese: Starke Paare gewinnen mind. 2x/Monat einen kleinen Betrag.
Simuliert verschiedene Ticket-Strategien basierend auf starken Paaren.

Autor: Kenobase V2.2
Datum: 2025-12-29
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

# Ensure project root is importable when running `python scripts/...`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.keno_quotes import get_fixed_quote

def load_keno_draws(path: str = "data/raw/keno/KENO_ab_2018.csv") -> pd.DataFrame:
    """Laedt KENO Ziehungen."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers"] = df[number_cols].values.tolist()
    df["numbers_set"] = df["numbers"].apply(set)

    return df


def get_strong_pairs(keno_df: pd.DataFrame, min_count: int = 200) -> List[Tuple[int, int]]:
    """Ermittelt starke Paare basierend auf Co-Occurrence."""
    pair_counts = defaultdict(int)

    for numbers in keno_df["numbers"].tolist():
        sorted_nums = sorted(numbers)
        for pair in combinations(sorted_nums, 2):
            pair_counts[pair] += 1

    strong_pairs = [(k, v) for k, v in pair_counts.items() if v >= min_count]
    strong_pairs.sort(key=lambda x: -x[1])

    return [p[0] for p in strong_pairs]


def simulate_ticket(
    ticket_numbers: List[int],
    keno_type: int,
    draw_numbers: set
) -> float:
    """
    Simuliert einen Tippschein und gibt Gewinn zurueck.

    Args:
        ticket_numbers: Getippte Zahlen
        keno_type: KENO Typ (2-10)
        draw_numbers: Gezogene Zahlen (als Set)

    Returns:
        Gewinn in EUR (bei 1 EUR Einsatz)
    """
    hits = sum(1 for n in ticket_numbers if n in draw_numbers)
    return get_fixed_quote(keno_type, hits)


def create_pair_ticket(pair: Tuple[int, int], keno_type: int, fill_strategy: str = "hot") -> List[int]:
    """
    Erstellt ein Ticket mit einem Paar und fuellt den Rest auf.

    Args:
        pair: Das Zahlenpaar
        keno_type: KENO Typ (2-10)
        fill_strategy: "hot" (haeufige Zahlen), "random", "sequential"

    Returns:
        Liste von Zahlen fuer das Ticket
    """
    ticket = list(pair)

    if keno_type == 2:
        return ticket

    # Haeufige Zahlen basierend auf Analyse
    hot_numbers = [49, 64, 3, 51, 24, 2, 9, 36, 41, 37, 4, 25, 31, 13, 66, 52, 45, 40, 21, 1]

    remaining = keno_type - 2

    if fill_strategy == "hot":
        fill_pool = [n for n in hot_numbers if n not in ticket]
    elif fill_strategy == "sequential":
        fill_pool = [n for n in range(1, 71) if n not in ticket]
    else:
        fill_pool = [n for n in range(1, 71) if n not in ticket]
        np.random.shuffle(fill_pool)

    ticket.extend(fill_pool[:remaining])
    return sorted(ticket)


def backtest_pair_tickets(
    keno_df: pd.DataFrame,
    strong_pairs: List[Tuple[int, int]],
    keno_types: List[int] = [2, 6, 8, 10],
    top_n_pairs: int = 10
) -> Dict:
    """
    Fuehrt Backtest fuer Paar-basierte Tickets durch.

    Args:
        keno_df: KENO Ziehungen
        strong_pairs: Liste starker Paare
        keno_types: Zu testende KENO Typen
        top_n_pairs: Anzahl Paare zu testen

    Returns:
        Dict mit Backtest-Ergebnissen
    """
    results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "total_draws": len(keno_df),
            "pairs_tested": top_n_pairs,
            "keno_types": keno_types
        },
        "by_type": {},
        "by_pair": {},
        "monthly_summary": {}
    }

    # Gruppiere nach Monat
    keno_df["month"] = keno_df["Datum"].dt.to_period("M")

    for keno_type in keno_types:
        type_key = f"typ_{keno_type}"
        results["by_type"][type_key] = {
            "total_invested": 0,
            "total_won": 0,
            "wins_by_class": defaultdict(int),
            "best_pair": None,
            "worst_pair": None
        }

        pair_results = []

        for pair in strong_pairs[:top_n_pairs]:
            ticket = create_pair_ticket(pair, keno_type, "hot")

            pair_key = f"({pair[0]},{pair[1]})"
            monthly_wins = defaultdict(lambda: {"count": 0, "amount": 0})

            total_invested = 0
            total_won = 0
            wins_by_class = defaultdict(int)

            for _, row in keno_df.iterrows():
                draw_set = row["numbers_set"]
                month = str(row["month"])

                win = simulate_ticket(ticket, keno_type, draw_set)

                total_invested += 1  # 1 EUR pro Ziehung
                total_won += win

                if win > 0:
                    monthly_wins[month]["count"] += 1
                    monthly_wins[month]["amount"] += win

                    # Treffer zaehlen
                    hits = sum(1 for n in ticket if n in draw_set)
                    wins_by_class[hits] += 1

            # Monatliche Statistik
            months = list(keno_df["month"].unique())
            months_with_win = sum(1 for m in months if str(m) in monthly_wins and monthly_wins[str(m)]["count"] > 0)

            pair_result = {
                "pair": pair_key,
                "ticket": ticket,
                "total_invested": total_invested,
                "total_won": total_won,
                "roi": (total_won - total_invested) / total_invested if total_invested > 0 else 0,
                "months_with_win": months_with_win,
                "total_months": len(months),
                "win_rate_monthly": months_with_win / len(months) if months else 0,
                "avg_wins_per_month": sum(m["count"] for m in monthly_wins.values()) / len(months) if months else 0,
                "avg_win_amount": total_won / sum(m["count"] for m in monthly_wins.values()) if sum(m["count"] for m in monthly_wins.values()) > 0 else 0,
                "wins_by_class": dict(wins_by_class)
            }

            pair_results.append(pair_result)

            # Aggregiere in Type-Ergebnis
            results["by_type"][type_key]["total_invested"] += total_invested
            results["by_type"][type_key]["total_won"] += total_won

            for hits, count in wins_by_class.items():
                results["by_type"][type_key]["wins_by_class"][hits] += count

        # Beste/Schlechteste Paare
        pair_results.sort(key=lambda x: -x["roi"])
        results["by_type"][type_key]["pair_results"] = pair_results

        if pair_results:
            results["by_type"][type_key]["best_pair"] = pair_results[0]["pair"]
            results["by_type"][type_key]["worst_pair"] = pair_results[-1]["pair"]
            results["by_type"][type_key]["best_roi"] = pair_results[0]["roi"]
            results["by_type"][type_key]["worst_roi"] = pair_results[-1]["roi"]

        # Konvertiere defaultdict zu dict
        results["by_type"][type_key]["wins_by_class"] = dict(results["by_type"][type_key]["wins_by_class"])

    return results


def analyze_guarantee_thresholds(results: Dict) -> Dict:
    """
    Analysiert welche Gewinn-Schwellen mit welcher Wahrscheinlichkeit erreicht werden.
    """
    thresholds = {
        "100_eur": {"pairs_meeting": 0, "pairs_tested": 0},
        "500_eur": {"pairs_meeting": 0, "pairs_tested": 0},
        "monthly_win": {"pairs_meeting": 0, "pairs_tested": 0}
    }

    for type_key, type_data in results["by_type"].items():
        for pair_result in type_data.get("pair_results", []):
            thresholds["monthly_win"]["pairs_tested"] += 1

            if pair_result["win_rate_monthly"] >= 0.80:
                thresholds["monthly_win"]["pairs_meeting"] += 1

            if pair_result["total_won"] >= 100:
                thresholds["100_eur"]["pairs_meeting"] += 1
            thresholds["100_eur"]["pairs_tested"] += 1

            if pair_result["total_won"] >= 500:
                thresholds["500_eur"]["pairs_meeting"] += 1
            thresholds["500_eur"]["pairs_tested"] += 1

    return thresholds


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("BACKTEST: PAAR-GEWINN-FREQUENZ (WL-005)")
    print("=" * 70)
    print()

    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    output_path = base_path / "results" / "pair_guarantee_backtest.json"

    # Daten laden
    print("Lade Daten...")
    keno_df = load_keno_draws(str(keno_path))
    print(f"  Ziehungen: {len(keno_df)}")
    print(f"  Zeitraum: {keno_df['Datum'].min()} bis {keno_df['Datum'].max()}")
    print()

    # Starke Paare ermitteln
    print("Ermittle starke Paare...")
    strong_pairs = get_strong_pairs(keno_df, min_count=200)
    print(f"  Starke Paare (>=200x): {len(strong_pairs)}")
    print(f"  Top-5: {strong_pairs[:5]}")
    print()

    # Backtest durchfuehren
    print("Fuehre Backtest durch...")
    results = backtest_pair_tickets(
        keno_df,
        strong_pairs,
        keno_types=[2, 6, 8, 10],
        top_n_pairs=20
    )

    # Garantie-Schwellen analysieren
    thresholds = analyze_guarantee_thresholds(results)
    results["guarantee_thresholds"] = thresholds

    # Ergebnisse ausgeben
    print("\n" + "=" * 70)
    print("ERGEBNISSE")
    print("=" * 70)

    for type_key, type_data in results["by_type"].items():
        print(f"\n--- {type_key.upper()} ---")
        print(f"  Investiert: {type_data['total_invested']:,} EUR")
        print(f"  Gewonnen: {type_data['total_won']:,} EUR")
        roi = (type_data['total_won'] - type_data['total_invested']) / type_data['total_invested'] * 100 if type_data['total_invested'] > 0 else 0
        print(f"  ROI: {roi:.2f}%")

        if type_data.get("pair_results"):
            best = type_data["pair_results"][0]
            print(f"\n  Bestes Paar: {best['pair']}")
            print(f"    Ticket: {best['ticket']}")
            print(f"    ROI: {best['roi']*100:.2f}%")
            print(f"    Monate mit Gewinn: {best['months_with_win']}/{best['total_months']} ({best['win_rate_monthly']*100:.1f}%)")
            print(f"    Durchschn. Gewinne/Monat: {best['avg_wins_per_month']:.2f}")

    print("\n" + "=" * 70)
    print("WL-005 VALIDIERUNG")
    print("=" * 70)

    # WL-005 Test: Starke Paare gewinnen mind. 2x/Monat
    typ2_results = results["by_type"].get("typ_2", {}).get("pair_results", [])
    if typ2_results:
        pairs_meeting_criteria = sum(1 for p in typ2_results if p["avg_wins_per_month"] >= 2.0)
        total_pairs = len(typ2_results)

        print(f"\nTyp-2 Tickets (nur Paar):")
        print(f"  Paare mit >=2 Gewinnen/Monat: {pairs_meeting_criteria}/{total_pairs}")
        print(f"  Rate: {pairs_meeting_criteria/total_pairs*100:.1f}%")

        if pairs_meeting_criteria >= total_pairs * 0.5:
            print("  STATUS: BESTAETIGT - Mehrheit der Paare gewinnt >=2x/Monat")
            results["wl005_status"] = "BESTAETIGT"
        else:
            print("  STATUS: TEILWEISE - Nicht alle Paare erfuellen Kriterium")
            results["wl005_status"] = "TEILWEISE"

    # Speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse gespeichert: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
