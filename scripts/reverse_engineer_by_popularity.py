"""
Reverse Engineering der Gewinner-Kombination durch Popularitaets-Analyse.

LOGIK:
Wenn das System die 20 Zahlen so waehlt, dass die "Anderen 10" populaer sind,
dann ist der Kandidat mit den POPULAERSTEN "Anderen 10" der wahrscheinlichste Gewinner.

METHODE:
1. Generiere alle Kandidaten (mit Constraints)
2. Fuer jeden Kandidaten: Berechne Popularitaet der "Anderen 10"
3. Sortiere Kandidaten nach Popularitaet der "Anderen 10" (absteigend)
4. Top-Kandidaten = wahrscheinlichste Gewinner
"""

from itertools import combinations
from collections import Counter
import json
import numpy as np
from pathlib import Path


def get_popularity_score(zahl: int) -> float:
    """Berechnet Popularitaets-Score fuer eine Zahl (0-1)."""
    score = 0.0

    # Birthday-Zahlen (1-31): +0.4
    if 1 <= zahl <= 31:
        score += 0.4

    # Sehr niedrige Zahlen (1-12 Monate): +0.2
    if 1 <= zahl <= 12:
        score += 0.2

    # Glueckszahlen: +0.3
    if zahl in [7, 3, 9, 13, 21]:
        score += 0.3

    # Runde Zahlen (Zehner): +0.15
    if zahl % 10 == 0:
        score += 0.15

    # Generelle Praeferenz fuer niedrige Zahlen
    score += 0.3 * (70 - zahl) / 69

    # "Unbeliebte" Zahlen
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
    # Optional: Keine Endziffer 1 (in allen 3 bekannten Faellen)
    if count_endziffer_1(combo) > 0:
        return False
    return True


def reverse_engineer_winner(drawn_20: list[int], known_winner: list[int] = None) -> dict:
    """
    Versucht den Gewinner durch Popularitaets-Analyse zu ermitteln.
    """
    drawn_set = set(drawn_20)

    print(f"\n{'='*70}")
    print("REVERSE ENGINEERING DURCH POPULARITAETS-ANALYSE")
    print(f"{'='*70}")
    print(f"\n20 gezogene Zahlen: {sorted(drawn_20)}")

    if known_winner:
        print(f"Bekannter Gewinner: {sorted(known_winner)}")

    # 1. Generiere alle Kandidaten mit Constraints
    print(f"\nGeneriere Kandidaten (mit Constraints)...")
    candidates = []

    for combo in combinations(sorted(drawn_20), 10):
        if passes_constraints(list(combo)):
            candidates.append(set(combo))

    print(f"Anzahl Kandidaten nach Constraints: {len(candidates):,}")

    if not candidates:
        print("FEHLER: Keine Kandidaten gefunden!")
        return None

    # 2. Berechne fuer jeden Kandidaten die Popularitaet der "Anderen 10"
    print(f"\nBerechne Popularitaet der 'Anderen 10' fuer jeden Kandidaten...")

    candidates_scored = []
    for candidate in candidates:
        other_10 = drawn_set - candidate
        other_popularity = np.mean([get_popularity_score(z) for z in other_10])
        winner_popularity = np.mean([get_popularity_score(z) for z in candidate])

        # Birthday-Zahlen zaehlen
        birthday_in_other = sum(1 for z in other_10 if z <= 31)
        birthday_in_winner = sum(1 for z in candidate if z <= 31)

        candidates_scored.append({
            "candidate": sorted(candidate),
            "other_10": sorted(other_10),
            "other_popularity": other_popularity,
            "winner_popularity": winner_popularity,
            "popularity_diff": other_popularity - winner_popularity,
            "birthday_in_other": birthday_in_other,
            "birthday_in_winner": birthday_in_winner,
        })

    # 3. Sortiere nach Popularitaet der "Anderen 10" (absteigend)
    # Hypothese: Je populaerer die "Anderen 10", desto wahrscheinlicher ist der Kandidat der Gewinner
    candidates_scored.sort(key=lambda x: x["other_popularity"], reverse=True)

    # 4. Zeige Top-10 Kandidaten
    print(f"\n{'='*70}")
    print("TOP-10 WAHRSCHEINLICHSTE GEWINNER")
    print("(Sortiert nach Popularitaet der 'Anderen 10')")
    print(f"{'='*70}")

    print(f"\n{'Rang':>4} {'Other Pop':>10} {'Win Pop':>10} {'Diff':>8} {'BD Oth':>7} {'BD Win':>7}")
    print("-" * 70)

    for i, c in enumerate(candidates_scored[:10]):
        is_winner = ""
        if known_winner and set(c["candidate"]) == set(known_winner):
            is_winner = " *** GEWINNER ***"

        print(f"{i+1:>4} {c['other_popularity']:>10.3f} {c['winner_popularity']:>10.3f} "
              f"{c['popularity_diff']:>+8.3f} {c['birthday_in_other']:>7} {c['birthday_in_winner']:>7}{is_winner}")

    # Zeige die Top-3 Kandidaten im Detail
    print(f"\n{'='*70}")
    print("TOP-3 KANDIDATEN IM DETAIL")
    print(f"{'='*70}")

    for i, c in enumerate(candidates_scored[:3]):
        is_winner = " *** ECHTER GEWINNER ***" if known_winner and set(c["candidate"]) == set(known_winner) else ""
        print(f"\n#{i+1}{is_winner}")
        print(f"  Kandidat (Gewinner):  {c['candidate']}")
        print(f"  Andere 10:            {c['other_10']}")
        print(f"  Popularitaet Andere:  {c['other_popularity']:.3f}")
        print(f"  Popularitaet Gewinner: {c['winner_popularity']:.3f}")
        print(f"  Birthday in Andere:   {c['birthday_in_other']}/10")
        print(f"  Birthday in Gewinner: {c['birthday_in_winner']}/10")

    # 5. Wenn bekannter Gewinner: Finde seine Position
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
            print(f"\nBekannter Gewinner gefunden auf Rang: #{winner_rank} von {len(candidates_scored)}")
            print(f"Percentile: Top {100 - percentile:.1f}%")

            if winner_rank <= 10:
                print(f"\n  ✓ ERFOLG! Gewinner in Top-10 ({winner_rank}/10)")
            elif winner_rank <= len(candidates_scored) * 0.1:
                print(f"\n  ✓ GUT! Gewinner in Top-10% (Rang {winner_rank})")
            elif winner_rank <= len(candidates_scored) * 0.25:
                print(f"\n  ~ MODERAT. Gewinner in Top-25% (Rang {winner_rank})")
            else:
                print(f"\n  ✗ SCHWACH. Gewinner nicht in Top-25% (Rang {winner_rank})")
        else:
            print(f"\n  ✗ FEHLER: Bekannter Gewinner nicht in Kandidaten gefunden!")

    return {
        "drawn_20": sorted(drawn_20),
        "known_winner": sorted(known_winner) if known_winner else None,
        "total_candidates": len(candidates_scored),
        "top_10": candidates_scored[:10],
        "winner_rank": winner_rank,
        "winner_percentile": (1 - winner_rank / len(candidates_scored)) * 100 if winner_rank else None,
    }


