#!/usr/bin/env python
"""
Analyse: Aktive Zonen (1/3 der 70 Zahlen)

Hypothese: Zu jedem Zeitpunkt ist nur ~1/3 der Zahlen "aktiv".
Der Trick ist, dieses Drittel korrekt zu erkennen.

Ansatz:
1. Teile 70 Zahlen in Segmente
2. Analysiere welches Segment wann "hot" ist
3. Finde Indikatoren fuer Segment-Wechsel
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

# Pfade
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_DIR = BASE_DIR / "results"


def load_data():
    """Lade KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=";", encoding="utf-8")

    # Parse Datum
    df["datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    # Parse Zahlen aus separaten Spalten (Keno_Z1 bis Keno_Z20)
    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].apply(
        lambda row: [int(x) for x in row if pd.notna(x)], axis=1
    )

    df = df.dropna(subset=["datum"])
    df = df.sort_values("datum").reset_index(drop=True)
    return df


def get_number_zones():
    """Definiere 3 Zonen (Drittel) der 70 Zahlen."""
    return {
        "zone_A": set(range(1, 24)),    # 1-23 (niedrig)
        "zone_B": set(range(24, 48)),   # 24-47 (mittel)
        "zone_C": set(range(48, 71)),   # 48-70 (hoch)
    }


def analyze_zone_activity(df, window=50):
    """
    Analysiere welche Zone in welchem Zeitraum aktiv war.
    """
    zones = get_number_zones()
    results = []

    for i in range(window, len(df)):
        # Letzte N Ziehungen
        recent = df.iloc[i-window:i]
        current_date = df.iloc[i]["datum"]

        # Zaehle Treffer pro Zone
        zone_counts = {z: 0 for z in zones}
        total_numbers = 0

        for zahlen in recent["zahlen"]:
            for num in zahlen:
                total_numbers += 1
                for zone_name, zone_nums in zones.items():
                    if num in zone_nums:
                        zone_counts[zone_name] += 1
                        break

        # Berechne Anteile
        zone_shares = {z: c / total_numbers * 100 for z, c in zone_counts.items()}

        # Bestimme dominante Zone
        dominant = max(zone_shares, key=zone_shares.get)

        results.append({
            "datum": current_date,
            "zone_A_pct": zone_shares["zone_A"],
            "zone_B_pct": zone_shares["zone_B"],
            "zone_C_pct": zone_shares["zone_C"],
            "dominant": dominant,
            "dominant_pct": zone_shares[dominant],
        })

    return pd.DataFrame(results)


def analyze_dynamic_hot_zone(df, window=30):
    """
    Dynamische Hot-Zone Analyse: Finde die aktivsten 23 Zahlen
    in einem Rolling Window.
    """
    results = []

    for i in range(window, len(df)):
        # Letzte N Ziehungen
        recent = df.iloc[i-window:i]
        current_date = df.iloc[i]["datum"]
        current_numbers = set(df.iloc[i]["zahlen"])

        # Zaehle alle Zahlen
        freq = defaultdict(int)
        for zahlen in recent["zahlen"]:
            for num in zahlen:
                freq[num] += 1

        # Top 23 Zahlen (1/3 von 70)
        sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
        hot_zone = set([n for n, _ in sorted_nums[:23]])

        # Wie viele der aktuellen 20 Zahlen sind in der Hot Zone?
        hits_in_hot = len(current_numbers & hot_zone)

        # Erwartung bei Zufall: 20 * 23/70 = 6.57
        expected = 20 * 23 / 70

        results.append({
            "datum": current_date,
            "hot_zone": sorted(hot_zone),
            "hits_in_hot": hits_in_hot,
            "expected": expected,
            "lift": hits_in_hot / expected,
            "hot_coverage": hits_in_hot / 20 * 100,  # % der gezogenen in Hot Zone
        })

    return pd.DataFrame(results)


def find_optimal_zone_size(df, window=30):
    """
    Finde optimale Zonen-Groesse (nicht unbedingt 23).
    """
    results = []

    for zone_size in [15, 18, 20, 23, 25, 28, 30, 35]:
        lifts = []
        coverages = []

        for i in range(window, len(df)):
            recent = df.iloc[i-window:i]
            current_numbers = set(df.iloc[i]["zahlen"])

            # Zaehle alle Zahlen
            freq = defaultdict(int)
            for zahlen in recent["zahlen"]:
                for num in zahlen:
                    freq[num] += 1

            # Top N Zahlen
            sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
            hot_zone = set([n for n, _ in sorted_nums[:zone_size]])

            hits_in_hot = len(current_numbers & hot_zone)
            expected = 20 * zone_size / 70

            lifts.append(hits_in_hot / expected if expected > 0 else 0)
            coverages.append(hits_in_hot / 20 * 100)

        results.append({
            "zone_size": zone_size,
            "avg_lift": np.mean(lifts),
            "avg_coverage": np.mean(coverages),
            "coverage_std": np.std(coverages),
            "min_coverage": np.min(coverages),
            "max_coverage": np.max(coverages),
        })

    return pd.DataFrame(results)


