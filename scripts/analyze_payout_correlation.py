#!/usr/bin/env python
"""
Analyse: Auszahlungen vs Zahlen-Priorisierung
Untersucht das Verhaeltnis zwischen:
- Gesamtauszahlung pro Tag/Periode
- Gesamtgewinner pro Tag/Periode
- Nachfolgende Zahlen-Aenderungen
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent

# ============================================================================
# DATEN LADEN
# ============================================================================
print("Lade Daten...")

# KENO Ziehungen
keno_file = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
df_keno = pd.read_csv(keno_file, sep=';', encoding='utf-8')
df_keno['datum'] = pd.to_datetime(df_keno['Datum'], format='%d.%m.%Y', errors='coerce')
zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
df_keno['zahlen'] = df_keno[zahl_cols].apply(lambda row: set(int(x) for x in row if pd.notna(x)), axis=1)
df_keno = df_keno.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)

# Gewinnquoten 2022-2024
gq_file1 = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
gq_file2 = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv"

df_gq1 = pd.read_csv(gq_file1, encoding='utf-8-sig')
df_gq2 = pd.read_csv(gq_file2, encoding='utf-8-sig')
df_gq = pd.concat([df_gq1, df_gq2], ignore_index=True)

# Bereinige Spalten
df_gq.columns = df_gq.columns.str.strip()
df_gq['datum'] = pd.to_datetime(df_gq['Datum'], format='%d.%m.%Y', errors='coerce')

# Parse Gewinner (deutsche Zahlenformat: 1.234 = 1234)
def parse_german_number(x):
    if pd.isna(x):
        return 0
    if isinstance(x, (int, float)):
        return float(x)
    return float(str(x).replace('.', '').replace(',', '.'))

df_gq['gewinner'] = df_gq['Anzahl der Gewinner'].apply(parse_german_number)

# Parse Gewinn (z.B. "6 €" -> 6)
def parse_gewinn(x):
    if pd.isna(x):
        return 0
    s = str(x).replace('€', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(s)
    except:
        return 0

df_gq['gewinn_pro_euro'] = df_gq['1 Euro Gewinn'].apply(parse_gewinn)
df_gq['typ'] = df_gq['Keno-Typ'].astype(int)
df_gq['richtige'] = df_gq['Anzahl richtiger Zahlen'].astype(int)

# Berechne Auszahlung pro Zeile (Gewinner × Gewinn)
df_gq['auszahlung'] = df_gq['gewinner'] * df_gq['gewinn_pro_euro']

print(f"KENO Ziehungen: {len(df_keno)}")
print(f"Gewinnquoten-Eintraege: {len(df_gq)}")
print(f"Datum-Range GQ: {df_gq['datum'].min()} bis {df_gq['datum'].max()}")
print()

# ============================================================================
# TAGES-STATISTIKEN BERECHNEN
# ============================================================================
print("Berechne Tages-Statistiken...")

# Aggregiere pro Tag
daily_stats = df_gq.groupby('datum').agg({
    'gewinner': 'sum',
    'auszahlung': 'sum'
}).reset_index()

daily_stats.columns = ['datum', 'total_gewinner', 'total_auszahlung']

# Finde 10/10 Jackpot-Tage (Typ 10, 10 Richtige)
jackpot_10_10 = df_gq[(df_gq['typ'] == 10) & (df_gq['richtige'] == 10) & (df_gq['gewinner'] > 0)]
jackpot_days = set(jackpot_10_10['datum'].dropna())

daily_stats['is_jackpot_10_10'] = daily_stats['datum'].isin(jackpot_days)

# Merge mit KENO-Ziehungen
df_merged = pd.merge(df_keno[['datum', 'zahlen']], daily_stats, on='datum', how='left')
df_merged = df_merged.dropna(subset=['total_auszahlung'])

print(f"Merged Tage: {len(df_merged)}")
print(f"10/10 Jackpot-Tage: {len(jackpot_days)}")
print()

# ============================================================================
# ANALYSE 1: Hot-Zone Aenderungen nach hohen Auszahlungen
# ============================================================================
print("=" * 80)
print("ANALYSE 1: Hot-Zone Aenderungen nach Auszahlungs-Niveau")
print("=" * 80)
print()

def get_hot_7(zahlen_list, window=50):
    """Top-7 aus letzten Ziehungen."""
    freq = Counter()
    for zahlen in zahlen_list[-window:]:
        freq.update(zahlen)
    return set(n for n, _ in freq.most_common(7))

# Berechne Hot-Zone fuer jeden Tag
df_merged = df_merged.sort_values('datum').reset_index(drop=True)
hot_zones = []
for i in range(len(df_merged)):
    if i < 50:
        hot_zones.append(set())
    else:
        hz = get_hot_7(df_merged['zahlen'].iloc[:i].tolist(), 50)
        hot_zones.append(hz)

df_merged['hot_zone'] = hot_zones

# Berechne Hot-Zone Aenderung zum Vortag
def hz_change(row_idx, df):
    if row_idx < 51:
        return 0
    prev_hz = df.iloc[row_idx - 1]['hot_zone']
    curr_hz = df.iloc[row_idx]['hot_zone']
    if not prev_hz or not curr_hz:
        return 0
    return len(curr_hz - prev_hz)  # Neue Zahlen in Hot-Zone

hz_changes = [hz_change(i, df_merged) for i in range(len(df_merged))]
df_merged['hz_change'] = hz_changes

# Teile Tage nach Auszahlungs-Niveau
auszahlung_median = df_merged['total_auszahlung'].median()
auszahlung_75 = df_merged['total_auszahlung'].quantile(0.75)
auszahlung_90 = df_merged['total_auszahlung'].quantile(0.90)

print(f"Auszahlungs-Verteilung:")
print(f"  Median: {auszahlung_median:,.0f} EUR")
print(f"  75%:    {auszahlung_75:,.0f} EUR")
print(f"  90%:    {auszahlung_90:,.0f} EUR")
print()

# Analysiere Hot-Zone Aenderungen in den naechsten 7/28/48 Tagen
def analyze_hz_changes_after(df, condition_col, days_after):
    """Analysiert HZ-Aenderungen nach Tagen mit bestimmter Bedingung."""
    condition_dates = df[df[condition_col]]['datum'].tolist()
    total_changes = []

    for d in condition_dates:
        future = df[(df['datum'] > d) & (df['datum'] <= d + timedelta(days=days_after))]
        if len(future) > 0:
            total_changes.append(future['hz_change'].sum())

    return total_changes

# Hohe Auszahlung = Top 10%
df_merged['high_payout'] = df_merged['total_auszahlung'] >= auszahlung_90

print("Hot-Zone Aenderungen nach HOHER Auszahlung (Top 10%):")
for days in [7, 28, 48, 60]:
    changes = analyze_hz_changes_after(df_merged, 'high_payout', days)
    if changes:
        print(f"  Nach {days:>2} Tagen: Durchschn. {np.mean(changes):.1f} Aenderungen")
print()

print("Hot-Zone Aenderungen nach 10/10 JACKPOT:")
for days in [7, 28, 48, 60]:
    changes = analyze_hz_changes_after(df_merged, 'is_jackpot_10_10', days)
    if changes:
        print(f"  Nach {days:>2} Tagen: Durchschn. {np.mean(changes):.1f} Aenderungen")
print()

# ============================================================================
# ANALYSE 2: Perioden-Analyse
# ============================================================================
print("=" * 80)
print("ANALYSE 2: Perioden zwischen Jackpots")
print("=" * 80)
print()

jackpot_dates = sorted(list(jackpot_days))
print(f"10/10 Jackpot-Tage: {len(jackpot_dates)}")

if len(jackpot_dates) > 1:
    # Berechne Perioden zwischen Jackpots
    periods = []
    for i in range(1, len(jackpot_dates)):
        period_start = jackpot_dates[i-1]
        period_end = jackpot_dates[i]
        period_days = (period_end - period_start).days

        period_data = df_merged[(df_merged['datum'] > period_start) & (df_merged['datum'] <= period_end)]

        if len(period_data) > 0:
            periods.append({
                'start': period_start,
                'end': period_end,
                'days': period_days,
                'total_auszahlung': period_data['total_auszahlung'].sum(),
                'total_gewinner': period_data['total_gewinner'].sum(),
                'avg_auszahlung': period_data['total_auszahlung'].mean(),
                'hz_changes': period_data['hz_change'].sum()
            })

    print(f"Perioden zwischen Jackpots: {len(periods)}")
    print()

    if periods:
        print(f"{'Periode':<25} {'Tage':>8} {'Auszahlung':>15} {'HZ-Aend.':>10}")
        print("-" * 65)
        for p in periods[:10]:
            print(f"{p['start'].strftime('%d.%m.%y')}-{p['end'].strftime('%d.%m.%y'):<12} {p['days']:>8} {p['total_auszahlung']:>15,.0f} {p['hz_changes']:>10}")
        print()

        # Korrelation: Auszahlung vs HZ-Aenderungen
        ausz = [p['total_auszahlung'] for p in periods]
        hz_ch = [p['hz_changes'] for p in periods]

        if len(ausz) > 2:
            corr = np.corrcoef(ausz, hz_ch)[0, 1]
            print(f"Korrelation (Auszahlung vs HZ-Aenderungen): {corr:.3f}")
print()

# ============================================================================
# ANALYSE 3: 28-Tage und 48-60 Tage Perioden
# ============================================================================
print("=" * 80)
print("ANALYSE 3: Feste Perioden (28 Tage, 48-60 Tage)")
print("=" * 80)
print()

def analyze_fixed_periods(df, period_days):
    """Analysiert feste Perioden."""
    results = []
    start = df['datum'].min()
    end = df['datum'].max()

    current = start
    while current + timedelta(days=period_days) <= end:
        period_end = current + timedelta(days=period_days)
        period_data = df[(df['datum'] >= current) & (df['datum'] < period_end)]

        if len(period_data) > 0:
            results.append({
                'start': current,
                'end': period_end,
                'total_auszahlung': period_data['total_auszahlung'].sum(),
                'total_gewinner': period_data['total_gewinner'].sum(),
                'hz_changes': period_data['hz_change'].sum(),
                'jackpots': period_data['is_jackpot_10_10'].sum()
            })

        current = period_end

    return results

for period_length in [28, 48, 60]:
    periods = analyze_fixed_periods(df_merged, period_length)
    if periods:
        ausz = [p['total_auszahlung'] for p in periods]
        hz_ch = [p['hz_changes'] for p in periods]
        jp = [p['jackpots'] for p in periods]

        corr_ausz_hz = np.corrcoef(ausz, hz_ch)[0, 1] if len(ausz) > 2 else 0
        corr_jp_hz = np.corrcoef(jp, hz_ch)[0, 1] if len(jp) > 2 else 0

        print(f"{period_length}-Tage Perioden ({len(periods)} Perioden):")
        print(f"  Korr. Auszahlung vs HZ-Aenderung: {corr_ausz_hz:.3f}")
        print(f"  Korr. Jackpots vs HZ-Aenderung:   {corr_jp_hz:.3f}")
        print()

# ============================================================================
# ANALYSE 4: Gewinner-Verhaeltnis
# ============================================================================
print("=" * 80)
print("ANALYSE 4: Gewinner-Verhaeltnis und Zahlen-Shift")
print("=" * 80)
print()

# Berechne Verhaeltnis: Auszahlung pro Gewinner
df_merged['auszahlung_pro_gewinner'] = df_merged['total_auszahlung'] / df_merged['total_gewinner'].replace(0, 1)

# Hohe Auszahlung pro Gewinner = viele Grosse Gewinne
high_ratio = df_merged['auszahlung_pro_gewinner'] >= df_merged['auszahlung_pro_gewinner'].quantile(0.90)
df_merged['high_ratio'] = high_ratio

print("Tage mit hoher Auszahlung pro Gewinner (Top 10%):")
print(f"  Anzahl: {high_ratio.sum()}")
print(f"  Durchschn. HZ-Aenderung am naechsten Tag: {df_merged[high_ratio]['hz_change'].shift(-1).mean():.2f}")
print()

# ============================================================================
# MARKDOWN REPORT
# ============================================================================
md = f"""# Analyse: Auszahlungen vs Zahlen-Priorisierung

