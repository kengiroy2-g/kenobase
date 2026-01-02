#!/usr/bin/env python3
"""
Test HYP_011: Regularitaet kleiner Gewinne (Axiom A3+A4)

Hypothese: Kleine Gewinne (Typ-2, 2 Treffer) sind GLEICHMAESSIGER verteilt
als bei reinem Zufall (Poisson-Prozess).

Methodik:
- Berechne Gewinn-Intervalle (Tage zwischen konsekutiven Gewinnen) pro Paar
- Berechne CV (Coefficient of Variation) = std/mean fuer beobachtete Intervalle
- Vergleiche mit theoretischem CV fuer Poisson-Prozess (CV=1)
- Acceptance: CV_observed < 1 mit p<0.05 (Bootstrap-Test)

Autor: Kenobase V2.2
Datum: 2025-12-30
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_keno_draws(path: str = "data/raw/keno/KENO_ab_2018.csv") -> pd.DataFrame:
    """Laedt KENO Ziehungen."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)

    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers"] = df[number_cols].values.tolist()
    df["numbers_set"] = df["numbers"].apply(set)

    return df


def get_strong_pairs(keno_df: pd.DataFrame, min_count: int = 200) -> List[Tuple[int, int]]:
    """Ermittelt starke Paare basierend auf Co-Occurrence."""
    pair_counts: Dict[Tuple[int, int], int] = defaultdict(int)

    for numbers in keno_df["numbers"].tolist():
        sorted_nums = sorted(numbers)
        for pair in combinations(sorted_nums, 2):
            pair_counts[pair] += 1

    strong_pairs = [(k, v) for k, v in pair_counts.items() if v >= min_count]
    strong_pairs.sort(key=lambda x: -x[1])

    return [p[0] for p in strong_pairs]


def compute_win_intervals(
    keno_df: pd.DataFrame,
    pair: Tuple[int, int]
) -> List[int]:
    """
    Berechnet Intervalle (in Ziehungen) zwischen konsekutiven Gewinnen fuer ein Paar.

    Args:
        keno_df: DataFrame mit Ziehungen
        pair: Das zu analysierende Zahlenpaar

    Returns:
        Liste von Intervallen (in Ziehungsnummern, nicht Tagen)
    """
    win_indices = []

    for idx, row in keno_df.iterrows():
        draw_set = row["numbers_set"]
        if pair[0] in draw_set and pair[1] in draw_set:
            win_indices.append(idx)

    # Berechne Intervalle zwischen konsekutiven Gewinnen
    intervals = []
    for i in range(1, len(win_indices)):
        interval = win_indices[i] - win_indices[i - 1]
        intervals.append(interval)

    return intervals


def compute_cv(intervals: List[int]) -> float:
    """
    Berechnet Coefficient of Variation (CV) = std/mean.

    Args:
        intervals: Liste von Intervallen

    Returns:
        CV-Wert (0 = perfekt regelmaessig, 1 = Poisson, >1 = geclustert)
    """
    if len(intervals) < 2:
        return float("nan")

    mean_val = np.mean(intervals)
    std_val = np.std(intervals, ddof=1)

    if mean_val == 0:
        return float("nan")

    return std_val / mean_val


def bootstrap_cv_test(
    intervals: List[int],
    n_bootstrap: int = 1000,
    null_cv: float = 1.0
) -> Tuple[float, float, float]:
    """
    Bootstrap-Test: Ist CV signifikant kleiner als null_cv?

    Args:
        intervals: Beobachtete Intervalle
        n_bootstrap: Anzahl Bootstrap-Samples
        null_cv: Erwarteter CV unter Nullhypothese (Poisson = 1.0)

    Returns:
        (observed_cv, p_value, ci_upper_95)
    """
    if len(intervals) < 5:
        return float("nan"), float("nan"), float("nan")

    observed_cv = compute_cv(intervals)

    # Bootstrap fuer Konfidenzintervall
    bootstrap_cvs = []
    arr = np.array(intervals)

    for _ in range(n_bootstrap):
        sample = np.random.choice(arr, size=len(arr), replace=True)
        if np.mean(sample) > 0:
            cv = np.std(sample, ddof=1) / np.mean(sample)
            bootstrap_cvs.append(cv)

    if len(bootstrap_cvs) < 100:
        return observed_cv, float("nan"), float("nan")

    ci_upper_95 = np.percentile(bootstrap_cvs, 95)

    # P-value: Anteil Bootstrap-Samples >= null_cv
    # Wenn CV < 1 signifikant, erwarten wir wenige Samples >= 1
    p_value = np.mean([cv >= null_cv for cv in bootstrap_cvs])

    return observed_cv, p_value, ci_upper_95


