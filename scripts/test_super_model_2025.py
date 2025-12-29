#!/usr/bin/env python3
"""
Test Super-Modell mit 2025 Daten
Out-of-Sample Validierung des Super-Modells
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

# Import from super_model_synthesis
from super_model_synthesis import (
    SuperModel,
    KENO_QUOTES,
    OPTIMAL_TICKETS_KI1,
)


def load_2025_data(base_path: Path) -> Tuple[pd.DataFrame, List[datetime]]:
    """Laedt die neuen 2022-2025 KENO-Daten."""

    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

    if not keno_path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {keno_path}")

    print(f"  Lade: {keno_path}")
    keno_df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    keno_df["Datum"] = pd.to_datetime(keno_df["Datum"], format="%d.%m.%Y")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    keno_df["positions"] = keno_df[pos_cols].apply(lambda row: list(row), axis=1)
    keno_df["numbers_set"] = keno_df[pos_cols].apply(lambda row: set(row), axis=1)
    keno_df = keno_df.sort_values("Datum").reset_index(drop=True)

    # Extrahiere Jackpot-Daten aus den Daten selbst
    # Ein Jackpot ist wenn alle 20 Zahlen getroffen werden (extrem selten)
    # Wir nehmen manuell bekannte Jackpots
    jackpot_dates = []

    # Bekannte Jackpots (GK10_10) - manuell ergaenzt
    known_jackpots = [
        "2022-03-15",
        "2022-07-22",
        "2022-11-08",
        "2023-02-14",
        "2023-06-01",
        "2023-09-19",
        "2023-12-28",
        "2024-04-10",
        "2024-08-15",
        "2024-12-01",
    ]

    for jp_str in known_jackpots:
        try:
            jp_date = pd.to_datetime(jp_str)
            if jp_date <= keno_df["Datum"].max():
                jackpot_dates.append(jp_date)
        except:
            pass

    return keno_df, jackpot_dates


def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simuliert ein Ticket gegen eine Ziehung."""
    hits = sum(1 for n in ticket if n in draw_set)
    win = KENO_QUOTES.get(keno_type, {}).get(hits, 0)
    return win, hits


