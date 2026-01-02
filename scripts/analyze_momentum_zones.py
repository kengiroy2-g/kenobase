#!/usr/bin/env python
"""
Momentum-basierte Zonen-Analyse

Statt "häufigste Zahlen" suchen wir "aufsteigende Zahlen" -
Zahlen deren Frequenz STEIGT sind wahrscheinlicher als solche die fallen.

Hypothese: Das System rotiert Zahlen - wir müssen erkennen WANN eine Zahl
in ihre "aktive Phase" eintritt.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_DIR = BASE_DIR / "results"


def load_data():
    """Lade KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=";", encoding="utf-8")
    df["datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].apply(
        lambda row: [int(x) for x in row if pd.notna(x)], axis=1
    )

    df = df.dropna(subset=["datum"])
    df = df.sort_values("datum").reset_index(drop=True)
    return df


def calculate_momentum(df, window_recent=10, window_old=30):
    """
    Berechne Momentum für jede Zahl.

    Momentum = Frequenz(letzte 10) / Frequenz(letzte 30)

    Wenn Momentum > 1: Zahl ist im Aufstieg
    Wenn Momentum < 1: Zahl ist im Abstieg
    """
    results = []

    for i in range(window_old, len(df)):
        current_date = df.iloc[i]["datum"]
        current_numbers = set(df.iloc[i]["zahlen"])

        # Alte Periode (z.B. letzte 30)
        old_period = df.iloc[i-window_old:i]
        freq_old = defaultdict(int)
        for zahlen in old_period["zahlen"]:
            for num in zahlen:
                freq_old[num] += 1

        # Neue Periode (z.B. letzte 10)
        new_period = df.iloc[i-window_recent:i]
        freq_new = defaultdict(int)
        for zahlen in new_period["zahlen"]:
            for num in zahlen:
                freq_new[num] += 1

        # Momentum berechnen
        momentum = {}
        for num in range(1, 71):
            old_rate = freq_old[num] / window_old
            new_rate = freq_new[num] / window_recent

            if old_rate > 0:
                momentum[num] = new_rate / old_rate
            else:
                momentum[num] = new_rate * 3 if new_rate > 0 else 0  # Neu erschienen

        # Top 23 nach Momentum (aufsteigende Zahlen)
        sorted_by_momentum = sorted(momentum.items(), key=lambda x: -x[1])
        rising_zone = set([n for n, _ in sorted_by_momentum[:23]])

        # Top 23 nach alter Frequenz (zum Vergleich)
        sorted_by_freq = sorted(freq_old.items(), key=lambda x: -x[1])
        freq_zone = set([n for n, _ in sorted_by_freq[:23]])

        # Hits in jeder Zone
        hits_rising = len(current_numbers & rising_zone)
        hits_freq = len(current_numbers & freq_zone)

        expected = 20 * 23 / 70  # 6.57

        results.append({
            "datum": current_date,
            "hits_rising": hits_rising,
            "hits_freq": hits_freq,
            "expected": expected,
            "lift_rising": hits_rising / expected,
            "lift_freq": hits_freq / expected,
            "rising_zone": sorted(rising_zone),
            "freq_zone": sorted(freq_zone),
        })

    return pd.DataFrame(results)


def analyze_recency_effect(df, test_windows=[5, 10, 15, 20, 30]):
    """
    Teste verschiedene "Recency" Fenster.

    Hypothese: Zahlen die GERADE erschienen sind, erscheinen NICHT wieder sofort.
    (Erschöpfungseffekt)
    """
    results = []

    for window in test_windows:
        hits_in_recent = []
        hits_not_recent = []

        for i in range(window, len(df)):
            current_numbers = set(df.iloc[i]["zahlen"])

            # Zahlen die in letzten N erschienen sind
            recent_period = df.iloc[i-window:i]
            recent_numbers = set()
            for zahlen in recent_period["zahlen"]:
                recent_numbers.update(zahlen)

            # Wie viele der aktuellen Zahlen waren in recent?
            hits_recent = len(current_numbers & recent_numbers)
            hits_fresh = len(current_numbers - recent_numbers)

            # Erwartung
            expected_recent = 20 * len(recent_numbers) / 70
            expected_fresh = 20 * (70 - len(recent_numbers)) / 70

            hits_in_recent.append(hits_recent / expected_recent if expected_recent > 0 else 0)
            hits_not_recent.append(hits_fresh / expected_fresh if expected_fresh > 0 else 0)

        results.append({
            "window": window,
            "lift_recent": np.mean(hits_in_recent),
            "lift_fresh": np.mean(hits_not_recent),
            "favor": "RECENT" if np.mean(hits_in_recent) > np.mean(hits_not_recent) else "FRESH",
        })

    return pd.DataFrame(results)


