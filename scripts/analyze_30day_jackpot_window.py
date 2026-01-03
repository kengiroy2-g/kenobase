#!/usr/bin/env python3
"""
30-TAGE JACKPOT-FENSTER ANALYSE

ZIEL: Herausfinden ob und wann innerhalb von 30 Tagen ein Typ 6/6
mit dynamisch angepassten Tickets erreichbar ist.

KERNFRAGEN:
1. Nach wie vielen Tagen "stabilisiert" sich der Pool?
2. Welche Signale zeigen an, dass ein Jackpot bevorsteht?
3. Wie kombinieren wir Pool-Konvergenz mit Timing-Regeln?

TIMING-REGELN (aus HYPOTHESEN_SYNTHESE.md):
- FRUEH-Phase: Tag 1-14 des Monats (+364% ROI)
- SPAET-Phase: Tag 15-28 des Monats (-58% ROI)
- Cooldown: 30 Tage nach GK10/10 Jackpot (-66% ROI)
- Boost-Phase: 8-14 Tage nach Jackpot (+36% ROI)

NEUE ERKENNTNISSE:
- Pool eliminiert 61.5% der Nicht-JP-Zahlen (Selektivitaet +3.9%)
- Durchschnittlich 3.06 NEUE Jackpot-Zahlen kommen hinzu
- Top-Events zeigen +85% Selektivitaet

ALGORITHMUS-IDEE:
1. Generiere Pool an Tag 1
2. Tracke taegliche Aenderungen
3. Berechne "Konvergenz-Score" basierend auf:
   - Pool-Stabilitaet (wie viel aendert sich?)
   - Timing (FRUEH/SPAET/Cooldown)
   - Pattern-Qualitaet (weniger BAD_PATTERNS)
4. Wenn Score > Schwelle UND Timing gut → SPIELEN

Autor: Kenobase V2
"""

import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

# ============================================================================
# KONSTANTEN
# ============================================================================

BIRTHDAY_NUMBERS = set(range(1, 32))
NON_BIRTHDAY_NUMBERS = set(range(32, 71))
ALL_NUMBERS = set(range(1, 71))
TOP_20_CORRECTION = {1, 2, 12, 14, 16, 18, 21, 24, 26, 32, 37, 38, 41, 42, 47, 52, 58, 60, 68, 70}

BAD_PATTERNS = {
    "0010010", "1000111", "0101011", "1010000", "0001101",
    "0001000", "0100100", "0001010", "0000111",
}

GOOD_PATTERNS = {
    "0011101", "1010011", "0001001", "1010101", "0010100",
    "1000001", "1000010", "0001011", "0010101",
}


# ============================================================================
# DATEN LADEN
# ============================================================================

def load_keno_data(filepath: Path) -> List[Dict]:
    data = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            try:
                datum_str = row.get("Datum", "").strip()
                if not datum_str:
                    continue
                datum = datetime.strptime(datum_str, "%d.%m.%Y")
                numbers = []
                for i in range(1, 21):
                    col = f"Keno_Z{i}"
                    if col in row and row[col]:
                        numbers.append(int(row[col]))
                if len(numbers) == 20:
                    data.append({"datum": datum, "zahlen": set(numbers)})
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def load_jackpot_dates(base_path: Path) -> List[datetime]:
    """Lade bekannte Jackpot-Daten."""
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
        return sorted(dates)
    except:
        return []


# ============================================================================
# POOL-GENERATOR FUNKTIONEN
# ============================================================================

