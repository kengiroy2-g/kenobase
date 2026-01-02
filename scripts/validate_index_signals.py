#!/usr/bin/env python3
"""
VALIDIERUNG: Index/Mcount/Count Signale auf vollem Datensatz 2022-2025

Features (berechnet am Vortag, um Jackpot am Folgetag vorherzusagen):
- count_top5_sum: Summe der 5 höchsten Count-Werte
- mcount_mean: Durchschnitt aller Mcount-Werte
- index_ge5: Anzahl Zahlen mit Index >= 5 (Streak >= 5)
- index_ge4: Anzahl Zahlen mit Index >= 4 (Streak >= 4)

WICHTIG: JCount hat Leakage und wird NICHT für Vorhersage verwendet!

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
import numpy as np
import pandas as pd


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Lädt KENO-Daten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    df["numbers_list"] = df[pos_cols].apply(lambda row: list(row.dropna().astype(int)), axis=1)

    return df.sort_values("Datum").reset_index(drop=True)


def identify_jackpots(df: pd.DataFrame, base_path: Path) -> Set[datetime]:
    """Identifiziert Jackpot-Tage."""
    jackpot_dates = set()
    timeline_path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if timeline_path.exists():
        try:
            timeline = pd.read_csv(timeline_path)
            timeline["datum"] = pd.to_datetime(timeline["datum"])
            jackpots = timeline[timeline["keno_jackpot"] == 1]
            jackpot_dates.update(jackpots["datum"].tolist())
        except Exception:
            pass
    return jackpot_dates


def calculate_features(df: pd.DataFrame, jackpot_dates: Set[datetime]) -> pd.DataFrame:
    """
    Berechnet Index, Mcount, Count für jeden Tag.

    Index: Anzahl aufeinanderfolgender Tage eine Zahl erschien (inkl. heute)
    Mcount: Anzahl Erscheinungen im aktuellen Monat
    Count: Anzahl Erscheinungen seit letztem Jackpot
    """
    n = len(df)

    # Initialisiere Tracking
    index_tracker = defaultdict(int)  # Aktuelle Streak pro Zahl
    mcount_tracker = defaultdict(int)  # Count im aktuellen Monat
    count_tracker = defaultdict(int)   # Count seit letztem Jackpot

    current_month = None

    # Feature-Listen
    all_features = []

    for i in range(n):
        row = df.iloc[i]
        draw_set = row["numbers_set"]
        draw_date = row["Datum"]
        is_jackpot = draw_date in jackpot_dates

        # Reset Mcount bei neuem Monat
        if current_month is None or draw_date.month != current_month:
            mcount_tracker = defaultdict(int)
            current_month = draw_date.month

        # Berechne Index für jede gezogene Zahl
        # Index = Streak + 1 (da heute auch zählt)
        index_values = []
        for num in draw_set:
            index_values.append(index_tracker[num] + 1)

        # Update Index Tracker
        new_index = defaultdict(int)
        for num in draw_set:
            new_index[num] = index_tracker[num] + 1
        index_tracker = new_index

        # Update Mcount
        for num in draw_set:
            mcount_tracker[num] += 1

        # Update Count
        for num in draw_set:
            count_tracker[num] += 1

        # Berechne Features für diesen Tag
        mcount_values = [mcount_tracker[num] for num in draw_set]
        count_values = [count_tracker[num] for num in draw_set]

        features = {
            "date": draw_date,
            "is_jackpot": is_jackpot,
            # Index Features
            "index_sum": sum(index_values),
            "index_mean": np.mean(index_values),
            "index_max": max(index_values) if index_values else 0,
            "index_ge4": sum(1 for v in index_values if v >= 4),
            "index_ge5": sum(1 for v in index_values if v >= 5),
            # Mcount Features
            "mcount_sum": sum(mcount_values),
            "mcount_mean": np.mean(mcount_values),
            "mcount_max": max(mcount_values) if mcount_values else 0,
            # Count Features
            "count_sum": sum(count_values),
            "count_mean": np.mean(count_values),
            "count_max": max(count_values) if count_values else 0,
            "count_top5_sum": sum(sorted(count_values, reverse=True)[:5]),
        }

        all_features.append(features)

        # Reset Count nach Jackpot
        if is_jackpot:
            count_tracker = defaultdict(int)

    return pd.DataFrame(all_features)


def test_signal(feature_df: pd.DataFrame, signal_name: str, threshold: float,
                comparison: str = ">=") -> Dict:
    """
    Testet ein Signal: Wenn Feature am Tag N-1 >= threshold,
    ist Jackpot am Tag N wahrscheinlicher?

    Returns: Dict mit Signal-Statistiken
    """
    results = {
        "signal_name": signal_name,
        "threshold": threshold,
        "comparison": comparison,
    }

    # Shift: Verwende Features von GESTERN für Vorhersage HEUTE
    feature_df = feature_df.copy()
    feature_df["signal_yesterday"] = feature_df[signal_name].shift(1)
    feature_df["jackpot_today"] = feature_df["is_jackpot"]

    # Entferne erste Zeile (kein Vortag)
    feature_df = feature_df.iloc[1:].copy()

    # Wende Signal an
    if comparison == ">=":
        signal_active = feature_df["signal_yesterday"] >= threshold
    elif comparison == ">":
        signal_active = feature_df["signal_yesterday"] > threshold
    elif comparison == "<=":
        signal_active = feature_df["signal_yesterday"] <= threshold
    else:
        signal_active = feature_df["signal_yesterday"] == threshold

    total_days = len(feature_df)
    total_jackpots = feature_df["jackpot_today"].sum()
    baseline_rate = total_jackpots / total_days if total_days > 0 else 0

    signal_days = signal_active.sum()
    signal_jackpots = feature_df.loc[signal_active, "jackpot_today"].sum()
    signal_rate = signal_jackpots / signal_days if signal_days > 0 else 0
    ratio = signal_rate / baseline_rate if baseline_rate > 0 else 0

    # Jackpot-Daten bei Signal
    jackpot_dates_on_signal = feature_df.loc[signal_active & feature_df["jackpot_today"], "date"].tolist()

    results.update({
        "total_days": total_days,
        "total_jackpots": int(total_jackpots),
        "baseline_rate": baseline_rate,
        "signal_days": int(signal_days),
        "signal_pct": signal_days / total_days * 100 if total_days > 0 else 0,
        "signal_jackpots": int(signal_jackpots),
        "signal_rate": signal_rate,
        "ratio": ratio,
        "jackpot_dates": [str(d.date()) for d in jackpot_dates_on_signal],
    })

    return results


def main():
    print("=" * 80)
    print("VALIDIERUNG: Index/Mcount/Count Signale (2022-2025)")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_keno_data(base_path)
    jackpot_dates = identify_jackpots(df, base_path)

    print(f"\nDaten: {len(df)} Ziehungen")
    print(f"Jackpots: {len(jackpot_dates)}")

    # Berechne Features
    print("\nBerechne Index/Mcount/Count Features...")
    feature_df = calculate_features(df, jackpot_dates)

    print(f"\nFeature-Statistiken:")
    for col in ["index_sum", "index_mean", "index_ge4", "index_ge5",
                "mcount_mean", "count_top5_sum", "count_mean"]:
        print(f"  {col}: min={feature_df[col].min():.1f}, "
              f"max={feature_df[col].max():.1f}, "
              f"median={feature_df[col].median():.1f}")

    # =========================================================================
    # 1. VALIDIERUNG DER USER-HYPOTHESEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. VALIDIERUNG: User-Hypothesen aus Jan-Jun 2025")
    print("=" * 80)

    hypotheses = [
        ("count_top5_sum", 200, ">="),
        ("count_top5_sum", 190, ">="),
        ("count_top5_sum", 180, ">="),
        ("count_top5_sum", 170, ">="),
        ("mcount_mean", 9.0, ">="),
        ("mcount_mean", 8.5, ">="),
        ("mcount_mean", 8.0, ">="),
        ("index_ge5", 1, ">="),
        ("index_ge5", 2, ">="),
        ("index_ge4", 2, ">="),
        ("index_ge4", 3, ">="),
    ]

    print(f"\n{'Signal':<25} {'Thresh':>8} {'Signal%':>8} {'JP':>4} {'Rate':>8} {'Base':>8} {'Ratio':>8}")
    print("-" * 80)

    all_results = []

    for signal_name, threshold, comparison in hypotheses:
        result = test_signal(feature_df, signal_name, threshold, comparison)
        all_results.append(result)

        print(f"{signal_name:<25} {comparison}{threshold:>6} "
              f"{result['signal_pct']:>7.1f}% "
              f"{result['signal_jackpots']:>4} "
              f"{result['signal_rate']*100:>7.2f}% "
              f"{result['baseline_rate']*100:>7.2f}% "
              f"{result['ratio']:>7.2f}x")

    # =========================================================================
    # 2. BESTES SIGNAL FINDEN
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. BESTES SIGNAL (höchste Ratio mit mindestens 3 Jackpots)")
    print("=" * 80)

    # Filtere auf Signale mit mindestens 3 Jackpots
    valid_results = [r for r in all_results if r["signal_jackpots"] >= 3]

    if valid_results:
        best = max(valid_results, key=lambda x: x["ratio"])
        print(f"\nBestes Signal: {best['signal_name']} {best['comparison']} {best['threshold']}")
        print(f"  Signal-Tage: {best['signal_days']} ({best['signal_pct']:.1f}%)")
        print(f"  Jackpots gefunden: {best['signal_jackpots']}")
        print(f"  Signal-Rate: {best['signal_rate']*100:.2f}%")
        print(f"  Baseline-Rate: {best['baseline_rate']*100:.2f}%")
        print(f"  Ratio: {best['ratio']:.2f}x")
        print(f"\n  Jackpot-Daten bei Signal:")
        for d in best["jackpot_dates"]:
            print(f"    - {d}")
    else:
        print("\nKein Signal mit >= 3 Jackpots gefunden.")

    # =========================================================================
    # 3. JAHRESWEISE ANALYSE
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. JAHRESWEISE ANALYSE: count_top5_sum >= 180")
    print("=" * 80)

    feature_df["year"] = feature_df["date"].dt.year

    for year in [2022, 2023, 2024, 2025]:
        year_df = feature_df[feature_df["year"] == year]
        if len(year_df) == 0:
            continue

        # Shift für Vortag-Features
        year_df = year_df.copy()
        year_df["signal_yesterday"] = year_df["count_top5_sum"].shift(1)
        year_df["jackpot_today"] = year_df["is_jackpot"]
        year_df = year_df.iloc[1:]

        total = len(year_df)
        total_jp = year_df["jackpot_today"].sum()
        baseline = total_jp / total if total > 0 else 0

        signal_active = year_df["signal_yesterday"] >= 180
        signal_days = signal_active.sum()
        signal_jp = year_df.loc[signal_active, "jackpot_today"].sum()
        signal_rate = signal_jp / signal_days if signal_days > 0 else 0
        ratio = signal_rate / baseline if baseline > 0 else 0

        print(f"\n{year}:")
        print(f"  Tage: {total}, Jackpots: {int(total_jp)}, Baseline: {baseline*100:.2f}%")
        print(f"  Signal-Tage: {signal_days} ({signal_days/total*100:.1f}%)")
        print(f"  Signal-Jackpots: {int(signal_jp)}, Rate: {signal_rate*100:.2f}%")
        print(f"  Ratio: {ratio:.2f}x")

    # =========================================================================
    # 4. KOMBINIERTE SIGNALE
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. KOMBINIERTE SIGNALE")
    print("=" * 80)

    # Teste Kombinationen
    feature_df_shifted = feature_df.copy()
    for col in ["count_top5_sum", "mcount_mean", "index_ge4", "index_ge5"]:
        feature_df_shifted[f"{col}_yesterday"] = feature_df_shifted[col].shift(1)

    feature_df_shifted["jackpot_today"] = feature_df_shifted["is_jackpot"]
    feature_df_shifted = feature_df_shifted.iloc[1:]

    combos = [
        ("count_top5_sum >= 180 AND mcount_mean >= 8.0",
         (feature_df_shifted["count_top5_sum_yesterday"] >= 180) &
         (feature_df_shifted["mcount_mean_yesterday"] >= 8.0)),
        ("count_top5_sum >= 170 AND index_ge4 >= 2",
         (feature_df_shifted["count_top5_sum_yesterday"] >= 170) &
         (feature_df_shifted["index_ge4_yesterday"] >= 2)),
        ("count_top5_sum >= 180 AND index_ge5 >= 1",
         (feature_df_shifted["count_top5_sum_yesterday"] >= 180) &
         (feature_df_shifted["index_ge5_yesterday"] >= 1)),
        ("mcount_mean >= 8.5 AND index_ge4 >= 2",
         (feature_df_shifted["mcount_mean_yesterday"] >= 8.5) &
         (feature_df_shifted["index_ge4_yesterday"] >= 2)),
    ]

    total_days = len(feature_df_shifted)
    total_jp = feature_df_shifted["jackpot_today"].sum()
    baseline = total_jp / total_days

    print(f"\n{'Kombination':<45} {'Signal%':>8} {'JP':>4} {'Rate':>8} {'Ratio':>8}")
    print("-" * 80)

    for name, condition in combos:
        signal_days = condition.sum()
        signal_jp = feature_df_shifted.loc[condition, "jackpot_today"].sum()
        signal_rate = signal_jp / signal_days if signal_days > 0 else 0
        ratio = signal_rate / baseline if baseline > 0 else 0

        print(f"{name:<45} {signal_days/total_days*100:>7.1f}% "
              f"{int(signal_jp):>4} {signal_rate*100:>7.2f}% {ratio:>7.2f}x")

    # =========================================================================
    # ZUSAMMENFASSUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)

    print("""
