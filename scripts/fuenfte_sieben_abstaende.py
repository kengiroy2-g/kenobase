#!/usr/bin/env python
"""
Abstaende: Fuenfte-7 Ermittlung bis Jackpot
Vergleich mit Top-7 (Hot-Zone)
"""

import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime, timedelta
import statistics

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

# Lade KENO-Daten
df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')

zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
df['zahlen'] = df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)


def get_nth_seven(df, end_date, window, n):
    """Holt die n-te Gruppe von 7 Zahlen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    sorted_nums = [num for num, _ in freq.most_common()]
    start_idx = (n - 1) * 7
    end_idx = start_idx + 7
    return sorted_nums[start_idx:end_idx]


def find_jackpots_with_dates(df, numbers, start_date, end_date):
    """Findet Jackpots mit Datum."""
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
            'end_date': pd.Timestamp(end_date),
            'start_test': pd.Timestamp(f'{year}-{month:02d}-01')
        })

min_date = df['datum'].min() + timedelta(days=100)
months = [m for m in months if m['end_date'] >= min_date]
end_test = pd.Timestamp('2025-12-31')

print("=" * 80)
print("ABSTAENDE: Ermittlung bis Jackpot")
print("=" * 80)
print()

# Berechne Abstaende fuer alle Gruppen
all_results = {}

for n in range(1, 6):
    gaps = []  # Liste von (monat, erster_jackpot_abstand)

    for m in months:
        nums = get_nth_seven(df, m['end_date'], 50, n)
        if len(nums) < 7:
            continue

        jackpots = find_jackpots_with_dates(df, nums, m['start_test'], end_test)

        if jackpots:
            # Erster Jackpot
            first_jp = min(jp['datum'] for jp in jackpots)
            gap_days = (first_jp - m['end_date']).days
            gaps.append({
                'monat': m['name'],
                'ermittlung': m['end_date'],
                'erster_jp': first_jp,
                'abstand_tage': gap_days,
                'zahlen': nums
            })

    all_results[n] = gaps

# Statistiken berechnen
print("ZUSAMMENFASSUNG: Erster Jackpot nach Ermittlung")
print("-" * 80)
print()
print(f"{'Gruppe':<15} {'Min':>10} {'Max':>10} {'Durchschn':>12} {'Median':>10} {'Anzahl':>10}")
print("-" * 80)

for n in range(1, 6):
    gaps = all_results[n]
    if gaps:
        tage = [g['abstand_tage'] for g in gaps]
        rang = f"Rang {(n-1)*7+1}-{n*7}"
        print(f"Gruppe {n} ({rang}): {min(tage):>5} Tage {max(tage):>5} Tage {statistics.mean(tage):>8.0f} Tage {statistics.median(tage):>6.0f} Tage {len(gaps):>6}")
print()

# Detail fuer Gruppe 5 (Fuenfte 7)
print("=" * 80)
print("DETAIL: Fuenfte 7 (Rang 29-35) - Abstaende")
print("=" * 80)
print()

gaps5 = all_results[5]
if gaps5:
    tage5 = [g['abstand_tage'] for g in gaps5]

    print(f"Minimum:      {min(tage5)} Tage ({min(tage5)/30:.1f} Monate)")
    print(f"Maximum:      {max(tage5)} Tage ({max(tage5)/30:.1f} Monate)")
    print(f"Durchschnitt: {statistics.mean(tage5):.0f} Tage ({statistics.mean(tage5)/30:.1f} Monate)")
    print(f"Median:       {statistics.median(tage5):.0f} Tage ({statistics.median(tage5)/30:.1f} Monate)")
    print()

    # Verteilung
    print("Verteilung:")
    buckets = {'<1 Mo': 0, '1-3 Mo': 0, '3-6 Mo': 0, '6-12 Mo': 0, '1-2 J': 0, '>2 J': 0}
    for t in tage5:
        if t < 30:
            buckets['<1 Mo'] += 1
        elif t < 90:
            buckets['1-3 Mo'] += 1
        elif t < 180:
            buckets['3-6 Mo'] += 1
        elif t < 365:
            buckets['6-12 Mo'] += 1
        elif t < 730:
            buckets['1-2 J'] += 1
        else:
            buckets['>2 J'] += 1

    for bucket, count in buckets.items():
        pct = count * 100 // len(tage5) if tage5 else 0
        bar = '#' * (pct // 2)
        print(f"  {bucket:>8}: {count:>3} ({pct:>2}%) {bar}")
    print()

    # Schnellste Jackpots
    print("Schnellste Jackpots (unter 60 Tage):")
    schnelle = sorted([g for g in gaps5 if g['abstand_tage'] < 60], key=lambda x: x['abstand_tage'])
    for g in schnelle[:10]:
        print(f"  {g['monat']}: {g['abstand_tage']} Tage -> {g['erster_jp'].strftime('%d.%m.%Y')}")
        print(f"    Zahlen: {g['zahlen']}")
    print()

# Markdown Report
md = f"""# Abstaende: Ermittlung bis Jackpot

