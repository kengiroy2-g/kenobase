#!/usr/bin/env python3
"""
TIEFENANALYSE: Muster in Pool-Misses finden

Ziel: Kombinierte Features finden die MISS vorhersagen
"""

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np

# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}


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


def get_pattern_last_7(draws: List[Dict], number: int) -> str:
    """Binaeres Muster der letzten 7 Tage (1=erschienen, 0=gefehlt)."""
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_gap_pattern(draws: List[Dict], number: int) -> List[int]:
    """Liste der Luecken zwischen Erscheinungen."""
    gaps = []
    last_seen = None
    for i, draw in enumerate(draws[-60:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return gaps


def build_reduced_pool(draws: List[Dict]) -> Tuple[Set[int], Set[int], Dict]:
    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    hot_filtered = hot - TOP_20_CORRECTION
    hot_sorted = sorted(hot_filtered, key=lambda z: get_index(draws, z))
    hot_keep = set(hot_sorted[:5]) if len(hot_sorted) >= 5 else set(hot_sorted)

    cold_bd_sorted = sorted(cold_birthday, key=lambda z: get_count(draws, z))
    cold_bd_keep = set(cold_bd_sorted[:6])

    cold_nbd_sorted = sorted(cold_nonbd, key=lambda z: get_count(draws, z))
    cold_nbd_keep = set(cold_nbd_sorted[:6])

    reduced_pool = hot_keep | cold_bd_keep | cold_nbd_keep
    details = {
        "hot_keep": hot_keep,
        "cold_bd_keep": cold_bd_keep,
        "cold_nbd_keep": cold_nbd_keep,
    }
    return reduced_pool, hot, details


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)

    print("=" * 80)
    print("TIEFENANALYSE: Muster in Pool-Misses")
    print("=" * 80)
    print()

    # Sammle alle Pool-Events
    events = []

    for draw in draws:
        if draw["datum"].year != 2025:
            continue

        draw_idx = draws.index(draw)
        if draw_idx < 60:
            continue

        train_data = draws[:draw_idx]
        pool, hot, details = build_reduced_pool(train_data)
        drawn = draw["zahlen"]

        for z in pool:
            is_hit = z in drawn
            pattern = get_pattern_last_7(train_data, z)
            gaps = get_gap_pattern(train_data, z)

            events.append({
                "datum": draw["datum"].strftime("%d.%m.%Y"),
                "number": z,
                "is_hit": is_hit,
                "is_birthday": z <= 31,
                "is_correction": z in TOP_20_CORRECTION,
                "is_hot": z in hot,
                "pool_type": (
                    "hot" if z in details["hot_keep"]
                    else "cold_bd" if z in details["cold_bd_keep"]
                    else "cold_nbd"
                ),
                "index": get_index(train_data, z),
                "count_7": get_count(train_data, z, 7),
                "count_30": get_count(train_data, z, 30),
                "streak": get_streak(train_data, z),
                "pattern_7": pattern,
                "ones_in_pattern": pattern.count("1"),
                "avg_gap": np.mean(gaps) if gaps else 10,
                "max_gap": max(gaps) if gaps else 10,
                "min_gap": min(gaps) if gaps else 1,
                "gap_std": np.std(gaps) if len(gaps) > 1 else 0,
            })

    print(f"Analysiere {len(events)} Pool-Events")
    print()

    # MUSTER-ANALYSE: 7-Tage-Pattern
    print("=" * 80)
    print("MUSTER 1: 7-Tage-Pattern vs. Miss-Rate")
    print("=" * 80)
    print()

    pattern_stats = defaultdict(lambda: {"miss": 0, "hit": 0})
    for e in events:
        if e["is_hit"]:
            pattern_stats[e["pattern_7"]]["hit"] += 1
        else:
            pattern_stats[e["pattern_7"]]["miss"] += 1

    # Sortiere nach Miss-Rate
    pattern_rates = []
    for pattern, stats in pattern_stats.items():
        total = stats["miss"] + stats["hit"]
        if total >= 20:  # Mindestens 20 Beobachtungen
            rate = stats["miss"] / total
            pattern_rates.append((pattern, rate, total, stats["miss"], stats["hit"]))

    pattern_rates.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Pattern':<12} {'Miss-Rate':<12} {'N':<8} {'Misses':<8} {'Hits':<8} {'Bedeutung'}")
    print("-" * 80)

    for pattern, rate, total, misses, hits in pattern_rates[:15]:
        ones = pattern.count("1")
        bedeutung = f"{ones}x erschienen in 7 Tagen"
        signal = "⚠️" if rate > 0.75 else "✅" if rate < 0.68 else ""
        print(f"{pattern:<12} {rate*100:>6.1f}% {signal:<3} {total:<8} {misses:<8} {hits:<8} {bedeutung}")

    print()
    print("Niedrigste Miss-Raten:")
    for pattern, rate, total, misses, hits in pattern_rates[-10:]:
        ones = pattern.count("1")
        bedeutung = f"{ones}x erschienen in 7 Tagen"
        print(f"{pattern:<12} {rate*100:>6.1f}%      {total:<8} {misses:<8} {hits:<8} {bedeutung}")

    # MUSTER 2: Kombination aus Features
    print()
    print("=" * 80)
    print("MUSTER 2: Feature-Kombinationen")
    print("=" * 80)
    print()

    # Definiere Buckets
    def get_bucket(e):
        buckets = []

        # Index-Bucket
        if e["index"] <= 2:
            buckets.append("idx_fresh")
        elif e["index"] >= 10:
            buckets.append("idx_old")
        else:
            buckets.append("idx_mid")

        # Streak-Bucket
        if e["streak"] >= 3:
            buckets.append("streak_hot")
        elif e["streak"] <= -5:
            buckets.append("streak_cold")
        else:
            buckets.append("streak_mid")

        # Pattern-Bucket (Ones in 7 days)
        if e["ones_in_pattern"] >= 3:
            buckets.append("active")
        elif e["ones_in_pattern"] <= 1:
            buckets.append("dormant")
        else:
            buckets.append("normal")

        return tuple(buckets)

    combo_stats = defaultdict(lambda: {"miss": 0, "hit": 0})
    for e in events:
        bucket = get_bucket(e)
        if e["is_hit"]:
            combo_stats[bucket]["hit"] += 1
        else:
            combo_stats[bucket]["miss"] += 1

    combo_rates = []
    for combo, stats in combo_stats.items():
        total = stats["miss"] + stats["hit"]
        if total >= 30:
            rate = stats["miss"] / total
            combo_rates.append((combo, rate, total, stats["miss"], stats["hit"]))

    combo_rates.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Kombination':<45} {'Miss-Rate':<12} {'N':<8}")
    print("-" * 70)

    for combo, rate, total, misses, hits in combo_rates[:15]:
        combo_str = " + ".join(combo)
        signal = "⚠️ VERMEIDEN" if rate > 0.75 else "✅ GUT" if rate < 0.65 else ""
        print(f"{combo_str:<45} {rate*100:>6.1f}% {signal:<12} {total:<8}")

    # MUSTER 3: Gap-Analyse
    print()
    print("=" * 80)
    print("MUSTER 3: Gap-Muster (Luecken zwischen Erscheinungen)")
    print("=" * 80)
    print()

    # Durchschnittliche Gap vs Miss-Rate
    gap_buckets = defaultdict(lambda: {"miss": 0, "hit": 0})
    for e in events:
        avg_gap = e["avg_gap"]
        if avg_gap <= 3:
            bucket = "gap_small"
        elif avg_gap <= 5:
            bucket = "gap_medium"
        else:
            bucket = "gap_large"

        if e["is_hit"]:
            gap_buckets[bucket]["hit"] += 1
        else:
            gap_buckets[bucket]["miss"] += 1

    print(f"{'Gap-Typ':<15} {'Bedeutung':<25} {'Miss-Rate':<12} {'N':<8}")
    print("-" * 65)

    for bucket in ["gap_small", "gap_medium", "gap_large"]:
        stats = gap_buckets[bucket]
        total = stats["miss"] + stats["hit"]
        rate = stats["miss"] / total * 100 if total > 0 else 0
        bedeutung = {
            "gap_small": "Avg Gap ≤3 (haeufig)",
            "gap_medium": "Avg Gap 4-5",
            "gap_large": "Avg Gap >5 (selten)",
        }[bucket]
        print(f"{bucket:<15} {bedeutung:<25} {rate:>6.1f}%      {total:<8}")

    # MUSTER 4: Nachbar-Analyse
    print()
    print("=" * 80)
    print("MUSTER 4: Nachbar-Korrelation")
    print("=" * 80)
    print()

    # Wenn Nachbar im Pool ist und gezogen wurde, wie ist unsere Miss-Rate?
    neighbor_stats = defaultdict(lambda: {"miss": 0, "hit": 0})

    for e in events:
        z = e["number"]
        datum = e["datum"]

        # Finde Events vom gleichen Tag
        day_events = [x for x in events if x["datum"] == datum]
        pool_numbers = set(x["number"] for x in day_events)

        # Pruefe Nachbarn
        has_neighbor_in_pool = (z - 1 in pool_numbers) or (z + 1 in pool_numbers)

        key = "with_neighbor" if has_neighbor_in_pool else "no_neighbor"
        if e["is_hit"]:
            neighbor_stats[key]["hit"] += 1
        else:
            neighbor_stats[key]["miss"] += 1

    for key in ["with_neighbor", "no_neighbor"]:
        stats = neighbor_stats[key]
        total = stats["miss"] + stats["hit"]
        rate = stats["miss"] / total * 100 if total > 0 else 0
        print(f"{key:<20} Miss-Rate: {rate:.1f}% (N={total})")

    # EMPFEHLUNGEN
    print()
    print("=" * 80)
    print("FILTER-EMPFEHLUNGEN fuer Pool-Generierung")
    print("=" * 80)
    print()

    # Beste und schlechteste Muster sammeln
    high_miss_patterns = [p for p, r, n, m, h in pattern_rates if r > 0.75 and n >= 30]
    low_miss_patterns = [p for p, r, n, m, h in pattern_rates if r < 0.65 and n >= 30]

    high_miss_combos = [c for c, r, n, m, h in combo_rates if r > 0.75 and n >= 30]

    print("AUSSCHLIESSEN wenn:")
    for combo, rate, total, _, _ in combo_rates[:5]:
        if rate > 0.72:
            combo_str = " + ".join(combo)
            print(f"  - {combo_str} (Miss-Rate: {rate*100:.1f}%)")

    print()
    print("BEVORZUGEN wenn:")
    for combo, rate, total, _, _ in combo_rates[-5:]:
        if rate < 0.70:
            combo_str = " + ".join(combo)
            print(f"  - {combo_str} (Miss-Rate: {rate*100:.1f}%)")

    print()
    print("7-TAGE-PATTERN FILTER:")
    print("  Ausschliessen: Muster mit >75% Miss-Rate")
    for p, r, n, m, h in pattern_rates[:5]:
        if r > 0.74:
            print(f"    '{p}' → {r*100:.1f}% Miss")

    # Speichern
    output = {
        "analysis_date": datetime.now().isoformat(),
        "pattern_analysis": [
            {"pattern": p, "miss_rate": r, "n": n}
            for p, r, n, m, h in pattern_rates
        ],
        "combo_analysis": [
            {"combo": list(c), "miss_rate": r, "n": n}
            for c, r, n, m, h in combo_rates
        ],
        "recommendations": {
            "exclude_combos": [list(c) for c, r, n, m, h in combo_rates[:5] if r > 0.72],
            "prefer_combos": [list(c) for c, r, n, m, h in combo_rates[-5:] if r < 0.70],
            "exclude_patterns": [p for p, r, n, m, h in pattern_rates[:5] if r > 0.74],
        }
    }

    output_path = base_path / "results/pool_miss_deep_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
