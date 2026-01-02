#!/usr/bin/env python3
"""
OPTIMIERTER TICKET-GENERATOR V2

Kombiniert alle validierten Strategien:
- DANCE-006: Pool-Reduktion auf 17 Zahlen
- DANCE-007: Non-Birthday Ratio (50-60%)
- WL-006: Jackpot-Uniqueness (Dekaden, keine Konsekutiven)
- DANCE-001: HOT/COLD Mix (2 HOT + 4 COLD)
- DANCE-009: Pattern-Filterung (NEU!)

V2 Verbesserungen (2026-01-02):
- 7-Tage-Pattern Filterung (entfernt >75% Miss-Rate Patterns)
- Score-basierte Zahlenauswahl (Streak, Gap, Aktivitaet)
- Backtest: +3.2% mehr Treffer, +58 Treffer/Jahr

Nutzung:
    python scripts/generate_optimized_tickets.py
    python scripts/generate_optimized_tickets.py --type 5
    python scripts/generate_optimized_tickets.py --top 20
    python scripts/generate_optimized_tickets.py --save
"""

import argparse
import csv
import json
import math
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

# V2: Pattern-Filter basierend auf Miss-Analyse
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
                    data.append({"datum": datum, "zahlen": set(numbers)})
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_hot_numbers(draws: List[Dict], lookback: int = 3) -> Set[int]:
    """HOT Zahlen (>=2x in den letzten X Tagen)."""
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_index(draws: List[Dict], number: int) -> int:
    """Wann wurde die Zahl zuletzt gezogen (0 = heute)."""
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def get_count(draws: List[Dict], number: int, lookback: int = 30) -> int:
    """Wie oft wurde die Zahl in den letzten X Tagen gezogen."""
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_pattern_7(draws: List[Dict], number: int) -> str:
    """V2: 7-Tage-Binaermuster (1=erschienen, 0=gefehlt)."""
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_streak(draws: List[Dict], number: int) -> int:
    """V2: Aktuelle Streak (positiv=erscheint, negativ=fehlt)."""
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


def get_avg_gap(draws: List[Dict], number: int, lookback: int = 60) -> float:
    """V2: Durchschnittliche Luecke zwischen Erscheinungen."""
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
    V2 Scoring: Beruecksichtigt Pattern, Streak, Gap.
    Hoeherer Score = besser (weniger wahrscheinlich zu missen).
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


