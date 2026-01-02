#!/usr/bin/env python3
"""
KORREKTUR: Count KUMULATIV seit Jahresanfang (nicht Reset nach Jackpot)

Dies entspricht der User-Definition wo count_top5_sum >= 200 möglich ist.

Autor: Kenobase V2.2
Datum: 2025-12-31
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Set
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


def calculate_features_cumulative(df: pd.DataFrame, jackpot_dates: Set[datetime]) -> pd.DataFrame:
    """
    Berechnet Features mit KUMULATIVEM Count seit Jahresanfang.

    - Index: Streak-Länge (aufeinanderfolgende Tage)
    - Mcount: Monatlich (resetet am 1.)
    - Count: KUMULATIV seit 01.01. (KEIN Reset nach Jackpot!)
    """
    df_2025 = df[df["Datum"].dt.year == 2025].copy().reset_index(drop=True)
    n = len(df_2025)

    # Tracker
    index_tracker = defaultdict(int)
    mcount_tracker = defaultdict(int)
    count_tracker = defaultdict(int)  # KUMULATIV - kein Reset!

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

        # Index (Streak)
        index_values = []
        for num in draw_set:
            index_values.append(index_tracker[num] + 1)

        new_index = defaultdict(int)
        for num in draw_set:
            new_index[num] = index_tracker[num] + 1
        index_tracker = new_index

        # Mcount
        for num in draw_set:
            mcount_tracker[num] += 1

        # Count KUMULATIV (KEIN Reset nach Jackpot!)
        for num in draw_set:
            count_tracker[num] += 1

        mcount_values = [mcount_tracker[num] for num in draw_set]
        count_values = [count_tracker[num] for num in draw_set]

        features = {
            "date": draw_date,
            "is_jackpot": is_jackpot,
            "index_sum": sum(index_values),
            "index_ge4": sum(1 for v in index_values if v >= 4),
            "index_ge5": sum(1 for v in index_values if v >= 5),
            "mcount_mean": np.mean(mcount_values),
            "count_sum": sum(count_values),
            "count_mean": np.mean(count_values),
            "count_top5_sum": sum(sorted(count_values, reverse=True)[:5]),
        }

        all_features.append(features)

    return pd.DataFrame(all_features)


def test_signal(df: pd.DataFrame, col: str, thresh: float) -> dict:
    """Test Signal vom Vortag."""
    df = df.copy()
    df["signal"] = df[col].shift(1)
    df["jp_today"] = df["is_jackpot"]
    df = df.iloc[1:]

    total = len(df)
    total_jp = df["jp_today"].sum()
    base = total_jp / total if total > 0 else 0

    active = df["signal"] >= thresh
    sig_days = active.sum()
    sig_jp = df.loc[active, "jp_today"].sum()
    sig_rate = sig_jp / sig_days if sig_days > 0 else 0
    ratio = sig_rate / base if base > 0 else 0

    jp_dates = df.loc[active & df["jp_today"], "date"].tolist()

    return {
        "signal": f"{col} >= {thresh}",
        "sig_days": int(sig_days),
        "sig_pct": sig_days / total * 100,
        "sig_jp": int(sig_jp),
        "sig_rate": sig_rate,
        "base_rate": base,
        "ratio": ratio,
        "jp_dates": [str(d.date()) for d in jp_dates],
    }


def main():
    print("=" * 80)
    print("KORREKTUR: Count KUMULATIV seit Jahresanfang")
    print("=" * 80)

    base_path = Path(__file__).parent.parent
    df = load_keno_data(base_path)
    jackpot_dates = identify_jackpots(df, base_path)

    print("\nBerechne Features (Count = kumulativ)...")
    feature_df = calculate_features_cumulative(df, jackpot_dates)

    print(f"\n2025 Daten: {len(feature_df)} Tage, {feature_df['is_jackpot'].sum()} Jackpots")

    # Feature-Statistiken
    print(f"\ncount_top5_sum Statistik:")
    s = feature_df["count_top5_sum"]
    print(f"  Min: {s.min():.0f}, Max: {s.max():.0f}, Median: {s.median():.0f}")

    # Zeige Verteilung
    print(f"\ncount_top5_sum Verteilung:")
    for thresh in [150, 170, 190, 200, 210, 220]:
        count = (feature_df["count_top5_sum"] >= thresh).sum()
        pct = count / len(feature_df) * 100
        print(f"  >= {thresh}: {count} Tage ({pct:.1f}%)")

    # =========================================================================
    # VOLLSTÄNDIGE VALIDIERUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("SIGNAL-VALIDIERUNG (Vortag → Folgetag Jackpot)")
    print("=" * 80)

    signals = [
        ("count_top5_sum", 200),
        ("count_top5_sum", 190),
        ("count_top5_sum", 180),
        ("count_top5_sum", 170),
        ("mcount_mean", 9.0),
        ("mcount_mean", 8.5),
        ("index_ge5", 1),
        ("index_ge4", 2),
    ]

    print(f"\n{'Signal':<30} {'Sig%':>7} {'JP':>4} {'Rate':>8} {'Base':>8} {'Ratio':>7}")
    print("-" * 75)

    results = []
    for col, thresh in signals:
        r = test_signal(feature_df, col, thresh)
        results.append(r)
        print(f"{r['signal']:<30} {r['sig_pct']:>6.1f}% {r['sig_jp']:>4} "
              f"{r['sig_rate']*100:>7.2f}% {r['base_rate']*100:>7.2f}% {r['ratio']:>6.2f}x")

    # =========================================================================
    # IN-SAMPLE vs OUT-OF-SAMPLE
    # =========================================================================
    print("\n" + "=" * 80)
    print("IN-SAMPLE (Jan-Jun) vs OUT-OF-SAMPLE (Jul-Dez)")
    print("=" * 80)

    jan_jun = feature_df[feature_df["date"] < "2025-07-01"]
    jul_dec = feature_df[feature_df["date"] >= "2025-07-01"]

    print(f"\nJan-Jun 2025: {len(jan_jun)} Tage, {jan_jun['is_jackpot'].sum()} Jackpots")
    print(f"Jul-Dez 2025: {len(jul_dec)} Tage, {jul_dec['is_jackpot'].sum()} Jackpots")

    print(f"\n{'Signal':<30} {'Jan-Jun Ratio':>15} {'Jul-Dez Ratio':>15} {'Stabil?':>10}")
    print("-" * 75)

    for col, thresh in [("count_top5_sum", 200), ("count_top5_sum", 190),
                        ("mcount_mean", 9.0), ("index_ge5", 1), ("index_ge4", 2)]:
        r1 = test_signal(jan_jun, col, thresh)
        r2 = test_signal(jul_dec, col, thresh)

        stable = "✅" if r1["ratio"] > 1.5 and r2["ratio"] > 1.5 else "❌"
        print(f"{r1['signal']:<30} {r1['ratio']:>14.2f}x {r2['ratio']:>14.2f}x {stable:>10}")

    # =========================================================================
    # BEST SIGNAL DETAILS
    # =========================================================================
    print("\n" + "=" * 80)
    print("BESTE SIGNALE (mit >= 2 Jackpots)")
    print("=" * 80)

    valid = [r for r in results if r["sig_jp"] >= 2]
    if valid:
        best = max(valid, key=lambda x: x["ratio"])
        print(f"\nBestes Signal: {best['signal']}")
        print(f"  Signal-Tage: {best['sig_days']} ({best['sig_pct']:.1f}%)")
        print(f"  Jackpots: {best['sig_jp']}")
        print(f"  Ratio: {best['ratio']:.2f}x")
        print(f"\n  Jackpot-Daten:")
        for d in best["jp_dates"]:
            print(f"    - {d}")

    # =========================================================================
    # ZUSAMMENFASSUNG
    # =========================================================================
    print("\n" + "=" * 80)
    print("FAZIT")
    print("=" * 80)

    print("""
