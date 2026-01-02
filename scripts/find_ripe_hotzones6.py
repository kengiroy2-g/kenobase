#!/usr/bin/env python
"""
Findet "reife" Hot-Zones für HZ6 (Top-6 Zahlen)

Angepasste Regeln für HZ6:
- Keine Wartezeit nötig (0 Tage optimal vs 48 für HZ7)
- Längere Zeit bis Jackpot erwartet (Median 352 Tage)
- Weniger Jackpots insgesamt, aber höhere Effizienz pro EUR
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


def get_hot_zone(df, end_date, window=50, top_n=6):
    """Top-N häufigste Zahlen."""
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return tuple(sorted([n for n, _ in freq.most_common(top_n)]))


def find_jackpots_hz6(df, hz_numbers, start_date, end_date):
    """
    Findet Typ-6 Jackpots für HZ6.
    Bei HZ6 müssen alle 6 Zahlen treffen (nur 1 Kombination).
    """
    numbers = sorted(hz_numbers)[:6]
    if len(numbers) < 6:
        return []

    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpots = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        if len(drawn & set(numbers)) == 6:
            jackpots.append({
                'datum': row['datum'],
                'gruppe': tuple(numbers),
                'gezogen': tuple(sorted(drawn))
            })
    return jackpots


def analyze_all_hotzones6():
    """Analysiert alle historischen HZ6 und ihre Jackpot-Historie."""
    hotzones = {}

    test_dates = pd.date_range(start='2022-04-01', end=LAST_DRAW - timedelta(days=30), freq='MS')

    for ermittlung_date in test_dates:
        hz = get_hot_zone(df, ermittlung_date, 50, 6)

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
        jackpots = find_jackpots_hz6(
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

        # Berechne Tage seit letzter Ermittlung
        data['tage_seit_ermittlung'] = (LAST_DRAW - data['letzte_ermittlung']).days

    return hotzones


def main():
    print("=" * 80)
    print("REIFE HOT-ZONES FÜR HZ6 (Top-6 Zahlen)")
    print("=" * 80)
    print()
    print(f"Letzte Ziehung: {LAST_DRAW.strftime('%d.%m.%Y')}")
    print(f"Analyse-Datum: {TODAY.strftime('%d.%m.%Y')}")
    print()

    print("Analysiere alle historischen HZ6...")
    hotzones = analyze_all_hotzones6()

    print(f"Gefunden: {len(hotzones)} unique HZ6")
    print()

    # Statistiken
    jp_counts = [data['jackpot_count'] for data in hotzones.values()]
    with_jp = sum(1 for c in jp_counts if c > 0)
    without_jp = sum(1 for c in jp_counts if c == 0)

    print(f"HZ6 mit Jackpot: {with_jp}")
    print(f"HZ6 ohne Jackpot: {without_jp}")
    print()

    # =========================================================================
    # KATEGORIE 1: HZ6 mit genau 1 Jackpot (2. Jackpot erwartet)
    # =========================================================================
    print("=" * 80)
    print("KATEGORIE 1: HZ6 mit genau 1 Jackpot (2. Jackpot erwartet)")
    print("=" * 80)
    print()
    print("Bei HZ6 ist die Zeit bis zum 2. Jackpot länger als bei HZ7.")
    print("Median HZ6: 444 Tage zwischen Jackpots")
    print()

    cat1 = []
    for hz, data in hotzones.items():
        if data['jackpot_count'] == 1:
            days_since = data['tage_seit_letztem_jp']
            # Für HZ6: Längeres Fenster (100-500 Tage)
            if 60 <= days_since <= 500:
                cat1.append((hz, data, days_since))

    cat1.sort(key=lambda x: x[2])

    if cat1:
        print(f"{'Tage':>6} {'Zahlen':<30} {'1. Jackpot':>12} {'Status':<15}")
        print("-" * 70)

        for hz, data, days in cat1:
            if 200 <= days <= 400:
                status = "OPTIMAL"
            elif 100 <= days < 200:
                status = "FRÜH"
            else:
                status = "SPÄT"

            jp_date = data['erster_jackpot'].strftime('%d.%m.%Y')
            print(f"{days:>6}d {str(list(hz)):<30} {jp_date:>12} {status:<15}")

        print()
        print(f"Gefunden: {len(cat1)} HZ6 mit 1 Jackpot")
    else:
        print("Keine HZ6 in dieser Kategorie gefunden.")

    # =========================================================================
    # KATEGORIE 2: HZ6 mit 2+ Jackpots (Pause vorbei)
    # =========================================================================
    print()
    print("=" * 80)
    print("KATEGORIE 2: HZ6 mit 2+ Jackpots (Pause vorbei)")
    print("=" * 80)
    print()

    cat2 = []
    for hz, data in hotzones.items():
        if data['jackpot_count'] >= 2:
            days_since = data['tage_seit_letztem_jp']
            if days_since >= 200:
                cat2.append((hz, data, days_since))

    cat2.sort(key=lambda x: -x[2])

    if cat2:
        print(f"{'Tage':>6} {'JP#':>4} {'Zahlen':<30} {'Letzter JP':>12} {'Status':<15}")
        print("-" * 75)

        for hz, data, days in cat2:
            if days >= 350:
                status = "SEHR REIF"
            elif days >= 270:
                status = "REIF"
            else:
                status = "BALD REIF"

            jp_date = data['letzter_jackpot'].strftime('%d.%m.%Y')
            print(f"{days:>6}d {data['jackpot_count']:>4} {str(list(hz)):<30} {jp_date:>12} {status:<15}")

        print()
        print(f"Gefunden: {len(cat2)} HZ6 mit 2+ Jackpots")
    else:
        print("Keine HZ6 in dieser Kategorie gefunden.")

    # =========================================================================
    # KATEGORIE 3: Aktive HZ6 ohne Jackpot (lange aktiv = "überfällig")
    # =========================================================================
    print()
    print("=" * 80)
    print("KATEGORIE 3: Lange aktive HZ6 ohne Jackpot (überfällig?)")
    print("=" * 80)
    print()
    print("Diese HZ6 waren lange aktiv aber hatten noch keinen Jackpot.")
    print("(Median bis Jackpot: 352 Tage)")
    print()

    cat3 = []
    for hz, data in hotzones.items():
        if data['jackpot_count'] == 0:
            n_ermittlungen = len(data['ermittlungen'])
            tage_aktiv = (data['letzte_ermittlung'] - data['erste_ermittlung']).days
            if tage_aktiv >= 180 or n_ermittlungen >= 6:
                cat3.append((hz, data, tage_aktiv, n_ermittlungen))

    cat3.sort(key=lambda x: -x[2])

    if cat3:
        print(f"{'Tage aktiv':>12} {'#Erm':>6} {'Zahlen':<30} {'Status':<15}")
        print("-" * 70)

        for hz, data, tage_aktiv, n_erm in cat3[:15]:
            if tage_aktiv >= 300:
                status = "SEHR ÜBERFÄLLIG"
            elif tage_aktiv >= 200:
                status = "ÜBERFÄLLIG"
            else:
                status = "REIFEND"

            print(f"{tage_aktiv:>10}d {n_erm:>6} {str(list(hz)):<30} {status:<15}")

        print()
        print(f"Gefunden: {len(cat3)} lange aktive HZ6 ohne Jackpot")
    else:
        print("Keine HZ6 in dieser Kategorie gefunden.")

    # =========================================================================
    # ZAHLEN-EXTRAKTION
    # =========================================================================
    print()
    print("=" * 80)
    print("ZAHLEN-EXTRAKTION AUS REIFEN HZ6")
    print("=" * 80)
    print()

    best_numbers = Counter()

    # Aus Kategorie 1 (1 Jackpot, optimal timing)
    for hz, data, days in cat1:
        weight = 3 if 200 <= days <= 400 else 1
        for num in hz:
            best_numbers[num] += weight

    # Aus Kategorie 2 (2+ Jackpots, sehr reif)
    for hz, data, days in cat2:
        weight = 3 if days >= 350 else 2
        for num in hz:
            best_numbers[num] += weight

    # Aus Kategorie 3 (überfällig)
    for hz, data, tage_aktiv, n_erm in cat3[:5]:
        weight = 2 if tage_aktiv >= 300 else 1
        for num in hz:
            best_numbers[num] += weight

    if best_numbers:
        print("Zahlen aus reifen HZ6:")
        print()

        sorted_nums = best_numbers.most_common(15)
        print(f"{'Zahl':>6} {'Punkte':>8} {'Bewertung':<20}")
        print("-" * 40)

        for num, count in sorted_nums:
            if count >= 5:
                bewertung = "★★★ SEHR GUT"
            elif count >= 3:
                bewertung = "★★ GUT"
            else:
                bewertung = "★ MÖGLICH"
            print(f"{num:>6} {count:>8} {bewertung:<20}")

        top6 = sorted([num for num, _ in sorted_nums[:6]])
        print()
        print(f"Empfohlene Top 6: {top6}")
    else:
        print("Nicht genügend Daten.")

    # =========================================================================
    # AKTUELLE HZ6
    # =========================================================================
    print()
    print("=" * 80)
    print("AKTUELLE HOT-ZONE 6")
    print("=" * 80)
    print()

    current_hz6_w50 = get_hot_zone(df, LAST_DRAW, 50, 6)
    current_hz6_w20 = get_hot_zone(df, LAST_DRAW, 20, 6)

    print(f"HZ6 W50: {list(current_hz6_w50)}")
    print(f"HZ6 W20: {list(current_hz6_w20)}")
    print()

    # Prüfe ob aktuelle HZ6 in einer Kategorie ist
    current_status = "UNBEKANNT"
    for hz, data, days in cat1:
        if hz == current_hz6_w50:
            current_status = f"1 Jackpot vor {days} Tagen"
            break
    for hz, data, days in cat2:
        if hz == current_hz6_w50:
            current_status = f"{data['jackpot_count']} Jackpots, letzter vor {days} Tagen"
            break

    print(f"Status aktuelle HZ6: {current_status}")

    # =========================================================================
    # FINALE EMPFEHLUNG HZ6
    # =========================================================================
    print()
    print("=" * 80)
    print("FINALE EMPFEHLUNG FÜR HZ6")
    print("=" * 80)
    print()

    if best_numbers:
        final6 = sorted([num for num, _ in best_numbers.most_common(6)])
        print(f"Empfohlene Zahlen: {final6}")
        print()
        print("Strategie HZ6:")
        print("  - Kosten: 1 EUR pro Ziehung (nur 1 Kombination)")
        print("  - KEINE Wartezeit nötig (sofort spielen)")
        print("  - Längere Zeit bis Jackpot erwartet (~352 Tage Median)")
        print("  - Effizienter pro EUR als HZ7 (5.00 vs 3.43 JP/EUR)")
        print()
        print(f"Deine Kombination: {final6}")
        print("Einsatz: 1 EUR")
    else:
        print("Verwende aktuelle Hot-Zone:")
        print(f"  {list(current_hz6_w50)}")

    # =========================================================================
    # VERGLEICH MIT HZ7
    # =========================================================================
    print()
    print("=" * 80)
    print("VERGLEICH: HZ6 vs HZ7 EMPFEHLUNG")
    print("=" * 80)
    print()

    current_hz7_w50 = get_hot_zone(df, LAST_DRAW, 50, 7)

    print(f"HZ6 Empfehlung: {final6 if best_numbers else list(current_hz6_w50)}")
    print(f"HZ7 Empfehlung: {list(current_hz7_w50)}")
    print()
    print("Kosten-Vergleich pro Monat (30 Ziehungen):")
    print(f"  HZ6: 30 x 1 EUR = 30 EUR")
    print(f"  HZ7: 30 x 7 EUR = 210 EUR")
    print()
    print("Erwartete Jackpots pro Jahr:")
    print(f"  HZ6: ~5 Jackpots = 2.500 EUR")
    print(f"  HZ7: ~24 Jackpots = 12.000 EUR")

    # =========================================================================
    # MARKDOWN REPORT
    # =========================================================================
    md = f"""# Reife Hot-Zones für HZ6 (Top-6)

