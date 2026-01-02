#!/usr/bin/env python
"""
Jackpot-Kombinationen Analyse - Reverse Engineering des KENO-Systems

Ziel: Identifiziere Kriterien, die echte Gewinner-Kombinationen von
allen möglichen Kombinationen unterscheiden.

Ansatz:
1. Lade Ziehungszahlen (20) für einen Jackpot-Tag
2. Generiere alle C(20,10) = 184.756 mögliche Tippscheine
3. Berechne für jede Kombination verschiedene Metriken
4. Vergleiche echte Gewinner-Kombination mit allen anderen
5. Identifiziere unterscheidende Kriterien
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from itertools import combinations
from collections import Counter
import json
from typing import Optional
import time


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Lade KENO-Ziehungsdaten."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df.sort_values("Datum").reset_index(drop=True)


def load_jackpot_dates(base_path: Path) -> list:
    """Lade alle Jackpot-Tage (10/10 mit Gewinnern) aus GQ-Daten."""
    gq_files = [
        base_path / "Keno_GPTs" / "Keno_GQ_2024.csv",
        base_path / "Keno_GPTs" / "Keno_GQ_02-2024.csv",
        base_path / "Keno_GPTs" / "Keno_GQ_2025.csv",
    ]

    all_jackpots = []
    for f in gq_files:
        if f.exists():
            df = pd.read_csv(f, encoding="utf-8")
            mask = (df["Keno-Typ"] == 10) & (df["Anzahl richtiger Zahlen"] == 10) & (df["Anzahl der Gewinner"] > 0)
            jackpots = df[mask][["Datum", "Anzahl der Gewinner"]].copy()
            all_jackpots.append(jackpots)

    if all_jackpots:
        result = pd.concat(all_jackpots, ignore_index=True)
        result = result.drop_duplicates(subset=["Datum"])
        result["DatumParsed"] = pd.to_datetime(result["Datum"], format="%d.%m.%Y")
        return result.sort_values("DatumParsed").to_dict("records")
    return []


def get_draw_numbers(df: pd.DataFrame, date: datetime) -> list:
    """Hole die 20 Ziehungszahlen für ein Datum."""
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    row = df[df["Datum"] == date]
    if len(row) > 0:
        return sorted([int(row[col].values[0]) for col in pos_cols])
    return []


def get_historical_frequency(df: pd.DataFrame, numbers: list, before_date: datetime, window_days: int = 30) -> dict:
    """Berechne historische Häufigkeit der Zahlen vor einem Datum."""
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    start_date = before_date - timedelta(days=window_days)
    mask = (df["Datum"] >= start_date) & (df["Datum"] < before_date)
    period_df = df[mask]

    freq = {n: 0 for n in numbers}
    for _, row in period_df.iterrows():
        drawn = set(int(row[col]) for col in pos_cols)
        for n in numbers:
            if n in drawn:
                freq[n] += 1

    return freq


def get_jackpot_frequency(df: pd.DataFrame, numbers: list, jackpot_dates: list, before_date: datetime) -> dict:
    """Wie oft erschien jede Zahl an Jackpot-Tagen (vor diesem Datum)?"""
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    freq = {n: 0 for n in numbers}

    for jp in jackpot_dates:
        jp_date = jp["DatumParsed"]
        if jp_date < before_date:
            row = df[df["Datum"] == jp_date]
            if len(row) > 0:
                drawn = set(int(row[col].values[0]) for col in pos_cols)
                for n in numbers:
                    if n in drawn:
                        freq[n] += 1

    return freq


def calculate_combination_metrics(
    combo: tuple,
    historical_freq: dict,
    jackpot_freq: dict,
    all_numbers: list
) -> dict:
    """Berechne Metriken für eine Kombination."""
    combo_set = set(combo)

    # Birthday-Zahlen (1-31)
    birthday_count = sum(1 for n in combo if n <= 31)

    # Dekaden-Verteilung (1-10, 11-20, ..., 61-70)
    decades = [0] * 7
    for n in combo:
        decade_idx = (n - 1) // 10
        decades[decade_idx] += 1

    # Gerade/Ungerade
    even_count = sum(1 for n in combo if n % 2 == 0)

    # Summe
    combo_sum = sum(combo)

    # Spread (max - min)
    spread = max(combo) - min(combo)

    # Historische Frequenz-Summe
    hist_freq_sum = sum(historical_freq.get(n, 0) for n in combo)
    hist_freq_avg = hist_freq_sum / len(combo)

    # Jackpot-Frequenz-Summe
    jp_freq_sum = sum(jackpot_freq.get(n, 0) for n in combo)
    jp_freq_avg = jp_freq_sum / len(combo)

    # Konsekutive Zahlen
    sorted_combo = sorted(combo)
    consecutive_pairs = sum(1 for i in range(len(sorted_combo)-1) if sorted_combo[i+1] - sorted_combo[i] == 1)

    # Gaps (Lücken zwischen Zahlen)
    gaps = [sorted_combo[i+1] - sorted_combo[i] for i in range(len(sorted_combo)-1)]
    max_gap = max(gaps) if gaps else 0
    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    return {
        "birthday_count": birthday_count,
        "birthday_pct": birthday_count / len(combo) * 100,
        "decades": decades,
        "decade_spread": max(decades) - min(decades),
        "decades_used": sum(1 for d in decades if d > 0),
        "even_count": even_count,
        "odd_count": len(combo) - even_count,
        "combo_sum": combo_sum,
        "spread": spread,
        "hist_freq_sum": hist_freq_sum,
        "hist_freq_avg": hist_freq_avg,
        "jp_freq_sum": jp_freq_sum,
        "jp_freq_avg": jp_freq_avg,
        "consecutive_pairs": consecutive_pairs,
        "max_gap": max_gap,
        "avg_gap": avg_gap,
    }


def analyze_jackpot_day(
    df: pd.DataFrame,
    jackpot_date: datetime,
    jackpot_dates: list,
    winner_numbers: Optional[list] = None,
    sample_size: int = 10000
) -> dict:
    """
    Analysiere einen Jackpot-Tag.

    Args:
        df: KENO-Daten
        jackpot_date: Datum des Jackpots
        jackpot_dates: Liste aller Jackpot-Daten
        winner_numbers: Bekannte Gewinner-Zahlen (falls verfügbar)
        sample_size: Anzahl zufälliger Kombinationen für Vergleich (0 = alle)
    """
    print(f"\n{'='*70}")
    print(f"Analysiere Jackpot: {jackpot_date.strftime('%d.%m.%Y')}")
    print(f"{'='*70}")

    # Ziehungszahlen holen
    draw_numbers = get_draw_numbers(df, jackpot_date)
    if not draw_numbers:
        print(f"FEHLER: Keine Ziehungsdaten für {jackpot_date}")
        return {}

    print(f"Ziehungszahlen (20): {draw_numbers}")

    if winner_numbers:
        print(f"Gewinner-Zahlen (10): {sorted(winner_numbers)}")
        # Prüfe ob Gewinner-Zahlen Subset der Ziehung sind
        if not set(winner_numbers).issubset(set(draw_numbers)):
            print("WARNUNG: Gewinner-Zahlen sind kein Subset der Ziehung!")

    # Historische Daten vorbereiten
    print("\nLade historische Daten...")
    hist_freq_30d = get_historical_frequency(df, draw_numbers, jackpot_date, window_days=30)
    hist_freq_60d = get_historical_frequency(df, draw_numbers, jackpot_date, window_days=60)
    jp_freq = get_jackpot_frequency(df, draw_numbers, jackpot_dates, jackpot_date)

    print(f"Historische Frequenz (30d): {hist_freq_30d}")
    print(f"Jackpot-Frequenz (vor diesem Tag): {jp_freq}")

    # Alle Kombinationen generieren
    total_combos = 184756  # C(20,10)
    print(f"\nGeneriere Kombinationen... (Total: {total_combos:,})")

    all_combos = list(combinations(draw_numbers, 10))

    # Sample für Performance
    if sample_size > 0 and sample_size < len(all_combos):
        print(f"Verwende Sample von {sample_size:,} Kombinationen für schnelle Analyse")
        np.random.seed(42)
        sample_indices = np.random.choice(len(all_combos), sample_size, replace=False)
        sample_combos = [all_combos[i] for i in sample_indices]

        # Gewinner-Kombination immer inkludieren
        if winner_numbers:
            winner_tuple = tuple(sorted(winner_numbers))
            if winner_tuple not in sample_combos:
                sample_combos.append(winner_tuple)
    else:
        sample_combos = all_combos

    # Metriken berechnen
    print(f"Berechne Metriken für {len(sample_combos):,} Kombinationen...")
    start_time = time.time()

    results = []
    winner_metrics = None

    for i, combo in enumerate(sample_combos):
        if i % 10000 == 0 and i > 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            remaining = (len(sample_combos) - i) / rate
            print(f"  {i:,}/{len(sample_combos):,} ({remaining:.1f}s verbleibend)")

        metrics = calculate_combination_metrics(
            combo,
            hist_freq_30d,
            jp_freq,
            draw_numbers
        )
        metrics["combo"] = combo
        metrics["is_winner"] = False

        if winner_numbers and set(combo) == set(winner_numbers):
            metrics["is_winner"] = True
            winner_metrics = metrics.copy()

        results.append(metrics)

    elapsed = time.time() - start_time
    print(f"Fertig in {elapsed:.1f}s")

    # Statistiken berechnen
    results_df = pd.DataFrame(results)

    print("\n" + "="*70)
    print("STATISTIKEN ALLER KOMBINATIONEN")
    print("="*70)

    numeric_cols = ["birthday_count", "combo_sum", "spread", "hist_freq_sum",
                    "jp_freq_sum", "consecutive_pairs", "max_gap", "decades_used"]

    stats = {}
    for col in numeric_cols:
        stats[col] = {
            "min": results_df[col].min(),
            "max": results_df[col].max(),
            "mean": results_df[col].mean(),
            "std": results_df[col].std(),
            "median": results_df[col].median(),
        }
        print(f"\n{col}:")
        print(f"  Min: {stats[col]['min']:.2f}, Max: {stats[col]['max']:.2f}")
        print(f"  Mean: {stats[col]['mean']:.2f}, Std: {stats[col]['std']:.2f}")
        print(f"  Median: {stats[col]['median']:.2f}")

    # Gewinner-Analyse
    if winner_metrics:
        print("\n" + "="*70)
        print("GEWINNER-KOMBINATION ANALYSE")
        print("="*70)
        print(f"Zahlen: {sorted(winner_metrics['combo'])}")

        for col in numeric_cols:
            val = winner_metrics[col]
            mean = stats[col]["mean"]
            std = stats[col]["std"]
            z_score = (val - mean) / std if std > 0 else 0
            percentile = (results_df[col] <= val).mean() * 100

            indicator = ""
            if abs(z_score) > 2:
                indicator = " ⚠️ AUFFÄLLIG!"
            elif abs(z_score) > 1:
                indicator = " 📊 Interessant"

            print(f"\n{col}: {val:.2f}")
            print(f"  Z-Score: {z_score:+.2f}, Perzentil: {percentile:.1f}%{indicator}")

    # Ergebnis speichern
    result = {
        "jackpot_date": jackpot_date.strftime("%d.%m.%Y"),
        "draw_numbers": draw_numbers,
        "winner_numbers": sorted(winner_numbers) if winner_numbers else None,
        "total_combinations": total_combos,
        "sample_size": len(sample_combos),
        "statistics": stats,
        "winner_metrics": winner_metrics,
        "historical_freq_30d": hist_freq_30d,
        "jackpot_freq": jp_freq,
    }

    return result


def main():
    base_path = Path(__file__).parent.parent

    print("="*70)
    print("JACKPOT-KOMBINATIONEN ANALYSE")
    print("Reverse Engineering des KENO-Systems")
    print("="*70)

    # Daten laden
    print("\nLade Daten...")
    df = load_keno_data(base_path)
    jackpot_dates = load_jackpot_dates(base_path)
    print(f"Ziehungen geladen: {len(df)}")
    print(f"Jackpot-Tage gefunden: {len(jackpot_dates)}")

    # Bekannte Gewinner-Fälle
    known_winners = {
        "25.10.2025": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],  # Kyritz
        # Weitere Fälle hier hinzufügen wenn gefunden
    }

    all_results = []

    # Analysiere Kyritz-Fall (bekannte Gewinner-Zahlen)
    kyritz_date = datetime(2025, 10, 25)
    result = analyze_jackpot_day(
        df,
        kyritz_date,
        jackpot_dates,
        winner_numbers=known_winners.get("25.10.2025"),
        sample_size=50000  # Größeres Sample für genauere Statistiken
    )
    all_results.append(result)

    # Speichern
    output_path = base_path / "results" / "jackpot_combination_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        # Konvertiere tuples zu lists für JSON
        for r in all_results:
            if r.get("winner_metrics"):
                r["winner_metrics"]["combo"] = list(r["winner_metrics"]["combo"])
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "="*70)
    print("ZUSAMMENFASSUNG")
    print("="*70)

    if result.get("winner_metrics"):
        wm = result["winner_metrics"]
        print(f"\nKyritz-Gewinner Auffälligkeiten:")
        print(f"  Birthday-Zahlen: {wm['birthday_count']}/10 ({wm['birthday_pct']:.0f}%)")
        print(f"  Summe: {wm['combo_sum']}")
        print(f"  Spread: {wm['spread']}")
        print(f"  Jackpot-Frequenz: {wm['jp_freq_sum']}")
        print(f"  Historische Frequenz (30d): {wm['hist_freq_sum']}")


if __name__ == "__main__":
    main()
