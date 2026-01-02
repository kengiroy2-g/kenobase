"""
Validierung der Hypothese: Differenz-Summe mod 7 = 3 bei KENO Jackpot-Gewinnern

HYPOTHESE: Bei KENO Jackpot-Gewinnern (Typ 10, 10 Richtige) ist die
"Differenz-Summe mod 7" der gewaehlten 10 Zahlen immer = 3

DEFINITION:
- Differenz-Summe = Summe aller paarweisen Differenzen zwischen den 10 Zahlen
- Bei 10 Zahlen gibt es C(10,2) = 45 Paare
- diff_sum = sum(|z_i - z_j|) fuer alle i < j
- Dann: diff_sum mod 7

Autor: Claude Code
Datum: 2025-12-31
"""

import pandas as pd
import numpy as np
from itertools import combinations
from pathlib import Path
from datetime import datetime
from collections import Counter


def calculate_diff_sum(numbers: list[int]) -> int:
    """
    Berechnet die Summe aller paarweisen Differenzen.

    Args:
        numbers: Liste von 10 Zahlen

    Returns:
        Summe aller |z_i - z_j| fuer alle i < j
    """
    total = 0
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            total += abs(numbers[i] - numbers[j])
    return total


def load_jackpot_dates(quotes_dir: Path) -> list[dict]:
    """
    Laedt alle Jackpot-Tage aus den Quoten-Dateien.

    Sucht nach: Keno-Typ=10, Anzahl richtiger Zahlen=10, Gewinner > 0

    Returns:
        Liste von {datum, anzahl_gewinner}
    """
    jackpot_days = []

    # Durchsuche alle CSV-Dateien
    csv_files = list(quotes_dir.rglob("*.csv")) + list(quotes_dir.rglob("*.CSV"))

    for csv_file in csv_files:
        try:
            # Versuche verschiedene Trennzeichen
            for sep in [',', ';']:
                try:
                    df = pd.read_csv(csv_file, sep=sep, encoding='utf-8', on_bad_lines='skip')

                    # Suche nach Spalten die Keno-Typ und Richtige enthalten
                    cols = df.columns.tolist()

                    # Suche nach dem Pattern: Datum, Keno-Typ=10, Richtige=10, Gewinner>0
                    for idx, row in df.iterrows():
                        try:
                            row_str = ','.join(str(x) for x in row.values)

                            # Pattern: Datum,10,10,Gewinner (wo Gewinner > 0)
                            parts = row_str.split(',')

                            for i in range(len(parts) - 3):
                                # Suche nach: ...,10,10,Gewinner,...
                                if parts[i] == '10' and parts[i+1] == '10':
                                    try:
                                        gewinner = int(parts[i+2].replace('.', ''))
                                        if gewinner > 0:
                                            # Finde das Datum (normalerweise am Anfang)
                                            datum = None
                                            for p in parts[:5]:
                                                if '.' in p and len(p) >= 8:
                                                    datum = p.strip()
                                                    break

                                            if datum:
                                                jackpot_days.append({
                                                    'datum': datum,
                                                    'gewinner': gewinner,
                                                    'quelle': str(csv_file.name)
                                                })
                                    except:
                                        pass
                        except:
                            continue
                    break
                except:
                    continue
        except Exception as e:
            continue

    # Dedupliziere nach Datum
    seen_dates = set()
    unique_jackpots = []
    for jp in jackpot_days:
        if jp['datum'] not in seen_dates:
            seen_dates.add(jp['datum'])
            unique_jackpots.append(jp)

    return unique_jackpots


def load_drawings(drawings_file: Path) -> dict[str, list[int]]:
    """
    Laedt die Ziehungsdaten.

    Returns:
        Dict: datum -> liste von 20 gezogenen Zahlen
    """
    drawings = {}

    try:
        df = pd.read_csv(drawings_file, sep=';', encoding='utf-8')

        for idx, row in df.iterrows():
            datum = str(row['Datum']).strip()

            # Extrahiere die 20 Zahlen
            zahlen = []
            for i in range(1, 21):
                col = f'Keno_Z{i}'
                if col in df.columns:
                    zahlen.append(int(row[col]))

            if len(zahlen) == 20:
                drawings[datum] = zahlen
    except Exception as e:
        print(f"Fehler beim Laden der Ziehungen: {e}")

    return drawings


def analyze_all_combinations(drawn_20: list[int]) -> dict:
    """
    Analysiert alle C(20,10) = 184.756 Kombinationen.

    Returns:
        Dict mit Statistiken pro mod 7 Wert
    """
    mod7_counts = Counter()
    mod7_combinations = {i: [] for i in range(7)}

    total_combinations = 0

    for combo in combinations(drawn_20, 10):
        diff_sum = calculate_diff_sum(list(combo))
        mod7 = diff_sum % 7
        mod7_counts[mod7] += 1
        total_combinations += 1

        # Speichere nur erste 5 Beispiele pro Kategorie
        if len(mod7_combinations[mod7]) < 5:
            mod7_combinations[mod7].append({
                'combo': list(combo),
                'diff_sum': diff_sum,
                'mod7': mod7
            })

    return {
        'total': total_combinations,
        'counts': dict(mod7_counts),
        'examples': mod7_combinations
    }


