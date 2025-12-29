#!/usr/bin/env python3
"""
WL-006: Uniqueness-Score fuer Jackpot-Kandidaten

Analysiert alle GK1-Events und berechnet Uniqueness-Kriterien.
Ziel: Identifiziere Kombinationen die Jackpot-wuerdig sind.

Autor: Kenobase V2.2
Datum: 2025-12-29
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np


def load_keno_draws(path: str = "data/raw/keno/KENO_ab_2018.csv") -> pd.DataFrame:
    """Laedt KENO Ziehungen."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

    number_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers"] = df[number_cols].values.tolist()

    return df


def load_gk1_events(path: str = "Keno_GPTs/10-9_KGDaten_gefiltert.csv") -> pd.DataFrame:
    """Laedt GK1 (Jackpot) Events."""
    df = pd.read_csv(path, encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df


def calculate_anti_birthday_score(numbers: List[int]) -> float:
    """
    Berechnet Anti-Birthday Score.
    Hoher Score = viele Zahlen ueber 31 (unbeliebte Zahlen).
    """
    above_31 = sum(1 for n in numbers if n > 31)
    return above_31 / len(numbers)


def calculate_consecutive_pairs(numbers: List[int]) -> int:
    """Zaehlt konsekutive Paare (z.B. 5,6 oder 23,24)."""
    sorted_nums = sorted(numbers)
    consecutive = 0
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i + 1] - sorted_nums[i] == 1:
            consecutive += 1
    return consecutive


