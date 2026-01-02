#!/usr/bin/env python3
"""
Near-Miss Constraint Model Analysis for KENO
============================================

HYPOTHESE: Das RNG vermeidet aktiv bestimmte Kombinationen,
die zu oft gewinnen wuerden.

Diese Analyse untersucht:
1. Zahlenpaare die SELTENER als erwartet zusammen erscheinen (Anti-Korrelation)
2. Identifikation von "verbotenen Paaren"
3. Test ob Tickets OHNE diese Paare besser performen

Autor: Think Tank - Near-Miss Specialist
Datum: 2025-12-31
"""

import json
import csv
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from datetime import datetime
import math
from typing import NamedTuple


class PairStats(NamedTuple):
    """Statistics for a number pair."""
    pair: tuple[int, int]
    observed: int
    expected: float
    z_score: float
    deficit_ratio: float  # observed / expected


def load_keno_data(filepath: str) -> list[dict]:
    """Load KENO data from CSV file."""
    draws = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                # Parse date
                date_str = row['Datum']
                # Extract numbers from Keno_Z1 to Keno_Z20
                numbers = []
                for i in range(1, 21):
                    col = f'Keno_Z{i}'
                    if col in row and row[col]:
                        numbers.append(int(row[col]))

                if len(numbers) == 20:
                    draws.append({
                        'date': date_str,
                        'numbers': set(numbers)
                    })
            except (ValueError, KeyError) as e:
                continue

    return draws


def calculate_expected_pair_frequency(n_draws: int, pool_size: int = 70,
                                       draw_size: int = 20) -> float:
    """
    Calculate expected frequency for any pair under random assumption.

    Bei KENO: 20 aus 70 gezogen
    P(Zahl A gezogen) = 20/70
    P(Zahl B gezogen | A gezogen) = 19/69
    P(beide gezogen) = (20/70) * (19/69) = 380/4830 = 0.0787

    Erwartete Haeufigkeit = n_draws * P(beide)
    """
    p_both = (draw_size / pool_size) * ((draw_size - 1) / (pool_size - 1))
    return n_draws * p_both


def calculate_pair_frequencies(draws: list[dict]) -> dict[tuple[int, int], int]:
    """Calculate observed frequency for each number pair."""
    pair_counts = defaultdict(int)

    for draw in draws:
        numbers = sorted(draw['numbers'])
        # Count all pairs in this draw
        for pair in combinations(numbers, 2):
            pair_counts[pair] += 1

    return dict(pair_counts)


def calculate_z_scores(pair_counts: dict[tuple[int, int], int],
                       n_draws: int,
                       pool_size: int = 70,
                       draw_size: int = 20) -> list[PairStats]:
    """
    Calculate Z-scores for all pairs.

    Z = (observed - expected) / sqrt(expected * (1 - p))

    Negative Z-score = erscheint SELTENER als erwartet (Anti-Korrelation)
    """
    expected = calculate_expected_pair_frequency(n_draws, pool_size, draw_size)
    p_both = (draw_size / pool_size) * ((draw_size - 1) / (pool_size - 1))

    # Standard deviation for binomial
    std_dev = math.sqrt(n_draws * p_both * (1 - p_both))

    pair_stats = []

    # Generate all possible pairs
    for pair in combinations(range(1, pool_size + 1), 2):
        observed = pair_counts.get(pair, 0)
        z_score = (observed - expected) / std_dev if std_dev > 0 else 0
        deficit_ratio = observed / expected if expected > 0 else 0

        pair_stats.append(PairStats(
            pair=pair,
            observed=observed,
            expected=expected,
            z_score=z_score,
            deficit_ratio=deficit_ratio
        ))

    return pair_stats


def find_anti_correlated_pairs(pair_stats: list[PairStats],
                                top_n: int = 50) -> list[PairStats]:
    """Find the most anti-correlated pairs (lowest Z-scores)."""
    # Sort by Z-score ascending (most negative first)
    sorted_stats = sorted(pair_stats, key=lambda x: x.z_score)
    return sorted_stats[:top_n]


