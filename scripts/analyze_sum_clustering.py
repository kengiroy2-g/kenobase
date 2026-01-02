#!/usr/bin/env python3
"""
Think Tank Analysis: Sum-Clustering Model Hypothesis

Hypothesis: The RNG keeps the sum of 20 drawn numbers within a specific range
to appear "natural". By creating tickets whose sum falls within the "allowed"
range, we may achieve better hit rates.

Expected sum for truly random draws: 20 * 35.5 = 710 (mean of 1-70)
Expected standard deviation: sqrt(20 * variance(1-70)) = sqrt(20 * 408.25) ~ 90.4

Author: Think Tank AI
Date: 2025-12-31
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import math
from typing import NamedTuple


class DrawResult(NamedTuple):
    """Single KENO draw result."""
    date: str
    numbers: list[int]
    sum_value: int


def load_keno_data(filepath: str) -> list[DrawResult]:
    """Load KENO data from CSV file."""
    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)  # Skip header

        for row in reader:
            if len(row) < 21:
                continue

            date = row[0]
            # Extract 20 KENO numbers (columns 1-20)
            numbers = []
            for i in range(1, 21):
                try:
                    num = int(row[i])
                    numbers.append(num)
                except (ValueError, IndexError):
                    continue

            if len(numbers) == 20:
                sum_value = sum(numbers)
                results.append(DrawResult(date=date, numbers=numbers, sum_value=sum_value))

    return results


def calculate_theoretical_values() -> dict:
    """Calculate theoretical values for truly random draws."""
    # For uniform distribution 1-70:
    # Mean = (1 + 70) / 2 = 35.5
    # Variance = ((70-1+1)^2 - 1) / 12 = (70^2 - 1) / 12 = 4899 / 12 = 408.25

    # But KENO draws WITHOUT replacement from 1-70, drawing 20 numbers
    # This is a hypergeometric-like scenario

    # Expected sum = 20 * 35.5 = 710
    # The variance for sum of k items drawn without replacement from 1..N:
    # Var(sum) = k * (N+1) * (N-k) / 12 = 20 * 71 * 50 / 12 = 5916.67
    # Std = sqrt(5916.67) = 76.92

    N = 70  # Numbers 1 to 70
    k = 20  # 20 numbers drawn

    expected_mean = k * (N + 1) / 2  # = 710
    variance = k * (N + 1) * (N - k) / 12  # = 5916.67
    expected_std = math.sqrt(variance)  # = 76.92

    # Min possible sum: 1+2+...+20 = 210
    min_sum = sum(range(1, 21))
    # Max possible sum: 51+52+...+70 = 1210
    max_sum = sum(range(51, 71))

    return {
        "expected_mean": expected_mean,
        "expected_variance": variance,
        "expected_std": expected_std,
        "theoretical_min": min_sum,
        "theoretical_max": max_sum,
        "method": "Hypergeometric (without replacement from 1-70, k=20)"
    }


def analyze_sum_distribution(draws: list[DrawResult]) -> dict:
    """Analyze the distribution of sums."""
    sums = [d.sum_value for d in draws]

    n = len(sums)
    mean = sum(sums) / n
    variance = sum((x - mean) ** 2 for x in sums) / n
    std = math.sqrt(variance)

    min_sum = min(sums)
    max_sum = max(sums)

    # Quartiles
    sorted_sums = sorted(sums)
    q1 = sorted_sums[n // 4]
    median = sorted_sums[n // 2]
    q3 = sorted_sums[3 * n // 4]

    return {
        "count": n,
        "mean": round(mean, 2),
        "std": round(std, 2),
        "variance": round(variance, 2),
        "min": min_sum,
        "max": max_sum,
        "range": max_sum - min_sum,
        "q1": q1,
        "median": median,
        "q3": q3,
        "iqr": q3 - q1
    }


def find_forbidden_zones(draws: list[DrawResult], theoretical: dict) -> dict:
    """Find sum ranges that never appear in the data."""
    sums = [d.sum_value for d in draws]
    sum_counter = Counter(sums)

    min_observed = min(sums)
    max_observed = max(sums)
    theoretical_min = theoretical["theoretical_min"]
    theoretical_max = theoretical["theoretical_max"]

    # Find gaps in the observed sums
    observed_set = set(sums)

    # Missing sums in the observed range
    missing_in_range = []
    for s in range(min_observed, max_observed + 1):
        if s not in observed_set:
            missing_in_range.append(s)

    # "Forbidden" zones at the extremes
    lower_forbidden = list(range(theoretical_min, min_observed))
    upper_forbidden = list(range(max_observed + 1, theoretical_max + 1))

    # Find rare sums (appearing only once or twice)
    rare_sums = [s for s, count in sum_counter.items() if count <= 2]

    # Analyze sum frequency distribution
    frequency_distribution = {}
    for s in range(min_observed, max_observed + 1, 10):
        bucket = f"{s}-{s+9}"
        count = sum(1 for x in sums if s <= x < s + 10)
        frequency_distribution[bucket] = count

    return {
        "observed_min": min_observed,
        "observed_max": max_observed,
        "theoretical_min": theoretical_min,
        "theoretical_max": theoretical_max,
        "lower_forbidden_zone": {
            "range": f"{theoretical_min}-{min_observed-1}" if min_observed > theoretical_min else None,
            "count": len(lower_forbidden)
        },
        "upper_forbidden_zone": {
            "range": f"{max_observed+1}-{theoretical_max}" if max_observed < theoretical_max else None,
            "count": len(upper_forbidden)
        },
        "missing_in_observed_range": missing_in_range[:20],  # First 20 gaps
        "missing_count": len(missing_in_range),
        "rare_sums_count": len(rare_sums),
        "frequency_by_bucket": frequency_distribution
    }


def analyze_sum_zones(draws: list[DrawResult], theoretical: dict) -> dict:
    """Divide sums into zones and analyze their characteristics."""
    sums = [d.sum_value for d in draws]
    mean = theoretical["expected_mean"]  # 710
    std = theoretical["expected_std"]    # ~77

    # Define zones based on standard deviations from mean
    zones = {
        "extreme_low": {"range": f"<{int(mean - 2*std)}", "min": 0, "max": int(mean - 2*std)},
        "low": {"range": f"{int(mean - 2*std)}-{int(mean - std)}", "min": int(mean - 2*std), "max": int(mean - std)},
        "normal_low": {"range": f"{int(mean - std)}-{int(mean)}", "min": int(mean - std), "max": int(mean)},
        "normal_high": {"range": f"{int(mean)}-{int(mean + std)}", "min": int(mean), "max": int(mean + std)},
        "high": {"range": f"{int(mean + std)}-{int(mean + 2*std)}", "min": int(mean + std), "max": int(mean + 2*std)},
        "extreme_high": {"range": f">{int(mean + 2*std)}", "min": int(mean + 2*std), "max": 9999}
    }

    zone_counts = {}
    for zone_name, zone_def in zones.items():
        count = sum(1 for s in sums if zone_def["min"] <= s < zone_def["max"])
        pct = round(100 * count / len(sums), 2)
        zone_counts[zone_name] = {
            "range": zone_def["range"],
            "count": count,
            "percentage": pct
        }

    # For normal distribution, we expect:
    # Within 1 std: ~68%
    # Within 2 std: ~95%
    # Beyond 2 std: ~5%

    within_1_std = sum(1 for s in sums if abs(s - mean) <= std)
    within_2_std = sum(1 for s in sums if abs(s - mean) <= 2*std)
    beyond_2_std = len(sums) - within_2_std

    return {
        "zones": zone_counts,
        "normality_test": {
            "within_1_std_observed": round(100 * within_1_std / len(sums), 2),
            "within_1_std_expected": 68.27,
            "within_2_std_observed": round(100 * within_2_std / len(sums), 2),
            "within_2_std_expected": 95.45,
            "beyond_2_std_observed": round(100 * beyond_2_std / len(sums), 2),
            "beyond_2_std_expected": 4.55
        }
    }


def calculate_optimal_ticket_sum_range(draws: list[DrawResult], stats: dict) -> dict:
    """Determine the optimal sum range for ticket creation."""
    sums = [d.sum_value for d in draws]
    mean = stats["mean"]
    std = stats["std"]

    # Find the most common sum range (mode area)
    sum_counter = Counter(sums)

    # Find the peak (most frequent sum)
    peak_sum = max(sum_counter, key=sum_counter.get)
    peak_count = sum_counter[peak_sum]

    # Find optimal range: where 80% of draws fall
    sorted_sums = sorted(sums)
    n = len(sums)
    p10 = sorted_sums[int(n * 0.1)]
    p90 = sorted_sums[int(n * 0.9)]

    # Calculate hit rate improvement potential
    # If we target the middle 80%, we'd expect to match 80% of draws
    # But if sums cluster more than expected, the benefit is higher

    middle_80_count = sum(1 for s in sums if p10 <= s <= p90)
    actual_middle_80_pct = 100 * middle_80_count / n

    # Calculate concentration ratio (vs uniform distribution)
    # Uniform would have each sum equally likely
    observed_range = max(sums) - min(sums)
    uniform_std = observed_range / math.sqrt(12)  # std of uniform distribution
    concentration_ratio = uniform_std / std if std > 0 else 1

    return {
        "peak_sum": peak_sum,
        "peak_frequency": peak_count,
        "optimal_range": {
            "lower": p10,
            "upper": p90,
            "description": "Contains 80% of all draws"
        },
        "tight_range": {
            "lower": int(mean - std),
            "upper": int(mean + std),
            "description": "Contains ~68% of all draws (1 std)"
        },
        "concentration_ratio": round(concentration_ratio, 3),
        "recommendation": f"Target ticket sums between {p10} and {p90} for best hit rate"
    }


def test_hypothesis(draws: list[DrawResult], theoretical: dict, observed: dict) -> dict:
    """Test the Sum-Clustering hypothesis."""
    expected_std = theoretical["expected_std"]
    observed_std = observed["std"]
    expected_mean = theoretical["expected_mean"]
    observed_mean = observed["mean"]

    # Hypothesis: If RNG is "clustering", observed std should be LESS than expected
    std_ratio = observed_std / expected_std
    mean_deviation = abs(observed_mean - expected_mean)

    # Chi-square-like test for clustering
    # Compare observed distribution to expected uniform
    sums = [d.sum_value for d in draws]

    # Divide into 10 buckets
    min_s, max_s = min(sums), max(sums)
    bucket_size = (max_s - min_s) / 10

    observed_buckets = [0] * 10
    for s in sums:
        bucket = min(9, int((s - min_s) / bucket_size))
        observed_buckets[bucket] += 1

    expected_per_bucket = len(sums) / 10

    chi_square = sum(
        (obs - expected_per_bucket) ** 2 / expected_per_bucket
        for obs in observed_buckets
    )

    # Clustering evidence
    clustering_evidence = {
        "std_ratio": round(std_ratio, 4),
        "std_interpretation": "LESS spread than expected (clustering)" if std_ratio < 1 else "MORE spread than expected (anti-clustering)" if std_ratio > 1 else "As expected",
        "mean_deviation": round(mean_deviation, 2),
        "mean_interpretation": "Mean is close to expected" if mean_deviation < 5 else "Mean deviates from expected",
        "chi_square_statistic": round(chi_square, 2),
        "bucket_distribution": observed_buckets
    }

    # Final hypothesis verdict
    if std_ratio < 0.95:
        verdict = "SUPPORTED: Evidence of sum clustering (tighter distribution than random)"
        confidence = "MEDIUM" if std_ratio < 0.90 else "LOW"
    elif std_ratio > 1.05:
        verdict = "REJECTED: Sums are MORE spread than expected"
        confidence = "HIGH" if std_ratio > 1.10 else "MEDIUM"
    else:
        verdict = "INCONCLUSIVE: Distribution is consistent with random draws"
        confidence = "N/A"

    return {
        "hypothesis": "Sum-Clustering Model: RNG keeps sum within specific range",
        "test_results": clustering_evidence,
        "verdict": verdict,
        "confidence": confidence,
        "practical_implication": "Target sums in the most frequent range" if std_ratio < 1 else "Sum targeting may not improve hit rate"
    }


def analyze_temporal_patterns(draws: list[DrawResult]) -> dict:
    """Analyze if sum patterns change over time."""
    # Group by month/year
    monthly_stats = defaultdict(list)

    for draw in draws:
        # Parse date (format: DD.MM.YYYY)
        parts = draw.date.split('.')
        if len(parts) == 3:
            month_year = f"{parts[2]}-{parts[1]}"  # YYYY-MM
            monthly_stats[month_year].append(draw.sum_value)

    monthly_analysis = {}
    for period, sums in sorted(monthly_stats.items()):
        if sums:
            mean = sum(sums) / len(sums)
            std = math.sqrt(sum((x - mean) ** 2 for x in sums) / len(sums)) if len(sums) > 1 else 0
            monthly_analysis[period] = {
                "count": len(sums),
                "mean": round(mean, 1),
                "std": round(std, 1),
                "min": min(sums),
                "max": max(sums)
            }

    # Check for trends
    means = [v["mean"] for v in monthly_analysis.values()]
    if len(means) > 1:
        trend = "increasing" if means[-1] > means[0] else "decreasing" if means[-1] < means[0] else "stable"
        trend_magnitude = abs(means[-1] - means[0])
    else:
        trend = "insufficient_data"
        trend_magnitude = 0

    return {
        "monthly_breakdown": monthly_analysis,
        "trend": {
            "direction": trend,
            "magnitude": round(trend_magnitude, 2),
            "interpretation": "No significant time-based pattern" if trend_magnitude < 10 else "Possible time-dependent pattern"
        }
    }


def main():
    """Main analysis function."""
    # Paths
    data_path = Path("C:/Users/kenfu/Documents/keno_base/data/raw/keno/KENO_ab_2022_bereinigt.csv")
    results_path = Path("C:/Users/kenfu/Documents/keno_base/results/think_tank_sums.json")

    print("=" * 70)
    print("THINK TANK ANALYSIS: Sum-Clustering Model Hypothesis")
    print("=" * 70)
    print()

    # Load data
    print(f"Loading data from: {data_path}")
    draws = load_keno_data(str(data_path))
    print(f"Loaded {len(draws)} KENO draws")
    print()

    # Calculate theoretical values
    print("Calculating theoretical values for random draws...")
    theoretical = calculate_theoretical_values()
    print(f"  Expected Mean: {theoretical['expected_mean']}")
    print(f"  Expected Std:  {theoretical['expected_std']:.2f}")
    print()

    # Analyze observed distribution
    print("Analyzing observed sum distribution...")
    observed = analyze_sum_distribution(draws)
    print(f"  Observed Mean: {observed['mean']}")
    print(f"  Observed Std:  {observed['std']}")
    print(f"  Observed Range: {observed['min']} - {observed['max']}")
    print()

    # Find forbidden zones
    print("Searching for 'forbidden' sum zones...")
    forbidden = find_forbidden_zones(draws, theoretical)
    print(f"  Lower forbidden zone: {forbidden['lower_forbidden_zone']['count']} values never seen")
    print(f"  Upper forbidden zone: {forbidden['upper_forbidden_zone']['count']} values never seen")
    print(f"  Gaps in observed range: {forbidden['missing_count']}")
    print()

    # Analyze zones
    print("Analyzing sum zones (by standard deviation)...")
    zones = analyze_sum_zones(draws, theoretical)
    for zone_name, zone_data in zones["zones"].items():
        print(f"  {zone_name}: {zone_data['percentage']}% ({zone_data['count']} draws)")
    print()

    # Calculate optimal range
    print("Calculating optimal ticket sum range...")
    optimal = calculate_optimal_ticket_sum_range(draws, observed)
    print(f"  Optimal range: {optimal['optimal_range']['lower']} - {optimal['optimal_range']['upper']}")
    print(f"  Peak sum: {optimal['peak_sum']}")
    print()

    # Test hypothesis
    print("Testing Sum-Clustering Hypothesis...")
    hypothesis = test_hypothesis(draws, theoretical, observed)
    print(f"  VERDICT: {hypothesis['verdict']}")
    print(f"  Confidence: {hypothesis['confidence']}")
    print()

    # Temporal patterns
    print("Analyzing temporal patterns...")
    temporal = analyze_temporal_patterns(draws)
    print(f"  Trend: {temporal['trend']['direction']} (magnitude: {temporal['trend']['magnitude']})")
    print()

    # Compile results
    results = {
        "metadata": {
            "analysis": "Sum-Clustering Model Hypothesis",
            "analyst": "Think Tank AI",
            "timestamp": datetime.now().isoformat(),
            "data_source": str(data_path),
            "total_draws": len(draws)
        },
        "theoretical_values": theoretical,
        "observed_statistics": observed,
        "forbidden_zones": forbidden,
        "zone_analysis": zones,
        "optimal_ticket_range": optimal,
        "hypothesis_test": hypothesis,
        "temporal_analysis": temporal,
        "conclusions": {
            "summary": hypothesis["verdict"],
            "key_findings": [
                f"Observed std ({observed['std']}) vs expected std ({theoretical['expected_std']:.2f})",
                f"Sum range in practice: {observed['min']} - {observed['max']}",
                f"Optimal target range: {optimal['optimal_range']['lower']} - {optimal['optimal_range']['upper']}",
                f"{zones['normality_test']['within_1_std_observed']}% of draws within 1 std (expected: 68.27%)"
            ],
            "recommendations": [
                optimal["recommendation"],
                "Avoid extreme sums (below " + str(forbidden['observed_min']) + " or above " + str(forbidden['observed_max']) + ")",
                "Consider temporal patterns for timing-based strategies" if temporal['trend']['magnitude'] > 10 else "No timing advantage detected"
            ]
        }
    }

    # Save results
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"Results saved to: {results_path}")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
