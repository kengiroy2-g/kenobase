#!/usr/bin/env python
"""
Bit Pattern Analysis for Verified KENO Winner Combinations

Analyzes binary/bit patterns looking for potential checksum or
engineering patterns in the winning number combinations.
"""

import json
from collections import Counter
from pathlib import Path


def to_binary(n: int, bits: int = 7) -> str:
    """Convert number to binary string with specified bit width."""
    return format(n, f'0{bits}b')


def popcount(n: int) -> int:
    """Count the number of set bits (1s) in a number."""
    return bin(n).count('1')


def hamming_distance(a: int, b: int) -> int:
    """Calculate Hamming distance between two numbers."""
    return popcount(a ^ b)


def analyze_combination(numbers: list[int], name: str) -> dict:
    """Perform comprehensive bit analysis on a single combination."""

    # Binary representations
    binary_repr = {n: to_binary(n) for n in numbers}

    # Popcount per number
    popcounts = {n: popcount(n) for n in numbers}
    total_popcount = sum(popcounts.values())

    # XOR all numbers
    xor_result = 0
    for n in numbers:
        xor_result ^= n

    # AND all numbers
    and_result = numbers[0]
    for n in numbers[1:]:
        and_result &= n

    # OR all numbers
    or_result = 0
    for n in numbers:
        or_result |= n

    # Parity of bit sum
    parity = total_popcount % 2

    # Hamming distances between consecutive numbers
    sorted_nums = sorted(numbers)
    hamming_distances = []
    for i in range(len(sorted_nums) - 1):
        hd = hamming_distance(sorted_nums[i], sorted_nums[i+1])
        hamming_distances.append({
            "pair": [sorted_nums[i], sorted_nums[i+1]],
            "distance": hd
        })

    avg_hamming = sum(h["distance"] for h in hamming_distances) / len(hamming_distances)

    # Bit position frequencies (which bits are set how often)
    bit_positions = {i: 0 for i in range(7)}  # bits 0-6
    for n in numbers:
        for bit in range(7):
            if n & (1 << bit):
                bit_positions[bit] += 1

    # Analyze bit patterns
    # Check if XOR has special properties
    xor_properties = {
        "value": xor_result,
        "binary": to_binary(xor_result),
        "popcount": popcount(xor_result),
        "is_power_of_2": xor_result > 0 and (xor_result & (xor_result - 1)) == 0,
        "is_mersenne": bin(xor_result + 1).count('1') == 1 if xor_result > 0 else False,
        "mod_7": xor_result % 7,
        "mod_10": xor_result % 10,
        "mod_70": xor_result % 70
    }

    # Sum analysis
    total_sum = sum(numbers)

    return {
        "name": name,
        "numbers": numbers,
        "binary_representations": binary_repr,
        "popcount_per_number": popcounts,
        "total_popcount": total_popcount,
        "xor_all": xor_properties,
        "and_all": {
            "value": and_result,
            "binary": to_binary(and_result),
            "meaning": "Common bits in ALL numbers"
        },
        "or_all": {
            "value": or_result,
            "binary": to_binary(or_result),
            "meaning": "Bits set in ANY number"
        },
        "parity": {
            "total_bits": total_popcount,
            "parity": parity,
            "parity_name": "even" if parity == 0 else "odd"
        },
        "hamming_distances": {
            "consecutive_pairs": hamming_distances,
            "average": round(avg_hamming, 3),
            "min": min(h["distance"] for h in hamming_distances),
            "max": max(h["distance"] for h in hamming_distances)
        },
        "bit_position_frequencies": {
            f"bit_{i}": bit_positions[i] for i in range(7)
        },
        "sum_analysis": {
            "total_sum": total_sum,
            "sum_mod_70": total_sum % 70,
            "sum_binary": to_binary(total_sum, 10),
            "sum_popcount": popcount(total_sum)
        }
    }


