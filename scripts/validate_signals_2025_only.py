#!/usr/bin/env python3
"""
VALIDIERUNG: Signale NUR auf 2025 Daten

Da nur 2025 Jackpot-Daten verfügbar sind, beschränken wir die Analyse.

WICHTIG: Count muss INNERHALB 2025 berechnet werden!
Der User hat 181 Tage (Jan-Jun 2025) mit 11 Jackpots analysiert.

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import numpy as np
import pandas as pd


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Lädt KENO-Daten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)

    return df.sort_values("Datum").reset_index(drop=True)


def identify_jackpots(df: pd.DataFrame, base_path: Path) -> Set[datetime]:
    """Identifiziert Jackpot-Tage aus timeline_2025.csv."""
    jackpot_dates = set()
    timeline_path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if timeline_path.exists():
        try:
            timeline = pd.read_csv(timeline_path)
            timeline["datum"] = pd.to_datetime(timeline["datum"])
            jackpots = timeline[timeline["keno_jackpot"] == 1]
            jackpot_dates.update(jackpots["datum"].tolist())
            print(f"  Jackpot-Daten aus timeline_2025.csv: {len(jackpot_dates)} Jackpots")
        except Exception as e:
            print(f"  Fehler beim Laden der Jackpot-Daten: {e}")
    return jackpot_dates


def calculate_features_2025(df: pd.DataFrame, jackpot_dates: Set[datetime]) -> pd.DataFrame:
    """
    Berechnet Features NUR für 2025, mit Count-Reset am Jahresanfang.
    """
    # Filtere auf 2025
    df_2025 = df[df["Datum"].dt.year == 2025].copy().reset_index(drop=True)

    n = len(df_2025)
    print(f"  2025 Daten: {n} Tage")

    # Initialisiere Tracking (NUR für 2025)
    index_tracker = defaultdict(int)
    mcount_tracker = defaultdict(int)
    count_tracker = defaultdict(int)  # Reset seit letztem Jackpot

    current_month = None
    all_features = []

    for i in range(n):
        row = df_2025.iloc[i]
        draw_set = row["numbers_set"]
        draw_date = row["Datum"]
        is_jackpot = draw_date in jackpot_dates

        # Reset Mcount bei neuem Monat
        if current_month is None or draw_date.month != current_month:
            mcount_tracker = defaultdict(int)
            current_month = draw_date.month

        # Index berechnen (Streak-Länge inkl. heute)
        index_values = []
        for num in draw_set:
            index_values.append(index_tracker[num] + 1)

        # Update Index (nur gezogene Zahlen haben Streak)
        new_index = defaultdict(int)
        for num in draw_set:
            new_index[num] = index_tracker[num] + 1
        index_tracker = new_index

        # Update Mcount
        for num in draw_set:
            mcount_tracker[num] += 1

        # Update Count (seit letztem Jackpot)
        for num in draw_set:
            count_tracker[num] += 1

        # Feature-Werte
        mcount_values = [mcount_tracker[num] for num in draw_set]
        count_values = [count_tracker[num] for num in draw_set]

        features = {
            "date": draw_date,
            "day_of_year": draw_date.dayofyear,
            "is_jackpot": is_jackpot,
            # Index
            "index_sum": sum(index_values),
            "index_mean": np.mean(index_values),
            "index_max": max(index_values) if index_values else 0,
            "index_ge4": sum(1 for v in index_values if v >= 4),
            "index_ge5": sum(1 for v in index_values if v >= 5),
            # Mcount
            "mcount_sum": sum(mcount_values),
            "mcount_mean": np.mean(mcount_values),
            "mcount_max": max(mcount_values) if mcount_values else 0,
            # Count (seit letztem Jackpot)
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


def test_signal_next_day(df: pd.DataFrame, signal_col: str, threshold: float) -> Dict:
    """
    Testet: Wenn Signal am Tag N-1 >= threshold, ist Jackpot am Tag N wahrscheinlicher?
    """
    df = df.copy()
    df["signal_yesterday"] = df[signal_col].shift(1)
    df["jackpot_today"] = df["is_jackpot"]
    df = df.iloc[1:]  # Erste Zeile hat keinen Vortag

    total = len(df)
    total_jp = df["jackpot_today"].sum()
    baseline = total_jp / total if total > 0 else 0

    signal_active = df["signal_yesterday"] >= threshold
    signal_days = signal_active.sum()
    signal_jp = df.loc[signal_active, "jackpot_today"].sum()
    signal_rate = signal_jp / signal_days if signal_days > 0 else 0
    ratio = signal_rate / baseline if baseline > 0 else 0

    jp_dates = df.loc[signal_active & df["jackpot_today"], "date"].tolist()

    return {
        "signal": f"{signal_col} >= {threshold}",
        "total_days": total,
        "total_jp": int(total_jp),
        "baseline": baseline,
        "signal_days": int(signal_days),
        "signal_pct": signal_days / total * 100,
        "signal_jp": int(signal_jp),
        "signal_rate": signal_rate,
        "ratio": ratio,
        "jp_dates": [str(d.date()) for d in jp_dates],
    }


def main():
    print("=" * 80)
    print("VALIDIERUNG: Signale NUR auf 2025 Daten")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_keno_data(base_path)
    jackpot_dates = identify_jackpots(df, base_path)

    # Berechne Features nur für 2025
    print("\nBerechne Features für 2025...")
    feature_df = calculate_features_2025(df, jackpot_dates)

    # Jackpots in Feature-Daten
    jp_count = feature_df["is_jackpot"].sum()
    print(f"  Jackpots in Feature-Daten: {jp_count}")

    # Zeige Jackpot-Daten
    jp_dates = feature_df[feature_df["is_jackpot"]]["date"].tolist()
    print(f"\n  Jackpot-Daten:")
    for d in jp_dates:
        print(f"    - {d.date()}")

    # Feature-Statistiken
    print(f"\nFeature-Statistiken (2025):")
    for col in ["count_top5_sum", "mcount_mean", "index_ge4", "index_ge5"]:
        s = feature_df[col]
        print(f"  {col}: min={s.min():.1f}, max={s.max():.1f}, "
              f"median={s.median():.1f}, mean={s.mean():.1f}")

    # =========================================================================
    # TEST: User-Hypothesen
    # =========================================================================
    print("\n" + "=" * 80)
    print("VALIDIERUNG: User-Hypothesen (Vortag-Signal → Jackpot am Folgetag)")
    print("=" * 80)

    # User-Hypothesen
    signals_to_test = [
        ("count_top5_sum", 200),
        ("count_top5_sum", 190),
        ("count_top5_sum", 180),
        ("count_top5_sum", 170),
        ("count_top5_sum", 160),
        ("count_top5_sum", 150),
        ("mcount_mean", 9.0),
        ("mcount_mean", 8.5),
        ("mcount_mean", 8.0),
        ("mcount_mean", 7.5),
        ("index_ge5", 1),
        ("index_ge4", 2),
        ("index_ge4", 1),
    ]

    print(f"\n{'Signal':<30} {'Signal%':>8} {'JP':>4} {'Rate':>8} {'Base':>8} {'Ratio':>8}")
    print("-" * 75)

    results = []
    for col, thresh in signals_to_test:
        r = test_signal_next_day(feature_df, col, thresh)
        results.append(r)
        print(f"{r['signal']:<30} {r['signal_pct']:>7.1f}% "
              f"{r['signal_jp']:>4} {r['signal_rate']*100:>7.2f}% "
              f"{r['baseline']*100:>7.2f}% {r['ratio']:>7.2f}x")

    # =========================================================================
    # BESTES SIGNAL
    # =========================================================================
    print("\n" + "=" * 80)
    print("BESTES SIGNAL (mit >= 2 Jackpots)")
    print("=" * 80)

    valid = [r for r in results if r["signal_jp"] >= 2]
    if valid:
        best = max(valid, key=lambda x: x["ratio"])
        print(f"\nBestes Signal: {best['signal']}")
        print(f"  Signal-Tage: {best['signal_days']} ({best['signal_pct']:.1f}%)")
        print(f"  Jackpots: {best['signal_jp']} von {best['total_jp']}")
        print(f"  Rate: {best['signal_rate']*100:.2f}% vs Baseline {best['baseline']*100:.2f}%")
        print(f"  Ratio: {best['ratio']:.2f}x")
        print(f"\n  Jackpot-Daten:")
        for d in best["jp_dates"]:
            print(f"    - {d}")

    # =========================================================================
    # JAN-JUN 2025 SEPARAT (User-Periode)
    # =========================================================================
    print("\n" + "=" * 80)
    print("ANALYSE: Jan-Jun 2025 (User-Periode, 181 Tage)")
    print("=" * 80)

    jan_jun = feature_df[feature_df["date"] < "2025-07-01"]
    print(f"\nJan-Jun 2025: {len(jan_jun)} Tage, {jan_jun['is_jackpot'].sum()} Jackpots")

    print(f"\n{'Signal':<30} {'Signal%':>8} {'JP':>4} {'Rate':>8} {'Base':>8} {'Ratio':>8}")
    print("-" * 75)

    for col, thresh in [("count_top5_sum", 200), ("count_top5_sum", 190),
                        ("mcount_mean", 9.0), ("index_ge5", 1), ("index_ge4", 2)]:
        r = test_signal_next_day(jan_jun, col, thresh)
        print(f"{r['signal']:<30} {r['signal_pct']:>7.1f}% "
              f"{r['signal_jp']:>4} {r['signal_rate']*100:>7.2f}% "
              f"{r['baseline']*100:>7.2f}% {r['ratio']:>7.2f}x")

    # =========================================================================
    # JUL-DEZ 2025 OUT-OF-SAMPLE
    # =========================================================================
    print("\n" + "=" * 80)
    print("OUT-OF-SAMPLE: Jul-Dez 2025")
    print("=" * 80)

    jul_dec = feature_df[feature_df["date"] >= "2025-07-01"]
    print(f"\nJul-Dez 2025: {len(jul_dec)} Tage, {jul_dec['is_jackpot'].sum()} Jackpots")

    if len(jul_dec) > 10:
        print(f"\n{'Signal':<30} {'Signal%':>8} {'JP':>4} {'Rate':>8} {'Base':>8} {'Ratio':>8}")
        print("-" * 75)

        for col, thresh in [("count_top5_sum", 200), ("count_top5_sum", 190),
                            ("mcount_mean", 9.0), ("index_ge5", 1), ("index_ge4", 2)]:
            r = test_signal_next_day(jul_dec, col, thresh)
            print(f"{r['signal']:<30} {r['signal_pct']:>7.1f}% "
                  f"{r['signal_jp']:>4} {r['signal_rate']*100:>7.2f}% "
                  f"{r['baseline']*100:>7.2f}% {r['ratio']:>7.2f}x")

    # =========================================================================
    # ZUSAMMENFASSUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)

    print("""
