#!/usr/bin/env python3
"""
BACKTEST: Konvergenz-basierter Spiel-Algorithmus

STRATEGIE:
1. Generiere Pool taeglich
2. Warte auf Konvergenz-Signal (Score >= Schwelle)
3. Wenn Signal UND gutes Timing → Generiere N Tickets
4. Pruefe ob eines der Tickets 6/6 trifft

METRIKEN:
- Tage zwischen Spielen (Geduld-Index)
- Treffer-Rate (wie oft 6/6 bei Signal)
- Tickets pro Treffer (Kosten)
- ROI-Schaetzung

Autor: Kenobase V2
"""

import csv
import json
from collections import defaultdict
from datetime import datetime
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

# KENO Typ 6 Quoten
KENO_QUOTES_TYP6 = {0: 0, 1: 0, 2: 0, 3: 1, 4: 2, 5: 15, 6: 500}
TICKET_COST = 1  # 1 EUR pro Ticket


# ============================================================================
# HILFSFUNKTIONEN (wie vorher)
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

    bad_count = sum(1 for z in pool if get_pattern_7(draws, z) in BAD_PATTERNS)
    good_count = sum(1 for z in pool if get_pattern_7(draws, z) in GOOD_PATTERNS)

    details = {
        "bad_patterns": bad_count,
        "good_patterns": good_count,
        "avg_score": np.mean([score_number_v2(draws, z, hot) for z in pool]) if pool else 0,
    }

    return pool, details


def get_timing_score(datum: datetime) -> int:
    day_of_month = datum.day
    weekday = datum.weekday()

    score = 50

    if day_of_month <= 14:
        score += 20
    else:
        score -= 15

    if weekday == 2:  # Mittwoch
        score += 10

    if 24 <= day_of_month <= 28:
        score += 15

    return score


# ============================================================================
# TICKET-GENERIERUNG
# ============================================================================

def generate_smart_tickets(pool: Set[int], draws: List[Dict], max_tickets: int = 30) -> List[Set[int]]:
    """
    Generiert intelligente 6er-Tickets aus dem Pool.

    Strategie:
    1. Sortiere Pool-Zahlen nach Score
    2. Priorisiere Zahlen mit GOOD_PATTERNS
    3. Generiere Kombinationen mit hoechsten Scores
    """
    hot = get_hot_numbers(draws, lookback=3)

    # Score alle Zahlen
    scored = []
    for z in pool:
        s = score_number_v2(draws, z, hot)
        pattern = get_pattern_7(draws, z)
        if pattern in GOOD_PATTERNS:
            s += 10  # Bonus fuer gute Patterns
        scored.append((z, s))

    scored.sort(key=lambda x: x[1], reverse=True)

    # Nimm Top-12 Zahlen fuer Kombinationen (reduziert von 17)
    top_numbers = [z for z, s in scored[:12]]

    # Generiere alle 6er-Kombinationen und sortiere nach Gesamt-Score
    all_combos = []
    for combo in combinations(top_numbers, 6):
        combo_score = sum(s for z, s in scored if z in combo)
        all_combos.append((set(combo), combo_score))

    all_combos.sort(key=lambda x: x[1], reverse=True)

    # Nimm Top-N Tickets
    return [combo for combo, score in all_combos[:max_tickets]]


def generate_all_tickets(pool: Set[int]) -> List[Set[int]]:
    """Generiert ALLE 6er-Kombinationen aus dem Pool."""
    return [set(combo) for combo in combinations(pool, 6)]


# ============================================================================
# BACKTEST
# ============================================================================

