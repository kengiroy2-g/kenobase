#!/usr/bin/env python
"""
Vollständige Analyse: Hot-Zone 6 für Keno Typ 6

Vergleicht Hot-Zone 6 (Top-6) mit Hot-Zone 7 (Top-7):
- Jackpot-Raten
- Timing-Muster
- Abkühlungs-Theorie
- Kosten-Nutzen-Analyse
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

TODAY = datetime.now()
LAST_DRAW = df['datum'].max()


def get_hot_zone(df, end_date, window, top_n):
    """Top-N häufigste Zahlen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return [n for n, _ in freq.most_common(top_n)]


def find_jackpots(df, numbers, start_date, end_date):
    """
    Findet Typ-6 Jackpots.
    Für HZ6: Nur 1 Kombination (alle 6 Zahlen müssen treffen)
    Für HZ7: 7 Kombinationen (je 6 aus 7)
    """
    numbers = sorted(numbers)
    n = len(numbers)

    if n < 6:
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
                break  # Nur ein Jackpot pro Ziehung
    return jackpots


def analyze_hotzone_performance(df, top_n, window, delays):
    """Analysiert Hot-Zone Performance für verschiedene Wartezeiten."""
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
                'end_date': pd.Timestamp(end_date),
                'start_test': pd.Timestamp(f'{year}-{month:02d}-01')
            })

    min_date = df['datum'].min() + timedelta(days=100)
    months = [m for m in months if m['end_date'] >= min_date]

    results = {d: {'jp_count': 0, 'unique_days': set()} for d in delays}

    for m in months:
        hz = get_hot_zone(df, m['end_date'], window, top_n)

        for delay in delays:
            start = m['start_test'] + timedelta(days=delay)
            end = start + timedelta(days=365)
            end = min(end, pd.Timestamp('2025-12-31'))

            if start >= end:
                continue

            jackpots = find_jackpots(df, hz, start, end)
            results[delay]['jp_count'] += len(jackpots)
            results[delay]['unique_days'].update(jp['datum'] for jp in jackpots)

    return results, len(months)


def analyze_period_distribution(df, top_n, window):
    """Analysiert Jackpot-Verteilung nach Perioden."""
    months = []
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            if month == 1:
                end_date = f'{year-1}-12-31'
            else:
                last_day = (pd.Timestamp(f'{year}-{month:02d}-01') - timedelta(days=1)).strftime('%Y-%m-%d')
                end_date = last_day
            months.append({
                'end_date': pd.Timestamp(end_date),
                'start_test': pd.Timestamp(f'{year}-{month:02d}-01')
            })

    min_date = df['datum'].min() + timedelta(days=100)
    months = [m for m in months if m['end_date'] >= min_date]

    periods = {
        '0-30 Tage': 0,
        '31-60 Tage': 0,
        '61-90 Tage': 0,
        '91-120 Tage': 0,
        '121-180 Tage': 0,
        '181-270 Tage': 0,
        '271-365 Tage': 0,
    }

    all_gaps = []

    for m in months:
        hz = get_hot_zone(df, m['end_date'], window, top_n)
        jackpots = find_jackpots(df, hz, m['start_test'], pd.Timestamp('2025-12-31'))

        for jp in jackpots:
            gap = (jp['datum'] - m['end_date']).days
            all_gaps.append(gap)

            if gap <= 30:
                periods['0-30 Tage'] += 1
            elif gap <= 60:
                periods['31-60 Tage'] += 1
            elif gap <= 90:
                periods['61-90 Tage'] += 1
            elif gap <= 120:
                periods['91-120 Tage'] += 1
            elif gap <= 180:
                periods['121-180 Tage'] += 1
            elif gap <= 270:
                periods['181-270 Tage'] += 1
            else:
                periods['271-365 Tage'] += 1

    return periods, all_gaps


