#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyse der Jackpot- und High-Win Ziehungen
============================================

Hypothese: Bei hohen Gewinnklassen (>=10.000€) werden populaere
Zahlen (Birthday, Glueckszahlen, Diagonalen) VERMIEDEN.

Gewinnklassen >=10.000€:
- KENO Typ 10, 10 richtig = 100.000€ (Jackpot)
- KENO Typ 9, 9 richtig = 50.000€
- KENO Typ 8, 8 richtig = 10.000€
- Lotto 6aus49, GK1 (6+SZ) = Jackpot
- Lotto 6aus49, GK2 (6 richtig) = ~500.000€
- Lotto 6aus49, GK3 (5+SZ) = ~10.000€
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact

# Pfade
BASE_DIR = Path(__file__).parent.parent.parent
KENO_PATH = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
KENO_GQ_PATH = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
KENO_GQ_2025_PATH = BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv"
LOTTO_PATH = BASE_DIR / "data" / "raw" / "lotto" / "LOTTO_ab_2022_bereinigt.csv"
LOTTO_GQ_PATH = BASE_DIR / "Keno_GPTs" / "Lotto6aus49_GQ_2025.csv"
OUTPUT_DIR = BASE_DIR / "results" / "ecosystem"

# Zahlen-Kategorien
BIRTHDAY_NUMBERS = set(range(1, 32))  # 1-31
NON_BIRTHDAY_NUMBERS = set(range(32, 50))  # 32-49 (fuer Lotto)
LUCKY_NUMBERS = {7, 13, 21, 27, 33, 42, 49}
LOW_NUMBERS = set(range(1, 26))  # Untere Haelfte
HIGH_NUMBERS = set(range(26, 50))  # Obere Haelfte


def load_keno_data(filepath: Path) -> pd.DataFrame:
    """Lade KENO Ziehungsdaten."""
    df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    number_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    df['numbers'] = df[number_cols].values.tolist()
    return df


def load_keno_gq(filepath: Path) -> pd.DataFrame:
    """Lade KENO Gewinnquoten."""
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    # Parse Datum
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    # Fallback fuer andere Formate
    mask = df['Datum'].isna()
    if mask.any():
        df.loc[mask, 'Datum'] = pd.to_datetime(
            df.loc[mask, 'Datum'].astype(str).str.extract(r'(\d{1,2}\.\d{1,2}\.)')[0] + '2024',
            format='%d.%m.%Y', errors='coerce'
        )
    return df


def load_lotto_data(filepath: Path) -> pd.DataFrame:
    """Lade Lotto Ziehungsdaten."""
    df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y')
    number_cols = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']
    df['numbers'] = df[number_cols].values.tolist()
    df['jackpot'] = pd.to_numeric(df['Jackpot_Kl1'], errors='coerce').fillna(0).astype(int)
    return df


def find_high_win_dates_keno(gq_df: pd.DataFrame) -> dict:
    """Finde Daten mit hohen Gewinnen bei KENO."""
    high_wins = {
        'typ10_10': [],  # 100.000€
        'typ9_9': [],    # 50.000€
        'typ8_8': [],    # 10.000€
    }

    for _, row in gq_df.iterrows():
        try:
            typ = int(row.get('Keno-Typ', 0))
            richtige = row.get('Anzahl richtiger Zahlen', '')
            gewinner = row.get('Anzahl der Gewinner', 0)
            datum = row.get('Datum')

            if pd.isna(datum):
                continue

            # Parse Gewinner
            if isinstance(gewinner, str):
                gewinner = float(gewinner.replace('.', '').replace(',', '.'))
            gewinner = int(float(gewinner)) if not pd.isna(gewinner) else 0

            # Parse richtige
            if isinstance(richtige, str) and richtige.isdigit():
                richtige = int(richtige)
            elif isinstance(richtige, (int, float)) and not pd.isna(richtige):
                richtige = int(richtige)
            else:
                continue

            # Hohe Gewinnklassen mit Gewinnern
            if typ == 10 and richtige == 10 and gewinner > 0:
                high_wins['typ10_10'].append(datum)
            elif typ == 9 and richtige == 9 and gewinner > 0:
                high_wins['typ9_9'].append(datum)
            elif typ == 8 and richtige == 8 and gewinner > 0:
                high_wins['typ8_8'].append(datum)

        except (ValueError, TypeError):
            continue

    # Deduplizieren
    for key in high_wins:
        high_wins[key] = list(set(high_wins[key]))

    return high_wins


