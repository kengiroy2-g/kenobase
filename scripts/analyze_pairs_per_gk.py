#!/usr/bin/env python3
"""
Paar-Analyse pro Gewinnklasse (WL-001, WL-007)

Analysiert Zahlenpaare nicht global, sondern pro Gewinnklasse.
Testet Hypothese: Starke Paare garantieren kleine Gewinne.

Autor: Kenobase V2.2
Datum: 2025-12-29
"""

import json
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

import pandas as pd
import numpy as np


def load_keno_draws(path: str = "data/raw/keno/KENO_ab_2018.csv") -> pd.DataFrame:
    """Laedt KENO Ziehungen."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    # Extrahiere Zahlen als Liste
    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers"] = df[number_cols].values.tolist()

    return df


def load_gewinnquoten(path: str = "Keno_GPTs/Keno_GQ_2022_2023-2024.csv") -> pd.DataFrame:
    """Laedt Gewinnquoten pro Gewinnklasse."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df["Keno-Typ"] = df["Keno-Typ"].astype(int)
    df["Anzahl richtiger Zahlen"] = df["Anzahl richtiger Zahlen"].astype(int)
    return df


def calculate_pair_cooccurrence(numbers_list: list) -> dict:
    """
    Berechnet Paar-Co-Occurrence fuer eine Liste von Ziehungen.

    Returns:
        Dict mit Paar als Key und Count als Value
    """
    pair_counts = defaultdict(int)

    for numbers in numbers_list:
        # Sortiere Zahlen fuer konsistente Paarbildung
        sorted_nums = sorted(numbers)
        for pair in combinations(sorted_nums, 2):
            pair_counts[pair] += 1

    return dict(pair_counts)


def simulate_type2_ticket(pair: tuple, draws: list) -> dict:
    """
    Simuliert ein Typ-2 Ticket mit einem Zahlenpaar.

    Args:
        pair: Zahlenpaar (z.B. (2, 3))
        draws: Liste von Ziehungen (jede Ziehung = Liste von 20 Zahlen)

    Returns:
        Dict mit Gewinn-Statistiken
    """
    wins = 0
    two_hits = 0  # 2/2 = GK1 (6 EUR bei 1 EUR Einsatz)
    one_hit = 0   # 1/2 = nichts
    zero_hits = 0 # 0/2 = nichts

    for draw in draws:
        draw_set = set(draw)
        hits = sum(1 for n in pair if n in draw_set)

        if hits == 2:
            two_hits += 1
            wins += 1
        elif hits == 1:
            one_hit += 1
        else:
            zero_hits += 1

    return {
        "pair": pair,
        "total_draws": len(draws),
        "wins_2_2": two_hits,
        "hits_1_2": one_hit,
        "hits_0_2": zero_hits,
        "win_rate": two_hits / len(draws) if draws else 0,
        "expected_rate": (20/70) * (19/69)  # ~7.8%
    }


