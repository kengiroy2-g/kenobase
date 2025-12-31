#!/usr/bin/env python
"""
Test der "Abkuehlungs-Theorie":
- Hot-Zahlen kuehlen sich ab nach Ermittlung
- Optimale Wartezeit vor dem Spielen: ~4 Monate
- Nach 48 Tagen ohne Treffer: weitere 48 Tage warten
"""

import pandas as pd
from pathlib import Path
from collections import Counter
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


def get_hot_zone(df, end_date, window=50):
    """Top-7 haeufigste Zahlen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return [n for n, _ in freq.most_common(7)]


def find_jackpots(df, numbers, start_date, end_date):
    """Findet Typ 6 Jackpots."""
    numbers = sorted(numbers)[:7]
    groups = list(combinations(numbers, 6))
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpots = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        for group in groups:
            if len(drawn & set(group)) == 6:
                jackpots.append(row['datum'])
    return jackpots


# Test-Monate generieren
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

print("=" * 80)
print("TEST: Abkuehlungs-Theorie")
print("=" * 80)
print()
print("Hypothese: Hot-Zahlen performen besser NACH einer Wartezeit")
print()

# ============================================================================
# TEST 1: Verschiedene Wartezeiten vergleichen
# ============================================================================
print("=" * 80)
print("TEST 1: Jackpots nach verschiedenen Wartezeiten")
print("=" * 80)
print()

# Teste verschiedene Verzoegerungen: 0, 30, 60, 90, 120, 150, 180 Tage
delays = [0, 30, 48, 60, 90, 120, 150, 180, 240, 300]
delay_results = {d: {'jp_count': 0, 'unique_days': set()} for d in delays}

for m in months:
    hz = get_hot_zone(df, m['end_date'], 50)

    for delay in delays:
        delayed_start = m['start_test'] + timedelta(days=delay)
        # Test-Ende: 1 Jahr nach delayed_start (um fair zu vergleichen)
        delayed_end = delayed_start + timedelta(days=365)
        delayed_end = min(delayed_end, pd.Timestamp('2025-12-31'))

        if delayed_start >= delayed_end:
            continue

        jackpots = find_jackpots(df, hz, delayed_start, delayed_end)
        delay_results[delay]['jp_count'] += len(jackpots)
        delay_results[delay]['unique_days'].update(jackpots)

print(f"{'Wartezeit':>12} {'Jackpots':>12} {'Unique Tage':>15} {'JP/Monat':>12}")
print("-" * 55)

for delay in delays:
    jp = delay_results[delay]['jp_count']
    days = len(delay_results[delay]['unique_days'])
    jp_per_month = jp / len(months) if months else 0
    marker = " ← BESTE" if jp == max(d['jp_count'] for d in delay_results.values()) else ""
    print(f"{delay:>10} Tage {jp:>10} {days:>15} {jp_per_month:>12.2f}{marker}")

print()

# ============================================================================
# TEST 2: Abkuehlungs-Perioden analysieren
# ============================================================================
print("=" * 80)
print("TEST 2: Jackpot-Verteilung nach Ermittlung (in Perioden)")
print("=" * 80)
print()

# Zaehle Jackpots in verschiedenen Perioden nach Ermittlung
period_results = {
    '0-30 Tage': 0,
    '31-60 Tage': 0,
    '61-90 Tage': 0,
    '91-120 Tage': 0,
    '121-180 Tage': 0,
    '181-270 Tage': 0,
    '271-365 Tage': 0,
    '>365 Tage': 0
}

all_gaps = []

for m in months:
    hz = get_hot_zone(df, m['end_date'], 50)
    jackpots = find_jackpots(df, hz, m['start_test'], pd.Timestamp('2025-12-31'))

    for jp_date in jackpots:
        gap = (jp_date - m['end_date']).days
        all_gaps.append(gap)

        if gap <= 30:
            period_results['0-30 Tage'] += 1
        elif gap <= 60:
            period_results['31-60 Tage'] += 1
        elif gap <= 90:
            period_results['61-90 Tage'] += 1
        elif gap <= 120:
            period_results['91-120 Tage'] += 1
        elif gap <= 180:
            period_results['121-180 Tage'] += 1
        elif gap <= 270:
            period_results['181-270 Tage'] += 1
        elif gap <= 365:
            period_results['271-365 Tage'] += 1
        else:
            period_results['>365 Tage'] += 1

total = sum(period_results.values())
print("Jackpot-Verteilung nach Abstand zur Ermittlung:")
print()

for period, count in period_results.items():
    pct = count * 100 // total if total else 0
    bar = '#' * (pct // 2)
    print(f"  {period:>15}: {count:>4} ({pct:>2}%) {bar}")

print()
print(f"Total: {total}")
print()

# ============================================================================
# TEST 3: Die 4-Monats-Theorie pruefen
# ============================================================================
print("=" * 80)
print("TEST 3: Die 4-Monats-Theorie (120 Tage Abkuehlung)")
print("=" * 80)
print()

# Vergleiche: Sofort spielen vs. Nach 4 Monaten spielen
sofort_jp = 0
sofort_days = set()
nach_4mo_jp = 0
nach_4mo_days = set()

for m in months:
    hz = get_hot_zone(df, m['end_date'], 50)

    # Sofort spielen: Tage 1-120
    jp1 = find_jackpots(df, hz, m['start_test'], m['start_test'] + timedelta(days=120))
    sofort_jp += len(jp1)
    sofort_days.update(jp1)

    # Nach 4 Monaten spielen: Tage 121-240
    delayed_start = m['start_test'] + timedelta(days=120)
    delayed_end = m['start_test'] + timedelta(days=240)
    jp2 = find_jackpots(df, hz, delayed_start, min(delayed_end, pd.Timestamp('2025-12-31')))
    nach_4mo_jp += len(jp2)
    nach_4mo_days.update(jp2)

print(f"{'Strategie':<25} {'Jackpots':>12} {'Unique Tage':>15}")
print("-" * 55)
print(f"{'Sofort (Tag 1-120)':<25} {sofort_jp:>12} {len(sofort_days):>15}")
print(f"{'Nach 4 Mo (Tag 121-240)':<25} {nach_4mo_jp:>12} {len(nach_4mo_days):>15}")
print()

if nach_4mo_jp > sofort_jp:
    print("✓ BESTAETIGT: Nach 4 Monaten mehr Jackpots!")
else:
    print("✗ NICHT BESTAETIGT: Sofort spielen hat mehr/gleich viele Jackpots")
print()

# ============================================================================
# TEST 4: Die 48-Tage-Regel
# ============================================================================
print("=" * 80)
print("TEST 4: Die 48-Tage-Regel")
print("=" * 80)
print()
print("Wenn nach 48 Tagen kein Jackpot, weitere 48 Tage warten?")
print()

# Zaehle: Wie viele Jackpots kommen in Tag 49-96 vs Tag 1-48?
tag_1_48 = 0
tag_49_96 = 0

for m in months:
    hz = get_hot_zone(df, m['end_date'], 50)

    jp1 = find_jackpots(df, hz, m['start_test'], m['start_test'] + timedelta(days=48))
    jp2 = find_jackpots(df, hz, m['start_test'] + timedelta(days=48), m['start_test'] + timedelta(days=96))

    tag_1_48 += len(jp1)
    tag_49_96 += len(jp2)

print(f"Tag 1-48:  {tag_1_48} Jackpots")
print(f"Tag 49-96: {tag_49_96} Jackpots")
print()

# ============================================================================
# MARKDOWN REPORT
# ============================================================================
md = f"""# Test: Abkuehlungs-Theorie