def analyze_number_distribution(numbers_list: list, label: str) -> dict:
    """Analysiere Zahlenverteilung fuer eine Liste von Ziehungen."""
    all_numbers = []
    for nums in numbers_list:
        all_numbers.extend([n for n in nums if 1 <= n <= 49])

    if not all_numbers:
        return {'error': 'Keine Zahlen'}

    counter = Counter(all_numbers)
    total = len(all_numbers)

    # Birthday vs Non-Birthday
    birthday_count = sum(counter.get(n, 0) for n in BIRTHDAY_NUMBERS)
    non_birthday_count = sum(counter.get(n, 0) for n in NON_BIRTHDAY_NUMBERS)

    birthday_pct = birthday_count / total * 100 if total > 0 else 0
    non_birthday_pct = non_birthday_count / total * 100 if total > 0 else 0

    # Normalisiert (pro Zahl)
    birthday_per_num = birthday_count / len(BIRTHDAY_NUMBERS)
    non_birthday_per_num = non_birthday_count / len(NON_BIRTHDAY_NUMBERS)

    # Glueckszahlen
    lucky_count = sum(counter.get(n, 0) for n in LUCKY_NUMBERS)
    other_count = total - lucky_count

    lucky_per_num = lucky_count / len(LUCKY_NUMBERS)
    other_per_num = other_count / (49 - len(LUCKY_NUMBERS))

    # Low vs High
    low_count = sum(counter.get(n, 0) for n in LOW_NUMBERS if n <= 49)
    high_count = sum(counter.get(n, 0) for n in HIGH_NUMBERS if n <= 49)

    return {
        'label': label,
        'total_numbers': total,
        'birthday_count': birthday_count,
        'non_birthday_count': non_birthday_count,
        'birthday_per_num': birthday_per_num,
        'non_birthday_per_num': non_birthday_per_num,
        'birthday_ratio': birthday_per_num / non_birthday_per_num if non_birthday_per_num > 0 else 0,
        'lucky_count': lucky_count,
        'lucky_per_num': lucky_per_num,
        'other_per_num': other_per_num,
        'lucky_ratio': lucky_per_num / other_per_num if other_per_num > 0 else 0,
        'low_count': low_count,
        'high_count': high_count,
        'low_high_ratio': low_count / high_count if high_count > 0 else 0,
    }


def compare_distributions(high_win_dist: dict, normal_dist: dict) -> dict:
    """Vergleiche zwei Verteilungen."""
    comparison = {}

    # Birthday-Ratio Vergleich
    hw_birthday = high_win_dist.get('birthday_ratio', 1)
    norm_birthday = normal_dist.get('birthday_ratio', 1)
    birthday_diff = (hw_birthday - norm_birthday) / norm_birthday * 100 if norm_birthday > 0 else 0

    comparison['birthday_ratio_high_win'] = hw_birthday
    comparison['birthday_ratio_normal'] = norm_birthday
    comparison['birthday_difference_pct'] = birthday_diff
    comparison['birthday_avoided'] = birthday_diff < -5  # 5% weniger = Vermeidung

    # Lucky-Ratio Vergleich
    hw_lucky = high_win_dist.get('lucky_ratio', 1)
    norm_lucky = normal_dist.get('lucky_ratio', 1)
    lucky_diff = (hw_lucky - norm_lucky) / norm_lucky * 100 if norm_lucky > 0 else 0

    comparison['lucky_ratio_high_win'] = hw_lucky
    comparison['lucky_ratio_normal'] = norm_lucky
    comparison['lucky_difference_pct'] = lucky_diff
    comparison['lucky_avoided'] = lucky_diff < -5

    # Low/High Vergleich
    hw_lowhigh = high_win_dist.get('low_high_ratio', 1)
    norm_lowhigh = normal_dist.get('low_high_ratio', 1)
    lowhigh_diff = (hw_lowhigh - norm_lowhigh) / norm_lowhigh * 100 if norm_lowhigh > 0 else 0

    comparison['low_high_ratio_high_win'] = hw_lowhigh
    comparison['low_high_ratio_normal'] = norm_lowhigh
    comparison['low_high_difference_pct'] = lowhigh_diff
    comparison['high_numbers_preferred'] = lowhigh_diff < -5

    return comparison


