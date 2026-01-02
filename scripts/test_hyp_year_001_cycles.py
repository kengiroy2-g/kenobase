#!/usr/bin/env python3
"""
TEST HYP_YEAR_001: Jahres-Zyklen (Jahr/Quartal/Monat)

PARADIGMA: AXIOM-FIRST
- Hypothese: Gibt es statistisch signifikante ROI-Unterschiede zwischen
  Jahren, Quartalen oder Monaten?
- Orthogonal zu HYP_CYC_001 (28-Tage Jackpot-Zyklen)
- Nullmodell: Jahr-Permutation (shuffle year labels, preserve draw order within year)

ACCEPTANCE CRITERIA:
- p < 0.05 (nach Bonferroni-Korrektur)
- UND ROI-Differenz > 20%

TRAIN/TEST SPLIT:
- Train: 2022-2024 (~1100 Draws)
- Test OOS: 2025 (~360 Draws)

Author: Kenobase V2.2
Date: 2025-12-30
Artifact: results/hyp_year_001_cycles.json
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from kenobase.core.keno_quotes import get_fixed_quote


# =============================================================================
# CONSTANTS
# =============================================================================

TICKET_V2 = {
    8: [3, 36, 43, 48, 51, 58, 61, 64],
    9: [3, 7, 36, 43, 48, 51, 58, 61, 64],
    10: [3, 7, 13, 36, 43, 48, 51, 58, 61, 64],
}

TICKET_ORIGINAL = {
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
}


# =============================================================================
# DATA LOADING
# =============================================================================


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Load KENO data from CSV."""
    keno_path = base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv"

    if not keno_path.exists():
        raise FileNotFoundError(f"Data file not found: {keno_path}")

    df = pd.read_csv(keno_path, sep=";", encoding="utf-8")
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")

    # Extract numbers as set
    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(
        lambda row: set(row.dropna().astype(int)), axis=1
    )

    df = df.sort_values("Datum").reset_index(drop=True)

    # Add time features
    df["year"] = df["Datum"].dt.year
    df["quarter"] = df["Datum"].dt.quarter
    df["month"] = df["Datum"].dt.month

    return df


