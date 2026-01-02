#!/usr/bin/env python3
"""
Backtest: HZ7 W20 mit MONATLICHER Berechnung

Original-Methodik aus hot_zone_fenster_vergleich:
- HZ7 wird am MONATSANFANG berechnet (Top-7 aus letzten 20 Ziehungen)
- Diese 7 Zahlen werden den ganzen Monat gespielt
- 7 Kombinationen (C(7,6) = 7), 7 EUR/Tag

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
    """Top-7 aus letzten 20 Ziehungen VOR end_date."""
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
        if set(combo).issubset(drawn):  # Alle 6 Zahlen muessen in den 20 gezogenen sein
            jackpots += 1
            winning_combos.append(list(combo))
    return jackpots, winning_combos


def count_hits(hz7, drawn):
    """Zaehle wie viele der 7 HZ-Zahlen in den 20 gezogenen sind."""
    return len(set(hz7) & drawn)


def backtest_monthly_hz7_w20(df):
    """Backtest mit monatlicher HZ7-Berechnung."""

    results = {
        'by_month': [],
        'by_year': {},
        'jackpots': [],
        'total_cost': 0,
        'total_wins': 0,
        'total_jp_count': 0,
        'hit_distribution': {i: 0 for i in range(8)}  # 0-7 Treffer
    }

    # Jahre und Monate durchgehen
    years = df['datum'].dt.year.unique()

    for year in sorted(years):
        if year < 2022:
            continue

        if year not in results['by_year']:
            results['by_year'][year] = {
                'days': 0, 'cost': 0, 'jackpots': 0, 'wins': 0, 'jp_events': 0
            }

        for month in range(1, 13):
            # Berechne HZ7 am Monatsanfang
            month_start = pd.Timestamp(f'{year}-{month:02d}-01')
            hz7 = get_hz7_w20(df, month_start)

            if hz7 is None:
                continue

            # Hole alle Ziehungen dieses Monats
            month_draws = df[(df['datum'].dt.year == year) & (df['datum'].dt.month == month)]

            month_data = {
                'month': f'{year}-{month:02d}',
                'hz7': hz7,
                'days': 0,
                'cost': 0,
                'jackpots': 0,
                'wins': 0,
                'jp_dates': []
            }

            for _, row in month_draws.iterrows():
                date = row['datum']
                drawn = row['zahlen']

                month_data['days'] += 1
                month_data['cost'] += 7
                results['total_cost'] += 7
                results['by_year'][year]['days'] += 1
                results['by_year'][year]['cost'] += 7

                # Zaehle Treffer (wie viele der 7 HZ-Zahlen in den 20 gezogenen)
                hits = count_hits(hz7, drawn)
                results['hit_distribution'][hits] += 1

                # Pruefe Jackpots (6/6 in einer der 7 Kombinationen)
                jp_count, winning = check_hz7_jackpots(hz7, drawn)

                if jp_count > 0:
                    month_data['jackpots'] += jp_count
                    month_data['wins'] += jp_count * 500
                    month_data['jp_dates'].append(date.strftime('%Y-%m-%d'))

                    results['total_jp_count'] += jp_count
                    results['total_wins'] += jp_count * 500
                    results['by_year'][year]['jackpots'] += jp_count
                    results['by_year'][year]['wins'] += jp_count * 500
                    results['by_year'][year]['jp_events'] += 1

                    results['jackpots'].append({
                        'date': date.strftime('%Y-%m-%d'),
                        'hz7': hz7,
                        'jp_count': jp_count,
                        'winning': winning,
                        'hits': hits
                    })

            results['by_month'].append(month_data)

    return results


def print_results(results):
    print("=" * 80)
    print("BACKTEST: HZ7 W20 - MONATLICHE BERECHNUNG (Original-Methodik)")
    print("=" * 80)
    print()

    # Jahresweise
    print("JAHRESWEISE ERGEBNISSE")
    print("-" * 80)
    print(f"{'Jahr':<8} {'Tage':<8} {'Kosten':<10} {'JP-Events':<12} {'JP-Anzahl':<10} {'Gewinn':<10} {'ROI':<10}")
    print("-" * 80)

    for year in sorted(results['by_year'].keys()):
        data = results['by_year'][year]
        profit = data['wins'] - data['cost']
        roi = (profit / data['cost'] * 100) if data['cost'] > 0 else 0
        print(f"{year:<8} {data['days']:<8} {data['cost']:<10} {data['jp_events']:<12} {data['jackpots']:<10} {data['wins']:<10} {roi:>8.1f}%")

    print("-" * 80)
    total_profit = results['total_wins'] - results['total_cost']
    total_roi = (total_profit / results['total_cost'] * 100) if results['total_cost'] > 0 else 0
    total_events = sum(d['jp_events'] for d in results['by_year'].values())
    print(f"{'GESAMT':<8} {'':<8} {results['total_cost']:<10} {total_events:<12} {results['total_jp_count']:<10} {results['total_wins']:<10} {total_roi:>8.1f}%")
    print()

    # Monatliche Uebersicht (nur Monate mit Jackpots)
    print("MONATE MIT JACKPOTS")
    print("-" * 80)
    print(f"{'Monat':<10} {'HZ7':<35} {'JPs':<6} {'Gewinn':<10}")
    print("-" * 80)

    months_with_jp = [m for m in results['by_month'] if m['jackpots'] > 0]
    for m in months_with_jp:
        print(f"{m['month']:<10} {str(m['hz7']):<35} {m['jackpots']:<6} {m['wins']:<10}")

    print("-" * 80)
    print(f"Monate mit Jackpot: {len(months_with_jp)} von {len(results['by_month'])} ({len(months_with_jp)/len(results['by_month'])*100:.0f}%)")
    print()

    # Treffer-Verteilung
    print("TREFFER-VERTEILUNG (wie viele der 7 HZ-Zahlen in den 20 gezogenen)")
    print("-" * 80)
    total_days = sum(results['hit_distribution'].values())
    for hits in range(8):
        count = results['hit_distribution'][hits]
        pct = (count / total_days * 100) if total_days > 0 else 0
        bar = '#' * int(pct)
        marker = " ← 6+ = JACKPOT" if hits >= 6 else ""
        print(f"  {hits} Treffer: {count:>5} ({pct:>5.1f}%) {bar}{marker}")
    print()

    # Jackpot-Details
    if results['jackpots']:
        print("JACKPOT-DETAILS")
        print("-" * 80)
        for jp in results['jackpots']:
            print(f"  {jp['date']}: {jp['jp_count']}x JP mit HZ7 {jp['hz7']}")
            print(f"             ({jp['hits']} von 7 Zahlen gezogen)")
    print()

    # Zusammenfassung
    print("=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"  Spieltage:          {results['total_cost'] // 7}")
    print(f"  Kosten:             {results['total_cost']} EUR")
    print(f"  Jackpot-Tage:       {len(results['jackpots'])}")
    print(f"  Jackpot-Anzahl:     {results['total_jp_count']}")
    print(f"  Gewinn:             {results['total_wins']} EUR")
    print(f"  Bilanz:             {total_profit} EUR")
    print(f"  ROI:                {total_roi:.1f}%")
    print()

    # Vergleich mit Dokumentation
    print("VERGLEICH MIT VALIDIERTE_FAKTEN.md")
    print("-" * 80)
    print(f"  Dokumentiert (2022-2024): 69 Jackpots")
    print(f"  Dieser Test (2022-2025): {results['total_jp_count']} Jackpots")
    print()


if __name__ == "__main__":
    print("Lade Daten...")
    df = load_data()
    print(f"Geladene Ziehungen: {len(df)}")
    print()

    results = backtest_monthly_hz7_w20(df)
    print_results(results)
