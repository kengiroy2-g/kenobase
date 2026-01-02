#!/usr/bin/env python
"""
Findet "reife" Hot-Zones basierend auf der Strategie:

1. Hot-Zones mit genau 1 Jackpot → 2. Jackpot steht bevor
2. Hot-Zones mit 2+ Jackpots → 7-9 Monate Pause vorbei → wieder spielbar

Basiert auf der Ultimativen Typ-6 Strategie.
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


def get_hot_zone(df, end_date, window=50):
    """Top-7 häufigste Zahlen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return tuple(sorted([n for n, _ in freq.most_common(7)]))


def find_jackpots_for_hotzone(df, hz_numbers, start_date, end_date):
    """Findet alle Typ-6 Jackpots für eine Hot-Zone."""
    numbers = sorted(hz_numbers)[:7]
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
                    'gezogen': tuple(sorted(drawn))
                })
                break  # Nur ein Jackpot pro Ziehung zählen
    return jackpots


def analyze_all_hotzones():
    """
    Analysiert alle historischen Hot-Zones und ihre Jackpot-Historie.
    """
    # Generiere Hot-Zones für jeden Monat
    hotzones = {}

    test_dates = pd.date_range(start='2022-04-01', end=LAST_DRAW - timedelta(days=30), freq='MS')

    for ermittlung_date in test_dates:
        hz = get_hot_zone(df, ermittlung_date, 50)

        if hz not in hotzones:
            hotzones[hz] = {
                'erste_ermittlung': ermittlung_date,
                'letzte_ermittlung': ermittlung_date,
                'ermittlungen': [ermittlung_date],
                'jackpots': [],
                'zahlen': hz
            }
        else:
            hotzones[hz]['letzte_ermittlung'] = ermittlung_date
            hotzones[hz]['ermittlungen'].append(ermittlung_date)

    # Finde Jackpots für jede Hot-Zone
    for hz, data in hotzones.items():
        # Suche Jackpots ab erster Ermittlung bis heute
        jackpots = find_jackpots_for_hotzone(
            df, hz,
            data['erste_ermittlung'],
            LAST_DRAW
        )
        data['jackpots'] = jackpots
        data['jackpot_count'] = len(jackpots)

        if jackpots:
            data['erster_jackpot'] = min(jp['datum'] for jp in jackpots)
            data['letzter_jackpot'] = max(jp['datum'] for jp in jackpots)
            data['tage_seit_letztem_jp'] = (LAST_DRAW - data['letzter_jackpot']).days
        else:
            data['erster_jackpot'] = None
            data['letzter_jackpot'] = None
            data['tage_seit_letztem_jp'] = None

    return hotzones