def add_win_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add hits and win columns for V2 and Original tickets."""
    for keno_type in [8, 9, 10]:
        ticket_v2 = TICKET_V2[keno_type]
        ticket_orig = TICKET_ORIGINAL[keno_type]

        # Hits
        df[f"v2_hits_t{keno_type}"] = df["numbers_set"].apply(
            lambda s: sum(1 for n in ticket_v2 if n in s)
        )
        df[f"orig_hits_t{keno_type}"] = df["numbers_set"].apply(
            lambda s: sum(1 for n in ticket_orig if n in s)
        )

        # Wins (EUR)
        df[f"v2_win_t{keno_type}"] = df[f"v2_hits_t{keno_type}"].apply(
            lambda h: get_fixed_quote(keno_type, h)
        )
        df[f"orig_win_t{keno_type}"] = df[f"orig_hits_t{keno_type}"].apply(
            lambda h: get_fixed_quote(keno_type, h)
        )

    return df


# =============================================================================
# ROI CALCULATION
# =============================================================================


def calculate_roi(wins: float, n: int) -> float:
    """Calculate ROI as percentage."""
    if n == 0:
        return 0.0
    return (wins - n) / n * 100


def compute_period_stats(
    df: pd.DataFrame,
    group_col: str,
    keno_type: int = 9,
    ticket: str = "v2",
) -> Dict:
    """Compute ROI and stats per period (year/quarter/month)."""
    win_col = f"{ticket}_win_t{keno_type}"

    results = {}
    for period, group in df.groupby(group_col):
        n = len(group)
        total_win = group[win_col].sum()
        roi = calculate_roi(total_win, n)

        results[int(period)] = {
            "n": n,
            "total_win": float(total_win),
            "roi": roi,
        }

    return results


# =============================================================================
# STATISTICAL TESTS
# =============================================================================


def chi_square_hit_distribution(
    df: pd.DataFrame,
    group_col: str,
    keno_type: int = 9,
    ticket: str = "v2",
) -> Dict:
    """
    Chi-square test for hit distribution across periods.

    H0: Hit distribution is the same across all periods.
    """
    hits_col = f"{ticket}_hits_t{keno_type}"

    # Create contingency table: rows = periods, cols = hit counts (0..keno_type)
    periods = sorted(df[group_col].unique())
    hit_range = list(range(keno_type + 1))

    contingency = []
    for period in periods:
        period_df = df[df[group_col] == period]
        hit_counts = period_df[hits_col].value_counts()
        row = [hit_counts.get(h, 0) for h in hit_range]
        contingency.append(row)

    contingency = np.array(contingency)

    # Remove columns with all zeros
    col_sums = contingency.sum(axis=0)
    nonzero_cols = col_sums > 0
    contingency_filtered = contingency[:, nonzero_cols]

    if contingency_filtered.shape[1] < 2:
        return {
            "valid": False,
            "reason": "Not enough hit classes with data",
        }

    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_filtered)

    return {
        "valid": True,
        "chi2": float(chi2),
        "p_value": float(p_value),
        "dof": int(dof),
        "n_periods": len(periods),
        "n_hit_classes": int(contingency_filtered.shape[1]),
    }


def kruskal_wallis_test(
    df: pd.DataFrame,
    group_col: str,
    keno_type: int = 9,
    ticket: str = "v2",
) -> Dict:
    """
    Kruskal-Wallis H-test for ROI/wins across periods.

    H0: All periods have the same distribution of wins.
    """
    win_col = f"{ticket}_win_t{keno_type}"

    groups = []
    for period, group in df.groupby(group_col):
        groups.append(group[win_col].values)

    if len(groups) < 2:
        return {
            "valid": False,
            "reason": "Not enough periods for comparison",
        }

    stat, p_value = stats.kruskal(*groups)

    return {
        "valid": True,
        "statistic": float(stat),
        "p_value": float(p_value),
        "n_groups": len(groups),
    }


# =============================================================================
# NULL MODEL: YEAR PERMUTATION
# =============================================================================


def run_year_permutation_null_model(
    df: pd.DataFrame,
    keno_type: int = 9,
    ticket: str = "v2",
    n_permutations: int = 1000,
) -> Dict:
    """
    Null model: Shuffle year labels, preserve draw order within year.

    Compare observed ROI variance with permutation distribution.
    """
    win_col = f"{ticket}_win_t{keno_type}"

    # Observed variance of ROI per year
    observed_stats = compute_period_stats(df, "year", keno_type, ticket)
    observed_rois = [v["roi"] for v in observed_stats.values()]
    observed_variance = np.var(observed_rois)
    observed_range = max(observed_rois) - min(observed_rois)

    # Permutation test
    permuted_variances = []
    permuted_ranges = []

    for _ in range(n_permutations):
        # Shuffle year labels
        df_perm = df.copy()
        years = df_perm["year"].values.copy()
        np.random.shuffle(years)
        df_perm["year"] = years

        # Compute ROI per permuted year
        perm_stats = compute_period_stats(df_perm, "year", keno_type, ticket)
        perm_rois = [v["roi"] for v in perm_stats.values()]

        permuted_variances.append(np.var(perm_rois))
        permuted_ranges.append(max(perm_rois) - min(perm_rois))

    # p-value: fraction of permutations with >= observed variance
    p_value_var = np.mean(np.array(permuted_variances) >= observed_variance)
    p_value_range = np.mean(np.array(permuted_ranges) >= observed_range)

    return {
        "observed_variance": float(observed_variance),
        "observed_range": float(observed_range),
        "permuted_variance_mean": float(np.mean(permuted_variances)),
        "permuted_variance_std": float(np.std(permuted_variances)),
        "permuted_range_mean": float(np.mean(permuted_ranges)),
        "permuted_range_std": float(np.std(permuted_ranges)),
        "p_value_variance": float(p_value_var),
        "p_value_range": float(p_value_range),
        "n_permutations": n_permutations,
    }


# =============================================================================
# TRAIN/TEST SPLIT
# =============================================================================


def train_test_split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split data: Train 2022-2024, Test OOS 2025."""
    train_df = df[df["year"].isin([2022, 2023, 2024])].copy()
    test_df = df[df["year"] == 2025].copy()
    return train_df, test_df


