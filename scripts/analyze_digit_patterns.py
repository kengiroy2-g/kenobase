"""
Ziffern-Muster-Analyse fuer verifizierte KENO-Gewinner-Kombinationen.

Analysiert:
1. Ziffernhaeufigkeit (0-9)
2. Erste Ziffer Verteilung (Benford's Law)
3. Letzte Ziffer Verteilung
4. Ziffernsumme pro Zahl und gesamt
5. Ziffernprodukt (ohne 0)
6. Palindrome (11, 22, 33...)
7. Wiederholte Ziffern
8. Aufsteigende/Absteigende Ziffern (12, 23, 34...)
9. Spiegelzahlen-Paare (12/21, 36/63)
10. Quersumme mod 9 (digitale Wurzel)
"""

import json
from collections import Counter
from pathlib import Path
from typing import Any
import math


def get_digits(number: int) -> list[int]:
    """Extrahiere Ziffern einer Zahl."""
    return [int(d) for d in str(number)]


def digit_sum(number: int) -> int:
    """Berechne Ziffernsumme."""
    return sum(get_digits(number))


def digit_product(number: int) -> int:
    """Berechne Ziffernprodukt (0 wird als 1 behandelt oder uebersprungen)."""
    digits = get_digits(number)
    product = 1
    for d in digits:
        if d != 0:
            product *= d
    return product


def digital_root(number: int) -> int:
    """Berechne digitale Wurzel (Quersumme mod 9, wobei 9 -> 9)."""
    if number == 0:
        return 0
    remainder = number % 9
    return remainder if remainder != 0 else 9


def is_palindrome(number: int) -> bool:
    """Pruefe ob Zahl ein Palindrom ist (z.B. 11, 22, 33, 44, 55, 66)."""
    s = str(number)
    return s == s[::-1] and len(s) > 1


def has_repeated_digits(number: int) -> bool:
    """Pruefe ob Zahl wiederholte Ziffern hat."""
    digits = get_digits(number)
    return len(digits) != len(set(digits))


def is_ascending_digits(number: int) -> bool:
    """Pruefe ob Ziffern aufsteigend sind (12, 23, 34, 45, 56, 67, 78, 89)."""
    s = str(number)
    if len(s) != 2:
        return False
    return int(s[1]) == int(s[0]) + 1


def is_descending_digits(number: int) -> bool:
    """Pruefe ob Ziffern absteigend sind (21, 32, 43, 54, 65, 76, 87, 98)."""
    s = str(number)
    if len(s) != 2:
        return False
    return int(s[0]) == int(s[1]) + 1


def get_mirror(number: int) -> int | None:
    """Hole Spiegelzahl (12 -> 21, 36 -> 63)."""
    s = str(number)
    if len(s) != 2:
        return None
    mirrored = int(s[::-1])
    if mirrored != number and 1 <= mirrored <= 70:
        return mirrored
    return None


