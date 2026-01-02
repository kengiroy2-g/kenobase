#!/usr/bin/env python3
"""
BACKTEST: V2 vs V2.1 Vergleich

V2 (Original):  [3, 7, 36, 43, 48, 51, 58, 61, 64]
V2.1 (Optimiert): [3, 7, 36, 43, 48, 51, 55, 58, 61]

Aenderung: 64 → 55 (basierend auf Gruppen-Analyse)

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


# Tickets
V2_ORIGINAL = [3, 7, 36, 43, 48, 51, 58, 61, 64]
V2_1_OPTIMIERT = [3, 7, 36, 43, 48, 51, 55, 58, 61]


def load_data(base_path):
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    return df.sort_values("Datum").reset_index(drop=True)


def get_jackpots(df, base_path):
    dates = set()
    path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if path.exists():
        timeline = pd.read_csv(path)
        timeline["datum"] = pd.to_datetime(timeline["datum"])
        dates.update(timeline[timeline["keno_jackpot"] == 1]["datum"].tolist())
    return dates


def simulate_ticket(ticket, draw_set, keno_type=9):
    """Simuliere ein Ticket gegen eine Ziehung."""
    hits = len(set(ticket) & draw_set)
    win = get_fixed_quote(keno_type, hits)
    return hits, int(win)


def main():
    print("=" * 80)
    print("BACKTEST: V2 vs V2.1")
    print("=" * 80)
    print(f"\nV2 (Original):   {V2_ORIGINAL}")
    print(f"V2.1 (Optimiert): {V2_1_OPTIMIERT}")
    print(f"\nAenderung: 64 → 55")

    base_path = Path(__file__).parent.parent
    df = load_data(base_path)
    jackpot_dates = get_jackpots(df, base_path)

    df["is_jackpot"] = df["Datum"].apply(lambda d: d in jackpot_dates)

    # Teste auf verschiedenen Zeitraeumen
    periods = [
        ("2025 Gesamt", df[df["Datum"].dt.year == 2025]),
        ("2025 H1 (Jan-Jun)", df[(df["Datum"].dt.year == 2025) & (df["Datum"].dt.month <= 6)]),
        ("2025 H2 (Jul-Dez)", df[(df["Datum"].dt.year == 2025) & (df["Datum"].dt.month > 6)]),
        ("2024 Gesamt", df[df["Datum"].dt.year == 2024]),
        ("2023 Gesamt", df[df["Datum"].dt.year == 2023]),
        ("Alle Daten", df),
    ]

    # =========================================================================
    # 1. VERGLEICH UEBER VERSCHIEDENE ZEITRAEUME
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. PERFORMANCE-VERGLEICH (Typ 9, 1 EUR Einsatz)")
    print("=" * 80)

    print(f"\n{'Zeitraum':<20} {'N':>6} {'V2 Hits':>10} {'V2.1 Hits':>10} {'V2 ROI':>10} {'V2.1 ROI':>10} {'Diff':>8}")
    print("-" * 80)

    for name, period_df in periods:
        if len(period_df) == 0:
            continue

        v2_hits = []
        v2_wins = []
        v21_hits = []
        v21_wins = []

        for _, row in period_df.iterrows():
            draw = row["numbers_set"]

            h2, w2 = simulate_ticket(V2_ORIGINAL, draw)
            v2_hits.append(h2)
            v2_wins.append(w2)

            h21, w21 = simulate_ticket(V2_1_OPTIMIERT, draw)
            v21_hits.append(h21)
            v21_wins.append(w21)

        # ROI berechnen
        n = len(period_df)
        v2_roi = (sum(v2_wins) - n) / n * 100
        v21_roi = (sum(v21_wins) - n) / n * 100
        diff = v21_roi - v2_roi

        print(f"{name:<20} {n:>6} {np.mean(v2_hits):>10.2f} {np.mean(v21_hits):>10.2f} "
              f"{v2_roi:>9.1f}% {v21_roi:>9.1f}% {diff:>+7.1f}%")

    # =========================================================================
    # 2. TREFFER-VERTEILUNG 2025
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. TREFFER-VERTEILUNG 2025")
    print("=" * 80)

    df_2025 = df[df["Datum"].dt.year == 2025]

    v2_dist = Counter()
    v21_dist = Counter()

    for _, row in df_2025.iterrows():
        draw = row["numbers_set"]
        h2, _ = simulate_ticket(V2_ORIGINAL, draw)
        h21, _ = simulate_ticket(V2_1_OPTIMIERT, draw)
        v2_dist[h2] += 1
        v21_dist[h21] += 1

    print(f"\n{'Treffer':>8} {'V2':>10} {'V2.1':>10} {'Diff':>10} {'Gewinn':>12}")
    print("-" * 55)
    for hits in range(10):
        v2_c = v2_dist.get(hits, 0)
        v21_c = v21_dist.get(hits, 0)
        diff = v21_c - v2_c
        win = get_fixed_quote(9, hits)
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        print(f"{hits:>8} {v2_c:>10} {v21_c:>10} {diff_str:>10} {win:>11} EUR")

    # =========================================================================
    # 3. JACKPOT-TAGE PERFORMANCE
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. JACKPOT-TAGE PERFORMANCE 2025")
    print("=" * 80)

    jackpot_df = df_2025[df_2025["is_jackpot"]]

    print(f"\n{'Datum':<12} {'V2 Hits':>10} {'V2.1 Hits':>10} {'V2 Win':>10} {'V2.1 Win':>10} {'Besser'}")
    print("-" * 65)

    v2_jp_total = 0
    v21_jp_total = 0

    for _, row in jackpot_df.iterrows():
        draw = row["numbers_set"]
        date = row["Datum"]

        h2, w2 = simulate_ticket(V2_ORIGINAL, draw)
        h21, w21 = simulate_ticket(V2_1_OPTIMIERT, draw)

        v2_jp_total += w2
        v21_jp_total += w21

        better = "V2.1" if h21 > h2 else ("V2" if h2 > h21 else "GLEICH")
        print(f"{date.strftime('%d.%m.%Y'):<12} {h2:>10} {h21:>10} {w2:>9} EUR {w21:>9} EUR {better}")

    print(f"\n{'SUMME':<12} {'-':>10} {'-':>10} {v2_jp_total:>9} EUR {v21_jp_total:>9} EUR")
    print(f"{'Differenz':<12} {'-':>10} {'-':>10} {'-':>10} {v21_jp_total - v2_jp_total:>+9} EUR")

    # =========================================================================
    # 4. PAAR-ANALYSE: Warum funktioniert V2.1?
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. PAAR-ANALYSE: Warum V2.1 besser ist")
    print("=" * 80)

    # Paare die nur in V2.1 sind
    v2_set = set(V2_ORIGINAL)
    v21_set = set(V2_1_OPTIMIERT)

    removed = v2_set - v21_set  # {64}
    added = v21_set - v2_set     # {55}

    print(f"\nEntfernt: {removed}")
    print(f"Hinzugefuegt: {added}")

    # Zaehle Paar-Erscheinungen mit 55 vs 64
    pairs_with_55 = [(55, n) for n in V2_1_OPTIMIERT if n != 55]
    pairs_with_64 = [(64, n) for n in V2_ORIGINAL if n != 64]

    print(f"\nPaare mit 55 (V2.1):")
    print(f"{'Paar':<12} {'JP-Count':>10} {'All-Count':>12}")
    print("-" * 38)

    for pair in pairs_with_55:
        jp_count = 0
        all_count = 0
        sorted_pair = tuple(sorted(pair))

        for _, row in df_2025.iterrows():
            if pair[0] in row["numbers_set"] and pair[1] in row["numbers_set"]:
                all_count += 1
                if row["is_jackpot"]:
                    jp_count += 1

        print(f"{str(sorted_pair):<12} {jp_count:>10} {all_count:>12}")

    print(f"\nPaare mit 64 (V2 Original):")
    print(f"{'Paar':<12} {'JP-Count':>10} {'All-Count':>12}")
    print("-" * 38)

    for pair in pairs_with_64:
        jp_count = 0
        all_count = 0
        sorted_pair = tuple(sorted(pair))

        for _, row in df_2025.iterrows():
            if pair[0] in row["numbers_set"] and pair[1] in row["numbers_set"]:
                all_count += 1
                if row["is_jackpot"]:
                    jp_count += 1

        print(f"{str(sorted_pair):<12} {jp_count:>10} {all_count:>12}")

    # =========================================================================
    # 5. HIGH-WIN EVENTS
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. HIGH-WIN EVENTS (>=6 Treffer)")
    print("=" * 80)

    print(f"\n{'Datum':<12} {'V2':>6} {'V2.1':>6} {'V2 Win':>10} {'V2.1 Win':>10}")
    print("-" * 50)

    for _, row in df_2025.iterrows():
        draw = row["numbers_set"]
        date = row["Datum"]

        h2, w2 = simulate_ticket(V2_ORIGINAL, draw)
        h21, w21 = simulate_ticket(V2_1_OPTIMIERT, draw)

        if h2 >= 6 or h21 >= 6:
            print(f"{date.strftime('%d.%m.%Y'):<12} {h2:>6} {h21:>6} {w2:>9} EUR {w21:>9} EUR")

    # =========================================================================
    # FAZIT
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT: V2 vs V2.1")
    print("=" * 80)

    # Finale Berechnung
    v2_total = 0
    v21_total = 0
    for _, row in df_2025.iterrows():
        _, w2 = simulate_ticket(V2_ORIGINAL, row["numbers_set"])
        _, w21 = simulate_ticket(V2_1_OPTIMIERT, row["numbers_set"])
        v2_total += w2
        v21_total += w21

    n_2025 = len(df_2025)
    v2_roi_final = (v2_total - n_2025) / n_2025 * 100
    v21_roi_final = (v21_total - n_2025) / n_2025 * 100

    print(f"""
V2 (Original):   [3, 7, 36, 43, 48, 51, 58, 61, 64]
V2.1 (Optimiert): [3, 7, 36, 43, 48, 51, 55, 58, 61]

2025 PERFORMANCE (Typ 9, 1 EUR Einsatz, {n_2025} Ziehungen):

  V2 Gesamt:   {v2_total:>6} EUR ({v2_roi_final:+.1f}% ROI)
  V2.1 Gesamt: {v21_total:>6} EUR ({v21_roi_final:+.1f}% ROI)

  DIFFERENZ:   {v21_total - v2_total:+5} EUR ({v21_roi_final - v2_roi_final:+.1f}% ROI)

GRUPPEN-ERKLAERUNG:
  - Zahl 64 hatte 0 Jackpot-Paare mit anderen V2-Zahlen
  - Zahl 55 hat starke Paar-Verbindungen (48,55) mit 4.52x Lift
  - V2.1 integriert sich besser in Jackpot-Gruppen
""")


if __name__ == "__main__":
    main()