Untersuchung des Verhaeltnisses zwischen Gesamtauszahlung, Gewinnern und nachfolgenden Zahlen-Aenderungen.

---

## Daten-Uebersicht

| Metrik | Wert |
|--------|------|
| KENO Ziehungen | {len(df_keno)} |
| Gewinnquoten-Tage | {len(daily_stats)} |
| 10/10 Jackpot-Tage | {len(jackpot_days)} |
| Auszahlung Median | {auszahlung_median:,.0f} EUR |
| Auszahlung 90% | {auszahlung_90:,.0f} EUR |

---

## Hypothese

Das KENO-System passt Zahlen-Priorisierung an basierend auf:
1. Hoehe der Gesamtauszahlung
2. Anzahl der Gewinner
3. 10/10 Jackpot-Events

---

## Ergebnisse

### Hot-Zone Aenderungen nach hoher Auszahlung (Top 10%)

| Nach X Tagen | Durchschn. HZ-Aenderungen |
|--------------|---------------------------|
"""

for days in [7, 28, 48, 60]:
    changes = analyze_hz_changes_after(df_merged, 'high_payout', days)
    if changes:
        md += f"| {days} Tage | {np.mean(changes):.1f} |\n"

md += f"""
### Hot-Zone Aenderungen nach 10/10 Jackpot

