#!/usr/bin/env python
"""Analysiert Positions-Muster in der Original-Ziehungsreihenfolge - KORRIGIERTE VERSION.

Korrekte Wahrscheinlichkeitsberechnung:
- Bei KENO werden 20 aus 70 Zahlen gezogen
- Wahrscheinlichkeit dass Zahl X (die heute an Pos i ist) morgen WIEDER gezogen wird: 20/70
- Wahrscheinlichkeit dass X morgen an DERSELBEN Position i ist: (20/70) * (1/20) = 1/70

Also: Erwartete Matches = (n-1) * 20 Positionen * (1/70) = (n-1) * 20/70
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import json


def load_keno_original_order(path: Path) -> pd.DataFrame:
    """Laedt KENO-Daten in Original-Ziehungsreihenfolge."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)
    return df


def analyze_vertical_matches_corrected(df: pd.DataFrame) -> dict:
    """Analysiert vertikale Matches mit KORREKTER Erwartung."""
    matches_by_position = defaultdict(int)
    matches_by_number = defaultdict(int)
    total_matches = 0
    match_examples = []

    n_draws = len(df)

    for i in range(n_draws - 1):
        for pos in range(1, 21):
            col = f"Keno_Z{pos}"
            current_num = df.loc[i, col]
            next_num = df.loc[i + 1, col]

            if current_num == next_num:
                matches_by_position[pos] += 1
                matches_by_number[int(current_num)] += 1
                total_matches += 1

                if len(match_examples) < 30:
                    match_examples.append({
                        "date1": df.loc[i, "Datum"],
                        "date2": df.loc[i + 1, "Datum"],
                        "position": pos,
                        "number": int(current_num),
                    })

    # KORREKTE Erwartung: (n-1) * 20 * (1/70)
    # Eine Zahl an Position i hat 1/70 Chance morgen an derselben Position zu sein
    expected_total = (n_draws - 1) * 20 * (1 / 70)
    expected_per_position = (n_draws - 1) * (1 / 70)

    return {
        "total_matches": total_matches,
        "expected_total": expected_total,
        "ratio": total_matches / expected_total if expected_total > 0 else 0,
        "deviation_pct": (total_matches / expected_total - 1) * 100 if expected_total > 0 else 0,
        "expected_per_position": expected_per_position,
        "matches_by_position": dict(matches_by_position),
        "top_numbers": dict(sorted(matches_by_number.items(), key=lambda x: -x[1])[:20]),
        "examples": match_examples,
    }


def analyze_diagonal_corrected(df: pd.DataFrame, direction: int = 1) -> dict:
    """Analysiert diagonale Matches mit KORREKTER Erwartung."""
    matches = []
    total = 0

    for i in range(len(df) - 1):
        for pos in range(1, 21):
            next_pos = pos + direction
            if 1 <= next_pos <= 20:
                col_current = f"Keno_Z{pos}"
                col_next = f"Keno_Z{next_pos}"
                current_num = df.loc[i, col_current]
                next_num = df.loc[i + 1, col_next]

                if current_num == next_num:
                    total += 1
                    if len(matches) < 20:
                        matches.append({
                            "date1": df.loc[i, "Datum"],
                            "date2": df.loc[i + 1, "Datum"],
                            "number": int(current_num),
                            "pos1": pos,
                            "pos2": next_pos,
                        })

    # Anzahl moeglicher Vergleiche: (n-1) * 19 (eine Position weniger am Rand)
    n_comparisons = (len(df) - 1) * 19

    # Erwartung: Jeder Vergleich hat 1/70 Chance auf Match
    expected = n_comparisons * (1 / 70)

    return {
        "total_matches": total,
        "expected": expected,
        "ratio": total / expected if expected > 0 else 0,
        "deviation_pct": (total / expected - 1) * 100 if expected > 0 else 0,
        "examples": matches,
    }


def analyze_same_number_any_position(df: pd.DataFrame) -> dict:
    """Analysiert ob eine Zahl von heute in der NAECHSTEN Ziehung irgendwo erscheint."""
    matches_count = []

    for i in range(len(df) - 1):
        today_numbers = set()
        tomorrow_numbers = set()

        for pos in range(1, 21):
            today_numbers.add(df.loc[i, f"Keno_Z{pos}"])
            tomorrow_numbers.add(df.loc[i + 1, f"Keno_Z{pos}"])

        overlap = len(today_numbers & tomorrow_numbers)
        matches_count.append(overlap)

    # Erwartung: 20 * 20 / 70 = 5.71 gemeinsame Zahlen
    expected = 20 * 20 / 70

    avg_overlap = np.mean(matches_count)

    return {
        "avg_overlap": avg_overlap,
        "expected_overlap": expected,
        "ratio": avg_overlap / expected,
        "deviation_pct": (avg_overlap / expected - 1) * 100,
        "min_overlap": min(matches_count),
        "max_overlap": max(matches_count),
        "std_overlap": np.std(matches_count),
    }


