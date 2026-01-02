#!/usr/bin/env python3
"""
TICKET-LEBENSZYKLUS: Walk-Forward Simulation

Simuliert ein dynamisches System:
1. Zu verschiedenen Zeitpunkten (Jahre, Quartale) Tickets erstellen
2. Performance ueber Zeit verfolgen
3. Analysieren ob Tickets "altern" oder stabil bleiben

Daten: 2022-2025 (4 Jahre)

Autor: Kenobase V2.2
Datum: 2025-12-30
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd

from kenobase.core.keno_quotes import get_fixed_quote


# =============================================================================
# TICKET-GENERIERUNG (basierend auf historischen Daten)
# =============================================================================

BIRTHDAY_NUMBERS = set(range(1, 32))
HIGH_NUMBERS = set(range(32, 71))


def generate_ticket_from_data(
    df: pd.DataFrame,
    keno_type: int,
    strategy: str = "frequency"
) -> List[int]:
    """
    Generiert ein Ticket basierend auf historischen Daten.

    Strategien:
    - frequency: Top-N haeufigste Zahlen
    - frequency_high: Top-N haeufigste aus 32-70
    - anti_birthday: Nur Zahlen 32-70
    """
    # Zahlenfrequenz berechnen
    freq = defaultdict(int)
    for _, row in df.iterrows():
        for n in row["numbers_set"]:
            freq[n] += 1

    if strategy == "frequency":
        # Top-N haeufigste
        sorted_numbers = sorted(freq.keys(), key=lambda x: -freq[x])
        return sorted_numbers[:keno_type]

    elif strategy == "frequency_high":
        # Top-N haeufigste aus 32-70
        high_freq = {n: f for n, f in freq.items() if n in HIGH_NUMBERS}
        sorted_high = sorted(high_freq.keys(), key=lambda x: -high_freq[x])
        return sorted_high[:keno_type]

    elif strategy == "anti_birthday":
        # Nur 32-70, nach Frequenz
        high_freq = {n: f for n, f in freq.items() if n in HIGH_NUMBERS}
        sorted_high = sorted(high_freq.keys(), key=lambda x: -high_freq[x])
        return sorted_high[:keno_type]

    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def generate_v2_style_ticket(df: pd.DataFrame, keno_type: int) -> List[int]:
    """
    Generiert ein V2-Style Ticket basierend auf aktuellen Daten.

    Methode:
    1. Berechne Frequenz der letzten 90 Tage
    2. Bevorzuge High-Numbers (32-70)
    3. Maximal 2 Birthday-Zahlen erlaubt
    """
    # Letzte 90 Tage
    recent_df = df.tail(90)

    freq = defaultdict(int)
    for _, row in recent_df.iterrows():
        for n in row["numbers_set"]:
            freq[n] += 1

    # High numbers priorisieren
    high_numbers = [(n, freq[n]) for n in HIGH_NUMBERS if freq[n] > 0]
    high_numbers.sort(key=lambda x: -x[1])

    birthday_numbers = [(n, freq[n]) for n in BIRTHDAY_NUMBERS if freq[n] > 0]
    birthday_numbers.sort(key=lambda x: -x[1])

    # Ticket zusammenstellen
    ticket = []

    # Erst High-Numbers (keno_type - 2)
    for n, _ in high_numbers[:keno_type - 2]:
        ticket.append(n)

    # Dann max 2 Birthday
    for n, _ in birthday_numbers[:2]:
        if len(ticket) < keno_type:
            ticket.append(n)

    # Falls noch Platz, mehr High-Numbers
    for n, _ in high_numbers[keno_type - 2:]:
        if len(ticket) < keno_type:
            if n not in ticket:
                ticket.append(n)

    return sorted(ticket[:keno_type])


# =============================================================================
# WALK-FORWARD SIMULATION
# =============================================================================

def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simuliert ein Ticket."""
    hits = sum(1 for n in ticket if n in draw_set)
    return int(get_fixed_quote(keno_type, hits)), hits


