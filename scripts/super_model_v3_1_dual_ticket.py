#!/usr/bin/env python3
"""
SUPER-MODELL V3.1 - DUAL TICKET STRATEGY

ERKENNTNIS AUS V3:
- Unterschiedliche Tickets haben unterschiedliche Trefferprofile
- Zwei Tickets am gleichen Tag koennen diversifizieren

NEUER ANSATZ:
Statt Budget aufzuteilen, spielen wir ZWEI verschiedene Tickets
am gleichen Tag fuer den GLEICHEN Typ:
- Ticket A: Original OPTIMAL_TICKETS
- Ticket B: Jackpot-optimiert (Birthday-Avoidance)

Hypothese: Die Tickets haben unterschiedliche Zahlen und koennen
sich gegenseitig ergaenzen - eines koennte treffen wenn das andere nicht.

Autor: Kenobase V2.2 - Dual Ticket Strategy
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

from super_model_synthesis import (
    KENO_QUOTES,
    OPTIMAL_TICKETS_KI1,
    load_data,
    simulate_ticket,
)


# ============================================================================
# TICKETS
# ============================================================================

# Original OPTIMAL_TICKETS (bewaehrt)
TICKET_A = {
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
}

# Jackpot-optimiert (Birthday-Avoidance)
TICKET_B = {
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}


def analyze_ticket_overlap():
    """Analysiert Ueberlappung zwischen Ticket A und B."""
    print("\n" + "=" * 60)
    print("TICKET-ANALYSE")
    print("=" * 60)

    for keno_type in [8, 9, 10]:
        a = set(TICKET_A[keno_type])
        b = set(TICKET_B[keno_type])
        overlap = a & b
        only_a = a - b
        only_b = b - a

        print(f"\nTyp {keno_type}:")
        print(f"  Ticket A: {sorted(a)}")
        print(f"  Ticket B: {sorted(b)}")
        print(f"  Ueberlappung: {sorted(overlap)} ({len(overlap)} Zahlen)")
        print(f"  Nur A: {sorted(only_a)}")
        print(f"  Nur B: {sorted(only_b)}")
        print(f"  Gesamt abgedeckt: {len(a | b)} von 70 Zahlen")


def backtest_dual_tickets(
    keno_df: pd.DataFrame,
    jackpot_dates: List,
    keno_type: int = 9,
    start_idx: int = 365,
    cooldown_days: int = 30
) -> Dict:
    """
    Backtest mit zwei Tickets pro Tag.

    Vergleicht:
    1. Nur Ticket A
    2. Nur Ticket B
    3. Beide Tickets (A + B)
    """
    results = {
        "keno_type": keno_type,
        "ticket_a_only": {"invested": 0, "won": 0, "skipped": 0, "high_wins": []},
        "ticket_b_only": {"invested": 0, "won": 0, "skipped": 0, "high_wins": []},
        "dual_tickets": {"invested": 0, "won": 0, "skipped": 0, "high_wins": []},
        "correlation": {"both_win": 0, "only_a_wins": 0, "only_b_wins": 0, "neither_wins": 0},
    }

    ticket_a = TICKET_A[keno_type]
    ticket_b = TICKET_B[keno_type]

    for i in range(start_idx, len(keno_df)):
        curr_row = keno_df.iloc[i]
        draw_set = curr_row["numbers_set"]
        curr_date = curr_row["Datum"]

        # Jackpot-Cooldown pruefen
        past_jackpots = [jp for jp in jackpot_dates if jp < curr_date]
        skip = False
        if past_jackpots:
            last_jp = max(past_jackpots)
            if (curr_date - last_jp).days <= cooldown_days:
                skip = True

        if skip:
            results["ticket_a_only"]["skipped"] += 1
            results["ticket_b_only"]["skipped"] += 1
            results["dual_tickets"]["skipped"] += 1
            continue

        # Simuliere beide Tickets
        win_a, hits_a = simulate_ticket(ticket_a, keno_type, draw_set)
        win_b, hits_b = simulate_ticket(ticket_b, keno_type, draw_set)

        # Ticket A only
        results["ticket_a_only"]["invested"] += 1
        results["ticket_a_only"]["won"] += win_a
        if win_a >= 100:
            results["ticket_a_only"]["high_wins"].append({
                "date": str(curr_date.date()), "hits": hits_a, "win": win_a
            })

        # Ticket B only
        results["ticket_b_only"]["invested"] += 1
        results["ticket_b_only"]["won"] += win_b
        if win_b >= 100:
            results["ticket_b_only"]["high_wins"].append({
                "date": str(curr_date.date()), "hits": hits_b, "win": win_b
            })

        # Dual Tickets (beide spielen)
        results["dual_tickets"]["invested"] += 2  # 2 EUR Einsatz
        results["dual_tickets"]["won"] += win_a + win_b
        if win_a >= 100 or win_b >= 100:
            results["dual_tickets"]["high_wins"].append({
                "date": str(curr_date.date()),
                "hits_a": hits_a, "win_a": win_a,
                "hits_b": hits_b, "win_b": win_b
            })

        # Korrelation
        a_wins = win_a > 0
        b_wins = win_b > 0

        if a_wins and b_wins:
            results["correlation"]["both_win"] += 1
        elif a_wins:
            results["correlation"]["only_a_wins"] += 1
        elif b_wins:
            results["correlation"]["only_b_wins"] += 1
        else:
            results["correlation"]["neither_wins"] += 1

    # ROIs berechnen
    for key in ["ticket_a_only", "ticket_b_only", "dual_tickets"]:
        r = results[key]
        if r["invested"] > 0:
            r["roi"] = (r["won"] - r["invested"]) / r["invested"] * 100
        else:
            r["roi"] = 0

    return results


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("SUPER-MODELL V3.1 - DUAL TICKET STRATEGY")
    print("=" * 70)
    print()
    print("KONZEPT:")
    print("  Zwei verschiedene Tickets am gleichen Tag spielen:")
    print("  - Ticket A: Original OPTIMAL_TICKETS")
    print("  - Ticket B: Jackpot-optimiert (Birthday-Avoidance)")
    print()

    # Ticket-Analyse
    analyze_ticket_overlap()

    base_path = Path(__file__).parent.parent

    print("\n\nLade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Backtest fuer alle Typen
    all_results = {}

    for keno_type in [8, 9, 10]:
        print(f"\n{'='*60}")
        print(f"TYP {keno_type}")
        print(f"{'='*60}")

        results = backtest_dual_tickets(keno_df, jackpot_dates, keno_type)
        all_results[f"typ_{keno_type}"] = results

        print(f"\nTicket A (Original):      ROI {results['ticket_a_only']['roi']:+.1f}%, "
              f"High-Wins: {len(results['ticket_a_only']['high_wins'])}")
        print(f"Ticket B (Birthday-Av.):  ROI {results['ticket_b_only']['roi']:+.1f}%, "
              f"High-Wins: {len(results['ticket_b_only']['high_wins'])}")
        print(f"DUAL (A+B):               ROI {results['dual_tickets']['roi']:+.1f}%, "
              f"High-Wins: {len(results['dual_tickets']['high_wins'])}")

        # Korrelation
        total = sum(results["correlation"].values())
        if total > 0:
            print(f"\nKorrelation:")
            print(f"  Beide gewinnen:  {results['correlation']['both_win']:4d} ({results['correlation']['both_win']/total*100:.1f}%)")
            print(f"  Nur A gewinnt:   {results['correlation']['only_a_wins']:4d} ({results['correlation']['only_a_wins']/total*100:.1f}%)")
            print(f"  Nur B gewinnt:   {results['correlation']['only_b_wins']:4d} ({results['correlation']['only_b_wins']/total*100:.1f}%)")
            print(f"  Keiner gewinnt:  {results['correlation']['neither_wins']:4d} ({results['correlation']['neither_wins']/total*100:.1f}%)")

            # Berechne Diversifikations-Vorteil
            unique_wins = results['correlation']['only_a_wins'] + results['correlation']['only_b_wins']
            print(f"\n  Diversifikations-Vorteil: {unique_wins} Tage wo nur ein Ticket gewann")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    print("\n{:<20} {:>12} {:>12} {:>12}".format(
        "Typ/Strategie", "A (Orig)", "B (Jackpot)", "DUAL"
    ))
    print("-" * 60)

    for keno_type in [8, 9, 10]:
        r = all_results[f"typ_{keno_type}"]
        print("{:<20} {:>+11.1f}% {:>+11.1f}% {:>+11.1f}%".format(
            f"Typ {keno_type}",
            r["ticket_a_only"]["roi"],
            r["ticket_b_only"]["roi"],
            r["dual_tickets"]["roi"]
        ))

    # Speichern
    output_path = base_path / "results" / "super_model_v3_1_dual.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Empfehlung
    print("\n" + "=" * 70)
    print("EMPFEHLUNG")
    print("=" * 70)

    # Beste Strategie pro Typ
    for keno_type in [8, 9, 10]:
        r = all_results[f"typ_{keno_type}"]
        strategies = [
            ("A (Original)", r["ticket_a_only"]["roi"]),
            ("B (Jackpot)", r["ticket_b_only"]["roi"]),
            ("DUAL", r["dual_tickets"]["roi"]),
        ]
        best = max(strategies, key=lambda x: x[1])
        print(f"\nTyp {keno_type}: BESTE = {best[0]} (ROI {best[1]:+.1f}%)")

        if best[0] == "DUAL":
            print(f"  Ticket A: {TICKET_A[keno_type]}")
            print(f"  Ticket B: {TICKET_B[keno_type]}")
        elif best[0] == "A (Original)":
            print(f"  Ticket: {TICKET_A[keno_type]}")
        else:
            print(f"  Ticket: {TICKET_B[keno_type]}")


if __name__ == "__main__":
    main()