def analyze_position_preferences(df: pd.DataFrame) -> dict:
    """Welche Zahlen bevorzugen welche Positionen?"""
    position_number_counts = defaultdict(lambda: defaultdict(int))

    for _, row in df.iterrows():
        for pos in range(1, 21):
            num = row[f"Keno_Z{pos}"]
            position_number_counts[pos][num] += 1

    # Erwartung: Jede Zahl sollte ~(n/70) mal an jeder Position erscheinen
    expected = len(df) / 70

    anomalies = []

    for pos in range(1, 21):
        for num, count in position_number_counts[pos].items():
            deviation = (count - expected) / expected * 100
            if abs(deviation) > 30:  # Mehr als 30% Abweichung
                anomalies.append({
                    "position": pos,
                    "number": int(num),
                    "count": count,
                    "expected": round(expected, 1),
                    "deviation_pct": round(deviation, 1),
                })

    return {
        "expected_per_position": expected,
        "anomalies": sorted(anomalies, key=lambda x: -abs(x["deviation_pct"])),
    }


def analyze_number_position_drift(df: pd.DataFrame, target_number: int) -> dict:
    """Analysiert wie eine bestimmte Zahl sich durch die Positionen bewegt."""
    positions_over_time = []

    for i, row in df.iterrows():
        for pos in range(1, 21):
            if row[f"Keno_Z{pos}"] == target_number:
                positions_over_time.append({
                    "draw_index": i,
                    "date": row["Datum"],
                    "position": pos,
                })
                break  # Nur erste Position pro Ziehung

    # Analysiere Position-zu-Position Sprünge
    position_jumps = []
    for i in range(len(positions_over_time) - 1):
        jump = positions_over_time[i + 1]["position"] - positions_over_time[i]["position"]
        position_jumps.append(jump)

    return {
        "number": target_number,
        "appearances": len(positions_over_time),
        "avg_position": np.mean([p["position"] for p in positions_over_time]) if positions_over_time else 0,
        "position_std": np.std([p["position"] for p in positions_over_time]) if positions_over_time else 0,
        "avg_jump": np.mean(position_jumps) if position_jumps else 0,
        "jump_std": np.std(position_jumps) if position_jumps else 0,
    }


