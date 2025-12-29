#!/usr/bin/env python3
"""Schnelle Hypothesen-Validierung fuer Kenobase.

Validiert 3 Hypothesen:
- HYP-009: Chi-Quadrat-Test auf Gleichverteilung
- HYP-005: Zahlenpool-Index korreliert mit Treffern
- HYP-002: Jackpot-Zyklen zeigen Muster

Usage:
    python scripts/validate_hypotheses.py --hypothesis HYP-009
    python scripts/validate_hypotheses.py --all
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

# Acceptance Criteria
P_VALUE_THRESHOLD = 0.05  # Signifikanz fuer Chi-Quadrat
CORRELATION_THRESHOLD = 0.3  # Mindest-Korrelation


def load_keno_data(filepath: Path) -> pd.DataFrame:
    """Laedt KENO-Ziehungsdaten aus CSV."""
    df = pd.read_csv(filepath, sep=";", encoding="utf-8")
    # Datum parsen (deutsches Format)
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df


def load_gk1_data(filepath: Path) -> pd.DataFrame:
    """Laedt GK1-Daten (Gewinnklasse 1 Events)."""
    df = pd.read_csv(filepath, encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df


def extract_numbers(df: pd.DataFrame) -> list[list[int]]:
    """Extrahiert Zahlen aus KENO-DataFrame (Spalten Keno_Z1 bis Keno_Z20)."""
    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    draws = []
    for _, row in df.iterrows():
        numbers = [int(row[col]) for col in number_cols if pd.notna(row[col])]
        draws.append(numbers)
    return draws


def validate_hyp009_chi_quadrat(draws: list[list[int]], number_range: int = 70) -> dict[str, Any]:
    """HYP-009: Chi-Quadrat-Test auf Gleichverteilung.

    Nullhypothese: Alle Zahlen 1-70 sind gleichverteilt.
    Akzeptanzkriterium: p-Wert < 0.05 -> Hypothese abgelehnt.

    Args:
        draws: Liste von Ziehungen (20 Zahlen pro Ziehung)
        number_range: Zahlenbereich (1 bis number_range)

    Returns:
        Dict mit chi2, p_value, status, interpretation
    """
    # Zaehle alle Zahlen
    counter: Counter[int] = Counter()
    for draw in draws:
        counter.update(draw)

    # Beobachtete Haeufigkeiten (fuer alle Zahlen 1-70)
    observed = [counter.get(i, 0) for i in range(1, number_range + 1)]

    # Erwartete Haeufigkeiten bei Gleichverteilung
    total_numbers = sum(observed)
    expected = [total_numbers / number_range] * number_range

    # Chi-Quadrat-Test
    chi2, p_value = stats.chisquare(observed, expected)

    # Interpretation
    if p_value < P_VALUE_THRESHOLD:
        status = "REJECTED"
        interpretation = (
            f"Gleichverteilung abgelehnt (p={p_value:.4f} < {P_VALUE_THRESHOLD}). "
            "Zahlen sind NICHT gleichverteilt - moeglicherweise Muster vorhanden."
        )
    else:
        status = "ACCEPTED"
        interpretation = (
            f"Gleichverteilung kann nicht abgelehnt werden (p={p_value:.4f} >= {P_VALUE_THRESHOLD}). "
            "Zahlen erscheinen zufaellig verteilt."
        )

    return {
        "hypothesis": "HYP-009",
        "test": "Chi-Quadrat Gleichverteilungstest",
        "n_draws": len(draws),
        "n_numbers": total_numbers,
        "chi2_statistic": float(chi2),
        "p_value": float(p_value),
        "threshold": P_VALUE_THRESHOLD,
        "status": status,
        "interpretation": interpretation,
        "observed_min": min(observed),
        "observed_max": max(observed),
        "expected_per_number": expected[0],
    }


def validate_hyp005_zahlenpool_index(
    draws: list[list[int]], window: int = 10
) -> dict[str, Any]:
    """HYP-005: Zahlenpool-Index korreliert mit Treffern (Simple Window).

    Hypothese: Haeufige Zahlen der letzten N Ziehungen erscheinen oefter.
    Akzeptanzkriterium: Korrelation r > 0.3

    Args:
        draws: Liste von Ziehungen
        window: Fenstergroesse fuer Zahlenpool

    Returns:
        Dict mit correlation, p_value, status
    """
    if len(draws) < window + 10:
        return {
            "hypothesis": "HYP-005",
            "status": "INSUFFICIENT_DATA",
            "interpretation": f"Mindestens {window + 10} Ziehungen benoetigt.",
        }

    # Fuer jede Ziehung (ab window):
    # - Berechne Top-11 der letzten window Ziehungen
    # - Pruefe wie viele der naechsten Ziehung im Pool sind
    pool_sizes = []
    actual_hits = []

    for i in range(window, len(draws)):
        # Top-11 aus den letzten window Ziehungen
        counter: Counter[int] = Counter()
        for j in range(i - window, i):
            counter.update(draws[j])
        top11 = [num for num, _ in counter.most_common(11)]

        # Wie viele der naechsten Ziehung sind im Pool?
        next_draw = draws[i]
        hits = len(set(next_draw) & set(top11))

        pool_sizes.append(len(top11))
        actual_hits.append(hits)

    # Korrelation zwischen Pool-Groesse und Hits
    # Da Pool-Groesse konstant ist, berechnen wir Trefferquote
    hit_rates = [h / 20 for h in actual_hits]  # 20 Zahlen pro Ziehung
    expected_random = 11 / 70 * 20  # Erwartung bei Zufall: 11/70 * 20 = 3.14

    # t-Test: Sind die Treffer signifikant hoeher als Zufall?
    t_stat, t_pvalue = stats.ttest_1samp(actual_hits, expected_random)

    mean_hits = np.mean(actual_hits)
    std_hits = np.std(actual_hits)

    # Effect Size (Cohen's d)
    cohens_d = (mean_hits - expected_random) / std_hits if std_hits > 0 else 0

    if t_pvalue < P_VALUE_THRESHOLD and mean_hits > expected_random:
        status = "CONFIRMED"
        interpretation = (
            f"Zahlenpool-Index signifikant besser als Zufall. "
            f"Durchschnitt: {mean_hits:.2f} Treffer vs. erwartet: {expected_random:.2f}. "
            f"Effect Size (Cohen's d): {cohens_d:.2f}"
        )
    else:
        status = "REJECTED"
        interpretation = (
            f"Zahlenpool-Index nicht signifikant besser als Zufall. "
            f"Durchschnitt: {mean_hits:.2f} Treffer vs. erwartet: {expected_random:.2f}."
        )

    return {
        "hypothesis": "HYP-005",
        "test": "Zahlenpool-Index Vorhersagekraft",
        "n_predictions": len(actual_hits),
        "window_size": window,
        "mean_hits": float(mean_hits),
        "std_hits": float(std_hits),
        "expected_random": float(expected_random),
        "t_statistic": float(t_stat),
        "p_value": float(t_pvalue),
        "cohens_d": float(cohens_d),
        "status": status,
        "interpretation": interpretation,
    }


def validate_hyp005_gk1_reset(
    keno_df: pd.DataFrame, gk1_df: pd.DataFrame, top_n: int = 11
) -> dict[str, Any]:
    """HYP-005: Index-System mit GK1-Reset.

    Hypothese: Zahlen-Index (Haeufigkeit seit letztem GK1-Event) korreliert
    mit Erscheinen in naechster Ziehung.

    Args:
        keno_df: DataFrame mit KENO-Ziehungsdaten
        gk1_df: DataFrame mit GK1-Events
        top_n: Anzahl Top-Zahlen fuer Vorhersage

    Returns:
        Dict mit correlation, index_table, status
    """
    from kenobase.analysis.number_index import (
        calculate_index_correlation,
        calculate_index_table,
        export_index_table,
    )

    # Konvertiere DataFrames zu Tuple-Listen
    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    draws: list[tuple[datetime, list[int]]] = []

    for _, row in keno_df.iterrows():
        date = row["Datum"].to_pydatetime() if hasattr(row["Datum"], "to_pydatetime") else row["Datum"]
        numbers = [int(row[col]) for col in number_cols if pd.notna(row[col])]
        draws.append((date, numbers))

    # GK1-Events extrahieren
    gk1_events: list[tuple[datetime, int]] = []
    for _, row in gk1_df.iterrows():
        date = row["Datum"].to_pydatetime() if hasattr(row["Datum"], "to_pydatetime") else row["Datum"]
        keno_typ = int(row["Keno-Typ"]) if pd.notna(row.get("Keno-Typ")) else 10
        gk1_events.append((date, keno_typ))

    if len(draws) < 50:
        return {
            "hypothesis": "HYP-005-GK1",
            "status": "INSUFFICIENT_DATA",
            "interpretation": f"Mindestens 50 Ziehungen benoetigt, nur {len(draws)} vorhanden.",
        }

    if len(gk1_events) < 3:
        return {
            "hypothesis": "HYP-005-GK1",
            "status": "INSUFFICIENT_DATA",
            "interpretation": f"Mindestens 3 GK1-Events benoetigt, nur {len(gk1_events)} vorhanden.",
        }

    # Berechne aktuelle Index-Tabelle
    index_result = calculate_index_table(draws, gk1_events, number_range=70)

    # Korrelationsanalyse
    corr_result = calculate_index_correlation(draws, gk1_events, number_range=70, top_n=top_n)

    # Exportiere Index-Tabelle
    output_path = Path("data/results/hyp005_index_table.json")
    export_index_table(index_result, str(output_path))

    # Status bestimmen
    if corr_result.p_value < P_VALUE_THRESHOLD and corr_result.mean_hits_high_index > corr_result.mean_hits_low_index:
        status = "CONFIRMED"
    elif corr_result.mean_hits_high_index > (top_n / 70 * 20) * 1.1:
        status = "TREND"
    else:
        status = "REJECTED"

    return {
        "hypothesis": "HYP-005-GK1",
        "test": "Index-System mit GK1-Reset",
        "n_draws": len(draws),
        "n_gk1_events": len(gk1_events),
        "n_segments": corr_result.n_segments,
        "last_reset_date": index_result.last_reset_date.isoformat() if index_result.last_reset_date else None,
        "draws_since_reset": index_result.draws_since_reset,
        "gk1_event_type": index_result.gk1_event_type,
        "top_n": top_n,
        "mean_hits_high_index": float(corr_result.mean_hits_high_index),
        "mean_hits_low_index": float(corr_result.mean_hits_low_index),
        "expected_random": float(top_n / 70 * 20),
        "p_value": float(corr_result.p_value),
        "effect_size": float(corr_result.effect_size),
        "correlation": float(corr_result.correlation),
        "status": status,
        "interpretation": corr_result.interpretation,
        "index_table_path": str(output_path),
    }


def validate_hyp002_jackpot_zyklen(gk1_df: pd.DataFrame) -> dict[str, Any]:
    """HYP-002: Jackpot-Zyklen zeigen Muster.

    Hypothese: Zeitintervalle zwischen GK1-Events sind nicht zufaellig.
    Akzeptanzkriterium: p-Wert < 0.05 (nicht-exponentiell verteilt)

    Extended Analysis (HYP-002 v2):
    - Calendar correlation (weekday, month, holiday proximity)
    - Poisson-based prediction model

    Args:
        gk1_df: DataFrame mit GK1-Daten

    Returns:
        Dict mit test results including calendar analysis and prediction
    """
    from kenobase.analysis.calendar_features import (
        analyze_calendar_correlation,
        predict_next_gk1,
        to_dict as calendar_to_dict,
    )

    if len(gk1_df) < 5:
        return {
            "hypothesis": "HYP-002",
            "status": "INSUFFICIENT_DATA",
            "interpretation": "Mindestens 5 GK1-Events benoetigt.",
        }

    # Zeitintervalle aus der Spalte "Vergangene Tage seit dem letzten Gewinnklasse 1"
    intervals = gk1_df["Vergangene Tage seit dem letzten Gewinnklasse 1"].dropna().values
    intervals = [int(x) for x in intervals if x > 0]  # Nur positive Intervalle

    if len(intervals) < 5:
        return {
            "hypothesis": "HYP-002",
            "status": "INSUFFICIENT_DATA",
            "interpretation": f"Nur {len(intervals)} positive Intervalle gefunden.",
        }

    # Kolmogorov-Smirnov Test gegen Exponentialverteilung
    # Bei echtem Zufall sollten Intervalle exponentiell verteilt sein
    intervals_arr = np.array(intervals, dtype=float)
    mean_interval = np.mean(intervals_arr)

    # Fit Exponential: scale = mean
    ks_stat, ks_pvalue = stats.kstest(
        intervals_arr,
        "expon",
        args=(0, mean_interval)  # loc=0, scale=mean
    )

    # Zusaetzlich: Runs-Test fuer Zufaelligkeit
    median_interval = np.median(intervals_arr)
    above_median = [1 if x > median_interval else 0 for x in intervals_arr]

    # Zaehle Runs (Wechsel zwischen 0 und 1)
    n_runs = 1
    for i in range(1, len(above_median)):
        if above_median[i] != above_median[i-1]:
            n_runs += 1

    n1 = sum(above_median)
    n2 = len(above_median) - n1

    # Erwarteter Wert und Varianz fuer Runs
    if n1 > 0 and n2 > 0:
        expected_runs = (2 * n1 * n2) / (n1 + n2) + 1
        var_runs = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
        z_runs = (n_runs - expected_runs) / np.sqrt(var_runs) if var_runs > 0 else 0
        runs_pvalue = 2 * (1 - stats.norm.cdf(abs(z_runs)))
    else:
        expected_runs = 0
        z_runs = 0
        runs_pvalue = 1.0

    # Calendar Analysis (NEW)
    dates = gk1_df["Datum"].tolist()
    # Convert to datetime if needed
    dates = [d.to_pydatetime() if hasattr(d, "to_pydatetime") else d for d in dates]
    calendar_result = analyze_calendar_correlation(dates)
    calendar_dict = calendar_to_dict(calendar_result)

    # Prediction Model (NEW)
    last_event_date = max(dates)
    prediction = predict_next_gk1(intervals, last_event_date)

    # Interpretation
    if ks_pvalue < P_VALUE_THRESHOLD:
        status = "PATTERN_DETECTED"
        interpretation = (
            f"Intervalle sind NICHT exponentiell verteilt (KS p={ks_pvalue:.4f}). "
            f"Moeglicherweise Zyklen oder Cluster vorhanden."
        )
    else:
        status = "RANDOM"
        interpretation = (
            f"Intervalle erscheinen zufaellig (KS p={ks_pvalue:.4f}). "
            f"Keine signifikanten Zyklen erkannt."
        )

    # Add calendar findings to interpretation
    if calendar_result.weekday_p_value < P_VALUE_THRESHOLD:
        interpretation += f" Wochentagsmuster erkannt."
    if calendar_result.month_p_value < P_VALUE_THRESHOLD:
        interpretation += f" Monatsmuster erkannt."

    return {
        "hypothesis": "HYP-002",
        "test": "Jackpot-Zyklen Analyse (erweitert)",
        "n_events": len(gk1_df),
        "n_intervals": len(intervals),
        "mean_interval_days": float(mean_interval),
        "median_interval_days": float(median_interval),
        "min_interval": int(min(intervals)),
        "max_interval": int(max(intervals)),
        "ks_statistic": float(ks_stat),
        "ks_p_value": float(ks_pvalue),
        "runs_test_z": float(z_runs),
        "runs_p_value": float(runs_pvalue),
        "calendar_analysis": calendar_dict,
        "prediction": prediction,
        "status": status,
        "interpretation": interpretation,
    }


def main() -> int:
    """Hauptfunktion."""
    parser = argparse.ArgumentParser(
        description="Validiere Kenobase Hypothesen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--hypothesis",
        choices=["HYP-009", "HYP-005", "HYP-005-GK1", "HYP-002"],
        help="Spezifische Hypothese validieren",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Alle Hypothesen validieren",
    )
    parser.add_argument(
        "--keno-data",
        type=Path,
        default=Path("data/raw/keno/KENO_ab_2018.csv"),
        help="Pfad zu KENO-Ziehungsdaten",
    )
    parser.add_argument(
        "--gk1-data",
        type=Path,
        default=Path("Keno_GPTs/10-9_KGDaten_gefiltert.csv"),
        help="Pfad zu GK1-Daten",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="JSON-Ausgabedatei (optional)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Ausfuehrliche Ausgabe",
    )

    args = parser.parse_args()

    if not args.hypothesis and not args.all:
        parser.print_help()
        return 1

    results: list[dict[str, Any]] = []

    # Lade Daten
    keno_df = None
    gk1_df = None
    draws = None

    hypotheses_to_run = []
    if args.all:
        hypotheses_to_run = ["HYP-009", "HYP-005", "HYP-005-GK1", "HYP-002"]
    elif args.hypothesis:
        hypotheses_to_run = [args.hypothesis]

    # HYP-009, HYP-005, HYP-005-GK1 brauchen KENO-Daten
    if "HYP-009" in hypotheses_to_run or "HYP-005" in hypotheses_to_run or "HYP-005-GK1" in hypotheses_to_run:
        if not args.keno_data.exists():
            print(f"FEHLER: KENO-Daten nicht gefunden: {args.keno_data}")
            return 1
        print(f"Lade KENO-Daten aus {args.keno_data}...")
        keno_df = load_keno_data(args.keno_data)
        draws = extract_numbers(keno_df)
        print(f"  -> {len(draws)} Ziehungen geladen")

    # HYP-002 und HYP-005-GK1 brauchen GK1-Daten
    if "HYP-002" in hypotheses_to_run or "HYP-005-GK1" in hypotheses_to_run:
        if not args.gk1_data.exists():
            print(f"FEHLER: GK1-Daten nicht gefunden: {args.gk1_data}")
            return 1
        print(f"Lade GK1-Daten aus {args.gk1_data}...")
        gk1_df = load_gk1_data(args.gk1_data)
        print(f"  -> {len(gk1_df)} Events geladen")

    print("\n" + "=" * 60)

    # Validierungen durchfuehren
    if "HYP-009" in hypotheses_to_run and draws:
        print("\nValidiere HYP-009: Chi-Quadrat Gleichverteilungstest...")
        result = validate_hyp009_chi_quadrat(draws)
        results.append(result)
        print(f"  Status: {result['status']}")
        print(f"  Chi2: {result['chi2_statistic']:.2f}, p-Wert: {result['p_value']:.4f}")
        print(f"  -> {result['interpretation']}")

    if "HYP-005" in hypotheses_to_run and draws:
        print("\nValidiere HYP-005: Zahlenpool-Index Vorhersagekraft...")
        result = validate_hyp005_zahlenpool_index(draws)
        results.append(result)
        print(f"  Status: {result['status']}")
        if "mean_hits" in result:
            print(f"  Durchschnitt: {result['mean_hits']:.2f} Treffer (erwartet: {result['expected_random']:.2f})")
            print(f"  p-Wert: {result['p_value']:.4f}, Cohen's d: {result['cohens_d']:.2f}")
        print(f"  -> {result.get('interpretation', 'N/A')}")

    if "HYP-005-GK1" in hypotheses_to_run and keno_df is not None and gk1_df is not None:
        print("\nValidiere HYP-005-GK1: Index-System mit GK1-Reset...")
        result = validate_hyp005_gk1_reset(keno_df, gk1_df)
        results.append(result)
        print(f"  Status: {result['status']}")
        if "mean_hits_high_index" in result:
            print(f"  Letzer Reset: {result.get('last_reset_date', 'N/A')} (Typ {result.get('gk1_event_type', 'N/A')})")
            print(f"  Ziehungen seit Reset: {result.get('draws_since_reset', 'N/A')}")
            print(f"  High-Index Treffer: {result['mean_hits_high_index']:.2f} vs. Low-Index: {result['mean_hits_low_index']:.2f}")
            print(f"  p-Wert: {result['p_value']:.4f}, Effect Size: {result['effect_size']:.2f}")
            if result.get('index_table_path'):
                print(f"  Index-Tabelle: {result['index_table_path']}")
        print(f"  -> {result.get('interpretation', 'N/A')}")

    if "HYP-002" in hypotheses_to_run and gk1_df is not None:
        print("\nValidiere HYP-002: Jackpot-Zyklen Analyse...")
        result = validate_hyp002_jackpot_zyklen(gk1_df)
        results.append(result)
        print(f"  Status: {result['status']}")
        if "mean_interval_days" in result:
            print(f"  Durchschnittliches Intervall: {result['mean_interval_days']:.1f} Tage")
            print(f"  KS-Test p-Wert: {result['ks_p_value']:.4f}")
        print(f"  -> {result.get('interpretation', 'N/A')}")

    print("\n" + "=" * 60)

    # Zusammenfassung
    print("\nZUSAMMENFASSUNG:")
    for r in results:
        status_icon = {
            "CONFIRMED": "[+]",
            "REJECTED": "[-]",
            "ACCEPTED": "[=]",
            "PATTERN_DETECTED": "[!]",
            "RANDOM": "[~]",
            "INSUFFICIENT_DATA": "[?]",
        }.get(r["status"], "[?]")
        print(f"  {status_icon} {r['hypothesis']}: {r['status']}")

    # JSON-Ausgabe
    if args.output:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nErgebnisse gespeichert in: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