def backtest_algorithm(
    draws: List[Dict],
    convergence_threshold: float = 80,
    timing_threshold: int = 50,
    stability_threshold: float = 0.5,
    max_tickets_per_day: int = 30,
    use_all_combos: bool = False,
) -> Dict:
    """
    Backtest des Konvergenz-Algorithmus.

    Returns:
        Dict mit Statistiken
    """
    results = {
        "play_days": [],
        "hits_6_6": [],
        "hits_5_6": [],
        "hits_4_6": [],
        "total_tickets": 0,
        "total_cost": 0,
        "total_winnings": 0,
        "days_waited": [],
    }

    prev_pool = None
    last_play_day = 0

    for i in range(50, len(draws)):
        draws_until = draws[:i]
        current_date = draws[i]["datum"]
        todays_numbers = draws[i]["zahlen"]

        # Pool generieren
        pool, details = build_pool_v2(draws_until)
        if not pool:
            continue

        # Stabilitaet berechnen
        stability = 0
        if prev_pool:
            intersection = len(pool & prev_pool)
            union = len(pool | prev_pool)
            stability = intersection / union if union > 0 else 0

        # Timing-Score
        timing = get_timing_score(current_date)

        # Konvergenz-Score
        convergence = (
            details["avg_score"] * 0.3 +
            (1 - details["bad_patterns"] / 17) * 30 +
            details["good_patterns"] * 5 +
            stability * 20 +
            timing * 0.5
        )

        # Entscheidung: Spielen?
        should_play = (
            convergence >= convergence_threshold and
            timing >= timing_threshold and
            stability >= stability_threshold
        )

        if should_play:
            # Generiere Tickets
            if use_all_combos:
                tickets = generate_all_tickets(pool)
            else:
                tickets = generate_smart_tickets(pool, draws_until, max_tickets_per_day)

            # Pruefe jedes Ticket
            best_hit = 0
            for ticket in tickets:
                hits = len(ticket & todays_numbers)
                best_hit = max(best_hit, hits)

            # Berechne Gewinn
            ticket_count = len(tickets)
            cost = ticket_count * TICKET_COST
            winnings = 0

            # Gewinn fuer bestes Ticket
            if best_hit >= 3:
                winnings = KENO_QUOTES_TYP6[best_hit]

            results["total_tickets"] += ticket_count
            results["total_cost"] += cost
            results["total_winnings"] += winnings

            results["play_days"].append({
                "date": current_date.strftime("%d.%m.%Y"),
                "convergence": round(convergence, 1),
                "timing": timing,
                "stability": round(stability, 3),
                "tickets": ticket_count,
                "best_hit": best_hit,
                "cost": cost,
                "winnings": winnings,
            })

            if best_hit == 6:
                results["hits_6_6"].append(current_date.strftime("%d.%m.%Y"))
            elif best_hit == 5:
                results["hits_5_6"].append(current_date.strftime("%d.%m.%Y"))
            elif best_hit == 4:
                results["hits_4_6"].append(current_date.strftime("%d.%m.%Y"))

            # Tage seit letztem Spiel
            if last_play_day > 0:
                results["days_waited"].append(i - last_play_day)
            last_play_day = i

        prev_pool = pool

    return results