def analyze_keno_high_wins(keno_df: pd.DataFrame, high_win_dates: dict) -> dict:
    """Analysiere KENO Hochgewinn-Ziehungen."""
    print("\n" + "=" * 60)
    print("KENO HOCHGEWINN-ANALYSE")
    print("=" * 60)

    results = {}

    # Alle Ziehungen als Baseline
    all_numbers = keno_df['numbers'].tolist()
    normal_dist = analyze_number_distribution(all_numbers, "Alle KENO Ziehungen")

    print(f"\nBaseline (alle {len(all_numbers)} Ziehungen):")
    print(f"  Birthday-Ratio: {normal_dist['birthday_ratio']:.3f}")
    print(f"  Lucky-Ratio: {normal_dist['lucky_ratio']:.3f}")

    results['baseline'] = normal_dist

    # Analysiere jede Hochgewinn-Kategorie
    for category, dates in high_win_dates.items():
        if not dates:
            print(f"\n--- {category}: Keine Daten ---")
            continue

        # Finde Ziehungen an diesen Daten
        category_df = keno_df[keno_df['Datum'].isin(dates)]

        if len(category_df) == 0:
            print(f"\n--- {category}: Keine passenden Ziehungen gefunden ---")
            continue

        category_numbers = category_df['numbers'].tolist()
        category_dist = analyze_number_distribution(category_numbers, category)

        print(f"\n--- {category} ({len(category_df)} Ziehungen) ---")
        print(f"  Birthday-Ratio: {category_dist['birthday_ratio']:.3f}")
        print(f"  Lucky-Ratio: {category_dist['lucky_ratio']:.3f}")

        # Vergleich
        comparison = compare_distributions(category_dist, normal_dist)

        print(f"  Birthday-Differenz: {comparison['birthday_difference_pct']:+.1f}%")
        print(f"  Lucky-Differenz: {comparison['lucky_difference_pct']:+.1f}%")
        print(f"  → Birthday vermieden: {'JA' if comparison['birthday_avoided'] else 'NEIN'}")
        print(f"  → Lucky vermieden: {'JA' if comparison['lucky_avoided'] else 'NEIN'}")

        results[category] = {
            'n_draws': len(category_df),
            'distribution': category_dist,
            'comparison': comparison
        }

    return results


