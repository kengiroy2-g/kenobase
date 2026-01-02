"""
TEST: Kombinierte Strategie für Typ 6, 7, 8, 9

Basierend auf Erkenntnissen aus Sektion 13 (Strategie-Kompatibilität):
- Filter interferieren unterschiedlich je nach Typ
- Nicht alle Kombinationen sind synergistisch

Testet alle Filter-Kombinationen für jeden Typ.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from itertools import combinations
import json


# Gewinnquoten für KENO (Einsatz 1 EUR)
KENO_GEWINN = {
    # Typ 10
    10: {10: 100000, 9: 1000, 8: 100, 7: 15, 6: 5, 5: 2, 0: 2},
    # Typ 9
    9: {9: 50000, 8: 1000, 7: 20, 6: 5, 5: 2, 0: 2},
    # Typ 8
    8: {8: 10000, 7: 100, 6: 15, 5: 2, 4: 1, 0: 2},
    # Typ 7
    7: {7: 5000, 6: 100, 5: 12, 4: 1, 0: 1},
    # Typ 6
    6: {6: 1000, 5: 50, 4: 4, 3: 1, 0: 1},
}


def load_data():
    """Lade KENO-Daten und Wirtschaftsdaten."""
    # KENO Ziehungen
    keno_path = Path("data/raw/keno/KENO_ab_2022_bereinigt.csv")
    keno_df = pd.read_csv(keno_path, sep=";", decimal=",")
    keno_df["Datum"] = pd.to_datetime(keno_df["Datum"], format="%d.%m.%Y")

    # Jackpot-Tage ermitteln
    quoten_paths = [
        Path("Keno_GPTs/Keno_GQ_2022_2023-2024.csv"),
        Path("Keno_GPTs/Keno_GQ_2025.csv"),
        Path("Keno_GPTs/Keno_GQ_2024.csv"),
        Path("Keno_GPTs/Keno_GQ_2023.csv"),
        Path("Keno_GPTs/Keno_GQ_2022.csv"),
    ]

    all_quoten = []
    for path in quoten_paths:
        if path.exists():
            try:
                df = pd.read_csv(path, encoding="utf-8-sig")
                all_quoten.append(df)
            except:
                pass

    quoten_df = pd.concat(all_quoten, ignore_index=True) if all_quoten else pd.DataFrame()

    # Jackpot-Tage extrahieren
    jackpot_dates = []
    if not quoten_df.empty and "Datum" in quoten_df.columns:
        def parse_date(d):
            if pd.isna(d):
                return pd.NaT
            d = str(d).strip()
            if ", " in d and len(d.split(", ")[0]) <= 3:
                d = d.split(", ")[1]
            try:
                return pd.to_datetime(d, format="%d.%m.%Y")
            except:
                return pd.NaT

        quoten_df["Datum_parsed"] = quoten_df["Datum"].apply(parse_date)
        jackpot_mask = (quoten_df["Keno-Typ"] == 10) & (quoten_df["Anzahl richtiger Zahlen"] == 10)
        jackpot_df = quoten_df[jackpot_mask].copy()

        if "Anzahl der Gewinner" in jackpot_df.columns:
            jackpot_df["Gewinner"] = jackpot_df["Anzahl der Gewinner"].astype(str).str.replace(".", "").str.replace(",", ".")
            jackpot_df["Gewinner"] = pd.to_numeric(jackpot_df["Gewinner"], errors="coerce").fillna(0).astype(int)
            jackpot_dates = jackpot_df[jackpot_df["Gewinner"] > 0]["Datum_parsed"].dropna().dt.strftime("%Y-%m-%d").tolist()

    # Wirtschaftsdaten laden
    wirtschaft_path = Path("AI_COLLABORATION/RESULTS/monthly_economic_data.json")
    wirtschaft = {}
    if wirtschaft_path.exists():
        with open(wirtschaft_path, "r") as f:
            data = json.load(f)
            for entry in data:
                month_key = entry.get("month", "")
                wirtschaft[month_key] = {
                    "inflation": entry.get("inflation", 3.0),
                    "dax_trend": "steigend" if entry.get("dax_change", 0) > 0 else "fallend"
                }

    return keno_df, jackpot_dates, wirtschaft


def check_timing_filter(date):
    """Tag 24-28 Filter (2.02x Effizienz)."""
    day = date.day
    if 24 <= day <= 28:
        return True, 2.02
    elif 22 <= day <= 28:
        return True, 1.63
    return False, 0.7


def check_cooldown_filter(date, jackpot_dates):
    """Korrigierter Cooldown-Filter."""
    for jp_str in jackpot_dates:
        try:
            jp_date = datetime.strptime(jp_str, "%Y-%m-%d")
            days_since = (date - jp_date).days

            if days_since < 0:
                continue

            if 8 <= days_since <= 14:
                return True, 1.54  # BOOST Phase!
            if 22 <= days_since <= 30:
                return False, 0.79  # Wahrer Cooldown
            if days_since >= 61:
                return False, 0.30  # Schlechteste Phase
        except:
            continue

    return True, 1.0


def check_wirtschaft_filter(date, wirtschaft):
    """Wirtschafts-Filter (Inflation + DAX)."""
    month_key = date.strftime("%Y-%m")
    if month_key in wirtschaft:
        data = wirtschaft[month_key]
        inflation = data.get("inflation", 3.0)
        dax_trend = data.get("dax_trend", "neutral")

        if inflation < 3.7 and dax_trend == "steigend":
            return True, 1.5
        elif inflation > 5.0 or dax_trend == "fallend":
            return False, 0.5

    return True, 1.0


def check_mod7_filter(numbers):
    """mod 7 = 3 Filter."""
    diff_sum = 0
    sorted_nums = sorted(numbers)
    for i in range(len(sorted_nums)):
        for j in range(i + 1, len(sorted_nums)):
            diff_sum += abs(sorted_nums[j] - sorted_nums[i])

    return diff_sum % 7 == 3, 7.0 if diff_sum % 7 == 3 else 0.14


def generate_random_ticket(keno_type):
    """Generiere zufaelliges Ticket für gegebenen Typ."""
    return sorted(np.random.choice(range(1, 71), size=keno_type, replace=False).tolist())


def calculate_gewinn(ticket, gezogene_20, keno_type):
    """Berechne Gewinn für ein Ticket."""
    treffer = len(set(ticket) & set(gezogene_20))

    gewinn_tabelle = KENO_GEWINN.get(keno_type, {})
    return gewinn_tabelle.get(treffer, 0)


def run_simulation(keno_df, jackpot_dates, wirtschaft, keno_type, strategy_flags, n_tickets=100):
    """
    Simuliere Strategie für gegebenen Typ.

    strategy_flags = {
        "timing": True/False,
        "cooldown": True/False,
        "wirtschaft": True/False,
        "mod7": True/False
    }
    """
    results = {
        "type": keno_type,
        "strategy": strategy_flags,
        "spiele": 0,
        "kosten": 0,
        "gewinn": 0,
        "treffer_verteilung": {},
    }

    # Fuer jeden Tag
    for _, row in keno_df.iterrows():
        date = row["Datum"].to_pydatetime()

        # Filter pruefen
        play = True

        if strategy_flags.get("timing"):
            passed, _ = check_timing_filter(date)
            if not passed:
                play = False

        if play and strategy_flags.get("cooldown"):
            passed, _ = check_cooldown_filter(date, jackpot_dates)
            if not passed:
                play = False

        if play and strategy_flags.get("wirtschaft"):
            passed, _ = check_wirtschaft_filter(date, wirtschaft)
            if not passed:
                play = False

        if not play:
            continue

        # Gezogene Zahlen (Spalten: Keno_Z1 bis Keno_Z20)
        gezogene_20 = []
        for i in range(1, 21):
            col = f"Keno_Z{i}"
            if col in row:
                gezogene_20.append(int(row[col]))

        if len(gezogene_20) != 20:
            continue

        # Generiere und teste Tickets
        for _ in range(n_tickets):
            ticket = generate_random_ticket(keno_type)

            # mod7 Filter (auf Ticket-Ebene)
            if strategy_flags.get("mod7"):
                passed, _ = check_mod7_filter(ticket)
                if not passed:
                    continue

            results["spiele"] += 1
            results["kosten"] += 1  # 1 EUR pro Spiel

            # Gewinn berechnen
            treffer = len(set(ticket) & set(gezogene_20))
            gewinn = calculate_gewinn(ticket, gezogene_20, keno_type)
            results["gewinn"] += gewinn

            # Treffer-Verteilung
            results["treffer_verteilung"][treffer] = results["treffer_verteilung"].get(treffer, 0) + 1

    # ROI berechnen
    if results["kosten"] > 0:
        results["roi"] = (results["gewinn"] - results["kosten"]) / results["kosten"] * 100
    else:
        results["roi"] = 0

    return results


def main():
    print("=" * 80)
    print("STRATEGIE-TEST: TYP 6, 7, 8, 9")
    print("=" * 80)

    print("\nLade Daten...")
    keno_df, jackpot_dates, wirtschaft = load_data()
    print(f"  Ziehungen: {len(keno_df)}")
    print(f"  Jackpot-Tage: {len(jackpot_dates)}")
    print(f"  Wirtschafts-Monate: {len(wirtschaft)}")

    # Strategie-Kombinationen (ohne Wirtschaft da keine Daten)
    strategies = [
        {"name": "Baseline", "timing": False, "cooldown": False, "wirtschaft": False, "mod7": False},
        {"name": "Nur Timing", "timing": True, "cooldown": False, "wirtschaft": False, "mod7": False},
        {"name": "Nur Cooldown", "timing": False, "cooldown": True, "wirtschaft": False, "mod7": False},
        {"name": "Nur mod7", "timing": False, "cooldown": False, "wirtschaft": False, "mod7": True},
        {"name": "Timing+Cooldown", "timing": True, "cooldown": True, "wirtschaft": False, "mod7": False},
        {"name": "Timing+mod7", "timing": True, "cooldown": False, "wirtschaft": False, "mod7": True},
        {"name": "Cooldown+mod7", "timing": False, "cooldown": True, "wirtschaft": False, "mod7": True},
        {"name": "Alle Filter", "timing": True, "cooldown": True, "wirtschaft": False, "mod7": True},
    ]

    all_results = {}

    for keno_type in [6, 7, 8, 9]:
        print(f"\n{'=' * 80}")
        print(f"TYP {keno_type}")
        print("=" * 80)

        type_results = []

        for strat in strategies:
            flags = {k: v for k, v in strat.items() if k != "name"}

            print(f"\n  Testing: {strat['name']}...", end=" ")

            result = run_simulation(
                keno_df, jackpot_dates, wirtschaft,
                keno_type, flags, n_tickets=50  # 50 Tickets pro Tag für Speed
            )
            result["strategy_name"] = strat["name"]
            type_results.append(result)

            print(f"ROI: {result['roi']:.1f}%, Spiele: {result['spiele']}")

        # Sortiere nach ROI
        type_results.sort(key=lambda x: x["roi"], reverse=True)
        all_results[keno_type] = type_results

        # Beste Strategie anzeigen
        best = type_results[0]
        print(f"\n  >>> BESTE STRATEGIE: {best['strategy_name']}")
        print(f"      ROI: {best['roi']:.1f}%")
        print(f"      Spiele: {best['spiele']}")
        print(f"      Gewinn: {best['gewinn']:.0f} EUR")
        print(f"      Kosten: {best['kosten']:.0f} EUR")

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG: BESTE STRATEGIE PRO TYP")
    print("=" * 80)

    print(f"\n{'Typ':<6} {'Beste Strategie':<20} {'ROI':<10} {'Spiele':<10} {'vs Baseline'}")
    print("-" * 70)

    for keno_type in [6, 7, 8, 9]:
        results = all_results[keno_type]
        best = results[0]
        baseline = next((r for r in results if r["strategy_name"] == "Baseline"), None)

        baseline_roi = baseline["roi"] if baseline else 0
        delta = best["roi"] - baseline_roi

        print(f"{keno_type:<6} {best['strategy_name']:<20} {best['roi']:.1f}%     {best['spiele']:<10} {delta:+.1f}%")

    # Speichern
    output = {
        "metadata": {
            "date": datetime.now().isoformat(),
            "types_tested": [6, 7, 8, 9],
            "tickets_per_day": 50,
        },
        "results": {}
    }

    for keno_type, results in all_results.items():
        output["results"][str(keno_type)] = [
            {
                "strategy": r["strategy_name"],
                "roi": round(r["roi"], 2),
                "spiele": r["spiele"],
                "gewinn": r["gewinn"],
                "kosten": r["kosten"],
            }
            for r in results
        ]

    output_path = Path("results/strategy_test_types_6_9.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
