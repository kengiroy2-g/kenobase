"""
Reverse-Engineering V2 - Mit ALLEN gefundenen Constraints.

Zusaetzliche Constraints:
- Keine Zahl endet auf 1 (0 von 30 in den Gewinnern)
- Digitale Wurzel 3 oder 9 bevorzugt (14 von 30, vs ~7 erwartet)
- Summe der Ziffern in bestimmtem Bereich
"""

from itertools import combinations
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
    """Zaehlt wie viele Dekaden besetzt sind."""
    dekaden = set(z // 10 for z in combo)
    return len(dekaden)


def alle_drittel_besetzt(combo: list[int]) -> bool:
    """Prueft ob alle 3 Drittel mindestens 1 Zahl haben."""
    hat_d1 = any(1 <= z <= 23 for z in combo)
    hat_d2 = any(24 <= z <= 46 for z in combo)
    hat_d3 = any(47 <= z <= 70 for z in combo)
    return hat_d1 and hat_d2 and hat_d3


def count_zeilen_besetzt(combo: list[int]) -> int:
    """Zaehlt wie viele Zeilen im Grid besetzt sind."""
    zeilen = set((z - 1) // 10 for z in combo)
    return len(zeilen)


# NEUE CONSTRAINTS

def count_endziffer_1(combo: list[int]) -> int:
    """Zaehlt Zahlen die auf 1 enden (11, 21, 31, ...)."""
    return sum(1 for z in combo if z % 10 == 1)


def digitale_wurzel(n: int) -> int:
    """Berechnet digitale Wurzel (Quersumme mod 9, 9->9)."""
    if n == 0:
        return 0
    r = n % 9
    return r if r != 0 else 9


def count_digitale_wurzel_3_9(combo: list[int]) -> int:
    """Zaehlt Zahlen mit digitaler Wurzel 3 oder 9."""
    return sum(1 for z in combo if digitale_wurzel(z) in [3, 9])


def count_ziffer_5(combo: list[int]) -> int:
    """Zaehlt wie oft Ziffer 5 vorkommt."""
    count = 0
    for z in combo:
        count += str(z).count('5')
    return count


def passes_constraints_v1(combo: list[int]) -> bool:
    """Originale 5 Constraints."""
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


def passes_constraints_v2(combo: list[int]) -> bool:
    """V1 + Keine Endziffer 1."""
    if not passes_constraints_v1(combo):
        return False
    # NEUER Constraint: Keine Zahl endet auf 1
    if count_endziffer_1(combo) > 0:
        return False
    return True


def passes_constraints_v3(combo: list[int]) -> bool:
    """V2 + Mindestens 3 Zahlen mit digitaler Wurzel 3 oder 9."""
    if not passes_constraints_v2(combo):
        return False
    # In den Gewinnern: 4-5 pro Kombination, Durchschnitt ~4.7
    # Setze Minimum auf 3
    if count_digitale_wurzel_3_9(combo) < 3:
        return False
    return True


def passes_constraints_v4(combo: list[int]) -> bool:
    """V3 + Mindestens 2x Ziffer 5 (Gewinner hatten 3-4)."""
    if not passes_constraints_v3(combo):
        return False
    if count_ziffer_5(combo) < 2:
        return False
    return True


def analyze_combo(combo: list[int]) -> dict:
    """Detaillierte Analyse einer Kombination."""
    return {
        "combo": combo,
        "ziffernprodukt_mod9": ziffernprodukt_mod9(combo),
        "einstellige": count_einstellig(combo),
        "dekaden": count_dekaden_besetzt(combo),
        "alle_drittel": alle_drittel_besetzt(combo),
        "zeilen": count_zeilen_besetzt(combo),
        "endziffer_1": count_endziffer_1(combo),
        "digitale_wurzel_3_9": count_digitale_wurzel_3_9(combo),
        "ziffer_5_count": count_ziffer_5(combo),
    }


def test_all_versions(jackpot_zahlen: list[int], gewinner: list[int]) -> dict:
    """Teste alle Constraint-Versionen."""

    total = 184756
    results = {}

    print(f"\nJackpot-Zahlen: {sorted(jackpot_zahlen)}")
    print(f"Gewinner:       {sorted(gewinner)}")

    # Zuerst: Analysiere den Gewinner
    print(f"\n--- Gewinner-Analyse ---")
    g_analysis = analyze_combo(gewinner)
    for k, v in g_analysis.items():
        if k != "combo":
            print(f"  {k}: {v}")

    versions = {
        "V1 (Original 5)": passes_constraints_v1,
        "V2 (+Keine Endziffer 1)": passes_constraints_v2,
        "V3 (+Digitale Wurzel 3/9)": passes_constraints_v3,
        "V4 (+Ziffer 5)": passes_constraints_v4,
    }

    for name, check_fn in versions.items():
        passed = []
        for combo in combinations(sorted(jackpot_zahlen), 10):
            if check_fn(list(combo)):
                passed.append(list(combo))

        gewinner_found = sorted(gewinner) in [sorted(c) for c in passed]
        position = None
        if gewinner_found:
            for i, c in enumerate(passed):
                if sorted(c) == sorted(gewinner):
                    position = i + 1
                    break

        results[name] = {
            "kandidaten": len(passed),
            "reduktion": round((1 - len(passed) / total) * 100, 2),
            "gewinner_gefunden": gewinner_found,
            "gewinner_position": position,
        }

        status = f"✓ #{position}" if gewinner_found else "✗ NICHT GEFUNDEN!"
        print(f"{name:<30} {len(passed):>8,} Kandidaten ({results[name]['reduktion']:>5.1f}% Reduktion) {status}")

    return results


def main():
    """Teste alle Constraint-Versionen."""

    print("="*70)
    print("REVERSE-ENGINEERING V2: Progressive Constraint-Filter")
    print("="*70)

    # Die 3 Test-Faelle
    tests = [
        {
            "name": "Kyritz",
            "gewinner": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],
            "other_10": [1, 7, 14, 23, 31, 39, 52, 58, 63, 70],
        },
        {
            "name": "Oberbayern",
            "gewinner": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68],
            "other_10": [2, 8, 11, 24, 32, 41, 49, 57, 62, 70],
        },
        {
            "name": "Nordsachsen",
            "gewinner": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67],
            "other_10": [3, 11, 22, 28, 35, 51, 54, 62, 66, 70],
        },
    ]

    all_results = {}

    for test in tests:
        print(f"\n{'='*70}")
        print(f"TEST: {test['name']}")
        print(f"{'='*70}")

        jackpot_zahlen = test["gewinner"] + test["other_10"]
        results = test_all_versions(jackpot_zahlen, test["gewinner"])
        all_results[test["name"]] = results

    # Zusammenfassung
    print(f"\n{'='*70}")
    print("ZUSAMMENFASSUNG: Kandidaten nach Constraint-Version")
    print(f"{'='*70}")

    print(f"\n{'Version':<30} {'Kyritz':>12} {'Oberbayern':>12} {'Nordsachsen':>12}")
    print("-"*70)

    for version in ["V1 (Original 5)", "V2 (+Keine Endziffer 1)",
                    "V3 (+Digitale Wurzel 3/9)", "V4 (+Ziffer 5)"]:
        vals = [all_results[name][version]["kandidaten"] for name in ["Kyritz", "Oberbayern", "Nordsachsen"]]
        founds = [all_results[name][version]["gewinner_gefunden"] for name in ["Kyritz", "Oberbayern", "Nordsachsen"]]
        v_str = [f"{v:,}" if f else f"{v:,}(X)" for v, f in zip(vals, founds)]
        print(f"{version:<30} {v_str[0]:>12} {v_str[1]:>12} {v_str[2]:>12}")

    # Speichern
    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/reverse_engineer_v2.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")

    return all_results


if __name__ == "__main__":
    main()
