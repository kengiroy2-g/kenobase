#!/usr/bin/env python3
"""
Analyse der Index/Count-Metriken fuer spezifische Zahlen.

Ziel: Verstehen warum 21, 29, 45, 67 unter-repraesentiert sind.
"""

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

TARGET_NUMBERS = [21, 29, 45, 67]


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


def calculate_metrics_for_date(
    draws: List[Dict],
    target_idx: int,
    zahlen: List[int]
) -> Dict[int, Dict]:
    """
    Berechnet Metriken fuer bestimmte Zahlen an einem bestimmten Tag.

    Metriken:
    - Index: Netto-Bilanz der letzten 20 Tage (+1 gezogen, -1 nicht gezogen)
    - Count: Anzahl Erscheinungen in letzten 20 Tagen
    - MCount: Anzahl Erscheinungen in letzten 3 Tagen (Momentum)
    - Gap: Tage seit letztem Erscheinen
    - Streak: Aufeinanderfolgende Tage gezogen/nicht gezogen
    """
    results = {}

    for zahl in zahlen:
        # Index und Count (letzte 20 Tage)
        lookback_20 = draws[max(0, target_idx-20):target_idx]
        count_20 = sum(1 for d in lookback_20 if zahl in d["zahlen"])
        index = 0
        for d in lookback_20:
            if zahl in d["zahlen"]:
                index += 1
            else:
                index -= 1

        # MCount (letzte 3 Tage)
        lookback_3 = draws[max(0, target_idx-3):target_idx]
        mcount = sum(1 for d in lookback_3 if zahl in d["zahlen"])

        # Gap: Tage seit letztem Erscheinen
        gap = 0
        for i in range(target_idx - 1, -1, -1):
            if zahl in draws[i]["zahlen"]:
                break
            gap += 1

        # Streak
        streak = 0
        if target_idx > 0:
            last_drawn = zahl in draws[target_idx - 1]["zahlen"]
            for i in range(target_idx - 1, -1, -1):
                current_drawn = zahl in draws[i]["zahlen"]
                if current_drawn == last_drawn:
                    streak += 1
                else:
                    break
            if not last_drawn:
                streak = -streak  # Negative fuer "nicht gezogen" Streak

        results[zahl] = {
            "index": index,
            "count_20": count_20,
            "mcount_3": mcount,
            "gap": gap,
            "streak": streak,
        }

    return results