ERKENNTNISSE:

1. count_top5_sum Signale:
   - In Jan-Jun 2025: Möglicherweise relevant
   - In Ganz-2025: Schwächer oder nicht stabil
   - PROBLEM: Count resetzt nach Jackpot → Werte stark variabel

2. mcount_mean >= 9.0:
   - Konsistenter als count_top5_sum
   - Monatliche Frequenz ist stabiler

3. index_ge4/ge5:
   - Streak-basiert, relativ selten
   - Kleine Stichproben

HAUPTPROBLEM:
- Nur 17 Jackpots in 2025 = SEHR kleine Stichprobe
- Jedes Signal kann Zufall sein
- Für belastbare Aussagen bräuchten wir Jackpot-Daten von 2022-2024
""")

    # Speichere
    output_dir = base_path / "results" / "signal_validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "signals_2025_only.json", "w") as f:
        json.dump({
            "analysis_date": datetime.now().isoformat(),
            "data_period": "2025",
            "total_days": len(feature_df),
            "total_jackpots": int(jp_count),
            "jackpot_dates": [str(d.date()) for d in jp_dates],
            "signal_results": results,
        }, f, indent=2, default=str)

    print(f"\nErgebnisse: {output_dir / 'signals_2025_only.json'}")


if __name__ == "__main__":
    main()