# =============================================================================
# MAIN TEST
# =============================================================================


def test_hyp_year_001(base_path: Path) -> Dict:
    """
    Main test for HYP_YEAR_001: Jahres-Zyklen.

    Tests:
    1. ROI by Year (2022, 2023, 2024, 2025)
    2. ROI by Quarter (Q1-Q4)
    3. ROI by Month (1-12)
    4. Chi-square on hit distribution
    5. Kruskal-Wallis test
    6. Year-permutation null model
    7. Train (2022-2024) vs Test OOS (2025)
    """
    print("=" * 70)
    print("TEST HYP_YEAR_001: Jahres-Zyklen (Jahr/Quartal/Monat)")
    print("PARADIGMA: AXIOM-FIRST")
    print("=" * 70)

    results = {
        "hypothesis_id": "HYP_YEAR_001",
        "hypothesis_name": "Jahres-Zyklen",
        "orthogonal_to": "HYP_CYC_001 (28-Tage Jackpot-Zyklen)",
        "acceptance_criteria": {
            "p_threshold": 0.05,
            "bonferroni_tests": 0,  # Will be updated
            "roi_diff_threshold_pct": 20.0,
        },
        "data_source": "data/raw/keno/KENO_ab_2022_bereinigt.csv",
    }

    # Load data
    print("\n[1] Loading data...")
    df = load_keno_data(base_path)
    df = add_win_columns(df)

    n_total = len(df)
    date_min = df["Datum"].min().strftime("%Y-%m-%d")
    date_max = df["Datum"].max().strftime("%Y-%m-%d")

    results["data_summary"] = {
        "n_total": n_total,
        "date_range": f"{date_min} to {date_max}",
        "years": sorted(df["year"].unique().tolist()),
    }

    print(f"  Loaded: N={n_total} draws")
    print(f"  Date range: {date_min} to {date_max}")
    print(f"  Years: {results['data_summary']['years']}")

    # Train/Test split
    train_df, test_df = train_test_split(df)
    n_train = len(train_df)
    n_test = len(test_df)

    results["train_test_split"] = {
        "train_years": [2022, 2023, 2024],
        "train_n": n_train,
        "test_year": 2025,
        "test_n": n_test,
    }

    print(f"\n  Train: N={n_train} (2022-2024)")
    print(f"  Test OOS: N={n_test} (2025)")

    # Count tests for Bonferroni
    n_tests = 0

    # ==========================================================================
    # TEST 2: ROI by Year
    # ==========================================================================
    print("\n[2] ROI by Year...")
    results["by_year"] = {}

    for keno_type in [8, 9, 10]:
        year_stats = compute_period_stats(df, "year", keno_type, "v2")
        results["by_year"][f"typ_{keno_type}"] = year_stats

        print(f"\n  Typ {keno_type}:")
        for year, stat in sorted(year_stats.items()):
            print(f"    {year}: N={stat['n']}, ROI={stat['roi']:+.1f}%")

        # ROI range
        rois = [s["roi"] for s in year_stats.values()]
        roi_range = max(rois) - min(rois)
        print(f"    ROI Range: {roi_range:.1f}%")

    # ==========================================================================
    # TEST 3: ROI by Quarter
    # ==========================================================================
    print("\n[3] ROI by Quarter...")
    results["by_quarter"] = {}

    for keno_type in [9]:  # Focus on Typ 9
        quarter_stats = compute_period_stats(df, "quarter", keno_type, "v2")
        results["by_quarter"][f"typ_{keno_type}"] = quarter_stats

        print(f"\n  Typ {keno_type}:")
        for q, stat in sorted(quarter_stats.items()):
            print(f"    Q{q}: N={stat['n']}, ROI={stat['roi']:+.1f}%")

    # ==========================================================================
    # TEST 4: ROI by Month
    # ==========================================================================
    print("\n[4] ROI by Month...")
    results["by_month"] = {}

    for keno_type in [9]:  # Focus on Typ 9
        month_stats = compute_period_stats(df, "month", keno_type, "v2")
        results["by_month"][f"typ_{keno_type}"] = month_stats

        print(f"\n  Typ {keno_type}:")
        for m, stat in sorted(month_stats.items()):
            print(f"    Month {m:2d}: N={stat['n']}, ROI={stat['roi']:+.1f}%")

        # Best/Worst months
        sorted_months = sorted(month_stats.items(), key=lambda x: -x[1]["roi"])
        best_month = sorted_months[0]
        worst_month = sorted_months[-1]

        print(f"\n    Best Month: {best_month[0]} ({best_month[1]['roi']:+.1f}%)")
        print(f"    Worst Month: {worst_month[0]} ({worst_month[1]['roi']:+.1f}%)")

    # ==========================================================================
    # TEST 5: Chi-square on Hit Distribution
    # ==========================================================================
    print("\n[5] Chi-square Tests (Hit Distribution)...")
    results["chi_square_tests"] = {}

    for granularity in ["year", "quarter", "month"]:
        chi2_result = chi_square_hit_distribution(df, granularity, 9, "v2")
        results["chi_square_tests"][granularity] = chi2_result
        n_tests += 1

        if chi2_result["valid"]:
            print(f"  {granularity}: Chi2={chi2_result['chi2']:.2f}, p={chi2_result['p_value']:.4f}")
        else:
            print(f"  {granularity}: {chi2_result['reason']}")

    # ==========================================================================
    # TEST 6: Kruskal-Wallis Test
    # ==========================================================================
    print("\n[6] Kruskal-Wallis Tests (Wins Distribution)...")
    results["kruskal_wallis_tests"] = {}

    for granularity in ["year", "quarter", "month"]:
        kw_result = kruskal_wallis_test(df, granularity, 9, "v2")
        results["kruskal_wallis_tests"][granularity] = kw_result
        n_tests += 1

        if kw_result["valid"]:
            print(f"  {granularity}: H={kw_result['statistic']:.2f}, p={kw_result['p_value']:.4f}")
        else:
            print(f"  {granularity}: {kw_result['reason']}")

    # ==========================================================================
    # TEST 7: Null Model (Year Permutation)
    # ==========================================================================
    print("\n[7] Null Model: Year Permutation (1000 iterations)...")
    null_result = run_year_permutation_null_model(df, 9, "v2", 1000)
    results["null_model"] = null_result
    n_tests += 2  # variance + range tests

    print(f"  Observed ROI Variance: {null_result['observed_variance']:.2f}")
    print(f"  Permuted Mean Variance: {null_result['permuted_variance_mean']:.2f} +/- {null_result['permuted_variance_std']:.2f}")
    print(f"  p-value (variance): {null_result['p_value_variance']:.4f}")
    print(f"\n  Observed ROI Range: {null_result['observed_range']:.1f}%")
    print(f"  Permuted Mean Range: {null_result['permuted_range_mean']:.1f}% +/- {null_result['permuted_range_std']:.1f}%")
    print(f"  p-value (range): {null_result['p_value_range']:.4f}")

    # ==========================================================================
    # TEST 8: Train vs Test OOS Comparison
    # ==========================================================================
    print("\n[8] Train (2022-2024) vs Test OOS (2025)...")
    results["train_vs_test"] = {}

    for keno_type in [8, 9, 10]:
        # Train stats (aggregated)
        train_wins = train_df[f"v2_win_t{keno_type}"].sum()
        train_roi = calculate_roi(train_wins, n_train)

        # Test stats
        test_wins = test_df[f"v2_win_t{keno_type}"].sum()
        test_roi = calculate_roi(test_wins, n_test)

        diff = test_roi - train_roi

        results["train_vs_test"][f"typ_{keno_type}"] = {
            "train_n": n_train,
            "train_roi": train_roi,
            "test_n": n_test,
            "test_roi": test_roi,
            "diff": diff,
            "significant_diff": abs(diff) > 20.0,
        }

        print(f"  Typ {keno_type}:")
        print(f"    Train ROI: {train_roi:+.1f}%")
        print(f"    Test OOS ROI: {test_roi:+.1f}%")
        print(f"    Diff: {diff:+.1f}% {'***' if abs(diff) > 20 else ''}")

    # ==========================================================================
    # SUMMARY & CONCLUSION
    # ==========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY & CONCLUSION")
    print("=" * 70)

    # Bonferroni correction
    results["acceptance_criteria"]["bonferroni_tests"] = n_tests
    bonferroni_alpha = 0.05 / n_tests
    results["acceptance_criteria"]["bonferroni_alpha"] = bonferroni_alpha

    print(f"\n  Total tests: {n_tests}")
    print(f"  Bonferroni-corrected alpha: {bonferroni_alpha:.5f}")

    # Check which tests are significant
    significant_tests = []

    for granularity, chi2 in results["chi_square_tests"].items():
        if chi2.get("valid") and chi2.get("p_value", 1.0) < bonferroni_alpha:
            significant_tests.append(f"Chi2_{granularity}")

    for granularity, kw in results["kruskal_wallis_tests"].items():
        if kw.get("valid") and kw.get("p_value", 1.0) < bonferroni_alpha:
            significant_tests.append(f"KW_{granularity}")

    if null_result["p_value_variance"] < bonferroni_alpha:
        significant_tests.append("NullModel_variance")
    if null_result["p_value_range"] < bonferroni_alpha:
        significant_tests.append("NullModel_range")

    results["significant_tests"] = significant_tests

    print(f"\n  Significant after Bonferroni: {len(significant_tests)}")
    for test in significant_tests:
        print(f"    - {test}")

    if not significant_tests:
        print("    (None)")

    # ROI difference check
    roi_diffs_over_20 = []

    for keno_type in [8, 9, 10]:
        year_stats = results["by_year"][f"typ_{keno_type}"]
        rois = [s["roi"] for s in year_stats.values()]
        roi_range = max(rois) - min(rois)
        if roi_range > 20.0:
            roi_diffs_over_20.append(f"Year_Typ{keno_type} (range={roi_range:.1f}%)")

    results["roi_diffs_over_20"] = roi_diffs_over_20

    print(f"\n  ROI differences > 20%:")
    for diff in roi_diffs_over_20:
        print(f"    - {diff}")

    if not roi_diffs_over_20:
        print("    (None)")

    # Final verdict
    is_significant = len(significant_tests) > 0 and len(roi_diffs_over_20) > 0

    results["conclusion"] = {
        "is_significant": is_significant,
        "verdict": "BESTAETIGT" if is_significant else "NICHT SIGNIFIKANT",
        "summary": (
            f"Jahres-Zyklen sind {'signifikant' if is_significant else 'NICHT signifikant'} "
            f"(p < {bonferroni_alpha:.5f} nach Bonferroni). "
            f"ROI-Unterschiede {'ueber' if roi_diffs_over_20 else 'unter'} 20% Schwelle."
        ),
    }

    print(f"\n  === VERDICT: {results['conclusion']['verdict']} ===")
    print(f"  {results['conclusion']['summary']}")

    # Recommendations
    if is_significant:
        results["recommendations"] = [
            "1. Beruecksichtige Jahr/Quartal/Monat bei Strategie-Auswahl",
            "2. Beste/schlechteste Perioden fuer selektives Spielen nutzen",
            "3. Kombinieren mit HYP_CYC_001 (28-Tage-Zyklen) fuer Multi-Faktor-Modell",
        ]
    else:
        results["recommendations"] = [
            "1. Keine systematischen Jahres-Zyklen gefunden",
            "2. Fokussiere auf HYP_CYC_001 (28-Tage Jackpot-Zyklen) stattdessen",
            "3. Jahr/Quartal/Monat nicht als Timing-Faktor verwenden",
        ]

    print("\n  Recommendations:")
    for rec in results["recommendations"]:
        print(f"    {rec}")

    return results


# =============================================================================
# MAIN
# =============================================================================


def main():
    base_path = Path(__file__).parent.parent

    # Run test
    results = test_hyp_year_001(base_path)

    # Add metadata
    results["metadata"] = {
        "script": "scripts/test_hyp_year_001_cycles.py",
        "timestamp": datetime.now().isoformat(),
        "repro_command": "python scripts/test_hyp_year_001_cycles.py",
    }

    # Save results
    output_path = base_path / "results" / "hyp_year_001_cycles.json"

    def json_serializer(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return str(obj)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=json_serializer)

    print(f"\n\nResults saved: {output_path}")
    print("\n" + "=" * 70)
    print("HYP_YEAR_001 TEST COMPLETE")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
