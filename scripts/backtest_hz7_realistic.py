#!/usr/bin/env python3
"""
KORRIGIERTER Backtest: HZ7 W20 - REALISTISCHE Methodik

WICHTIG: Die "69 Jackpots" aus VALIDIERTE_FAKTEN sind FALSCH!
Die Original-Analyse zaehlt fuer jede HZ7 alle zukuenftigen Jackpots bis 2025.
Das ist KEINE realistische Strategie.

Dieser Test macht es RICHTIG:
- HZ7 wird am Monatsanfang berechnet
- HZ7 wird NUR diesen Monat gespielt
- Naechsten Monat: Neue HZ7 berechnen

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
    for combo in combinations(hz7, 6):
        if set(combo).issubset(drawn):
            jackpots += 1
    return jackpots


def backtest_realistic(df):
    """
    REALISTISCHER Backtest:
    - Jeden Monat neue HZ7 berechnen
    - NUR in diesem Monat spielen
    - Kosten: 7 EUR/Tag (7 Kombinationen)
    """

    results = {
        'by_month': [],
        'by_year': {},
        'jackpots': [],
        'total_cost': 0,
        'total_wins': 0,
        'total_jp_count': 0,
        'total_days': 0
    }

    # Alle Monate durchgehen
    for year in range(2022, 2026):
        if year not in results['by_year']:
            results['by_year'][year] = {
                'months': 0, 'days': 0, 'cost': 0,
                'jp_count': 0, 'wins': 0
            }

        for month in range(1, 13):
            # Berechne HZ7 am Monatsanfang
            month_start = pd.Timestamp(f'{year}-{month:02d}-01')

            # Pruefe ob Monat in Daten existiert
            month_end = month_start + pd.offsets.MonthEnd(0)
            month_draws = df[(df['datum'] >= month_start) & (df['datum'] <= month_end)]

            if len(month_draws) == 0:
                continue

            hz7 = get_hz7_w20(df, month_start)
            if hz7 is None:
                continue

            results['by_year'][year]['months'] += 1

            month_data = {
                'month': f'{year}-{month:02d}',
                'hz7': hz7,
                'days': 0,
                'cost': 0,
                'jp_count': 0,
                'wins': 0,
                'jp_dates': []
            }

            # Spiele HZ7 jeden Tag dieses Monats
            for _, row in month_draws.iterrows():
                date = row['datum']
                drawn = row['zahlen']

                # Kosten: 7 EUR/Tag (7 Kombinationen)
                month_data['days'] += 1
                month_data['cost'] += 7
                results['total_cost'] += 7
                results['total_days'] += 1
                results['by_year'][year]['days'] += 1
                results['by_year'][year]['cost'] += 7

                # Pruefe Jackpots
                jp_count = check_hz7_jackpots(hz7, drawn)

                if jp_count > 0:
                    month_data['jp_count'] += jp_count
                    month_data['wins'] += jp_count * 500
                    month_data['jp_dates'].append(date.strftime('%Y-%m-%d'))

                    results['total_jp_count'] += jp_count
                    results['total_wins'] += jp_count * 500
                    results['by_year'][year]['jp_count'] += jp_count
                    results['by_year'][year]['wins'] += jp_count * 500

                    results['jackpots'].append({
                        'date': date.strftime('%Y-%m-%d'),
                        'hz7': hz7,
                        'jp_count': jp_count
                    })

            results['by_month'].append(month_data)

    return results


def print_results(results):
    print("=" * 80)
    print("KORRIGIERTER BACKTEST: HZ7 W20 - REALISTISCHE METHODIK")
    print("=" * 80)
    print()
    print("WICHTIG: Jede HZ7 wird NUR in ihrem Monat gespielt!")
    print("         (Nicht Jahre in die Zukunft wie im Original)")
    print()

    # Jahresweise
    print("JAHRESWEISE ERGEBNISSE")
    print("-" * 80)
    print(f"{'Jahr':<8} {'Monate':<8} {'Tage':<8} {'Kosten':<10} {'Jackpots':<10} {'Gewinn':<10} {'ROI':<10}")
    print("-" * 80)

    for year in sorted(results['by_year'].keys()):
        data = results['by_year'][year]
        if data['cost'] == 0:
            continue
        profit = data['wins'] - data['cost']
        roi = (profit / data['cost'] * 100) if data['cost'] > 0 else 0
        print(f"{year:<8} {data['months']:<8} {data['days']:<8} {data['cost']:<10} {data['jp_count']:<10} {data['wins']:<10} {roi:>8.1f}%")

    print("-" * 80)
    total_profit = results['total_wins'] - results['total_cost']
    total_roi = (total_profit / results['total_cost'] * 100) if results['total_cost'] > 0 else 0
    total_months = sum(d['months'] for d in results['by_year'].values())
    print(f"{'GESAMT':<8} {total_months:<8} {results['total_days']:<8} {results['total_cost']:<10} {results['total_jp_count']:<10} {results['total_wins']:<10} {total_roi:>8.1f}%")
    print()

    # Monate mit Jackpots
    months_with_jp = [m for m in results['by_month'] if m['jp_count'] > 0]
    print(f"MONATE MIT JACKPOTS: {len(months_with_jp)} von {len(results['by_month'])}")
    print("-" * 80)

    if months_with_jp:
        print(f"{'Monat':<10} {'HZ7':<35} {'JPs':<6} {'Gewinn':<10}")
        print("-" * 80)
        for m in months_with_jp:
            print(f"{m['month']:<10} {str(m['hz7']):<35} {m['jp_count']:<6} {m['wins']:<10}")
    else:
        print("KEINE Monate mit Jackpots!")
    print()

    # Jackpot-Details
    if results['jackpots']:
        print("JACKPOT-TAGE")
        print("-" * 80)
        for jp in results['jackpots']:
            print(f"  {jp['date']}: {jp['jp_count']}x JP mit HZ7 {jp['hz7']}")
    print()

    # Vergleich
    print("=" * 80)
    print("VERGLEICH MIT DOKUMENTATION")
    print("=" * 80)
    print()
    print("VALIDIERTE_FAKTEN.md behauptet:")
    print("  - 69 Jackpots in 32 Monaten (2022-2024)")
    print("  - ROI: +413%")
    print()
    print("REALISTISCHER TEST zeigt:")
    print(f"  - {results['total_jp_count']} Jackpots in {total_months} Monaten (2022-2025)")
    print(f"  - ROI: {total_roi:.1f}%")
    print()
    print("ERKLAERUNG DER DISKREPANZ:")
    print("  Die '69 Jackpots' sind KUMULATIV:")
    print("  Jede HZ7 wurde bis 2025 getestet, nicht nur ihren Monat.")
    print("  Oktober 2022 HZ7 mit '10 JP' = diese Zahlen 3 JAHRE spielen!")
    print("  Das ist KEINE realistische Strategie.")
    print()

    # Fazit
    print("=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"  Spieltage:        {results['total_days']}")
    print(f"  Kosten:           {results['total_cost']} EUR")
    print(f"  Jackpots:         {results['total_jp_count']}")
    print(f"  Gewinn:           {results['total_wins']} EUR")
    print(f"  Bilanz:           {total_profit} EUR")
    print(f"  ROI:              {total_roi:.1f}%")
    print()

    if results['total_jp_count'] > 0:
        days_per_jp = results['total_days'] / results['total_jp_count']
        cost_per_jp = results['total_cost'] / results['total_jp_count']
        print(f"  Tage pro Jackpot:   {days_per_jp:.0f}")
        print(f"  Kosten pro Jackpot: {cost_per_jp:.0f} EUR")
        print(f"  Break-Even:         {500} EUR Gewinn vs {cost_per_jp:.0f} EUR Kosten")
    print()


if __name__ == "__main__":
    print("Lade Daten...")
    df = load_data()
    print(f"Geladene Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['datum'].min().strftime('%Y-%m-%d')} bis {df['datum'].max().strftime('%Y-%m-%d')}")
    print()

    print("Starte REALISTISCHEN Backtest...")
    results = backtest_realistic(df)
    print_results(results)
