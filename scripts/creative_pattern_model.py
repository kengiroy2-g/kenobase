#!/usr/bin/env python
"""Kreatives Muster-Modell fuer KENO.

Sucht nach nicht-offensichtlichen Mustern:
1. Position-Regeln (bereits gefunden)
2. Visuelle Muster (Zahlen als 7x10 Matrix)
3. Wochentags-Muster
4. Mond-Phasen-Korrelation
5. "Luecken"-Muster (Zahlen die lange nicht kamen)
6. Nachbar-Muster (numerisch benachbarte Zahlen)
7. Summen-Muster (hohe/niedrige Summe)
8. Symmetrie-Muster
9. "Hot Zones" in der Zahlenmatrix
10. Sequenz-Erkennung
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import json
import math


def load_data(path: Path) -> pd.DataFrame:
    """Laedt KENO-Daten."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)
    return df


def get_numbers(row) -> set:
    """Extrahiert alle 20 Zahlen."""
    return set(row[f"Keno_Z{i}"] for i in range(1, 21))


def get_numbers_list(row) -> list:
    """Extrahiert alle 20 Zahlen als Liste (Originalreihenfolge)."""
    return [row[f"Keno_Z{i}"] for i in range(1, 21)]


# =============================================================================
# MUSTER 1: Visuelle Matrix (7 Spalten x 10 Reihen)
# =============================================================================
def number_to_matrix_pos(num: int) -> tuple[int, int]:
    """Konvertiert Zahl 1-70 zu Matrix-Position (row, col)."""
    # 7 Spalten, 10 Reihen
    # 1-7 = Reihe 0, 8-14 = Reihe 1, etc.
    row = (num - 1) // 7
    col = (num - 1) % 7
    return row, col


def analyze_matrix_patterns(df: pd.DataFrame) -> dict:
    """Analysiert Muster in der 7x10 Matrix-Darstellung."""

    # Zaehle wie oft jede Matrix-Position belegt ist
    position_counts = np.zeros((10, 7))

    # Zaehle Reihen und Spalten pro Ziehung
    row_counts_per_draw = []
    col_counts_per_draw = []

    # Diagonal-Muster
    diagonal_hits = defaultdict(int)

    for _, row in df.iterrows():
        nums = get_numbers(row)
        rows_hit = set()
        cols_hit = set()

        for num in nums:
            r, c = number_to_matrix_pos(num)
            position_counts[r, c] += 1
            rows_hit.add(r)
            cols_hit.add(c)

            # Diagonal-Index
            diag1 = r - c  # Haupt-Diagonale
            diag2 = r + c  # Anti-Diagonale
            diagonal_hits[f"diag1_{diag1}"] += 1
            diagonal_hits[f"diag2_{diag2}"] += 1

        row_counts_per_draw.append(len(rows_hit))
        col_counts_per_draw.append(len(cols_hit))

    # Erwartung: Jede Position sollte ~(n*20/70) mal belegt sein
    expected = len(df) * 20 / 70

    # Finde Hot Zones
    hot_zones = []
    cold_zones = []
    for r in range(10):
        for c in range(7):
            num = r * 7 + c + 1
            if num <= 70:
                deviation = (position_counts[r, c] - expected) / expected
                if deviation > 0.1:
                    hot_zones.append({
                        "number": num,
                        "row": r,
                        "col": c,
                        "count": int(position_counts[r, c]),
                        "deviation": deviation,
                    })
                elif deviation < -0.1:
                    cold_zones.append({
                        "number": num,
                        "row": r,
                        "col": c,
                        "count": int(position_counts[r, c]),
                        "deviation": deviation,
                    })

    return {
        "avg_rows_hit": np.mean(row_counts_per_draw),
        "avg_cols_hit": np.mean(col_counts_per_draw),
        "hot_zones": sorted(hot_zones, key=lambda x: -x["deviation"])[:15],
        "cold_zones": sorted(cold_zones, key=lambda x: x["deviation"])[:15],
        "top_diagonals": dict(sorted(diagonal_hits.items(), key=lambda x: -x[1])[:10]),
    }