def analyze_lotto_high_wins(lotto_df: pd.DataFrame) -> dict:
    """Analysiere Lotto Hochgewinn-Ziehungen."""
    print("\n" + "=" * 60)
    print("LOTTO 6aus49 HOCHGEWINN-ANALYSE")
    print("=" * 60)

    results = {}

    # Alle Ziehungen als Baseline
    all_numbers = lotto_df['numbers'].tolist()
    normal_dist = analyze_number_distribution(all_numbers, "Alle Lotto Ziehungen")

    print(f"\nBaseline (alle {len(all_numbers)} Ziehungen):")
    print(f"  Birthday-Ratio: {normal_dist['birthday_ratio']:.3f}")
    print(f"  Lucky-Ratio: {normal_dist['lucky_ratio']:.3f}")

    results['baseline'] = normal_dist

    # Jackpot-Ziehungen (GK1)
    jackpot_df = lotto_df[lotto_df['jackpot'] > 0]

    if len(jackpot_df) > 0:
        jp_numbers = jackpot_df['numbers'].tolist()
        jp_dist = analyze_number_distribution(jp_numbers, "Jackpot (6+SZ)")

        print(f"\n--- Jackpot-Ziehungen ({len(jackpot_df)} Ziehungen) ---")
        print(f"  Birthday-Ratio: {jp_dist['birthday_ratio']:.3f}")
        print(f"  Lucky-Ratio: {jp_dist['lucky_ratio']:.3f}")

        comparison = compare_distributions(jp_dist, normal_dist)

        print(f"  Birthday-Differenz: {comparison['birthday_difference_pct']:+.1f}%")
        print(f"  Lucky-Differenz: {comparison['lucky_difference_pct']:+.1f}%")
        print(f"  High-Numbers Differenz: {comparison['low_high_difference_pct']:+.1f}%")
        print(f"  → Birthday vermieden: {'JA' if comparison['birthday_avoided'] else 'NEIN'}")
        print(f"  → High Numbers bevorzugt: {'JA' if comparison['high_numbers_preferred'] else 'NEIN'}")

        results['jackpot'] = {
            'n_draws': len(jackpot_df),
            'distribution': jp_dist,
            'comparison': comparison
        }
    else:
        print("\n--- Keine Jackpot-Ziehungen gefunden ---")

    # Analyse der Zahlen bei ALLEN Ziehungen nach Summe
    print("\n--- Analyse nach Zahlensumme ---")
    lotto_df = lotto_df.copy()
    lotto_df['sum'] = lotto_df['numbers'].apply(sum)

    median_sum = lotto_df['sum'].median()

    high_sum_df = lotto_df[lotto_df['sum'] > median_sum]
    low_sum_df = lotto_df[lotto_df['sum'] <= median_sum]

    high_sum_numbers = high_sum_df['numbers'].tolist()
    low_sum_numbers = low_sum_df['numbers'].tolist()

    high_sum_dist = analyze_number_distribution(high_sum_numbers, "Hohe Summe")
    low_sum_dist = analyze_number_distribution(low_sum_numbers, "Niedrige Summe")

    print(f"  Median Summe: {median_sum}")
    print(f"  Hohe Summe: Birthday-Ratio = {high_sum_dist['birthday_ratio']:.3f}")
    print(f"  Niedrige Summe: Birthday-Ratio = {low_sum_dist['birthday_ratio']:.3f}")

    results['sum_analysis'] = {
        'median_sum': median_sum,
        'high_sum_birthday_ratio': high_sum_dist['birthday_ratio'],
        'low_sum_birthday_ratio': low_sum_dist['birthday_ratio'],
    }

    return results


