#!/usr/bin/env python3
"""
Vergleichs-Backtest: Verschiedene Strategien

Testet:
1. HZ6 W20 mit FRUEH + Cooldown (Original Budget-Strategie)
2. HZ7 W20 mit FRUEH + Cooldown (7 Kombinationen)
3. HZ6 W20 OHNE Einschraenkungen (alle Tage)
4. HZ7 W20 OHNE Einschraenkungen (alle Tage)

Zeitraum: 2024-2025
"""

import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import timedelta
from itertools import combinations

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

LOOP_ERWEITERT = [2, 3, 9, 10, 20, 24]

JACKPOT_DATES = [
    "2022-03-15", "2022-07-22", "2022-11-08",
    "2023-02-14", "2023-06-01", "2023-09-19", "2023-12-28",
    "2024-04-10", "2024-08-15", "2024-12-06",
]


def load_data():
    df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
    df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['zahlen'] = df[zahl_cols].apply(lambda row: set(int(x) for x in row if pd.notna(x)), axis=1)
    df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)
    return df


def get_hz_w20(df, end_date, top_n=6):
    """Berechne Top-N aus letzten 20 Ziehungen."""
    hist = df[df['datum'] < end_date].tail(20)
    if len(hist) < 20:
        return None
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return sorted([n for n, _ in freq.most_common(top_n)])


def is_in_cooldown(date, cooldown_days=30):
    for jp_date in JACKPOT_DATES:
        jp = pd.Timestamp(jp_date)
        if jp < date <= jp + timedelta(days=cooldown_days):
            return True
    return False


def check_hz6_jackpot(hz6, drawn):
    """Pruefe ob 6/6 (alle 6 Zahlen gezogen)."""
    return len(set(hz6) & drawn) == 6


def check_hz7_jackpots(hz7, drawn):
    """Pruefe wie viele der 7 Kombinationen 6/6 haben."""
    jackpots = 0
    for combo in combinations(hz7, 6):
        if len(set(combo) & drawn) == 6:
            jackpots += 1
    return jackpots