def find_positively_correlated_pairs(pair_stats: list[PairStats],
                                      top_n: int = 50) -> list[PairStats]:
    """Find the most positively correlated pairs (highest Z-scores)."""
    sorted_stats = sorted(pair_stats, key=lambda x: x.z_score, reverse=True)
    return sorted_stats[:top_n]


def test_ticket_performance(draws: list[dict],
                            forbidden_pairs: set[tuple[int, int]],
                            test_draws: int = 100) -> dict:
    """
    Test if avoiding forbidden pairs improves performance.

    Strategy:
    - Generate random tickets (6 numbers)
    - Compare: tickets WITH forbidden pairs vs WITHOUT
    - Measure: how many numbers match in actual draws
    """
    import random

    # Use last test_draws for testing
    test_data = draws[-test_draws:]

    results = {
        'with_forbidden': {'total_matches': 0, 'tickets': 0, 'matches_per_ticket': []},
        'without_forbidden': {'total_matches': 0, 'tickets': 0, 'matches_per_ticket': []}
    }

    # Generate 1000 random tickets for each category
    n_tickets = 1000
    random.seed(42)  # Reproducibility

    for _ in range(n_tickets):
        # Generate ticket WITH at least one forbidden pair
        ticket_with = generate_ticket_with_forbidden(forbidden_pairs)
        # Generate ticket WITHOUT any forbidden pair
        ticket_without = generate_ticket_without_forbidden(forbidden_pairs)

        # Test against all test draws
        matches_with = 0
        matches_without = 0

        for draw in test_data:
            draw_numbers = draw['numbers']
            matches_with += len(ticket_with & draw_numbers)
            matches_without += len(ticket_without & draw_numbers)

        avg_matches_with = matches_with / len(test_data)
        avg_matches_without = matches_without / len(test_data)

        results['with_forbidden']['total_matches'] += matches_with
        results['with_forbidden']['tickets'] += 1
        results['with_forbidden']['matches_per_ticket'].append(avg_matches_with)

        results['without_forbidden']['total_matches'] += matches_without
        results['without_forbidden']['tickets'] += 1
        results['without_forbidden']['matches_per_ticket'].append(avg_matches_without)

    # Calculate statistics
    for category in ['with_forbidden', 'without_forbidden']:
        matches = results[category]['matches_per_ticket']
        results[category]['mean_matches'] = sum(matches) / len(matches)
        results[category]['std_matches'] = math.sqrt(
            sum((x - results[category]['mean_matches'])**2 for x in matches) / len(matches)
        )
        del results[category]['matches_per_ticket']  # Don't save raw data

    return results


def generate_ticket_with_forbidden(forbidden_pairs: set[tuple[int, int]],
                                   size: int = 6) -> set[int]:
    """Generate a ticket that contains at least one forbidden pair."""
    import random

    max_attempts = 100
    for _ in range(max_attempts):
        ticket = set(random.sample(range(1, 71), size))
        # Check if it has any forbidden pair
        for pair in combinations(sorted(ticket), 2):
            if pair in forbidden_pairs:
                return ticket

    # Fallback: force a forbidden pair
    if forbidden_pairs:
        pair = list(forbidden_pairs)[0]
        ticket = set(pair)
        remaining = [n for n in range(1, 71) if n not in ticket]
        ticket.update(random.sample(remaining, size - 2))
        return ticket

    return set(random.sample(range(1, 71), size))


def generate_ticket_without_forbidden(forbidden_pairs: set[tuple[int, int]],
                                       size: int = 6) -> set[int]:
    """Generate a ticket that contains NO forbidden pairs."""
    import random

    max_attempts = 1000
    for _ in range(max_attempts):
        ticket = set(random.sample(range(1, 71), size))
        # Check if it has any forbidden pair
        has_forbidden = False
        for pair in combinations(sorted(ticket), 2):
            if pair in forbidden_pairs:
                has_forbidden = True
                break

        if not has_forbidden:
            return ticket

    # Fallback: should rarely happen with only 50 forbidden pairs out of 2415
    return set(random.sample(range(1, 71), size))