def analyze_combination(numbers: list[int], name: str) -> dict[str, Any]:
    """Analysiere eine einzelne Kombination."""
    result = {
        "name": name,
        "numbers": numbers,
        "count": len(numbers),
    }

    # Alle Ziffern extrahieren
    all_digits = []
    for n in numbers:
        all_digits.extend(get_digits(n))

    # 1. Ziffernhaeufigkeit (0-9)
    digit_freq = Counter(all_digits)
    result["digit_frequency"] = {str(i): digit_freq.get(i, 0) for i in range(10)}
    result["total_digits"] = len(all_digits)

    # 2. Erste Ziffer Verteilung
    first_digits = [get_digits(n)[0] for n in numbers]
    first_digit_freq = Counter(first_digits)
    result["first_digit_frequency"] = {str(i): first_digit_freq.get(i, 0) for i in range(1, 8)}

    # Benford's Law Erwartung (fuer Vergleich)
    benford_expected = {str(i): round(math.log10(1 + 1/i) * len(numbers), 2) for i in range(1, 8)}
    result["benford_expected"] = benford_expected

    # 3. Letzte Ziffer Verteilung
    last_digits = [get_digits(n)[-1] for n in numbers]
    last_digit_freq = Counter(last_digits)
    result["last_digit_frequency"] = {str(i): last_digit_freq.get(i, 0) for i in range(10)}

    # 4. Ziffernsumme
    digit_sums = {n: digit_sum(n) for n in numbers}
    result["digit_sums"] = digit_sums
    result["total_digit_sum"] = sum(digit_sums.values())
    result["avg_digit_sum"] = round(sum(digit_sums.values()) / len(numbers), 2)

    # 5. Ziffernprodukt
    digit_products = {n: digit_product(n) for n in numbers}
    result["digit_products"] = digit_products

    # 6. Palindrome
    palindromes = [n for n in numbers if is_palindrome(n)]
    result["palindromes"] = palindromes
    result["palindrome_count"] = len(palindromes)

    # 7. Wiederholte Ziffern
    repeated = [n for n in numbers if has_repeated_digits(n)]
    result["repeated_digit_numbers"] = repeated
    result["repeated_digit_count"] = len(repeated)

    # 8. Aufsteigende/Absteigende Ziffern
    ascending = [n for n in numbers if is_ascending_digits(n)]
    descending = [n for n in numbers if is_descending_digits(n)]
    result["ascending_digit_numbers"] = ascending
    result["descending_digit_numbers"] = descending

    # 9. Spiegelzahlen-Paare
    mirrors_found = []
    numbers_set = set(numbers)
    for n in numbers:
        mirror = get_mirror(n)
        if mirror and mirror in numbers_set:
            pair = tuple(sorted([n, mirror]))
            if pair not in mirrors_found:
                mirrors_found.append(pair)
    result["mirror_pairs"] = [list(p) for p in mirrors_found]

    # 10. Digitale Wurzel (Quersumme mod 9)
    digital_roots = {n: digital_root(n) for n in numbers}
    result["digital_roots"] = digital_roots
    root_freq = Counter(digital_roots.values())
    result["digital_root_frequency"] = {str(i): root_freq.get(i, 0) for i in range(1, 10)}

    return result


def find_cross_combination_patterns(combinations: list[dict]) -> dict[str, Any]:
    """Finde Muster ueber alle Kombinationen hinweg."""
    patterns = {}

    # Gesamte Ziffernhaeufigkeit
    total_digit_freq = Counter()
    for combo in combinations:
        for digit, count in combo["digit_frequency"].items():
            total_digit_freq[int(digit)] += count

    patterns["total_digit_frequency"] = {str(i): total_digit_freq.get(i, 0) for i in range(10)}

    # Gesamte erste Ziffer
    total_first = Counter()
    for combo in combinations:
        for digit, count in combo["first_digit_frequency"].items():
            total_first[int(digit)] += count
    patterns["total_first_digit_frequency"] = {str(i): total_first.get(i, 0) for i in range(1, 8)}

    # Gesamte letzte Ziffer
    total_last = Counter()
    for combo in combinations:
        for digit, count in combo["last_digit_frequency"].items():
            total_last[int(digit)] += count
    patterns["total_last_digit_frequency"] = {str(i): total_last.get(i, 0) for i in range(10)}

    # Gesamte digitale Wurzel
    total_roots = Counter()
    for combo in combinations:
        for digit, count in combo["digital_root_frequency"].items():
            total_roots[int(digit)] += count
    patterns["total_digital_root_frequency"] = {str(i): total_roots.get(i, 0) for i in range(1, 10)}

    # Gemeinsame Zahlen
    all_numbers = [set(c["numbers"]) for c in combinations]
    common_all = all_numbers[0].intersection(*all_numbers[1:])
    patterns["common_numbers_all"] = sorted(list(common_all))

    # Paarweise gemeinsame
    patterns["common_pairs"] = {}
    names = [c["name"] for c in combinations]
    for i in range(len(combinations)):
        for j in range(i+1, len(combinations)):
            common = all_numbers[i].intersection(all_numbers[j])
            key = f"{names[i]}_and_{names[j]}"
            patterns["common_pairs"][key] = sorted(list(common))

    # Alle Palindrome
    all_palindromes = []
    for combo in combinations:
        all_palindromes.extend(combo["palindromes"])
    patterns["all_palindromes"] = sorted(list(set(all_palindromes)))

    # Alle aufsteigenden Ziffern
    all_ascending = []
    for combo in combinations:
        all_ascending.extend(combo["ascending_digit_numbers"])
    patterns["all_ascending"] = sorted(list(set(all_ascending)))

    # Alle absteigenden Ziffern
    all_descending = []
    for combo in combinations:
        all_descending.extend(combo["descending_digit_numbers"])
    patterns["all_descending"] = sorted(list(set(all_descending)))

    # Alle Spiegelpaare
    all_mirrors = []
    for combo in combinations:
        all_mirrors.extend(combo["mirror_pairs"])
    patterns["all_mirror_pairs"] = all_mirrors

    return patterns


