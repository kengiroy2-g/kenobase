#!/usr/bin/env python3
"""
COOLDOWN RULE ISOLATED TEST (SYN_001)

Tests the Cooldown-Rule (WL-003) in isolation with proper statistical controls.

Axiom-First Approach:
- Axiom A1 (House-Edge): Nach Jackpot muss System sparen = weniger Gewinne
- Axiom A7 (Reset-Zyklen): System "spart" nach Jackpots

Hypothesis: ROI im 30-Tage Cooldown nach Jackpot ist niedriger als Normal-Periode.

Controls:
- Train/Test Split: 2022-2023 (Train) vs 2024 (Test)
- Negative Control: Random 30d windows (ohne Jackpot-Bezug)
- Chi2-Test + Mann-Whitney U fuer statistische Signifikanz

Output: results/cooldown_rule_isolated_test.json

Repro: python scripts/test_cooldown_rule_isolated.py
"""

import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np
from scipy import stats

from kenobase.core.keno_quotes import KENO_FIXED_QUOTES_BY_TYPE


# ============================================================================
# KENO QUOTES
# ============================================================================

KENO_QUOTES = {
    int(keno_type): {int(hits): float(quote) for hits, quote in mapping.items()}
    for keno_type, mapping in KENO_FIXED_QUOTES_BY_TYPE.items()
}


# ============================================================================
# REFERENCE TICKETS (from existing analysis)
# ============================================================================

REFERENCE_TICKETS = {
    6: [3, 9, 10, 32, 49, 64],
    7: [3, 24, 30, 49, 51, 59, 64],
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
}


# ============================================================================
# DATA LOADING
# ============================================================================

def load_data(base_path: Path) -> Tuple[pd.DataFrame, List[datetime]]:
    """Loads KENO and Jackpot data."""

    # KENO Daten
    keno_paths = [
        base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    ]

    keno_df = None
    for p in keno_paths:
        if p.exists():
            keno_df = pd.read_csv(p, sep=";", encoding="utf-8")
            keno_df["Datum"] = pd.to_datetime(keno_df["Datum"], format="%d.%m.%Y")
            break

    if keno_df is None:
        raise FileNotFoundError("Keine KENO-Datendatei gefunden")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    keno_df["positions"] = keno_df[pos_cols].apply(lambda row: list(row), axis=1)
    keno_df["numbers_set"] = keno_df[pos_cols].apply(lambda row: set(row), axis=1)
    keno_df = keno_df.sort_values("Datum").reset_index(drop=True)

    # Jackpot Daten (10/10 events)
    gk1_path = base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv"
    jackpot_dates = []
    if gk1_path.exists():
        gk1_df = pd.read_csv(gk1_path, encoding="utf-8")
        gk1_df["Datum"] = pd.to_datetime(gk1_df["Datum"], format="%d.%m.%Y")
        jackpot_dates = sorted(gk1_df[gk1_df["Keno-Typ"] == 10]["Datum"].tolist())

    return keno_df, jackpot_dates


# ============================================================================
# COOLDOWN DETECTION (exakt 30 Tage)
# ============================================================================

def is_in_cooldown(
    date: datetime,
    jackpot_dates: List[datetime],
    cooldown_days: int = 30
) -> Tuple[bool, int]:
    """
    Determines if a date is in 30-day cooldown window.

    Cooldown-Semantik (WL-003):
    - cooldown: 0 < days_since_jackpot <= 30
    - normal:   days_since_jackpot > 30 or no prior jackpot
    """
    if not jackpot_dates:
        return False, -1

    past_jackpots = [jp for jp in jackpot_dates if jp < date]
    if not past_jackpots:
        return False, -1

    last_jackpot = max(past_jackpots)
    days_since = (date - last_jackpot).days

    is_cd = 0 < days_since <= cooldown_days
    return is_cd, days_since


# ============================================================================
# TICKET SIMULATION
# ============================================================================

