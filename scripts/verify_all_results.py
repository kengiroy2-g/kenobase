#!/usr/bin/env python
"""
VOLLSTAENDIGE VERIFIKATION aller Ergebnisse
Klaert die Diskrepanz und zeigt exakt was gezaehlt wird.
"""

import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from datetime import timedelta

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

# Lade KENO-Daten
df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')

zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
df['zahlen'] = df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)

print("=" * 80)
print("VOLLSTAENDIGE VERIFIKATION")
print("=" * 80)
print()
print(f"Daten von {df['datum'].min().strftime('%d.%m.%Y')} bis {df['datum'].max().strftime('%d.%m.%Y')}")
print(f"Anzahl Ziehungen: {len(df)}")
print()

# ============================================================================
# FRAGE 1: Was bedeutet "Unique Tage" im frueheren Vergleich?
# ============================================================================
print("=" * 80)
print("ERKLAERUNG: Was wurde vorher gezaehlt?")
print("=" * 80)
print()
print("Im frueheren Vergleich wurde PRO MONAT gezaehlt:")
print("- Fuer jeden Monat (z.B. 2022-05) werden die Hot-Zone Zahlen ermittelt")
print("- Diese Zahlen werden gegen ALLE zukuenftigen Ziehungen getestet")
print("- Jackpots von 2022-05 bis 2025-12 werden gezaehlt")
print()
print("Bei DYNAMISCHEN Methoden (Hot-Zone): Jeder Monat hat ANDERE Zahlen")
print("  -> Verschiedene Jackpots werden gefunden")
print("  -> Die Summe ist die Gesamtzahl verschiedener Treffer-Kombinationen")
print()
print("Bei STATISCHEN Methoden (Synthesizer): GLEICHE Zahlen jeden Monat")
print("  -> Dieselben 3 Jackpots werden 32x gezaehlt!")
print("  -> Das war der FEHLER in meiner Berechnung")
print()

# ============================================================================
# FRAGE 2: Was sind die ECHTEN Ergebnisse?
# ============================================================================
print("=" * 80)
print("ECHTE ERGEBNISSE: Einmalige Jackpots pro Methode")
print("=" * 80)
print()

