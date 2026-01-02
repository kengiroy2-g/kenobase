#!/usr/bin/env python3
"""
Analyse: Paar-Kombinationen statt Einzelzahlen.

Hypothese: Das KENO-System korrigiert gegen einzelne populaere Zahlen,
aber Paar-Kombinationen koennten andere Muster zeigen.

Methode:
1. Fuer jedes Paar im Pool: Zaehle gemeinsames Erscheinen
2. Vergleiche mit Erwartung (bei Unabhaengigkeit)
3. Finde Paare die signifikant abweichen
4. Baue Tickets die auf "starken Paaren" basieren
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Tuple
import math

BIRTHDAY_POPULAR = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}


def load_keno_data(filepath: Path) -> List[Dict]:
    """Laedt KENO-Ziehungsdaten."""
    data = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                datum_str = row.get("Datum", "").strip()
                if not datum_str:
                    continue
                datum = datetime.strptime(datum_str, "%d.%m.%Y")
                numbers = []
                for i in range(1, 21):
                    col = f"Keno_Z{i}"
                    if col in row and row[col]:
                        numbers.append(int(row[col]))
                if len(numbers) == 20:
                    data.append({
                        "datum": datum,
                        "datum_str": datum_str,
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_momentum_numbers(draws: List[Dict], target_date: datetime, lookback: int = 3) -> Set[int]:
    """Holt Momentum-Zahlen."""
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set()
    recent = relevant[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def analyze_pairs(
    pool: Set[int],
    draws: List[Dict],
    start_date: datetime,
    end_date: datetime
) -> Dict:
    """Analysiert Paar-Haeufigkeiten."""
    test_draws = [d for d in draws if start_date <= d["datum"] <= end_date]
    n_draws = len(test_draws)

    # Einzelhaeufigkeiten
    single_counts = {z: 0 for z in pool}
    for draw in test_draws:
        for z in pool:
            if z in draw["zahlen"]:
                single_counts[z] += 1

    # Einzelwahrscheinlichkeiten
    single_probs = {z: c / n_draws for z, c in single_counts.items()}

    # Paar-Haeufigkeiten
    pair_counts = {}
    for z1, z2 in combinations(sorted(pool), 2):
        count = sum(1 for d in test_draws if z1 in d["zahlen"] and z2 in d["zahlen"])
        pair_counts[(z1, z2)] = count

    # Erwartete Paar-Haeufigkeit (bei Unabhaengigkeit)
    # E[pair] = n_draws * P(z1) * P(z2)
    pair_expected = {}
    pair_deviation = {}

    for (z1, z2), count in pair_counts.items():
        expected = n_draws * single_probs[z1] * single_probs[z2]
        pair_expected[(z1, z2)] = expected

        if expected > 0:
            deviation = (count - expected) / expected
        else:
            deviation = 0
        pair_deviation[(z1, z2)] = deviation

    return {
        "n_draws": n_draws,
        "single_counts": single_counts,
        "single_probs": single_probs,
        "pair_counts": pair_counts,
        "pair_expected": pair_expected,
        "pair_deviation": pair_deviation,
    }


def find_strong_weak_pairs(pair_deviation: Dict, threshold: float = 0.2) -> Tuple[List, List]:
    """Findet starke (ueber-repraesentierte) und schwache (unter-repraesentierte) Paare."""
    strong_pairs = [(p, d) for p, d in pair_deviation.items() if d > threshold]
    weak_pairs = [(p, d) for p, d in pair_deviation.items() if d < -threshold]

    strong_pairs.sort(key=lambda x: x[1], reverse=True)
    weak_pairs.sort(key=lambda x: x[1])

    return strong_pairs, weak_pairs


def build_ticket_from_pairs(strong_pairs: List, pool: Set[int], ticket_size: int) -> List[int]:
    """
    Baut ein Ticket aus den staerksten Paaren.

    Strategie: Waehle Zahlen die in vielen starken Paaren vorkommen.
    """
    # Zaehle wie oft jede Zahl in starken Paaren vorkommt
    pair_member_count = defaultdict(float)

    for (z1, z2), deviation in strong_pairs:
        # Gewichte nach Deviations-Staerke
        pair_member_count[z1] += deviation
        pair_member_count[z2] += deviation

    # Sortiere nach Gewicht
    sorted_numbers = sorted(pair_member_count.items(), key=lambda x: x[1], reverse=True)

    # Nimm die besten
    ticket = [z for z, _ in sorted_numbers[:ticket_size]]

    # Falls nicht genug, fuelle mit Pool-Zahlen auf
    if len(ticket) < ticket_size:
        remaining = [z for z in pool if z not in ticket]
        ticket.extend(remaining[:ticket_size - len(ticket)])

    return sorted(ticket)


def build_ticket_avoiding_weak_pairs(weak_pairs: List, pool: Set[int], ticket_size: int) -> List[int]:
    """
    Baut ein Ticket das schwache Paare vermeidet.

    Strategie: Vermeide Zahlen die oft in schwachen Paaren vorkommen.
    """
    # Zaehle wie oft jede Zahl in schwachen Paaren vorkommt
    weak_member_count = defaultdict(float)

    for (z1, z2), deviation in weak_pairs:
        weak_member_count[z1] += abs(deviation)
        weak_member_count[z2] += abs(deviation)

    # Sortiere Pool-Zahlen: zuerst die mit wenigsten schwachen Paaren
    sorted_numbers = sorted(pool, key=lambda z: weak_member_count.get(z, 0))

    return sorted(sorted_numbers[:ticket_size])


def build_ticket_maximal_connected(pair_counts: Dict, pool: Set[int], ticket_size: int, min_pair_count: int = 5) -> List[int]:
    """
    Baut ein Ticket wo alle Zahlen gut miteinander verbunden sind.

    Strategie: Finde eine Gruppe von Zahlen wo jedes Paar mindestens X mal zusammen erschien.
    """
    pool_list = sorted(pool)

    # Pruefe alle moeglichen Kombinationen (bei kleinem ticket_size machbar)
    best_ticket = None
    best_min_pair = 0

    for combo in combinations(pool_list, ticket_size):
        # Finde minimale Paar-Haeufigkeit in dieser Kombination
        min_pair = float('inf')
        for z1, z2 in combinations(combo, 2):
            pair = (min(z1, z2), max(z1, z2))
            count = pair_counts.get(pair, 0)
            min_pair = min(min_pair, count)

        if min_pair > best_min_pair:
            best_min_pair = min_pair
            best_ticket = combo

    return list(best_ticket) if best_ticket else pool_list[:ticket_size]


def test_ticket(ticket: List[int], draws: List[Dict], start_date: datetime, end_date: datetime) -> Dict:
    """Testet ein Ticket."""
    test_draws = [d for d in draws if start_date <= d["datum"] <= end_date]
    ticket_set = set(ticket)
    typ = len(ticket)

    hits = [len(ticket_set & d["zahlen"]) for d in test_draws]
    jackpots = sum(1 for h in hits if h == typ)
    near_miss = sum(1 for h in hits if h == typ - 1)

    return {
        "ticket": ticket,
        "typ": typ,
        "n_days": len(test_draws),
        "avg_hits": sum(hits) / len(hits) if hits else 0,
        "jackpots": jackpots,
        "near_miss": near_miss,
        "expected": typ * 20 / 70,
    }


def main():
    print("=" * 100)
    print("PAAR-KOMBINATIONEN ANALYSE")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Test-Setup
    stichtag = datetime(2025, 2, 1)
    train_end = datetime(2025, 4, 30)
    test_end = datetime(2025, 7, 31)

    # Pool
    momentum = get_momentum_numbers(draws, stichtag, lookback=3)
    pool = BIRTHDAY_POPULAR | momentum
    pool_list = sorted(pool)

    print(f"\nPool ({len(pool)} Zahlen): {pool_list}")
    print(f"Anzahl moeglicher Paare: {len(list(combinations(pool_list, 2)))}")

    # === TRAININGS-PHASE: Paar-Analyse ===
    print(f"\n{'='*100}")
    print(f"TRAININGS-ANALYSE: {stichtag.date()} bis {train_end.date()}")
    print(f"{'='*100}")

    pair_data = analyze_pairs(pool, draws, stichtag, train_end)

    print(f"\nZiehungen analysiert: {pair_data['n_draws']}")

    # Einzelhaeufigkeiten
    print(f"\n--- Einzelzahlen-Haeufigkeit ---")
    sorted_singles = sorted(pair_data['single_counts'].items(), key=lambda x: x[1], reverse=True)
    for z, count in sorted_singles[:10]:
        prob = pair_data['single_probs'][z]
        print(f"  {z}: {count}x ({prob*100:.1f}%)")

    # Starke und schwache Paare
    strong_pairs, weak_pairs = find_strong_weak_pairs(pair_data['pair_deviation'], threshold=0.3)

    print(f"\n--- STARKE PAARE (>30% ueber Erwartung) ---")
    print(f"Anzahl: {len(strong_pairs)}")
    for (z1, z2), dev in strong_pairs[:15]:
        count = pair_data['pair_counts'][(z1, z2)]
        expected = pair_data['pair_expected'][(z1, z2)]
        print(f"  ({z1}, {z2}): {count}x (erw. {expected:.1f}, {dev*100:+.0f}%)")

    print(f"\n--- SCHWACHE PAARE (>30% unter Erwartung) ---")
    print(f"Anzahl: {len(weak_pairs)}")
    for (z1, z2), dev in weak_pairs[:15]:
        count = pair_data['pair_counts'][(z1, z2)]
        expected = pair_data['pair_expected'][(z1, z2)]
        print(f"  ({z1}, {z2}): {count}x (erw. {expected:.1f}, {dev*100:+.0f}%)")

    # === TICKETS BAUEN ===
    print(f"\n{'='*100}")
    print("TICKETS BAUEN")
    print(f"{'='*100}")

    # Strategie 1: Staerkste Paare
    ticket_6_strong = build_ticket_from_pairs(strong_pairs, pool, 6)
    ticket_7_strong = build_ticket_from_pairs(strong_pairs, pool, 7)

    # Strategie 2: Schwache Paare vermeiden
    ticket_6_avoid = build_ticket_avoiding_weak_pairs(weak_pairs, pool, 6)
    ticket_7_avoid = build_ticket_avoiding_weak_pairs(weak_pairs, pool, 7)

    # Strategie 3: Maximal verbundene Zahlen
    ticket_6_connected = build_ticket_maximal_connected(pair_data['pair_counts'], pool, 6)
    ticket_7_connected = build_ticket_maximal_connected(pair_data['pair_counts'], pool, 7)

    tickets = [
        ("Typ6-StarkePaare", ticket_6_strong),
        ("Typ6-VermeideSchw", ticket_6_avoid),
        ("Typ6-MaxVerbunden", ticket_6_connected),
        ("Typ7-StarkePaare", ticket_7_strong),
        ("Typ7-VermeideSchw", ticket_7_avoid),
        ("Typ7-MaxVerbunden", ticket_7_connected),
    ]

    print("\nGenerierte Tickets:")
    for name, ticket in tickets:
        print(f"  {name}: {ticket}")

    # === TEST-PHASE ===
    print(f"\n{'='*100}")
    print(f"TEST-PHASE: {train_end.date()} bis {test_end.date()}")
    print(f"{'='*100}")

    print(f"\n{'Ticket':<20} {'Zahlen':<30} {'AvgHits':<10} {'vs.Erw.':<10} {'Jackpots':<10} {'NearMiss'}")
    print("-" * 100)

    for name, ticket in tickets:
        result = test_ticket(ticket, draws, train_end, test_end)
        diff_pct = (result['avg_hits'] / result['expected'] - 1) * 100
        print(f"{name:<20} {str(ticket):<30} {result['avg_hits']:<10.2f} {diff_pct:>+8.1f}%  {result['jackpots']:<10} {result['near_miss']}")

    # === ANALYSE: Warum funktioniert es (nicht)? ===
    print(f"\n{'='*100}")
    print("ANALYSE: Paar-Stabilitaet Train vs Test")
    print(f"{'='*100}")

    # Analysiere Paare auch in Test-Phase
    test_pair_data = analyze_pairs(pool, draws, train_end, test_end)

    # Vergleiche starke Paare: Sind sie im Test noch stark?
    print("\n--- Starke Paare aus Training: Wie im Test? ---")
    stable_strong = 0
    for (z1, z2), train_dev in strong_pairs[:10]:
        test_dev = test_pair_data['pair_deviation'].get((z1, z2), 0)
        train_count = pair_data['pair_counts'][(z1, z2)]
        test_count = test_pair_data['pair_counts'].get((z1, z2), 0)

        status = "STABIL" if test_dev > 0.1 else "INSTABIL"
        if test_dev > 0.1:
            stable_strong += 1
        print(f"  ({z1:>2}, {z2:>2}): Train {train_dev*100:+.0f}% ({train_count}x) → Test {test_dev*100:+.0f}% ({test_count}x) [{status}]")

    print(f"\n  Stabile starke Paare: {stable_strong}/10")

    # Vergleiche schwache Paare
    print("\n--- Schwache Paare aus Training: Wie im Test? ---")
    stable_weak = 0
    for (z1, z2), train_dev in weak_pairs[:10]:
        test_dev = test_pair_data['pair_deviation'].get((z1, z2), 0)
        train_count = pair_data['pair_counts'][(z1, z2)]
        test_count = test_pair_data['pair_counts'].get((z1, z2), 0)

        status = "STABIL" if test_dev < -0.1 else "INSTABIL"
        if test_dev < -0.1:
            stable_weak += 1
        print(f"  ({z1:>2}, {z2:>2}): Train {train_dev*100:+.0f}% ({train_count}x) → Test {test_dev*100:+.0f}% ({test_count}x) [{status}]")

    print(f"\n  Stabile schwache Paare: {stable_weak}/10")

    print(f"\n[Analyse abgeschlossen]")


if __name__ == "__main__":
    main()