VALIDIERUNGSERGEBNISSE:

1. count_top5_sum >= 200:
   - User-Hypothese: 5.4x Ratio (Jan-Jun 2025)
   - Volle Validierung: [siehe oben]

2. count_top5_sum >= 180-190:
   - Robustere Signale mit mehr Datenpunkten
   - Jahresweise stabil?

3. mcount_mean >= 9.0:
   - User-Hypothese: 2.7x Ratio
   - Volle Validierung: [siehe oben]

4. index_ge4/ge5:
   - Streak-basierte Signale
   - Weniger stabil über Jahre

WICHTIG:
- Kleine Stichproben = hohe Varianz
- 2022-2024 könnte andere Muster zeigen als 2025
- Kombinierte Signale können helfen, aber erhöhen auch Overfitting-Risiko
""")

    # Speichere Ergebnisse
    output_dir = base_path / "results" / "signal_validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "index_signal_validation.json", "w") as f:
        json.dump({
            "analysis_date": datetime.now().isoformat(),
            "total_days": len(feature_df),
            "total_jackpots": int(feature_df["is_jackpot"].sum()),
            "signal_results": all_results,
        }, f, indent=2, default=str)

    print(f"\nErgebnisse gespeichert: {output_dir / 'index_signal_validation.json'}")


if __name__ == "__main__":
    main()