**Analyse-Datum:** {TODAY.strftime('%d.%m.%Y')}
**Letzte Ziehung:** {LAST_DRAW.strftime('%d.%m.%Y')}

---

## Strategie-Unterschiede: HZ6 vs HZ7

| Merkmal | HZ6 | HZ7 |
|---------|-----|-----|
| Kombinationen | 1 | 7 |
| Kosten/Ziehung | 1 EUR | 7 EUR |
| Optimale Wartezeit | **0 Tage** | 48 Tage |
| Median bis Jackpot | 352 Tage | 386 Tage |
| Effizienz (JP/EUR) | **5.00** | 3.43 |

---

## Kategorie 1: HZ6 mit 1 Jackpot

| Tage seit JP | Zahlen | 1. Jackpot | Status |
|--------------|--------|------------|--------|
"""

    for hz, data, days in cat1[:10]:
        status = "**OPTIMAL**" if 200 <= days <= 400 else "FRÜH" if days < 200 else "SPÄT"
        jp_date = data['erster_jackpot'].strftime('%d.%m.%Y')
        md += f"| {days}d | {list(hz)} | {jp_date} | {status} |\n"

    md += f"""

---

## Kategorie 2: HZ6 mit 2+ Jackpots

| Tage seit JP | JP# | Zahlen | Status |
|--------------|-----|--------|--------|
"""

    for hz, data, days in cat2[:10]:
        status = "**SEHR REIF**" if days >= 350 else "REIF"
        md += f"| {days}d | {data['jackpot_count']} | {list(hz)} | {status} |\n"

    md += f"""

