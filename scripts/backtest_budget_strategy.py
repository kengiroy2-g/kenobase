#!/usr/bin/env python3
"""
Backtest: HZ6 W20 + Loop Mini Strategie (32 EUR/Monat)

Strategie:
- HZ6 W20: Tag 1-14, 1 EUR/Tag (Top-6 aus letzten 20 Ziehungen)
- Loop-Erweitert [2,3,9,10,20,24]: Tag 1, 7, 14, 6 EUR/Tag
- Cooldown: 30 Tage nach 10/10 Jackpot nicht spielen

Testzeitraum: 2024-2025
"""

import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta
from itertools import combinations

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

# Loop-Erweitert Zahlen (statisch)
LOOP_ERWEITERT = [2, 3, 9, 10, 20, 24]

# Bekannte 10/10 Jackpot-Termine (fuer Cooldown)
JACKPOT_DATES = [
    "2022-03-15", "2022-07-22", "2022-11-08",
    "2023-02-14", "2023-06-01", "2023-09-19", "2023-12-28",
    "2024-04-10", "2024-08-15", "2024-12-06",
]

def load_data():
    """Lade KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
    df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['zahlen'] = df[zahl_cols].apply(lambda row: set(int(x) for x in row if pd.notna(x)), axis=1)
    df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)
    return df


def get_hz6_w20(df, end_date):
    """Berechne Top-6 aus letzten 20 Ziehungen vor end_date."""
    hist = df[df['datum'] < end_date].tail(20)
    if len(hist) < 20:
        return None
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    top6 = [n for n, _ in freq.most_common(6)]
    return sorted(top6)


def is_in_cooldown(date, jackpot_dates, cooldown_days=30):
    """Pruefe ob Datum in Cooldown-Phase ist."""
    for jp_date in jackpot_dates:
        jp = pd.Timestamp(jp_date)
        if jp < date <= jp + timedelta(days=cooldown_days):
            return True
    return False


def check_jackpot(ticket, drawn):
    """Pruefe ob 6/6 Jackpot (alle 6 Zahlen gezogen)."""
    return len(set(ticket) & drawn) == 6


def backtest_strategy(df, start_year=2024, end_year=2025):
    """Fuehre Backtest durch."""

    # Parse jackpot dates
    jp_dates = [pd.Timestamp(d) for d in JACKPOT_DATES]

    results = {
        'months': [],
        'hz6_jackpots': 0,
        'loop_jackpots': 0,
        'hz6_costs': 0,
        'loop_costs': 0,
        'hz6_wins': 0,
        'loop_wins': 0,
        'skipped_cooldown': 0,
        'skipped_late_phase': 0,
        'played_days': 0,
        'details': []
    }

    # Fuer jeden Monat
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            # Skip future months
            if year == 2025 and month > 12:
                continue
            if year == 2026:
                continue

            month_start = pd.Timestamp(f'{year}-{month:02d}-01')

            # Berechne HZ6 W20 am Monatsanfang
            hz6 = get_hz6_w20(df, month_start)
            if hz6 is None:
                continue

            month_data = {
                'month': f'{year}-{month:02d}',
                'hz6': hz6,
                'hz6_jp': 0,
                'loop_jp': 0,
                'hz6_cost': 0,
                'loop_cost': 0,
                'cooldown_days': 0,
                'played_days': 0
            }

            # Hole Ziehungen des Monats
            month_draws = df[(df['datum'].dt.year == year) & (df['datum'].dt.month == month)]

            for _, row in month_draws.iterrows():
                date = row['datum']
                day = date.day
                drawn = row['zahlen']

                # Nur Tag 1-14 (FRUEH-Phase)
                if day > 14:
                    results['skipped_late_phase'] += 1
                    continue

                # Cooldown-Check
                if is_in_cooldown(date, JACKPOT_DATES):
                    results['skipped_cooldown'] += 1
                    month_data['cooldown_days'] += 1
                    continue

                month_data['played_days'] += 1
                results['played_days'] += 1

                # HZ6 W20 spielen (jeden Tag 1-14)
                month_data['hz6_cost'] += 1
                results['hz6_costs'] += 1

                if check_jackpot(hz6, drawn):
                    month_data['hz6_jp'] += 1
                    results['hz6_jackpots'] += 1
                    results['hz6_wins'] += 500
                    results['details'].append({
                        'date': date.strftime('%Y-%m-%d'),
                        'type': 'HZ6',
                        'numbers': hz6,
                        'drawn': list(drawn),
                        'win': 500
                    })

                # Loop-Erweitert spielen (nur Tag 1, 7, 14)
                if day in [1, 7, 14]:
                    month_data['loop_cost'] += 6
                    results['loop_costs'] += 6

                    if check_jackpot(LOOP_ERWEITERT, drawn):
                        month_data['loop_jp'] += 1
                        results['loop_jackpots'] += 1
                        results['loop_wins'] += 500
                        results['details'].append({
                            'date': date.strftime('%Y-%m-%d'),
                            'type': 'LOOP',
                            'numbers': LOOP_ERWEITERT,
                            'drawn': list(drawn),
                            'win': 500
                        })

            results['months'].append(month_data)

    return results


def print_results(results):
    """Drucke Ergebnisse."""

    print("=" * 70)
    print("BACKTEST: HZ6 W20 + Loop Mini Strategie (32 EUR/Monat Budget)")
    print("=" * 70)
    print()

    # Gesamtuebersicht
    total_costs = results['hz6_costs'] + results['loop_costs']
    total_wins = results['hz6_wins'] + results['loop_wins']
    total_jackpots = results['hz6_jackpots'] + results['loop_jackpots']
    roi = ((total_wins - total_costs) / total_costs * 100) if total_costs > 0 else 0

    print("GESAMTERGEBNIS (2024-2025)")
    print("-" * 70)
    print(f"  Gespielte Tage:       {results['played_days']}")
    print(f"  Uebersprungen (Cooldown): {results['skipped_cooldown']}")
    print(f"  Uebersprungen (SPAET):    {results['skipped_late_phase']}")
    print()
    print(f"  KOSTEN:")
    print(f"    HZ6 W20:            {results['hz6_costs']} EUR")
    print(f"    Loop-Erweitert:     {results['loop_costs']} EUR")
    print(f"    GESAMT:             {total_costs} EUR")
    print()
    print(f"  GEWINNE:")
    print(f"    HZ6 Jackpots:       {results['hz6_jackpots']} x 500 EUR = {results['hz6_wins']} EUR")
    print(f"    Loop Jackpots:      {results['loop_jackpots']} x 500 EUR = {results['loop_wins']} EUR")
    print(f"    GESAMT:             {total_jackpots} Jackpots = {total_wins} EUR")
    print()
    print(f"  BILANZ:")
    print(f"    Gewinn - Kosten:    {total_wins - total_costs} EUR")
    print(f"    ROI:                {roi:.1f}%")
    print()

    # Monatliche Details
    print("MONATLICHE UEBERSICHT")
    print("-" * 70)
    print(f"{'Monat':<10} {'HZ6 Zahlen':<30} {'HZ6 JP':<8} {'Loop JP':<8} {'Kosten':<8}")
    print("-" * 70)

    for m in results['months']:
        hz6_str = str(m['hz6']) if m['hz6'] else '-'
        cost = m['hz6_cost'] + m['loop_cost']
        print(f"{m['month']:<10} {hz6_str:<30} {m['hz6_jp']:<8} {m['loop_jp']:<8} {cost:<8}")

    print("-" * 70)
    print()

    # Jackpot-Details
    if results['details']:
        print("JACKPOT-DETAILS")
        print("-" * 70)
        for d in results['details']:
            print(f"  {d['date']}: {d['type']} - {d['numbers']}")
            print(f"           Gezogen: {sorted(d['drawn'])[:10]}...")
            print(f"           Gewinn: {d['win']} EUR")
            print()
    else:
        print("KEINE JACKPOTS in diesem Zeitraum.")
        print()

    # Fazit
    print("=" * 70)
    print("FAZIT")
    print("=" * 70)
    if total_wins > total_costs:
        print(f"  GEWINN: +{total_wins - total_costs} EUR ({roi:.1f}% ROI)")
    else:
        print(f"  VERLUST: {total_wins - total_costs} EUR ({roi:.1f}% ROI)")
    print()

    months_count = len(results['months'])
    avg_monthly_cost = total_costs / months_count if months_count > 0 else 0
    print(f"  Durchschnittliche Kosten/Monat: {avg_monthly_cost:.1f} EUR")
    print(f"  (Budget war 32 EUR/Monat)")
    print()

    return {
        'total_costs': total_costs,
        'total_wins': total_wins,
        'total_jackpots': total_jackpots,
        'roi': roi,
        'played_days': results['played_days']
    }


if __name__ == "__main__":
    print("Lade Daten...")
    df = load_data()
    print(f"Geladene Ziehungen: {len(df)}")
    print()

    print("Starte Backtest 2024-2025...")
    results = backtest_strategy(df, start_year=2024, end_year=2025)

    summary = print_results(results)
