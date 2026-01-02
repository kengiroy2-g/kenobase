#!/usr/bin/env python3
"""
HIGH-RISK STRATEGIE: Wann ist der beste Zeitpunkt für einen Schuss?

Perspektive: Nicht Stabilität, sondern MAXIMALER ERWARTUNGSWERT bei EINEM Versuch.

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Set
import numpy as np
import pandas as pd

from kenobase.core.keno_quotes import get_fixed_quote


# V2 Tickets
V2_TICKETS = {
    6: [3, 36, 43, 48, 51, 58],
    7: [3, 36, 43, 48, 51, 58, 61],
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}


def load_data(base_path):
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_jackpots(df, base_path) -> Set:
    dates = set()
    path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path.exists():
        timeline = pd.read_csv(path)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())
    return dates


def simulate(ticket, keno_type, draw_set):
    hits = sum(1 for n in ticket if n in draw_set)
    return hits, int(get_fixed_quote(keno_type, hits))


def main():
    print("=" * 80)
    print("HIGH-RISK STRATEGIE: Maximaler Erwartungswert bei EINEM Versuch")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)
    jackpot_dates = get_jackpots(df, base_path)

    df_2025 = df[df["Datum"].dt.year == 2025].copy().reset_index(drop=True)
    df_2025["is_jackpot"] = df_2025["Datum"].apply(lambda d: d in jackpot_dates)

    print(f"\n2025: {len(df_2025)} Ziehungen, {df_2025['is_jackpot'].sum()} Jackpots")

    # =========================================================================
    # 1. V2 PERFORMANCE BEI ALLEN ZIEHUNGEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. V2 TREFFER-VERTEILUNG (alle 2025 Ziehungen)")
    print("=" * 80)

    for keno_type in [9, 10]:
        ticket = set(V2_TICKETS[keno_type])
        hits_all = []
        wins_all = []

        for _, row in df_2025.iterrows():
            h, w = simulate(ticket, keno_type, row["numbers_set"])
            hits_all.append(h)
            wins_all.append(w)

        hit_dist = pd.Series(hits_all).value_counts().sort_index()

        print(f"\nTyp {keno_type} V2: {sorted(ticket)}")
        print(f"  Treffer-Verteilung:")
        for h, count in hit_dist.items():
            quote = get_fixed_quote(keno_type, h)
            print(f"    {h} Treffer: {count}x ({count/len(df_2025)*100:.1f}%) → {quote} EUR")

        # Erwartungswert
        ev = np.mean(wins_all) - 1  # Minus 1 EUR Einsatz
        print(f"  Erwartungswert pro Spiel: {ev:+.3f} EUR")

    # =========================================================================
    # 2. JACKPOT-TAGE VS NORMALE TAGE
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. V2 PERFORMANCE: Jackpot-Tage vs Normale Tage")
    print("=" * 80)

    for keno_type in [9, 10]:
        ticket = set(V2_TICKETS[keno_type])

        jp_hits = []
        normal_hits = []

        for _, row in df_2025.iterrows():
            h, _ = simulate(ticket, keno_type, row["numbers_set"])
            if row["is_jackpot"]:
                jp_hits.append(h)
            else:
                normal_hits.append(h)

        print(f"\nTyp {keno_type}:")
        print(f"  Jackpot-Tage:  Mean={np.mean(jp_hits):.2f}, Max={max(jp_hits)}")
        print(f"  Normale Tage:  Mean={np.mean(normal_hits):.2f}, Max={max(normal_hits)}")

    # =========================================================================
    # 3. WELCHES TICKET HAT DIE BESTEN CHANCEN AUF HIGH-WIN?
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. HIGH-WIN CHANCEN pro Ticket-Typ")
    print("=" * 80)

    print(f"\n{'Typ':<6} {'>=6 Treffer':>15} {'>=7 Treffer':>15} {'>=8 Treffer':>15} {'Max Treffer':>12}")
    print("-" * 70)

    for keno_type in [6, 7, 8, 9, 10]:
        ticket = set(V2_TICKETS[keno_type])
        hits_all = [sum(1 for n in ticket if n in row["numbers_set"])
                    for _, row in df_2025.iterrows()]

        pct_6 = sum(1 for h in hits_all if h >= 6) / len(hits_all) * 100
        pct_7 = sum(1 for h in hits_all if h >= 7) / len(hits_all) * 100
        pct_8 = sum(1 for h in hits_all if h >= 8) / len(hits_all) * 100

        print(f"Typ {keno_type:<3} {pct_6:>14.2f}% {pct_7:>14.2f}% {pct_8:>14.2f}% {max(hits_all):>12}")

    # =========================================================================
    # 4. SIGNAL-BASIERTE HIGH-RISK STRATEGIE
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. SIGNAL-BASIERTE STRATEGIE: Wann ist V2 am besten?")
    print("=" * 80)

    # Berechne mcount_mean für jeden Tag
    mcount_tracker = defaultdict(int)
    current_month = None

    for i in range(len(df_2025)):
        row = df_2025.iloc[i]
        draw_set = row["numbers_set"]
        draw_date = row["Datum"]

        if current_month is None or draw_date.month != current_month:
            mcount_tracker = defaultdict(int)
            current_month = draw_date.month

        for num in draw_set:
            mcount_tracker[num] += 1

        mcount_values = [mcount_tracker[num] for num in draw_set]
        df_2025.loc[df_2025.index[i], "mcount_mean"] = np.mean(mcount_values)

    # Teste: Bessere Performance wenn mcount_mean hoch?
    print("\nV2 Typ 9 Performance nach mcount_mean:")

    ticket = set(V2_TICKETS[9])
    for thresh in [7.0, 8.0, 8.5, 9.0]:
        high_mcount = df_2025[df_2025["mcount_mean"] >= thresh]
        low_mcount = df_2025[df_2025["mcount_mean"] < thresh]

        if len(high_mcount) > 0:
            high_hits = [sum(1 for n in ticket if n in row["numbers_set"])
                        for _, row in high_mcount.iterrows()]
            high_wins = [get_fixed_quote(9, h) for h in high_hits]
            high_ev = np.mean(high_wins) - 1

            low_hits = [sum(1 for n in ticket if n in row["numbers_set"])
                       for _, row in low_mcount.iterrows()]
            low_wins = [get_fixed_quote(9, h) for h in low_hits]
            low_ev = np.mean(low_wins) - 1

            print(f"\n  mcount_mean >= {thresh}:")
            print(f"    Tage: {len(high_mcount)} ({len(high_mcount)/len(df_2025)*100:.1f}%)")
            print(f"    Mean Hits: {np.mean(high_hits):.2f} vs {np.mean(low_hits):.2f}")
            print(f"    EV: {high_ev:+.3f} vs {low_ev:+.3f} EUR")
            print(f"    Max Hits: {max(high_hits)} vs {max(low_hits)}")

    # =========================================================================
    # 5. BESTE TAGE FINDEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. TOP 10 BESTE TAGE für V2 Typ 9")
    print("=" * 80)

    ticket = set(V2_TICKETS[9])
    df_2025["v2_hits"] = [sum(1 for n in ticket if n in row["numbers_set"])
                          for _, row in df_2025.iterrows()]
    df_2025["v2_win"] = [get_fixed_quote(9, h) for h in df_2025["v2_hits"]]

    top_days = df_2025.nlargest(10, "v2_hits")

    print(f"\n{'Datum':<12} {'Hits':>6} {'Gewinn':>8} {'Jackpot?':>10} {'mcount_mean':>12}")
    print("-" * 55)

    for _, row in top_days.iterrows():
        jp = "★ JA" if row["is_jackpot"] else "nein"
        print(f"{row['Datum'].date()} {row['v2_hits']:>6} {row['v2_win']:>7} EUR "
              f"{jp:>10} {row['mcount_mean']:>12.1f}")

    # =========================================================================
    # 6. HIGH-RISK EMPFEHLUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("HIGH-RISK STRATEGIE EMPFEHLUNG")
    print("=" * 80)

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       HIGH-RISK STRATEGIE                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  KERNFRAGE: Wann ist der beste Zeitpunkt für EINEN Schuss?                    ║
║                                                                               ║
║  ERKENNTNISSE:                                                                ║
║  1. V2 Typ 9 hat Max 6 Treffer erreicht (nie 8+ für 1000 EUR)                 ║
║  2. V2 Typ 10 hat bessere Chancen auf High-Wins (10 Zahlen = mehr Overlap)    ║
║  3. mcount_mean >= 9.0 korreliert mit JACKPOT-TAGEN, nicht mit HIGH-HITS      ║
║                                                                               ║
║  PROBLEM:                                                                     ║
║  Jackpot-Tag ≠ Hohe Treffer für unser Ticket!                                 ║
║  Die Signale sagen "wann Jackpot", nicht "wann unser Ticket gut performt"     ║
║                                                                               ║
║  ALTERNATIVE STRATEGIE:                                                       ║
║  Statt Jackpot-Vorhersage → ZAHLEN-VORHERSAGE                                 ║
║  Finde Signale die vorhersagen, wann UNSERE ZAHLEN erscheinen!                ║
║                                                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