def main():
    path = Path("Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv")

    print("=" * 70)
    print("KENOBASE - Positions-Muster Analyse V2 (KORRIGIERT)")
    print("=" * 70)

    print("\n[1] Lade Daten...")
    df = load_keno_original_order(path)
    n = len(df)
    print(f"    {n} Ziehungen geladen")

    # Vertikale Matches (korrigiert)
    print("\n[2] Vertikale Matches (gleiche Zahl, gleiche Position, naechster Tag)...")
    vertical = analyze_vertical_matches_corrected(df)
    print(f"    Gefunden:  {vertical['total_matches']}")
    print(f"    Erwartet:  {vertical['expected_total']:.1f}")
    print(f"    Ratio:     {vertical['ratio']:.3f}")
    print(f"    Abweichung: {vertical['deviation_pct']:+.1f}%")

    print(f"\n    Pro Position (erwartet: {vertical['expected_per_position']:.1f}):")
    sorted_pos = sorted(vertical['matches_by_position'].items(), key=lambda x: -x[1])
    for pos, count in sorted_pos[:5]:
        ratio = count / vertical['expected_per_position']
        print(f"      Pos {pos:2d}: {count:3d} ({ratio:.2f}x)")

    print(f"\n    Beispiele:")
    for ex in vertical['examples'][:5]:
        print(f"      {ex['date1'].date()} -> {ex['date2'].date()}: "
              f"Zahl {ex['number']:2d} an Position {ex['position']}")

    # Diagonale Matches (korrigiert)
    print("\n[3] Diagonale Matches (Zahl wandert eine Position)...")
    diag_right = analyze_diagonal_corrected(df, direction=1)
    diag_left = analyze_diagonal_corrected(df, direction=-1)

    print(f"    Nach RECHTS: {diag_right['total_matches']} gefunden, "
          f"{diag_right['expected']:.1f} erwartet ({diag_right['deviation_pct']:+.1f}%)")
    print(f"    Nach LINKS:  {diag_left['total_matches']} gefunden, "
          f"{diag_left['expected']:.1f} erwartet ({diag_left['deviation_pct']:+.1f}%)")

    # Overlap zwischen Tagen
    print("\n[4] Zahlen-Overlap zwischen aufeinanderfolgenden Ziehungen...")
    overlap = analyze_same_number_any_position(df)
    print(f"    Durchschnitt:  {overlap['avg_overlap']:.2f} gemeinsame Zahlen")
    print(f"    Erwartet:      {overlap['expected_overlap']:.2f}")
    print(f"    Ratio:         {overlap['ratio']:.3f}")
    print(f"    Abweichung:    {overlap['deviation_pct']:+.1f}%")
    print(f"    Min/Max:       {overlap['min_overlap']} / {overlap['max_overlap']}")

    # Position-Praeferenzen
    print("\n[5] Zahlen mit starker Position-Praeferenz (>30% Abweichung)...")
    prefs = analyze_position_preferences(df)
    print(f"    {len(prefs['anomalies'])} Anomalien gefunden")

    print(f"\n    Top 15 Anomalien:")
    print(f"    {'Pos':>4} {'Zahl':>6} {'Count':>7} {'Erwartet':>9} {'Abweichung':>11}")
    print("    " + "-" * 45)
    for a in prefs['anomalies'][:15]:
        print(f"    {a['position']:>4d} {a['number']:>6d} {a['count']:>7d} "
              f"{a['expected']:>9.1f} {a['deviation_pct']:>+10.1f}%")

    # Positions-Drift fuer Top-Zahlen
    print("\n[6] Positions-Drift fuer ausgewaehlte Zahlen...")
    target_numbers = [49, 3, 9, 33, 50, 38, 61]  # Unsere Kern-Zahlen + Anomalien
    print(f"    {'Zahl':>6} {'Erschein.':>10} {'Avg Pos':>8} {'Pos Std':>8} {'Avg Jump':>9}")
    print("    " + "-" * 50)
    for num in target_numbers:
        drift = analyze_number_position_drift(df, num)
        print(f"    {drift['number']:>6d} {drift['appearances']:>10d} "
              f"{drift['avg_position']:>8.1f} {drift['position_std']:>8.1f} "
              f"{drift['avg_jump']:>+9.2f}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    print(f"""
    Vertikale Matches:     {vertical['deviation_pct']:+.1f}% vs Erwartung
    Diagonale (rechts):    {diag_right['deviation_pct']:+.1f}% vs Erwartung
    Diagonale (links):     {diag_left['deviation_pct']:+.1f}% vs Erwartung
    Zahlen-Overlap:        {overlap['deviation_pct']:+.1f}% vs Erwartung
    """)

    # Interpretation
    if abs(vertical['deviation_pct']) < 10:
        print("    Die Ziehungsreihenfolge zeigt KEINE signifikante Anomalie")
        print("    bei vertikalen/diagonalen Matches.")
    else:
        print("    *** SIGNIFIKANTE ANOMALIE bei Positions-Matches! ***")

    if len(prefs['anomalies']) > 0:
        print(f"\n    ABER: {len(prefs['anomalies'])} Position-Praeferenzen gefunden!")
        print("    Bestimmte Zahlen erscheinen haeufiger an bestimmten Positionen.")
        print("\n    Top 5 Position-Praeferenzen:")
        for a in prefs['anomalies'][:5]:
            print(f"      Zahl {a['number']:2d} bevorzugt Position {a['position']:2d} ({a['deviation_pct']:+.1f}%)")

    # Speichere Ergebnisse
    results = {
        "n_draws": n,
        "vertical_matches": {
            "found": vertical['total_matches'],
            "expected": vertical['expected_total'],
            "deviation_pct": vertical['deviation_pct'],
        },
        "diagonal_right": {
            "found": diag_right['total_matches'],
            "expected": diag_right['expected'],
            "deviation_pct": diag_right['deviation_pct'],
        },
        "diagonal_left": {
            "found": diag_left['total_matches'],
            "expected": diag_left['expected'],
            "deviation_pct": diag_left['deviation_pct'],
        },
        "overlap": overlap,
        "position_preferences": prefs['anomalies'][:30],
    }

    output_path = Path("results/position_patterns_v2.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n[7] Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
