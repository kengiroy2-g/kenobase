"""
Tiefere Analyse der signifikanten Muster aus der ersten Analyse.

Fokus auf:
1. XOR-Eigenschaften (30% Differenz)
2. Parity Count (40% Differenz)
3. Modulo-Summen (signifikante Unterschiede)
4. Fibonacci-Abstand (41% Differenz)
"""

import math
from collections import Counter
from itertools import combinations
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

FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]


def count_ones_in_binary(n: int) -> int:
    return bin(n).count('1')


def is_prime(n: int) -> bool:
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


def xor_all(numbers: list[int]) -> int:
    result = 0
    for n in numbers:
        result ^= n
    return result


def parity_count(numbers: list[int]) -> int:
    """Anzahl der Zahlen mit ungerader Anzahl 1-Bits."""
    return sum(1 for n in numbers if count_ones_in_binary(n) % 2 == 1)


print("=" * 80)
print("TIEFERE ANALYSE DER SIGNIFIKANTEN MUSTER")
print("=" * 80)

# =============================================================================
# 1. XOR-ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("1. XOR-EIGENSCHAFTEN")
print("=" * 80)

print("\nXOR aller Zahlen:")
for name, nums in {**WINNERS, **NON_WINNERS}.items():
    xor_val = xor_all(nums)
    is_winner = "WINNER" if name in WINNERS else "NON-WINNER"
    popcount = count_ones_in_binary(xor_val)

    # XOR ist interessant wenn...
    print(f"{name} ({is_winner}): XOR = {xor_val:3d} = {bin(xor_val):>12} (Popcount: {popcount})")

print("\n--- XOR-Muster-Analyse ---")
print("Hypothese: Gewinner haben höheren XOR-Wert")
winner_xors = [xor_all(nums) for nums in WINNERS.values()]
non_winner_xors = [xor_all(nums) for nums in NON_WINNERS.values()]
print(f"Gewinner XOR-Werte: {winner_xors}, Mittel: {np.mean(winner_xors):.1f}")
print(f"Nicht-Gewinner XOR-Werte: {non_winner_xors}, Mittel: {np.mean(non_winner_xors):.1f}")

# XOR-Bits analysieren
print("\n--- XOR-Bit-Positionen ---")
for name, nums in {**WINNERS, **NON_WINNERS}.items():
    xor_val = xor_all(nums)
    # Welche Bit-Positionen sind gesetzt?
    bits_set = [i for i in range(7) if xor_val & (1 << i)]
    print(f"{name}: Bits gesetzt an Position {bits_set}")

# =============================================================================
# 2. PARITY-ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("2. PARITY-ANALYSE (Anzahl Zahlen mit ungerader 1-Bit-Anzahl)")
print("=" * 80)

print("\nParity-Verteilung (Zahlen mit ungerader Anzahl 1-Bits):")
for name, nums in {**WINNERS, **NON_WINNERS}.items():
    is_winner = "WINNER" if name in WINNERS else "NON-WINNER"
    odd_parity = [n for n in nums if count_ones_in_binary(n) % 2 == 1]
    even_parity = [n for n in nums if count_ones_in_binary(n) % 2 == 0]
    print(f"\n{name} ({is_winner}):")
    print(f"  Ungerade Parität ({len(odd_parity)}): {odd_parity}")
    print(f"  Gerade Parität ({len(even_parity)}): {even_parity}")

print("\n--- Parity-Hypothese ---")
print("Gewinner haben tendenziell WENIGER Zahlen mit ungerader Parität")
winner_parity = [parity_count(nums) for nums in WINNERS.values()]
non_winner_parity = [parity_count(nums) for nums in NON_WINNERS.values()]
print(f"Gewinner Parity-Counts: {winner_parity}, Mittel: {np.mean(winner_parity):.1f}")
print(f"Nicht-Gewinner Parity-Counts: {non_winner_parity}, Mittel: {np.mean(non_winner_parity):.1f}")

