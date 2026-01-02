#!/usr/bin/env python
"""
Statistical and Entropy Analysis of Verified KENO Winner Combinations

Analyzes 3 verified winner combinations for statistical anomalies:
1. Kyritz: [5,12,20,26,34,36,42,45,48,66]
2. Oberbayern: [3,15,18,27,47,53,54,55,66,68]
3. Nordsachsen: [9,19,37,38,43,45,48,57,59,67]

Metrics:
- Variance, Standard Deviation
- Skewness, Kurtosis
- Digit Entropy (0-9 distribution)
- Gap Analysis
- Run-Length Analysis
- Median/Mean Ratio
- IQR (Interquartile Range)
- Coefficient of Variation

Compares with expected values for random 10-from-70 selection.

Author: Kenobase Analysis
Date: 2026-01-01
"""

import json
import math
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from scipy import stats
from collections import Counter
import random


# The 3 verified winner combinations
WINNER_COMBINATIONS = {
    "Kyritz": [5, 12, 20, 26, 34, 36, 42, 45, 48, 66],
    "Oberbayern": [3, 15, 18, 27, 47, 53, 54, 55, 66, 68],
    "Nordsachsen": [9, 19, 37, 38, 43, 45, 48, 57, 59, 67],
}


def calculate_variance(numbers: List[int]) -> float:
    """Calculate population variance."""
    return float(np.var(numbers))


def calculate_std_dev(numbers: List[int]) -> float:
    """Calculate population standard deviation."""
    return float(np.std(numbers))


def calculate_skewness(numbers: List[int]) -> float:
    """Calculate skewness (asymmetry of distribution)."""
    return float(stats.skew(numbers))


def calculate_kurtosis(numbers: List[int]) -> float:
    """Calculate kurtosis (tailedness of distribution)."""
    return float(stats.kurtosis(numbers))


def calculate_digit_entropy(numbers: List[int]) -> Dict[str, Any]:
    """
    Calculate Shannon entropy of digit distribution (0-9).

    For each number, extract all digits and count their distribution.
    Higher entropy = more uniform digit distribution.
    """
    # Extract all digits from all numbers
    all_digits = []
    for num in numbers:
        for digit in str(num):
            all_digits.append(int(digit))

    # Count digit frequencies
    digit_counts = Counter(all_digits)
    total_digits = len(all_digits)

    # Calculate Shannon entropy
    entropy = 0.0
    digit_probs = {}
    for digit in range(10):
        count = digit_counts.get(digit, 0)
        if count > 0:
            prob = count / total_digits
            digit_probs[str(digit)] = round(prob, 4)
            entropy -= prob * math.log2(prob)
        else:
            digit_probs[str(digit)] = 0.0

    # Maximum possible entropy (uniform distribution over 10 digits)
    max_entropy = math.log2(10)
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    return {
        "digit_distribution": digit_probs,
        "total_digits": total_digits,
        "shannon_entropy": round(entropy, 4),
        "max_possible_entropy": round(max_entropy, 4),
        "normalized_entropy": round(normalized_entropy, 4),
        "interpretation": "uniform" if normalized_entropy > 0.9 else (
            "slightly_skewed" if normalized_entropy > 0.7 else "skewed"
        )
    }


def calculate_gaps(numbers: List[int]) -> List[int]:
    """Calculate gaps between consecutive sorted numbers."""
    sorted_nums = sorted(numbers)
    return [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]


def analyze_gaps(numbers: List[int]) -> Dict[str, Any]:
    """Comprehensive gap analysis."""
    gaps = calculate_gaps(numbers)

    return {
        "gaps": gaps,
        "min_gap": min(gaps),
        "max_gap": max(gaps),
        "mean_gap": round(float(np.mean(gaps)), 2),
        "std_gap": round(float(np.std(gaps)), 2),
        "median_gap": float(np.median(gaps)),
        "gap_variance": round(float(np.var(gaps)), 2),
        "consecutive_pairs": gaps.count(1),
        "large_gaps_gt_10": sum(1 for g in gaps if g > 10),
    }