def calculate_decade_distribution(numbers: List[int]) -> Tuple[float, Dict]:
    """
    Berechnet Dekaden-Verteilung (1-10, 11-20, ..., 61-70).
    Gute Verteilung = niedrige Varianz.
    """
    decades = {i: 0 for i in range(1, 8)}  # 7 Dekaden

    for n in numbers:
        decade = min((n - 1) // 10 + 1, 7)
        decades[decade] += 1

    values = list(decades.values())
    mean_val = np.mean(values)
    variance = np.var(values)

    # Normalisiere: niedrige Varianz = hoher Score
    # Perfekte Verteilung waere 20/7 = 2.86 pro Dekade
    max_variance = 20 * 20  # Worst case
    distribution_score = 1 - (variance / max_variance)

    return distribution_score, decades


def calculate_sum_extremity(numbers: List[int]) -> float:
    """
    Berechnet wie extrem die Summe ist.
    Extreme Summen sind unbeliebter (sehr niedrig oder sehr hoch).
    """
    total_sum = sum(numbers)

    # Erwartete Summe bei 20 aus 70: 20 * 35.5 = 710
    expected_sum = 710
    min_sum = sum(range(1, 21))  # 210
    max_sum = sum(range(51, 71))  # 1210

    # Normalisiere Abweichung
    deviation = abs(total_sum - expected_sum)
    max_deviation = max(expected_sum - min_sum, max_sum - expected_sum)

    extremity_score = deviation / max_deviation
    return extremity_score


def calculate_popularity_score(numbers: List[int]) -> float:
    """
    Berechnet wie populaer die Zahlen sind (niedrig = Geburtstage, Glueckszahlen).
    Hoher Score = unbeliebte Zahlen.
    """
    # Beliebte Zahlen (Geburtstage, Glueckszahlen)
    popular = {1, 2, 3, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 21, 22, 23, 24, 25, 27, 28, 29, 31}

    in_popular = sum(1 for n in numbers if n in popular)
    return 1 - (in_popular / len(numbers))


def calculate_uniqueness_score(numbers: List[int]) -> Dict:
    """
    Berechnet Gesamt-Uniqueness-Score.

    Komponenten:
    - Anti-Birthday (30%): Viele Zahlen > 31
    - Keine Konsekutive (20%): Wenige aufeinanderfolgende Zahlen
    - Dekaden-Verteilung (20%): Gute Streuung ueber alle Dekaden
    - Sum-Extremitaet (15%): Extreme Summe (sehr hoch oder niedrig)
    - Unpopularitaet (15%): Wenige beliebte Zahlen
    """
    anti_birthday = calculate_anti_birthday_score(numbers)
    consecutive = calculate_consecutive_pairs(numbers)
    decade_dist, decades = calculate_decade_distribution(numbers)
    sum_extremity = calculate_sum_extremity(numbers)
    unpopularity = calculate_popularity_score(numbers)

    # Konsekutiv-Score: weniger ist besser
    # Bei 20 Zahlen max ~10 konsekutive moeglich
    consecutive_score = 1 - (consecutive / 10)

    # Gewichteter Score
    total_score = (
        anti_birthday * 0.30 +
        consecutive_score * 0.20 +
        decade_dist * 0.20 +
        sum_extremity * 0.15 +
        unpopularity * 0.15
    )

    return {
        "total_score": round(total_score, 3),
        "anti_birthday": round(anti_birthday, 3),
        "consecutive_pairs": consecutive,
        "consecutive_score": round(consecutive_score, 3),
        "decade_distribution": round(decade_dist, 3),
        "decades": decades,
        "sum": sum(numbers),
        "sum_extremity": round(sum_extremity, 3),
        "unpopularity": round(unpopularity, 3)
    }


def analyze_gk1_uniqueness(keno_df: pd.DataFrame, gk1_df: pd.DataFrame) -> Dict:
    """
    Analysiert Uniqueness aller GK1-Events.
    """
    results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "gk1_events": len(gk1_df),
            "threshold": 0.5
        },
        "gk1_analysis": [],
        "summary": {}
    }

    # Merge GK1 Events mit Ziehungen
    gk1_typ10 = gk1_df[gk1_df["Keno-Typ"] == 10]

    for _, gk1_row in gk1_typ10.iterrows():
        date = gk1_row["Datum"]

        # Finde Ziehung fuer dieses Datum
        draw_row = keno_df[keno_df["Datum"] == date]

        if len(draw_row) == 0:
            continue

        numbers = draw_row.iloc[0]["numbers"]
        uniqueness = calculate_uniqueness_score(numbers)

        results["gk1_analysis"].append({
            "date": str(date.date()),
            "numbers": numbers,
            "uniqueness": uniqueness,
            "winners": int(gk1_row["Anzahl der Gewinner"]) if pd.notna(gk1_row["Anzahl der Gewinner"]) else 0,
            "days_since_last": int(gk1_row["Vergangene Tage seit dem letzten Gewinnklasse 1"]) if pd.notna(gk1_row["Vergangene Tage seit dem letzten Gewinnklasse 1"]) else 0
        })

    # Zusammenfassung
    if results["gk1_analysis"]:
        scores = [e["uniqueness"]["total_score"] for e in results["gk1_analysis"]]
        results["summary"] = {
            "avg_uniqueness": round(np.mean(scores), 3),
            "min_uniqueness": round(min(scores), 3),
            "max_uniqueness": round(max(scores), 3),
            "above_threshold": sum(1 for s in scores if s >= 0.5),
            "total_events": len(scores)
        }

    return results


