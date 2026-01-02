#!/usr/bin/env python3
"""
OPTIMIERTER POOL-GENERATOR V2

Nutzt die Erkenntnisse aus der Miss-Analyse:
1. Filtert Zahlen mit schlechten 7-Tage-Patterns
2. Bevorzugt Zahlen mit guenstigen Feature-Kombinationen
3. Beruecksichtigt Gap-Muster

Verbesserungen gegenueber V1:
- 7-Tage-Pattern Filter
- Streak-basierte Filterung
- Gap-basiertes Ranking
"""

import csv
import json
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np

# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}

# NEUE FILTER basierend auf Miss-Analyse
BAD_PATTERNS = {
    "0010010",  # 83.3% Miss
    "1000111",  # 82.1% Miss
    "0101011",  # 81.1% Miss
    "1010000",  # 80.4% Miss
    "0001101",  # 77.3% Miss
    "0001000",  # 77.1% Miss
    "0100100",  # 77.1% Miss
    "0001010",  # 77.0% Miss
    "0000111",  # 75.9% Miss
}

GOOD_PATTERNS = {
    "0011101",  # 55.6% Miss - BESTE!
    "1010011",  # 59.3% Miss
    "0001001",  # 60.3% Miss
    "1010101",  # 60.7% Miss
    "0010100",  # 62.1% Miss
    "1000001",  # 62.3% Miss
    "1000010",  # 63.1% Miss
    "0001011",  # 64.2% Miss
    "0010101",  # 64.9% Miss
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
    """7-Tage-Binaermuster."""
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_avg_gap(draws: List[Dict], number: int, lookback: int = 60) -> float:
    """Durchschnittliche Luecke zwischen Erscheinungen."""
    gaps = []
    last_seen = None
    for i, draw in enumerate(draws[-lookback:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return np.mean(gaps) if gaps else 10.0


def score_number_v2(draws: List[Dict], number: int, hot: Set[int]) -> float:
    """
    V2 Scoring: Beruecksichtigt Pattern, Streak, Gap
    Hoeherer Score = besser (weniger wahrscheinlich zu missen)
    """
    score = 50.0  # Basis

    # 1. Pattern-Check (STARK)
    pattern = get_pattern_7(draws, number)
    if pattern in BAD_PATTERNS:
        score -= 20  # Stark abwerten
    elif pattern in GOOD_PATTERNS:
        score += 15  # Bonus fuer gute Patterns

    # 2. Streak-Check
    streak = get_streak(draws, number)
    if streak >= 3:  # Zu heiss = schlecht
        score -= 10
    elif streak <= -5:  # Zu kalt = neutral
        score -= 5
    elif 0 < streak <= 2:  # Optimal
        score += 5

    # 3. Gap-Check
    avg_gap = get_avg_gap(draws, number)
    if avg_gap <= 3:  # Kleine Gaps = gut
        score += 10
    elif avg_gap > 5:  # Grosse Gaps = schlecht
        score -= 5

    # 4. Index-Check
    index = get_index(draws, number)
    if index >= 10:  # Zu lange nicht erschienen
        score -= 5
    elif 3 <= index <= 6:  # Optimal
        score += 5

    # 5. Ones in Pattern (Aktivitaet)
    ones = pattern.count("1")
    if ones == 2 or ones == 3:  # Moderate Aktivitaet = gut
        score += 5
    elif ones >= 5:  # Zu aktiv = schlecht
        score -= 5

    return score


def build_optimized_pool_v2(draws: List[Dict], target_size: int = 17) -> Tuple[Set[int], Dict]:
    """
    V2 Pool-Generierung mit Pattern-Filterung.
    """
    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    # HOT: Ohne Korrektur, sortiert nach V2-Score
    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number_v2(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)  # Hoechster Score zuerst
    hot_keep = set(z for z, s in hot_scored[:5])

    # COLD-Birthday: Niedrigster Count, aber mit V2-Filter
    cold_bd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot))
                      for z in cold_birthday]
    # Sortiere nach Count (niedrig), dann nach Score (hoch)
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))

    # Filtere Zahlen mit schlechtem Pattern
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored
                        if get_pattern_7(draws, z) not in BAD_PATTERNS]

    # Nimm die besten 6
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:6])

    # Falls nicht genug, nimm auch ungefilterte
    if len(cold_bd_keep) < 6:
        remaining = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(remaining[:6 - len(cold_bd_keep)])

    # COLD-Non-Birthday: Gleiche Logik
    cold_nbd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot))
                       for z in cold_nonbd]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))

    cold_nbd_filtered = [(z, c, s) for z, c, s in cold_nbd_scored
                         if get_pattern_7(draws, z) not in BAD_PATTERNS]

    cold_nbd_keep = set(z for z, c, s in cold_nbd_filtered[:6])

    if len(cold_nbd_keep) < 6:
        remaining = [z for z, c, s in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(remaining[:6 - len(cold_nbd_keep)])

    reduced_pool = hot_keep | cold_bd_keep | cold_nbd_keep

    # Details sammeln
    details = {
        "hot_keep": sorted(hot_keep),
        "cold_bd_keep": sorted(cold_bd_keep),
        "cold_nbd_keep": sorted(cold_nbd_keep),
        "pool_size": len(reduced_pool),
        "filtered_by_pattern": len([z for z in ALL_NUMBERS
                                    if get_pattern_7(draws, z) in BAD_PATTERNS]),
    }

    return reduced_pool, details


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    last_draw = draws[-1]

    print("=" * 80)
    print("OPTIMIERTER POOL-GENERATOR V2")
    print("Mit Pattern-Filterung basierend auf Miss-Analyse")
    print("=" * 80)
    print()
    print(f"Letzte Ziehung: {last_draw['datum'].strftime('%d.%m.%Y')}")
    print(f"Gezogen: {sorted(last_draw['zahlen'])}")
    print()

    # V1 Pool (zum Vergleich)
    from generate_optimized_tickets import build_reduced_pool as build_v1
    pool_v1, details_v1 = build_v1(draws)

    # V2 Pool
    pool_v2, details_v2 = build_optimized_pool_v2(draws)

    print("=" * 80)
    print("VERGLEICH V1 vs V2")
    print("=" * 80)
    print()

    print(f"V1 Pool ({len(pool_v1)} Zahlen): {sorted(pool_v1)}")
    print(f"V2 Pool ({len(pool_v2)} Zahlen): {sorted(pool_v2)}")
    print()

    # Unterschiede
    only_v1 = pool_v1 - pool_v2
    only_v2 = pool_v2 - pool_v1
    both = pool_v1 & pool_v2

    print(f"Gemeinsam:   {sorted(both)} ({len(both)} Zahlen)")
    print(f"Nur in V1:   {sorted(only_v1)} ({len(only_v1)} Zahlen)")
    print(f"Nur in V2:   {sorted(only_v2)} ({len(only_v2)} Zahlen)")
    print()

    # Zeige Pattern-Details fuer nur-V1 Zahlen
    if only_v1:
        print("Warum V1-Zahlen in V2 gefiltert wurden:")
        for z in sorted(only_v1):
            pattern = get_pattern_7(draws, z)
            score = score_number_v2(draws, z, get_hot_numbers(draws, 3))
            streak = get_streak(draws, z)
            avg_gap = get_avg_gap(draws, z)
            bad = "⚠️ BAD PATTERN" if pattern in BAD_PATTERNS else ""
            print(f"  {z}: Pattern={pattern} {bad}, Score={score:.0f}, Streak={streak}, Gap={avg_gap:.1f}")

    print()

    # V2 Pool Details
    print("=" * 80)
    print("V2 POOL DETAILS")
    print("=" * 80)
    print()

    print(f"HOT behalten:        {details_v2['hot_keep']}")
    print(f"COLD-Birthday:       {details_v2['cold_bd_keep']}")
    print(f"COLD-Non-Birthday:   {details_v2['cold_nbd_keep']}")
    print(f"Durch Pattern gefiltert: {details_v2['filtered_by_pattern']} Zahlen")
    print()

    # Score-Details fuer V2 Pool
    print("V2 Pool mit Scores:")
    for z in sorted(pool_v2):
        pattern = get_pattern_7(draws, z)
        score = score_number_v2(draws, z, get_hot_numbers(draws, 3))
        typ = "HOT" if z in details_v2["hot_keep"] else "COLD-BD" if z in details_v2["cold_bd_keep"] else "COLD-NBD"
        good = "✅" if pattern in GOOD_PATTERNS else ""
        print(f"  {z:>2}: Score={score:>5.0f}, Pattern={pattern} {good}, Typ={typ}")

    # Speichern
    output = {
        "generated_at": datetime.now().isoformat(),
        "last_draw": last_draw["datum"].strftime("%d.%m.%Y"),
        "pool_v1": sorted(pool_v1),
        "pool_v2": sorted(pool_v2),
        "only_v1": sorted(only_v1),
        "only_v2": sorted(only_v2),
        "details_v2": details_v2,
        "improvements": {
            "pattern_filter": "Filtert Zahlen mit >75% Miss-Rate Patterns",
            "score_based": "Beruecksichtigt Streak, Gap, Aktivitaet",
        }
    }

    output_path = base_path / "results/optimized_pool_v2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
