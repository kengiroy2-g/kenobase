#!/usr/bin/env python
"""
Berechnet den aktuellen Spielstatus basierend auf der Ultimativen Typ-6 Strategie.
Prueft alle Bedingungen und gibt eine Empfehlung aus.
"""

import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent
KENO_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
GQ_FILE_1 = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
GQ_FILE_2 = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv"


def load_keno_data():
    """Laedt KENO-Ziehungsdaten."""
    df = pd.read_csv(KENO_FILE, sep=';', encoding='utf-8')
    df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['zahlen'] = df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
    df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)
    return df


def load_gq_data():
    """Laedt Gewinnquoten-Daten."""
    dfs = []
    for f in [GQ_FILE_1, GQ_FILE_2]:
        if f.exists():
            df = pd.read_csv(f, sep=',', encoding='utf-8-sig')
            dfs.append(df)
    if not dfs:
        return None
    df = pd.concat(dfs, ignore_index=True)
    df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    # Rename columns for easier access
    df = df.rename(columns={
        'Keno-Typ': 'Typ',
        'Anzahl richtiger Zahlen': 'GK',
        'Anzahl der Gewinner': 'Gewinner',
        '1 Euro Gewinn': 'Gewinn'
    })
    # Parse Gewinn (remove Euro sign and convert)
    def parse_gewinn(s):
        try:
            # Remove any non-numeric chars except comma and dot
            s = str(s).replace('€', '').replace('\xa0', '').strip()
            s = s.replace('.', '').replace(',', '.')
            return float(s) if s else 0
        except:
            return 0

    df['Gewinn_num'] = df['Gewinn'].apply(parse_gewinn)
    df['Gewinner'] = pd.to_numeric(df['Gewinner'], errors='coerce').fillna(0)
    df['Auszahlung'] = df['Gewinn_num'] * df['Gewinner']
    return df.dropna(subset=['datum'])


def get_hot_zone(df, window=50):
    """Berechnet aktuelle Hot-Zone (Top-7)."""
    hist = df.tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return [n for n, _ in freq.most_common(7)]


def find_last_jackpot_10_10(df_gq):
    """Findet letzten 10/10 Jackpot (mit Gewinner)."""
    if df_gq is None:
        return None

    # 10/10 = Typ 10 mit 10 richtigen UND mindestens 1 Gewinner
    jackpots = df_gq[(df_gq['Typ'] == 10) & (df_gq['GK'] == 10) & (df_gq['Gewinner'] > 0)]
    if jackpots.empty:
        return None
    return jackpots['datum'].max()


def get_last_high_payout_day(df_gq, threshold=130000):
    """Findet letzten Tag mit hoher Auszahlung."""
    if df_gq is None:
        return None

    daily = df_gq.groupby('datum')['Auszahlung'].sum().reset_index()
    high_days = daily[daily['Auszahlung'] > threshold]
    if high_days.empty:
        return None
    return high_days['datum'].max()


def get_cycle_day(today):
    """Berechnet aktuellen Tag im 28-Tage-Zyklus."""
    # Annahme: Zyklus beginnt am 1. jedes Monats
    return today.day