def analyze_jackpot_sequences(df, top_n, window):
    """Analysiert Jackpot-Sequenzen (1., 2., 3. Jackpot etc.)."""
    months = []
    for year in [2022, 2023, 2024]:
        for month in range(1, 13):
            if month == 1:
                end_date = f'{year-1}-12-31'
            else:
                last_day = (pd.Timestamp(f'{year}-{month:02d}-01') - timedelta(days=1)).strftime('%Y-%m-%d')
                end_date = last_day
            months.append({
                'end_date': pd.Timestamp(end_date),
                'start_test': pd.Timestamp(f'{year}-{month:02d}-01')
            })

    min_date = df['datum'].min() + timedelta(days=100)
    months = [m for m in months if m['end_date'] >= min_date]

    # Sammle alle Hot-Zones und ihre Jackpot-Historie
    hotzone_history = defaultdict(lambda: {'jackpots': [], 'ermittlung': None})

    for m in months:
        hz = tuple(sorted(get_hot_zone(df, m['end_date'], window, top_n)))

        if hotzone_history[hz]['ermittlung'] is None:
            hotzone_history[hz]['ermittlung'] = m['end_date']

        jackpots = find_jackpots(df, hz, m['start_test'], pd.Timestamp('2025-12-31'))
        for jp in jackpots:
            if jp['datum'] not in [j['datum'] for j in hotzone_history[hz]['jackpots']]:
                hotzone_history[hz]['jackpots'].append(jp)

    # Statistiken
    jp_counts = [len(data['jackpots']) for data in hotzone_history.values()]
    count_distribution = Counter(jp_counts)

    # Zeit zwischen 1. und 2. Jackpot
    gaps_1_to_2 = []
    gaps_2_to_3 = []

    for hz, data in hotzone_history.items():
        jps = sorted(data['jackpots'], key=lambda x: x['datum'])
        if len(jps) >= 2:
            gap = (jps[1]['datum'] - jps[0]['datum']).days
            gaps_1_to_2.append(gap)
        if len(jps) >= 3:
            gap = (jps[2]['datum'] - jps[1]['datum']).days
            gaps_2_to_3.append(gap)

    return hotzone_history, count_distribution, gaps_1_to_2, gaps_2_to_3