def cross_combination_analysis(combinations: list[dict]) -> dict:
    """Analyze patterns across all combinations."""

    all_xors = [c["xor_all"]["value"] for c in combinations]
    all_popcounts = [c["total_popcount"] for c in combinations]
    all_parities = [c["parity"]["parity"] for c in combinations]
    all_sums = [c["sum_analysis"]["total_sum"] for c in combinations]

    # XOR of all XORs
    meta_xor = 0
    for x in all_xors:
        meta_xor ^= x

    # Aggregate bit position frequencies
    aggregate_bit_freq = {f"bit_{i}": 0 for i in range(7)}
    for c in combinations:
        for i in range(7):
            aggregate_bit_freq[f"bit_{i}"] += c["bit_position_frequencies"][f"bit_{i}"]

    # Check for checksum patterns
    checksum_analysis = {
        "xor_checksum": {
            "all_xors": all_xors,
            "meta_xor": meta_xor,
            "meta_xor_binary": to_binary(meta_xor),
            "observation": "XOR of all XORs"
        },
        "sum_checksum": {
            "all_sums": all_sums,
            "total_sum": sum(all_sums),
            "average_sum": round(sum(all_sums) / len(all_sums), 2),
            "sum_mod_patterns": {
                "mod_7": [s % 7 for s in all_sums],
                "mod_10": [s % 10 for s in all_sums],
                "mod_70": [s % 70 for s in all_sums]
            }
        },
        "popcount_checksum": {
            "all_popcounts": all_popcounts,
            "total_popcount": sum(all_popcounts),
            "average_popcount": round(sum(all_popcounts) / len(all_popcounts), 2),
            "popcount_range": max(all_popcounts) - min(all_popcounts)
        },
        "parity_checksum": {
            "all_parities": all_parities,
            "all_same": len(set(all_parities)) == 1,
            "xor_parities": all_parities[0] ^ all_parities[1] ^ all_parities[2]
        }
    }

    # Bit position analysis across all
    most_common_bits = sorted(aggregate_bit_freq.items(), key=lambda x: x[1], reverse=True)

    # Expected frequency if random (each number has ~50% chance per bit)
    expected_per_bit = 30 * 0.5  # 30 numbers total, 50% chance each

    bit_deviation = {}
    for bit_name, freq in aggregate_bit_freq.items():
        bit_idx = int(bit_name.split('_')[1])
        # For KENO 1-70, different bits have different expected frequencies
        # Bit 6 (64): numbers 64-70 = 7 numbers, so 7/70 * 30 = 3 expected
        # Bit 5 (32): numbers 32-63 + 64-70 = 39 numbers, so 39/70 * 30 = 16.7 expected
        # etc.
        expected = {
            0: 15,   # ~50% of numbers are odd
            1: 15,   # ~50% have bit 1 set (2,3,6,7,10,11...)
            2: 15,   # ~50% have bit 2 set (4-7,12-15,20-23...)
            3: 15,   # ~50% have bit 3 set (8-15,24-31,40-47,56-63)
            4: 15,   # ~50% have bit 4 set (16-31,48-63)
            5: 16.7, # 32-70 have bit 5 or 6
            6: 3,    # only 64-70 have bit 6
        }
        bit_deviation[bit_name] = {
            "observed": freq,
            "expected_approx": expected.get(bit_idx, 15),
            "deviation": round(freq - expected.get(bit_idx, 15), 2)
        }

    return {
        "cross_analysis": checksum_analysis,
        "aggregate_bit_frequencies": aggregate_bit_freq,
        "most_to_least_common_bits": most_common_bits,
        "bit_deviation_from_expected": bit_deviation,
        "potential_patterns": []
    }


