#!/usr/bin/env python
"""Analysiert Positions-Muster in der Original-Ziehungsreihenfolge.

Prueft:
1. Vertikale Muster: Gleiche Zahl an gleicher Position in aufeinanderfolgenden Ziehungen
2. Diagonale Muster: Zahl wandert eine Position weiter in der naechsten Ziehung
3. Anti-Diagonale: Zahl wandert eine Position zurueck
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


def analyze_vertical_matches(df: pd.DataFrame) -> dict:
    """Analysiert vertikale Matches (gleiche Position, naechster Tag)."""
    matches_by_position = defaultdict(int)
    matches_by_number = defaultdict(int)
    total_matches = 0

    for i in range(len(df) - 1):
        for pos in range(1, 21):
            col = f"Keno_Z{pos}"
            current_num = df.loc[i, col]
            next_num = df.loc[i + 1, col]

            if current_num == next_num:
                matches_by_position[pos] += 1
                matches_by_number[int(current_num)] += 1
                total_matches += 1

    # Erwartungswert bei Zufall: 20/70 = 0.2857 pro Position
    expected_per_position = (len(df) - 1) * (20 / 70)

    return {
        "total_matches": total_matches,
        "expected_total": expected_per_position * 20,
        "ratio": total_matches / (expected_per_position * 20),
        "matches_by_position": dict(matches_by_position),
        "top_numbers": dict(sorted(matches_by_number.items(), key=lambda x: -x[1])[:20]),
    }


def analyze_diagonal_matches(df: pd.DataFrame, direction: int = 1) -> dict:
    """Analysiert diagonale Matches.

    direction=1: Zahl wandert nach rechts (Z_i -> Z_(i+1))
    direction=-1: Zahl wandert nach links (Z_i -> Z_(i-1))
    """
    matches = []
    matches_by_start_pos = defaultdict(int)
    matches_by_number = defaultdict(int)

    for i in range(len(df) - 1):
        for pos in range(1, 21):
            col_current = f"Keno_Z{pos}"
            next_pos = pos + direction

            if 1 <= next_pos <= 20:
                col_next = f"Keno_Z{next_pos}"
                current_num = df.loc[i, col_current]
                next_num = df.loc[i + 1, col_next]

                if current_num == next_num:
                    matches.append({
                        "date1": df.loc[i, "Datum"],
                        "date2": df.loc[i + 1, "Datum"],
                        "number": int(current_num),
                        "pos1": pos,
                        "pos2": next_pos,
                    })
                    matches_by_start_pos[pos] += 1
                    matches_by_number[int(current_num)] += 1

    # Erwartungswert bei Zufall
    num_comparisons = (len(df) - 1) * 19  # 19 moegliche Diagonalen pro Zeile
    expected = num_comparisons * (20 / 70)

    return {
        "total_matches": len(matches),
        "expected_total": expected,
        "ratio": len(matches) / expected if expected > 0 else 0,
        "matches_by_start_position": dict(matches_by_start_pos),
        "top_numbers": dict(sorted(matches_by_number.items(), key=lambda x: -x[1])[:20]),
        "sample_matches": matches[:20],
    }


def analyze_multi_step_diagonal(df: pd.DataFrame, steps: int = 2) -> dict:
    """Analysiert Multi-Step-Diagonalen (Zahl springt mehrere Positionen)."""
    matches_by_step = {}

    for step in range(-steps, steps + 1):
        if step == 0:
            continue

        count = 0
        for i in range(len(df) - 1):
            for pos in range(1, 21):
                next_pos = pos + step
                if 1 <= next_pos <= 20:
                    col_current = f"Keno_Z{pos}"
                    col_next = f"Keno_Z{next_pos}"
                    if df.loc[i, col_current] == df.loc[i + 1, col_next]:
                        count += 1

        # Berechne verfuegbare Positionen fuer diesen Step
        if step > 0:
            num_positions = 20 - step
        else:
            num_positions = 20 + step

        expected = (len(df) - 1) * num_positions * (20 / 70)
        matches_by_step[step] = {
            "count": count,
            "expected": expected,
            "ratio": count / expected if expected > 0 else 0,
        }

    return matches_by_step


def analyze_position_correlation(df: pd.DataFrame) -> dict:
    """Analysiert Korrelation zwischen Positionen ueber Ziehungen."""
    # Fuer jede Position: Welche Zahlen erscheinen am haeufigsten?
    position_stats = {}

    for pos in range(1, 21):
        col = f"Keno_Z{pos}"
        value_counts = df[col].value_counts()

        # Erwartung: Jede Zahl sollte ~(total/70) mal erscheinen
        expected = len(df) / 70

        # Top 5 ueberdurchschnittliche Zahlen
        top_numbers = []
        for num, count in value_counts.head(10).items():
            deviation = (count - expected) / expected * 100
            if deviation > 5:  # Mehr als 5% ueber Erwartung
                top_numbers.append({
                    "number": int(num),
                    "count": int(count),
                    "expected": round(expected, 1),
                    "deviation_pct": round(deviation, 1),
                })

        position_stats[pos] = {
            "most_common": int(value_counts.index[0]),
            "most_common_count": int(value_counts.iloc[0]),
            "least_common": int(value_counts.index[-1]),
            "least_common_count": int(value_counts.iloc[-1]),
            "overrepresented": top_numbers[:5],
        }

    return position_stats


def find_repeating_sequences(df: pd.DataFrame, min_length: int = 3) -> list:
    """Findet Sequenzen wo eine Zahl mehrere Ziehungen hintereinander an aehnlicher Position bleibt."""
    sequences = []

    for pos in range(1, 21):
        col = f"Keno_Z{pos}"
        current_num = None
        start_idx = 0
        length = 0

        for i in range(len(df)):
            num = df.loc[i, col]
            if num == current_num:
                length += 1
            else:
                if length >= min_length and current_num is not None:
                    sequences.append({
                        "number": int(current_num),
                        "position": pos,
                        "start_date": df.loc[start_idx, "Datum"],
                        "end_date": df.loc[start_idx + length - 1, "Datum"],
                        "length": length,
                    })
                current_num = num
                start_idx = i
                length = 1

        # Check last sequence
        if length >= min_length:
            sequences.append({
                "number": int(current_num),
                "position": pos,
                "start_date": df.loc[start_idx, "Datum"],
                "end_date": df.loc[start_idx + length - 1, "Datum"],
                "length": length,
            })

    return sorted(sequences, key=lambda x: -x["length"])


def main():
    path = Path("Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv")

    print("=" * 70)
    print("KENOBASE - Positions-Muster Analyse (Original-Ziehungsreihenfolge)")
    print("=" * 70)

    print("\n[1] Lade Daten...")
    df = load_keno_original_order(path)
    print(f"    {len(df)} Ziehungen geladen")
    print(f"    Zeitraum: {df['Datum'].min().date()} bis {df['Datum'].max().date()}")

    # Vertikale Matches
    print("\n[2] Vertikale Matches (gleiche Position, naechster Tag)...")
    vertical = analyze_vertical_matches(df)
    print(f"    Gefunden: {vertical['total_matches']}")
    print(f"    Erwartet: {vertical['expected_total']:.0f}")
    print(f"    Ratio:    {vertical['ratio']:.3f} ({(vertical['ratio']-1)*100:+.1f}%)")

    print("\n    Top Positionen mit Matches:")
    sorted_pos = sorted(vertical['matches_by_position'].items(), key=lambda x: -x[1])
    for pos, count in sorted_pos[:5]:
        expected = (len(df) - 1) * (20 / 70)
        ratio = count / expected
        print(f"      Position {pos:2d}: {count:4d} Matches ({ratio:.2f}x Erwartung)")

    print("\n    Top Zahlen mit vertikalen Matches:")
    for num, count in list(vertical['top_numbers'].items())[:10]:
        print(f"      Zahl {num:2d}: {count:3d} mal")

    # Diagonale Matches (rechts)
    print("\n[3] Diagonale Matches (Zahl wandert nach RECHTS)...")
    diag_right = analyze_diagonal_matches(df, direction=1)
    print(f"    Gefunden: {diag_right['total_matches']}")
    print(f"    Erwartet: {diag_right['expected_total']:.0f}")
    print(f"    Ratio:    {diag_right['ratio']:.3f} ({(diag_right['ratio']-1)*100:+.1f}%)")

    # Diagonale Matches (links)
    print("\n[4] Diagonale Matches (Zahl wandert nach LINKS)...")
    diag_left = analyze_diagonal_matches(df, direction=-1)
    print(f"    Gefunden: {diag_left['total_matches']}")
    print(f"    Erwartet: {diag_left['expected_total']:.0f}")
    print(f"    Ratio:    {diag_left['ratio']:.3f} ({(diag_left['ratio']-1)*100:+.1f}%)")

    # Multi-Step Diagonalen
    print("\n[5] Multi-Step Diagonalen...")
    multi_step = analyze_multi_step_diagonal(df, steps=5)
    print(f"    {'Step':>6} {'Count':>8} {'Expected':>10} {'Ratio':>8}")
    print("    " + "-" * 40)
    for step, data in sorted(multi_step.items()):
        ratio_str = f"{data['ratio']:.3f}"
        deviation = (data['ratio'] - 1) * 100
        flag = " ***" if abs(deviation) > 5 else ""
        print(f"    {step:>+6d} {data['count']:>8d} {data['expected']:>10.0f} {ratio_str:>8}{flag}")

    # Position-Korrelation
    print("\n[6] Position-spezifische Zahlen-Praeferenzen...")
    pos_stats = analyze_position_correlation(df)
    anomalies = []
    for pos, stats in pos_stats.items():
        if stats['overrepresented']:
            for item in stats['overrepresented']:
                anomalies.append({
                    "position": pos,
                    **item
                })

    anomalies = sorted(anomalies, key=lambda x: -x['deviation_pct'])[:15]
    print(f"    {'Pos':>4} {'Zahl':>6} {'Count':>7} {'Erwartet':>9} {'Abweichung':>11}")
    print("    " + "-" * 45)
    for a in anomalies:
        print(f"    {a['position']:>4d} {a['number']:>6d} {a['count']:>7d} {a['expected']:>9.1f} {a['deviation_pct']:>+10.1f}%")

    # Wiederholende Sequenzen
    print("\n[7] Laengste Sequenzen (gleiche Zahl, gleiche Position)...")
    sequences = find_repeating_sequences(df, min_length=2)
    print(f"    Gefunden: {len(sequences)} Sequenzen mit Laenge >= 2")
    print(f"\n    Top 10 laengste Sequenzen:")
    print(f"    {'Zahl':>6} {'Pos':>5} {'Laenge':>7} {'Start':>12} {'Ende':>12}")
    print("    " + "-" * 50)
    for seq in sequences[:10]:
        print(f"    {seq['number']:>6d} {seq['position']:>5d} {seq['length']:>7d} "
              f"{str(seq['start_date'].date()):>12} {str(seq['end_date'].date()):>12}")

    # Beispiele fuer diagonale Matches zeigen
    print("\n[8] Beispiele fuer diagonale Matches (rechts)...")
    for match in diag_right['sample_matches'][:10]:
        print(f"    {match['date1'].date()}: Zahl {match['number']:2d} an Pos {match['pos1']:2d} "
              f"-> {match['date2'].date()}: Pos {match['pos2']:2d}")

    # Speichere Ergebnisse
    results = {
        "total_draws": len(df),
        "vertical_matches": {
            "total": vertical['total_matches'],
            "expected": vertical['expected_total'],
            "ratio": vertical['ratio'],
            "by_position": vertical['matches_by_position'],
            "top_numbers": vertical['top_numbers'],
        },
        "diagonal_right": {
            "total": diag_right['total_matches'],
            "expected": diag_right['expected_total'],
            "ratio": diag_right['ratio'],
        },
        "diagonal_left": {
            "total": diag_left['total_matches'],
            "expected": diag_left['expected_total'],
            "ratio": diag_left['ratio'],
        },
        "multi_step": multi_step,
        "position_anomalies": anomalies,
        "longest_sequences": [
            {**s, "start_date": str(s["start_date"].date()), "end_date": str(s["end_date"].date())}
            for s in sequences[:20]
        ],
    }

    output_path = Path("results/position_patterns.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n[9] Ergebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    v_dev = (vertical['ratio'] - 1) * 100
    dr_dev = (diag_right['ratio'] - 1) * 100
    dl_dev = (diag_left['ratio'] - 1) * 100

    print(f"\n  Vertikale Matches:     {v_dev:+.1f}% vs Erwartung")
    print(f"  Diagonale (rechts):    {dr_dev:+.1f}% vs Erwartung")
    print(f"  Diagonale (links):     {dl_dev:+.1f}% vs Erwartung")

    if abs(v_dev) > 5 or abs(dr_dev) > 5 or abs(dl_dev) > 5:
        print("\n  *** ANOMALIE GEFUNDEN! ***")
        if v_dev > 5:
            print(f"  -> Vertikale Matches sind {v_dev:.1f}% haeufiger als erwartet!")
        if dr_dev > 5:
            print(f"  -> Diagonale (rechts) sind {dr_dev:.1f}% haeufiger als erwartet!")
        if dl_dev > 5:
            print(f"  -> Diagonale (links) sind {dl_dev:.1f}% haeufiger als erwartet!")
    else:
        print("\n  Keine signifikante Anomalie in Position-Patterns gefunden.")
        print("  Die Ziehungsreihenfolge scheint zufaellig zu sein.")


if __name__ == "__main__":
    main()
