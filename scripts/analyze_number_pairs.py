#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KENO Zahlenpaare-Analyse
========================

Analysiert Zahlenpaare, Trios und Dekaden-Muster in KENO-Ziehungsdaten.

Grundannahme: Das System ist manipuliert. Zahlenpaare die oft zusammen
erscheinen sind vorhersagbarer.
"""

import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from datetime import datetime
import math


def load_keno_data(filepath: str) -> list[dict]:
    """
    Laedt KENO-Ziehungsdaten aus CSV.

    Args:
        filepath: Pfad zur CSV-Datei (Separator: ;)

    Returns:
        Liste von Ziehungen mit Datum und Zahlen
    """
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                # Parse Datum
                datum_str = row.get('Datum', '')
                if datum_str:
                    datum = datetime.strptime(datum_str, '%d.%m.%Y')
                else:
                    continue

                # Parse Zahlen (Keno_Z1 bis Keno_Z20)
                zahlen = []
                for i in range(1, 21):
                    col_name = f'Keno_Z{i}'
                    if col_name in row and row[col_name]:
                        zahlen.append(int(row[col_name]))

                if len(zahlen) == 20:
                    draws.append({
                        'datum': datum,
                        'zahlen': sorted(zahlen)
                    })
            except (ValueError, KeyError) as e:
                continue

    return draws


def calculate_pair_frequencies(draws: list[dict]) -> Counter:
    """
    Berechnet Haeufigkeit aller Zahlenpaare.

    Args:
        draws: Liste von Ziehungen

    Returns:
        Counter mit (z1, z2) -> Anzahl
    """
    pair_counter = Counter()

    for draw in draws:
        zahlen = draw['zahlen']
        # Alle Paare aus den 20 gezogenen Zahlen
        for pair in combinations(zahlen, 2):
            pair_counter[pair] += 1

    return pair_counter


def calculate_trio_frequencies(draws: list[dict]) -> Counter:
    """
    Berechnet Haeufigkeit aller Zahlen-Trios.

    Args:
        draws: Liste von Ziehungen

    Returns:
        Counter mit (z1, z2, z3) -> Anzahl
    """
    trio_counter = Counter()

    for draw in draws:
        zahlen = draw['zahlen']
        # Alle Trios aus den 20 gezogenen Zahlen
        for trio in combinations(zahlen, 3):
            trio_counter[trio] += 1

    return trio_counter


def calculate_expected_pair_frequency(n_draws: int) -> float:
    """
    Berechnet den Erwartungswert fuer Paar-Haeufigkeit.

    Bei KENO werden 20 aus 70 Zahlen gezogen.
    P(beide Zahlen gezogen) = (20/70) * (19/69)
    Erwartungswert = P * n_draws

    Args:
        n_draws: Anzahl Ziehungen

    Returns:
        Erwartete Haeufigkeit pro Paar
    """
    p_pair = (20/70) * (19/69)
    return p_pair * n_draws


def calculate_expected_trio_frequency(n_draws: int) -> float:
    """
    Berechnet den Erwartungswert fuer Trio-Haeufigkeit.

    P(alle drei Zahlen gezogen) = (20/70) * (19/69) * (18/68)

    Args:
        n_draws: Anzahl Ziehungen

    Returns:
        Erwartete Haeufigkeit pro Trio
    """
    p_trio = (20/70) * (19/69) * (18/68)
    return p_trio * n_draws


def get_decade(number: int) -> int:
    """
    Gibt die Dekade einer Zahl zurueck (1-10 -> 1, 11-20 -> 2, etc.)
    """
    return (number - 1) // 10 + 1


def calculate_decade_correlations(draws: list[dict]) -> dict:
    """
    Berechnet Dekaden-Korrelationsmatrix.

    Args:
        draws: Liste von Ziehungen

    Returns:
        Dict mit Dekaden-Statistiken
    """
    decade_pair_counter = Counter()
    decade_counts = Counter()

    for draw in draws:
        zahlen = draw['zahlen']
        # Zaehle Dekaden in dieser Ziehung
        decades_in_draw = [get_decade(z) for z in zahlen]
        decade_counter = Counter(decades_in_draw)

        for d, count in decade_counter.items():
            decade_counts[d] += count

        # Dekaden-Paare (nur verschiedene Dekaden)
        unique_decades = list(set(decades_in_draw))
        for d1, d2 in combinations(sorted(unique_decades), 2):
            decade_pair_counter[(d1, d2)] += 1

    # Korrelationsmatrix als 7x7 Array (Dekaden 1-7)
    matrix = [[0 for _ in range(7)] for _ in range(7)]
    for (d1, d2), count in decade_pair_counter.items():
        matrix[d1-1][d2-1] = count
        matrix[d2-1][d1-1] = count  # Symmetrisch

    return {
        'decade_pair_counts': {f"{k[0]}-{k[1]}": v for k, v in decade_pair_counter.most_common()},
        'decade_totals': dict(decade_counts),
        'correlation_matrix': matrix
    }


def calculate_gap_patterns(draws: list[dict]) -> dict:
    """
    Analysiert Luecken-Muster: Zahlen die nach langer Abwesenheit (>10 Tage) zurueckkehren.

    Args:
        draws: Liste von Ziehungen (chronologisch sortiert)

    Returns:
        Dict mit Luecken-Statistiken
    """
    # Sortiere nach Datum aufsteigend
    sorted_draws = sorted(draws, key=lambda x: x['datum'])

    # Letztes Erscheinen jeder Zahl
    last_seen = {z: -1 for z in range(1, 71)}

    # Sammle Rueckkehrer nach langer Abwesenheit
    returners = []  # (Zahl, Luecke, Rueckkehr-Datum)
    gap_distribution = Counter()  # Verteilung der Luecken

    for i, draw in enumerate(sorted_draws):
        zahlen = draw['zahlen']

        for z in zahlen:
            if last_seen[z] >= 0:
                gap = i - last_seen[z]
                gap_distribution[gap] += 1

                if gap > 10:
                    returners.append({
                        'zahl': z,
                        'luecke': gap,
                        'datum': draw['datum'].strftime('%Y-%m-%d')
                    })

            last_seen[z] = i

    # Analysiere Rueckkehrer-Muster
    returner_counts = Counter(r['zahl'] for r in returners)

    # Zahlen die am haeufigsten nach langer Abwesenheit zurueckkehren
    frequent_returners = returner_counts.most_common(20)

    # Durchschnittliche Luecke pro Zahl
    avg_gaps = {}
    gap_per_number = defaultdict(list)

    for i, draw in enumerate(sorted_draws):
        for z in draw['zahlen']:
            if last_seen[z] >= 0 and last_seen[z] != i:
                # Dies ist redundant, aber berechnen wir nochmal sauber
                pass

    # Berechne Durchschnitt der Luecken > 10 pro Zahl
    long_gaps_per_number = defaultdict(list)
    for r in returners:
        long_gaps_per_number[r['zahl']].append(r['luecke'])

    for z in range(1, 71):
        if long_gaps_per_number[z]:
            avg_gaps[z] = sum(long_gaps_per_number[z]) / len(long_gaps_per_number[z])

    return {
        'total_long_gaps': len(returners),
        'frequent_returners': [{'zahl': z, 'count': c} for z, c in frequent_returners],
        'gap_distribution': {str(k): v for k, v in sorted(gap_distribution.items())[:50]},
        'avg_long_gap_per_number': {str(k): round(v, 2) for k, v in sorted(avg_gaps.items(), key=lambda x: -x[1])[:20]}
    }


def analyze_consecutive_pairs(draws: list[dict]) -> dict:
    """
    Analysiert aufeinanderfolgende Zahlenpaare (z.B. 5-6, 23-24).
    """
    consecutive_counter = Counter()

    for draw in draws:
        zahlen = sorted(draw['zahlen'])
        for i in range(len(zahlen) - 1):
            if zahlen[i+1] - zahlen[i] == 1:
                consecutive_counter[(zahlen[i], zahlen[i+1])] += 1

    return {
        'consecutive_pairs': [
            {'pair': list(p), 'count': c}
            for p, c in consecutive_counter.most_common(30)
        ]
    }


def main():
    # Pfade
    data_path = Path("C:/Users/kenfu/Documents/keno_base/data/raw/keno/KENO_ab_2018.csv")
    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/number_pairs_analysis.json")

    # Stelle sicher, dass Output-Verzeichnis existiert
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Lade KENO-Daten von {data_path}...")
    draws = load_keno_data(data_path)
    n_draws = len(draws)
    print(f"Geladen: {n_draws} Ziehungen")

    # A) PAAR-FREQUENZ
    print("\nBerechne Paar-Frequenzen...")
    pair_freq = calculate_pair_frequencies(draws)
    expected_pair = calculate_expected_pair_frequency(n_draws)
    print(f"Erwartungswert pro Paar: {expected_pair:.2f}")

    # Top 100 Paare
    top_pairs = []
    for pair, count in pair_freq.most_common(100):
        deviation = count - expected_pair
        deviation_pct = (deviation / expected_pair) * 100
        top_pairs.append({
            'pair': list(pair),
            'frequency': count,
            'expected': round(expected_pair, 2),
            'deviation': round(deviation, 2),
            'deviation_percent': round(deviation_pct, 2)
        })

    # Paare ueber Erwartung
    pairs_above_expected = [p for p in top_pairs if p['deviation'] > 0]
    print(f"Paare ueber Erwartung in Top 100: {len(pairs_above_expected)}")

    # B) TRIO-FREQUENZ
    print("\nBerechne Trio-Frequenzen...")
    trio_freq = calculate_trio_frequencies(draws)
    expected_trio = calculate_expected_trio_frequency(n_draws)
    print(f"Erwartungswert pro Trio: {expected_trio:.2f}")

    # Top 20 Trios
    top_trios = []
    for trio, count in trio_freq.most_common(20):
        deviation = count - expected_trio
        deviation_pct = (deviation / expected_trio) * 100
        top_trios.append({
            'trio': list(trio),
            'frequency': count,
            'expected': round(expected_trio, 2),
            'deviation': round(deviation, 2),
            'deviation_percent': round(deviation_pct, 2)
        })

    # C) DEKADEN-MUSTER
    print("\nBerechne Dekaden-Korrelationen...")
    decade_data = calculate_decade_correlations(draws)

    # D) LUECKEN-MUSTER
    print("\nAnalysiere Luecken-Muster...")
    gap_data = calculate_gap_patterns(draws)

    # Bonus: Aufeinanderfolgende Paare
    print("\nAnalysiere aufeinanderfolgende Paare...")
    consecutive_data = analyze_consecutive_pairs(draws)

    # Statistiken
    total_pairs = len(pair_freq)  # 2415 moeglich (70 choose 2)
    total_trios = len(trio_freq)  # 54834 moeglich (70 choose 3)

    # Zusammenfassung
    result = {
        'metadata': {
            'data_source': str(data_path),
            'n_draws': n_draws,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'expected_pair_frequency': round(expected_pair, 2),
            'expected_trio_frequency': round(expected_trio, 2),
            'total_possible_pairs': 2415,
            'total_possible_trios': 54834
        },
        'pair_analysis': {
            'top_100_pairs': top_pairs,
            'pairs_above_expected_count': len(pairs_above_expected),
            'max_deviation_percent': max(p['deviation_percent'] for p in top_pairs) if top_pairs else 0,
            'statistics': {
                'max_frequency': pair_freq.most_common(1)[0][1] if pair_freq else 0,
                'min_frequency': min(pair_freq.values()) if pair_freq else 0,
                'avg_frequency': round(sum(pair_freq.values()) / len(pair_freq), 2) if pair_freq else 0
            }
        },
        'trio_analysis': {
            'top_20_trios': top_trios,
            'max_deviation_percent': max(t['deviation_percent'] for t in top_trios) if top_trios else 0
        },
        'decade_analysis': decade_data,
        'gap_analysis': gap_data,
        'consecutive_pairs': consecutive_data
    }

    # Speichern
    print(f"\nSpeichere Ergebnisse nach {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Ausgabe der wichtigsten Ergebnisse
    print("\n" + "="*60)
    print("ZUSAMMENFASSUNG")
    print("="*60)

    print(f"\nZiehungen analysiert: {n_draws}")
    print(f"Erwartungswert Paar: {expected_pair:.2f}")
    print(f"Erwartungswert Trio: {expected_trio:.2f}")

    print("\n--- TOP 10 PAARE ---")
    for i, p in enumerate(top_pairs[:10], 1):
        print(f"{i:2}. {p['pair'][0]:2}-{p['pair'][1]:2}: {p['frequency']}x "
              f"(+{p['deviation']:.1f}, +{p['deviation_percent']:.1f}%)")

    print("\n--- TOP 10 TRIOS ---")
    for i, t in enumerate(top_trios[:10], 1):
        print(f"{i:2}. {t['trio'][0]:2}-{t['trio'][1]:2}-{t['trio'][2]:2}: {t['frequency']}x "
              f"(+{t['deviation']:.1f}, +{t['deviation_percent']:.1f}%)")

    print("\n--- DEKADEN-HAEUFIGKEIT ---")
    for d, count in sorted(decade_data['decade_totals'].items()):
        print(f"Dekade {d} ({(d-1)*10+1:2}-{d*10:2}): {count}x")

    print("\n--- HAEUFIGSTE RUECKKEHRER (nach >10 Tagen Pause) ---")
    for r in gap_data['frequent_returners'][:10]:
        print(f"Zahl {r['zahl']:2}: {r['count']}x")

    print(f"\nErgebnisse gespeichert: {output_path}")

    return result


if __name__ == '__main__':
    main()
