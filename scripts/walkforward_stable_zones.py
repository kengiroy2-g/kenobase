#!/usr/bin/env python
"""
Walk-Forward mit STABILEN Zonen

Problem vorher: 652 Zonen für 729 Tage (fast täglich neu)
Lösung: Längere Gültigkeitsräume, weniger Wechsel

Ansatz:
1. Zone nur alle X Tage neu berechnen (z.B. wöchentlich)
2. Oder: Zone nur bei SIGNIFIKANTER Änderung wechseln (>50%)
3. Ticket bleibt stabil innerhalb der Gültigkeitsperiode
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import json

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_DIR = BASE_DIR / "results"

WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


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
    df["weekday"] = df["datum"].dt.dayofweek
    df["week"] = df["datum"].dt.isocalendar().week
    df["year_week"] = df["datum"].dt.strftime("%Y-W%W")
    return df


def get_keno_quote(hits):
    """KENO Typ 9 Quoten."""
    quotes = {0: 2, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 5, 7: 20, 8: 1000, 9: 50000}
    return quotes.get(hits, 0)


def calculate_zone(hist_df, long_window=100):
    """
    Berechne Zone basierend auf einfacher Frequenz (stabiler).
    """
    recent = hist_df.tail(long_window)

    freq = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq[num] += 1

    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    zone = [n for n, _ in sorted_nums[:23]]

    return zone


def run_weekly_zones(df, start_date="2024-01-01"):
    """
    Wöchentliche Zonen - Zone wird nur 1x pro Woche neu berechnet.
    """
    start_dt = pd.Timestamp(start_date)
    start_idx = df[df["datum"] >= start_dt].index[0]

    print("STRATEGIE: Wöchentliche Zonen")
    print(f"Zone wird jeden Montag neu berechnet")
    print("=" * 80)

    all_zones = []
    all_results = []

    current_zone = None
    current_ticket = None
    zone_id = 0
    last_zone_week = None

    for i in range(start_idx, len(df)):
        current = df.iloc[i]
        current_date = current["datum"]
        current_numbers = set(current["zahlen"])
        current_week = current["year_week"]

        hist = df.iloc[:i]

        # Neue Zone nur wenn neue Woche beginnt
        if current_week != last_zone_week:
            zone_id += 1
            current_zone = calculate_zone(hist, long_window=100)
            current_ticket = current_zone[:9]
            last_zone_week = current_week

            all_zones.append({
                "zone_id": zone_id,
                "start_week": current_week,
                "ticket": current_ticket,
            })

        # Test
        ticket_set = set(current_ticket)
        zone_set = set(current_zone)

        hits = len(current_numbers & ticket_set)
        zone_hits = len(current_numbers & zone_set)
        win = get_keno_quote(hits)

        all_results.append({
            "datum": current_date.strftime("%Y-%m-%d"),
            "zone_id": zone_id,
            "hits": hits,
            "zone_hits": zone_hits,
            "win": win,
        })

    return all_zones, all_results


def run_monthly_zones(df, start_date="2024-01-01"):
    """
    Monatliche Zonen - Zone wird nur 1x pro Monat neu berechnet.
    """
    start_dt = pd.Timestamp(start_date)
    start_idx = df[df["datum"] >= start_dt].index[0]

    print("STRATEGIE: Monatliche Zonen")
    print(f"Zone wird am 1. jeden Monats neu berechnet")
    print("=" * 80)

    all_zones = []
    all_results = []

    current_zone = None
    current_ticket = None
    zone_id = 0
    last_zone_month = None

    for i in range(start_idx, len(df)):
        current = df.iloc[i]
        current_date = current["datum"]
        current_numbers = set(current["zahlen"])
        current_month = current_date.strftime("%Y-%m")

        hist = df.iloc[:i]

        # Neue Zone nur wenn neuer Monat beginnt
        if current_month != last_zone_month:
            zone_id += 1
            current_zone = calculate_zone(hist, long_window=100)
            current_ticket = current_zone[:9]
            last_zone_month = current_month

            all_zones.append({
                "zone_id": zone_id,
                "start_month": current_month,
                "ticket": current_ticket,
            })

        # Test
        ticket_set = set(current_ticket)
        zone_set = set(current_zone)

        hits = len(current_numbers & ticket_set)
        zone_hits = len(current_numbers & zone_set)
        win = get_keno_quote(hits)

        all_results.append({
            "datum": current_date.strftime("%Y-%m-%d"),
            "zone_id": zone_id,
            "hits": hits,
            "zone_hits": zone_hits,
            "win": win,
        })

    return all_zones, all_results


def run_fixed_period_zones(df, start_date="2024-01-01", period_days=14):
    """
    Feste Perioden - Zone wird alle X Tage neu berechnet.
    """
    start_dt = pd.Timestamp(start_date)
    start_idx = df[df["datum"] >= start_dt].index[0]

    print(f"STRATEGIE: {period_days}-Tage Zonen")
    print(f"Zone wird alle {period_days} Tage neu berechnet")
    print("=" * 80)

    all_zones = []
    all_results = []

    current_zone = None
    current_ticket = None
    zone_id = 0
    zone_start_idx = start_idx

    for i in range(start_idx, len(df)):
        current = df.iloc[i]
        current_date = current["datum"]
        current_numbers = set(current["zahlen"])

        hist = df.iloc[:i]

        # Neue Zone alle X Tage
        if (i - zone_start_idx) >= period_days or current_zone is None:
            zone_id += 1
            current_zone = calculate_zone(hist, long_window=100)
            current_ticket = current_zone[:9]
            zone_start_idx = i

            all_zones.append({
                "zone_id": zone_id,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "ticket": current_ticket,
            })

        # Test
        ticket_set = set(current_ticket)
        zone_set = set(current_zone)

        hits = len(current_numbers & ticket_set)
        zone_hits = len(current_numbers & zone_set)
        win = get_keno_quote(hits)

        all_results.append({
            "datum": current_date.strftime("%Y-%m-%d"),
            "zone_id": zone_id,
            "hits": hits,
            "zone_hits": zone_hits,
            "win": win,
        })

    return all_zones, all_results


def analyze_results(results, zones, strategy_name):
    """Analysiere und drucke Ergebnisse."""
    total_stake = len(results)
    total_win = sum(r["win"] for r in results)
    total_netto = total_win - total_stake
    roi = (total_win / total_stake - 1) * 100

    avg_hits = sum(r["hits"] for r in results) / len(results)
    avg_zone_hits = sum(r["zone_hits"] for r in results) / len(results)
    expected_zone = 20 * 23 / 70
    zone_lift = avg_zone_hits / expected_zone

    print(f"\n{strategy_name}:")
    print(f"  Zonen erstellt: {len(zones)}")
    print(f"  Ziehungen: {len(results)}")
    print(f"  Avg Zone Hits: {avg_zone_hits:.2f} (Lift: {zone_lift:.3f}x)")
    print(f"  Avg Ticket Hits: {avg_hits:.2f}")
    print(f"  Einsatz: {total_stake} EUR")
    print(f"  Gewinn: {total_win} EUR")
    print(f"  Netto: {total_netto:+} EUR")
    print(f"  ROI: {roi:+.1f}%")

    # Treffer-Verteilung
    hit_counts = defaultdict(int)
    for r in results:
        hit_counts[r["hits"]] += 1

    print(f"\n  Treffer-Verteilung:")
    for h in range(10):
        count = hit_counts[h]
        if count > 0:
            pct = count / len(results) * 100
            print(f"    {h} Treffer: {count:4}x ({pct:5.1f}%)")

    return {
        "strategy": strategy_name,
        "zones": len(zones),
        "draws": len(results),
        "avg_zone_hits": avg_zone_hits,
        "zone_lift": zone_lift,
        "avg_ticket_hits": avg_hits,
        "stake": total_stake,
        "win": total_win,
        "netto": total_netto,
        "roi": roi,
    }


def main():
    print("=" * 80)
    print("WALK-FORWARD MIT STABILEN ZONEN")
    print("Test verschiedener Gültigkeitszeiträume")
    print("=" * 80)

    df = load_data()
    print(f"\nGeladene Ziehungen: {len(df)}")

    all_strategies = []

    # 1. Wöchentliche Zonen
    print("\n" + "=" * 80)
    zones, results = run_weekly_zones(df, "2024-01-01")
    stats = analyze_results(results, zones, "WÖCHENTLICH")
    all_strategies.append(stats)

    # 2. Monatliche Zonen
    print("\n" + "=" * 80)
    zones, results = run_monthly_zones(df, "2024-01-01")
    stats = analyze_results(results, zones, "MONATLICH")
    all_strategies.append(stats)

    # 3. 14-Tage Zonen
    print("\n" + "=" * 80)
    zones, results = run_fixed_period_zones(df, "2024-01-01", period_days=14)
    stats = analyze_results(results, zones, "14-TAGE")
    all_strategies.append(stats)

    # 4. 30-Tage Zonen
    print("\n" + "=" * 80)
    zones, results = run_fixed_period_zones(df, "2024-01-01", period_days=30)
    stats = analyze_results(results, zones, "30-TAGE")
    all_strategies.append(stats)

    # 5. 60-Tage Zonen
    print("\n" + "=" * 80)
    zones, results = run_fixed_period_zones(df, "2024-01-01", period_days=60)
    stats = analyze_results(results, zones, "60-TAGE")
    all_strategies.append(stats)

    # Vergleich
    print("\n" + "=" * 80)
    print("VERGLEICH ALLER STRATEGIEN")
    print("=" * 80)

    print(f"\n{'Strategie':<15} {'Zonen':>6} {'Zone Lift':>10} {'Ticket Hits':>12} {'ROI':>8}")
    print("-" * 60)

    for s in all_strategies:
        print(f"{s['strategy']:<15} {s['zones']:>6} {s['zone_lift']:>10.3f}x "
              f"{s['avg_ticket_hits']:>12.2f} {s['roi']:>+7.1f}%")

    # Beste Strategie
    best = max(all_strategies, key=lambda x: x["zone_lift"])
    print(f"\n→ Beste Zone-Performance: {best['strategy']} (Lift: {best['zone_lift']:.3f}x)")

    best_roi = max(all_strategies, key=lambda x: x["roi"])
    print(f"→ Beste ROI: {best_roi['strategy']} ({best_roi['roi']:+.1f}%)")

    # Erwartung bei Zufall
    print(f"\nZur Erinnerung:")
    print(f"  Zone Lift 1.000x = Zufall")
    print(f"  ROI -58% = KENO Typ 9 House Edge")

    # Speichern
    RESULTS_DIR.mkdir(exist_ok=True)
    output = {
        "timestamp": datetime.now().isoformat(),
        "test_period": "2024-01-01 bis 2025-12-29",
        "strategies": all_strategies,
    }
    with open(RESULTS_DIR / "stable_zones_comparison.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nErgebnisse gespeichert: {RESULTS_DIR / 'stable_zones_comparison.json'}")


if __name__ == "__main__":
    main()
