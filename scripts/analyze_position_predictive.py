#!/usr/bin/env python
"""Analysiert ob Position-Praeferenzen praediktiv nutzbar sind.

Untersucht:
1. Wenn Zahl X an bevorzugter Position Y erscheint - was passiert am naechsten Tag?
2. Welche Zahlen erscheinen NICHT wenn bestimmte Muster auftreten?
3. Kontext-Analyse: Tage davor und danach
4. Backtest der praediktiven Erkenntnisse
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import json
from typing import Optional
from datetime import timedelta


def load_data(path: Path) -> pd.DataFrame:
    """Laedt KENO-Daten."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)
    return df


def get_all_numbers(row, as_set: bool = True):
    """Extrahiert alle 20 Zahlen aus einer Zeile."""
    nums = [row[f"Keno_Z{i}"] for i in range(1, 21)]
    return set(nums) if as_set else nums


def identify_position_preferences(df: pd.DataFrame, threshold: float = 0.3) -> list[dict]:
    """Identifiziert signifikante Position-Praeferenzen."""
    expected = len(df) / 70
    preferences = []

    for pos in range(1, 21):
        col = f"Keno_Z{pos}"
        counts = df[col].value_counts()

        for num, count in counts.items():
            deviation = (count - expected) / expected
            if abs(deviation) > threshold:
                preferences.append({
                    "number": int(num),
                    "position": pos,
                    "count": int(count),
                    "expected": expected,
                    "deviation": deviation,
                    "is_positive": deviation > 0,
                })

    return sorted(preferences, key=lambda x: -abs(x["deviation"]))


def analyze_context_around_pattern(
    df: pd.DataFrame,
    number: int,
    position: int,
    days_before: int = 3,
    days_after: int = 3,
) -> dict:
    """Analysiert Kontext um ein bestimmtes Muster herum."""

    # Finde alle Indizes wo Zahl an dieser Position erscheint
    col = f"Keno_Z{position}"
    pattern_indices = df[df[col] == number].index.tolist()

    # Sammle Zahlen vor und nach dem Muster
    numbers_before = defaultdict(int)
    numbers_after = defaultdict(int)
    numbers_same_day = defaultdict(int)

    # Zahlen die am naechsten Tag NICHT erscheinen
    absent_after = defaultdict(int)
    total_after_checks = 0

    for idx in pattern_indices:
        # Same day - andere Zahlen in derselben Ziehung
        same_day_nums = get_all_numbers(df.loc[idx])
        for n in same_day_nums:
            if n != number:
                numbers_same_day[n] += 1

        # Days before
        for d in range(1, days_before + 1):
            before_idx = idx - d
            if before_idx >= 0:
                before_nums = get_all_numbers(df.loc[before_idx])
                for n in before_nums:
                    numbers_before[n] += 1

        # Days after
        for d in range(1, days_after + 1):
            after_idx = idx + d
            if after_idx < len(df):
                after_nums = get_all_numbers(df.loc[after_idx])
                for n in after_nums:
                    numbers_after[n] += 1

        # Speziell: Was erscheint NICHT am naechsten Tag?
        if idx + 1 < len(df):
            total_after_checks += 1
            next_day_nums = get_all_numbers(df.loc[idx + 1])
            for n in range(1, 71):
                if n not in next_day_nums:
                    absent_after[n] += 1

    # Erwartungswerte
    expected_per_number = len(pattern_indices) * (20 / 70)

    # Analysiere Abweichungen
    after_deviations = []
    for n in range(1, 71):
        count = numbers_after.get(n, 0)
        if expected_per_number > 0:
            deviation = (count - expected_per_number * days_after) / (expected_per_number * days_after)
            after_deviations.append({
                "number": n,
                "count": count,
                "expected": expected_per_number * days_after,
                "deviation": deviation,
            })

    # Zahlen die ueberdurchschnittlich oft NICHT erscheinen nach dem Muster
    absent_analysis = []
    expected_absent = total_after_checks * (50 / 70)  # 50 von 70 erscheinen nicht
    for n in range(1, 71):
        absent_count = absent_after.get(n, 0)
        if expected_absent > 0:
            deviation = (absent_count - expected_absent) / expected_absent
            if deviation > 0.1:  # Mehr als 10% haeufiger absent
                absent_analysis.append({
                    "number": n,
                    "absent_count": absent_count,
                    "total_checks": total_after_checks,
                    "absent_rate": absent_count / total_after_checks if total_after_checks > 0 else 0,
                    "expected_absent_rate": 50 / 70,
                    "deviation": deviation,
                })

    return {
        "trigger_number": number,
        "trigger_position": position,
        "occurrences": len(pattern_indices),
        "numbers_more_likely_after": sorted(
            [d for d in after_deviations if d["deviation"] > 0.15],
            key=lambda x: -x["deviation"]
        )[:10],
        "numbers_less_likely_after": sorted(
            [d for d in after_deviations if d["deviation"] < -0.15],
            key=lambda x: x["deviation"]
        )[:10],
        "numbers_absent_after": sorted(absent_analysis, key=lambda x: -x["deviation"])[:15],
    }