def analyze_pairs_per_gewinnklasse(
    keno_df: pd.DataFrame,
    gq_df: pd.DataFrame,
    min_cooccurrence: int = 200
) -> dict:
    """
    Hauptanalyse: Paare pro Gewinnklasse.

    Args:
        keno_df: KENO Ziehungen
        gq_df: Gewinnquoten DataFrame
        min_cooccurrence: Minimum Co-Occurrence fuer "starke" Paare

    Returns:
        Dict mit Analyse-Ergebnissen
    """
    results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "total_draws": len(keno_df),
            "gq_records": len(gq_df),
            "min_cooccurrence": min_cooccurrence
        },
        "global_pairs": {},
        "pairs_per_gk": {},
        "pair_guarantee_test": {},
        "monthly_backtest": {}
    }

    # 1. Globale Paar-Analyse
    print("=== Globale Paar-Analyse ===")
    all_draws = keno_df["numbers"].tolist()
    global_pairs = calculate_pair_cooccurrence(all_draws)

    # Top-Paare filtern
    strong_pairs = {k: v for k, v in global_pairs.items() if v >= min_cooccurrence}
    results["global_pairs"] = {
        "total_pairs": len(global_pairs),
        "strong_pairs_count": len(strong_pairs),
        "top_20": sorted(strong_pairs.items(), key=lambda x: -x[1])[:20]
    }

    print(f"Gesamt Paare: {len(global_pairs)}")
    print(f"Starke Paare (>={min_cooccurrence}x): {len(strong_pairs)}")
    print(f"Top-5 Paare: {results['global_pairs']['top_20'][:5]}")

    # 2. Paar-Analyse pro Gewinnklasse
    print("\n=== Paar-Analyse pro Gewinnklasse ===")

    # Merge Ziehungen mit Gewinnquoten
    merged = pd.merge(
        keno_df[["Datum", "numbers"]],
        gq_df[["Datum", "Keno-Typ", "Anzahl richtiger Zahlen", "Anzahl der Gewinner"]],
        on="Datum",
        how="inner"
    )

    # Gruppiere nach Gewinnklasse
    for keno_typ in range(2, 11):
        for treffer in range(0, keno_typ + 1):
            gk_key = f"GK_{keno_typ}_{treffer}"

            # Filtere Ziehungen wo diese GK Gewinner hatte
            mask = (merged["Keno-Typ"] == keno_typ) & \
                   (merged["Anzahl richtiger Zahlen"] == treffer) & \
                   (merged["Anzahl der Gewinner"] > 0)

            gk_draws = merged[mask]["numbers"].tolist()

            if len(gk_draws) < 10:
                continue

            gk_pairs = calculate_pair_cooccurrence(gk_draws)

            # Erwartete Co-Occurrence berechnen
            n_draws = len(gk_draws)
            expected = n_draws * (20/70) * (19/69) * 190  # 190 = C(20,2)

            # Top-Paare fuer diese GK
            top_gk_pairs = sorted(gk_pairs.items(), key=lambda x: -x[1])[:10]

            # Lift berechnen
            gk_analysis = []
            for pair, count in top_gk_pairs:
                exp_per_pair = n_draws * (20/70) * (19/69)  # ~7.8% pro Ziehung
                lift = count / exp_per_pair if exp_per_pair > 0 else 0
                gk_analysis.append({
                    "pair": pair,
                    "count": count,
                    "expected": round(exp_per_pair, 2),
                    "lift": round(lift, 3)
                })

            results["pairs_per_gk"][gk_key] = {
                "draws_with_winners": n_draws,
                "top_pairs": gk_analysis
            }

    # Zeige interessanteste GKs
    print("\nInteressante Gewinnklassen:")
    for gk_key in ["GK_2_2", "GK_10_10", "GK_10_9"]:
        if gk_key in results["pairs_per_gk"]:
            gk = results["pairs_per_gk"][gk_key]
            print(f"  {gk_key}: {gk['draws_with_winners']} Ziehungen")
            if gk["top_pairs"]:
                print(f"    Top-Paar: {gk['top_pairs'][0]}")

    # 3. Paar-Garantie Test (WL-001)
    print("\n=== Paar-Garantie Test (WL-001) ===")
    print("Teste: Gewinnt jedes starke Paar mind. 1x/Monat als Typ-2 Ticket?")

    # Gruppiere Ziehungen nach Monat
    keno_df["month"] = keno_df["Datum"].dt.to_period("M")
    months = keno_df["month"].unique()

    pair_monthly_wins = defaultdict(lambda: defaultdict(int))

    for _, row in keno_df.iterrows():
        month = str(row["month"])
        draw_set = set(row["numbers"])

        for pair in list(strong_pairs.keys())[:30]:  # Top-30 Paare testen
            if pair[0] in draw_set and pair[1] in draw_set:
                pair_monthly_wins[pair][month] += 1

    # Auswertung
    guarantee_results = []
    for pair in list(strong_pairs.keys())[:30]:
        pair_str = f"({pair[0]},{pair[1]})"
        monthly_data = pair_monthly_wins[pair]
        months_with_win = sum(1 for m in months if str(m) in monthly_data and monthly_data[str(m)] > 0)
        total_months = len(months)

        guarantee_results.append({
            "pair": pair_str,
            "months_with_win": months_with_win,
            "total_months": total_months,
            "guarantee_rate": round(months_with_win / total_months, 3) if total_months > 0 else 0,
            "avg_wins_per_month": round(sum(monthly_data.values()) / total_months, 2) if total_months > 0 else 0
        })

    results["pair_guarantee_test"] = {
        "hypothesis": "WL-001: Starke Paare gewinnen mind. 1x/Monat",
        "threshold": 0.90,
        "pairs_tested": len(guarantee_results),
        "pairs_meeting_threshold": sum(1 for r in guarantee_results if r["guarantee_rate"] >= 0.90),
        "results": sorted(guarantee_results, key=lambda x: -x["guarantee_rate"])
    }

    passed = results["pair_guarantee_test"]["pairs_meeting_threshold"]
    tested = results["pair_guarantee_test"]["pairs_tested"]
    print(f"Paare mit >90% Garantie: {passed}/{tested}")

    if guarantee_results:
        print(f"Bestes Paar: {guarantee_results[0]}")

    # 4. Typ-2 Backtest
    print("\n=== Typ-2 Backtest ===")

    all_draws_list = keno_df["numbers"].tolist()
    backtest_results = []

    for pair in list(strong_pairs.keys())[:10]:
        sim = simulate_type2_ticket(pair, all_draws_list)
        backtest_results.append(sim)
        print(f"Paar {pair}: {sim['wins_2_2']}/{sim['total_draws']} Gewinne ({sim['win_rate']*100:.2f}%)")

    results["monthly_backtest"] = {
        "description": "Typ-2 Ticket Simulation mit starken Paaren",
        "results": backtest_results
    }

    return results