| Nach X Tagen | Durchschn. HZ-Aenderungen |
|--------------|---------------------------|
"""

for days in [7, 28, 48, 60]:
    changes = analyze_hz_changes_after(df_merged, 'is_jackpot_10_10', days)
    if changes:
        md += f"| {days} Tage | {np.mean(changes):.1f} |\n"

md += f"""
### Korrelationen (Feste Perioden)

| Perioden-Laenge | Korr. Auszahlung-HZ | Korr. Jackpot-HZ |
|-----------------|---------------------|------------------|
"""

for period_length in [28, 48, 60]:
    periods = analyze_fixed_periods(df_merged, period_length)
    if periods:
        ausz = [p['total_auszahlung'] for p in periods]
        hz_ch = [p['hz_changes'] for p in periods]
        jp = [p['jackpots'] for p in periods]
        corr_ausz_hz = np.corrcoef(ausz, hz_ch)[0, 1] if len(ausz) > 2 else 0
        corr_jp_hz = np.corrcoef(jp, hz_ch)[0, 1] if len(jp) > 2 else 0
        md += f"| {period_length} Tage | {corr_ausz_hz:.3f} | {corr_jp_hz:.3f} |\n"

md += f"""
---

## Fazit

Die Analyse zeigt die Beziehung zwischen Auszahlungen und Hot-Zone Aenderungen.

---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

output_file = BASE_DIR / "results" / "auszahlung_zahlen_korrelation.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"Report gespeichert: {output_file}")
