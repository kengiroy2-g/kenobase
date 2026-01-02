#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Consecutive Number Avoidance Analysis for KENO

Hypothese: Das KENO-System vermeidet zu viele aufeinanderfolgende Zahlen,
um "zufällig" auszusehen.

Analysiert:
1. Häufigkeit von 2er-Sequenzen (consecutive pairs)
2. Häufigkeit von 3er-Sequenzen
3. Maximale Sequenzlängen
4. Vergleich mit zufälliger Erwartung (Monte-Carlo)
"""

import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime
import math

# KENO Konfiguration
KENO_NUMBERS = 70  # Zahlen 1-70
DRAW_SIZE = 20     # 20 Zahlen pro Ziehung


def load_keno_data(filepath: str) -> list[list[int]]:
    """Lädt KENO-Ziehungsdaten aus CSV."""
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # Skip header

        for row in reader:
            if len(row) >= 21:
                try:
                    # Zahlen sind in Spalten 1-20 (Index 1-20)
                    numbers = [int(row[i]) for i in range(1, 21)]
                    numbers.sort()
                    draws.append(numbers)
                except (ValueError, IndexError):
                    continue

    return draws


def find_consecutive_sequences(draw: list[int]) -> dict:
    """
    Findet alle aufeinanderfolgenden Sequenzen in einer Ziehung.

    Returns:
        dict mit:
        - pairs: Liste von 2er-Sequenzen (Start, Ende)
        - triplets: Liste von 3er-Sequenzen
        - max_length: Maximale Sequenzlänge
        - all_sequences: Alle Sequenzen mit Länge >= 2
    """
    sorted_draw = sorted(draw)
    sequences = []
    current_seq = [sorted_draw[0]]

    for i in range(1, len(sorted_draw)):
        if sorted_draw[i] == sorted_draw[i-1] + 1:
            current_seq.append(sorted_draw[i])
        else:
            if len(current_seq) >= 2:
                sequences.append(current_seq)
            current_seq = [sorted_draw[i]]

    # Letzte Sequenz prüfen
    if len(current_seq) >= 2:
        sequences.append(current_seq)

    # Sequenzen kategorisieren
    pairs = [s for s in sequences if len(s) == 2]
    triplets = [s for s in sequences if len(s) == 3]
    quadruplets = [s for s in sequences if len(s) == 4]
    longer = [s for s in sequences if len(s) >= 5]

    max_len = max([len(s) for s in sequences]) if sequences else 0

    return {
        'pairs': pairs,
        'triplets': triplets,
        'quadruplets': quadruplets,
        'longer': longer,
        'max_length': max_len,
        'all_sequences': sequences
    }


def count_all_consecutive_pairs(draw: list[int]) -> list[tuple[int, int]]:
    """
    Zählt alle möglichen konsekutiven Paare (n, n+1) in einer Ziehung.
    Ein Trio (1,2,3) enthält 2 Paare: (1,2) und (2,3).
    """
    sorted_draw = sorted(draw)
    pairs = []

    for i in range(len(sorted_draw) - 1):
        if sorted_draw[i+1] == sorted_draw[i] + 1:
            pairs.append((sorted_draw[i], sorted_draw[i+1]))

    return pairs


def calculate_expected_pairs_probability():
    """
    Berechnet die erwartete Anzahl von konsekutiven Paaren bei zufälliger Ziehung.

    Bei KENO: 20 aus 70 Zahlen

    Für jedes mögliche Paar (n, n+1) mit n in [1, 69]:
    P(beide gezogen) = C(68, 18) / C(70, 20)

    Erwartete Anzahl Paare = 69 * P(beide)
    """
    from math import comb

    # Anzahl möglicher konsekutiver Paare: (1,2), (2,3), ..., (69,70) = 69 Paare
    num_possible_pairs = 69

    # Wahrscheinlichkeit, dass ein bestimmtes Paar (n, n+1) beide gezogen werden
    # P = C(68, 18) / C(70, 20)
    p_pair = comb(68, 18) / comb(70, 20)

    # Erwartete Anzahl = 69 * p_pair
    expected = num_possible_pairs * p_pair

    return expected, p_pair, num_possible_pairs


def calculate_expected_triplets_probability():
    """
    Berechnet die erwartete Anzahl von 3er-Sequenzen bei zufälliger Ziehung.

    Für jedes mögliche Triplet (n, n+1, n+2) mit n in [1, 68]:
    P(alle drei gezogen) = C(67, 17) / C(70, 20)
    """
    from math import comb

    num_possible_triplets = 68
    p_triplet = comb(67, 17) / comb(70, 20)
    expected = num_possible_triplets * p_triplet

    return expected, p_triplet, num_possible_triplets


def monte_carlo_simulation(n_simulations: int = 100000) -> dict:
    """
    Monte-Carlo-Simulation für zufällige KENO-Ziehungen.
    Berechnet erwartete Verteilung von Sequenzen.
    """
    pair_counts = []
    triplet_counts = []
    quadruplet_counts = []
    max_lengths = []
    sequence_length_dist = Counter()

    for _ in range(n_simulations):
        # Zufällige Ziehung: 20 aus 70
        draw = sorted(random.sample(range(1, 71), 20))

        # Sequenzen finden
        result = find_consecutive_sequences(draw)

        # Zählen
        n_pairs = len(result['pairs']) + 2 * len(result['triplets']) + \
                  3 * len(result['quadruplets']) + sum(len(s)-1 for s in result['longer'])
        # Eigentlich: Anzahl der konsekutiven Paare (überlappend gezählt)
        all_pairs = count_all_consecutive_pairs(draw)

        pair_counts.append(len(all_pairs))
        triplet_counts.append(len(result['triplets']) + len(result['quadruplets']) + len(result['longer']))
        quadruplet_counts.append(len(result['quadruplets']) + len(result['longer']))
        max_lengths.append(result['max_length'])

        for seq in result['all_sequences']:
            sequence_length_dist[len(seq)] += 1

    # Max-Längen-Verteilung
    max_len_dist = Counter(max_lengths)

    return {
        'mean_pairs': sum(pair_counts) / n_simulations,
        'std_pairs': (sum((x - sum(pair_counts)/n_simulations)**2 for x in pair_counts) / n_simulations) ** 0.5,
        'mean_triplets': sum(triplet_counts) / n_simulations,
        'mean_quadruplets': sum(quadruplet_counts) / n_simulations,
        'mean_max_length': sum(max_lengths) / n_simulations,
        'max_length_distribution': dict(sorted(max_len_dist.items())),
        'sequence_length_distribution': dict(sorted(sequence_length_dist.items())),
        'pair_distribution': dict(Counter(pair_counts)),
        'n_simulations': n_simulations
    }


def analyze_real_data(draws: list[list[int]]) -> dict:
    """Analysiert die echten KENO-Daten."""
    all_pairs = []
    pair_counts_per_draw = []
    triplet_counts_per_draw = []
    quadruplet_counts_per_draw = []
    max_lengths = []
    sequence_details = []
    specific_pair_counts = Counter()

    for i, draw in enumerate(draws):
        pairs = count_all_consecutive_pairs(draw)
        all_pairs.extend(pairs)
        pair_counts_per_draw.append(len(pairs))

        result = find_consecutive_sequences(draw)
        triplet_counts_per_draw.append(len(result['triplets']))
        quadruplet_counts_per_draw.append(len(result['quadruplets']) + len(result['longer']))
        max_lengths.append(result['max_length'])

        # Spezifische Paare zählen
        for p in pairs:
            specific_pair_counts[p] += 1

        # Detail für außergewöhnliche Ziehungen
        if result['max_length'] >= 4:
            sequence_details.append({
                'draw_index': i,
                'max_length': result['max_length'],
                'sequences': result['all_sequences']
            })

    # Max-Längen-Verteilung
    max_len_dist = Counter(max_lengths)
    pair_count_dist = Counter(pair_counts_per_draw)

    # Top häufigste konsekutive Paare
    top_pairs = specific_pair_counts.most_common(20)

    return {
        'total_draws': len(draws),
        'total_consecutive_pairs': len(all_pairs),
        'mean_pairs_per_draw': sum(pair_counts_per_draw) / len(draws),
        'std_pairs_per_draw': (sum((x - sum(pair_counts_per_draw)/len(draws))**2 for x in pair_counts_per_draw) / len(draws)) ** 0.5,
        'total_triplets': sum(triplet_counts_per_draw),
        'mean_triplets_per_draw': sum(triplet_counts_per_draw) / len(draws),
        'total_quadruplets_or_longer': sum(quadruplet_counts_per_draw),
        'max_length_ever': max(max_lengths),
        'mean_max_length': sum(max_lengths) / len(draws),
        'max_length_distribution': dict(sorted(max_len_dist.items())),
        'pair_count_distribution': dict(sorted(pair_count_dist.items())),
        'top_consecutive_pairs': top_pairs,
        'exceptional_draws': sequence_details[:20]  # Erste 20 mit langen Sequenzen
    }


def statistical_test(observed: float, expected: float, std_expected: float, n: int) -> dict:
    """
    Führt einen Z-Test durch.
    """
    if std_expected == 0:
        z_score = 0
    else:
        z_score = (observed - expected) / (std_expected / math.sqrt(n))

    # Einfache p-Wert Approximation (einseitig, für observed < expected)
    # Für genauere Berechnung: scipy.stats.norm.sf(abs(z_score))

    return {
        'observed': observed,
        'expected': expected,
        'std_expected': std_expected,
        'z_score': z_score,
        'interpretation': 'UNTERREPRÄSENTIERT' if z_score < -1.96 else
                         ('ÜBERREPRÄSENTIERT' if z_score > 1.96 else 'NORMAL')
    }


def main():
    # Pfade
    data_path = Path(r"C:\Users\kenfu\Documents\keno_base\data\raw\keno\KENO_ab_2022_bereinigt.csv")
    results_path = Path(r"C:\Users\kenfu\Documents\keno_base\results\think_tank_consecutive.json")

    print("=" * 70)
    print("KENO CONSECUTIVE NUMBER AVOIDANCE ANALYSIS")
    print("=" * 70)
    print()

    # 1. Daten laden
    print("[1] Lade KENO-Daten...")
    draws = load_keno_data(str(data_path))
    print(f"    Geladen: {len(draws)} Ziehungen")
    print()

    # 2. Theoretische Erwartung berechnen
    print("[2] Berechne theoretische Erwartung...")
    exp_pairs, p_pair, n_pairs = calculate_expected_pairs_probability()
    exp_triplets, p_triplet, n_triplets = calculate_expected_triplets_probability()

    print(f"    Erwartete konsekutive Paare pro Ziehung: {exp_pairs:.4f}")
    print(f"    P(spezifisches Paar beide gezogen): {p_pair:.6f}")
    print(f"    Erwartete Triplets pro Ziehung: {exp_triplets:.4f}")
    print()

    # 3. Monte-Carlo-Simulation
    print("[3] Monte-Carlo-Simulation (100.000 Iterationen)...")
    mc_results = monte_carlo_simulation(100000)
    print(f"    MC Erwartete Paare pro Ziehung: {mc_results['mean_pairs']:.4f} (σ={mc_results['std_pairs']:.4f})")
    print(f"    MC Erwartete Triplets pro Ziehung: {mc_results['mean_triplets']:.4f}")
    print(f"    MC Erwartete max. Sequenzlänge: {mc_results['mean_max_length']:.2f}")
    print()

    # 4. Echte Daten analysieren
    print("[4] Analysiere echte KENO-Daten...")
    real_results = analyze_real_data(draws)
    print(f"    Beobachtete Paare pro Ziehung: {real_results['mean_pairs_per_draw']:.4f} (σ={real_results['std_pairs_per_draw']:.4f})")
    print(f"    Beobachtete Triplets pro Ziehung: {real_results['mean_triplets_per_draw']:.4f}")
    print(f"    Maximale je beobachtete Sequenzlänge: {real_results['max_length_ever']}")
    print()

    # 5. Statistische Tests
    print("[5] Statistische Auswertung...")

    # Z-Test für Paare
    pair_test = statistical_test(
        real_results['mean_pairs_per_draw'],
        mc_results['mean_pairs'],
        mc_results['std_pairs'],
        real_results['total_draws']
    )

    print(f"\n    KONSEKUTIVE PAARE:")
    print(f"    Beobachtet: {pair_test['observed']:.4f}")
    print(f"    Erwartet:   {pair_test['expected']:.4f}")
    print(f"    Z-Score:    {pair_test['z_score']:.2f}")
    print(f"    → {pair_test['interpretation']}")

    # Abweichung in Prozent
    deviation_pairs = ((real_results['mean_pairs_per_draw'] - mc_results['mean_pairs']) / mc_results['mean_pairs']) * 100
    print(f"    Abweichung: {deviation_pairs:+.2f}%")

    # Triplets
    deviation_triplets = ((real_results['mean_triplets_per_draw'] - mc_results['mean_triplets']) / mc_results['mean_triplets']) * 100 if mc_results['mean_triplets'] > 0 else 0
    print(f"\n    3er-SEQUENZEN:")
    print(f"    Beobachtet: {real_results['mean_triplets_per_draw']:.4f}")
    print(f"    Erwartet:   {mc_results['mean_triplets']:.4f}")
    print(f"    Abweichung: {deviation_triplets:+.2f}%")

    # Max-Längen-Analyse
    print(f"\n    MAX-SEQUENZLÄNGEN-VERTEILUNG:")
    print(f"    {'Länge':<10} {'Beobachtet':<15} {'MC-Erwartet':<15}")
    print(f"    {'-'*40}")

    for length in range(0, max(max(real_results['max_length_distribution'].keys(), default=0),
                               max(mc_results['max_length_distribution'].keys(), default=0)) + 1):
        obs = real_results['max_length_distribution'].get(length, 0)
        exp = mc_results['max_length_distribution'].get(length, 0)
        exp_pct = exp / mc_results['n_simulations'] * 100
        obs_pct = obs / real_results['total_draws'] * 100
        print(f"    {length:<10} {obs:>6} ({obs_pct:>5.1f}%)    {exp:>6} ({exp_pct:>5.1f}%)")

    # 6. Hypothesen-Bewertung
    print("\n" + "=" * 70)
    print("HYPOTHESEN-BEWERTUNG")
    print("=" * 70)

    # Kriterien für "Vermeidung"
    avoidance_score = 0
    findings = []

    # Kriterium 1: Weniger Paare als erwartet?
    if deviation_pairs < -5:
        avoidance_score += 2
        findings.append(f"✓ Deutlich weniger 2er-Sequenzen ({deviation_pairs:+.2f}%)")
    elif deviation_pairs < -2:
        avoidance_score += 1
        findings.append(f"○ Leicht weniger 2er-Sequenzen ({deviation_pairs:+.2f}%)")
    else:
        findings.append(f"✗ 2er-Sequenzen im Normalbereich ({deviation_pairs:+.2f}%)")

    # Kriterium 2: Weniger Triplets als erwartet?
    if deviation_triplets < -10:
        avoidance_score += 2
        findings.append(f"✓ Deutlich weniger 3er-Sequenzen ({deviation_triplets:+.2f}%)")
    elif deviation_triplets < -5:
        avoidance_score += 1
        findings.append(f"○ Leicht weniger 3er-Sequenzen ({deviation_triplets:+.2f}%)")
    else:
        findings.append(f"✗ 3er-Sequenzen im Normalbereich ({deviation_triplets:+.2f}%)")

    # Kriterium 3: Maximale Sequenzlänge begrenzt?
    max_len_ever = real_results['max_length_ever']
    # Bei 1456 Ziehungen: erwarten wir gelegentlich 5er oder 6er Sequenzen
    if max_len_ever <= 4:
        avoidance_score += 2
        findings.append(f"✓ Max. Sequenzlänge auf {max_len_ever} begrenzt (verdächtig!)")
    elif max_len_ever <= 5:
        avoidance_score += 1
        findings.append(f"○ Max. Sequenzlänge {max_len_ever} (evtl. eingeschränkt)")
    else:
        findings.append(f"✗ Max. Sequenzlänge {max_len_ever} (normal)")

    print("\nKriterien-Prüfung:")
    for f in findings:
        print(f"  {f}")

    print(f"\nGesamt-Score: {avoidance_score}/6")

    if avoidance_score >= 4:
        verdict = "HYPOTHESE BESTÄTIGT: Das System vermeidet systematisch konsekutive Sequenzen!"
        recommendation = "EMPFEHLUNG: Keine konsekutiven Zahlen spielen!"
    elif avoidance_score >= 2:
        verdict = "HYPOTHESE TEILWEISE BESTÄTIGT: Leichte Tendenz zur Vermeidung erkennbar."
        recommendation = "EMPFEHLUNG: Konsekutive Zahlen vorsichtig einsetzen."
    else:
        verdict = "HYPOTHESE NICHT BESTÄTIGT: Keine signifikante Vermeidung von Sequenzen."
        recommendation = "EMPFEHLUNG: Konsekutive Zahlen spielen wie beliebige andere."

    print(f"\n>>> {verdict}")
    print(f">>> {recommendation}")

    # 7. Ergebnisse speichern
    results = {
        'analysis_date': datetime.now().isoformat(),
        'hypothesis': 'Consecutive Number Avoidance',
        'description': 'Das KENO-System vermeidet zu viele aufeinanderfolgende Zahlen um zufällig auszusehen.',
        'data_source': str(data_path),
        'total_draws': real_results['total_draws'],

        'theoretical_expectation': {
            'expected_pairs_per_draw': exp_pairs,
            'expected_triplets_per_draw': exp_triplets,
            'probability_specific_pair': p_pair,
            'probability_specific_triplet': p_triplet
        },

        'monte_carlo_simulation': {
            'n_simulations': mc_results['n_simulations'],
            'mean_pairs_per_draw': mc_results['mean_pairs'],
            'std_pairs_per_draw': mc_results['std_pairs'],
            'mean_triplets_per_draw': mc_results['mean_triplets'],
            'mean_quadruplets_per_draw': mc_results['mean_quadruplets'],
            'mean_max_sequence_length': mc_results['mean_max_length'],
            'max_length_distribution': mc_results['max_length_distribution'],
            'pair_count_distribution': mc_results['pair_distribution']
        },

        'observed_data': {
            'mean_pairs_per_draw': real_results['mean_pairs_per_draw'],
            'std_pairs_per_draw': real_results['std_pairs_per_draw'],
            'total_consecutive_pairs': real_results['total_consecutive_pairs'],
            'mean_triplets_per_draw': real_results['mean_triplets_per_draw'],
            'total_triplets': real_results['total_triplets'],
            'total_quadruplets_or_longer': real_results['total_quadruplets_or_longer'],
            'max_sequence_length_ever': real_results['max_length_ever'],
            'mean_max_sequence_length': real_results['mean_max_length'],
            'max_length_distribution': real_results['max_length_distribution'],
            'pair_count_distribution': real_results['pair_count_distribution'],
            'top_20_consecutive_pairs': [(f"{p[0]}-{p[0]+1}", c) for p, c in real_results['top_consecutive_pairs']],
            'exceptional_draws_with_long_sequences': real_results['exceptional_draws']
        },

        'statistical_comparison': {
            'pairs': {
                'observed': real_results['mean_pairs_per_draw'],
                'expected': mc_results['mean_pairs'],
                'deviation_percent': deviation_pairs,
                'z_score': pair_test['z_score'],
                'interpretation': pair_test['interpretation']
            },
            'triplets': {
                'observed': real_results['mean_triplets_per_draw'],
                'expected': mc_results['mean_triplets'],
                'deviation_percent': deviation_triplets
            },
            'max_sequence_length': {
                'observed_max': real_results['max_length_ever'],
                'observed_mean': real_results['mean_max_length'],
                'expected_mean': mc_results['mean_max_length']
            }
        },

        'hypothesis_evaluation': {
            'avoidance_score': avoidance_score,
            'max_possible_score': 6,
            'criteria_results': findings,
            'verdict': verdict,
            'recommendation': recommendation
        },

        'strategic_implications': {
            'should_play_consecutive_pairs': avoidance_score < 2,
            'max_consecutive_to_play': 2 if avoidance_score >= 4 else (3 if avoidance_score >= 2 else 'any'),
            'reasoning': 'Wenn das System Sequenzen vermeidet, sollten wir auch keine spielen.'
        }
    }

    # JSON speichern
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[*] Ergebnisse gespeichert: {results_path}")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