def walk_forward_simulation(
    df: pd.DataFrame,
    keno_type: int = 9,
    train_days: int = 365,
    test_days: int = 90,
    step_days: int = 90
) -> Dict:
    """
    Walk-Forward Simulation:

    1. Train auf ersten `train_days` Tagen
    2. Generiere Ticket
    3. Test auf naechsten `test_days` Tagen
    4. Verschiebe um `step_days`
    5. Wiederhole
    """
    results = {
        "keno_type": keno_type,
        "train_days": train_days,
        "test_days": test_days,
        "step_days": step_days,
        "iterations": [],
    }

    strategies = ["frequency", "frequency_high", "v2_style"]

    i = 0
    while i + train_days + test_days <= len(df):
        train_df = df.iloc[i:i + train_days]
        test_df = df.iloc[i + train_days:i + train_days + test_days]

        train_start = train_df["Datum"].min()
        train_end = train_df["Datum"].max()
        test_start = test_df["Datum"].min()
        test_end = test_df["Datum"].max()

        iteration = {
            "iteration": len(results["iterations"]) + 1,
            "train_period": f"{train_start.date()} - {train_end.date()}",
            "test_period": f"{test_start.date()} - {test_end.date()}",
            "strategies": {},
        }

        for strategy in strategies:
            # Ticket generieren
            if strategy == "v2_style":
                ticket = generate_v2_style_ticket(train_df, keno_type)
            else:
                ticket = generate_ticket_from_data(train_df, keno_type, strategy)

            # Test
            wins = 0
            hits_dist = defaultdict(int)
            high_wins = []

            for _, row in test_df.iterrows():
                win, hits = simulate_ticket(ticket, keno_type, row["numbers_set"])
                wins += win
                hits_dist[hits] += 1
                if win >= 100:
                    high_wins.append({
                        "date": str(row["Datum"].date()),
                        "hits": hits,
                        "win": win,
                    })

            invested = len(test_df)
            roi = (wins - invested) / invested * 100 if invested > 0 else 0

            iteration["strategies"][strategy] = {
                "ticket": ticket,
                "invested": invested,
                "won": wins,
                "roi": roi,
                "high_wins": len(high_wins),
                "high_win_details": high_wins,
            }

        results["iterations"].append(iteration)
        i += step_days

    return results


# =============================================================================
# JAHRES-BASIERTE ANALYSE
# =============================================================================

def yearly_ticket_analysis(df: pd.DataFrame, keno_type: int = 9) -> Dict:
    """
    Jahres-basierte Analyse:

    1. Erstelle Ticket basierend auf Jahr X
    2. Teste auf Jahr X+1
    3. Verfolge ueber alle Folgejahre
    """
    years = sorted(df["Datum"].dt.year.unique())

    results = {
        "keno_type": keno_type,
        "tickets_by_year": {},
        "performance_matrix": {},
    }

    strategies = ["frequency", "frequency_high", "v2_style"]

    for train_year in years[:-1]:  # Nicht das letzte Jahr
        train_df = df[df["Datum"].dt.year == train_year]

        year_tickets = {}

        for strategy in strategies:
            if strategy == "v2_style":
                ticket = generate_v2_style_ticket(train_df, keno_type)
            else:
                ticket = generate_ticket_from_data(train_df, keno_type, strategy)

            year_tickets[strategy] = ticket

        results["tickets_by_year"][int(train_year)] = year_tickets

        # Teste auf alle Folgejahre
        for test_year in years:
            if test_year <= train_year:
                continue

            test_df = df[df["Datum"].dt.year == test_year]

            for strategy, ticket in year_tickets.items():
                wins = 0
                high_wins = 0

                for _, row in test_df.iterrows():
                    win, hits = simulate_ticket(ticket, keno_type, row["numbers_set"])
                    wins += win
                    if win >= 100:
                        high_wins += 1

                invested = len(test_df)
                roi = (wins - invested) / invested * 100 if invested > 0 else 0

                key = f"train_{train_year}_test_{test_year}_{strategy}"
                results["performance_matrix"][key] = {
                    "train_year": int(train_year),
                    "test_year": int(test_year),
                    "strategy": strategy,
                    "ticket": ticket,
                    "invested": invested,
                    "won": wins,
                    "roi": roi,
                    "high_wins": high_wins,
                    "years_apart": int(test_year - train_year),
                }

    return results


# =============================================================================
# TICKET-ALTERUNG ANALYSE
# =============================================================================