def analyze_zone_stability(df, window=30, forecast=10):
    """
    Wie stabil bleibt die Hot Zone ueber Zeit?
    Wenn wir heute die Hot Zone bestimmen, wie gut ist sie in N Tagen?
    """
    results = []

    for i in range(window, len(df) - forecast):
        recent = df.iloc[i-window:i]

        # Bestimme Hot Zone HEUTE
        freq = defaultdict(int)
        for zahlen in recent["zahlen"]:
            for num in zahlen:
                freq[num] += 1

        sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
        hot_zone_today = set([n for n, _ in sorted_nums[:23]])

        # Teste auf naechste N Ziehungen
        future_hits = []
        for j in range(i, min(i + forecast, len(df))):
            future_numbers = set(df.iloc[j]["zahlen"])
            hits = len(future_numbers & hot_zone_today)
            future_hits.append(hits)

        # Verfall ueber Zeit
        results.append({
            "start_date": df.iloc[i]["datum"],
            "day_0": future_hits[0] if len(future_hits) > 0 else 0,
            "day_5": future_hits[4] if len(future_hits) > 4 else 0,
            "day_10": future_hits[9] if len(future_hits) > 9 else 0,
            "avg_hits": np.mean(future_hits),
        })

    return pd.DataFrame(results)


def analyze_zone_transitions(df, window=30):
    """
    Analysiere wann und wie sich die Hot Zone aendert.
    """
    transitions = []
    prev_hot_zone = None

    for i in range(window, len(df)):
        recent = df.iloc[i-window:i]
        current_date = df.iloc[i]["datum"]

        freq = defaultdict(int)
        for zahlen in recent["zahlen"]:
            for num in zahlen:
                freq[num] += 1

        sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
        hot_zone = set([n for n, _ in sorted_nums[:23]])

        if prev_hot_zone is not None:
            # Wie viele Zahlen haben sich geaendert?
            new_nums = hot_zone - prev_hot_zone
            dropped_nums = prev_hot_zone - hot_zone
            overlap = len(hot_zone & prev_hot_zone)

            transitions.append({
                "datum": current_date,
                "overlap": overlap,
                "new_count": len(new_nums),
                "dropped_count": len(dropped_nums),
                "stability": overlap / 23 * 100,
                "new_nums": sorted(new_nums),
                "dropped_nums": sorted(dropped_nums),
            })

        prev_hot_zone = hot_zone

    return pd.DataFrame(transitions)


def create_zone_ticket(df, window=30, ticket_size=9):
    """
    Generiere Ticket nur aus der Hot Zone.
    """
    recent = df.tail(window)

    freq = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq[num] += 1

    # Top 23 = Hot Zone
    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    hot_zone = [n for n, _ in sorted_nums[:23]]

    # Ticket: Top 9 aus Hot Zone
    ticket = hot_zone[:ticket_size]

    return ticket, hot_zone