def identify_engineering_patterns(combinations: list[dict], cross: dict) -> list[str]:
    """Identify potential engineering/checksum patterns."""

    patterns = []

    # Check 1: Consistent parity
    parities = [c["parity"]["parity"] for c in combinations]
    if len(set(parities)) == 1:
        patterns.append(f"PATTERN: All combinations have {parities[0]} ({'even' if parities[0]==0 else 'odd'}) total bit parity")

    # Check 2: XOR range
    xors = [c["xor_all"]["value"] for c in combinations]
    if max(xors) - min(xors) < 20:
        patterns.append(f"PATTERN: XOR values clustered in narrow range ({min(xors)}-{max(xors)})")

    # Check 3: Popcount consistency
    pops = [c["total_popcount"] for c in combinations]
    if max(pops) - min(pops) <= 3:
        patterns.append(f"PATTERN: Total popcounts very consistent ({min(pops)}-{max(pops)})")

    # Check 4: Sum range
    sums = [c["sum_analysis"]["total_sum"] for c in combinations]
    if max(sums) - min(sums) < 50:
        patterns.append(f"PATTERN: Sums clustered in narrow range ({min(sums)}-{max(sums)})")

    # Check 5: Specific bit always/never set
    for i in range(7):
        bit_key = f"bit_{i}"
        freq = cross["aggregate_bit_frequencies"][bit_key]
        if freq == 30:  # All 30 numbers have this bit
            patterns.append(f"PATTERN: Bit {i} (value {2**i}) set in ALL numbers")
        elif freq == 0:  # No numbers have this bit
            patterns.append(f"PATTERN: Bit {i} (value {2**i}) NEVER set")

    # Check 6: XOR divisibility
    for c in combinations:
        xor_val = c["xor_all"]["value"]
        if xor_val % 7 == 0:
            patterns.append(f"OBSERVATION: {c['name']} XOR ({xor_val}) divisible by 7")
        if xor_val % 10 == 0:
            patterns.append(f"OBSERVATION: {c['name']} XOR ({xor_val}) divisible by 10")

    # Check 7: Hamming distance patterns
    for c in combinations:
        avg_hd = c["hamming_distances"]["average"]
        if 2.5 <= avg_hd <= 3.5:
            patterns.append(f"OBSERVATION: {c['name']} has moderate avg Hamming distance ({avg_hd})")

    # Check 8: Sum mod patterns
    sum_mod7 = [c["sum_analysis"]["total_sum"] % 7 for c in combinations]
    if len(set(sum_mod7)) == 1:
        patterns.append(f"PATTERN: All sums have same mod 7 value ({sum_mod7[0]})")

    sum_mod10 = [c["sum_analysis"]["total_sum"] % 10 for c in combinations]
    if len(set(sum_mod10)) == 1:
        patterns.append(f"PATTERN: All sums have same mod 10 value ({sum_mod10[0]})")

    return patterns