def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simulates a ticket against a draw."""
    hits = sum(1 for n in ticket if n in draw_set)
    win = KENO_QUOTES.get(keno_type, {}).get(hits, 0)
    return win, hits


# ============================================================================
# BACKTEST FUNCTION
# ============================================================================

def backtest_cooldown_isolated(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int,
    ticket: List[int],
    date_filter: Tuple[datetime, datetime] = None
) -> Dict:
    """
    Runs isolated cooldown backtest.

    Returns separate ROI for cooldown (0-30d) vs normal (>30d) periods.
    """
    results = {
        "cooldown": {"invested": 0, "won": 0, "draws": [], "rois": []},
        "normal": {"invested": 0, "won": 0, "draws": [], "rois": []},
    }

    for i in range(1, len(keno_df)):
        row = keno_df.iloc[i]
        curr_date = row["Datum"]

        # Apply date filter if specified
        if date_filter:
            start_date, end_date = date_filter
            if curr_date < start_date or curr_date > end_date:
                continue

        is_cd, days_since = is_in_cooldown(curr_date, jackpot_dates)

        # Simulate ticket
        draw_set = row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        phase = "cooldown" if is_cd else "normal"
        results[phase]["invested"] += 1
        results[phase]["won"] += win
        results[phase]["draws"].append({
            "date": str(curr_date.date()),
            "hits": hits,
            "win": win,
            "days_since_jackpot": days_since
        })

        # Per-draw ROI for Mann-Whitney
        draw_roi = (win - 1) / 1 * 100  # ROI per 1 EUR
        results[phase]["rois"].append(draw_roi)

    # Calculate aggregate ROI
    for phase in ["cooldown", "normal"]:
        inv = results[phase]["invested"]
        won = results[phase]["won"]
        if inv > 0:
            results[phase]["roi"] = (won - inv) / inv * 100
        else:
            results[phase]["roi"] = 0.0

    return results


# ============================================================================
# NEGATIVE CONTROL: Random 30d Windows
# ============================================================================

def generate_random_windows(
    keno_df: pd.DataFrame,
    n_windows: int,
    window_days: int = 30,
    exclude_jackpots: List[datetime] = None,
    seed: int = 42
) -> List[Tuple[datetime, datetime]]:
    """
    Generates random 30-day windows that do NOT start at jackpot dates.

    Used as negative control to compare with actual cooldown windows.
    """
    random.seed(seed)

    min_date = keno_df["Datum"].min()
    max_date = keno_df["Datum"].max() - timedelta(days=window_days)

    if exclude_jackpots is None:
        exclude_jackpots = []

    exclude_set = set(jp.date() for jp in exclude_jackpots)

    all_dates = keno_df[keno_df["Datum"] <= max_date]["Datum"].tolist()
    eligible_dates = [d for d in all_dates if d.date() not in exclude_set]

    selected_dates = random.sample(eligible_dates, min(n_windows, len(eligible_dates)))

    windows = []
    for start in selected_dates:
        end = start + timedelta(days=window_days)
        windows.append((start, end))

    return windows


def backtest_random_windows(
    keno_df: pd.DataFrame,
    random_windows: List[Tuple[datetime, datetime]],
    keno_type: int,
    ticket: List[int]
) -> Dict:
    """
    Backtest on random windows (negative control).

    Returns aggregated ROI across random windows.
    """
    results = {
        "total_invested": 0,
        "total_won": 0,
        "window_rois": [],
        "all_draw_rois": []
    }

    for start, end in random_windows:
        window_invested = 0
        window_won = 0

        for i in range(len(keno_df)):
            row = keno_df.iloc[i]
            curr_date = row["Datum"]

            if curr_date < start or curr_date > end:
                continue

            draw_set = row["numbers_set"]
            win, hits = simulate_ticket(ticket, keno_type, draw_set)

            window_invested += 1
            window_won += win
            results["all_draw_rois"].append((win - 1) * 100)

        if window_invested > 0:
            window_roi = (window_won - window_invested) / window_invested * 100
            results["window_rois"].append(window_roi)

        results["total_invested"] += window_invested
        results["total_won"] += window_won

    if results["total_invested"] > 0:
        results["avg_roi"] = (
            (results["total_won"] - results["total_invested"]) /
            results["total_invested"] * 100
        )
    else:
        results["avg_roi"] = 0.0

    return results


# ============================================================================
# STATISTICAL TESTS
# ============================================================================

def chi2_test_high_wins(
    cooldown_draws: List[Dict],
    normal_draws: List[Dict],
    high_win_threshold: int = 100
) -> Dict:
    """
    Chi2-Test for high-win rate difference between cooldown and normal.

    H0: High-win rate is equal in cooldown and normal periods.
    """
    cooldown_n = len(cooldown_draws)
    normal_n = len(normal_draws)

    cooldown_high = sum(1 for d in cooldown_draws if d["win"] >= high_win_threshold)
    normal_high = sum(1 for d in normal_draws if d["win"] >= high_win_threshold)

    # Contingency table: [[cooldown_high, cooldown_low], [normal_high, normal_low]]
    observed = np.array([
        [cooldown_high, cooldown_n - cooldown_high],
        [normal_high, normal_n - normal_high]
    ])

    # Chi2 test (with continuity correction)
    # Guard against zero expected values
    try:
        if observed.sum() > 0 and (cooldown_high + normal_high) > 0:
            chi2, p_value, dof, expected = stats.chi2_contingency(observed, correction=True)
        else:
            chi2, p_value = 0.0, 1.0
    except ValueError:
        # Expected frequencies may be zero - use Fisher's exact if available
        try:
            _, p_value = stats.fisher_exact(observed)
            chi2 = 0.0  # Fisher's doesn't give chi2
        except Exception:
            chi2, p_value = 0.0, 1.0

    return {
        "cooldown_high_wins": cooldown_high,
        "cooldown_total": cooldown_n,
        "cooldown_rate": cooldown_high / cooldown_n * 100 if cooldown_n > 0 else 0,
        "normal_high_wins": normal_high,
        "normal_total": normal_n,
        "normal_rate": normal_high / normal_n * 100 if normal_n > 0 else 0,
        "chi2": chi2,
        "p_value": p_value,
        "significant": p_value < 0.05
    }


def mann_whitney_test(cooldown_rois: List[float], normal_rois: List[float]) -> Dict:
    """
    Mann-Whitney U test for ROI distribution difference.

    H0: ROI distributions are equal.
    """
    if len(cooldown_rois) < 5 or len(normal_rois) < 5:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "note": "Insufficient samples"
        }

    statistic, p_value = stats.mannwhitneyu(
        cooldown_rois, normal_rois, alternative="two-sided"
    )

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
        "cooldown_median": float(np.median(cooldown_rois)),
        "normal_median": float(np.median(normal_rois))
    }


# ============================================================================
# MAIN TEST FUNCTION
# ============================================================================

def run_isolated_cooldown_test(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_types: List[int] = [6, 7, 8, 9, 10]
) -> Dict:
    """
    Runs the isolated cooldown test with all controls.

    Returns:
    - Train/Test split results
    - Negative control comparison
    - Statistical tests
    """

    # Date splits
    train_end = datetime(2023, 12, 31)
    test_start = datetime(2024, 1, 1)

    train_jackpots = [jp for jp in jackpot_dates if jp <= train_end]
    test_jackpots = [jp for jp in jackpot_dates if jp > train_end]

    results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "cooldown_semantics": {
                "cooldown": "0-30 Tage nach 10/10 Jackpot",
                "normal": ">30 Tage nach Jackpot"
            },
            "train_period": "2022-2023",
            "test_period": "2024",
            "train_jackpots": len(train_jackpots),
            "test_jackpots": len(test_jackpots),
            "total_jackpots": len(jackpot_dates)
        },
        "by_type": {},
        "negative_control": {},
        "summary": {}
    }

    for keno_type in keno_types:
        ticket = REFERENCE_TICKETS[keno_type]

        # TRAIN: 2022-2023
        train_min = keno_df["Datum"].min()
        train_results = backtest_cooldown_isolated(
            keno_df, jackpot_dates, keno_type, ticket,
            date_filter=(train_min, train_end)
        )

        # TEST: 2024
        test_max = keno_df["Datum"].max()
        test_results = backtest_cooldown_isolated(
            keno_df, jackpot_dates, keno_type, ticket,
            date_filter=(test_start, test_max)
        )

        # NEGATIVE CONTROL: Random 30d windows
        random_windows = generate_random_windows(
            keno_df, n_windows=len(jackpot_dates), window_days=30,
            exclude_jackpots=jackpot_dates, seed=42
        )
        negative_control = backtest_random_windows(
            keno_df, random_windows, keno_type, ticket
        )

        # Statistical tests
        train_chi2 = chi2_test_high_wins(
            train_results["cooldown"]["draws"],
            train_results["normal"]["draws"]
        )

        test_chi2 = chi2_test_high_wins(
            test_results["cooldown"]["draws"],
            test_results["normal"]["draws"]
        )

        train_mw = mann_whitney_test(
            train_results["cooldown"]["rois"],
            train_results["normal"]["rois"]
        )

        test_mw = mann_whitney_test(
            test_results["cooldown"]["rois"],
            test_results["normal"]["rois"]
        )

        # Compare cooldown ROI vs negative control
        cooldown_vs_control_mw = mann_whitney_test(
            train_results["cooldown"]["rois"] + test_results["cooldown"]["rois"],
            negative_control["all_draw_rois"]
        )

        # Build results for this type
        type_result = {
            "ticket": ticket,
            "train": {
                "cooldown_draws": train_results["cooldown"]["invested"],
                "cooldown_roi": train_results["cooldown"]["roi"],
                "normal_draws": train_results["normal"]["invested"],
                "normal_roi": train_results["normal"]["roi"],
                "delta_roi": train_results["cooldown"]["roi"] - train_results["normal"]["roi"],
                "chi2_test": train_chi2,
                "mann_whitney": train_mw
            },
            "test": {
                "cooldown_draws": test_results["cooldown"]["invested"],
                "cooldown_roi": test_results["cooldown"]["roi"],
                "normal_draws": test_results["normal"]["invested"],
                "normal_roi": test_results["normal"]["roi"],
                "delta_roi": test_results["cooldown"]["roi"] - test_results["normal"]["roi"],
                "chi2_test": test_chi2,
                "mann_whitney": test_mw
            },
            "negative_control": {
                "n_windows": len(random_windows),
                "total_draws": negative_control["total_invested"],
                "avg_roi": negative_control["avg_roi"],
                "cooldown_vs_control": cooldown_vs_control_mw
            }
        }

        results["by_type"][f"typ_{keno_type}"] = type_result
        results["negative_control"][f"typ_{keno_type}"] = {
            "window_rois": negative_control["window_rois"][:5],  # Sample only
            "avg_roi": negative_control["avg_roi"]
        }

    # Summary
    train_cooldown_worse = 0
    test_cooldown_worse = 0
    significant_count = 0

    for typ_key, typ_data in results["by_type"].items():
        if typ_data["train"]["delta_roi"] < 0:
            train_cooldown_worse += 1
        if typ_data["test"]["delta_roi"] < 0:
            test_cooldown_worse += 1
        if typ_data["train"]["chi2_test"]["significant"] or typ_data["test"]["chi2_test"]["significant"]:
            significant_count += 1

    results["summary"] = {
        "total_types_tested": len(keno_types),
        "train_cooldown_worse": train_cooldown_worse,
        "test_cooldown_worse": test_cooldown_worse,
        "significant_effects": significant_count,
        "hypothesis_status": (
            "CONFIRMED" if train_cooldown_worse >= 3 and test_cooldown_worse >= 1
            else "WEAK" if train_cooldown_worse >= 2
            else "NOT_CONFIRMED"
        ),
        "statistical_power_warning": (
            "LOW - Only {0} jackpots in total, Chi2 test may lack power".format(
                len(jackpot_dates)
            )
        )
    }

    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function for isolated cooldown test."""
    print("=" * 70)
    print("COOLDOWN RULE ISOLATED TEST (SYN_001)")
    print("=" * 70)
    print()
    print("Cooldown-Semantik (WL-003 konform):")
    print("  - cooldown: 0-30 Tage nach 10/10 Jackpot")
    print("  - normal:   >30 Tage nach Jackpot")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots (10/10): {len(jackpot_dates)}")

    # Filter for test period (2022-2024)
    keno_df = keno_df[keno_df["Datum"] >= datetime(2022, 1, 1)]
    keno_df = keno_df.reset_index(drop=True)
    print(f"  Gefiltert (2022+): {len(keno_df)} Ziehungen")

    # Show jackpot dates
    print(f"\nJackpot-Daten:")
    for i, jp in enumerate(jackpot_dates[:5], 1):
        print(f"  {i}. {jp.date()}")
    if len(jackpot_dates) > 5:
        print(f"  ... und {len(jackpot_dates) - 5} weitere")

    # Run test
    print("\n" + "=" * 70)
    print("RUNNING ISOLATED COOLDOWN TEST...")
    print("=" * 70)

    results = run_isolated_cooldown_test(keno_df, jackpot_dates)

    # Output results
    for typ_key, typ_data in results["by_type"].items():
        print(f"\n  {typ_key.upper()}:")
        print(f"    TRAIN (2022-2023):")
        print(f"      Cooldown: {typ_data['train']['cooldown_draws']} draws, ROI: {typ_data['train']['cooldown_roi']:+.2f}%")
        print(f"      Normal:   {typ_data['train']['normal_draws']} draws, ROI: {typ_data['train']['normal_roi']:+.2f}%")
        print(f"      Delta:    {typ_data['train']['delta_roi']:+.2f}%")
        print(f"      Chi2 p:   {typ_data['train']['chi2_test']['p_value']:.4f}")

        print(f"    TEST (2024):")
        print(f"      Cooldown: {typ_data['test']['cooldown_draws']} draws, ROI: {typ_data['test']['cooldown_roi']:+.2f}%")
        print(f"      Normal:   {typ_data['test']['normal_draws']} draws, ROI: {typ_data['test']['normal_roi']:+.2f}%")
        print(f"      Delta:    {typ_data['test']['delta_roi']:+.2f}%")

        print(f"    NEGATIVE CONTROL:")
        print(f"      Random windows ROI: {typ_data['negative_control']['avg_roi']:+.2f}%")

    # Save results
    output_path = base_path / "results" / "cooldown_rule_isolated_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    summary = results["summary"]
    print(f"\n  Types tested:         {summary['total_types_tested']}")
    print(f"  Train cooldown worse: {summary['train_cooldown_worse']}/{summary['total_types_tested']}")
    print(f"  Test cooldown worse:  {summary['test_cooldown_worse']}/{summary['total_types_tested']}")
    print(f"  Significant effects:  {summary['significant_effects']}")
    print(f"\n  Hypothesis status:    {summary['hypothesis_status']}")
    print(f"  Warning:              {summary['statistical_power_warning']}")

    print("\n" + "=" * 70)
    print("REPRO COMMAND:")
    print("  python scripts/test_cooldown_rule_isolated.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
