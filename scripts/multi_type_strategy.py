#!/usr/bin/env python
"""
Multi-Type KENO Strategy Analysis
=================================

Vergleicht die Combined Constraint Strategy für verschiedene KENO-Typen:
- Typ 6 (6 Zahlen, GK6_6 = 500€)
- Typ 7 (7 Zahlen, GK7_7 = 5.000€)
- Typ 8 (8 Zahlen, GK8_8 = 10.000€)
- Typ 9 (9 Zahlen, GK9_9 = 50.000€)

Ziel: Finden des optimalen Ticket-Typs für unsere Constraint-Strategie.

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

# KENO Quoten nach Typ (Einsatz 1€)
KENO_QUOTES = {
    6: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 15, 6: 500},
    7: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 6, 6: 100, 7: 5000},
    8: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 15, 7: 100, 8: 10000},
    9: {0: 2, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 5, 7: 20, 8: 1000, 9: 50000},
    10: {0: 2, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000},
}

# Verbotene und bevorzugte Paare (aus Think Tank)
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
    if len(numbers) < 3:
        return False
    sorted_nums = sorted(numbers)
    for i in range(len(sorted_nums) - 2):
        if sorted_nums[i+1] == sorted_nums[i] + 1 and sorted_nums[i+2] == sorted_nums[i] + 2:
            return True
    return False


def calculate_spread(numbers):
    """Berechnet Spread (Max - Min)."""
    return max(numbers) - min(numbers)


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


def is_valid_ticket_for_type(numbers, ticket_type):
    """
    Prüft ob ein Ticket die Constraints für einen bestimmten Typ erfüllt.

    Angepasste Constraints pro Typ:
    - Typ 6: Spread >= 30, min 3 Dekaden
    - Typ 7: Spread >= 35, min 4 Dekaden
    - Typ 8: Spread >= 45, min 4 Dekaden
    - Typ 9: Spread >= 55, min 5 Dekaden
    """
    # Keine 3er-Sequenzen (für alle Typen)
    if has_consecutive_triplet(numbers):
        return False, "3+ consecutive"

    # Typ-spezifische Spread-Anforderungen
    spread_requirements = {6: 30, 7: 35, 8: 45, 9: 55}
    min_spread = spread_requirements.get(ticket_type, 30)

    spread = calculate_spread(numbers)
    if spread < min_spread:
        return False, f"Spread too low ({spread} < {min_spread})"

    # Typ-spezifische Dekaden-Anforderungen
    decade_requirements = {6: 3, 7: 4, 8: 4, 9: 5}
    min_decades = decade_requirements.get(ticket_type, 3)

    decades = count_decades_covered(numbers)
    if decades < min_decades:
        return False, f"Too few decades ({decades} < {min_decades})"

    # Verbotene Paare (max 1 für alle)
    forbidden = count_forbidden_pairs(numbers)
    if forbidden > 1:
        return False, f"Too many forbidden pairs ({forbidden})"

    return True, "valid"


def generate_constrained_ticket(pool_numbers, ticket_size, max_attempts=1000):
    """
    Generiert ein Ticket das alle Constraints erfüllt.
    """
    # Bevorzuge Zahlen aus bevorzugten Paaren
    favored_numbers = set()
    for p1, p2 in FAVORED_PAIRS:
        if p1 in pool_numbers:
            favored_numbers.add(p1)
        if p2 in pool_numbers:
            favored_numbers.add(p2)

    # Meide Zahlen aus verbotenen Paaren
    forbidden_counts = defaultdict(int)
    for p1, p2 in FORBIDDEN_PAIRS:
        forbidden_counts[p1] += 1
        forbidden_counts[p2] += 1

    def preference_score(n):
        score = 0
        if n in favored_numbers:
            score += 10
        score -= forbidden_counts.get(n, 0)
        return score

    weighted_pool = sorted(pool_numbers, key=preference_score, reverse=True)

    for attempt in range(max_attempts):
        if attempt < max_attempts // 2:
            # Erst: Top-gewichtete Zahlen bevorzugen
            n_preferred = min(ticket_size - 1, len(weighted_pool[:20]))
            ticket = random.sample(weighted_pool[:min(20, len(weighted_pool))], n_preferred)
            remaining = [x for x in weighted_pool if x not in ticket]
            if len(remaining) >= ticket_size - len(ticket):
                ticket.extend(random.sample(remaining, ticket_size - len(ticket)))
        else:
            # Später: Mehr Zufälligkeit
            if len(pool_numbers) >= ticket_size:
                ticket = random.sample(pool_numbers, ticket_size)
            else:
                continue

        if len(ticket) != ticket_size:
            continue

        valid, reason = is_valid_ticket_for_type(ticket, ticket_size)
        if valid:
            return sorted(ticket)

    return None


def calculate_frequency_zone(df, window=50):
    """Berechnet die Hot Zone basierend auf Frequenz."""
    recent = df.tail(window)

    freq = defaultdict(int)
    for zahlen in recent["zahlen"]:
        for num in zahlen:
            freq[num] += 1

    sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
    return [n for n, _ in sorted_nums[:35]]


def backtest_type(df, ticket_type, start_date="2024-01-01"):
    """
    Backtest für einen bestimmten KENO-Typ.
    """
    start_dt = pd.Timestamp(start_date)
    start_idx = df[df["datum"] >= start_dt].index[0]

    quotes = KENO_QUOTES[ticket_type]
    results = []

    for i in range(start_idx, len(df)):
        current = df.iloc[i]
        current_date = current["datum"]
        current_numbers = set(current["zahlen"])

        hist = df.iloc[:i]
        hot_zone = calculate_frequency_zone(hist, window=50)

        # Constrained Ticket generieren
        ticket = generate_constrained_ticket(hot_zone, ticket_type)

        if ticket is None:
            # Fallback
            ticket = hot_zone[:ticket_type]

        ticket_set = set(ticket)

        # Performance messen
        hits = len(current_numbers & ticket_set)
        win = quotes.get(hits, 0)

        results.append({
            "datum": current_date.strftime("%Y-%m-%d"),
            "ticket": ticket,
            "hits": hits,
            "win": win,
        })

    return results


def analyze_type_results(results, ticket_type):
    """Analysiere Ergebnisse für einen Typ."""
    n = len(results)
    total_stake = n
    total_win = sum(r["win"] for r in results)
    netto = total_win - total_stake
    roi = (total_win / total_stake - 1) * 100

    avg_hits = sum(r["hits"] for r in results) / n
    expected_hits = 20 * ticket_type / 70
    lift = avg_hits / expected_hits

    # Treffer-Verteilung
    hit_dist = defaultdict(int)
    for r in results:
        hit_dist[r["hits"]] += 1

    # Beste Gewinne
    best_wins = sorted([r for r in results if r["win"] > 0], key=lambda x: -x["win"])[:10]

    # Vollgewinne (alle Zahlen richtig)
    jackpots = sum(1 for r in results if r["hits"] == ticket_type)

    return {
        "ticket_type": ticket_type,
        "total_draws": n,
        "total_stake": total_stake,
        "total_win": total_win,
        "netto": netto,
        "roi": roi,
        "avg_hits": avg_hits,
        "expected_hits": expected_hits,
        "lift": lift,
        "hit_distribution": dict(sorted(hit_dist.items())),
        "jackpots": jackpots,
        "best_wins": [{"datum": w["datum"], "hits": w["hits"], "win": w["win"]} for w in best_wins[:5]],
    }


def calculate_theoretical_probabilities():
    """
    Berechnet theoretische Wahrscheinlichkeiten für verschiedene Gewinnklassen.
    """
    from math import comb

    results = {}

    for ticket_type in [6, 7, 8, 9, 10]:
        probs = {}
        for hits in range(ticket_type + 1):
            # Hypergeometrische Verteilung
            # P(k hits) = C(20, k) * C(50, n-k) / C(70, n)
            # wobei n = ticket_type, k = hits
            p = comb(20, hits) * comb(70 - 20, ticket_type - hits) / comb(70, ticket_type)
            probs[hits] = p

        # Erwarteter Wert
        quotes = KENO_QUOTES[ticket_type]
        ev = sum(probs[h] * quotes.get(h, 0) for h in range(ticket_type + 1))

        results[ticket_type] = {
            "probabilities": probs,
            "expected_value": ev,
            "house_edge": (1 - ev) * 100,
            "jackpot_prob": probs[ticket_type],
            "jackpot_odds": f"1:{int(1/probs[ticket_type]):,}" if probs[ticket_type] > 0 else "N/A"
        }

    return results


def main():
    print("=" * 80)
    print("MULTI-TYPE KENO STRATEGY ANALYSIS")
    print("Vergleich: Typ 6, 7, 8, 9")
    print("=" * 80)

    # Daten laden
    print("\n[1] Loading KENO data...")
    df = load_data()
    print(f"    Loaded {len(df)} draws")

    # Theoretische Wahrscheinlichkeiten
    print("\n[2] Theoretical Analysis:")
    theory = calculate_theoretical_probabilities()

    print(f"\n    {'Typ':<6} {'Jackpot Odds':<18} {'EV':<8} {'House Edge':<12}")
    print("    " + "-" * 50)
    for t in [6, 7, 8, 9]:
        th = theory[t]
        print(f"    Typ {t:<3} {th['jackpot_odds']:<18} {th['expected_value']:.4f}   {th['house_edge']:.2f}%")

    # Backtest für jeden Typ
    print("\n[3] Running Backtests (2024-01-01 to today)...")

    all_results = {}
    for ticket_type in [6, 7, 8, 9]:
        print(f"\n    Testing Typ {ticket_type}...")
        results = backtest_type(df, ticket_type, "2024-01-01")
        stats = analyze_type_results(results, ticket_type)
        all_results[ticket_type] = stats

    # Ergebnisse vergleichen
    print("\n" + "=" * 80)
    print("BACKTEST RESULTS COMPARISON")
    print("=" * 80)

    print(f"\n{'Typ':<6} {'Draws':<8} {'Avg Hits':<10} {'Lift':<8} {'Jackpots':<10} {'ROI':<10} {'Netto':<10}")
    print("-" * 70)

    for t in [6, 7, 8, 9]:
        s = all_results[t]
        print(f"Typ {t:<3} {s['total_draws']:<8} {s['avg_hits']:<10.3f} {s['lift']:<8.4f} "
              f"{s['jackpots']:<10} {s['roi']:>+8.1f}%  {s['netto']:>+8} EUR")

    # Detail pro Typ
    for t in [6, 7, 8, 9]:
        s = all_results[t]
        print(f"\n--- TYP {t} DETAILS ---")
        print(f"Hit Distribution:")
        quotes = KENO_QUOTES[t]
        for hits, count in sorted(s['hit_distribution'].items()):
            pct = count / s['total_draws'] * 100
            win = quotes.get(hits, 0)
            total_won = count * win
            print(f"    {hits} hits: {count:4}x ({pct:5.1f}%) × {win:>6} EUR = {total_won:>8} EUR")

        if s['best_wins']:
            print(f"Best Wins:")
            for w in s['best_wins']:
                print(f"    {w['datum']}: {w['hits']} hits = {w['win']} EUR")

    # Bester Typ ermitteln
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)

    # Nach Lift
    best_lift = max(all_results.items(), key=lambda x: x[1]['lift'])
    print(f"\nBester Lift: Typ {best_lift[0]} ({best_lift[1]['lift']:.4f}x)")

    # Nach ROI
    best_roi = max(all_results.items(), key=lambda x: x[1]['roi'])
    print(f"Beste ROI: Typ {best_roi[0]} ({best_roi[1]['roi']:+.1f}%)")

    # Nach Netto
    best_netto = max(all_results.items(), key=lambda x: x[1]['netto'])
    print(f"Bestes Netto: Typ {best_netto[0]} ({best_netto[1]['netto']:+} EUR)")

    # Jackpot-Analyse
    print(f"\nJackpot-Analyse:")
    for t in [6, 7, 8, 9]:
        s = all_results[t]
        jackpot_value = KENO_QUOTES[t][t]
        if s['jackpots'] > 0:
            print(f"    Typ {t}: {s['jackpots']} Jackpots × {jackpot_value:,} EUR = {s['jackpots'] * jackpot_value:,} EUR! 🎉")
        else:
            expected_jackpots = s['total_draws'] * theory[t]['probabilities'][t]
            print(f"    Typ {t}: 0 Jackpots (erwartet: {expected_jackpots:.2f})")

    # Empfehlung
    print("\n" + "=" * 80)
    print("EMPFEHLUNG")
    print("=" * 80)

    # Finde den Typ mit bestem Verhältnis
    print("\nBasierend auf der Analyse:")

    for t in [6, 7, 8, 9]:
        s = all_results[t]
        th = theory[t]

        # Vergleich: Beobachtet vs Erwartet
        actual_ev = s['total_win'] / s['total_draws']
        theoretical_ev = th['expected_value']
        ev_improvement = ((actual_ev / theoretical_ev) - 1) * 100 if theoretical_ev > 0 else 0

        print(f"\nTyp {t}:")
        print(f"    Theoretischer EV: {theoretical_ev:.4f} EUR")
        print(f"    Beobachteter EV: {actual_ev:.4f} EUR")
        print(f"    Verbesserung durch Strategie: {ev_improvement:+.1f}%")

    # Nächstes Ticket für jeden Typ
    print("\n" + "=" * 80)
    print("NÄCHSTE TICKETS")
    print("=" * 80)

    hot_zone = calculate_frequency_zone(df, window=50)
    print(f"\nHot Zone: {hot_zone[:20]}...")

    for t in [6, 7, 8, 9]:
        ticket = generate_constrained_ticket(hot_zone, t)
        if ticket:
            forbidden = count_forbidden_pairs(ticket)
            favored = count_favored_pairs(ticket)
            spread = calculate_spread(ticket)
            decades = count_decades_covered(ticket)
            print(f"\nTyp {t}: {ticket}")
            print(f"    Spread: {spread}, Dekaden: {decades}, Forbidden: {forbidden}, Favored: {favored}")

    # Speichern
    RESULTS_DIR.mkdir(exist_ok=True)
    output = {
        "timestamp": datetime.now().isoformat(),
        "analysis": "Multi-Type KENO Strategy Comparison",
        "theoretical": {str(k): v for k, v in theory.items()},
        "backtest_results": {str(k): v for k, v in all_results.items()},
        "next_tickets": {
            str(t): generate_constrained_ticket(hot_zone, t) or hot_zone[:t]
            for t in [6, 7, 8, 9]
        },
        "hot_zone": hot_zone,
    }

    output_file = RESULTS_DIR / "multi_type_analysis.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved: {output_file}")


if __name__ == "__main__":
    main()