def get_hot_numbers(draws: List[Dict], lookback: int = 3) -> Set[int]:
    if len(draws) < lookback:
        return set()
    recent = draws[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def get_count(draws: List[Dict], number: int, lookback: int = 30) -> int:
    recent = draws[-lookback:] if len(draws) >= lookback else draws
    return sum(1 for d in recent if number in d["zahlen"])


def get_streak(draws: List[Dict], number: int) -> int:
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


def get_pattern_7(draws: List[Dict], number: int) -> str:
    pattern = ""
    for draw in draws[-7:]:
        pattern += "1" if number in draw["zahlen"] else "0"
    return pattern


def get_avg_gap(draws: List[Dict], number: int, lookback: int = 60) -> float:
    gaps = []
    last_seen = None
    for i, draw in enumerate(draws[-lookback:]):
        if number in draw["zahlen"]:
            if last_seen is not None:
                gaps.append(i - last_seen)
            last_seen = i
    return np.mean(gaps) if gaps else 10.0


def get_index(draws: List[Dict], number: int) -> int:
    for i, draw in enumerate(reversed(draws)):
        if number in draw["zahlen"]:
            return i
    return len(draws)


def score_number_v2(draws: List[Dict], number: int, hot: Set[int]) -> float:
    score = 50.0
    pattern = get_pattern_7(draws, number)
    if pattern in BAD_PATTERNS:
        score -= 20
    elif pattern in GOOD_PATTERNS:
        score += 15
    streak = get_streak(draws, number)
    if streak >= 3:
        score -= 10
    elif streak <= -5:
        score -= 5
    elif 0 < streak <= 2:
        score += 5
    avg_gap = get_avg_gap(draws, number)
    if avg_gap <= 3:
        score += 10
    elif avg_gap > 5:
        score -= 5
    index = get_index(draws, number)
    if index >= 10:
        score -= 5
    elif 3 <= index <= 6:
        score += 5
    ones = pattern.count("1")
    if ones == 2 or ones == 3:
        score += 5
    elif ones >= 5:
        score -= 5
    return score


def build_pool_v2(draws: List[Dict]) -> Tuple[Set[int], Dict]:
    """Generiert Pool mit Detail-Informationen."""
    if len(draws) < 10:
        return set(), {}

    hot = get_hot_numbers(draws, lookback=3)
    cold = ALL_NUMBERS - hot
    cold_birthday = cold & BIRTHDAY_NUMBERS
    cold_nonbd = cold & NON_BIRTHDAY_NUMBERS

    hot_filtered = hot - TOP_20_CORRECTION
    hot_scored = [(z, score_number_v2(draws, z, hot)) for z in hot_filtered]
    hot_scored.sort(key=lambda x: x[1], reverse=True)
    hot_keep = set(z for z, s in hot_scored[:5])

    cold_bd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot))
                      for z in cold_birthday]
    cold_bd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_bd_filtered = [(z, c, s) for z, c, s in cold_bd_scored
                        if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_bd_keep = set(z for z, c, s in cold_bd_filtered[:6])
    if len(cold_bd_keep) < 6:
        remaining = [z for z, c, s in cold_bd_scored if z not in cold_bd_keep]
        cold_bd_keep.update(remaining[:6 - len(cold_bd_keep)])

    cold_nbd_scored = [(z, get_count(draws, z), score_number_v2(draws, z, hot))
                       for z in cold_nonbd]
    cold_nbd_scored.sort(key=lambda x: (x[1], -x[2]))
    cold_nbd_filtered = [(z, c, s) for z, c, s in cold_nbd_scored
                         if get_pattern_7(draws, z) not in BAD_PATTERNS]
    cold_nbd_keep = set(z for z, c, s in cold_nbd_filtered[:6])
    if len(cold_nbd_keep) < 6:
        remaining = [z for z, c, s in cold_nbd_scored if z not in cold_nbd_keep]
        cold_nbd_keep.update(remaining[:6 - len(cold_nbd_keep)])

    pool = hot_keep | cold_bd_keep | cold_nbd_keep

    # Pattern-Qualitaet berechnen
    bad_count = sum(1 for z in pool if get_pattern_7(draws, z) in BAD_PATTERNS)
    good_count = sum(1 for z in pool if get_pattern_7(draws, z) in GOOD_PATTERNS)

    details = {
        "hot_keep": len(hot_keep),
        "cold_bd_keep": len(cold_bd_keep),
        "cold_nbd_keep": len(cold_nbd_keep),
        "bad_patterns": bad_count,
        "good_patterns": good_count,
        "avg_score": np.mean([score_number_v2(draws, z, hot) for z in pool]) if pool else 0,
    }

    return pool, details


# ============================================================================
# TIMING-FUNKTIONEN
# ============================================================================

def get_timing_score(datum: datetime, last_jackpot: Optional[datetime]) -> Dict:
    """Berechnet Timing-Score basierend auf bekannten Regeln."""
    day_of_month = datum.day
    weekday = datum.weekday()  # 0=Mo, 6=So

    score = 50  # Basis
    reasons = []

    # FRUEH vs SPAET Phase
    if day_of_month <= 14:
        score += 20
        reasons.append("FRUEH-Phase (+20)")
    else:
        score -= 15
        reasons.append("SPAET-Phase (-15)")

    # Wochentag (Mittwoch = 2, Samstag = 5)
    if weekday == 2:  # Mittwoch
        score += 10
        reasons.append("Mittwoch (+10)")

    # Jackpot-Timing
    if last_jackpot:
        days_since_jp = (datum - last_jackpot).days
        if 0 <= days_since_jp <= 7:
            score -= 30
            reasons.append(f"Cooldown-Beginn ({days_since_jp}d nach JP, -30)")
        elif 8 <= days_since_jp <= 14:
            score += 25
            reasons.append(f"Boost-Phase ({days_since_jp}d nach JP, +25)")
        elif 15 <= days_since_jp <= 30:
            score -= 10
            reasons.append(f"Cooldown ({days_since_jp}d nach JP, -10)")
        elif days_since_jp > 30:
            score += 5
            reasons.append(f"Post-Cooldown ({days_since_jp}d nach JP, +5)")

    # Tag 24-28 Bonus (aus Anti-Momentum Strategie)
    if 24 <= day_of_month <= 28:
        score += 15
        reasons.append("Tag 24-28 Fenster (+15)")

    return {
        "score": score,
        "reasons": reasons,
        "day_of_month": day_of_month,
        "weekday": weekday,
    }


# ============================================================================
# KONVERGENZ-ANALYSE
# ============================================================================

def analyze_30day_window(draws: List[Dict], start_idx: int, jackpot_dates: List[datetime]) -> Dict:
    """
    Analysiert ein 30-Tage-Fenster ab start_idx.

    Trackt:
    - Taegliche Pool-Aenderungen
    - Konvergenz-Metriken
    - Wann ein 6/6 moeglich gewesen waere
    """
    if start_idx + 30 >= len(draws):
        return None

    window_draws = draws[start_idx:start_idx + 30]
    start_date = window_draws[0]["datum"]

    # Finde letzten Jackpot vor diesem Fenster
    last_jackpot = None
    for jp_date in reversed(jackpot_dates):
        if jp_date < start_date:
            last_jackpot = jp_date
            break

    results = {
        "start_date": start_date,
        "daily_pools": [],
        "convergence_events": [],
        "potential_wins": [],
    }

    prev_pool = None

    for day_offset in range(30):
        current_idx = start_idx + day_offset
        if current_idx >= len(draws):
            break

        # Ziehungen bis gestern (wir wissen ja nicht was heute kommt)
        draws_until_yesterday = draws[:current_idx]
        if len(draws_until_yesterday) < 30:
            continue

        current_date = draws[current_idx]["datum"]
        todays_numbers = draws[current_idx]["zahlen"]

        # Pool generieren
        pool, pool_details = build_pool_v2(draws_until_yesterday)
        if not pool:
            continue

        # Timing-Score
        timing = get_timing_score(current_date, last_jackpot)

        # Pool-Stabilitaet (Jaccard-Index mit gestern)
        stability = 0
        if prev_pool:
            intersection = len(pool & prev_pool)
            union = len(pool | prev_pool)
            stability = intersection / union if union > 0 else 0

        # Treffer heute
        hits = pool & todays_numbers
        hit_count = len(hits)

        # 6er-Kombinationen aus Pool die 6/6 waeren
        potential_6_6 = 0
        if hit_count >= 6:
            # Zaehle wie viele 6er-Kombis aus dem Pool 6/6 treffen wuerden
            pool_list = list(pool)
            for combo in combinations(pool_list, 6):
                if set(combo) <= todays_numbers:
                    potential_6_6 += 1

        # Konvergenz-Score berechnen
        convergence_score = (
            pool_details["avg_score"] * 0.3 +
            (1 - pool_details["bad_patterns"] / 17) * 30 +
            pool_details["good_patterns"] * 5 +
            stability * 20 +
            timing["score"] * 0.5
        )

        day_result = {
            "day": day_offset + 1,
            "date": current_date.strftime("%d.%m.%Y"),
            "weekday": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][current_date.weekday()],
            "pool_size": len(pool),
            "pool": sorted(pool),
            "hits": hit_count,
            "hit_numbers": sorted(hits),
            "stability": round(stability, 3),
            "timing_score": timing["score"],
            "timing_reasons": timing["reasons"],
            "convergence_score": round(convergence_score, 1),
            "potential_6_6": potential_6_6,
            "bad_patterns": pool_details["bad_patterns"],
            "good_patterns": pool_details["good_patterns"],
        }

        results["daily_pools"].append(day_result)

        # Markiere potentielle Gewinn-Tage
        if potential_6_6 > 0:
            results["potential_wins"].append({
                "day": day_offset + 1,
                "date": current_date.strftime("%d.%m.%Y"),
                "combinations_6_6": potential_6_6,
                "convergence_score": convergence_score,
                "timing_score": timing["score"],
            })

        # Markiere Konvergenz-Events (hoher Score)
        if convergence_score >= 70 and timing["score"] >= 50:
            results["convergence_events"].append({
                "day": day_offset + 1,
                "date": current_date.strftime("%d.%m.%Y"),
                "score": convergence_score,
                "reason": "Hohe Konvergenz + gutes Timing",
            })

        prev_pool = pool

    return results


