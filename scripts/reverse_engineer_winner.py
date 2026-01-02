"""
Reverse-Engineering eines Gewinner-Tickets aus den 20 Jackpot-Zahlen.

Hypothese: Die gefundenen Invarianten koennen als Filter dienen,
um aus C(20,10) = 184.756 moeglichen Kombinationen die tatsaechliche
Gewinner-Kombination zu identifizieren.

INVARIANTEN:
1. Ziffernprodukt mod 9 = 0
2. Genau 1 einstellige Zahl (1-9)
3. 6 von 7 Dekaden besetzt
4. Alle 3 Drittel besetzt (1-23, 24-46, 47-70)
5. 6 von 7 Zeilen im Grid (85.7%)
"""

from itertools import combinations
from functools import reduce
import json
from pathlib import Path


def ziffernprodukt_mod9(combo: list[int]) -> int:
    """Berechnet Ziffernprodukt (ohne 0) mod 9."""
    produkt = 1
    for z in combo:
        for d in str(z):
            if d != '0':
                produkt *= int(d)
    return produkt % 9


def count_einstellig(combo: list[int]) -> int:
    """Zaehlt einstellige Zahlen (1-9)."""
    return sum(1 for z in combo if z <= 9)


def count_dekaden_besetzt(combo: list[int]) -> int:
    """Zaehlt wie viele Dekaden (0-9, 10-19, ..., 60-69) besetzt sind."""
    dekaden = set(z // 10 for z in combo)
    return len(dekaden)


def alle_drittel_besetzt(combo: list[int]) -> bool:
    """Prueft ob alle 3 Drittel (1-23, 24-46, 47-70) mindestens 1 Zahl haben."""
    hat_d1 = any(1 <= z <= 23 for z in combo)
    hat_d2 = any(24 <= z <= 46 for z in combo)
    hat_d3 = any(47 <= z <= 70 for z in combo)
    return hat_d1 and hat_d2 and hat_d3


def count_zeilen_besetzt(combo: list[int]) -> int:
    """Zaehlt wie viele Zeilen im 7x10 Grid besetzt sind."""
    zeilen = set((z - 1) // 10 for z in combo)
    return len(zeilen)


def check_all_constraints(combo: list[int]) -> dict:
    """Prueft alle Constraints und gibt Details zurueck."""
    return {
        "ziffernprodukt_mod9": ziffernprodukt_mod9(combo),
        "einstellige_zahlen": count_einstellig(combo),
        "dekaden_besetzt": count_dekaden_besetzt(combo),
        "alle_drittel": alle_drittel_besetzt(combo),
        "zeilen_besetzt": count_zeilen_besetzt(combo),
    }


def passes_all_constraints(combo: list[int], strict: bool = True) -> bool:
    """Prueft ob eine Kombination alle Constraints erfuellt."""
    # Constraint 1: Ziffernprodukt mod 9 = 0
    if ziffernprodukt_mod9(combo) != 0:
        return False

    # Constraint 2: Genau 1 einstellige Zahl
    if count_einstellig(combo) != 1:
        return False

    # Constraint 3: 6 von 7 Dekaden besetzt
    if count_dekaden_besetzt(combo) != 6:
        return False

    # Constraint 4: Alle 3 Drittel besetzt
    if not alle_drittel_besetzt(combo):
        return False

    # Constraint 5: 6 von 7 Zeilen besetzt
    if count_zeilen_besetzt(combo) != 6:
        return False

    return True


def reverse_engineer_winner(jackpot_zahlen: list[int],
                            bekannter_gewinner: list[int] = None) -> dict:
    """
    Versucht den Gewinner aus den 20 Jackpot-Zahlen zu ermitteln.

    Args:
        jackpot_zahlen: Die 20 gezogenen Zahlen am Jackpot-Tag
        bekannter_gewinner: Optional - die bekannte Gewinner-Kombination zur Verifikation
    """
    if len(jackpot_zahlen) != 20:
        raise ValueError(f"Erwartet 20 Zahlen, bekam {len(jackpot_zahlen)}")

    total_combinations = 184756  # C(20,10)

    print(f"\n{'='*70}")
    print("REVERSE-ENGINEERING: Gewinner-Ticket aus Jackpot-Zahlen")
    print(f"{'='*70}")
    print(f"\nJackpot-Zahlen (20): {sorted(jackpot_zahlen)}")
    print(f"Moegliche Kombinationen: {total_combinations:,}")

    if bekannter_gewinner:
        print(f"Bekannter Gewinner: {sorted(bekannter_gewinner)}")
        # Pruefe ob Gewinner in Jackpot-Zahlen enthalten
        if not all(z in jackpot_zahlen for z in bekannter_gewinner):
            print("FEHLER: Gewinner-Zahlen nicht alle in Jackpot-Zahlen!")
            return None

    # Generiere alle C(20,10) Kombinationen und filtere
    passed_combos = []
    constraint_stats = {
        "ziffernprodukt_mod9_failed": 0,
        "einstellig_failed": 0,
        "dekaden_failed": 0,
        "drittel_failed": 0,
        "zeilen_failed": 0,
    }

    print("\nFiltere Kombinationen...")

    for combo in combinations(sorted(jackpot_zahlen), 10):
        combo_list = list(combo)

        # Constraint-Checks mit Statistik
        if ziffernprodukt_mod9(combo_list) != 0:
            constraint_stats["ziffernprodukt_mod9_failed"] += 1
            continue

        if count_einstellig(combo_list) != 1:
            constraint_stats["einstellig_failed"] += 1
            continue

        if count_dekaden_besetzt(combo_list) != 6:
            constraint_stats["dekaden_failed"] += 1
            continue

        if not alle_drittel_besetzt(combo_list):
            constraint_stats["drittel_failed"] += 1
            continue

        if count_zeilen_besetzt(combo_list) != 6:
            constraint_stats["zeilen_failed"] += 1
            continue

        # Alle Constraints erfuellt!
        passed_combos.append(combo_list)

    print(f"\n{'='*70}")
    print("ERGEBNISSE")
    print(f"{'='*70}")

    print(f"\nConstraint-Statistik (welcher Filter eliminierte wie viele):")
    print(f"  Ziffernprodukt mod 9 != 0: {constraint_stats['ziffernprodukt_mod9_failed']:,} eliminiert")
    print(f"  Einstellige != 1:          {constraint_stats['einstellig_failed']:,} eliminiert")
    print(f"  Dekaden != 6:              {constraint_stats['dekaden_failed']:,} eliminiert")
    print(f"  Nicht alle Drittel:        {constraint_stats['drittel_failed']:,} eliminiert")
    print(f"  Zeilen != 6:               {constraint_stats['zeilen_failed']:,} eliminiert")

    remaining = len(passed_combos)
    reduction = (1 - remaining / total_combinations) * 100

    print(f"\n*** VERBLEIBENDE KANDIDATEN: {remaining:,} von {total_combinations:,} ({reduction:.2f}% Reduktion) ***")

    result = {
        "jackpot_zahlen": sorted(jackpot_zahlen),
        "total_combinations": total_combinations,
        "passed_constraints": remaining,
        "reduction_percent": round(reduction, 2),
        "constraint_stats": constraint_stats,
        "candidates": passed_combos[:50],  # Max 50 speichern
    }

    if bekannter_gewinner:
        gewinner_sorted = sorted(bekannter_gewinner)
        gewinner_found = gewinner_sorted in [sorted(c) for c in passed_combos]
        result["gewinner_bekannt"] = gewinner_sorted
        result["gewinner_in_kandidaten"] = gewinner_found

        print(f"\n*** VERIFIKATION ***")
        if gewinner_found:
            print(f"  ✓ ERFOLG: Bekannter Gewinner IST in den {remaining} Kandidaten!")
            # Finde Position
            for i, c in enumerate(passed_combos):
                if sorted(c) == gewinner_sorted:
                    print(f"    Position: #{i+1} von {remaining}")
                    result["gewinner_position"] = i + 1
                    break
        else:
            print(f"  ✗ FEHLER: Bekannter Gewinner NICHT in Kandidaten!")
            # Debug: Welcher Constraint wurde verletzt?
            print(f"\n  Debug - Gewinner Constraint-Check:")
            checks = check_all_constraints(bekannter_gewinner)
            for k, v in checks.items():
                print(f"    {k}: {v}")

    # Zeige erste Kandidaten
    if passed_combos:
        print(f"\nErste 10 Kandidaten:")
        for i, combo in enumerate(passed_combos[:10]):
            checks = check_all_constraints(combo)
            print(f"  {i+1}. {combo}")

    return result


def main():
    """Teste mit bekannten Jackpot-Daten."""

    # Bekannte Jackpots mit ihren 20 Zahlen und Gewinner-Tickets
    # Format: (Jackpot-Tag-Zahlen, Gewinner-Ticket)

    # Wir brauchen die 20 gezogenen Zahlen von den Jackpot-Tagen
    # Die Gewinner-Tickets sind bekannt:
    # Kyritz: [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]
    # Oberbayern: [3, 15, 18, 27, 47, 53, 54, 55, 66, 68]
    # Nordsachsen: [9, 19, 37, 38, 43, 45, 48, 57, 59, 67]

    print("\n" + "="*70)
    print("TEST 1: Theoretischer Test mit konstruierten Daten")
    print("="*70)

    # Fuer den Test: Nehme Gewinner + 10 zusaetzliche Zahlen
    gewinner_kyritz = [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]

    # Konstruiere hypothetische Jackpot-Zahlen (Gewinner + 10 andere)
    # Die 10 anderen muessen aus 1-70 sein, aber nicht im Gewinner
    other_10 = [1, 7, 14, 23, 31, 39, 52, 58, 63, 70]  # Beispiel

    jackpot_zahlen = gewinner_kyritz + other_10

    result1 = reverse_engineer_winner(jackpot_zahlen, gewinner_kyritz)

    print("\n" + "="*70)
    print("TEST 2: Anderer konstruierter Fall")
    print("="*70)

    gewinner_oberbayern = [3, 15, 18, 27, 47, 53, 54, 55, 66, 68]
    other_10_v2 = [2, 8, 11, 24, 32, 41, 49, 57, 62, 70]
    jackpot_zahlen_2 = gewinner_oberbayern + other_10_v2

    result2 = reverse_engineer_winner(jackpot_zahlen_2, gewinner_oberbayern)

    print("\n" + "="*70)
    print("TEST 3: Nordsachsen")
    print("="*70)

    gewinner_nordsachsen = [9, 19, 37, 38, 43, 45, 48, 57, 59, 67]
    other_10_v3 = [3, 11, 22, 28, 35, 51, 54, 62, 66, 70]
    jackpot_zahlen_3 = gewinner_nordsachsen + other_10_v3

    result3 = reverse_engineer_winner(jackpot_zahlen_3, gewinner_nordsachsen)

    # Zusammenfassung
    print("\n" + "="*70)
    print("ZUSAMMENFASSUNG")
    print("="*70)

    results = [result1, result2, result3]
    names = ["Kyritz", "Oberbayern", "Nordsachsen"]

    print(f"\n{'Jackpot':<15} {'Kandidaten':>12} {'Reduktion':>12} {'Gewinner gefunden?':>20}")
    print("-"*60)
    for name, r in zip(names, results):
        if r:
            found = "JA" if r.get("gewinner_in_kandidaten") else "NEIN"
            pos = r.get("gewinner_position", "N/A")
            if found == "JA":
                found = f"JA (#{pos})"
            print(f"{name:<15} {r['passed_constraints']:>12,} {r['reduction_percent']:>11.1f}% {found:>20}")

    # Speichern
    output = {
        "analyse_typ": "Reverse-Engineering Gewinner-Ticket",
        "hypothese": "Invarianten koennen als Filter dienen um Gewinner zu identifizieren",
        "constraints_verwendet": [
            "Ziffernprodukt mod 9 = 0",
            "Genau 1 einstellige Zahl",
            "6 von 7 Dekaden besetzt",
            "Alle 3 Drittel besetzt",
            "6 von 7 Zeilen im Grid"
        ],
        "tests": {
            "Kyritz": result1,
            "Oberbayern": result2,
            "Nordsachsen": result3,
        }
    }

    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/reverse_engineer_winner.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    return output


if __name__ == "__main__":
    main()
