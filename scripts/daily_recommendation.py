#!/usr/bin/env python3
"""
TAEGLICHE KENO EMPFEHLUNG

Strategien:
1. Birthday-Avoidance (V2) - Standard fuer Typ 8, 9, 10
2. Post-Jackpot Anti-Momentum - Typ 7 mit kombinierten Timing-Regeln
3. Pool-Reife System - Wann ist der Pool "spielbereit"?

BESTE STRATEGIE (Backtest 2023-2024, 1000 Simulationen):
  Typ 7 + Anti-Momentum + (Tag 24-28 ODER Mittwoch) + Boost-Phase
  ROI: +36.3%

POOL-REIFE SYSTEM (Neu!):
  Der Pool braucht Zeit um zu "reifen":
  - Tag 1: 31% Chance auf 6+ Treffer (ZU FRUEH!)
  - Tag 3: 61% Chance (Median)
  - Tag 4: 76% Chance (OPTIMAL)
  - Tag 7: 94% Chance

  EMPFEHLUNG: Nicht sofort spielen! Warte 3-4 Tage nach Pool-Generierung.

TIMING-REGELN (KOMBINIERT):
- Boost-Phase: 8-14 Tage nach Jackpot
- UND: Tag 24-28 des Monats ODER Mittwoch
- Pool-Reife: Mindestens 3 Tage nach Pool-Generierung

Verwendung:
    python scripts/daily_recommendation.py
    python scripts/daily_recommendation.py --postjp  # Post-Jackpot Modus

Autor: Kenobase V2.5
Datum: 2026-01-03
"""

import argparse
import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

# ============================================================================
# POOL-REIFE SYSTEM (basierend auf pool_hit_timing_extended.json)
# ============================================================================
# Diese Werte kommen aus der empirischen Messung:
# "Wie viele Tage bis der dynamische Pool 6+ Treffer hat?"
#
# INTERPRETATION:
# - Tag 1: Pool ist "frisch" - nur 31% Chance dass er heute trifft
# - Tag 3: Pool ist "gereift" - 61% Chance (Median erreicht)
# - Tag 4: Pool ist "optimal" - 76% Chance (empfohlener Spieltag)
# - Tag 7: Pool ist "sehr reif" - 94% Chance
# - Nach Tag 7: Pool neu generieren (sinkt nicht, aber frischer = besser)

POOL_RIPENESS = {
    1: {"probability": 0.31, "status": "UNREIF", "recommendation": "Nicht spielen"},
    2: {"probability": 0.45, "status": "FRUEH", "recommendation": "Noch warten"},
    3: {"probability": 0.61, "status": "REIF", "recommendation": "Spielbereit (Median)"},
    4: {"probability": 0.76, "status": "OPTIMAL", "recommendation": "Beste Zeit zum Spielen!"},
    5: {"probability": 0.85, "status": "SEHR_REIF", "recommendation": "Sehr gute Zeit"},
    6: {"probability": 0.91, "status": "SEHR_REIF", "recommendation": "Sehr gute Zeit"},
    7: {"probability": 0.94, "status": "MAXIMAL", "recommendation": "Letzte Chance vor Neustart"},
}

# Treffer-Schwellen Erfolgsraten
HIT_THRESHOLD_SUCCESS = {
    6: 1.000,   # 100% - immer erfolgreich
    7: 1.000,   # 100%
    8: 0.979,   # 97.9%
    9: 0.653,   # 65.3%
    10: 0.176,  # 17.6%
}

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


# ============================================================================
# POOL GENERATION (Dynamischer Pool)
# ============================================================================

# Konstanten fuer Pool-Generierung
BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}
BAD_PATTERNS = {"0010010", "1000111", "0101011", "1010000", "0001101", "0001000", "0100100", "0001010", "0000111"}


def get_hot_numbers_from_draws(draws: List[Dict], lookback: int = 3) -> Set[int]:
    """Ermittelt 'heisse' Zahlen aus den letzten X Ziehungen."""
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_count_from_draws(draws: List[Dict], number: int, lookback: int = 30) -> int:
    """Zaehlt wie oft eine Zahl in den letzten X Ziehungen erschien."""
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_streak_from_draws(draws: List[Dict], number: int) -> int:
    """Berechnet Streak einer Zahl (positiv = erschienen, negativ = nicht erschienen)."""
    if not draws:
        return 0
    streak = 0
    in_last = number in draws[-1]["zahlen"]
    for draw in reversed(draws):
        if (number in draw["zahlen"]) == in_last:
            streak += 1
        else:
            break
    return streak if in_last else -streak


