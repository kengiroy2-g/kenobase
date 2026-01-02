#!/usr/bin/env python3
"""
Backtest: Pure HZ7 W20 Strategie (Original aus VALIDIERTE_FAKTEN)

- Top-7 aus letzten 20 Ziehungen
- 7 Kombinationen (C(7,6) = 7)
- Jeden Tag spielen
- 7 EUR pro Tag

Testzeitraum: 2022-2025
"""

import pandas as pd
from pathlib import Path
from collections import Counter
from itertools import combinations

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"


def load_data():
    df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
    df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['zahlen'] = df[zahl_cols].apply(lambda row: set(int(x) for x in row if pd.notna(x)), axis=1)
    df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)
    return df


def get_hz7_w20(df, end_date):
    """Top-7 aus letzten 20 Ziehungen."""
    hist = df[df['datum'] < end_date].tail(20)
    if len(hist) < 20:
        return None
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return sorted([n for n, _ in freq.most_common(7)])


def check_hz7_jackpots(hz7, drawn):
    """Zaehle wie viele der 7 Kombinationen 6/6 haben."""
    jackpots = 0
    winning_combos = []
    for combo in combinations(hz7, 6):
        if len(set(combo) & drawn) == 6:
            jackpots += 1
            winning_combos.append(sorted(combo))
    return jackpots, winning_combos


def backtest_pure_hz7_w20(df):
    """Backtest ohne Regeln."""

    results = {
        'by_year': {},
        'jackpots': [],
        'total_cost': 0,
        'total_wins': 0,
        'total_jp_count': 0
    }

    start_idx = 20

    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        date = row['datum']
        drawn = row['zahlen']
        year = date.year

        if year not in results['by_year']:
            results['by_year'][year] = {
                'days': 0, 'cost': 0, 'jackpots': 0, 'wins': 0, 'jp_events': 0
            }

        hz7 = get_hz7_w20(df, date)
        if hz7 is None:
            continue

        results['total_cost'] += 7  # 7 EUR pro Tag
        results['by_year'][year]['days'] += 1
        results['by_year'][year]['cost'] += 7

        # Pruefe alle 7 Kombinationen
        jp_count, winning = check_hz7_jackpots(hz7, drawn)

        if jp_count > 0:
            results['total_jp_count'] += jp_count
            results['total_wins'] += jp_count * 500
            results['by_year'][year]['jackpots'] += jp_count
            results['by_year'][year]['wins'] += jp_count * 500
            results['by_year'][year]['jp_events'] += 1

            results['jackpots'].append({
                'date': date.strftime('%Y-%m-%d'),
                'hz7': hz7,
                'jp_count': jp_count,
                'winning_combos': winning,
                'drawn': sorted(list(drawn))[:10]
            })

    return results


def print_results(results):
    print("=" * 70)
    print("BACKTEST: PURE HZ7 W20 (Keine Regeln, 7 EUR/Tag)")
    print("=" * 70)
    print()

    print("JAHRESWEISE ERGEBNISSE")
    print("-" * 70)
    print(f"{'Jahr':<8} {'Tage':<8} {'Kosten':<10} {'JP-Events':<12} {'JP-Anzahl':<10} {'Gewinn':<10} {'ROI':<10}")
    print("-" * 70)

    total_events = 0
    for year in sorted(results['by_year'].keys()):
        data = results['by_year'][year]
        profit = data['wins'] - data['cost']
        roi = (profit / data['cost'] * 100) if data['cost'] > 0 else 0
        events = data.get('jp_events', 0)
        total_events += events
        print(f"{year:<8} {data['days']:<8} {data['cost']:<10} {events:<12} {data['jackpots']:<10} {data['wins']:<10} {roi:>8.1f}%")

    print("-" * 70)
    total_profit = results['total_wins'] - results['total_cost']
    total_roi = (total_profit / results['total_cost'] * 100) if results['total_cost'] > 0 else 0
    print(f"{'GESAMT':<8} {'':<8} {results['total_cost']:<10} {total_events:<12} {results['total_jp_count']:<10} {results['total_wins']:<10} {total_roi:>8.1f}%")
    print()

    # Jackpot-Details
    if results['jackpots']:
        print("JACKPOT-DETAILS (Tage mit mindestens 1 Jackpot)")
        print("-" * 70)
        for jp in results['jackpots']:
            print(f"  {jp['date']}: HZ7 {jp['hz7']}")
            print(f"             {jp['jp_count']}x Jackpot = {jp['jp_count'] * 500} EUR")
            if jp['jp_count'] == 7:
                print(f"             *** ALLE 7 ZAHLEN GEZOGEN! ***")
        print()

    # Zusammenfassung
    print("=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"  Zeitraum:           2022-2025 ({len(results['by_year'])} Jahre)")
    print(f"  Spieltage:          {results['total_cost'] // 7}")
    print(f"  Kosten:             {results['total_cost']} EUR")
    print(f"  Jackpot-Tage:       {len(results['jackpots'])}")
    print(f"  Jackpot-Anzahl:     {results['total_jp_count']} (mehrere pro Tag moeglich)")
    print(f"  Gewinn:             {results['total_wins']} EUR")
    print(f"  Bilanz:             {total_profit} EUR")
    print(f"  ROI:                {total_roi:.1f}%")
    print()

    if results['total_jp_count'] > 0:
        days = results['total_cost'] // 7
        print(f"  Tage pro Jackpot:     {days / results['total_jp_count']:.0f}")
        print(f"  Kosten pro Jackpot:   {results['total_cost'] / results['total_jp_count']:.0f} EUR")
        print(f"  Gewinn pro Jackpot:   500 EUR")
    print()

    # Monatliche Kosten
    months = results['total_cost'] // 7 / 30
    monthly_cost = results['total_cost'] / months if months > 0 else 0
    print(f"  Durchschnitt/Monat: {monthly_cost:.0f} EUR Kosten")
    print()


if __name__ == "__main__":
    print("Lade Daten...")
    df = load_data()
    print(f"Geladene Ziehungen: {len(df)}")
    print()

    print("Starte Backtest...")
    results = backtest_pure_hz7_w20(df)
    print_results(results)
