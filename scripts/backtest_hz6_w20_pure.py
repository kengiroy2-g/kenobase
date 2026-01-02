#!/usr/bin/env python3
"""
Backtest: Pure HZ6 W20 Strategie

Keine Regeln. Nur:
- Top-6 aus letzten 20 Ziehungen
- Jeden Tag spielen
- 1 EUR pro Tag

Testzeitraum: 2022-2025 (komplett)
"""

import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"


def load_data():
    df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
    df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['zahlen'] = df[zahl_cols].apply(lambda row: set(int(x) for x in row if pd.notna(x)), axis=1)
    df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)
    return df


def get_hz6_w20(df, end_date):
    """Top-6 aus letzten 20 Ziehungen."""
    hist = df[df['datum'] < end_date].tail(20)
    if len(hist) < 20:
        return None
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return sorted([n for n, _ in freq.most_common(6)])


def check_jackpot(hz6, drawn):
    """6/6 = alle 6 Zahlen gezogen."""
    return len(set(hz6) & drawn) == 6


def count_hits(hz6, drawn):
    """Zaehle Treffer."""
    return len(set(hz6) & drawn)


def backtest_pure_hz6_w20(df):
    """Backtest ohne Regeln."""

    results = {
        'by_year': {},
        'jackpots': [],
        'total_cost': 0,
        'total_wins': 0,
        'hit_distribution': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    }

    # Starte ab 2022-02 (brauchen 20 Ziehungen Historie)
    start_idx = 20

    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        date = row['datum']
        drawn = row['zahlen']
        year = date.year

        # Initialisiere Jahr
        if year not in results['by_year']:
            results['by_year'][year] = {
                'days': 0, 'cost': 0, 'jackpots': 0, 'wins': 0,
                'hits': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            }

        # Berechne HZ6 W20 fuer diesen Tag
        hz6 = get_hz6_w20(df, date)
        if hz6 is None:
            continue

        results['total_cost'] += 1
        results['by_year'][year]['days'] += 1
        results['by_year'][year]['cost'] += 1

        # Zaehle Treffer
        hits = count_hits(hz6, drawn)
        results['hit_distribution'][hits] += 1
        results['by_year'][year]['hits'][hits] += 1

        # Jackpot?
        if hits == 6:
            results['jackpots'].append({
                'date': date.strftime('%Y-%m-%d'),
                'hz6': hz6,
                'drawn': sorted(list(drawn))
            })
            results['total_wins'] += 500
            results['by_year'][year]['jackpots'] += 1
            results['by_year'][year]['wins'] += 500

    return results


def print_results(results):
    print("=" * 70)
    print("BACKTEST: PURE HZ6 W20 (Keine Regeln)")
    print("=" * 70)
    print()

    # Jahresweise
    print("JAHRESWEISE ERGEBNISSE")
    print("-" * 70)
    print(f"{'Jahr':<8} {'Tage':<8} {'Kosten':<10} {'Jackpots':<10} {'Gewinn':<10} {'ROI':<10}")
    print("-" * 70)

    for year in sorted(results['by_year'].keys()):
        data = results['by_year'][year]
        profit = data['wins'] - data['cost']
        roi = (profit / data['cost'] * 100) if data['cost'] > 0 else 0
        print(f"{year:<8} {data['days']:<8} {data['cost']:<10} {data['jackpots']:<10} {data['wins']:<10} {roi:>8.1f}%")

    print("-" * 70)
    total_profit = results['total_wins'] - results['total_cost']
    total_roi = (total_profit / results['total_cost'] * 100) if results['total_cost'] > 0 else 0
    print(f"{'GESAMT':<8} {results['total_cost']:<8} {results['total_cost']:<10} {len(results['jackpots']):<10} {results['total_wins']:<10} {total_roi:>8.1f}%")
    print()

    # Treffer-Verteilung
    print("TREFFER-VERTEILUNG (alle Jahre)")
    print("-" * 70)
    total_days = sum(results['hit_distribution'].values())
    for hits in range(7):
        count = results['hit_distribution'][hits]
        pct = (count / total_days * 100) if total_days > 0 else 0
        bar = '#' * int(pct)
        print(f"  {hits} Treffer: {count:>5} ({pct:>5.1f}%) {bar}")
    print()

    # Jackpot-Details
    if results['jackpots']:
        print("JACKPOT-DETAILS")
        print("-" * 70)
        for jp in results['jackpots']:
            print(f"  {jp['date']}: HZ6 {jp['hz6']}")
        print()
    else:
        print("KEINE JACKPOTS!")
        print()

    # Zusammenfassung
    print("=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"  Zeitraum:        2022-2025")
    print(f"  Spieltage:       {results['total_cost']}")
    print(f"  Kosten:          {results['total_cost']} EUR")
    print(f"  Jackpots:        {len(results['jackpots'])}")
    print(f"  Gewinn:          {results['total_wins']} EUR")
    print(f"  Bilanz:          {total_profit} EUR")
    print(f"  ROI:             {total_roi:.1f}%")
    print()

    if len(results['jackpots']) > 0:
        days_per_jp = results['total_cost'] / len(results['jackpots'])
        print(f"  Tage pro Jackpot: {days_per_jp:.0f}")
        print(f"  Kosten pro Jackpot: {results['total_cost'] / len(results['jackpots']):.0f} EUR")
    print()


if __name__ == "__main__":
    print("Lade Daten...")
    df = load_data()
    print(f"Geladene Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['datum'].min().strftime('%Y-%m-%d')} bis {df['datum'].max().strftime('%Y-%m-%d')}")
    print()

    print("Starte Backtest...")
    results = backtest_pure_hz6_w20(df)
    print_results(results)