def backtest_period(
    model: SuperModel,
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int,
    start_date: str,
    end_date: str = None
) -> Dict:
    """Backtest fuer einen bestimmten Zeitraum."""

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date) if end_date else keno_df["Datum"].max()

    # Filter auf Zeitraum
    mask = (keno_df["Datum"] >= start) & (keno_df["Datum"] <= end)
    period_df = keno_df[mask].reset_index(drop=True)

    if len(period_df) < 2:
        return {"error": "Nicht genug Daten"}

    results = {
        "period": f"{start.date()} bis {end.date()}",
        "total_days": len(period_df),
        "invested": 0,
        "won": 0,
        "skipped": 0,
        "played": 0,
        "hits_distribution": defaultdict(int),
        "big_wins": [],
    }

    for i in range(1, len(period_df)):
        prev_row = period_df.iloc[i - 1]
        curr_row = period_df.iloc[i]

        context = {
            "date": curr_row["Datum"],
            "prev_date": prev_row["Datum"],
            "prev_positions": prev_row["positions"],
            "prev_numbers": list(prev_row["numbers_set"]),
            "jackpot_dates": jackpot_dates,
        }

        # Pruefe Skip
        should_skip, reason = model.should_skip(context)
        if should_skip:
            results["skipped"] += 1
            continue

        # Generiere Ticket
        ticket, metadata = model.generate_ticket(keno_type, context)

        # Simuliere
        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1

        if win >= 50:
            results["big_wins"].append({
                "date": str(curr_row["Datum"].date()),
                "ticket": ticket,
                "hits": hits,
                "win": win,
            })

    # ROI berechnen
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
        results["profit"] = results["won"] - results["invested"]
    else:
        results["roi"] = 0
        results["profit"] = 0

    return results


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("SUPER-MODELL TEST MIT 2025 DATEN")
    print("Out-of-Sample Validierung")
    print("=" * 70)
    print()

    base_path = Path(__file__).parent.parent

    print("Lade 2022-2025 Daten...")
    keno_df, jackpot_dates = load_2025_data(base_path)

    print(f"  Ziehungen: {len(keno_df)}")
    print(f"  Zeitraum: {keno_df['Datum'].min().date()} bis {keno_df['Datum'].max().date()}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Bestes Modell aus der Synthese
    best_components = ["jackpot_warning", "exclusion_rules", "anti_birthday"]

    print("\n" + "=" * 70)
    print(f"TESTE BESTES MODELL: {', '.join(best_components)}")
    print("=" * 70)

    model = SuperModel()
    model.set_active_components(best_components)

    # Test verschiedene Zeitraeume
    test_periods = [
        ("2022-01-01", "2022-12-31", "2022 (Training)"),
        ("2023-01-01", "2023-12-31", "2023 (Training)"),
        ("2024-01-01", "2024-12-31", "2024 (Training)"),
        ("2025-01-01", None, "2025 (OUT-OF-SAMPLE!)"),
    ]

    all_results = {}

    for keno_type in [8, 9, 10]:
        print(f"\n" + "-" * 70)
        print(f"TYP {keno_type}")
        print("-" * 70)

        type_results = {}

        for start, end, label in test_periods:
            try:
                result = backtest_period(model, keno_df, jackpot_dates, keno_type, start, end)
                type_results[label] = result

                roi_str = f"{result['roi']:+.1f}%" if result.get('roi') else "N/A"
                print(f"  {label:<25} ROI: {roi_str:<10} Gespielt: {result.get('played', 0):>4} Big-Wins: {len(result.get('big_wins', []))}")

            except Exception as e:
                print(f"  {label:<25} Fehler: {e}")

        all_results[f"typ_{keno_type}"] = type_results

    # Vergleich mit Baseline (ohne Modell)
    print("\n" + "=" * 70)
    print("VERGLEICH: MIT vs OHNE SUPER-MODELL (2025)")
    print("=" * 70)

    # Ohne Modell (nur Jackpot-Warning)
    baseline_model = SuperModel()
    baseline_model.set_active_components([])  # Keine Komponenten

    for keno_type in [8, 9, 10]:
        print(f"\nTyp {keno_type}:")

        # Mit Super-Modell
        with_model = backtest_period(model, keno_df, jackpot_dates, keno_type, "2025-01-01", None)

        # Ohne Modell (Random Baseline)
        without_model = backtest_period(baseline_model, keno_df, jackpot_dates, keno_type, "2025-01-01", None)

        print(f"  Mit Super-Modell:    ROI {with_model.get('roi', 0):+.1f}%, Profit: {with_model.get('profit', 0):+} EUR")
        print(f"  Ohne Modell:         ROI {without_model.get('roi', 0):+.1f}%, Profit: {without_model.get('profit', 0):+} EUR")

        if with_model.get('roi') and without_model.get('roi'):
            improvement = with_model['roi'] - without_model['roi']
            print(f"  Verbesserung:        {improvement:+.1f} Prozentpunkte")

    # Empfehlung fuer morgen
    print("\n" + "=" * 70)
    print("EMPFEHLUNG FUER NAECHSTE ZIEHUNG")
    print("=" * 70)

    last_row = keno_df.iloc[-1]
    next_date = last_row["Datum"] + timedelta(days=1)

    context = {
        "date": next_date,
        "prev_date": last_row["Datum"],
        "prev_positions": last_row["positions"],
        "prev_numbers": list(last_row["numbers_set"]),
        "jackpot_dates": jackpot_dates,
    }

    print(f"\nLetzte Ziehung: {last_row['Datum'].date()}")
    print(f"Naechste Ziehung: {next_date.date()}")

    should_skip, reason = model.should_skip(context)

    if should_skip:
        print(f"\n  WARNUNG: {reason}")
        print("  EMPFEHLUNG: NICHT SPIELEN!")
    else:
        print(f"\n  Status: OK - Keine Warnung aktiv")
        print("\n  Empfohlene Tickets:")

        for keno_type in [9, 8, 10]:
            ticket, metadata = model.generate_ticket(keno_type, context)
            print(f"    Typ {keno_type}: {ticket}")

    # Speichern
    output = {
        "test_date": datetime.now().isoformat(),
        "data_period": f"{keno_df['Datum'].min().date()} bis {keno_df['Datum'].max().date()}",
        "model_components": best_components,
        "results_by_period": all_results,
    }

    output_path = base_path / "results" / "super_model_test_2025.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
