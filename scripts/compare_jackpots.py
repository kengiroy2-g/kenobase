"""
Jackpot-Vergleichs-Analyse: Kyritz vs Oberbayern

Berechnet alle Merkmale für beide Jackpots und deren "nicht-gewählte" Zahlen,
um gemeinsame Unterscheidungsmerkmale zu finden.
"""

import numpy as np
from itertools import combinations

# Jackpot-Daten
JACKPOTS = {
    "KYRITZ_2025_10_25": {
        "date": "2025-10-25",
        "drawn_20": [2, 5, 9, 12, 19, 20, 26, 34, 35, 36, 39, 42, 45, 48, 49, 54, 55, 62, 64, 66],
        "winner_10": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],
        "not_chosen_10": [2, 9, 19, 35, 39, 49, 54, 55, 62, 64],
    },
    "OBERBAYERN_2023_06_28": {
        "date": "2023-06-28",
        "drawn_20": [3, 6, 13, 15, 18, 24, 27, 36, 38, 40, 43, 47, 51, 53, 54, 55, 56, 63, 66, 68],
        "winner_10": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68],
        "not_chosen_10": [6, 13, 24, 36, 38, 40, 43, 51, 56, 63],
    }
}

def calculate_features(numbers: list[int]) -> dict:
    """Berechne alle Merkmale für eine 10er-Kombination."""
    nums = sorted(numbers)

    # Grundstatistiken
    sum_val = sum(nums)
    mean_val = np.mean(nums)
    std_val = np.std(nums)
    range_val = nums[-1] - nums[0]

    # Gerade/Ungerade
    even_count = sum(1 for n in nums if n % 2 == 0)
    odd_count = 10 - even_count

    # Primzahlen (bis 70)
    primes = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67}
    prime_count = sum(1 for n in nums if n in primes)

    # Zehnergruppen
    decades = {}
    for n in nums:
        decade = (n - 1) // 10  # 1-10=0, 11-20=1, etc.
        decades[decade] = decades.get(decade, 0) + 1
    decades_used = len(decades)
    max_per_decade = max(decades.values())

    # Abstände (Gaps)
    gaps = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
    avg_gap = np.mean(gaps)
    min_gap = min(gaps)
    max_gap = max(gaps)

    # Konsekutive Paare (Abstand = 1)
    consecutive_pairs = sum(1 for g in gaps if g == 1)

    # Endziffern-Verteilung
    end_digits = [n % 10 for n in nums]
    unique_end_digits = len(set(end_digits))

    # Dezimale Summe (Quersumme)
    digit_sum = sum(int(d) for n in nums for d in str(n))

    return {
        "sum": sum_val,
        "mean": round(mean_val, 1),
        "std": round(std_val, 1),
        "range": range_val,
        "even_count": even_count,
        "odd_count": odd_count,
        "prime_count": prime_count,
        "decades_used": decades_used,
        "max_per_decade": max_per_decade,
        "avg_gap": round(avg_gap, 1),
        "min_gap": min_gap,
        "max_gap": max_gap,
        "consecutive_pairs": consecutive_pairs,
        "unique_end_digits": unique_end_digits,
        "digit_sum": digit_sum,
    }

