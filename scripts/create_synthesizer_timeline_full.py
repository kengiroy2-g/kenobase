#!/usr/bin/env python
"""
Timeline fuer HypothesisSynthesizer Zahlen: [36, 64, 14, 24, 42, 60, 57]
Ab Januar 2022 (vollstaendiger Vergleich)
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

# HypothesisSynthesizer Zahlen (statisch)
SYNTH_NUMBERS = [36, 64, 14, 24, 42, 60, 57]

def find_jackpots(df, numbers, start_date, end_date):
    """Findet alle Typ 6 Jackpots (6/6 = 500 EUR)."""
    numbers = sorted(numbers)
    groups = list(combinations(numbers, 6))
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpots = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        for group in groups:
            if len(drawn & set(group)) == 6:
                jackpots.append({
                    'datum': row['datum'],
                    'gruppe': list(group),
                    'gezogen': sorted(list(drawn))
                })
    return jackpots

# Finde alle Jackpots ab Mai 2022 (erste Daten)
start_date = pd.Timestamp('2022-05-01')
end_date = pd.Timestamp('2025-12-31')

jackpots = find_jackpots(df, SYNTH_NUMBERS, start_date, end_date)

# Gruppiere nach Monat
monthly_jackpots = defaultdict(list)
for jp in jackpots:
    month_key = jp['datum'].strftime('%Y-%m')
    monthly_jackpots[month_key].append(jp)

# Erstelle Timeline-Visualisierung
def create_timeline_ascii(jackpots, start_date, end_date):
    """Erstellt ASCII-Timeline."""
    if not jackpots:
        return "   KEINE JACKPOTS im Zeitraum"

    total_days = (end_date - start_date).days
    timeline_width = 60

    lines = []
    lines.append(f"     Mai 2022{' ' * 44}Dez 2025")
    lines.append(f"        |{' ' * 56}|")
    lines.append(f"        v{' ' * 56}v")

    # Timeline-Linie mit Markierungen
    timeline = ['-'] * timeline_width
    positions = []

    for jp in jackpots:
        days_since_start = (jp['datum'] - start_date).days
        pos = int((days_since_start / total_days) * (timeline_width - 1))
        pos = max(0, min(pos, timeline_width - 1))
        timeline[pos] = '*'
        positions.append((pos, jp['datum']))

    lines.append("   -----" + ''.join(timeline) + "-----")

    return '\n'.join(lines)

# Markdown erstellen
md = f"""# HypothesisSynthesizer Timeline: Mai 2022 - Dezember 2025

Analyse der statischen HypothesisSynthesizer-Zahlen und ihrer Jackpot-Performance.
- **Typ 6 (6/6 = 500€)** - Jackpot-Treffer
- **Zahlen:** {SYNTH_NUMBERS}

---

## Methode: HypothesisSynthesizer

**Algorithmus:**
```
1. Lade Ergebnisse von HYP-007, HYP-010, HYP-011, HYP-012
2. Berechne gewichteten Score pro Zahl (1-70):
   - HYP-007 (Patterns): Gewicht 0.1
   - HYP-010 (Odds Correlation): Gewicht 0.3
   - HYP-011 (Temporal Cycles): Gewicht 0.3
   - HYP-012 (Stake Correlation): Gewicht 0.3
3. Combined Score = Summe(score × weight) / Summe(weight)
4. Top-7 nach Combined Score
```

**Die 7 Zahlen und ihre Scores:**

| Zahl | Bedeutung |
|------|-----------|
| 36 | Hoch gerankt in Patterns + Safe Number |
| 64 | Low-Stake + wenig Mitspieler |
| 14 | Pattern-Zahl + Temporal-Effekt |
| 24 | Safe Number + Low-Stake |
| 42 | Pattern-Haeufigkeit |
| 60 | Low-Stake + Safe |
| 57 | Pattern + Temporal |