def identify_unusual_patterns(combinations: list[dict], cross_patterns: dict) -> list[dict]:
    """Identifiziere ungewoehnliche Muster die ein Mensch nicht waehlen wuerde."""
    unusual = []

    # 1. Endziffer-Clustering
    last_freq = cross_patterns["total_last_digit_frequency"]
    max_last = max(int(v) for v in last_freq.values())
    dominant_last = [k for k, v in last_freq.items() if int(v) == max_last]
    if max_last >= 6:  # 6+ von 30 Zahlen enden mit gleicher Ziffer
        unusual.append({
            "pattern": "Endziffer-Dominanz",
            "description": f"Ziffer(n) {dominant_last} erscheinen {max_last}x als Endziffer",
            "significance": "Hoch - Menschen vermeiden solche Cluster",
            "values": dominant_last,
            "count": max_last
        })

    # 2. Aufsteigende Ziffern-Haeufung
    ascending_count = len(cross_patterns["all_ascending"])
    if ascending_count >= 3:
        unusual.append({
            "pattern": "Aufsteigende-Ziffern-Cluster",
            "description": f"{ascending_count} Zahlen mit aufsteigenden Ziffern (12,23,34...)",
            "significance": "Mittel - Strukturiertes Muster",
            "values": cross_patterns["all_ascending"],
            "count": ascending_count
        })

    # 3. Palindrom-Praesenz
    palindrome_count = len(cross_patterns["all_palindromes"])
    if palindrome_count >= 2:
        unusual.append({
            "pattern": "Palindrom-Praesenz",
            "description": f"{palindrome_count} Palindrome (11,22,33..66)",
            "significance": "Niedrig - Aber merkwuerdig bei kleinem Pool",
            "values": cross_patterns["all_palindromes"],
            "count": palindrome_count
        })

    # 4. Digitale Wurzel Verteilung
    root_freq = cross_patterns["total_digital_root_frequency"]
    # Pruefe auf Anomalien (erwarteter Wert: ~3.3 pro Wurzel bei 30 Zahlen)
    expected_per_root = 30 / 9
    anomalies = []
    for root, count in root_freq.items():
        if int(count) >= expected_per_root * 2:  # Doppelt so haeufig
            anomalies.append({"root": root, "count": count})
        elif int(count) == 0:  # Komplett fehlend
            anomalies.append({"root": root, "count": 0, "missing": True})

    if anomalies:
        unusual.append({
            "pattern": "Digitale-Wurzel-Anomalie",
            "description": "Ungleichmaessige Verteilung der Quersummen mod 9",
            "significance": "Hoch - Koennte algorithmisch sein",
            "anomalies": anomalies
        })

    # 5. Erste-Ziffer-Deviation von Benford
    first_freq = cross_patterns["total_first_digit_frequency"]
    # Bei KENO 1-70 ist Benford nicht perfekt anwendbar, aber Abweichungen interessant
    if int(first_freq.get("6", 0)) >= 8:  # Viele 6x-Zahlen
        unusual.append({
            "pattern": "Hohe-Dekade-Praeferenz",
            "description": f"{first_freq.get('6', 0)} Zahlen beginnen mit 6 (60-69)",
            "significance": "Mittel - Ungewoehnlich bei zufaelliger Wahl",
            "values": first_freq
        })

    # 6. Ziffern-Frequenz-Anomalien
    digit_freq = cross_patterns["total_digit_frequency"]
    total_digits = sum(int(v) for v in digit_freq.values())
    expected_per_digit = total_digits / 10

    over_represented = []
    under_represented = []
    for digit, count in digit_freq.items():
        ratio = int(count) / expected_per_digit if expected_per_digit > 0 else 0
        if ratio >= 1.5:
            over_represented.append({"digit": digit, "count": count, "ratio": round(ratio, 2)})
        elif ratio <= 0.5:
            under_represented.append({"digit": digit, "count": count, "ratio": round(ratio, 2)})

    if over_represented or under_represented:
        unusual.append({
            "pattern": "Ziffern-Frequenz-Bias",
            "description": "Bestimmte Ziffern ueber/unter-repraesentiert",
            "significance": "Hoch - Deutet auf nicht-zufaellige Auswahl",
            "over_represented": over_represented,
            "under_represented": under_represented,
            "expected_per_digit": round(expected_per_digit, 2)
        })

    # 7. Gemeinsame Zahlen ueber Kombinationen
    common = cross_patterns["common_numbers_all"]
    if common:
        unusual.append({
            "pattern": "Gemeinsame-Zahlen",
            "description": f"Zahlen die in ALLEN Kombinationen vorkommen",
            "significance": "Sehr Hoch - Bei unabhaengigen Ziehungen extrem unwahrscheinlich",
            "values": common
        })

    # 8. Paarweise gemeinsame Zahlen
    for pair_name, common_nums in cross_patterns["common_pairs"].items():
        if len(common_nums) >= 2:
            unusual.append({
                "pattern": f"Paarweise-Ueberschneidung ({pair_name})",
                "description": f"{len(common_nums)} gemeinsame Zahlen",
                "significance": "Mittel-Hoch",
                "values": common_nums
            })

    return unusual


