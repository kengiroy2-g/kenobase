#!/usr/bin/env python3
"""
BACKTEST: Pool V1 vs V2

Vergleicht die Performance der beiden Pool-Generatoren
ueber ein bestimmtes Jahr (Default: 2025).
"""

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

# Konstanten
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}

BAD_PATTERNS = {
    "0010010", "1000111", "0101011", "1010000", "0001101",
    "0001000", "0100100", "0001010", "0000111",
}

GOOD_PATTERNS = {
    "0011101", "1010011", "0001001", "1010101", "0010100",
    "1000001", "1000010", "0001011", "0010101",
}


def sign_test_two_sided_p_value(wins: int, losses: int) -> float:
    """Exakter 2-seitiger Sign-Test p-Wert (Binomial)."""
    n = wins + losses
    if n == 0:
        return 1.0

    k = min(wins, losses)
    numerator = sum(math.comb(n, i) for i in range(k + 1))
    p_value = 2 * numerator / (2**n)
    return float(min(1.0, p_value))


def permutation_sign_flip_p_value(
    abs_diffs: List[int],
    observed_total: int,
    n_permutations: int,
    seed: int,
) -> Optional[float]:
    """Permutationstest (Sign-Flip) fuer Summe der Diffs (2-seitig)."""
    if n_permutations <= 0:
        return None

    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_permutations):
        total = 0
        for d in abs_diffs:
            total += d if rng.random() < 0.5 else -d
        if abs(total) >= abs(observed_total):
            extreme += 1
    return (extreme + 1) / (n_permutations + 1)


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


def get_index(draws, number):
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


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


def build_pool_v1(draws):
    """Original V1 Pool."""
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

    return hot_keep | cold_bd_keep | cold_nbd_keep


def score_number_v2(draws, number, hot):
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


def build_pool_v2(draws):
    """V2 Pool mit Pattern-Filterung."""
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