def main():
    """Hauptfunktion."""
    print("=" * 60)
    print("PAAR-ANALYSE PRO GEWINNKLASSE (WL-001, WL-007)")
    print("=" * 60)
    print()

    # Pfade
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    gq_path = base_path / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
    output_path = base_path / "results" / "pairs_per_gk_analysis.json"

    # Daten laden
    print("Lade Daten...")
    keno_df = load_keno_draws(str(keno_path))
    print(f"  KENO Ziehungen: {len(keno_df)}")

    gq_df = load_gewinnquoten(str(gq_path))
    print(f"  Gewinnquoten: {len(gq_df)}")
    print()

    # Analyse durchfuehren
    results = analyze_pairs_per_gewinnklasse(keno_df, gq_df)

    # Ergebnisse speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Konvertiere Tupel zu Strings fuer JSON
    def convert_tuples(obj):
        if isinstance(obj, dict):
            return {str(k) if isinstance(k, tuple) else k: convert_tuples(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_tuples(item) for item in obj]
        elif isinstance(obj, tuple):
            return str(obj)
        else:
            return obj

    results_json = convert_tuples(results)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results_json, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG")
    print("=" * 60)

    gt = results["pair_guarantee_test"]
    print(f"\nWL-001 Ergebnis:")
    print(f"  Paare getestet: {gt['pairs_tested']}")
    print(f"  Paare mit >90% Garantie: {gt['pairs_meeting_threshold']}")

    if gt['pairs_meeting_threshold'] >= gt['pairs_tested'] * 0.9:
        print("  STATUS: BESTAETIGT - Starke Paare garantieren monatliche Gewinne")
    else:
        print("  STATUS: TEILWEISE - Nicht alle Paare erfuellen Garantie")

    # GK-spezifische Erkenntnisse
    print(f"\nWL-007 Ergebnis:")
    print(f"  Analysierte Gewinnklassen: {len(results['pairs_per_gk'])}")

    # Finde GK mit staerksten Paaren
    best_gk = None
    best_lift = 0
    for gk_key, gk_data in results["pairs_per_gk"].items():
        if gk_data["top_pairs"]:
            top_lift = gk_data["top_pairs"][0].get("lift", 0)
            if top_lift > best_lift:
                best_lift = top_lift
                best_gk = gk_key

    if best_gk:
        print(f"  Staerkste GK: {best_gk} (Lift: {best_lift:.2f}x)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
