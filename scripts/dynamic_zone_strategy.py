#!/usr/bin/env python
"""
Dynamisches Zonen-System

Kombiniert:
1. Wochentag-spezifische Zonen (langfristig)
2. Kurzfristiges Momentum (letzte 10 Ziehungen)
3. Gültigkeitszeitraum-Tracking

Ziel: Das "richtige Drittel" für einen bestimmten Gültigkeitsraum finden.
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
    return df


def get_keno_quote(hits):
    """KENO Typ 9 Quoten."""
    quotes = {0: 2, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 5, 7: 20, 8: 1000, 9: 50000}
    return quotes.get(hits, 0)


def calculate_dynamic_zone(df, target_weekday, long_window=100, short_window=10):
    """
    Berechne eine dynamische Zone die Langzeit-Muster (Wochentag)
    mit Kurzzeit-Momentum kombiniert.
    """
    # 1. Langzeit: Wochentag-spezifische Frequenzen
    wd_data = df[df["weekday"] == target_weekday].tail(long_window)

    freq_long = defaultdict(int)
    for zahlen in wd_data["zahlen"]:
        for num in zahlen:
            freq_long[num] += 1

    # 2. Kurzzeit: Letzte N Ziehungen (unabhängig vom Wochentag)
    recent = df.tail(short_window)

    freq_short = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq_short[num] += 1

    # 3. Kombinierter Score
    # Gewichtung: 70% Langzeit (Wochentag), 30% Kurzzeit (Momentum)
    scores = {}
    for num in range(1, 71):
        long_score = freq_long[num] / long_window if long_window > 0 else 0
        short_score = freq_short[num] / short_window if short_window > 0 else 0

        # Normalisieren
        combined = 0.7 * long_score + 0.3 * short_score

        # Momentum Bonus: Wenn kurzfristig höher als langfristig
        if short_score > long_score * 1.5:
            combined *= 1.2  # 20% Bonus

        scores[num] = combined

    # Top 23
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
    zone = [n for n, _ in sorted_scores[:23]]

    return zone, scores


def calculate_zone_validity(df, zone, forward_days=10):
    """
    Berechne wie lange eine Zone gültig bleibt (wie viele Tage
    sie überdurchschnittliche Performance hat).
    """
    zone_set = set(zone)
    expected = 20 * len(zone) / 70

    performances = []
    for i in range(min(forward_days, len(df))):
        zahlen = set(df.iloc[-(forward_days-i)]["zahlen"]) if forward_days-i > 0 else set()
        if len(zahlen) > 0:
            hits = len(zahlen & zone_set)
            lift = hits / expected
            performances.append(lift)

    return performances


def backtest_dynamic_strategy(df, long_window=100, short_window=10):
    """
    Backtest der dynamischen Strategie.
    """
    results = []

    # Startpunkt: Genug Daten für Training
    start_idx = max(long_window * 7, short_window + 50)

    for i in range(start_idx, len(df)):
        current = df.iloc[i]
        current_numbers = set(current["zahlen"])
        current_weekday = current["weekday"]

        # Historische Daten
        hist = df.iloc[:i]

        # Dynamische Zone
        dynamic_zone, _ = calculate_dynamic_zone(
            hist, current_weekday,
            long_window=long_window,
            short_window=short_window
        )
        dynamic_zone_set = set(dynamic_zone)

        # Nur Wochentag-Zone (zum Vergleich)
        wd_data = hist[hist["weekday"] == current_weekday].tail(long_window)
        freq_wd = defaultdict(int)
        for zahlen in wd_data["zahlen"]:
            for num in zahlen:
                freq_wd[num] += 1
        weekday_zone = set([n for n, _ in sorted(freq_wd.items(), key=lambda x: -x[1])[:23]])

        # Allgemeine Zone (zum Vergleich)
        freq_gen = defaultdict(int)
        for zahlen in hist.tail(50)["zahlen"]:
            for num in zahlen:
                freq_gen[num] += 1
        general_zone = set([n for n, _ in sorted(freq_gen.items(), key=lambda x: -x[1])[:23]])

        # Hits
        hits_dynamic = len(current_numbers & dynamic_zone_set)
        hits_weekday = len(current_numbers & weekday_zone)
        hits_general = len(current_numbers & general_zone)

        expected = 20 * 23 / 70

        results.append({
            "datum": current["datum"],
            "weekday": current_weekday,
            "hits_dynamic": hits_dynamic,
            "hits_weekday": hits_weekday,
            "hits_general": hits_general,
            "lift_dynamic": hits_dynamic / expected,
            "lift_weekday": hits_weekday / expected,
            "lift_general": hits_general / expected,
        })

    return pd.DataFrame(results)


def optimize_weights(df, test_weights=None):
    """
    Finde optimale Gewichtung für Langzeit vs. Kurzzeit.
    """
    if test_weights is None:
        test_weights = [
            (100, 5), (100, 10), (100, 15), (100, 20),
            (75, 5), (75, 10), (75, 15),
            (50, 5), (50, 10), (50, 15),
        ]

    results = []
    for long_w, short_w in test_weights:
        bt_df = backtest_dynamic_strategy(df, long_window=long_w, short_window=short_w)

        results.append({
            "long_window": long_w,
            "short_window": short_w,
            "avg_hits": bt_df["hits_dynamic"].mean(),
            "lift": bt_df["lift_dynamic"].mean(),
            "vs_weekday": bt_df["lift_dynamic"].mean() - bt_df["lift_weekday"].mean(),
            "vs_general": bt_df["lift_dynamic"].mean() - bt_df["lift_general"].mean(),
        })

    return pd.DataFrame(results)


def generate_tickets_for_week(df, long_window=100, short_window=10):
    """
    Generiere Tickets für alle 7 Wochentage.
    """
    tickets = {}

    for wd in range(7):
        zone, scores = calculate_dynamic_zone(
            df, wd,
            long_window=long_window,
            short_window=short_window
        )
        ticket = zone[:9]

        tickets[WEEKDAYS[wd]] = {
            "zone": zone,
            "ticket": ticket,
            "top_scores": [(n, scores[n]) for n in ticket],
        }

    return tickets


def simulate_week_play(df, tickets, stake_per_draw=1):
    """
    Simuliere eine Woche Spielen mit den generierten Tickets.
    """
    last_week = df.tail(7)

    total_stake = 0
    total_win = 0

    print("\nSimulation letzte 7 Ziehungen:")
    print("-" * 60)

    for _, row in last_week.iterrows():
        wd = row["weekday"]
        ticket = set(tickets[WEEKDAYS[wd]]["ticket"])
        drawn = set(row["zahlen"])

        hits = len(ticket & drawn)
        win = get_keno_quote(hits)

        total_stake += stake_per_draw
        total_win += win

        print(f"  {row['datum'].strftime('%d.%m.%Y')} ({WEEKDAYS[wd]}): "
              f"{hits} Treffer = {win} EUR")

    print("-" * 60)
    print(f"  Einsatz: {total_stake} EUR")
    print(f"  Gewinn:  {total_win} EUR")
    print(f"  Netto:   {total_win - total_stake} EUR")
    print(f"  ROI:     {(total_win/total_stake - 1)*100:.1f}%")

    return total_win - total_stake


def main():
    print("=" * 80)
    print("DYNAMISCHES ZONEN-SYSTEM")
    print("=" * 80)

    df = load_data()
    print(f"\nGeladene Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['datum'].min().date()} bis {df['datum'].max().date()}")

    # 1. Parameter-Optimierung
    print("\n" + "=" * 80)
    print("1. PARAMETER-OPTIMIERUNG")
    print("=" * 80)

    opt_df = optimize_weights(df)
    print("\n  Long   Short   Avg Hits   Lift    vs WD    vs Gen")
    print("-" * 60)
    for _, row in opt_df.iterrows():
        print(f"  {int(row['long_window']):>3}    {int(row['short_window']):>3}      "
              f"{row['avg_hits']:.2f}     {row['lift']:.3f}x   "
              f"{row['vs_weekday']:+.3f}   {row['vs_general']:+.3f}")

    best = opt_df.loc[opt_df["lift"].idxmax()]
    print(f"\n  → Beste Konfiguration: Long={int(best['long_window'])}, Short={int(best['short_window'])}")
    print(f"     Lift: {best['lift']:.3f}x")

    # 2. Backtest mit bester Konfiguration
    print("\n" + "=" * 80)
    print("2. BACKTEST MIT OPTIMALER KONFIGURATION")
    print("=" * 80)

    bt_df = backtest_dynamic_strategy(
        df,
        long_window=int(best['long_window']),
        short_window=int(best['short_window'])
    )

    print(f"\nGesamtergebnis (2022-2025):")
    print(f"  Dynamic Zone:  {bt_df['hits_dynamic'].mean():.2f} Hits (Lift: {bt_df['lift_dynamic'].mean():.3f}x)")
    print(f"  Weekday Zone:  {bt_df['hits_weekday'].mean():.2f} Hits (Lift: {bt_df['lift_weekday'].mean():.3f}x)")
    print(f"  General Zone:  {bt_df['hits_general'].mean():.2f} Hits (Lift: {bt_df['lift_general'].mean():.3f}x)")

    # 2025 Ergebnis
    bt_2025 = bt_df[bt_df["datum"] >= "2025-01-01"]
    if len(bt_2025) > 0:
        print(f"\n2025 Ergebnis:")
        print(f"  Dynamic Zone: {bt_2025['hits_dynamic'].mean():.2f} Hits (Lift: {bt_2025['lift_dynamic'].mean():.3f}x)")
        print(f"  Weekday Zone: {bt_2025['hits_weekday'].mean():.2f} Hits (Lift: {bt_2025['lift_weekday'].mean():.3f}x)")

    # Ergebnis pro Wochentag
    print("\nErgebnis pro Wochentag:")
    for wd in range(7):
        wd_df = bt_df[bt_df["weekday"] == wd]
        print(f"  {WEEKDAYS[wd]}: Dynamic {wd_df['hits_dynamic'].mean():.2f} | "
              f"Weekday {wd_df['hits_weekday'].mean():.2f} | "
              f"General {wd_df['hits_general'].mean():.2f}")

    # 3. Aktuelle Tickets
    print("\n" + "=" * 80)
    print("3. AKTUELLE TICKETS FÜR DIESE WOCHE")
    print("=" * 80)

    tickets = generate_tickets_for_week(
        df,
        long_window=int(best['long_window']),
        short_window=int(best['short_window'])
    )

    for wd in range(7):
        info = tickets[WEEKDAYS[wd]]
        print(f"\n  {WEEKDAYS[wd]}:")
        print(f"    Zone:   {info['zone']}")
        print(f"    Ticket: {info['ticket']}")

    # 4. Simulation letzte Woche
    print("\n" + "=" * 80)
    print("4. SIMULATION (Letzte 7 Ziehungen)")
    print("=" * 80)

    simulate_week_play(df, tickets)

    # 5. Nächstes Ticket
    print("\n" + "=" * 80)
    print("5. NÄCHSTES TICKET")
    print("=" * 80)

    last_date = df["datum"].max()
    next_date = last_date + pd.Timedelta(days=1)
    next_weekday = next_date.dayofweek

    next_zone, next_scores = calculate_dynamic_zone(
        df, next_weekday,
        long_window=int(best['long_window']),
        short_window=int(best['short_window'])
    )

    print(f"\nNächste Ziehung: {next_date.strftime('%d.%m.%Y')} ({WEEKDAYS[next_weekday]})")
    print(f"\nGültigkeitsraum: Diese Woche für {WEEKDAYS[next_weekday]}")
    print(f"\nAktive Zone (23 Zahlen - das 'richtige Drittel'):")
    print(f"  {next_zone}")
    print(f"\nEmpfohlenes Ticket (Top 9):")
    print(f"  {next_zone[:9]}")

    # Score Details
    print(f"\nTop 9 Zahlen mit Scores:")
    for num in next_zone[:9]:
        print(f"  {num:2d}: Score {next_scores[num]:.4f}")

    # 6. Speichern
    RESULTS_DIR.mkdir(exist_ok=True)

    result = {
        "timestamp": datetime.now().isoformat(),
        "optimal_long_window": int(best['long_window']),
        "optimal_short_window": int(best['short_window']),
        "overall_lift": float(best['lift']),
        "next_date": next_date.strftime("%Y-%m-%d"),
        "next_weekday": WEEKDAYS[next_weekday],
        "next_zone": next_zone,
        "next_ticket": next_zone[:9],
        "all_weekday_tickets": {
            wd: {"ticket": tickets[wd]["ticket"], "zone": tickets[wd]["zone"]}
            for wd in WEEKDAYS
        },
        "validity_period": f"Woche {next_date.strftime('%W')}, {next_date.year}",
    }

    with open(RESULTS_DIR / "dynamic_zone_strategy.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nErgebnisse gespeichert: {RESULTS_DIR / 'dynamic_zone_strategy.json'}")


if __name__ == "__main__":
    main()