# =============================================================================
# MUSTER 2: Wochentags-Muster
# =============================================================================
def analyze_weekday_patterns(df: pd.DataFrame) -> dict:
    """Analysiert Muster pro Wochentag."""

    weekday_numbers = defaultdict(lambda: defaultdict(int))
    weekday_counts = defaultdict(int)

    for _, row in df.iterrows():
        weekday = row["Datum"].weekday()  # 0=Montag, 6=Sonntag
        weekday_counts[weekday] += 1

        for num in get_numbers(row):
            weekday_numbers[weekday][num] += 1

    # Finde Zahlen die an bestimmten Tagen ueberdurchschnittlich sind
    weekday_favorites = {}
    weekday_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    for wd in range(7):
        if weekday_counts[wd] == 0:
            continue

        expected = weekday_counts[wd] * 20 / 70
        favorites = []

        for num in range(1, 71):
            count = weekday_numbers[wd].get(num, 0)
            if expected > 0:
                deviation = (count - expected) / expected
                if deviation > 0.15:
                    favorites.append({
                        "number": num,
                        "count": count,
                        "deviation": deviation,
                    })

        weekday_favorites[weekday_names[wd]] = sorted(favorites, key=lambda x: -x["deviation"])[:10]

    return {
        "weekday_counts": dict(weekday_counts),
        "weekday_favorites": weekday_favorites,
    }


# =============================================================================
# MUSTER 3: Luecken-Analyse (wie lange nicht gezogen)
# =============================================================================
def analyze_gap_patterns(df: pd.DataFrame) -> dict:
    """Analysiert Luecken zwischen Auftritten und ob lange Luecken vorhersagbar sind."""

    last_seen = {n: -1 for n in range(1, 71)}
    gaps = defaultdict(list)

    # Nach langer Luecke: Was kommt?
    after_long_gap = defaultdict(lambda: defaultdict(int))
    long_gap_threshold = 20  # Tage

    for idx, row in df.iterrows():
        nums = get_numbers(row)

        # Fuer jede Zahl: Berechne Luecke
        for num in range(1, 71):
            if num in nums:
                if last_seen[num] >= 0:
                    gap = idx - last_seen[num]
                    gaps[num].append(gap)

                    # Wenn lange Luecke: Was kam mit dieser Zahl?
                    if gap >= long_gap_threshold:
                        for other in nums:
                            if other != num:
                                after_long_gap[num][other] += 1

                last_seen[num] = idx

    # Statistiken pro Zahl
    gap_stats = []
    for num in range(1, 71):
        if gaps[num]:
            gap_stats.append({
                "number": num,
                "avg_gap": np.mean(gaps[num]),
                "max_gap": max(gaps[num]),
                "min_gap": min(gaps[num]),
                "std_gap": np.std(gaps[num]),
            })

    # Zahlen mit ungewoehnlich langen Luecken
    avg_overall = np.mean([s["avg_gap"] for s in gap_stats])
    irregular = [s for s in gap_stats if s["avg_gap"] > avg_overall * 1.2 or s["std_gap"] > 3]

    # Top Partner nach langer Luecke
    long_gap_partners = {}
    for num, partners in after_long_gap.items():
        if partners:
            sorted_partners = sorted(partners.items(), key=lambda x: -x[1])[:5]
            long_gap_partners[num] = sorted_partners

    return {
        "avg_gap_overall": avg_overall,
        "irregular_numbers": sorted(irregular, key=lambda x: -x["std_gap"])[:15],
        "long_gap_partners": dict(sorted(long_gap_partners.items(), key=lambda x: -sum(p[1] for p in x[1]))[:20]),
    }


# =============================================================================
# MUSTER 4: Nachbar-Muster (numerisch benachbarte Zahlen)
# =============================================================================
def analyze_neighbor_patterns(df: pd.DataFrame) -> dict:
    """Analysiert wie oft numerische Nachbarn zusammen erscheinen."""

    neighbor_pairs = defaultdict(int)
    sequence_counts = defaultdict(int)  # Laenge von Sequenzen (z.B. 5,6,7)

    for _, row in df.iterrows():
        nums = sorted(get_numbers(row))

        # Zaehle Nachbar-Paare
        for i in range(len(nums) - 1):
            if nums[i + 1] - nums[i] == 1:
                neighbor_pairs[(nums[i], nums[i + 1])] += 1

        # Zaehle Sequenzen
        seq_len = 1
        for i in range(len(nums) - 1):
            if nums[i + 1] - nums[i] == 1:
                seq_len += 1
            else:
                if seq_len >= 2:
                    sequence_counts[seq_len] += 1
                seq_len = 1
        if seq_len >= 2:
            sequence_counts[seq_len] += 1

    # Erwartung fuer Nachbar-Paare: ~(n * C(20,2) * 2/69) / 69
    # Vereinfacht: Etwa 55 mal pro Paar bei 2242 Ziehungen
    expected_pair = len(df) * (20 * 19 / 2) * (1 / 69) / 69

    # Ueberdurchschnittliche Paare
    hot_pairs = []
    for pair, count in neighbor_pairs.items():
        deviation = (count - expected_pair) / expected_pair if expected_pair > 0 else 0
        if deviation > 0.2:
            hot_pairs.append({
                "pair": pair,
                "count": count,
                "deviation": deviation,
            })

    return {
        "top_neighbor_pairs": sorted(neighbor_pairs.items(), key=lambda x: -x[1])[:20],
        "hot_neighbor_pairs": sorted(hot_pairs, key=lambda x: -x["deviation"])[:15],
        "sequence_distribution": dict(sorted(sequence_counts.items())),
        "avg_sequences_per_draw": sum(sequence_counts.values()) / len(df),
    }