def main():
    parser = argparse.ArgumentParser(description="Backtest: Pool V1 vs V2")
    parser.add_argument("--year", type=int, default=2025, help="Jahr fuer den Backtest (Default: 2025)")
    parser.add_argument(
        "--min-history",
        type=int,
        default=60,
        help="Minimale Anzahl vorheriger Ziehungen bevor evaluiert wird (Default: 60)",
    )
    parser.add_argument(
        "--permutations",
        type=int,
        default=20000,
        help="Anzahl Sign-Flip Permutationen fuer p-Wert (0 deaktiviert, Default: 20000)",
    )
    parser.add_argument("--seed", type=int, default=0, help="Seed fuer Permutationstest (Default: 0)")
    parser.add_argument(
        "--output",
        type=str,
        default="results/pool_v1_vs_v2_backtest.json",
        help="Output JSON Pfad relativ zum Repo-Root (Default: results/pool_v1_vs_v2_backtest.json)",
    )
    args = parser.parse_args()

    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)

    print("=" * 80)
    print(f"BACKTEST: Pool V1 vs V2 ({args.year})")
    print("=" * 80)
    print()

    # Statistiken sammeln
    v1_hits = []
    v2_hits = []
    v1_pool_sizes = []
    v2_pool_sizes = []
    v1_better_days = 0
    v2_better_days = 0
    equal_days = 0

    daily_results = []

    for draw_idx, draw in enumerate(draws):
        if draw["datum"].year != args.year:
            continue

        if draw_idx < args.min_history:
            continue

        train_data = draws[:draw_idx]
        drawn = draw["zahlen"]

        pool_v1 = build_pool_v1(train_data)
        pool_v2 = build_pool_v2(train_data)

        hits_v1 = len(pool_v1 & drawn)
        hits_v2 = len(pool_v2 & drawn)

        v1_hits.append(hits_v1)
        v2_hits.append(hits_v2)
        v1_pool_sizes.append(len(pool_v1))
        v2_pool_sizes.append(len(pool_v2))

        if hits_v2 > hits_v1:
            v2_better_days += 1
        elif hits_v1 > hits_v2:
            v1_better_days += 1
        else:
            equal_days += 1

        daily_results.append({
            "datum": draw["datum"].strftime("%d.%m.%Y"),
            "hits_v1": hits_v1,
            "hits_v2": hits_v2,
            "diff": hits_v2 - hits_v1,
        })

    if not v1_hits:
        raise SystemExit(
            f"Keine Daten fuer Jahr {args.year} gefunden (oder min_history={args.min_history} zu hoch)."
        )

    # Ergebnisse
    print(f"Analysierte Tage: {len(v1_hits)}")
    print()
    print("=" * 60)
    print("TREFFER-STATISTIK")
    print("=" * 60)
    print()
    print(f"{'Metrik':<30} {'V1':<12} {'V2':<12} {'Diff':<12}")
    print("-" * 60)

    avg_v1 = np.mean(v1_hits)
    avg_v2 = np.mean(v2_hits)
    print(f"{'Durchschnittl. Treffer':<30} {avg_v1:<12.2f} {avg_v2:<12.2f} {avg_v2-avg_v1:+.2f}")

    sum_v1 = sum(v1_hits)
    sum_v2 = sum(v2_hits)
    print(f"{'Gesamt Treffer':<30} {sum_v1:<12} {sum_v2:<12} {sum_v2-sum_v1:+d}")

    max_v1 = max(v1_hits)
    max_v2 = max(v2_hits)
    print(f"{'Maximum Treffer/Tag':<30} {max_v1:<12} {max_v2:<12}")

    # Kontext: Random Baseline (hypergeometrischer Erwartungswert)
    avg_pool_v1 = float(np.mean(v1_pool_sizes))
    avg_pool_v2 = float(np.mean(v2_pool_sizes))
    expected_random_v1 = avg_pool_v1 * 20 / 70
    expected_random_v2 = avg_pool_v2 * 20 / 70

    print()
    print("=" * 60)
    print("KONTEXT (RANDOM BASELINE)")
    print("=" * 60)
    print()
    print(f"{'Ø Pool-Groesse':<30} {avg_pool_v1:<12.2f} {avg_pool_v2:<12.2f}")
    print(f"{'E[Hits] Random':<30} {expected_random_v1:<12.2f} {expected_random_v2:<12.2f}")
    print(f"{'Lift vs Random':<30} {(avg_v1-expected_random_v1):<+12.2f} {(avg_v2-expected_random_v2):<+12.2f}")

    print()
    print("=" * 60)
    print("TAGES-VERGLEICH")
    print("=" * 60)
    print()
    print(f"V2 besser:    {v2_better_days} Tage ({v2_better_days/len(v1_hits)*100:.1f}%)")
    print(f"V1 besser:    {v1_better_days} Tage ({v1_better_days/len(v1_hits)*100:.1f}%)")
    print(f"Gleich:       {equal_days} Tage ({equal_days/len(v1_hits)*100:.1f}%)")

    # Treffer-Verteilung
    print()
    print("=" * 60)
    print("TREFFER-VERTEILUNG")
    print("=" * 60)
    print()
    print(f"{'Treffer':<10} {'V1 Tage':<12} {'V2 Tage':<12} {'Differenz':<12}")
    print("-" * 50)

    for h in range(max(max_v1, max_v2) + 1):
        count_v1 = v1_hits.count(h)
        count_v2 = v2_hits.count(h)
        diff = count_v2 - count_v1
        if count_v1 > 0 or count_v2 > 0:
            print(f"{h:<10} {count_v1:<12} {count_v2:<12} {diff:+d}")

    # Tage mit grossem Unterschied
    print()
    print("=" * 60)
    print("TAGE MIT GROSSEM UNTERSCHIED (|diff| >= 3)")
    print("=" * 60)
    print()

    big_diff_days = [d for d in daily_results if abs(d["diff"]) >= 3]
    if big_diff_days:
        print(f"{'Datum':<12} {'V1':<6} {'V2':<6} {'Diff':<8} {'Gewinner'}")
        print("-" * 45)
        for d in big_diff_days:
            winner = "V2 ✅" if d["diff"] > 0 else "V1"
            print(f"{d['datum']:<12} {d['hits_v1']:<6} {d['hits_v2']:<6} {d['diff']:+d}     {winner}")
    else:
        print("Keine Tage mit grossem Unterschied gefunden.")

    # Signifikanz (Paired)
    diffs = [d["diff"] for d in daily_results]
    wins = sum(1 for d in diffs if d > 0)
    losses = sum(1 for d in diffs if d < 0)
    ties = sum(1 for d in diffs if d == 0)
    sign_p = sign_test_two_sided_p_value(wins, losses)

    nonzero_abs = [abs(d) for d in diffs if d != 0]
    observed_total = int(sum(diffs))
    perm_p = permutation_sign_flip_p_value(nonzero_abs, observed_total, args.permutations, args.seed)

    print()
    print("=" * 60)
    print("SIGNIFIKANZ (V2 - V1)")
    print("=" * 60)
    print()
    print(f"Wins/Losses/Ties: {wins}/{losses}/{ties}")
    print(f"Sign-Test p (2-seitig):      {sign_p:.4f}")
    if perm_p is not None:
        print(f"Permutation p (2-seitig):   {perm_p:.4f}  (N={args.permutations}, seed={args.seed})")
    else:
        print("Permutation p (2-seitig):   deaktiviert (--permutations 0)")

    # Speichern
    output = {
        "analysis_date": datetime.now().isoformat(),
        "params": {
            "year": args.year,
            "min_history": args.min_history,
            "permutations": args.permutations,
            "seed": args.seed,
        },
        "total_days": len(v1_hits),
        "summary": {
            "avg_hits_v1": avg_v1,
            "avg_hits_v2": avg_v2,
            "total_hits_v1": sum_v1,
            "total_hits_v2": sum_v2,
            "v2_better_days": v2_better_days,
            "v1_better_days": v1_better_days,
            "equal_days": equal_days,
            "improvement_hits": sum_v2 - sum_v1,
            "improvement_pct": (sum_v2 - sum_v1) / sum_v1 * 100 if sum_v1 > 0 else 0,
            "avg_pool_size_v1": avg_pool_v1,
            "avg_pool_size_v2": avg_pool_v2,
            "expected_random_hits_v1": expected_random_v1,
            "expected_random_hits_v2": expected_random_v2,
            "lift_vs_random_v1": avg_v1 - expected_random_v1,
            "lift_vs_random_v2": avg_v2 - expected_random_v2,
        },
        "significance": {
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "sign_test_p_two_sided": sign_p,
            "permutation_p_two_sided": perm_p,
        },
        "daily_results": daily_results,
    }

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = base_path / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print()
    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