def calculate_run_length(numbers: List[int]) -> Dict[str, Any]:
    """
    Calculate run-length analysis.

    A "run" is defined as a sequence where gaps are monotonically increasing
    or monotonically decreasing.
    """
    gaps = calculate_gaps(numbers)

    if len(gaps) < 2:
        return {
            "max_increasing_run": len(gaps),
            "max_decreasing_run": len(gaps),
            "all_runs": [],
        }

    # Find runs of increasing gaps
    increasing_runs = []
    current_run = 1
    for i in range(1, len(gaps)):
        if gaps[i] > gaps[i-1]:
            current_run += 1
        else:
            if current_run > 1:
                increasing_runs.append(current_run)
            current_run = 1
    if current_run > 1:
        increasing_runs.append(current_run)

    # Find runs of decreasing gaps
    decreasing_runs = []
    current_run = 1
    for i in range(1, len(gaps)):
        if gaps[i] < gaps[i-1]:
            current_run += 1
        else:
            if current_run > 1:
                decreasing_runs.append(current_run)
            current_run = 1
    if current_run > 1:
        decreasing_runs.append(current_run)

    # Alternative: runs of same-direction gap changes
    direction_changes = []
    for i in range(1, len(gaps)):
        if gaps[i] > gaps[i-1]:
            direction_changes.append(1)  # increasing
        elif gaps[i] < gaps[i-1]:
            direction_changes.append(-1)  # decreasing
        else:
            direction_changes.append(0)  # same

    return {
        "max_increasing_run": max(increasing_runs) if increasing_runs else 0,
        "max_decreasing_run": max(decreasing_runs) if decreasing_runs else 0,
        "increasing_runs": increasing_runs,
        "decreasing_runs": decreasing_runs,
        "direction_changes": direction_changes,
        "total_direction_changes": sum(1 for i in range(1, len(direction_changes))
                                       if direction_changes[i] != direction_changes[i-1] and
                                       direction_changes[i] != 0 and direction_changes[i-1] != 0),
    }


def calculate_median_mean_ratio(numbers: List[int]) -> Dict[str, Any]:
    """Calculate ratio of median to mean."""
    mean_val = float(np.mean(numbers))
    median_val = float(np.median(numbers))

    ratio = median_val / mean_val if mean_val != 0 else 0

    return {
        "mean": round(mean_val, 2),
        "median": median_val,
        "ratio": round(ratio, 4),
        "interpretation": "symmetric" if 0.95 <= ratio <= 1.05 else (
            "left_skewed" if ratio > 1.05 else "right_skewed"
        )
    }


def calculate_iqr(numbers: List[int]) -> Dict[str, Any]:
    """Calculate Interquartile Range."""
    q1 = float(np.percentile(numbers, 25))
    q3 = float(np.percentile(numbers, 75))
    iqr = q3 - q1

    return {
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "lower_bound": q1 - 1.5 * iqr,
        "upper_bound": q3 + 1.5 * iqr,
        "outliers": [n for n in numbers if n < q1 - 1.5 * iqr or n > q3 + 1.5 * iqr],
    }


def calculate_coefficient_of_variation(numbers: List[int]) -> float:
    """Calculate Coefficient of Variation (CV = std / mean)."""
    mean_val = np.mean(numbers)
    std_val = np.std(numbers)
    return float(std_val / mean_val) if mean_val != 0 else 0


def calculate_spread(numbers: List[int]) -> int:
    """Calculate spread (max - min)."""
    return max(numbers) - min(numbers)


def calculate_decade_distribution(numbers: List[int]) -> Dict[str, int]:
    """Distribute numbers across decades (1-10, 11-20, ..., 61-70)."""
    decades = {f"{i*10+1}-{(i+1)*10}": 0 for i in range(7)}
    for num in numbers:
        decade_idx = (num - 1) // 10
        decade_key = f"{decade_idx*10+1}-{(decade_idx+1)*10}"
        decades[decade_key] = decades.get(decade_key, 0) + 1
    return decades