Hypothese: Hot-Zahlen performen besser NACH einer Wartezeit von ~4 Monaten.

---

## Test 1: Verschiedene Wartezeiten

| Wartezeit | Jackpots | Unique Tage | JP/Monat |
|-----------|----------|-------------|----------|
"""

for delay in delays:
    jp = delay_results[delay]['jp_count']
    days = len(delay_results[delay]['unique_days'])
    jp_per_month = jp / len(months) if months else 0
    best = " **BESTE**" if jp == max(d['jp_count'] for d in delay_results.values()) else ""
    md += f"| {delay} Tage | {jp} | {days} | {jp_per_month:.2f}{best} |\n"

md += f"""
---

## Test 2: Jackpot-Verteilung nach Ermittlung

| Periode | Jackpots | Anteil |
|---------|----------|--------|
"""

for period, count in period_results.items():
    pct = count * 100 // total if total else 0
    md += f"| {period} | {count} | {pct}% |\n"

md += f"""
---

## Test 3: Die 4-Monats-Theorie

| Strategie | Jackpots | Unique Tage |
|-----------|----------|-------------|
| Sofort (Tag 1-120) | {sofort_jp} | {len(sofort_days)} |
| Nach 4 Mo (Tag 121-240) | {nach_4mo_jp} | {len(nach_4mo_days)} |

**Ergebnis:** {"BESTAETIGT" if nach_4mo_jp > sofort_jp else "NICHT BESTAETIGT"}

---

## Test 4: Die 48-Tage-Regel

| Periode | Jackpots |
|---------|----------|
| Tag 1-48 | {tag_1_48} |
| Tag 49-96 | {tag_49_96} |

---

## Fazit

"""

best_delay = max(delay_results.items(), key=lambda x: x[1]['jp_count'])[0]
md += f"""Die Daten zeigen:

1. **Optimale Wartezeit:** {best_delay} Tage
2. **4-Monats-Theorie:** {"Bestaetigt" if nach_4mo_jp > sofort_jp else "Nicht bestaetigt"} (Sofort: {sofort_jp}, Nach 4 Mo: {nach_4mo_jp})
3. **48-Tage-Regel:** Tag 1-48 ({tag_1_48}) vs Tag 49-96 ({tag_49_96})

Die Verteilung zeigt, dass die meisten Jackpots in der Periode **{max(period_results.items(), key=lambda x: x[1])[0]}** auftreten.

---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

output_file = BASE_DIR / "results" / "abkuehlungs_theorie_test.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"Report gespeichert: {output_file}")
