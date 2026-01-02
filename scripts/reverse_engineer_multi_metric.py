"""
Reverse Engineering mit MULTI-METRIK Ansatz.

Statt nur Popularitaet: Kombiniere mehrere Metriken zu einem Score.
"""

from itertools import combinations
from collections import Counter
import json
import numpy as np
from pathlib import Path


def get_popularity_score(zahl: int) -> float:
    """Berechnet Popularitaets-Score fuer eine Zahl (0-1)."""
    score = 0.0
    if 1 <= zahl <= 31:
        score += 0.4
    if 1 <= zahl <= 12:
        score += 0.2
    if zahl in [7, 3, 9, 13, 21]:
        score += 0.3
    if zahl % 10 == 0:
        score += 0.15
    score += 0.3 * (70 - zahl) / 69
    if zahl >= 60 and zahl not in [60, 66, 69, 70]:
        score -= 0.1
    return max(0.0, min(1.0, score))


# CONSTRAINT FUNCTIONS
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


def count_konsekutive(combo: list[int]) -> int:
    """Zaehlt konsekutive Paare."""
    s = sorted(combo)
    return sum(1 for i in range(len(s)-1) if s[i+1] - s[i] == 1)


def passes_constraints(combo: list[int]) -> bool:
    """Prueft alle bekannten Constraints."""
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


def calculate_multi_score(
    candidate: set[int],
    other_10: set[int],
    weights: dict = None
) -> dict:
    """
    Berechnet Multi-Metrik Score fuer einen Kandidaten.

    Metriken:
    1. other_popularity: Hohe Popularitaet in "Andere 10" = gut
    2. winner_unpopularity: Niedrige Popularitaet in Gewinner = gut
    3. winner_high_numbers: Viele hohe Zahlen im Gewinner = gut
    4. birthday_avoidance: Wenig Birthday im Gewinner = gut
    5. spread: Grosse Streuung im Gewinner = gut
    6. low_consecutive: Wenig konsekutive Paare = gut
    """
    if weights is None:
        weights = {
            'other_popularity': 1.0,
            'winner_unpopularity': 1.0,
            'winner_high_numbers': 0.5,
            'birthday_avoidance': 1.5,
            'spread': 0.3,
            'low_consecutive': 0.5,
        }

    # 1. Other Popularity (normiert 0-1)
    other_pop = np.mean([get_popularity_score(z) for z in other_10])

    # 2. Winner Unpopularity (invertiert)
    winner_pop = np.mean([get_popularity_score(z) for z in candidate])
    winner_unpop = 1.0 - winner_pop

    # 3. High Numbers in Winner (>50)
    high_count = sum(1 for z in candidate if z > 50)
    high_ratio = high_count / 10.0

    # 4. Birthday Avoidance (invertiert)
    birthday_in_winner = sum(1 for z in candidate if z <= 31)
    birthday_avoidance = 1.0 - (birthday_in_winner / 10.0)

    # 5. Spread (normiert)
    candidate_list = sorted(candidate)
    spread = (max(candidate) - min(candidate)) / 69.0

    # 6. Low Consecutive
    konsek = count_konsekutive(list(candidate))
    low_konsek = 1.0 - (konsek / 5.0)  # Max 5 konsekutive moeglich

    # Gewichteter Score
    total_weight = sum(weights.values())
    score = (
        weights['other_popularity'] * other_pop +
        weights['winner_unpopularity'] * winner_unpop +
        weights['winner_high_numbers'] * high_ratio +
        weights['birthday_avoidance'] * birthday_avoidance +
        weights['spread'] * spread +
        weights['low_consecutive'] * low_konsek
    ) / total_weight

    return {
        'score': score,
        'other_popularity': other_pop,
        'winner_unpopularity': winner_unpop,
        'high_numbers': high_count,
        'birthday_in_winner': birthday_in_winner,
        'spread': max(candidate) - min(candidate),
        'consecutive': konsek,
    }


