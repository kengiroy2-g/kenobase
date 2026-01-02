#!/usr/bin/env python3
"""TASK_042: Validate 2025 as Statistical Outlier vs 2018-2024.

This script performs statistical tests to determine if 2025 KENO data
represents a significant departure from the 2018-2024 baseline.

Uses metrics from existing distribution analysis artifacts to ensure consistency.

Tests performed:
- Welch's t-test for mean daily payout
- Bootstrap 95% CI for difference in means
- Cohen's d effect size
- Chi-squared test for Jackpot-10 proportion
- Levene's test for variance difference (CV proxy)

Output: results/outlier_year_2025_validation.json
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# Add parent to path for kenobase imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kenobase.analysis.distribution import load_gq_data as kenobase_load_gq


def parse_german_number(value: str) -> float:
    """Parse German-formatted number (1.234,56 -> 1234.56)."""
    if pd.isna(value) or value == "" or value == "-":
        return 0.0
    value = str(value).strip()
    # Remove currency symbol and euro
    value = re.sub(r"[€\s]", "", value)
    value = value.replace("Gewinnquote", "")
    # German format: 1.234,56 -> 1234.56
    value = value.replace(".", "")
    value = value.replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return 0.0


def load_gq_data_custom(path: Path, year_filter: list[int] | None = None) -> pd.DataFrame:
    """Load Gewinnquoten CSV using kenobase loader + add parsed_date."""
    df = kenobase_load_gq(str(path))

    if df.empty:
        return df

    # Add parsed_date for grouping
    if "Datum" in df.columns:
        df["parsed_date"] = pd.to_datetime(df["Datum"])
        if year_filter:
            df = df[df["parsed_date"].dt.year.isin(year_filter)]

    return df


def compute_daily_payouts(df: pd.DataFrame) -> pd.Series:
    """Aggregate total daily payouts from GQ data.

    Uses kenobase-parsed columns: Anzahl der Gewinner * 1 Euro Gewinn
    """
    if "parsed_date" not in df.columns:
        return pd.Series(dtype=float)

    # Compute payout per row
    df = df.copy()
    df["payout"] = df["Anzahl der Gewinner"].astype(float) * df["1 Euro Gewinn"].astype(float)

    daily = df.groupby(df["parsed_date"].dt.date)["payout"].sum()
    daily = daily[daily > 0]  # Remove zero-payout days
    return daily


def identify_jackpot_10_days(df: pd.DataFrame) -> set:
    """Identify days with Keno-Typ 10, 10 matches (Jackpot-10).

    Jackpot-10 is when Keno-Typ=10 AND Anzahl richtiger Zahlen="10" AND winners > 0.
    """
    if "Keno-Typ" not in df.columns or "Anzahl richtiger Zahlen" not in df.columns:
        return set()

    # Convert columns to string for comparison (data may be mixed types)
    keno_typ = df["Keno-Typ"].astype(str).str.strip()
    anzahl_richtig = df["Anzahl richtiger Zahlen"].astype(str).str.strip()

    # Parse winner count
    if "Anzahl der Gewinner" in df.columns:
        def parse_winner_count(x):
            try:
                x = str(x).replace(".", "").replace(",", ".")
                return float(x)
            except (ValueError, TypeError):
                return 0.0
        winners = df["Anzahl der Gewinner"].apply(parse_winner_count)
    else:
        winners = pd.Series([0] * len(df))

    # Jackpot-10: Keno-Typ=10, 10 richtige, at least 1 winner
    jackpot_mask = (keno_typ == "10") & (anzahl_richtig == "10") & (winners > 0)

    if "parsed_date" in df.columns:
        jackpot_dates = df.loc[jackpot_mask, "parsed_date"].dt.date.unique()
        return set(jackpot_dates)
    return set()


def bootstrap_ci(
    sample1: np.ndarray,
    sample2: np.ndarray,
    n_bootstrap: int = 10000,
    ci: float = 0.95,
) -> tuple[float, float, float]:
    """Bootstrap confidence interval for difference in means."""
    rng = np.random.default_rng(42)
    diffs = []

    for _ in range(n_bootstrap):
        boot1 = rng.choice(sample1, size=len(sample1), replace=True)
        boot2 = rng.choice(sample2, size=len(sample2), replace=True)
        diffs.append(np.mean(boot1) - np.mean(boot2))

    diffs = np.array(diffs)
    alpha = 1 - ci
    lower = np.percentile(diffs, 100 * alpha / 2)
    upper = np.percentile(diffs, 100 * (1 - alpha / 2))
    mean_diff = np.mean(diffs)

    return mean_diff, lower, upper


def cohens_d(sample1: np.ndarray, sample2: np.ndarray) -> float:
    """Calculate Cohen's d effect size (pooled std)."""
    n1, n2 = len(sample1), len(sample2)
    var1, var2 = np.var(sample1, ddof=1), np.var(sample2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(sample1) - np.mean(sample2)) / pooled_std


