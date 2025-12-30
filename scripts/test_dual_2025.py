#!/usr/bin/env python3
"""
TEST: Dual Ticket Strategy auf 2025 Daten

Out-of-Sample Test der Dual-Strategie auf echten 2025 Daten.

Datenquelle: data/raw/keno/KENO_ab_2022_bereinigt.csv
2025 Daten: 363 Ziehungen (01.01.2025 - 29.12.2025)

Autor: Kenobase V2.2
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np


# ============================================================================
# TICKETS
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


def load_2025_data(base_path: Path) -> pd.DataFrame:
    """Laedt KENO 2025 Daten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors='coerce')

    # Falls anderes Format
    if df["Datum"].isna().all():
        df["Datum"] = pd.to_datetime(df["Datum"])

    # Filter 2025
    df_2025 = df[df["Datum"].dt.year == 2025].copy()

    # Create numbers set
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df_2025["numbers_set"] = df_2025[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    df_2025 = df_2025.sort_values("Datum").reset_index(drop=True)

    return df_2025


def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simuliert ein Ticket."""
    hits = sum(1 for n in ticket if n in draw_set)
    win = KENO_QUOTES.get(keno_type, {}).get(hits, 0)
    return win, hits


def test_2025(df: pd.DataFrame) -> Dict:
    """Testet Dual-Strategie auf 2025 Daten."""

    results = {
        "test_year": 2025,
        "test_period": {
            "start": str(df['Datum'].min().date()),
            "end": str(df['Datum'].max().date()),
            "days": len(df)
        },
        "by_type": {}
    }

    print(f"\n{'='*70}")
    print(f"2025 DUAL-TICKET TEST")
    print(f"{'='*70}")
    print(f"Zeitraum: {df['Datum'].min().date()} bis {df['Datum'].max().date()}")
    print(f"Ziehungen: {len(df)}")

    for keno_type in [8, 9, 10]:
        print(f"\n{'='*70}")
        print(f"TYP {keno_type}")
        print(f"{'='*70}")

        ticket_a = TICKET_A[keno_type]
        ticket_b = TICKET_B[keno_type]

        print(f"\nTicket A (Original):     {ticket_a}")
        print(f"Ticket B (Birthday-Av.): {ticket_b}")

        # Results tracking
        a_results = {"invested": 0, "won": 0, "hits": defaultdict(int), "wins": []}
        b_results = {"invested": 0, "won": 0, "hits": defaultdict(int), "wins": []}
        dual_results = {"invested": 0, "won": 0, "wins": []}
        correlation = {"both": 0, "only_a": 0, "only_b": 0, "neither": 0}

        for _, row in df.iterrows():
            draw_set = row["numbers_set"]

            win_a, hits_a = simulate_ticket(ticket_a, keno_type, draw_set)
            win_b, hits_b = simulate_ticket(ticket_b, keno_type, draw_set)

            # Ticket A
            a_results["invested"] += 1
            a_results["won"] += win_a
            a_results["hits"][hits_a] += 1
            if win_a > 0:
                a_results["wins"].append({
                    "date": str(row["Datum"].date()),
                    "hits": hits_a,
                    "win": win_a
                })

            # Ticket B
            b_results["invested"] += 1
            b_results["won"] += win_b
            b_results["hits"][hits_b] += 1
            if win_b > 0:
                b_results["wins"].append({
                    "date": str(row["Datum"].date()),
                    "hits": hits_b,
                    "win": win_b
                })

            # Dual
            dual_results["invested"] += 2
            dual_results["won"] += win_a + win_b
            if win_a > 0 or win_b > 0:
                dual_results["wins"].append({
                    "date": str(row["Datum"].date()),
                    "win_a": win_a,
                    "win_b": win_b,
                    "total": win_a + win_b
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

        print(f"\n--- ERGEBNISSE ---")
        print(f"\nTicket A (Original):")
        print(f"  Investiert: {a_results['invested']} EUR")
        print(f"  Gewonnen:   {a_results['won']} EUR")
        print(f"  ROI:        {a_roi:+.1f}%")
        print(f"  Gewinntage: {len(a_results['wins'])} von {len(df)}")

        print(f"\nTicket B (Birthday-Avoidance):")
        print(f"  Investiert: {b_results['invested']} EUR")
        print(f"  Gewonnen:   {b_results['won']} EUR")
        print(f"  ROI:        {b_roi:+.1f}%")
        print(f"  Gewinntage: {len(b_results['wins'])} von {len(df)}")

        print(f"\nDUAL (beide Tickets):")
        print(f"  Investiert: {dual_results['invested']} EUR")
        print(f"  Gewonnen:   {dual_results['won']} EUR")
        print(f"  ROI:        {dual_roi:+.1f}%")
        print(f"  Gewinntage: {len(dual_results['wins'])} von {len(df)}")

        # Korrelation
        total = len(df)
        print(f"\nKorrelation (Diversifikation):")
        print(f"  Beide gewinnen:  {correlation['both']:3d} ({correlation['both']/total*100:5.1f}%)")
        print(f"  Nur A gewinnt:   {correlation['only_a']:3d} ({correlation['only_a']/total*100:5.1f}%)")
        print(f"  Nur B gewinnt:   {correlation['only_b']:3d} ({correlation['only_b']/total*100:5.1f}%)")
        print(f"  Keiner gewinnt:  {correlation['neither']:3d} ({correlation['neither']/total*100:5.1f}%)")

        diversification = correlation['only_a'] + correlation['only_b']
        print(f"\n  DIVERSIFIKATIONS-VORTEIL: {diversification} Tage wo nur EIN Ticket gewann")

        # High wins
        high_a = [w for w in a_results["wins"] if w["win"] >= 100]
        high_b = [w for w in b_results["wins"] if w["win"] >= 100]

        print(f"\nHigh-Wins (>=100 EUR):")
        print(f"  Ticket A: {len(high_a)}")
        for hw in high_a:
            print(f"    {hw['date']}: {hw['hits']} Treffer = {hw['win']} EUR")

        print(f"  Ticket B: {len(high_b)}")
        for hw in high_b:
            print(f"    {hw['date']}: {hw['hits']} Treffer = {hw['win']} EUR")

        # Hits distribution
        print(f"\nTreffer-Verteilung:")
        print(f"  {'Treffer':<10} {'Ticket A':<12} {'Ticket B':<12}")
        for h in sorted(set(list(a_results["hits"].keys()) + list(b_results["hits"].keys())), reverse=True):
            print(f"  {h:<10} {a_results['hits'].get(h, 0):<12} {b_results['hits'].get(h, 0):<12}")

        # Store results
        results["by_type"][f"typ_{keno_type}"] = {
            "ticket_a": {
                "ticket": ticket_a,
                "roi": a_roi,
                "invested": a_results["invested"],
                "won": a_results["won"],
                "win_days": len(a_results["wins"]),
                "high_wins": len(high_a),
                "high_win_details": high_a,
            },
            "ticket_b": {
                "ticket": ticket_b,
                "roi": b_roi,
                "invested": b_results["invested"],
                "won": b_results["won"],
                "win_days": len(b_results["wins"]),
                "high_wins": len(high_b),
                "high_win_details": high_b,
            },
            "dual": {
                "roi": dual_roi,
                "invested": dual_results["invested"],
                "won": dual_results["won"],
                "win_days": len(dual_results["wins"]),
            },
            "correlation": correlation,
            "diversification_days": diversification,
        }

    return results


def main():
    print("=" * 70)
    print("DUAL-TICKET STRATEGIE - 2025 TEST")
    print("=" * 70)
    print()
    print("Out-of-Sample Test auf echten 2025 KENO Daten")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade 2025 Daten...")
    df = load_2025_data(base_path)
    print(f"  Geladen: {len(df)} Ziehungen")

    if len(df) == 0:
        print("FEHLER: Keine 2025 Daten gefunden!")
        return

    # Run test
    results = test_2025(df)

    # Final Summary
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG 2025")
    print("=" * 70)

    print(f"\nTest-Zeitraum: {results['test_period']['start']} bis {results['test_period']['end']}")
    print(f"Ziehungen:     {results['test_period']['days']}")

    print("\n{:<10} {:>12} {:>12} {:>12} {:>10} {:>8}".format(
        "Typ", "A (Orig)", "B (Bday)", "DUAL", "Diversif.", "Beste"
    ))
    print("-" * 70)

    total_a = 0
    total_b = 0
    total_dual = 0

    for keno_type in [8, 9, 10]:
        r = results["by_type"][f"typ_{keno_type}"]
        a_roi = r["ticket_a"]["roi"]
        b_roi = r["ticket_b"]["roi"]
        d_roi = r["dual"]["roi"]
        div = r["diversification_days"]

        total_a += r["ticket_a"]["won"]
        total_b += r["ticket_b"]["won"]
        total_dual += r["dual"]["won"]

        best = "A" if a_roi >= b_roi and a_roi >= d_roi else ("B" if b_roi >= d_roi else "DUAL")

        print("{:<10} {:>+11.1f}% {:>+11.1f}% {:>+11.1f}% {:>10} {:>8}".format(
            f"Typ {keno_type}", a_roi, b_roi, d_roi, div, best
        ))

    # Total
    invested = results['test_period']['days']
    print("-" * 70)
    print("{:<10} {:>12} {:>12} {:>12}".format(
        "GESAMT", f"{total_a} EUR", f"{total_b} EUR", f"{total_dual} EUR"
    ))

    # Save
    output_path = base_path / "results" / "dual_strategy_2025_test.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Recommendation
    print("\n" + "=" * 70)
    print("EMPFEHLUNG BASIEREND AUF 2025 DATEN")
    print("=" * 70)

    for keno_type in [8, 9, 10]:
        r = results["by_type"][f"typ_{keno_type}"]
        a_roi = r["ticket_a"]["roi"]
        b_roi = r["ticket_b"]["roi"]
        d_roi = r["dual"]["roi"]

        if d_roi > a_roi and d_roi > b_roi:
            print(f"\nTyp {keno_type}: DUAL empfohlen")
            print(f"  Ticket A: {r['ticket_a']['ticket']}")
            print(f"  Ticket B: {r['ticket_b']['ticket']}")
        elif a_roi > b_roi:
            print(f"\nTyp {keno_type}: ORIGINAL (A) empfohlen")
            print(f"  Ticket: {r['ticket_a']['ticket']}")
        else:
            print(f"\nTyp {keno_type}: BIRTHDAY-AV. (B) empfohlen")
            print(f"  Ticket: {r['ticket_b']['ticket']}")


if __name__ == "__main__":
    main()