**Charakteristik:** STATISCH - Immer dieselben Zahlen, keine monatliche Anpassung!

---

## Gesamt-Timeline

```
==============================================================================
TIMELINE: HypothesisSynthesizer Zahlen -> Jackpots
==============================================================================

Zahlen: {SYNTH_NUMBERS}
Testzeitraum: Mai 2022 - Dezember 2025

{create_timeline_ascii(jackpots, start_date, end_date)}

   Typ 6 Jackpots (6/6 = 500€):      {len(jackpots)}
   Unique Tage:                       {len(set(jp['datum'] for jp in jackpots))}
```

---

## Alle Jackpots chronologisch

| # | Datum | Gewinner-Gruppe | Monate seit Start |
|---|-------|-----------------|-------------------|
"""

for i, jp in enumerate(sorted(jackpots, key=lambda x: x['datum']), 1):
    months_since = (jp['datum'] - start_date).days // 30
    md += f"| {i} | {jp['datum'].strftime('%d.%m.%Y')} | {jp['gruppe']} | +{months_since} Mo |\n"

md += f"""
---

## Monatliche Uebersicht

| Jahr | Monat | Jackpots | Tage | Details |
|------|-------|----------|------|---------|
"""

# Alle Monate von 2022-2025
for year in [2022, 2023, 2024, 2025]:
    start_month = 5 if year == 2022 else 1
    for month in range(start_month, 13):
        month_key = f'{year}-{month:02d}'
        if month_key > end_date.strftime('%Y-%m'):
            break

        month_jps = monthly_jackpots.get(month_key, [])
        jp_count = len(month_jps)
        unique_days = len(set(jp['datum'] for jp in month_jps))

        if jp_count > 0:
            dates = ', '.join(sorted(set(jp['datum'].strftime('%d.') for jp in month_jps)))
            md += f"| {year} | {month:02d} | **{jp_count}** | {unique_days} | {dates} |\n"
        else:
            md += f"| {year} | {month:02d} | - | - | - |\n"

# Jaehrliche Zusammenfassung
md += """
---

## Jaehrliche Zusammenfassung

| Jahr | Jackpots | Unique Tage | Erfolgreiche Monate |
|------|----------|-------------|---------------------|
"""

for year in [2022, 2023, 2024, 2025]:
    year_jps = [jp for jp in jackpots if jp['datum'].year == year]
    jp_count = len(year_jps)
    unique_days = len(set(jp['datum'] for jp in year_jps))
    success_months = len(set(jp['datum'].strftime('%Y-%m') for jp in year_jps))
    total_months = 8 if year == 2022 else 12
    md += f"| {year} | {jp_count} | {unique_days} | {success_months}/{total_months} |\n"

# Statistiken
unique_days_total = len(set(jp['datum'] for jp in jackpots))
success_months_total = len(monthly_jackpots)
total_months = 44  # Mai 2022 - Dez 2025

# Zeitliche Verteilung
first_jp = min(jp['datum'] for jp in jackpots) if jackpots else None
last_jp = max(jp['datum'] for jp in jackpots) if jackpots else None

md += f"""
---

## Statistiken