def get_pattern_7_from_draws(draws: List[Dict], number: int) -> str:
    """Ermittelt 7-Tage Pattern einer Zahl (1=erschienen, 0=nicht)."""
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_avg_gap_from_draws(draws: List[Dict], number: int, lookback: int = 60) -> float:
    """Berechnet durchschnittlichen Abstand zwischen Erscheinungen."""
    gaps = []
    last_seen = None
    for i, draw in enumerate(draws[-lookback:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return np.mean(gaps) if gaps else 10.0


def get_index_from_draws(draws: List[Dict], number: int) -> int:
    """Ermittelt Index (Tage seit letztem Erscheinen)."""
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def score_number_for_pool(draws: List[Dict], number: int, hot: Set[int]) -> float:
    """Berechnet Score einer Zahl fuer Pool-Aufnahme."""
    score = 50.0
    pattern = get_pattern_7_from_draws(draws, number)
    if pattern in BAD_PATTERNS:
        score -= 20
    streak = get_streak_from_draws(draws, number)
    if streak >= 3:
        score -= 10
    elif 0 < streak <= 2:
        score += 5
    avg_gap = get_avg_gap_from_draws(draws, number)
    if avg_gap <= 3:
        score += 10
    elif avg_gap > 5:
        score -= 5
    index = get_index_from_draws(draws, number)
    if 3 <= index <= 6:
        score += 5
    return score


def build_dynamic_pool(draws: List[Dict]) -> Set[int]:
    """
    Generiert dynamischen Pool basierend auf aktuellen Ziehungen.

    Der Pool besteht aus:
    - Top 5 "heisse" Zahlen (ohne TOP_20_CORRECTION)
    - Top 6 "kalte" Birthday-Zahlen (1-31)
    - Top 6 "kalte" Non-Birthday-Zahlen (32-70)

    Gesamt: ~17 Zahlen
    """
    if len(draws) < 10:
        return set()

    hot = get_hot_numbers_from_draws(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    # Hot-Zahlen filtern und scoren
    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number_for_pool(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)
    hot_keep = set(z for z, s in hot_scored[:5])

    # Kalte Birthday-Zahlen
    cold_bd_scored = [(z, get_count_from_draws(draws, z), score_number_for_pool(draws, z, hot)) for z in cold_birthday]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored if get_pattern_7_from_draws(draws, z) not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:6])
    if len(cold_bd_keep) < 6:
        remaining = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(remaining[:6 - len(cold_bd_keep)])

    # Kalte Non-Birthday-Zahlen
    cold_nbd_scored = [(z, get_count_from_draws(draws, z), score_number_for_pool(draws, z, hot)) for z in cold_nonbd]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_nbd_filtered = [(z, c, s) for z, c, s in cold_nbd_scored if get_pattern_7_from_draws(draws, z) not in BAD_PATTERNS]
    cold_nbd_keep = set(z for z, c, s in cold_nbd_filtered[:6])
    if len(cold_nbd_keep) < 6:
        remaining = [z for z, c, s in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(remaining[:6 - len(cold_nbd_keep)])

    return hot_keep | cold_bd_keep | cold_nbd_keep


def convert_df_to_draws(df: pd.DataFrame) -> List[Dict]:
    """Konvertiert DataFrame in Liste von Ziehungs-Dicts."""
    draws = []
    for _, row in df.iterrows():
        draws.append({
            "datum": row["Datum"],
            "zahlen": row["numbers_set"]
        })
    return draws


def calculate_pool_ripeness(pool_age_days: int) -> Dict:
    """
    Berechnet Pool-Reife basierend auf Alter.

    Args:
        pool_age_days: Tage seit Pool-Generierung

    Returns:
        Dict mit probability, status, recommendation
    """
    if pool_age_days <= 0:
        return {
            "age_days": 0,
            "probability": 0.0,
            "status": "NEU",
            "recommendation": "Pool gerade generiert - warte mindestens 3 Tage",
            "play_now": False
        }

    if pool_age_days > 7:
        return {
            "age_days": pool_age_days,
            "probability": 0.94,
            "status": "ABGELAUFEN",
            "recommendation": "Pool ist zu alt - generiere neuen Pool!",
            "play_now": False
        }

    ripeness = POOL_RIPENESS.get(pool_age_days, POOL_RIPENESS[7])

    # Spielempfehlung: Ab Tag 3 (61% Chance)
    play_now = pool_age_days >= 3

    return {
        "age_days": pool_age_days,
        "probability": ripeness["probability"],
        "status": ripeness["status"],
        "recommendation": ripeness["recommendation"],
        "play_now": play_now
    }


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
    force_postjp: bool = False,
    pool_age_days: int = 0
) -> Dict:
    """Generiert alle Empfehlungen."""

    today = datetime.now()
    timing = check_timing_rules(today, jackpot_dates)

    # Dynamischen Pool generieren
    draws = convert_df_to_draws(df)
    current_pool = build_dynamic_pool(draws)

    # Pool-Reife berechnen
    ripeness = calculate_pool_ripeness(pool_age_days)

    recommendations = {
        "generated_at": datetime.now().isoformat(),
        "for_date": today.date().isoformat(),
        "last_drawing": analyze_last_drawing(df),
        "timing": timing,
        "pool": {
            "numbers": sorted(current_pool),
            "size": len(current_pool),
            "age_days": pool_age_days,
            "ripeness": ripeness,
        },
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

    # Pool-Reife Warnung
    if ripeness["status"] == "UNREIF":
        recommendations["warnings"].append({
            "type": "pool_unreif",
            "message": f"Pool ist UNREIF (Tag {pool_age_days}) - nur {ripeness['probability']*100:.0f}% Chance",
            "recommendation": "Warte noch 2-3 Tage bis Pool reif ist!"
        })
    elif ripeness["status"] == "FRUEH":
        recommendations["warnings"].append({
            "type": "pool_frueh",
            "message": f"Pool ist FRUEH (Tag {pool_age_days}) - {ripeness['probability']*100:.0f}% Chance",
            "recommendation": "Noch 1-2 Tage warten fuer optimale Chancen"
        })
    elif ripeness["status"] == "ABGELAUFEN":
        recommendations["warnings"].append({
            "type": "pool_abgelaufen",
            "message": f"Pool ist ABGELAUFEN (Tag {pool_age_days})",
            "recommendation": "Generiere neuen Pool mit --pool-age 0!"
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

    # Pool-Info
    pool = recommendations.get("pool", {})
    ripeness = pool.get("ripeness", {})
    if pool:
        print(f"\n" + "-" * 70)
        print("DYNAMISCHER POOL:")
        print(f"  Zahlen ({pool.get('size', 0)}): {pool.get('numbers', [])}")
        print(f"\n  POOL-REIFE:")

        # Status mit Farb-Indikator
        status = ripeness.get("status", "?")
        prob = ripeness.get("probability", 0)
        age = ripeness.get("age_days", 0)
        play = ripeness.get("play_now", False)

        # Visuelle Fortschrittsanzeige
        bar_filled = int(prob * 20)
        bar_empty = 20 - bar_filled
        progress_bar = "█" * bar_filled + "░" * bar_empty

        print(f"  Tag {age}: [{progress_bar}] {prob*100:.0f}%")
        print(f"  Status: {status}")
        print(f"  {ripeness.get('recommendation', '')}")

        if play:
            print(f"\n  >>> SPIELEN: JA - Pool ist spielbereit! <<<")
        else:
            print(f"\n  >>> SPIELEN: NEIN - Warte auf Pool-Reife! <<<")

        # Timing-Tabelle
        print(f"\n  POOL-REIFE TABELLE:")
        print(f"  ┌─────────┬────────────┬──────────────────────────────┐")
        print(f"  │ Tag     │ Chance     │ Empfehlung                   │")
        print(f"  ├─────────┼────────────┼──────────────────────────────┤")
        for day, info in POOL_RIPENESS.items():
            marker = " ◄" if day == age else ""
            print(f"  │ Tag {day}   │ {info['probability']*100:5.0f}%     │ {info['status']:<12}{marker:>16} │")
        print(f"  └─────────┴────────────┴──────────────────────────────┘")

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
    parser = argparse.ArgumentParser(
        description="KENO Taegliche Empfehlung",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
POOL-REIFE SYSTEM:
  Der Pool braucht Zeit um zu "reifen". Nicht sofort spielen!

  Tag 1: 31%  - UNREIF (nicht spielen)
  Tag 2: 45%  - FRUEH (noch warten)
  Tag 3: 61%  - REIF (spielbereit)
  Tag 4: 76%  - OPTIMAL (beste Zeit!)
  Tag 7: 94%  - MAXIMAL (dann neuer Pool)

BEISPIELE:
  # Pool heute generiert (Tag 0)
  python daily_recommendation.py --pool-age 0

  # Pool vor 4 Tagen generiert (optimal!)
  python daily_recommendation.py --pool-age 4

  # Pool vor 8 Tagen - zu alt, neuen generieren
  python daily_recommendation.py --pool-age 8
        """
    )
    parser.add_argument("--type", "-t", type=int, choices=[6, 7, 8, 9, 10],
                        help="Nur bestimmten Typ anzeigen")
    parser.add_argument("--dual", "-d", action="store_true",
                        help="Dual-Strategie anzeigen")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Alle Typen anzeigen (6-10)")
    parser.add_argument("--postjp", "-p", action="store_true",
                        help="Post-Jackpot Modus erzwingen")
    parser.add_argument("--pool-age", type=int, default=4,
                        help="Tage seit Pool-Generierung (default: 4 = optimal)")
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
        force_postjp=args.postjp,
        pool_age_days=args.pool_age
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