def generate_random_baseline(n_samples: int = 10000, pick_size: int = 10,
                              max_num: int = 70) -> Dict[str, Any]:
    """
    Generate expected statistics for random 10-from-70 selection.
    Uses Monte Carlo simulation.
    """
    random.seed(42)  # Reproducibility

    variances = []
    std_devs = []
    skewnesses = []
    kurtoses = []
    entropies = []
    mean_gaps = []
    max_runs = []
    median_mean_ratios = []
    iqrs = []
    cvs = []
    spreads = []

    for _ in range(n_samples):
        sample = sorted(random.sample(range(1, max_num + 1), pick_size))

        variances.append(np.var(sample))
        std_devs.append(np.std(sample))
        skewnesses.append(stats.skew(sample))
        kurtoses.append(stats.kurtosis(sample))

        # Digit entropy
        all_digits = [int(d) for n in sample for d in str(n)]
        digit_counts = Counter(all_digits)
        total = len(all_digits)
        entropy = 0.0
        for count in digit_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        entropies.append(entropy)

        # Gaps
        gaps = [sample[i+1] - sample[i] for i in range(len(sample)-1)]
        mean_gaps.append(np.mean(gaps))

        # Run length (simplified: max increasing run)
        if len(gaps) >= 2:
            max_inc = 1
            curr = 1
            for i in range(1, len(gaps)):
                if gaps[i] > gaps[i-1]:
                    curr += 1
                    max_inc = max(max_inc, curr)
                else:
                    curr = 1
            max_runs.append(max_inc)
        else:
            max_runs.append(1)

        # Median/Mean ratio
        median_mean_ratios.append(np.median(sample) / np.mean(sample))

        # IQR
        q1, q3 = np.percentile(sample, [25, 75])
        iqrs.append(q3 - q1)

        # CV
        cvs.append(np.std(sample) / np.mean(sample))

        # Spread
        spreads.append(max(sample) - min(sample))

    return {
        "n_samples": n_samples,
        "variance": {
            "mean": round(float(np.mean(variances)), 2),
            "std": round(float(np.std(variances)), 2),
            "p5": round(float(np.percentile(variances, 5)), 2),
            "p95": round(float(np.percentile(variances, 95)), 2),
        },
        "std_dev": {
            "mean": round(float(np.mean(std_devs)), 2),
            "std": round(float(np.std(std_devs)), 2),
            "p5": round(float(np.percentile(std_devs, 5)), 2),
            "p95": round(float(np.percentile(std_devs, 95)), 2),
        },
        "skewness": {
            "mean": round(float(np.mean(skewnesses)), 4),
            "std": round(float(np.std(skewnesses)), 4),
            "p5": round(float(np.percentile(skewnesses, 5)), 4),
            "p95": round(float(np.percentile(skewnesses, 95)), 4),
        },
        "kurtosis": {
            "mean": round(float(np.mean(kurtoses)), 4),
            "std": round(float(np.std(kurtoses)), 4),
            "p5": round(float(np.percentile(kurtoses, 5)), 4),
            "p95": round(float(np.percentile(kurtoses, 95)), 4),
        },
        "digit_entropy": {
            "mean": round(float(np.mean(entropies)), 4),
            "std": round(float(np.std(entropies)), 4),
            "p5": round(float(np.percentile(entropies, 5)), 4),
            "p95": round(float(np.percentile(entropies, 95)), 4),
        },
        "mean_gap": {
            "mean": round(float(np.mean(mean_gaps)), 2),
            "std": round(float(np.std(mean_gaps)), 2),
            "p5": round(float(np.percentile(mean_gaps, 5)), 2),
            "p95": round(float(np.percentile(mean_gaps, 95)), 2),
        },
        "max_increasing_run": {
            "mean": round(float(np.mean(max_runs)), 2),
            "std": round(float(np.std(max_runs)), 2),
            "mode": int(stats.mode(max_runs, keepdims=False).mode),
        },
        "median_mean_ratio": {
            "mean": round(float(np.mean(median_mean_ratios)), 4),
            "std": round(float(np.std(median_mean_ratios)), 4),
            "p5": round(float(np.percentile(median_mean_ratios, 5)), 4),
            "p95": round(float(np.percentile(median_mean_ratios, 95)), 4),
        },
        "iqr": {
            "mean": round(float(np.mean(iqrs)), 2),
            "std": round(float(np.std(iqrs)), 2),
            "p5": round(float(np.percentile(iqrs, 5)), 2),
            "p95": round(float(np.percentile(iqrs, 95)), 2),
        },
        "cv": {
            "mean": round(float(np.mean(cvs)), 4),
            "std": round(float(np.std(cvs)), 4),
            "p5": round(float(np.percentile(cvs, 5)), 4),
            "p95": round(float(np.percentile(cvs, 95)), 4),
        },
        "spread": {
            "mean": round(float(np.mean(spreads)), 2),
            "std": round(float(np.std(spreads)), 2),
            "p5": round(float(np.percentile(spreads, 5)), 2),
            "p95": round(float(np.percentile(spreads, 95)), 2),
        },
    }


