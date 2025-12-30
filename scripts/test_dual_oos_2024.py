#!/usr/bin/env python3
"""
OUT-OF-SAMPLE TEST: Dual Ticket Strategy auf 2024 Daten

Da 2025 Gewinnzahlen nicht verfuegbar sind, testen wir auf den
letzten verfuegbaren Daten (2024), die NICHT fuer die Modell-
Optimierung verwendet wurden.

Test-Zeitraum: Letzte 90 Tage der verfuegbaren Daten
Training-Zeitraum: Alles davor

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


# ============================================================================
# TICKETS (identisch zu V3.1)
# ============================================================================

TICKET_A = {
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
}

TICKET_B = {
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}

KENO_QUOTES = {
    8: {8: 10000, 7: 1000, 6: 100, 5: 10, 4: 2, 3: 0, 2: 0, 1: 0, 0: 0},
    9: {9: 50000, 8: 5000, 7: 500, 6: 50, 5: 10, 4: 2, 3: 0, 2: 0, 1: 0, 0: 0},
    10: {10: 100000, 9: 10000, 8: 1000, 7: 100, 6: 15, 5: 5, 4: 0, 3: 0, 2: 0, 1: 0, 0: 2}
}


def load_data(base_path: Path) -> pd.DataFrame:
    """Laedt KENO-Daten."""
    keno_path = base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv"

    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row), axis=1)
    df = df.sort_values("Datum").reset_index(drop=True)

    return df


def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simuliert ein Ticket."""
    hits = sum(1 for n in ticket if n in draw_set)
    win = KENO_QUOTES.get(keno_type, {}).get(hits, 0)
    return win, hits


def run_oos_test(
    df: pd.DataFrame,
    test_days: int = 90
) -> Dict:
    """
    Out-of-Sample Test.

    Letzte `test_days` Tage als Test-Set.
    """
    total_rows = len(df)
    test_start = total_rows - test_days

    test_df = df.iloc[test_start:]
    train_df = df.iloc[:test_start]

    print(f"\n{'='*60}")
    print(f"OUT-OF-SAMPLE TEST SETUP")
    print(f"{'='*60}")
    print(f"Training: {train_df['Datum'].min().date()} bis {train_df['Datum'].max().date()} ({len(train_df)} Tage)")
    print(f"Test:     {test_df['Datum'].min().date()} bis {test_df['Datum'].max().date()} ({len(test_df)} Tage)")

    results = {
        "test_period": {
            "start": str(test_df['Datum'].min().date()),
            "end": str(test_df['Datum'].max().date()),
            "days": len(test_df)
        },
        "by_type": {}
    }

    for keno_type in [8, 9, 10]:
        print(f"\n{'='*60}")
        print(f"TYP {keno_type} - OUT-OF-SAMPLE TEST")
        print(f"{'='*60}")

        ticket_a = TICKET_A[keno_type]
        ticket_b = TICKET_B[keno_type]

        # Test results
        a_results = {"invested": 0, "won": 0, "hits": defaultdict(int), "wins": []}
        b_results = {"invested": 0, "won": 0, "hits": defaultdict(int), "wins": []}
        dual_results = {"invested": 0, "won": 0, "wins": []}
        correlation = {"both": 0, "only_a": 0, "only_b": 0, "neither": 0}

        for _, row in test_df.iterrows():
            draw_set = row["numbers_set"]

            win_a, hits_a = simulate_ticket(ticket_a, keno_type, draw_set)
            win_b, hits_b = simulate_ticket(ticket_b, keno_type, draw_set)

            # Ticket A
            a_results["invested"] += 1
            a_results["won"] += win_a
            a_results["hits"][hits_a] += 1
            if win_a > 0:
                a_results["wins"].append({"date": str(row["Datum"].date()), "hits": hits_a, "win": win_a})

            # Ticket B
            b_results["invested"] += 1
            b_results["won"] += win_b
            b_results["hits"][hits_b] += 1
            if win_b > 0:
                b_results["wins"].append({"date": str(row["Datum"].date()), "hits": hits_b, "win": win_b})

            # Dual
            dual_results["invested"] += 2
            dual_results["won"] += win_a + win_b
            if win_a > 0 or win_b > 0:
                dual_results["wins"].append({
                    "date": str(row["Datum"].date()),
                    "win_a": win_a, "win_b": win_b
                })

            # Correlation
            a_wins = win_a > 0
            b_wins = win_b > 0
            if a_wins and b_wins:
                correlation["both"] += 1
            elif a_wins:
                correlation["only_a"] += 1
            elif b_wins:
                correlation["only_b"] += 1
            else:
                correlation["neither"] += 1

        # Calculate ROIs
        a_roi = (a_results["won"] - a_results["invested"]) / a_results["invested"] * 100
        b_roi = (b_results["won"] - b_results["invested"]) / b_results["invested"] * 100
        dual_roi = (dual_results["won"] - dual_results["invested"]) / dual_results["invested"] * 100

        print(f"\nTicket A (Original): {ticket_a}")
        print(f"  Investiert: {a_results['invested']} EUR")
        print(f"  Gewonnen:   {a_results['won']} EUR")
        print(f"  ROI:        {a_roi:+.1f}%")
        print(f"  Gewinntage: {len(a_results['wins'])}")

        print(f"\nTicket B (Birthday-Av.): {ticket_b}")
        print(f"  Investiert: {b_results['invested']} EUR")
        print(f"  Gewonnen:   {b_results['won']} EUR")
        print(f"  ROI:        {b_roi:+.1f}%")
        print(f"  Gewinntage: {len(b_results['wins'])}")

        print(f"\nDUAL (A+B):")
        print(f"  Investiert: {dual_results['invested']} EUR")
        print(f"  Gewonnen:   {dual_results['won']} EUR")
        print(f"  ROI:        {dual_roi:+.1f}%")
        print(f"  Gewinntage: {len(dual_results['wins'])}")

        print(f"\nKorrelation ({len(test_df)} Tage):")
        print(f"  Beide gewinnen:  {correlation['both']:3d} ({correlation['both']/len(test_df)*100:.1f}%)")
        print(f"  Nur A gewinnt:   {correlation['only_a']:3d} ({correlation['only_a']/len(test_df)*100:.1f}%)")
        print(f"  Nur B gewinnt:   {correlation['only_b']:3d} ({correlation['only_b']/len(test_df)*100:.1f}%)")
        print(f"  Keiner gewinnt:  {correlation['neither']:3d} ({correlation['neither']/len(test_df)*100:.1f}%)")

        # High wins
        high_wins_a = [w for w in a_results["wins"] if w["win"] >= 100]
        high_wins_b = [w for w in b_results["wins"] if w["win"] >= 100]

        print(f"\nHigh-Wins (>=100 EUR):")
        print(f"  Ticket A: {len(high_wins_a)}")
        print(f"  Ticket B: {len(high_wins_b)}")

        if high_wins_a:
            print(f"    Details A: {high_wins_a}")
        if high_wins_b:
            print(f"    Details B: {high_wins_b}")

        # Store results
        results["by_type"][f"typ_{keno_type}"] = {
            "ticket_a": {
                "ticket": ticket_a,
                "roi": a_roi,
                "invested": a_results["invested"],
                "won": a_results["won"],
                "win_days": len(a_results["wins"]),
                "high_wins": len(high_wins_a),
            },
            "ticket_b": {
                "ticket": ticket_b,
                "roi": b_roi,
                "invested": b_results["invested"],
                "won": b_results["won"],
                "win_days": len(b_results["wins"]),
                "high_wins": len(high_wins_b),
            },
            "dual": {
                "roi": dual_roi,
                "invested": dual_results["invested"],
                "won": dual_results["won"],
                "win_days": len(dual_results["wins"]),
            },
            "correlation": correlation,
        }

    return results