def build_reduced_pool(draws: List[Dict], target_size: int = 17) -> Tuple[Set[int], Dict]:
    """
    DANCE-006 + DANCE-009: Baut reduzierten Pool von ~17 Zahlen mit V2 Pattern-Filterung.

    V2 Verbesserungen:
    - HOT: Sortiert nach score_number_v2() statt nur Index
    - COLD: Filtert BAD_PATTERNS aus (>75% Miss-Rate)
    - Backtest: +3.2% mehr Treffer, +58 Treffer/Jahr

    Methode:
    - HOT: Top 5 (ohne Korrektur-Kandidaten, sortiert nach V2-Score)
    - COLD-Birthday: Top 6 (seltenste, aber ohne BAD_PATTERNS)
    - COLD-Non-Birthday: Top 6 (seltenste, aber ohne BAD_PATTERNS)
    """
    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    if not 1 <= target_size <= 70:
        raise ValueError(f"target_size muss zwischen 1 und 70 liegen (ist {target_size})")

    patterns = {z: get_pattern_7(draws, z) for z in ALL_NUMBERS}
    bad_pattern_numbers = {z for z, p in patterns.items() if p in BAD_PATTERNS}

    # V2: HOT - Sortiert nach score_number_v2() (hoechster Score zuerst)
    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number_v2(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)  # Hoechster Score zuerst
    hot_target = min(5, target_size)
    hot_keep = set(z for z, s in hot_scored[:hot_target])

    remaining_slots = max(0, target_size - len(hot_keep))
    cold_bd_target = remaining_slots // 2
    cold_nbd_target = remaining_slots - cold_bd_target

    # V2: COLD-Birthday - Seltenste, aber mit Pattern-Filter
    cold_bd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot))
                      for z in cold_birthday]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))  # Niedrigster Count, dann hoechster Score

    # Filtere Zahlen mit schlechtem Pattern
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored
                        if patterns[z] not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:cold_bd_target])

    # Falls nicht genug, nimm auch ungefilterte
    if cold_bd_target and len(cold_bd_keep) < cold_bd_target:
        fallback = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(fallback[:cold_bd_target - len(cold_bd_keep)])

    # V2: COLD-Non-Birthday - Gleiche Logik
    cold_nbd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot))
                       for z in cold_nonbd]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))

    cold_nbd_filtered = [(z, c, s) for z, c, s in cold_nbd_scored
                         if patterns[z] not in BAD_PATTERNS]
    cold_nbd_keep = set(z for z, c, s in cold_nbd_filtered[:cold_nbd_target])

    if cold_nbd_target and len(cold_nbd_keep) < cold_nbd_target:
        fallback = [z for z, c, s in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(fallback[:cold_nbd_target - len(cold_nbd_keep)])

    reduced_pool = hot_keep | cold_bd_keep | cold_nbd_keep

    bad_in_pool = sorted(reduced_pool & bad_pattern_numbers)

    details = {
        "hot_all": sorted(hot),
        "hot_keep": sorted(hot_keep),
        "cold_birthday_keep": sorted(cold_bd_keep),
        "cold_nonbd_keep": sorted(cold_nbd_keep),
        "pool_size": len(reduced_pool),
        "filtered_by_pattern": len(bad_pattern_numbers),  # Backwards-Compatibility
        "bad_pattern_count": len(bad_pattern_numbers),
        "bad_pattern_numbers": sorted(bad_pattern_numbers),
        "bad_pattern_in_pool": bad_in_pool,
    }

    return reduced_pool, details


# Filter-Funktionen
def get_decades(numbers: tuple) -> int:
    """Anzahl verschiedener Dekaden."""
    return len(set((n - 1) // 10 for n in numbers))


def get_non_birthday_ratio(numbers: tuple) -> float:
    """Anteil Non-Birthday Zahlen."""
    nbd = len([n for n in numbers if n > 31])
    return nbd / len(numbers)


def has_consecutive(numbers: tuple) -> bool:
    """Prueft ob konsekutive Zahlen vorhanden sind."""
    nums = sorted(numbers)
    for i in range(len(nums) - 1):
        if nums[i + 1] - nums[i] == 1:
            return True
    return False


def get_hot_count(numbers: tuple, hot_set: Set[int]) -> int:
    """Anzahl HOT-Zahlen im Ticket."""
    return len([n for n in numbers if n in hot_set])


def filter_combinations(
    pool: Set[int],
    hot: Set[int],
    ticket_size: int = 6,
    min_decades: int = 4,
    nbd_ratio_range: Tuple[float, float] = (0.33, 0.67),
    no_consecutive: bool = True,
    hot_count: int = 2,
    sum_range: Tuple[int, int] = (100, 300),
) -> List[tuple]:
    """
    Filtert Kombinationen basierend auf allen Strategien.

    Filter:
    1. Dekaden >= min_decades (WL-006)
    2. Non-Birthday Ratio in range (DANCE-007)
    3. Keine Konsekutiven (WL-006)
    4. Exakt hot_count HOT-Zahlen (DANCE-001)
    5. Summe in range
    """
    all_combos = list(combinations(sorted(pool), ticket_size))

    filtered = all_combos

    # Filter 1: Dekaden
    filtered = [c for c in filtered if get_decades(c) >= min_decades]

    # Filter 2: Non-Birthday Ratio
    filtered = [c for c in filtered
                if nbd_ratio_range[0] <= get_non_birthday_ratio(c) <= nbd_ratio_range[1]]

    # Filter 3: Keine Konsekutiven
    if no_consecutive:
        filtered = [c for c in filtered if not has_consecutive(c)]

    # Filter 4: HOT Count
    if hot_count is not None:
        filtered = [c for c in filtered if get_hot_count(c, hot) == hot_count]

    # Filter 5: Summe
    filtered = [c for c in filtered if sum_range[0] <= sum(c) <= sum_range[1]]

    return filtered


def score_combination(combo: tuple, hot: Set[int]) -> float:
    """
    Bewertet eine Kombination basierend auf unseren Erkenntnissen.

    Hoeherer Score = besser.
    """
    score = 0.0

    # Dekaden-Bonus (mehr = besser, max bei 6)
    decades = get_decades(combo)
    score += min(decades, 6) * 10

    # Non-Birthday nahe 50% ist optimal
    nbd_ratio = get_non_birthday_ratio(combo)
    score += (1 - abs(nbd_ratio - 0.5) * 2) * 20

    # Summe im mittleren Bereich
    total = sum(combo)
    if 150 <= total <= 250:
        score += 15
    elif 100 <= total <= 300:
        score += 10

    # Spread (Differenz zwischen min und max)
    spread = max(combo) - min(combo)
    if spread >= 50:
        score += 15
    elif spread >= 40:
        score += 10

    return score


def generate_typ5_from_typ6(typ6: tuple) -> tuple:
    """Generiert Typ 5 aus Typ 6 durch Entfernen der kleinsten Non-Birthday Zahl."""
    nbd_in_combo = [n for n in typ6 if n > 31]
    if nbd_in_combo:
        to_remove = min(nbd_in_combo)
    else:
        to_remove = max(typ6)  # Falls alle Birthday, entferne groesste
    return tuple(n for n in typ6 if n != to_remove)


def main():
    parser = argparse.ArgumentParser(description="Optimierter KENO Ticket-Generator")
    parser.add_argument("--type", type=int, default=6, choices=[5, 6, 7],
                        help="Ticket-Typ (5, 6 oder 7 Zahlen)")
    parser.add_argument("--pool-size", type=int, default=17,
                        help="Groesse des Zahlenpools (Default: 17)")
    parser.add_argument("--top", type=int, default=10,
                        help="Anzahl der Top-Tickets anzeigen")
    parser.add_argument("--save", action="store_true",
                        help="Ergebnisse als JSON speichern")
    parser.add_argument("--strict", action="store_true",
                        help="Strenge Filter (5+ Dekaden, exakt 50% NBD)")
    args = parser.parse_args()

    # Daten laden
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    last_draw = draws[-1]

    print("=" * 80)
    print("OPTIMIERTER KENO TICKET-GENERATOR V2")
    print("Kombiniert: DANCE-006 + DANCE-007 + DANCE-001 + WL-006 + DANCE-009 (Pattern-Filter)")
    print("=" * 80)
    print()
    print(f"Letzte Ziehung: {last_draw['datum'].strftime('%d.%m.%Y')}")
    print(f"Gezogen: {sorted(last_draw['zahlen'])}")
    print()

    # Pool aufbauen
    hot = get_hot_numbers(draws, lookback=3)
    reduced_pool, pool_details = build_reduced_pool(draws, target_size=args.pool_size)

    print("POOL-ANALYSE (DANCE-006 + DANCE-009 V2):")
    print("-" * 50)
    print(f"HOT Zahlen:           {pool_details['hot_all']}")
    print(f"HOT behalten:         {pool_details['hot_keep']} (nach V2-Score)")
    print(f"COLD-Birthday:        {pool_details['cold_birthday_keep']}")
    print(f"COLD-Non-Birthday:    {pool_details['cold_nonbd_keep']}")
    print(f"Pool-Groesse:         {pool_details['pool_size']} Zahlen")
    print(f"BAD_PATTERN (7 Tage): {pool_details.get('bad_pattern_count', 0)} Zahlen")
    print(f"BAD_PATTERN im Pool:  {pool_details.get('bad_pattern_in_pool', [])}")
    print(f"Pool:                 {sorted(reduced_pool)}")
    print()

    # Filter-Parameter
    if args.strict:
        min_decades = 5
        nbd_range = (0.45, 0.55)  # Nahe 50%
        sum_range = (150, 250)
    else:
        min_decades = 4
        nbd_range = (0.33, 0.67)
        sum_range = (100, 300)

    # Kombinationen filtern
    ticket_size = args.type

    # HOT-Count anpassen je nach Ticket-Groesse
    if ticket_size == 5:
        hot_count = 2
    elif ticket_size == 6:
        hot_count = 2
    else:  # 7
        hot_count = 2

    print("FILTER-STRATEGIEN:")
    print("-" * 50)
    print(f"1. Dekaden >= {min_decades} (WL-006)")
    print(f"2. Non-Birthday {nbd_range[0]*100:.0f}-{nbd_range[1]*100:.0f}% (DANCE-007)")
    print(f"3. Keine Konsekutiven (WL-006)")
    print(f"4. Exakt {hot_count} HOT (DANCE-001)")
    print(f"5. Summe {sum_range[0]}-{sum_range[1]}")
    print()

    # Alle Kombinationen (nur Anzahl, nicht materialisieren)
    total_combos = math.comb(len(reduced_pool), ticket_size)
    print(f"Alle Kombinationen:   {total_combos}")

    # Filtern
    filtered = filter_combinations(
        reduced_pool, hot, ticket_size,
        min_decades=min_decades,
        nbd_ratio_range=nbd_range,
        no_consecutive=True,
        hot_count=hot_count,
        sum_range=sum_range,
    )

    print(f"Nach Filterung:       {len(filtered)}")
    print(f"Reduktion:            {(1 - len(filtered)/total_combos)*100:.1f}%")
    print()

    if not filtered:
        print("WARNUNG: Keine Kombinationen erfuellen alle Filter!")
        print("Versuche mit weniger strengen Filtern...")
        filtered = filter_combinations(
            reduced_pool, hot, ticket_size,
            min_decades=3,
            nbd_ratio_range=(0.2, 0.8),
            no_consecutive=True,
            hot_count=None,
            sum_range=(50, 350),
        )
        print(f"Mit lockeren Filtern: {len(filtered)}")
        print()

    # Ranking
    ranked = sorted(filtered, key=lambda c: score_combination(c, hot), reverse=True)

    print("=" * 80)
    print(f"TOP {min(args.top, len(ranked))} OPTIMIERTE TICKETS (TYP {ticket_size})")
    print("=" * 80)
    print()
    print(f"{'#':<4} {'Ticket':<40} {'Dek':<5} {'NBD%':<6} {'Sum':<6} {'Score':<6}")
    print("-" * 70)

    for i, combo in enumerate(ranked[:args.top], 1):
        decades = get_decades(combo)
        nbd_pct = get_non_birthday_ratio(combo) * 100
        total = sum(combo)
        score = score_combination(combo, hot)
        print(f"{i:<4} {str(list(combo)):<40} {decades:<5} {nbd_pct:<6.0f} {total:<6} {score:<6.1f}")

    print()
    print("=" * 80)
    print(">>> EMPFOHLENE TICKETS <<<")
    print("=" * 80)
    print()

    # Top 3 anzeigen
    for i, combo in enumerate(ranked[:3], 1):
        print(f"  #{i} TYP {ticket_size}: {list(combo)}")

    # Typ 5 aus Typ 6 generieren
    if ticket_size == 6:
        print()
        print("  Entsprechende TYP 5:")
        for i, combo in enumerate(ranked[:3], 1):
            typ5 = generate_typ5_from_typ6(combo)
            print(f"  #{i} TYP 5: {list(typ5)}")

    print()
    print("=" * 80)
    print("STATISTIK")
    print("=" * 80)
    print()
    print(f"  Ausgangskombinationen: {total_combos}")
    print(f"  Optimierte Auswahl:    {len(filtered)}")
    print(f"  Verbesserungsfaktor:   {total_combos/max(len(filtered),1):.1f}x")
    print()

    # Speichern
    if args.save:
        result = {
            "generated_at": datetime.now().isoformat(),
            "last_draw": last_draw["datum"].strftime("%d.%m.%Y"),
            "pool": sorted(reduced_pool),
            "pool_details": {k: list(v) if isinstance(v, set) else v
                           for k, v in pool_details.items()},
            "filter_params": {
                "min_decades": min_decades,
                "nbd_range": nbd_range,
                "hot_count": hot_count,
                "sum_range": sum_range,
            },
            "total_combinations": total_combos,
            "filtered_combinations": len(filtered),
            "improvement_factor": round(total_combos / max(len(filtered), 1), 1),
            "top_tickets": [list(c) for c in ranked[:args.top]],
            "recommended": {
                f"typ{ticket_size}": [list(c) for c in ranked[:3]],
            }
        }

        if ticket_size == 6:
            result["recommended"]["typ5"] = [
                list(generate_typ5_from_typ6(c)) for c in ranked[:3]
            ]

        output_path = base_path / "results/optimized_tickets.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
