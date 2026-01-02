#!/usr/bin/env python
"""
Combined Constraint Strategy for KENO
=====================================

Kombiniert die nutzbaren Erkenntnisse aus dem Think Tank:

1. Consecutive Avoidance: Keine 3+ aufeinanderfolgenden Zahlen
2. Entropy Balance: Spread zwischen 55-69, Balance Score >= 0.88
3. Near-Miss Pairs: Verbotene Paare meiden, bevorzugte Paare nutzen

Diese Strategie generiert Tickets, die den "natürlichen" Constraints
des KENO-Systems entsprechen.

Autor: Think Tank Synthesis
Datum: 2025-12-31
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from itertools import combinations
from datetime import datetime
import json
import random

BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_DIR = BASE_DIR / "results"

# KENO Typ 9 Quoten
KENO_QUOTES = {0: 2, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 5, 7: 20, 8: 1000, 9: 50000}

# Top 50 verbotene Paare (aus Near-Miss Analyse)
FORBIDDEN_PAIRS = {
    (22, 57), (22, 69), (13, 69), (19, 29), (22, 60), (53, 60),
    (1, 19), (5, 32), (7, 29), (7, 60), (22, 66), (29, 37),
    (29, 60), (31, 58), (32, 60), (32, 66), (37, 57), (7, 25),
    (7, 53), (7, 57), (10, 25), (13, 22), (14, 60), (19, 60),
    (22, 36), (22, 52), (25, 29), (25, 53), (25, 60), (25, 66),
    (29, 53), (29, 57), (32, 53), (37, 60), (53, 66), (58, 60),
    (7, 66), (13, 32), (14, 29), (19, 25), (19, 32), (19, 53),
    (22, 25), (22, 32), (25, 32), (25, 37), (25, 57), (29, 32),
    (32, 37), (32, 57)
}

# Top 50 bevorzugte Paare (aus Near-Miss Analyse)
FAVORED_PAIRS = {
    (3, 9), (9, 36), (9, 39), (49, 55), (3, 25), (9, 45),
    (10, 45), (12, 45), (36, 42), (45, 61), (5, 9), (9, 16),
    (9, 43), (9, 63), (17, 45), (2, 45), (4, 63), (9, 10),
    (9, 33), (9, 50), (9, 56), (45, 55), (3, 63), (4, 9),
    (4, 45), (5, 45), (6, 45), (9, 12), (9, 17), (9, 27),
    (9, 41), (9, 49), (9, 55), (9, 64), (12, 63), (17, 63),
    (20, 45), (27, 45), (39, 55), (43, 45), (45, 49), (45, 63),
    (45, 64), (45, 68), (3, 45), (5, 63), (6, 63), (9, 14),
    (9, 20), (9, 28)
}


def load_data():
    """Lade KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=";", encoding="utf-8")
    df["datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].apply(
        lambda row: [int(x) for x in row if pd.notna(x)], axis=1
    )

    df = df.dropna(subset=["datum"])
    df = df.sort_values("datum").reset_index(drop=True)
    return df


def has_consecutive_triplet(numbers):
    """Prüft ob 3+ aufeinanderfolgende Zahlen vorhanden sind."""
    sorted_nums = sorted(numbers)
    for i in range(len(sorted_nums) - 2):
        if sorted_nums[i+1] == sorted_nums[i] + 1 and sorted_nums[i+2] == sorted_nums[i] + 2:
            return True
    return False


def calculate_spread(numbers):
    """Berechnet Spread (Max - Min)."""
    return max(numbers) - min(numbers)


def calculate_balance_score(numbers, max_num=70):
    """Berechnet Balance Score (0-1)."""
    sorted_nums = sorted(numbers)

    # Alle Gaps inkl. Anfang und Ende
    gaps = [sorted_nums[0]]  # Gap zum Start
    for i in range(len(sorted_nums) - 1):
        gaps.append(sorted_nums[i+1] - sorted_nums[i])
    gaps.append(max_num + 1 - sorted_nums[-1])  # Gap zum Ende

    # Varianz der Gaps
    mean_gap = sum(gaps) / len(gaps)
    variance = sum((g - mean_gap)**2 for g in gaps) / len(gaps)
    std_gap = variance ** 0.5

    # Normalisieren
    max_variance = max_num / 2
    balance = 1 - min(std_gap / max_variance, 1)

    return round(balance, 4)