def main():
    print("=" * 70)
    print("OUT-OF-SAMPLE TEST: DUAL TICKET STRATEGY")
    print("=" * 70)
    print()
    print("Testet die Dual-Ticket-Strategie auf Daten, die NICHT")
    print("fuer die Modell-Optimierung verwendet wurden.")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    df = load_data(base_path)
    print(f"  Gesamt: {len(df)} Ziehungen")
    print(f"  Zeitraum: {df['Datum'].min().date()} bis {df['Datum'].max().date()}")

    # Run OOS test on last 90 days
    results = run_oos_test(df, test_days=90)

    # Summary
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG - OUT-OF-SAMPLE TEST")
    print("=" * 70)

    print(f"\nTest-Zeitraum: {results['test_period']['start']} bis {results['test_period']['end']}")
    print(f"               ({results['test_period']['days']} Tage)")

    print("\n{:<12} {:>12} {:>12} {:>12} {:>8}".format(
        "Typ", "A (Orig)", "B (Bday)", "DUAL", "Beste"
    ))
    print("-" * 60)

    for keno_type in [8, 9, 10]:
        r = results["by_type"][f"typ_{keno_type}"]
        a_roi = r["ticket_a"]["roi"]
        b_roi = r["ticket_b"]["roi"]
        d_roi = r["dual"]["roi"]

        best = "A" if a_roi >= b_roi and a_roi >= d_roi else ("B" if b_roi >= d_roi else "DUAL")

        print("{:<12} {:>+11.1f}% {:>+11.1f}% {:>+11.1f}% {:>8}".format(
            f"Typ {keno_type}", a_roi, b_roi, d_roi, best
        ))

    # Save results
    output_path = base_path / "results" / "dual_strategy_oos_test.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