# =============================================================================
# 3. MODULO-SUMMEN ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("3. MODULO-SUMMEN ANALYSE")
print("=" * 80)

for mod in [7, 11, 13, 17, 19, 23]:
    print(f"\n--- Modulo {mod} ---")
    winner_sums = [sum(nums) % mod for nums in WINNERS.values()]
    non_winner_sums = [sum(nums) % mod for nums in NON_WINNERS.values()]

    print(f"Gewinner Summen mod {mod}: {winner_sums}")
    print(f"Nicht-Gewinner Summen mod {mod}: {non_winner_sums}")

    # Teste auf Muster
    w_unique = len(set(winner_sums))
    nw_unique = len(set(non_winner_sums))
    print(f"Unique Werte: Gewinner={w_unique}, Nicht-Gewinner={nw_unique}")

# =============================================================================
# 4. FIBONACCI-NÄHE ANALYSE
# =============================================================================
print("\n" + "=" * 80)
print("4. FIBONACCI-NÄHE ANALYSE")
print("=" * 80)

def distance_to_fibonacci(n: int) -> int:
    return min(abs(n - f) for f in FIBONACCI)

def is_fibonacci(n: int) -> bool:
    return n in FIBONACCI

print("\nFibonacci-Zahlen im Bereich 1-70:", [f for f in FIBONACCI if f <= 70])

print("\n--- Fibonacci-Zahlen in Kombinationen ---")
for name, nums in {**WINNERS, **NON_WINNERS}.items():
    is_winner = "WINNER" if name in WINNERS else "NON-WINNER"
    fibs = [n for n in nums if is_fibonacci(n)]
    distances = [distance_to_fibonacci(n) for n in nums]
    print(f"{name} ({is_winner}):")
    print(f"  Fibonacci-Zahlen: {fibs}")
    print(f"  Abstände: {distances}")
    print(f"  Summe der Abstände: {sum(distances)}, Mittel: {np.mean(distances):.2f}")

# =============================================================================
# 5. KOMBINIERTE EIGENSCHAFTEN
# =============================================================================
print("\n" + "=" * 80)
print("5. KOMBINIERTE ALGORITHMUS-EIGENSCHAFTEN")
print("=" * 80)

def combined_score(numbers: list[int]) -> dict:
    """Berechnet einen kombinierten Score basierend auf nicht-menschlichen Eigenschaften."""
    xor_val = xor_all(numbers)
    parity = parity_count(numbers)
    mod11_sum = sum(numbers) % 11
    mod7_sum = sum(numbers) % 7
    fib_dist = sum(distance_to_fibonacci(n) for n in numbers)

    # Popcount des XOR
    xor_popcount = count_ones_in_binary(xor_val)

    return {
        "xor": xor_val,
        "xor_popcount": xor_popcount,
        "parity_count": parity,
        "mod7_sum": mod7_sum,
        "mod11_sum": mod11_sum,
        "fib_dist_sum": fib_dist,
        "score": (xor_val * 0.3 - parity * 10 + mod11_sum * 5 + fib_dist * 2)
    }

print("\nKombinierter Score:")
for name, nums in {**WINNERS, **NON_WINNERS}.items():
    is_winner = "WINNER" if name in WINNERS else "NON-WINNER"
    score = combined_score(nums)
    print(f"{name} ({is_winner}): Score = {score['score']:.1f}")
    print(f"  XOR={score['xor']}, XOR-Popcount={score['xor_popcount']}, Parity={score['parity_count']}")
    print(f"  Mod7={score['mod7_sum']}, Mod11={score['mod11_sum']}, FibDist={score['fib_dist_sum']}")

# =============================================================================
# 6. BITWEISE MUSTER DER GESAMTKOMBINATION
# =============================================================================
print("\n" + "=" * 80)
print("6. BITWEISE MUSTER DER GESAMTKOMBINATION")
print("=" * 80)