def main():
    print("=" * 80)
    print("VOLLSTÄNDIGE ANALYSE: HOT-ZONE 6 FÜR KENO TYP 6")
    print("=" * 80)
    print()
    print(f"Letzte Ziehung: {LAST_DRAW.strftime('%d.%m.%Y')}")
    print()

    delays = [0, 30, 48, 60, 90, 120, 150, 180]

    # =========================================================================
    # TEIL 1: Basis-Performance Vergleich
    # =========================================================================
    print("=" * 80)
    print("TEIL 1: BASIS-PERFORMANCE VERGLEICH (HZ6 vs HZ7)")
    print("=" * 80)
    print()

    print("Analysiere Hot-Zone 6...")
    hz6_results, n_months = analyze_hotzone_performance(df, top_n=6, window=50, delays=delays)

    print("Analysiere Hot-Zone 7...")
    hz7_results, _ = analyze_hotzone_performance(df, top_n=7, window=50, delays=delays)

    print()
    print(f"{'Delay':>10} {'HZ6 JP':>10} {'HZ6 Tage':>10} {'HZ7 JP':>10} {'HZ7 Tage':>10} {'Diff':>10}")
    print("-" * 65)

    for delay in delays:
        hz6_jp = hz6_results[delay]['jp_count']
        hz6_days = len(hz6_results[delay]['unique_days'])
        hz7_jp = hz7_results[delay]['jp_count']
        hz7_days = len(hz7_results[delay]['unique_days'])
        diff = hz6_jp - hz7_jp
        diff_str = f"{diff:+d}" if diff != 0 else "0"
        print(f"{delay:>8}d {hz6_jp:>10} {hz6_days:>10} {hz7_jp:>10} {hz7_days:>10} {diff_str:>10}")

    print()

    # Kosten-Nutzen-Analyse
    print("KOSTEN-NUTZEN-ANALYSE:")
    print()
    print("Hot-Zone 6: 1 Kombination = 1 EUR/Ziehung")
    print("Hot-Zone 7: 7 Kombinationen = 7 EUR/Ziehung")
    print()

    # Beste Wartezeit für HZ6
    best_delay_hz6 = max(hz6_results.items(), key=lambda x: x[1]['jp_count'])[0]
    best_delay_hz7 = max(hz7_results.items(), key=lambda x: x[1]['jp_count'])[0]

    print(f"Beste Wartezeit HZ6: {best_delay_hz6} Tage")
    print(f"Beste Wartezeit HZ7: {best_delay_hz7} Tage")

    # =========================================================================
    # TEIL 2: Perioden-Verteilung
    # =========================================================================
    print()
    print("=" * 80)
    print("TEIL 2: JACKPOT-VERTEILUNG NACH PERIODEN")
    print("=" * 80)
    print()

    hz6_periods, hz6_gaps = analyze_period_distribution(df, top_n=6, window=50)
    hz7_periods, hz7_gaps = analyze_period_distribution(df, top_n=7, window=50)

    total_hz6 = sum(hz6_periods.values())
    total_hz7 = sum(hz7_periods.values())

    print(f"{'Periode':<15} {'HZ6':>8} {'%':>6} {'HZ7':>8} {'%':>6}")
    print("-" * 50)

    for period in hz6_periods.keys():
        hz6_count = hz6_periods[period]
        hz7_count = hz7_periods[period]
        hz6_pct = hz6_count * 100 / total_hz6 if total_hz6 else 0
        hz7_pct = hz7_count * 100 / total_hz7 if total_hz7 else 0
        print(f"{period:<15} {hz6_count:>8} {hz6_pct:>5.1f}% {hz7_count:>8} {hz7_pct:>5.1f}%")

    print()
    if hz6_gaps:
        print(f"HZ6 - Median Abstand: {statistics.median(hz6_gaps):.0f} Tage")
        print(f"HZ6 - Durchschnitt:   {statistics.mean(hz6_gaps):.0f} Tage")
    if hz7_gaps:
        print(f"HZ7 - Median Abstand: {statistics.median(hz7_gaps):.0f} Tage")
        print(f"HZ7 - Durchschnitt:   {statistics.mean(hz7_gaps):.0f} Tage")

    # =========================================================================
    # TEIL 3: Jackpot-Sequenzen (1., 2., 3. Jackpot)
    # =========================================================================
    print()
    print("=" * 80)
    print("TEIL 3: JACKPOT-SEQUENZEN")
    print("=" * 80)
    print()

    hz6_history, hz6_dist, hz6_gaps_1_2, hz6_gaps_2_3 = analyze_jackpot_sequences(df, 6, 50)
    hz7_history, hz7_dist, hz7_gaps_1_2, hz7_gaps_2_3 = analyze_jackpot_sequences(df, 7, 50)

    print("Verteilung der Jackpot-Anzahl pro Hot-Zone:")
    print()
    print(f"{'Jackpots':<12} {'HZ6':>10} {'HZ7':>10}")
    print("-" * 35)

    all_counts = set(hz6_dist.keys()) | set(hz7_dist.keys())
    for count in sorted(all_counts):
        hz6_c = hz6_dist.get(count, 0)
        hz7_c = hz7_dist.get(count, 0)
        print(f"{count:>8} JP {hz6_c:>10} {hz7_c:>10}")

    print()
    print("Zeit zwischen Jackpots:")
    print()

    if hz6_gaps_1_2:
        print(f"HZ6 - 1.→2. Jackpot: Median {statistics.median(hz6_gaps_1_2):.0f}d, "
              f"Min {min(hz6_gaps_1_2)}d, Max {max(hz6_gaps_1_2)}d (n={len(hz6_gaps_1_2)})")
    if hz7_gaps_1_2:
        print(f"HZ7 - 1.→2. Jackpot: Median {statistics.median(hz7_gaps_1_2):.0f}d, "
              f"Min {min(hz7_gaps_1_2)}d, Max {max(hz7_gaps_1_2)}d (n={len(hz7_gaps_1_2)})")

    if hz6_gaps_2_3:
        print(f"HZ6 - 2.→3. Jackpot: Median {statistics.median(hz6_gaps_2_3):.0f}d, "
              f"Min {min(hz6_gaps_2_3)}d, Max {max(hz6_gaps_2_3)}d (n={len(hz6_gaps_2_3)})")
    if hz7_gaps_2_3:
        print(f"HZ7 - 2.→3. Jackpot: Median {statistics.median(hz7_gaps_2_3):.0f}d, "
              f"Min {min(hz7_gaps_2_3)}d, Max {max(hz7_gaps_2_3)}d (n={len(hz7_gaps_2_3)})")

    # =========================================================================
    # TEIL 4: Aktuelle Hot-Zone 6
    # =========================================================================
    print()
    print("=" * 80)
    print("TEIL 4: AKTUELLE HOT-ZONE 6")
    print("=" * 80)
    print()

    current_hz6_w50 = get_hot_zone(df, LAST_DRAW, 50, 6)
    current_hz6_w20 = get_hot_zone(df, LAST_DRAW, 20, 6)
    current_hz7_w50 = get_hot_zone(df, LAST_DRAW, 50, 7)

    print(f"Hot-Zone 6 (W50): {sorted(current_hz6_w50)}")
    print(f"Hot-Zone 6 (W20): {sorted(current_hz6_w20)}")
    print(f"Hot-Zone 7 (W50): {sorted(current_hz7_w50)}")
    print()

    # Welche Zahl fehlt in HZ6?
    missing = set(current_hz7_w50) - set(current_hz6_w50)
    print(f"In HZ7 aber nicht in HZ6: {sorted(missing)}")

    # =========================================================================
    # TEIL 5: Strategie-Empfehlung für HZ6
    # =========================================================================
    print()
    print("=" * 80)
    print("TEIL 5: STRATEGIE-EMPFEHLUNG FÜR HOT-ZONE 6")
    print("=" * 80)
    print()

    # Vergleiche Effizienz
    hz6_best = hz6_results[best_delay_hz6]['jp_count']
    hz7_best = hz7_results[best_delay_hz7]['jp_count']

    hz6_cost = 1  # 1 EUR pro Ziehung
    hz7_cost = 7  # 7 EUR pro Ziehung

    hz6_efficiency = hz6_best / hz6_cost if hz6_cost else 0
    hz7_efficiency = hz7_best / hz7_cost if hz7_cost else 0

    print("EFFIZIENZ-VERGLEICH:")
    print()
    print(f"HZ6: {hz6_best} Jackpots / {hz6_cost} EUR = {hz6_efficiency:.2f} JP/EUR")
    print(f"HZ7: {hz7_best} Jackpots / {hz7_cost} EUR = {hz7_efficiency:.2f} JP/EUR")
    print()

    if hz6_efficiency > hz7_efficiency:
        print(f"→ HZ6 ist {hz6_efficiency/hz7_efficiency:.1f}x effizienter (JP pro EUR)")
    else:
        print(f"→ HZ7 ist {hz7_efficiency/hz6_efficiency:.1f}x effizienter (JP pro EUR)")

    print()
    print("STRATEGIE-ANPASSUNG FÜR HZ6:")
    print()
    print("1. WANN SPIELEN?")
    print(f"   - Optimale Wartezeit: {best_delay_hz6} Tage (vs {best_delay_hz7} für HZ7)")
    if hz6_gaps:
        print(f"   - Median bis Jackpot: {statistics.median(hz6_gaps):.0f} Tage")
    print()

    print("2. KOSTEN:")
    print("   - HZ6: 1 EUR pro Ziehung (1 Kombination)")
    print("   - HZ7: 7 EUR pro Ziehung (7 Kombinationen)")
    print()

    print("3. JACKPOT-WAHRSCHEINLICHKEIT:")
    print(f"   - HZ6: {hz6_best} Jackpots in Testperiode")
    print(f"   - HZ7: {hz7_best} Jackpots in Testperiode")
    print(f"   - HZ7 hat {hz7_best/hz6_best:.1f}x mehr Jackpots (aber 7x Kosten)")
    print()

    print("4. EMPFEHLUNG:")
    if hz6_efficiency > hz7_efficiency:
        print("   → FÜR KLEINE BUDGETS: HZ6 bevorzugen (besseres Preis-Leistungs-Verhältnis)")
        print("   → FÜR MAXIMALE JACKPOTS: HZ7 bevorzugen (mehr absolute Treffer)")
    else:
        print("   → HZ7 bietet besseres Gesamtpaket")
        print("   → HZ6 nur bei sehr knappem Budget")

    # =========================================================================
    # MARKDOWN REPORT
    # =========================================================================
    md = f"""# Hot-Zone 6 Analyse für Keno Typ 6

**Analyse-Datum:** {TODAY.strftime('%d.%m.%Y')}
**Letzte Ziehung:** {LAST_DRAW.strftime('%d.%m.%Y')}

---

## Übersicht

| Merkmal | Hot-Zone 6 | Hot-Zone 7 |
|---------|------------|------------|
| Anzahl Zahlen | 6 | 7 |
| Kombinationen | 1 | 7 |
| Kosten/Ziehung | 1 EUR | 7 EUR |
| Beste Wartezeit | {best_delay_hz6}d | {best_delay_hz7}d |
| Jackpots (best) | {hz6_best} | {hz7_best} |
| Effizienz (JP/EUR) | {hz6_efficiency:.2f} | {hz7_efficiency:.2f} |

---

## Teil 1: Performance nach Wartezeit

| Delay | HZ6 JP | HZ6 Tage | HZ7 JP | HZ7 Tage |
|-------|--------|----------|--------|----------|
"""

    for delay in delays:
        hz6_jp = hz6_results[delay]['jp_count']
        hz6_days = len(hz6_results[delay]['unique_days'])
        hz7_jp = hz7_results[delay]['jp_count']
        hz7_days = len(hz7_results[delay]['unique_days'])
        md += f"| {delay}d | {hz6_jp} | {hz6_days} | {hz7_jp} | {hz7_days} |\n"

    md += f"""

---

## Teil 2: Jackpot-Verteilung nach Perioden

| Periode | HZ6 | % | HZ7 | % |
|---------|-----|---|-----|---|
"""

    for period in hz6_periods.keys():
        hz6_count = hz6_periods[period]
        hz7_count = hz7_periods[period]
        hz6_pct = hz6_count * 100 / total_hz6 if total_hz6 else 0
        hz7_pct = hz7_count * 100 / total_hz7 if total_hz7 else 0
        md += f"| {period} | {hz6_count} | {hz6_pct:.1f}% | {hz7_count} | {hz7_pct:.1f}% |\n"

    md += f"""

### Median-Abstände

| Metrik | HZ6 | HZ7 |
|--------|-----|-----|
| Median Abstand | {statistics.median(hz6_gaps):.0f}d | {statistics.median(hz7_gaps):.0f}d |
| Durchschnitt | {statistics.mean(hz6_gaps):.0f}d | {statistics.mean(hz7_gaps):.0f}d |

---

## Teil 3: Jackpot-Sequenzen

### Verteilung Jackpots pro Hot-Zone

| Jackpots | HZ6 | HZ7 |
|----------|-----|-----|
"""

    for count in sorted(all_counts):
        hz6_c = hz6_dist.get(count, 0)
        hz7_c = hz7_dist.get(count, 0)
        md += f"| {count} | {hz6_c} | {hz7_c} |\n"

    md += f"""

### Zeit zwischen Jackpots

| Sequenz | HZ6 Median | HZ7 Median |
|---------|------------|------------|
| 1.→2. Jackpot | {statistics.median(hz6_gaps_1_2):.0f}d | {statistics.median(hz7_gaps_1_2):.0f}d |
"""

    if hz6_gaps_2_3 and hz7_gaps_2_3:
        md += f"| 2.→3. Jackpot | {statistics.median(hz6_gaps_2_3):.0f}d | {statistics.median(hz7_gaps_2_3):.0f}d |\n"

    md += f"""

---

## Teil 4: Aktuelle Hot-Zones

| Fenster | HZ6 | HZ7 |
|---------|-----|-----|
| W50 | {sorted(current_hz6_w50)} | {sorted(current_hz7_w50)} |
| W20 | {sorted(current_hz6_w20)} | - |

**Differenz:** In HZ7 aber nicht in HZ6: {sorted(missing)}

---

## Teil 5: Strategie-Empfehlung

### Effizienz-Vergleich

| Metrik | HZ6 | HZ7 |
|--------|-----|-----|
| Jackpots | {hz6_best} | {hz7_best} |
| Kosten | 1 EUR | 7 EUR |
| **JP/EUR** | **{hz6_efficiency:.2f}** | **{hz7_efficiency:.2f}** |

### Empfehlung

"""

    if hz6_efficiency > hz7_efficiency:
        md += f"""**HZ6 ist {hz6_efficiency/hz7_efficiency:.1f}x effizienter pro EUR!**

| Situation | Empfehlung |
|-----------|------------|
| Kleines Budget | **HZ6** - besseres Preis-Leistungs-Verhältnis |
| Maximale Jackpots | HZ7 - mehr absolute Treffer |
| Langzeit-Spieler | HZ6 - nachhaltigere Kosten |
"""
    else:
        md += f"""**HZ7 bietet besseres Gesamtpaket.**

| Situation | Empfehlung |
|-----------|------------|
| Standard | **HZ7** - bessere Gesamtperformance |
| Sehr knappes Budget | HZ6 - niedrigere Kosten |
"""

    md += f"""

---

## Strategie-Parameter für HZ6

| Parameter | HZ6 Wert | Anpassung vs HZ7 |
|-----------|----------|------------------|
| Optimale Wartezeit | {best_delay_hz6}d | {"Gleich" if best_delay_hz6 == best_delay_hz7 else f"vs {best_delay_hz7}d"} |
| Nach 10/10 Jackpot | 30 Tage warten | Keine Änderung |
| Nach 2x Treffer | 7-9 Monate Pause | Keine Änderung |
| Median bis Jackpot | {statistics.median(hz6_gaps):.0f}d | vs {statistics.median(hz7_gaps):.0f}d |

---

*Erstellt: {TODAY.strftime('%d.%m.%Y %H:%M')}*
"""

    output_file = BASE_DIR / "results" / "hotzone6_analyse.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print()
    print(f"Report gespeichert: {output_file}")


if __name__ == "__main__":
    main()
