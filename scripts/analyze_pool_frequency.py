#!/usr/bin/env python3
"""
Tiefere Analyse: Wie OFT war jede Pool-Zahl an Jackpots beteiligt?

Vergleich: Tatsaechliche vs. erwartete Haeufigkeit.
Zahlen die UNTER-repraesentiert sind = vom System korrigiert.
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set

BIRTHDAY_POPULAR = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}


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
                    data.append({
                        "datum": datum,
                        "datum_str": datum_str,
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_momentum_numbers(draws: List[Dict], target_date: datetime, lookback: int = 3) -> Set[int]:
    """Holt Momentum-Zahlen."""
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set()

    recent = relevant[-lookback:]
    counts = defaultdict(int)

    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1

    return {z for z, c in counts.items() if c >= 2}


def analyze_frequency(
    pool: Set[int],
    draws: List[Dict],
    start_date: datetime,
    months: int = 6
) -> Dict:
    """
    Zaehlt wie oft jede Pool-Zahl an 6/6 und 7/7 Treffern beteiligt war.
    """
    end_date = start_date + timedelta(days=months * 30)
    test_draws = [d for d in draws if start_date <= d["datum"] <= end_date]

    pool_list = sorted(pool)

    # Zaehler fuer jede Zahl
    count_in_6_6 = defaultdict(int)
    count_in_7_7 = defaultdict(int)
    count_drawn = defaultdict(int)  # Wie oft wurde die Zahl ueberhaupt gezogen?

    total_6_6 = 0
    total_7_7 = 0

    print(f"\nAnalysiere gegen {len(test_draws)} Ziehungen...")

    for draw in test_draws:
        drawn = draw["zahlen"]

        # Zaehle wie oft jede Pool-Zahl gezogen wurde
        for z in pool:
            if z in drawn:
                count_drawn[z] += 1

        # Pool-Zahlen die in dieser Ziehung gezogen wurden
        pool_in_draw = pool & drawn

        if len(pool_in_draw) >= 6:
            # Fuer jede 6er Kombi aus den getroffenen Pool-Zahlen
            for combo in combinations(sorted(pool_in_draw), 6):
                total_6_6 += 1
                for z in combo:
                    count_in_6_6[z] += 1

        if len(pool_in_draw) >= 7:
            # Fuer jede 7er Kombi
            for combo in combinations(sorted(pool_in_draw), 7):
                total_7_7 += 1
                for z in combo:
                    count_in_7_7[z] += 1

    return {
        "pool": pool,
        "test_draws": len(test_draws),
        "total_6_6": total_6_6,
        "total_7_7": total_7_7,
        "count_in_6_6": dict(count_in_6_6),
        "count_in_7_7": dict(count_in_7_7),
        "count_drawn": dict(count_drawn),
    }


def main():
    print("=" * 80)
    print("FREQUENZ-ANALYSE: Wie oft war jede Pool-Zahl an Jackpots beteiligt?")
    print("=" * 80)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Test ab 01.02.2025
    target_date = datetime(2025, 2, 1)
    momentum = get_momentum_numbers(draws, target_date, lookback=3)
    pool = BIRTHDAY_POPULAR | momentum

    print(f"\nPool ({len(pool)} Zahlen): {sorted(pool)}")

    results = analyze_frequency(pool, draws, target_date, months=6)

    # Berechne erwartete Haeufigkeit
    # Wenn alle Zahlen gleich verteilt waeren:
    total_6_6 = results["total_6_6"]
    total_7_7 = results["total_7_7"]
    pool_size = len(pool)

    # In einer 6er Kombi sind 6 Zahlen, also sollte jede Zahl
    # bei Gleichverteilung (total_6_6 * 6 / pool_size) mal vorkommen
    expected_6_6 = (total_6_6 * 6) / pool_size
    expected_7_7 = (total_7_7 * 7) / pool_size

    print(f"\n{'='*80}")
    print("ERGEBNISSE")
    print(f"{'='*80}")

    print(f"\nGesamt 6/6 Jackpots: {total_6_6}")
    print(f"Gesamt 7/7 Jackpots: {total_7_7}")
    print(f"Erwartete 6/6 pro Zahl (bei Gleichverteilung): {expected_6_6:.1f}")
    print(f"Erwartete 7/7 pro Zahl (bei Gleichverteilung): {expected_7_7:.1f}")

    print(f"\n{'='*80}")
    print("6/6 JACKPOT-BETEILIGUNG PRO ZAHL")
    print(f"{'='*80}")

    print(f"\n{'Zahl':<6} {'Gezogen':<10} {'In 6/6':<10} {'Erwartet':<10} {'Diff%':<10} {'Status'}")
    print("-" * 65)

    sorted_6_6 = sorted(pool, key=lambda z: results["count_in_6_6"].get(z, 0))

    for z in sorted_6_6:
        drawn = results["count_drawn"].get(z, 0)
        count = results["count_in_6_6"].get(z, 0)
        diff_pct = ((count - expected_6_6) / expected_6_6) * 100 if expected_6_6 > 0 else 0

        if diff_pct < -20:
            status = "UNTER-repraesentiert!"
        elif diff_pct > 20:
            status = "UEBER-repraesentiert"
        else:
            status = "Normal"

        is_birthday = "B" if z in BIRTHDAY_POPULAR else " "
        is_momentum = "M" if z in momentum else " "
        flags = is_birthday + is_momentum

        print(f"{z:<4}{flags} {drawn:<10} {count:<10} {expected_6_6:<10.1f} {diff_pct:>+8.1f}%  {status}")

    print(f"\n{'='*80}")
    print("7/7 JACKPOT-BETEILIGUNG PRO ZAHL")
    print(f"{'='*80}")

    print(f"\n{'Zahl':<6} {'Gezogen':<10} {'In 7/7':<10} {'Erwartet':<10} {'Diff%':<10} {'Status'}")
    print("-" * 65)

    sorted_7_7 = sorted(pool, key=lambda z: results["count_in_7_7"].get(z, 0))

    for z in sorted_7_7:
        drawn = results["count_drawn"].get(z, 0)
        count = results["count_in_7_7"].get(z, 0)
        diff_pct = ((count - expected_7_7) / expected_7_7) * 100 if expected_7_7 > 0 else 0

        if diff_pct < -20:
            status = "UNTER-repraesentiert!"
        elif diff_pct > 20:
            status = "UEBER-repraesentiert"
        else:
            status = "Normal"

        is_birthday = "B" if z in BIRTHDAY_POPULAR else " "
        is_momentum = "M" if z in momentum else " "
        flags = is_birthday + is_momentum

        print(f"{z:<4}{flags} {drawn:<10} {count:<10} {expected_7_7:<10.1f} {diff_pct:>+8.1f}%  {status}")

    # Identifiziere unter-repraesentierte Zahlen
    print(f"\n{'='*80}")
    print("ZUSAMMENFASSUNG: UNTER-REPRAESENTIERTE ZAHLEN (< -20%)")
    print(f"{'='*80}")

    under_6_6 = [z for z in pool if ((results["count_in_6_6"].get(z, 0) - expected_6_6) / expected_6_6) * 100 < -20]
    under_7_7 = [z for z in pool if ((results["count_in_7_7"].get(z, 0) - expected_7_7) / expected_7_7) * 100 < -20]
    under_both = set(under_6_6) & set(under_7_7)

    print(f"\n  Unter-repraesentiert bei 6/6: {sorted(under_6_6)}")
    print(f"  Unter-repraesentiert bei 7/7: {sorted(under_7_7)}")
    print(f"\n  >>> BEI BEIDEN unter-repraesentiert: {sorted(under_both)} <<<")

    if under_both:
        print(f"\n  Diese {len(under_both)} Zahlen werden moeglicherweise vom System KORRIGIERT!")
        for z in sorted(under_both):
            is_b = "Birthday" if z in BIRTHDAY_POPULAR else ""
            is_m = "Momentum" if z in momentum else ""
            typ = f"({is_b} {is_m})".strip("() ")
            print(f"    - {z} {typ}")


if __name__ == "__main__":
    main()
