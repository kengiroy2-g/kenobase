#!/usr/bin/env python3
"""
ERWEITERTE MESSUNG: Pool-Treffer Timing

Varianten:
1. Alle 7 Tage starten (mehr Datenpunkte)
2. 30-Tage und 60-Tage Startintervalle
3. Nach Treffer-Anzahl (6, 7, 8+ Hits)

Autor: Kenobase V2
"""

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import numpy as np

# Konstanten (wie vorher)
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}
BAD_PATTERNS = {"0010010", "1000111", "0101011", "1010000", "0001101", "0001000", "0100100", "0001010", "0000111"}


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


def get_hot_numbers(draws, lookback=3):
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_count(draws, number, lookback=30):
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_streak(draws, number):
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


def get_pattern_7(draws, number):
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_avg_gap(draws, number, lookback=60):
    gaps = []
    last_seen = None
    for i, draw in enumerate(draws[-lookback:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return np.mean(gaps) if gaps else 10.0


def get_index(draws, number):
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def score_number(draws, number, hot):
    score = 50.0
    pattern = get_pattern_7(draws, number)
    if pattern in BAD_PATTERNS:
        score -= 20
    streak = get_streak(draws, number)
    if streak >= 3:
        score -= 10
    elif 0 < streak <= 2:
        score += 5
    avg_gap = get_avg_gap(draws, number)
    if avg_gap <= 3:
        score += 10
    elif avg_gap > 5:
        score -= 5
    index = get_index(draws, number)
    if 3 <= index <= 6:
        score += 5
    return score


def build_pool(draws):
    if len(draws) < 10:
        return set()
    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)
    hot_keep = set(z for z, s in hot_scored[:5])

    cold_bd_scored = [(z, get_count(draws, z), score_number(draws, z, hot)) for z in cold_birthday]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:6])
    if len(cold_bd_keep) < 6:
        remaining = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(remaining[:6 - len(cold_bd_keep)])

    cold_nbd_scored = [(z, get_count(draws, z), score_number(draws, z, hot)) for z in cold_nonbd]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_nbd_filtered = [(z, c, s) for z, c, s in cold_nbd_scored if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_nbd_keep = set(z for z, c, s in cold_nbd_filtered[:6])
    if len(cold_nbd_keep) < 6:
        remaining = [z for z, c, s in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(remaining[:6 - len(cold_nbd_keep)])

    return hot_keep | cold_bd_keep | cold_nbd_keep


def measure_wait_times(draws, start_interval, max_wait, min_hits=6):
    """Misst Wartezeiten mit dynamischem Pool."""
    start_indices = list(range(50, len(draws) - max_wait, start_interval))
    wait_times = []

    for start_idx in start_indices:
        for day_offset in range(1, max_wait + 1):
            check_idx = start_idx + day_offset
            if check_idx >= len(draws):
                break

            pool = build_pool(draws[:check_idx])
            if not pool:
                continue

            hits = len(pool & draws[check_idx]["zahlen"])

            if hits >= min_hits:
                wait_times.append(day_offset)
                break

    return wait_times, len(start_indices)


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)

    print("=" * 100)
    print("ERWEITERTE MESSUNG: Pool-Treffer Timing")
    print("=" * 100)
    print(f"\nZiehungen: {len(draws)}")

    # Test 1: Verschiedene Startintervalle
    print("\n" + "=" * 100)
    print("TEST 1: Verschiedene Startintervalle (min. 6 Treffer)")
    print("=" * 100)

    intervals = [7, 14, 30, 60]

    print(f"\n{'Intervall':<12} {'Durchgaenge':<12} {'Erfolge':<10} {'Min':<6} {'Max':<6} {'Avg':<8} {'Median':<8}")
    print("-" * 70)

    for interval in intervals:
        wait_times, total = measure_wait_times(draws, interval, max_wait=60, min_hits=6)
        if wait_times:
            success = len(wait_times)
            print(f"{interval} Tage      {total:<12} {success:<10} {min(wait_times):<6} {max(wait_times):<6} {np.mean(wait_times):<8.1f} {np.median(wait_times):<8.1f}")

    # Test 2: Verschiedene Hit-Schwellen
    print("\n" + "=" * 100)
    print("TEST 2: Verschiedene Treffer-Schwellen (Intervall: 7 Tage)")
    print("=" * 100)

    hit_thresholds = [6, 7, 8, 9, 10]

    print(f"\n{'Min Hits':<10} {'Durchgaenge':<12} {'Erfolge':<10} {'Rate':<10} {'Min':<6} {'Max':<6} {'Avg':<8} {'Median':<8}")
    print("-" * 80)

    for min_hits in hit_thresholds:
        wait_times, total = measure_wait_times(draws, 7, max_wait=60, min_hits=min_hits)
        if wait_times:
            success = len(wait_times)
            rate = success / total * 100
            print(f"{min_hits:<10} {total:<12} {success:<10} {rate:<9.1f}% {min(wait_times):<6} {max(wait_times):<6} {np.mean(wait_times):<8.1f} {np.median(wait_times):<8.1f}")
        else:
            print(f"{min_hits:<10} {total:<12} {'0':<10} {'0.0':<9}%")

    # Test 3: Detaillierte Verteilung fuer 6+ Hits
    print("\n" + "=" * 100)
    print("TEST 3: Detaillierte Verteilung (6+ Hits, Intervall: 7 Tage)")
    print("=" * 100)

    wait_times, total = measure_wait_times(draws, 7, max_wait=60, min_hits=6)

    if wait_times:
        print(f"\nGesamt: {len(wait_times)} Erfolge von {total} Durchgaengen ({len(wait_times)/total*100:.1f}%)")
        print()

        # Kumulative Verteilung
        print("Kumulative Verteilung (Chance auf Treffer BIS Tag X):")
        print()
        for day in [1, 2, 3, 4, 5, 6, 7, 10, 14, 21, 30]:
            count = sum(1 for w in wait_times if w <= day)
            pct = count / len(wait_times) * 100
            bar = "█" * int(pct / 2)
            print(f"  Tag {day:2}: {pct:5.1f}% {bar}")

    # Test 4: 60-Tage Intervall separat
    print("\n" + "=" * 100)
    print("TEST 4: 60-TAGE INTERVALL (wie vom User gewuenscht)")
    print("=" * 100)

    wait_times_60, total_60 = measure_wait_times(draws, 60, max_wait=90, min_hits=6)

    if wait_times_60:
        print(f"\nDurchgaenge: {total_60}")
        print(f"Erfolge: {len(wait_times_60)} ({len(wait_times_60)/total_60*100:.1f}%)")
        print()
        print(f"MINIMUM:   {min(wait_times_60)} Tage")
        print(f"MAXIMUM:   {max(wait_times_60)} Tage")
        print(f"DURCHSCHNITT: {np.mean(wait_times_60):.1f} Tage")
        print(f"MEDIAN:    {np.median(wait_times_60):.1f} Tage")
        print()

        print("Verteilung:")
        bins = [(1, 3), (4, 7), (8, 14), (15, 21), (22, 30), (31, 60), (61, 90)]
        for low, high in bins:
            count = sum(1 for w in wait_times_60 if low <= w <= high)
            if count > 0:
                pct = count / len(wait_times_60) * 100
                bar = "█" * int(pct / 2)
                print(f"  Tag {low:2}-{high:2}: {count:3} ({pct:5.1f}%) {bar}")

    # FINALE LEITLINIE
    print("\n" + "=" * 100)
    print("FINALE LEITLINIE")
    print("=" * 100)

    wait_times_all, _ = measure_wait_times(draws, 7, max_wait=60, min_hits=6)

    if wait_times_all:
        p25 = np.percentile(wait_times_all, 25)
        p50 = np.percentile(wait_times_all, 50)
        p75 = np.percentile(wait_times_all, 75)
        p90 = np.percentile(wait_times_all, 90)
        p99 = np.percentile(wait_times_all, 99)

        print(f"""
WANN SPIELEN? (basierend auf {len(wait_times_all)} Messungen)

  Tag 1-{int(p25)}:   25% Chance auf >= 6 Treffer
  Tag 1-{int(p50)}:   50% Chance auf >= 6 Treffer
  Tag 1-{int(p75)}:   75% Chance auf >= 6 Treffer
  Tag 1-{int(p90)}:  90% Chance auf >= 6 Treffer
  Tag 1-{int(p99)}:  99% Chance auf >= 6 Treffer

EMPFEHLUNG:
  ✓ Pool taeglich neu generieren
  ✓ Ab Tag {int(p25)} ist Pool "spielbereit"
  ✓ Spaetestens Tag {int(p75)} sollte Treffer kommen
  ✓ Nach Tag {int(p90)} wird es unwahrscheinlich

KONKRET:
  - Generiere Pool am Montag
  - Spiele Mittwoch, Freitag, Sonntag (alle 2 Tage)
  - Nach spaetestens {int(p90)} Tagen neuer Zyklus starten
""")

    # Export
    import json
    export = {
        "intervals_test": {str(i): {"avg": float(np.mean(measure_wait_times(draws, i, 60, 6)[0])) if measure_wait_times(draws, i, 60, 6)[0] else None} for i in intervals},
        "hit_thresholds_test": {str(h): {"success_rate": len(measure_wait_times(draws, 7, 60, h)[0]) / measure_wait_times(draws, 7, 60, h)[1] * 100 if measure_wait_times(draws, 7, 60, h)[0] else 0} for h in hit_thresholds},
        "recommendation": {
            "p25_days": float(p25) if wait_times_all else None,
            "p50_days": float(p50) if wait_times_all else None,
            "p75_days": float(p75) if wait_times_all else None,
            "p90_days": float(p90) if wait_times_all else None,
        }
    }

    results_path = base_path / "results" / "pool_hit_timing_extended.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2)

    print(f"\nErgebnisse: {results_path}")


if __name__ == "__main__":
    main()