def simulate_poisson_intervals(
    n_wins: int,
    n_draws: int,
    n_simulations: int = 1000
) -> List[float]:
    """
    Simuliert CV-Verteilung unter Poisson-Nullmodell.

    Args:
        n_wins: Anzahl Gewinne
        n_draws: Anzahl Gesamtziehungen
        n_simulations: Anzahl Simulationen

    Returns:
        Liste von simulierten CVs
    """
    cvs = []
    p = n_wins / n_draws  # Gewinn-Wahrscheinlichkeit pro Ziehung

    for _ in range(n_simulations):
        # Simuliere Bernoulli-Prozess
        wins = np.random.binomial(1, p, n_draws)
        win_indices = np.where(wins == 1)[0]

        if len(win_indices) >= 3:
            intervals = np.diff(win_indices)
            if np.mean(intervals) > 0:
                cv = np.std(intervals, ddof=1) / np.mean(intervals)
                cvs.append(cv)

    return cvs


def analyze_regularity(
    keno_df: pd.DataFrame,
    pairs: List[Tuple[int, int]],
    top_n: int = 20
) -> Dict:
    """
    Fuehrt Regularitaets-Analyse fuer alle Paare durch.

    Args:
        keno_df: DataFrame mit Ziehungen
        pairs: Liste starker Paare
        top_n: Anzahl zu analysierende Paare

    Returns:
        Dict mit Analyse-Ergebnissen
    """
    results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "total_draws": len(keno_df),
            "pairs_analyzed": min(top_n, len(pairs)),
            "hypothesis": "HYP_011: Regularitaet kleiner Gewinne",
            "null_model": "Poisson-Prozess (CV=1)",
            "acceptance_criterion": "CV < 1 mit p<0.05"
        },
        "pair_results": [],
        "summary": {}
    }

    all_cvs = []
    pairs_below_1 = 0
    pairs_significant = 0

    for pair in pairs[:top_n]:
        intervals = compute_win_intervals(keno_df, pair)

        if len(intervals) < 5:
            continue

        # Grundlegende Statistiken
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals, ddof=1)
        observed_cv = compute_cv(intervals)

        # Bootstrap-Test
        _, p_value, ci_upper = bootstrap_cv_test(intervals, n_bootstrap=1000)

        # Poisson-Simulation fuer Vergleich
        n_wins = len(intervals) + 1
        poisson_cvs = simulate_poisson_intervals(n_wins, len(keno_df), 1000)
        poisson_cv_mean = np.mean(poisson_cvs) if poisson_cvs else 1.0
        poisson_cv_std = np.std(poisson_cvs) if poisson_cvs else 0.0

        # Vergleich: Wie viele Poisson-Simulationen haben CV <= observed?
        p_poisson = np.mean([cv <= observed_cv for cv in poisson_cvs]) if poisson_cvs else 0.5

        pair_result = {
            "pair": f"({pair[0]},{pair[1]})",
            "n_wins": n_wins,
            "n_intervals": len(intervals),
            "mean_interval": round(mean_interval, 2),
            "std_interval": round(std_interval, 2),
            "observed_cv": round(observed_cv, 4),
            "ci_upper_95": round(ci_upper, 4) if not np.isnan(ci_upper) else None,
            "poisson_cv_mean": round(poisson_cv_mean, 4),
            "poisson_cv_std": round(poisson_cv_std, 4),
            "p_value_poisson": round(p_poisson, 4),
            "is_more_regular": bool(observed_cv < 1.0),
            "is_significant": bool(p_poisson < 0.05)
        }

        results["pair_results"].append(pair_result)
        all_cvs.append(observed_cv)

        if observed_cv < 1.0:
            pairs_below_1 += 1
        if p_poisson < 0.05:
            pairs_significant += 1

    # Aggregierte Statistiken
    if all_cvs:
        # Binomial-Test: Sind signifikant mehr Paare regular als erwartet?
        # Unter H0 (Poisson): ~50% der CVs sollten < 1 sein (durch Varianz)
        n_total = len(all_cvs)
        binom_result = stats.binomtest(pairs_below_1, n_total, 0.5, alternative="greater")
        binom_p = binom_result.pvalue

        results["summary"] = {
            "total_pairs_analyzed": n_total,
            "pairs_with_cv_below_1": pairs_below_1,
            "pairs_significant_p005": pairs_significant,
            "mean_cv_all_pairs": round(np.mean(all_cvs), 4),
            "std_cv_all_pairs": round(np.std(all_cvs), 4),
            "median_cv": round(np.median(all_cvs), 4),
            "binomial_test_p": round(binom_p, 6),
            "hypothesis_status": "BESTAETIGT" if (
                np.mean(all_cvs) < 1.0 and binom_p < 0.05
            ) else "NICHT_BESTAETIGT"
        }

    return results


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("TEST HYP_011: REGULARITAET KLEINER GEWINNE")
    print("=" * 70)
    print()

    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    output_path = base_path / "results" / "hyp011_regularity.json"

    # Daten laden
    print("Lade Daten...")
    keno_df = load_keno_draws(str(keno_path))
    print(f"  Ziehungen: {len(keno_df)}")
    print(f"  Zeitraum: {keno_df['Datum'].min()} bis {keno_df['Datum'].max()}")
    print()

    # Starke Paare ermitteln
    print("Ermittle starke Paare...")
    strong_pairs = get_strong_pairs(keno_df, min_count=200)
    print(f"  Starke Paare (>=200x): {len(strong_pairs)}")
    print()

    # Regularitaets-Analyse
    print("Fuehre Regularitaets-Analyse durch...")
    print("  (Bootstrap n=1000, Poisson-Simulation n=1000)")
    results = analyze_regularity(keno_df, strong_pairs, top_n=20)

    # Ergebnisse ausgeben
    print("\n" + "=" * 70)
    print("ERGEBNISSE")
    print("=" * 70)

    print("\n--- TOP-5 PAARE (nach CV) ---")
    sorted_pairs = sorted(results["pair_results"], key=lambda x: x["observed_cv"])
    for pr in sorted_pairs[:5]:
        sig = "*" if pr["is_significant"] else ""
        print(f"  {pr['pair']}: CV={pr['observed_cv']:.4f} "
              f"(Poisson: {pr['poisson_cv_mean']:.4f}+/-{pr['poisson_cv_std']:.4f}) "
              f"p={pr['p_value_poisson']:.4f}{sig}")

    print("\n--- AGGREGIERTE STATISTIK ---")
    summary = results["summary"]
    print(f"  Analysierte Paare: {summary['total_pairs_analyzed']}")
    print(f"  Paare mit CV < 1: {summary['pairs_with_cv_below_1']} "
          f"({summary['pairs_with_cv_below_1']/summary['total_pairs_analyzed']*100:.1f}%)")
    print(f"  Signifikant (p<0.05): {summary['pairs_significant_p005']}")
    print(f"  Mittlerer CV: {summary['mean_cv_all_pairs']:.4f} +/- {summary['std_cv_all_pairs']:.4f}")
    print(f"  Median CV: {summary['median_cv']:.4f}")
    print(f"  Binomial-Test p: {summary['binomial_test_p']:.6f}")

    print("\n" + "=" * 70)
    print("HYP_011 VALIDIERUNG")
    print("=" * 70)
    print(f"\n  Hypothese: Kleine Gewinne sind REGELMAESSIGER als Poisson")
    print(f"  Acceptance: CV < 1 mit signifikanter Mehrheit (p<0.05)")
    print(f"\n  Status: {summary['hypothesis_status']}")

    if summary["hypothesis_status"] == "BESTAETIGT":
        print("  -> Gewinne sind gleichmaessiger verteilt als reiner Zufall")
        print("  -> Axiom A3+A4 (Spiel muss attraktiv bleiben) wird gestuetzt")
    else:
        print("  -> Gewinne folgen Poisson-Verteilung (reiner Zufall)")
        print("  -> Kein Nachweis fuer aktive Regulierung der Gewinn-Frequenz")

    # Speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")
    print("=" * 70)

    # Repro-Command
    print("\n# Repro-Command:")
    print(f"# python scripts/test_hyp011_regularity.py")


if __name__ == "__main__":
    main()
