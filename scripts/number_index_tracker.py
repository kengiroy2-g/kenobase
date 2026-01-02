#!/usr/bin/env python
"""
Number Index Tracker - KENO Zahlen-Tracking System

Tracking-Metriken:
- Index: Tage in Folge (Streak) - Reset auf 0 wenn nicht gezogen
- Count: Gesamterscheinungen - RESET AUF 0 AM JACKPOT-TAG für gezogene Zahlen
- JCount: Erscheinungen an Jackpot-Tagen (kumulativ)

Jackpot-Tage 2025:
- 16.01.2025, 29.01.2025, 02.02.2025, 16.02.2025
"""

import pandas as pd
from datetime import datetime
from pathlib import Path


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Lade KENO-Daten aus CSV."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    return df.sort_values("Datum").reset_index(drop=True)


def load_jackpot_dates(base_path: Path, year: int = 2025) -> list:
    """Lade Jackpot-Daten aus timeline CSV."""
    timeline_path = base_path / "data" / "processed" / "ecosystem" / f"timeline_{year}.csv"

    if timeline_path.exists():
        tl = pd.read_csv(timeline_path)
        tl["datum"] = pd.to_datetime(tl["datum"])
        jackpot_dates = tl[tl["keno_jackpot"] == 1]["datum"].tolist()
        return jackpot_dates
    else:
        # Fallback: Bekannte Jackpot-Tage 2025
        return [
            datetime(2025, 1, 16),
            datetime(2025, 1, 29),
            datetime(2025, 2, 2),
            datetime(2025, 2, 16),
        ]


def track_numbers(df: pd.DataFrame, jackpot_dates: list, start_date: datetime, end_date: datetime):
    """
    Tracke Zahlen mit Index, Mcount, Count, JCount, JCountY, TCount.

    - Index: Tage in Folge (Streak)
    - Mcount: Monats-Count (Reset am Monatsanfang)
    - Count: Gesamt-Count (Reset am Tag NACH Jackpot)
    - JCount: Jackpot-Erscheinungen fortlaufend (kein Reset)
    - JCountY: Jackpot-Erscheinungen pro Jahr (Reset bei Jahreswechsel)
    - TCount: Total-Count im Suchzeitraum (kein Reset)
    """
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    # Filter auf Zeitraum
    mask = (df["Datum"] >= start_date) & (df["Datum"] <= end_date)
    period_df = df[mask].copy()

    # Initialisierung
    number_index = {i: 0 for i in range(1, 71)}
    month_count = {i: 0 for i in range(1, 71)}
    number_count = {i: 0 for i in range(1, 71)}
    jackpot_count = {i: 0 for i in range(1, 71)}      # JCount - fortlaufend
    jackpot_count_year = {i: 0 for i in range(1, 71)} # JCountY - pro Jahr
    total_count = {i: 0 for i in range(1, 71)}        # TCount - nie Reset
    previous_drawn = set()
    last_jackpot_numbers = set()
    current_month = None
    current_year = None  # Für Jahreswechsel-Erkennung

    results = []

    for _, row in period_df.iterrows():
        date = row["Datum"]
        is_jackpot = date in jackpot_dates

        # JAHRESWECHSEL: JCountY auf 0 zurücksetzen
        if current_year is None or date.year != current_year:
            jackpot_count_year = {i: 0 for i in range(1, 71)}
            current_year = date.year

        # MONATSWECHSEL: Mcount auf 0 zurücksetzen
        if current_month is None or date.month != current_month:
            month_count = {i: 0 for i in range(1, 71)}
            current_month = date.month

        # Gezogene Zahlen in Original-Reihenfolge
        drawn = [int(row[col]) for col in pos_cols]
        drawn_set = set(drawn)

        # NACH JACKPOT: Count für Jackpot-Zahlen zurücksetzen
        if last_jackpot_numbers:
            for num in last_jackpot_numbers:
                number_count[num] = 0
            last_jackpot_numbers = set()

        # Neuer Index berechnen
        new_index = {i: 0 for i in range(1, 71)}

        for num in drawn:
            if num in previous_drawn:
                new_index[num] = number_index[num] + 1
            else:
                new_index[num] = 1

        # Counts erhöhen
        for num in drawn_set:
            month_count[num] += 1
            number_count[num] += 1
            total_count[num] += 1  # TCount - nie Reset
            if is_jackpot:
                jackpot_count[num] += 1       # JCount - fortlaufend
                jackpot_count_year[num] += 1  # JCountY - pro Jahr

        # Jackpot-Zahlen merken für Reset am NÄCHSTEN Tag
        if is_jackpot:
            last_jackpot_numbers = drawn_set.copy()

        # Ergebnis speichern
        result = {
            "Datum": date.strftime("%d.%m.%Y"),
            "Wochentag": date.strftime("%A"),
            "Jackpot": "★ JACKPOT" if is_jackpot else "",
            "Zahlen": drawn,
            "Index": [new_index[num] for num in drawn],
            "Mcount": [month_count[num] for num in drawn],
            "Count": [number_count[num] for num in drawn],
            "JCount": [jackpot_count[num] for num in drawn],
            "JCountY": [jackpot_count_year[num] for num in drawn],
            "TCount": [total_count[num] for num in drawn],
        }
        results.append(result)

        # Update für nächsten Tag
        number_index = new_index
        previous_drawn = drawn_set

    return results


