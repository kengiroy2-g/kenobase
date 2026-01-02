"""
Analyse nicht-menschlicher mathematischer Eigenschaften von KENO-Gewinnerkombinationen.

Untersucht Eigenschaften die ein Algorithmus nutzen koennte, aber ein Mensch
nicht intuitiv pruefen wuerde.
"""

import hashlib
import math
from collections import Counter
from typing import Callable

import numpy as np


# =============================================================================
# DATEN
# =============================================================================

WINNERS = {
    "Kyritz": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],
    "Oberbayern": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68],
    "Nordsachsen": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67],
}

NON_WINNERS = {
    "Kyritz_NW": [2, 9, 19, 35, 39, 49, 54, 55, 62, 64],
    "Oberbayern_NW": [6, 13, 24, 36, 38, 40, 43, 51, 56, 63],
    "Nordsachsen_NW": [3, 7, 12, 13, 16, 17, 21, 36, 52, 54],
}


# =============================================================================
# PRIMZAHLEN UND FIBONACCI
# =============================================================================

def is_prime(n: int) -> bool:
    """Prueft ob n eine Primzahl ist."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def prime_factorization(n: int) -> list[int]:
    """Gibt die Primfaktorzerlegung zurueck."""
    if n < 2:
        return []
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def count_prime_factors(n: int) -> int:
    """Anzahl der Primfaktoren (mit Vielfachheit)."""
    return len(prime_factorization(n))


def count_distinct_prime_factors(n: int) -> int:
    """Anzahl verschiedener Primfaktoren."""
    return len(set(prime_factorization(n)))


PRIMES_TO_100 = [p for p in range(2, 101) if is_prime(p)]
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]


def distance_to_nearest_prime(n: int) -> int:
    """Abstand zur naechsten Primzahl."""
    if is_prime(n):
        return 0
    lower = upper = n
    while True:
        lower -= 1
        upper += 1
        if lower >= 2 and is_prime(lower):
            return n - lower
        if is_prime(upper):
            return upper - n


def distance_to_nearest_fibonacci(n: int) -> int:
    """Abstand zur naechsten Fibonacci-Zahl."""
    return min(abs(n - f) for f in FIBONACCI)


# =============================================================================
# BINAER-EIGENSCHAFTEN
# =============================================================================

def count_ones_in_binary(n: int) -> int:
    """Anzahl der 1-Bits in der Binaerdarstellung (Popcount)."""
    return bin(n).count('1')


def binary_length(n: int) -> int:
    """Laenge der Binaerdarstellung."""
    return n.bit_length()


def leading_zeros_mod8(n: int) -> int:
    """Fuehrende Nullen wenn auf 8 Bit aufgefuellt."""
    return 8 - n.bit_length() if n < 256 else 0


def binary_palindrome(n: int) -> bool:
    """Ist die Binaerdarstellung ein Palindrom?"""
    b = bin(n)[2:]
    return b == b[::-1]


def binary_alternating(n: int) -> bool:
    """Hat die Binaerdarstellung alternierende Bits (wie 0101)?"""
    b = bin(n)[2:]
    for i in range(len(b) - 1):
        if b[i] == b[i + 1]:
            return False
    return True


# =============================================================================
# QUERSUMME UND DIGITALE WURZEL
# =============================================================================

def digit_sum(n: int) -> int:
    """Quersumme."""
    return sum(int(d) for d in str(n))


def digital_root(n: int) -> int:
    """Iterierte Quersumme bis einstellig."""
    while n >= 10:
        n = digit_sum(n)
    return n


def digit_product(n: int) -> int:
    """Produkt aller Ziffern."""
    result = 1
    for d in str(n):
        result *= int(d)
    return result


# =============================================================================
# MODULO-MUSTER
# =============================================================================

def modulo_pattern(numbers: list[int], mod: int) -> list[int]:
    """Reste bei Division durch mod."""
    return [n % mod for n in numbers]


def modulo_distribution(numbers: list[int], mod: int) -> dict[int, int]:
    """Verteilung der Reste."""
    return dict(Counter(n % mod for n in numbers))


def modulo_sum(numbers: list[int], mod: int) -> int:
    """Summe modulo mod."""
    return sum(numbers) % mod


# =============================================================================
# HASH-BASIERTE EIGENSCHAFTEN
# =============================================================================

def hash_combination(numbers: list[int], algorithm: str = "md5") -> str:
    """Hash der sortierten Kombination."""
    sorted_nums = sorted(numbers)
    data = ",".join(str(n) for n in sorted_nums).encode()
    if algorithm == "md5":
        return hashlib.md5(data).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data).hexdigest()
    return ""


def hash_first_byte(numbers: list[int]) -> int:
    """Erstes Byte des MD5-Hash als Zahl."""
    h = hash_combination(numbers, "md5")
    return int(h[:2], 16)


def hash_mod_70(numbers: list[int]) -> int:
    """MD5-Hash modulo 70 (KENO-Zahlenraum)."""
    h = hash_combination(numbers, "md5")
    return int(h, 16) % 70


# =============================================================================
# KOMBINATORISCHE EIGENSCHAFTEN
# =============================================================================

def consecutive_pairs(numbers: list[int]) -> int:
    """Anzahl aufeinanderfolgender Zahlenpaare."""
    sorted_nums = sorted(numbers)
    count = 0
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i + 1] - sorted_nums[i] == 1:
            count += 1
    return count


def gap_pattern(numbers: list[int]) -> list[int]:
    """Abstände zwischen aufeinanderfolgenden Zahlen."""
    sorted_nums = sorted(numbers)
    return [sorted_nums[i + 1] - sorted_nums[i] for i in range(len(sorted_nums) - 1)]


def gap_variance(numbers: list[int]) -> float:
    """Varianz der Abstände."""
    gaps = gap_pattern(numbers)
    return float(np.var(gaps))


def gap_entropy(numbers: list[int]) -> float:
    """Entropie der Luecken-Verteilung."""
    gaps = gap_pattern(numbers)
    gap_counts = Counter(gaps)
    total = len(gaps)
    entropy = 0.0
    for count in gap_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def sum_of_squares(numbers: list[int]) -> int:
    """Summe der Quadrate."""
    return sum(n * n for n in numbers)


def product_mod_1000(numbers: list[int]) -> int:
    """Produkt aller Zahlen modulo 1000."""
    result = 1
    for n in numbers:
        result = (result * n) % 1000
    return result


# =============================================================================
# PHYSIK-INSPIRIERTE METRIKEN
# =============================================================================

def center_of_mass(numbers: list[int]) -> float:
    """Schwerpunkt der Zahlen."""
    return sum(numbers) / len(numbers)


def moment_of_inertia(numbers: list[int]) -> float:
    """Traegheitsmoment bezogen auf Schwerpunkt."""
    com = center_of_mass(numbers)
    return sum((n - com) ** 2 for n in numbers)


def spread_ratio(numbers: list[int]) -> float:
    """Verhaeltnis max-min zu Mittelwert."""
    sorted_nums = sorted(numbers)
    spread = sorted_nums[-1] - sorted_nums[0]
    return spread / center_of_mass(numbers)


# =============================================================================
# XOR-BASIERTE EIGENSCHAFTEN
# =============================================================================

def xor_all(numbers: list[int]) -> int:
    """XOR aller Zahlen."""
    result = 0
    for n in numbers:
        result ^= n
    return result


def xor_checksum(numbers: list[int]) -> int:
    """XOR-Pruefsumme modulo 256."""
    return xor_all(numbers) % 256


def parity_count(numbers: list[int]) -> int:
    """Anzahl der Zahlen mit ungerader Paritaet (ungerade Anzahl 1-Bits)."""
    return sum(1 for n in numbers if count_ones_in_binary(n) % 2 == 1)


# =============================================================================
# ANALYSE-FUNKTIONEN
# =============================================================================

def analyze_single_number(n: int) -> dict:
    """Analysiert eine einzelne Zahl."""
    return {
        "value": n,
        "is_prime": is_prime(n),
        "prime_factors": prime_factorization(n),
        "num_prime_factors": count_prime_factors(n),
        "distinct_prime_factors": count_distinct_prime_factors(n),
        "dist_to_prime": distance_to_nearest_prime(n),
        "dist_to_fibonacci": distance_to_nearest_fibonacci(n),
        "binary": bin(n)[2:],
        "popcount": count_ones_in_binary(n),
        "binary_length": binary_length(n),
        "binary_palindrome": binary_palindrome(n),
        "digit_sum": digit_sum(n),
        "digital_root": digital_root(n),
        "mod_7": n % 7,
        "mod_11": n % 11,
        "mod_13": n % 13,
    }


def analyze_combination(name: str, numbers: list[int]) -> dict:
    """Analysiert eine Kombination."""
    return {
        "name": name,
        "numbers": numbers,
        "sum": sum(numbers),
        "mean": center_of_mass(numbers),
        "sum_of_squares": sum_of_squares(numbers),
        "product_mod_1000": product_mod_1000(numbers),

        # Primzahl-Eigenschaften
        "prime_count": sum(1 for n in numbers if is_prime(n)),
        "total_prime_factors": sum(count_prime_factors(n) for n in numbers),
        "avg_dist_to_prime": sum(distance_to_nearest_prime(n) for n in numbers) / len(numbers),
        "avg_dist_to_fib": sum(distance_to_nearest_fibonacci(n) for n in numbers) / len(numbers),

        # Binaer-Eigenschaften
        "total_popcount": sum(count_ones_in_binary(n) for n in numbers),
        "avg_popcount": sum(count_ones_in_binary(n) for n in numbers) / len(numbers),
        "binary_palindrome_count": sum(1 for n in numbers if binary_palindrome(n)),

        # Quersumme
        "total_digit_sum": sum(digit_sum(n) for n in numbers),
        "digital_roots": [digital_root(n) for n in numbers],
        "digital_root_distribution": dict(Counter(digital_root(n) for n in numbers)),

        # Modulo-Muster
        "mod_7_pattern": modulo_pattern(numbers, 7),
        "mod_7_sum": modulo_sum(numbers, 7),
        "mod_7_distribution": modulo_distribution(numbers, 7),
        "mod_11_pattern": modulo_pattern(numbers, 11),
        "mod_11_sum": modulo_sum(numbers, 11),
        "mod_13_pattern": modulo_pattern(numbers, 13),
        "mod_13_sum": modulo_sum(numbers, 13),

        # Gap-Analyse
        "consecutive_pairs": consecutive_pairs(numbers),
        "gaps": gap_pattern(numbers),
        "gap_variance": gap_variance(numbers),
        "gap_entropy": gap_entropy(numbers),

        # Hash-basiert
        "md5_hash": hash_combination(numbers),
        "hash_first_byte": hash_first_byte(numbers),
        "hash_mod_70": hash_mod_70(numbers),

        # XOR-basiert
        "xor_all": xor_all(numbers),
        "xor_checksum": xor_checksum(numbers),
        "parity_count": parity_count(numbers),

        # Physik-inspiriert
        "center_of_mass": center_of_mass(numbers),
        "moment_of_inertia": moment_of_inertia(numbers),
        "spread_ratio": spread_ratio(numbers),
    }


def compare_winners_vs_non_winners():
    """Vergleicht Gewinner- mit Nicht-Gewinner-Kombinationen."""
    print("=" * 80)
    print("ANALYSE NICHT-MENSCHLICHER EIGENSCHAFTEN VON KENO-KOMBINATIONEN")
    print("=" * 80)

    winner_analyses = {name: analyze_combination(name, nums) for name, nums in WINNERS.items()}
    non_winner_analyses = {name: analyze_combination(name, nums) for name, nums in NON_WINNERS.items()}

    # Metriken zum Vergleichen
    metrics = [
        ("sum", "Summe"),
        ("prime_count", "Anzahl Primzahlen"),
        ("total_prime_factors", "Summe Primfaktoren"),
        ("avg_dist_to_prime", "Mittl. Abstand zu Primzahl"),
        ("avg_dist_to_fib", "Mittl. Abstand zu Fibonacci"),
        ("total_popcount", "Summe Popcount (1-Bits)"),
        ("avg_popcount", "Mittl. Popcount"),
        ("total_digit_sum", "Summe Quersummen"),
        ("mod_7_sum", "Summe mod 7"),
        ("mod_11_sum", "Summe mod 11"),
        ("mod_13_sum", "Summe mod 13"),
        ("consecutive_pairs", "Aufeinanderfolgende Paare"),
        ("gap_variance", "Varianz der Luecken"),
        ("gap_entropy", "Entropie der Luecken"),
        ("xor_all", "XOR aller Zahlen"),
        ("xor_checksum", "XOR Checksum mod 256"),
        ("parity_count", "Ungerade Paritaet Count"),
        ("center_of_mass", "Schwerpunkt"),
        ("moment_of_inertia", "Traegheitsmoment"),
        ("spread_ratio", "Spread Ratio"),
        ("hash_first_byte", "Hash erstes Byte"),
        ("hash_mod_70", "Hash mod 70"),
        ("product_mod_1000", "Produkt mod 1000"),
    ]

    print("\n" + "=" * 80)
    print("VERGLEICH: GEWINNER vs. NICHT-GEWINNER")
    print("=" * 80)

    print("\n{:<30} | {:^30} | {:^30}".format(
        "METRIK", "GEWINNER (Mittel)", "NICHT-GEWINNER (Mittel)"
    ))
    print("-" * 95)

    significant_differences = []

    for metric_key, metric_name in metrics:
        winner_values = [a[metric_key] for a in winner_analyses.values()]
        non_winner_values = [a[metric_key] for a in non_winner_analyses.values()]

        winner_mean = np.mean(winner_values)
        non_winner_mean = np.mean(non_winner_values)

        diff_pct = abs(winner_mean - non_winner_mean) / max(abs(winner_mean), abs(non_winner_mean), 0.001) * 100

        marker = ""
        if diff_pct > 20:
            marker = " ***"
            significant_differences.append((metric_name, winner_mean, non_winner_mean, diff_pct))
        elif diff_pct > 10:
            marker = " **"
        elif diff_pct > 5:
            marker = " *"

        print("{:<30} | {:>28.2f} | {:>28.2f}{}".format(
            metric_name, winner_mean, non_winner_mean, marker
        ))

    # Detaillierte Analyse pro Kombination
    print("\n" + "=" * 80)
    print("DETAILLIERTE ANALYSE PRO KOMBINATION")
    print("=" * 80)

    for name, analysis in {**winner_analyses, **non_winner_analyses}.items():
        is_winner = "GEWINNER" if name in WINNERS else "NICHT-GEZOGEN"
        print(f"\n--- {name} ({is_winner}) ---")
        print(f"Zahlen: {analysis['numbers']}")
        print(f"  Summe: {analysis['sum']}, Schwerpunkt: {analysis['center_of_mass']:.1f}")
        print(f"  Primzahlen: {analysis['prime_count']}, Primfaktoren gesamt: {analysis['total_prime_factors']}")
        print(f"  Popcount gesamt: {analysis['total_popcount']}, Mittel: {analysis['avg_popcount']:.2f}")
        print(f"  Digital Roots: {analysis['digital_roots']}")
        print(f"  Mod 7 Pattern: {analysis['mod_7_pattern']} (Summe: {analysis['mod_7_sum']})")
        print(f"  Mod 11 Pattern: {analysis['mod_11_pattern']} (Summe: {analysis['mod_11_sum']})")
        print(f"  Luecken: {analysis['gaps']}")
        print(f"  XOR: {analysis['xor_all']}, XOR-Checksum: {analysis['xor_checksum']}")
        print(f"  Hash-Byte: {analysis['hash_first_byte']}, Hash mod 70: {analysis['hash_mod_70']}")

    # Signifikante Unterschiede hervorheben
    if significant_differences:
        print("\n" + "=" * 80)
        print("SIGNIFIKANTE UNTERSCHIEDE (>20% Differenz)")
        print("=" * 80)
        for metric_name, w_mean, nw_mean, diff in sorted(significant_differences, key=lambda x: -x[3]):
            direction = "hoeher" if w_mean > nw_mean else "niedriger"
            print(f"  {metric_name}: Gewinner {diff:.1f}% {direction}")
            print(f"    Gewinner: {w_mean:.2f}, Nicht-Gewinner: {nw_mean:.2f}")

    # Einzelzahl-Analyse fuer spezifische Muster
    print("\n" + "=" * 80)
    print("EINZELZAHL-ANALYSE")
    print("=" * 80)

    all_winner_nums = [n for nums in WINNERS.values() for n in nums]
    all_non_winner_nums = [n for nums in NON_WINNERS.values() for n in nums]

    print("\n--- Primzahlen-Anteil ---")
    winner_primes = [n for n in all_winner_nums if is_prime(n)]
    non_winner_primes = [n for n in all_non_winner_nums if is_prime(n)]
    print(f"Gewinner: {len(winner_primes)}/{len(all_winner_nums)} = {len(winner_primes)/len(all_winner_nums)*100:.1f}%")
    print(f"  Primzahlen: {sorted(winner_primes)}")
    print(f"Nicht-Gewinner: {len(non_winner_primes)}/{len(all_non_winner_nums)} = {len(non_winner_primes)/len(all_non_winner_nums)*100:.1f}%")
    print(f"  Primzahlen: {sorted(non_winner_primes)}")

    print("\n--- Digital Root Verteilung ---")
    winner_dr = Counter(digital_root(n) for n in all_winner_nums)
    non_winner_dr = Counter(digital_root(n) for n in all_non_winner_nums)
    print(f"Gewinner: {dict(sorted(winner_dr.items()))}")
    print(f"Nicht-Gewinner: {dict(sorted(non_winner_dr.items()))}")

    print("\n--- Popcount (Anzahl 1-Bits) Verteilung ---")
    winner_pc = Counter(count_ones_in_binary(n) for n in all_winner_nums)
    non_winner_pc = Counter(count_ones_in_binary(n) for n in all_non_winner_nums)
    print(f"Gewinner: {dict(sorted(winner_pc.items()))}")
    print(f"Nicht-Gewinner: {dict(sorted(non_winner_pc.items()))}")

    print("\n--- Modulo 7 Verteilung ---")
    winner_m7 = Counter(n % 7 for n in all_winner_nums)
    non_winner_m7 = Counter(n % 7 for n in all_non_winner_nums)
    print(f"Gewinner: {dict(sorted(winner_m7.items()))}")
    print(f"Nicht-Gewinner: {dict(sorted(non_winner_m7.items()))}")

    print("\n--- Modulo 11 Verteilung ---")
    winner_m11 = Counter(n % 11 for n in all_winner_nums)
    non_winner_m11 = Counter(n % 11 for n in all_non_winner_nums)
    print(f"Gewinner: {dict(sorted(winner_m11.items()))}")
    print(f"Nicht-Gewinner: {dict(sorted(non_winner_m11.items()))}")

    # Spezielle Muster-Suche
    print("\n" + "=" * 80)
    print("SPEZIELLE MUSTER-SUCHE")
    print("=" * 80)

    # Konsistenz-Check: Welche Eigenschaften sind bei ALLEN Gewinnern gleich?
    print("\n--- Konsistente Eigenschaften bei allen Gewinnern ---")

    # Mod 7 Summe
    mod7_sums_w = [a["mod_7_sum"] for a in winner_analyses.values()]
    mod7_sums_nw = [a["mod_7_sum"] for a in non_winner_analyses.values()]
    print(f"Mod 7 Summen - Gewinner: {mod7_sums_w}, Nicht-Gewinner: {mod7_sums_nw}")

    # Mod 11 Summe
    mod11_sums_w = [a["mod_11_sum"] for a in winner_analyses.values()]
    mod11_sums_nw = [a["mod_11_sum"] for a in non_winner_analyses.values()]
    print(f"Mod 11 Summen - Gewinner: {mod11_sums_w}, Nicht-Gewinner: {mod11_sums_nw}")

    # XOR Checksum
    xor_w = [a["xor_checksum"] for a in winner_analyses.values()]
    xor_nw = [a["xor_checksum"] for a in non_winner_analyses.values()]
    print(f"XOR Checksums - Gewinner: {xor_w}, Nicht-Gewinner: {xor_nw}")

    # Parity Count
    parity_w = [a["parity_count"] for a in winner_analyses.values()]
    parity_nw = [a["parity_count"] for a in non_winner_analyses.values()]
    print(f"Parity Counts - Gewinner: {parity_w}, Nicht-Gewinner: {parity_nw}")

    # Produkt mod 1000
    prod_w = [a["product_mod_1000"] for a in winner_analyses.values()]
    prod_nw = [a["product_mod_1000"] for a in non_winner_analyses.values()]
    print(f"Produkt mod 1000 - Gewinner: {prod_w}, Nicht-Gewinner: {prod_nw}")

    # XOR-Werte genauer analysieren
    print("\n--- XOR-Analyse ---")
    for name, analysis in winner_analyses.items():
        xor_val = analysis["xor_all"]
        print(f"{name}: XOR={xor_val}, Binary={bin(xor_val)}, Popcount={count_ones_in_binary(xor_val)}")
    for name, analysis in non_winner_analyses.items():
        xor_val = analysis["xor_all"]
        print(f"{name}: XOR={xor_val}, Binary={bin(xor_val)}, Popcount={count_ones_in_binary(xor_val)}")

    # Summe der Abstände zu Primzahlen
    print("\n--- Primzahl-Nähe-Analyse ---")
    for name, nums in {**WINNERS, **NON_WINNERS}.items():
        distances = [distance_to_nearest_prime(n) for n in nums]
        print(f"{name}: Abstände={distances}, Summe={sum(distances)}, Mittel={np.mean(distances):.2f}")

    # Binaer-Muster-Analyse
    print("\n--- Binaer-Muster-Analyse ---")
    for name, nums in {**WINNERS, **NON_WINNERS}.items():
        binary_strs = [bin(n)[2:].zfill(7) for n in nums]
        # Zähle führende 1en
        leading_ones = [b.index('0') if '0' in b else len(b) for b in binary_strs]
        print(f"{name}: Leading 1s={leading_ones}, Sum={sum(leading_ones)}")


if __name__ == "__main__":
    compare_winners_vs_non_winners()