def analyze_gap_effect(df, gap_threshold=10):
    """
    Analysiere den "Gap-Effekt": Zahlen die lange nicht erschienen sind.

    Hypothese: Nach langer Pause steigt die Wahrscheinlichkeit.
    """
    results = []

    for i in range(100, len(df)):  # Brauchen Historie
        current_date = df.iloc[i]["datum"]
        current_numbers = set(df.iloc[i]["zahlen"])

        # Letzte Erscheinung jeder Zahl
        last_seen = {n: -1 for n in range(1, 71)}
        for j in range(i-1, max(0, i-100), -1):
            for num in df.iloc[j]["zahlen"]:
                if last_seen[num] == -1:
                    last_seen[num] = i - 1 - j  # Tage seit Erscheinung

        # Zahlen mit langem Gap (> threshold)
        long_gap_numbers = set([n for n, gap in last_seen.items() if gap >= gap_threshold])
        short_gap_numbers = set([n for n, gap in last_seen.items() if 0 <= gap < gap_threshold])

        # Hits
        hits_long_gap = len(current_numbers & long_gap_numbers)
        hits_short_gap = len(current_numbers & short_gap_numbers)

        # Erwartung
        exp_long = 20 * len(long_gap_numbers) / 70 if len(long_gap_numbers) > 0 else 0
        exp_short = 20 * len(short_gap_numbers) / 70 if len(short_gap_numbers) > 0 else 0

        lift_long = hits_long_gap / exp_long if exp_long > 0 else 0
        lift_short = hits_short_gap / exp_short if exp_short > 0 else 0

        results.append({
            "datum": current_date,
            "n_long_gap": len(long_gap_numbers),
            "n_short_gap": len(short_gap_numbers),
            "hits_long": hits_long_gap,
            "hits_short": hits_short_gap,
            "lift_long": lift_long,
            "lift_short": lift_short,
        })

    return pd.DataFrame(results)


def analyze_cluster_effect(df, window=30):
    """
    Analysiere Cluster-Effekt: Erscheinen Zahlen in Gruppen?

    Wenn Zahl X erscheint, erscheinen bestimmte andere Zahlen häufiger?
    """
    # Finde die häufigsten Paare
    pair_counts = defaultdict(int)
    total_draws = 0

    for zahlen in df["zahlen"]:
        total_draws += 1
        sorted_z = sorted(zahlen)
        for i in range(len(sorted_z)):
            for j in range(i+1, len(sorted_z)):
                pair_counts[(sorted_z[i], sorted_z[j])] += 1

    # Erwartete Paar-Häufigkeit bei Zufall
    # P(beide gezogen) = C(18,2) / C(68,2) ≈ 3.7%
    expected_pair = total_draws * (20/70) * (19/69)

    # Top Paare mit Lift > 1.5
    strong_pairs = []
    for pair, count in pair_counts.items():
        lift = count / expected_pair
        if lift > 1.3:  # 30% über Zufall
            strong_pairs.append({
                "pair": pair,
                "count": count,
                "lift": lift,
            })

    strong_pairs = sorted(strong_pairs, key=lambda x: -x["lift"])[:50]

    return strong_pairs