def main():
    print("=" * 80)
    print("ANALYSE: AKTIVE ZONEN (1/3 DER 70 ZAHLEN)")
    print("=" * 80)

    df = load_data()
    print(f"\nGeladene Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['datum'].min().date()} bis {df['datum'].max().date()}")

    # 1. Statische Zonen-Analyse
    print("\n" + "=" * 80)
    print("1. STATISCHE ZONEN (1-23, 24-47, 48-70)")
    print("=" * 80)

    zone_activity = analyze_zone_activity(df, window=50)

    print("\nDurchschnittliche Verteilung:")
    print(f"  Zone A (1-23):  {zone_activity['zone_A_pct'].mean():.1f}%")
    print(f"  Zone B (24-47): {zone_activity['zone_B_pct'].mean():.1f}%")
    print(f"  Zone C (48-70): {zone_activity['zone_C_pct'].mean():.1f}%")

    print(f"\nErwartung bei Zufall: 32.9% / 34.3% / 32.9%")

    # Dominante Zone pro Monat (2025)
    zone_2025 = zone_activity[zone_activity["datum"] >= "2025-01-01"].copy()
    if len(zone_2025) > 0:
        print("\nDominante Zone in 2025 (pro Monat):")
        zone_2025["month"] = zone_2025["datum"].dt.to_period("M")
        monthly = zone_2025.groupby("month").agg({
            "zone_A_pct": "mean",
            "zone_B_pct": "mean",
            "zone_C_pct": "mean",
        })
        for month, row in monthly.iterrows():
            dominant = "A" if row["zone_A_pct"] > row["zone_B_pct"] and row["zone_A_pct"] > row["zone_C_pct"] else \
                       "B" if row["zone_B_pct"] > row["zone_C_pct"] else "C"
            print(f"  {month}: Zone {dominant} ({max(row):.1f}%)")

    # 2. Dynamische Hot Zone
    print("\n" + "=" * 80)
    print("2. DYNAMISCHE HOT ZONE (Top 23 nach Frequenz)")
    print("=" * 80)

    hot_zone_df = analyze_dynamic_hot_zone(df, window=30)

    print(f"\nDurchschnitt ueber alle Ziehungen:")
    print(f"  Hits in Hot Zone: {hot_zone_df['hits_in_hot'].mean():.2f} von 20")
    print(f"  Erwartung Zufall: {hot_zone_df['expected'].mean():.2f}")
    print(f"  Lift: {hot_zone_df['lift'].mean():.2f}x")
    print(f"  Coverage: {hot_zone_df['hot_coverage'].mean():.1f}%")

    # Verteilung
    print("\nVerteilung der Hits in Hot Zone:")
    for hits in range(0, 16):
        count = len(hot_zone_df[hot_zone_df["hits_in_hot"] == hits])
        if count > 0:
            pct = count / len(hot_zone_df) * 100
            bar = "#" * int(pct / 2)
            print(f"  {hits:2d} Hits: {count:4d}x ({pct:5.1f}%) {bar}")

    # 3. Optimale Zonen-Groesse
    print("\n" + "=" * 80)
    print("3. OPTIMALE ZONEN-GROESSE")
    print("=" * 80)

    optimal_df = find_optimal_zone_size(df, window=30)
    print("\n  Size   Avg Lift   Avg Coverage   Min    Max")
    print("-" * 50)
    for _, row in optimal_df.iterrows():
        print(f"  {int(row['zone_size']):3d}      {row['avg_lift']:.2f}x      "
              f"{row['avg_coverage']:5.1f}%      {row['min_coverage']:.0f}%   {row['max_coverage']:.0f}%")

    # 4. Zonen-Stabilitaet ueber Zeit
    print("\n" + "=" * 80)
    print("4. ZONEN-STABILITAET (Verfall ueber Zeit)")
    print("=" * 80)

    stability_df = analyze_zone_stability(df, window=30, forecast=10)

    print("\nDurchschnittliche Hits wenn Hot Zone an Tag 0 definiert:")
    print(f"  Tag 0:  {stability_df['day_0'].mean():.2f} Hits")
    print(f"  Tag 5:  {stability_df['day_5'].mean():.2f} Hits")
    print(f"  Tag 10: {stability_df['day_10'].mean():.2f} Hits")
    print(f"\n  Verfall Tag 0->5:  {(1 - stability_df['day_5'].mean()/stability_df['day_0'].mean())*100:.1f}%")
    print(f"  Verfall Tag 0->10: {(1 - stability_df['day_10'].mean()/stability_df['day_0'].mean())*100:.1f}%")

    # 5. Zonen-Transitionen
    print("\n" + "=" * 80)
    print("5. ZONEN-TRANSITIONEN (Wie oft aendert sich die Zone?)")
    print("=" * 80)

    transitions_df = analyze_zone_transitions(df, window=30)

    print(f"\nDurchschnittliche Stabilitaet: {transitions_df['stability'].mean():.1f}%")
    print(f"Durchschnittlich neue Zahlen pro Tag: {transitions_df['new_count'].mean():.2f}")

    # Grosse Transitionen
    big_transitions = transitions_df[transitions_df["new_count"] >= 3]
    print(f"\nGrosse Transitionen (3+ neue Zahlen): {len(big_transitions)}x")

    if len(big_transitions) > 0:
        recent_big = big_transitions.tail(5)
        print("\nLetzte 5 grosse Transitionen:")
        for _, row in recent_big.iterrows():
            print(f"  {row['datum'].strftime('%d.%m.%Y')}: "
                  f"+{row['new_count']} neue, -{row['dropped_count']} raus")

    # 6. Aktuelles Ticket
    print("\n" + "=" * 80)
    print("6. AKTUELLES TICKET (Nur aus Hot Zone)")
    print("=" * 80)

    ticket, hot_zone = create_zone_ticket(df, window=30, ticket_size=9)

    print(f"\nAktuelle Hot Zone (23 Zahlen):")
    print(f"  {sorted(hot_zone)}")

    print(f"\nEmpfohlenes Ticket (Top 9 aus Hot Zone):")
    print(f"  {ticket}")

    # Zone-Verteilung im Ticket
    zones = get_number_zones()
    zone_dist = {z: len(set(ticket) & zones[z]) for z in zones}
    print(f"\n  Zone A (1-23):  {zone_dist['zone_A']} Zahlen")
    print(f"  Zone B (24-47): {zone_dist['zone_B']} Zahlen")
    print(f"  Zone C (48-70): {zone_dist['zone_C']} Zahlen")

    # Speichern
    RESULTS_DIR.mkdir(exist_ok=True)
    result = {
        "timestamp": datetime.now().isoformat(),
        "window": 30,
        "hot_zone": sorted(hot_zone),
        "ticket": ticket,
        "avg_coverage": float(hot_zone_df['hot_coverage'].mean()),
        "avg_lift": float(hot_zone_df['lift'].mean()),
        "zone_stability": float(transitions_df['stability'].mean()),
    }

    import json
    with open(RESULTS_DIR / "active_zones_analysis.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nErgebnisse gespeichert: {RESULTS_DIR / 'active_zones_analysis.json'}")


if __name__ == "__main__":
    main()