def main():
    print("=" * 80)
    print("VALIDIERUNG: Differenz-Summe mod 7 = 3 Hypothese")
    print("=" * 80)
    print()

    base_dir = Path(__file__).parent.parent
    keno_gpts_dir = base_dir / "Keno_GPTs"
    drawings_file = base_dir / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

    # 1. Lade Jackpot-Tage
    print("[1] Lade Jackpot-Tage aus Quoten-Dateien...")
    jackpots = load_jackpot_dates(keno_gpts_dir)
    print(f"    Gefunden: {len(jackpots)} einzigartige Jackpot-Tage")
    print()

    # 2. Lade Ziehungsdaten
    print("[2] Lade Ziehungsdaten...")
    drawings = load_drawings(drawings_file)
    print(f"    Gefunden: {len(drawings)} Ziehungen")
    print()

    # 3. Bekannte Jackpot-Gewinner (aus der Aufgabe)
    known_winners = [
        {"name": "Kyritz", "numbers": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]},
        {"name": "Oberbayern", "numbers": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68]},
        {"name": "Nordsachsen", "numbers": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67]},
    ]

    print("[3] Validiere bekannte Jackpot-Gewinner:")
    print("-" * 60)

    for winner in known_winners:
        diff_sum = calculate_diff_sum(winner["numbers"])
        mod7 = diff_sum % 7
        print(f"    {winner['name']}: {winner['numbers']}")
        print(f"        Differenz-Summe = {diff_sum}")
        print(f"        mod 7 = {mod7}")
        print(f"        Status: {'OK' if mod7 == 3 else 'ABWEICHUNG!'}")
        print()

    # 4. Analysiere Jackpot-Tage
    print("[4] Analysiere Jackpot-Tage mit verfuegbaren Ziehungsdaten:")
    print("-" * 60)

    matched_jackpots = []

    for jp in jackpots:
        datum = jp['datum']
        if datum in drawings:
            matched_jackpots.append({
                'datum': datum,
                'gewinner': jp['gewinner'],
                'drawn_20': drawings[datum]
            })

    print(f"    Jackpot-Tage mit Ziehungsdaten: {len(matched_jackpots)}")
    print()

    # 5. Detailanalyse fuer jeden Jackpot-Tag
    print("[5] Detailanalyse der Kombinationen (mod 7 Verteilung):")
    print("=" * 80)

    results_summary = []

    for i, jp in enumerate(matched_jackpots[:10]):  # Erste 10 detailliert
        print(f"\n--- Jackpot-Tag {i+1}: {jp['datum']} ({jp['gewinner']} Gewinner) ---")
        print(f"    Gezogene 20 Zahlen: {sorted(jp['drawn_20'])}")

        analysis = analyze_all_combinations(jp['drawn_20'])

        print(f"\n    Verteilung der {analysis['total']:,} Kombinationen nach mod 7:")
        print("    " + "-" * 50)

        for mod_val in range(7):
            count = analysis['counts'].get(mod_val, 0)
            pct = count / analysis['total'] * 100
            expected = analysis['total'] / 7
            deviation = ((count - expected) / expected) * 100

            bar = '*' * int(pct / 2)
            marker = " <-- ZIEL" if mod_val == 3 else ""

            print(f"    mod 7 = {mod_val}: {count:>6,} ({pct:5.2f}%) {bar}{marker}")

        mod3_count = analysis['counts'].get(3, 0)
        results_summary.append({
            'datum': jp['datum'],
            'gewinner': jp['gewinner'],
            'mod3_count': mod3_count,
            'total': analysis['total'],
            'mod3_pct': mod3_count / analysis['total'] * 100
        })

    # 6. Gesamt-Zusammenfassung
    print("\n" + "=" * 80)
    print("[6] ZUSAMMENFASSUNG")
    print("=" * 80)

    print("\nERWARTUNG BEI ZUFALL:")
    print(f"    Total Kombinationen: C(20,10) = 184.756")
    print(f"    Erwartete Kombinationen mit mod 7 = 3: 184.756 / 7 = 26.394 (14.29%)")

    print("\nTATSAECHLICHE ERGEBNISSE:")
    print("-" * 60)
    print(f"{'Datum':<12} {'Gewinner':>8} {'mod7=3':>10} {'Prozent':>10} {'Reduktion':>12}")
    print("-" * 60)

    for r in results_summary:
        reduktion = r['total'] / r['mod3_count'] if r['mod3_count'] > 0 else float('inf')
        print(f"{r['datum']:<12} {r['gewinner']:>8} {r['mod3_count']:>10,} {r['mod3_pct']:>9.2f}% {reduktion:>10.1f}x")

    print("-" * 60)

    # Durchschnittswerte
    if results_summary:
        avg_mod3_pct = sum(r['mod3_pct'] for r in results_summary) / len(results_summary)
        avg_mod3_count = sum(r['mod3_count'] for r in results_summary) / len(results_summary)

        print(f"\nDURCHSCHNITT:")
        print(f"    Kombinationen mit mod 7 = 3: {avg_mod3_count:,.0f}")
        print(f"    Prozentsatz: {avg_mod3_pct:.2f}%")
        print(f"    Reduktionsfaktor: {184756 / avg_mod3_count:.1f}x")

    print("\n" + "=" * 80)
    print("FAZIT:")
    print("=" * 80)
    print("""
    Die Hypothese 'mod 7 = 3' filtert ca. 14.3% aller moeglichen Kombinationen.

    Bei einer Jackpot-Ziehung mit 20 gezogenen Zahlen gibt es 184.756 moegliche
    10er-Kombinationen. Der Filter reduziert diese auf ca. 26.000-27.000.

    WICHTIG: Dies sagt NICHTS darueber aus, ob die Gewinner-Kombination
    tatsaechlich mod 7 = 3 hat! Die drei bekannten Gewinner haben zufaellig
    alle mod 7 = 3, aber das ist eine sehr kleine Stichprobe.

    Um die Hypothese zu validieren, braeuchten wir die TATSAECHLICHEN
    10 Zahlen, die jeder Gewinner getippt hat - nicht nur die 20 gezogenen.
    """)


if __name__ == "__main__":
    main()
