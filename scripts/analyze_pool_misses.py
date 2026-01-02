#!/usr/bin/env python3
"""
ANALYSE: Pool-Zahlen die NICHT gezogen wurden

Ziel: Finde Muster in den "Miss"-Zahlen um sie VOR der Pool-Generierung
zu erkennen und auszuschliessen.

Fragen:
1. Welche Pool-Zahlen werden am haeufigsten NICHT gezogen?
2. Haben diese Zahlen gemeinsame Eigenschaften?
3. Koennen wir sie anhand von Pre-Draw-Metriken identifizieren?
"""

import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np

# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}


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
    """Tage seit letztem Erscheinen."""
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def get_count(draws: List[Dict], number: int, lookback: int = 30) -> int:
    """Haeufigkeit in den letzten X Tagen."""
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_streak(draws: List[Dict], number: int) -> int:
    """Aktuelle Streak (aufeinander folgende Tage mit/ohne Zahl)."""
    if not draws:
        return 0
    streak = 0
    in_last = number in draws[-1]["zahlen"]
    for draw in reversed(draws):
        if (number in draw["zahlen"]) == in_last:
            streak += 1
        else:
            break
    return streak if in_last else -streak  # Positiv = erscheint, Negativ = fehlt


def build_reduced_pool(draws: List[Dict]) -> Tuple[Set[int], Set[int], Dict]:
    """Baut reduzierten Pool."""
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


