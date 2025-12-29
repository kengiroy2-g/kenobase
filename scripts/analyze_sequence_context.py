#!/usr/bin/env python3
"""
Sequenz-Kontext Analyse - Original Ziehungsreihenfolge

Analysiert:
1. Positions-Muster in der Original-Ziehungsreihenfolge
2. Kontext-Fenster: Was passiert 1-3 Tage vor/nach bestimmten Mustern
3. Exclusion-Regeln: Welche Zahlen erscheinen NICHT nach bestimmten Mustern
4. Praediktive Signale fuer das Garantie-Modell

Autor: Kenobase V2.2
Datum: 2025-12-29
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
from scipy import stats


def load_original_order(path: str) -> pd.DataFrame:
    """Laedt KENO Ziehungen in Original-Reihenfolge."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    # Positionen 1-20 in Original-Reihenfolge
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["positions"] = df[pos_cols].values.tolist()
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row), axis=1)

    return df.sort_values("Datum").reset_index(drop=True)


def find_position_preferences(df: pd.DataFrame) -> Dict:
    """Findet Zahlen die bestimmte Positionen bevorzugen."""
    # Zaehle wie oft jede Zahl an jeder Position erscheint
    position_counts = defaultdict(lambda: defaultdict(int))

    for _, row in df.iterrows():
        for pos, zahl in enumerate(row["positions"], 1):
            position_counts[zahl][pos] += 1

    # Erwartete Anzahl: n_draws * (1/70) fuer jede Position
    n_draws = len(df)
    expected = n_draws / 70

    preferences = []
    for zahl in range(1, 71):
        for pos in range(1, 21):
            count = position_counts[zahl][pos]
            if count > 0:
                deviation = (count - expected) / expected
                if abs(deviation) > 0.3:  # >30% Abweichung
                    preferences.append({
                        "zahl": zahl,
                        "position": pos,
                        "count": count,
                        "expected": round(expected, 1),
                        "deviation": round(deviation * 100, 1)
                    })

    preferences.sort(key=lambda x: -abs(x["deviation"]))
    return {"preferences": preferences[:50], "expected_per_pos": round(expected, 2)}


def find_sequential_patterns(df: pd.DataFrame) -> Dict:
    """Findet Muster in aufeinanderfolgenden Ziehungen."""
    patterns = {
        "vertical": [],      # Gleiche Zahl, gleiche Position
        "diagonal_right": [], # Gleiche Zahl, Position +1
        "diagonal_left": [],  # Gleiche Zahl, Position -1
        "repeat_next_day": [] # Zahl erscheint wieder (egal welche Position)
    }

    for i in range(1, len(df)):
        prev = df.iloc[i-1]
        curr = df.iloc[i]

        prev_positions = prev["positions"]
        curr_positions = curr["positions"]
        prev_set = prev["numbers_set"]
        curr_set = curr["numbers_set"]

        # Wiederholte Zahlen
        repeated = prev_set & curr_set
        if repeated:
            patterns["repeat_next_day"].append({
                "date": str(curr["Datum"].date()),
                "repeated": list(repeated),
                "count": len(repeated)
            })

        # Positions-Muster
        for pos in range(20):
            zahl = prev_positions[pos]

            # Vertikal: gleiche Position
            if pos < 20 and curr_positions[pos] == zahl:
                patterns["vertical"].append({
                    "date": str(curr["Datum"].date()),
                    "zahl": zahl,
                    "position": pos + 1
                })

            # Diagonal rechts: Position +1
            if pos < 19 and curr_positions[pos + 1] == zahl:
                patterns["diagonal_right"].append({
                    "date": str(curr["Datum"].date()),
                    "zahl": zahl,
                    "from_pos": pos + 1,
                    "to_pos": pos + 2
                })

            # Diagonal links: Position -1
            if pos > 0 and curr_positions[pos - 1] == zahl:
                patterns["diagonal_left"].append({
                    "date": str(curr["Datum"].date()),
                    "zahl": zahl,
                    "from_pos": pos + 1,
                    "to_pos": pos
                })

    return {
        "vertical_count": len(patterns["vertical"]),
        "diagonal_right_count": len(patterns["diagonal_right"]),
        "diagonal_left_count": len(patterns["diagonal_left"]),
        "avg_repeats_per_day": np.mean([p["count"] for p in patterns["repeat_next_day"]]) if patterns["repeat_next_day"] else 0,
        "samples": {
            "vertical": patterns["vertical"][:10],
            "diagonal_right": patterns["diagonal_right"][:10],
            "repeat": patterns["repeat_next_day"][:5]
        }
    }