def main():
    """Hauptfunktion."""
    # Die 3 Gewinner-Kombinationen
    combinations_raw = [
        {"name": "Kyritz", "numbers": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]},
        {"name": "Oberbayern", "numbers": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68]},
        {"name": "Nordsachsen", "numbers": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67]},
    ]

    # Einzelanalysen
    analyzed = []
    for combo in combinations_raw:
        analysis = analyze_combination(combo["numbers"], combo["name"])
        analyzed.append(analysis)

    # Cross-Combination Patterns
    cross_patterns = find_cross_combination_patterns(analyzed)

    # Ungewoehnliche Muster
    unusual_patterns = identify_unusual_patterns(analyzed, cross_patterns)

    # Zusammenfassung
    result = {
        "title": "Ziffern-Muster-Analyse: 3 verifizierte KENO-Typ10-Gewinne",
        "combinations_analyzed": 3,
        "total_numbers": 30,
        "individual_analyses": analyzed,
        "cross_combination_patterns": cross_patterns,
        "unusual_patterns": unusual_patterns,
        "summary": {
            "total_palindromes": len(cross_patterns["all_palindromes"]),
            "total_ascending": len(cross_patterns["all_ascending"]),
            "total_descending": len(cross_patterns["all_descending"]),
            "mirror_pairs_found": len(cross_patterns["all_mirror_pairs"]),
            "common_numbers_all": cross_patterns["common_numbers_all"],
            "unusual_pattern_count": len(unusual_patterns)
        },
        "interpretation": {
            "key_findings": [],
            "algorithmic_indicators": [],
            "human_unlikely_patterns": []
        }
    }

    # Key Findings generieren
    if cross_patterns["common_numbers_all"]:
        result["interpretation"]["key_findings"].append(
            f"KRITISCH: Zahlen {cross_patterns['common_numbers_all']} erscheinen in ALLEN Kombinationen"
        )

    # Endziffer-Analyse
    last_freq = cross_patterns["total_last_digit_frequency"]
    top_last = sorted(last_freq.items(), key=lambda x: -int(x[1]))[:3]
    result["interpretation"]["key_findings"].append(
        f"Top-3 Endziffern: {top_last[0][0]} ({top_last[0][1]}x), {top_last[1][0]} ({top_last[1][1]}x), {top_last[2][0]} ({top_last[2][1]}x)"
    )

    # Erste-Ziffer-Analyse
    first_freq = cross_patterns["total_first_digit_frequency"]
    top_first = sorted(first_freq.items(), key=lambda x: -int(x[1]))[:3]
    result["interpretation"]["key_findings"].append(
        f"Top-3 Anfangsziffern: {top_first[0][0]} ({top_first[0][1]}x), {top_first[1][0]} ({top_first[1][1]}x), {top_first[2][0]} ({top_first[2][1]}x)"
    )

    # Algorithmische Indikatoren
    digit_freq = cross_patterns["total_digit_frequency"]
    most_common_digit = max(digit_freq.items(), key=lambda x: int(x[1]))
    least_common_digit = min(digit_freq.items(), key=lambda x: int(x[1]))
    result["interpretation"]["algorithmic_indicators"].append(
        f"Haeufigste Ziffer: {most_common_digit[0]} ({most_common_digit[1]}x)"
    )
    result["interpretation"]["algorithmic_indicators"].append(
        f"Seltenste Ziffer: {least_common_digit[0]} ({least_common_digit[1]}x)"
    )

    # Spezifische Muster
    for pattern in unusual_patterns:
        if pattern.get("significance", "").startswith("Hoch") or pattern.get("significance", "").startswith("Sehr"):
            result["interpretation"]["human_unlikely_patterns"].append(pattern["description"])

    # Speichern
    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/digit_pattern_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Analyse gespeichert: {output_path}")

    # Console Output
    print("\n" + "="*70)
    print("ZIFFERN-MUSTER-ANALYSE: 3 VERIFIZIERTE KENO-TYP10-GEWINNE")
    print("="*70)

    print("\n--- EINZELANALYSEN ---")
    for combo in analyzed:
        print(f"\n{combo['name']}: {combo['numbers']}")
        print(f"  Ziffernsumme gesamt: {combo['total_digit_sum']}")
        print(f"  Palindrome: {combo['palindromes']}")
        print(f"  Aufsteigende Ziffern: {combo['ascending_digit_numbers']}")
        print(f"  Absteigende Ziffern: {combo['descending_digit_numbers']}")
        print(f"  Spiegelpaare: {combo['mirror_pairs']}")

    print("\n--- CROSS-KOMBINATION MUSTER ---")
    print(f"Gemeinsame Zahlen (alle): {cross_patterns['common_numbers_all']}")
    print(f"Alle Palindrome: {cross_patterns['all_palindromes']}")
    print(f"Alle aufsteigenden: {cross_patterns['all_ascending']}")

    print("\n--- ZIFFERN-FREQUENZ (GESAMT) ---")
    for digit in range(10):
        count = digit_freq.get(str(digit), 0)
        bar = "#" * int(count)
        print(f"  {digit}: {bar} ({count})")

    print("\n--- ENDZIFFER-FREQUENZ ---")
    for digit in range(10):
        count = last_freq.get(str(digit), 0)
        bar = "#" * int(count)
        print(f"  {digit}: {bar} ({count})")

    print("\n--- ERSTE-ZIFFER-FREQUENZ ---")
    for digit in range(1, 8):
        count = first_freq.get(str(digit), 0)
        bar = "#" * int(count)
        print(f"  {digit}: {bar} ({count})")

    print("\n--- UNGEWOEHNLICHE MUSTER ---")
    for pattern in unusual_patterns:
        print(f"\n  [{pattern['significance']}] {pattern['pattern']}")
        print(f"    {pattern['description']}")

    print("\n" + "="*70)

    return result


if __name__ == "__main__":
    main()