def analyze_number_features(draws: List[Dict], number: int) -> Dict:
    """Berechnet alle Features einer Zahl."""
    return {
        "number": number,
        "is_birthday": number <= 31,
        "is_hot": number in get_hot_numbers(draws, lookback=3),
        "is_correction": number in TOP_20_CORRECTION,
        "decade": (number - 1) // 10,
        "index": get_index(draws, number),
        "count_7": get_count(draws, number, lookback=7),
        "count_14": get_count(draws, number, lookback=14),
        "count_30": get_count(draws, number, lookback=30),
        "streak": get_streak(draws, number),
        "last_3_appearances": sum(1 for d in draws[-3:] if number in d["zahlen"]),
    }


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)

    print("=" * 80)
    print("ANALYSE: Pool-Zahlen die NICHT gezogen wurden")
    print("=" * 80)
    print()

    # Sammle Daten fuer 2025
    draws_2025 = [d for d in draws if d["datum"].year == 2025]
    print(f"Analysiere {len(draws_2025)} Ziehungen in 2025")
    print()

    # Fuer jeden Tag: Pool bilden, dann pruefen welche Pool-Zahlen NICHT gezogen wurden
    miss_counts = defaultdict(int)  # Wie oft wurde jede Zahl aus Pool NICHT gezogen
    hit_counts = defaultdict(int)   # Wie oft wurde jede Zahl aus Pool gezogen
    miss_features = []  # Features der Miss-Zahlen
    hit_features = []   # Features der Hit-Zahlen

    total_pool_appearances = defaultdict(int)  # Wie oft war jede Zahl im Pool

    for i, draw in enumerate(draws):
        if draw["datum"].year != 2025:
            continue

        # Finde Index in Gesamtdaten
        draw_idx = draws.index(draw)
        if draw_idx < 30:
            continue

        # Pool am Vortag bilden
        train_data = draws[:draw_idx]
        pool, hot, details = build_reduced_pool(train_data)

        drawn = draw["zahlen"]

        # Welche Pool-Zahlen wurden gezogen / nicht gezogen?
        hits = pool & drawn
        misses = pool - drawn

        for z in pool:
            total_pool_appearances[z] += 1

        for z in hits:
            hit_counts[z] += 1
            features = analyze_number_features(train_data, z)
            features["pool_type"] = (
                "hot" if z in details["hot_keep"]
                else "cold_bd" if z in details["cold_bd_keep"]
                else "cold_nbd"
            )
            features["result"] = "HIT"
            hit_features.append(features)

        for z in misses:
            miss_counts[z] += 1
            features = analyze_number_features(train_data, z)
            features["pool_type"] = (
                "hot" if z in details["hot_keep"]
                else "cold_bd" if z in details["cold_bd_keep"]
                else "cold_nbd"
            )
            features["result"] = "MISS"
            miss_features.append(features)

    # Analyse
    print("=" * 80)
    print("MISS-RATE PRO ZAHL (wie oft aus Pool NICHT gezogen)")
    print("=" * 80)
    print()

    # Berechne Miss-Rate pro Zahl
    miss_rates = {}
    for z in total_pool_appearances:
        total = total_pool_appearances[z]
        misses = miss_counts[z]
        miss_rates[z] = misses / total if total > 0 else 0

    # Sortiere nach Miss-Rate (hoechste zuerst)
    sorted_by_miss = sorted(miss_rates.items(), key=lambda x: x[1], reverse=True)

    print(f"{'Zahl':<6} {'Pool-Tage':<12} {'Misses':<10} {'Hits':<10} {'Miss-Rate':<12} {'Typ'}")
    print("-" * 70)

    for z, rate in sorted_by_miss[:30]:
        total = total_pool_appearances[z]
        misses = miss_counts[z]
        hits = hit_counts[z]
        typ = "BD" if z <= 31 else "NBD"
        corr = " (CORR)" if z in TOP_20_CORRECTION else ""
        print(f"{z:<6} {total:<12} {misses:<10} {hits:<10} {rate*100:<10.1f}% {typ}{corr}")

    # Feature-Analyse: Unterschiede zwischen MISS und HIT
    print()
    print("=" * 80)
    print("FEATURE-ANALYSE: Was unterscheidet MISS von HIT?")
    print("=" * 80)
    print()

    # Aggregiere Features
    miss_agg = defaultdict(list)
    hit_agg = defaultdict(list)

    for f in miss_features:
        for key, val in f.items():
            if isinstance(val, (int, float)) and key not in ["number"]:
                miss_agg[key].append(val)

    for f in hit_features:
        for key, val in f.items():
            if isinstance(val, (int, float)) and key not in ["number"]:
                hit_agg[key].append(val)

    print(f"{'Feature':<20} {'MISS (Avg)':<15} {'HIT (Avg)':<15} {'Differenz':<15} {'Signal'}")
    print("-" * 80)

    signals = []
    for key in sorted(miss_agg.keys()):
        if key in hit_agg and len(miss_agg[key]) > 0 and len(hit_agg[key]) > 0:
            miss_avg = np.mean(miss_agg[key])
            hit_avg = np.mean(hit_agg[key])
            diff = miss_avg - hit_avg
            diff_pct = (diff / hit_avg * 100) if hit_avg != 0 else 0

            # Bestimme Signal-Staerke
            if abs(diff_pct) > 20:
                signal = "⚠️ STARK"
            elif abs(diff_pct) > 10:
                signal = "📊 MITTEL"
            elif abs(diff_pct) > 5:
                signal = "📈 SCHWACH"
            else:
                signal = ""

            signals.append((key, miss_avg, hit_avg, diff, diff_pct, signal))
            print(f"{key:<20} {miss_avg:<15.2f} {hit_avg:<15.2f} {diff:+.2f} ({diff_pct:+.1f}%) {signal}")

    # Pool-Typ Analyse
    print()
    print("=" * 80)
    print("MISS-RATE PRO POOL-TYP")
    print("=" * 80)
    print()

    pool_type_stats = defaultdict(lambda: {"miss": 0, "hit": 0})
    for f in miss_features:
        pool_type_stats[f["pool_type"]]["miss"] += 1
    for f in hit_features:
        pool_type_stats[f["pool_type"]]["hit"] += 1

    print(f"{'Pool-Typ':<15} {'Misses':<10} {'Hits':<10} {'Miss-Rate':<12}")
    print("-" * 50)

    for ptype in ["hot", "cold_bd", "cold_nbd"]:
        stats = pool_type_stats[ptype]
        total = stats["miss"] + stats["hit"]
        rate = stats["miss"] / total * 100 if total > 0 else 0
        print(f"{ptype:<15} {stats['miss']:<10} {stats['hit']:<10} {rate:.1f}%")

    # Dekaden-Analyse
    print()
    print("=" * 80)
    print("MISS-RATE PRO DEKADE")
    print("=" * 80)
    print()

    decade_stats = defaultdict(lambda: {"miss": 0, "hit": 0})
    for f in miss_features:
        decade_stats[f["decade"]]["miss"] += 1
    for f in hit_features:
        decade_stats[f["decade"]]["hit"] += 1

    print(f"{'Dekade':<10} {'Zahlen':<15} {'Misses':<10} {'Hits':<10} {'Miss-Rate':<12}")
    print("-" * 60)

    for dec in range(7):
        stats = decade_stats[dec]
        total = stats["miss"] + stats["hit"]
        rate = stats["miss"] / total * 100 if total > 0 else 0
        zahlen = f"{dec*10+1}-{min((dec+1)*10, 70)}"
        print(f"{dec:<10} {zahlen:<15} {stats['miss']:<10} {stats['hit']:<10} {rate:.1f}%")

    # Index-Analyse (Tage seit letztem Erscheinen)
    print()
    print("=" * 80)
    print("MISS-RATE NACH INDEX (Tage seit letztem Erscheinen)")
    print("=" * 80)
    print()

    index_stats = defaultdict(lambda: {"miss": 0, "hit": 0})
    for f in miss_features:
        idx_bucket = min(f["index"] // 3, 10)  # 0-2, 3-5, 6-8, ...
        index_stats[idx_bucket]["miss"] += 1
    for f in hit_features:
        idx_bucket = min(f["index"] // 3, 10)
        index_stats[idx_bucket]["hit"] += 1

    print(f"{'Index-Bereich':<15} {'Misses':<10} {'Hits':<10} {'Miss-Rate':<12} {'Signal'}")
    print("-" * 60)

    for bucket in sorted(index_stats.keys()):
        stats = index_stats[bucket]
        total = stats["miss"] + stats["hit"]
        rate = stats["miss"] / total * 100 if total > 0 else 0
        bereich = f"{bucket*3}-{bucket*3+2}" if bucket < 10 else "30+"
        signal = "⚠️ HOCH" if rate > 75 else "✅ OK" if rate < 70 else ""
        print(f"{bereich:<15} {stats['miss']:<10} {stats['hit']:<10} {rate:.1f}% {signal}")

    # Streak-Analyse
    print()
    print("=" * 80)
    print("MISS-RATE NACH STREAK")
    print("=" * 80)
    print()

    streak_stats = defaultdict(lambda: {"miss": 0, "hit": 0})
    for f in miss_features:
        streak_bucket = max(-5, min(5, f["streak"]))  # -5 bis +5
        streak_stats[streak_bucket]["miss"] += 1
    for f in hit_features:
        streak_bucket = max(-5, min(5, f["streak"]))
        streak_stats[streak_bucket]["hit"] += 1

    print(f"{'Streak':<15} {'Bedeutung':<25} {'Misses':<10} {'Hits':<10} {'Miss-Rate':<12}")
    print("-" * 80)

    for streak in sorted(streak_stats.keys()):
        stats = streak_stats[streak]
        total = stats["miss"] + stats["hit"]
        rate = stats["miss"] / total * 100 if total > 0 else 0
        bedeutung = f"{abs(streak)} Tage {'erschienen' if streak > 0 else 'gefehlt'}"
        print(f"{streak:<15} {bedeutung:<25} {stats['miss']:<10} {stats['hit']:<10} {rate:.1f}%")

    # Empfehlungen
    print()
    print("=" * 80)
    print("EMPFEHLUNGEN: Zahlen vor Pool-Generierung ausschliessen")
    print("=" * 80)
    print()

    # Finde Zahlen mit hoher Miss-Rate
    high_miss_numbers = [z for z, rate in sorted_by_miss if rate > 0.75 and total_pool_appearances[z] >= 20]

    print("Zahlen mit >75% Miss-Rate (mind. 20 Pool-Tage):")
    for z in high_miss_numbers[:10]:
        rate = miss_rates[z]
        total = total_pool_appearances[z]
        typ = "Birthday" if z <= 31 else "Non-Birthday"
        corr = " (Korrektur-Liste)" if z in TOP_20_CORRECTION else ""
        print(f"  {z}: {rate*100:.1f}% Miss-Rate ({total} Pool-Tage) - {typ}{corr}")

    print()
    print("FILTER-REGELN basierend auf Analyse:")
    print()

    # Finde beste Signale
    strong_signals = [(k, m, h, d, p, s) for k, m, h, d, p, s in signals if "STARK" in s or "MITTEL" in s]

    for key, miss_avg, hit_avg, diff, diff_pct, signal in strong_signals:
        if diff > 0:
            print(f"  - {key} > {hit_avg:.1f} → hoehere Miss-Wahrscheinlichkeit")
        else:
            print(f"  - {key} < {miss_avg:.1f} → hoehere Miss-Wahrscheinlichkeit")

    # Speichern
    output = {
        "analysis_date": datetime.now().isoformat(),
        "total_days_analyzed": len([d for d in draws if d["datum"].year == 2025]),
        "miss_rates": {str(z): rate for z, rate in sorted_by_miss},
        "high_miss_numbers": high_miss_numbers,
        "pool_type_miss_rates": {
            k: v["miss"] / (v["miss"] + v["hit"]) if (v["miss"] + v["hit"]) > 0 else 0
            for k, v in pool_type_stats.items()
        },
        "feature_signals": [
            {"feature": k, "miss_avg": m, "hit_avg": h, "diff_pct": p}
            for k, m, h, d, p, s in signals if abs(p) > 5
        ],
    }

    output_path = base_path / "results/pool_miss_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