def print_results(results: list):
    """Ausgabe der Ergebnisse im KENO-Format."""
    print("=" * 110)
    print("NUMBER INDEX TRACKER - KENO Zahlen-Tracking")
    print("Index=Streak | Mcount=Monat | Count=JP-Reset | JCount=JP-Total | JCountY=JP-Jahr | TCount=Total")
    print("=" * 110)

    for r in results:
        jp_marker = r["Jackpot"]
        print(f"\n{r['Datum']} ({r['Wochentag']}) {jp_marker}")
        print("-" * 90)

        # Zahlen-Zeile
        zahlen_str = " ".join([f"{z:2d}" for z in r["Zahlen"]])
        print(f"Zahlen:  {zahlen_str}")

        # Index-Zeile
        index_str = " ".join([f"{i:2d}" for i in r["Index"]])
        print(f"Index:   {index_str}")

        # Mcount-Zeile
        mcount_str = " ".join([f"{m:2d}" for m in r["Mcount"]])
        print(f"Mcount:  {mcount_str}")

        # Count-Zeile
        count_str = " ".join([f"{c:2d}" for c in r["Count"]])
        print(f"Count:   {count_str}")

        # JCount-Zeile (fortlaufend)
        jcount_str = " ".join([f"{j:2d}" for j in r["JCount"]])
        print(f"JCount:  {jcount_str}")

        # JCountY-Zeile (pro Jahr)
        jcounty_str = " ".join([f"{j:2d}" for j in r["JCountY"]])
        print(f"JCountY: {jcounty_str}")

        # TCount-Zeile (Total)
        tcount_str = " ".join([f"{t:2d}" for t in r["TCount"]])
        print(f"TCount:  {tcount_str}")

        # Highlight hohe Index-Werte
        high_index = [(r["Zahlen"][i], r["Index"][i]) for i in range(20) if r["Index"][i] >= 4]
        if high_index:
            print(f"  → Hoher Index (≥4): {high_index}")


def main():
    base_path = Path(__file__).parent.parent

    # Daten laden
    print("Lade KENO-Daten...")
    df = load_keno_data(base_path)

    print("Lade Jackpot-Daten...")
    jackpot_dates = load_jackpot_dates(base_path, 2025)
    print(f"Jackpot-Tage: {[d.strftime('%d.%m.%Y') for d in jackpot_dates]}")

    # Januar 2022 bis Dezember 2025 - DURCHGEHEND
    print("\n" + "=" * 100)
    print("JANUAR 2022 - DEZEMBER 2025 (DURCHGEHEND)")
    print("=" * 100)

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2025, 12, 31)

    # Lade Jackpot-Daten für alle Jahre
    jackpot_dates_2024 = load_jackpot_dates(base_path, 2024)
    jackpot_dates_2023 = load_jackpot_dates(base_path, 2023)
    jackpot_dates_2022 = load_jackpot_dates(base_path, 2022)
    all_jackpot_dates = jackpot_dates + jackpot_dates_2024 + jackpot_dates_2023 + jackpot_dates_2022
    print(f"Jackpot-Tage 2024: {[d.strftime('%d.%m.%Y') for d in jackpot_dates_2024]}")
    print(f"Jackpot-Tage 2023: {[d.strftime('%d.%m.%Y') for d in jackpot_dates_2023]}")
    print(f"Jackpot-Tage 2022: {[d.strftime('%d.%m.%Y') for d in jackpot_dates_2022]}")

    results = track_numbers(df, all_jackpot_dates, start_date, end_date)
    print_results(results)


if __name__ == "__main__":
    main()
