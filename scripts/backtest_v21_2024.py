#!/usr/bin/env python3
"""
BACKTEST: V2.1 Ticket fuer das Jahr 2024

V2.1 Ticket: [3, 7, 36, 43, 48, 51, 55, 58, 61]

Simuliert die Performance ab Januar 2024 bis Dezember 2024.

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

from collections import Counter
from pathlib import Path
import pandas as pd
import numpy as np

# Import quotes
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from kenobase.core.keno_quotes import get_fixed_quote


# V2.1 Ticket
V2_1_TICKET = [3, 7, 36, 43, 48, 51, 55, 58, 61]
KENO_TYPE = 9
EINSATZ = 1  # EUR pro Ziehung


def load_data(base_path):
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def simulate_ticket(ticket, draw_set, keno_type=9):
    """Simuliere ein Ticket gegen eine Ziehung."""
    hits = len(set(ticket) & draw_set)
    win = get_fixed_quote(keno_type, hits)
    return hits, int(win)


def main():
    print("=" * 80)
    print("BACKTEST: V2.1 TICKET - JAHR 2024")
    print("=" * 80)
    print(f"\nV2.1 Ticket: {V2_1_TICKET}")
    print(f"Keno Typ:    {KENO_TYPE}")
    print(f"Einsatz:     {EINSATZ} EUR pro Ziehung")

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)

    # Filter auf 2024
    df_2024 = df[(df["Datum"].dt.year == 2024)].copy()
    df_2024 = df_2024.sort_values("Datum").reset_index(drop=True)

    print(f"\nZeitraum: 01.01.2024 - 31.12.2024")
    print(f"Anzahl Ziehungen: {len(df_2024)}")

    # =========================================================================
    # MONATLICHE PERFORMANCE
    # =========================================================================
    print("\n" + "=" * 80)
    print("MONATLICHE PERFORMANCE 2024")
    print("=" * 80)

    df_2024["month"] = df_2024["Datum"].dt.month
    df_2024["month_name"] = df_2024["Datum"].dt.strftime("%B")

    monthly_results = []

    print(f"\n{'Monat':<12} {'Zieh.':>6} {'Treffer':>8} {'Gewinn':>10} {'Kosten':>8} {'Netto':>10} {'ROI':>10}")
    print("-" * 70)

    for month in range(1, 13):
        month_df = df_2024[df_2024["month"] == month]
        if len(month_df) == 0:
            continue

        month_name = month_df["month_name"].iloc[0]
        hits_list = []
        wins_list = []

        for _, row in month_df.iterrows():
            draw = row["numbers_set"]
            hits, win = simulate_ticket(V2_1_TICKET, draw, KENO_TYPE)
            hits_list.append(hits)
            wins_list.append(win)

        n_draws = len(month_df)
        total_win = sum(wins_list)
        total_cost = n_draws * EINSATZ
        netto = total_win - total_cost
        roi = (netto / total_cost) * 100
        avg_hits = np.mean(hits_list)

        monthly_results.append({
            "month": month,
            "month_name": month_name,
            "draws": n_draws,
            "avg_hits": avg_hits,
            "total_win": total_win,
            "total_cost": total_cost,
            "netto": netto,
            "roi": roi,
            "hits_dist": Counter(hits_list)
        })

        print(f"{month_name:<12} {n_draws:>6} {avg_hits:>8.2f} {total_win:>9} EUR {total_cost:>7} EUR {netto:>+9} EUR {roi:>+9.1f}%")

    # =========================================================================
    # JAHRES-ZUSAMMENFASSUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("JAHRES-ZUSAMMENFASSUNG 2024")
    print("=" * 80)

    total_draws = sum(m["draws"] for m in monthly_results)
    total_win = sum(m["total_win"] for m in monthly_results)
    total_cost = sum(m["total_cost"] for m in monthly_results)
    total_netto = total_win - total_cost
    total_roi = (total_netto / total_cost) * 100

    # Kombiniere alle Treffer-Verteilungen
    all_hits = Counter()
    for m in monthly_results:
        all_hits.update(m["hits_dist"])

    print(f"""
GESAMT 2024:
  Ziehungen:    {total_draws}
  Einsatz:      {total_cost} EUR
  Gewinn:       {total_win} EUR
  NETTO:        {total_netto:+} EUR
  ROI:          {total_roi:+.1f}%
