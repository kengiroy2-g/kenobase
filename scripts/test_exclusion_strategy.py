#!/usr/bin/env python3
"""
NEUE STRATEGIE: Zahlen ausschliessen statt vorhersagen.

Paradigmenwechsel:
- Nicht: "Welche Zahlen werden gezogen?"
- Sondern: "Welche Zahlen wird das System KORRIGIEREN (nicht ziehen)?"

Methode:
1. Finde Zahlen/Muster die das System wahrscheinlich korrigiert
2. Schliesse diese aus dem Pool aus
3. Waehle Tickets aus dem REDUZIERTEN Pool
4. Durch kleineren Pool = bessere Trefferchance
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from random import sample, seed
from typing import Dict, List, Set, Tuple

BIRTHDAY_POPULAR = {1, 2, 3, 7, 11, 13, 17, 19, 21, 23, 27, 29, 31}


def load_keno_data(filepath: Path) -> List[Dict]:
    """Laedt KENO-Ziehungsdaten."""
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
                    data.append({
                        "datum": datum,
                        "datum_str": datum_str,
                        "zahlen": set(numbers),
                    })
            except Exception:
                continue
    return sorted(data, key=lambda x: x["datum"])


def get_momentum_numbers(draws: List[Dict], target_date: datetime, lookback: int = 3) -> Set[int]:
    """Holt Momentum-Zahlen (HOT)."""
    relevant = [d for d in draws if d["datum"] < target_date]
    if len(relevant) < lookback:
        return set()
    recent = relevant[-lookback:]
    counts = defaultdict(int)
    for draw in recent:
        for z in draw["zahlen"]:
            counts[z] += 1
    return {z for z, c in counts.items() if c >= 2}


def calculate_index(draws: List[Dict], target_idx: int, zahl: int) -> int:
    """Berechnet Index (letzte 20 Tage)."""
    lookback_20 = draws[max(0, target_idx-20):target_idx]
    return sum(1 if zahl in d["zahlen"] else -1 for d in lookback_20)


def identify_correction_candidates(
    draws: List[Dict],
    target_idx: int,
    pool: Set[int]
) -> Tuple[Set[int], Dict]:
    """
    Identifiziert Zahlen die wahrscheinlich vom System KORRIGIERT werden.

    Korrektur-Kriterien (basierend auf unseren Analysen):
    1. HOT + Birthday = wird korrigiert (zu populaer)
    2. Hoher Index (> -3) + steigender Trend = wird korrigiert
    3. In vielen starken Tripeln = wird korrigiert
    """
    corrections = {}

    # Berechne Metriken fuer jede Zahl
    momentum = get_momentum_numbers(draws, draws[target_idx]["datum"], lookback=3)

    # Pre-Phase fuer Trend
    pre_start_idx = max(0, target_idx - 14)

    for z in pool:
        score = 0
        reasons = []

        # Aktueller Index
        current_idx = calculate_index(draws, target_idx, z)

        # Index vor 14 Tagen
        past_idx = calculate_index(draws, pre_start_idx, z)
        trend = current_idx - past_idx

        is_hot = z in momentum
        is_birthday = z in BIRTHDAY_POPULAR

        # Kriterium 1: HOT + Birthday
        if is_hot and is_birthday:
            score += 3
            reasons.append("HOT+Birthday")

        # Kriterium 2: Hoher Index + steigender Trend
        if current_idx > -4 and trend > 3:
            score += 2
            reasons.append(f"HighIdx({current_idx:+d})+RisingTrend({trend:+d})")

        # Kriterium 3: Nur HOT (auch ohne Birthday)
        if is_hot:
            score += 1
            reasons.append("HOT")

        # Kriterium 4: Sehr hoher Index (nahe 0 oder positiv)
        if current_idx >= 0:
            score += 2
            reasons.append(f"VeryHighIdx({current_idx:+d})")
        elif current_idx > -3:
            score += 1
            reasons.append(f"HighIdx({current_idx:+d})")

        corrections[z] = {
            "score": score,
            "reasons": reasons,
            "index": current_idx,
            "trend": trend,
            "is_hot": is_hot,
            "is_birthday": is_birthday,
        }

    # Zahlen mit Score >= 3 werden ausgeschlossen
    to_exclude = {z for z, data in corrections.items() if data["score"] >= 3}

    return to_exclude, corrections


def test_exclusion_strategy(
    draws: List[Dict],
    stichtag: datetime,
    test_end: datetime,
    exclusion_threshold: int = 3
):
    """Testet die Ausschluss-Strategie."""

    # Finde Indizes
    stichtag_idx = next(i for i, d in enumerate(draws) if d["datum"] >= stichtag)

    # Voller Pool (1-70)
    full_pool = set(range(1, 71))

    # Birthday + Momentum Pool (wie bisher)
    momentum = get_momentum_numbers(draws, stichtag, lookback=3)
    standard_pool = BIRTHDAY_POPULAR | momentum

    # Identifiziere Korrektur-Kandidaten
    to_exclude, corrections = identify_correction_candidates(draws, stichtag_idx, full_pool)

    # Reduzierter Pool: Alle Zahlen AUSSER Korrektur-Kandidaten
    reduced_pool = full_pool - to_exclude

    # Test-Ziehungen
    test_draws = [d for d in draws if stichtag <= d["datum"] <= test_end]

    return {
        "stichtag": stichtag,
        "test_days": len(test_draws),
        "full_pool_size": len(full_pool),
        "standard_pool_size": len(standard_pool),
        "excluded_count": len(to_exclude),
        "reduced_pool_size": len(reduced_pool),
        "to_exclude": to_exclude,
        "reduced_pool": reduced_pool,
        "corrections": corrections,
        "test_draws": test_draws,
    }


def evaluate_exclusion(result: Dict):
    """Evaluiert wie gut die Ausschluss-Strategie funktioniert hat."""

    test_draws = result["test_draws"]
    to_exclude = result["to_exclude"]
    reduced_pool = result["reduced_pool"]

    # Zaehle wie oft ausgeschlossene Zahlen NICHT gezogen wurden
    exclusion_success = []

    for draw in test_draws:
        drawn = draw["zahlen"]
        excluded_drawn = to_exclude & drawn
        excluded_not_drawn = to_exclude - drawn

        # Erfolgsrate: Wie viele der ausgeschlossenen wurden NICHT gezogen?
        if to_exclude:
            success_rate = len(excluded_not_drawn) / len(to_exclude)
            exclusion_success.append(success_rate)

    avg_exclusion_success = sum(exclusion_success) / len(exclusion_success) if exclusion_success else 0

    # Erwartung: Bei Zufall werden 50/70 = 71.4% NICHT gezogen
    expected_not_drawn = 50 / 70

    # Wie viele Zahlen aus dem reduzierten Pool werden pro Tag gezogen?
    reduced_hits = []
    for draw in test_draws:
        hits = len(reduced_pool & draw["zahlen"])
        reduced_hits.append(hits)

    avg_reduced_hits = sum(reduced_hits) / len(reduced_hits) if reduced_hits else 0
    expected_reduced_hits = len(reduced_pool) * 20 / 70

    return {
        "avg_exclusion_success": avg_exclusion_success,
        "expected_not_drawn": expected_not_drawn,
        "exclusion_improvement": (avg_exclusion_success - expected_not_drawn) / expected_not_drawn * 100,
        "avg_reduced_hits": avg_reduced_hits,
        "expected_reduced_hits": expected_reduced_hits,
        "reduced_hits_improvement": (avg_reduced_hits - expected_reduced_hits) / expected_reduced_hits * 100,
    }


def build_tickets_from_reduced_pool(reduced_pool: Set[int], n_tickets: int = 10) -> List[List[int]]:
    """Baut Tickets aus dem reduzierten Pool."""
    pool_list = sorted(reduced_pool)

    # Verschiedene Strategien
    tickets = []

    # Einfach die ersten 6/7
    tickets.append(("First6", pool_list[:6]))
    tickets.append(("First7", pool_list[:7]))

    # Zufaellige Auswahl (mehrere)
    seed(42)
    for i in range(3):
        tickets.append((f"Random6_{i+1}", sorted(sample(pool_list, 6))))
        tickets.append((f"Random7_{i+1}", sorted(sample(pool_list, 7))))

    return tickets


def main():
    print("=" * 100)
    print("AUSSCHLUSS-STRATEGIE: Korrigierte Zahlen eliminieren")
    print("=" * 100)

    base_path = Path("C:/Users/kenfu/Documents/keno_base")
    keno_path = base_path / "data/raw/keno/KENO_ab_2022_bereinigt.csv"

    draws = load_keno_data(keno_path)
    print(f"Ziehungen geladen: {len(draws)}")

    # Test verschiedene Stichtage
    test_cases = [
        (datetime(2025, 2, 1), datetime(2025, 7, 31)),
        (datetime(2025, 3, 1), datetime(2025, 7, 31)),
        (datetime(2025, 4, 1), datetime(2025, 7, 31)),
        (datetime(2025, 5, 1), datetime(2025, 7, 31)),
    ]

    all_results = []

    for stichtag, test_end in test_cases:
        print(f"\n{'='*100}")
        print(f"STICHTAG: {stichtag.date()}")
        print(f"{'='*100}")

        result = test_exclusion_strategy(draws, stichtag, test_end)
        evaluation = evaluate_exclusion(result)

        print(f"\n  Pool-Groessen:")
        print(f"    Voll (1-70):     {result['full_pool_size']}")
        print(f"    Ausgeschlossen:  {result['excluded_count']} Zahlen")
        print(f"    Reduziert:       {result['reduced_pool_size']} Zahlen")

        print(f"\n  Ausgeschlossene Zahlen: {sorted(result['to_exclude'])}")

        # Zeige Gruende fuer Ausschluss
        print(f"\n  Ausschluss-Gruende:")
        for z in sorted(result['to_exclude']):
            c = result['corrections'][z]
            print(f"    {z:>2}: Score={c['score']}, {', '.join(c['reasons'])}")

        print(f"\n  EVALUATION ({result['test_days']} Test-Tage):")
        print(f"    Ausschluss-Erfolg: {evaluation['avg_exclusion_success']*100:.1f}% nicht gezogen")
        print(f"    Erwartung (Zufall): {evaluation['expected_not_drawn']*100:.1f}%")
        print(f"    Verbesserung: {evaluation['exclusion_improvement']:+.1f}%")

        print(f"\n    Treffer im reduzierten Pool: {evaluation['avg_reduced_hits']:.2f}/Tag")
        print(f"    Erwartung: {evaluation['expected_reduced_hits']:.2f}/Tag")
        print(f"    Verbesserung: {evaluation['reduced_hits_improvement']:+.1f}%")

        all_results.append({
            "stichtag": stichtag,
            "result": result,
            "evaluation": evaluation,
        })

    # === ZUSAMMENFASSUNG ===
    print(f"\n\n{'='*100}")
    print("ZUSAMMENFASSUNG UEBER ALLE STICHTAGE")
    print(f"{'='*100}")

    avg_exclusion_improvement = sum(r['evaluation']['exclusion_improvement'] for r in all_results) / len(all_results)
    avg_hits_improvement = sum(r['evaluation']['reduced_hits_improvement'] for r in all_results) / len(all_results)

    print(f"\n  Durchschnittliche Ausschluss-Verbesserung: {avg_exclusion_improvement:+.1f}%")
    print(f"  Durchschnittliche Treffer-Verbesserung:    {avg_hits_improvement:+.1f}%")

    # === TICKETS TESTEN ===
    print(f"\n\n{'='*100}")
    print("TICKET-TEST: Reduzierter Pool vs. Standard")
    print(f"{'='*100}")

    # Nimm den ersten Stichtag
    result = all_results[0]['result']
    test_draws = result['test_draws']
    reduced_pool = result['reduced_pool']

    # Baue Tickets
    tickets = build_tickets_from_reduced_pool(reduced_pool)

    print(f"\n  Tickets aus reduziertem Pool ({len(reduced_pool)} Zahlen):")

    for name, ticket in tickets:
        ticket_set = set(ticket)
        typ = len(ticket)
        hits = [len(ticket_set & d["zahlen"]) for d in test_draws]
        avg_hits = sum(hits) / len(hits)
        expected = typ * 20 / 70
        diff_pct = (avg_hits / expected - 1) * 100
        jackpots = sum(1 for h in hits if h == typ)
        near_miss = sum(1 for h in hits if h == typ - 1)

        print(f"    {name:<12}: {ticket} → {avg_hits:.2f} Treffer ({diff_pct:+.1f}%), JP:{jackpots}, NM:{near_miss}")

    # === THEORETISCHE VERBESSERUNG ===
    print(f"\n\n{'='*100}")
    print("THEORETISCHE VERBESSERUNG DURCH POOL-REDUKTION")
    print(f"{'='*100}")

    # Wenn wir von 70 auf X Zahlen reduzieren, verbessern sich die Odds
    full_pool = 70
    reduced = len(reduced_pool)

    # Fuer Typ 6: C(n,6) Kombinationen
    from math import comb

    full_combos_6 = comb(full_pool, 6)
    reduced_combos_6 = comb(reduced, 6)
    improvement_6 = (1 - reduced_combos_6 / full_combos_6) * 100

    full_combos_7 = comb(full_pool, 7)
    reduced_combos_7 = comb(reduced, 7)
    improvement_7 = (1 - reduced_combos_7 / full_combos_7) * 100

    print(f"\n  Pool-Reduktion: {full_pool} → {reduced} Zahlen ({full_pool - reduced} ausgeschlossen)")
    print(f"\n  Typ 6:")
    print(f"    Voller Pool:     {full_combos_6:,} moegliche 6er-Kombis")
    print(f"    Reduzierter Pool: {reduced_combos_6:,} moegliche 6er-Kombis")
    print(f"    Reduktion:       {improvement_6:.1f}% weniger Kombinationen")

    print(f"\n  Typ 7:")
    print(f"    Voller Pool:     {full_combos_7:,} moegliche 7er-Kombis")
    print(f"    Reduzierter Pool: {reduced_combos_7:,} moegliche 7er-Kombis")
    print(f"    Reduktion:       {improvement_7:.1f}% weniger Kombinationen")

    print(f"\n[Analyse abgeschlossen]")


if __name__ == "__main__":
    main()