def ticket_aging_analysis(df: pd.DataFrame, keno_type: int = 9) -> Dict:
    """
    Analysiert wie Tickets "altern":

    1. Erstelle Ticket zu einem Zeitpunkt
    2. Messe Performance in 28-Tage-Bloecken
    3. Analysiere ob Performance ueber Zeit abnimmt
    """
    results = {
        "keno_type": keno_type,
        "aging_curves": {},
    }

    # Erstelle Tickets zu verschiedenen Startpunkten
    start_points = [0, 365, 730]  # Tag 0, Jahr 1, Jahr 2

    for start_idx in start_points:
        if start_idx + 365 >= len(df):
            continue

        # Train auf ersten 365 Tagen ab Startpunkt
        train_df = df.iloc[start_idx:start_idx + 365]
        ticket = generate_v2_style_ticket(train_df, keno_type)

        start_date = train_df["Datum"].min()

        # Verfolge in 28-Tage-Bloecken
        aging_curve = []
        test_start = start_idx + 365

        block = 0
        while test_start + 28 <= len(df):
            test_df = df.iloc[test_start:test_start + 28]

            wins = sum(
                simulate_ticket(ticket, keno_type, row["numbers_set"])[0]
                for _, row in test_df.iterrows()
            )

            roi = (wins - 28) / 28 * 100

            aging_curve.append({
                "block": block,
                "days_since_creation": (block + 1) * 28,
                "period": f"{test_df['Datum'].min().date()} - {test_df['Datum'].max().date()}",
                "roi": roi,
            })

            test_start += 28
            block += 1

        results["aging_curves"][f"start_{start_date.date()}"] = {
            "ticket": ticket,
            "train_period": f"{train_df['Datum'].min().date()} - {train_df['Datum'].max().date()}",
            "blocks": aging_curve,
        }

    return results


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("TICKET-LEBENSZYKLUS: Walk-Forward Simulation")
    print("=" * 70)

    base_path = Path(__file__).parent.parent

    # Daten laden
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(
        lambda row: set(row.dropna().astype(int)), axis=1
    )
    df = df.sort_values("Datum").reset_index(drop=True)

    print(f"\nDaten: {len(df)} Ziehungen")
    print(f"Zeitraum: {df['Datum'].min().date()} - {df['Datum'].max().date()}")
    print(f"Jahre: {sorted(df['Datum'].dt.year.unique())}")

    # ==========================================================================
    # 1. WALK-FORWARD SIMULATION
    # ==========================================================================
    print("\n" + "=" * 70)
    print("1. WALK-FORWARD SIMULATION (Typ 9)")
    print("=" * 70)

    wf_results = walk_forward_simulation(df, keno_type=9, train_days=365, test_days=90, step_days=90)

    print(f"\nIterationen: {len(wf_results['iterations'])}")
    print(f"\n{'Iteration':<12} {'Test-Periode':<25} {'Frequency':>12} {'Freq-High':>12} {'V2-Style':>12}")
    print("-" * 80)

    for it in wf_results["iterations"]:
        freq_roi = it["strategies"]["frequency"]["roi"]
        high_roi = it["strategies"]["frequency_high"]["roi"]
        v2_roi = it["strategies"]["v2_style"]["roi"]

        print(f"{it['iteration']:<12} {it['test_period']:<25} {freq_roi:>+11.1f}% {high_roi:>+11.1f}% {v2_roi:>+11.1f}%")

    # Durchschnitte
    avg_freq = np.mean([it["strategies"]["frequency"]["roi"] for it in wf_results["iterations"]])
    avg_high = np.mean([it["strategies"]["frequency_high"]["roi"] for it in wf_results["iterations"]])
    avg_v2 = np.mean([it["strategies"]["v2_style"]["roi"] for it in wf_results["iterations"]])

    print("-" * 80)
    print(f"{'DURCHSCHNITT':<12} {'':<25} {avg_freq:>+11.1f}% {avg_high:>+11.1f}% {avg_v2:>+11.1f}%")

    # ==========================================================================
    # 2. JAHRES-BASIERTE ANALYSE
    # ==========================================================================
    print("\n" + "=" * 70)
    print("2. JAHRES-BASIERTE ANALYSE (Typ 9)")
    print("=" * 70)
    print("\nTickets erstellt auf Jahr X, getestet auf Jahr Y")

    yearly_results = yearly_ticket_analysis(df, keno_type=9)

    print(f"\n{'Train':<8} {'Test':<8} {'Jahre':<8} {'Frequency':>12} {'Freq-High':>12} {'V2-Style':>12}")
    print("-" * 70)

    # Gruppiere nach Train-Jahr
    for train_year in sorted(yearly_results["tickets_by_year"].keys()):
        for test_year in sorted(df["Datum"].dt.year.unique()):
            if test_year <= train_year:
                continue

            freq_key = f"train_{train_year}_test_{test_year}_frequency"
            high_key = f"train_{train_year}_test_{test_year}_frequency_high"
            v2_key = f"train_{train_year}_test_{test_year}_v2_style"

            if freq_key in yearly_results["performance_matrix"]:
                freq_roi = yearly_results["performance_matrix"][freq_key]["roi"]
                high_roi = yearly_results["performance_matrix"][high_key]["roi"]
                v2_roi = yearly_results["performance_matrix"][v2_key]["roi"]
                years_apart = test_year - train_year

                print(f"{train_year:<8} {test_year:<8} {years_apart:<8} {freq_roi:>+11.1f}% {high_roi:>+11.1f}% {v2_roi:>+11.1f}%")

    # Zeige Tickets
    print("\n\nGenerierte Tickets pro Jahr:")
    for year, tickets in yearly_results["tickets_by_year"].items():
        print(f"\n  {year}:")
        for strat, ticket in tickets.items():
            print(f"    {strat}: {ticket}")

    # ==========================================================================
    # 3. TICKET-ALTERUNG
    # ==========================================================================
    print("\n" + "=" * 70)
    print("3. TICKET-ALTERUNG (Typ 9)")
    print("=" * 70)
    print("\nWie altert ein Ticket ueber Zeit?")

    aging_results = ticket_aging_analysis(df, keno_type=9)

    for start_key, aging_data in aging_results["aging_curves"].items():
        print(f"\n  Ticket erstellt: {aging_data['train_period']}")
        print(f"  Ticket: {aging_data['ticket']}")
        print(f"\n  {'Block':<8} {'Tage':>8} {'ROI':>12}")
        print("  " + "-" * 30)

        for block in aging_data["blocks"][:12]:  # Erste 12 Bloecke (336 Tage)
            print(f"  {block['block']:<8} {block['days_since_creation']:>8} {block['roi']:>+11.1f}%")

        if len(aging_data["blocks"]) > 12:
            print(f"  ... ({len(aging_data['blocks']) - 12} weitere Bloecke)")

        # Trend berechnen
        if len(aging_data["blocks"]) > 2:
            rois = [b["roi"] for b in aging_data["blocks"]]
            trend = np.polyfit(range(len(rois)), rois, 1)[0]
            print(f"\n  TREND: {trend:+.2f}% pro 28-Tage-Block")
            print(f"  -> {'ALTERUNG' if trend < -1 else 'STABIL' if abs(trend) < 1 else 'VERBESSERUNG'}")

    # ==========================================================================
    # 4. ZUSAMMENFASSUNG
    # ==========================================================================
    print("\n" + "=" * 70)
    print("4. ZUSAMMENFASSUNG")
    print("=" * 70)

    print("""
ERKENNTNISSE:

1. WALK-FORWARD PERFORMANCE:
   - Zeigt wie verschiedene Strategien ueber Zeit performen
   - V2-Style vs Frequency vs Frequency-High

2. JAHRES-TRANSFER:
   - Wie gut transferiert ein Ticket von Jahr X auf Jahr Y?
   - Je weiter die Jahre auseinander, desto mehr "Alterung"?

3. TICKET-ALTERUNG:
   - ROI-Trend ueber Zeit
   - Negative Trends = Ticket verliert Gueltigkeit
   - Positive Trends = Ticket wird besser (unwahrscheinlich)

4. EMPFEHLUNG:
   - Tickets regelmaessig neu generieren (alle 90-180 Tage)
   - 28-Tage-Dauerschein-Limit beachten
   - Walk-Forward-Performance als Entscheidungsgrundlage
""")

    # Speichern
    all_results = {
        "walk_forward": wf_results,
        "yearly": yearly_results,
        "aging": aging_results,
    }

    def json_serializer(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return str(obj)

    output_path = base_path / "results" / "ticket_lifecycle_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=json_serializer)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