def analyze_sequence_patterns(df: pd.DataFrame, number: int, position: int) -> dict:
    """Analysiert Sequenz-Muster wenn eine Zahl an einer Position erscheint."""

    col = f"Keno_Z{position}"
    pattern_indices = df[df[col] == number].index.tolist()

    # Was passiert wenn das Muster 2x hintereinander kommt?
    consecutive_indices = []
    for i in range(len(pattern_indices) - 1):
        if pattern_indices[i + 1] - pattern_indices[i] == 1:
            consecutive_indices.append(pattern_indices[i])

    # Analysiere Tag nach Doppel-Muster
    after_double_numbers = defaultdict(int)
    for idx in consecutive_indices:
        after_idx = idx + 2  # Tag nach dem zweiten Auftreten
        if after_idx < len(df):
            nums = get_all_numbers(df.loc[after_idx])
            for n in nums:
                after_double_numbers[n] += 1

    # Gap-Analyse: Wie viele Tage zwischen Auftritten?
    gaps = []
    for i in range(len(pattern_indices) - 1):
        gap = pattern_indices[i + 1] - pattern_indices[i]
        gaps.append(gap)

    return {
        "number": number,
        "position": position,
        "total_occurrences": len(pattern_indices),
        "consecutive_occurrences": len(consecutive_indices),
        "avg_gap": np.mean(gaps) if gaps else 0,
        "min_gap": min(gaps) if gaps else 0,
        "max_gap": max(gaps) if gaps else 0,
        "after_double_pattern": dict(sorted(
            after_double_numbers.items(), key=lambda x: -x[1]
        )[:10]) if consecutive_indices else {},
    }


def build_exclusion_rules(df: pd.DataFrame, preferences: list[dict]) -> list[dict]:
    """Baut Ausschluss-Regeln basierend auf Kontext-Analyse."""

    rules = []

    for pref in preferences[:20]:  # Top 20 Praeferenzen
        context = analyze_context_around_pattern(
            df,
            pref["number"],
            pref["position"],
            days_before=2,
            days_after=1,
        )

        # Regel: Wenn Zahl X an Position Y erscheint, dann sind diese Zahlen weniger wahrscheinlich
        if context["numbers_less_likely_after"]:
            exclude_numbers = [d["number"] for d in context["numbers_less_likely_after"][:5]]
            avg_deviation = np.mean([d["deviation"] for d in context["numbers_less_likely_after"][:5]])

            rules.append({
                "trigger": f"Zahl {pref['number']} an Position {pref['position']}",
                "trigger_number": pref["number"],
                "trigger_position": pref["position"],
                "action": "exclude",
                "exclude_numbers": exclude_numbers,
                "confidence": abs(avg_deviation),
                "occurrences": context["occurrences"],
            })

        # Regel: Diese Zahlen sind wahrscheinlicher
        if context["numbers_more_likely_after"]:
            include_numbers = [d["number"] for d in context["numbers_more_likely_after"][:5]]
            avg_deviation = np.mean([d["deviation"] for d in context["numbers_more_likely_after"][:5]])

            rules.append({
                "trigger": f"Zahl {pref['number']} an Position {pref['position']}",
                "trigger_number": pref["number"],
                "trigger_position": pref["position"],
                "action": "include",
                "include_numbers": include_numbers,
                "confidence": avg_deviation,
                "occurrences": context["occurrences"],
            })

    return sorted(rules, key=lambda x: -x["confidence"])