# =============================================================================
# MUSTER 5: Summen-Muster
# =============================================================================
def analyze_sum_patterns(df: pd.DataFrame) -> dict:
    """Analysiert Summen-Muster und was nach bestimmten Summen kommt."""

    sums = []
    sum_to_next = defaultdict(list)  # Summe heute -> Zahlen morgen

    for idx, row in df.iterrows():
        nums = get_numbers(row)
        total = sum(nums)
        sums.append(total)

        # Was kommt nach dieser Summe?
        if idx + 1 < len(df):
            next_nums = get_numbers(df.loc[idx + 1])

            # Kategorisiere Summe
            if total < 680:
                cat = "low"
            elif total > 740:
                cat = "high"
            else:
                cat = "mid"

            for n in next_nums:
                sum_to_next[cat].append(n)

    # Zahlen die nach hoher/niedriger Summe wahrscheinlicher sind
    sum_favorites = {}
    for cat in ["low", "mid", "high"]:
        counts = defaultdict(int)
        for n in sum_to_next[cat]:
            counts[n] += 1

        total_cat = len(sum_to_next[cat])
        expected = total_cat / 70

        favorites = []
        for num, count in counts.items():
            deviation = (count - expected) / expected if expected > 0 else 0
            if deviation > 0.1:
                favorites.append({"number": num, "count": count, "deviation": deviation})

        sum_favorites[cat] = sorted(favorites, key=lambda x: -x["deviation"])[:10]

    return {
        "avg_sum": np.mean(sums),
        "std_sum": np.std(sums),
        "min_sum": min(sums),
        "max_sum": max(sums),
        "sum_favorites": sum_favorites,
    }


# =============================================================================
# MUSTER 6: Symmetrie-Muster (Zahlen + Komplement = 71)
# =============================================================================
def analyze_symmetry_patterns(df: pd.DataFrame) -> dict:
    """Analysiert Symmetrie-Muster (Zahl X und 71-X)."""

    symmetric_pairs = defaultdict(int)

    for _, row in df.iterrows():
        nums = get_numbers(row)

        # Finde symmetrische Paare in derselben Ziehung
        for num in nums:
            complement = 71 - num
            if complement in nums and complement > num:
                symmetric_pairs[(num, complement)] += 1

    # Erwartung: ~(n * C(20,2) * 1/69) / 35
    expected = len(df) * (20 * 19 / 2) / (70 * 69 / 2) * 35

    return {
        "top_symmetric_pairs": dict(sorted(symmetric_pairs.items(), key=lambda x: -x[1])[:20]),
        "total_symmetric_occurrences": sum(symmetric_pairs.values()),
        "expected_symmetric": expected,
    }


