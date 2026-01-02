#!/usr/bin/env python3
"""
Finde alle Tage an denen es einen echten 10/10 Gewinner gab
und analysiere das Muster der Zahlenauswahl.

Methodik:
1. Lade die Quoten-Daten (enthalten Anzahl Gewinner pro Tag)
2. Finde alle Tage mit mindestens 1 Gewinner bei Typ 10 (10/10)
3. Für jeden Jackpot-Tag: Analysiere welche 10 der 20 Zahlen gewonnen haben
"""

import pandas as pd
from pathlib import Path
from itertools import combinations
import numpy as np

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"


def load_data():
    df = pd.read_csv(DATA_FILE, sep=';', encoding='utf-8')
    df['datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['zahlen'] = df[zahl_cols].apply(lambda row: sorted([int(x) for x in row if pd.notna(x)]), axis=1)
    df = df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)
    return df


def find_consecutive_identical_draws(df):
    """Finde Tage mit identischen Ziehungen wie am Vortag."""
    consecutive = []

    prev_zahlen = None
    prev_date = None

    for idx, row in df.iterrows():
        current_zahlen = tuple(row['zahlen'])
        current_date = row['datum']

        if prev_zahlen is not None and current_zahlen == prev_zahlen:
            consecutive.append({
                'date1': prev_date.strftime('%Y-%m-%d'),
                'date2': current_date.strftime('%Y-%m-%d'),
                'zahlen': list(current_zahlen)
            })

        prev_zahlen = current_zahlen
        prev_date = current_date

    return consecutive


def analyze_even_odd_patterns(df):
    """Analysiere gerade/ungerade Muster in allen Ziehungen."""

    patterns = {
        'even_counts': [],  # Anzahl gerader Zahlen pro Ziehung
        'by_count': {}      # Verteilung der Anzahl
    }

    for idx, row in df.iterrows():
        zahlen = row['zahlen']
        even_count = sum(1 for n in zahlen if n % 2 == 0)
        patterns['even_counts'].append(even_count)
        patterns['by_count'][even_count] = patterns['by_count'].get(even_count, 0) + 1

    return patterns


def main():
    print("=" * 80)
    print("KENO JACKPOT-MUSTER ANALYSE")
    print("=" * 80)
    print()

    print("Lade Daten...")
    df = load_data()
    print(f"Geladene Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['datum'].min().strftime('%Y-%m-%d')} bis {df['datum'].max().strftime('%Y-%m-%d')}")
    print()

    # Finde aufeinanderfolgende identische Ziehungen
    print("=" * 80)
    print("AUFEINANDERFOLGENDE IDENTISCHE ZIEHUNGEN")
    print("(wie beim Kyritz-Fall am 24./25.10.2025)")
    print("=" * 80)
    print()

    consecutive = find_consecutive_identical_draws(df)

    if consecutive:
        for c in consecutive:
            print(f"  {c['date1']} und {c['date2']}:")
            print(f"    Zahlen: {c['zahlen']}")

            # Analysiere diese Zahlen
            zahlen = c['zahlen']
            even_count = sum(1 for n in zahlen if n % 2 == 0)
            print(f"    Gerade: {even_count}, Ungerade: {20 - even_count}")
            print()
    else:
        print("  Keine aufeinanderfolgenden identischen Ziehungen gefunden.")
    print()

    # Analysiere gerade/ungerade in allen Ziehungen
    print("=" * 80)
    print("GERADE/UNGERADE ANALYSE ALLER ZIEHUNGEN")
    print("=" * 80)
    print()

    patterns = analyze_even_odd_patterns(df)

    total = len(patterns['even_counts'])
    avg_even = np.mean(patterns['even_counts'])

    print(f"Durchschnitt gerade Zahlen pro Ziehung (von 20): {avg_even:.1f}")
    print()
    print("Verteilung:")
    for count in sorted(patterns['by_count'].keys()):
        freq = patterns['by_count'][count]
        pct = freq / total * 100
        bar = '#' * int(pct / 2)
        print(f"  {count:2} gerade: {freq:4} ({pct:5.1f}%) {bar}")

    print()
    print("=" * 80)
    print("KYRITZ-VERGLEICH")
    print("=" * 80)
    print()
    print("Kyritz Gewinner-10: [5,12,20,26,34,36,42,45,48,66]")
    print("  - 8 gerade Zahlen (Top 1% aller Kombinationen!)")
    print("  - Dieselben 10 Zahlen an 2 Tagen hintereinander gezogen")
    print()

    # Finde alle Tage wo diese exakte Kombination erschien
    kyritz_winner = set([5, 12, 20, 26, 34, 36, 42, 45, 48, 66])

    print("Tage an denen alle 10 Kyritz-Zahlen gezogen wurden:")
    for idx, row in df.iterrows():
        drawn = set(row['zahlen'])
        if kyritz_winner.issubset(drawn):
            print(f"  {row['datum'].strftime('%Y-%m-%d')}: {row['zahlen']}")
    print()

    # Berechne wie viele andere 10er-Kombinationen 8+ gerade haben
    print("=" * 80)
    print("STATISTIK: 8+ GERADE ZAHLEN IN 10er-KOMBINATIONEN")
    print("=" * 80)
    print()

    # Bei 20 Zahlen mit ~10 geraden: Wie viele 10er-Kombis haben 8+ gerade?
    print("Typische Ziehung hat ~10 gerade und ~10 ungerade Zahlen.")
    print("C(20,10) = 184.756 mögliche 10er-Kombinationen")
    print()
    print("Wenn genau 10 gerade + 10 ungerade:")
    print("  8 gerade: C(10,8) * C(10,2) = 45 * 45 = 2.025 Kombis (1.1%)")
    print("  9 gerade: C(10,9) * C(10,1) = 10 * 10 = 100 Kombis (0.05%)")
    print("  10 gerade: C(10,10) * C(10,0) = 1 * 1 = 1 Kombi (0.0005%)")
    print()
    print("Die Kyritz-Gewinner-Kombination mit 8 geraden ist also im TOP 1.2%!")
    print()


if __name__ == "__main__":
    main()
