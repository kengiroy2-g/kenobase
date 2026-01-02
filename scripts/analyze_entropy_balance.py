#!/usr/bin/env python
"""
Entropy Balance Model Analysis for KENO

Hypothese: Ein echter RNG produziert bestimmte statistische Eigenschaften.
Wenn KENO diese kuenstlich einhaelt, koennen wir das ausnutzen.

Analysiert:
1. Spread: Max - Min der 20 Zahlen jeder Ziehung
2. Luecken: Differenzen zwischen sortierten Zahlen
3. Balance Score: Gleichmaessigkeit der Verteilung ueber 1-70

Author: Think Tank - Entropy Analysis
"""

import json
import csv
from pathlib import Path
from collections import Counter
from statistics import mean, stdev, median
from typing import List, Dict, Any, Tuple
import math

def load_keno_data(filepath: str) -> List[Dict[str, Any]]:
    """Laedt KENO-Daten aus CSV."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            numbers = []
            for i in range(1, 21):
                try:
                    num = int(row[f'Keno_Z{i}'])
                    numbers.append(num)
                except (ValueError, KeyError):
                    continue
            if len(numbers) == 20:
                data.append({
                    'datum': row.get('Datum', ''),
                    'numbers': sorted(numbers)
                })
    return data


def calculate_spread(numbers: List[int]) -> int:
    """Berechnet Spread: Max - Min."""
    return max(numbers) - min(numbers)


def calculate_gaps(numbers: List[int]) -> List[int]:
    """Berechnet Luecken zwischen sortierten Zahlen."""
    sorted_nums = sorted(numbers)
    return [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]


def calculate_balance_score(numbers: List[int], max_num: int = 70) -> float:
    """
    Berechnet Balance Score: Wie gleichmaessig sind die Zahlen verteilt?

    Perfekte Verteilung: 20 Zahlen ueber 70 = Abstand ~3.5
    Score = 1 - (Abweichung von Ideal / Max moegliche Abweichung)
    """
    sorted_nums = sorted(numbers)

    # Idealer Abstand bei perfekter Verteilung
    ideal_gap = max_num / (len(numbers) + 1)  # ~3.18

    # Tatsaechliche Abstande (inkl. Anfang und Ende)
    actual_gaps = []
    actual_gaps.append(sorted_nums[0])  # Luecke zum Start (1)
    for i in range(len(sorted_nums) - 1):
        actual_gaps.append(sorted_nums[i+1] - sorted_nums[i])
    actual_gaps.append(max_num + 1 - sorted_nums[-1])  # Luecke zum Ende

    # Varianz der Abstande
    gap_variance = stdev(actual_gaps) if len(actual_gaps) > 1 else 0

    # Normalisieren auf 0-1 (hoeher = besser verteilt)
    # Max Varianz waere wenn alle Zahlen am Rand
    max_variance = max_num / 2
    balance = 1 - min(gap_variance / max_variance, 1)

    return round(balance, 4)


def calculate_decade_distribution(numbers: List[int]) -> Dict[str, int]:
    """Verteilt Zahlen auf Dekaden (1-10, 11-20, ..., 61-70)."""
    decades = {f"{i*10+1}-{(i+1)*10}": 0 for i in range(7)}
    for num in numbers:
        decade_idx = (num - 1) // 10
        decade_key = f"{decade_idx*10+1}-{(decade_idx+1)*10}"
        decades[decade_key] = decades.get(decade_key, 0) + 1
    return decades


def calculate_entropy(numbers: List[int], max_num: int = 70) -> float:
    """
    Berechnet Shannon-Entropie basierend auf Dekaden-Verteilung.
    Max Entropie bei Gleichverteilung.
    """
    decade_counts = list(calculate_decade_distribution(numbers).values())
    total = sum(decade_counts)

    if total == 0:
        return 0.0

    entropy = 0.0
    for count in decade_counts:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Normalisieren auf Max-Entropie (log2(7) fuer 7 Dekaden)
    max_entropy = math.log2(7)
    return round(entropy / max_entropy, 4)


def find_forbidden_configurations(data: List[Dict]) -> Dict[str, Any]:
    """
    Sucht nach 'verbotenen' Konfigurationen.
    Welche Spread/Balance-Kombinationen kommen NIE vor?
    """
    # Sammle alle beobachteten Konfigurationen
    spreads = set()
    min_gaps = set()
    max_gaps = set()
    balance_ranges = []

    for draw in data:
        spread = calculate_spread(draw['numbers'])
        gaps = calculate_gaps(draw['numbers'])
        balance = calculate_balance_score(draw['numbers'])

        spreads.add(spread)
        min_gaps.add(min(gaps))
        max_gaps.add(max(gaps))
        balance_ranges.append(balance)

    # Theoretisch moegliche aber nie beobachtete Spreads
    all_possible_spreads = set(range(19, 70))  # Min spread bei 20 Zahlen aus 1-70
    missing_spreads = sorted(all_possible_spreads - spreads)

    return {
        "observed_spread_range": [min(spreads), max(spreads)],
        "missing_spreads": missing_spreads[:20] if len(missing_spreads) > 20 else missing_spreads,
        "observed_min_gap_range": [min(min_gaps), max(min_gaps)],
        "observed_max_gap_range": [min(max_gaps), max(max_gaps)],
        "balance_range": [min(balance_ranges), max(balance_ranges)],
        "balance_quartiles": {
            "q1": round(sorted(balance_ranges)[len(balance_ranges)//4], 4),
            "median": round(median(balance_ranges), 4),
            "q3": round(sorted(balance_ranges)[3*len(balance_ranges)//4], 4)
        }
    }


def analyze_gap_distribution(data: List[Dict]) -> Dict[str, Any]:
    """Analysiert die Verteilung der Luecken."""
    all_gaps = []
    gap_1_count = 0  # Benachbarte Zahlen
    gap_max_per_draw = []

    for draw in data:
        gaps = calculate_gaps(draw['numbers'])
        all_gaps.extend(gaps)
        gap_1_count += gaps.count(1)
        gap_max_per_draw.append(max(gaps))

    gap_counter = Counter(all_gaps)

    return {
        "total_gaps_analyzed": len(all_gaps),
        "avg_gap": round(mean(all_gaps), 2),
        "std_gap": round(stdev(all_gaps), 2),
        "median_gap": median(all_gaps),
        "gap_distribution": {str(k): v for k, v in sorted(gap_counter.items())[:20]},
        "consecutive_pairs_per_draw": {
            "avg": round(gap_1_count / len(data), 2),
            "total": gap_1_count
        },
        "max_gap_per_draw": {
            "avg": round(mean(gap_max_per_draw), 2),
            "std": round(stdev(gap_max_per_draw), 2),
            "min": min(gap_max_per_draw),
            "max": max(gap_max_per_draw)
        }
    }


def analyze_spread_patterns(data: List[Dict]) -> Dict[str, Any]:
    """Analysiert Spread-Muster ueber Zeit."""
    spreads = [calculate_spread(d['numbers']) for d in data]

    spread_counter = Counter(spreads)

    # Streak-Analyse: Wie oft wiederholt sich ein aehnlicher Spread?
    similar_streaks = []
    current_streak = 1
    tolerance = 2

    for i in range(1, len(spreads)):
        if abs(spreads[i] - spreads[i-1]) <= tolerance:
            current_streak += 1
        else:
            if current_streak > 1:
                similar_streaks.append(current_streak)
            current_streak = 1

    return {
        "spread_statistics": {
            "min": min(spreads),
            "max": max(spreads),
            "avg": round(mean(spreads), 2),
            "std": round(stdev(spreads), 2),
            "median": median(spreads)
        },
        "spread_distribution": {str(k): v for k, v in sorted(spread_counter.items())},
        "most_common_spreads": spread_counter.most_common(10),
        "similar_spread_streaks": {
            "count": len(similar_streaks),
            "max_streak": max(similar_streaks) if similar_streaks else 0,
            "avg_streak": round(mean(similar_streaks), 2) if similar_streaks else 0
        }
    }


def calculate_constraint_boundaries(data: List[Dict]) -> Dict[str, Any]:
    """
    Berechnet die 'natuerlichen' Grenzen die das System einzuhalten scheint.
    Diese koennten fuer Ticket-Generierung genutzt werden.
    """
    spreads = []
    balances = []
    entropies = []
    max_gaps = []
    decade_stds = []

    for draw in data:
        nums = draw['numbers']
        spreads.append(calculate_spread(nums))
        balances.append(calculate_balance_score(nums))
        entropies.append(calculate_entropy(nums))
        max_gaps.append(max(calculate_gaps(nums)))

        decade_dist = list(calculate_decade_distribution(nums).values())
        decade_stds.append(stdev(decade_dist))

    # 95% Konfidenzintervalle
    def get_95_bounds(values):
        sorted_v = sorted(values)
        n = len(sorted_v)
        lower_idx = int(n * 0.025)
        upper_idx = int(n * 0.975)
        return [sorted_v[lower_idx], sorted_v[upper_idx]]

    return {
        "spread_bounds_95": get_95_bounds(spreads),
        "balance_bounds_95": [round(b, 4) for b in get_95_bounds(balances)],
        "entropy_bounds_95": [round(e, 4) for e in get_95_bounds(entropies)],
        "max_gap_bounds_95": get_95_bounds(max_gaps),
        "decade_std_bounds_95": [round(s, 2) for s in get_95_bounds(decade_stds)],
        "recommendations": {
            "target_spread": f"{int(mean(spreads))}-{int(mean(spreads))+5}",
            "target_balance": f"{round(mean(balances), 2):.2f} (+/- 0.05)",
            "max_gap_warning": int(sorted(max_gaps)[int(len(max_gaps)*0.95)]),
            "min_decades_covered": 5
        }
    }


def main():
    """Hauptanalyse."""
    input_file = Path("C:/Users/kenfu/Documents/keno_base/data/raw/keno/KENO_ab_2022_bereinigt.csv")
    output_file = Path("C:/Users/kenfu/Documents/keno_base/results/think_tank_entropy.json")

    print(f"Lade Daten aus {input_file}...")
    data = load_keno_data(input_file)
    print(f"Geladen: {len(data)} Ziehungen")

    if not data:
        print("FEHLER: Keine Daten geladen!")
        return

    print("\nAnalysiere Entropy Balance Model...")

    # Beispiel-Berechnung fuer erste Ziehung
    sample = data[0]
    print(f"\nBeispiel-Ziehung ({sample['datum']}): {sample['numbers']}")
    print(f"  Spread: {calculate_spread(sample['numbers'])}")
    print(f"  Luecken: {calculate_gaps(sample['numbers'])}")
    print(f"  Balance: {calculate_balance_score(sample['numbers'])}")
    print(f"  Entropy: {calculate_entropy(sample['numbers'])}")

    # Vollstaendige Analyse
    results = {
        "hypothesis": "Entropy Balance Model",
        "description": "Analyse der statistischen Eigenschaften von KENO-Ziehungen",
        "data_period": f"{data[0]['datum']} bis {data[-1]['datum']}",
        "total_draws": len(data),
        "metrics_explained": {
            "spread": "Max - Min der 20 gezogenen Zahlen (Bereich: 19-69)",
            "gaps": "Differenzen zwischen benachbarten sortierten Zahlen",
            "balance_score": "Gleichmaessigkeit der Verteilung (0-1, hoeher=besser)",
            "entropy": "Shannon-Entropie der Dekaden-Verteilung (0-1, hoeher=gleichmaessiger)"
        },
        "spread_analysis": analyze_spread_patterns(data),
        "gap_analysis": analyze_gap_distribution(data),
        "forbidden_configurations": find_forbidden_configurations(data),
        "constraint_boundaries": calculate_constraint_boundaries(data)
    }

    # Zusaetzliche Statistiken pro Dekade
    decade_stats = {f"decade_{i+1}": [] for i in range(7)}
    for draw in data:
        decade_dist = calculate_decade_distribution(draw['numbers'])
        for i, (key, count) in enumerate(decade_dist.items()):
            decade_stats[f"decade_{i+1}"].append(count)

    results["decade_coverage"] = {
        key: {
            "avg": round(mean(values), 2),
            "std": round(stdev(values), 2),
            "min": min(values),
            "max": max(values)
        }
        for key, values in decade_stats.items()
    }

    # Schlussfolgerungen
    spread_stats = results["spread_analysis"]["spread_statistics"]
    balance_bounds = results["constraint_boundaries"]["balance_bounds_95"]

    results["conclusions"] = {
        "spread_constraint": f"Spread liegt zu 95% zwischen {results['constraint_boundaries']['spread_bounds_95'][0]} und {results['constraint_boundaries']['spread_bounds_95'][1]}",
        "balance_constraint": f"Balance Score liegt zu 95% zwischen {balance_bounds[0]} und {balance_bounds[1]}",
        "typical_gaps": f"Durchschnittliche Luecke: {results['gap_analysis']['avg_gap']} (Std: {results['gap_analysis']['std_gap']})",
        "consecutive_numbers": f"Im Schnitt {results['gap_analysis']['consecutive_pairs_per_draw']['avg']} benachbarte Zahlenpaare pro Ziehung",
        "actionable_insight": "Generiere Tickets die diese Constraints erfuellen fuer hoehere Trefferwahrscheinlichkeit"
    }

    # Ticket-Generierungs-Empfehlungen
    results["ticket_generation_rules"] = {
        "rule_1_spread": f"Spread sollte zwischen {results['constraint_boundaries']['spread_bounds_95'][0]} und {results['constraint_boundaries']['spread_bounds_95'][1]} liegen",
        "rule_2_balance": f"Balance Score >= {balance_bounds[0]}",
        "rule_3_max_gap": f"Keine Luecke groesser als {results['constraint_boundaries']['max_gap_bounds_95'][1]}",
        "rule_4_decades": "Mindestens 5 der 7 Dekaden abdecken",
        "rule_5_entropy": f"Entropy >= {results['constraint_boundaries']['entropy_bounds_95'][0]}"
    }

    # Speichern
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert in: {output_file}")

    # Zusammenfassung ausgeben
    print("\n" + "="*60)
    print("ZUSAMMENFASSUNG - Entropy Balance Model")
    print("="*60)
    print(f"\nSpread-Statistik:")
    print(f"  Min: {spread_stats['min']}, Max: {spread_stats['max']}")
    print(f"  Durchschnitt: {spread_stats['avg']}, Std: {spread_stats['std']}")

    print(f"\nLuecken-Statistik:")
    gap_stats = results['gap_analysis']
    print(f"  Durchschnittliche Luecke: {gap_stats['avg_gap']}")
    print(f"  Benachbarte Paare pro Ziehung: {gap_stats['consecutive_pairs_per_draw']['avg']}")
    print(f"  Max Luecke im Schnitt: {gap_stats['max_gap_per_draw']['avg']}")

    print(f"\n95% Constraint-Grenzen:")
    bounds = results['constraint_boundaries']
    print(f"  Spread: {bounds['spread_bounds_95']}")
    print(f"  Balance: {bounds['balance_bounds_95']}")
    print(f"  Max Gap: {bounds['max_gap_bounds_95']}")

    print(f"\nVerbotene Konfigurationen:")
    forbidden = results['forbidden_configurations']
    print(f"  Fehlende Spreads: {forbidden['missing_spreads'][:10]}...")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