Analyse der Zeitspanne zwischen Zahlen-Ermittlung und erstem Jackpot-Treffer.
Fenster: 50 Ziehungen

---

## Zusammenfassung: Alle Gruppen

| Gruppe | Rang | Min | Max | Durchschnitt | Median | Anzahl |
|--------|------|-----|-----|--------------|--------|--------|
"""

for n in range(1, 6):
    gaps = all_results[n]
    if gaps:
        tage = [g['abstand_tage'] for g in gaps]
        rang = f"{(n-1)*7+1}-{n*7}"
        md += f"| Gruppe {n} | {rang} | {min(tage)} Tage | {max(tage)} Tage | {statistics.mean(tage):.0f} Tage | {statistics.median(tage):.0f} Tage | {len(gaps)} |\n"

md += """
### In Monaten

| Gruppe | Rang | Min | Durchschnitt | Median |
|--------|------|-----|--------------|--------|
"""

for n in range(1, 6):
    gaps = all_results[n]
    if gaps:
        tage = [g['abstand_tage'] for g in gaps]
        rang = f"{(n-1)*7+1}-{n*7}"
        md += f"| Gruppe {n} | {rang} | {min(tage)/30:.1f} Mo | {statistics.mean(tage)/30:.1f} Mo | {statistics.median(tage)/30:.1f} Mo |\n"

md += f"""
---

## Detail: Fuenfte 7 (Rang 29-35)

| Metrik | Tage | Monate |
|--------|------|--------|
| Minimum | {min(tage5)} | {min(tage5)/30:.1f} |
| Maximum | {max(tage5)} | {max(tage5)/30:.1f} |
| Durchschnitt | {statistics.mean(tage5):.0f} | {statistics.mean(tage5)/30:.1f} |
| Median | {statistics.median(tage5):.0f} | {statistics.median(tage5)/30:.1f} |

### Verteilung

```
"""

for bucket, count in buckets.items():
    pct = count * 100 // len(tage5) if tage5 else 0
    bar = '#' * pct
    md += f"  {bucket:>8}: {count:>3} ({pct:>2}%) {bar}\n"

md += """```

---

## Schnellste Jackpots: Fuenfte 7

| Monat | Abstand | Jackpot-Datum | Zahlen (Rang 29-35) |
|-------|---------|---------------|---------------------|
"""

schnelle = sorted([g for g in gaps5 if g['abstand_tage'] < 90], key=lambda x: x['abstand_tage'])
for g in schnelle[:15]:
    md += f"| {g['monat']} | {g['abstand_tage']} Tage | {g['erster_jp'].strftime('%d.%m.%Y')} | {g['zahlen']} |\n"

md += f"""
---

## Vergleich: Top-7 vs Fuenfte-7

| Metrik | Top-7 (Rang 1-7) | Fuenfte-7 (Rang 29-35) |
|--------|------------------|------------------------|
| Min Abstand | {min([g['abstand_tage'] for g in all_results[1]])} Tage | {min(tage5)} Tage |
| Durchschn. Abstand | {statistics.mean([g['abstand_tage'] for g in all_results[1]]):.0f} Tage | {statistics.mean(tage5):.0f} Tage |
| Median Abstand | {statistics.median([g['abstand_tage'] for g in all_results[1]]):.0f} Tage | {statistics.median(tage5):.0f} Tage |
| Erfolgreiche Monate | {len(all_results[1])}/{len(months)} | {len(gaps5)}/{len(months)} |

---

## Alle Abstaende: Fuenfte 7 pro Monat

| Monat | Abstand (Tage) | Erster Jackpot |
|-------|----------------|----------------|
"""

for g in sorted(gaps5, key=lambda x: x['monat']):
    md += f"| {g['monat']} | {g['abstand_tage']} | {g['erster_jp'].strftime('%d.%m.%Y')} |\n"

md += f"""
---

## Fazit

"""

# Vergleich Top-7 vs Fuenfte-7
tage1 = [g['abstand_tage'] for g in all_results[1]]
median1 = statistics.median(tage1)
median5 = statistics.median(tage5)

if median5 < median1:
    md += f"""Die **Fuenfte-7** hat einen kuerzeren Median-Abstand ({median5:.0f} Tage) als die **Top-7** ({median1:.0f} Tage).

Das bedeutet: Seltenere Zahlen (Rang 29-35) treffen schneller nach der Ermittlung!
"""
else:
    md += f"""Die **Top-7** hat einen kuerzeren Median-Abstand ({median1:.0f} Tage) als die **Fuenfte-7** ({median5:.0f} Tage).

Das bedeutet: Haeufigere Zahlen (Rang 1-7) treffen schneller nach der Ermittlung.
"""

md += f"""
---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

# Speichern
output_file = BASE_DIR / "results" / "fuenfte_sieben_abstaende.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"Report gespeichert: {output_file}")