def analyze_bit_patterns(numbers: list[int]) -> dict:
    """Analysiert bitweise Muster über alle Zahlen."""
    # Zähle wie oft jedes Bit gesetzt ist
    bit_counts = [0] * 8
    for n in numbers:
        for i in range(8):
            if n & (1 << i):
                bit_counts[i] += 1

    # OR aller Zahlen
    or_all = 0
    for n in numbers:
        or_all |= n

    # AND aller Zahlen
    and_all = 0xFF
    for n in numbers:
        and_all &= n

    return {
        "bit_counts": bit_counts,
        "or_all": or_all,
        "and_all": and_all,
        "bit_entropy": sum(1 for c in bit_counts if c > 0 and c < len(numbers))
    }

print("\nBit-Position-Analyse (Bit 0 = LSB):")
for name, nums in {**WINNERS, **NON_WINNERS}.items():
    is_winner = "WINNER" if name in WINNERS else "NON-WINNER"
    patterns = analyze_bit_patterns(nums)
    print(f"\n{name} ({is_winner}):")
    print(f"  Bit-Counts: {patterns['bit_counts']}")
    print(f"  OR-Ergebnis: {patterns['or_all']} = {bin(patterns['or_all'])}")
    print(f"  AND-Ergebnis: {patterns['and_all']} = {bin(patterns['and_all'])}")

# =============================================================================
# 7. DIFFERENZ-ANALYSE ZWISCHEN ZAHLEN
# =============================================================================
print("\n" + "=" * 80)
print("7. DIFFERENZ-MUSTER")
print("=" * 80)

def analyze_differences(numbers: list[int]) -> dict:
    """Analysiert Differenzen zwischen allen Zahlenpaaren."""
    diffs = []
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            diffs.append(abs(numbers[i] - numbers[j]))

    # XOR der Differenzen
    xor_diffs = 0
    for d in diffs:
        xor_diffs ^= d

    return {
        "diffs": diffs,
        "xor_diffs": xor_diffs,
        "diff_sum": sum(diffs),
        "diff_mod7": sum(diffs) % 7,
        "diff_mod11": sum(diffs) % 11,
    }

print("\nDifferenz-Analyse:")
for name, nums in {**WINNERS, **NON_WINNERS}.items():
    is_winner = "WINNER" if name in WINNERS else "NON-WINNER"
    diff_analysis = analyze_differences(nums)
    print(f"{name} ({is_winner}):")
    print(f"  Summe aller Differenzen: {diff_analysis['diff_sum']}")
    print(f"  XOR der Differenzen: {diff_analysis['xor_diffs']}")
    print(f"  Diff-Summe mod 7: {diff_analysis['diff_mod7']}")
    print(f"  Diff-Summe mod 11: {diff_analysis['diff_mod11']}")

# =============================================================================
# 8. MULTIPLIKATIVE EIGENSCHAFTEN
# =============================================================================
print("\n" + "=" * 80)
print("8. MULTIPLIKATIVE EIGENSCHAFTEN")
print("=" * 80)

def multiplicative_analysis(numbers: list[int]) -> dict:
    """Analysiert multiplikative Eigenschaften."""
    # Produkt modulo verschiedener Primzahlen
    prod = 1
    for n in numbers:
        prod *= n

    return {
        "prod_mod_7": prod % 7,
        "prod_mod_11": prod % 11,
        "prod_mod_13": prod % 13,
        "prod_mod_17": prod % 17,
        "prod_mod_70": prod % 70,
    }

print("\nProdukt-Modulo-Analyse:")
for name, nums in {**WINNERS, **NON_WINNERS}.items():
    is_winner = "WINNER" if name in WINNERS else "NON-WINNER"
    mult = multiplicative_analysis(nums)
    print(f"{name} ({is_winner}): mod7={mult['prod_mod_7']}, mod11={mult['prod_mod_11']}, mod13={mult['prod_mod_13']}, mod17={mult['prod_mod_17']}, mod70={mult['prod_mod_70']}")