def analyze_specific_numbers_in_jackpots(keno_df: pd.DataFrame, lotto_df: pd.DataFrame,
                                          high_win_dates: dict) -> dict:
    """Detaillierte Analyse einzelner Zahlen in Jackpot-Ziehungen."""
    print("\n" + "=" * 60)
    print("EINZELZAHLEN-ANALYSE BEI HOCHGEWINNEN")
    print("=" * 60)

    results = {}

    # KENO Typ 10/10 Zahlen
    typ10_dates = high_win_dates.get('typ10_10', [])
    if typ10_dates:
        jackpot_keno = keno_df[keno_df['Datum'].isin(typ10_dates)]

        if len(jackpot_keno) > 0:
            # Zaehle alle Zahlen
            jp_counter = Counter()
            for nums in jackpot_keno['numbers']:
                jp_counter.update(nums)

            # Vergleich mit Gesamt
            all_counter = Counter()
            for nums in keno_df['numbers']:
                all_counter.update(nums)

            # Normalisiere
            jp_total = sum(jp_counter.values())
            all_total = sum(all_counter.values())

            print(f"\n--- KENO Typ10/10 Einzelzahlen ({len(jackpot_keno)} Jackpots) ---")

            # Finde ueber- und unterrepraesentierte Zahlen
            over_represented = []
            under_represented = []

            for num in range(1, 71):
                jp_freq = jp_counter.get(num, 0) / jp_total if jp_total > 0 else 0
                all_freq = all_counter.get(num, 0) / all_total if all_total > 0 else 0

                if all_freq > 0:
                    ratio = jp_freq / all_freq
                    if ratio > 1.3:
                        over_represented.append((num, ratio))
                    elif ratio < 0.7:
                        under_represented.append((num, ratio))

            over_represented.sort(key=lambda x: x[1], reverse=True)
            under_represented.sort(key=lambda x: x[1])

            print("\nUeberrepraesentiert bei Jackpots (>130%):")
            for num, ratio in over_represented[:10]:
                is_birthday = "BD" if num <= 31 else ""
                is_lucky = "LK" if num in LUCKY_NUMBERS else ""
                print(f"  Zahl {num:2d}: {ratio:.1%} {is_birthday} {is_lucky}")

            print("\nUnterrepraesentiert bei Jackpots (<70%):")
            for num, ratio in under_represented[:10]:
                is_birthday = "BD" if num <= 31 else ""
                is_lucky = "LK" if num in LUCKY_NUMBERS else ""
                print(f"  Zahl {num:2d}: {ratio:.1%} {is_birthday} {is_lucky}")

            # Statistik
            over_birthday = sum(1 for n, _ in over_represented if n <= 31)
            under_birthday = sum(1 for n, _ in under_represented if n <= 31)

            print(f"\nBirthday-Zahlen (1-31):")
            print(f"  Ueberrepraesentiert: {over_birthday} von {len(over_represented)}")
            print(f"  Unterrepraesentiert: {under_birthday} von {len(under_represented)}")

            results['keno_typ10'] = {
                'over_represented': over_represented[:10],
                'under_represented': under_represented[:10],
                'over_birthday_count': over_birthday,
                'under_birthday_count': under_birthday,
            }

    # Lotto Jackpot-Zahlen
    lotto_jackpots = lotto_df[lotto_df['jackpot'] > 0]

    if len(lotto_jackpots) > 0:
        jp_counter = Counter()
        for nums in lotto_jackpots['numbers']:
            jp_counter.update(nums)

        all_counter = Counter()
        for nums in lotto_df['numbers']:
            all_counter.update(nums)

        jp_total = sum(jp_counter.values())
        all_total = sum(all_counter.values())

        print(f"\n--- LOTTO Jackpot Einzelzahlen ({len(lotto_jackpots)} Jackpots) ---")

        over_represented = []
        under_represented = []

        for num in range(1, 50):
            jp_freq = jp_counter.get(num, 0) / jp_total if jp_total > 0 else 0
            all_freq = all_counter.get(num, 0) / all_total if all_total > 0 else 0

            if all_freq > 0:
                ratio = jp_freq / all_freq
                if ratio > 1.3:
                    over_represented.append((num, ratio))
                elif ratio < 0.7:
                    under_represented.append((num, ratio))

        over_represented.sort(key=lambda x: x[1], reverse=True)
        under_represented.sort(key=lambda x: x[1])

        print("\nUeberrepraesentiert bei Jackpots (>130%):")
        for num, ratio in over_represented[:10]:
            is_birthday = "BD" if num <= 31 else ""
            is_lucky = "LK" if num in LUCKY_NUMBERS else ""
            print(f"  Zahl {num:2d}: {ratio:.1%} {is_birthday} {is_lucky}")

        print("\nUnterrepraesentiert bei Jackpots (<70%):")
        for num, ratio in under_represented[:10]:
            is_birthday = "BD" if num <= 31 else ""
            is_lucky = "LK" if num in LUCKY_NUMBERS else ""
            print(f"  Zahl {num:2d}: {ratio:.1%} {is_birthday} {is_lucky}")

        # Statistik
        over_birthday = sum(1 for n, _ in over_represented if n <= 31)
        under_birthday = sum(1 for n, _ in under_represented if n <= 31)

        over_high = sum(1 for n, _ in over_represented if n > 31)
        under_high = sum(1 for n, _ in under_represented if n > 31)

        print(f"\nBirthday-Zahlen (1-31):")
        print(f"  Ueberrepraesentiert: {over_birthday} von {len(over_represented)}")
        print(f"  Unterrepraesentiert: {under_birthday} von {len(under_represented)}")

        print(f"\nHohe Zahlen (32-49):")
        print(f"  Ueberrepraesentiert: {over_high} von {len(over_represented)}")
        print(f"  Unterrepraesentiert: {under_high} von {len(under_represented)}")

        results['lotto_jackpot'] = {
            'over_represented': over_represented[:10],
            'under_represented': under_represented[:10],
            'over_birthday_count': over_birthday,
            'under_birthday_count': under_birthday,
            'over_high_count': over_high,
            'under_high_count': under_high,
        }

    return results


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("JACKPOT & HOCHGEWINN-ANALYSE")
    print("=" * 60)
    print("\nHypothese: Bei hohen Gewinnen werden populaere Zahlen VERMIEDEN")

    # Output-Verzeichnis
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Daten laden
    print("\nLade Daten...")
    keno_df = load_keno_data(KENO_PATH)
    print(f"  KENO Ziehungen: {len(keno_df)}")

    lotto_df = load_lotto_data(LOTTO_PATH)
    print(f"  Lotto Ziehungen: {len(lotto_df)}")

    # Lade Gewinnquoten fuer High-Win Detection
    try:
        keno_gq = load_keno_gq(KENO_GQ_PATH)
        print(f"  KENO GQ 2022-2024: {len(keno_gq)}")
    except Exception as e:
        print(f"  KENO GQ 2022-2024: Fehler - {e}")
        keno_gq = pd.DataFrame()

    try:
        keno_gq_2025 = load_keno_gq(KENO_GQ_2025_PATH)
        print(f"  KENO GQ 2025: {len(keno_gq_2025)}")
        # Kombiniere
        if not keno_gq.empty:
            keno_gq = pd.concat([keno_gq, keno_gq_2025], ignore_index=True)
        else:
            keno_gq = keno_gq_2025
    except Exception as e:
        print(f"  KENO GQ 2025: Fehler - {e}")

    all_results = {}

    # Finde High-Win Daten
    print("\nSuche Hochgewinn-Ziehungen...")
    high_win_dates = find_high_win_dates_keno(keno_gq)

    for key, dates in high_win_dates.items():
        print(f"  {key}: {len(dates)} Ziehungen")

    # KENO Analyse
    all_results['keno'] = analyze_keno_high_wins(keno_df, high_win_dates)

    # Lotto Analyse
    all_results['lotto'] = analyze_lotto_high_wins(lotto_df)

    # Einzelzahlen-Analyse
    all_results['einzelzahlen'] = analyze_specific_numbers_in_jackpots(
        keno_df, lotto_df, high_win_dates
    )

    # Speichern
    output_file = OUTPUT_DIR / "high_wins_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n\nErgebnisse gespeichert: {output_file}")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)

    print("\nKERN-FRAGE: Werden Birthday/Lucky-Zahlen bei Jackpots vermieden?")

    # KENO Ergebnis
    if 'typ10_10' in all_results.get('keno', {}):
        keno_result = all_results['keno']['typ10_10']
        comp = keno_result.get('comparison', {})
        print(f"\nKENO Typ10/10 (Jackpot):")
        print(f"  Birthday-Differenz: {comp.get('birthday_difference_pct', 0):+.1f}%")
        print(f"  → {'VERMIEDEN' if comp.get('birthday_avoided') else 'NICHT vermieden'}")

    # Lotto Ergebnis
    if 'jackpot' in all_results.get('lotto', {}):
        lotto_result = all_results['lotto']['jackpot']
        comp = lotto_result.get('comparison', {})
        print(f"\nLOTTO Jackpot:")
        print(f"  Birthday-Differenz: {comp.get('birthday_difference_pct', 0):+.1f}%")
        print(f"  High-Numbers-Differenz: {comp.get('low_high_difference_pct', 0):+.1f}%")
        print(f"  → Birthday {'VERMIEDEN' if comp.get('birthday_avoided') else 'NICHT vermieden'}")
        print(f"  → High Numbers {'BEVORZUGT' if comp.get('high_numbers_preferred') else 'NICHT bevorzugt'}")

    return all_results


if __name__ == '__main__':
    main()
