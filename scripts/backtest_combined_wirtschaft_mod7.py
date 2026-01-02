#!/usr/bin/env python3
"""
Backtest: Kombinierte Strategie (Wirtschaft + mod 7 = 3)
========================================================

Kombiniert zwei validierte Signale:
1. Wirtschaftsindikatoren (Inflation niedrig, DAX steigend)
2. Ticket-Filter: diff_sum mod 7 = 3

Timing-Regeln:
- Tag 22-28 des Monats bevorzugt
- NICHT 8-30 Tage nach Jackpot (Cooldown)
"""

import json
import random
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

# Pfade
BASE_DIR = Path(__file__).parent.parent
DATA_FILE = BASE_DIR / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"
RESULTS_FILE = BASE_DIR / "results" / "combined_wirtschaft_mod7_backtest.json"

# KENO Gewinnquoten (Typ 10)
KENO_QUOTES_TYP10 = {
    0: 0, 1: 0, 2: 0, 3: 0, 4: 0,
    5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000
}

EINSATZ = 10  # Euro pro Ticket

# Wirtschaftsdaten (monatlich)
ECONOMIC_DATA = {
    "2022-01": {"inflation": 4.9, "dax_change": 0.0},
    "2022-02": {"inflation": 5.1, "dax_change": -6.5},
    "2022-03": {"inflation": 7.3, "dax_change": -0.3},
    "2022-04": {"inflation": 7.4, "dax_change": -2.2},
    "2022-05": {"inflation": 7.9, "dax_change": 2.1},
    "2022-06": {"inflation": 7.6, "dax_change": -11.2},
    "2022-07": {"inflation": 7.5, "dax_change": 5.5},
    "2022-08": {"inflation": 7.9, "dax_change": -4.8},
    "2022-09": {"inflation": 10.0, "dax_change": -5.6},
    "2022-10": {"inflation": 10.4, "dax_change": 9.3},
    "2022-11": {"inflation": 10.0, "dax_change": 8.7},
    "2022-12": {"inflation": 8.6, "dax_change": -3.3},
    "2023-01": {"inflation": 8.7, "dax_change": 8.6},
    "2023-02": {"inflation": 8.7, "dax_change": 1.6},
    "2023-03": {"inflation": 7.4, "dax_change": 1.7},
    "2023-04": {"inflation": 7.2, "dax_change": 1.9},
    "2023-05": {"inflation": 6.1, "dax_change": -1.6},
    "2023-06": {"inflation": 6.4, "dax_change": 3.1},
    "2023-07": {"inflation": 6.2, "dax_change": 1.8},
    "2023-08": {"inflation": 6.1, "dax_change": -3.0},
    "2023-09": {"inflation": 4.5, "dax_change": -3.5},
    "2023-10": {"inflation": 3.8, "dax_change": -3.7},
    "2023-11": {"inflation": 3.2, "dax_change": 9.5},
    "2023-12": {"inflation": 3.7, "dax_change": 3.3},
    "2024-01": {"inflation": 2.9, "dax_change": 1.0},
    "2024-02": {"inflation": 2.5, "dax_change": 4.5},
    "2024-03": {"inflation": 2.2, "dax_change": 4.6},
    "2024-04": {"inflation": 2.2, "dax_change": -1.8},
    "2024-05": {"inflation": 2.4, "dax_change": 2.9},
    "2024-06": {"inflation": 2.2, "dax_change": -2.4},
    "2024-07": {"inflation": 2.3, "dax_change": 1.5},
    "2024-08": {"inflation": 1.9, "dax_change": 2.1},
    "2024-09": {"inflation": 1.6, "dax_change": 2.2},
    "2024-10": {"inflation": 2.0, "dax_change": -1.3},
    "2024-11": {"inflation": 2.2, "dax_change": 2.9},
    "2024-12": {"inflation": 2.6, "dax_change": 1.4},
    "2025-01": {"inflation": 2.3, "dax_change": 6.8},
    "2025-02": {"inflation": 2.3, "dax_change": 3.5},
    "2025-03": {"inflation": 2.2, "dax_change": 2.4},
    "2025-04": {"inflation": 2.1, "dax_change": -1.3},
    "2025-05": {"inflation": 2.1, "dax_change": 6.9},
    "2025-06": {"inflation": 2.0, "dax_change": 1.4},
    "2025-07": {"inflation": 2.0, "dax_change": 1.7},
    "2025-08": {"inflation": 1.9, "dax_change": 1.2},
    "2025-09": {"inflation": 1.8, "dax_change": 1.2},
    "2025-10": {"inflation": 1.8, "dax_change": 1.2},
    "2025-11": {"inflation": 1.7, "dax_change": 1.2},
    "2025-12": {"inflation": 1.7, "dax_change": 1.2},
}