| Metrik | Wert |
|--------|------|
| **Zahlen** | {SYNTH_NUMBERS} |
| **Total Jackpots** | {len(jackpots)} |
| **Unique Tage** | {unique_days_total} |
| **Erfolgreiche Monate** | {success_months_total}/{total_months} ({success_months_total*100//total_months}%) |
| **JP pro Tag** | {len(jackpots)/max(unique_days_total,1):.2f} |
| **Erster Jackpot** | {first_jp.strftime('%d.%m.%Y') if first_jp else '-'} |
| **Letzter Jackpot** | {last_jp.strftime('%d.%m.%Y') if last_jp else '-'} |

---

## Gruppen-Analyse

Welche 6er-Kombinationen aus den 7 Zahlen haben getroffen?

| Gruppe | Ohne Zahl | Treffer | Anteil |
|--------|-----------|---------|--------|
"""

# Zaehle Gruppen
group_counts = defaultdict(int)
for jp in jackpots:
    group_key = tuple(sorted(jp['gruppe']))
    group_counts[group_key] += 1

for group, count in sorted(group_counts.items(), key=lambda x: -x[1]):
    missing = set(SYNTH_NUMBERS) - set(group)
    missing_num = list(missing)[0] if missing else '-'
    pct = count * 100 // len(jackpots) if jackpots else 0
    md += f"| {list(group)} | {missing_num} | {count} | {pct}% |\n"

# Abstaende zwischen Jackpots
if len(jackpots) > 1:
    sorted_jps = sorted(jackpots, key=lambda x: x['datum'])
    gaps = []
    for i in range(1, len(sorted_jps)):
        gap = (sorted_jps[i]['datum'] - sorted_jps[i-1]['datum']).days
        gaps.append(gap)

    md += f"""
---

## Abstaende zwischen Jackpots

| Metrik | Tage | Monate |
|--------|------|--------|
| Minimum | {min(gaps)} | {min(gaps)/30:.1f} |
| Maximum | {max(gaps)} | {max(gaps)/30:.1f} |
| Durchschnitt | {sum(gaps)/len(gaps):.0f} | {sum(gaps)/len(gaps)/30:.1f} |

### Alle Abstaende:

| Von | Bis | Tage |
|-----|-----|------|
"""
    for i in range(1, len(sorted_jps)):
        gap = (sorted_jps[i]['datum'] - sorted_jps[i-1]['datum']).days
        md += f"| {sorted_jps[i-1]['datum'].strftime('%d.%m.%Y')} | {sorted_jps[i]['datum'].strftime('%d.%m.%Y')} | {gap} |\n"

md += f"""
---

## Vergleich mit Hot-Zone Methoden

| Methode | Unique Tage | Total JP | Erfolgsquote | Typ |
|---------|-------------|----------|--------------|-----|
| **HypothesisSynthesizer** | {unique_days_total} | {len(jackpots)} | {success_months_total*100//total_months}% | Statisch |
| Hot-Zone W20 | 57 | 69 | 75% | Dynamisch |
| Hot-Zone W50 | 47 | 65 | 71% | Dynamisch |
| NumberPoolGenerator | 47 | 59 | 75% | Dynamisch |

---

## Erkenntnisse

### Performance der statischen Zahlen

Die HypothesisSynthesizer-Zahlen **{SYNTH_NUMBERS}** zeigen:

1. **{len(jackpots)} Jackpots** ueber {(end_date - start_date).days // 30} Monate
2. **{unique_days_total} verschiedene Tage** mit Treffern
3. **{success_months_total} erfolgreiche Monate** von {total_months}

### Interpretation

- Die statischen Zahlen basieren auf **langfristigen Mustern** aus den Hypothesen
- Sie sind **nicht optimiert** fuer kurzfristige Trends
- Die Methode funktioniert als **Baseline**, aber dynamische Methoden (Hot-Zone) performen besser

---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

# Speichern
output_file = BASE_DIR / "results" / "synthesizer_timeline_2022_2025.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"Timeline gespeichert: {output_file}")
print()
print("=" * 70)
print(f"ZUSAMMENFASSUNG: HypothesisSynthesizer Zahlen {SYNTH_NUMBERS}")
print("=" * 70)
print()
print(f"Zeitraum: Mai 2022 - Dezember 2025")
print(f"Total Jackpots: {len(jackpots)}")
print(f"Unique Tage: {unique_days_total}")
print(f"Erfolgreiche Monate: {success_months_total}/{total_months}")
print()

if jackpots:
    print("Alle Jackpots:")
    for jp in sorted(jackpots, key=lambda x: x['datum']):
        print(f"  {jp['datum'].strftime('%d.%m.%Y')}: {jp['gruppe']}")