def generate_jackpot_candidate(strong_pairs: List[Tuple[int, int]], target_uniqueness: float = 0.6) -> Dict:
    """
    Generiert einen Jackpot-Kandidaten basierend auf Uniqueness-Kriterien.
    """
    # Basis: Anti-Birthday Zahlen (>31) und starke Paare
    anti_birthday_pool = list(range(32, 71))
    birthday_pool = list(range(1, 32))

    # Starte mit starken Paaren die hohe Zahlen haben
    high_pairs = [(p[0], p[1]) for p in strong_pairs if p[0] > 31 or p[1] > 31]

    best_candidate = None
    best_score = 0

    # Versuche verschiedene Kombinationen
    for _ in range(100):
        candidate = []

        # Nehme 1-2 starke Paare
        if high_pairs:
            pair = high_pairs[np.random.randint(len(high_pairs))]
            candidate.extend(pair)

        # Fuelle mit Anti-Birthday Zahlen auf
        remaining = 10 - len(candidate)
        available = [n for n in anti_birthday_pool if n not in candidate]

        if len(available) >= remaining:
            fill = list(np.random.choice(available, remaining, replace=False))
            candidate.extend(fill)

        if len(candidate) == 10:
            uniqueness = calculate_uniqueness_score(candidate)
            if uniqueness["total_score"] > best_score:
                best_score = uniqueness["total_score"]
                best_candidate = {
                    "numbers": sorted(candidate),
                    "uniqueness": uniqueness
                }

    return best_candidate


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("WL-006: UNIQUENESS-SCORE FUER JACKPOT-KANDIDATEN")
    print("=" * 70)
    print()

    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    gk1_path = base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv"
    output_path = base_path / "results" / "uniqueness_analysis.json"

    # Daten laden
    print("Lade Daten...")
    keno_df = load_keno_draws(str(keno_path))
    gk1_df = load_gk1_events(str(gk1_path))
    print(f"  Ziehungen: {len(keno_df)}")
    print(f"  GK1-Events: {len(gk1_df)}")
    print()

    # GK1 Analyse
    print("Analysiere GK1-Events...")
    results = analyze_gk1_uniqueness(keno_df, gk1_df)

    print(f"\n{'='*70}")
    print("GK1 JACKPOT-ANALYSE")
    print(f"{'='*70}")

    for event in results["gk1_analysis"]:
        score = event["uniqueness"]["total_score"]
        status = "HIGH" if score >= 0.5 else "LOW"
        print(f"\n{event['date']} ({event['winners']} Gewinner):")
        print(f"  Zahlen: {event['numbers']}")
        print(f"  Uniqueness: {score:.3f} [{status}]")
        print(f"    Anti-Birthday: {event['uniqueness']['anti_birthday']:.2f}")
        print(f"    Konsekutiv: {event['uniqueness']['consecutive_pairs']} Paare")
        print(f"    Dekaden: {event['uniqueness']['decade_distribution']:.2f}")
        print(f"    Summe: {event['uniqueness']['sum']} (Extremitaet: {event['uniqueness']['sum_extremity']:.2f})")

    # Zusammenfassung
    print(f"\n{'='*70}")
    print("ZUSAMMENFASSUNG")
    print(f"{'='*70}")

    summary = results["summary"]
    print(f"\nGK1 Uniqueness Statistik:")
    print(f"  Durchschnitt: {summary['avg_uniqueness']:.3f}")
    print(f"  Minimum: {summary['min_uniqueness']:.3f}")
    print(f"  Maximum: {summary['max_uniqueness']:.3f}")
    print(f"  Ueber Schwelle (0.5): {summary['above_threshold']}/{summary['total_events']}")

    # WL-006 Validierung
    print(f"\n{'='*70}")
    print("WL-006 VALIDIERUNG")
    print(f"{'='*70}")

    above_threshold_rate = summary["above_threshold"] / summary["total_events"] if summary["total_events"] > 0 else 0

    if above_threshold_rate >= 0.7:
        print(f"\nSTATUS: BESTAETIGT - {above_threshold_rate*100:.1f}% der Jackpots haben hohe Uniqueness")
        results["wl006_status"] = "BESTAETIGT"
    else:
        print(f"\nSTATUS: TEILWEISE - Nur {above_threshold_rate*100:.1f}% haben hohe Uniqueness")
        results["wl006_status"] = "TEILWEISE"

    # Generiere Jackpot-Kandidat
    print(f"\n{'='*70}")
    print("JACKPOT-KANDIDAT GENERIERUNG")
    print(f"{'='*70}")

    # Lade starke Paare aus vorheriger Analyse
    strong_pairs = [(9, 50), (20, 36), (9, 10), (32, 64), (33, 49), (33, 50)]
    candidate = generate_jackpot_candidate(strong_pairs)

    if candidate:
        print(f"\nEmpfohlener Jackpot-Kandidat:")
        print(f"  Zahlen: {candidate['numbers']}")
        print(f"  Uniqueness: {candidate['uniqueness']['total_score']:.3f}")
        print(f"  Anti-Birthday: {candidate['uniqueness']['anti_birthday']:.2f}")
        print(f"  Summe: {candidate['uniqueness']['sum']}")

        results["jackpot_candidate"] = candidate

    # Speichern
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse gespeichert: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
