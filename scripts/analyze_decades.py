#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Think Tank Analyse: Decade Distribution Constraint

Hypothese: Das KENO-System stellt sicher, dass jede Dekade (1-10, 11-20, ..., 61-70)
fair vertreten ist. Bei Zufall: 20 Zahlen aus 70 => 20/7 ~ 2.86 pro Dekade.

Analysiert:
1. Dekaden-Verteilungen pro Ziehung
2. Haeufigkeit verschiedener Verteilungsmuster
3. "Verbotene" Verteilungen (z.B. 0 aus einer Dekade)
4. Korrelationen zwischen Dekaden
"""

import json
import pandas as pd
import numpy as np
from collections import Counter
from pathlib import Path
from itertools import combinations
from scipy import stats

def get_decade(number: int) -> int:
    """Gibt die Dekade (0-6) fuer eine Zahl 1-70 zurueck."""
    return (number - 1) // 10

def analyze_decades(csv_path: str, output_path: str) -> dict:
    """
    Hauptanalyse der Dekaden-Verteilung.

    Args:
        csv_path: Pfad zur KENO-CSV
        output_path: Pfad fuer JSON-Output

    Returns:
        Analyse-Ergebnis als Dictionary
    """
    # Daten laden
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')

    # Zahlen-Spalten identifizieren
    number_cols = [f'Keno_Z{i}' for i in range(1, 21)]

    # Dekaden-Namen
    decade_names = ['1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70']

    # Analysevariablen
    distribution_patterns = []
    decade_counts_per_draw = []
    decade_correlations = np.zeros((7, 7))

    # Pro Ziehung analysieren
    for idx, row in df.iterrows():
        numbers = [row[col] for col in number_cols if pd.notna(row[col])]

        # Dekaden zaehlen
        decade_count = [0] * 7
        for num in numbers:
            decade = get_decade(int(num))
            decade_count[decade] += 1

        decade_counts_per_draw.append(decade_count)

        # Pattern als String (sortiert absteigend)
        pattern = '-'.join(map(str, sorted(decade_count, reverse=True)))
        distribution_patterns.append(tuple(decade_count))

    # In numpy array konvertieren fuer Statistik
    decade_matrix = np.array(decade_counts_per_draw)
    n_draws = len(decade_matrix)

    # 1. Grundstatistik pro Dekade
    decade_stats = {}
    for i, name in enumerate(decade_names):
        counts = decade_matrix[:, i]
        decade_stats[name] = {
            'mean': float(np.mean(counts)),
            'std': float(np.std(counts)),
            'min': int(np.min(counts)),
            'max': int(np.max(counts)),
            'expected': 20/7,  # ~2.857
            'deviation_from_expected': float(np.mean(counts) - 20/7)
        }

    # 2. Verteilungsmuster zaehlen
    pattern_counter = Counter()
    for dc in decade_counts_per_draw:
        # Pattern: sortierte Verteilung (unabhaengig von Dekade)
        sorted_pattern = tuple(sorted(dc, reverse=True))
        pattern_counter[sorted_pattern] += 1

    # Top Patterns
    top_patterns = pattern_counter.most_common(30)
    pattern_analysis = {
        '-'.join(map(str, p)): {
            'count': c,
            'frequency': c / n_draws,
            'percentage': round(c / n_draws * 100, 2)
        }
        for p, c in top_patterns
    }

    # 3. Spezifische Dekaden-Verteilungen (exakte Positionen)
    exact_distribution_counter = Counter()
    for dc in decade_counts_per_draw:
        exact_distribution_counter[tuple(dc)] += 1

    # Top exakte Verteilungen
    top_exact = exact_distribution_counter.most_common(50)
    exact_analysis = {
        '-'.join(map(str, p)): {
            'count': c,
            'frequency': c / n_draws,
            'percentage': round(c / n_draws * 100, 2)
        }
        for p, c in top_exact
    }

    # 4. "Verbotene" Verteilungen: Ziehungen mit 0 in einer Dekade
    zero_decade_analysis = {name: 0 for name in decade_names}
    for dc in decade_counts_per_draw:
        for i, count in enumerate(dc):
            if count == 0:
                zero_decade_analysis[decade_names[i]] += 1

    zero_decade_freq = {
        k: {
            'count': v,
            'frequency': v / n_draws,
            'percentage': round(v / n_draws * 100, 2)
        }
        for k, v in zero_decade_analysis.items()
    }

    # 5. Multiple Zeros: Wie oft mehrere Dekaden = 0
    multi_zero_counter = Counter()
    for dc in decade_counts_per_draw:
        num_zeros = dc.count(0)
        multi_zero_counter[num_zeros] += 1

    multi_zero_analysis = {
        f'{k}_decades_empty': {
            'count': v,
            'frequency': v / n_draws,
            'percentage': round(v / n_draws * 100, 2)
        }
        for k, v in sorted(multi_zero_counter.items())
    }

    # 6. Korrelation zwischen Dekaden (wenn eine Dekade viele hat, haben andere weniger)
    correlation_matrix = np.corrcoef(decade_matrix.T)
    correlation_analysis = {}
    for i, name_i in enumerate(decade_names):
        correlation_analysis[name_i] = {}
        for j, name_j in enumerate(decade_names):
            if i != j:
                correlation_analysis[name_i][name_j] = round(correlation_matrix[i, j], 4)

    # 7. Chi-Quadrat Test: Ist die Verteilung gleichmaessig?
    # Erwartete Verteilung: jede Dekade sollte im Schnitt 20/7 ~ 2.857 haben
    # Test ob Gesamtzahlen gleichmaessig auf Dekaden verteilt sind
    total_per_decade = decade_matrix.sum(axis=0)
    expected_per_decade = np.full(7, total_per_decade.sum() / 7)
    chi2, p_value = stats.chisquare(total_per_decade, expected_per_decade)

    uniformity_test = {
        'chi2_statistic': float(chi2),
        'p_value': float(p_value),
        'is_uniform_alpha_005': p_value > 0.05,
        'total_per_decade': {decade_names[i]: int(total_per_decade[i]) for i in range(7)},
        'expected_per_decade': float(expected_per_decade[0])
    }

    # 8. Extreme Verteilungen identifizieren
    # Finde Ziehungen mit extremen Dekaden-Konzentrationen
    extreme_draws = []
    for idx, dc in enumerate(decade_counts_per_draw):
        max_in_decade = max(dc)
        min_in_decade = min(dc)
        if max_in_decade >= 6 or min_in_decade == 0:
            extreme_draws.append({
                'draw_index': idx,
                'date': df.iloc[idx]['Datum'] if 'Datum' in df.columns else None,
                'distribution': list(dc),
                'max_in_decade': max_in_decade,
                'min_in_decade': min_in_decade
            })

    # 9. Theoretische vs. Beobachtete Verteilung
    # Bei voelligem Zufall: Hypergeometrische Verteilung
    # P(k aus Dekade) = C(10,k) * C(60, 20-k) / C(70, 20)
    from scipy.special import comb

    def hypergeom_prob(k, pop_size=70, decade_size=10, draw_size=20):
        """Hypergeometrische Wahrscheinlichkeit fuer k Treffer aus einer Dekade."""
        return comb(decade_size, k) * comb(pop_size - decade_size, draw_size - k) / comb(pop_size, draw_size)

    theoretical_distribution = {}
    observed_distribution = {i: 0 for i in range(11)}  # 0-10 moeglich

    for dc in decade_counts_per_draw:
        for count in dc:
            observed_distribution[count] += 1

    # Normieren (7 Dekaden * n_draws Beobachtungen)
    total_observations = 7 * n_draws

    for k in range(11):
        theoretical_distribution[k] = hypergeom_prob(k)
        observed_distribution[k] = observed_distribution[k] / total_observations

    theoretical_vs_observed = {
        'counts_0_to_10': {
            str(k): {
                'theoretical': round(theoretical_distribution[k], 6),
                'observed': round(observed_distribution[k], 6),
                'ratio': round(observed_distribution[k] / theoretical_distribution[k], 4) if theoretical_distribution[k] > 0 else None
            }
            for k in range(11) if theoretical_distribution[k] > 1e-10 or observed_distribution[k] > 0
        }
    }

    # 10. Ticket-Empfehlung basierend auf "erlaubten" Verteilungen
    # Finde die haeufigsten Muster und empfehle Ticket-Struktur
    most_common_pattern = pattern_counter.most_common(1)[0][0]
    recommendation = {
        'most_common_pattern': '-'.join(map(str, most_common_pattern)),
        'pattern_frequency': pattern_counter[most_common_pattern] / n_draws,
        'strategy': 'Erstelle Tickets mit Dekaden-Verteilung, die dem haeufigsten Muster entspricht',
        'suggested_distribution': {
            decade_names[i]: round(20/7) for i in range(7)
        },
        'optimal_ranges': {
            decade_names[i]: f'{max(0, int(20/7 - 1))}-{int(20/7 + 1)}' for i in range(7)
        }
    }

    # Zusammenfassung
    result = {
        'metadata': {
            'file': csv_path,
            'total_draws': n_draws,
            'numbers_per_draw': 20,
            'decades': decade_names,
            'expected_per_decade': round(20/7, 4)
        },
        'decade_statistics': decade_stats,
        'distribution_patterns': {
            'top_30_sorted_patterns': pattern_analysis,
            'top_50_exact_distributions': exact_analysis
        },
        'zero_decade_analysis': {
            'per_decade': zero_decade_freq,
            'multiple_empty_decades': multi_zero_analysis
        },
        'correlation_between_decades': correlation_analysis,
        'uniformity_test': uniformity_test,
        'theoretical_vs_observed': theoretical_vs_observed,
        'extreme_draws_count': len(extreme_draws),
        'extreme_draws_sample': extreme_draws[:20] if len(extreme_draws) > 20 else extreme_draws,
        'recommendation': recommendation,
        'hypothesis_assessment': {
            'hypothesis': 'Decade Distribution Constraint - Das System stellt sicher dass jede Dekade fair vertreten ist',
            'evidence_for': [],
            'evidence_against': [],
            'conclusion': None
        }
    }

    # Hypothese bewerten
    # Evidenz FUER: Wenn Verteilung signifikant gleichmaessiger als Zufall
    # Evidenz GEGEN: Wenn Verteilung dem Zufall entspricht

    if p_value > 0.05:
        result['hypothesis_assessment']['evidence_against'].append(
            f'Chi-Quadrat-Test zeigt gleichmaessige Verteilung (p={p_value:.4f}) - entspricht Zufallserwartung'
        )
    else:
        result['hypothesis_assessment']['evidence_for'].append(
            f'Chi-Quadrat-Test zeigt signifikante Abweichung (p={p_value:.4f}) - moeglicherweise Constraint'
        )

    # Pruefen ob 0-Dekaden seltener als erwartet
    theoretical_zero_prob = hypergeom_prob(0)
    observed_zero_prob = sum(zero_decade_analysis.values()) / (7 * n_draws)

    if observed_zero_prob < theoretical_zero_prob * 0.8:
        result['hypothesis_assessment']['evidence_for'].append(
            f'Leere Dekaden seltener als erwartet: beobachtet={observed_zero_prob:.4f}, erwartet={theoretical_zero_prob:.4f}'
        )
    elif observed_zero_prob > theoretical_zero_prob * 1.2:
        result['hypothesis_assessment']['evidence_against'].append(
            f'Leere Dekaden haeufiger als erwartet: beobachtet={observed_zero_prob:.4f}, erwartet={theoretical_zero_prob:.4f}'
        )
    else:
        result['hypothesis_assessment']['evidence_against'].append(
            f'Leere Dekaden im erwarteten Bereich: beobachtet={observed_zero_prob:.4f}, erwartet={theoretical_zero_prob:.4f}'
        )

    # Durchschnittliche Korrelation
    avg_correlation = np.mean([correlation_matrix[i, j] for i in range(7) for j in range(7) if i != j])
    if avg_correlation < -0.2:
        result['hypothesis_assessment']['evidence_for'].append(
            f'Starke negative Korrelation zwischen Dekaden (avg={avg_correlation:.4f}) - Anti-Clustering'
        )
    else:
        result['hypothesis_assessment']['evidence_against'].append(
            f'Schwache Korrelation zwischen Dekaden (avg={avg_correlation:.4f}) - kein Anti-Clustering'
        )

    # Fazit
    n_for = len(result['hypothesis_assessment']['evidence_for'])
    n_against = len(result['hypothesis_assessment']['evidence_against'])

    if n_for > n_against:
        result['hypothesis_assessment']['conclusion'] = 'WAHRSCHEINLICH: Es gibt Hinweise auf einen Decade Distribution Constraint'
    elif n_against > n_for:
        result['hypothesis_assessment']['conclusion'] = 'UNWAHRSCHEINLICH: Die Verteilung entspricht dem Zufallsmodell'
    else:
        result['hypothesis_assessment']['conclusion'] = 'UNENTSCHIEDEN: Weitere Analysen erforderlich'

    # Speichern
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)

    print(f"Analyse gespeichert nach: {output_path}")
    return result


if __name__ == '__main__':
    csv_path = r'C:\Users\kenfu\Documents\keno_base\data\raw\keno\KENO_ab_2022_bereinigt.csv'
    output_path = r'C:\Users\kenfu\Documents\keno_base\results\think_tank_decades.json'

    result = analyze_decades(csv_path, output_path)

    # Zusammenfassung ausgeben
    print("\n" + "="*80)
    print("THINK TANK: DECADE DISTRIBUTION CONSTRAINT ANALYSE")
    print("="*80)
    print(f"\nDatensatz: {result['metadata']['total_draws']} Ziehungen")
    print(f"Erwartet pro Dekade: {result['metadata']['expected_per_decade']:.4f}")

    print("\n--- DEKADEN-STATISTIK ---")
    for decade, stats in result['decade_statistics'].items():
        print(f"{decade}: mean={stats['mean']:.3f}, std={stats['std']:.3f}, "
              f"range=[{stats['min']}-{stats['max']}], abweichung={stats['deviation_from_expected']:.4f}")

    print("\n--- TOP 10 VERTEILUNGSMUSTER (sortiert) ---")
    for i, (pattern, data) in enumerate(list(result['distribution_patterns']['top_30_sorted_patterns'].items())[:10]):
        print(f"{i+1}. {pattern}: {data['count']} ({data['percentage']:.1f}%)")

    print("\n--- LEERE DEKADEN ---")
    for zero_count, data in result['zero_decade_analysis']['multiple_empty_decades'].items():
        print(f"{zero_count}: {data['count']} ({data['percentage']:.1f}%)")

    print("\n--- GLEICHMAESSIGKEITS-TEST ---")
    ut = result['uniformity_test']
    print(f"Chi-Quadrat: {ut['chi2_statistic']:.4f}, p-Wert: {ut['p_value']:.4f}")
    print(f"Ist gleichmaessig (alpha=0.05): {ut['is_uniform_alpha_005']}")

    print("\n--- HYPOTHESEN-BEWERTUNG ---")
    ha = result['hypothesis_assessment']
    print(f"\nEvidenz FUER die Hypothese:")
    for e in ha['evidence_for']:
        print(f"  + {e}")
    print(f"\nEvidenz GEGEN die Hypothese:")
    for e in ha['evidence_against']:
        print(f"  - {e}")
    print(f"\n>>> FAZIT: {ha['conclusion']}")

    print("\n--- EMPFEHLUNG ---")
    rec = result['recommendation']
    print(f"Haeufigster Pattern: {rec['most_common_pattern']} ({rec['pattern_frequency']*100:.1f}%)")
    print(f"Strategie: {rec['strategy']}")