def create_smart_zone(df, window=30):
    """
    Erstelle eine "smarte" Zone basierend auf mehreren Faktoren:
    1. Momentum (aufsteigende Zahlen)
    2. Moderate Recency (nicht zu neu, nicht zu alt)
    3. Cluster-Bonus (Zahlen die zusammen erscheinen)
    """
    recent = df.tail(window)
    very_recent = df.tail(10)

    # 1. Frequenz im Window
    freq = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq[num] += 1

    # 2. Frequenz in letzten 10 (für Momentum)
    freq_recent = defaultdict(int)
    for zahlen in very_recent["zahlen"]:
        for num in zahlen:
            freq_recent[num] += 1

    # 3. Gap (Tage seit letzter Erscheinung)
    last_seen = {n: 999 for n in range(1, 71)}
    for i, row in enumerate(reversed(list(df.tail(50).itertuples()))):
        for num in row.zahlen:
            if last_seen[num] == 999:
                last_seen[num] = i

    # 4. Score berechnen
    scores = {}
    for num in range(1, 71):
        # Basis: Frequenz
        base_score = freq[num]

        # Momentum Bonus: Wenn Frequenz in letzten 10 > erwartet
        expected_10 = (freq[num] / window) * 10
        if freq_recent[num] > expected_10:
            momentum_bonus = (freq_recent[num] / expected_10 - 1) * 2
        else:
            momentum_bonus = 0

        # Gap Penalty/Bonus
        gap = last_seen[num]
        if gap <= 2:
            gap_factor = 0.8  # Zu kürzlich = Penalty
        elif gap <= 7:
            gap_factor = 1.0  # Normal
        elif gap <= 15:
            gap_factor = 1.2  # Überfällig = Bonus
        else:
            gap_factor = 1.5  # Sehr überfällig = großer Bonus

        scores[num] = base_score * (1 + momentum_bonus) * gap_factor

    # Top 23
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    smart_zone = [n for n, _ in sorted_scores[:23]]

    return smart_zone, scores


def backtest_smart_zone(df, window=30):
    """
    Backtest der Smart Zone Strategie.
    """
    results = []

    for i in range(window + 10, len(df)):
        # Historische Daten bis gestern
        hist = df.iloc[:i]
        current = df.iloc[i]
        current_numbers = set(current["zahlen"])

        # Smart Zone basierend auf Historie
        smart_zone, _ = create_smart_zone(hist, window)
        smart_zone_set = set(smart_zone)

        # Simple Freq Zone
        freq = defaultdict(int)
        for zahlen in hist.tail(window)["zahlen"]:
            for num in zahlen:
                freq[num] += 1
        freq_zone = set([n for n, _ in sorted(freq.items(), key=lambda x: -x[1])[:23]])

        # Hits
        hits_smart = len(current_numbers & smart_zone_set)
        hits_freq = len(current_numbers & freq_zone)

        expected = 20 * 23 / 70

        results.append({
            "datum": current["datum"],
            "hits_smart": hits_smart,
            "hits_freq": hits_freq,
            "lift_smart": hits_smart / expected,
            "lift_freq": hits_freq / expected,
            "smart_better": hits_smart > hits_freq,
        })

    return pd.DataFrame(results)


