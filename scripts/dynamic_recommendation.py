#!/usr/bin/env python3
"""
Dynamisches Empfehlungssystem mit Exclusion-Filter

Kombiniert:
1. Optimale Basis-Tickets (Typ 9: +351% ROI)
2. Multi-Exclusion Regeln (96%+ Accuracy)
3. Inclusion-Boost basierend auf heutiger Ziehung
4. Korrelierte Absenzen

Autor: Kenobase V2.2
Datum: 2025-12-29
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import numpy as np


# Optimale Basis-Tickets aus Analyse
OPTIMAL_TICKETS = {
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],      # ROI +351%
    8: [3, 20, 24, 27, 36, 49, 51, 64],         # ROI +115%
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],  # ROI +189%
    7: [3, 24, 30, 49, 51, 59, 64],             # ROI +41%
    6: [3, 9, 10, 32, 49, 64],                  # ROI ±0%
}

# Multi-Exclusion Regeln (Trigger -> [Exclude Zahlen], Accuracy)
MULTI_EXCLUSION_RULES = {
    (56, 11): ([41, 45, 70], 96.0),
    (57, 5): ([33, 19, 42], 93.3),
    (31, 10): ([59, 13, 28], 90.8),
    (60, 8): ([46, 48, 16], 90.0),
    (27, 15): ([1, 23, 30], 88.4),
    (4, 17): ([70], 100.0),
    (24, 2): ([22], 100.0),
    (4, 14): ([25], 100.0),
    (14, 7): ([38], 100.0),
    (5, 2): ([13], 100.0),
    (68, 20): ([65], 100.0),
    (50, 4): ([64], 100.0),
    (1, 8): ([33], 100.0),
}

# Inclusion-Boost Regeln (Trigger -> [Boost Zahlen])
INCLUSION_RULES = {
    (38, 11): [19, 67, 42, 50, 64],
    (49, 1): [70, 10, 18, 22, 17],
}

# Korrelierte Absenzen
CORRELATED_ABSENCES = [
    (41, 45, 7.5),
    (1, 37, 6.7),
    (1, 45, 6.3),
    (45, 51, 6.2),
]

# Kern-Zahlen (erscheinen in allen profitablen Tickets)
CORE_NUMBERS = [3, 24, 49, 51, 64]

# Hot Numbers (aus Frequenz-Analyse)
HOT_NUMBERS = [49, 64, 3, 51, 24, 2, 9, 36, 41, 37, 4, 25, 31, 13, 66, 52, 20, 10]


def load_latest_draw(path: str) -> Optional[Dict]:
    """Laedt die letzte Ziehung."""
    df = pd.read_csv(path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")
    df = df.sort_values("Datum", ascending=False)

    if len(df) == 0:
        return None

    latest = df.iloc[0]
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]

    return {
        "date": latest["Datum"],
        "positions": [int(latest[col]) for col in pos_cols],
        "numbers_set": set(int(latest[col]) for col in pos_cols)
    }


def apply_exclusion_rules(today_positions: List[int]) -> Set[int]:
    """Wendet Exclusion-Regeln auf heutige Ziehung an."""
    exclude = set()

    for (trigger_zahl, trigger_pos), (exclude_zahlen, accuracy) in MULTI_EXCLUSION_RULES.items():
        # Pruefe ob Trigger erfuellt (Position ist 1-indexed in Regeln)
        if trigger_pos <= len(today_positions):
            if today_positions[trigger_pos - 1] == trigger_zahl:
                exclude.update(exclude_zahlen)
                print(f"  REGEL: Zahl {trigger_zahl} an Pos {trigger_pos} -> Exclude {exclude_zahlen} ({accuracy}%)")

    return exclude


def apply_inclusion_boost(today_positions: List[int]) -> List[int]:
    """Wendet Inclusion-Boost auf heutige Ziehung an."""
    boost = []

    for (trigger_zahl, trigger_pos), boost_zahlen in INCLUSION_RULES.items():
        if trigger_pos <= len(today_positions):
            if today_positions[trigger_pos - 1] == trigger_zahl:
                boost.extend(boost_zahlen)
                print(f"  BOOST: Zahl {trigger_zahl} an Pos {trigger_pos} -> Boost {boost_zahlen}")

    return boost


def apply_absence_correlations(today_absent: Set[int]) -> Set[int]:
    """Wenn eine Zahl der korrelierten Paare fehlt, ist Partner auch unwahrscheinlich."""
    likely_absent = set()

    for z1, z2, correlation in CORRELATED_ABSENCES:
        if z1 in today_absent:
            likely_absent.add(z2)
        if z2 in today_absent:
            likely_absent.add(z1)

    return likely_absent


def generate_dynamic_ticket(
    keno_type: int,
    exclude: Set[int],
    boost: List[int],
    likely_absent: Set[int]
) -> List[int]:
    """Generiert dynamisches Ticket basierend auf Regeln."""
    # Starte mit optimalem Basis-Ticket
    base_ticket = OPTIMAL_TICKETS.get(keno_type, OPTIMAL_TICKETS[9][:keno_type])

    # Entferne excludierte Zahlen
    filtered = [z for z in base_ticket if z not in exclude and z not in likely_absent]

    # Fuege Boost-Zahlen hinzu (falls nicht excluded)
    for z in boost:
        if z not in exclude and z not in likely_absent and z not in filtered:
            filtered.append(z)

    # Fuelle mit Hot Numbers auf
    for z in HOT_NUMBERS:
        if len(filtered) >= keno_type:
            break
        if z not in exclude and z not in likely_absent and z not in filtered:
            filtered.append(z)

    # Fuelle mit Core Numbers auf
    for z in CORE_NUMBERS:
        if len(filtered) >= keno_type:
            break
        if z not in exclude and z not in likely_absent and z not in filtered:
            filtered.append(z)

    # Falls immer noch zu wenig, fuelle mit verbleibenden Zahlen
    all_numbers = list(range(1, 71))
    np.random.shuffle(all_numbers)
    for z in all_numbers:
        if len(filtered) >= keno_type:
            break
        if z not in exclude and z not in likely_absent and z not in filtered:
            filtered.append(z)

    return sorted(filtered[:keno_type])


def generate_recommendations(today_draw: Dict) -> Dict:
    """Generiert alle Empfehlungen fuer morgen."""
    today_positions = today_draw["positions"]
    today_set = today_draw["numbers_set"]
    today_absent = set(range(1, 71)) - today_set

    print("\n" + "=" * 70)
    print(f"ANALYSE DER HEUTIGEN ZIEHUNG ({today_draw['date'].date()})")
    print("=" * 70)
    print(f"\nPositionen: {today_positions}")
    print()

    # 1. Exclusion-Regeln anwenden
    print("EXCLUSION-REGELN:")
    exclude = apply_exclusion_rules(today_positions)
    if not exclude:
        print("  Keine Exclusion-Regeln getriggert")
    print(f"\n  MORGEN AUSSCHLIESSEN: {sorted(exclude) if exclude else 'keine'}")

    # 2. Inclusion-Boost anwenden
    print("\nINCLUSION-BOOST:")
    boost = apply_inclusion_boost(today_positions)
    if not boost:
        print("  Keine Boost-Regeln getriggert")
    print(f"\n  MORGEN BEVORZUGEN: {boost if boost else 'keine'}")

    # 3. Korrelierte Absenzen
    print("\nKORRELIERTE ABSENZEN:")
    likely_absent = apply_absence_correlations(today_absent)
    print(f"  Wahrscheinlich auch absent: {sorted(likely_absent) if likely_absent else 'keine'}")

    # 4. Dynamische Tickets generieren
    print("\n" + "=" * 70)
    print("EMPFEHLUNGEN FUER MORGEN")
    print("=" * 70)

    recommendations = {
        "analysis_date": str(today_draw["date"].date()),
        "for_date": str((today_draw["date"] + timedelta(days=1)).date()),
        "exclusions": sorted(exclude),
        "boosts": boost,
        "likely_absent": sorted(likely_absent),
        "tickets": {}
    }

    for keno_type in [9, 8, 10, 7, 6]:
        ticket = generate_dynamic_ticket(keno_type, exclude, boost, likely_absent)
        base = OPTIMAL_TICKETS.get(keno_type, [])

        # Berechne Aenderungen
        removed = set(base) - set(ticket)
        added = set(ticket) - set(base)

        recommendations["tickets"][f"typ_{keno_type}"] = {
            "zahlen": ticket,
            "basis": base,
            "entfernt": sorted(removed),
            "hinzugefuegt": sorted(added)
        }

        print(f"\nTYP {keno_type}:")
        print(f"  Basis:    {base}")
        print(f"  Dynamisch: {ticket}")
        if removed:
            print(f"  Entfernt: {sorted(removed)} (excluded)")
        if added:
            print(f"  Neu:      {sorted(added)}")

    return recommendations


def main():
    """Hauptfunktion."""
    print("=" * 70)
    print("KENOBASE - DYNAMISCHES EMPFEHLUNGSSYSTEM")
    print("=" * 70)
    print()

    base_path = Path(__file__).parent.parent

    # Versuche verschiedene Datenpfade
    data_paths = [
        base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    ]

    data_path = None
    for p in data_paths:
        if p.exists():
            data_path = p
            break

    if not data_path:
        print("FEHLER: Keine Datendatei gefunden!")
        return

    print(f"Lade Daten: {data_path}")

    # Letzte Ziehung laden
    today = load_latest_draw(str(data_path))
    if not today:
        print("FEHLER: Keine Ziehungsdaten gefunden!")
        return

    print(f"Letzte Ziehung: {today['date'].date()}")

    # Empfehlungen generieren
    recommendations = generate_recommendations(today)

    # Speichern
    output_path = base_path / "results" / "dynamic_recommendations.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nEmpfehlungen gespeichert: {output_path}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    print(f"""
FUER MORGEN ({recommendations['for_date']}):

BESTE EMPFEHLUNG (Typ 9, ROI +351%):
  {recommendations['tickets']['typ_9']['zahlen']}

AUSGESCHLOSSEN (basierend auf heute):
  {recommendations['exclusions'] if recommendations['exclusions'] else 'keine'}

BEVORZUGT (basierend auf heute):
  {recommendations['boosts'] if recommendations['boosts'] else 'keine'}

HINWEIS: Dies ist ein statistisches Modell.
         Keine Gewinngarantie!
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
