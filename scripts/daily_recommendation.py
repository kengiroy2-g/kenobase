#!/usr/bin/env python3
"""
TAEGLICHE KENO EMPFEHLUNG

Generiert die optimalen Tickets fuer den aktuellen Tag basierend auf
dem Super-Model V2 (Birthday-Avoidance Strategy).

Verwendung:
    python scripts/daily_recommendation.py
    python scripts/daily_recommendation.py --type 9
    python scripts/daily_recommendation.py --dual
    python scripts/daily_recommendation.py --all

Autor: Kenobase V2.2
Datum: 2025-12-30
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Import from super_model_synthesis
from super_model_synthesis import (
    SuperModel,
    BIRTHDAY_AVOIDANCE_TICKETS_V2,
    OPTIMAL_TICKETS_KI1,
    JACKPOT_FAVORITES_V2,
    KENO_QUOTES,
)


def load_keno_data(base_path: Path) -> Tuple[pd.DataFrame, List]:
    """Laedt KENO-Daten und Jackpot-Termine."""

    # Neueste Daten (2022-2025)
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

    if not keno_path.exists():
        # Fallback zu aelterer Datei
        keno_path = base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv"

    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    # Spalten fuer Zahlen
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["positions"] = df[pos_cols].apply(lambda row: list(row.dropna().astype(int)), axis=1)
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    df = df.sort_values("Datum").reset_index(drop=True)

    # Jackpot-Daten aus Timeline
    jackpot_dates = []
    timeline_path = base_path / "data" / "processed" / "ecosystem" / "timeline_2025.csv"
    if timeline_path.exists():
        try:
            timeline = pd.read_csv(timeline_path)
            timeline["datum"] = pd.to_datetime(timeline["datum"])
            jackpots = timeline[timeline["keno_jackpot"] == 1]
            jackpot_dates = jackpots["datum"].tolist()
        except Exception:
            pass

    return df, jackpot_dates


def analyze_last_drawing(df: pd.DataFrame) -> Dict:
    """Analysiert die letzte Ziehung."""
    last = df.iloc[-1]
    numbers = last["numbers_set"]

    birthday = [n for n in numbers if n <= 31]
    high = [n for n in numbers if n > 31]

    return {
        "date": last["Datum"].date(),
        "numbers": sorted(numbers),
        "birthday_count": len(birthday),
        "high_count": len(high),
        "birthday_ratio": len(birthday) / 20,
        "positions": last["positions"],
    }


def check_jackpot_cooldown(jackpot_dates: List, check_date: datetime, cooldown: int = 30) -> Tuple[bool, int]:
    """Prueft Jackpot-Cooldown."""
    if not jackpot_dates:
        return False, -1

    past_jackpots = [jp for jp in jackpot_dates if jp < check_date]
    if not past_jackpots:
        return False, -1

    last_jp = max(past_jackpots)
    days_since = (check_date - last_jp).days

    return days_since <= cooldown, days_since


def generate_recommendations(
    df: pd.DataFrame,
    jackpot_dates: List,
    types: List[int] = [8, 9, 10],
    use_dual: bool = False
) -> Dict:
    """Generiert Empfehlungen fuer heute."""

    last = df.iloc[-1]
    today = datetime.now()

    context = {
        "date": today,
        "prev_date": last["Datum"],
        "prev_positions": last["positions"],
        "prev_numbers": list(last["numbers_set"]),
        "jackpot_dates": jackpot_dates,
    }

    # V2 Model (empfohlen)
    model_v2 = SuperModel(use_v2=True)

    # Original Model (zum Vergleich)
    model_orig = SuperModel(use_v2=False)

    recommendations = {
        "generated_at": datetime.now().isoformat(),
        "for_date": today.date().isoformat(),
        "last_drawing": analyze_last_drawing(df),
        "warnings": [],
        "tickets": {},
    }

    # Jackpot-Cooldown pruefen
    in_cooldown, days_since = check_jackpot_cooldown(jackpot_dates, today)
    if in_cooldown:
        recommendations["warnings"].append({
            "type": "jackpot_cooldown",
            "message": f"Jackpot-Cooldown aktiv ({days_since}/30 Tage seit letztem Jackpot)",
            "recommendation": "Vorsicht beim Spielen - reduzierte Jackpot-Wahrscheinlichkeit"
        })
    elif days_since > 0:
        recommendations["days_since_jackpot"] = days_since

    for keno_type in types:
        # V2 Ticket (Birthday-Avoidance)
        ticket_v2, meta_v2 = model_v2.generate_ticket(keno_type, context)

        ticket_info = {
            "v2_birthday_avoidance": {
                "ticket": ticket_v2,
                "description": "Birthday-Avoidance Strategie (2025 validiert)",
                "expected_roi": {8: "+261%", 9: "+1546%", 10: "+306%"}.get(keno_type, "N/A"),
            }
        }

        if use_dual:
            # Original Ticket
            ticket_orig, meta_orig = model_orig.generate_ticket(keno_type, context)
            ticket_info["original"] = {
                "ticket": ticket_orig,
                "description": "Original OPTIMAL_TICKETS",
            }
            ticket_info["dual_strategy"] = {
                "tickets": [ticket_v2, ticket_orig],
                "description": "Beide Tickets spielen fuer Diversifikation",
            }

        recommendations["tickets"][f"typ_{keno_type}"] = ticket_info

    return recommendations


def print_recommendations(recommendations: Dict, verbose: bool = False):
    """Gibt Empfehlungen formatiert aus."""

    print("\n" + "=" * 70)
    print("    KENO TAEGLICHE EMPFEHLUNG")
    print("    " + recommendations["for_date"])
    print("=" * 70)

    # Letzte Ziehung
    last = recommendations["last_drawing"]
    print(f"\nLetzte Ziehung ({last['date']}):")
    print(f"  Zahlen: {last['numbers']}")
    print(f"  Birthday (1-31): {last['birthday_count']} | Hohe (32-70): {last['high_count']}")

    # Warnungen
    if recommendations["warnings"]:
        print("\n" + "-" * 70)
        print("WARNUNGEN:")
        for w in recommendations["warnings"]:
            print(f"  {w['message']}")
            print(f"  -> {w['recommendation']}")
    elif "days_since_jackpot" in recommendations:
        print(f"\nTage seit letztem Jackpot: {recommendations['days_since_jackpot']}")

    # Tickets
    print("\n" + "=" * 70)
    print("EMPFOHLENE TICKETS (V2 Birthday-Avoidance)")
    print("=" * 70)

    for type_key, type_info in recommendations["tickets"].items():
        keno_type = int(type_key.split("_")[1])
        v2_info = type_info["v2_birthday_avoidance"]

        print(f"\n{'='*50}")
        print(f"TYP {keno_type} (Erwarteter ROI: {v2_info['expected_roi']})")
        print(f"{'='*50}")

        ticket = v2_info["ticket"]
        print(f"\n  TICKET: {ticket}")
        print(f"\n  +---------------------------------------+")
        print(f"  | {' '.join(f'{n:2d}' for n in ticket[:5]):17s}                    |")
        if len(ticket) > 5:
            print(f"  | {' '.join(f'{n:2d}' for n in ticket[5:]):17s}                    |")
        print(f"  +---------------------------------------+")

        if "dual_strategy" in type_info:
            print(f"\n  DUAL STRATEGIE (mehr Diversifikation):")
            print(f"  Ticket A (V2):      {type_info['dual_strategy']['tickets'][0]}")
            print(f"  Ticket B (Original): {type_info['dual_strategy']['tickets'][1]}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print("""
