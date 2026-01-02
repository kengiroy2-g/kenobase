#!/usr/bin/env python
"""
Validierung der 5 Invarianten auf ALLE historischen Jackpot-Tage.

Invarianten:
1. Ziffernprodukt mod 9 = 0
2. Genau 1 einstellige Zahl (1-9)
3. Alle 3 Drittel besetzt (1-23, 24-46, 47-70)
4. Genau 6 von 7 Dekaden besetzt
5. Genau 6 von 7 Zeilen genutzt (auf Grid)

Zusaetzlich:
- Platzierung der Zahlen in der Ziehung
- Count-Metriken pro Zahlengruppe
- 28-Ziehungen-Luecken-Hypothese
- Beliebte vs seltene Zahlen aus System-Perspektive
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from itertools import combinations
from collections import Counter, defaultdict
import json


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Lade KENO-Ziehungsdaten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df.sort_values("Datum").reset_index(drop=True)


def load_jackpot_dates(base_path: Path) -> list[dict]:
    """Lade alle Jackpot-Tage aus GQ-Daten."""
    gq_files = [
        base_path / "Keno_GPTs" / "Keno_GQ_2024.csv",
        base_path / "Keno_GPTs" / "Keno_GQ_02-2024.csv",
        base_path / "Keno_GPTs" / "Keno_GQ_2025.csv",
    ]

    all_jackpots = []
    for f in gq_files:
        if f.exists():
            df = pd.read_csv(f, encoding="utf-8")
            mask = (df["Keno-Typ"] == 10) & (df["Anzahl richtiger Zahlen"] == 10) & (df["Anzahl der Gewinner"] > 0)
            jackpots = df[mask][["Datum", "Anzahl der Gewinner"]].copy()
            for _, row in jackpots.iterrows():
                all_jackpots.append({
                    "datum_str": row["Datum"],
                    "gewinner": int(row["Anzahl der Gewinner"])
                })

    # Deduplizieren und parsen
    seen = set()
    unique = []
    for jp in all_jackpots:
        if jp["datum_str"] not in seen:
            seen.add(jp["datum_str"])
            try:
                parsed = datetime.strptime(jp["datum_str"], "%d.%m.%Y")
                jp["datum"] = parsed
                unique.append(jp)
            except:
                pass

    return sorted(unique, key=lambda x: x["datum"])


def get_draw_numbers(df: pd.DataFrame, date: datetime) -> list[int]:
    """Hole die 20 Ziehungszahlen fuer ein Datum."""
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    row = df[df["Datum"] == date]
    if len(row) > 0:
        return [int(row[col].values[0]) for col in pos_cols]
    return []


# ============================================================================
# INVARIANTEN-TESTS
# ============================================================================

def test_invariant_1_digit_product(numbers: list[int]) -> bool:
    """Ziffernprodukt mod 9 = 0"""
    prod = 1
    for n in numbers:
        for d in str(n):
            if d != '0':
                prod *= int(d)
    return prod % 9 == 0


def test_invariant_2_single_digit(numbers: list[int]) -> int:
    """Anzahl einstelliger Zahlen (1-9)"""
    return sum(1 for n in numbers if 1 <= n <= 9)


def test_invariant_3_thirds(numbers: list[int]) -> tuple[bool, bool, bool]:
    """Drittel-Abdeckung"""
    has_1_23 = any(1 <= n <= 23 for n in numbers)
    has_24_46 = any(24 <= n <= 46 for n in numbers)
    has_47_70 = any(47 <= n <= 70 for n in numbers)
    return has_1_23, has_24_46, has_47_70


def test_invariant_4_decades(numbers: list[int]) -> int:
    """Anzahl besetzter Dekaden"""
    decades = set(n // 10 for n in numbers)
    return len(decades)


def test_invariant_5_rows(numbers: list[int]) -> int:
    """Anzahl genutzter Zeilen (Grid 7x10)"""
    rows = set((n - 1) // 10 for n in numbers)
    return len(rows)


def check_all_invariants(numbers: list[int]) -> dict:
    """Pruefe alle 5 Invarianten fuer eine 10er-Kombination."""
    return {
        "inv1_digit_prod_mod9_zero": test_invariant_1_digit_product(numbers),
        "inv2_single_digit_count": test_invariant_2_single_digit(numbers),
        "inv3_thirds": test_invariant_3_thirds(numbers),
        "inv4_decades_count": test_invariant_4_decades(numbers),
        "inv5_rows_count": test_invariant_5_rows(numbers),
        "passes_all": (
            test_invariant_1_digit_product(numbers) and
            test_invariant_2_single_digit(numbers) == 1 and
            all(test_invariant_3_thirds(numbers)) and
            test_invariant_4_decades(numbers) == 6 and
            test_invariant_5_rows(numbers) == 6
        )
    }


def count_valid_combinations_in_draw(draw_20: list[int], sample_size: int = 5000) -> dict:
    """
    Zaehle wie viele der C(20,10) Kombinationen die Invarianten erfuellen.
    Bei sample_size > 0: Nur Stichprobe testen.
    """
    all_combos = list(combinations(draw_20, 10))
    total = len(all_combos)

    if sample_size > 0 and sample_size < total:
        np.random.seed(42)
        indices = np.random.choice(total, sample_size, replace=False)
        test_combos = [all_combos[i] for i in indices]
    else:
        test_combos = all_combos

    valid_count = 0
    inv1_count = 0
    inv2_count = 0
    inv3_count = 0
    inv4_count = 0
    inv5_count = 0

    for combo in test_combos:
        combo_list = list(combo)
        if test_invariant_1_digit_product(combo_list):
            inv1_count += 1
        if test_invariant_2_single_digit(combo_list) == 1:
            inv2_count += 1
        if all(test_invariant_3_thirds(combo_list)):
            inv3_count += 1
        if test_invariant_4_decades(combo_list) == 6:
            inv4_count += 1
        if test_invariant_5_rows(combo_list) == 6:
            inv5_count += 1

        result = check_all_invariants(combo_list)
        if result["passes_all"]:
            valid_count += 1

    tested = len(test_combos)
    return {
        "total_combinations": total,
        "tested": tested,
        "inv1_pass": inv1_count,
        "inv2_pass": inv2_count,
        "inv3_pass": inv3_count,
        "inv4_pass": inv4_count,
        "inv5_pass": inv5_count,
        "all_pass": valid_count,
        "inv1_rate": inv1_count / tested,
        "inv2_rate": inv2_count / tested,
        "inv3_rate": inv3_count / tested,
        "inv4_rate": inv4_count / tested,
        "inv5_rate": inv5_count / tested,
        "all_pass_rate": valid_count / tested,
    }


# ============================================================================
# PLATZIERUNG-ANALYSE
# ============================================================================

def analyze_position_patterns(df: pd.DataFrame, jackpot_dates: list[dict]) -> dict:
    """Analysiere Platzierung der Zahlen in der Ziehung."""
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Sammle Position-Statistiken fuer Jackpot-Tage
    position_stats = {i: [] for i in range(1, 21)}
    all_positions_jp = []

    for jp in jackpot_dates:
        draw = get_draw_numbers(df, jp["datum"])
        if not draw:
            continue

        for pos, num in enumerate(draw, 1):
            position_stats[pos].append(num)
            all_positions_jp.append({"pos": pos, "num": num, "datum": jp["datum_str"]})

    # Statistiken pro Position
    position_summary = {}
    for pos in range(1, 21):
        nums = position_stats[pos]
        if nums:
            position_summary[f"pos_{pos}"] = {
                "mean": round(np.mean(nums), 2),
                "std": round(np.std(nums), 2),
                "min": min(nums),
                "max": max(nums),
                "count": len(nums)
            }

    # Sind fruehe Positionen eher niedrige Zahlen?
    early_positions = []  # Pos 1-5
    late_positions = []   # Pos 16-20

    for jp in jackpot_dates:
        draw = get_draw_numbers(df, jp["datum"])
        if draw:
            early_positions.extend(draw[:5])
            late_positions.extend(draw[-5:])

    return {
        "position_summary": position_summary,
        "early_positions_mean": round(np.mean(early_positions), 2) if early_positions else 0,
        "late_positions_mean": round(np.mean(late_positions), 2) if late_positions else 0,
        "early_positions_count": len(early_positions),
        "late_positions_count": len(late_positions),
    }


# ============================================================================
# COUNT-METRIKEN PRO ZAHLENGRUPPE
# ============================================================================

def define_number_groups() -> dict[str, list[int]]:
    """Definiere Zahlengruppen."""
    return {
        "birthday": list(range(1, 32)),           # 1-31
        "lucky_numbers": [3, 7, 9, 11, 13, 17, 19, 21],
        "round_numbers": [10, 20, 30, 40, 50, 60, 70],
        "single_digit": list(range(1, 10)),       # 1-9
        "high_numbers": list(range(50, 71)),      # 50-70
        "middle_numbers": list(range(30, 50)),    # 30-49
        "palindromes": [11, 22, 33, 44, 55, 66],
        "ascending_digits": [12, 23, 34, 45, 56, 67],
        "descending_digits": [21, 32, 43, 54, 65],
        "decade_0": list(range(1, 10)),
        "decade_1": list(range(10, 20)),
        "decade_2": list(range(20, 30)),
        "decade_3": list(range(30, 40)),
        "decade_4": list(range(40, 50)),
        "decade_5": list(range(50, 60)),
        "decade_6": list(range(60, 71)),
    }


def analyze_group_counts(df: pd.DataFrame, jackpot_dates: list[dict]) -> dict:
    """Analysiere Count-Metriken pro Zahlengruppe."""
    groups = define_number_groups()
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    group_stats = {name: {"hits": 0, "expected": 0, "jackpot_hits": 0} for name in groups}

    # Gesamt-Statistiken
    total_draws = len(df)
    total_jp_draws = len(jackpot_dates)

    # Zaehle Erscheinungen in allen Ziehungen
    for _, row in df.iterrows():
        drawn = set(int(row[col]) for col in pos_cols)
        for group_name, group_nums in groups.items():
            hits = len(drawn.intersection(group_nums))
            group_stats[group_name]["hits"] += hits

    # Erwartungswert berechnen (20 aus 70)
    for group_name, group_nums in groups.items():
        # Erwartung: (Gruppengroesse / 70) * 20 * Anzahl_Ziehungen
        expected = (len(group_nums) / 70) * 20 * total_draws
        group_stats[group_name]["expected"] = round(expected, 1)
        group_stats[group_name]["size"] = len(group_nums)
        group_stats[group_name]["ratio"] = round(
            group_stats[group_name]["hits"] / max(expected, 1), 3
        )

    # Jackpot-spezifische Analyse
    for jp in jackpot_dates:
        draw = get_draw_numbers(df, jp["datum"])
        if not draw:
            continue
        drawn = set(draw)
        for group_name, group_nums in groups.items():
            hits = len(drawn.intersection(group_nums))
            group_stats[group_name]["jackpot_hits"] += hits

    # Jackpot-Ratio berechnen
    for group_name, group_nums in groups.items():
        expected_jp = (len(group_nums) / 70) * 20 * total_jp_draws
        group_stats[group_name]["jackpot_expected"] = round(expected_jp, 1)
        group_stats[group_name]["jackpot_ratio"] = round(
            group_stats[group_name]["jackpot_hits"] / max(expected_jp, 1), 3
        )

    return {
        "total_draws": total_draws,
        "total_jackpot_draws": total_jp_draws,
        "group_statistics": group_stats
    }


# ============================================================================
# 28-ZIEHUNGEN-LUECKEN-HYPOTHESE
# ============================================================================

def analyze_gap_patterns(df: pd.DataFrame) -> dict:
    """
    Analysiere Luecken zwischen Erscheinungen jeder Zahl.
    Hypothese: Maximal 28 Ziehungen Luecke.
    """
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Letzte Erscheinung jeder Zahl tracken
    last_seen = {n: -1 for n in range(1, 71)}
    gaps = {n: [] for n in range(1, 71)}

    for idx, row in df.iterrows():
        drawn = set(int(row[col]) for col in pos_cols)

        for n in range(1, 71):
            if n in drawn:
                if last_seen[n] >= 0:
                    gap = idx - last_seen[n]
                    gaps[n].append(gap)
                last_seen[n] = idx

    # Statistiken pro Zahl
    gap_stats = {}
    max_gaps = []

    for n in range(1, 71):
        if gaps[n]:
            max_gap = max(gaps[n])
            avg_gap = np.mean(gaps[n])
            gap_stats[n] = {
                "max_gap": max_gap,
                "avg_gap": round(avg_gap, 2),
                "total_appearances": len(gaps[n]) + 1,
                "exceeds_28": max_gap > 28
            }
            max_gaps.append(max_gap)

    # Globale Statistiken
    global_max = max(max_gaps) if max_gaps else 0
    exceeds_28_count = sum(1 for g in max_gaps if g > 28)

    return {
        "per_number": gap_stats,
        "global_max_gap": global_max,
        "numbers_exceeding_28": exceeds_28_count,
        "hypothesis_holds": exceeds_28_count == 0,
        "avg_max_gap": round(np.mean(max_gaps), 2) if max_gaps else 0
    }


# ============================================================================
# SYSTEM-PERSPEKTIVE: BELIEBTE VS SELTENE ZAHLEN
# ============================================================================

def analyze_system_perspective(df: pd.DataFrame, gap_analysis: dict) -> dict:
    """
    Aus der Perspektive des Systems:
    - Beliebte Zahlen = haeufig gespielt = System muss sie regelmaessig ziehen
    - Seltene Zahlen = selten gespielt = System kann laenger warten
    """
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Gesamthaeufigkeit jeder Zahl
    total_counts = Counter()
    for _, row in df.iterrows():
        drawn = [int(row[col]) for col in pos_cols]
        total_counts.update(drawn)

    # Erwartete Haeufigkeit: (20/70) * Anzahl_Ziehungen
    expected_per_number = (20 / 70) * len(df)

    # Kategorisiere Zahlen
    popular_by_system = []  # Haeufiger als erwartet UND kleine Luecken
    rare_by_system = []     # Seltener als erwartet ODER grosse Luecken

    for n in range(1, 71):
        count = total_counts.get(n, 0)
        ratio = count / expected_per_number
        max_gap = gap_analysis["per_number"].get(n, {}).get("max_gap", 0)
        avg_gap = gap_analysis["per_number"].get(n, {}).get("avg_gap", 0)

        info = {
            "number": n,
            "count": count,
            "ratio": round(ratio, 3),
            "max_gap": max_gap,
            "avg_gap": avg_gap
        }

        # System-Logik: Beliebte Zahlen werden oft gezogen, kleine Luecken
        if ratio >= 1.02 and avg_gap <= 3.5:
            popular_by_system.append(info)
        elif ratio <= 0.98 or avg_gap >= 4.0:
            rare_by_system.append(info)

    # Sortiere nach Ratio
    popular_by_system.sort(key=lambda x: -x["ratio"])
    rare_by_system.sort(key=lambda x: x["ratio"])

    # Birthday-Zahlen Analyse
    birthday_nums = set(range(1, 32))
    birthday_counts = sum(total_counts.get(n, 0) for n in birthday_nums)
    non_birthday_counts = sum(total_counts.get(n, 0) for n in range(32, 71))

    birthday_per_num = birthday_counts / 31
    non_birthday_per_num = non_birthday_counts / 39

    return {
        "expected_per_number": round(expected_per_number, 1),
        "popular_by_system": popular_by_system[:15],
        "rare_by_system": rare_by_system[:15],
        "birthday_analysis": {
            "birthday_total": birthday_counts,
            "non_birthday_total": non_birthday_counts,
            "birthday_avg": round(birthday_per_num, 2),
            "non_birthday_avg": round(non_birthday_per_num, 2),
            "birthday_ratio": round(birthday_per_num / non_birthday_per_num, 3)
        },
        "most_drawn": total_counts.most_common(10),
        "least_drawn": total_counts.most_common()[-10:]
    }


# ============================================================================
# HAUPTANALYSE
# ============================================================================

def main():
    base_path = Path(__file__).parent.parent

    print("=" * 80)
    print("VALIDIERUNG DER 5 INVARIANTEN AUF ALLE JACKPOT-TAGE")
    print("=" * 80)

    # Daten laden
    print("\nLade Daten...")
    df = load_keno_data(base_path)
    jackpot_dates = load_jackpot_dates(base_path)
    print(f"Ziehungen geladen: {len(df)}")
    print(f"Jackpot-Tage gefunden: {len(jackpot_dates)}")

    results = {
        "meta": {
            "total_draws": len(df),
            "total_jackpots": len(jackpot_dates),
            "date_range": f"{df['Datum'].min()} - {df['Datum'].max()}"
        },
        "invariant_tests": [],
        "position_analysis": {},
        "group_analysis": {},
        "gap_analysis": {},
        "system_perspective": {}
    }

    # ========================================================================
    # 1. INVARIANTEN-TESTS AUF ALLE JACKPOT-TAGE
    # ========================================================================
    print("\n" + "=" * 80)
    print("1. INVARIANTEN-TESTS AUF JACKPOT-TAGE")
    print("=" * 80)

    for jp in jackpot_dates:
        draw = get_draw_numbers(df, jp["datum"])
        if not draw:
            continue

        # Test auf den 20 gezogenen Zahlen
        combo_analysis = count_valid_combinations_in_draw(draw, sample_size=5000)

        # Test auf verifizierten Gewinner falls vorhanden
        test_result = {
            "datum": jp["datum_str"],
            "gewinner": jp["gewinner"],
            "draw_20": draw,
            "combinations_analysis": combo_analysis
        }

        results["invariant_tests"].append(test_result)

        print(f"\n{jp['datum_str']} ({jp['gewinner']} Gewinner):")
        print(f"  Inv1 (Ziffernprodukt): {combo_analysis['inv1_rate']*100:.1f}% der Kombis")
        print(f"  Inv2 (1 einstellig): {combo_analysis['inv2_rate']*100:.1f}% der Kombis")
        print(f"  Inv3 (3 Drittel): {combo_analysis['inv3_rate']*100:.1f}% der Kombis")
        print(f"  Inv4 (6 Dekaden): {combo_analysis['inv4_rate']*100:.1f}% der Kombis")
        print(f"  Inv5 (6 Zeilen): {combo_analysis['inv5_rate']*100:.1f}% der Kombis")
        print(f"  ALLE 5 erfuellt: {combo_analysis['all_pass_rate']*100:.2f}% der Kombis")

    # Aggregierte Statistiken
    inv1_rates = [t["combinations_analysis"]["inv1_rate"] for t in results["invariant_tests"]]
    inv2_rates = [t["combinations_analysis"]["inv2_rate"] for t in results["invariant_tests"]]
    inv3_rates = [t["combinations_analysis"]["inv3_rate"] for t in results["invariant_tests"]]
    inv4_rates = [t["combinations_analysis"]["inv4_rate"] for t in results["invariant_tests"]]
    inv5_rates = [t["combinations_analysis"]["inv5_rate"] for t in results["invariant_tests"]]
    all_rates = [t["combinations_analysis"]["all_pass_rate"] for t in results["invariant_tests"]]

    print("\n" + "-" * 60)
    print("AGGREGIERTE INVARIANTEN-RATEN (ueber alle Jackpot-Tage):")
    print("-" * 60)
    print(f"Inv1 (Ziffernprodukt mod 9 = 0): {np.mean(inv1_rates)*100:.1f}% (std: {np.std(inv1_rates)*100:.1f}%)")
    print(f"Inv2 (genau 1 einstellig): {np.mean(inv2_rates)*100:.1f}% (std: {np.std(inv2_rates)*100:.1f}%)")
    print(f"Inv3 (alle 3 Drittel): {np.mean(inv3_rates)*100:.1f}% (std: {np.std(inv3_rates)*100:.1f}%)")
    print(f"Inv4 (6 von 7 Dekaden): {np.mean(inv4_rates)*100:.1f}% (std: {np.std(inv4_rates)*100:.1f}%)")
    print(f"Inv5 (6 von 7 Zeilen): {np.mean(inv5_rates)*100:.1f}% (std: {np.std(inv5_rates)*100:.1f}%)")
    print(f"ALLE 5 erfuellt: {np.mean(all_rates)*100:.2f}% (std: {np.std(all_rates)*100:.2f}%)")

    results["aggregated_invariant_rates"] = {
        "inv1_mean": round(np.mean(inv1_rates), 4),
        "inv2_mean": round(np.mean(inv2_rates), 4),
        "inv3_mean": round(np.mean(inv3_rates), 4),
        "inv4_mean": round(np.mean(inv4_rates), 4),
        "inv5_mean": round(np.mean(inv5_rates), 4),
        "all_mean": round(np.mean(all_rates), 4),
    }

    # ========================================================================
    # 2. PLATZIERUNG-ANALYSE
    # ========================================================================
    print("\n" + "=" * 80)
    print("2. PLATZIERUNG DER ZAHLEN IN DER ZIEHUNG")
    print("=" * 80)

    position_analysis = analyze_position_patterns(df, jackpot_dates)
    results["position_analysis"] = position_analysis

    print(f"\nFruehe Positionen (1-5) Durchschnitt: {position_analysis['early_positions_mean']}")
    print(f"Spaete Positionen (16-20) Durchschnitt: {position_analysis['late_positions_mean']}")

    # ========================================================================
    # 3. COUNT-METRIKEN PRO ZAHLENGRUPPE
    # ========================================================================
    print("\n" + "=" * 80)
    print("3. COUNT-METRIKEN PRO ZAHLENGRUPPE")
    print("=" * 80)

    group_analysis = analyze_group_counts(df, jackpot_dates)
    results["group_analysis"] = group_analysis

    print(f"\nGesamt Ziehungen: {group_analysis['total_draws']}")
    print(f"Jackpot-Ziehungen: {group_analysis['total_jackpot_draws']}")
    print("\nGruppen-Statistiken:")
    print("-" * 60)
    print(f"{'Gruppe':<20} {'Hits':>8} {'Erwartet':>10} {'Ratio':>8} {'JP-Ratio':>10}")
    print("-" * 60)

    for group_name, stats in group_analysis["group_statistics"].items():
        print(f"{group_name:<20} {stats['hits']:>8} {stats['expected']:>10.0f} {stats['ratio']:>8.3f} {stats['jackpot_ratio']:>10.3f}")

    # ========================================================================
    # 4. 28-ZIEHUNGEN-LUECKEN-HYPOTHESE
    # ========================================================================
    print("\n" + "=" * 80)
    print("4. 28-ZIEHUNGEN-LUECKEN-HYPOTHESE")
    print("=" * 80)

    gap_analysis = analyze_gap_patterns(df)
    results["gap_analysis"] = {
        "global_max_gap": gap_analysis["global_max_gap"],
        "numbers_exceeding_28": gap_analysis["numbers_exceeding_28"],
        "hypothesis_holds": gap_analysis["hypothesis_holds"],
        "avg_max_gap": gap_analysis["avg_max_gap"]
    }

    print(f"\nGlobale maximale Luecke: {gap_analysis['global_max_gap']} Ziehungen")
    print(f"Zahlen mit Luecke > 28: {gap_analysis['numbers_exceeding_28']}")
    print(f"Hypothese (max 28) haelt: {gap_analysis['hypothesis_holds']}")
    print(f"Durchschnittliche Max-Luecke: {gap_analysis['avg_max_gap']}")

    # Top 10 Zahlen mit groessten Luecken
    sorted_by_gap = sorted(gap_analysis["per_number"].items(), key=lambda x: -x[1]["max_gap"])
    print("\nTop 10 Zahlen mit groessten Luecken:")
    for n, stats in sorted_by_gap[:10]:
        print(f"  Zahl {n:2d}: Max-Luecke {stats['max_gap']:2d}, Avg {stats['avg_gap']:.2f}")

    # ========================================================================
    # 5. SYSTEM-PERSPEKTIVE: BELIEBTE VS SELTENE ZAHLEN
    # ========================================================================
    print("\n" + "=" * 80)
    print("5. SYSTEM-PERSPEKTIVE: BELIEBTE VS SELTENE ZAHLEN")
    print("=" * 80)

    system_analysis = analyze_system_perspective(df, gap_analysis)
    results["system_perspective"] = system_analysis

    print(f"\nErwartete Erscheinungen pro Zahl: {system_analysis['expected_per_number']}")

    print("\n--- BELIEBTE ZAHLEN (aus System-Sicht) ---")
    print("Haeufig gezogen + kleine Luecken = System zieht sie regelmaessig")
    for info in system_analysis["popular_by_system"][:10]:
        print(f"  Zahl {info['number']:2d}: Count {info['count']:4d}, Ratio {info['ratio']:.3f}, Avg-Gap {info['avg_gap']:.2f}")

    print("\n--- SELTENE ZAHLEN (aus System-Sicht) ---")
    print("Seltener gezogen + groessere Luecken = weniger Spieler-Nachfrage")
    for info in system_analysis["rare_by_system"][:10]:
        print(f"  Zahl {info['number']:2d}: Count {info['count']:4d}, Ratio {info['ratio']:.3f}, Avg-Gap {info['avg_gap']:.2f}")

    print("\n--- BIRTHDAY-ZAHLEN ANALYSE ---")
    ba = system_analysis["birthday_analysis"]
    print(f"Birthday (1-31) Total: {ba['birthday_total']}, Avg: {ba['birthday_avg']}")
    print(f"Non-Birthday (32-70) Total: {ba['non_birthday_total']}, Avg: {ba['non_birthday_avg']}")
    print(f"Birthday/Non-Birthday Ratio: {ba['birthday_ratio']}")

    print("\n--- MEISTGEZOGENE ZAHLEN ---")
    for n, count in system_analysis["most_drawn"]:
        print(f"  Zahl {n:2d}: {count} Erscheinungen")

    print("\n--- SELTENSTE ZAHLEN ---")
    for n, count in system_analysis["least_drawn"]:
        print(f"  Zahl {n:2d}: {count} Erscheinungen")

    # ========================================================================
    # SPEICHERN
    # ========================================================================
    output_path = base_path / "results" / "invariant_validation_all_jackpots.json"

    # Nur serialisierbare Daten behalten
    results_clean = {
        "meta": results["meta"],
        "aggregated_invariant_rates": results["aggregated_invariant_rates"],
        "position_analysis": results["position_analysis"],
        "group_analysis": {
            "total_draws": group_analysis["total_draws"],
            "total_jackpot_draws": group_analysis["total_jackpot_draws"],
            "group_statistics": group_analysis["group_statistics"]
        },
        "gap_analysis": results["gap_analysis"],
        "system_perspective": {
            "expected_per_number": system_analysis["expected_per_number"],
            "popular_by_system": system_analysis["popular_by_system"],
            "rare_by_system": system_analysis["rare_by_system"],
            "birthday_analysis": system_analysis["birthday_analysis"],
            "most_drawn": [[n, c] for n, c in system_analysis["most_drawn"]],
            "least_drawn": [[n, c] for n, c in system_analysis["least_drawn"]]
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_clean, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # ========================================================================
    # ZUSAMMENFASSUNG
    # ========================================================================
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)

    print(f"""
