#!/usr/bin/env python
"""
Test: Die fuenfte 7 (Rang 29-35) statt Top-7 (Rang 1-7)
"""

import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
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


def get_nth_seven(df, end_date, window, n):
    """
    Holt die n-te Gruppe von 7 Zahlen nach Haeufigkeit.
    n=1: Rang 1-7 (Top-7)
    n=2: Rang 8-14
    n=3: Rang 15-21
    n=4: Rang 22-28
    n=5: Rang 29-35
    """
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)

    sorted_nums = [num for num, _ in freq.most_common()]
    start_idx = (n - 1) * 7
    end_idx = start_idx + 7

    return sorted_nums[start_idx:end_idx]


def find_jackpots(df, numbers, start_date, end_date):
    """Findet alle Typ 6 Jackpots."""
    numbers = sorted(numbers)[:7]
    if len(numbers) < 6:
        return []

    groups = list(combinations(numbers, 6))
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpots = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        for group in groups:
            if len(drawn & set(group)) == 6:
                jackpots.append({
                    'datum': row['datum'],
                    'gruppe': tuple(sorted(group))
                })
    return jackpots


# Test-Monate
months = []
for year in [2022, 2023, 2024]:
    for month in range(1, 13):
        if month == 1:
            end_date = f'{year-1}-12-31'
        else:
            last_day = (pd.Timestamp(f'{year}-{month:02d}-01') - timedelta(days=1)).strftime('%Y-%m-%d')
            end_date = last_day

        months.append({
            'name': f'{year}-{month:02d}',
            'end_date': end_date,
            'start_test': f'{year}-{month:02d}-01'
        })

min_date = df['datum'].min() + timedelta(days=100)
months = [m for m in months if pd.Timestamp(m['end_date']) >= min_date]
end_test = pd.Timestamp('2025-12-31')

print("=" * 80)
print("VERGLEICH: Top-7 vs Fuenfte-7 (Rang 29-35)")
print("=" * 80)
print()

# Teste alle Gruppen (1-5)
results = {}

for n in range(1, 6):
    all_jackpots = set()
    details = []

    for m in months:
        nums = get_nth_seven(df, m['end_date'], 50, n)  # Window 50
        if len(nums) < 7:
            continue

        jackpots = find_jackpots(df, nums, m['start_test'], end_test)

        for jp in jackpots:
            key = (jp['datum'], jp['gruppe'])
            if key not in all_jackpots:
                all_jackpots.add(key)
                details.append({
                    'datum': jp['datum'],
                    'gruppe': jp['gruppe'],
                    'zahlen': tuple(sorted(nums)),
                    'monat': m['name']
                })

    unique_days = len(set(d['datum'] for d in details))
    results[n] = {
        'events': len(details),
        'days': unique_days,
        'details': details
    }

    rang_start = (n-1) * 7 + 1
    rang_end = n * 7
    print(f"Gruppe {n} (Rang {rang_start}-{rang_end}): {len(details)} Events, {unique_days} Tage")

print()

# Detaillierte Ausgabe fuer Gruppe 5 (Fuenfte 7)
print("=" * 80)
print("DETAIL: Fuenfte 7 (Rang 29-35)")
print("=" * 80)
print()

fifth_details = results[5]['details']
if fifth_details:
    print(f"Total Jackpots: {len(fifth_details)}")
    print(f"Unique Tage: {results[5]['days']}")
    print()
    print("Alle Jackpots:")
    for jp in sorted(fifth_details, key=lambda x: x['datum']):
        print(f"  {jp['datum'].strftime('%d.%m.%Y')}: {list(jp['gruppe'])}")
        print(f"    Fuenfte-7: {list(jp['zahlen'])}")
        print()
else:
    print("Keine Jackpots gefunden!")
print()

# Markdown Report
md = f"""# Vergleich: Top-7 vs Fuenfte-7 (Rang 29-35)

Test verschiedener Frequenz-Gruppen fuer KENO Typ 6 (6/6 = 500€).
Fenster: 50 Ziehungen

---

## Uebersicht: Alle Gruppen

| Gruppe | Rang | Events | Unique Tage |
|--------|------|--------|-------------|
"""

for n in range(1, 6):
    rang_start = (n-1) * 7 + 1
    rang_end = n * 7
    md += f"| Gruppe {n} | {rang_start}-{rang_end} | {results[n]['events']} | {results[n]['days']} |\n"

md += f"""
---

## Erklaerung

- **Gruppe 1 (Rang 1-7)**: Die 7 haeufigsten Zahlen = "Hot-Zone"
- **Gruppe 2 (Rang 8-14)**: Die naechsten 7 haeufigsten
- **Gruppe 3 (Rang 15-21)**: Mittlere Haeufigkeit
- **Gruppe 4 (Rang 22-28)**: Unterdurchschnittliche Haeufigkeit
- **Gruppe 5 (Rang 29-35)**: Die "fuenfte 7" = seltenere Zahlen

---

## Detail: Fuenfte 7 (Rang 29-35)

**Total Jackpots:** {len(fifth_details)}
**Unique Tage:** {results[5]['days']}

### Alle Jackpots

| # | Datum | Gewinner-Gruppe | Fuenfte-7 Zahlen |
|---|-------|-----------------|------------------|
"""

for i, jp in enumerate(sorted(fifth_details, key=lambda x: x['datum']), 1):
    md += f"| {i} | {jp['datum'].strftime('%d.%m.%Y')} | {list(jp['gruppe'])} | {list(jp['zahlen'])} |\n"

md += f"""
---

## Monatliche Beispiele

Zeige welche Zahlen als "Fuenfte 7" pro Monat ermittelt wurden:

| Monat | Fuenfte-7 (Rang 29-35) |
|-------|------------------------|
"""

# Zeige einige Beispiel-Monate
for m in months[:6]:
    nums = get_nth_seven(df, m['end_date'], 50, 5)
    md += f"| {m['name']} | {nums} |\n"

md += """| ... | ... |

---

## Fazit

"""

# Vergleich
if results[1]['days'] > results[5]['days']:
    diff = results[1]['days'] - results[5]['days']
    md += f"""Die **Top-7 (Gruppe 1)** performt besser als die **Fuenfte-7 (Gruppe 5)**:

- Top-7: {results[1]['days']} Tage
- Fuenfte-7: {results[5]['days']} Tage
- Differenz: {diff} Tage

**Interpretation:** Haeufigere Zahlen ("Hot") haben eine hoehere Trefferquote.
"""
else:
    md += f"""Die **Fuenfte-7 (Gruppe 5)** performt ueberraschend gut:

- Fuenfte-7: {results[5]['days']} Tage
- Top-7: {results[1]['days']} Tage

**Interpretation:** Auch weniger haeufige Zahlen koennen Treffer erzielen.
"""

md += f"""
---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

# Speichern
output_file = BASE_DIR / "results" / "fuenfte_sieben_vergleich.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"Report gespeichert: {output_file}")