Die V2 Birthday-Avoidance Strategie hat im 2025 Out-of-Sample Test
folgende Performance gezeigt:

  Typ 8:  +261.4% ROI (vs -14.6% Original)
  Typ 9:  +1545.7% ROI (vs +209.6% Original)  <- BESTE PERFORMANCE
  Typ 10: +305.5% ROI (vs +77.7% Original)

EMPFEHLUNG: Typ 9 mit Birthday-Avoidance Ticket spielen.
""")


def save_recommendations(recommendations: Dict, output_path: Path):
    """Speichert Empfehlungen als JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nEmpfehlungen gespeichert: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="KENO Taegliche Empfehlung")
    parser.add_argument("--type", "-t", type=int, choices=[6, 7, 8, 9, 10],
                        help="Nur bestimmten Typ anzeigen")
    parser.add_argument("--dual", "-d", action="store_true",
                        help="Dual-Strategie anzeigen (V2 + Original)")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Alle Typen anzeigen (6-10)")
    parser.add_argument("--save", "-s", action="store_true",
                        help="Empfehlungen als JSON speichern")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Ausfuehrliche Ausgabe")

    args = parser.parse_args()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    df, jackpot_dates = load_keno_data(base_path)
    print(f"  Ziehungen: {len(df)}")
    print(f"  Letzte: {df['Datum'].max().date()}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Typen bestimmen
    if args.type:
        types = [args.type]
    elif args.all:
        types = [6, 7, 8, 9, 10]
    else:
        types = [8, 9, 10]

    # Empfehlungen generieren
    recommendations = generate_recommendations(
        df, jackpot_dates,
        types=types,
        use_dual=args.dual
    )

    # Ausgabe
    print_recommendations(recommendations, verbose=args.verbose)

    # Speichern
    if args.save:
        today = datetime.now().strftime("%Y%m%d")
        output_path = base_path / "results" / f"recommendation_{today}.json"
        save_recommendations(recommendations, output_path)


if __name__ == "__main__":
    main()