def reverse_engineer_multi(drawn_20: list[int], known_winner: list[int] = None) -> dict:
    """
    Reverse Engineering mit Multi-Metrik Ansatz.
    """
    drawn_set = set(drawn_20)

    print(f"\n{'='*70}")
    print("REVERSE ENGINEERING: MULTI-METRIK ANSATZ")
    print(f"{'='*70}")
    print(f"\n20 gezogene Zahlen: {sorted(drawn_20)}")

    if known_winner:
        print(f"Bekannter Gewinner: {sorted(known_winner)}")

    # 1. Generiere Kandidaten
    print(f"\nGeneriere Kandidaten...")
    candidates = []
    for combo in combinations(sorted(drawn_20), 10):
        if passes_constraints(list(combo)):
            candidates.append(set(combo))

    print(f"Anzahl Kandidaten nach Constraints: {len(candidates):,}")

    if not candidates:
        print("FEHLER: Keine Kandidaten gefunden!")
        return None

    # 2. Score fuer jeden Kandidaten
    print(f"Berechne Multi-Metrik Score...")

    candidates_scored = []
    for candidate in candidates:
        other_10 = drawn_set - candidate
        metrics = calculate_multi_score(candidate, other_10)

        candidates_scored.append({
            "candidate": sorted(candidate),
            "other_10": sorted(other_10),
            **metrics
        })

    # 3. Sortiere nach Score (absteigend)
    candidates_scored.sort(key=lambda x: x["score"], reverse=True)

    # 4. Output
    print(f"\n{'='*70}")
    print("TOP-10 KANDIDATEN (MULTI-METRIK)")
    print(f"{'='*70}")

    print(f"\n{'Rang':>4} {'Score':>8} {'OthPop':>8} {'Birthday':>10} {'High':>6} {'Konsek':>8}")
    print("-" * 70)

    for i, c in enumerate(candidates_scored[:10]):
        is_winner = ""
        if known_winner and set(c["candidate"]) == set(known_winner):
            is_winner = " *** GEWINNER ***"

        print(f"{i+1:>4} {c['score']:>8.4f} {c['other_popularity']:>8.3f} "
              f"{c['birthday_in_winner']:>10} {c['high_numbers']:>6} "
              f"{c['consecutive']:>8}{is_winner}")

    # Top-3 Detail
    print(f"\n{'='*70}")
    print("TOP-3 KANDIDATEN IM DETAIL")
    print(f"{'='*70}")

    for i, c in enumerate(candidates_scored[:3]):
        is_winner = " *** ECHTER GEWINNER ***" if known_winner and set(c["candidate"]) == set(known_winner) else ""
        print(f"\n#{i+1}{is_winner}")
        print(f"  Kandidat: {c['candidate']}")
        print(f"  Andere:   {c['other_10']}")
        print(f"  Multi-Score: {c['score']:.4f}")
        print(f"    - Other Popularity: {c['other_popularity']:.3f}")
        print(f"    - Winner Unpopularity: {c['winner_unpopularity']:.3f}")
        print(f"    - Birthday in Winner: {c['birthday_in_winner']}/10")
        print(f"    - High Numbers (>50): {c['high_numbers']}/10")

    # 5. Validation
    winner_rank = None
    if known_winner:
        known_set = set(known_winner)
        for i, c in enumerate(candidates_scored):
            if set(c["candidate"]) == known_set:
                winner_rank = i + 1
                break

        print(f"\n{'='*70}")
        print("VALIDIERUNG")
        print(f"{'='*70}")

        if winner_rank:
            percentile = (1 - winner_rank / len(candidates_scored)) * 100
            print(f"\nBekannter Gewinner auf Rang: #{winner_rank} von {len(candidates_scored)}")
            print(f"Percentile: Top {100 - percentile:.1f}%")

            if winner_rank <= 10:
                print(f"\n  ✓ ERFOLG! Gewinner in Top-10")
            elif winner_rank <= len(candidates_scored) * 0.1:
                print(f"\n  ✓ GUT! Gewinner in Top-10%")
            elif winner_rank <= len(candidates_scored) * 0.25:
                print(f"\n  ~ MODERAT. Gewinner in Top-25%")
            else:
                print(f"\n  ✗ SCHWACH. Gewinner nicht in Top-25%")

    return {
        "drawn_20": sorted(drawn_20),
        "known_winner": sorted(known_winner) if known_winner else None,
        "total_candidates": len(candidates_scored),
        "top_10": candidates_scored[:10],
        "winner_rank": winner_rank,
    }


def main():
    """Teste Multi-Metrik Ansatz auf allen bekannten Jackpots."""

    print("=" * 70)
    print("MULTI-METRIK REVERSE ENGINEERING")
    print("=" * 70)
    print("""
Kombiniert mehrere Faktoren:
- Popularitaet der 'Anderen 10'
- Unpopularitaet des Gewinners
- Birthday-Vermeidung im Gewinner
- Hohe Zahlen im Gewinner
- Spread und Konsekutive
""")

    # Lade Events
    events_path = Path("C:/Users/kenfu/Documents/keno_base/AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json")

    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    for event in data["events"]:
        print(f"\n\n{'#'*70}")
        print(f"# TEST: {event.get('city', event['id'])}")
        print(f"{'#'*70}")

        result = reverse_engineer_multi(
            event["drawn_20"],
            event["winner_10"]
        )
        result["event_id"] = event["id"]
        result["city"] = event.get("city", "Unknown")
        results.append(result)

    # Zusammenfassung
    print(f"\n\n{'='*70}")
    print("GESAMTZUSAMMENFASSUNG: MULTI-METRIK")
    print(f"{'='*70}")

    print(f"\n{'Event':<20} {'Kandidaten':>12} {'Rang':>10} {'Erfolg':>12}")
    print("-" * 60)

    success_count = 0
    for r in results:
        if r["winner_rank"]:
            percentile = (1 - r["winner_rank"] / r["total_candidates"]) * 100
            if r["winner_rank"] <= 10:
                success = "TOP-10"
                success_count += 1
            elif percentile >= 90:
                success = "TOP-10%"
                success_count += 1
            elif percentile >= 75:
                success = "TOP-25%"
            else:
                success = "NEIN"
        else:
            success = "N/A"

        print(f"{r['city']:<20} {r['total_candidates']:>12,} #{r['winner_rank']:>9} {success:>12}")

    print(f"\n{'='*70}")
    print(f"Erfolgsquote: {success_count}/{len(results)}")
    print(f"{'='*70}")

    # Speichern
    output = {
        "methode": "Multi-Metrik Reverse Engineering",
        "metriken": [
            "other_popularity",
            "winner_unpopularity",
            "birthday_avoidance",
            "high_numbers",
            "spread",
            "low_consecutive"
        ],
        "ergebnisse": results,
        "erfolgsquote": success_count / len(results) if results else 0,
    }

    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/reverse_engineer_multi_metric.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    return results


if __name__ == "__main__":
    main()