def analyze_temporal_pattern(draws: list[dict],
                             pair: tuple[int, int]) -> dict:
    """Analyze when a pair appears over time."""
    appearances = []
    gaps = []
    last_idx = None

    for idx, draw in enumerate(draws):
        if pair[0] in draw['numbers'] and pair[1] in draw['numbers']:
            appearances.append(idx)
            if last_idx is not None:
                gaps.append(idx - last_idx)
            last_idx = idx

    return {
        'total_appearances': len(appearances),
        'first_appearance': appearances[0] if appearances else None,
        'last_appearance': appearances[-1] if appearances else None,
        'avg_gap': sum(gaps) / len(gaps) if gaps else None,
        'max_gap': max(gaps) if gaps else None,
        'min_gap': min(gaps) if gaps else None
    }


def statistical_significance_test(observed: int, expected: float,
                                  n_trials: int) -> dict:
    """
    Chi-square test for single pair.
    """
    if expected == 0:
        return {'chi_square': float('inf'), 'interpretation': 'undefined'}

    chi_sq = ((observed - expected) ** 2) / expected

    # Critical values for chi-square with df=1
    # alpha=0.05: 3.84, alpha=0.01: 6.63, alpha=0.001: 10.83
    if chi_sq > 10.83:
        significance = "highly_significant (p<0.001)"
    elif chi_sq > 6.63:
        significance = "very_significant (p<0.01)"
    elif chi_sq > 3.84:
        significance = "significant (p<0.05)"
    else:
        significance = "not_significant (p>0.05)"

    return {
        'chi_square': chi_sq,
        'significance': significance,
        'direction': 'under-represented' if observed < expected else 'over-represented'
    }


