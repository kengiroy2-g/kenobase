#!/usr/bin/env python3
"""
HYPOTHESE: Pool-Evolution vor Jackpots

THESE:
Wenn ein Pool am Tag 1 generiert wird mit [a,b,c,d,e,x,y,z]
und einige Tage spaeter Typ 6/6 erscheint mit [a,b,c,d,x,y],
koennte es sein, dass bei taeglicher Pool-Neuberechnung
e und z bereits VOR dem Jackpot-Tag eliminiert wurden.

TEST:
1. Finde alle 6/6 (oder hohe Gewinnklassen)
2. Fuer jeden: Generiere Pool N Tage vorher
3. Generiere Pool jeden Tag bis zum Jackpot
4. Miss ob "Nicht-Jackpot-Zahlen" progressiv eliminiert werden

Autor: Kenobase V2
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np


# ============================================================================
# POOL-GENERATOR (aus generate_optimized_pool_v2.py)
# ============================================================================

BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}

BAD_PATTERNS = {
    "0010010", "1000111", "0101011", "1010000", "0001101",
    "0001000", "0100100", "0001010", "0000111",
}


def load_keno_data(filepath: Path) -> List[Dict]:
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
                    data.append({"datum": datum, "zahlen": set(numbers)})
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_hot_numbers(draws: List[Dict], lookback: int = 3) -> Set[int]:
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_index(draws: List[Dict], number: int) -> int:
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def get_count(draws: List[Dict], number: int, lookback: int = 30) -> int:
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_streak(draws: List[Dict], number: int) -> int:
    if not draws:
        return 0
    streak = 0
    in_last = number in draws[-1]["zahlen"]
    for draw in reversed(draws):
        if (number in draw["zahlen"]) == in_last:
            streak += 1
        else:
            break
    return streak if in_last else -streak


def get_pattern_7(draws: List[Dict], number: int) -> str:
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_avg_gap(draws: List[Dict], number: int, lookback: int = 60) -> float:
    gaps = []
    last_seen = None
    for i, draw in enumerate(draws[-lookback:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return np.mean(gaps) if gaps else 10.0


def score_number_v2(draws: List[Dict], number: int, hot: Set[int]) -> float:
    score = 50.0
    pattern = get_pattern_7(draws, number)
    if pattern in BAD_PATTERNS:
        score -= 20
    streak = get_streak(draws, number)
    if streak >= 3:
        score -= 10
    elif streak <= -5:
        score -= 5
    elif 0 < streak <= 2:
        score += 5
    avg_gap = get_avg_gap(draws, number)
    if avg_gap <= 3:
        score += 10
    elif avg_gap > 5:
        score -= 5
    index = get_index(draws, number)
    if index >= 10:
        score -= 5
    elif 3 <= index <= 6:
        score += 5
    ones = pattern.count("1")
    if ones == 2 or ones == 3:
        score += 5
    elif ones >= 5:
        score -= 5
    return score


def build_pool_v2(draws: List[Dict], target_size: int = 17) -> Set[int]:
    """Generiert Pool aus Ziehungen bis zu diesem Zeitpunkt."""
    if len(draws) < 10:
        return set()

    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number_v2(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)
    hot_keep = set(z for z, s in hot_scored[:5])

    cold_bd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot))
                      for z in cold_birthday]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored
                        if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:6])
    if len(cold_bd_keep) < 6:
        remaining = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(remaining[:6 - len(cold_bd_keep)])

    cold_nbd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot))
                       for z in cold_nonbd]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_nbd_filtered = [(z, c, s) for z, c, s in cold_nbd_scored
                         if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_nbd_keep = set(z for z, c, s in cold_nbd_filtered[:6])
    if len(cold_nbd_keep) < 6:
        remaining = [z for z, c, s in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(remaining[:6 - len(cold_nbd_keep)])

    return hot_keep | cold_bd_keep | cold_nbd_keep


# ============================================================================
# HYPOTHESE TEST
# ============================================================================

def find_high_wins(draws: List[Dict], min_overlap: int = 6) -> List[Dict]:
    """
    Finde Ziehungen wo ein Typ-6 Ticket 6/6 getroffen haette.
    Da wir keine echten Jackpot-Daten haben, simulieren wir:
    Eine Ziehung ist "interessant" wenn der Pool von N Tagen vorher
    mindestens 6 Treffer haette.
    """
    high_wins = []

    for i in range(30, len(draws)):
        # Generiere Pool von vor 7 Tagen
        draws_before = draws[:i-7]
        if len(draws_before) < 30:
            continue

        pool_7d_ago = build_pool_v2(draws_before)
        if not pool_7d_ago:
            continue

        jackpot_numbers = draws[i]["zahlen"]
        overlap = pool_7d_ago & jackpot_numbers

        if len(overlap) >= min_overlap:
            high_wins.append({
                "index": i,
                "datum": draws[i]["datum"],
                "jackpot": jackpot_numbers,
                "overlap": overlap,
                "pool_7d_ago": pool_7d_ago
            })

    return high_wins


def analyze_pool_evolution(draws: List[Dict], jackpot_idx: int, lookback_days: int = 10):
    """
    Analysiere wie sich der Pool in den Tagen vor dem Jackpot entwickelt.

    Returns:
        Dict mit Evolution-Metriken
    """
    jackpot_numbers = draws[jackpot_idx]["zahlen"]
    results = []

    for days_before in range(lookback_days, 0, -1):
        idx = jackpot_idx - days_before
        if idx < 30:
            continue

        draws_until = draws[:idx]
        pool = build_pool_v2(draws_until)

        if not pool:
            continue

        # Metriken
        overlap = pool & jackpot_numbers  # Treffer
        non_overlap = pool - jackpot_numbers  # Nicht-Jackpot-Zahlen im Pool

        results.append({
            "days_before": days_before,
            "pool_size": len(pool),
            "overlap_count": len(overlap),
            "non_overlap_count": len(non_overlap),
            "overlap": sorted(overlap),
            "non_overlap": sorted(non_overlap),
            "precision": len(overlap) / len(pool) if pool else 0
        })

    return results


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print("=" * 80)
    print("HYPOTHESE: Pool-Evolution vor Jackpots")
    print("=" * 80)
    print(f"\nGeladene Ziehungen: {len(draws)}")
    print(f"Zeitraum: {draws[0]['datum'].strftime('%d.%m.%Y')} - {draws[-1]['datum'].strftime('%d.%m.%Y')}")
    print()

    # Finde "High-Win" Events (Pool hatte >= 6 Treffer)
    print("Suche Events wo Pool >= 6 Treffer hatte...")
    high_wins = find_high_wins(draws, min_overlap=6)
    print(f"Gefunden: {len(high_wins)} Events\n")

    if not high_wins:
        print("Keine Events gefunden. Versuche mit min_overlap=5...")
        high_wins = find_high_wins(draws, min_overlap=5)
        print(f"Gefunden: {len(high_wins)} Events\n")

    # Analysiere Pool-Evolution fuer erste 10 Events
    evolution_stats = {
        "non_overlap_eliminated": [],  # Wie viele Nicht-Jackpot-Zahlen wurden eliminiert
        "precision_improvement": [],    # Praezisions-Verbesserung von Tag-10 zu Tag-1
    }

    print("=" * 80)
    print("POOL-EVOLUTION ANALYSE")
    print("=" * 80)

    for event in high_wins[:20]:  # Analysiere bis zu 20 Events
        evolution = analyze_pool_evolution(draws, event["index"], lookback_days=10)

        if len(evolution) < 5:
            continue

        print(f"\n--- Event: {event['datum'].strftime('%d.%m.%Y')} ---")
        print(f"Jackpot-Zahlen: {sorted(event['jackpot'])}")
        print()

        first_day = evolution[0]  # Tag -10 (oder fruehester)
        last_day = evolution[-1]  # Tag -1 (direkt vor Jackpot)

        print(f"{'Tage vorher':>12} {'Pool':>6} {'Treffer':>8} {'Nicht-JP':>10} {'Praezision':>10}")
        print("-" * 52)

        for e in evolution:
            print(f"{e['days_before']:>12} {e['pool_size']:>6} {e['overlap_count']:>8} "
                  f"{e['non_overlap_count']:>10} {e['precision']*100:>9.1f}%")

        # Statistiken sammeln
        non_overlap_reduction = first_day["non_overlap_count"] - last_day["non_overlap_count"]
        precision_improvement = last_day["precision"] - first_day["precision"]

        evolution_stats["non_overlap_eliminated"].append(non_overlap_reduction)
        evolution_stats["precision_improvement"].append(precision_improvement)

        # Zeige welche Zahlen eliminiert wurden
        eliminated = set(first_day["non_overlap"]) - set(last_day["non_overlap"])
        if eliminated:
            print(f"\nEliminierte Nicht-JP-Zahlen: {sorted(eliminated)}")

        # Zeige welche Nicht-JP-Zahlen noch im finalen Pool sind
        print(f"Noch im finalen Pool (Nicht-JP): {sorted(last_day['non_overlap'])}")

    # Gesamt-Statistik
    print("\n" + "=" * 80)
    print("GESAMT-STATISTIK")
    print("=" * 80)

    if evolution_stats["non_overlap_eliminated"]:
        avg_eliminated = np.mean(evolution_stats["non_overlap_eliminated"])
        avg_precision_imp = np.mean(evolution_stats["precision_improvement"])

        print(f"\nAnalysierte Events: {len(evolution_stats['non_overlap_eliminated'])}")
        print(f"\nDurchschnittlich eliminierte Nicht-JP-Zahlen: {avg_eliminated:.2f}")
        print(f"Durchschnittliche Praezisions-Verbesserung: {avg_precision_imp*100:.2f}%")

        # Wie oft wurde mindestens 1 Nicht-JP-Zahl eliminiert?
        events_with_elimination = sum(1 for x in evolution_stats["non_overlap_eliminated"] if x > 0)
        print(f"\nEvents mit Elimination: {events_with_elimination}/{len(evolution_stats['non_overlap_eliminated'])} "
              f"({events_with_elimination/len(evolution_stats['non_overlap_eliminated'])*100:.1f}%)")

        # Hypothese bestaetigt wenn avg_eliminated > 0
        print("\n" + "=" * 80)
        if avg_eliminated > 0.5:
            print("HYPOTHESE UNTERSTUETZT!")
            print(f"Der dynamische Pool eliminiert im Schnitt {avg_eliminated:.1f} Nicht-Jackpot-Zahlen")
            print("bevor der Jackpot eintritt.")
        else:
            print("HYPOTHESE NICHT BESTAETIGT")
            print("Der Pool aendert sich nicht signifikant vor Jackpots.")

    # Export
    results = {
        "events_analyzed": len(evolution_stats["non_overlap_eliminated"]),
        "avg_non_overlap_eliminated": float(np.mean(evolution_stats["non_overlap_eliminated"])) if evolution_stats["non_overlap_eliminated"] else 0,
        "avg_precision_improvement": float(np.mean(evolution_stats["precision_improvement"])) if evolution_stats["precision_improvement"] else 0,
        "hypothesis_supported": float(np.mean(evolution_stats["non_overlap_eliminated"])) > 0.5 if evolution_stats["non_overlap_eliminated"] else False,
    }

    results_path = base_path / "results" / "pool_evolution_hypothesis.json"
    import json
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nErgebnisse gespeichert: {results_path}")


if __name__ == "__main__":
    main()
