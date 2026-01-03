#!/usr/bin/env python3
"""
HYPOTHESE V2: Pool-Evolution - Praezisere Analyse

Die urspruengliche Frage war:
- Werden Nicht-Jackpot-Zahlen VOR dem Jackpot eliminiert?
- Bleiben Jackpot-Zahlen im Pool erhalten?

Neue Metriken:
1. TREFFER-RETENTION: Wenn eine Zahl am Tag-10 im Pool UND im Jackpot ist,
   bleibt sie bis Tag-1 im Pool?
2. NICHT-JP-ELIMINATION: Wenn eine Zahl am Tag-10 im Pool aber NICHT im Jackpot ist,
   wird sie bis Tag-1 eliminiert?
3. SIGNAL-VERSTAERKUNG: Verbessert sich die Praezision ueber die Zeit?
"""

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np


# Pool-Generator Code (wie vorher)
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


def build_pool_v2(draws: List[Dict]) -> Set[int]:
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


def analyze_evolution_detailed(draws: List[Dict], jackpot_idx: int, lookback: int = 10):
    """Detaillierte Analyse der Pool-Evolution."""
    jackpot_numbers = draws[jackpot_idx]["zahlen"]

    # Generiere Pools fuer jeden Tag
    pools_by_day = {}
    for days_before in range(lookback, 0, -1):
        idx = jackpot_idx - days_before
        if idx < 30:
            continue
        pools_by_day[days_before] = build_pool_v2(draws[:idx])

    if not pools_by_day:
        return None

    first_day = max(pools_by_day.keys())
    last_day = min(pools_by_day.keys())

    pool_first = pools_by_day[first_day]
    pool_last = pools_by_day[last_day]

    # Kategorisiere Zahlen vom ersten Pool
    treffer_first = pool_first & jackpot_numbers  # Im Pool UND im Jackpot
    non_jp_first = pool_first - jackpot_numbers   # Im Pool aber NICHT im Jackpot

    # Wie viele Treffer blieben erhalten?
    treffer_retained = treffer_first & pool_last
    treffer_lost = treffer_first - pool_last

    # Wie viele Nicht-JP wurden eliminiert?
    non_jp_eliminated = non_jp_first - pool_last
    non_jp_retained = non_jp_first & pool_last

    # Neue Zahlen im letzten Pool
    new_in_last = pool_last - pool_first
    new_treffer = new_in_last & jackpot_numbers
    new_non_jp = new_in_last - jackpot_numbers

    return {
        "first_day": first_day,
        "last_day": last_day,
        "pool_first_size": len(pool_first),
        "pool_last_size": len(pool_last),
        # Treffer-Retention
        "treffer_first": len(treffer_first),
        "treffer_retained": len(treffer_retained),
        "treffer_lost": len(treffer_lost),
        "treffer_retention_rate": len(treffer_retained) / len(treffer_first) if treffer_first else 0,
        # Nicht-JP-Elimination
        "non_jp_first": len(non_jp_first),
        "non_jp_eliminated": len(non_jp_eliminated),
        "non_jp_retained": len(non_jp_retained),
        "non_jp_elimination_rate": len(non_jp_eliminated) / len(non_jp_first) if non_jp_first else 0,
        # Neue Zahlen
        "new_treffer": len(new_treffer),
        "new_non_jp": len(new_non_jp),
        # Praezision
        "precision_first": len(treffer_first) / len(pool_first) if pool_first else 0,
        "precision_last": len(pool_last & jackpot_numbers) / len(pool_last) if pool_last else 0,
        # Details
        "treffer_lost_numbers": sorted(treffer_lost),
        "non_jp_eliminated_numbers": sorted(non_jp_eliminated),
        "new_treffer_numbers": sorted(new_treffer),
    }


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print("=" * 80)
    print("HYPOTHESE V2: Pool-Evolution - Detaillierte Analyse")
    print("=" * 80)
    print(f"\nZiehungen: {len(draws)}")
    print()

    # Analysiere alle Events wo Pool >= 6 Treffer hatte
    results = []

    for i in range(40, len(draws)):
        draws_before = draws[:i-7]
        if len(draws_before) < 30:
            continue
        pool_7d_ago = build_pool_v2(draws_before)
        if not pool_7d_ago:
            continue
        jackpot = draws[i]["zahlen"]
        if len(pool_7d_ago & jackpot) >= 6:
            analysis = analyze_evolution_detailed(draws, i, lookback=10)
            if analysis:
                analysis["datum"] = draws[i]["datum"]
                results.append(analysis)

    print(f"Analysierte Events: {len(results)}\n")

    # Aggregierte Statistiken
    treffer_retention_rates = [r["treffer_retention_rate"] for r in results]
    non_jp_elim_rates = [r["non_jp_elimination_rate"] for r in results]
    precision_improvements = [r["precision_last"] - r["precision_first"] for r in results]
    new_treffer_counts = [r["new_treffer"] for r in results]

    print("=" * 80)
    print("KERN-METRIKEN")
    print("=" * 80)

    print(f"\n1. TREFFER-RETENTION (Jackpot-Zahlen bleiben im Pool)")
    print(f"   Durchschnitt: {np.mean(treffer_retention_rates)*100:.1f}%")
    print(f"   Min:          {np.min(treffer_retention_rates)*100:.1f}%")
    print(f"   Max:          {np.max(treffer_retention_rates)*100:.1f}%")

    print(f"\n2. NICHT-JP-ELIMINATION (Falsche Zahlen werden entfernt)")
    print(f"   Durchschnitt: {np.mean(non_jp_elim_rates)*100:.1f}%")
    print(f"   Min:          {np.min(non_jp_elim_rates)*100:.1f}%")
    print(f"   Max:          {np.max(non_jp_elim_rates)*100:.1f}%")

    print(f"\n3. NEUE TREFFER (Jackpot-Zahlen kommen hinzu)")
    print(f"   Durchschnitt: {np.mean(new_treffer_counts):.2f}")
    print(f"   Events mit neuen Treffern: {sum(1 for x in new_treffer_counts if x > 0)}/{len(new_treffer_counts)}")

    print(f"\n4. PRAEZISIONS-VERBESSERUNG (Tag-10 → Tag-1)")
    print(f"   Durchschnitt: {np.mean(precision_improvements)*100:+.2f}%")
    print(f"   Positive:     {sum(1 for x in precision_improvements if x > 0)}/{len(precision_improvements)}")

    # Die entscheidende Frage
    print("\n" + "=" * 80)
    print("HYPOTHESE-BEWERTUNG")
    print("=" * 80)

    # Hypothese ist unterstuetzt wenn:
    # - Treffer-Retention hoch (>70%)
    # - Nicht-JP-Elimination hoeher als Treffer-Verlust
    avg_treffer_retention = np.mean(treffer_retention_rates)
    avg_non_jp_elim = np.mean(non_jp_elim_rates)

    print(f"\nTreffer-Retention:    {avg_treffer_retention*100:.1f}%")
    print(f"Nicht-JP-Elimination: {avg_non_jp_elim*100:.1f}%")

    # Differenz = wie selektiv ist die Elimination?
    selectivity = avg_non_jp_elim - (1 - avg_treffer_retention)
    print(f"\nSelektivitaet:        {selectivity*100:+.1f}%")
    print("  (Positiv = System eliminiert mehr falsche als richtige Zahlen)")

    if selectivity > 0:
        print("\n✓ HYPOTHESE TEILWEISE UNTERSTUETZT!")
        print(f"  Der Pool eliminiert selektiv Nicht-Jackpot-Zahlen.")
        print(f"  Elimination-Rate fuer Nicht-JP: {avg_non_jp_elim*100:.1f}%")
        print(f"  Verlust-Rate fuer Treffer:      {(1-avg_treffer_retention)*100:.1f}%")
    else:
        print("\n✗ HYPOTHESE NICHT UNTERSTUETZT")
        print("  Die Elimination ist nicht selektiv.")

    # Zeige Beispiele
    print("\n" + "=" * 80)
    print("BEISPIELE (Top 5 mit hoher Selektivitaet)")
    print("=" * 80)

    # Sortiere nach Selektivitaet
    for r in results:
        r["selectivity"] = r["non_jp_elimination_rate"] - (1 - r["treffer_retention_rate"])

    sorted_results = sorted(results, key=lambda x: x["selectivity"], reverse=True)

    for r in sorted_results[:5]:
        print(f"\n{r['datum'].strftime('%d.%m.%Y')}:")
        print(f"  Treffer: {r['treffer_first']} → {r['treffer_retained']} (Retention: {r['treffer_retention_rate']*100:.0f}%)")
        print(f"  Nicht-JP: {r['non_jp_first']} → {r['non_jp_retained']} (Elimination: {r['non_jp_elimination_rate']*100:.0f}%)")
        print(f"  Neue Treffer: {r['new_treffer']}")
        print(f"  Selektivitaet: {r['selectivity']*100:+.1f}%")
        if r["new_treffer_numbers"]:
            print(f"  Neue Jackpot-Zahlen im Pool: {r['new_treffer_numbers']}")

    # Export
    export = {
        "events_analyzed": len(results),
        "avg_treffer_retention": float(avg_treffer_retention),
        "avg_non_jp_elimination": float(avg_non_jp_elim),
        "avg_precision_improvement": float(np.mean(precision_improvements)),
        "avg_new_treffer": float(np.mean(new_treffer_counts)),
        "selectivity": float(selectivity),
        "hypothesis_supported": selectivity > 0,
    }

    results_path = base_path / "results" / "pool_evolution_hypothesis_v2.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"\n\nErgebnisse: {results_path}")


if __name__ == "__main__":
    main()