def backtest_exclusion_rules(
    df: pd.DataFrame,
    rules: list[dict],
    test_start_idx: int = None,
) -> dict:
    """Backtestet die Ausschluss-Regeln."""

    if test_start_idx is None:
        test_start_idx = len(df) // 2  # Letzte Haelfte als Test

    results = {
        "total_predictions": 0,
        "correct_exclusions": 0,
        "wrong_exclusions": 0,
        "correct_inclusions": 0,
        "wrong_inclusions": 0,
        "rule_performance": [],
    }

    for rule in rules[:30]:  # Top 30 Regeln testen
        rule_correct = 0
        rule_wrong = 0
        rule_applications = 0

        for idx in range(test_start_idx, len(df) - 1):
            col = f"Keno_Z{rule['trigger_position']}"
            if df.loc[idx, col] == rule["trigger_number"]:
                # Regel triggered!
                rule_applications += 1
                next_day_nums = get_all_numbers(df.loc[idx + 1])

                if rule["action"] == "exclude":
                    for excl_num in rule["exclude_numbers"]:
                        results["total_predictions"] += 1
                        if excl_num not in next_day_nums:
                            results["correct_exclusions"] += 1
                            rule_correct += 1
                        else:
                            results["wrong_exclusions"] += 1
                            rule_wrong += 1

                elif rule["action"] == "include":
                    for incl_num in rule["include_numbers"]:
                        results["total_predictions"] += 1
                        if incl_num in next_day_nums:
                            results["correct_inclusions"] += 1
                            rule_correct += 1
                        else:
                            results["wrong_inclusions"] += 1
                            rule_wrong += 1

        if rule_applications > 0:
            accuracy = rule_correct / (rule_correct + rule_wrong) if (rule_correct + rule_wrong) > 0 else 0
            results["rule_performance"].append({
                "rule": rule["trigger"],
                "action": rule["action"],
                "applications": rule_applications,
                "correct": rule_correct,
                "wrong": rule_wrong,
                "accuracy": accuracy,
                "numbers": rule.get("exclude_numbers") or rule.get("include_numbers"),
            })

    # Sortiere nach Accuracy
    results["rule_performance"] = sorted(
        results["rule_performance"],
        key=lambda x: -x["accuracy"]
    )

    return results


def find_correlated_absences(df: pd.DataFrame) -> dict:
    """Findet Zahlen die oft zusammen NICHT erscheinen."""

    # Fuer jedes Zahlenpaar: Wie oft erscheinen beide NICHT?
    pair_both_absent = defaultdict(int)
    pair_one_absent = defaultdict(int)

    for idx in range(len(df)):
        nums = get_all_numbers(df.loc[idx])
        absent = set(range(1, 71)) - nums

        absent_list = list(absent)
        for i in range(len(absent_list)):
            for j in range(i + 1, len(absent_list)):
                pair = tuple(sorted([absent_list[i], absent_list[j]]))
                pair_both_absent[pair] += 1

    # Erwartung: Beide absent = (50/70)^2 ≈ 0.51 der Ziehungen
    expected_both = len(df) * (50/70) * (49/69)

    # Finde Paare die oefter zusammen absent sind als erwartet
    correlated = []
    for pair, count in pair_both_absent.items():
        deviation = (count - expected_both) / expected_both
        if deviation > 0.05:  # Mehr als 5% ueber Erwartung
            correlated.append({
                "pair": pair,
                "both_absent_count": count,
                "expected": expected_both,
                "deviation": deviation,
            })

    return {
        "correlated_absence_pairs": sorted(correlated, key=lambda x: -x["deviation"])[:30],
    }


