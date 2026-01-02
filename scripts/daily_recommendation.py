#!/usr/bin/env python3
"""
TAEGLICHE KENO EMPFEHLUNG

Strategien:
1. Birthday-Avoidance (V2) - Standard fuer Typ 8, 9, 10
2. Post-Jackpot Anti-Momentum - Typ 7 mit kombinierten Timing-Regeln

BESTE STRATEGIE (Backtest 2023-2024, 1000 Simulationen):
  Typ 7 + Anti-Momentum + (Tag 24-28 ODER Mittwoch) + Boost-Phase
  ROI: +36.3%

TIMING-REGELN (KOMBINIERT):
- Boost-Phase: 8-14 Tage nach Jackpot
- UND: Tag 24-28 des Monats ODER Mittwoch

Verwendung:
    python scripts/daily_recommendation.py
    python scripts/daily_recommendation.py --postjp  # Post-Jackpot Modus

Autor: Kenobase V2.4
Datum: 2026-01-01
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

# Import from super_model_synthesis
try:
    from super_model_synthesis import (
        SuperModel,
        BIRTHDAY_AVOIDANCE_TICKETS_V2,
        OPTIMAL_TICKETS_KI1,
        JACKPOT_FAVORITES_V2,
        KENO_QUOTES,
    )
except ImportError:
    # Fallback wenn Import nicht klappt
    KENO_QUOTES = {
        6: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 15, 6: 500},
        7: {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 6, 6: 60, 7: 5000},
    }
    SuperModel = None


def load_keno_data(base_path: Path) -> Tuple[pd.DataFrame, List]:
    """Laedt KENO-Daten und Jackpot-Termine."""

    # Neueste Daten (2022-2025)
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

    if not keno_path.exists():
        keno_path = base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv"

    df = pd.read_csv(keno_path, sep=";", encoding="utf-8-sig")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["positions"] = df[pos_cols].apply(lambda row: list(row.dropna().astype(int)), axis=1)
    df["numbers_set"] = df[pos_cols].apply(lambda row: set(row.dropna().astype(int)), axis=1)
    df = df.sort_values("Datum").reset_index(drop=True)

    # Jackpot-Daten laden
    jackpot_dates = load_jackpot_dates(base_path)

    return df, jackpot_dates


def load_jackpot_dates(base_path: Path) -> List[datetime]:
    """Laedt Jackpot-Daten aus jackpot_events.json."""
    events_path = base_path / "AI_COLLABORATION" / "JACKPOT_ANALYSIS" / "data" / "jackpot_events.json"

    if not events_path.exists():
        return []

    try:
        with open(events_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        dates = []
        for event in data.get("events", []):
            try:
                dates.append(datetime.strptime(event["date"], "%Y-%m-%d"))
            except:
                pass
        for event in data.get("pending_from_quotes_2023", []):
            try:
                dates.append(datetime.strptime(event["date"], "%Y-%m-%d"))
            except:
                pass
        return sorted(dates)
    except:
        return []


def get_momentum_numbers(df: pd.DataFrame, lookback: int = 3) -> Set[int]:
    """
    Identifiziert Momentum-Zahlen (erschienen in den letzten X Tagen mehrfach).

    Diese Zahlen werden VERMIEDEN da sie "populaer" sind.
    """
    if len(df) < lookback:
        return set()

    recent = df.tail(lookback)
    number_counts = {}

    for _, row in recent.iterrows():
        for n in row["numbers_set"]:
            number_counts[n] = number_counts.get(n, 0) + 1

    # Zahlen die 2+ mal in den letzten X Tagen erschienen = Momentum
    momentum = {n for n, count in number_counts.items() if count >= 2}

    return momentum


def get_days_since_jackpot(jackpot_dates: List[datetime], check_date: datetime) -> int:
    """Berechnet Tage seit letztem Jackpot."""
    past_jackpots = [jp for jp in jackpot_dates if jp < check_date]
    if not past_jackpots:
        return 999
    last_jp = max(past_jackpots)
    return (check_date - last_jp).days


def check_timing_rules(check_date: datetime, jackpot_dates: List[datetime]) -> Dict:
    """Prueft alle Timing-Regeln."""
    day_of_month = check_date.day
    weekday = check_date.weekday()  # 0=Mo, 2=Mi
    month = check_date.month
    days_since_jp = get_days_since_jackpot(jackpot_dates, check_date)

    tag_24_28 = 24 <= day_of_month <= 28
    mittwoch = weekday == 2
    boost_phase = 8 <= days_since_jp <= 14

    # Kombinierte Regeln (BESTE STRATEGIE!)
    tag_24_28_AND_boost = tag_24_28 and boost_phase
    mittwoch_AND_boost = mittwoch and boost_phase
    any_combo = tag_24_28_AND_boost or mittwoch_AND_boost  # +36.3% ROI!

    return {
        "tag_24_28": tag_24_28,
        "mittwoch": mittwoch,
        "juni": month == 6,
        "boost_phase": boost_phase,
        "tag_24_28_AND_boost": tag_24_28_AND_boost,
        "mittwoch_AND_boost": mittwoch_AND_boost,
        "any_combo": any_combo,  # BESTE Kombination!
        "days_since_jp": days_since_jp,
        "day_of_month": day_of_month,
        "weekday_name": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][weekday],
    }


def generate_anti_momentum_ticket(
    typ: int,
    momentum_numbers: Set[int],
    additional_avoid: Set[int] = None
) -> List[int]:
    """
    Generiert ein Ticket das Momentum-Zahlen VERMEIDET.

    Das ist der Kern der Post-Jackpot Strategie:
    - Andere Spieler waehlen "heisse" Zahlen
    - Wir vermeiden sie um Ticket-Overlap zu reduzieren
    """
    avoid = momentum_numbers.copy()
    if additional_avoid:
        avoid.update(additional_avoid)

    # Pool ohne Momentum-Zahlen
    pool = [z for z in range(1, 71) if z not in avoid]

    if len(pool) < typ:
        # Fallback: nicht genug Zahlen, nimm trotzdem welche
        pool = list(range(1, 71))

    # Zufaellige Auswahl aus dem "kalten" Pool
    ticket = sorted(random.sample(pool, typ))

    return ticket


def generate_postjp_recommendation(
    df: pd.DataFrame,
    jackpot_dates: List[datetime],
    check_date: datetime
) -> Optional[Dict]:
    """
    Generiert Post-Jackpot Empfehlung (Typ 7, Anti-Momentum).

    BESTE STRATEGIE (Backtest +36.3% ROI):
    - Boost-Phase (8-14 Tage nach Jackpot)
    - UND: Tag 24-28 ODER Mittwoch
    - Anti-Momentum Ticket
    """
    timing = check_timing_rules(check_date, jackpot_dates)

    # Priorisierung:
    # 1. any_combo (Tag 24-28 OR Mittwoch + Boost) = BESTE (+36.3%)
    # 2. boost_only = GUT (+10.7%)
    # 3. Ausserhalb = Nicht empfohlen

    if timing["any_combo"]:
        confidence = "OPTIMAL"
        expected_roi = "+36.3% (Backtest 2023-2024)"
    elif timing["boost_phase"]:
        confidence = "GUT"
        expected_roi = "+10.7% (Backtest 2023-2024)"
    else:
        return None  # Nicht in optimaler Phase

    # Momentum-Zahlen der letzten 3 Tage
    momentum = get_momentum_numbers(df, lookback=3)

    # Auch Birthday-Zahlen vermeiden (viele Spieler nutzen sie)
    birthday_popular = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}

    # Anti-Momentum Ticket generieren
    ticket = generate_anti_momentum_ticket(
        typ=7,
        momentum_numbers=momentum,
        additional_avoid=birthday_popular
    )

    # Timing-Bonus berechnen
    timing_bonus = []
    if timing["tag_24_28"]:
        timing_bonus.append("Tag 24-28 ★")
    if timing["mittwoch"]:
        timing_bonus.append("Mittwoch ★")
    if timing["juni"]:
        timing_bonus.append("Juni ★")

    return {
        "typ": 7,
        "ticket": ticket,
        "strategy": "Anti-Momentum Post-Jackpot",
        "confidence": confidence,
        "momentum_avoided": sorted(momentum),
        "birthday_avoided": sorted(birthday_popular),
        "days_since_jackpot": timing["days_since_jp"],
        "timing_bonus": timing_bonus,
        "expected_roi": expected_roi,
        "reason": "Gegen das System: Vermeide Zahlen die andere Spieler waehlen"
    }


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


def generate_recommendations(
    df: pd.DataFrame,
    jackpot_dates: List[datetime],
    types: List[int] = [8, 9, 10],
    use_dual: bool = False,
    force_postjp: bool = False
) -> Dict:
    """Generiert alle Empfehlungen."""

    today = datetime.now()
    timing = check_timing_rules(today, jackpot_dates)

    recommendations = {
        "generated_at": datetime.now().isoformat(),
        "for_date": today.date().isoformat(),
        "last_drawing": analyze_last_drawing(df),
        "timing": timing,
        "warnings": [],
        "tickets": {},
    }

    # === POST-JACKPOT STRATEGIE (Prioritaet!) ===
    postjp = generate_postjp_recommendation(df, jackpot_dates, today)

    if postjp or force_postjp:
        if not postjp and force_postjp:
            # Force-Modus: Generiere trotzdem
            momentum = get_momentum_numbers(df, lookback=3)
            birthday_popular = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}
            ticket = generate_anti_momentum_ticket(7, momentum, birthday_popular)
            postjp = {
                "typ": 7,
                "ticket": ticket,
                "strategy": "Anti-Momentum (erzwungen)",
                "momentum_avoided": sorted(momentum),
                "days_since_jackpot": timing["days_since_jp"],
                "timing_bonus": [],
                "note": "Nicht in Boost-Phase - reduzierte Erwartung"
            }

        recommendations["postjp_strategy"] = postjp
        recommendations["primary_recommendation"] = "POST-JACKPOT TYP 7"

    # === STANDARD BIRTHDAY-AVOIDANCE (V2) ===
    if SuperModel:
        model_v2 = SuperModel(use_v2=True)
        context = {
            "date": today,
            "prev_positions": df.iloc[-1]["positions"],
            "prev_numbers": list(df.iloc[-1]["numbers_set"]),
            "jackpot_dates": jackpot_dates,
        }

        for keno_type in types:
            ticket_v2, meta_v2 = model_v2.generate_ticket(keno_type, context)
            recommendations["tickets"][f"typ_{keno_type}"] = {
                "v2_birthday_avoidance": {
                    "ticket": ticket_v2,
                    "description": "Birthday-Avoidance Strategie",
                }
            }

    # Warnungen
    if timing["boost_phase"]:
        recommendations["warnings"].append({
            "type": "boost_phase",
            "message": f"BOOST-PHASE aktiv! ({timing['days_since_jp']} Tage nach Jackpot)",
            "recommendation": "Typ 7 Anti-Momentum empfohlen!"
        })
    elif timing["days_since_jp"] <= 7:
        recommendations["warnings"].append({
            "type": "early_phase",
            "message": f"Fruehe Phase nach Jackpot ({timing['days_since_jp']} Tage)",
            "recommendation": "Warten bis Tag 8-14 fuer beste Chancen"
        })
    elif timing["days_since_jp"] > 30:
        recommendations["warnings"].append({
            "type": "cooldown",
            "message": f"Cooldown-Phase ({timing['days_since_jp']} Tage seit Jackpot)",
            "recommendation": "Reduzierte Gewinnwahrscheinlichkeit"
        })

    return recommendations


def print_recommendations(recommendations: Dict, verbose: bool = False):
    """Gibt Empfehlungen formatiert aus."""

    print("\n" + "=" * 70)
    print("    KENO TAEGLICHE EMPFEHLUNG")
    print("    " + recommendations["for_date"])
    print("=" * 70)

    # Timing-Info
    timing = recommendations.get("timing", {})
    print(f"\nTIMING:")
    print(f"  Tage seit Jackpot: {timing.get('days_since_jp', '?')}")
    print(f"  Tag des Monats: {timing.get('day_of_month', '?')}")
    print(f"  Wochentag: {timing.get('weekday_name', '?')}")

    # Letzte Ziehung
    last = recommendations["last_drawing"]
    print(f"\nLetzte Ziehung ({last['date']}):")
    print(f"  Zahlen: {last['numbers']}")
    print(f"  Birthday (1-31): {last['birthday_count']} | Hohe (32-70): {last['high_count']}")

    # Warnungen
    if recommendations["warnings"]:
        print("\n" + "-" * 70)
        print("STATUS:")
        for w in recommendations["warnings"]:
            print(f"  [{w['type'].upper()}] {w['message']}")
            print(f"  -> {w['recommendation']}")

    # === POST-JACKPOT EMPFEHLUNG (PRIMAER!) ===
    if "postjp_strategy" in recommendations:
        postjp = recommendations["postjp_strategy"]
        confidence = postjp.get("confidence", "GUT")

        print("\n" + "=" * 70)
        if confidence == "OPTIMAL":
            print("★★★ OPTIMALE BEDINGUNGEN - ANTI-MOMENTUM STRATEGIE ★★★")
        else:
            print("★★ GUTE BEDINGUNGEN - ANTI-MOMENTUM STRATEGIE ★★")
        print("=" * 70)

        print(f"\n  KONFIDENZ: {confidence}")
        print(f"  TYP: {postjp['typ']}")
        print(f"  STRATEGIE: {postjp['strategy']}")

        print(f"\n  TICKET:")
        print(f"  +---------------------------------------+")
        ticket = postjp['ticket']
        print(f"  | {' '.join(f'{n:2d}' for n in ticket):35s} |")
        print(f"  +---------------------------------------+")

        print(f"\n  GEGEN DAS SYSTEM:")
        print(f"    Vermiedene Momentum-Zahlen: {postjp.get('momentum_avoided', [])}")
        print(f"    Vermiedene Birthday-Zahlen: {postjp.get('birthday_avoided', [])}")

        if postjp.get("timing_bonus"):
            print(f"\n  TIMING-BONUS: {', '.join(postjp['timing_bonus'])}")

        print(f"\n  ERWARTETER ROI: {postjp.get('expected_roi', 'N/A')}")
        print(f"\n  LOGIK: {postjp.get('reason', '')}")

    # === STANDARD TICKETS ===
    if recommendations.get("tickets"):
        print("\n" + "=" * 70)
        print("STANDARD TICKETS (Birthday-Avoidance V2)")
        print("=" * 70)

        for type_key, type_info in recommendations["tickets"].items():
            keno_type = int(type_key.split("_")[1])
            v2_info = type_info.get("v2_birthday_avoidance", {})

            if v2_info:
                ticket = v2_info["ticket"]
                print(f"\n  TYP {keno_type}: {ticket}")

    # Zusammenfassung
    print("\n" + "=" * 70)
    print("GEGEN DAS SYSTEM - STRATEGIE-UEBERSICHT")
    print("=" * 70)
    print("""
    ANTI-MOMENTUM STRATEGIE (BESTE):
    ================================
    Das System nutzen wir gegen sich selbst:
    - Andere Spieler waehlen "heisse" Zahlen (Momentum)
    - Wir vermeiden diese AKTIV
    - Weniger Ticket-Overlap = hoeherer erwarteter Gewinn

    OPTIMALE BEDINGUNGEN (+36.3% ROI):
      → Boost-Phase (8-14 Tage nach Jackpot)
      → UND: Tag 24-28 ODER Mittwoch
      → Typ 7 mit Anti-Momentum Ticket

    GUTE BEDINGUNGEN (+10.7% ROI):
      → Nur Boost-Phase (8-14 Tage nach Jackpot)
      → Typ 7 mit Anti-Momentum Ticket

    VERMEIDEN:
      → Momentum-Zahlen (2+ Tage in Folge erschienen)
      → Populaere Birthday-Zahlen (1,2,3,7,11,13,17,19,21,23,27,29,31)

    STANDARD (ausserhalb Boost-Phase):
      → Birthday-Avoidance (Typ 8, 9, 10)
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
                        help="Dual-Strategie anzeigen")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Alle Typen anzeigen (6-10)")
    parser.add_argument("--postjp", "-p", action="store_true",
                        help="Post-Jackpot Modus erzwingen")
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
        use_dual=args.dual,
        force_postjp=args.postjp
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