def count_decades_covered(numbers):
    """Zählt wie viele Dekaden abgedeckt sind."""
    decades = set((n - 1) // 10 for n in numbers)
    return len(decades)


def count_forbidden_pairs(numbers):
    """Zählt verbotene Paare im Ticket."""
    count = 0
    for pair in combinations(sorted(numbers), 2):
        if pair in FORBIDDEN_PAIRS:
            count += 1
    return count


def count_favored_pairs(numbers):
    """Zählt bevorzugte Paare im Ticket."""
    count = 0
    for pair in combinations(sorted(numbers), 2):
        if pair in FAVORED_PAIRS:
            count += 1
    return count


def is_valid_ticket(numbers):
    """
    Prüft ob ein Ticket alle Constraints erfüllt.

    Constraints:
    1. Keine 3+ konsekutiven Zahlen
    2. Spread >= 55
    3. Balance Score >= 0.88
    4. Mindestens 5 Dekaden abgedeckt
    5. Keine verbotenen Paare (streng) oder max 1 (locker)
    """
    if has_consecutive_triplet(numbers):
        return False, "3+ consecutive"

    spread = calculate_spread(numbers)
    if spread < 55:
        return False, f"Spread too low ({spread})"

    balance = calculate_balance_score(numbers)
    if balance < 0.88:
        return False, f"Balance too low ({balance})"

    decades = count_decades_covered(numbers)
    if decades < 5:
        return False, f"Too few decades ({decades})"

    forbidden = count_forbidden_pairs(numbers)
    if forbidden > 1:
        return False, f"Too many forbidden pairs ({forbidden})"

    return True, "valid"


def generate_constrained_ticket(pool_numbers, max_attempts=1000):
    """
    Generiert ein Ticket das alle Constraints erfüllt.

    Args:
        pool_numbers: Liste von Kandidaten-Zahlen
        max_attempts: Maximale Versuche

    Returns:
        Liste von 9 Zahlen oder None
    """
    # Strategie: Bevorzuge Zahlen die in bevorzugten Paaren vorkommen
    favored_numbers = set()
    for p1, p2 in FAVORED_PAIRS:
        if p1 in pool_numbers:
            favored_numbers.add(p1)
        if p2 in pool_numbers:
            favored_numbers.add(p2)

    # Meide Zahlen die oft in verbotenen Paaren vorkommen
    forbidden_counts = defaultdict(int)
    for p1, p2 in FORBIDDEN_PAIRS:
        forbidden_counts[p1] += 1
        forbidden_counts[p2] += 1

    # Sortiere Pool nach Präferenz
    def preference_score(n):
        score = 0
        if n in favored_numbers:
            score += 10
        score -= forbidden_counts.get(n, 0)
        return score

    weighted_pool = sorted(pool_numbers, key=preference_score, reverse=True)

    for attempt in range(max_attempts):
        # Wähle 9 Zahlen
        if attempt < max_attempts // 2:
            # Erst: Bevorzuge top-gewichtete Zahlen
            n_preferred = min(6, len(weighted_pool[:20]))
            ticket = random.sample(weighted_pool[:20], n_preferred)
            remaining = [x for x in weighted_pool if x not in ticket]
            ticket.extend(random.sample(remaining, 9 - len(ticket)))
        else:
            # Später: Mehr Zufälligkeit
            ticket = random.sample(pool_numbers, 9)

        valid, reason = is_valid_ticket(ticket)
        if valid:
            return sorted(ticket)

    return None


def calculate_frequency_zone(df, window=50):
    """
    Berechnet die Hot Zone basierend auf Frequenz.
    """
    recent = df.tail(window)

    freq = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq[num] += 1

    # Top 35 (oberes Drittel, plus Buffer)
    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:35]]


def backtest_strategy(df, start_date="2024-01-01"):
    """
    Walk-Forward Backtest der Combined Constraint Strategy.
    """
    start_dt = pd.Timestamp(start_date)
    start_idx = df[df["datum"] >= start_dt].index[0]

    results = []
    tickets_generated = []

    for i in range(start_idx, len(df)):
        current = df.iloc[i]
        current_date = current["datum"]
        current_numbers = set(current["zahlen"])

        # Historische Daten
        hist = df.iloc[:i]

        # Hot Zone berechnen
        hot_zone = calculate_frequency_zone(hist, window=50)

        # Constrained Ticket generieren
        ticket = generate_constrained_ticket(hot_zone)

        if ticket is None:
            # Fallback: Einfaches Frequenz-Ticket
            ticket = hot_zone[:9]

        ticket_set = set(ticket)

        # Performance messen
        hits = len(current_numbers & ticket_set)
        win = KENO_QUOTES.get(hits, 0)

        # Constraint-Checks für Analyse
        spread = calculate_spread(ticket)
        balance = calculate_balance_score(ticket)
        decades = count_decades_covered(ticket)
        forbidden = count_forbidden_pairs(ticket)
        favored = count_favored_pairs(ticket)
        has_triplet = has_consecutive_triplet(ticket)

        results.append({
            "datum": current_date.strftime("%Y-%m-%d"),
            "ticket": ticket,
            "hits": hits,
            "win": win,
            "spread": spread,
            "balance": balance,
            "decades": decades,
            "forbidden_pairs": forbidden,
            "favored_pairs": favored,
            "has_triplet": has_triplet,
        })

        if i % 100 == 0:
            print(f"  Processed {i - start_idx + 1} draws...")

    return results


