#!/usr/bin/env python3
"""
MESSUNG: Wie viele Tage bis Pool >= 6 Treffer hat?

Einfache Analyse:
1. Generiere Pool an Tag 1
2. Warte bis Pool >= 6 Treffer in einer Ziehung hat
3. Messe die Wartezeit

Das gibt uns:
- MINIMUM: Wie schnell kann es gehen?
- MAXIMUM: Wie lange muss man hoechstens warten?
- DURCHSCHNITT: Erwartete Wartezeit

Autor: Kenobase V2
"""

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import numpy as np

# Konstanten
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


def get_hot_numbers(draws: List[Dict], lookback: int = 3) -> Set[int]:
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


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


def get_index(draws: List[Dict], number: int) -> int:
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def score_number(draws: List[Dict], number: int, hot: Set[int]) -> float:
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


def build_pool(draws: List[Dict]) -> Set[int]:
    """Generiert 17er Pool."""
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


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)

    print("=" * 100)
    print("MESSUNG: Tage bis Pool >= 6 Treffer")
    print("=" * 100)
    print(f"\nZiehungen: {len(draws)}")
    print(f"Zeitraum: {draws[0]['datum'].strftime('%d.%m.%Y')} - {draws[-1]['datum'].strftime('%d.%m.%Y')}")

    # Strategie 1: STATISCHER Pool (einmal generieren, dann warten)
    print("\n" + "=" * 100)
    print("STRATEGIE 1: STATISCHER POOL")
    print("Pool wird EINMAL generiert und dann gewartet bis >= 6 Treffer")
    print("=" * 100)

    wait_times_static = []
    hit_events_static = []

    # Starte alle 30 Tage einen neuen "Durchgang"
    start_indices = list(range(50, len(draws) - 60, 30))

    for start_idx in start_indices:
        # Generiere Pool an Tag 1
        pool = build_pool(draws[:start_idx])
        if not pool:
            continue

        start_date = draws[start_idx]["datum"]

        # Warte bis >= 6 Treffer
        for day_offset in range(1, 61):  # Max 60 Tage warten
            check_idx = start_idx + day_offset
            if check_idx >= len(draws):
                break

            todays_numbers = draws[check_idx]["zahlen"]
            hits = len(pool & todays_numbers)

            if hits >= 6:
                wait_times_static.append(day_offset)
                hit_events_static.append({
                    "start": start_date.strftime("%d.%m.%Y"),
                    "hit": draws[check_idx]["datum"].strftime("%d.%m.%Y"),
                    "days": day_offset,
                    "hits": hits,
                    "pool": sorted(pool),
                    "matching": sorted(pool & todays_numbers),
                })
                break

    if wait_times_static:
        print(f"\nDurchgaenge: {len(start_indices)}")
        print(f"Erfolge (>= 6 Treffer): {len(wait_times_static)} ({len(wait_times_static)/len(start_indices)*100:.1f}%)")
        print()
        print(f"MINIMUM Wartezeit:      {min(wait_times_static)} Tage")
        print(f"MAXIMUM Wartezeit:      {max(wait_times_static)} Tage")
        print(f"DURCHSCHNITT:           {np.mean(wait_times_static):.1f} Tage")
        print(f"MEDIAN:                 {np.median(wait_times_static):.1f} Tage")

        # Verteilung
        print("\nVerteilung der Wartezeiten:")
        bins = [1, 5, 10, 15, 20, 25, 30, 60]
        for i in range(len(bins) - 1):
            count = sum(1 for w in wait_times_static if bins[i] <= w < bins[i + 1])
            pct = count / len(wait_times_static) * 100
            bar = "█" * int(pct / 2)
            print(f"  {bins[i]:2}-{bins[i+1]-1:2} Tage: {count:3} ({pct:5.1f}%) {bar}")

    # Strategie 2: DYNAMISCHER Pool (taeglich neu generieren)
    print("\n" + "=" * 100)
    print("STRATEGIE 2: DYNAMISCHER POOL")
    print("Pool wird JEDEN TAG neu generiert")
    print("=" * 100)

    wait_times_dynamic = []
    hit_events_dynamic = []

    for start_idx in start_indices:
        start_date = draws[start_idx]["datum"]

        # Warte bis >= 6 Treffer mit dynamischem Pool
        for day_offset in range(1, 61):
            check_idx = start_idx + day_offset
            if check_idx >= len(draws):
                break

            # Pool neu generieren (mit Daten bis gestern)
            pool = build_pool(draws[:check_idx])
            if not pool:
                continue

            todays_numbers = draws[check_idx]["zahlen"]
            hits = len(pool & todays_numbers)

            if hits >= 6:
                wait_times_dynamic.append(day_offset)
                hit_events_dynamic.append({
                    "start": start_date.strftime("%d.%m.%Y"),
                    "hit": draws[check_idx]["datum"].strftime("%d.%m.%Y"),
                    "days": day_offset,
                    "hits": hits,
                })
                break

    if wait_times_dynamic:
        print(f"\nDurchgaenge: {len(start_indices)}")
        print(f"Erfolge (>= 6 Treffer): {len(wait_times_dynamic)} ({len(wait_times_dynamic)/len(start_indices)*100:.1f}%)")
        print()
        print(f"MINIMUM Wartezeit:      {min(wait_times_dynamic)} Tage")
        print(f"MAXIMUM Wartezeit:      {max(wait_times_dynamic)} Tage")
        print(f"DURCHSCHNITT:           {np.mean(wait_times_dynamic):.1f} Tage")
        print(f"MEDIAN:                 {np.median(wait_times_dynamic):.1f} Tage")

        # Verteilung
        print("\nVerteilung der Wartezeiten:")
        bins = [1, 5, 10, 15, 20, 25, 30, 60]
        for i in range(len(bins) - 1):
            count = sum(1 for w in wait_times_dynamic if bins[i] <= w < bins[i + 1])
            pct = count / len(wait_times_dynamic) * 100
            bar = "█" * int(pct / 2)
            print(f"  {bins[i]:2}-{bins[i+1]-1:2} Tage: {count:3} ({pct:5.1f}%) {bar}")

    # Vergleich
    print("\n" + "=" * 100)
    print("VERGLEICH: STATISCH vs DYNAMISCH")
    print("=" * 100)

    if wait_times_static and wait_times_dynamic:
        print(f"\n{'Metrik':<25} {'Statisch':<15} {'Dynamisch':<15} {'Differenz':<15}")
        print("-" * 70)
        print(f"{'Erfolgsrate':<25} {len(wait_times_static)/len(start_indices)*100:<14.1f}% {len(wait_times_dynamic)/len(start_indices)*100:<14.1f}%")
        print(f"{'Min. Wartezeit':<25} {min(wait_times_static):<14} {min(wait_times_dynamic):<14} {min(wait_times_dynamic) - min(wait_times_static):+}")
        print(f"{'Max. Wartezeit':<25} {max(wait_times_static):<14} {max(wait_times_dynamic):<14} {max(wait_times_dynamic) - max(wait_times_static):+}")
        print(f"{'Durchschnitt':<25} {np.mean(wait_times_static):<14.1f} {np.mean(wait_times_dynamic):<14.1f} {np.mean(wait_times_dynamic) - np.mean(wait_times_static):+.1f}")
        print(f"{'Median':<25} {np.median(wait_times_static):<14.1f} {np.median(wait_times_dynamic):<14.1f} {np.median(wait_times_dynamic) - np.median(wait_times_static):+.1f}")

    # Beispiele zeigen
    print("\n" + "=" * 100)
    print("BEISPIELE: Schnellste Treffer (Dynamisch)")
    print("=" * 100)

    sorted_events = sorted(hit_events_dynamic, key=lambda x: x["days"])
    for e in sorted_events[:10]:
        print(f"  Start: {e['start']} → Treffer: {e['hit']} ({e['days']} Tage, {e['hits']} Hits)")

    print("\n" + "=" * 100)
    print("BEISPIELE: Langsamste Treffer (Dynamisch)")
    print("=" * 100)

    for e in sorted_events[-5:]:
        print(f"  Start: {e['start']} → Treffer: {e['hit']} ({e['days']} Tage, {e['hits']} Hits)")

    # LEITLINIE
    print("\n" + "=" * 100)
    print("LEITLINIE FUER SPIELSTRATEGIE")
    print("=" * 100)

    if wait_times_dynamic:
        median = np.median(wait_times_dynamic)
        p25 = np.percentile(wait_times_dynamic, 25)
        p75 = np.percentile(wait_times_dynamic, 75)

        print(f"""
BASIEREND AUF DYNAMISCHEM POOL:

  MINIMUM:     {min(wait_times_dynamic)} Tage   (schnellster Treffer)
  25%-PERZENTIL: {p25:.0f} Tage   (25% der Treffer kommen bis hier)
  MEDIAN:      {median:.0f} Tage   (50% der Treffer kommen bis hier)
  75%-PERZENTIL: {p75:.0f} Tage   (75% der Treffer kommen bis hier)
  MAXIMUM:     {max(wait_times_dynamic)} Tage   (laengste Wartezeit)

EMPFEHLUNG:
  - Warte mindestens {int(p25)} Tage bevor du spielst
  - Spiele spaetestens nach {int(p75)} Tagen
  - Wenn nach {int(median)} Tagen kein Treffer: Pool ist "reif"

ERFOLGSRATE:
  - {len(wait_times_dynamic)/len(start_indices)*100:.1f}% der 60-Tage-Fenster haben >= 6 Treffer
""")

    # Export
    import json
    export = {
        "static": {
            "success_rate": len(wait_times_static) / len(start_indices) * 100 if start_indices else 0,
            "min_days": int(min(wait_times_static)) if wait_times_static else None,
            "max_days": int(max(wait_times_static)) if wait_times_static else None,
            "avg_days": float(np.mean(wait_times_static)) if wait_times_static else None,
            "median_days": float(np.median(wait_times_static)) if wait_times_static else None,
        },
        "dynamic": {
            "success_rate": len(wait_times_dynamic) / len(start_indices) * 100 if start_indices else 0,
            "min_days": int(min(wait_times_dynamic)) if wait_times_dynamic else None,
            "max_days": int(max(wait_times_dynamic)) if wait_times_dynamic else None,
            "avg_days": float(np.mean(wait_times_dynamic)) if wait_times_dynamic else None,
            "median_days": float(np.median(wait_times_dynamic)) if wait_times_dynamic else None,
            "p25": float(np.percentile(wait_times_dynamic, 25)) if wait_times_dynamic else None,
            "p75": float(np.percentile(wait_times_dynamic, 75)) if wait_times_dynamic else None,
        },
        "recommendation": {
            "wait_min_days": int(np.percentile(wait_times_dynamic, 25)) if wait_times_dynamic else None,
            "play_by_days": int(np.percentile(wait_times_dynamic, 75)) if wait_times_dynamic else None,
            "optimal_day": int(np.median(wait_times_dynamic)) if wait_times_dynamic else None,
        }
    }

    results_path = base_path / "results" / "pool_hit_timing.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2)

    print(f"\nErgebnisse: {results_path}")


if __name__ == "__main__":
    main()