# =============================================================================
# 9. KONSISTENZ-CHECK: Was ist bei ALLEN Gewinnern gleich?
# =============================================================================
print("\n" + "=" * 80)
print("9. KONSISTENZ-CHECK: Gemeinsame Eigenschaften aller Gewinner")
print("=" * 80)

# Sammle alle Eigenschaften
def get_all_properties(numbers: list[int]) -> dict:
    xor_val = xor_all(numbers)
    return {
        "xor_popcount": count_ones_in_binary(xor_val),
        "xor_mod_7": xor_val % 7,
        "xor_mod_11": xor_val % 11,
        "parity": parity_count(numbers),
        "sum_mod_7": sum(numbers) % 7,
        "sum_mod_11": sum(numbers) % 11,
        "sum_mod_13": sum(numbers) % 13,
        "has_fibonacci_34": 34 in numbers,
        "has_fibonacci_55": 55 in numbers,
        "prime_count": sum(1 for n in numbers if is_prime(n)),
    }

winner_props = [get_all_properties(nums) for nums in WINNERS.values()]
non_winner_props = [get_all_properties(nums) for nums in NON_WINNERS.values()]

print("\n--- Vergleich der Eigenschaften ---")
for prop in winner_props[0].keys():
    w_values = [p[prop] for p in winner_props]
    nw_values = [p[prop] for p in non_winner_props]

    # Check auf Konsistenz
    w_consistent = len(set(w_values)) == 1
    nw_consistent = len(set(nw_values)) == 1

    marker = ""
    if w_consistent and not nw_consistent:
        marker = " <-- INTERESSANT (Gewinner konsistent)"
    elif not w_consistent and nw_consistent:
        marker = " <-- INTERESSANT (Nicht-Gewinner konsistent)"

    print(f"{prop}:")
    print(f"  Gewinner: {w_values} (konsistent: {w_consistent})")
    print(f"  Nicht-Gewinner: {nw_values} (konsistent: {nw_consistent}){marker}")

# =============================================================================
# FAZIT
# =============================================================================
print("\n" + "=" * 80)
print("FAZIT: POTENTIELLE ALGORITHMUS-SIGNATUREN")
print("=" * 80)

print("""
Basierend auf der Analyse wurden folgende potentiell nicht-zufällige Muster identifiziert:

1. XOR-WERT: Gewinner haben im Mittel höheren XOR-Wert (83.3 vs 58.3)
   -> Möglicherweise werden Zahlen so gewählt, dass bestimmte Bits togglen

2. PARITY-COUNT: Gewinner haben weniger Zahlen mit ungerader Bit-Parität
   -> Gewinner: 3.0, Nicht-Gewinner: 5.0 (40% Differenz)
   -> Dies ist ein sehr technisches Kriterium das kein Mensch prüfen würde

3. FIBONACCI-DISTANZ: Gewinner sind im Mittel weiter von Fibonacci-Zahlen entfernt
   -> Dies widerspricht der "natürlichen" Erwartung
   -> Möglicherweise werden Fibonacci-nahe Zahlen absichtlich vermieden

4. MODULO-11-SUMME: Deutlicher Unterschied (6.0 vs 3.3)
   -> 11 ist eine besondere Primzahl für Checksummen (ISBN, etc.)

5. GAP-VARIANZ: Gewinner haben höhere Varianz in den Lücken
   -> Gewinner: 27.7, Nicht-Gewinner: 20.2
   -> "Zufälliger aussehende" Verteilung bei Gewinnern

WARNUNG: Die Stichprobe (n=3 pro Gruppe) ist zu klein für statistische Signifikanz.
Diese Muster müssen an größeren Datensätzen validiert werden.
""")