def analyze_combination(name: str, numbers: List[int]) -> Dict[str, Any]:
    """Perform complete statistical analysis on a combination."""
    sorted_numbers = sorted(numbers)

    return {
        "name": name,
        "numbers": sorted_numbers,
        "count": len(numbers),
        "sum": sum(numbers),
        "statistics": {
            "variance": round(calculate_variance(numbers), 2),
            "std_dev": round(calculate_std_dev(numbers), 2),
            "skewness": round(calculate_skewness(numbers), 4),
            "kurtosis": round(calculate_kurtosis(numbers), 4),
            "spread": calculate_spread(numbers),
            "coefficient_of_variation": round(calculate_coefficient_of_variation(numbers), 4),
        },
        "digit_entropy": calculate_digit_entropy(numbers),
        "gap_analysis": analyze_gaps(numbers),
        "run_length_analysis": calculate_run_length(numbers),
        "median_mean_analysis": calculate_median_mean_ratio(numbers),
        "iqr_analysis": calculate_iqr(numbers),
        "decade_distribution": calculate_decade_distribution(numbers),
    }


def compare_with_baseline(combo_analysis: Dict[str, Any],
                          baseline: Dict[str, Any]) -> Dict[str, Any]:
    """Compare combination statistics with random baseline."""
    stats_combo = combo_analysis["statistics"]

    def is_anomaly(value: float, baseline_stat: Dict[str, float]) -> Tuple[bool, str]:
        """Check if value is outside 5-95 percentile range."""
        p5, p95 = baseline_stat.get("p5", 0), baseline_stat.get("p95", 0)
        if value < p5:
            return True, f"below_p5 ({p5})"
        elif value > p95:
            return True, f"above_p95 ({p95})"
        return False, "normal"

    comparisons = {}

    # Variance
    is_anom, status = is_anomaly(stats_combo["variance"], baseline["variance"])
    comparisons["variance"] = {
        "value": stats_combo["variance"],
        "baseline_mean": baseline["variance"]["mean"],
        "baseline_range": [baseline["variance"]["p5"], baseline["variance"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # Std Dev
    is_anom, status = is_anomaly(stats_combo["std_dev"], baseline["std_dev"])
    comparisons["std_dev"] = {
        "value": stats_combo["std_dev"],
        "baseline_mean": baseline["std_dev"]["mean"],
        "baseline_range": [baseline["std_dev"]["p5"], baseline["std_dev"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # Skewness
    is_anom, status = is_anomaly(stats_combo["skewness"], baseline["skewness"])
    comparisons["skewness"] = {
        "value": stats_combo["skewness"],
        "baseline_mean": baseline["skewness"]["mean"],
        "baseline_range": [baseline["skewness"]["p5"], baseline["skewness"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # Kurtosis
    is_anom, status = is_anomaly(stats_combo["kurtosis"], baseline["kurtosis"])
    comparisons["kurtosis"] = {
        "value": stats_combo["kurtosis"],
        "baseline_mean": baseline["kurtosis"]["mean"],
        "baseline_range": [baseline["kurtosis"]["p5"], baseline["kurtosis"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # Digit Entropy
    entropy_val = combo_analysis["digit_entropy"]["shannon_entropy"]
    is_anom, status = is_anomaly(entropy_val, baseline["digit_entropy"])
    comparisons["digit_entropy"] = {
        "value": entropy_val,
        "baseline_mean": baseline["digit_entropy"]["mean"],
        "baseline_range": [baseline["digit_entropy"]["p5"], baseline["digit_entropy"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # Mean Gap
    mean_gap_val = combo_analysis["gap_analysis"]["mean_gap"]
    is_anom, status = is_anomaly(mean_gap_val, baseline["mean_gap"])
    comparisons["mean_gap"] = {
        "value": mean_gap_val,
        "baseline_mean": baseline["mean_gap"]["mean"],
        "baseline_range": [baseline["mean_gap"]["p5"], baseline["mean_gap"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # Median/Mean Ratio
    mm_ratio = combo_analysis["median_mean_analysis"]["ratio"]
    is_anom, status = is_anomaly(mm_ratio, baseline["median_mean_ratio"])
    comparisons["median_mean_ratio"] = {
        "value": mm_ratio,
        "baseline_mean": baseline["median_mean_ratio"]["mean"],
        "baseline_range": [baseline["median_mean_ratio"]["p5"], baseline["median_mean_ratio"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # IQR
    iqr_val = combo_analysis["iqr_analysis"]["IQR"]
    is_anom, status = is_anomaly(iqr_val, baseline["iqr"])
    comparisons["iqr"] = {
        "value": iqr_val,
        "baseline_mean": baseline["iqr"]["mean"],
        "baseline_range": [baseline["iqr"]["p5"], baseline["iqr"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # CV
    is_anom, status = is_anomaly(stats_combo["coefficient_of_variation"], baseline["cv"])
    comparisons["cv"] = {
        "value": stats_combo["coefficient_of_variation"],
        "baseline_mean": baseline["cv"]["mean"],
        "baseline_range": [baseline["cv"]["p5"], baseline["cv"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # Spread
    is_anom, status = is_anomaly(stats_combo["spread"], baseline["spread"])
    comparisons["spread"] = {
        "value": stats_combo["spread"],
        "baseline_mean": baseline["spread"]["mean"],
        "baseline_range": [baseline["spread"]["p5"], baseline["spread"]["p95"]],
        "is_anomaly": is_anom,
        "status": status,
    }

    # Count anomalies
    anomaly_count = sum(1 for v in comparisons.values() if v["is_anomaly"])

    return {
        "comparisons": comparisons,
        "anomaly_count": anomaly_count,
        "total_metrics": len(comparisons),
        "anomaly_rate": round(anomaly_count / len(comparisons), 4),
    }


def find_common_patterns(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find patterns common across all winner combinations."""
    # Compare decade distributions
    decade_distributions = [a["decade_distribution"] for a in analyses]

    # Check which decades appear in all combinations
    all_decades = set(decade_distributions[0].keys())
    common_covered = []
    for decade in all_decades:
        if all(d[decade] > 0 for d in decade_distributions):
            common_covered.append(decade)

    # Compare digit distributions
    digit_distributions = [a["digit_entropy"]["digit_distribution"] for a in analyses]

    # Find consistently present/absent digits
    always_present = []
    rarely_present = []
    for digit in "0123456789":
        counts = [d[digit] for d in digit_distributions]
        if all(c > 0.05 for c in counts):
            always_present.append(digit)
        if all(c < 0.05 for c in counts):
            rarely_present.append(digit)

    # Gap patterns
    gap_analyses = [a["gap_analysis"] for a in analyses]
    consecutive_pairs = [g["consecutive_pairs"] for g in gap_analyses]
    large_gaps = [g["large_gaps_gt_10"] for g in gap_analyses]

    # Skewness direction
    skewnesses = [a["statistics"]["skewness"] for a in analyses]
    skew_direction = "consistent_right" if all(s > 0 for s in skewnesses) else (
        "consistent_left" if all(s < 0 for s in skewnesses) else "mixed"
    )

    return {
        "common_decades_covered": common_covered,
        "decades_coverage": {
            name: sum(1 for v in d.values() if v > 0)
            for name, d in zip([a["name"] for a in analyses], decade_distributions)
        },
        "digit_patterns": {
            "always_present_above_5pct": always_present,
            "rarely_present_below_5pct": rarely_present,
        },
        "gap_patterns": {
            "consecutive_pairs": consecutive_pairs,
            "avg_consecutive_pairs": round(sum(consecutive_pairs) / len(consecutive_pairs), 2),
            "large_gaps_gt_10": large_gaps,
        },
        "skewness_pattern": {
            "values": [round(s, 4) for s in skewnesses],
            "direction": skew_direction,
            "interpretation": "All winners tend toward higher numbers" if skew_direction == "consistent_right" else (
                "All winners tend toward lower numbers" if skew_direction == "consistent_left" else
                "Mixed tendency"
            ),
        },
    }


def main():
    """Main analysis function."""
    output_file = Path("C:/Users/kenfu/Documents/keno_base/results/entropy_analysis.json")

    print("=" * 70)
    print("STATISTICAL/ENTROPY ANALYSIS OF VERIFIED KENO WINNERS")
    print("=" * 70)

    # Generate random baseline (Monte Carlo simulation)
    print("\n[1/4] Generating random baseline (10,000 simulations)...")
    baseline = generate_random_baseline(n_samples=10000)
    print("      Done.")

    # Analyze each combination
    print("\n[2/4] Analyzing winner combinations...")
    analyses = []
    for name, numbers in WINNER_COMBINATIONS.items():
        print(f"      - {name}: {sorted(numbers)}")
        analysis = analyze_combination(name, numbers)
        analyses.append(analysis)

    # Compare with baseline
    print("\n[3/4] Comparing with random baseline...")
    baseline_comparisons = []
    for analysis in analyses:
        comparison = compare_with_baseline(analysis, baseline)
        analysis["baseline_comparison"] = comparison
        baseline_comparisons.append({
            "name": analysis["name"],
            "comparison": comparison,
        })

    # Find common patterns
    print("\n[4/4] Finding common patterns across winners...")
    common_patterns = find_common_patterns(analyses)

    # Aggregate anomalies
    total_anomalies = sum(bc["comparison"]["anomaly_count"] for bc in baseline_comparisons)
    total_metrics = sum(bc["comparison"]["total_metrics"] for bc in baseline_comparisons)

    # Determine algorithmic selection indicators
    algorithmic_indicators = []

    # Check for consistent patterns
    if common_patterns["skewness_pattern"]["direction"] != "mixed":
        algorithmic_indicators.append({
            "indicator": "Consistent skewness direction",
            "detail": common_patterns["skewness_pattern"]["direction"],
            "significance": "moderate",
        })

    # Check decade coverage
    coverages = list(common_patterns["decades_coverage"].values())
    if all(c >= 5 for c in coverages):
        algorithmic_indicators.append({
            "indicator": "All winners cover 5+ decades",
            "detail": f"Coverages: {coverages}",
            "significance": "low (expected for random)",
        })

    # Check anomaly rate
    for bc in baseline_comparisons:
        if bc["comparison"]["anomaly_rate"] > 0.3:
            algorithmic_indicators.append({
                "indicator": f"High anomaly rate for {bc['name']}",
                "detail": f"{bc['comparison']['anomaly_count']}/{bc['comparison']['total_metrics']} anomalies",
                "significance": "high",
            })

    # Check consecutive pairs
    avg_consecutive = common_patterns["gap_patterns"]["avg_consecutive_pairs"]
    if avg_consecutive >= 2:
        algorithmic_indicators.append({
            "indicator": "Higher than expected consecutive pairs",
            "detail": f"Average: {avg_consecutive}",
            "significance": "moderate",
        })

    # Build final results
    results = {
        "analysis_title": "Statistical and Entropy Analysis of Verified KENO Winners",
        "analysis_date": "2026-01-01",
        "methodology": {
            "metrics_analyzed": [
                "Variance",
                "Standard Deviation",
                "Skewness (asymmetry)",
                "Kurtosis (tailedness)",
                "Digit Entropy (0-9 distribution)",
                "Gap Analysis (distances between numbers)",
                "Run-Length Analysis (monotonic gap sequences)",
                "Median/Mean Ratio",
                "IQR (Interquartile Range)",
                "Coefficient of Variation",
            ],
            "baseline_method": "Monte Carlo simulation with 10,000 random 10-from-70 selections",
            "anomaly_threshold": "Outside 5th-95th percentile of baseline",
        },
        "winner_combinations": analyses,
        "random_baseline": baseline,
        "common_patterns": common_patterns,
        "algorithmic_selection_indicators": algorithmic_indicators,
        "summary": {
            "total_anomalies_detected": total_anomalies,
            "total_metrics_checked": total_metrics,
            "overall_anomaly_rate": round(total_anomalies / total_metrics, 4),
            "conclusion": "",
        },
    }

    # Determine conclusion
    anomaly_rate = total_anomalies / total_metrics
    if anomaly_rate > 0.3:
        results["summary"]["conclusion"] = (
            "HIGH probability of non-random selection. "
            f"Detected {total_anomalies} anomalies across {total_metrics} metrics "
            f"({round(anomaly_rate*100, 1)}% anomaly rate). "
            "Multiple statistical indicators deviate significantly from random baseline."
        )
    elif anomaly_rate > 0.15:
        results["summary"]["conclusion"] = (
            "MODERATE indication of non-random patterns. "
            f"Detected {total_anomalies} anomalies across {total_metrics} metrics "
            f"({round(anomaly_rate*100, 1)}% anomaly rate). "
            "Some statistical indicators show deviation from random expectation."
        )
    else:
        results["summary"]["conclusion"] = (
            "LOW indication of algorithmic selection. "
            f"Detected {total_anomalies} anomalies across {total_metrics} metrics "
            f"({round(anomaly_rate*100, 1)}% anomaly rate). "
            "Winner combinations appear statistically consistent with random selection."
        )

    # Save results
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\nPer-Combination Statistics:")
    for analysis in analyses:
        stats = analysis["statistics"]
        print(f"\n  {analysis['name']}:")
        print(f"    Numbers: {analysis['numbers']}")
        print(f"    Variance: {stats['variance']}")
        print(f"    Std Dev: {stats['std_dev']}")
        print(f"    Skewness: {stats['skewness']} ({'right-skewed' if stats['skewness'] > 0 else 'left-skewed'})")
        print(f"    Kurtosis: {stats['kurtosis']}")
        print(f"    CV: {stats['coefficient_of_variation']}")
        print(f"    Digit Entropy: {analysis['digit_entropy']['normalized_entropy']} (normalized)")
        print(f"    Gaps: min={analysis['gap_analysis']['min_gap']}, max={analysis['gap_analysis']['max_gap']}, mean={analysis['gap_analysis']['mean_gap']}")
        print(f"    Consecutive pairs: {analysis['gap_analysis']['consecutive_pairs']}")
        print(f"    Anomalies vs baseline: {analysis['baseline_comparison']['anomaly_count']}/{analysis['baseline_comparison']['total_metrics']}")

    print("\nRandom Baseline (10-from-70):")
    print(f"  Expected Variance: {baseline['variance']['mean']} (range: {baseline['variance']['p5']}-{baseline['variance']['p95']})")
    print(f"  Expected Std Dev: {baseline['std_dev']['mean']} (range: {baseline['std_dev']['p5']}-{baseline['std_dev']['p95']})")
    print(f"  Expected Skewness: {baseline['skewness']['mean']} (range: {baseline['skewness']['p5']}-{baseline['skewness']['p95']})")
    print(f"  Expected Kurtosis: {baseline['kurtosis']['mean']} (range: {baseline['kurtosis']['p5']}-{baseline['kurtosis']['p95']})")

    print("\nCommon Patterns Across Winners:")
    print(f"  Skewness direction: {common_patterns['skewness_pattern']['direction']}")
    print(f"  Consecutive pairs: {common_patterns['gap_patterns']['consecutive_pairs']} (avg: {common_patterns['gap_patterns']['avg_consecutive_pairs']})")
    print(f"  Decades covered: {common_patterns['decades_coverage']}")

    print("\nAlgorithmic Selection Indicators:")
    if algorithmic_indicators:
        for indicator in algorithmic_indicators:
            print(f"  - {indicator['indicator']}: {indicator['detail']} (significance: {indicator['significance']})")
    else:
        print("  None detected")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print(f"\n{results['summary']['conclusion']}")
    print("\n" + "=" * 70)

    return results


if __name__ == "__main__":
    main()