def find_6_6_events(draws: List[Dict]) -> List[Dict]:
    """Finde alle Tage wo ein Pool >= 6 Treffer hatte."""
    events = []
    for i in range(40, len(draws)):
        draws_until = draws[:i]
        pool, _ = build_pool_v2(draws_until)
        if not pool:
            continue
        hits = pool & draws[i]["zahlen"]
        if len(hits) >= 6:
            events.append({
                "index": i,
                "date": draws[i]["datum"],
                "hits": len(hits),
                "pool_size": len(pool),
            })
    return events


# ============================================================================
# HAUPT-ANALYSE
# ============================================================================

def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    print("=" * 100)
    print("30-TAGE JACKPOT-FENSTER ANALYSE")
    print("Ziel: Wann ist der optimale Zeitpunkt fuer Typ 6/6?")
    print("=" * 100)

    draws = load_keno_data(keno_path)
    jackpot_dates = load_jackpot_dates(base_path)

    print(f"\nGeladene Ziehungen: {len(draws)}")
    print(f"Bekannte Jackpots: {len(jackpot_dates)}")
    print(f"Zeitraum: {draws[0]['datum'].strftime('%d.%m.%Y')} - {draws[-1]['datum'].strftime('%d.%m.%Y')}")

    # Finde alle 6/6 Events
    print("\n" + "-" * 100)
    print("PHASE 1: Identifiziere alle Tage mit Pool >= 6 Treffer")
    print("-" * 100)

    six_six_events = find_6_6_events(draws)
    print(f"\nGefunden: {len(six_six_events)} Tage mit >= 6 Treffern")

    # Analysiere 30-Tage-Fenster VOR jedem 6/6 Event
    print("\n" + "-" * 100)
    print("PHASE 2: Analysiere 30-Tage-Fenster vor 6/6 Events")
    print("-" * 100)

    detailed_analyses = []
    convergence_stats = defaultdict(list)

    # Nimm Stichprobe von Events (jedes 10.)
    sample_events = six_six_events[::10][:50]  # Max 50 Events

    for event in sample_events:
        # Starte Analyse 30 Tage vor dem Event
        start_idx = max(40, event["index"] - 30)
        analysis = analyze_30day_window(draws, start_idx, jackpot_dates)

        if analysis and analysis["daily_pools"]:
            # Finde den Tag an dem das 6/6 Event war
            event_day = event["index"] - start_idx + 1

            # Sammle Statistiken
            for day_result in analysis["daily_pools"]:
                if day_result["day"] <= event_day:
                    days_before = event_day - day_result["day"]
                    convergence_stats[days_before].append({
                        "convergence": day_result["convergence_score"],
                        "timing": day_result["timing_score"],
                        "stability": day_result["stability"],
                        "hits": day_result["hits"],
                        "potential_6_6": day_result["potential_6_6"],
                    })

            detailed_analyses.append({
                "event_date": event["date"].strftime("%d.%m.%Y"),
                "event_day_in_window": event_day,
                "analysis": analysis,
            })

    # Aggregierte Statistiken
    print("\n" + "=" * 100)
    print("AGGREGIERTE STATISTIKEN: Metriken nach Tagen vor 6/6 Event")
    print("=" * 100)

    print(f"\n{'Tage vor 6/6':>15} {'Konvergenz':>12} {'Timing':>10} {'Stabilitaet':>12} {'Treffer':>10} {'6/6 moegl.':>12}")
    print("-" * 75)

    days_sorted = sorted(convergence_stats.keys())
    optimal_days = []

    for days_before in days_sorted[:20]:  # Zeige nur erste 20 Tage
        stats = convergence_stats[days_before]
        avg_conv = np.mean([s["convergence"] for s in stats])
        avg_timing = np.mean([s["timing"] for s in stats])
        avg_stab = np.mean([s["stability"] for s in stats])
        avg_hits = np.mean([s["hits"] for s in stats])
        pct_6_6 = sum(1 for s in stats if s["potential_6_6"] > 0) / len(stats) * 100

        print(f"{days_before:>15} {avg_conv:>12.1f} {avg_timing:>10.1f} {avg_stab:>12.3f} {avg_hits:>10.1f} {pct_6_6:>11.1f}%")

        if avg_conv >= 65 and avg_timing >= 50 and pct_6_6 >= 20:
            optimal_days.append(days_before)

    # Identifiziere optimale Spiel-Tage
    print("\n" + "=" * 100)
    print("OPTIMALE SPIEL-FENSTER")
    print("=" * 100)

    if optimal_days:
        print(f"\nTage mit hoher Konvergenz + gutem Timing + >20% 6/6-Chance:")
        print(f"  {optimal_days}")
    else:
        print("\nKeine eindeutigen optimalen Tage gefunden.")

    # Detaillierte Analyse eines Beispiel-Events
    print("\n" + "=" * 100)
    print("DETAIL-BEISPIEL: Ein 30-Tage-Fenster vor 6/6")
    print("=" * 100)

    if detailed_analyses:
        example = detailed_analyses[0]
        print(f"\n6/6 Event: {example['event_date']} (Tag {example['event_day_in_window']} im Fenster)")
        print()

        print(f"{'Tag':>4} {'Datum':>12} {'WT':>3} {'Pool':>5} {'Hits':>5} {'Stab':>6} {'Conv':>6} {'Time':>6} {'6/6':>5} Status")
        print("-" * 85)

        for day in example["analysis"]["daily_pools"]:
            is_event = day["day"] == example["event_day_in_window"]
            status = "← 6/6!" if is_event else ""

            # Markiere gute Spieltage
            if day["convergence_score"] >= 65 and day["timing_score"] >= 50:
                status = status or "★ SPIELEN"
            elif day["potential_6_6"] > 0:
                status = status or f"({day['potential_6_6']} Kombis)"

            print(f"{day['day']:>4} {day['date']:>12} {day['weekday']:>3} "
                  f"{day['pool_size']:>5} {day['hits']:>5} {day['stability']:>6.2f} "
                  f"{day['convergence_score']:>6.1f} {day['timing_score']:>6} {day['potential_6_6']:>5} {status}")

        # Zeige potentielle Gewinne
        if example["analysis"]["potential_wins"]:
            print(f"\nPotentielle 6/6 Tage in diesem Fenster:")
            for win in example["analysis"]["potential_wins"]:
                print(f"  Tag {win['day']} ({win['date']}): {win['combinations_6_6']} Kombinationen moeglich")

    # Algorithmus-Empfehlung
    print("\n" + "=" * 100)
    print("ALGORITHMUS-EMPFEHLUNG")
    print("=" * 100)

    print("""
SPIELEN wenn ALLE Bedingungen erfuellt:

1. KONVERGENZ-SCORE >= 65
   - Pool-Qualitaet hoch (wenig BAD_PATTERNS)
   - Stabilitaet >= 0.7 (Pool aendert sich wenig)
   - Durchschnitts-Score der Zahlen hoch

2. TIMING-SCORE >= 50
   - FRUEH-Phase (Tag 1-14) ODER
   - Tag 24-28 des Monats ODER
   - Boost-Phase (8-14 Tage nach Jackpot)
   - Mittwoch bevorzugt

3. POOL-STABILITAET >= 0.7
   - Pool hat sich 2+ Tage kaum geaendert
   - Zeigt "Konvergenz" an

NICHT SPIELEN wenn:
   - SPAET-Phase (Tag 15-23) ohne anderen Bonus
   - Cooldown (0-7 Tage nach Jackpot)
   - Konvergenz < 60
   - Pool sehr instabil (Stabilitaet < 0.5)

TICKET-STRATEGIE:
   - Aus Pool (17 Zahlen) 6er-Kombinationen bilden
   - Maximal 20-30 Kombinationen pro Spieltag
   - Fokus auf Zahlen mit GOOD_PATTERNS
""")

    # Export Ergebnisse
    export = {
        "total_6_6_events": len(six_six_events),
        "analyzed_windows": len(detailed_analyses),
        "convergence_by_days_before": {
            str(k): {
                "avg_convergence": float(np.mean([s["convergence"] for s in v])),
                "avg_timing": float(np.mean([s["timing"] for s in v])),
                "pct_6_6_possible": float(sum(1 for s in v if s["potential_6_6"] > 0) / len(v) * 100),
            }
            for k, v in convergence_stats.items()
        },
        "optimal_days_before_6_6": optimal_days,
    }

    results_path = base_path / "results" / "30day_jackpot_window_analysis.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse gespeichert: {results_path}")


if __name__ == "__main__":
    main()