def main():
    print("=" * 100)
    print(f"METRIKEN-ANALYSE: Zahlen {TARGET_NUMBERS}")
    print("Zeitraum: 01.02.2025 bis letzter Testtag")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Finde Start-Index (01.02.2025)
    start_date = datetime(2025, 2, 1)
    end_date = datetime(2025, 7, 31)

    start_idx = None
    end_idx = None
    for i, d in enumerate(draws):
        if d["datum"] >= start_date and start_idx is None:
            start_idx = i
        if d["datum"] <= end_date:
            end_idx = i

    if start_idx is None:
        print("Startdatum nicht gefunden!")
        return

    print(f"Analysiere von Index {start_idx} bis {end_idx}")
    print(f"Erste Ziehung: {draws[start_idx]['datum_str']}")
    print(f"Letzte Ziehung: {draws[end_idx]['datum_str']}")

    # Header
    print(f"\n{'='*100}")
    print(f"{'Datum':<12} | ", end="")
    for z in TARGET_NUMBERS:
        print(f"  {z:^18}  |", end="")
    print()
    print(f"{'':12} | ", end="")
    for z in TARGET_NUMBERS:
        print(f" Idx Cnt MC Gap Str |", end="")
    print()
    print("-" * 100)

    # Sammle Statistiken
    stats = {z: {"drawn": 0, "not_drawn": 0, "high_index": 0, "low_index": 0} for z in TARGET_NUMBERS}
    all_metrics = {z: [] for z in TARGET_NUMBERS}

    for idx in range(start_idx, end_idx + 1):
        draw = draws[idx]
        metrics = calculate_metrics_for_date(draws, idx, TARGET_NUMBERS)

        # Welche Zahlen wurden gezogen?
        drawn_targets = [z for z in TARGET_NUMBERS if z in draw["zahlen"]]

        print(f"{draw['datum_str']:<12} | ", end="")

        for z in TARGET_NUMBERS:
            m = metrics[z]
            drawn_marker = "*" if z in draw["zahlen"] else " "

            # Statistiken sammeln
            if z in draw["zahlen"]:
                stats[z]["drawn"] += 1
            else:
                stats[z]["not_drawn"] += 1

            if m["index"] >= 2:
                stats[z]["high_index"] += 1
            elif m["index"] <= -2:
                stats[z]["low_index"] += 1

            all_metrics[z].append(m)

            print(f" {m['index']:+3d} {m['count_20']:>2d} {m['mcount_3']:>2d} {m['gap']:>3d} {m['streak']:+3d}{drawn_marker}|", end="")

        print(f"  Gezogen: {drawn_targets if drawn_targets else '-'}")

    # Zusammenfassung
    print(f"\n{'='*100}")
    print("ZUSAMMENFASSUNG PRO ZAHL")
    print(f"{'='*100}")

    total_days = end_idx - start_idx + 1
    expected_drawn = total_days * 20 / 70  # Erwartete Haeufigkeit bei Gleichverteilung

    print(f"\nTage analysiert: {total_days}")
    print(f"Erwartete Ziehungen pro Zahl (20/70): {expected_drawn:.1f}")

    print(f"\n{'Zahl':<6} {'Gezogen':<10} {'Erwartet':<10} {'Diff%':<10} {'Idx>=2':<10} {'Idx<=-2':<10} {'Avg Idx':<10}")
    print("-" * 75)

    for z in TARGET_NUMBERS:
        drawn = stats[z]["drawn"]
        diff_pct = ((drawn - expected_drawn) / expected_drawn) * 100
        high_idx = stats[z]["high_index"]
        low_idx = stats[z]["low_index"]
        avg_idx = sum(m["index"] for m in all_metrics[z]) / len(all_metrics[z]) if all_metrics[z] else 0

        print(f"{z:<6} {drawn:<10} {expected_drawn:<10.1f} {diff_pct:>+8.1f}%  {high_idx:<10} {low_idx:<10} {avg_idx:>+8.2f}")

    # Detailanalyse: Wann wurden sie gezogen vs. nicht gezogen?
    print(f"\n{'='*100}")
    print("DETAILANALYSE: Index bei Ziehung vs. Nicht-Ziehung")
    print(f"{'='*100}")

    for z in TARGET_NUMBERS:
        drawn_indices = []
        not_drawn_indices = []

        for idx in range(start_idx, end_idx + 1):
            draw = draws[idx]
            metrics = calculate_metrics_for_date(draws, idx, [z])
            m = metrics[z]

            if z in draw["zahlen"]:
                drawn_indices.append(m["index"])
            else:
                not_drawn_indices.append(m["index"])

        avg_drawn = sum(drawn_indices) / len(drawn_indices) if drawn_indices else 0
        avg_not_drawn = sum(not_drawn_indices) / len(not_drawn_indices) if not_drawn_indices else 0

        print(f"\nZahl {z}:")
        print(f"  Wenn GEZOGEN:       Avg Index = {avg_drawn:+.2f} (n={len(drawn_indices)})")
        print(f"  Wenn NICHT gezogen: Avg Index = {avg_not_drawn:+.2f} (n={len(not_drawn_indices)})")
        print(f"  Differenz:          {avg_drawn - avg_not_drawn:+.2f}")

        # Index-Verteilung bei Ziehung
        if drawn_indices:
            print(f"  Index bei Ziehung:  min={min(drawn_indices):+d}, max={max(drawn_indices):+d}")
        if not_drawn_indices:
            print(f"  Index bei Nicht-Z:  min={min(not_drawn_indices):+d}, max={max(not_drawn_indices):+d}")

    # Korrelation: Hoher Index -> Nicht gezogen?
    print(f"\n{'='*100}")
    print("KORRELATION: Hoher Index (>=2) -> Wird die Zahl korrigiert?")
    print(f"{'='*100}")

    for z in TARGET_NUMBERS:
        high_idx_drawn = 0
        high_idx_not_drawn = 0

        for idx in range(start_idx, end_idx + 1):
            draw = draws[idx]
            metrics = calculate_metrics_for_date(draws, idx, [z])
            m = metrics[z]

            if m["index"] >= 2:
                if z in draw["zahlen"]:
                    high_idx_drawn += 1
                else:
                    high_idx_not_drawn += 1

        total_high = high_idx_drawn + high_idx_not_drawn
        if total_high > 0:
            not_drawn_pct = high_idx_not_drawn / total_high * 100
            print(f"\nZahl {z} bei Index >= 2:")
            print(f"  Gezogen:       {high_idx_drawn} ({100-not_drawn_pct:.1f}%)")
            print(f"  NICHT gezogen: {high_idx_not_drawn} ({not_drawn_pct:.1f}%)")
            print(f"  Erwartung (Random): ~71.4% nicht gezogen")
            if not_drawn_pct > 75:
                print(f"  >>> KORREKTUR-EFFEKT: Haeufiger nicht gezogen als erwartet! <<<")


if __name__ == "__main__":
    main()