def main():
    path = Path("Keno_GPTs/Kenogpts_2/Basis_Tab/KENO_ab_2018.csv")

    print("=" * 70)
    print("KENOBASE - Position-Praeferenzen Praediktive Analyse")
    print("=" * 70)

    print("\n[1] Lade Daten...")
    df = load_data(path)
    n = len(df)
    print(f"    {n} Ziehungen geladen")

    # Identifiziere Position-Praeferenzen
    print("\n[2] Identifiziere Position-Praeferenzen...")
    preferences = identify_position_preferences(df, threshold=0.3)
    print(f"    {len(preferences)} signifikante Praeferenzen gefunden")

    # Top 10 zeigen
    print(f"\n    Top 10 Praeferenzen:")
    print(f"    {'Zahl':>6} {'Pos':>5} {'Count':>7} {'Erwartet':>9} {'Abweichung':>11}")
    print("    " + "-" * 45)
    for p in preferences[:10]:
        print(f"    {p['number']:>6d} {p['position']:>5d} {p['count']:>7d} "
              f"{p['expected']:>9.1f} {p['deviation']*100:>+10.1f}%")

    # Kontext-Analyse fuer Top-Praeferenzen
    print("\n[3] Analysiere Kontext um Top-Praeferenzen...")

    for pref in preferences[:5]:
        print(f"\n    === Zahl {pref['number']} an Position {pref['position']} ===")
        context = analyze_context_around_pattern(df, pref["number"], pref["position"])

        print(f"    Auftritte: {context['occurrences']}")

        if context["numbers_more_likely_after"]:
            print(f"    Wahrscheinlicher am naechsten Tag:")
            for d in context["numbers_more_likely_after"][:5]:
                print(f"      Zahl {d['number']:2d}: {d['deviation']*100:+.1f}%")

        if context["numbers_less_likely_after"]:
            print(f"    Weniger wahrscheinlich am naechsten Tag:")
            for d in context["numbers_less_likely_after"][:5]:
                print(f"      Zahl {d['number']:2d}: {d['deviation']*100:+.1f}%")

    # Sequenz-Muster
    print("\n[4] Analysiere Sequenz-Muster...")
    for pref in preferences[:3]:
        seq = analyze_sequence_patterns(df, pref["number"], pref["position"])
        print(f"\n    Zahl {seq['number']} an Pos {seq['position']}:")
        print(f"      Auftritte: {seq['total_occurrences']}, Konsekutiv: {seq['consecutive_occurrences']}")
        print(f"      Gap: min={seq['min_gap']}, avg={seq['avg_gap']:.1f}, max={seq['max_gap']}")

    # Baue Regeln
    print("\n[5] Baue Praediktive Regeln...")
    rules = build_exclusion_rules(df, preferences)
    print(f"    {len(rules)} Regeln erstellt")

    print(f"\n    Top 10 Regeln (nach Confidence):")
    for r in rules[:10]:
        nums = r.get("exclude_numbers") or r.get("include_numbers")
        print(f"    {r['trigger']:30} -> {r['action']:7} {nums} (conf: {r['confidence']:.2f})")

    # Backtest
    print("\n[6] Backteste Regeln (letzte 50% der Daten)...")
    backtest = backtest_exclusion_rules(df, rules)

    print(f"\n    Gesamt-Statistik:")
    print(f"      Total Predictions:    {backtest['total_predictions']}")
    print(f"      Correct Exclusions:   {backtest['correct_exclusions']}")
    print(f"      Wrong Exclusions:     {backtest['wrong_exclusions']}")
    print(f"      Correct Inclusions:   {backtest['correct_inclusions']}")
    print(f"      Wrong Inclusions:     {backtest['wrong_inclusions']}")

    # Exclusion Accuracy
    if backtest['correct_exclusions'] + backtest['wrong_exclusions'] > 0:
        excl_acc = backtest['correct_exclusions'] / (backtest['correct_exclusions'] + backtest['wrong_exclusions'])
        expected_excl = 50 / 70  # Bei Zufall: 71.4% der Zahlen erscheinen nicht
        print(f"\n      Exclusion Accuracy:   {excl_acc:.1%} (Zufall: {expected_excl:.1%})")
        print(f"      Verbesserung:         {(excl_acc - expected_excl) * 100:+.1f}%")

    # Inclusion Accuracy
    if backtest['correct_inclusions'] + backtest['wrong_inclusions'] > 0:
        incl_acc = backtest['correct_inclusions'] / (backtest['correct_inclusions'] + backtest['wrong_inclusions'])
        expected_incl = 20 / 70  # Bei Zufall: 28.6% der Zahlen erscheinen
        print(f"\n      Inclusion Accuracy:   {incl_acc:.1%} (Zufall: {expected_incl:.1%})")
        print(f"      Verbesserung:         {(incl_acc - expected_incl) * 100:+.1f}%")

    # Beste Regeln
    print(f"\n    Top 10 beste Regeln im Backtest:")
    print(f"    {'Regel':35} {'Action':8} {'Apps':>5} {'Acc':>7} {'Zahlen'}")
    print("    " + "-" * 75)
    for r in backtest["rule_performance"][:10]:
        nums_str = ",".join(map(str, r["numbers"][:3])) + "..." if r["numbers"] else ""
        print(f"    {r['rule']:35} {r['action']:8} {r['applications']:>5} "
              f"{r['accuracy']:>6.1%} {nums_str}")

    # Korrelierte Absenzen
    print("\n[7] Analysiere korrelierte Absenzen...")
    corr = find_correlated_absences(df)

    print(f"    Top 10 Zahlenpaare die oft zusammen NICHT erscheinen:")
    for c in corr["correlated_absence_pairs"][:10]:
        print(f"      {c['pair']}: {c['both_absent_count']} mal beide absent "
              f"({c['deviation']*100:+.1f}% vs Erwartung)")

    # Speichere Ergebnisse
    results = {
        "n_draws": n,
        "top_preferences": preferences[:30],
        "rules": rules[:50],
        "backtest": {
            "total_predictions": backtest["total_predictions"],
            "exclusion_accuracy": backtest['correct_exclusions'] / (backtest['correct_exclusions'] + backtest['wrong_exclusions']) if (backtest['correct_exclusions'] + backtest['wrong_exclusions']) > 0 else 0,
            "inclusion_accuracy": backtest['correct_inclusions'] / (backtest['correct_inclusions'] + backtest['wrong_inclusions']) if (backtest['correct_inclusions'] + backtest['wrong_inclusions']) > 0 else 0,
            "top_rules": backtest["rule_performance"][:20],
        },
        "correlated_absences": corr["correlated_absence_pairs"][:20],
    }

    output_path = Path("results/position_predictive.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    excl_acc = backtest['correct_exclusions'] / (backtest['correct_exclusions'] + backtest['wrong_exclusions']) if (backtest['correct_exclusions'] + backtest['wrong_exclusions']) > 0 else 0
    incl_acc = backtest['correct_inclusions'] / (backtest['correct_inclusions'] + backtest['wrong_inclusions']) if (backtest['correct_inclusions'] + backtest['wrong_inclusions']) > 0 else 0

    print(f"""
    Position-Praeferenzen gefunden:     {len(preferences)}
    Praediktive Regeln erstellt:        {len(rules)}

    BACKTEST ERGEBNISSE:
    Exclusion Accuracy: {excl_acc:.1%} (Zufall: 71.4%)
    Inclusion Accuracy: {incl_acc:.1%} (Zufall: 28.6%)
    """)

    if excl_acc > 0.72 or incl_acc > 0.30:
        print("    *** PRAEDIKTIVER WERT GEFUNDEN! ***")
        print("    Die Regeln performen besser als Zufall!")
    else:
        print("    Kein signifikanter praediktiver Wert.")
        print("    Position-Praeferenzen sind historisch, aber nicht vorhersagbar.")

    print(f"\n[8] Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
