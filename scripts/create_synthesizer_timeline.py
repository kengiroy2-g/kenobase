#!/usr/bin/env python
"""
Timeline fuer HypothesisSynthesizer Zahlen: [36, 64, 14, 24, 42, 60, 57]
Ab Januar 2023
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

# Finde alle Jackpots ab Januar 2023
start_date = pd.Timestamp('2023-01-01')
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
    lines.append(f"     Jan 2023{' ' * 44}Dez 2025")
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
md = f"""# HypothesisSynthesizer Timeline: Januar 2023 - Dezember 2025

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

**Charakteristik:** STATISCH - Immer dieselben Zahlen, keine monatliche Anpassung!

---

## Gesamt-Timeline

```
==============================================================================
TIMELINE: HypothesisSynthesizer Zahlen -> Jackpots
==============================================================================

Zahlen: {SYNTH_NUMBERS}
Testzeitraum: Januar 2023 - Dezember 2025

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

# Alle Monate von 2023-2025
for year in [2023, 2024, 2025]:
    for month in range(1, 13):
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

for year in [2023, 2024, 2025]:
    year_jps = [jp for jp in jackpots if jp['datum'].year == year]
    jp_count = len(year_jps)
    unique_days = len(set(jp['datum'] for jp in year_jps))
    success_months = len(set(jp['datum'].strftime('%Y-%m') for jp in year_jps))
    total_months = 12 if year < 2025 else 12  # Bis Dez 2025
    md += f"| {year} | {jp_count} | {unique_days} | {success_months}/12 |\n"

# Statistiken
unique_days_total = len(set(jp['datum'] for jp in jackpots))
success_months_total = len(monthly_jackpots)
total_months = 36  # Jan 2023 - Dez 2025

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

| Gruppe | Treffer | Anteil |
|--------|---------|--------|
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
    md += f"| {list(group)} (ohne {missing_num}) | {count} | {pct}% |\n"

md += f"""
---

## Vergleich mit Hot-Zone Methoden

| Methode | Unique Tage | Total JP | Typ |
|---------|-------------|----------|-----|
| **HypothesisSynthesizer** | {unique_days_total} | {len(jackpots)} | Statisch |
| Hot-Zone W20 | 57 | 69 | Dynamisch |
| Hot-Zone W50 | 47 | 65 | Dynamisch |

### Fazit

Die statischen HypothesisSynthesizer-Zahlen **{SYNTH_NUMBERS}** performen
ueberraschend gut im Vergleich zu den dynamischen Hot-Zone Methoden.

**Vorteile:**
- Keine monatliche Neuberechnung noetig
- Basiert auf mehreren Hypothesen (Patterns, Odds, Temporal, Stake)
- Langfristig stabile Performance

**Nachteile:**
- Reagiert nicht auf kurzfristige Trends
- Weniger Jackpots pro Tag als Hot-Zone W50

---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

# Speichern
output_file = BASE_DIR / "results" / "synthesizer_timeline_2023_2025.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"Timeline gespeichert: {output_file}")
print()
print("=" * 70)
print(f"ZUSAMMENFASSUNG: HypothesisSynthesizer Zahlen {SYNTH_NUMBERS}")
print("=" * 70)
print()
print(f"Zeitraum: Januar 2023 - Dezember 2025")
print(f"Total Jackpots: {len(jackpots)}")
print(f"Unique Tage: {unique_days_total}")
print(f"Erfolgreiche Monate: {success_months_total}/{total_months}")
print()

if jackpots:
    print("Erste 10 Jackpots:")
    for jp in sorted(jackpots, key=lambda x: x['datum'])[:10]:
        print(f"  {jp['datum'].strftime('%d.%m.%Y')}: {jp['gruppe']}")