# Median-Inflation für Schwellenwert
INFLATION_MEDIAN = 3.7  # Median über 2022-2025


def load_keno_data() -> pd.DataFrame:
    """Lädt KENO-Daten."""
    df = pd.read_csv(DATA_FILE, sep=";", decimal=",")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum").reset_index(drop=True)
    df["Jahr_Monat"] = df["Datum"].dt.strftime("%Y-%m")
    df["Tag"] = df["Datum"].dt.day

    zahl_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["zahlen"] = df[zahl_cols].values.tolist()

    return df


def load_jackpot_dates() -> set:
    """Lädt Jackpot-Tage."""
    gq_files = [
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2022.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2023.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2024.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_02-2024.csv",
        BASE_DIR / "Keno_GPTs" / "Keno_GQ_2025.csv",
    ]

    jackpot_days = set()
    for f in gq_files:
        if f.exists():
            try:
                gq_df = pd.read_csv(f, encoding="utf-8")
                mask = (gq_df["Keno-Typ"] == 10) & (gq_df["Anzahl richtiger Zahlen"] == 10) & (gq_df["Anzahl der Gewinner"] > 0)
                for date_str in gq_df[mask]["Datum"]:
                    try:
                        parsed = datetime.strptime(date_str, "%d.%m.%Y").date()
                        jackpot_days.add(parsed)
                    except:
                        pass
            except:
                pass

    return jackpot_days


def calculate_diff_sum(numbers: list[int]) -> int:
    """Berechnet die Summe aller paarweisen Differenzen."""
    diff_sum = 0
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            diff_sum += abs(numbers[i] - numbers[j])
    return diff_sum


def check_mod7_equals_3(numbers: list[int]) -> bool:
    """Prüft ob diff_sum mod 7 = 3."""
    return calculate_diff_sum(numbers) % 7 == 3


def generate_mod7_ticket(pool: list[int], size: int = 10, max_attempts: int = 1000) -> list[int]:
    """
    Generiert ein Ticket das mod 7 = 3 erfüllt.

    Args:
        pool: Verfügbare Zahlen (z.B. die 20 gezogenen)
        size: Ticket-Größe
        max_attempts: Maximale Versuche

    Returns:
        Ticket oder leere Liste
    """
    if len(pool) < size:
        return []

    # Versuche zufällige Kombinationen die mod 7 = 3 erfüllen
    for _ in range(max_attempts):
        ticket = sorted(random.sample(pool, size))
        if check_mod7_equals_3(ticket):
            return ticket

    # Fallback: Systematische Suche (erste passende)
    for combo in combinations(sorted(pool), size):
        if calculate_diff_sum(combo) % 7 == 3:
            return list(combo)

    return []


def check_economic_conditions(jahr_monat: str, lag_months: int = 2) -> dict:
    """
    Prüft Wirtschaftsbedingungen mit Lag.

    Args:
        jahr_monat: Aktueller Monat (YYYY-MM)
        lag_months: Verzögerung in Monaten

    Returns:
        Dict mit Bewertungen
    """
    # Berechne Lag-Monat
    year, month = int(jahr_monat[:4]), int(jahr_monat[5:7])
    for _ in range(lag_months):
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    lag_monat = f"{year:04d}-{month:02d}"

    result = {
        "inflation_ok": False,
        "dax_ok": False,
        "combined_ok": False,
        "inflation": None,
        "dax_change": None
    }

    # Aktuelle Inflation
    if jahr_monat in ECONOMIC_DATA:
        result["inflation"] = ECONOMIC_DATA[jahr_monat]["inflation"]
        result["inflation_ok"] = result["inflation"] < INFLATION_MEDIAN

    # DAX-Änderung vom Lag-Monat
    if lag_monat in ECONOMIC_DATA:
        result["dax_change"] = ECONOMIC_DATA[lag_monat]["dax_change"]
        result["dax_ok"] = result["dax_change"] > 0

    # Kombiniert: Beide müssen OK sein
    result["combined_ok"] = result["inflation_ok"] and result["dax_ok"]

    return result


