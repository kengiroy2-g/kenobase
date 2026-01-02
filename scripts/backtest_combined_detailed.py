"""
DETAILLIERTER BACKTEST: Kombinierte KENO-Strategie

Analysiert jeden Filter einzeln und in Kombination.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from collections import defaultdict


def load_data():
    """Lade alle benoetigten Daten."""
    # KENO Daten
    keno_path = Path("data/raw/keno/KENO_ab_2022_bereinigt.csv")
    keno_df = pd.read_csv(keno_path, sep=";", decimal=",")
    keno_df["Datum"] = pd.to_datetime(keno_df["Datum"], format="%d.%m.%Y")

    # Jackpot-Tage
    paths = [
        Path("Keno_GPTs/Keno_GQ_2022_2023-2024.csv"),
        Path("Keno_GPTs/Keno_GQ_2025.csv"),
        Path("Keno_GPTs/Keno_GQ_2024.csv"),
        Path("Keno_GPTs/Keno_GQ_2023.csv"),
        Path("Keno_GPTs/Keno_GQ_2022.csv"),
    ]

    all_quoten = []
    for path in paths:
        if path.exists():
            try:
                df = pd.read_csv(path, encoding="utf-8-sig")
                all_quoten.append(df)
            except:
                pass

    quoten_df = pd.concat(all_quoten, ignore_index=True)

    def parse_date(date_str):
        if pd.isna(date_str):
            return pd.NaT
        date_str = str(date_str).strip()
        if ", " in date_str and len(date_str.split(", ")[0]) <= 3:
            date_str = date_str.split(", ")[1]
        if date_str.count(".") == 2 and len(date_str.split(".")[-1]) == 4:
            try:
                return pd.to_datetime(date_str, format="%d.%m.%Y")
            except:
                pass
        return pd.NaT

    quoten_df["Datum"] = quoten_df["Datum"].apply(parse_date)
    quoten_df = quoten_df.dropna(subset=["Datum"])

    # Jackpot = Typ 10, 10 Richtige, Gewinner > 0
    jackpot_mask = (quoten_df["Keno-Typ"] == 10) & (quoten_df["Anzahl richtiger Zahlen"] == 10)
    jackpot_df = quoten_df[jackpot_mask].copy()

    jackpot_df["Anzahl der Gewinner"] = jackpot_df["Anzahl der Gewinner"].astype(str).str.replace(".", "").str.replace(",", ".")
    jackpot_df["Anzahl der Gewinner"] = pd.to_numeric(jackpot_df["Anzahl der Gewinner"], errors="coerce").fillna(0).astype(int)

    jackpot_days = set(jackpot_df[jackpot_df["Anzahl der Gewinner"] > 0]["Datum"].dt.date)

    return keno_df, jackpot_days


def analyze_single_filters(keno_df, jackpot_days):
    """Analysiere jeden Filter einzeln."""

    print("="*80)
    print("EINZELFILTER-ANALYSE")
    print("="*80)

    all_dates = keno_df["Datum"].dt.date.tolist()
    total_days = len(all_dates)
    total_jackpots = len([d for d in all_dates if d in jackpot_days])

    baseline_rate = total_jackpots / total_days
    print(f"\nBaseline: {total_jackpots} Jackpots in {total_days} Tagen = {baseline_rate*100:.2f}%")

    results = {}

    # Filter 1: Tag des Monats
    print("\n--- FILTER 1: Tag des Monats ---")
    for start_day in [1, 8, 15, 22]:
        end_day = start_day + 6
        filter_days = [d for d in all_dates if start_day <= d.day <= end_day]
        filter_jackpots = len([d for d in filter_days if d in jackpot_days])

        if len(filter_days) > 0:
            rate = filter_jackpots / len(filter_days)
            boost = rate / baseline_rate if baseline_rate > 0 else 0
            print(f"  Tag {start_day:2}-{end_day:2}: {len(filter_days):4} Tage, {filter_jackpots:2} JP, "
                  f"{rate*100:.2f}% ({boost:.2f}x)")

            results[f"day_{start_day}_{end_day}"] = {
                "days": len(filter_days),
                "jackpots": filter_jackpots,
                "rate": rate,
                "boost": boost
            }

    # Filter 2: Wochentag
    print("\n--- FILTER 2: Wochentag ---")
    weekday_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    for wd in range(7):
        filter_days = [d for d in all_dates if d.weekday() == wd]
        filter_jackpots = len([d for d in filter_days if d in jackpot_days])

        if len(filter_days) > 0:
            rate = filter_jackpots / len(filter_days)
            boost = rate / baseline_rate if baseline_rate > 0 else 0
            print(f"  {weekday_names[wd]}: {len(filter_days):4} Tage, {filter_jackpots:2} JP, "
                  f"{rate*100:.2f}% ({boost:.2f}x)")

    # Filter 3: Monat
    print("\n--- FILTER 3: Monat ---")
    for month in range(1, 13):
        filter_days = [d for d in all_dates if d.month == month]
        filter_jackpots = len([d for d in filter_days if d in jackpot_days])

        if len(filter_days) > 0:
            rate = filter_jackpots / len(filter_days)
            boost = rate / baseline_rate if baseline_rate > 0 else 0
            month_name = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun",
                         "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"][month-1]
            print(f"  {month_name}: {len(filter_days):4} Tage, {filter_jackpots:2} JP, "
                  f"{rate*100:.2f}% ({boost:.2f}x)")

    # Filter 4: Quartal
    print("\n--- FILTER 4: Quartal ---")
    for q in range(1, 5):
        months = [q*3-2, q*3-1, q*3]
        filter_days = [d for d in all_dates if d.month in months]
        filter_jackpots = len([d for d in filter_days if d in jackpot_days])

        if len(filter_days) > 0:
            rate = filter_jackpots / len(filter_days)
            boost = rate / baseline_rate if baseline_rate > 0 else 0
            print(f"  Q{q}: {len(filter_days):4} Tage, {filter_jackpots:2} JP, "
                  f"{rate*100:.2f}% ({boost:.2f}x)")

    return results


def analyze_cooldown(keno_df, jackpot_days):
    """Analysiere Cooldown-Effekt nach Jackpots."""

    print("\n" + "="*80)
    print("COOLDOWN-ANALYSE")
    print("="*80)

    all_dates = sorted(keno_df["Datum"].dt.date.tolist())
    jackpot_list = sorted([d for d in all_dates if d in jackpot_days])

    total_days = len(all_dates)
    total_jackpots = len(jackpot_list)
    baseline_rate = total_jackpots / total_days

    print(f"\nAnalysiere Tage NACH Jackpots:")

    # Fuer jeden Tag: Berechne Tage seit letztem Jackpot
    days_since_jackpot = {}
    last_jp = None

    for date in all_dates:
        if date in jackpot_days:
            if last_jp is not None:
                days_since_jackpot[date] = (date - last_jp).days
            last_jp = date
        elif last_jp is not None:
            days_since_jackpot[date] = (date - last_jp).days

    # Gruppiere nach Tagen seit Jackpot
    print("\n  Tage nach JP    Tage     Jackpots    Quote      vs. Baseline")
    print("-"*65)

    for period_start, period_end in [(1, 7), (8, 14), (15, 21), (22, 30), (31, 60), (61, 999)]:
        period_dates = [d for d, days in days_since_jackpot.items()
                       if period_start <= days <= period_end]
        period_jackpots = len([d for d in period_dates if d in jackpot_days])

        if len(period_dates) > 0:
            rate = period_jackpots / len(period_dates)
            boost = rate / baseline_rate if baseline_rate > 0 else 0
            label = f"{period_start:2}-{period_end:2}" if period_end < 999 else f"{period_start:2}+"
            print(f"  {label:12}    {len(period_dates):4}     {period_jackpots:4}        "
                  f"{rate*100:.2f}%      {boost:.2f}x")


def analyze_combined_best(keno_df, jackpot_days):
    """Analysiere die beste Kombination von Filtern."""

    print("\n" + "="*80)
    print("BESTE FILTER-KOMBINATION")
    print("="*80)

    all_dates = keno_df["Datum"].dt.date.tolist()
    total_days = len(all_dates)
    total_jackpots = len([d for d in all_dates if d in jackpot_days])
    baseline_rate = total_jackpots / total_days

    # Beste Einzelfilter basierend auf vorheriger Analyse:
    # - Tag 22-28 (1.63x)
    # - Q1 leicht besser

    combinations = [
        ("Tag 22-28", lambda d: 22 <= d.day <= 28),
        ("Tag 22-31", lambda d: 22 <= d.day <= 31),
        ("Nicht Nov", lambda d: d.month != 11),
        ("Q1", lambda d: d.month in [1, 2, 3]),
        ("Tag 22-28 + Q1", lambda d: (22 <= d.day <= 28) and (d.month in [1, 2, 3])),
        ("Tag 22-28 + Nicht Nov", lambda d: (22 <= d.day <= 28) and (d.month != 11)),
    ]

    print(f"\n{'Kombination':<30} {'Tage':<8} {'JP':<6} {'Quote':<10} {'Boost':<8} {'JP-Anteil'}")
    print("-"*80)

    for name, filter_func in combinations:
        filter_days = [d for d in all_dates if filter_func(d)]
        filter_jackpots = len([d for d in filter_days if d in jackpot_days])

        if len(filter_days) > 0:
            rate = filter_jackpots / len(filter_days)
            boost = rate / baseline_rate if baseline_rate > 0 else 0
            jp_coverage = filter_jackpots / total_jackpots * 100 if total_jackpots > 0 else 0
            cost_reduction = (1 - len(filter_days) / total_days) * 100

            print(f"{name:<30} {len(filter_days):<8} {filter_jackpots:<6} {rate*100:.2f}%     "
                  f"{boost:.2f}x    {jp_coverage:.1f}%")


def calculate_efficiency(keno_df, jackpot_days):
    """Berechne Effizienz-Score fuer verschiedene Strategien."""

    print("\n" + "="*80)
    print("EFFIZIENZ-RANKING")
    print("="*80)

    all_dates = keno_df["Datum"].dt.date.tolist()
    total_days = len(all_dates)
    total_jackpots = len([d for d in all_dates if d in jackpot_days])

    strategies = [
        ("Jeden Tag spielen", lambda d: True),
        ("Tag 22-28", lambda d: 22 <= d.day <= 28),
        ("Tag 22-31", lambda d: 22 <= d.day <= 31),
        ("Nur Q1", lambda d: d.month in [1, 2, 3]),
        ("Nur Q4", lambda d: d.month in [10, 11, 12]),
        ("Nicht November", lambda d: d.month != 11),
        ("Tag 22-28 + Q1", lambda d: (22 <= d.day <= 28) and (d.month in [1, 2, 3])),
        ("Tag 24-28", lambda d: 24 <= d.day <= 28),
        ("Tag 25-28", lambda d: 25 <= d.day <= 28),
    ]

    print(f"\n{'Strategie':<25} {'Tage':<8} {'JP':<5} {'Quote':<8} {'Effizienz':<12} {'Kosten-Spar.'}")
    print("-"*80)

    results = []
    for name, filter_func in strategies:
        filter_days = [d for d in all_dates if filter_func(d)]
        filter_jackpots = len([d for d in filter_days if d in jackpot_days])

        if len(filter_days) > 0:
            rate = filter_jackpots / len(filter_days)
            cost_reduction = 1 - (len(filter_days) / total_days)
            jp_coverage = filter_jackpots / total_jackpots if total_jackpots > 0 else 0

            # Effizienz = JP-Anteil / Kosten-Anteil
            cost_ratio = len(filter_days) / total_days
            efficiency = jp_coverage / cost_ratio if cost_ratio > 0 else 0

            results.append({
                "name": name,
                "days": len(filter_days),
                "jackpots": filter_jackpots,
                "rate": rate,
                "efficiency": efficiency,
                "cost_reduction": cost_reduction,
                "jp_coverage": jp_coverage
            })

    # Sortiere nach Effizienz
    results.sort(key=lambda x: x["efficiency"], reverse=True)

    for r in results:
        print(f"{r['name']:<25} {r['days']:<8} {r['jackpots']:<5} {r['rate']*100:.2f}%   "
              f"{r['efficiency']:.2f}x         {r['cost_reduction']*100:.1f}%")

    return results


def main():
    """Hauptfunktion."""
    print("Lade Daten...")
    keno_df, jackpot_days = load_data()

    print(f"  Ziehungen: {len(keno_df)}")
    print(f"  Jackpot-Tage: {len(jackpot_days)}")

    # Einzelfilter
    analyze_single_filters(keno_df, jackpot_days)

    # Cooldown
    analyze_cooldown(keno_df, jackpot_days)

    # Kombinationen
    analyze_combined_best(keno_df, jackpot_days)

    # Effizienz-Ranking
    results = calculate_efficiency(keno_df, jackpot_days)

    # Zusammenfassung
    print("\n" + "="*80)
    print("EMPFEHLUNG")
    print("="*80)

    best = results[0]
    print(f"""
BESTE STRATEGIE: {best['name']}

Kennzahlen:
  - Spieltage: {best['days']} ({best['days']/len(keno_df)*100:.1f}% aller Tage)
  - Jackpots: {best['jackpots']} ({best['jp_coverage']*100:.1f}% aller Jackpots)
  - Trefferquote: {best['rate']*100:.2f}%
  - Effizienz: {best['efficiency']:.2f}x
  - Kosten-Ersparnis: {best['cost_reduction']*100:.1f}%

INTERPRETATION:
  Mit {best['cost_reduction']*100:.0f}% weniger Spieltagen werden
  {best['jp_coverage']*100:.0f}% der Jackpots abgedeckt.
    """)


if __name__ == "__main__":
    main()