def main():
    print("=" * 80)
    print("REIFE HOT-ZONES FINDEN")
    print("=" * 80)
    print()
    print(f"Letzte Ziehung: {LAST_DRAW.strftime('%d.%m.%Y')}")
    print(f"Analyse-Datum: {TODAY.strftime('%d.%m.%Y')}")
    print()

    print("Analysiere alle historischen Hot-Zones...")
    hotzones = analyze_all_hotzones()

    print(f"Gefunden: {len(hotzones)} unique Hot-Zones")
    print()

    # =========================================================================
    # KATEGORIE 1: Genau 1 Jackpot - 2. Jackpot steht bevor
    # =========================================================================
    print("=" * 80)
    print("KATEGORIE 1: Hot-Zones mit genau 1 Jackpot (2. Jackpot erwartet)")
    print("=" * 80)
    print()
    print("Diese Hot-Zones hatten bereits 1 Jackpot.")
    print("Laut Statistik kommt der 2. Jackpot oft 48-120 Tage nach dem ersten.")
    print()

    cat1 = []
    for hz, data in hotzones.items():
        if data['jackpot_count'] == 1:
            days_since = data['tage_seit_letztem_jp']
            # Optimales Fenster: 48-180 Tage seit erstem Jackpot
            if 30 <= days_since <= 200:
                cat1.append((hz, data, days_since))

    cat1.sort(key=lambda x: x[2])  # Nach Tagen sortieren

    if cat1:
        print(f"{'Tage':>6} {'Zahlen':<35} {'1. Jackpot':>12} {'Status':<15}")
        print("-" * 80)

        for hz, data, days in cat1:
            status = "OPTIMAL" if 48 <= days <= 120 else "MÖGLICH"
            jp_date = data['erster_jackpot'].strftime('%d.%m.%Y')
            print(f"{days:>6}d {str(list(hz)):<35} {jp_date:>12} {status:<15}")

        print()
        print(f"Gefunden: {len(cat1)} Hot-Zones mit 1 Jackpot im spielbaren Zeitfenster")
    else:
        print("Keine Hot-Zones in dieser Kategorie gefunden.")

    # =========================================================================
    # KATEGORIE 2: 2+ Jackpots - 7-9 Monate Pause vorbei
    # =========================================================================
    print()
    print("=" * 80)
    print("KATEGORIE 2: Hot-Zones mit 2+ Jackpots (Pause vorbei)")
    print("=" * 80)
    print()
    print("Diese Hot-Zones hatten bereits 2+ Jackpots.")
    print("Nach 2x Treffer: 7-9 Monate (210-270 Tage) Pause empfohlen.")
    print()

    cat2 = []
    for hz, data in hotzones.items():
        if data['jackpot_count'] >= 2:
            days_since = data['tage_seit_letztem_jp']
            # Pause vorbei: mindestens 210 Tage (7 Monate)
            if days_since >= 200:
                cat2.append((hz, data, days_since))

    cat2.sort(key=lambda x: -x[2])  # Nach Tagen sortieren (längste Pause zuerst)

    if cat2:
        print(f"{'Tage':>6} {'JP#':>4} {'Zahlen':<35} {'Letzter JP':>12} {'Status':<15}")
        print("-" * 80)

        for hz, data, days in cat2:
            if days >= 270:
                status = "SEHR REIF"
            elif days >= 210:
                status = "REIF"
            else:
                status = "BALD REIF"

            jp_date = data['letzter_jackpot'].strftime('%d.%m.%Y')
            print(f"{days:>6}d {data['jackpot_count']:>4} {str(list(hz)):<35} {jp_date:>12} {status:<15}")

        print()
        print(f"Gefunden: {len(cat2)} Hot-Zones mit 2+ Jackpots und Pause >= 200 Tage")
    else:
        print("Keine Hot-Zones in dieser Kategorie gefunden.")

    # =========================================================================
    # BESTE KANDIDATEN KOMBINIEREN
    # =========================================================================
    print()
    print("=" * 80)
    print("BESTE KANDIDATEN - ZAHLEN EXTRAKTION")
    print("=" * 80)
    print()

    # Sammle alle Zahlen aus den besten Hot-Zones
    best_numbers = Counter()

    # Aus Kategorie 1 (optimal = 48-120 Tage)
    optimal_cat1 = [(hz, data, days) for hz, data, days in cat1 if 48 <= days <= 120]
    for hz, data, days in optimal_cat1[:5]:  # Top 5
        weight = 2 if 48 <= days <= 80 else 1
        for num in hz:
            best_numbers[num] += weight

    # Aus Kategorie 2 (sehr reif = 270+ Tage)
    very_ripe_cat2 = [(hz, data, days) for hz, data, days in cat2 if days >= 250]
    for hz, data, days in very_ripe_cat2[:5]:  # Top 5
        weight = 2 if days >= 300 else 1
        for num in hz:
            best_numbers[num] += weight

    if best_numbers:
        print("Zahlen die in mehreren 'reifen' Hot-Zones vorkommen:")
        print()

        sorted_nums = best_numbers.most_common(20)
        print(f"{'Zahl':>6} {'Punkte':>8} {'Bewertung':<20}")
        print("-" * 40)

        for num, count in sorted_nums:
            if count >= 4:
                bewertung = "★★★ SEHR GUT"
            elif count >= 2:
                bewertung = "★★ GUT"
            else:
                bewertung = "★ MÖGLICH"
            print(f"{num:>6} {count:>8} {bewertung:<20}")

        # Top 7 extrahieren
        top7 = [num for num, _ in sorted_nums[:7]]
        print()
        print(f"Empfohlene Top 7: {sorted(top7)}")
    else:
        print("Nicht genügend Daten für Empfehlung.")

    # =========================================================================
    # DETAILLIERTE JACKPOT-HISTORIE DER BESTEN
    # =========================================================================
    print()
    print("=" * 80)
    print("DETAILLIERTE JACKPOT-HISTORIE")
    print("=" * 80)
    print()

    # Zeige Details für die besten Hot-Zones
    print("KATEGORIE 1 - Besten 3 (1 Jackpot, optimal timing):")
    print()

    for i, (hz, data, days) in enumerate(optimal_cat1[:3], 1):
        print(f"{i}. Hot-Zone: {list(hz)}")
        print(f"   Ermittelt: {data['erste_ermittlung'].strftime('%d.%m.%Y')}")
        print(f"   1. Jackpot: {data['erster_jackpot'].strftime('%d.%m.%Y')} ({days} Tage her)")
        print(f"   Erwartung: 2. Jackpot sollte bald kommen!")
        print()

    print("KATEGORIE 2 - Besten 3 (2+ Jackpots, Pause vorbei):")
    print()

    for i, (hz, data, days) in enumerate(very_ripe_cat2[:3], 1):
        print(f"{i}. Hot-Zone: {list(hz)}")
        print(f"   Jackpots: {data['jackpot_count']}")
        jp_dates = [jp['datum'].strftime('%d.%m.%Y') for jp in sorted(data['jackpots'], key=lambda x: x['datum'])]
        print(f"   Jackpot-Daten: {', '.join(jp_dates)}")
        print(f"   Letzter vor: {days} Tagen ({days/30:.1f} Monate)")
        print(f"   Status: Pause vorbei - wieder spielbar!")
        print()

    # =========================================================================
    # FINALE EMPFEHLUNG
    # =========================================================================
    print()
    print("=" * 80)
    print("FINALE EMPFEHLUNG")
    print("=" * 80)
    print()

    if best_numbers:
        final7 = sorted([num for num, _ in best_numbers.most_common(7)])
        print(f"Empfohlene Zahlen: {final7}")
        print()
        print("Diese Zahlen kommen aus Hot-Zones die:")
        print("  - Bereits 1 Jackpot hatten (2. erwartet)")
        print("  - ODER 2+ Jackpots hatten und die 7-9 Monate Pause vorbei ist")
        print()

        print("7 Kombinationen:")
        for i, exclude in enumerate(final7, 1):
            combo = sorted([n for n in final7 if n != exclude])
            print(f"  Kombi {i}: {combo}")

        print()
        print("Einsatz: 7 x 1 EUR = 7 EUR")

    # =========================================================================
    # MARKDOWN REPORT
    # =========================================================================
    md = f"""# Reife Hot-Zones Analyse

**Analyse-Datum:** {TODAY.strftime('%d.%m.%Y')}
**Letzte Ziehung:** {LAST_DRAW.strftime('%d.%m.%Y')}

---

## Strategie-Grundlage

| Situation | Regel |
|-----------|-------|
| Hot-Zone mit 1 Jackpot | 2. Jackpot erwartet (48-120 Tage optimal) |
| Hot-Zone mit 2+ Jackpots | 7-9 Monate Pause, dann wieder spielbar |

---

## Kategorie 1: Hot-Zones mit 1 Jackpot (2. erwartet)

| Tage seit JP | Zahlen | 1. Jackpot | Status |
|--------------|--------|------------|--------|
"""

    for hz, data, days in cat1[:10]:
        status = "**OPTIMAL**" if 48 <= days <= 120 else "MÖGLICH"
        jp_date = data['erster_jackpot'].strftime('%d.%m.%Y')
        md += f"| {days}d | {list(hz)} | {jp_date} | {status} |\n"

    md += f"""

---

## Kategorie 2: Hot-Zones mit 2+ Jackpots (Pause vorbei)

| Tage seit JP | JP# | Zahlen | Letzter JP | Status |
|--------------|-----|--------|------------|--------|
"""

    for hz, data, days in cat2[:10]:
        status = "**SEHR REIF**" if days >= 270 else "REIF" if days >= 210 else "BALD"
        jp_date = data['letzter_jackpot'].strftime('%d.%m.%Y')
        md += f"| {days}d | {data['jackpot_count']} | {list(hz)} | {jp_date} | {status} |\n"

    md += f"""

---

## Zahlen-Extraktion aus reifen Hot-Zones

| Zahl | Punkte | Bewertung |
|------|--------|-----------|
"""

    for num, count in best_numbers.most_common(15):
        if count >= 4:
            bewertung = "★★★ SEHR GUT"
        elif count >= 2:
            bewertung = "★★ GUT"
        else:
            bewertung = "★ MÖGLICH"
        md += f"| {num} | {count} | {bewertung} |\n"

    if best_numbers:
        final7 = sorted([num for num, _ in best_numbers.most_common(7)])
        md += f"""

---

## Finale Empfehlung

### Empfohlene Zahlen: {final7}

| # | Kombination |
|---|-------------|
"""
        for i, exclude in enumerate(final7, 1):
            combo = sorted([n for n in final7 if n != exclude])
            md += f"| {i} | {combo} |\n"

    md += f"""

---

*Erstellt: {TODAY.strftime('%d.%m.%Y %H:%M')}*
"""

    output_file = BASE_DIR / "results" / "reife_hotzones.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print()
    print(f"Report gespeichert: {output_file}")


if __name__ == "__main__":
    main()