def backtest_all_strategies(df, start_year=2024, end_year=2025):
    """Teste alle Strategien."""

    strategies = {
        'hz6_frueh_cooldown': {'jp': 0, 'cost': 0, 'days': 0},
        'hz7_frueh_cooldown': {'jp': 0, 'cost': 0, 'days': 0},
        'hz6_all_days': {'jp': 0, 'cost': 0, 'days': 0},
        'hz7_all_days': {'jp': 0, 'cost': 0, 'days': 0},
        'loop_frueh_cooldown': {'jp': 0, 'cost': 0, 'days': 0},
        'loop_all_days': {'jp': 0, 'cost': 0, 'days': 0},
    }

    jackpot_details = []

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == 2025 and month > 12:
                continue

            month_start = pd.Timestamp(f'{year}-{month:02d}-01')
            hz6 = get_hz_w20(df, month_start, top_n=6)
            hz7 = get_hz_w20(df, month_start, top_n=7)

            if hz6 is None or hz7 is None:
                continue

            month_draws = df[(df['datum'].dt.year == year) & (df['datum'].dt.month == month)]

            for _, row in month_draws.iterrows():
                date = row['datum']
                day = date.day
                drawn = row['zahlen']

                in_cooldown = is_in_cooldown(date)
                in_frueh = day <= 14

                # HZ6 mit FRUEH + Cooldown
                if in_frueh and not in_cooldown:
                    strategies['hz6_frueh_cooldown']['cost'] += 1
                    strategies['hz6_frueh_cooldown']['days'] += 1
                    if check_hz6_jackpot(hz6, drawn):
                        strategies['hz6_frueh_cooldown']['jp'] += 1
                        jackpot_details.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'strategy': 'HZ6 FRUEH+CD',
                            'numbers': hz6
                        })

                # HZ7 mit FRUEH + Cooldown (7 Kombinationen = 7 EUR)
                if in_frueh and not in_cooldown:
                    strategies['hz7_frueh_cooldown']['cost'] += 7
                    strategies['hz7_frueh_cooldown']['days'] += 1
                    jp_count = check_hz7_jackpots(hz7, drawn)
                    if jp_count > 0:
                        strategies['hz7_frueh_cooldown']['jp'] += jp_count
                        jackpot_details.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'strategy': 'HZ7 FRUEH+CD',
                            'numbers': hz7,
                            'count': jp_count
                        })

                # HZ6 OHNE Einschraenkungen
                strategies['hz6_all_days']['cost'] += 1
                strategies['hz6_all_days']['days'] += 1
                if check_hz6_jackpot(hz6, drawn):
                    strategies['hz6_all_days']['jp'] += 1
                    jackpot_details.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'strategy': 'HZ6 ALLE',
                        'numbers': hz6
                    })

                # HZ7 OHNE Einschraenkungen
                strategies['hz7_all_days']['cost'] += 7
                strategies['hz7_all_days']['days'] += 1
                jp_count = check_hz7_jackpots(hz7, drawn)
                if jp_count > 0:
                    strategies['hz7_all_days']['jp'] += jp_count
                    jackpot_details.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'strategy': 'HZ7 ALLE',
                        'numbers': hz7,
                        'count': jp_count
                    })

                # Loop mit FRUEH + Cooldown
                if in_frueh and not in_cooldown:
                    strategies['loop_frueh_cooldown']['cost'] += 6
                    strategies['loop_frueh_cooldown']['days'] += 1
                    if check_hz6_jackpot(LOOP_ERWEITERT, drawn):
                        strategies['loop_frueh_cooldown']['jp'] += 1
                        jackpot_details.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'strategy': 'LOOP FRUEH+CD',
                            'numbers': LOOP_ERWEITERT
                        })

                # Loop OHNE Einschraenkungen
                strategies['loop_all_days']['cost'] += 6
                strategies['loop_all_days']['days'] += 1
                if check_hz6_jackpot(LOOP_ERWEITERT, drawn):
                    strategies['loop_all_days']['jp'] += 1
                    jackpot_details.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'strategy': 'LOOP ALLE',
                        'numbers': LOOP_ERWEITERT
                    })

    return strategies, jackpot_details


def print_comparison(strategies, details):
    print("=" * 80)
    print("STRATEGIE-VERGLEICH: 2024-2025")
    print("=" * 80)
    print()
    print(f"{'Strategie':<25} {'Tage':<8} {'Kosten':<10} {'Jackpots':<10} {'Gewinn':<10} {'ROI':<10}")
    print("-" * 80)

    for name, data in strategies.items():
        wins = data['jp'] * 500
        profit = wins - data['cost']
        roi = ((wins - data['cost']) / data['cost'] * 100) if data['cost'] > 0 else 0
        print(f"{name:<25} {data['days']:<8} {data['cost']:<10} {data['jp']:<10} {wins:<10} {roi:>8.1f}%")

    print("-" * 80)
    print()

    # Details zu Jackpots
    if details:
        print("JACKPOT-DETAILS:")
        print("-" * 80)
        seen = set()
        for d in details:
            key = (d['date'], d['strategy'])
            if key not in seen:
                seen.add(key)
                count = d.get('count', 1)
                print(f"  {d['date']}: {d['strategy']:<15} {d['numbers']} (x{count})")
    else:
        print("KEINE JACKPOTS gefunden!")

    print()


if __name__ == "__main__":
    print("Lade Daten...")
    df = load_data()
    print(f"Geladene Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['datum'].min().strftime('%Y-%m-%d')} bis {df['datum'].max().strftime('%Y-%m-%d')}")
    print()

    print("Starte Vergleichs-Backtest...")
    strategies, details = backtest_all_strategies(df, 2024, 2025)
    print_comparison(strategies, details)

    # Zusaetzlich: Was waere mit W50 statt W20?
    print()
    print("=" * 80)
    print("HINWEIS: Dieser Test verwendet W20 (letzte 20 Ziehungen)")
    print("Der hot_zone_fenster_vergleich zeigt dass W20 69 JP in 32 Monaten hatte.")
    print("Aber das war mit HZ7 (7 Kombinationen), nicht HZ6 (1 Kombination).")
    print("=" * 80)
