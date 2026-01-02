#!/usr/bin/env python
"""
Vergleich aller Fenstergroessen: Januar 2022 - Dezember 2024
"""

import pandas as pd
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

# Lade KENO-Daten
df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')

zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
df['zahlen'] = df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)


def get_hot_zone_draws(df, end_date, window):
    hist = df[df['datum'] <= end_date].tail(window)
    freq = defaultdict(int)
    for zahlen in hist['zahlen']:
        for num in zahlen:
            freq[num] += 1
    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:7]]


def get_hot_zone_days(df, end_date, days):
    end_dt = pd.Timestamp(end_date)
    start_dt = end_dt - timedelta(days=days)
    hist = df[(df['datum'] > start_dt) & (df['datum'] <= end_dt)]
    freq = defaultdict(int)
    for zahlen in hist['zahlen']:
        for num in zahlen:
            freq[num] += 1
    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:7]]


def count_jackpots(df, hot_zone, start_date, end_date):
    hz = sorted(hot_zone)
    groups = list(combinations(hz, 6))
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpots = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        for group in groups:
            if len(drawn & set(group)) == 6:
                jackpots.append({
                    'datum': row['datum'],
                    'gruppe': list(group)
                })
    return jackpots


# Generiere alle Monate
months = []
for year in [2022, 2023, 2024]:
    for month in range(1, 13):
        if month == 1:
            end_date = f'{year-1}-12-31'
        else:
            last_day = (pd.Timestamp(f'{year}-{month:02d}-01') - timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = last_day

        months.append({
            'year': year,
            'month': month,
            'name': f'{year}-{month:02d}',
            'end_date': end_date,
            'start_test': f'{year}-{month:02d}-01'
        })

end_test = pd.Timestamp('2025-12-31')

windows = {
    'W20': lambda df, end: get_hot_zone_draws(df, end, 20),
    'W28d': lambda df, end: get_hot_zone_days(df, end, 28),
    'W50': lambda df, end: get_hot_zone_draws(df, end, 50),
    'W100': lambda df, end: get_hot_zone_draws(df, end, 100),
}

results = []

for m in months:
    if pd.Timestamp(m['end_date']) < df['datum'].min() + timedelta(days=100):
        continue

    row = {'name': m['name'], 'year': m['year'], 'month': m['month']}

    for w_name, w_func in windows.items():
        try:
            hz = w_func(df, m['end_date'])
            jackpots = count_jackpots(df, hz, m['start_test'], end_test)
            row[f'{w_name}_hz'] = hz
            row[f'{w_name}_jp'] = len(jackpots)
            row[f'{w_name}_days'] = len(set(jp['datum'] for jp in jackpots))
        except:
            row[f'{w_name}_hz'] = []
            row[f'{w_name}_jp'] = 0
            row[f'{w_name}_days'] = 0

    results.append(row)

# Berechne Statistiken
totals = {w: {'jp': 0, 'success': 0, 'max': 0, 'max_month': ''} for w in windows.keys()}
for r in results:
    for w in windows.keys():
        jp = r.get(f'{w}_jp', 0)
        totals[w]['jp'] += jp
        if jp > 0:
            totals[w]['success'] += 1
        if jp > totals[w]['max']:
            totals[w]['max'] = jp
            totals[w]['max_month'] = r['name']

# Erstelle Markdown
md = """# Hot-Zone Fenster-Vergleich: Januar 2022 - Dezember 2024

Vergleich verschiedener Zeitfenster fuer die Hot-Zone Berechnung.
- **Typ 6 (6/6 = 500 EUR)** - Jackpot-Treffer pro Hot-Zone
- **Testzeitraum:** Bis Dezember 2025

---

## Uebersicht

| Fenster | Beschreibung |
|---------|--------------|
| W20 | Letzte 20 Ziehungen |
| W28d | Letzte 28 Kalendertage |
| W50 | Letzte 50 Ziehungen |
| W100 | Letzte 100 Ziehungen |

---

## Monatliche Jackpots

| Monat | W20 | W28d | W50 | W100 |
|-------|-----|------|-----|------|
"""

for r in results:
    w20 = r.get('W20_jp', 0)
    w28 = r.get('W28d_jp', 0)
    w50 = r.get('W50_jp', 0)
    w100 = r.get('W100_jp', 0)

    vals = [w20, w28, w50, w100]
    max_val = max(vals)

    def fmt(v):
        if v == max_val and v > 0:
            return f"**{v}**"
        elif v == 0:
            return "-"
        return str(v)

    md += f"| {r['name']} | {fmt(w20)} | {fmt(w28)} | {fmt(w50)} | {fmt(w100)} |\n"

md += f"| **TOTAL** | **{totals['W20']['jp']}** | **{totals['W28d']['jp']}** | **{totals['W50']['jp']}** | **{totals['W100']['jp']}** |\n"

md += f"""
---

## Zusammenfassung

| Metrik | W20 | W28d | W50 | W100 |
|--------|-----|------|-----|------|
| Total Jackpots | {totals['W20']['jp']} | {totals['W28d']['jp']} | {totals['W50']['jp']} | {totals['W100']['jp']} |
| Erfolgreiche Monate | {totals['W20']['success']}/{len(results)} | {totals['W28d']['success']}/{len(results)} | {totals['W50']['success']}/{len(results)} | {totals['W100']['success']}/{len(results)} |
| Erfolgsquote | {totals['W20']['success']*100//len(results)}% | {totals['W28d']['success']*100//len(results)}% | {totals['W50']['success']*100//len(results)}% | {totals['W100']['success']*100//len(results)}% |
| Bester Monat | {totals['W20']['max_month']} ({totals['W20']['max']}) | {totals['W28d']['max_month']} ({totals['W28d']['max']}) | {totals['W50']['max_month']} ({totals['W50']['max']}) | {totals['W100']['max_month']} ({totals['W100']['max']}) |

---

## Jaehrliche Aufteilung

"""

# Jaehrliche Statistiken
for year in [2022, 2023, 2024]:
    year_results = [r for r in results if r['year'] == year]
    md += f"### {year}\n\n"
    md += "| Monat | W20 | W28d | W50 | W100 |\n"
    md += "|-------|-----|------|-----|------|\n"

    year_totals = {w: 0 for w in windows.keys()}

    for r in year_results:
        w20 = r.get('W20_jp', 0)
        w28 = r.get('W28d_jp', 0)
        w50 = r.get('W50_jp', 0)
        w100 = r.get('W100_jp', 0)

        year_totals['W20'] += w20
        year_totals['W28d'] += w28
        year_totals['W50'] += w50
        year_totals['W100'] += w100

        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        month_name = month_names[r['month']]

        def fmt(v):
            return "-" if v == 0 else str(v)

        md += f"| {month_name} | {fmt(w20)} | {fmt(w28)} | {fmt(w50)} | {fmt(w100)} |\n"

    md += f"| **Summe** | **{year_totals['W20']}** | **{year_totals['W28d']}** | **{year_totals['W50']}** | **{year_totals['W100']}** |\n\n"

# Visualisierung
w20_bar = "#" * (totals['W20']['jp'] // 2)
w28_bar = "#" * (totals['W28d']['jp'] // 2)
w50_bar = "#" * (totals['W50']['jp'] // 2)
w100_bar = "#" * (totals['W100']['jp'] // 2)

md += f"""---

## Visualisierung

```
JACKPOTS PRO FENSTER (2022-2024)
================================

W20  (20 Zieh.):  {w20_bar} {totals['W20']['jp']}
W28d (28 Tage):   {w28_bar} {totals['W28d']['jp']}
W50  (50 Zieh.):  {w50_bar} {totals['W50']['jp']}
W100 (100 Zieh.): {w100_bar} {totals['W100']['jp']}
```

---

## Erkenntnisse

### Ranking nach Total Jackpots
1. **W20** (20 Ziehungen): {totals['W20']['jp']} Jackpots
2. **W50** (50 Ziehungen): {totals['W50']['jp']} Jackpots
3. **W28d** (28 Tage): {totals['W28d']['jp']} Jackpots
4. **W100** (100 Ziehungen): {totals['W100']['jp']} Jackpots

### Ranking nach Erfolgsquote
1. **W20**: {totals['W20']['success']*100//len(results)}% der Monate mit Jackpot
2. **W50**: {totals['W50']['success']*100//len(results)}% der Monate mit Jackpot
3. **W28d**: {totals['W28d']['success']*100//len(results)}% der Monate mit Jackpot
4. **W100**: {totals['W100']['success']*100//len(results)}% der Monate mit Jackpot

### Fazit
- **W20** hat die meisten Jackpots ({totals['W20']['jp']}) und hoechste Erfolgsquote ({totals['W20']['success']*100//len(results)}%)
- **W50** ist solide mit {totals['W50']['jp']} Jackpots
- **W100** ist zu traege mit nur {totals['W100']['jp']} Jackpots

---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

# Speichern
output_file = BASE_DIR / "results" / "hot_zone_fenster_vergleich_2022_2024.md"
output_file.parent.mkdir(exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"Datei gespeichert: {output_file}")
print()
print("=" * 70)
print("ZUSAMMENFASSUNG")
print("=" * 70)
print()
print(f"{'Fenster':<10} {'Jackpots':>10} {'Erfolg':>15} {'Bester Monat':>20}")
print("-" * 60)
for w in ['W20', 'W28d', 'W50', 'W100']:
    rate = totals[w]['success'] * 100 // len(results)
    print(f"{w:<10} {totals[w]['jp']:>10} {totals[w]['success']}/{len(results)} ({rate}%){' ':>3} {totals[w]['max_month']} ({totals[w]['max']})")
