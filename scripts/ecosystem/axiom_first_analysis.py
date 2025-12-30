#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Axiom-First Analyse: Drei Ansaetze
==================================

1. Event-basierte Analyse (Jackpot-Trigger, Einsatz-Schwellen)
2. Zahlen-Ebene (Cross-Lotterie Zahlen-Korrelation)
3. Dauerschein-Simulation (typische Spieler-Muster)

PARADIGMA: Wirtschaftslogik statt Pattern-Suche
"""

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, ttest_ind

# Pfade
BASE_DIR = Path(__file__).parent.parent.parent
KENO_PATH = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
LOTTO_PATH = BASE_DIR / "data" / "raw" / "lotto" / "LOTTO_ab_2022_bereinigt.csv"
ECOSYSTEM_PATH = BASE_DIR / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
OUTPUT_DIR = BASE_DIR / "results" / "ecosystem"

# Typische Spieler-Muster
BIRTHDAY_NUMBERS = list(range(1, 32))  # 1-31
LUCKY_NUMBERS = [7, 13, 21, 27, 33, 42, 49]
SPIELSCHEIN_DIAGONALS = [
    [1, 9, 17, 25, 33, 41],      # Diagonal
    [7, 13, 19, 25, 31, 37],     # Diagonal
    [1, 2, 3, 4, 5, 6],          # Erste Reihe
    [43, 44, 45, 46, 47, 48, 49] # Letzte Reihe
]


def load_keno_numbers(filepath: Path) -> pd.DataFrame:
    """Lade KENO Gewinnzahlen."""
    df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    # Extrahiere Zahlen
    number_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['numbers'] = df[number_cols].values.tolist()

    # Spieleinsatz parsen
    if 'Keno_Spieleinsatz' in df.columns:
        df['spieleinsatz'] = df['Keno_Spieleinsatz'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)

    return df[['Datum', 'numbers', 'spieleinsatz']].copy()


def load_lotto_numbers(filepath: Path) -> pd.DataFrame:
    """Lade Lotto 6aus49 Gewinnzahlen."""
    df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')

    # Extrahiere Zahlen
    number_cols = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']
    df['numbers'] = df[number_cols].values.tolist()

    # Jackpot (behandle '--' und andere ungueltige Werte)
    df['jackpot'] = pd.to_numeric(df['Jackpot_Kl1'], errors='coerce').fillna(0).astype(int)

    # Spieleinsatz
    if 'Spieleinsatz' in df.columns:
        df['spieleinsatz'] = df['Spieleinsatz'].astype(str).str.replace('.', '').str.replace(',', '.').astype(float)

    return df[['Datum', 'numbers', 'jackpot', 'spieleinsatz']].copy()


# =============================================================================
# ANSATZ 1: EVENT-BASIERTE ANALYSE
# =============================================================================

def analyze_events(eco_df: pd.DataFrame) -> dict:
    """
    Event-basierte Analyse.

    Hypothesen:
    - EVT-001: Jackpot-Kaskaden-Vermeidung
    - EVT-002: Einsatz-Schwellen-Trigger
    - EVT-003: Gewinner-Dichte-Ausgleich
    """
    print("\n" + "=" * 60)
    print("ANSATZ 1: EVENT-BASIERTE ANALYSE")
    print("=" * 60)

    results = {}

    # --- EVT-001: Jackpot-Kaskaden-Vermeidung ---
    print("\n--- EVT-001: Jackpot-Kaskaden-Vermeidung ---")

    # Finde alle Jackpot-Tage
    eco_df = eco_df.copy()
    eco_df['any_jackpot'] = (eco_df['keno_jackpot'].fillna(0) + eco_df['lotto_jackpot'].fillna(0)) > 0

    jackpot_indices = eco_df[eco_df['any_jackpot']].index.tolist()

    # Berechne Tage bis zum naechsten Jackpot
    days_to_next = []
    for i, jp_idx in enumerate(jackpot_indices[:-1]):
        next_jp_idx = jackpot_indices[i + 1]
        days = next_jp_idx - jp_idx
        days_to_next.append(days)

    if days_to_next:
        avg_days = np.mean(days_to_next)
        std_days = np.std(days_to_next)
        min_days = min(days_to_next)
        max_days = max(days_to_next)

        print(f"Durchschnitt Tage zwischen Jackpots: {avg_days:.1f}")
        print(f"Standardabweichung: {std_days:.1f}")
        print(f"Minimum: {min_days}, Maximum: {max_days}")

        # Pruefe ob Jackpots geclustert oder verteilt sind
        # Erwartung bei Zufall: exponentialverteilt
        cv = std_days / avg_days if avg_days > 0 else 0
        print(f"Variationskoeffizient: {cv:.2f}")
        print(f"Interpretation: {'GLEICHMAESSIG verteilt' if cv < 1 else 'GECLUSTERT'}")

        results['evt_001'] = {
            'avg_days_between_jackpots': avg_days,
            'std_days': std_days,
            'min_days': min_days,
            'max_days': max_days,
            'coefficient_of_variation': cv,
            'distributed_evenly': cv < 1
        }
    else:
        results['evt_001'] = {'error': 'Nicht genug Jackpots'}

    # --- EVT-002: Einsatz-Schwellen-Trigger ---
    print("\n--- EVT-002: Gewinner-Autokorrelation ---")

    # Autokorrelation der Oekosystem-Gewinner
    winners = eco_df['ecosystem_winners'].dropna().values

    if len(winners) > 10:
        autocorrs = []
        for lag in range(1, 8):
            if len(winners) > lag:
                r, p = pearsonr(winners[:-lag], winners[lag:])
                autocorrs.append({'lag': lag, 'correlation': r, 'p_value': p})
                print(f"Lag {lag}: r={r:.3f}, p={p:.4f}")

        # Negative Autokorrelation = Ausgleich
        lag1_corr = autocorrs[0]['correlation'] if autocorrs else 0
        print(f"\nLag-1 Korrelation: {lag1_corr:.3f}")
        print(f"Interpretation: {'AUSGLEICH (neg. Korr.)' if lag1_corr < -0.1 else 'KEIN Ausgleich'}")

        results['evt_002'] = {
            'autocorrelations': autocorrs,
            'lag1_correlation': lag1_corr,
            'shows_compensation': lag1_corr < -0.1
        }
    else:
        results['evt_002'] = {'error': 'Nicht genug Daten'}

    return results


# =============================================================================
# ANSATZ 2: ZAHLEN-EBENE ANALYSE
# =============================================================================

def analyze_numbers(keno_df: pd.DataFrame, lotto_df: pd.DataFrame) -> dict:
    """
    Zahlen-Ebene Analyse: Cross-Lotterie Korrelation.

    Hypothesen:
    - NUM-001: Zahlen-Ausschluss (gleiche Woche)
    - NUM-002: Inverse Zahlen-Frequenz
    - NUM-003: Dekaden-Balancing
    """
    print("\n" + "=" * 60)
    print("ANSATZ 2: ZAHLEN-EBENE ANALYSE")
    print("=" * 60)

    results = {}

    # Gemeinsamer Zahlenraum: 1-49
    common_range = range(1, 50)

    # --- NUM-001: Zahlen-Ausschluss (gleiche Woche) ---
    print("\n--- NUM-001: Zahlen-Ausschluss (gleiche Woche) ---")

    # Erstelle Wochen-Mapping
    keno_df = keno_df.copy()
    lotto_df = lotto_df.copy()
    keno_df['week'] = keno_df['Datum'].dt.isocalendar().week.astype(str) + '-' + keno_df['Datum'].dt.year.astype(str)
    lotto_df['week'] = lotto_df['Datum'].dt.isocalendar().week.astype(str) + '-' + lotto_df['Datum'].dt.year.astype(str)

    # Finde gemeinsame Wochen
    common_weeks = set(keno_df['week']).intersection(set(lotto_df['week']))
    print(f"Gemeinsame Wochen: {len(common_weeks)}")

    jaccard_scores = []
    overlap_counts = []

    for week in common_weeks:
        # KENO Zahlen dieser Woche (nur 1-49)
        keno_week = keno_df[keno_df['week'] == week]
        keno_numbers = set()
        for nums in keno_week['numbers']:
            keno_numbers.update([n for n in nums if 1 <= n <= 49])

        # Lotto Zahlen dieser Woche
        lotto_week = lotto_df[lotto_df['week'] == week]
        lotto_numbers = set()
        for nums in lotto_week['numbers']:
            lotto_numbers.update([n for n in nums if 1 <= n <= 49])

        if keno_numbers and lotto_numbers:
            # Jaccard-Index
            intersection = len(keno_numbers.intersection(lotto_numbers))
            union = len(keno_numbers.union(lotto_numbers))
            jaccard = intersection / union if union > 0 else 0
            jaccard_scores.append(jaccard)
            overlap_counts.append(intersection)

    if jaccard_scores:
        avg_jaccard = np.mean(jaccard_scores)
        avg_overlap = np.mean(overlap_counts)

        # Erwartungswert bei Zufall
        # KENO: ~35 verschiedene Zahlen/Woche (aus 1-49)
        # Lotto: ~10 verschiedene Zahlen/Woche
        # Erwartete Ueberlappung: 35 * 10 / 49 ≈ 7.1
        expected_overlap = 7.1
        expected_jaccard = expected_overlap / 38  # ≈ 0.19

        print(f"Durchschnittliche Ueberlappung: {avg_overlap:.1f} Zahlen")
        print(f"Erwartete Ueberlappung (Zufall): {expected_overlap:.1f}")
        print(f"Durchschnitt Jaccard-Index: {avg_jaccard:.3f}")
        print(f"Erwarteter Jaccard (Zufall): {expected_jaccard:.3f}")

        diff_pct = (avg_overlap - expected_overlap) / expected_overlap * 100
        print(f"Abweichung vom Zufall: {diff_pct:+.1f}%")
        print(f"Interpretation: {'WENIGER Ueberlappung = VERMEIDUNG' if diff_pct < -10 else 'Normal'}")

        results['num_001'] = {
            'avg_overlap': avg_overlap,
            'expected_overlap': expected_overlap,
            'avg_jaccard': avg_jaccard,
            'deviation_pct': diff_pct,
            'shows_avoidance': diff_pct < -10
        }
    else:
        results['num_001'] = {'error': 'Keine Daten'}

    # --- NUM-002: Inverse Zahlen-Frequenz ---
    print("\n--- NUM-002: Inverse Zahlen-Frequenz (Monatsweise) ---")

    keno_df['month'] = keno_df['Datum'].dt.to_period('M')
    lotto_df['month'] = lotto_df['Datum'].dt.to_period('M')

    common_months = set(keno_df['month']).intersection(set(lotto_df['month']))

    correlations = []
    for month in common_months:
        # KENO Frequenzen
        keno_month = keno_df[keno_df['month'] == month]
        keno_freq = Counter()
        for nums in keno_month['numbers']:
            keno_freq.update([n for n in nums if 1 <= n <= 49])

        # Lotto Frequenzen
        lotto_month = lotto_df[lotto_df['month'] == month]
        lotto_freq = Counter()
        for nums in lotto_month['numbers']:
            lotto_freq.update([n for n in nums if 1 <= n <= 49])

        # Korrelation
        keno_vec = [keno_freq.get(n, 0) for n in common_range]
        lotto_vec = [lotto_freq.get(n, 0) for n in common_range]

        if sum(keno_vec) > 0 and sum(lotto_vec) > 0:
            r, p = pearsonr(keno_vec, lotto_vec)
            correlations.append({'month': str(month), 'r': r, 'p': p})

    if correlations:
        avg_r = np.mean([c['r'] for c in correlations])
        print(f"Durchschnittliche Korrelation KENO vs Lotto: r={avg_r:.3f}")
        print(f"Interpretation: {'INVERSE Frequenz' if avg_r < -0.1 else 'KEINE inverse Frequenz'}")

        results['num_002'] = {
            'avg_correlation': avg_r,
            'monthly_correlations': correlations[:5],  # Erste 5
            'shows_inverse': avg_r < -0.1
        }
    else:
        results['num_002'] = {'error': 'Keine Daten'}

    # --- NUM-003: Dekaden-Balancing ---
    print("\n--- NUM-003: Dekaden-Balancing ---")

    # Dekaden: 1-10, 11-20, 21-30, 31-40, 41-49
    def get_decade(n):
        if n <= 10: return 1
        if n <= 20: return 2
        if n <= 30: return 3
        if n <= 40: return 4
        return 5

    decade_correlations = []
    for month in common_months:
        keno_month = keno_df[keno_df['month'] == month]
        lotto_month = lotto_df[lotto_df['month'] == month]

        keno_decades = Counter()
        for nums in keno_month['numbers']:
            for n in nums:
                if 1 <= n <= 49:
                    keno_decades[get_decade(n)] += 1

        lotto_decades = Counter()
        for nums in lotto_month['numbers']:
            for n in nums:
                if 1 <= n <= 49:
                    lotto_decades[get_decade(n)] += 1

        keno_vec = [keno_decades.get(d, 0) for d in range(1, 6)]
        lotto_vec = [lotto_decades.get(d, 0) for d in range(1, 6)]

        if sum(keno_vec) > 0 and sum(lotto_vec) > 0:
            r, p = pearsonr(keno_vec, lotto_vec)
            decade_correlations.append(r)

    if decade_correlations:
        avg_decade_r = np.mean(decade_correlations)
        print(f"Durchschnittliche Dekaden-Korrelation: r={avg_decade_r:.3f}")
        print(f"Interpretation: {'DEKADEN-BALANCING' if avg_decade_r < -0.1 else 'Kein Balancing'}")

        results['num_003'] = {
            'avg_decade_correlation': avg_decade_r,
            'shows_balancing': avg_decade_r < -0.1
        }
    else:
        results['num_003'] = {'error': 'Keine Daten'}

    return results


# =============================================================================
# ANSATZ 3: DAUERSCHEIN-SIMULATION
# =============================================================================

def analyze_dauerschein(keno_df: pd.DataFrame, lotto_df: pd.DataFrame) -> dict:
    """
    Dauerschein-Simulation.

    Hypothesen:
    - DAU-001: Birthday-Zahlen-Haeufigkeit
    - DAU-002: Glueckszahlen-Vermeidung
    - DAU-003: Diagonalen-Vermeidung
    """
    print("\n" + "=" * 60)
    print("ANSATZ 3: DAUERSCHEIN-SIMULATION")
    print("=" * 60)

    results = {}

    # --- DAU-001: Birthday-Zahlen ---
    print("\n--- DAU-001: Birthday-Zahlen (1-31) vs Nicht-Birthday (32-49) ---")

    # Lotto Frequenzen
    lotto_freq = Counter()
    for nums in lotto_df['numbers']:
        lotto_freq.update(nums)

    birthday_freq = sum(lotto_freq.get(n, 0) for n in range(1, 32))
    non_birthday_freq = sum(lotto_freq.get(n, 0) for n in range(32, 50))

    # Normalisiere auf Anzahl Zahlen
    birthday_per_number = birthday_freq / 31
    non_birthday_per_number = non_birthday_freq / 18

    print(f"Birthday (1-31): {birthday_per_number:.1f} pro Zahl")
    print(f"Nicht-Birthday (32-49): {non_birthday_per_number:.1f} pro Zahl")

    diff = (birthday_per_number - non_birthday_per_number) / non_birthday_per_number * 100
    print(f"Unterschied: {diff:+.1f}%")
    print(f"Interpretation: {'Birthday BEVORZUGT' if diff > 5 else 'Birthday VERMIEDEN' if diff < -5 else 'Ausgeglichen'}")

    results['dau_001'] = {
        'birthday_per_number': birthday_per_number,
        'non_birthday_per_number': non_birthday_per_number,
        'difference_pct': diff,
        'birthday_compensated': abs(diff) < 5
    }

    # --- DAU-002: Glueckszahlen ---
    print("\n--- DAU-002: Glueckszahlen (7, 13, 21, 27, 33, 42, 49) ---")

    lucky_freq = sum(lotto_freq.get(n, 0) for n in LUCKY_NUMBERS)
    other_freq = sum(lotto_freq.get(n, 0) for n in range(1, 50) if n not in LUCKY_NUMBERS)

    lucky_per_number = lucky_freq / len(LUCKY_NUMBERS)
    other_per_number = other_freq / (49 - len(LUCKY_NUMBERS))

    print(f"Glueckszahlen: {lucky_per_number:.1f} pro Zahl")
    print(f"Andere Zahlen: {other_per_number:.1f} pro Zahl")

    lucky_diff = (lucky_per_number - other_per_number) / other_per_number * 100
    print(f"Unterschied: {lucky_diff:+.1f}%")
    print(f"Interpretation: {'Glueckszahlen VERMIEDEN' if lucky_diff < -5 else 'Normal'}")

    results['dau_002'] = {
        'lucky_per_number': lucky_per_number,
        'other_per_number': other_per_number,
        'difference_pct': lucky_diff,
        'lucky_avoided': lucky_diff < -5
    }

    # --- DAU-003: Diagonalen-Vermeidung ---
    print("\n--- DAU-003: Spielschein-Diagonalen ---")

    # Zaehle wie oft Diagonalen zusammen erscheinen
    diagonal_counts = []

    for diag in SPIELSCHEIN_DIAGONALS:
        count = 0
        for nums in lotto_df['numbers']:
            nums_set = set(nums)
            # Wie viele der Diagonal-Zahlen sind in dieser Ziehung?
            overlap = len(set(diag).intersection(nums_set))
            if overlap >= 3:  # Mindestens 3 der 6-7 Zahlen
                count += 1
        diagonal_counts.append({
            'diagonal': diag,
            'count': count,
            'pct': count / len(lotto_df) * 100
        })

    print("Haeufigkeit (min. 3 Zahlen der Diagonale):")
    for dc in diagonal_counts:
        print(f"  {dc['diagonal'][:3]}...: {dc['count']}x ({dc['pct']:.1f}%)")

    # Erwartung bei Zufall (vereinfacht)
    expected_3_of_6 = 0.5  # ca. 0.5% Wahrscheinlichkeit
    avg_pct = np.mean([dc['pct'] for dc in diagonal_counts])
    print(f"\nDurchschnitt: {avg_pct:.2f}%")
    print(f"Erwartung bei Zufall: ~{expected_3_of_6:.1f}%")
    print(f"Interpretation: {'Diagonalen VERMIEDEN' if avg_pct < expected_3_of_6 * 0.8 else 'Normal'}")

    results['dau_003'] = {
        'diagonal_analysis': diagonal_counts,
        'avg_diagonal_pct': avg_pct,
        'diagonals_avoided': avg_pct < expected_3_of_6 * 0.8
    }

    return results


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("AXIOM-FIRST ANALYSE: DREI ANSAETZE")
    print("=" * 60)
    print("\nParadigma: Wirtschaftslogik statt Pattern-Suche")

    # Output-Verzeichnis
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Daten laden
    print("\nLade Daten...")
    keno_df = load_keno_numbers(KENO_PATH)
    print(f"  KENO: {len(keno_df)} Ziehungen")

    lotto_df = load_lotto_numbers(LOTTO_PATH)
    print(f"  Lotto: {len(lotto_df)} Ziehungen")

    eco_df = pd.read_csv(ECOSYSTEM_PATH, parse_dates=['datum'])
    print(f"  Oekosystem: {len(eco_df)} Tage")

    all_results = {}

    # Ansatz 1: Event-basiert
    all_results['events'] = analyze_events(eco_df)

    # Ansatz 2: Zahlen-Ebene
    all_results['numbers'] = analyze_numbers(keno_df, lotto_df)

    # Ansatz 3: Dauerschein
    all_results['dauerschein'] = analyze_dauerschein(keno_df, lotto_df)

    # Speichern
    output_file = OUTPUT_DIR / "axiom_first_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n\nErgebnisse gespeichert: {output_file}")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)

    print("\n1. EVENT-BASIERTE ANALYSE:")
    if 'evt_001' in all_results['events']:
        evt = all_results['events']['evt_001']
        if 'distributed_evenly' in evt:
            status = "BESTAETIGT" if evt['distributed_evenly'] else "NICHT bestaetigt"
            print(f"   EVT-001 Jackpot-Verteilung: {status}")

    print("\n2. ZAHLEN-EBENE ANALYSE:")
    if 'num_001' in all_results['numbers']:
        num = all_results['numbers']['num_001']
        if 'shows_avoidance' in num:
            status = "BESTAETIGT" if num['shows_avoidance'] else "NICHT bestaetigt"
            print(f"   NUM-001 Zahlen-Ausschluss: {status} ({num.get('deviation_pct', 0):+.1f}%)")

    if 'num_002' in all_results['numbers']:
        num = all_results['numbers']['num_002']
        if 'shows_inverse' in num:
            status = "BESTAETIGT" if num['shows_inverse'] else "NICHT bestaetigt"
            print(f"   NUM-002 Inverse Frequenz: {status}")

    print("\n3. DAUERSCHEIN-SIMULATION:")
    if 'dau_001' in all_results['dauerschein']:
        dau = all_results['dauerschein']['dau_001']
        if 'birthday_compensated' in dau:
            status = "BESTAETIGT" if dau['birthday_compensated'] else "NICHT bestaetigt"
            print(f"   DAU-001 Birthday-Kompensation: {status}")

    if 'dau_002' in all_results['dauerschein']:
        dau = all_results['dauerschein']['dau_002']
        if 'lucky_avoided' in dau:
            status = "BESTAETIGT" if dau['lucky_avoided'] else "NICHT bestaetigt"
            print(f"   DAU-002 Glueckszahlen-Vermeidung: {status}")

    return all_results


if __name__ == '__main__':
    main()
