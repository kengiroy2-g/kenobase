#!/usr/bin/env python3
"""
Backtest: Strategie-Kompatibilität (Typ 6, 8, 10)
=================================================

Testet welche Strategien sich gegenseitig verbessern oder verschlechtern.
Analysiert Synergien und Antagonismen zwischen:
- Wirtschaft (Inflation, DAX)
- Timing (Tag 22-28, kein Cooldown)
- mod7=3 Filter

Ticket-Typen: 6, 8, 10
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
RESULTS_FILE = BASE_DIR / "results" / "strategy_compatibility_analysis.json"

# KENO Gewinnquoten nach Typ
KENO_QUOTES = {
    6: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 15, 6: 500},
    8: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 2, 6: 15, 7: 100, 8: 10000},
    10: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 5, 7: 15, 8: 100, 9: 1000, 10: 100000}
}

# Einsatz
EINSATZ = {6: 6, 8: 8, 10: 10}

# Wirtschaftsdaten
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

INFLATION_MEDIAN = 3.7


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
    """Berechnet Summe aller paarweisen Differenzen."""
    diff_sum = 0
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            diff_sum += abs(numbers[i] - numbers[j])
    return diff_sum


def generate_mod7_ticket(pool: list[int], size: int, max_attempts: int = 500) -> list[int]:
    """Generiert Ticket mit mod 7 = 3."""
    if len(pool) < size:
        return []

    for _ in range(max_attempts):
        ticket = sorted(random.sample(pool, size))
        if calculate_diff_sum(ticket) % 7 == 3:
            return ticket

    return sorted(random.sample(pool, size))  # Fallback


def check_economic_conditions(jahr_monat: str) -> dict:
    """Prüft Wirtschaftsbedingungen mit Lag."""
    year, month = int(jahr_monat[:4]), int(jahr_monat[5:7])

    # 2 Monate Lag
    for _ in range(2):
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    lag_monat = f"{year:04d}-{month:02d}"

    result = {"inflation_ok": False, "dax_ok": False}

    if jahr_monat in ECONOMIC_DATA:
        result["inflation_ok"] = ECONOMIC_DATA[jahr_monat]["inflation"] < INFLATION_MEDIAN

    if lag_monat in ECONOMIC_DATA:
        result["dax_ok"] = ECONOMIC_DATA[lag_monat]["dax_change"] > 0

    return result


def is_in_cooldown(date: datetime, jackpot_days: set) -> bool:
    """Prüft Cooldown-Phase (8-30 Tage nach Jackpot)."""
    current_date = date.date() if hasattr(date, 'date') else date
    for days_back in range(8, 31):
        if (current_date - timedelta(days=days_back)) in jackpot_days:
            return True
    return False


def is_optimal_day(tag: int) -> bool:
    """Prüft ob Tag 22-28."""
    return 22 <= tag <= 28


def calculate_hits(ticket: list[int], drawn: list[int]) -> int:
    """Berechnet Treffer."""
    return len(set(ticket) & set(drawn))


def calculate_payout(hits: int, typ: int) -> float:
    """Berechnet Auszahlung."""
    return KENO_QUOTES[typ].get(hits, 0)


def run_strategy_test(
    df: pd.DataFrame,
    jackpot_days: set,
    typ: int,
    use_wirtschaft: bool,
    use_timing: bool,
    use_mod7: bool
) -> dict:
    """
    Testet eine spezifische Strategie-Kombination.
    """
    result = {
        "plays": 0,
        "cost": 0,
        "payout": 0,
        "hits_dist": {},
        "high_wins": 0  # 5+ bei Typ 6, 6+ bei Typ 8, 7+ bei Typ 10
    }

    high_win_threshold = {6: 5, 8: 6, 10: 7}[typ]

    random.seed(42)

    for idx, row in df.iterrows():
        date = row["Datum"]
        jahr_monat = row["Jahr_Monat"]
        tag = row["Tag"]
        drawn = row["zahlen"]

        # Filter anwenden
        play = True

        if use_wirtschaft:
            econ = check_economic_conditions(jahr_monat)
            if not (econ["inflation_ok"] and econ["dax_ok"]):
                play = False

        if use_timing and play:
            if not is_optimal_day(tag) or is_in_cooldown(date, jackpot_days):
                play = False

        if not play:
            continue

        # Ticket generieren
        if use_mod7:
            ticket = generate_mod7_ticket(list(range(1, 71)), typ)
        else:
            ticket = sorted(random.sample(range(1, 71), typ))

        hits = calculate_hits(ticket, drawn)
        payout = calculate_payout(hits, typ)

        result["plays"] += 1
        result["cost"] += EINSATZ[typ]
        result["payout"] += payout
        result["hits_dist"][str(hits)] = result["hits_dist"].get(str(hits), 0) + 1

        if hits >= high_win_threshold:
            result["high_wins"] += 1

    # ROI berechnen
    if result["cost"] > 0:
        result["roi"] = round((result["payout"] - result["cost"]) / result["cost"] * 100, 2)
        result["profit"] = result["payout"] - result["cost"]
    else:
        result["roi"] = 0
        result["profit"] = 0

    return result


def analyze_compatibility(results: dict) -> dict:
    """
    Analysiert Kompatibilität zwischen Strategien.
    Berechnet Synergie-Scores.
    """
    compatibility = {}

    for typ in [6, 8, 10]:
        compatibility[f"typ_{typ}"] = {}

        # Baseline ROI
        baseline_roi = results[f"typ_{typ}"]["baseline"]["roi"]

        # Einzelne Filter-Effekte
        w_effect = results[f"typ_{typ}"]["W"]["roi"] - baseline_roi
        t_effect = results[f"typ_{typ}"]["T"]["roi"] - baseline_roi
        m_effect = results[f"typ_{typ}"]["M"]["roi"] - baseline_roi

        # Kombinierte Effekte
        wt_effect = results[f"typ_{typ}"]["W+T"]["roi"] - baseline_roi
        wm_effect = results[f"typ_{typ}"]["W+M"]["roi"] - baseline_roi
        tm_effect = results[f"typ_{typ}"]["T+M"]["roi"] - baseline_roi
        wtm_effect = results[f"typ_{typ}"]["W+T+M"]["roi"] - baseline_roi

        # Synergie = Kombiniert - (Summe Einzeleffekte)
        # Positiv = Synergistisch, Negativ = Antagonistisch
        compatibility[f"typ_{typ}"]["einzeleffekte"] = {
            "wirtschaft": round(w_effect, 2),
            "timing": round(t_effect, 2),
            "mod7": round(m_effect, 2)
        }

        compatibility[f"typ_{typ}"]["kombinationen"] = {
            "W+T": {
                "effekt": round(wt_effect, 2),
                "erwartet": round(w_effect + t_effect, 2),
                "synergie": round(wt_effect - (w_effect + t_effect), 2)
            },
            "W+M": {
                "effekt": round(wm_effect, 2),
                "erwartet": round(w_effect + m_effect, 2),
                "synergie": round(wm_effect - (w_effect + m_effect), 2)
            },
            "T+M": {
                "effekt": round(tm_effect, 2),
                "erwartet": round(t_effect + m_effect, 2),
                "synergie": round(tm_effect - (t_effect + m_effect), 2)
            },
            "W+T+M": {
                "effekt": round(wtm_effect, 2),
                "erwartet": round(w_effect + t_effect + m_effect, 2),
                "synergie": round(wtm_effect - (w_effect + t_effect + m_effect), 2)
            }
        }

    return compatibility


def print_results(results: dict, compatibility: dict):
    """Druckt Ergebnisse."""
    print("\n" + "=" * 100)
    print("STRATEGIE-KOMPATIBILITÄT: TYP 6, 8, 10")
    print("=" * 100)

    # Legende
    print("\nLegende: W=Wirtschaft, T=Timing, M=mod7")

    for typ in [6, 8, 10]:
        print(f"\n{'='*100}")
        print(f"TYP {typ} (Einsatz: {EINSATZ[typ]}€)")
        print("=" * 100)

        typ_results = results[f"typ_{typ}"]

        print(f"\n{'Strategie':<15} {'Spiele':>8} {'Kosten':>10} {'Auszahl.':>10} {'Profit':>10} {'ROI':>10} {'High-Wins':>10}")
        print("-" * 85)

        strategies = ["baseline", "W", "T", "M", "W+T", "W+M", "T+M", "W+T+M"]
        labels = {
            "baseline": "Baseline",
            "W": "Wirtschaft",
            "T": "Timing",
            "M": "mod7",
            "W+T": "W+T",
            "W+M": "W+M",
            "T+M": "T+M",
            "W+T+M": "ALLE"
        }

        for s in strategies:
            r = typ_results[s]
            print(f"{labels[s]:<15} {r['plays']:>8} {r['cost']:>10.0f}€ {r['payout']:>10.0f}€ {r['profit']:>+10.0f}€ {r['roi']:>+9.1f}% {r['high_wins']:>10}")

        # Kompatibilitäts-Analyse
        comp = compatibility[f"typ_{typ}"]

        print(f"\n--- SYNERGIE-ANALYSE ---")
        print(f"\nEinzeleffekte (vs Baseline):")
        for name, effect in comp["einzeleffekte"].items():
            print(f"  {name}: {effect:+.2f}%")

        print(f"\nKombinations-Synergien:")
        print(f"{'Kombination':<12} {'Effekt':>10} {'Erwartet':>10} {'Synergie':>10} {'Bewertung':<15}")
        print("-" * 60)

        for combo, data in comp["kombinationen"].items():
            if data["synergie"] > 0.5:
                bewertung = "SYNERGISTISCH"
            elif data["synergie"] < -0.5:
                bewertung = "ANTAGONISTISCH"
            else:
                bewertung = "NEUTRAL"

            print(f"{combo:<12} {data['effekt']:>+9.2f}% {data['erwartet']:>+9.2f}% {data['synergie']:>+9.2f}% {bewertung:<15}")

    # Beste Kombination pro Typ
    print("\n" + "=" * 100)
    print("BESTE STRATEGIEN PRO TYP")
    print("=" * 100)

    for typ in [6, 8, 10]:
        typ_results = results[f"typ_{typ}"]
        best = max(typ_results.items(), key=lambda x: x[1]["roi"])
        print(f"\nTyp {typ}: {best[0]} mit ROI {best[1]['roi']:+.1f}%")

        # Vergleich zu Baseline
        baseline_roi = typ_results["baseline"]["roi"]
        improvement = best[1]["roi"] - baseline_roi
        print(f"         Verbesserung vs Baseline: {improvement:+.1f}%")

    # Gesamtempfehlung
    print("\n" + "=" * 100)
    print("GESAMTEMPFEHLUNG")
    print("=" * 100)

    # Finde beste Typ/Strategie-Kombination
    all_results = []
    for typ in [6, 8, 10]:
        for strat, data in results[f"typ_{typ}"].items():
            all_results.append({
                "typ": typ,
                "strategie": strat,
                "roi": data["roi"],
                "plays": data["plays"],
                "profit": data["profit"]
            })

    all_results.sort(key=lambda x: x["roi"], reverse=True)

    print("\nTop 5 Typ/Strategie-Kombinationen:")
    for i, r in enumerate(all_results[:5], 1):
        print(f"  {i}. Typ {r['typ']} + {r['strategie']}: ROI {r['roi']:+.1f}% ({r['plays']} Spiele)")

    print("\nSchlechteste Kombinationen (VERMEIDEN):")
    for i, r in enumerate(all_results[-3:], 1):
        print(f"  {i}. Typ {r['typ']} + {r['strategie']}: ROI {r['roi']:+.1f}%")


def main():
    print("=" * 100)
    print("BACKTEST: STRATEGIE-KOMPATIBILITÄT (TYP 6, 8, 10)")
    print("=" * 100)

    # Daten laden
    print("\nLade Daten...")
    df = load_keno_data()
    jackpot_days = load_jackpot_dates()
    print(f"Ziehungen: {len(df)}")
    print(f"Jackpot-Tage: {len(jackpot_days)}")

    # Alle Kombinationen testen
    print("\nTeste alle Strategie-Kombinationen...")

    results = {}

    for typ in [6, 8, 10]:
        print(f"\n  Typ {typ}...")
        results[f"typ_{typ}"] = {}

        # Alle Kombinationen
        test_configs = [
            ("baseline", False, False, False),
            ("W", True, False, False),
            ("T", False, True, False),
            ("M", False, False, True),
            ("W+T", True, True, False),
            ("W+M", True, False, True),
            ("T+M", False, True, True),
            ("W+T+M", True, True, True),
        ]

        for name, w, t, m in test_configs:
            result = run_strategy_test(df, jackpot_days, typ, w, t, m)
            results[f"typ_{typ}"][name] = result
            print(f"    {name}: ROI {result['roi']:+.1f}%, {result['plays']} Spiele")

    # Kompatibilität analysieren
    print("\nAnalysiere Kompatibilität...")
    compatibility = analyze_compatibility(results)

    # Ergebnisse ausgeben
    print_results(results, compatibility)

    # Speichern
    save_data = {
        "results": results,
        "compatibility": compatibility
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