# =============================================================================
# MUSTER 7: Erste/Letzte Zahl Muster
# =============================================================================
def analyze_first_last_patterns(df: pd.DataFrame) -> dict:
    """Analysiert Muster der ersten und letzten gezogenen Zahl."""

    first_to_next_first = defaultdict(int)
    last_to_next = defaultdict(lambda: defaultdict(int))

    first_numbers = []
    last_numbers = []

    for idx, row in df.iterrows():
        nums = get_numbers_list(row)
        first = nums[0]
        last = nums[-1]

        first_numbers.append(first)
        last_numbers.append(last)

        if idx + 1 < len(df):
            next_nums = get_numbers(df.loc[idx + 1])
            next_first = df.loc[idx + 1, "Keno_Z1"]

            first_to_next_first[(first, next_first)] += 1

            for n in next_nums:
                last_to_next[last][n] += 1

    # Top erste Zahl Sequenzen
    top_first_sequences = sorted(first_to_next_first.items(), key=lambda x: -x[1])[:20]

    # Wenn letzte Zahl X, was kommt morgen?
    last_to_next_favorites = {}
    for last_num, next_counts in last_to_next.items():
        total = sum(next_counts.values())
        expected = total / 70
        favorites = []
        for num, count in next_counts.items():
            deviation = (count - expected) / expected if expected > 0 else 0
            if deviation > 0.2:
                favorites.append({"number": num, "deviation": deviation})
        if favorites:
            last_to_next_favorites[last_num] = sorted(favorites, key=lambda x: -x["deviation"])[:5]

    return {
        "most_common_first": pd.Series(first_numbers).value_counts().head(10).to_dict(),
        "most_common_last": pd.Series(last_numbers).value_counts().head(10).to_dict(),
        "top_first_sequences": top_first_sequences,
        "last_to_next_favorites": dict(sorted(last_to_next_favorites.items(), key=lambda x: -len(x[1]))[:15]),
    }


# =============================================================================
# MUSTER 8: Dekaden-Balance
# =============================================================================
def analyze_decade_patterns(df: pd.DataFrame) -> dict:
    """Analysiert Balance zwischen Dekaden und Muster."""

    decade_distributions = []
    decade_to_next = defaultdict(lambda: defaultdict(int))

    for idx, row in df.iterrows():
        nums = get_numbers(row)

        # Zaehle pro Dekade (1-10, 11-20, ..., 61-70)
        decade_counts = [0] * 7
        for num in nums:
            decade = (num - 1) // 10
            decade_counts[decade] += 1

        decade_distributions.append(tuple(decade_counts))

        # Dominant Decade -> Was kommt morgen?
        dominant = decade_counts.index(max(decade_counts))
        if idx + 1 < len(df):
            next_nums = get_numbers(df.loc[idx + 1])
            for n in next_nums:
                decade_to_next[dominant][n] += 1

    # Haeufigste Dekaden-Verteilungen
    dist_counts = defaultdict(int)
    for dist in decade_distributions:
        dist_counts[dist] += 1

    # Nach dominanter Dekade: Welche Zahlen wahrscheinlicher?
    decade_favorites = {}
    for decade, next_counts in decade_to_next.items():
        total = sum(next_counts.values())
        expected = total / 70
        favorites = []
        for num, count in next_counts.items():
            deviation = (count - expected) / expected if expected > 0 else 0
            if deviation > 0.1:
                favorites.append({"number": num, "deviation": deviation})
        decade_favorites[f"decade_{decade}"] = sorted(favorites, key=lambda x: -x["deviation"])[:10]

    return {
        "top_distributions": sorted(dist_counts.items(), key=lambda x: -x[1])[:10],
        "decade_favorites": decade_favorites,
    }


# =============================================================================
# MUSTER 9: Wiederholungs-Muster (gleiche Zahl erscheint wieder)
# =============================================================================
def analyze_repeat_patterns(df: pd.DataFrame) -> dict:
    """Analysiert Muster wenn eine Zahl am naechsten Tag wieder erscheint."""

    repeat_count = 0
    repeat_partners = defaultdict(lambda: defaultdict(int))
    no_repeat_partners = defaultdict(lambda: defaultdict(int))

    for idx in range(len(df) - 1):
        today = get_numbers(df.loc[idx])
        tomorrow = get_numbers(df.loc[idx + 1])

        repeats = today & tomorrow
        repeat_count += len(repeats)

        # Wenn Zahl wiederholt: Was kommt noch?
        for rep in repeats:
            for other in tomorrow:
                if other != rep:
                    repeat_partners[rep][other] += 1

        # Wenn Zahl NICHT wiederholt: Was kommt stattdessen?
        non_repeats = today - tomorrow
        for nr in non_repeats:
            for other in tomorrow:
                no_repeat_partners[nr][other] += 1

    # Top Partner bei Wiederholung
    repeat_favorites = {}
    for num, partners in repeat_partners.items():
        if sum(partners.values()) > 10:
            sorted_p = sorted(partners.items(), key=lambda x: -x[1])[:5]
            repeat_favorites[num] = sorted_p

    return {
        "avg_repeats_per_day": repeat_count / (len(df) - 1),
        "expected_repeats": 20 * 20 / 70,
        "top_repeat_partners": dict(sorted(repeat_favorites.items(), key=lambda x: -sum(p[1] for p in x[1]))[:20]),
    }