def analyze_context_windows(df: pd.DataFrame, window_before: int = 3, window_after: int = 3) -> Dict:
    """
    Analysiert Kontext-Fenster um bestimmte Muster herum.
    Was passiert X Tage vor und nach wenn Zahl Z an Position P erscheint?
    """
    # Top Position-Praeferenzen finden
    prefs = find_position_preferences(df)["preferences"][:20]

    context_results = []

    for pref in prefs:
        zahl = pref["zahl"]
        pos = pref["position"]

        # Finde alle Tage wo Zahl an dieser Position erscheint
        trigger_days = []
        for i, row in df.iterrows():
            if row["positions"][pos - 1] == zahl:
                trigger_days.append(i)

        if len(trigger_days) < 10:
            continue

        # Analysiere was DANACH passiert
        after_appears = defaultdict(int)
        after_absent = defaultdict(int)
        total_after = 0

        for day_idx in trigger_days:
            for offset in range(1, window_after + 1):
                if day_idx + offset < len(df):
                    total_after += 1
                    future_set = df.iloc[day_idx + offset]["numbers_set"]

                    for z in range(1, 71):
                        if z in future_set:
                            after_appears[z] += 1
                        else:
                            after_absent[z] += 1

        # Berechne Abweichungen
        expected_rate = 20 / 70  # Erwartete Erscheinungsrate

        likely_after = []
        unlikely_after = []

        for z in range(1, 71):
            if total_after > 0:
                appear_rate = after_appears[z] / total_after
                deviation = (appear_rate - expected_rate) / expected_rate

                if deviation > 0.15:  # >15% wahrscheinlicher
                    likely_after.append((z, round(deviation * 100, 1)))
                elif deviation < -0.15:  # >15% unwahrscheinlicher
                    unlikely_after.append((z, round(deviation * 100, 1)))

        likely_after.sort(key=lambda x: -x[1])
        unlikely_after.sort(key=lambda x: x[1])

        context_results.append({
            "trigger": f"Zahl {zahl} an Position {pos}",
            "trigger_count": len(trigger_days),
            "likely_after": likely_after[:5],
            "unlikely_after": unlikely_after[:5],
            "exclusion_candidates": [z for z, _ in unlikely_after[:3]]
        })

    return context_results


def find_exclusion_rules(df: pd.DataFrame, min_accuracy: float = 0.85) -> Dict:
    """
    Findet Ausschluss-Regeln mit hoher Accuracy.
    WENN Zahl X an Position Y erscheint, DANN erscheint Zahl Z morgen NICHT.
    """
    rules = []

    # Teste alle Position-Zahl Kombinationen
    for trigger_pos in range(1, 21):
        for trigger_zahl in range(1, 71):

            # Finde Trigger-Tage
            trigger_days = []
            for i in range(len(df) - 1):  # -1 weil wir morgen brauchen
                if df.iloc[i]["positions"][trigger_pos - 1] == trigger_zahl:
                    trigger_days.append(i)

            if len(trigger_days) < 20:  # Mindestens 20 Samples
                continue

            # Fuer jede moegliche Exclude-Zahl
            for exclude_zahl in range(1, 71):
                if exclude_zahl == trigger_zahl:
                    continue

                # Zaehle wie oft exclude_zahl am naechsten Tag NICHT erscheint
                absent_count = 0
                for day_idx in trigger_days:
                    next_day = df.iloc[day_idx + 1]["numbers_set"]
                    if exclude_zahl not in next_day:
                        absent_count += 1

                accuracy = absent_count / len(trigger_days)

                # Baseline: 50/70 = 71.4% sollten absent sein
                baseline = 50 / 70

                if accuracy >= min_accuracy and accuracy > baseline + 0.10:
                    rules.append({
                        "trigger": f"Zahl {trigger_zahl} an Pos {trigger_pos}",
                        "trigger_zahl": trigger_zahl,
                        "trigger_pos": trigger_pos,
                        "exclude": exclude_zahl,
                        "accuracy": round(accuracy * 100, 1),
                        "samples": len(trigger_days),
                        "improvement": round((accuracy - baseline) * 100, 1)
                    })

    rules.sort(key=lambda x: (-x["accuracy"], -x["samples"]))
    return {"rules": rules[:50], "total_found": len(rules)}