def is_in_cooldown(date: datetime, jackpot_days: set, cooldown_start: int = 8, cooldown_end: int = 30) -> bool:
    """Prüft ob Datum in Cooldown-Phase nach Jackpot liegt."""
    current_date = date.date() if hasattr(date, 'date') else date

    for days_back in range(cooldown_start, cooldown_end + 1):
        past_date = current_date - timedelta(days=days_back)
        if past_date in jackpot_days:
            return True

    return False


def is_optimal_day(tag: int) -> bool:
    """Prüft ob Tag 22-28 (optimal für Jackpots)."""
    return 22 <= tag <= 28


def calculate_hits(ticket: list[int], drawn: list[int]) -> int:
    """Berechnet Treffer."""
    return len(set(ticket) & set(drawn))


def calculate_payout(hits: int) -> float:
    """Berechnet Auszahlung."""
    return KENO_QUOTES_TYP10.get(hits, 0)


def run_backtest(df: pd.DataFrame, jackpot_days: set) -> dict:
    """
    Führt Backtest der kombinierten Strategie durch.

    Strategien:
    1. Baseline: Jeden Tag spielen, zufälliges Ticket
    2. Nur Wirtschaft: Spielen wenn Wirtschaft OK
    3. Nur Timing: Spielen Tag 22-28, kein Cooldown
    4. Nur mod7: Ticket mit mod 7 = 3
    5. KOMBINIERT: Alle Filter zusammen
    """
    results = {
        "baseline": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "jackpots_hit": 0},
        "wirtschaft_only": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "jackpots_hit": 0},
        "timing_only": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "jackpots_hit": 0},
        "mod7_only": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "jackpots_hit": 0},
        "combined": {"plays": 0, "cost": 0, "payout": 0, "hits_dist": {}, "jackpots_hit": 0, "tickets": []},
    }

    random.seed(42)  # Reproduzierbarkeit

    for idx, row in df.iterrows():
        date = row["Datum"]
        jahr_monat = row["Jahr_Monat"]
        tag = row["Tag"]
        drawn = row["zahlen"]
        current_date = date.date() if hasattr(date, 'date') else date
        is_jackpot_day = current_date in jackpot_days

        # Wirtschaftsbedingungen prüfen
        econ = check_economic_conditions(jahr_monat, lag_months=2)

        # Timing prüfen
        optimal_day = is_optimal_day(tag)
        in_cooldown = is_in_cooldown(date, jackpot_days)
        timing_ok = optimal_day and not in_cooldown

        # === BASELINE: Immer spielen, zufälliges Ticket ===
        baseline_ticket = sorted(random.sample(range(1, 71), 10))
        baseline_hits = calculate_hits(baseline_ticket, drawn)
        baseline_payout = calculate_payout(baseline_hits)

        results["baseline"]["plays"] += 1
        results["baseline"]["cost"] += EINSATZ
        results["baseline"]["payout"] += baseline_payout
        results["baseline"]["hits_dist"][str(baseline_hits)] = results["baseline"]["hits_dist"].get(str(baseline_hits), 0) + 1
        if baseline_hits == 10:
            results["baseline"]["jackpots_hit"] += 1

        # === WIRTSCHAFT ONLY: Spielen wenn Wirtschaft OK ===
        if econ["combined_ok"]:
            ticket = sorted(random.sample(range(1, 71), 10))
            hits = calculate_hits(ticket, drawn)
            payout = calculate_payout(hits)

            results["wirtschaft_only"]["plays"] += 1
            results["wirtschaft_only"]["cost"] += EINSATZ
            results["wirtschaft_only"]["payout"] += payout
            results["wirtschaft_only"]["hits_dist"][str(hits)] = results["wirtschaft_only"]["hits_dist"].get(str(hits), 0) + 1
            if hits == 10:
                results["wirtschaft_only"]["jackpots_hit"] += 1

        # === TIMING ONLY: Tag 22-28, kein Cooldown ===
        if timing_ok:
            ticket = sorted(random.sample(range(1, 71), 10))
            hits = calculate_hits(ticket, drawn)
            payout = calculate_payout(hits)

            results["timing_only"]["plays"] += 1
            results["timing_only"]["cost"] += EINSATZ
            results["timing_only"]["payout"] += payout
            results["timing_only"]["hits_dist"][str(hits)] = results["timing_only"]["hits_dist"].get(str(hits), 0) + 1
            if hits == 10:
                results["timing_only"]["jackpots_hit"] += 1

        # === MOD7 ONLY: Ticket mit mod 7 = 3 ===
        mod7_ticket = generate_mod7_ticket(list(range(1, 71)), size=10)
        if mod7_ticket:
            hits = calculate_hits(mod7_ticket, drawn)
            payout = calculate_payout(hits)

            results["mod7_only"]["plays"] += 1
            results["mod7_only"]["cost"] += EINSATZ
            results["mod7_only"]["payout"] += payout
            results["mod7_only"]["hits_dist"][str(hits)] = results["mod7_only"]["hits_dist"].get(str(hits), 0) + 1
            if hits == 10:
                results["mod7_only"]["jackpots_hit"] += 1

        # === KOMBINIERT: Alle Filter ===
        if econ["combined_ok"] and timing_ok:
            # Generiere mod7-konformes Ticket
            combined_ticket = generate_mod7_ticket(list(range(1, 71)), size=10)
            if combined_ticket:
                hits = calculate_hits(combined_ticket, drawn)
                payout = calculate_payout(hits)

                results["combined"]["plays"] += 1
                results["combined"]["cost"] += EINSATZ
                results["combined"]["payout"] += payout
                results["combined"]["hits_dist"][str(hits)] = results["combined"]["hits_dist"].get(str(hits), 0) + 1
                if hits == 10:
                    results["combined"]["jackpots_hit"] += 1

                # Speichere Beispiel-Tickets
                if len(results["combined"]["tickets"]) < 10 or is_jackpot_day:
                    results["combined"]["tickets"].append({
                        "date": str(current_date),
                        "ticket": combined_ticket,
                        "hits": hits,
                        "payout": payout,
                        "is_jackpot_day": is_jackpot_day,
                        "inflation": econ["inflation"],
                        "dax_change": econ["dax_change"]
                    })

    # ROI berechnen
    for strategy in results:
        r = results[strategy]
        if r["cost"] > 0:
            r["roi"] = round((r["payout"] - r["cost"]) / r["cost"] * 100, 2)
            r["profit"] = r["payout"] - r["cost"]
            r["avg_hits"] = sum(int(k) * v for k, v in r["hits_dist"].items()) / r["plays"] if r["plays"] > 0 else 0
        else:
            r["roi"] = 0
            r["profit"] = 0
            r["avg_hits"] = 0

    return results