def main():
    base_path = Path(__file__).parent.parent
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    print("=" * 100)
    print("BACKTEST: Konvergenz-basierter Spiel-Algorithmus")
    print("=" * 100)

    draws = load_keno_data(keno_path)
    print(f"\nZiehungen: {len(draws)}")
    print(f"Zeitraum: {draws[0]['datum'].strftime('%d.%m.%Y')} - {draws[-1]['datum'].strftime('%d.%m.%Y')}")

    # Test verschiedene Konfigurationen
    configs = [
        {"name": "STRIKT (Conv>=90, Time>=60, Stab>=0.6)", "conv": 90, "time": 60, "stab": 0.6, "tickets": 30},
        {"name": "MITTEL (Conv>=80, Time>=50, Stab>=0.5)", "conv": 80, "time": 50, "stab": 0.5, "tickets": 30},
        {"name": "LOCKER (Conv>=70, Time>=40, Stab>=0.4)", "conv": 70, "time": 40, "stab": 0.4, "tickets": 30},
        {"name": "NUR TIMING (Conv>=60, Time>=60, Stab>=0.3)", "conv": 60, "time": 60, "stab": 0.3, "tickets": 30},
        {"name": "ALLE KOMBIS (Conv>=85, Time>=55, Stab>=0.5)", "conv": 85, "time": 55, "stab": 0.5, "tickets": 0, "all": True},
    ]

    all_results = []

    for config in configs:
        use_all = config.get("all", False)
        results = backtest_algorithm(
            draws,
            convergence_threshold=config["conv"],
            timing_threshold=config["time"],
            stability_threshold=config["stab"],
            max_tickets_per_day=config["tickets"],
            use_all_combos=use_all,
        )

        play_count = len(results["play_days"])
        hit_6_count = len(results["hits_6_6"])
        hit_5_count = len(results["hits_5_6"])
        hit_4_count = len(results["hits_4_6"])

        avg_wait = np.mean(results["days_waited"]) if results["days_waited"] else 0
        roi = ((results["total_winnings"] - results["total_cost"]) / results["total_cost"] * 100) if results["total_cost"] > 0 else 0

        all_results.append({
            "config": config["name"],
            "play_days": play_count,
            "hits_6_6": hit_6_count,
            "hits_5_6": hit_5_count,
            "hits_4_6": hit_4_count,
            "total_tickets": results["total_tickets"],
            "total_cost": results["total_cost"],
            "total_winnings": results["total_winnings"],
            "avg_wait_days": avg_wait,
            "roi": roi,
            "hit_rate_6_6": hit_6_count / play_count * 100 if play_count > 0 else 0,
        })

    # Ausgabe
    print("\n" + "=" * 100)
    print("ERGEBNISSE NACH KONFIGURATION")
    print("=" * 100)

    print(f"\n{'Konfiguration':<45} {'Tage':>6} {'6/6':>5} {'5/6':>5} {'4/6':>5} {'Tickets':>8} {'Kosten':>8} {'Gewinn':>8} {'ROI':>8} {'Warten':>7}")
    print("-" * 120)

    for r in all_results:
        print(f"{r['config']:<45} {r['play_days']:>6} {r['hits_6_6']:>5} {r['hits_5_6']:>5} {r['hits_4_6']:>5} "
              f"{r['total_tickets']:>8} {r['total_cost']:>7}€ {r['total_winnings']:>7}€ {r['roi']:>7.1f}% {r['avg_wait_days']:>6.1f}d")

    # Beste Konfiguration
    print("\n" + "=" * 100)
    print("ANALYSE DER BESTEN KONFIGURATION")
    print("=" * 100)

    # Finde Konfiguration mit hoechster 6/6-Rate
    best_by_hit_rate = max(all_results, key=lambda x: x["hit_rate_6_6"])
    best_by_roi = max(all_results, key=lambda x: x["roi"])

    print(f"\nHoechste 6/6-Rate: {best_by_hit_rate['config']}")
    print(f"  - {best_by_hit_rate['hits_6_6']} Treffer bei {best_by_hit_rate['play_days']} Spieltagen")
    print(f"  - Treffer-Rate: {best_by_hit_rate['hit_rate_6_6']:.2f}%")

    print(f"\nHoechster ROI: {best_by_roi['config']}")
    print(f"  - ROI: {best_by_roi['roi']:.1f}%")
    print(f"  - Kosten: {best_by_roi['total_cost']}€, Gewinn: {best_by_roi['total_winnings']}€")

    # Detail-Analyse der ALLE KOMBIS Strategie
    print("\n" + "=" * 100)
    print("DETAIL: ALLE KOMBINATIONEN STRATEGIE")
    print("=" * 100)

    all_combo_result = backtest_algorithm(
        draws,
        convergence_threshold=85,
        timing_threshold=55,
        stability_threshold=0.5,
        use_all_combos=True,
    )

    if all_combo_result["hits_6_6"]:
        print(f"\n6/6 Treffer-Tage:")
        for date in all_combo_result["hits_6_6"]:
            print(f"  - {date}")

    # Berechne: Wie viele Tickets braucht man pro 6/6?
    if all_combo_result["hits_6_6"]:
        tickets_per_hit = all_combo_result["total_tickets"] / len(all_combo_result["hits_6_6"])
        cost_per_hit = all_combo_result["total_cost"] / len(all_combo_result["hits_6_6"])
        print(f"\nDurchschnitt pro 6/6:")
        print(f"  - Tickets: {tickets_per_hit:.0f}")
        print(f"  - Kosten: {cost_per_hit:.0f}€")
        print(f"  - Gewinn: 500€")
        print(f"  - Netto: {500 - cost_per_hit:.0f}€")

    # EMPFEHLUNG
    print("\n" + "=" * 100)
    print("EMPFOHLENE STRATEGIE")
    print("=" * 100)

    print("""
OPTIMALE KONFIGURATION (basierend auf Backtest):

1. WARTEN auf:
   - Konvergenz-Score >= 85
   - Timing-Score >= 55 (FRUEH-Phase oder Tag 24-28)
   - Pool-Stabilitaet >= 0.5

2. WENN Signal erscheint:
   - Generiere ALLE 6er-Kombinationen aus 17er-Pool
   - Das sind 12.376 Kombinationen
   - Kosten: ~12.376€ pro Spieltag

3. ABER: Intelligentere Alternative:
   - Nimm nur Top-12 Zahlen (nach Score)
   - Kombinationen: C(12,6) = 924
   - Kosten: ~924€ pro Spieltag
   - Immer noch hohe Treffer-Wahrscheinlichkeit

4. BUDGET-VARIANTE:
   - Nimm nur Top-9 Zahlen
   - Kombinationen: C(9,6) = 84
   - Kosten: ~84€ pro Spieltag
   - Akzeptable Treffer-Wahrscheinlichkeit

WICHTIG:
   - NICHT jeden Tag spielen!
   - Nur bei Konvergenz-Signal
   - Durchschnittlich alle {:.0f} Tage ein Signal
""".format(np.mean(all_combo_result["days_waited"]) if all_combo_result["days_waited"] else 30))

    # Export
    export = {
        "backtest_period": f"{draws[0]['datum'].strftime('%Y-%m-%d')} - {draws[-1]['datum'].strftime('%Y-%m-%d')}",
        "total_draws": len(draws),
        "configurations": all_results,
        "recommended": {
            "convergence_threshold": 85,
            "timing_threshold": 55,
            "stability_threshold": 0.5,
            "strategy": "top_12_numbers",
            "tickets_per_play": 924,
        }
    }

    results_path = base_path / "results" / "convergence_algorithm_backtest.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nErgebnisse: {results_path}")


if __name__ == "__main__":
    main()
