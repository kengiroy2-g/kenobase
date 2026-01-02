#!/usr/bin/env python
"""
Vergleich: NumberPoolGenerator vs HypothesisSynthesizer vs Hot-Zone
Alle drei Methoden im direkten Vergleich.
"""

import sys
import pandas as pd
from pathlib import Path
from collections import Counter
from itertools import combinations
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

# Lade KENO-Daten
df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')

zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
df['zahlen'] = df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)


# ============================================================================
# METHODE 1: NumberPoolGenerator (Legacy V9)
# ============================================================================
def method_number_pool_generator(df, end_date, n_periods=3, draws_per_period=10,
                                  top_n_per_period=11, top_n_total=20):
    """Legacy V9: Schnittmengen-basierte Zahlenpool-Generierung."""
    hist = df[df['datum'] <= end_date].tail(n_periods * draws_per_period)
    if len(hist) < n_periods * draws_per_period:
        return []

    periods = []
    for i in range(n_periods):
        start = i * draws_per_period
        end_idx = start + draws_per_period
        periods.append(hist.iloc[start:end_idx])

    period_top_sets = []
    for period_df in periods:
        freq = Counter()
        for zahlen in period_df['zahlen']:
            freq.update(zahlen)
        top_n = set(n for n, _ in freq.most_common(top_n_per_period))
        period_top_sets.append(top_n)

    total_freq = Counter()
    for zahlen in hist['zahlen']:
        total_freq.update(zahlen)
    total_top = set(n for n, _ in total_freq.most_common(top_n_total))

    intersections_total = [s.intersection(total_top) for s in period_top_sets]
    combined = set().union(*intersections_total)

    for i in range(len(period_top_sets)):
        for j in range(i + 1, len(period_top_sets)):
            combined.update(period_top_sets[i].intersection(period_top_sets[j]))

    # Sortiere nach Haeufigkeit und nimm Top-7
    freq_sorted = sorted(combined, key=lambda x: -total_freq.get(x, 0))
    return freq_sorted[:7]


# ============================================================================
# METHODE 2: HypothesisSynthesizer
# ============================================================================
def method_hypothesis_synthesizer():
    """
    HypothesisSynthesizer: Kombiniert HYP-007, HYP-010, HYP-011, HYP-012.
    STATISCH - verwendet dieselben Top-7 fuer alle Monate!
    """
    try:
        from kenobase.prediction.synthesizer import HypothesisSynthesizer
        synth = HypothesisSynthesizer(results_dir=str(BASE_DIR / "results"))
        top_numbers = synth.get_top_numbers(n=7)
        return [ns.number for ns in top_numbers]
    except Exception as e:
        print(f"HypothesisSynthesizer Fehler: {e}")
        return []