def main():
    print("=" * 80)
    print("JACKPOT-VERGLEICHS-ANALYSE")
    print("=" * 80)
    print()

    # Berechne Features für alle
    results = {}
    for name, data in JACKPOTS.items():
        winner_features = calculate_features(data["winner_10"])
        not_chosen_features = calculate_features(data["not_chosen_10"])

        results[name] = {
            "winner": winner_features,
            "not_chosen": not_chosen_features,
        }

        print(f"\n{'=' * 40}")
        print(f"JACKPOT: {name}")
        print(f"Datum: {data['date']}")
        print(f"{'=' * 40}")

        print(f"\nGewinner-10: {sorted(data['winner_10'])}")
        print(f"Nicht-Gew-10: {sorted(data['not_chosen_10'])}")

        print(f"\n{'Merkmal':<25} {'Gewinner':>10} {'Nicht-Gew':>10} {'Delta':>10}")
        print("-" * 55)

        for feature in winner_features.keys():
            w = winner_features[feature]
            n = not_chosen_features[feature]
            delta = w - n if isinstance(w, (int, float)) else "N/A"
            if isinstance(delta, float):
                delta = round(delta, 1)
            print(f"{feature:<25} {str(w):>10} {str(n):>10} {str(delta):>10}")

    # Cross-Jackpot Vergleich
    print("\n" + "=" * 80)
    print("CROSS-JACKPOT VERGLEICH: Gemeinsame Unterscheidungsmerkmale")
    print("=" * 80)

    print(f"\n{'Merkmal':<25} {'KYR-Δ':>10} {'OBB-Δ':>10} {'Konsistent?':>12}")
    print("-" * 57)

    kyritz = results["KYRITZ_2025_10_25"]
    oberbayern = results["OBERBAYERN_2023_06_28"]

    consistent_features = []

    for feature in kyritz["winner"].keys():
        kyr_delta = kyritz["winner"][feature] - kyritz["not_chosen"][feature]
        obb_delta = oberbayern["winner"][feature] - oberbayern["not_chosen"][feature]

        # Konsistent = beide Deltas haben gleiches Vorzeichen und sind beide != 0
        same_sign = (kyr_delta > 0 and obb_delta > 0) or (kyr_delta < 0 and obb_delta < 0)
        consistent = "JA ✓" if same_sign and kyr_delta != 0 and obb_delta != 0 else "NEIN"

        if same_sign and kyr_delta != 0 and obb_delta != 0:
            consistent_features.append((feature, kyr_delta, obb_delta))

        if isinstance(kyr_delta, float):
            kyr_delta = round(kyr_delta, 1)
        if isinstance(obb_delta, float):
            obb_delta = round(obb_delta, 1)

        print(f"{feature:<25} {str(kyr_delta):>10} {str(obb_delta):>10} {consistent:>12}")

    print("\n" + "=" * 80)
    print("KONSISTENTE UNTERSCHEIDUNGSMERKMALE (Gewinner vs Nicht-Gewählt)")
    print("=" * 80)

    if consistent_features:
        for feature, kyr, obb in consistent_features:
            direction = "HÖHER" if kyr > 0 else "NIEDRIGER"
            print(f"\n  ✓ {feature}: Gewinner haben {direction} als Nicht-Gewählte")
            print(f"    Kyritz: {'+' if kyr > 0 else ''}{kyr}")
            print(f"    Oberbayern: {'+' if obb > 0 else ''}{obb}")
    else:
        print("\n  KEINE konsistenten Unterscheidungsmerkmale gefunden!")
        print("  Die Jackpot-Gewinner haben keine gemeinsamen Unterscheidungsmuster.")

    # Gemeinsame Zahlen
    print("\n" + "=" * 80)
    print("GEMEINSAME ZAHLEN")
    print("=" * 80)

    kyr_winner = set(JACKPOTS["KYRITZ_2025_10_25"]["winner_10"])
    obb_winner = set(JACKPOTS["OBERBAYERN_2023_06_28"]["winner_10"])
    common = kyr_winner & obb_winner

    print(f"\nGemeinsame Gewinner-Zahlen: {sorted(common) if common else 'Keine'}")

    kyr_not = set(JACKPOTS["KYRITZ_2025_10_25"]["not_chosen_10"])
    obb_not = set(JACKPOTS["OBERBAYERN_2023_06_28"]["not_chosen_10"])
    common_not = kyr_not & obb_not

    print(f"Gemeinsame Nicht-Gewählt-Zahlen: {sorted(common_not) if common_not else 'Keine'}")

if __name__ == "__main__":
    main()
