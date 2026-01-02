"""
Vorhersage der Gewinner fuer Pending Jackpots.

Nutzt die erkannten Muster:
1. Universelle Constraints (Ziffernprodukt, Dekaden, etc.)
2. Jackpot-Muster (wenig Birthday, hohe Zahlen bevorzugt)
3. Ueberrepräsentierte Zahlen an Jackpot-Tagen
"""

from itertools import combinations
import json
import numpy as np
from pathlib import Path
from datetime import datetime


# Überrepräsentierte Zahlen an Jackpot-Tagen (aus Analyse)
JACKPOT_FAVORITES = {43, 51, 52, 36, 40, 19, 38, 4, 61, 69, 62, 13, 8, 35, 45}
JACKPOT_AVOID = {1, 16, 21, 27, 29, 37, 67, 25, 68, 28}


def ziffernprodukt_mod9(combo: list[int]) -> int:
    produkt = 1
    for z in combo:
        for d in str(z):
            if d != '0':
                produkt *= int(d)
    return produkt % 9


def count_einstellig(combo: list[int]) -> int:
    return sum(1 for z in combo if z <= 9)


def count_dekaden_besetzt(combo: list[int]) -> int:
    return len(set(z // 10 for z in combo))


def alle_drittel_besetzt(combo: list[int]) -> bool:
    return (any(1 <= z <= 23 for z in combo) and
            any(24 <= z <= 46 for z in combo) and
            any(47 <= z <= 70 for z in combo))


def count_zeilen_besetzt(combo: list[int]) -> int:
    return len(set((z - 1) // 10 for z in combo))


def count_endziffer_1(combo: list[int]) -> int:
    return sum(1 for z in combo if z % 10 == 1)


def passes_constraints(combo: list[int]) -> bool:
    """Universelle Constraints."""
    if ziffernprodukt_mod9(combo) != 0:
        return False
    if count_einstellig(combo) != 1:
        return False
    if count_dekaden_besetzt(combo) != 6:
        return False
    if not alle_drittel_besetzt(combo):
        return False
    if count_zeilen_besetzt(combo) != 6:
        return False
    if count_endziffer_1(combo) > 0:
        return False
    return True


def calculate_jackpot_score(candidate: set[int], drawn_20: set[int]) -> dict:
    """
    Berechnet Score basierend auf Jackpot-Mustern.

    Hoeherer Score = wahrscheinlicherer Gewinner.
    """
    other_10 = drawn_20 - candidate

    # 1. Birthday-Vermeidung (weniger Birthday im Gewinner = besser)
    birthday_winner = sum(1 for z in candidate if z <= 31)
    birthday_score = (10 - birthday_winner) / 10.0  # 0-1, mehr = besser

    # 2. Hohe Zahlen im Gewinner (mehr >50 = besser)
    high_winner = sum(1 for z in candidate if z > 50)
    high_score = high_winner / 10.0

    # 3. Jackpot-Favorites im Gewinner
    favorites_in_winner = len(candidate & JACKPOT_FAVORITES)
    favorites_score = favorites_in_winner / 10.0

    # 4. Jackpot-Avoid NICHT im Gewinner
    avoid_in_winner = len(candidate & JACKPOT_AVOID)
    avoid_score = (10 - avoid_in_winner) / 10.0

    # 5. Birthday in Andere 10 (mehr = besser, System will kleine Gewinne)
    birthday_other = sum(1 for z in other_10 if z <= 31)
    birthday_other_score = birthday_other / 10.0

    # 6. Summe des Gewinners (höher = besser, basierend auf Analyse)
    summe = sum(candidate)
    summe_score = (summe - 200) / 300.0  # Normalisiert ~0.3-0.7

    # Gewichteter Gesamtscore
    total_score = (
        birthday_score * 2.0 +      # Birthday-Vermeidung wichtig
        high_score * 1.5 +          # Hohe Zahlen wichtig
        favorites_score * 1.0 +     # Jackpot-Favorites
        avoid_score * 1.0 +         # Avoid-Zahlen vermeiden
        birthday_other_score * 1.5 + # Birthday in Andere
        summe_score * 0.5           # Summe
    ) / 7.5

    return {
        'total_score': total_score,
        'birthday_winner': birthday_winner,
        'high_winner': high_winner,
        'favorites_in_winner': favorites_in_winner,
        'avoid_in_winner': avoid_in_winner,
        'birthday_other': birthday_other,
        'summe': summe,
    }


def predict_winner(drawn_20: list[int], event_id: str) -> dict:
    """Vorhersage für einen Jackpot-Tag."""

    drawn_set = set(drawn_20)

    print(f"\n{'='*70}")
    print(f"VORHERSAGE: {event_id}")
    print(f"{'='*70}")
    print(f"20 gezogene Zahlen: {sorted(drawn_20)}")

    # 1. Generiere Kandidaten
    candidates = []
    for combo in combinations(sorted(drawn_20), 10):
        if passes_constraints(list(combo)):
            candidates.append(set(combo))

    print(f"Kandidaten nach Constraints: {len(candidates):,}")

    if not candidates:
        print("FEHLER: Keine Kandidaten!")
        return None

    # 2. Score berechnen
    scored = []
    for candidate in candidates:
        metrics = calculate_jackpot_score(candidate, drawn_set)
        scored.append({
            'candidate': sorted(candidate),
            'other_10': sorted(drawn_set - candidate),
            **metrics
        })

    # 3. Sortieren nach Score
    scored.sort(key=lambda x: x['total_score'], reverse=True)

    # 4. Output
    print(f"\n{'Rang':>4} {'Score':>8} {'BD-W':>6} {'High':>6} {'Fav':>5} {'Avoid':>6} {'BD-O':>6}")
    print("-" * 50)

    for i, c in enumerate(scored[:10]):
        print(f"{i+1:>4} {c['total_score']:>8.3f} {c['birthday_winner']:>6} "
              f"{c['high_winner']:>6} {c['favorites_in_winner']:>5} "
              f"{c['avoid_in_winner']:>6} {c['birthday_other']:>6}")

    # Top-3 Detail
    print(f"\n--- TOP-3 KANDIDATEN ---")
    for i, c in enumerate(scored[:3]):
        print(f"\n#{i+1} (Score: {c['total_score']:.3f})")
        print(f"  Gewinner:  {c['candidate']}")
        print(f"  Andere 10: {c['other_10']}")
        print(f"  Birthday im Gewinner: {c['birthday_winner']}/10")
        print(f"  Hohe (>50) im Gewinner: {c['high_winner']}/10")

    return {
        'event_id': event_id,
        'drawn_20': sorted(drawn_20),
        'total_candidates': len(candidates),
        'top_10': scored[:10],
        'best_prediction': scored[0]['candidate'],
    }


def main():
    print("=" * 70)
    print("VORHERSAGE FUER PENDING JACKPOTS (2023)")
    print("=" * 70)
    print("""
Methode:
- Universelle Constraints (reduziert auf ~3.000-28.000 Kandidaten)
- Jackpot-Muster-Score:
  * Weniger Birthday im Gewinner = besser
  * Mehr hohe Zahlen = besser
  * Jackpot-Favorites im Gewinner = besser
  * Jackpot-Avoid vermeiden = besser
""")

    base_path = Path("C:/Users/kenfu/Documents/keno_base")

    # Lade Pending Events
    events_path = base_path / "AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json"
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    pending = data.get("pending_from_quotes_2023", [])

    print(f"\nPending Jackpots: {len(pending)}")

    results = []

    for event in pending:
        event_id = event["id"]
        drawn_20 = event["drawn_20"]
        winners = event.get("total_winners", 1)

        print(f"\n{'#'*70}")
        print(f"# {event_id} ({winners} Gewinner)")
        print(f"{'#'*70}")

        result = predict_winner(drawn_20, event_id)
        if result:
            result['total_winners'] = winners
            results.append(result)

    # Zusammenfassung
    print(f"\n\n{'='*70}")
    print("ZUSAMMENFASSUNG ALLER VORHERSAGEN")
    print(f"{'='*70}")

    print(f"\n{'Event':<25} {'Kandidaten':>12} {'Top-1 Score':>12} {'Top-1 BD':>10}")
    print("-" * 65)

    for r in results:
        top1 = r['top_10'][0]
        print(f"{r['event_id']:<25} {r['total_candidates']:>12,} "
              f"{top1['total_score']:>12.3f} {top1['birthday_winner']:>10}/10")

    # Speichern
    output = {
        "analyse": "Pending Jackpot Vorhersagen",
        "methode": "Universelle Constraints + Jackpot-Muster-Score",
        "datum": datetime.now().isoformat(),
        "jackpot_favorites": list(JACKPOT_FAVORITES),
        "jackpot_avoid": list(JACKPOT_AVOID),
        "vorhersagen": results,
    }

    output_path = base_path / "results/pending_jackpot_predictions.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Besondere Events hervorheben
    print(f"\n{'='*70}")
    print("BESONDERE EVENTS")
    print(f"{'='*70}")

    for r in results:
        if r['total_winners'] >= 10:
            print(f"\n*** {r['event_id']} ({r['total_winners']} GEWINNER!) ***")
            print(f"Top-Vorhersage: {r['best_prediction']}")

    return results


if __name__ == "__main__":
    main()
