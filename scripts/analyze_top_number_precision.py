#!/usr/bin/env python3
"""
ANALYSE: Praezision der Top-N Zahlen

KERNFRAGE:
Wenn wir nur die Top-6, Top-8, Top-10 Zahlen aus dem Pool nehmen,
wie oft treffen diese 6/6, 5/6, etc.?

Das Ziel ist NICHT alle Kombinationen zu spielen,
sondern EIN TICKET mit den besten 6 Zahlen.

Autor: Kenobase V2
"""

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np

# Konstanten (wie vorher)
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}
BAD_PATTERNS = {"0010010", "1000111", "0101011", "1010000", "0001101", "0001000", "0100100", "0001010", "0000111"}
GOOD_PATTERNS = {"0011101", "1010011", "0001001", "1010101", "0010100", "1000001", "1000010", "0001011", "0010101"}


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


def score_number_v2(draws: List[Dict], number: int, hot: Set[int]) -> float:
    score = 50.0
    pattern = get_pattern_7(draws, number)
    if pattern in BAD_PATTERNS:
        score -= 20
    elif pattern in GOOD_PATTERNS:
        score += 15
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


def build_pool_and_rank(draws: List[Dict]) -> Tuple[List[Tuple[int, float]], Dict]:
    """Baut Pool und rankt alle Zahlen nach Score."""
    if len(draws) < 10:
        return [], {}

    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    # Baue Pool wie vorher
    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number_v2(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)
    hot_keep = set(z for z, s in hot_scored[:5])

    cold_bd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot)) for z in cold_birthday]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:6])
    if len(cold_bd_keep) < 6:
        remaining = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(remaining[:6 - len(cold_bd_keep)])

    cold_nbd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot)) for z in cold_nonbd]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_nbd_filtered = [(z, c, s) for z, c, s in cold_nbd_scored if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_nbd_keep = set(z for z, c, s in cold_nbd_filtered[:6])
    if len(cold_nbd_keep) < 6:
        remaining = [z for z, c, s in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(remaining[:6 - len(cold_nbd_keep)])

    pool = hot_keep | cold_bd_keep | cold_nbd_keep

    # Ranke alle Pool-Zahlen nach Score + Pattern-Bonus
    ranked = []
    for z in pool:
        s = score_number_v2(draws, z, hot)
        pattern = get_pattern_7(draws, z)
        if pattern in GOOD_PATTERNS:
            s += 10
        ranked.append((z, s))

    ranked.sort(key=lambda x: x[1], reverse=True)

    details = {
        "pool_size": len(pool),
        "bad_patterns": sum(1 for z in pool if get_pattern_7(draws, z) in BAD_PATTERNS),
        "good_patterns": sum(1 for z in pool if get_pattern_7(draws, z) in GOOD_PATTERNS),
    }

    return ranked, details


def get_timing_score(datum: datetime) -> int:
    day_of_month = datum.day
    weekday = datum.weekday()
    score = 50
    if day_of_month <= 14:
        score += 20
    else:
        score -= 15
    if weekday == 2:
        score += 10
    if 24 <= day_of_month <= 28:
        score += 15
    return score


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    print("=" * 100)
    print("ANALYSE: Praezision der Top-N Zahlen")
    print("=" * 100)

    draws = load_keno_data(keno_path)
    print(f"\nZiehungen: {len(draws)}")

    # Teste verschiedene Top-N Groessen
    top_n_sizes = [6, 7, 8, 9, 10, 12]
    convergence_thresholds = [70, 80, 90]
    timing_threshold = 50

    results_matrix = {}

    for conv_thresh in convergence_thresholds:
        results_matrix[conv_thresh] = {}

        for top_n in top_n_sizes:
            stats = {
                "total_days": 0,
                "hits_by_count": defaultdict(int),  # {6: count, 5: count, ...}
            }

            prev_pool = None

            for i in range(50, len(draws)):
                draws_until = draws[:i]
                current_date = draws[i]["datum"]
                todays_numbers = draws[i]["zahlen"]

                ranked, details = build_pool_and_rank(draws_until)
                if not ranked:
                    continue

                pool = set(z for z, s in ranked)

                # Stabilitaet
                stability = 0
                if prev_pool:
                    intersection = len(pool & prev_pool)
                    union = len(pool | prev_pool)
                    stability = intersection / union if union > 0 else 0

                # Timing
                timing = get_timing_score(current_date)

                # Konvergenz
                avg_score = np.mean([s for z, s in ranked])
                convergence = (
                    avg_score * 0.3 +
                    (1 - details["bad_patterns"] / 17) * 30 +
                    details["good_patterns"] * 5 +
                    stability * 20 +
                    timing * 0.5
                )

                # Filtern nach Schwellen
                if convergence >= conv_thresh and timing >= timing_threshold:
                    # Nimm Top-N Zahlen
                    top_numbers = set(z for z, s in ranked[:top_n])

                    # Zaehle Treffer
                    hits = len(top_numbers & todays_numbers)
                    stats["total_days"] += 1
                    stats["hits_by_count"][hits] += 1

                prev_pool = pool

            results_matrix[conv_thresh][top_n] = stats

    # Ausgabe
    print("\n" + "=" * 100)
    print("TREFFER-VERTEILUNG: Top-N Zahlen bei verschiedenen Konvergenz-Schwellen")
    print("=" * 100)

    for conv_thresh in convergence_thresholds:
        print(f"\n### Konvergenz >= {conv_thresh}, Timing >= {timing_threshold}")
        print()

        print(f"{'Top-N':<8} {'Tage':<8} {'6 Tr.':<8} {'5 Tr.':<8} {'4 Tr.':<8} {'3 Tr.':<8} {'0-2 Tr.':<8} {'Rate 6+':<10} {'Rate 5+':<10}")
        print("-" * 85)

        for top_n in top_n_sizes:
            stats = results_matrix[conv_thresh][top_n]
            total = stats["total_days"]

            if total == 0:
                continue

            h6 = stats["hits_by_count"][6]
            h5 = stats["hits_by_count"][5]
            h4 = stats["hits_by_count"][4]
            h3 = stats["hits_by_count"][3]
            h_low = sum(stats["hits_by_count"][i] for i in range(3))

            rate_6 = h6 / total * 100 if total > 0 else 0
            rate_5_plus = (h6 + h5) / total * 100 if total > 0 else 0

            print(f"{top_n:<8} {total:<8} {h6:<8} {h5:<8} {h4:<8} {h3:<8} {h_low:<8} {rate_6:<9.2f}% {rate_5_plus:<9.2f}%")

    # Erweiterte Analyse: Welche Tage hatten 6/6 mit Top-6?
    print("\n" + "=" * 100)
    print("DETAIL: Tage mit 6/6 Treffer (Top-6 Zahlen, Conv>=80)")
    print("=" * 100)

    prev_pool = None
    six_six_days = []

    for i in range(50, len(draws)):
        draws_until = draws[:i]
        current_date = draws[i]["datum"]
        todays_numbers = draws[i]["zahlen"]

        ranked, details = build_pool_and_rank(draws_until)
        if not ranked:
            continue

        pool = set(z for z, s in ranked)
        stability = 0
        if prev_pool:
            intersection = len(pool & prev_pool)
            union = len(pool | prev_pool)
            stability = intersection / union if union > 0 else 0

        timing = get_timing_score(current_date)
        avg_score = np.mean([s for z, s in ranked])
        convergence = avg_score * 0.3 + (1 - details["bad_patterns"] / 17) * 30 + details["good_patterns"] * 5 + stability * 20 + timing * 0.5

        if convergence >= 80 and timing >= 50:
            top_6 = set(z for z, s in ranked[:6])
            hits = len(top_6 & todays_numbers)

            if hits == 6:
                six_six_days.append({
                    "date": current_date.strftime("%d.%m.%Y"),
                    "weekday": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][current_date.weekday()],
                    "top_6": sorted(top_6),
                    "convergence": round(convergence, 1),
                    "timing": timing,
                    "stability": round(stability, 3),
                })

        prev_pool = pool

    print(f"\nGefunden: {len(six_six_days)} Tage mit 6/6 bei Top-6")

    for day in six_six_days[:20]:  # Zeige max 20
        print(f"  {day['date']} ({day['weekday']}): {day['top_6']}")
        print(f"    Conv={day['convergence']}, Time={day['timing']}, Stab={day['stability']}")

    # Berechne Erwartungswert
    print("\n" + "=" * 100)
    print("KOSTEN-NUTZEN-ANALYSE: 1 Ticket mit Top-6 Zahlen")
    print("=" * 100)

    # Bei Conv>=80, Time>=50
    stats_6 = results_matrix[80][6]
    total_days = stats_6["total_days"]
    hits_6 = stats_6["hits_by_count"][6]
    hits_5 = stats_6["hits_by_count"][5]
    hits_4 = stats_6["hits_by_count"][4]
    hits_3 = stats_6["hits_by_count"][3]

    print(f"\nKonfiguration: Conv>=80, Time>=50, Top-6 Zahlen")
    print(f"Spieltage im Backtest: {total_days}")
    print()

    # KENO Typ 6 Quoten
    prize_6 = 500
    prize_5 = 15
    prize_4 = 2
    prize_3 = 1

    total_cost = total_days * 1  # 1€ pro Ticket
    total_winnings = hits_6 * prize_6 + hits_5 * prize_5 + hits_4 * prize_4 + hits_3 * prize_3

    print(f"Kosten (1€ x {total_days}):   {total_cost}€")
    print(f"Gewinne:")
    print(f"  - 6/6 x {hits_6} x 500€ = {hits_6 * prize_6}€")
    print(f"  - 5/6 x {hits_5} x  15€ = {hits_5 * prize_5}€")
    print(f"  - 4/6 x {hits_4} x   2€ = {hits_4 * prize_4}€")
    print(f"  - 3/6 x {hits_3} x   1€ = {hits_3 * prize_3}€")
    print(f"Gesamt Gewinn:            {total_winnings}€")
    print(f"Netto:                    {total_winnings - total_cost}€")
    print(f"ROI:                      {(total_winnings - total_cost) / total_cost * 100:.1f}%")

    print()
    print(f"Erwartungswert pro Spieltag: {total_winnings / total_days:.2f}€")
    print(f"Kosten pro Spieltag:         1.00€")

    # Was wenn wir striktere Kriterien nehmen?
    print("\n" + "=" * 100)
    print("OPTIMIERUNG: Strengere Kriterien fuer hoehere Treffer-Rate")
    print("=" * 100)

    # Teste strengere Stabilitaet
    for min_stab in [0.5, 0.6, 0.7]:
        prev_pool = None
        strict_stats = {"total": 0, 6: 0, 5: 0, 4: 0, 3: 0}

        for i in range(50, len(draws)):
            draws_until = draws[:i]
            current_date = draws[i]["datum"]
            todays_numbers = draws[i]["zahlen"]

            ranked, details = build_pool_and_rank(draws_until)
            if not ranked:
                continue

            pool = set(z for z, s in ranked)
            stability = 0
            if prev_pool:
                intersection = len(pool & prev_pool)
                union = len(pool | prev_pool)
                stability = intersection / union if union > 0 else 0

            timing = get_timing_score(current_date)
            avg_score = np.mean([s for z, s in ranked])
            convergence = avg_score * 0.3 + (1 - details["bad_patterns"] / 17) * 30 + details["good_patterns"] * 5 + stability * 20 + timing * 0.5

            if convergence >= 85 and timing >= 55 and stability >= min_stab:
                top_6 = set(z for z, s in ranked[:6])
                hits = len(top_6 & todays_numbers)
                strict_stats["total"] += 1
                if hits >= 3:
                    strict_stats[hits] += 1

            prev_pool = pool

        if strict_stats["total"] > 0:
            total = strict_stats["total"]
            winnings = strict_stats[6]*500 + strict_stats[5]*15 + strict_stats[4]*2 + strict_stats[3]*1
            roi = (winnings - total) / total * 100

            print(f"\nStab >= {min_stab}:")
            print(f"  Spieltage: {total}")
            print(f"  6/6: {strict_stats[6]} ({strict_stats[6]/total*100:.2f}%)")
            print(f"  5/6: {strict_stats[5]} ({strict_stats[5]/total*100:.2f}%)")
            print(f"  ROI: {roi:.1f}%")

    # Export
    export = {
        "analysis": "top_n_precision",
        "best_config": {
            "convergence": 80,
            "timing": 50,
            "top_n": 6,
        },
        "six_six_days": len(six_six_days),
        "six_six_rate_percent": hits_6 / total_days * 100 if total_days > 0 else 0,
    }

    results_path = base_path / "results" / "top_number_precision_analysis.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)

    print(f"\n\nErgebnisse: {results_path}")


if __name__ == "__main__":
    main()
