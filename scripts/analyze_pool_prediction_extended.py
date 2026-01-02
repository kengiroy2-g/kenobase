#!/usr/bin/env python3
"""
ERWEITERTE Vorhersage-Analyse.

Zusaetzliche Metriken:
- Trend (Index-Aenderung in letzten 2 Wochen)
- Volatilitaet (Schwankung des Index)
- Hot/Cold Status (basierend auf MCount)
- Stichtag-Metriken vs. Test-Ergebnis
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import stdev
from typing import Dict, List, Set

UNDER_REPRESENTED = {21, 29, 45, 67}
OVER_REPRESENTED = {26, 2, 27}
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


def calculate_metrics(draws: List[Dict], target_idx: int, zahl: int) -> Dict:
    """Berechnet alle Metriken."""
    lookback_20 = draws[max(0, target_idx-20):target_idx]
    count_20 = sum(1 for d in lookback_20 if zahl in d["zahlen"])
    index = sum(1 if zahl in d["zahlen"] else -1 for d in lookback_20)
    lookback_3 = draws[max(0, target_idx-3):target_idx]
    mcount = sum(1 for d in lookback_3 if zahl in d["zahlen"])
    gap = 0
    for i in range(target_idx - 1, -1, -1):
        if zahl in draws[i]["zahlen"]:
            break
        gap += 1
    return {"index": index, "count_20": count_20, "mcount_3": mcount, "gap": gap}


def main():
    print("=" * 100)
    print("ERWEITERTE VORHERSAGE-ANALYSE")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    stichtag = datetime(2025, 2, 1)
    pre_start = datetime(2025, 1, 18)
    test_end = datetime(2025, 7, 31)

    pre_start_idx = next(i for i, d in enumerate(draws) if d["datum"] >= pre_start)
    stichtag_idx = next(i for i, d in enumerate(draws) if d["datum"] >= stichtag)
    test_end_idx = next(i for i, d in enumerate(draws) if d["datum"] > test_end) - 1

    momentum = get_momentum_numbers(draws, stichtag, lookback=3)
    pool = BIRTHDAY_POPULAR | momentum
    pool_list = sorted(pool)

    print(f"\nPool: {pool_list}")
    print(f"Unter-repraesentiert: {sorted(UNDER_REPRESENTED)}")
    print(f"Ueber-repraesentiert: {sorted(OVER_REPRESENTED)}")

    # === Berechne erweiterte Metriken ===
    results = {}

    for z in pool_list:
        # Pre-Phase Metriken (jeden Tag)
        pre_indices = []
        for idx in range(pre_start_idx, stichtag_idx):
            m = calculate_metrics(draws, idx, z)
            pre_indices.append(m["index"])

        # Stichtag-Metriken
        stichtag_metrics = calculate_metrics(draws, stichtag_idx, z)

        # Test-Phase Metriken
        test_indices = []
        test_drawn_count = 0
        for idx in range(stichtag_idx, test_end_idx + 1):
            m = calculate_metrics(draws, idx, z)
            test_indices.append(m["index"])
            if z in draws[idx]["zahlen"]:
                test_drawn_count += 1

        # Trend berechnen (Aenderung ueber Pre-Phase)
        if len(pre_indices) >= 2:
            trend = pre_indices[-1] - pre_indices[0]
        else:
            trend = 0

        # Volatilitaet (Standardabweichung des Index)
        volatility = stdev(pre_indices) if len(pre_indices) >= 2 else 0

        # Hot/Cold am Stichtag
        is_hot = stichtag_metrics["mcount_3"] >= 2
        is_cold = stichtag_metrics["gap"] >= 5

        results[z] = {
            "pre_avg_idx": sum(pre_indices) / len(pre_indices) if pre_indices else 0,
            "pre_start_idx": pre_indices[0] if pre_indices else 0,
            "pre_end_idx": pre_indices[-1] if pre_indices else 0,
            "trend": trend,
            "volatility": volatility,
            "stichtag_idx": stichtag_metrics["index"],
            "stichtag_mcount": stichtag_metrics["mcount_3"],
            "stichtag_gap": stichtag_metrics["gap"],
            "is_hot": is_hot,
            "is_cold": is_cold,
            "test_avg_idx": sum(test_indices) / len(test_indices) if test_indices else 0,
            "test_drawn": test_drawn_count,
            "test_days": test_end_idx - stichtag_idx + 1,
        }

    # === Ausgabe 1: Alle Zahlen sortiert nach Stichtag-Index ===
    print(f"\n{'='*100}")
    print("SORTIERT NACH STICHTAG-INDEX (am 01.02.2025)")
    print(f"{'='*100}")

    sorted_by_idx = sorted(pool_list, key=lambda z: results[z]["stichtag_idx"])

    print(f"\n{'Zahl':<6} {'Stichtag':<10} {'Trend':<8} {'Volat':<8} {'Hot?':<6} {'Cold?':<6} {'TestDrw':<8} {'Kat'}")
    print("-" * 80)

    for z in sorted_by_idx:
        r = results[z]
        if z in UNDER_REPRESENTED:
            cat = "UNTER"
        elif z in OVER_REPRESENTED:
            cat = "UEBER"
        else:
            cat = "-"

        hot = "JA" if r["is_hot"] else ""
        cold = "JA" if r["is_cold"] else ""

        print(f"{z:<6} {r['stichtag_idx']:>+8}   {r['trend']:>+6.1f}   {r['volatility']:<8.2f} {hot:<6} {cold:<6} {r['test_drawn']:<8} {cat}")

    # === Ausgabe 2: Momentum-Status am Stichtag ===
    print(f"\n{'='*100}")
    print("MOMENTUM-STATUS AM STICHTAG")
    print(f"{'='*100}")

    hot_numbers = [z for z in pool_list if results[z]["is_hot"]]
    cold_numbers = [z for z in pool_list if results[z]["is_cold"]]

    print(f"\n  HOT (MCount >= 2): {sorted(hot_numbers)}")
    print(f"    Davon UNTER: {sorted(set(hot_numbers) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER: {sorted(set(hot_numbers) & OVER_REPRESENTED)}")

    print(f"\n  COLD (Gap >= 5): {sorted(cold_numbers)}")
    print(f"    Davon UNTER: {sorted(set(cold_numbers) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER: {sorted(set(cold_numbers) & OVER_REPRESENTED)}")

    # === Ausgabe 3: Trend-Analyse ===
    print(f"\n{'='*100}")
    print("TREND-ANALYSE (Index-Aenderung in Pre-Phase)")
    print(f"{'='*100}")

    rising = [z for z in pool_list if results[z]["trend"] > 2]
    falling = [z for z in pool_list if results[z]["trend"] < -2]
    stable = [z for z in pool_list if -2 <= results[z]["trend"] <= 2]

    print(f"\n  STEIGEND (Trend > +2): {sorted(rising)}")
    print(f"    Davon UNTER: {sorted(set(rising) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER: {sorted(set(rising) & OVER_REPRESENTED)}")

    print(f"\n  FALLEND (Trend < -2): {sorted(falling)}")
    print(f"    Davon UNTER: {sorted(set(falling) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER: {sorted(set(falling) & OVER_REPRESENTED)}")

    print(f"\n  STABIL (-2 bis +2): {sorted(stable)}")
    print(f"    Davon UNTER: {sorted(set(stable) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER: {sorted(set(stable) & OVER_REPRESENTED)}")

    # === Ausgabe 4: Kombinierte Indikatoren ===
    print(f"\n{'='*100}")
    print("KOMBINIERTE INDIKATOREN")
    print(f"{'='*100}")

    # Niedrigster Index + HOT = potentiell unter-repraesentiert?
    low_idx_hot = [z for z in pool_list if results[z]["stichtag_idx"] < -5 and results[z]["is_hot"]]
    print(f"\n  NIEDRIGER Index (< -5) + HOT:")
    print(f"    Zahlen: {sorted(low_idx_hot)}")
    print(f"    Davon UNTER: {sorted(set(low_idx_hot) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER: {sorted(set(low_idx_hot) & OVER_REPRESENTED)}")

    # Hoechster Index + COLD = potentiell ueber-repraesentiert?
    high_idx_cold = [z for z in pool_list if results[z]["stichtag_idx"] > 0 and results[z]["is_cold"]]
    print(f"\n  HOHER Index (> 0) + COLD:")
    print(f"    Zahlen: {sorted(high_idx_cold)}")
    print(f"    Davon UNTER: {sorted(set(high_idx_cold) & UNDER_REPRESENTED)}")
    print(f"    Davon UEBER: {sorted(set(high_idx_cold) & OVER_REPRESENTED)}")

    # === Ausgabe 5: Ziehungshaeufigkeit vs. Erwartung ===
    print(f"\n{'='*100}")
    print("ZIEHUNGSHAEUFIGKEIT IM TEST vs. ERWARTUNG")
    print(f"{'='*100}")

    test_days = results[pool_list[0]]["test_days"]
    expected_draws = test_days * 20 / 70  # Erwartete Ziehungen pro Zahl

    print(f"\n  Test-Tage: {test_days}")
    print(f"  Erwartete Ziehungen pro Zahl: {expected_draws:.1f}")

    print(f"\n{'Zahl':<6} {'Gezogen':<10} {'Erwartet':<10} {'Diff%':<10} {'Sticht.Idx':<12} {'Hot?':<6} {'Kat'}")
    print("-" * 80)

    sorted_by_drawn = sorted(pool_list, key=lambda z: results[z]["test_drawn"])

    for z in sorted_by_drawn:
        r = results[z]
        diff_pct = ((r["test_drawn"] - expected_draws) / expected_draws) * 100

        if z in UNDER_REPRESENTED:
            cat = "UNTER"
        elif z in OVER_REPRESENTED:
            cat = "UEBER"
        else:
            cat = "-"

        hot = "JA" if r["is_hot"] else ""

        print(f"{z:<6} {r['test_drawn']:<10} {expected_draws:<10.1f} {diff_pct:>+8.1f}%  {r['stichtag_idx']:>+10}   {hot:<6} {cat}")

    # === Ausgabe 6: Detailvergleich UNTER vs. UEBER ===
    print(f"\n{'='*100}")
    print("DETAILVERGLEICH: UNTER vs. UEBER-REPRAESENTIERTE")
    print(f"{'='*100}")

    print(f"\n  UNTER-REPRAESENTIERTE ZAHLEN ({len(UNDER_REPRESENTED & pool)}):")
    for z in sorted(UNDER_REPRESENTED & pool):
        r = results[z]
        print(f"    {z}: StichtagIdx={r['stichtag_idx']:+d}, Trend={r['trend']:+.1f}, Hot={r['is_hot']}, TestDrawn={r['test_drawn']}")

    print(f"\n  UEBER-REPRAESENTIERTE ZAHLEN ({len(OVER_REPRESENTED & pool)}):")
    for z in sorted(OVER_REPRESENTED & pool):
        r = results[z]
        print(f"    {z}: StichtagIdx={r['stichtag_idx']:+d}, Trend={r['trend']:+.1f}, Hot={r['is_hot']}, TestDrawn={r['test_drawn']}")

    # === Ausgabe 7: Muster-Suche ===
    print(f"\n{'='*100}")
    print("MUSTER-SUCHE: Was unterscheidet UNTER von UEBER?")
    print(f"{'='*100}")

    under_in_pool = UNDER_REPRESENTED & pool
    over_in_pool = OVER_REPRESENTED & pool

    avg_under_idx = sum(results[z]["stichtag_idx"] for z in under_in_pool) / len(under_in_pool) if under_in_pool else 0
    avg_over_idx = sum(results[z]["stichtag_idx"] for z in over_in_pool) / len(over_in_pool) if over_in_pool else 0

    avg_under_trend = sum(results[z]["trend"] for z in under_in_pool) / len(under_in_pool) if under_in_pool else 0
    avg_over_trend = sum(results[z]["trend"] for z in over_in_pool) / len(over_in_pool) if over_in_pool else 0

    under_hot_count = sum(1 for z in under_in_pool if results[z]["is_hot"])
    over_hot_count = sum(1 for z in over_in_pool if results[z]["is_hot"])

    avg_under_drawn = sum(results[z]["test_drawn"] for z in under_in_pool) / len(under_in_pool) if under_in_pool else 0
    avg_over_drawn = sum(results[z]["test_drawn"] for z in over_in_pool) / len(over_in_pool) if over_in_pool else 0

    print(f"""
    METRIK                    UNTER       UEBER       DIFFERENZ
    ----------------------------------------------------------------
    Stichtag-Index (avg)      {avg_under_idx:+.2f}       {avg_over_idx:+.2f}       {avg_under_idx - avg_over_idx:+.2f}
    Trend (avg)               {avg_under_trend:+.2f}       {avg_over_trend:+.2f}       {avg_under_trend - avg_over_trend:+.2f}
    Anzahl HOT                {under_hot_count}/{len(under_in_pool)}           {over_hot_count}/{len(over_in_pool)}
    Test-Ziehungen (avg)      {avg_under_drawn:.1f}        {avg_over_drawn:.1f}        {avg_under_drawn - avg_over_drawn:+.1f}
    """)

    # === Moegliche Vorhersage-Regel ===
    print(f"\n{'='*100}")
    print("MOEGLICHE VORHERSAGE-REGEL (zu testen)")
    print(f"{'='*100}")

    # Schauen ob es ein Muster gibt
    # UNTER: 21, 29, 45, 67 - alle waren HOT am Stichtag!
    # UEBER: 2, 26, 27 - wie war deren Status?

    under_all_hot = all(results[z]["is_hot"] for z in under_in_pool)
    over_all_hot = all(results[z]["is_hot"] for z in over_in_pool)

    print(f"\n  Beobachtung 1: UNTER-repraesentierte alle HOT am Stichtag? {under_all_hot}")
    print(f"  Beobachtung 2: UEBER-repraesentierte alle HOT am Stichtag? {over_all_hot}")

    # Unterschied koennte in der KOMBINATION von Merkmalen liegen
    print(f"\n  Alle HOT-Zahlen am Stichtag: {sorted([z for z in pool_list if results[z]['is_hot']])}")

    # Birthday vs Non-Birthday bei HOT
    hot_birthday = [z for z in pool_list if results[z]["is_hot"] and z in BIRTHDAY_POPULAR]
    hot_non_birthday = [z for z in pool_list if results[z]["is_hot"] and z not in BIRTHDAY_POPULAR]

    print(f"\n  HOT + Birthday: {sorted(hot_birthday)}")
    print(f"    Davon UNTER: {sorted(set(hot_birthday) & UNDER_REPRESENTED)}")

    print(f"\n  HOT + Non-Birthday: {sorted(hot_non_birthday)}")
    print(f"    Davon UNTER: {sorted(set(hot_non_birthday) & UNDER_REPRESENTED)}")

    print(f"\n[Analyse abgeschlossen - keine Schlussfolgerungen gezogen]")


if __name__ == "__main__":
    main()
