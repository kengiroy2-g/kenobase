#!/usr/bin/env python
"""Liste alle KENO 10/10 Jackpots mit Gewinnern."""

import pandas as pd
from pathlib import Path

def main():
    base = Path(__file__).parent.parent

    # 2023 hat anderes Datumsformat - ueberspringe vorerst
    files = [
        base / 'Keno_GPTs/Keno_GQ_2024.csv',
        base / 'Keno_GPTs/Keno_GQ_02-2024.csv',
        base / 'Keno_GPTs/Keno_GQ_2025.csv',
    ]

    all_data = []
    for f in files:
        if f.exists():
            df = pd.read_csv(f, encoding='utf-8')
            all_data.append(df)

    combined = pd.concat(all_data, ignore_index=True)
    combined['DatumParsed'] = pd.to_datetime(combined['Datum'], format='%d.%m.%Y')

    mask = (combined['Keno-Typ'] == 10) & (combined['Anzahl richtiger Zahlen'] == 10) & (combined['Anzahl der Gewinner'] > 0)
    jackpots = combined[mask].drop_duplicates(subset=['Datum'])[['Datum', 'Anzahl der Gewinner', 'DatumParsed']]
    jackpots = jackpots.sort_values('DatumParsed')

    print('VOLLSTAENDIGE JACKPOT-LISTE (10/10 MIT GEWINNERN)')
    print('=' * 60)

    current_year = None
    for _, row in jackpots.iterrows():
        year = row['DatumParsed'].year
        if year != current_year:
            print()
            print(f'=== {year} ===')
            current_year = year

        weekday = row['DatumParsed'].strftime('%a')
        winners = int(row['Anzahl der Gewinner'])
        print(f"  {row['Datum']} ({weekday}) | {winners} Gewinner")

    print()
    print(f'Gesamt: {len(jackpots)} Jackpot-Tage')
    print()
    print('HINWEIS: Maerz-Dezember 2024 fehlen in unseren GQ-Daten!')


if __name__ == "__main__":
    main()
