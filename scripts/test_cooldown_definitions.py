"""
TEST: Cooldown-Effekt mit verschiedenen Jackpot-Definitionen

Definitionen:
1. JP_10_10: Typ 10, 10/10 richtig, ≥1 Gewinner (100.000€)
2. JP_9_9:   Typ 9, 9/9 richtig, ≥1 Gewinner (50.000€)
3. JP_10_9:  Typ 10, 9/10 richtig, ≥1 Gewinner (1.000€)

Testet ob der Cooldown-Effekt (8-14 Tage = BOOST) auch für andere
Jackpot-Definitionen gilt.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json


def load_quoten_data():
    """Lade alle Quoten-Daten."""
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
            except Exception as e:
                print(f"  Fehler bei {path}: {e}")

    if not all_quoten:
        return pd.DataFrame()

    quoten_df = pd.concat(all_quoten, ignore_index=True)

    # Datum parsen
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
    quoten_df = quoten_df.dropna(subset=["Datum_parsed"])

    # Gewinner-Spalte bereinigen
    if "Anzahl der Gewinner" in quoten_df.columns:
        quoten_df["Gewinner"] = quoten_df["Anzahl der Gewinner"].astype(str).str.replace(".", "").str.replace(",", ".")
        quoten_df["Gewinner"] = pd.to_numeric(quoten_df["Gewinner"], errors="coerce").fillna(0).astype(int)

    return quoten_df


def extract_jackpot_dates(quoten_df, definition):
    """Extrahiere Jackpot-Tage basierend auf Definition."""

    if definition == "JP_10_10":
        # Typ 10, 10/10 richtig, ≥1 Gewinner
        mask = (
            (quoten_df["Keno-Typ"] == 10) &
            (quoten_df["Anzahl richtiger Zahlen"] == 10) &
            (quoten_df["Gewinner"] > 0)
        )
    elif definition == "JP_9_9":
        # Typ 9, 9/9 richtig, ≥1 Gewinner
        mask = (
            (quoten_df["Keno-Typ"] == 9) &
            (quoten_df["Anzahl richtiger Zahlen"] == 9) &
            (quoten_df["Gewinner"] > 0)
        )
    elif definition == "JP_10_9":
        # Typ 10, 9/10 richtig, ≥1 Gewinner
        mask = (
            (quoten_df["Keno-Typ"] == 10) &
            (quoten_df["Anzahl richtiger Zahlen"] == 9) &
            (quoten_df["Gewinner"] > 0)
        )
    else:
        return set()

    jp_dates = quoten_df[mask]["Datum_parsed"].dt.date.unique()
    return set(jp_dates)


def load_keno_data():
    """Lade KENO-Ziehungsdaten."""
    keno_path = Path("data/raw/keno/KENO_ab_2022_bereinigt.csv")
    keno_df = pd.read_csv(keno_path, sep=";", decimal=",")
    keno_df["Datum"] = pd.to_datetime(keno_df["Datum"], format="%d.%m.%Y")
    return keno_df


def analyze_cooldown(keno_df, jackpot_dates, definition_name):
    """Analysiere Cooldown-Effekt für gegebene Jackpot-Definition."""

    all_dates = sorted(keno_df["Datum"].dt.date.tolist())
    jackpot_list = sorted([d for d in jackpot_dates if d in set(all_dates)])

    total_days = len(all_dates)
    total_jackpots_10_10 = len(jackpot_list)

    # Für Baseline: verwende immer 10/10 Jackpots
    # Aber für Cooldown-Berechnung: verwende die angegebene Definition

    # Berechne Tage seit letztem "Jackpot" (nach Definition)
    days_since_jackpot = {}
    last_jp = None

    for date in all_dates:
        if date in jackpot_dates:
            if last_jp is not None:
                days_since_jackpot[date] = (date - last_jp).days
            last_jp = date
        elif last_jp is not None:
            days_since_jackpot[date] = (date - last_jp).days

    return days_since_jackpot, jackpot_list


def test_cooldown_strategy(keno_df, quoten_df, jp_definition, test_type=6):
    """
    Teste Strategie mit gegebener Jackpot-Definition für Cooldown.

    Spielt nur wenn 8-14 Tage seit letztem "Jackpot" (nach Definition).
    """

    # Jackpot-Tage für diese Definition
    jp_dates = extract_jackpot_dates(quoten_df, jp_definition)

    # Für Gewinn-Berechnung: 10/10 Jackpots
    jp_10_10 = extract_jackpot_dates(quoten_df, "JP_10_10")

    # Gewinnquoten
    KENO_GEWINN = {
        6: {6: 1000, 5: 50, 4: 4, 3: 1, 0: 1},
        7: {7: 5000, 6: 100, 5: 12, 4: 1, 0: 1},
        8: {8: 10000, 7: 100, 6: 15, 5: 2, 4: 1, 0: 2},
    }

    results = {
        "definition": jp_definition,
        "jp_count": len(jp_dates),
        "type": test_type,
        "periods": {},
    }

    all_dates = keno_df["Datum"].dt.date.tolist()

    # Berechne Tage seit letztem JP (nach Definition)
    days_since = {}
    last_jp = None
    for date in sorted(all_dates):
        if date in jp_dates:
            last_jp = date
        if last_jp is not None:
            days_since[date] = (date - last_jp).days

    # Teste verschiedene Perioden
    periods = [
        ("1-7", 1, 7),
        ("8-14", 8, 14),
        ("15-21", 15, 21),
        ("22-30", 22, 30),
        ("31-60", 31, 60),
        ("61+", 61, 9999),
    ]

    for period_name, start, end in periods:
        spiele = 0
        gewinn = 0

        for _, row in keno_df.iterrows():
            date = row["Datum"].date()

            if date not in days_since:
                continue

            ds = days_since[date]
            if not (start <= ds <= end):
                continue

            # Gezogene Zahlen
            gezogene_20 = [int(row[f"Keno_Z{i}"]) for i in range(1, 21)]

            # Simuliere 20 zufällige Tickets
            for _ in range(20):
                ticket = sorted(np.random.choice(range(1, 71), size=test_type, replace=False).tolist())
                treffer = len(set(ticket) & set(gezogene_20))

                spiele += 1
                gewinn += KENO_GEWINN[test_type].get(treffer, 0)

        roi = (gewinn - spiele) / spiele * 100 if spiele > 0 else 0

        results["periods"][period_name] = {
            "spiele": spiele,
            "gewinn": gewinn,
            "kosten": spiele,
            "roi": round(roi, 1),
        }

    return results


def main():
    print("=" * 80)
    print("COOLDOWN-TEST: 3 JACKPOT-DEFINITIONEN")
    print("=" * 80)

    print("\nLade Daten...")
    quoten_df = load_quoten_data()
    keno_df = load_keno_data()

    print(f"  Ziehungen: {len(keno_df)}")
    print(f"  Quoten-Einträge: {len(quoten_df)}")

    # Jackpot-Counts pro Definition
    definitions = ["JP_10_10", "JP_9_9", "JP_10_9"]

    print("\n" + "-" * 80)
    print("JACKPOT-DEFINITIONEN:")
    print("-" * 80)

    for defn in definitions:
        jp_dates = extract_jackpot_dates(quoten_df, defn)
        desc = {
            "JP_10_10": "Typ 10, 10/10 richtig (100.000€)",
            "JP_9_9": "Typ 9, 9/9 richtig (50.000€)",
            "JP_10_9": "Typ 10, 9/10 richtig (1.000€)",
        }
        print(f"  {defn}: {len(jp_dates)} Tage - {desc[defn]}")

    # Teste jede Definition für Typ 6, 7, 8
    all_results = {}

    for test_type in [6, 7, 8]:
        print(f"\n{'=' * 80}")
        print(f"TYP {test_type}")
        print("=" * 80)

        type_results = {}

        for defn in definitions:
            print(f"\n  Testing {defn}...", end=" ")
            result = test_cooldown_strategy(keno_df, quoten_df, defn, test_type)
            type_results[defn] = result

            # Beste Periode finden
            best_period = max(result["periods"].items(), key=lambda x: x[1]["roi"])
            print(f"Beste Periode: {best_period[0]} (ROI: {best_period[1]['roi']}%)")

        all_results[test_type] = type_results

        # Vergleichstabelle
        print(f"\n  {'Definition':<12} {'1-7':<10} {'8-14':<10} {'15-21':<10} {'22-30':<10} {'31-60':<10} {'61+':<10}")
        print("  " + "-" * 72)

        for defn in definitions:
            row = f"  {defn:<12}"
            for period in ["1-7", "8-14", "15-21", "22-30", "31-60", "61+"]:
                roi = type_results[defn]["periods"][period]["roi"]
                marker = "**" if roi > 20 else ""
                row += f" {roi:>6.1f}%{marker:<2}"
            print(row)

    # Zusammenfassung
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG: BESTE DEFINITION PRO TYP")
    print("=" * 80)

    print(f"\n{'Typ':<6} {'Beste Definition':<15} {'Beste Periode':<12} {'ROI':<10} {'vs JP_10_10'}")
    print("-" * 60)

    summary = {}
    for test_type in [6, 7, 8]:
        best_defn = None
        best_roi = -999
        best_period = None

        for defn in definitions:
            for period, data in all_results[test_type][defn]["periods"].items():
                if data["roi"] > best_roi:
                    best_roi = data["roi"]
                    best_defn = defn
                    best_period = period

        # ROI mit JP_10_10 für Vergleich
        jp_10_10_roi = all_results[test_type]["JP_10_10"]["periods"].get("8-14", {}).get("roi", 0)
        delta = best_roi - jp_10_10_roi

        print(f"{test_type:<6} {best_defn:<15} {best_period:<12} {best_roi:>6.1f}%    {delta:+.1f}%")

        summary[test_type] = {
            "best_definition": best_defn,
            "best_period": best_period,
            "best_roi": best_roi,
        }

    # Detailanalyse: 8-14 Tage Vergleich
    print("\n" + "=" * 80)
    print("DETAIL: PERIODE 8-14 TAGE (BOOST-PHASE)")
    print("=" * 80)

    print(f"\n{'Typ':<6} {'JP_10_10':<12} {'JP_9_9':<12} {'JP_10_9':<12} {'Beste'}")
    print("-" * 55)

    for test_type in [6, 7, 8]:
        rois = {}
        for defn in definitions:
            rois[defn] = all_results[test_type][defn]["periods"]["8-14"]["roi"]

        best = max(rois, key=rois.get)
        print(f"{test_type:<6} {rois['JP_10_10']:>8.1f}%    {rois['JP_9_9']:>8.1f}%    {rois['JP_10_9']:>8.1f}%    {best}")

    # Speichern
    output = {
        "metadata": {
            "date": datetime.now().isoformat(),
            "definitions": {
                "JP_10_10": "Typ 10, 10/10 richtig, ≥1 Gewinner (100.000€)",
                "JP_9_9": "Typ 9, 9/9 richtig, ≥1 Gewinner (50.000€)",
                "JP_10_9": "Typ 10, 9/10 richtig, ≥1 Gewinner (1.000€)",
            },
            "jp_counts": {
                defn: len(extract_jackpot_dates(quoten_df, defn))
                for defn in definitions
            },
        },
        "results": {},
        "summary": summary,
    }

    for test_type in [6, 7, 8]:
        output["results"][str(test_type)] = {}
        for defn in definitions:
            output["results"][str(test_type)][defn] = all_results[test_type][defn]["periods"]

    output_path = Path("results/cooldown_definitions_test.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
