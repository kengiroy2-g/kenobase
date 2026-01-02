#!/usr/bin/env python
"""
Perioden-basierte Zonen-Analyse

Idee: Es gibt PERIODEN in denen bestimmte Zahlen "aktiv" sind.
Der Trick ist, den START und das ENDE einer Periode zu erkennen.

Hypothese: Das System rotiert in Zyklen - wenn wir den Zyklus erkennen,
können wir die nächste aktive Zone vorhersagen.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
JACKPOT_FILE = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
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


def load_jackpots():
    """Lade Jackpot-Daten."""
    df = pd.read_csv(JACKPOT_FILE, sep=";", encoding="utf-8")
    df["datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    # Nur echte Jackpots (Typ 10 mit 10/10 oder Typ 9 mit 9/9)
    jackpots = df[
        ((df["Keno-Typ"] == 10) & (df["Anzahl richtiger Zahlen"] == 10)) |
        ((df["Keno-Typ"] == 9) & (df["Anzahl richtiger Zahlen"] == 9))
    ]
    jackpots = jackpots[jackpots["Anzahl der Gewinner"] > 0]

    return sorted(jackpots["datum"].dt.date.unique())


def find_optimal_segment_length(df, min_len=7, max_len=60):
    """
    Finde die optimale Segment-Länge.

    Für jede Segment-Länge:
    1. Berechne die "dominante Zone" jedes Segments
    2. Teste wie gut diese Zone im NÄCHSTEN Segment funktioniert
    """
    results = []

    for seg_len in range(min_len, max_len + 1, 5):
        scores = []

        for i in range(seg_len * 2, len(df), seg_len):
            # Training Segment
            train_seg = df.iloc[i-seg_len*2:i-seg_len]
            # Test Segment
            test_seg = df.iloc[i-seg_len:i]

            # Finde dominante Zone im Training
            freq = defaultdict(int)
            for zahlen in train_seg["zahlen"]:
                for num in zahlen:
                    freq[num] += 1

            sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
            zone = set([n for n, _ in sorted_nums[:23]])

            # Teste im Test Segment
            hits_list = []
            for zahlen in test_seg["zahlen"]:
                hits = len(set(zahlen) & zone)
                hits_list.append(hits)

            expected = 20 * 23 / 70
            avg_hits = np.mean(hits_list)
            lift = avg_hits / expected

            scores.append(lift)

        results.append({
            "segment_length": seg_len,
            "avg_lift": np.mean(scores),
            "std_lift": np.std(scores),
            "n_segments": len(scores),
        })

    return pd.DataFrame(results)


def analyze_jackpot_zones(df, jackpots):
    """
    Analysiere Zonen VOR und NACH Jackpots.

    Hypothese: Nach einem Jackpot ändert sich die aktive Zone.
    """
    results = []

    for i, jp_date in enumerate(jackpots[:-1]):
        next_jp = jackpots[i + 1]

        # Ziehungen zwischen den Jackpots
        jp_datetime = pd.Timestamp(jp_date)
        next_jp_datetime = pd.Timestamp(next_jp)

        period = df[(df["datum"] > jp_datetime) & (df["datum"] <= next_jp_datetime)]

        if len(period) < 10:
            continue

        # Teile in erste und zweite Hälfte
        mid = len(period) // 2
        first_half = period.iloc[:mid]
        second_half = period.iloc[mid:]

        # Zone der ersten Hälfte
        freq_first = defaultdict(int)
        for zahlen in first_half["zahlen"]:
            for num in zahlen:
                freq_first[num] += 1

        zone_first = set([n for n, _ in sorted(freq_first.items(), key=lambda x: -x[1])[:23]])

        # Teste in zweiter Hälfte
        hits_list = []
        for zahlen in second_half["zahlen"]:
            hits = len(set(zahlen) & zone_first)
            hits_list.append(hits)

        expected = 20 * 23 / 70
        avg_hits = np.mean(hits_list)
        lift = avg_hits / expected

        results.append({
            "jp_start": jp_date,
            "jp_end": next_jp,
            "period_days": (next_jp - jp_date).days,
            "n_draws": len(period),
            "lift_first_to_second": lift,
            "zone_stability": "STABLE" if lift > 1.0 else "UNSTABLE",
        })

    return pd.DataFrame(results)


def analyze_weekly_patterns(df):
    """
    Analysiere wöchentliche Muster.

    Hypothese: Bestimmte Wochentage haben unterschiedliche aktive Zonen.
    """
    df = df.copy()
    df["weekday"] = df["datum"].dt.dayofweek

    weekday_zones = {}
    for wd in range(7):
        wd_data = df[df["weekday"] == wd]

        freq = defaultdict(int)
        for zahlen in wd_data["zahlen"]:
            for num in zahlen:
                freq[num] += 1

        zone = set([n for n, _ in sorted(freq.items(), key=lambda x: -x[1])[:23]])
        weekday_zones[wd] = zone

    # Vergleiche Zonen
    print("\nWochentag-Zonen Überlappung:")
    weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    for i in range(7):
        for j in range(i+1, 7):
            overlap = len(weekday_zones[i] & weekday_zones[j])
            print(f"  {weekdays[i]} vs {weekdays[j]}: {overlap}/23 gemeinsam")

    return weekday_zones


def find_zone_change_indicators(df, window=30):
    """
    Finde Indikatoren die einen Zonen-Wechsel anzeigen.

    Mögliche Indikatoren:
    1. Plötzlicher Anstieg der Treffer in "neuen" Zahlen
    2. Abfall der Treffer in der aktuellen Zone
    3. Veränderung in der Summen-Verteilung
    """
    results = []

    for i in range(window * 2, len(df)):
        old_period = df.iloc[i-window*2:i-window]
        new_period = df.iloc[i-window:i]
        current = df.iloc[i]
        current_numbers = set(current["zahlen"])

        # Alte Zone (basierend auf alter Periode)
        freq_old = defaultdict(int)
        for zahlen in old_period["zahlen"]:
            for num in zahlen:
                freq_old[num] += 1
        old_zone = set([n for n, _ in sorted(freq_old.items(), key=lambda x: -x[1])[:23]])

        # Neue Zone (basierend auf neuer Periode)
        freq_new = defaultdict(int)
        for zahlen in new_period["zahlen"]:
            for num in zahlen:
                freq_new[num] += 1
        new_zone = set([n for n, _ in sorted(freq_new.items(), key=lambda x: -x[1])[:23]])

        # Zone Change Indicator
        zone_overlap = len(old_zone & new_zone)
        zone_change = 23 - zone_overlap

        # Performance alter Zone in neuer Periode
        hits_old_zone = []
        for zahlen in new_period["zahlen"]:
            hits = len(set(zahlen) & old_zone)
            hits_old_zone.append(hits)
        avg_old_perf = np.mean(hits_old_zone)

        # Performance neuer Zone in neuer Periode
        hits_new_zone = []
        for zahlen in new_period["zahlen"]:
            hits = len(set(zahlen) & new_zone)
            hits_new_zone.append(hits)
        avg_new_perf = np.mean(hits_new_zone)

        # Aktuelle Hits
        hits_old = len(current_numbers & old_zone)
        hits_new = len(current_numbers & new_zone)

        results.append({
            "datum": current["datum"],
            "zone_change": zone_change,
            "old_zone_perf": avg_old_perf,
            "new_zone_perf": avg_new_perf,
            "perf_delta": avg_new_perf - avg_old_perf,
            "hits_old": hits_old,
            "hits_new": hits_new,
            "better_zone": "NEW" if hits_new > hits_old else "OLD" if hits_old > hits_new else "TIE",
        })

    return pd.DataFrame(results)


def create_adaptive_zone(df, window=30, momentum_weight=0.3):
    """
    Erstelle eine adaptive Zone die sich langsam anpasst.

    Statt abrupt zu wechseln, mischen wir alte und neue Zone.
    """
    recent = df.tail(window)
    very_recent = df.tail(10)

    # Langfristige Frequenz
    freq_long = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq_long[num] += 1

    # Kurzfristige Frequenz (Momentum)
    freq_short = defaultdict(int)
    for zahlen in very_recent["zahlen"]:
        for num in zahlen:
            freq_short[num] += 1

    # Kombinierter Score
    scores = {}
    for num in range(1, 71):
        long_score = freq_long[num] / window
        short_score = freq_short[num] / 10

        # Gewichteter Durchschnitt
        combined = (1 - momentum_weight) * long_score + momentum_weight * short_score

        # Bonus für aufsteigende Zahlen
        if short_score > long_score * 1.5:
            combined *= 1.3  # 30% Bonus für stark steigende

        scores[num] = combined

    # Top 23
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    adaptive_zone = [n for n, _ in sorted_scores[:23]]

    return adaptive_zone, scores


def backtest_period_strategy(df, period_length=20):
    """
    Backtest: Nutze die Zone der letzten Periode für die nächste.
    """
    results = []

    for i in range(period_length * 2, len(df)):
        # Trainings-Periode (vorletzte Periode)
        train = df.iloc[i-period_length*2:i-period_length]

        # Test (aktuelle Ziehung)
        current = df.iloc[i]
        current_numbers = set(current["zahlen"])

        # Zone aus Training
        freq = defaultdict(int)
        for zahlen in train["zahlen"]:
            for num in zahlen:
                freq[num] += 1

        zone = set([n for n, _ in sorted(freq.items(), key=lambda x: -x[1])[:23]])

        # Hits
        hits = len(current_numbers & zone)
        expected = 20 * 23 / 70

        results.append({
            "datum": current["datum"],
            "hits": hits,
            "lift": hits / expected,
        })

    return pd.DataFrame(results)


def main():
    print("=" * 80)
    print("PERIODEN-BASIERTE ZONEN-ANALYSE")
    print("=" * 80)

    df = load_data()
    print(f"\nGeladene Ziehungen: {len(df)}")

    # 1. Optimale Segment-Länge
    print("\n" + "=" * 80)
    print("1. OPTIMALE SEGMENT-LÄNGE")
    print("=" * 80)

    seg_df = find_optimal_segment_length(df, min_len=7, max_len=50)
    print("\n  Segment   Avg Lift   Std Lift")
    print("-" * 40)
    for _, row in seg_df.iterrows():
        print(f"  {int(row['segment_length']):3d} Tage    {row['avg_lift']:.3f}x     {row['std_lift']:.3f}")

    best_seg = seg_df.loc[seg_df["avg_lift"].idxmax()]
    print(f"\n  → Beste Segment-Länge: {int(best_seg['segment_length'])} Tage (Lift: {best_seg['avg_lift']:.3f}x)")

    # 2. Jackpot-basierte Perioden
    print("\n" + "=" * 80)
    print("2. JACKPOT-BASIERTE PERIODEN")
    print("=" * 80)

    try:
        jackpots = load_jackpots()
        print(f"\nGeladene Jackpots: {len(jackpots)}")

        jp_df = analyze_jackpot_zones(df, jackpots)
        print(f"\nStabilität der Zone innerhalb Jackpot-Perioden:")
        print(f"  Stabile Perioden:   {len(jp_df[jp_df['zone_stability'] == 'STABLE'])}x")
        print(f"  Instabile Perioden: {len(jp_df[jp_df['zone_stability'] == 'UNSTABLE'])}x")
        print(f"  Durchschnittlicher Lift: {jp_df['lift_first_to_second'].mean():.3f}x")

        # Korrelation mit Perioden-Länge
        short_periods = jp_df[jp_df["period_days"] <= 30]
        long_periods = jp_df[jp_df["period_days"] > 30]
        print(f"\n  Kurze Perioden (≤30 Tage): Lift {short_periods['lift_first_to_second'].mean():.3f}x")
        print(f"  Lange Perioden (>30 Tage): Lift {long_periods['lift_first_to_second'].mean():.3f}x")

    except Exception as e:
        print(f"  Fehler beim Laden der Jackpots: {e}")

    # 3. Wochentag-Muster
    print("\n" + "=" * 80)
    print("3. WOCHENTAG-MUSTER")
    print("=" * 80)

    weekday_zones = analyze_weekly_patterns(df)

    # 4. Zone-Change Indikatoren
    print("\n" + "=" * 80)
    print("4. ZONEN-WECHSEL INDIKATOREN")
    print("=" * 80)

    change_df = find_zone_change_indicators(df, window=30)

    print(f"\nDurchschnittliche Zone-Änderung pro Tag: {change_df['zone_change'].mean():.2f} Zahlen")
    print(f"Performance Delta (Neu vs Alt): {change_df['perf_delta'].mean():.3f}")

    # Wann ist NEW besser?
    new_better = change_df[change_df["better_zone"] == "NEW"]
    old_better = change_df[change_df["better_zone"] == "OLD"]
    print(f"\nNEUE Zone besser: {len(new_better)}x ({len(new_better)/len(change_df)*100:.1f}%)")
    print(f"ALTE Zone besser: {len(old_better)}x ({len(old_better)/len(change_df)*100:.1f}%)")

    # 5. Period-basierter Backtest
    print("\n" + "=" * 80)
    print("5. PERIODEN-BACKTEST")
    print("=" * 80)

    for period in [10, 15, 20, 30, 45]:
        bt_df = backtest_period_strategy(df, period_length=period)
        print(f"  Periode {period:2d} Tage: Lift {bt_df['lift'].mean():.3f}x, Hits {bt_df['hits'].mean():.2f}")

    # 6. Aktuelles Ticket
    print("\n" + "=" * 80)
    print("6. AKTUELLES ADAPTIVES TICKET")
    print("=" * 80)

    adaptive_zone, scores = create_adaptive_zone(df, window=30, momentum_weight=0.3)
    print(f"\nAdaptive Zone (23 Zahlen):")
    print(f"  {adaptive_zone}")

    ticket = adaptive_zone[:9]
    print(f"\nTicket (Top 9):")
    print(f"  {ticket}")

    # Speichern
    RESULTS_DIR.mkdir(exist_ok=True)
    import json
    result = {
        "timestamp": datetime.now().isoformat(),
        "adaptive_zone": adaptive_zone,
        "ticket": ticket,
        "optimal_segment_days": int(best_seg['segment_length']),
        "optimal_segment_lift": float(best_seg['avg_lift']),
    }
    with open(RESULTS_DIR / "period_zones_analysis.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nErgebnisse gespeichert: {RESULTS_DIR / 'period_zones_analysis.json'}")


if __name__ == "__main__":
    main()