def main():
    print("=" * 70)
    print("TYP-6 SPIELSTATUS - Ultimative Strategie Check")
    print("=" * 70)
    print()

    today = datetime.now()
    print(f"Datum: {today.strftime('%d.%m.%Y')}")
    print()

    # Daten laden
    df = load_keno_data()
    df_gq = load_gq_data()

    last_draw = df['datum'].max()
    print(f"Letzte Ziehung: {last_draw.strftime('%d.%m.%Y')}")
    print()

    # =========================================================================
    # CHECK 1: Letzter 10/10 Jackpot
    # =========================================================================
    print("-" * 70)
    print("CHECK 1: 10/10 Jackpot (30 Tage Abstand erforderlich)")
    print("-" * 70)

    last_jp = find_last_jackpot_10_10(df_gq)
    if last_jp:
        days_since_jp = (today - last_jp).days
        check1_ok = days_since_jp >= 30
        status1 = "OK" if check1_ok else "WARTEN"
        print(f"  Letzter 10/10 Jackpot: {last_jp.strftime('%d.%m.%Y')}")
        print(f"  Tage seit Jackpot: {days_since_jp}")
        print(f"  Status: {status1}")
        if not check1_ok:
            print(f"  -> Noch {30 - days_since_jp} Tage warten!")
    else:
        check1_ok = True
        print("  Keine 10/10 Jackpot-Daten verfuegbar")
        print("  Status: OK (Annahme)")
    print()

    # =========================================================================
    # CHECK 2: Hohe Tagesauszahlung
    # =========================================================================
    print("-" * 70)
    print("CHECK 2: Hohe Tagesauszahlung (>130k = 7-14 Tage Pause)")
    print("-" * 70)

    last_high = get_last_high_payout_day(df_gq)
    if last_high:
        days_since_high = (today - last_high).days
        check2_ok = days_since_high >= 7
        status2 = "OK" if check2_ok else "WARTEN"
        print(f"  Letzte hohe Auszahlung: {last_high.strftime('%d.%m.%Y')}")
        print(f"  Tage seit hoher Auszahlung: {days_since_high}")
        print(f"  Status: {status2}")
        if not check2_ok:
            print(f"  -> Noch {7 - days_since_high} Tage warten!")
    else:
        check2_ok = True
        print("  Keine Auszahlungsdaten verfuegbar")
        print("  Status: OK (Annahme)")
    print()

    # =========================================================================
    # CHECK 3: Zyklus-Tag (FRUEH vs SPAET)
    # =========================================================================
    print("-" * 70)
    print("CHECK 3: 28-Tage-Zyklus (Tag 1-14 = FRUEH = beste ROI)")
    print("-" * 70)

    cycle_day = get_cycle_day(today)
    is_frueh = cycle_day <= 14
    check3_ok = is_frueh
    status3 = "FRUEH (optimal)" if is_frueh else "SPAET (suboptimal)"
    print(f"  Aktueller Zyklus-Tag: {cycle_day}")
    print(f"  Phase: {status3}")
    if not is_frueh:
        # Calculate days until next month (new cycle)
        import calendar
        _, last_day_of_month = calendar.monthrange(today.year, today.month)
        days_to_new_month = last_day_of_month - cycle_day + 1
        print(f"  -> In {days_to_new_month} Tagen beginnt FRUEH-Phase (naechster Monat)")
    print()

    # =========================================================================
    # AKTUELLE HOT-ZONE
    # =========================================================================
    print("-" * 70)
    print("AKTUELLE HOT-ZONE (W50)")
    print("-" * 70)

    hot_zone = get_hot_zone(df, 50)
    print(f"  Top-7 Zahlen: {hot_zone}")
    print()

    # Hot-Zone W20 zum Vergleich
    hot_zone_w20 = get_hot_zone(df, 20)
    print(f"  Hot-Zone W20: {hot_zone_w20}")
    print()

    # =========================================================================
    # GESAMTSTATUS
    # =========================================================================
    print("=" * 70)
    print("GESAMTSTATUS")
    print("=" * 70)
    print()

    all_ok = check1_ok and check2_ok and check3_ok

    if all_ok:
        print("  *** SPIELEN EMPFOHLEN ***")
        print()
        print("  Empfohlene Zahlen (Hot-Zone W50):")
        print(f"    {hot_zone}")
        print()
        print("  7 Kombinationen (je 6 Zahlen):")
        for i, exclude in enumerate(hot_zone):
            combo = [n for n in hot_zone if n != exclude]
            print(f"    Kombi {i+1}: {combo}")
        print()
        print("  Einsatz: 7 x 1 EUR = 7 EUR")
    else:
        print("  *** NICHT SPIELEN - WARTEN ***")
        print()
        print("  Gruende:")
        if not check1_ok:
            print(f"    - 10/10 Jackpot vor {days_since_jp} Tagen (mind. 30 erforderlich)")
        if not check2_ok:
            print(f"    - Hohe Auszahlung vor {days_since_high} Tagen (mind. 7 erforderlich)")
        if not check3_ok:
            print(f"    - SPAET-Phase (Tag {cycle_day}, optimal: Tag 1-14)")

    print()
    print("=" * 70)

    # Markdown-Report
    md = f"""# Typ-6 Spielstatus

**Datum:** {today.strftime('%d.%m.%Y')}
**Letzte Ziehung:** {last_draw.strftime('%d.%m.%Y')}

---

## Checkliste

| Check | Status | Details |
|-------|--------|---------|
| 10/10 Jackpot (30 Tage) | {'OK' if check1_ok else 'WARTEN'} | {f'{days_since_jp} Tage seit letztem JP' if last_jp else 'Keine Daten'} |
| Hohe Auszahlung (7 Tage) | {'OK' if check2_ok else 'WARTEN'} | {f'{days_since_high} Tage seit hoher AZ' if last_high else 'Keine Daten'} |
| Zyklus-Phase (FRUEH) | {'OK' if check3_ok else 'WARTEN'} | Tag {cycle_day} ({status3}) |

---

## Empfehlung

**{'SPIELEN' if all_ok else 'NICHT SPIELEN'}**

"""

    if all_ok:
        md += f"""### Hot-Zone W50

{hot_zone}

### 7 Kombinationen

| # | Zahlen |
|---|--------|
"""
        for i, exclude in enumerate(hot_zone):
            combo = [n for n in hot_zone if n != exclude]
            md += f"| {i+1} | {combo} |\n"

        md += "\n**Einsatz:** 7 EUR\n"
    else:
        md += """### Warte-Gruende

"""
        if not check1_ok:
            md += f"- 10/10 Jackpot vor {days_since_jp} Tagen (mind. 30 erforderlich)\n"
        if not check2_ok:
            md += f"- Hohe Auszahlung vor {days_since_high} Tagen (mind. 7 erforderlich)\n"
        if not check3_ok:
            md += f"- SPAET-Phase (Tag {cycle_day}, optimal: Tag 1-14)\n"

    md += f"""
---

*Erstellt: {today.strftime('%d.%m.%Y %H:%M')}*
"""

    output_file = BASE_DIR / "results" / "spielstatus_aktuell.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"Report gespeichert: {output_file}")


if __name__ == "__main__":
    main()