""")

    # =========================================================================
    # TREFFER-VERTEILUNG
    # =========================================================================
    print("=" * 80)
    print("TREFFER-VERTEILUNG 2024")
    print("=" * 80)

    print(f"\n{'Treffer':>8} {'Anzahl':>10} {'Prozent':>10} {'Gewinn/Treffer':>15} {'Gesamt':>12}")
    print("-" * 60)

    for hits in range(10):
        count = all_hits.get(hits, 0)
        pct = count / total_draws * 100 if total_draws > 0 else 0
        win_per = get_fixed_quote(KENO_TYPE, hits)
        total_for_hits = count * win_per
        print(f"{hits:>8} {count:>10} {pct:>9.1f}% {win_per:>14} EUR {total_for_hits:>11} EUR")

    # =========================================================================
    # BESTE UND SCHLECHTESTE MONATE
    # =========================================================================
    print("\n" + "=" * 80)
    print("BESTE UND SCHLECHTESTE MONATE")
    print("=" * 80)

    sorted_by_roi = sorted(monthly_results, key=lambda x: x["roi"], reverse=True)

    print("\nBeste Monate:")
    for m in sorted_by_roi[:3]:
        print(f"  {m['month_name']:<12}: {m['roi']:+.1f}% ROI ({m['netto']:+} EUR)")

    print("\nSchlechteste Monate:")
    for m in sorted_by_roi[-3:]:
        print(f"  {m['month_name']:<12}: {m['roi']:+.1f}% ROI ({m['netto']:+} EUR)")

    # =========================================================================
    # HIGH-WIN EVENTS (>=6 Treffer)
    # =========================================================================
    print("\n" + "=" * 80)
    print("HIGH-WIN EVENTS 2024 (>=6 Treffer)")
    print("=" * 80)

    print(f"\n{'Datum':<12} {'Treffer':>8} {'Gewinn':>10} {'Gezogene Zahlen'}")
    print("-" * 70)

    high_win_count = 0
    for _, row in df_2024.iterrows():
        draw = row["numbers_set"]
        date = row["Datum"]
        hits, win = simulate_ticket(V2_1_TICKET, draw, KENO_TYPE)

        if hits >= 6:
            high_win_count += 1
            matching = sorted(set(V2_1_TICKET) & draw)
            print(f"{date.strftime('%d.%m.%Y'):<12} {hits:>8} {win:>9} EUR {matching}")

    print(f"\nGesamt High-Win Events: {high_win_count}")

    # =========================================================================
    # KUMULATIVE ENTWICKLUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("KUMULATIVE ENTWICKLUNG (Quartalsweise)")
    print("=" * 80)

    cumulative = 0
    cumulative_cost = 0

    quarters = [
        ("Q1 (Jan-Mrz)", [1, 2, 3]),
        ("Q2 (Apr-Jun)", [4, 5, 6]),
        ("Q3 (Jul-Sep)", [7, 8, 9]),
        ("Q4 (Okt-Dez)", [10, 11, 12])
    ]

    print(f"\n{'Quartal':<15} {'Zieh.':>6} {'Q-Gewinn':>10} {'Kumulativ':>12} {'Kum. ROI':>10}")
    print("-" * 55)

    for q_name, months in quarters:
        q_results = [m for m in monthly_results if m["month"] in months]
        q_draws = sum(m["draws"] for m in q_results)
        q_win = sum(m["total_win"] for m in q_results)
        q_cost = sum(m["total_cost"] for m in q_results)

        cumulative += q_win
        cumulative_cost += q_cost
        cum_netto = cumulative - cumulative_cost
        cum_roi = (cum_netto / cumulative_cost) * 100 if cumulative_cost > 0 else 0

        print(f"{q_name:<15} {q_draws:>6} {q_win:>9} EUR {cum_netto:>+11} EUR {cum_roi:>+9.1f}%")

    # =========================================================================
    # FAZIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT: V2.1 TICKET 2024")
    print("=" * 80)

    avg_monthly_netto = total_netto / 12

    print(f"""
V2.1 TICKET: {V2_1_TICKET}

JAHRES-BILANZ 2024:
  Gesamt-Einsatz:    {total_cost:>6} EUR
  Gesamt-Gewinn:     {total_win:>6} EUR
  NETTO-ERGEBNIS:    {total_netto:>+6} EUR
  ROI:               {total_roi:>+6.1f}%

DURCHSCHNITT PRO MONAT:
  Einsatz:           {total_cost/12:>6.0f} EUR
  Netto:             {avg_monthly_netto:>+6.0f} EUR

TREFFER-STATISTIK:
  0 Treffer:         {all_hits.get(0, 0):>4}x
  1-2 Treffer:       {all_hits.get(1, 0) + all_hits.get(2, 0):>4}x
  3-4 Treffer:       {all_hits.get(3, 0) + all_hits.get(4, 0):>4}x (Gewinn!)
  5+ Treffer:        {sum(all_hits.get(h, 0) for h in range(5, 10)):>4}x (Hoher Gewinn!)

BEWERTUNG:
  {'PROFITABEL' if total_netto > 0 else 'VERLUST'} - V2.1 haette 2024 {abs(total_netto)} EUR {'Gewinn' if total_netto > 0 else 'Verlust'} erzielt.
""")


if __name__ == "__main__":
    main()