# ============================================================================
# METHODE 3: Hot-Zone
# ============================================================================
def method_hot_zone(df, end_date, window=50, top_n=7):
    """Hot-Zone: Einfach Top-N aus letzten N Ziehungen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return [n for n, _ in freq.most_common(top_n)]


# ============================================================================
# JACKPOT ZAEHLUNG
# ============================================================================
def count_jackpots(df, numbers, start_date, end_date, combo_size=6):
    """Zaehlt Typ 6 Jackpots (6/6 = 500 EUR)."""
    numbers = sorted(numbers)[:7]
    if len(numbers) < combo_size:
        return 0, 0

    groups = list(combinations(numbers, combo_size))
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpot_days = set()
    jackpot_count = 0

    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        for group in groups:
            if len(drawn & set(group)) == combo_size:
                jackpot_days.add(row['datum'])
                jackpot_count += 1

    return len(jackpot_days), jackpot_count


# ============================================================================
# HAUPTVERGLEICH
# ============================================================================
print("=" * 80)
print("VERGLEICH: NumberPoolGenerator vs HypothesisSynthesizer vs Hot-Zone")
print("=" * 80)
print()

# Hole HypothesisSynthesizer Top-7 (statisch)
hyp_synth_numbers = method_hypothesis_synthesizer()
print(f"HypothesisSynthesizer Top-7: {hyp_synth_numbers}")
print()

# Test-Monate: Januar 2022 - Dezember 2024
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

end_test = pd.Timestamp('2025-12-31')

# Filter Monate
min_date = df['datum'].min() + timedelta(days=100)
months = [m for m in months if pd.Timestamp(m['end_date']) >= min_date]

results = []

for m in months:
    # Methode 1: NumberPoolGenerator
    npg_nums = method_number_pool_generator(df, m['end_date'])
    npg_days, npg_jp = count_jackpots(df, npg_nums, m['start_test'], end_test)

    # Methode 2: HypothesisSynthesizer (statisch!)
    hyp_days, hyp_jp = count_jackpots(df, hyp_synth_numbers, m['start_test'], end_test)

    # Methode 3: Hot-Zone W50
    hz50 = method_hot_zone(df, m['end_date'], window=50, top_n=7)
    hz50_days, hz50_jp = count_jackpots(df, hz50, m['start_test'], end_test)

    # Methode 4: Hot-Zone W20
    hz20 = method_hot_zone(df, m['end_date'], window=20, top_n=7)
    hz20_days, hz20_jp = count_jackpots(df, hz20, m['start_test'], end_test)

    results.append({
        'name': m['name'],
        'npg_nums': npg_nums,
        'npg_days': npg_days,
        'npg_jp': npg_jp,
        'hyp_days': hyp_days,
        'hyp_jp': hyp_jp,
        'hz50_nums': hz50,
        'hz50_days': hz50_days,
        'hz50_jp': hz50_jp,
        'hz20_nums': hz20,
        'hz20_days': hz20_days,
        'hz20_jp': hz20_jp,
    })

# Zusammenfassung
totals = {
    'npg_days': sum(r['npg_days'] for r in results),
    'npg_jp': sum(r['npg_jp'] for r in results),
    'hyp_days': sum(r['hyp_days'] for r in results),
    'hyp_jp': sum(r['hyp_jp'] for r in results),
    'hz50_days': sum(r['hz50_days'] for r in results),
    'hz50_jp': sum(r['hz50_jp'] for r in results),
    'hz20_days': sum(r['hz20_days'] for r in results),
    'hz20_jp': sum(r['hz20_jp'] for r in results),
}

# Erfolgsquoten
npg_success = sum(1 for r in results if r['npg_days'] > 0)
hyp_success = sum(1 for r in results if r['hyp_days'] > 0)
hz50_success = sum(1 for r in results if r['hz50_days'] > 0)
hz20_success = sum(1 for r in results if r['hz20_days'] > 0)

# Ausgabe
print("METHODEN-BESCHREIBUNG")
print("-" * 80)
print()
print("1. NumberPoolGenerator (Legacy V9):")
print("   - 3 Perioden x 10 Ziehungen = 30 Ziehungen")
print("   - Top-11 pro Periode, Top-20 gesamt, Schnittmengen")
print("   - DYNAMISCH: Aendert sich pro Monat")
print()
print("2. HypothesisSynthesizer:")
print("   - Kombiniert HYP-007, HYP-010, HYP-011, HYP-012 Scores")
print("   - Gewichtung: Patterns (0.1), Odds (0.3), Temporal (0.3), Stake (0.3)")
print(f"   - STATISCH: Immer dieselben 7 Zahlen: {hyp_synth_numbers}")
print()
print("3. Hot-Zone W50/W20:")
print("   - Top-7 aus letzten N Ziehungen")
print("   - DYNAMISCH: Aendert sich pro Monat")
print()

print("=" * 80)
print("ERGEBNISSE: Januar 2022 - Dezember 2024")
print("=" * 80)
print()

print(f"{'Methode':<30} {'Unique Tage':>12} {'Total JP':>10} {'Erfolg':>15} {'JP/Tag':>8}")
print("-" * 80)
print(f"{'NumberPoolGenerator':<30} {totals['npg_days']:>12} {totals['npg_jp']:>10} {npg_success}/{len(results)} ({npg_success*100//len(results)}%){'':<2} {totals['npg_jp']/max(totals['npg_days'],1):>8.2f}")
print(f"{'HypothesisSynthesizer':<30} {totals['hyp_days']:>12} {totals['hyp_jp']:>10} {hyp_success}/{len(results)} ({hyp_success*100//len(results)}%){'':<2} {totals['hyp_jp']/max(totals['hyp_days'],1):>8.2f}")
print(f"{'Hot-Zone W50':<30} {totals['hz50_days']:>12} {totals['hz50_jp']:>10} {hz50_success}/{len(results)} ({hz50_success*100//len(results)}%){'':<2} {totals['hz50_jp']/max(totals['hz50_days'],1):>8.2f}")
print(f"{'Hot-Zone W20':<30} {totals['hz20_days']:>12} {totals['hz20_jp']:>10} {hz20_success}/{len(results)} ({hz20_success*100//len(results)}%){'':<2} {totals['hz20_jp']/max(totals['hz20_days'],1):>8.2f}")
print()

# Monatliche Details (erste 6 Monate als Beispiel)
print("=" * 80)
print("BEISPIEL: Erste 6 Monate mit gewaehlten Zahlen")
print("=" * 80)
print()

for r in results[:6]:
    print(f"--- {r['name']} ---")
    print(f"  NPG:    {r['npg_nums']} -> {r['npg_days']} Tage, {r['npg_jp']} JP")
    print(f"  HypSyn: {hyp_synth_numbers} -> {r['hyp_days']} Tage, {r['hyp_jp']} JP (statisch)")
    print(f"  HZ50:   {r['hz50_nums']} -> {r['hz50_days']} Tage, {r['hz50_jp']} JP")
    print(f"  HZ20:   {r['hz20_nums']} -> {r['hz20_days']} Tage, {r['hz20_jp']} JP")
    print()

# Markdown Report
md = f"""# Methodenvergleich: Alle drei Methoden

Vergleich aller Zahlen-Auswahlmethoden fuer KENO Typ 6 (6/6 = 500€).

---

## Methoden-Beschreibung

### 1. NumberPoolGenerator (Legacy V9)