def analyze_results(results):
    """Analysiere Backtest-Ergebnisse."""
    n = len(results)
    total_stake = n
    total_win = sum(r["win"] for r in results)
    netto = total_win - total_stake
    roi = (total_win / total_stake - 1) * 100

    avg_hits = sum(r["hits"] for r in results) / n
    expected_hits = 20 * 9 / 70  # ~2.57
    lift = avg_hits / expected_hits

    # Treffer-Verteilung
    hit_dist = defaultdict(int)
    for r in results:
        hit_dist[r["hits"]] += 1

    # Constraint-Statistiken
    avg_spread = sum(r["spread"] for r in results) / n
    avg_balance = sum(r["balance"] for r in results) / n
    avg_decades = sum(r["decades"] for r in results) / n
    avg_forbidden = sum(r["forbidden_pairs"] for r in results) / n
    avg_favored = sum(r["favored_pairs"] for r in results) / n
    triplet_violations = sum(1 for r in results if r["has_triplet"])

    return {
        "total_draws": n,
        "total_stake": total_stake,
        "total_win": total_win,
        "netto": netto,
        "roi": roi,
        "avg_hits": avg_hits,
        "expected_hits": expected_hits,
        "lift": lift,
        "hit_distribution": dict(sorted(hit_dist.items())),
        "constraint_stats": {
            "avg_spread": avg_spread,
            "avg_balance": avg_balance,
            "avg_decades": avg_decades,
            "avg_forbidden_pairs": avg_forbidden,
            "avg_favored_pairs": avg_favored,
            "triplet_violations": triplet_violations,
        }
    }


def compare_with_baseline(df, start_date="2024-01-01"):
    """
    Vergleicht Combined Strategy mit Baseline (nur Frequenz).
    """
    start_dt = pd.Timestamp(start_date)
    start_idx = df[df["datum"] >= start_dt].index[0]

    baseline_results = []
    combined_results = []

    for i in range(start_idx, len(df)):
        current = df.iloc[i]
        current_numbers = set(current["zahlen"])

        hist = df.iloc[:i]
        hot_zone = calculate_frequency_zone(hist, window=50)

        # Baseline: Einfach Top 9
        baseline_ticket = set(hot_zone[:9])
        baseline_hits = len(current_numbers & baseline_ticket)

        # Combined: Mit Constraints
        combined_ticket = generate_constrained_ticket(hot_zone)
        if combined_ticket is None:
            combined_ticket = hot_zone[:9]
        combined_hits = len(current_numbers & set(combined_ticket))

        baseline_results.append(baseline_hits)
        combined_results.append(combined_hits)

    return {
        "baseline": {
            "avg_hits": sum(baseline_results) / len(baseline_results),
            "lift": sum(baseline_results) / len(baseline_results) / (20 * 9 / 70),
        },
        "combined": {
            "avg_hits": sum(combined_results) / len(combined_results),
            "lift": sum(combined_results) / len(combined_results) / (20 * 9 / 70),
        },
        "improvement": sum(combined_results) / len(combined_results) - sum(baseline_results) / len(baseline_results),
    }