def get_hot_zone(df, end_date, window):
    """Hot-Zone: Top-7 aus letzten N Ziehungen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return [n for n, _ in freq.most_common(7)]

def find_all_jackpots(df, numbers, start_date, end_date):
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
                    'gruppe': tuple(sorted(group)),
                    'hot_zone': tuple(sorted(numbers))
                })
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
            'end_date': end_date,
            'start_test': f'{year}-{month:02d}-01'
        })

min_date = df['datum'].min() + timedelta(days=100)
months = [m for m in months if pd.Timestamp(m['end_date']) >= min_date]
end_test = pd.Timestamp('2025-12-31')

# ============================================================================
# METHODE 1: Hot-Zone W20 - Alle einzigartigen Jackpots
# ============================================================================
print("--- HOT-ZONE W20 ---")
print()

all_hz20_jackpots = set()  # (datum, gruppe) Tupel
hz20_details = []

for m in months:
    hz = get_hot_zone(df, m['end_date'], 20)
    jackpots = find_all_jackpots(df, hz, m['start_test'], end_test)

    for jp in jackpots:
        key = (jp['datum'], jp['gruppe'])
        if key not in all_hz20_jackpots:
            all_hz20_jackpots.add(key)
            hz20_details.append({
                'datum': jp['datum'],
                'gruppe': jp['gruppe'],
                'hot_zone': jp['hot_zone'],
                'ermittelt_fuer': m['name']
            })

hz20_unique_days = len(set(jp['datum'] for jp in hz20_details))
print(f"Einzigartige Jackpot-Events: {len(hz20_details)}")
print(f"Einzigartige Tage: {hz20_unique_days}")
print()

# ============================================================================
# METHODE 2: Hot-Zone W50 - Alle einzigartigen Jackpots
# ============================================================================
print("--- HOT-ZONE W50 ---")
print()

all_hz50_jackpots = set()
hz50_details = []

for m in months:
    hz = get_hot_zone(df, m['end_date'], 50)
    jackpots = find_all_jackpots(df, hz, m['start_test'], end_test)

    for jp in jackpots:
        key = (jp['datum'], jp['gruppe'])
        if key not in all_hz50_jackpots:
            all_hz50_jackpots.add(key)
            hz50_details.append({
                'datum': jp['datum'],
                'gruppe': jp['gruppe'],
                'hot_zone': jp['hot_zone'],
                'ermittelt_fuer': m['name']
            })

hz50_unique_days = len(set(jp['datum'] for jp in hz50_details))
print(f"Einzigartige Jackpot-Events: {len(hz50_details)}")
print(f"Einzigartige Tage: {hz50_unique_days}")
print()

# ============================================================================
# METHODE 3: HypothesisSynthesizer - Statische Zahlen
# ============================================================================
print("--- HYPOTHESISSYNTHESIZER (STATISCH) ---")
print()

SYNTH_NUMBERS = [36, 64, 14, 24, 42, 60, 57]
print(f"Zahlen: {SYNTH_NUMBERS}")
print()

# Teste NUR einmal gegen alle Ziehungen
synth_jackpots = find_all_jackpots(df, SYNTH_NUMBERS, df['datum'].min(), end_test)
synth_unique_days = len(set(jp['datum'] for jp in synth_jackpots))

print(f"Einzigartige Jackpot-Events: {len(synth_jackpots)}")
print(f"Einzigartige Tage: {synth_unique_days}")
print()

if synth_jackpots:
    print("Alle Jackpots:")
    for jp in sorted(synth_jackpots, key=lambda x: x['datum']):
        print(f"  {jp['datum'].strftime('%d.%m.%Y')}: {list(jp['gruppe'])}")
print()

# ============================================================================
# ZUSAMMENFASSUNG
# ============================================================================
print("=" * 80)
print("KORRIGIERTE ZUSAMMENFASSUNG")
print("=" * 80)
print()
print(f"{'Methode':<25} {'Unique Events':>15} {'Unique Tage':>15}")
print("-" * 60)
print(f"{'Hot-Zone W20':<25} {len(hz20_details):>15} {hz20_unique_days:>15}")
print(f"{'Hot-Zone W50':<25} {len(hz50_details):>15} {hz50_unique_days:>15}")
print(f"{'HypothesisSynthesizer':<25} {len(synth_jackpots):>15} {synth_unique_days:>15}")
print()

# ============================================================================
# STICHPROBEN-VERIFIKATION
# ============================================================================
print("=" * 80)
print("STICHPROBEN-VERIFIKATION: Hot-Zone W20")
print("=" * 80)
print()
print("Zeige erste 5 Jackpots mit Details:")
print()

for i, jp in enumerate(sorted(hz20_details, key=lambda x: x['datum'])[:5], 1):
    print(f"{i}. {jp['datum'].strftime('%d.%m.%Y')}")
    print(f"   Hot-Zone (ermittelt fuer {jp['ermittelt_fuer']}): {list(jp['hot_zone'])}")
    print(f"   Gewinner-Gruppe: {list(jp['gruppe'])}")
    print()

# ============================================================================
# MANUELLE VERIFIKATION eines Jackpots
# ============================================================================
print("=" * 80)
print("MANUELLE VERIFIKATION: Erster Hot-Zone W20 Jackpot")
print("=" * 80)
print()

if hz20_details:
    first_jp = sorted(hz20_details, key=lambda x: x['datum'])[0]
    jp_date = first_jp['datum']

    # Finde die Ziehung an diesem Tag
    ziehung = df[df['datum'] == jp_date].iloc[0]
    gezogen = sorted(ziehung['zahlen'])

    print(f"Datum: {jp_date.strftime('%d.%m.%Y')}")
    print(f"Gezogene Zahlen: {gezogen}")
    print(f"Hot-Zone (7 Zahlen): {list(first_jp['hot_zone'])}")
    print(f"Gewinner-Gruppe (6 Zahlen): {list(first_jp['gruppe'])}")
    print()

    # Pruefe ob alle 6 Zahlen gezogen wurden
    gruppe_set = set(first_jp['gruppe'])
    gezogen_set = set(gezogen)
    treffer = gruppe_set & gezogen_set

    print(f"Ueberschneidung: {len(treffer)}/6 Zahlen")
    print(f"Treffer: {sorted(treffer)}")
    print(f"Jackpot VERIFIZIERT: {len(treffer) == 6}")
print()

# ============================================================================
# ERKLAERUNG DER DISKREPANZ
# ============================================================================
print("=" * 80)
print("ERKLAERUNG DER FRUEHEREN DISKREPANZ")
print("=" * 80)
print()
print("FEHLER im frueheren Vergleich:")
print()
print("1. Fuer HypothesisSynthesizer wurden dieselben 3 Jackpots")
print("   fuer jeden der 32 Testmonate gezaehlt.")
print()
print("2. Das fuehrte zu: 3 Jackpots × ~19 Monate (Durchschnitt) = ~57 'Tage'")
print("   Aber es waren immer dieselben 3 Tage!")
print()
print("3. Bei Hot-Zone ist das anders: Jeder Monat hat ANDERE Zahlen,")
print("   daher werden tatsaechlich verschiedene Jackpots gefunden.")
print()
print("KORREKTUR:")
print(f"  - HypothesisSynthesizer: {len(synth_jackpots)} echte Jackpots")
print(f"  - Hot-Zone W20: {len(hz20_details)} echte Jackpots")
print(f"  - Hot-Zone W50: {len(hz50_details)} echte Jackpots")
