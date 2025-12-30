#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Oekosystem-Datenaufbereitung
============================

Fuehrt alle deutschen Lotterie-Gewinnquoten auf eine gemeinsame
Zeitachse zusammen fuer Cross-Lotterie-Analyse.

PARADIGMA: Axiom-First
- Keine Pattern-Suche auf Einzelspielen
- Suche nach SYSTEMISCHEN Zusammenhaengen
- Triviale Perioden (7, 30 Tage) existieren NICHT
"""

import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from kenobase.core.parsing import parse_int_mixed_german

# Pfade
BASE_DIR = Path(__file__).parent.parent.parent
KENO_GQ_PATH = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv"
LOTTO_GQ_PATH = BASE_DIR / "Keno_GPTs" / "Lotto6aus49_GQ_2025.csv"
EJ_GQ_PATH = BASE_DIR / "Keno_GPTs" / "EuroJackpot_GQ_2025.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "ecosystem"


def parse_german_date(date_str: str, year: int = 2025) -> datetime | None:
    """Parse deutsches Datum wie 'So, 28.12.' -> datetime.

    Die gescrapten 2025-Dateien enthalten i.d.R. **kein** Jahr; daher ist ``year``
    ein notwendiger Fallback. Wir wenden *keine* heuristische Rueckdatierung an,
    damit Dezember-Ziehungen korrekt in 2025 bleiben.
    """
    match = re.search(r"(\d{1,2})\.(\d{1,2})\.?", str(date_str))
    if not match:
        return None
    try:
        day = int(match.group(1))
        month = int(match.group(2))
        return datetime(int(year), month, day)
    except ValueError:
        return None


def parse_german_number(s: str) -> float:
    """Parse deutsches Zahlenformat: 1.234,56 -> 1234.56"""
    return float(parse_int_mixed_german(s, default=0))
    if pd.isna(s) or s == '':
        return 0.0
    s = str(s).strip()
    # Entferne Euro-Zeichen und Leerzeichen
    s = s.replace('€', '').replace(' ', '').strip()
    # Entferne Tausender-Punkte, ersetze Dezimal-Komma
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0


def load_keno_gq(filepath: Path) -> pd.DataFrame:
    """Lade KENO Gewinnquoten."""
    print(f"Lade KENO GQ von {filepath}...")

    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            datum = parse_german_date(row.get('Datum', ''))
            if datum is None:
                continue

            keno_typ = row.get('Keno-Typ', '')
            if not keno_typ.isdigit():
                continue

            richtige = row.get('Anzahl richtiger Zahlen', '')
            gewinner = row.get('Anzahl der Gewinner', '0')

            # Nur Hauptgewinnklassen (Zahl = Anzahl richtige)
            if richtige.isdigit():
                rows.append({
                    'datum': datum,
                    'spiel': 'KENO',
                    'typ': f'Typ{keno_typ}',
                    'klasse': f'GK{richtige}',
                    'gewinner': parse_german_number(gewinner),
                })

    df = pd.DataFrame(rows)
    print(f"  -> {len(df)} Eintraege geladen")
    return df


def load_lotto_gq(filepath: Path) -> pd.DataFrame:
    """Lade Lotto 6aus49 Gewinnquoten (inkl. Spiel77, Super6)."""
    print(f"Lade Lotto GQ von {filepath}...")

    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            datum = parse_german_date(row.get('Datum', ''))
            if datum is None:
                continue

            spiel = row.get('Spiel', '')
            klasse = row.get('Gewinnklasse', '')
            gewinner = row.get('Anzahl Gewinner', '0')

            # Extrahiere Klassen-Nummer
            klasse_match = re.search(r'^(\d+)', klasse)
            if klasse_match:
                klasse_num = klasse_match.group(1)
            else:
                continue

            rows.append({
                'datum': datum,
                'spiel': spiel.replace(' ', '_'),
                'typ': spiel.replace(' ', '_'),
                'klasse': f'GK{klasse_num}',
                'gewinner': parse_german_number(gewinner),
            })

    df = pd.DataFrame(rows)
    print(f"  -> {len(df)} Eintraege geladen")
    return df


def load_eurojackpot_gq(filepath: Path) -> pd.DataFrame:
    """Lade EuroJackpot Gewinnquoten."""
    print(f"Lade EuroJackpot GQ von {filepath}...")

    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            datum = parse_german_date(row.get('Datum', ''))
            if datum is None:
                continue

            klasse = row.get('Gewinnklasse', '')
            gewinner = row.get('Anzahl Gewinner', '0')

            # Extrahiere Klassen-Nummer
            klasse_match = re.search(r'^(\d+)', klasse)
            if klasse_match:
                klasse_num = klasse_match.group(1)
            else:
                continue

            rows.append({
                'datum': datum,
                'spiel': 'EuroJackpot',
                'typ': 'EuroJackpot',
                'klasse': f'GK{klasse_num}',
                'gewinner': parse_german_number(gewinner),
            })

    df = pd.DataFrame(rows)
    print(f"  -> {len(df)} Eintraege geladen")
    return df


def create_timeline(keno_df: pd.DataFrame, lotto_df: pd.DataFrame, ej_df: pd.DataFrame) -> pd.DataFrame:
    """
    Erstelle gemeinsame Zeitachse fuer alle Spiele.

    Aggregiert pro Tag:
    - Gesamt-Gewinner pro Spiel
    - Top-Gewinnklasse Gewinner (GK1, GK2)
    - Hat Jackpot (GK1 > 0)
    """
    # Kombiniere alle Daten
    all_df = pd.concat([keno_df, lotto_df, ej_df], ignore_index=True)

    # Alle einzigartigen Daten
    all_dates = sorted(all_df['datum'].unique())
    print(f"\nZeitachse: {min(all_dates)} bis {max(all_dates)}")
    print(f"Tage gesamt: {len(all_dates)}")

    # Aggregiere pro Tag und Spiel
    timeline_rows = []

    for date in all_dates:
        day_data = all_df[all_df['datum'] == date]

        row = {'datum': date}

        # KENO Metriken
        keno_day = day_data[day_data['spiel'] == 'KENO']
        if len(keno_day) > 0:
            row['keno_total_winners'] = keno_day['gewinner'].sum()
            keno_gk10 = keno_day[(keno_day['typ'] == 'Typ10') & (keno_day['klasse'] == 'GK10')]
            row['keno_jackpot'] = 1 if len(keno_gk10) > 0 and keno_gk10['gewinner'].sum() > 0 else 0
            row['keno_near_miss'] = keno_day[keno_day['klasse'] == 'GK9']['gewinner'].sum()
        else:
            row['keno_total_winners'] = np.nan
            row['keno_jackpot'] = np.nan
            row['keno_near_miss'] = np.nan

        # Lotto 6aus49 Metriken
        lotto_day = day_data[day_data['spiel'] == 'Lotto_6aus49']
        if len(lotto_day) > 0:
            row['lotto_total_winners'] = lotto_day['gewinner'].sum()
            lotto_gk1 = lotto_day[lotto_day['klasse'] == 'GK1']
            row['lotto_jackpot'] = 1 if len(lotto_gk1) > 0 and lotto_gk1['gewinner'].sum() > 0 else 0
            lotto_gk2 = lotto_day[lotto_day['klasse'] == 'GK2']
            row['lotto_gk2'] = lotto_gk2['gewinner'].sum() if len(lotto_gk2) > 0 else 0
        else:
            row['lotto_total_winners'] = np.nan
            row['lotto_jackpot'] = np.nan
            row['lotto_gk2'] = np.nan

        # EuroJackpot Metriken (separat - nicht Teil des Oekosystems!)
        ej_day = day_data[day_data['spiel'] == 'EuroJackpot']
        if len(ej_day) > 0:
            row['ej_total_winners'] = ej_day['gewinner'].sum()
            ej_gk1 = ej_day[ej_day['klasse'] == 'GK1']
            row['ej_jackpot'] = 1 if len(ej_gk1) > 0 and ej_gk1['gewinner'].sum() > 0 else 0
        else:
            row['ej_total_winners'] = np.nan
            row['ej_jackpot'] = np.nan

        timeline_rows.append(row)

    timeline_df = pd.DataFrame(timeline_rows)
    timeline_df = timeline_df.sort_values('datum').reset_index(drop=True)

    return timeline_df


def create_ecosystem_signal(timeline_df: pd.DataFrame) -> pd.DataFrame:
    """
    Erstelle Oekosystem-Signal (nur deutsche Lotterien, NICHT EuroJackpot).

    Signale:
    - ecosystem_winners: Summe aller Gewinner (KENO + Lotto)
    - ecosystem_jackpots: Anzahl Jackpots am Tag
    - ecosystem_pressure: Normalisierter "Druck" auf das System
    """
    df = timeline_df.copy()

    # Ecosystem = KENO + Lotto (NICHT EuroJackpot!)
    df['ecosystem_winners'] = df['keno_total_winners'].fillna(0) + df['lotto_total_winners'].fillna(0)
    df['ecosystem_jackpots'] = df['keno_jackpot'].fillna(0) + df['lotto_jackpot'].fillna(0)

    # Normalisierter Druck (z-Score)
    mean_winners = df['ecosystem_winners'].mean()
    std_winners = df['ecosystem_winners'].std()
    if std_winners > 0:
        df['ecosystem_pressure'] = (df['ecosystem_winners'] - mean_winners) / std_winners
    else:
        df['ecosystem_pressure'] = 0

    # Kumulierte Gewinner seit letztem Jackpot
    cumsum = 0
    cumsum_list = []
    for _, row in df.iterrows():
        if row['ecosystem_jackpots'] > 0:
            cumsum = 0
        else:
            cumsum += row['ecosystem_winners'] if not np.isnan(row['ecosystem_winners']) else 0
        cumsum_list.append(cumsum)
    df['winners_since_jackpot'] = cumsum_list

    return df


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("OEKOSYSTEM-DATENAUFBEREITUNG")
    print("=" * 60)

    # Output-Verzeichnis erstellen
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Daten laden
    keno_df = load_keno_gq(KENO_GQ_PATH)
    lotto_df = load_lotto_gq(LOTTO_GQ_PATH)
    ej_df = load_eurojackpot_gq(EJ_GQ_PATH)

    # Timeline erstellen
    print("\nErstelle Zeitachse...")
    timeline_df = create_timeline(keno_df, lotto_df, ej_df)

    # Oekosystem-Signal
    print("Berechne Oekosystem-Signal...")
    ecosystem_df = create_ecosystem_signal(timeline_df)

    # Speichern
    timeline_path = OUTPUT_DIR / "timeline_2025.csv"
    ecosystem_df.to_csv(timeline_path, index=False)
    print(f"\nGespeichert: {timeline_path}")

    # Statistiken
    print("\n" + "=" * 60)
    print("STATISTIKEN")
    print("=" * 60)

    print(f"\nZeitraum: {ecosystem_df['datum'].min()} bis {ecosystem_df['datum'].max()}")
    print(f"Tage: {len(ecosystem_df)}")

    print("\n--- KENO ---")
    keno_days = ecosystem_df['keno_total_winners'].notna().sum()
    keno_jackpots = ecosystem_df['keno_jackpot'].sum()
    print(f"Tage mit Daten: {keno_days}")
    print(f"Jackpots: {int(keno_jackpots)}")

    print("\n--- Lotto 6aus49 ---")
    lotto_days = ecosystem_df['lotto_total_winners'].notna().sum()
    lotto_jackpots = ecosystem_df['lotto_jackpot'].sum()
    print(f"Tage mit Daten: {lotto_days}")
    print(f"Jackpots: {int(lotto_jackpots)}")

    print("\n--- EuroJackpot (SEPARAT) ---")
    ej_days = ecosystem_df['ej_total_winners'].notna().sum()
    ej_jackpots = ecosystem_df['ej_jackpot'].sum()
    print(f"Tage mit Daten: {ej_days}")
    print(f"Jackpots: {int(ej_jackpots)}")

    print("\n--- Oekosystem (KENO + Lotto) ---")
    eco_jackpots = ecosystem_df['ecosystem_jackpots'].sum()
    print(f"Gesamt-Jackpots: {int(eco_jackpots)}")
    print(f"Durchschnitt Gewinner/Tag: {ecosystem_df['ecosystem_winners'].mean():,.0f}")
    print(f"Max Gewinner/Tag: {ecosystem_df['ecosystem_winners'].max():,.0f}")

    return ecosystem_df


if __name__ == '__main__':
    main()