def main():
    print("=" * 80)
    print("COMBINED CONSTRAINT STRATEGY")
    print("Synthesis of Think Tank Findings")
    print("=" * 80)

    # Daten laden
    print("\n[1] Loading KENO data...")
    df = load_data()
    print(f"    Loaded {len(df)} draws from {df['datum'].min().date()} to {df['datum'].max().date()}")

    # Constraint-Zusammenfassung
    print("\n[2] Active Constraints:")
    print("    1. NO 3+ consecutive numbers (found -26% in data)")
    print("    2. Spread >= 55 (95% boundary)")
    print("    3. Balance Score >= 0.88 (95% boundary)")
    print("    4. At least 5 decades covered")
    print("    5. Max 1 forbidden pair per ticket")
    print(f"    Forbidden pairs: {len(FORBIDDEN_PAIRS)}")
    print(f"    Favored pairs: {len(FAVORED_PAIRS)}")

    # Backtest
    print("\n[3] Running Walk-Forward Backtest from 2024-01-01...")
    results = backtest_strategy(df, "2024-01-01")

    # Analyse
    print("\n[4] Analyzing Results...")
    stats = analyze_results(results)

    print("\n" + "=" * 80)
    print("BACKTEST RESULTS")
    print("=" * 80)

    print(f"\nPerformance (2024-01-01 bis heute):")
    print(f"  Draws: {stats['total_draws']}")
    print(f"  Avg Hits: {stats['avg_hits']:.2f} (Expected: {stats['expected_hits']:.2f})")
    print(f"  Lift: {stats['lift']:.4f}x")
    print(f"  Stake: {stats['total_stake']} EUR")
    print(f"  Win: {stats['total_win']} EUR")
    print(f"  Netto: {stats['netto']:+} EUR")
    print(f"  ROI: {stats['roi']:+.1f}%")

    print(f"\nHit Distribution:")
    for hits, count in sorted(stats['hit_distribution'].items()):
        pct = count / stats['total_draws'] * 100
        win = KENO_QUOTES.get(hits, 0)
        print(f"    {hits} hits: {count:4}x ({pct:5.1f}%) = {win} EUR")

    print(f"\nConstraint Statistics:")
    cs = stats['constraint_stats']
    print(f"    Avg Spread: {cs['avg_spread']:.1f}")
    print(f"    Avg Balance: {cs['avg_balance']:.4f}")
    print(f"    Avg Decades: {cs['avg_decades']:.2f}")
    print(f"    Avg Forbidden Pairs: {cs['avg_forbidden_pairs']:.2f}")
    print(f"    Avg Favored Pairs: {cs['avg_favored_pairs']:.2f}")
    print(f"    Triplet Violations: {cs['triplet_violations']}")

    # Vergleich mit Baseline
    print("\n[5] Comparing with Baseline...")
    comparison = compare_with_baseline(df, "2024-01-01")

    print(f"\nBaseline (Pure Frequency):")
    print(f"    Avg Hits: {comparison['baseline']['avg_hits']:.4f}")
    print(f"    Lift: {comparison['baseline']['lift']:.4f}x")

    print(f"\nCombined (With Constraints):")
    print(f"    Avg Hits: {comparison['combined']['avg_hits']:.4f}")
    print(f"    Lift: {comparison['combined']['lift']:.4f}x")

    improvement_pct = (comparison['improvement'] / comparison['baseline']['avg_hits']) * 100
    print(f"\nImprovement: {comparison['improvement']:+.4f} hits ({improvement_pct:+.2f}%)")

    # Nächstes Ticket generieren
    print("\n" + "=" * 80)
    print("NEXT TICKET RECOMMENDATION")
    print("=" * 80)

    hot_zone = calculate_frequency_zone(df, window=50)
    next_ticket = generate_constrained_ticket(hot_zone)

    if next_ticket:
        print(f"\nHot Zone (Top 35): {hot_zone}")
        print(f"\nRecommended Ticket (9 numbers):")
        print(f"  {next_ticket}")

        # Ticket-Analyse
        print(f"\nTicket Analysis:")
        print(f"    Spread: {calculate_spread(next_ticket)}")
        print(f"    Balance: {calculate_balance_score(next_ticket)}")
        print(f"    Decades: {count_decades_covered(next_ticket)}")
        print(f"    Forbidden Pairs: {count_forbidden_pairs(next_ticket)}")
        print(f"    Favored Pairs: {count_favored_pairs(next_ticket)}")
        print(f"    Has Triplet: {has_consecutive_triplet(next_ticket)}")
    else:
        print("\nWarning: Could not generate valid constrained ticket!")
        print(f"Using fallback: {hot_zone[:9]}")

    # Ergebnisse speichern
    RESULTS_DIR.mkdir(exist_ok=True)
    output = {
        "timestamp": datetime.now().isoformat(),
        "strategy": "Combined Constraint Strategy",
        "constraints": {
            "no_consecutive_triplets": True,
            "min_spread": 55,
            "min_balance": 0.88,
            "min_decades": 5,
            "max_forbidden_pairs": 1,
        },
        "backtest_results": stats,
        "comparison": comparison,
        "next_ticket": {
            "numbers": next_ticket if next_ticket else hot_zone[:9],
            "hot_zone": hot_zone,
        },
        "think_tank_sources": [
            "results/think_tank_nearmiss.json",
            "results/think_tank_consecutive.json",
            "results/think_tank_entropy.json",
        ],
    }

    output_file = RESULTS_DIR / "combined_constraint_strategy.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {output_file}")


if __name__ == "__main__":
    main()