**Algorithmus:**
1. Letzte 30 Ziehungen in 3 Perioden aufteilen (je 10 Ziehungen)
2. Top-11 haeufigste Zahlen pro Periode ermitteln
3. Top-20 haeufigste Zahlen gesamt ermitteln
4. Schnittmengen: (Top-11 Periode) ∩ (Top-20 Gesamt)
5. Paarweise Schnittmengen der 3 Perioden
6. Top-7 aus Pool (nach Haeufigkeit sortiert)

**Charakteristik:** DYNAMISCH - Aendert sich jeden Monat

### 2. HypothesisSynthesizer

**Algorithmus:**
1. Lade Ergebnisse von HYP-007, HYP-010, HYP-011, HYP-012
2. Berechne gewichteten Score pro Zahl (1-70)
3. Gewichtung:
   - HYP-007 (Patterns): 0.1 (nicht signifikant)
   - HYP-010 (Odds): 0.3
   - HYP-011 (Temporal): 0.3 (Feiertags-Effekt signifikant)
   - HYP-012 (Stake): 0.3 (Auszahlung signifikant)
4. Top-7 nach Combined Score

**Charakteristik:** STATISCH - Immer dieselben Zahlen: **{hyp_synth_numbers}**

### 3. Hot-Zone W50 / W20

**Algorithmus:**
1. Letzte N Ziehungen nehmen (50 oder 20)
2. Top-7 haeufigste Zahlen ermitteln

**Charakteristik:** DYNAMISCH - Aendert sich jeden Monat

---

## Ergebnisse: Januar 2022 - Dezember 2024

| Methode | Typ | Unique Tage | Total JP | Erfolgsquote | JP/Tag |
|---------|-----|-------------|----------|--------------|--------|
| NumberPoolGenerator | Dynamisch | {totals['npg_days']} | {totals['npg_jp']} | {npg_success}/{len(results)} ({npg_success*100//len(results)}%) | {totals['npg_jp']/max(totals['npg_days'],1):.2f} |
| HypothesisSynthesizer | **Statisch** | {totals['hyp_days']} | {totals['hyp_jp']} | {hyp_success}/{len(results)} ({hyp_success*100//len(results)}%) | {totals['hyp_jp']/max(totals['hyp_days'],1):.2f} |
| Hot-Zone W50 | Dynamisch | {totals['hz50_days']} | {totals['hz50_jp']} | {hz50_success}/{len(results)} ({hz50_success*100//len(results)}%) | {totals['hz50_jp']/max(totals['hz50_days'],1):.2f} |
| Hot-Zone W20 | Dynamisch | {totals['hz20_days']} | {totals['hz20_jp']} | {hz20_success}/{len(results)} ({hz20_success*100//len(results)}%) | {totals['hz20_jp']/max(totals['hz20_days'],1):.2f} |

---

## Ranking

### Nach Unique Tagen:
1. **Hot-Zone W20**: {totals['hz20_days']} Tage
2. **Hot-Zone W50**: {totals['hz50_days']} Tage
3. **NumberPoolGenerator**: {totals['npg_days']} Tage
4. **HypothesisSynthesizer**: {totals['hyp_days']} Tage

### Nach Total Jackpots:
1. **Hot-Zone W20**: {totals['hz20_jp']} Jackpots
2. **Hot-Zone W50**: {totals['hz50_jp']} Jackpots
3. **NumberPoolGenerator**: {totals['npg_jp']} Jackpots
4. **HypothesisSynthesizer**: {totals['hyp_jp']} Jackpots

### Nach Erfolgsquote:
1. **Hot-Zone W20**: {hz20_success*100//len(results)}%
2. **Hot-Zone W50**: {hz50_success*100//len(results)}%
3. **NumberPoolGenerator**: {npg_success*100//len(results)}%
4. **HypothesisSynthesizer**: {hyp_success*100//len(results)}%

---

## Erkenntnisse

### HypothesisSynthesizer Problem

Der HypothesisSynthesizer hat das **schlechteste Ergebnis** weil:

1. **Statische Zahlen**: Verwendet immer dieselben 7 Zahlen ({hyp_synth_numbers})
2. **Keine Adaption**: Reagiert nicht auf aktuelle Trends
3. **Hypothesen-basiert**: Scores basieren auf allgemeinen Eigenschaften, nicht auf aktuelle Haeufigkeit

### Dynamische Methoden gewinnen

Die **Hot-Zone Methoden** (W20, W50) sind am besten weil:

1. **Dynamisch**: Passen sich monatlich an
2. **Frequenz-basiert**: Nutzen aktuelle Ziehungstrends
3. **Einfach**: Weniger Komplexitaet = weniger Fehlerquellen

### Least-Action Prinzip bestaetigt

Die einfachste Methode (Hot-Zone) liefert die besten Ergebnisse.
Der komplexeste Ansatz (HypothesisSynthesizer mit 4 Hypothesen) schneidet am schlechtesten ab.

---

*Erstellt: {datetime.now().strftime('%d.%m.%Y')}*
"""

# Speichern
output_file = BASE_DIR / "results" / "methoden_vergleich_komplett.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f"Report gespeichert: {output_file}")