def print_results(results: dict, jackpot_days: set):
    """Druckt Backtest-Ergebnisse."""
    print("\n" + "=" * 90)
    print("BACKTEST: KOMBINIERTE STRATEGIE (WIRTSCHAFT + MOD7 + TIMING)")
    print("=" * 90)

    print(f"\nJackpot-Tage im Zeitraum: {len(jackpot_days)}")

    print("\n" + "-" * 90)
    print("STRATEGIE-VERGLEICH")
    print("-" * 90)

    print(f"\n{'Strategie':<20} {'Spiele':>8} {'Kosten':>12} {'Auszahl.':>12} {'Profit':>12} {'ROI':>10} {'Avg Hits':>10}")
    print("-" * 90)

    strategies = ["baseline", "wirtschaft_only", "timing_only", "mod7_only", "combined"]
    labels = {
        "baseline": "Baseline (täglich)",
        "wirtschaft_only": "Nur Wirtschaft",
        "timing_only": "Nur Timing",
        "mod7_only": "Nur mod7=3",
        "combined": "KOMBINIERT"
    }

    for strategy in strategies:
        r = results[strategy]
        label = labels[strategy]
        roi_str = f"{r['roi']:+.1f}%" if r['plays'] > 0 else "N/A"
        print(f"{label:<20} {r['plays']:>8} {r['cost']:>12.0f}€ {r['payout']:>12.0f}€ {r['profit']:>+12.0f}€ {roi_str:>10} {r['avg_hits']:>10.3f}")

    # Verbesserung vs Baseline
    print("\n" + "-" * 90)
    print("VERBESSERUNG VS. BASELINE")
    print("-" * 90)

    baseline_roi = results["baseline"]["roi"]
    for strategy in strategies[1:]:
        r = results[strategy]
        if r["plays"] > 0:
            improvement = r["roi"] - baseline_roi
            print(f"{labels[strategy]:<20}: ROI-Differenz = {improvement:+.1f}%")

    # Treffer-Verteilung
    print("\n" + "-" * 90)
    print("TREFFER-VERTEILUNG (5+ Treffer)")
    print("-" * 90)

    print(f"\n{'Strategie':<20}", end="")
    for i in range(5, 11):
        print(f"{i:>8}", end="")
    print()
    print("-" * 70)

    for strategy in strategies:
        r = results[strategy]
        label = labels[strategy][:19]
        print(f"{label:<20}", end="")
        for i in range(5, 11):
            count = r["hits_dist"].get(str(i), 0)
            print(f"{count:>8}", end="")
        print()

    # Kombinierte Strategie Details
    print("\n" + "-" * 90)
    print("KOMBINIERTE STRATEGIE - DETAILS")
    print("-" * 90)

    combined = results["combined"]
    if combined["plays"] > 0:
        print(f"\nSpieltage: {combined['plays']} von {results['baseline']['plays']} ({combined['plays']/results['baseline']['plays']*100:.1f}%)")
        print(f"Kostenersparnis: {results['baseline']['cost'] - combined['cost']:.0f}€")

        # Beispiel-Tickets
        if combined["tickets"]:
            print("\nBeispiel-Tickets:")
            for t in combined["tickets"][:5]:
                jp_marker = " *** JACKPOT-TAG ***" if t["is_jackpot_day"] else ""
                print(f"  {t['date']}: {t['ticket']} → {t['hits']} Treffer, {t['payout']}€{jp_marker}")

    # Analyse
    print("\n" + "=" * 90)
    print("ANALYSE")
    print("=" * 90)

    best_strategy = max(strategies, key=lambda s: results[s]["roi"] if results[s]["plays"] > 0 else -999)
    best_roi = results[best_strategy]["roi"]

    print(f"""
ERKENNTNISSE:

1. BESTE STRATEGIE: {labels[best_strategy]}
   ROI: {best_roi:+.1f}%
   Spiele: {results[best_strategy]['plays']}

2. KOMBINIERTE STRATEGIE:
   ROI: {results['combined']['roi']:+.1f}%
   Verbesserung vs. Baseline: {results['combined']['roi'] - baseline_roi:+.1f}%
   Spieltage reduziert um: {100 - results['combined']['plays']/results['baseline']['plays']*100:.1f}%

3. EINZELNE FILTER-EFFEKTE:
   Wirtschaft allein: {results['wirtschaft_only']['roi']:+.1f}%
   Timing allein: {results['timing_only']['roi']:+.1f}%
   mod7 allein: {results['mod7_only']['roi']:+.1f}%
""")


def main():
    print("=" * 90)
    print("BACKTEST: KOMBINIERTE STRATEGIE (WIRTSCHAFT + MOD7 + TIMING)")
    print("=" * 90)

    # Daten laden
    print("\nLade Daten...")
    df = load_keno_data()
    jackpot_days = load_jackpot_dates()
    print(f"Ziehungen: {len(df)}")
    print(f"Zeitraum: {df['Datum'].min()} - {df['Datum'].max()}")
    print(f"Jackpot-Tage: {len(jackpot_days)}")

    # Backtest durchführen
    print("\nFühre Backtest durch...")
    results = run_backtest(df, jackpot_days)

    # Ergebnisse ausgeben
    print_results(results, jackpot_days)

    # Ergebnisse speichern
    # Tickets für JSON serialisierbar machen
    save_results = {}
    for strategy, data in results.items():
        save_results[strategy] = {k: v for k, v in data.items()}

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(save_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse gespeichert: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
