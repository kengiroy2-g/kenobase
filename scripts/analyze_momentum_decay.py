#!/usr/bin/env python3
"""
MOMENTUM DECAY ANALYSE

Untersucht: Wie lange haelt das Momentum an bevor die Korrektur einsetzt?

Hypothese:
- HOT Zahlen performen gut in den ersten 1-3 Tagen
- Dann setzt die Korrektur ein
- Nach X Tagen werden sie zu COLD und performen schlecht

Diese Analyse hilft das optimale Timing zu finden.
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple

ALL_NUMBERS = set(range(1, 71))


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


def get_hot_numbers(draws: List[Dict], target_idx: int, lookback: int = 3) -> Set[int]:
    """Zahlen die >= 2x in den letzten 'lookback' Ziehungen erschienen."""
    if target_idx < lookback:
        return set()

    recent = draws[target_idx - lookback:target_idx]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1

    return {z for z, c in counts.items() if c >= 2}


def analyze_momentum_decay(draws: List[Dict], start_idx: int, max_days_ahead: int = 14) -> Dict:
    """
    Analysiert wie HOT Zahlen in den folgenden Tagen performen.

    Fuer jeden Tag nach dem "HOT werden":
    - Zaehle wie oft HOT Zahlen noch gezogen werden
    - Vergleiche mit Erwartung (20/70 = 28.57%)
    """
    results = {day: {"total_hot": 0, "drawn": 0, "not_drawn": 0} for day in range(1, max_days_ahead + 1)}

    for idx in range(start_idx, len(draws) - max_days_ahead):
        # Finde HOT Zahlen an diesem Tag
        hot = get_hot_numbers(draws, idx, lookback=3)

        if not hot:
            continue

        # Pruefe fuer jeden folgenden Tag
        for day_ahead in range(1, max_days_ahead + 1):
            future_draw = draws[idx + day_ahead]
            future_numbers = future_draw["zahlen"]

            for z in hot:
                results[day_ahead]["total_hot"] += 1
                if z in future_numbers:
                    results[day_ahead]["drawn"] += 1
                else:
                    results[day_ahead]["not_drawn"] += 1

    return results


def analyze_cold_decay(draws: List[Dict], start_idx: int, max_days_ahead: int = 14) -> Dict:
    """
    Analysiert wie COLD Zahlen in den folgenden Tagen performen.
    """
    results = {day: {"total_cold": 0, "drawn": 0, "not_drawn": 0} for day in range(1, max_days_ahead + 1)}

    for idx in range(start_idx, len(draws) - max_days_ahead):
        hot = get_hot_numbers(draws, idx, lookback=3)
        cold = ALL_NUMBERS - hot

        if not cold:
            continue

        for day_ahead in range(1, max_days_ahead + 1):
            future_draw = draws[idx + day_ahead]
            future_numbers = future_draw["zahlen"]

            for z in cold:
                results[day_ahead]["total_cold"] += 1
                if z in future_numbers:
                    results[day_ahead]["drawn"] += 1
                else:
                    results[day_ahead]["not_drawn"] += 1

    return results


def main():
    print("=" * 100)
    print("MOMENTUM DECAY ANALYSE")
    print("Wie lange haelt das Momentum? Wann setzt die Korrektur ein?")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Starte Analyse ab Tag 100 fuer genug History
    start_idx = 100

    # === HOT ZAHLEN DECAY ===
    print(f"\n{'='*100}")
    print("HOT ZAHLEN: Performance in den folgenden Tagen")
    print(f"{'='*100}")

    hot_results = analyze_momentum_decay(draws, start_idx, max_days_ahead=14)

    expected_rate = 20 / 70  # 28.57%

    print(f"\n{'Tag':<6} {'Gezogen':<12} {'Nicht':<12} {'Rate':<10} {'vs.Erw.':<12} {'Signal'}")
    print("-" * 80)

    for day in range(1, 15):
        r = hot_results[day]
        if r["total_hot"] > 0:
            rate = r["drawn"] / r["total_hot"]
            diff = (rate - expected_rate) / expected_rate * 100
            signal = "HOT +" if diff > 2 else ("KORREKTUR" if diff < -2 else "NEUTRAL")
            print(f"T+{day:<4} {r['drawn']:<12} {r['not_drawn']:<12} {rate*100:.1f}%     {diff:>+6.1f}%      {signal}")

    # === COLD ZAHLEN DECAY ===
    print(f"\n{'='*100}")
    print("COLD ZAHLEN: Performance in den folgenden Tagen")
    print(f"{'='*100}")

    cold_results = analyze_cold_decay(draws, start_idx, max_days_ahead=14)

    print(f"\n{'Tag':<6} {'Gezogen':<12} {'Nicht':<12} {'Rate':<10} {'vs.Erw.':<12} {'Signal'}")
    print("-" * 80)

    for day in range(1, 15):
        r = cold_results[day]
        if r["total_cold"] > 0:
            rate = r["drawn"] / r["total_cold"]
            diff = (rate - expected_rate) / expected_rate * 100
            signal = "COLD +" if diff > 2 else ("DUE" if diff < -2 else "NEUTRAL")
            print(f"T+{day:<4} {r['drawn']:<12} {r['not_drawn']:<12} {rate*100:.1f}%     {diff:>+6.1f}%      {signal}")

    # === MOMENTUM vs CORRECTION CROSSOVER ===
    print(f"\n{'='*100}")
    print("MOMENTUM vs. KORREKTUR: Crossover-Analyse")
    print(f"{'='*100}")

    print(f"\n{'Tag':<6} {'HOT Rate':<12} {'COLD Rate':<12} {'Differenz':<12} {'Empfehlung'}")
    print("-" * 80)

    for day in range(1, 15):
        hot_r = hot_results[day]
        cold_r = cold_results[day]

        if hot_r["total_hot"] > 0 and cold_r["total_cold"] > 0:
            hot_rate = hot_r["drawn"] / hot_r["total_hot"]
            cold_rate = cold_r["drawn"] / cold_r["total_cold"]
            diff = (hot_rate - cold_rate) * 100

            if diff > 1:
                rec = "→ Spiele HOT"
            elif diff < -1:
                rec = "→ Spiele COLD"
            else:
                rec = "→ Neutral"

            print(f"T+{day:<4} {hot_rate*100:.2f}%      {cold_rate*100:.2f}%      {diff:>+6.2f}%      {rec}")

    # === OPTIMALES TIMING ===
    print(f"\n{'='*100}")
    print("OPTIMALES TIMING: Wann wechseln?")
    print(f"{'='*100}")

    # Finde Crossover-Punkt
    crossover_day = None
    for day in range(1, 15):
        hot_r = hot_results[day]
        cold_r = cold_results[day]

        if hot_r["total_hot"] > 0 and cold_r["total_cold"] > 0:
            hot_rate = hot_r["drawn"] / hot_r["total_hot"]
            cold_rate = cold_r["drawn"] / cold_r["total_cold"]

            if cold_rate > hot_rate and crossover_day is None:
                crossover_day = day
                break

    if crossover_day:
        print(f"\n  CROSSOVER an Tag {crossover_day}:")
        print(f"  - Bis Tag {crossover_day - 1}: HOT Zahlen spielen")
        print(f"  - Ab Tag {crossover_day}: COLD Zahlen spielen")
    else:
        print("\n  Kein klarer Crossover gefunden.")
        print("  HOT Zahlen scheinen durchgehend zu performen.")

    # === STRATEGIE-EMPFEHLUNG ===
    print(f"\n{'='*100}")
    print("STRATEGIE-EMPFEHLUNG")
    print(f"{'='*100}")

    # Berechne durchschnittliche Performance
    hot_avg = sum(hot_results[d]["drawn"] / hot_results[d]["total_hot"]
                  for d in range(1, 8) if hot_results[d]["total_hot"] > 0) / 7
    cold_avg = sum(cold_results[d]["drawn"] / cold_results[d]["total_cold"]
                   for d in range(1, 8) if cold_results[d]["total_cold"] > 0) / 7

    hot_diff = (hot_avg - expected_rate) / expected_rate * 100
    cold_diff = (cold_avg - expected_rate) / expected_rate * 100

    print(f"""
    DURCHSCHNITTLICHE PERFORMANCE (Tag 1-7):

    HOT Zahlen:  {hot_avg*100:.2f}% ({hot_diff:+.1f}% vs. Erwartung)
    COLD Zahlen: {cold_avg*100:.2f}% ({cold_diff:+.1f}% vs. Erwartung)

    EMPFEHLUNG:
    """)

    if hot_diff > cold_diff + 1:
        print(f"    → MOMENTUM-STRATEGIE: Spiele HOT Zahlen")
        print(f"    → HOT Zahlen haben {hot_diff - cold_diff:.1f}% Vorteil")
    elif cold_diff > hot_diff + 1:
        print(f"    → KORREKTUR-STRATEGIE: Spiele COLD Zahlen")
        print(f"    → COLD Zahlen haben {cold_diff - hot_diff:.1f}% Vorteil")
    else:
        print(f"    → NEUTRAL: Kein signifikanter Unterschied")
        print(f"    → Andere Faktoren (Birthday, Pool-Groesse) wichtiger")

    print(f"\n[Analyse abgeschlossen]")


if __name__ == "__main__":
    main()