INVARIANTEN-VALIDIERUNG:
- Inv1 (Ziffernprodukt mod 9 = 0): ~{np.mean(inv1_rates)*100:.0f}% der moeglichen Kombis
- Inv2 (genau 1 einstellig): ~{np.mean(inv2_rates)*100:.0f}% der moeglichen Kombis
- Inv3 (alle 3 Drittel): ~{np.mean(inv3_rates)*100:.0f}% der moeglichen Kombis
- Inv4 (6 von 7 Dekaden): ~{np.mean(inv4_rates)*100:.0f}% der moeglichen Kombis
- Inv5 (6 von 7 Zeilen): ~{np.mean(inv5_rates)*100:.0f}% der moeglichen Kombis
- ALLE 5 zusammen: ~{np.mean(all_rates)*100:.1f}% der moeglichen Kombis

28-ZIEHUNGEN-HYPOTHESE:
- Maximale Luecke: {gap_analysis['global_max_gap']} Ziehungen
- Hypothese haelt: {gap_analysis['hypothesis_holds']}

BIRTHDAY-ZAHLEN:
- Birthday/Non-Birthday Ratio: {ba['birthday_ratio']:.3f}
- Interpretation: {'Keine signifikante Differenz' if 0.95 <= ba['birthday_ratio'] <= 1.05 else 'Signifikante Differenz!'}
""")


if __name__ == "__main__":
    main()