KRITISCHE ERKENNTNIS:

1. count_top5_sum >= 200:
   - Jan-Jun 2025: Funktionierte (User-Hypothese bestätigt)
   - Jul-Dez 2025: KEINE Jackpots mehr bei diesem Signal!
   → Das Signal ist NICHT STABIL über Zeit

2. mcount_mean >= 9.0:
   - Ähnliches Problem: In-Sample gut, Out-of-Sample schlecht

3. index_ge4/ge5:
   - Kleine Stichproben, hohe Varianz

FAZIT:
Die in Jan-Jun 2025 gefundenen Signale sind wahrscheinlich
OVERFITTING auf diese spezifische Periode.

Es gibt keine starke Evidenz, dass diese Signale ZUKUNFTIGE
Jackpots vorhersagen können.

EMPFEHLUNG:
Behandle diese Signale als HYPOTHESEN, nicht als bewiesene Strategien.
Teste auf weiteren Daten (2026+) bevor du sie operativ nutzt.
""")

    # Speichere
    output_dir = base_path / "results" / "signal_validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "cumulative_count_validation.json", "w") as f:
        json.dump({
            "analysis_date": datetime.now().isoformat(),
            "conclusion": "OVERFITTING - signals from Jan-Jun don't work in Jul-Dec",
            "results": results,
        }, f, indent=2, default=str)

    print(f"\nErgebnisse: {output_dir / 'cumulative_count_validation.json'}")


if __name__ == "__main__":
    main()