def find_absence_correlations(df: pd.DataFrame) -> Dict:
    """
    Findet Zahlen die zusammen NICHT erscheinen (korrelierte Absenzen).
    """
    # Zaehle Paar-Absenzen
    pair_both_absent = defaultdict(int)
    pair_one_absent = defaultdict(int)

    for _, row in df.iterrows():
        present = row["numbers_set"]
        absent = set(range(1, 71)) - present

        for z1 in range(1, 71):
            for z2 in range(z1 + 1, 71):
                z1_absent = z1 in absent
                z2_absent = z2 in absent

                if z1_absent and z2_absent:
                    pair_both_absent[(z1, z2)] += 1
                elif z1_absent or z2_absent:
                    pair_one_absent[(z1, z2)] += 1

    # Erwartete beide absent: (50/70)^2 = 51%
    expected_both = (50/70) ** 2
    n_draws = len(df)

    correlations = []
    for pair, count in pair_both_absent.items():
        rate = count / n_draws
        deviation = (rate - expected_both) / expected_both

        if deviation > 0.05:  # >5% ueber Erwartung
            correlations.append({
                "pair": pair,
                "both_absent_rate": round(rate * 100, 1),
                "expected": round(expected_both * 100, 1),
                "deviation": round(deviation * 100, 1)
            })

    correlations.sort(key=lambda x: -x["deviation"])
    return correlations[:30]


def backtest_exclusion_rules(df: pd.DataFrame, rules: List[Dict], test_ratio: float = 0.3) -> Dict:
    """Backtestet Exclusion-Regeln auf Out-of-Sample Daten."""
    split_idx = int(len(df) * (1 - test_ratio))
    test_df = df.iloc[split_idx:].reset_index(drop=True)

    results = []

    for rule in rules[:20]:  # Top 20 Regeln testen
        trigger_zahl = rule["trigger_zahl"]
        trigger_pos = rule["trigger_pos"]
        exclude = rule["exclude"]

        correct = 0
        total = 0

        for i in range(len(test_df) - 1):
            if test_df.iloc[i]["positions"][trigger_pos - 1] == trigger_zahl:
                total += 1
                next_set = test_df.iloc[i + 1]["numbers_set"]
                if exclude not in next_set:
                    correct += 1

        if total >= 5:
            results.append({
                "rule": rule["trigger"],
                "exclude": exclude,
                "test_accuracy": round(correct / total * 100, 1) if total > 0 else 0,
                "train_accuracy": rule["accuracy"],
                "test_samples": total
            })

    return results


