"""
Time-Based RNG Seed Pattern Analysis
=====================================

HYPOTHESE: Der RNG-Seed koennte zeitbasiert sein (Uhrzeit, Datum, Wochentag).

Diese Analyse untersucht:
1. Wochentag-Muster (Mo-So)
2. Tag im Monat (1-31)
3. Monat (Jan-Dez)
4. Kalenderwoche (1-53)

Autor: Think Tank - Time Pattern Analyst
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


def load_keno_data(filepath: str) -> pd.DataFrame:
    """Laedt KENO-Daten aus CSV."""
    df = pd.read_csv(filepath, sep=";", decimal=",")

    # Parse Datum
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    # Extrahiere Zeitkomponenten
    df["weekday"] = df["Datum"].dt.dayofweek  # 0=Mo, 6=So
    df["weekday_name"] = df["Datum"].dt.day_name()
    df["day_of_month"] = df["Datum"].dt.day
    df["month"] = df["Datum"].dt.month
    df["month_name"] = df["Datum"].dt.month_name()
    df["calendar_week"] = df["Datum"].dt.isocalendar().week
    df["year"] = df["Datum"].dt.year

    return df


def extract_numbers(row: pd.Series) -> list[int]:
    """Extrahiert die 20 Keno-Zahlen aus einer Zeile."""
    cols = [f"Keno_Z{i}" for i in range(1, 21)]
    return [int(row[col]) for col in cols]


def calculate_number_frequencies(df: pd.DataFrame, group_col: str) -> dict[Any, dict[int, int]]:
    """Berechnet Haeufigkeiten pro Zahl fuer jede Gruppe."""
    frequencies = defaultdict(lambda: defaultdict(int))

    for _, row in df.iterrows():
        group_val = row[group_col]
        numbers = extract_numbers(row)
        for num in numbers:
            frequencies[group_val][num] += 1

    return {k: dict(v) for k, v in frequencies.items()}


def analyze_deviations(
    frequencies: dict[Any, dict[int, int]],
    total_draws_per_group: dict[Any, int]
) -> dict:
    """
    Analysiert Abweichungen von der erwarteten Haeufigkeit.

    Bei 70 moeglichen Zahlen und 20 gezogenen pro Ziehung:
    Erwartete Wahrscheinlichkeit pro Zahl = 20/70 = 0.2857 (28.57%)
    """
    EXPECTED_PROB = 20 / 70

    results = {}

    for group, freq_dict in frequencies.items():
        total_draws = total_draws_per_group[group]
        expected_per_number = total_draws * EXPECTED_PROB

        # Berechne Abweichungen fuer alle 70 Zahlen
        deviations = {}
        for num in range(1, 71):
            actual = freq_dict.get(num, 0)
            deviation = actual - expected_per_number
            deviation_percent = (deviation / expected_per_number) * 100 if expected_per_number > 0 else 0

            deviations[num] = {
                "actual": actual,
                "expected": round(expected_per_number, 2),
                "deviation": round(deviation, 2),
                "deviation_percent": round(deviation_percent, 2),
                "rate": round(actual / total_draws, 4) if total_draws > 0 else 0
            }

        # Sortiere nach Abweichung
        sorted_by_dev = sorted(deviations.items(), key=lambda x: x[1]["deviation"], reverse=True)

        # Top Performer (ueberdurchschnittlich)
        top_performers = [(num, data) for num, data in sorted_by_dev[:10]]

        # Bottom Performer (unterdurchschnittlich)
        bottom_performers = [(num, data) for num, data in sorted_by_dev[-10:]]

        results[group] = {
            "total_draws": total_draws,
            "expected_rate": round(EXPECTED_PROB, 4),
            "top_performers": {num: data for num, data in top_performers},
            "bottom_performers": {num: data for num, data in bottom_performers},
            "all_numbers": deviations
        }

    return results


def chi_square_test(frequencies: dict[int, int], total_draws: int) -> dict:
    """
    Fuehrt Chi-Quadrat-Test durch um zu pruefen ob die Verteilung
    signifikant von der Gleichverteilung abweicht.
    """
    EXPECTED_PROB = 20 / 70
    expected = total_draws * EXPECTED_PROB

    observed = [frequencies.get(num, 0) for num in range(1, 71)]
    expected_vals = [expected] * 70

    chi2, p_value = stats.chisquare(observed, expected_vals)

    return {
        "chi2_statistic": round(chi2, 4),
        "p_value": round(p_value, 6),
        "degrees_of_freedom": 69,
        "significant_at_005": p_value < 0.05,
        "significant_at_001": p_value < 0.01
    }


def find_best_numbers_for_date(
    weekday_analysis: dict,
    day_analysis: dict,
    month_analysis: dict,
    week_analysis: dict,
    target_weekday: int,
    target_day: int,
    target_month: int,
    target_week: int
) -> dict:
    """
    Findet die besten Zahlen fuer ein bestimmtes Datum basierend auf
    historischen Mustern.
    """
    # Sammle Scores fuer alle Zahlen
    number_scores = defaultdict(float)

    # Gewichte fuer verschiedene Zeiteinheiten
    WEIGHTS = {
        "weekday": 0.25,
        "day": 0.35,
        "month": 0.20,
        "week": 0.20
    }

    # Wochentag-Beitrag
    if target_weekday in weekday_analysis:
        for num, data in weekday_analysis[target_weekday]["all_numbers"].items():
            number_scores[num] += data["deviation_percent"] * WEIGHTS["weekday"]

    # Tag im Monat-Beitrag
    if target_day in day_analysis:
        for num, data in day_analysis[target_day]["all_numbers"].items():
            number_scores[num] += data["deviation_percent"] * WEIGHTS["day"]

    # Monat-Beitrag
    if target_month in month_analysis:
        for num, data in month_analysis[target_month]["all_numbers"].items():
            number_scores[num] += data["deviation_percent"] * WEIGHTS["month"]

    # Kalenderwoche-Beitrag
    if target_week in week_analysis:
        for num, data in week_analysis[target_week]["all_numbers"].items():
            number_scores[num] += data["deviation_percent"] * WEIGHTS["week"]

    # Sortiere nach kombiniertem Score
    sorted_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)

    return {
        "top_20": {num: round(score, 2) for num, score in sorted_numbers[:20]},
        "bottom_10": {num: round(score, 2) for num, score in sorted_numbers[-10:]},
        "target_info": {
            "weekday": target_weekday,
            "day_of_month": target_day,
            "month": target_month,
            "calendar_week": target_week
        }
    }


def identify_strong_patterns(analysis: dict, threshold: float = 10.0) -> list[dict]:
    """
    Identifiziert statistisch auffaellige Muster (Abweichung > threshold%).
    """
    strong_patterns = []

    for group, data in analysis.items():
        for num, num_data in data["top_performers"].items():
            if num_data["deviation_percent"] > threshold:
                strong_patterns.append({
                    "group": group,
                    "number": num,
                    "deviation_percent": num_data["deviation_percent"],
                    "actual_rate": num_data["rate"],
                    "expected_rate": data["expected_rate"],
                    "sample_size": data["total_draws"]
                })

        for num, num_data in data["bottom_performers"].items():
            if num_data["deviation_percent"] < -threshold:
                strong_patterns.append({
                    "group": group,
                    "number": num,
                    "deviation_percent": num_data["deviation_percent"],
                    "actual_rate": num_data["rate"],
                    "expected_rate": data["expected_rate"],
                    "sample_size": data["total_draws"]
                })

    return sorted(strong_patterns, key=lambda x: abs(x["deviation_percent"]), reverse=True)


def analyze_correlations(df: pd.DataFrame) -> dict:
    """
    Analysiert Korrelationen zwischen Zeitkomponenten und Zahlenhaeufigkeiten.
    """
    correlations = {}

    for num in range(1, 71):
        # Erstelle Indikator ob Zahl in Ziehung war
        df[f"has_{num}"] = df.apply(
            lambda row: 1 if num in extract_numbers(row) else 0,
            axis=1
        )

    # Korrelationen berechnen
    time_cols = ["weekday", "day_of_month", "month", "calendar_week"]
    number_cols = [f"has_{num}" for num in range(1, 71)]

    for time_col in time_cols:
        corr_data = {}
        for num in range(1, 71):
            corr, p_value = stats.pointbiserialr(df[time_col], df[f"has_{num}"])
            if abs(corr) > 0.05:  # Nur relevante Korrelationen
                corr_data[num] = {
                    "correlation": round(corr, 4),
                    "p_value": round(p_value, 6),
                    "significant": p_value < 0.05
                }
        correlations[time_col] = corr_data

    # Aufr aeumen
    for num in range(1, 71):
        df.drop(f"has_{num}", axis=1, inplace=True)

    return correlations


def main():
    # Pfade
    data_path = Path("C:/Users/kenfu/Documents/keno_base/data/raw/keno/KENO_ab_2022_bereinigt.csv")
    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/think_tank_time.json")

    print("=" * 60)
    print("TIME-BASED RNG SEED PATTERN ANALYSIS")
    print("=" * 60)

    # Daten laden
    print("\n[1] Lade KENO-Daten...")
    df = load_keno_data(str(data_path))
    print(f"    Geladen: {len(df)} Ziehungen")
    print(f"    Zeitraum: {df['Datum'].min().date()} bis {df['Datum'].max().date()}")

    # Haeufigkeiten berechnen
    print("\n[2] Berechne Haeufigkeiten nach Zeiteinheiten...")

    weekday_freq = calculate_number_frequencies(df, "weekday")
    day_freq = calculate_number_frequencies(df, "day_of_month")
    month_freq = calculate_number_frequencies(df, "month")
    week_freq = calculate_number_frequencies(df, "calendar_week")

    # Ziehungen pro Gruppe
    weekday_counts = df.groupby("weekday").size().to_dict()
    day_counts = df.groupby("day_of_month").size().to_dict()
    month_counts = df.groupby("month").size().to_dict()
    week_counts = df.groupby("calendar_week").size().to_dict()

    print(f"    Wochentage: {dict(weekday_counts)}")
    print(f"    Monate (Ziehungen): {dict(month_counts)}")

    # Abweichungen analysieren
    print("\n[3] Analysiere Abweichungen von Gleichverteilung...")

    weekday_analysis = analyze_deviations(weekday_freq, weekday_counts)
    day_analysis = analyze_deviations(day_freq, day_counts)
    month_analysis = analyze_deviations(month_freq, month_counts)
    week_analysis = analyze_deviations(week_freq, week_counts)

    # Chi-Quadrat-Tests
    print("\n[4] Fuehre Chi-Quadrat-Tests durch...")

    chi2_results = {
        "weekday": {},
        "day_of_month": {},
        "month": {},
        "calendar_week": {}
    }

    for day in range(7):
        if day in weekday_freq:
            chi2_results["weekday"][day] = chi_square_test(weekday_freq[day], weekday_counts[day])

    for day in range(1, 32):
        if day in day_freq:
            chi2_results["day_of_month"][day] = chi_square_test(day_freq[day], day_counts[day])

    for month in range(1, 13):
        if month in month_freq:
            chi2_results["month"][month] = chi_square_test(month_freq[month], month_counts[month])

    # Signifikante Chi2-Ergebnisse
    significant_chi2 = []
    for category, results in chi2_results.items():
        for group, data in results.items():
            if data["significant_at_005"]:
                significant_chi2.append({
                    "category": category,
                    "group": group,
                    "chi2": data["chi2_statistic"],
                    "p_value": data["p_value"]
                })

    print(f"    Signifikante Abweichungen (p<0.05): {len(significant_chi2)}")

    # Starke Muster identifizieren
    print("\n[5] Identifiziere starke Muster (>10% Abweichung)...")

    strong_weekday = identify_strong_patterns(weekday_analysis, threshold=10.0)
    strong_day = identify_strong_patterns(day_analysis, threshold=15.0)  # Hoehere Schwelle wegen weniger Daten
    strong_month = identify_strong_patterns(month_analysis, threshold=8.0)

    print(f"    Wochentag-Muster: {len(strong_weekday)}")
    print(f"    Tag-im-Monat-Muster: {len(strong_day)}")
    print(f"    Monats-Muster: {len(strong_month)}")

    # Spezifische Analyse: Dienstag der 15.
    print("\n[6] Spezifische Analyse: Dienstag der 15. (aktuelles Datum-Beispiel)...")

    # Aktuelles Datum analysieren
    today = datetime.now()
    target_weekday = today.weekday()  # 0=Mo
    target_day = today.day
    target_month = today.month
    target_week = today.isocalendar().week

    # Beispiel: Dienstag (1) der 15.
    tuesday_15_analysis = find_best_numbers_for_date(
        weekday_analysis, day_analysis, month_analysis, week_analysis,
        target_weekday=1,  # Dienstag
        target_day=15,
        target_month=target_month,
        target_week=target_week
    )

    # Heute-Analyse
    today_analysis = find_best_numbers_for_date(
        weekday_analysis, day_analysis, month_analysis, week_analysis,
        target_weekday=target_weekday,
        target_day=target_day,
        target_month=target_month,
        target_week=target_week
    )

    print(f"    Top 5 fuer Dienstag 15.: {list(tuesday_15_analysis['top_20'].keys())[:5]}")
    print(f"    Top 5 fuer heute ({today.strftime('%A %d.%m.')}): {list(today_analysis['top_20'].keys())[:5]}")

    # Korrelationsanalyse
    print("\n[7] Berechne Zeit-Zahlen-Korrelationen...")
    correlations = analyze_correlations(df)

    significant_correlations = []
    for time_col, corr_data in correlations.items():
        for num, data in corr_data.items():
            if data["significant"]:
                significant_correlations.append({
                    "time_component": time_col,
                    "number": num,
                    "correlation": data["correlation"],
                    "p_value": data["p_value"]
                })

    print(f"    Signifikante Korrelationen: {len(significant_correlations)}")

    # Erstelle Kompakt-Summaries
    def create_compact_summary(analysis: dict, name: str) -> dict:
        """Erstellt kompakte Zusammenfassung."""
        summary = {}
        for group, data in analysis.items():
            top_nums = [num for num in data["top_performers"].keys()]
            bottom_nums = [num for num in data["bottom_performers"].keys()]
            summary[str(group)] = {
                "draws": data["total_draws"],
                "hot_numbers": top_nums[:5],
                "cold_numbers": bottom_nums[:5]
            }
        return summary

    # Ergebnis zusammenstellen
    results = {
        "hypothesis": {
            "name": "Time-Based RNG Seed Pattern",
            "description": "Der RNG-Seed koennte zeitbasiert sein (Uhrzeit, Datum, Wochentag)",
            "analyst": "Think Tank - Time Pattern",
            "date": datetime.now().isoformat()
        },
        "data_summary": {
            "total_draws": len(df),
            "date_range": {
                "start": df["Datum"].min().strftime("%Y-%m-%d"),
                "end": df["Datum"].max().strftime("%Y-%m-%d")
            },
            "draws_by_weekday": {
                "Monday": weekday_counts.get(0, 0),
                "Tuesday": weekday_counts.get(1, 0),
                "Wednesday": weekday_counts.get(2, 0),
                "Thursday": weekday_counts.get(3, 0),
                "Friday": weekday_counts.get(4, 0),
                "Saturday": weekday_counts.get(5, 0),
                "Sunday": weekday_counts.get(6, 0)
            }
        },
        "weekday_patterns": {
            "summary": create_compact_summary(weekday_analysis, "weekday"),
            "strong_patterns": strong_weekday[:20],
            "chi2_tests": {
                "Monday": chi2_results["weekday"].get(0, {}),
                "Tuesday": chi2_results["weekday"].get(1, {}),
                "Wednesday": chi2_results["weekday"].get(2, {}),
                "Thursday": chi2_results["weekday"].get(3, {}),
                "Friday": chi2_results["weekday"].get(4, {}),
                "Saturday": chi2_results["weekday"].get(5, {}),
                "Sunday": chi2_results["weekday"].get(6, {})
            }
        },
        "day_of_month_patterns": {
            "summary": create_compact_summary(day_analysis, "day"),
            "strong_patterns": strong_day[:30],
            "most_significant_days": sorted(
                [(d, chi2_results["day_of_month"].get(d, {}).get("p_value", 1.0))
                 for d in range(1, 32) if d in chi2_results["day_of_month"]],
                key=lambda x: x[1]
            )[:10]
        },
        "month_patterns": {
            "summary": create_compact_summary(month_analysis, "month"),
            "strong_patterns": strong_month[:20],
            "chi2_tests": {
                month: chi2_results["month"].get(month, {})
                for month in range(1, 13)
            }
        },
        "calendar_week_patterns": {
            "summary": create_compact_summary(week_analysis, "week"),
            "weeks_with_extreme_patterns": sorted(
                [(w, len([p for p in identify_strong_patterns({w: week_analysis[w]}, 12.0)]))
                 for w in week_analysis.keys()],
                key=lambda x: x[1], reverse=True
            )[:10]
        },
        "correlations": {
            "significant_count": len(significant_correlations),
            "top_correlations": sorted(
                significant_correlations,
                key=lambda x: abs(x["correlation"]),
                reverse=True
            )[:20]
        },
        "specific_predictions": {
            "tuesday_15th": tuesday_15_analysis,
            "today": {
                **today_analysis,
                "date": today.strftime("%Y-%m-%d"),
                "weekday_name": today.strftime("%A")
            }
        },
        "statistical_significance": {
            "chi2_significant_groups": significant_chi2,
            "total_significant": len(significant_chi2),
            "interpretation": (
                "SIGNIFIKANT: Abweichungen von Gleichverteilung gefunden"
                if len(significant_chi2) > 5
                else "NICHT SIGNIFIKANT: Keine starken zeitbasierten Muster"
            )
        },
        "hypothesis_verdict": {
            "supported": len(significant_chi2) > 5 and len(significant_correlations) > 10,
            "confidence": "LOW" if len(significant_chi2) < 3 else "MEDIUM" if len(significant_chi2) < 10 else "HIGH",
            "reasoning": "",
            "recommendation": ""
        }
    }

    # Reasoning basierend auf Ergebnissen
    if results["hypothesis_verdict"]["supported"]:
        results["hypothesis_verdict"]["reasoning"] = (
            f"Es wurden {len(significant_chi2)} signifikante Chi2-Abweichungen und "
            f"{len(significant_correlations)} signifikante Korrelationen gefunden. "
            "Dies deutet darauf hin, dass zeitbasierte Muster existieren koennten."
        )
        results["hypothesis_verdict"]["recommendation"] = (
            "Weitere Untersuchung empfohlen. Die Zahlen aus 'specific_predictions' "
            "sollten in einem Backtest validiert werden."
        )
    else:
        results["hypothesis_verdict"]["reasoning"] = (
            f"Mit nur {len(significant_chi2)} signifikanten Chi2-Abweichungen und "
            f"{len(significant_correlations)} Korrelationen ist die Evidenz schwach. "
            "Die Abweichungen liegen im Rahmen statistischer Fluktuation."
        )
        results["hypothesis_verdict"]["recommendation"] = (
            "Die Hypothese wird nicht durch die Daten gestuetzt. "
            "Zeitbasierte Muster scheinen keine zuverlaessige Vorhersagekraft zu haben."
        )

    # Detailierte Wochentags-Hot/Cold Numbers
    weekday_hot_cold = {}
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day_num in range(7):
        if day_num in weekday_analysis:
            hot = list(weekday_analysis[day_num]["top_performers"].keys())[:10]
            cold = list(weekday_analysis[day_num]["bottom_performers"].keys())[:10]
            weekday_hot_cold[weekday_names[day_num]] = {
                "hot_numbers": hot,
                "cold_numbers": cold,
                "draws": weekday_analysis[day_num]["total_draws"]
            }
    results["weekday_hot_cold"] = weekday_hot_cold

    # Speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n{'=' * 60}")
    print("ANALYSE ABGESCHLOSSEN")
    print(f"{'=' * 60}")
    print(f"\nErgebnisse gespeichert: {output_path}")
    print(f"\nZUSAMMENFASSUNG:")
    print(f"  - Chi2 signifikante Gruppen: {len(significant_chi2)}")
    print(f"  - Signifikante Korrelationen: {len(significant_correlations)}")
    print(f"  - Hypothese unterstuetzt: {results['hypothesis_verdict']['supported']}")
    print(f"  - Konfidenz: {results['hypothesis_verdict']['confidence']}")

    return results


if __name__ == "__main__":
    main()