---

## Kategorie 3: Überfällige HZ6 (kein Jackpot)

| Tage aktiv | Ermittlungen | Zahlen | Status |
|------------|--------------|--------|--------|
"""

    for hz, data, tage_aktiv, n_erm in cat3[:10]:
        status = "**ÜBERFÄLLIG**" if tage_aktiv >= 200 else "REIFEND"
        md += f"| {tage_aktiv}d | {n_erm} | {list(hz)} | {status} |\n"

    md += f"""

---

## Zahlen-Extraktion

| Zahl | Punkte | Bewertung |
|------|--------|-----------|
"""

    for num, count in best_numbers.most_common(12):
        if count >= 5:
            bewertung = "★★★ SEHR GUT"
        elif count >= 3:
            bewertung = "★★ GUT"
        else:
            bewertung = "★"
        md += f"| {num} | {count} | {bewertung} |\n"

    if best_numbers:
        final6 = sorted([num for num, _ in best_numbers.most_common(6)])
        md += f"""

---

## Finale Empfehlung HZ6

### Zahlen: {final6}

**Kosten:** 1 EUR pro Ziehung

**Strategie-Regeln für HZ6:**
1. KEINE Wartezeit - sofort spielen
2. Längere Geduld nötig (~352 Tage Median)
3. Effizienter pro EUR als HZ7

---

## Vergleich: HZ6 vs HZ7

| Merkmal | HZ6 | HZ7 |
|---------|-----|-----|
| Empfohlene Zahlen | {final6} | {list(current_hz7_w50)} |
| Kosten/Monat | 30 EUR | 210 EUR |
| Erwartete JP/Jahr | ~5 | ~24 |
| Erwarteter Gewinn/Jahr | 2.500 EUR | 12.000 EUR |
"""

    md += f"""

---

*Erstellt: {TODAY.strftime('%d.%m.%Y %H:%M')}*
"""

    output_file = BASE_DIR / "results" / "reife_hotzones6.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print()
    print(f"Report gespeichert: {output_file}")


if __name__ == "__main__":
    main()