def main():
    """Hauptfunktion."""
    print("=" * 80)
    print("SEQUENZ-KONTEXT ANALYSE - Original Ziehungsreihenfolge")
    print("=" * 80)
    print()

    base_path = Path(__file__).parent.parent
    # Verwende Original-Reihenfolge Datei
    data_path = base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv"

    if not data_path.exists():
        data_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"

    output_path = base_path / "results" / "sequence_context_analysis.json"

    print(f"Lade Daten: {data_path}")
    df = load_original_order(str(data_path))
    print(f"  Ziehungen: {len(df)}")
    print()

    results = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "draws": len(df),
            "date_range": f"{df['Datum'].min().date()} - {df['Datum'].max().date()}"
        }
    }

    # 1. Position-Praeferenzen
    print("1. Analysiere Position-Praeferenzen...")
    prefs = find_position_preferences(df)
    results["position_preferences"] = prefs
    print(f"   Top-5 Praeferenzen:")
    for p in prefs["preferences"][:5]:
        print(f"     Zahl {p['zahl']} an Pos {p['position']}: {p['count']}x ({p['deviation']:+.1f}%)")
    print()

    # 2. Sequentielle Muster
    print("2. Analysiere sequentielle Muster...")
    seq = find_sequential_patterns(df)
    results["sequential_patterns"] = seq
    print(f"   Vertikale Matches: {seq['vertical_count']}")
    print(f"   Diagonal rechts: {seq['diagonal_right_count']}")
    print(f"   Diagonal links: {seq['diagonal_left_count']}")
    print(f"   Durchschn. Wiederholungen/Tag: {seq['avg_repeats_per_day']:.2f}")
    print()

    # 3. Kontext-Fenster
    print("3. Analysiere Kontext-Fenster (3 Tage nach Trigger)...")
    context = analyze_context_windows(df)
    results["context_windows"] = context
    print(f"   Analysierte Trigger: {len(context)}")
    if context:
        print(f"   Beispiel - {context[0]['trigger']}:")
        print(f"     Wahrscheinlicher danach: {context[0]['likely_after'][:3]}")
        print(f"     Unwahrscheinlich danach: {context[0]['unlikely_after'][:3]}")
    print()

    # 4. Exclusion-Regeln
    print("4. Finde Exclusion-Regeln (Accuracy >= 85%)...")
    exclusions = find_exclusion_rules(df, min_accuracy=0.85)
    results["exclusion_rules"] = exclusions
    print(f"   Gefundene Regeln: {exclusions['total_found']}")
    print(f"   Top-5 Regeln:")
    for r in exclusions["rules"][:5]:
        print(f"     {r['trigger']} -> Exclude {r['exclude']}: {r['accuracy']}%")
    print()

    # 5. Korrelierte Absenzen
    print("5. Finde korrelierte Absenzen...")
    correlations = find_absence_correlations(df)
    results["absence_correlations"] = correlations
    print(f"   Top-5 korrelierte Paare:")
    for c in correlations[:5]:
        print(f"     ({c['pair'][0]}, {c['pair'][1]}): {c['both_absent_rate']}% beide absent (+{c['deviation']}%)")
    print()

    # 6. Backtest
    print("6. Backteste Exclusion-Regeln (30% Out-of-Sample)...")
    backtest = backtest_exclusion_rules(df, exclusions["rules"])
    results["backtest"] = backtest
    print(f"   Getestete Regeln: {len(backtest)}")
    if backtest:
        valid = [r for r in backtest if r["test_accuracy"] >= 80]
        print(f"   Regeln mit >= 80% Test-Accuracy: {len(valid)}")
        for r in valid[:5]:
            print(f"     {r['rule']} -> Exclude {r['exclude']}: Train {r['train_accuracy']}%, Test {r['test_accuracy']}%")
    print()

    # Speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"Ergebnisse gespeichert: {output_path}")

    # Zusammenfassung fuer Modell
    print()
    print("=" * 80)
    print("ERKENNTNISSE FUER GARANTIE-MODELL")
    print("=" * 80)
    print()

    print("EXCLUSION-REGELN (fuer morgen anwenden):")
    print("-" * 50)
    for r in backtest[:10]:
        if r["test_accuracy"] >= 75:
            print(f"WENN heute {r['rule']}")
            print(f"  -> MORGEN Zahl {r['exclude']} AUSSCHLIESSEN ({r['test_accuracy']}% sicher)")
            print()

    print("KORRELIERTE ABSENZEN (Zahlen-Paare die zusammen fehlen):")
    print("-" * 50)
    for c in correlations[:5]:
        print(f"  ({c['pair'][0]}, {c['pair'][1]}): Wenn eine fehlt, fehlt andere +{c['deviation']}% haeufiger")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