# =============================================================================
# KOMBINIERTES MODELL
# =============================================================================
def build_combined_model(df: pd.DataFrame, all_patterns: dict) -> dict:
    """Baut kombiniertes Vorhersage-Modell aus allen Mustern."""

    # Lade Position-Regeln
    position_rules_path = Path("results/position_predictive.json")
    position_rules = {}
    if position_rules_path.exists():
        with open(position_rules_path, "r", encoding="utf-8") as f:
            position_rules = json.load(f)

    # Score pro Zahl basierend auf allen Mustern
    number_scores = {n: 0.0 for n in range(1, 71)}

    # 1. Hot Zones (Matrix)
    for hz in all_patterns["matrix"]["hot_zones"]:
        number_scores[hz["number"]] += hz["deviation"] * 10
    for cz in all_patterns["matrix"]["cold_zones"]:
        number_scores[cz["number"]] += cz["deviation"] * 10  # Negativ!

    # 2. Gap-Analyse: Zahlen mit hoher Variabilitaet
    for irr in all_patterns["gaps"]["irregular_numbers"]:
        number_scores[irr["number"]] += irr["std_gap"] * 2

    # 3. Hot Neighbor Pairs
    for pair_info in all_patterns["neighbors"]["hot_neighbor_pairs"]:
        for num in pair_info["pair"]:
            number_scores[num] += pair_info["deviation"] * 5

    # 4. Position-Praeferenzen (aus vorheriger Analyse)
    for pref in position_rules.get("top_preferences", []):
        if pref["deviation"] > 0:
            number_scores[pref["number"]] += pref["deviation"] * 8

    # Sortiere nach Score
    ranked_numbers = sorted(number_scores.items(), key=lambda x: -x[1])

    # Baue finale Regeln
    combined_rules = {
        "top_numbers": [{"number": n, "score": round(s, 2)} for n, s in ranked_numbers[:20]],
        "exclusion_rules": position_rules.get("backtest", {}).get("top_rules", [])[:10],
        "patterns_used": list(all_patterns.keys()),
    }

    return combined_rules