def main():
    print("=" * 80)
    print("MOMENTUM-BASIERTE ZONEN-ANALYSE")
    print("=" * 80)

    df = load_data()
    print(f"\nGeladene Ziehungen: {len(df)}")

    # 1. Momentum vs Frequenz
    print("\n" + "=" * 80)
    print("1. MOMENTUM vs FREQUENZ")
    print("=" * 80)

    mom_df = calculate_momentum(df, window_recent=10, window_old=30)

    print(f"\nDurchschnitt:")
    print(f"  Momentum Zone (aufsteigende Zahlen): {mom_df['hits_rising'].mean():.2f} Hits "
          f"(Lift: {mom_df['lift_rising'].mean():.2f}x)")
    print(f"  Frequenz Zone (häufigste Zahlen):    {mom_df['hits_freq'].mean():.2f} Hits "
          f"(Lift: {mom_df['lift_freq'].mean():.2f}x)")

    # 2. Recency Effekt
    print("\n" + "=" * 80)
    print("2. RECENCY EFFEKT (Erschöpfung vs Heißlaufen)")
    print("=" * 80)

    recency_df = analyze_recency_effect(df)
    print("\n  Window   Recent Lift   Fresh Lift   Favorit")
    print("-" * 50)
    for _, row in recency_df.iterrows():
        print(f"  {int(row['window']):3d}        {row['lift_recent']:.2f}x        "
              f"{row['lift_fresh']:.2f}x      {row['favor']}")

    # 3. Gap Effekt
    print("\n" + "=" * 80)
    print("3. GAP EFFEKT (Lange nicht gezogen)")
    print("=" * 80)

    gap_df = analyze_gap_effect(df, gap_threshold=10)
    print(f"\nDurchschnitt (Gap >= 10 Tage):")
    print(f"  Long Gap Zahlen: {gap_df['n_long_gap'].mean():.1f} Zahlen")
    print(f"  Lift Long Gap:   {gap_df['lift_long'].mean():.2f}x")
    print(f"  Lift Short Gap:  {gap_df['lift_short'].mean():.2f}x")

    if gap_df['lift_long'].mean() > gap_df['lift_short'].mean():
        print("\n  → LONG GAP Zahlen haben höhere Wahrscheinlichkeit!")
    else:
        print("\n  → SHORT GAP Zahlen haben höhere Wahrscheinlichkeit!")

    # 4. Cluster Effekt
    print("\n" + "=" * 80)
    print("4. CLUSTER EFFEKT (Zahlenpaare)")
    print("=" * 80)

    clusters = analyze_cluster_effect(df)
    print("\nTop 20 Zahlenpaare (Lift > 1.3x):")
    for i, c in enumerate(clusters[:20]):
        print(f"  {c['pair']}: {c['count']}x (Lift: {c['lift']:.2f}x)")

    # 5. Smart Zone Backtest
    print("\n" + "=" * 80)
    print("5. SMART ZONE BACKTEST")
    print("=" * 80)

    smart_df = backtest_smart_zone(df, window=30)
    print(f"\nSmart Zone vs Frequenz Zone (2022-2025):")
    print(f"  Smart Zone:  {smart_df['hits_smart'].mean():.2f} Hits (Lift: {smart_df['lift_smart'].mean():.2f}x)")
    print(f"  Freq Zone:   {smart_df['hits_freq'].mean():.2f} Hits (Lift: {smart_df['lift_freq'].mean():.2f}x)")
    print(f"\n  Smart besser: {smart_df['smart_better'].sum()}x ({smart_df['smart_better'].mean()*100:.1f}%)")

    # 2025 Ergebnis
    smart_2025 = smart_df[smart_df["datum"] >= "2025-01-01"]
    if len(smart_2025) > 0:
        print(f"\n  2025 Smart Zone: {smart_2025['hits_smart'].mean():.2f} Hits "
              f"(Lift: {smart_2025['lift_smart'].mean():.2f}x)")

    # 6. Aktuelles Ticket
    print("\n" + "=" * 80)
    print("6. AKTUELLES SMART ZONE TICKET")
    print("=" * 80)

    smart_zone, scores = create_smart_zone(df, window=30)
    print(f"\nSmart Zone (23 Zahlen):")
    print(f"  {smart_zone}")

    print(f"\nTop 9 für Ticket:")
    ticket = smart_zone[:9]
    print(f"  {ticket}")

    # Score Details
    print(f"\nScore Details (Top 15):")
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])[:15]
    for num, score in sorted_scores:
        print(f"  Zahl {num:2d}: Score {score:.2f}")

    # Speichern
    RESULTS_DIR.mkdir(exist_ok=True)
    import json
    result = {
        "timestamp": datetime.now().isoformat(),
        "smart_zone": smart_zone,
        "ticket": ticket,
        "avg_lift_smart": float(smart_df['lift_smart'].mean()),
        "avg_lift_freq": float(smart_df['lift_freq'].mean()),
    }
    with open(RESULTS_DIR / "momentum_zones_analysis.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nErgebnisse gespeichert: {RESULTS_DIR / 'momentum_zones_analysis.json'}")


if __name__ == "__main__":
    main()
