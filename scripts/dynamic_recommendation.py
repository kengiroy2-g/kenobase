#!/usr/bin/env python3
"""
Dynamisches Empfehlungssystem mit Exclusion-Filter und Jackpot-Warnung

Kombiniert:
1. Optimale Basis-Tickets (Typ 9: +351% ROI)
2. Multi-Exclusion Regeln (96%+ Accuracy)
3. Inclusion-Boost basierend auf heutiger Ziehung
4. Korrelierte Absenzen
5. NEU: Jackpot-Warnung (30 Tage nach GK10_10 = NICHT SPIELEN)

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


# Jackpot-Warnung Konfiguration
JACKPOT_COOLDOWN_DAYS = 30  # Tage nach Jackpot ohne Spiel
JACKPOT_ROI_PENALTY = 0.66  # 66% schlechtere Performance nach Jackpot


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


def load_jackpot_dates(gk1_path: str) -> List[datetime]:
    """Laedt alle GK10_10 Jackpot-Daten."""
    if not Path(gk1_path).exists():
        return []

    gk1_df = pd.read_csv(gk1_path, encoding="utf-8")
    gk1_df["Datum"] = pd.to_datetime(gk1_df["Datum"], format="%d.%m.%Y")

    # Nur Typ 10 Jackpots
    gk1_typ10 = gk1_df[gk1_df["Keno-Typ"] == 10]

    return sorted(gk1_typ10["Datum"].tolist())


def check_jackpot_warning(
    check_date: datetime,
    jackpot_dates: List[datetime],
    cooldown_days: int = JACKPOT_COOLDOWN_DAYS
) -> Dict:
    """
    Prueft ob ein Datum im Post-Jackpot Cooldown liegt.

    Returns:
        Dict mit:
        - in_cooldown: bool
        - days_since_jackpot: int oder None
        - last_jackpot: datetime oder None
        - days_remaining: int oder None
        - warning_level: str (NONE, LOW, MEDIUM, HIGH, CRITICAL)
    """
    result = {
        "in_cooldown": False,
        "days_since_jackpot": None,
        "last_jackpot": None,
        "days_remaining": None,
        "warning_level": "NONE"
    }

    if not jackpot_dates:
        return result

    # Finde letzten Jackpot vor check_date
    past_jackpots = [jp for jp in jackpot_dates if jp < check_date]

    if not past_jackpots:
        return result

    last_jackpot = max(past_jackpots)
    days_since = (check_date - last_jackpot).days

    result["last_jackpot"] = last_jackpot
    result["days_since_jackpot"] = days_since

    if days_since <= cooldown_days:
        result["in_cooldown"] = True
        result["days_remaining"] = cooldown_days - days_since

        # Warning Level basierend auf Tagen seit Jackpot
        if days_since <= 7:
            result["warning_level"] = "CRITICAL"  # Erste Woche: -80% ROI
        elif days_since <= 14:
            result["warning_level"] = "HIGH"      # Zweite Woche: -70% ROI
        elif days_since <= 21:
            result["warning_level"] = "MEDIUM"    # Dritte Woche: -50% ROI
        else:
            result["warning_level"] = "LOW"       # Vierte Woche: -30% ROI

    return result


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


def generate_recommendations(
    today_draw: Dict,
    jackpot_dates: List[datetime] = None
) -> Dict:
    """Generiert alle Empfehlungen fuer morgen mit Jackpot-Warnung."""
    today_positions = today_draw["positions"]
    today_set = today_draw["numbers_set"]
    today_absent = set(range(1, 71)) - today_set
    tomorrow = today_draw["date"] + timedelta(days=1)

    print("\n" + "=" * 70)
    print(f"ANALYSE DER HEUTIGEN ZIEHUNG ({today_draw['date'].date()})")
    print("=" * 70)

    # 0. JACKPOT-WARNUNG PRUEFEN (NEU!)
    jackpot_warning = None
    if jackpot_dates:
        jackpot_warning = check_jackpot_warning(tomorrow, jackpot_dates)

        if jackpot_warning["in_cooldown"]:
            print("\n" + "!" * 70)
            print(f"  ⚠️  JACKPOT-WARNUNG: {jackpot_warning['warning_level']}  ⚠️")
            print("!" * 70)
            print(f"  Letzter Jackpot: {jackpot_warning['last_jackpot'].date()}")
            print(f"  Tage seit Jackpot: {jackpot_warning['days_since_jackpot']}")
            print(f"  Verbleibende Cooldown-Tage: {jackpot_warning['days_remaining']}")
            print()
            print("  EMPFEHLUNG: NICHT SPIELEN!")
            print("  Grund: Post-Jackpot Perioden haben -66% ROI vs normal")
            print("!" * 70)
        else:
            print(f"\n  ✓ Kein Jackpot-Cooldown aktiv")
            if jackpot_warning["last_jackpot"]:
                print(f"    Letzter Jackpot: {jackpot_warning['last_jackpot'].date()} ({jackpot_warning['days_since_jackpot']} Tage her)")

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
        "for_date": str(tomorrow.date()),
        "jackpot_warning": {
            "in_cooldown": jackpot_warning["in_cooldown"] if jackpot_warning else False,
            "warning_level": jackpot_warning["warning_level"] if jackpot_warning else "NONE",
            "days_since_jackpot": jackpot_warning["days_since_jackpot"] if jackpot_warning else None,
            "days_remaining": jackpot_warning["days_remaining"] if jackpot_warning else None,
            "last_jackpot": str(jackpot_warning["last_jackpot"].date()) if jackpot_warning and jackpot_warning["last_jackpot"] else None,
            "recommendation": "NICHT SPIELEN" if (jackpot_warning and jackpot_warning["in_cooldown"]) else "SPIELEN OK"
        },
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
    print("KENOBASE - DYNAMISCHES EMPFEHLUNGSSYSTEM V2 (mit Jackpot-Warnung)")
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

    # Jackpot-Daten laden
    gk1_path = base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv"
    jackpot_dates = []
    if gk1_path.exists():
        jackpot_dates = load_jackpot_dates(str(gk1_path))
        print(f"Jackpot-Daten geladen: {len(jackpot_dates)} GK10_10 Events")
    else:
        print("WARNUNG: Keine Jackpot-Daten gefunden - Warnung deaktiviert")

    # Letzte Ziehung laden
    today = load_latest_draw(str(data_path))
    if not today:
        print("FEHLER: Keine Ziehungsdaten gefunden!")
        return

    print(f"Letzte Ziehung: {today['date'].date()}")

    # Empfehlungen generieren (mit Jackpot-Warnung)
    recommendations = generate_recommendations(today, jackpot_dates)

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

    jp_info = recommendations.get("jackpot_warning", {})
    jp_status = "⚠️ NICHT SPIELEN" if jp_info.get("in_cooldown") else "✓ SPIELEN OK"

    print(f"""
FUER MORGEN ({recommendations['for_date']}):

JACKPOT-STATUS: {jp_status}
  Letzter Jackpot: {jp_info.get('last_jackpot', 'unbekannt')}
  Tage seit Jackpot: {jp_info.get('days_since_jackpot', 'N/A')}
  Warning Level: {jp_info.get('warning_level', 'NONE')}
""")

    if jp_info.get("in_cooldown"):
        print(f"""  ⚠️ ACHTUNG: Noch {jp_info.get('days_remaining')} Tage Cooldown!
  Post-Jackpot Perioden haben -66% ROI vs normal.
  Empfehlung: Warten bis Cooldown abgelaufen.
""")
    else:
        print(f"""BESTE EMPFEHLUNG (Typ 9, ROI +351%):
  {recommendations['tickets']['typ_9']['zahlen']}

AUSGESCHLOSSEN (basierend auf heute):
  {recommendations['exclusions'] if recommendations['exclusions'] else 'keine'}

BEVORZUGT (basierend auf heute):
  {recommendations['boosts'] if recommendations['boosts'] else 'keine'}
""")

    print("""HINWEIS: Dies ist ein statistisches Modell.
         Keine Gewinngarantie!
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
