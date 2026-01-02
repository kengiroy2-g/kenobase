"""
Analyse der Aehnlichkeit zwischen Kandidaten-Kombinationen.

Fragen:
1. Wie viele Zahlen teilen die Kandidaten gemeinsam?
2. Gibt es einen "Kern" von Zahlen die in ALLEN Kandidaten vorkommen?
3. Welche Zahlen variieren am meisten?
4. Wie gross ist die typische Ueberlappung zwischen 2 Kandidaten?
"""

from itertools import combinations
from collections import Counter
import json
from pathlib import Path
import random


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


def passes_constraints(combo: list[int]) -> bool:
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
    return True


def analyze_candidates(jackpot_zahlen: list[int], gewinner: list[int]) -> dict:
    """Analysiere die Aehnlichkeit zwischen allen Kandidaten."""

    print(f"\n{'='*70}")
    print("KANDIDATEN-AEHNLICHKEITS-ANALYSE")
    print(f"{'='*70}")
    print(f"\nJackpot-Zahlen (20): {sorted(jackpot_zahlen)}")
    print(f"Gewinner:            {sorted(gewinner)}")

    # Generiere alle Kandidaten
    candidates = []
    for combo in combinations(sorted(jackpot_zahlen), 10):
        if passes_constraints(list(combo)):
            candidates.append(set(combo))

    n_candidates = len(candidates)
    print(f"\nAnzahl Kandidaten: {n_candidates:,}")

    # 1. KERN-ZAHLEN: Welche Zahlen kommen in ALLEN Kandidaten vor?
    if candidates:
        kern = candidates[0].copy()
        for c in candidates[1:]:
            kern = kern.intersection(c)
        kern = sorted(kern)
    else:
        kern = []

    print(f"\n--- KERN-ZAHLEN (in ALLEN {n_candidates:,} Kandidaten) ---")
    print(f"    {kern if kern else 'KEINE'}")
    print(f"    Anzahl: {len(kern)} von 10")

    # 2. HÄUFIGKEIT jeder Zahl in Kandidaten
    zahl_frequenz = Counter()
    for c in candidates:
        for z in c:
            zahl_frequenz[z] += 1

    # Sortiere nach Häufigkeit
    freq_sorted = sorted(zahl_frequenz.items(), key=lambda x: -x[1])

    print(f"\n--- ZAHLEN-HÄUFIGKEIT in Kandidaten ---")
    print(f"{'Zahl':>6} {'Anzahl':>10} {'Prozent':>10} {'In Gewinner?':>15}")
    print("-" * 45)

    gewinner_set = set(gewinner)
    for zahl, count in freq_sorted:
        pct = count / n_candidates * 100
        in_gewinner = "✓ JA" if zahl in gewinner_set else ""
        print(f"{zahl:>6} {count:>10,} {pct:>9.1f}% {in_gewinner:>15}")

    # 3. KLASSIFIZIERUNG der Zahlen
    sehr_haeufig = [z for z, c in freq_sorted if c / n_candidates > 0.8]  # >80%
    haeufig = [z for z, c in freq_sorted if 0.5 < c / n_candidates <= 0.8]  # 50-80%
    mittel = [z for z, c in freq_sorted if 0.2 < c / n_candidates <= 0.5]  # 20-50%
    selten = [z for z, c in freq_sorted if c / n_candidates <= 0.2]  # <20%

    print(f"\n--- KLASSIFIZIERUNG ---")
    print(f"Sehr häufig (>80%):  {sehr_haeufig}")
    print(f"Häufig (50-80%):     {haeufig}")
    print(f"Mittel (20-50%):     {mittel}")
    print(f"Selten (<20%):       {selten}")

    # 4. ÜBERLAPPUNG zwischen Kandidaten (Stichprobe)
    print(f"\n--- PAARWEISE ÜBERLAPPUNG (Stichprobe) ---")

    if n_candidates > 1:
        # Zufällige Stichprobe von 1000 Paaren
        sample_size = min(1000, n_candidates * (n_candidates - 1) // 2)
        overlaps = []

        # Für kleine Mengen: alle Paare
        if n_candidates <= 100:
            for i in range(len(candidates)):
                for j in range(i + 1, len(candidates)):
                    overlap = len(candidates[i].intersection(candidates[j]))
                    overlaps.append(overlap)
        else:
            # Stichprobe
            random.seed(42)
            indices = list(range(len(candidates)))
            for _ in range(sample_size):
                i, j = random.sample(indices, 2)
                overlap = len(candidates[i].intersection(candidates[j]))
                overlaps.append(overlap)

        overlap_dist = Counter(overlaps)
        avg_overlap = sum(overlaps) / len(overlaps)

        print(f"\nVerteilung der gemeinsamen Zahlen (von 10):")
        print(f"{'Gemeinsam':>10} {'Anzahl':>10} {'Prozent':>10}")
        print("-" * 35)
        for overlap in sorted(overlap_dist.keys(), reverse=True):
            count = overlap_dist[overlap]
            pct = count / len(overlaps) * 100
            print(f"{overlap:>10} {count:>10,} {pct:>9.1f}%")

        print(f"\nDurchschnittliche Überlappung: {avg_overlap:.2f} von 10 Zahlen")
        print(f"Das heißt: Kandidaten unterscheiden sich durchschnittlich in {10 - avg_overlap:.2f} Zahlen")

    # 5. WIE VIELE KANDIDATEN hat jede Zahlen-Kombination des Gewinners?
    # Prüfe: Wenn wir 9 von 10 Gewinner-Zahlen kennen, wie viele Kandidaten bleiben?
    print(f"\n--- WENN WIR TEILE DES GEWINNERS KENNEN ---")

    for known in [5, 6, 7, 8, 9]:
        # Wie viele Kandidaten enthalten mindestens 'known' Zahlen des Gewinners?
        matches = [c for c in candidates if len(c.intersection(gewinner_set)) >= known]
        print(f"Kandidaten mit >= {known} Gewinner-Zahlen: {len(matches):>6,}")

    # 6. UMGEKEHRT: Wie ist der Gewinner relativ zu allen Kandidaten?
    print(f"\n--- GEWINNER-POSITION IN KANDIDATEN ---")

    # Sortiere Kandidaten nach Ähnlichkeit zum Gewinner
    candidates_with_score = []
    for c in candidates:
        overlap = len(c.intersection(gewinner_set))
        candidates_with_score.append((c, overlap))

    candidates_with_score.sort(key=lambda x: -x[1])

    # Finde Position des Gewinners
    for i, (c, score) in enumerate(candidates_with_score):
        if c == gewinner_set:
            print(f"Gewinner-Rang nach Überlappung: #{i+1} von {n_candidates}")
            print(f"Gewinner-Überlappung mit sich selbst: {score}/10 (natürlich 10)")
            break

    # Zeige Top-10 ähnlichste zum Gewinner
    print(f"\nTop-10 ähnlichste Kandidaten zum Gewinner:")
    print(f"{'#':>4} {'Kandidat':^50} {'Überlappung':>12}")
    print("-" * 70)
    for i, (c, score) in enumerate(candidates_with_score[:10]):
        c_sorted = sorted(c)
        is_winner = " *** GEWINNER ***" if c == gewinner_set else ""
        print(f"{i+1:>4} {str(c_sorted):<50} {score:>10}/10 {is_winner}")

    # 7. UNTERSCHIED zum nächstbesten Kandidaten
    print(f"\n--- UNTERSCHIED GEWINNER vs NÄCHSTBESTER ---")

    for i, (c, score) in enumerate(candidates_with_score):
        if c != gewinner_set:
            diff_zahlen = gewinner_set.symmetric_difference(c)
            nur_gewinner = gewinner_set - c
            nur_kandidat = c - gewinner_set
            print(f"Nächstbester Kandidat (Position #{i+1}):")
            print(f"  Kandidat: {sorted(c)}")
            print(f"  Überlappung: {score}/10")
            print(f"  Nur im Gewinner: {sorted(nur_gewinner)}")
            print(f"  Nur im Kandidat: {sorted(nur_kandidat)}")
            print(f"  Unterschied: {len(diff_zahlen)} Zahlen")
            break

    return {
        "n_kandidaten": n_candidates,
        "kern_zahlen": kern,
        "sehr_haeufig": sehr_haeufig,
        "haeufig": haeufig,
        "zahlen_frequenz": dict(zahl_frequenz),
        "avg_overlap": avg_overlap if n_candidates > 1 else 10,
    }


def main():
    # Test mit Kyritz-Daten
    gewinner = [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]
    other_10 = [1, 7, 14, 23, 31, 39, 52, 58, 63, 70]
    jackpot_zahlen = gewinner + other_10

    result = analyze_candidates(jackpot_zahlen, gewinner)

    print(f"\n{'='*70}")
    print("ZUSAMMENFASSUNG")
    print(f"{'='*70}")

    print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  KERN-ERKENNTNIS                                                          ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  Kandidaten: {result['n_kandidaten']:,}                                                       ║
║  Kern-Zahlen (in ALLEN): {len(result['kern_zahlen'])} Stück                                         ║
║  Sehr häufige Zahlen (>80%): {len(result['sehr_haeufig'])} Stück                                    ║
║                                                                           ║
║  Durchschnittliche Überlappung: {result['avg_overlap']:.1f} von 10 Zahlen                     ║
║  → Kandidaten unterscheiden sich in ~{10 - result['avg_overlap']:.1f} Zahlen                       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    # Speichern
    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/candidate_similarity.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Ergebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