def main():
    path = Path("Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv")

    print("=" * 70)
    print("KENOBASE - Kreatives Muster-Modell")
    print("=" * 70)

    print("\n[1] Lade Daten...")
    df = load_data(path)
    print(f"    {len(df)} Ziehungen")

    all_patterns = {}

    # Matrix-Muster
    print("\n[2] Analysiere Matrix-Muster (7x10 Visualisierung)...")
    all_patterns["matrix"] = analyze_matrix_patterns(df)
    print(f"    Avg Reihen belegt: {all_patterns['matrix']['avg_rows_hit']:.1f}")
    print(f"    Avg Spalten belegt: {all_patterns['matrix']['avg_cols_hit']:.1f}")
    print(f"    Hot Zones: {len(all_patterns['matrix']['hot_zones'])}")
    print(f"    Cold Zones: {len(all_patterns['matrix']['cold_zones'])}")

    if all_patterns['matrix']['hot_zones']:
        print(f"\n    Top 5 Hot Zones:")
        for hz in all_patterns['matrix']['hot_zones'][:5]:
            print(f"      Zahl {hz['number']:2d} (Reihe {hz['row']}, Spalte {hz['col']}): {hz['deviation']*100:+.1f}%")

    # Wochentags-Muster
    print("\n[3] Analysiere Wochentags-Muster...")
    all_patterns["weekday"] = analyze_weekday_patterns(df)
    for day, favs in all_patterns["weekday"]["weekday_favorites"].items():
        if favs:
            nums = [f["number"] for f in favs[:3]]
            print(f"    {day}: Favoriten {nums}")

    # Luecken-Muster
    print("\n[4] Analysiere Luecken-Muster...")
    all_patterns["gaps"] = analyze_gap_patterns(df)
    print(f"    Durchschnittliche Luecke: {all_patterns['gaps']['avg_gap_overall']:.1f} Tage")
    print(f"    Zahlen mit unregelmaessigem Verhalten: {len(all_patterns['gaps']['irregular_numbers'])}")

    if all_patterns['gaps']['long_gap_partners']:
        print(f"\n    Nach langer Luecke - Top Partner:")
        for num, partners in list(all_patterns['gaps']['long_gap_partners'].items())[:5]:
            partner_nums = [p[0] for p in partners[:3]]
            print(f"      Zahl {num} -> oft mit {partner_nums}")

    # Nachbar-Muster
    print("\n[5] Analysiere Nachbar-Muster...")
    all_patterns["neighbors"] = analyze_neighbor_patterns(df)
    print(f"    Avg Sequenzen pro Ziehung: {all_patterns['neighbors']['avg_sequences_per_draw']:.2f}")
    print(f"    Top Nachbar-Paare: {all_patterns['neighbors']['top_neighbor_pairs'][:5]}")

    # Summen-Muster
    print("\n[6] Analysiere Summen-Muster...")
    all_patterns["sums"] = analyze_sum_patterns(df)
    print(f"    Avg Summe: {all_patterns['sums']['avg_sum']:.0f} (Std: {all_patterns['sums']['std_sum']:.0f})")
    print(f"    Range: {all_patterns['sums']['min_sum']} - {all_patterns['sums']['max_sum']}")

    for cat in ["low", "high"]:
        if all_patterns['sums']['sum_favorites'].get(cat):
            nums = [f["number"] for f in all_patterns['sums']['sum_favorites'][cat][:5]]
            print(f"    Nach {cat} Summe wahrscheinlicher: {nums}")

    # Symmetrie-Muster
    print("\n[7] Analysiere Symmetrie-Muster...")
    all_patterns["symmetry"] = analyze_symmetry_patterns(df)
    top_sym = list(all_patterns['symmetry']['top_symmetric_pairs'].items())[:5]
    print(f"    Top symmetrische Paare (X + Y = 71):")
    for pair, count in top_sym:
        print(f"      {pair}: {count}x")

    # Erste/Letzte Muster
    print("\n[8] Analysiere Erste/Letzte Zahl Muster...")
    all_patterns["first_last"] = analyze_first_last_patterns(df)
    print(f"    Haeufigste erste Zahlen: {list(all_patterns['first_last']['most_common_first'].keys())[:5]}")
    print(f"    Haeufigste letzte Zahlen: {list(all_patterns['first_last']['most_common_last'].keys())[:5]}")

    # Dekaden-Muster
    print("\n[9] Analysiere Dekaden-Muster...")
    all_patterns["decades"] = analyze_decade_patterns(df)
    top_dists = all_patterns['decades']['top_distributions'][:3]
    print(f"    Haeufigste Dekaden-Verteilungen:")
    for dist, count in top_dists:
        print(f"      {dist}: {count}x")

    # Wiederholungs-Muster
    print("\n[10] Analysiere Wiederholungs-Muster...")
    all_patterns["repeats"] = analyze_repeat_patterns(df)
    print(f"    Avg Wiederholungen/Tag: {all_patterns['repeats']['avg_repeats_per_day']:.2f}")
    print(f"    Erwartet: {all_patterns['repeats']['expected_repeats']:.2f}")

    # Kombiniertes Modell
    print("\n[11] Baue kombiniertes Modell...")
    combined = build_combined_model(df, all_patterns)

    print(f"\n    TOP 20 ZAHLEN (kombinierter Score):")
    print(f"    {'Rang':>4} {'Zahl':>6} {'Score':>8}")
    print("    " + "-" * 25)
    for i, item in enumerate(combined['top_numbers'], 1):
        print(f"    {i:>4d} {item['number']:>6d} {item['score']:>8.2f}")

    # Speichere alles
    output = {
        "generated_at": datetime.now().isoformat(),
        "n_draws": len(df),
        "patterns": all_patterns,
        "combined_model": combined,
    }

    # Convert numpy/pandas types
    def convert_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(i) for i in obj]
        elif isinstance(obj, tuple):
            return tuple(convert_types(i) for i in obj)
        return obj

    output = convert_types(output)

    output_path = Path("results/creative_patterns.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n[12] Ergebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("KREATIVE MUSTER - ZUSAMMENFASSUNG")
    print("=" * 70)

    print(f"""
    Matrix Hot Zones:           {len(all_patterns['matrix']['hot_zones'])} Zahlen
    Wochentags-Favoriten:       {sum(len(v) for v in all_patterns['weekday']['weekday_favorites'].values())} Zahlen
    Unregelmaessige Zahlen:     {len(all_patterns['gaps']['irregular_numbers'])}
    Hot Neighbor Pairs:         {len(all_patterns['neighbors']['hot_neighbor_pairs'])}
    Symmetrie-Anomalien:        {len(all_patterns['symmetry']['top_symmetric_pairs'])}

    TOP 10 ZAHLEN NACH KOMBINIERTEM SCORE:
    {[item['number'] for item in combined['top_numbers'][:10]]}
    """)


if __name__ == "__main__":
    main()
