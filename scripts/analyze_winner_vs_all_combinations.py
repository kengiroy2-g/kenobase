"""
KENO Jackpot: Gewinner vs. ALLE C(20,10) Kombinationen

Für jeden Jackpot-Tag:
1. Generiere alle 184.756 möglichen 10er-Kombinationen aus den 20 gezogenen
2. Berechne Charakteristiken für jede Kombination
3. Finde wo die Gewinner-Kombination im Ranking steht (Percentile)
4. Identifiziere extreme Merkmale (Top/Bottom 5%)
5. Vergleiche über alle 3 Jackpots: Was ist KONSISTENT extrem?
"""

import json
from itertools import combinations
from pathlib import Path
from collections import defaultdict
import numpy as np

# Konfiguration
LUCKY_NUMBERS = {7, 3, 9, 11, 19}
BIRTHDAY_RANGE = range(1, 32)
HIGH_RANGE = range(50, 71)
EXTREME_THRESHOLD = 5  # Top/Bottom 5%


def load_jackpot_events():
    """Lade alle Jackpot-Events."""
    path = Path("AI_COLLABORATION/JACKPOT_ANALYSIS/data/jackpot_events.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["events"]


def calculate_characteristics(combo: tuple[int, ...]) -> dict:
    """Berechne Charakteristiken für eine Kombination."""
    nums = sorted(combo)

    # Beliebtheit
    birthday_count = sum(1 for n in nums if n in BIRTHDAY_RANGE)
    lucky_count = sum(1 for n in nums if n in LUCKY_NUMBERS)
    high_count = sum(1 for n in nums if n in HIGH_RANGE)

    # Strukturell
    even_count = sum(1 for n in nums if n % 2 == 0)

    # Gaps und Konsekutive
    gaps = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
    consecutive_pairs = sum(1 for g in gaps if g == 1)
    min_gap = min(gaps)
    max_gap = max(gaps)
    avg_gap = sum(gaps) / len(gaps)

    # Dekaden
    decades = defaultdict(int)
    for n in nums:
        decade = ((n - 1) // 10) + 1
        decades[decade] += 1
    decades_used = len(decades)
    max_per_decade = max(decades.values())

    # Numerisch
    total_sum = sum(nums)
    std_dev = np.std(nums)

    return {
        "birthday_count": birthday_count,
        "lucky_count": lucky_count,
        "high_count": high_count,
        "even_count": even_count,
        "consecutive_pairs": consecutive_pairs,
        "min_gap": min_gap,
        "max_gap": max_gap,
        "avg_gap": avg_gap,
        "decades_used": decades_used,
        "max_per_decade": max_per_decade,
        "sum": total_sum,
        "std_dev": std_dev,
    }


def analyze_jackpot(event: dict) -> dict:
    """
    Analysiere einen Jackpot: Gewinner vs. alle C(20,10) Kombinationen.
    """
    drawn_20 = event["drawn_20"]
    winner_10 = tuple(sorted(event["winner_10"]))

    print(f"\n{'='*60}")
    print(f"Analysiere: {event['id']}")
    print(f"20 Gezogene: {drawn_20}")
    print(f"Gewinner-10: {list(winner_10)}")
    print(f"{'='*60}")

    # Generiere alle C(20,10) = 184.756 Kombinationen
    all_combos = list(combinations(drawn_20, 10))
    total_combos = len(all_combos)
    print(f"Generiere {total_combos:,} Kombinationen...")

    # Berechne Charakteristiken für alle
    all_chars = []
    for combo in all_combos:
        chars = calculate_characteristics(combo)
        chars["combo"] = tuple(sorted(combo))
        all_chars.append(chars)

    # Finde Gewinner-Charakteristiken
    winner_chars = None
    winner_idx = None
    for i, chars in enumerate(all_chars):
        if chars["combo"] == winner_10:
            winner_chars = chars
            winner_idx = i
            break

    if winner_chars is None:
        print("FEHLER: Gewinner-Kombination nicht gefunden!")
        return None

    print(f"Gewinner gefunden bei Index {winner_idx}")

    # Berechne Percentile für jede Charakteristik
    results = {"id": event["id"], "date": event["date"], "characteristics": {}}

    keys = [k for k in winner_chars.keys() if k != "combo"]

    for key in keys:
        values = [c[key] for c in all_chars]
        winner_value = winner_chars[key]

        # Percentile: Wie viel % haben einen niedrigeren Wert?
        lower_count = sum(1 for v in values if v < winner_value)
        percentile = (lower_count / total_combos) * 100

        # Statistiken
        mean_val = np.mean(values)
        std_val = np.std(values)
        min_val = min(values)
        max_val = max(values)

        # Z-Score
        z_score = (winner_value - mean_val) / std_val if std_val > 0 else 0

        # Ist extrem?
        is_extreme_low = percentile <= EXTREME_THRESHOLD
        is_extreme_high = percentile >= (100 - EXTREME_THRESHOLD)

        results["characteristics"][key] = {
            "winner_value": winner_value,
            "percentile": round(percentile, 1),
            "mean": round(mean_val, 2),
            "std": round(std_val, 2),
            "min": min_val,
            "max": max_val,
            "z_score": round(z_score, 2),
            "is_extreme_low": is_extreme_low,
            "is_extreme_high": is_extreme_high,
        }

    return results


def find_consistent_extremes(all_results: list[dict]) -> dict:
    """
    Finde Charakteristiken die bei ALLEN Jackpots extrem sind.
    """
    if not all_results:
        return {}

    keys = list(all_results[0]["characteristics"].keys())
    consistent = {}

    for key in keys:
        # Sammle Extremitäts-Info für alle Jackpots
        extreme_low = []
        extreme_high = []
        percentiles = []

        for result in all_results:
            char = result["characteristics"][key]
            extreme_low.append(char["is_extreme_low"])
            extreme_high.append(char["is_extreme_high"])
            percentiles.append(char["percentile"])

        # Konsistent extrem niedrig?
        if all(extreme_low):
            consistent[key] = {
                "direction": "KONSISTENT_NIEDRIG",
                "percentiles": percentiles,
                "interpretation": f"Gewinner haben IMMER niedrige {key} (Bottom {EXTREME_THRESHOLD}%)",
            }
        # Konsistent extrem hoch?
        elif all(extreme_high):
            consistent[key] = {
                "direction": "KONSISTENT_HOCH",
                "percentiles": percentiles,
                "interpretation": f"Gewinner haben IMMER hohe {key} (Top {EXTREME_THRESHOLD}%)",
            }
        else:
            consistent[key] = {
                "direction": "NICHT_KONSISTENT",
                "percentiles": percentiles,
                "low_count": sum(extreme_low),
                "high_count": sum(extreme_high),
            }

    return consistent


def print_results(all_results: list[dict], consistent: dict):
    """Drucke die Ergebnisse."""

    print("\n" + "=" * 80)
    print("EINZELERGEBNISSE: Gewinner-Percentile pro Jackpot")
    print("=" * 80)

    for result in all_results:
        print(f"\n{result['id']} ({result['date']}):")
        print(f"{'Charakteristik':<20} {'Wert':>8} {'Percentile':>10} {'Z-Score':>8} {'Extrem?':>10}")
        print("-" * 60)

        for key, data in result["characteristics"].items():
            val = data["winner_value"]
            pct = data["percentile"]
            z = data["z_score"]

            if data["is_extreme_low"]:
                extreme = f"LOW ({pct:.0f}%)"
            elif data["is_extreme_high"]:
                extreme = f"HIGH ({pct:.0f}%)"
            else:
                extreme = "-"

            if isinstance(val, float):
                val_str = f"{val:.1f}"
            else:
                val_str = str(val)

            print(f"{key:<20} {val_str:>8} {pct:>9.1f}% {z:>+8.2f} {extreme:>10}")

    print("\n" + "=" * 80)
    print(f"KONSISTENZ-ANALYSE (über alle {len(all_results)} Jackpots)")
    print("=" * 80)

    # Sortiere: Konsistente zuerst
    sorted_keys = sorted(consistent.keys(),
                        key=lambda k: consistent[k]["direction"] != "NICHT_KONSISTENT",
                        reverse=True)

    print(f"\n{'Charakteristik':<20} {'Status':>20} {'Percentiles'}")
    print("-" * 70)

    for key in sorted_keys:
        c = consistent[key]
        pcts = c["percentiles"]
        pct_str = str([f"{p:.0f}%" for p in pcts])

        if c["direction"] == "KONSISTENT_NIEDRIG":
            status = "KONSISTENT NIEDRIG"
        elif c["direction"] == "KONSISTENT_HOCH":
            status = "KONSISTENT HOCH"
        else:
            status = f"MIXED ({c['low_count']}L/{c['high_count']}H)"

        print(f"{key:<20} {status:>20} {pct_str}")

    # Gefundene Regeln
    print("\n" + "=" * 80)
    print("GEFUNDENE KONSISTENTE EXTREMMUSTER:")
    print("=" * 80)

    found_any = False
    for key, c in consistent.items():
        if c["direction"] in ["KONSISTENT_NIEDRIG", "KONSISTENT_HOCH"]:
            print(f"\n  ✓ {key}:")
            print(f"    {c['interpretation']}")
            print(f"    Percentiles: {c['percentiles']}")
            found_any = True

    if not found_any:
        print("\n  KEINE konsistenten Extremmuster gefunden.")
        print("  Das System verschleiert Muster sehr effektiv!")

        # Zeige fast-konsistente
        print("\n  FAST-KONSISTENTE (2 von 3 extrem):")
        for key, c in consistent.items():
            if c["direction"] == "NICHT_KONSISTENT":
                total_extreme = c["low_count"] + c["high_count"]
                if total_extreme >= 2:
                    direction = "niedrig" if c["low_count"] > c["high_count"] else "hoch"
                    print(f"    - {key}: {total_extreme}/3 extrem {direction}")
                    print(f"      Percentiles: {c['percentiles']}")


def main():
    """Hauptfunktion."""
    events = load_jackpot_events()
    print(f"Geladene Jackpot-Events: {len(events)}")

    # Analysiere jeden Jackpot
    all_results = []
    for event in events:
        result = analyze_jackpot(event)
        if result:
            all_results.append(result)

    # Finde konsistente Extreme
    consistent = find_consistent_extremes(all_results)

    # Drucke Ergebnisse
    print_results(all_results, consistent)

    # Speichere Ergebnisse
    output = {
        "jackpot_results": all_results,
        "consistency_analysis": consistent,
    }

    output_path = Path("AI_COLLABORATION/JACKPOT_ANALYSIS/results/winner_vs_all_combinations.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert: {output_path}")


if __name__ == "__main__":
    main()
