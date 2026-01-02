#!/usr/bin/env python
"""
Wochentag-basierte Zonen-Strategie

Erkenntnis: Die Wochentage haben unterschiedliche "aktive Zonen".
Mi und Do haben z.B. nur 4/23 gemeinsam.

Strategie: Für jeden Wochentag eine separate Zone verwenden.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime

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


def calculate_weekday_zones(df, window=50):
    """
    Berechne die Zone für jeden Wochentag basierend auf historischen Daten.
    """
    zones = {}

    for wd in range(7):
        wd_data = df[df["weekday"] == wd].tail(window)

        freq = defaultdict(int)
        for zahlen in wd_data["zahlen"]:
            for num in zahlen:
                freq[num] += 1

        sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
        zone = [n for n, _ in sorted_nums[:23]]
        zones[wd] = zone

    return zones


def backtest_weekday_strategy(df, train_window=50):
    """
    Backtest: Nutze wochentag-spezifische Zonen.
    """
    results = []

    # Für jeden möglichen Test-Punkt
    for i in range(train_window * 7, len(df)):
        current = df.iloc[i]
        current_numbers = set(current["zahlen"])
        current_weekday = current["weekday"]

        # Historische Daten für Training
        train_df = df.iloc[:i]

        # Zone für diesen Wochentag
        wd_train = train_df[train_df["weekday"] == current_weekday].tail(train_window)

        freq = defaultdict(int)
        for zahlen in wd_train["zahlen"]:
            for num in zahlen:
                freq[num] += 1

        sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
        weekday_zone = set([n for n, _ in sorted_nums[:23]])

        # Allgemeine Zone (zum Vergleich)
        general_train = train_df.tail(train_window)
        freq_gen = defaultdict(int)
        for zahlen in general_train["zahlen"]:
            for num in zahlen:
                freq_gen[num] += 1

        sorted_gen = sorted(freq_gen.items(), key=lambda x: -x[1])
        general_zone = set([n for n, _ in sorted_gen[:23]])

        # Hits
        hits_weekday = len(current_numbers & weekday_zone)
        hits_general = len(current_numbers & general_zone)

        expected = 20 * 23 / 70

        results.append({
            "datum": current["datum"],
            "weekday": current_weekday,
            "hits_weekday": hits_weekday,
            "hits_general": hits_general,
            "lift_weekday": hits_weekday / expected,
            "lift_general": hits_general / expected,
            "weekday_better": hits_weekday > hits_general,
        })

    return pd.DataFrame(results)


def analyze_weekday_stability(df, window=30):
    """
    Analysiere wie stabil die Wochentag-Zonen über Zeit sind.
    """
    results = []

    for wd in range(7):
        wd_data = df[df["weekday"] == wd]

        if len(wd_data) < window * 2:
            continue

        stabilities = []
        for i in range(window, len(wd_data) - window):
            old_period = wd_data.iloc[i-window:i]
            new_period = wd_data.iloc[i:i+window]

            # Alte Zone
            freq_old = defaultdict(int)
            for zahlen in old_period["zahlen"]:
                for num in zahlen:
                    freq_old[num] += 1
            old_zone = set([n for n, _ in sorted(freq_old.items(), key=lambda x: -x[1])[:23]])

            # Neue Zone
            freq_new = defaultdict(int)
            for zahlen in new_period["zahlen"]:
                for num in zahlen:
                    freq_new[num] += 1
            new_zone = set([n for n, _ in sorted(freq_new.items(), key=lambda x: -x[1])[:23]])

            overlap = len(old_zone & new_zone) / 23
            stabilities.append(overlap)

        results.append({
            "weekday": wd,
            "weekday_name": WEEKDAYS[wd],
            "avg_stability": np.mean(stabilities),
            "min_stability": np.min(stabilities),
            "max_stability": np.max(stabilities),
        })

    return pd.DataFrame(results)


def find_best_weekday_window(df):
    """
    Finde die optimale Window-Größe für Wochentag-Zonen.
    """
    results = []

    for window in [10, 20, 30, 40, 50, 75, 100]:
        bt_df = backtest_weekday_strategy(df, train_window=window)

        results.append({
            "window": window,
            "avg_lift_weekday": bt_df["lift_weekday"].mean(),
            "avg_lift_general": bt_df["lift_general"].mean(),
            "weekday_win_rate": bt_df["weekday_better"].mean() * 100,
        })

    return pd.DataFrame(results)


def create_weekday_ticket(df, weekday, window=50):
    """
    Erstelle ein Ticket für einen bestimmten Wochentag.
    """
    wd_data = df[df["weekday"] == weekday].tail(window)

    freq = defaultdict(int)
    for zahlen in wd_data["zahlen"]:
        for num in zahlen:
            freq[num] += 1

    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    zone = [n for n, _ in sorted_nums[:23]]
    ticket = zone[:9]

    return ticket, zone


def main():
    print("=" * 80)
    print("WOCHENTAG-BASIERTE ZONEN-STRATEGIE")
    print("=" * 80)

    df = load_data()
    print(f"\nGeladene Ziehungen: {len(df)}")

    # 1. Aktuelle Wochentag-Zonen
    print("\n" + "=" * 80)
    print("1. AKTUELLE WOCHENTAG-ZONEN (letzte 50 Ziehungen pro Tag)")
    print("=" * 80)

    zones = calculate_weekday_zones(df, window=50)

    for wd in range(7):
        print(f"\n  {WEEKDAYS[wd]}: {zones[wd][:10]}...")

    # Zonen-Überlappung Matrix
    print("\n\nZonen-Überlappung Matrix:")
    print("    ", end="")
    for wd in WEEKDAYS:
        print(f" {wd:>4}", end="")
    print()

    for i in range(7):
        print(f"  {WEEKDAYS[i]}", end="")
        for j in range(7):
            overlap = len(set(zones[i]) & set(zones[j]))
            print(f" {overlap:>4}", end="")
        print()

    # 2. Stabilität der Wochentag-Zonen
    print("\n" + "=" * 80)
    print("2. STABILITÄT DER WOCHENTAG-ZONEN")
    print("=" * 80)

    stab_df = analyze_weekday_stability(df, window=30)
    print("\n  Wochentag   Avg Stab   Min Stab   Max Stab")
    print("-" * 50)
    for _, row in stab_df.iterrows():
        print(f"  {row['weekday_name']:>8}     {row['avg_stability']:.1%}      "
              f"{row['min_stability']:.1%}      {row['max_stability']:.1%}")

    # 3. Optimale Window-Größe
    print("\n" + "=" * 80)
    print("3. OPTIMALE WINDOW-GRÖSSE")
    print("=" * 80)

    win_df = find_best_weekday_window(df)
    print("\n  Window   Weekday Lift   General Lift   Weekday Win%")
    print("-" * 60)
    for _, row in win_df.iterrows():
        print(f"  {int(row['window']):>4}        {row['avg_lift_weekday']:.3f}x         "
              f"{row['avg_lift_general']:.3f}x         {row['weekday_win_rate']:.1f}%")

    best_win = win_df.loc[win_df["avg_lift_weekday"].idxmax()]
    print(f"\n  → Beste Window-Größe: {int(best_win['window'])} (Lift: {best_win['avg_lift_weekday']:.3f}x)")

    # 4. Backtest-Ergebnisse
    print("\n" + "=" * 80)
    print("4. BACKTEST: WOCHENTAG vs ALLGEMEIN")
    print("=" * 80)

    bt_df = backtest_weekday_strategy(df, train_window=int(best_win['window']))

    print(f"\nGesamtergebnis (2022-2025):")
    print(f"  Wochentag-Zone: {bt_df['hits_weekday'].mean():.2f} Hits (Lift: {bt_df['lift_weekday'].mean():.3f}x)")
    print(f"  Allgemeine Zone: {bt_df['hits_general'].mean():.2f} Hits (Lift: {bt_df['lift_general'].mean():.3f}x)")
    print(f"\n  Wochentag besser: {bt_df['weekday_better'].sum()}x ({bt_df['weekday_better'].mean()*100:.1f}%)")

    # Ergebnis pro Wochentag
    print("\nErgebnis pro Wochentag:")
    for wd in range(7):
        wd_df = bt_df[bt_df["weekday"] == wd]
        print(f"  {WEEKDAYS[wd]}: Weekday {wd_df['hits_weekday'].mean():.2f} vs General {wd_df['hits_general'].mean():.2f}")

    # 2025 Ergebnis
    bt_2025 = bt_df[bt_df["datum"] >= "2025-01-01"]
    if len(bt_2025) > 0:
        print(f"\n2025 Ergebnis:")
        print(f"  Wochentag-Zone: {bt_2025['hits_weekday'].mean():.2f} Hits (Lift: {bt_2025['lift_weekday'].mean():.3f}x)")
        print(f"  Wochentag besser: {bt_2025['weekday_better'].sum()}x ({bt_2025['weekday_better'].mean()*100:.1f}%)")

    # 5. Tickets für jeden Wochentag
    print("\n" + "=" * 80)
    print("5. TICKETS FÜR JEDEN WOCHENTAG")
    print("=" * 80)

    optimal_window = int(best_win['window'])
    for wd in range(7):
        ticket, zone = create_weekday_ticket(df, wd, window=optimal_window)
        print(f"\n  {WEEKDAYS[wd]}: {ticket}")

    # 6. Nächstes Ticket (basierend auf morgen)
    print("\n" + "=" * 80)
    print("6. NÄCHSTES TICKET")
    print("=" * 80)

    # Heute ist der letzte Tag im Datensatz
    last_date = df["datum"].max()
    next_date = last_date + pd.Timedelta(days=1)
    next_weekday = next_date.dayofweek

    ticket, zone = create_weekday_ticket(df, next_weekday, window=optimal_window)
    print(f"\nNächste Ziehung: {next_date.strftime('%d.%m.%Y')} ({WEEKDAYS[next_weekday]})")
    print(f"\nEmpfohlene Zone (23 Zahlen):")
    print(f"  {zone}")
    print(f"\nEmpfohlenes Ticket (Top 9):")
    print(f"  {ticket}")

    # Speichern
    RESULTS_DIR.mkdir(exist_ok=True)
    import json

    all_tickets = {}
    for wd in range(7):
        ticket, zone = create_weekday_ticket(df, wd, window=optimal_window)
        all_tickets[WEEKDAYS[wd]] = {
            "ticket": ticket,
            "zone": zone,
        }

    result = {
        "timestamp": datetime.now().isoformat(),
        "optimal_window": optimal_window,
        "next_date": next_date.strftime("%Y-%m-%d"),
        "next_weekday": WEEKDAYS[next_weekday],
        "next_ticket": ticket,
        "next_zone": zone,
        "all_weekday_tickets": all_tickets,
        "weekday_lift": float(bt_df['lift_weekday'].mean()),
        "general_lift": float(bt_df['lift_general'].mean()),
    }
    with open(RESULTS_DIR / "weekday_zones_analysis.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nErgebnisse gespeichert: {RESULTS_DIR / 'weekday_zones_analysis.json'}")


if __name__ == "__main__":
    main()