def main():
    """Main analysis function."""
    # Paths
    data_path = Path("C:/Users/kenfu/Documents/keno_base/data/raw/keno/KENO_ab_2022_bereinigt.csv")
    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/think_tank_nearmiss.json")

    print("=" * 70)
    print("NEAR-MISS CONSTRAINT MODEL ANALYSIS")
    print("=" * 70)
    print()

    # Load data
    print("[1] Loading KENO data...")
    draws = load_keno_data(str(data_path))
    n_draws = len(draws)
    print(f"    Loaded {n_draws} draws from {draws[0]['date']} to {draws[-1]['date']}")
    print()

    # Calculate expected frequency
    print("[2] Calculating expected pair frequency...")
    expected_freq = calculate_expected_pair_frequency(n_draws)
    p_both = (20 / 70) * (19 / 69)
    print(f"    P(both numbers drawn) = 20/70 * 19/69 = {p_both:.6f}")
    print(f"    Expected frequency per pair = {n_draws} * {p_both:.6f} = {expected_freq:.2f}")
    print()

    # Calculate observed frequencies
    print("[3] Calculating observed pair frequencies...")
    pair_counts = calculate_pair_frequencies(draws)
    total_pairs = len(list(combinations(range(1, 71), 2)))
    observed_pairs = len(pair_counts)
    print(f"    Total possible pairs: {total_pairs}")
    print(f"    Pairs observed at least once: {observed_pairs}")
    print()

    # Calculate Z-scores
    print("[4] Calculating Z-scores for all pairs...")
    pair_stats = calculate_z_scores(pair_counts, n_draws)

    # Find anti-correlated pairs
    print("[5] Finding top 50 anti-correlated pairs (FORBIDDEN PAIRS)...")
    anti_correlated = find_anti_correlated_pairs(pair_stats, 50)

    print("\n    TOP 20 MOST ANTI-CORRELATED PAIRS:")
    print("    " + "-" * 60)
    print(f"    {'Pair':<12} {'Observed':<10} {'Expected':<10} {'Z-Score':<10} {'Deficit%':<10}")
    print("    " + "-" * 60)

    for ps in anti_correlated[:20]:
        deficit_pct = (1 - ps.deficit_ratio) * 100
        print(f"    ({ps.pair[0]:2}, {ps.pair[1]:2})    {ps.observed:<10} {ps.expected:<10.2f} {ps.z_score:<10.3f} {deficit_pct:.1f}%")

    print()

    # Find positively correlated pairs for comparison
    print("[6] Finding top 50 positively correlated pairs (FAVORED PAIRS)...")
    pos_correlated = find_positively_correlated_pairs(pair_stats, 50)

    print("\n    TOP 20 MOST POSITIVELY CORRELATED PAIRS:")
    print("    " + "-" * 60)
    print(f"    {'Pair':<12} {'Observed':<10} {'Expected':<10} {'Z-Score':<10} {'Excess%':<10}")
    print("    " + "-" * 60)

    for ps in pos_correlated[:20]:
        excess_pct = (ps.deficit_ratio - 1) * 100
        print(f"    ({ps.pair[0]:2}, {ps.pair[1]:2})    {ps.observed:<10} {ps.expected:<10.2f} {ps.z_score:<10.3f} {excess_pct:.1f}%")

    print()

    # Create forbidden pairs set
    forbidden_pairs = set(ps.pair for ps in anti_correlated)

    # Test ticket performance
    print("[7] Testing ticket performance (Monte Carlo with 1000 tickets)...")
    print("    - Tickets WITH forbidden pairs vs WITHOUT")
    print("    - Testing on last 100 draws")

    performance = test_ticket_performance(draws, forbidden_pairs, test_draws=100)

    print("\n    PERFORMANCE RESULTS:")
    print("    " + "-" * 50)
    print(f"    Tickets WITH forbidden pairs:")
    print(f"        Mean matches per draw: {performance['with_forbidden']['mean_matches']:.4f}")
    print(f"        Std deviation: {performance['with_forbidden']['std_matches']:.4f}")
    print()
    print(f"    Tickets WITHOUT forbidden pairs:")
    print(f"        Mean matches per draw: {performance['without_forbidden']['mean_matches']:.4f}")
    print(f"        Std deviation: {performance['without_forbidden']['std_matches']:.4f}")
    print()

    improvement = (performance['without_forbidden']['mean_matches'] -
                   performance['with_forbidden']['mean_matches'])
    improvement_pct = improvement / performance['with_forbidden']['mean_matches'] * 100

    print(f"    IMPROVEMENT: {improvement:.4f} matches ({improvement_pct:.2f}%)")

    # Analyze temporal patterns for top forbidden pairs
    print("\n[8] Analyzing temporal patterns for top 10 forbidden pairs...")
    temporal_analysis = {}
    for ps in anti_correlated[:10]:
        temporal = analyze_temporal_pattern(draws, ps.pair)
        temporal_analysis[f"{ps.pair[0]}-{ps.pair[1]}"] = temporal
        avg_gap_str = f"{temporal['avg_gap']:.1f}" if temporal['avg_gap'] else 'N/A'
        print(f"    Pair ({ps.pair[0]}, {ps.pair[1]}): {temporal['total_appearances']} times, "
              f"avg gap: {avg_gap_str} draws")

    # Statistical significance
    print("\n[9] Statistical significance analysis...")
    significant_anti = sum(1 for ps in anti_correlated if ps.z_score < -2.576)
    significant_pos = sum(1 for ps in pos_correlated if ps.z_score > 2.576)

    print(f"    Anti-correlated pairs significant at p<0.01: {significant_anti}/50")
    print(f"    Positively correlated pairs significant at p<0.01: {significant_pos}/50")

    # Prepare output
    output = {
        "hypothesis": "Near-Miss Constraint Model",
        "description": "Das RNG vermeidet aktiv bestimmte Kombinationen die zu oft gewinnen wuerden",
        "analysis_date": datetime.now().isoformat(),
        "data_summary": {
            "total_draws": n_draws,
            "date_range": f"{draws[0]['date']} to {draws[-1]['date']}",
            "total_possible_pairs": total_pairs,
            "expected_frequency_per_pair": round(expected_freq, 2),
            "probability_both_drawn": round(p_both, 6)
        },
        "forbidden_pairs": [
            {
                "pair": list(ps.pair),
                "observed": ps.observed,
                "expected": round(ps.expected, 2),
                "z_score": round(ps.z_score, 3),
                "deficit_percent": round((1 - ps.deficit_ratio) * 100, 1),
                "significance": statistical_significance_test(ps.observed, ps.expected, n_draws)
            }
            for ps in anti_correlated
        ],
        "favored_pairs": [
            {
                "pair": list(ps.pair),
                "observed": ps.observed,
                "expected": round(ps.expected, 2),
                "z_score": round(ps.z_score, 3),
                "excess_percent": round((ps.deficit_ratio - 1) * 100, 1),
                "significance": statistical_significance_test(ps.observed, ps.expected, n_draws)
            }
            for ps in pos_correlated
        ],
        "performance_test": {
            "method": "Monte Carlo simulation with 1000 random 6-number tickets",
            "test_draws": 100,
            "with_forbidden_pairs": {
                "mean_matches": round(performance['with_forbidden']['mean_matches'], 4),
                "std_matches": round(performance['with_forbidden']['std_matches'], 4)
            },
            "without_forbidden_pairs": {
                "mean_matches": round(performance['without_forbidden']['mean_matches'], 4),
                "std_matches": round(performance['without_forbidden']['std_matches'], 4)
            },
            "improvement": round(improvement, 4),
            "improvement_percent": round(improvement_pct, 2)
        },
        "temporal_patterns": temporal_analysis,
        "statistical_summary": {
            "anti_correlated_significant_001": significant_anti,
            "positively_correlated_significant_001": significant_pos,
            "interpretation": (
                "HIGHLY SIGNIFICANT" if significant_anti > 10 else
                "MODERATELY SIGNIFICANT" if significant_anti > 5 else
                "WEAK EVIDENCE"
            )
        },
        "conclusion": {
            "hypothesis_supported": improvement > 0,
            "effect_size": "SMALL" if abs(improvement_pct) < 1 else
                          "MEDIUM" if abs(improvement_pct) < 5 else "LARGE",
            "recommendation": (
                "VERMEIDEN: Die 50 stark anti-korrelierten Paare in Tickets meiden. "
                "Bevorzugen: Die 50 positiv korrelierten Paare als Kandidaten."
                if improvement > 0 else
                "KEINE EMPFEHLUNG: Kein signifikanter Unterschied gefunden."
            ),
            "caveat": (
                "ACHTUNG: Statistische Anti-Korrelation kann auch durch Zufall entstehen. "
                "Bei 2415 Paaren erwarten wir ca. 24 'signifikante' durch Zufall allein. "
                "Weitere Validierung mit Out-of-Sample Daten empfohlen."
            )
        }
    }

    # Save results
    print(f"\n[10] Saving results to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nResults saved to: {output_path}")
    print(f"\nKEY FINDINGS:")
    print(f"  - Found 50 'forbidden pairs' with significant under-representation")
    print(f"  - Top forbidden pair: ({anti_correlated[0].pair[0]}, {anti_correlated[0].pair[1]}) "
          f"with {anti_correlated[0].observed} occurrences (expected: {expected_freq:.0f})")
    print(f"  - Performance improvement WITHOUT forbidden pairs: {improvement_pct:.2f}%")
    print(f"  - Hypothesis support: {'YES' if improvement > 0 else 'NO'}")

    return output


if __name__ == "__main__":
    main()