def main():
    """Teste Reverse Engineering auf allen bekannten Jackpots."""

    print("=" * 70)
    print("REVERSE ENGINEERING DURCH POPULARITAETS-VERTEILUNG")
    print("=" * 70)
    print("""
Hypothese: Das System waehlt 20 Zahlen so, dass die "Anderen 10" populaer sind.
Methode:   Sortiere Kandidaten nach Popularitaet der "Anderen 10".
Erwartung: Der echte Gewinner sollte in den Top-Raengen erscheinen.
""")

    # Lade Jackpot-Events
    events_path = Path("C:/Users/kenfu/Documents/keno_base/AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json")

    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    # Teste auf verifizierten Events
    for event in data["events"]:
        print(f"\n\n{'#'*70}")
        print(f"# TEST: {event.get('city', event['id'])}")
        print(f"{'#'*70}")

        result = reverse_engineer_winner(
            event["drawn_20"],
            event["winner_10"]
        )
        result["event_id"] = event["id"]
        result["city"] = event.get("city", "Unknown")
        results.append(result)

    # Zusammenfassung
    print(f"\n\n{'='*70}")
    print("GESAMTZUSAMMENFASSUNG")
    print(f"{'='*70}")

    print(f"\n{'Event':<20} {'Kandidaten':>12} {'Gewinner-Rang':>15} {'Percentile':>12} {'Erfolg':>10}")
    print("-" * 70)

    success_count = 0
    for r in results:
        if r["winner_rank"]:
            success = "TOP-10" if r["winner_rank"] <= 10 else ("TOP-10%" if r["winner_percentile"] >= 90 else "NEIN")
            if r["winner_rank"] <= 10 or r["winner_percentile"] >= 90:
                success_count += 1
        else:
            success = "N/A"

        print(f"{r['city']:<20} {r['total_candidates']:>12,} "
              f"#{r['winner_rank'] if r['winner_rank'] else 'N/A':>14} "
              f"{r['winner_percentile']:.1f}%{'' if r['winner_percentile'] else 'N/A':>10} "
              f"{success:>10}")

    print(f"\n{'='*70}")
    print("FAZIT")
    print(f"{'='*70}")

    if success_count >= len(results) * 0.6:
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  METHODE FUNKTIONIERT! ({success_count}/{len(results)} Erfolge)                                   ║
║                                                                           ║
║  Die Sortierung nach Popularitaet der "Anderen 10" identifiziert         ║
║  den echten Gewinner in den meisten Faellen in den Top-Raengen.          ║
║                                                                           ║
║  ANWENDUNG:                                                               ║
║  Fuer Jackpot-Tage OHNE bekannte Gewinner-Zahlen koennen wir die         ║
║  Top-Kandidaten als wahrscheinlichste Gewinner identifizieren.           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    else:
        print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  METHODE ZEIGT GEMISCHTE ERGEBNISSE ({success_count}/{len(results)} Erfolge)                      ║
║                                                                           ║
║  Die Popularitaets-Sortierung allein reicht nicht aus.                   ║
║  Zusaetzliche Constraints oder Metriken benoetigt.                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    # Speichern
    output = {
        "methode": "Reverse Engineering durch Popularitaets-Analyse",
        "hypothese": "Kandidat mit populaersten 'Anderen 10' ist wahrscheinlichster Gewinner",
        "ergebnisse": results,
        "erfolgsquote": success_count / len(results) if results else 0,
    }

    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/reverse_engineer_popularity.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    return results


if __name__ == "__main__":
    main()