def run_validation() -> dict:
    """Run full 2025 outlier validation."""
    base_path = Path(__file__).parent.parent

    # Load 2025 data
    gq_2025_path = base_path / "Keno_GPTs" / "Keno_GQ_2025.csv"
    df_2025 = load_gq_data_custom(gq_2025_path)
    daily_2025 = compute_daily_payouts(df_2025)
    jackpot_days_2025 = identify_jackpot_10_days(df_2025)

    # Load 2022-2024 data (as baseline for comparison)
    gq_baseline_path = base_path / "Keno_GPTs" / "Keno_GQ_2022_2023-2024.csv"
    df_baseline = load_gq_data_custom(gq_baseline_path)
    daily_baseline = compute_daily_payouts(df_baseline)
    jackpot_days_baseline = identify_jackpot_10_days(df_baseline)

    # Also load 2018-2024 draw count from raw data for jackpot rate
    keno_2018_path = base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv"
    total_draws_2018_2024 = 0
    if keno_2018_path.exists():
        df_2018 = pd.read_csv(keno_2018_path, sep=";", encoding="utf-8")
        df_2018["parsed_date"] = pd.to_datetime(df_2018["Datum"], format="%d.%m.%Y")
        df_2018 = df_2018[df_2018["parsed_date"].dt.year < 2025]
        total_draws_2018_2024 = len(df_2018)

    # Calculate metrics
    mean_2025 = float(daily_2025.mean()) if len(daily_2025) > 0 else 0.0
    std_2025 = float(daily_2025.std()) if len(daily_2025) > 0 else 0.0
    cv_2025 = std_2025 / mean_2025 if mean_2025 > 0 else 0.0
    n_days_2025 = len(daily_2025)
    n_jackpot_2025 = len(jackpot_days_2025)

    mean_baseline = float(daily_baseline.mean()) if len(daily_baseline) > 0 else 0.0
    std_baseline = float(daily_baseline.std()) if len(daily_baseline) > 0 else 0.0
    cv_baseline = std_baseline / mean_baseline if mean_baseline > 0 else 0.0
    n_days_baseline = len(daily_baseline)
    n_jackpot_baseline = len(jackpot_days_baseline)

    # Test 1: Welch's t-test for mean difference
    if len(daily_2025) > 1 and len(daily_baseline) > 1:
        t_stat, p_value_ttest = stats.ttest_ind(
            daily_2025.values, daily_baseline.values, equal_var=False
        )
    else:
        t_stat, p_value_ttest = 0.0, 1.0

    # Test 2: Bootstrap CI for difference
    if len(daily_2025) > 1 and len(daily_baseline) > 1:
        mean_diff, ci_lower, ci_upper = bootstrap_ci(
            daily_2025.values, daily_baseline.values, n_bootstrap=10000, ci=0.95
        )
    else:
        mean_diff, ci_lower, ci_upper = 0.0, 0.0, 0.0

    # Test 3: Cohen's d effect size
    if len(daily_2025) > 1 and len(daily_baseline) > 1:
        effect_size = cohens_d(daily_2025.values, daily_baseline.values)
    else:
        effect_size = 0.0

    # Test 4: Chi-squared for Jackpot-10 rate
    # Using contingency table: [jackpot_yes, jackpot_no] for 2025 vs baseline
    observed = np.array(
        [
            [n_jackpot_2025, n_days_2025 - n_jackpot_2025],
            [n_jackpot_baseline, n_days_baseline - n_jackpot_baseline],
        ]
    )
    if observed.min() >= 0 and observed.sum() > 0:
        chi2, p_value_chi2, dof, expected = stats.chi2_contingency(observed)
    else:
        chi2, p_value_chi2, dof = 0.0, 1.0, 1

    # Test 5: Levene's test for variance equality (CV proxy)
    if len(daily_2025) > 1 and len(daily_baseline) > 1:
        levene_stat, p_value_levene = stats.levene(
            daily_2025.values, daily_baseline.values
        )
    else:
        levene_stat, p_value_levene = 0.0, 1.0

    # Calculate jackpot rates
    jackpot_rate_2025 = n_jackpot_2025 / n_days_2025 if n_days_2025 > 0 else 0.0
    jackpot_rate_baseline = (
        n_jackpot_baseline / n_days_baseline if n_days_baseline > 0 else 0.0
    )

    # Effect interpretation
    def interpret_effect_size(d: float) -> str:
        d_abs = abs(d)
        if d_abs < 0.2:
            return "negligible"
        elif d_abs < 0.5:
            return "small"
        elif d_abs < 0.8:
            return "medium"
        else:
            return "large"

    # Compile results
    results = {
        "analysis_date": datetime.now().isoformat(),
        "task_id": "TASK_042",
        "description": "2025 Outlier Validation vs 2018-2024 Baseline",
        "data_sources": {
            "2025": str(gq_2025_path),
            "baseline": str(gq_baseline_path),
            "historical_draws": str(keno_2018_path) if keno_2018_path.exists() else None,
        },
        "sample_sizes": {
            "n_days_2025": n_days_2025,
            "n_days_baseline": n_days_baseline,
            "total_draws_2018_2024": total_draws_2018_2024,
        },
        "metrics_2025": {
            "mean_daily_payout": round(mean_2025, 2),
            "std_daily_payout": round(std_2025, 2),
            "cv_payout": round(cv_2025, 4),
            "jackpot_10_count": n_jackpot_2025,
            "jackpot_10_rate": round(jackpot_rate_2025, 4),
        },
        "metrics_baseline": {
            "mean_daily_payout": round(mean_baseline, 2),
            "std_daily_payout": round(std_baseline, 2),
            "cv_payout": round(cv_baseline, 4),
            "jackpot_10_count": n_jackpot_baseline,
            "jackpot_10_rate": round(jackpot_rate_baseline, 4),
        },
        "comparison": {
            "mean_payout_diff_pct": round(
                100 * (mean_2025 - mean_baseline) / mean_baseline
                if mean_baseline > 0
                else 0.0,
                2,
            ),
            "cv_diff": round(cv_2025 - cv_baseline, 4),
            "jackpot_rate_diff_pct": round(
                100 * (jackpot_rate_2025 - jackpot_rate_baseline), 2
            ),
        },
        "statistical_tests": {
            "welch_ttest": {
                "t_statistic": round(t_stat, 4),
                "p_value": round(p_value_ttest, 6),
                "significant_at_005": p_value_ttest < 0.05,
                "interpretation": "2025 mean significantly different"
                if p_value_ttest < 0.05
                else "No significant difference",
            },
            "bootstrap_ci_95": {
                "mean_difference": round(mean_diff, 2),
                "ci_lower": round(ci_lower, 2),
                "ci_upper": round(ci_upper, 2),
                "ci_excludes_zero": (ci_lower > 0) or (ci_upper < 0),
            },
            "cohens_d": {
                "effect_size": round(effect_size, 4),
                "interpretation": interpret_effect_size(effect_size),
            },
            "chi2_jackpot_rate": {
                "chi2_statistic": round(chi2, 4),
                "p_value": round(p_value_chi2, 6),
                "significant_at_005": p_value_chi2 < 0.05,
                "interpretation": "Jackpot rate significantly different"
                if p_value_chi2 < 0.05
                else "No significant difference in jackpot rate",
            },
            "levene_variance": {
                "statistic": round(levene_stat, 4),
                "p_value": round(p_value_levene, 6),
                "significant_at_005": p_value_levene < 0.05,
                "interpretation": "Variance significantly different"
                if p_value_levene < 0.05
                else "No significant variance difference",
            },
        },
        "conclusion": {
            "is_2025_outlier": (p_value_ttest < 0.05)
            or (abs(effect_size) >= 0.5)
            or (p_value_chi2 < 0.05),
            "evidence_summary": [],
        },
    }

    # Build evidence summary
    evidence = []
    if p_value_ttest < 0.05:
        evidence.append(f"Mean payout significantly higher (t={t_stat:.2f}, p={p_value_ttest:.4f})")
    if abs(effect_size) >= 0.2:
        evidence.append(f"Effect size {interpret_effect_size(effect_size)} (d={effect_size:.3f})")
    if p_value_chi2 < 0.05:
        evidence.append(f"Jackpot-10 rate differs (chi2={chi2:.2f}, p={p_value_chi2:.4f})")
    if p_value_levene < 0.05:
        evidence.append(f"Variance differs (Levene={levene_stat:.2f}, p={p_value_levene:.4f})")
    if not evidence:
        evidence.append("No significant differences detected at alpha=0.05")

    results["conclusion"]["evidence_summary"] = evidence

    return results


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, (np.bool_, np.bool)):
        return bool(obj)
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def main():
    """Main entry point."""
    results = run_validation()

    # Convert numpy types for JSON serialization
    results = convert_numpy_types(results)

    # Save results
    output_path = Path(__file__).parent.parent / "results" / "outlier_year_2025_validation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_path}")
    print(f"\nConclusion: 2025 is outlier = {results['conclusion']['is_2025_outlier']}")
    print("Evidence:")
    for e in results["conclusion"]["evidence_summary"]:
        print(f"  - {e}")


if __name__ == "__main__":
    main()