def main():
    """Main analysis function."""

    # The 3 verified winner combinations
    winner_combinations = [
        {"name": "Kyritz", "numbers": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66]},
        {"name": "Oberbayern", "numbers": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68]},
        {"name": "Nordsachsen", "numbers": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67]},
    ]

    print("=" * 70)
    print("BIT PATTERN ANALYSIS - VERIFIED KENO WINNERS")
    print("=" * 70)

    # Analyze each combination
    analyzed = []
    for combo in winner_combinations:
        result = analyze_combination(combo["numbers"], combo["name"])
        analyzed.append(result)

        print(f"\n{'='*70}")
        print(f"COMBINATION: {combo['name']}")
        print(f"Numbers: {combo['numbers']}")
        print("-" * 70)

        print("\nBinary Representations (7-bit):")
        for n, b in result["binary_representations"].items():
            print(f"  {n:2d} = {b} (popcount: {result['popcount_per_number'][n]})")

        print(f"\nTotal Popcount: {result['total_popcount']}")
        print(f"Parity: {result['parity']['parity_name']} ({result['parity']['parity']})")

        print(f"\nXOR of all numbers:")
        xor = result["xor_all"]
        print(f"  Value: {xor['value']} = {xor['binary']}")
        print(f"  Popcount: {xor['popcount']}")
        print(f"  Is power of 2: {xor['is_power_of_2']}")
        print(f"  Mod 7: {xor['mod_7']}, Mod 10: {xor['mod_10']}, Mod 70: {xor['mod_70']}")

        print(f"\nAND of all numbers: {result['and_all']['value']} = {result['and_all']['binary']}")
        print(f"OR of all numbers: {result['or_all']['value']} = {result['or_all']['binary']}")

        print(f"\nHamming Distances (consecutive sorted):")
        print(f"  Average: {result['hamming_distances']['average']}")
        print(f"  Range: {result['hamming_distances']['min']} - {result['hamming_distances']['max']}")

        print(f"\nBit Position Frequencies:")
        for i in range(6, -1, -1):  # Print from MSB to LSB
            freq = result["bit_position_frequencies"][f"bit_{i}"]
            bar = "#" * freq
            print(f"  Bit {i} (val {2**i:2d}): {freq:2d}/10 {bar}")

        print(f"\nSum Analysis:")
        print(f"  Total: {result['sum_analysis']['total_sum']}")
        print(f"  Mod 70: {result['sum_analysis']['sum_mod_70']}")
        print(f"  Binary: {result['sum_analysis']['sum_binary']}")

    # Cross-combination analysis
    cross = cross_combination_analysis(analyzed)

    print(f"\n{'='*70}")
    print("CROSS-COMBINATION ANALYSIS")
    print("=" * 70)

    print("\nXOR Values:")
    xors = [c["xor_all"]["value"] for c in analyzed]
    for i, c in enumerate(analyzed):
        print(f"  {c['name']}: {c['xor_all']['value']} = {c['xor_all']['binary']}")
    print(f"  Meta-XOR (XOR of XORs): {cross['cross_analysis']['xor_checksum']['meta_xor']} = {cross['cross_analysis']['xor_checksum']['meta_xor_binary']}")

    print("\nPopcount Analysis:")
    pops = cross['cross_analysis']['popcount_checksum']
    print(f"  All popcounts: {pops['all_popcounts']}")
    print(f"  Total: {pops['total_popcount']}")
    print(f"  Average: {pops['average_popcount']}")
    print(f"  Range: {pops['popcount_range']}")

    print("\nSum Analysis:")
    sums = cross['cross_analysis']['sum_checksum']
    print(f"  All sums: {sums['all_sums']}")
    print(f"  Total: {sums['total_sum']}")
    print(f"  Average: {sums['average_sum']}")
    print(f"  Mod 7 pattern: {sums['sum_mod_patterns']['mod_7']}")
    print(f"  Mod 10 pattern: {sums['sum_mod_patterns']['mod_10']}")

    print("\nAggregate Bit Frequencies (30 numbers total):")
    for i in range(6, -1, -1):
        freq = cross["aggregate_bit_frequencies"][f"bit_{i}"]
        dev = cross["bit_deviation_from_expected"][f"bit_{i}"]
        bar = "#" * freq
        print(f"  Bit {i} (val {2**i:2d}): {freq:2d}/30 (expected ~{dev['expected_approx']:.1f}, dev: {dev['deviation']:+.1f}) {bar}")

    # Identify patterns
    patterns = identify_engineering_patterns(analyzed, cross)
    cross["potential_patterns"] = patterns

    print(f"\n{'='*70}")
    print("IDENTIFIED PATTERNS / OBSERVATIONS")
    print("=" * 70)
    for p in patterns:
        print(f"  * {p}")

    if not patterns:
        print("  No obvious engineering patterns detected.")

    # Compile final results
    results = {
        "analysis_type": "Binary/Bit Pattern Analysis",
        "description": "Analysis of bit patterns in verified KENO Typ-10 winner combinations",
        "methodology": {
            "binary_representation": "7-bit representation (sufficient for 1-70)",
            "popcount": "Number of set bits (1s) per number",
            "xor": "XOR of all 10 numbers reveals bit balance",
            "and": "AND shows bits common to ALL numbers",
            "or": "OR shows all bits used by ANY number",
            "hamming_distance": "Bit differences between consecutive numbers",
            "checksum_search": "Looking for patterns an engineer might implement"
        },
        "combinations_analyzed": analyzed,
        "cross_combination_analysis": cross,
        "potential_engineering_patterns": patterns,
        "summary": {
            "total_numbers_analyzed": 30,
            "xor_values": [c["xor_all"]["value"] for c in analyzed],
            "popcount_range": [min(c["total_popcount"] for c in analyzed),
                              max(c["total_popcount"] for c in analyzed)],
            "sum_range": [min(c["sum_analysis"]["total_sum"] for c in analyzed),
                         max(c["sum_analysis"]["total_sum"] for c in analyzed)],
            "parity_pattern": [c["parity"]["parity_name"] for c in analyzed]
        }
    }

    # Save results
    output_path = Path("C:/Users/kenfu/Documents/keno_base/results/bit_pattern_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"Results saved to: {output_path}")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
