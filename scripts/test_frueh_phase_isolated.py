#!/usr/bin/env python3
"""
FRUEH-PHASE ISOLATED TEST (SYN_002)

Tests the FRUEH-Phase (Day 1-14 after Jackpot) in isolation with proper statistical controls.

Axiom-First Approach:
- Axiom A1 (House-Edge): Nach Jackpot muss System sparen = weniger Gewinne
- Axiom A7 (Reset-Zyklen): System "spart" nach Jackpots

Hypothesis: ROI in FRUEH-Phase (1-14d) ist niedriger als SPAET-Phase (15-30d) und NORMAL (>30d).

Sub-Cooldown Semantik:
- FRUEH: 1-14 Tage nach 10/10 Jackpot (strikter Cooldown)
- SPAET: 15-30 Tage nach 10/10 Jackpot (Erholungsphase)
- NORMAL: >30 Tage nach Jackpot (keine Cooldown)

Controls:
- Train/Test Split: 2022-2023 (Train) vs 2024 (Test)
- Negative Control: Random windows (ohne Jackpot-Bezug)
- Chi2-Test + Mann-Whitney U fuer statistische Signifikanz

Output: results/frueh_phase_isolated_test.json

Repro: python scripts/test_frueh_phase_isolated.py
"""

import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from kenobase.core.keno_quotes import KENO_FIXED_QUOTES_BY_TYPE
from kenobase.analysis.cycle_phases import (
    SubCooldownPhase,
    get_sub_cooldown_phase,
    FRUEH_MAX_DAYS,
    SPAET_MAX_DAYS,
)


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
# SUB-COOLDOWN DETECTION
# ============================================================================

def get_sub_phase(
    date: datetime,
    jackpot_dates: List[datetime]
) -> Tuple[SubCooldownPhase, int]:
    """
    Determines the sub-cooldown phase for a date.

    Returns:
        (SubCooldownPhase, days_since_jackpot)
    """
    if not jackpot_dates:
        return SubCooldownPhase.UNKNOWN, -1

    past_jackpots = [jp for jp in jackpot_dates if jp < date]
    if not past_jackpots:
        return SubCooldownPhase.UNKNOWN, -1

    last_jackpot = max(past_jackpots)
    days_since = (date - last_jackpot).days

    phase = get_sub_cooldown_phase(days_since)
    return phase, days_since


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

def backtest_sub_cooldown_isolated(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int,
    ticket: List[int],
    date_filter: Tuple[datetime, datetime] = None
) -> Dict:
    """
    Runs isolated sub-cooldown backtest.

    Returns separate ROI for FRUEH (1-14d) vs SPAET (15-30d) vs NORMAL (>30d).
    """
    results = {
        "frueh": {"invested": 0, "won": 0, "draws": [], "rois": []},
        "spaet": {"invested": 0, "won": 0, "draws": [], "rois": []},
        "normal": {"invested": 0, "won": 0, "draws": [], "rois": []},
    }

    phase_map = {
        SubCooldownPhase.FRUEH: "frueh",
        SubCooldownPhase.SPAET: "spaet",
        SubCooldownPhase.NORMAL: "normal",
    }

    for i in range(1, len(keno_df)):
        row = keno_df.iloc[i]
        curr_date = row["Datum"]

        # Apply date filter if specified
        if date_filter:
            start_date, end_date = date_filter
            if curr_date < start_date or curr_date > end_date:
                continue

        sub_phase, days_since = get_sub_phase(curr_date, jackpot_dates)

        # Skip UNKNOWN
        if sub_phase == SubCooldownPhase.UNKNOWN:
            continue

        # Simulate ticket
        draw_set = row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        phase_key = phase_map[sub_phase]
        results[phase_key]["invested"] += 1
        results[phase_key]["won"] += win
        results[phase_key]["draws"].append({
            "date": str(curr_date.date()),
            "hits": hits,
            "win": win,
            "days_since_jackpot": days_since
        })

        # Per-draw ROI for Mann-Whitney
        draw_roi = (win - 1) / 1 * 100  # ROI per 1 EUR
        results[phase_key]["rois"].append(draw_roi)

    # Calculate aggregate ROI
    for phase in ["frueh", "spaet", "normal"]:
        inv = results[phase]["invested"]
        won = results[phase]["won"]
        if inv > 0:
            results[phase]["roi"] = (won - inv) / inv * 100
        else:
            results[phase]["roi"] = 0.0

    return results


# ============================================================================
# NEGATIVE CONTROL: Random 14d Windows
# ============================================================================

def generate_random_windows(
    keno_df: pd.DataFrame,
    n_windows: int,
    window_days: int = 14,
    exclude_jackpots: List[datetime] = None,
    seed: int = 42
) -> List[Tuple[datetime, datetime]]:
    """
    Generates random 14-day windows that do NOT start at jackpot dates.

    Used as negative control to compare with actual FRUEH windows.
    """
    random.seed(seed)

    min_date = keno_df["Datum"].min()
    max_date = keno_df["Datum"].max() - timedelta(days=window_days)

    if exclude_jackpots is None:
        exclude_jackpots = []

    # Exclude jackpot dates AND the 30 days after
    exclude_set = set()
    for jp in exclude_jackpots:
        for d in range(31):
            exclude_set.add((jp + timedelta(days=d)).date())

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
    phase_a_draws: List[Dict],
    phase_b_draws: List[Dict],
    high_win_threshold: int = 100
) -> Dict:
    """
    Chi2-Test for high-win rate difference between two phases.

    H0: High-win rate is equal in both phases.
    """
    a_n = len(phase_a_draws)
    b_n = len(phase_b_draws)

    a_high = sum(1 for d in phase_a_draws if d["win"] >= high_win_threshold)
    b_high = sum(1 for d in phase_b_draws if d["win"] >= high_win_threshold)

    # Contingency table
    observed = np.array([
        [a_high, a_n - a_high],
        [b_high, b_n - b_high]
    ])

    # Chi2 test (with continuity correction)
    try:
        if observed.sum() > 0 and (a_high + b_high) > 0:
            chi2, p_value, dof, expected = stats.chi2_contingency(observed, correction=True)
        else:
            chi2, p_value = 0.0, 1.0
    except ValueError:
        try:
            _, p_value = stats.fisher_exact(observed)
            chi2 = 0.0
        except Exception:
            chi2, p_value = 0.0, 1.0

    return {
        "phase_a_high_wins": a_high,
        "phase_a_total": a_n,
        "phase_a_rate": a_high / a_n * 100 if a_n > 0 else 0,
        "phase_b_high_wins": b_high,
        "phase_b_total": b_n,
        "phase_b_rate": b_high / b_n * 100 if b_n > 0 else 0,
        "chi2": chi2,
        "p_value": p_value,
        "significant": p_value < 0.05
    }


def mann_whitney_test(rois_a: List[float], rois_b: List[float]) -> Dict:
    """
    Mann-Whitney U test for ROI distribution difference.

    H0: ROI distributions are equal.
    """
    if len(rois_a) < 5 or len(rois_b) < 5:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "note": "Insufficient samples"
        }

    statistic, p_value = stats.mannwhitneyu(
        rois_a, rois_b, alternative="two-sided"
    )

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
        "median_a": float(np.median(rois_a)),
        "median_b": float(np.median(rois_b))
    }


# ============================================================================
# MAIN TEST FUNCTION
# ============================================================================

def run_frueh_phase_isolated_test(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_types: List[int] = [6, 7, 8, 9, 10]
) -> Dict:
    """
    Runs the isolated FRUEH-phase test with all controls.

    Returns:
    - Train/Test split results
    - Negative control comparison
    - Statistical tests for FRUEH vs SPAET vs NORMAL
    """

    # Date splits
    train_end = datetime(2023, 12, 31)
    test_start = datetime(2024, 1, 1)

    train_jackpots = [jp for jp in jackpot_dates if jp <= train_end]
    test_jackpots = [jp for jp in jackpot_dates if jp > train_end]

    results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "sub_cooldown_semantics": {
                "frueh": f"1-{FRUEH_MAX_DAYS} Tage nach 10/10 Jackpot",
                "spaet": f"{FRUEH_MAX_DAYS + 1}-{SPAET_MAX_DAYS} Tage nach Jackpot",
                "normal": f">{SPAET_MAX_DAYS} Tage nach Jackpot"
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
        train_results = backtest_sub_cooldown_isolated(
            keno_df, jackpot_dates, keno_type, ticket,
            date_filter=(train_min, train_end)
        )

        # TEST: 2024
        test_max = keno_df["Datum"].max()
        test_results = backtest_sub_cooldown_isolated(
            keno_df, jackpot_dates, keno_type, ticket,
            date_filter=(test_start, test_max)
        )

        # NEGATIVE CONTROL: Random 14d windows
        random_windows = generate_random_windows(
            keno_df, n_windows=len(jackpot_dates) * 2, window_days=14,
            exclude_jackpots=jackpot_dates, seed=42
        )
        negative_control = backtest_random_windows(
            keno_df, random_windows, keno_type, ticket
        )

        # Statistical tests: FRUEH vs SPAET
        train_chi2_frueh_vs_spaet = chi2_test_high_wins(
            train_results["frueh"]["draws"],
            train_results["spaet"]["draws"]
        )

        test_chi2_frueh_vs_spaet = chi2_test_high_wins(
            test_results["frueh"]["draws"],
            test_results["spaet"]["draws"]
        )

        train_mw_frueh_vs_spaet = mann_whitney_test(
            train_results["frueh"]["rois"],
            train_results["spaet"]["rois"]
        )

        test_mw_frueh_vs_spaet = mann_whitney_test(
            test_results["frueh"]["rois"],
            test_results["spaet"]["rois"]
        )

        # Compare FRUEH vs NORMAL
        train_mw_frueh_vs_normal = mann_whitney_test(
            train_results["frueh"]["rois"],
            train_results["normal"]["rois"]
        )

        test_mw_frueh_vs_normal = mann_whitney_test(
            test_results["frueh"]["rois"],
            test_results["normal"]["rois"]
        )

        # Compare FRUEH ROI vs negative control
        frueh_all_rois = train_results["frueh"]["rois"] + test_results["frueh"]["rois"]
        frueh_vs_control_mw = mann_whitney_test(
            frueh_all_rois,
            negative_control["all_draw_rois"]
        )

        # Build results for this type
        type_result = {
            "ticket": ticket,
            "train": {
                "frueh_draws": train_results["frueh"]["invested"],
                "frueh_roi": train_results["frueh"]["roi"],
                "spaet_draws": train_results["spaet"]["invested"],
                "spaet_roi": train_results["spaet"]["roi"],
                "normal_draws": train_results["normal"]["invested"],
                "normal_roi": train_results["normal"]["roi"],
                "delta_frueh_vs_spaet": train_results["frueh"]["roi"] - train_results["spaet"]["roi"],
                "delta_frueh_vs_normal": train_results["frueh"]["roi"] - train_results["normal"]["roi"],
                "chi2_frueh_vs_spaet": train_chi2_frueh_vs_spaet,
                "mann_whitney_frueh_vs_spaet": train_mw_frueh_vs_spaet,
                "mann_whitney_frueh_vs_normal": train_mw_frueh_vs_normal
            },
            "test": {
                "frueh_draws": test_results["frueh"]["invested"],
                "frueh_roi": test_results["frueh"]["roi"],
                "spaet_draws": test_results["spaet"]["invested"],
                "spaet_roi": test_results["spaet"]["roi"],
                "normal_draws": test_results["normal"]["invested"],
                "normal_roi": test_results["normal"]["roi"],
                "delta_frueh_vs_spaet": test_results["frueh"]["roi"] - test_results["spaet"]["roi"],
                "delta_frueh_vs_normal": test_results["frueh"]["roi"] - test_results["normal"]["roi"],
                "chi2_frueh_vs_spaet": test_chi2_frueh_vs_spaet,
                "mann_whitney_frueh_vs_spaet": test_mw_frueh_vs_spaet,
                "mann_whitney_frueh_vs_normal": test_mw_frueh_vs_normal
            },
            "negative_control": {
                "n_windows": len(random_windows),
                "total_draws": negative_control["total_invested"],
                "avg_roi": negative_control["avg_roi"],
                "frueh_vs_control": frueh_vs_control_mw
            }
        }

        results["by_type"][f"typ_{keno_type}"] = type_result
        results["negative_control"][f"typ_{keno_type}"] = {
            "window_rois": negative_control["window_rois"][:5],  # Sample only
            "avg_roi": negative_control["avg_roi"]
        }

    # Summary
    train_frueh_worse_vs_spaet = 0
    train_frueh_worse_vs_normal = 0
    test_frueh_worse_vs_spaet = 0
    test_frueh_worse_vs_normal = 0
    significant_count = 0

    for typ_key, typ_data in results["by_type"].items():
        if typ_data["train"]["delta_frueh_vs_spaet"] < 0:
            train_frueh_worse_vs_spaet += 1
        if typ_data["train"]["delta_frueh_vs_normal"] < 0:
            train_frueh_worse_vs_normal += 1
        if typ_data["test"]["delta_frueh_vs_spaet"] < 0:
            test_frueh_worse_vs_spaet += 1
        if typ_data["test"]["delta_frueh_vs_normal"] < 0:
            test_frueh_worse_vs_normal += 1
        if (typ_data["train"]["mann_whitney_frueh_vs_spaet"].get("significant", False) or
            typ_data["test"]["mann_whitney_frueh_vs_spaet"].get("significant", False)):
            significant_count += 1

    n_types = len(keno_types)

    # Hypothesis status: FRUEH should be worse than SPAET in most cases
    hypothesis_status = "NOT_CONFIRMED"
    if train_frueh_worse_vs_spaet >= 3 and test_frueh_worse_vs_spaet >= 1:
        hypothesis_status = "CONFIRMED"
    elif train_frueh_worse_vs_spaet >= 2:
        hypothesis_status = "WEAK"

    results["summary"] = {
        "total_types_tested": n_types,
        "train_frueh_worse_vs_spaet": train_frueh_worse_vs_spaet,
        "train_frueh_worse_vs_normal": train_frueh_worse_vs_normal,
        "test_frueh_worse_vs_spaet": test_frueh_worse_vs_spaet,
        "test_frueh_worse_vs_normal": test_frueh_worse_vs_normal,
        "significant_effects": significant_count,
        "hypothesis_status": hypothesis_status,
        "statistical_power_warning": (
            f"LOW - Only {len(jackpot_dates)} jackpots in total, tests may lack power"
        )
    }

    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function for isolated FRUEH-phase test."""
    print("=" * 70)
    print("FRUEH-PHASE ISOLATED TEST (SYN_002)")
    print("=" * 70)
    print()
    print("Sub-Cooldown-Semantik:")
    print(f"  - FRUEH:  1-{FRUEH_MAX_DAYS} Tage nach 10/10 Jackpot")
    print(f"  - SPAET:  {FRUEH_MAX_DAYS + 1}-{SPAET_MAX_DAYS} Tage nach Jackpot")
    print(f"  - NORMAL: >{SPAET_MAX_DAYS} Tage nach Jackpot")
    print()
    print("Hypothese: FRUEH-Phase hat schlechtere ROI als SPAET und NORMAL.")
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
    print("RUNNING ISOLATED FRUEH-PHASE TEST...")
    print("=" * 70)

    results = run_frueh_phase_isolated_test(keno_df, jackpot_dates)

    # Output results
    for typ_key, typ_data in results["by_type"].items():
        print(f"\n  {typ_key.upper()}:")
        print(f"    TRAIN (2022-2023):")
        print(f"      FRUEH:  {typ_data['train']['frueh_draws']} draws, ROI: {typ_data['train']['frueh_roi']:+.2f}%")
        print(f"      SPAET:  {typ_data['train']['spaet_draws']} draws, ROI: {typ_data['train']['spaet_roi']:+.2f}%")
        print(f"      NORMAL: {typ_data['train']['normal_draws']} draws, ROI: {typ_data['train']['normal_roi']:+.2f}%")
        print(f"      Delta (FRUEH-SPAET):  {typ_data['train']['delta_frueh_vs_spaet']:+.2f}%")
        print(f"      Delta (FRUEH-NORMAL): {typ_data['train']['delta_frueh_vs_normal']:+.2f}%")

        print(f"    TEST (2024):")
        print(f"      FRUEH:  {typ_data['test']['frueh_draws']} draws, ROI: {typ_data['test']['frueh_roi']:+.2f}%")
        print(f"      SPAET:  {typ_data['test']['spaet_draws']} draws, ROI: {typ_data['test']['spaet_roi']:+.2f}%")
        print(f"      NORMAL: {typ_data['test']['normal_draws']} draws, ROI: {typ_data['test']['normal_roi']:+.2f}%")
        print(f"      Delta (FRUEH-SPAET):  {typ_data['test']['delta_frueh_vs_spaet']:+.2f}%")
        print(f"      Delta (FRUEH-NORMAL): {typ_data['test']['delta_frueh_vs_normal']:+.2f}%")

        print(f"    NEGATIVE CONTROL:")
        print(f"      Random windows ROI: {typ_data['negative_control']['avg_roi']:+.2f}%")

    # Save results
    output_path = base_path / "results" / "frueh_phase_isolated_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    summary = results["summary"]
    print(f"\n  Types tested:              {summary['total_types_tested']}")
    print(f"  Train FRUEH worse vs SPAET:  {summary['train_frueh_worse_vs_spaet']}/{summary['total_types_tested']}")
    print(f"  Train FRUEH worse vs NORMAL: {summary['train_frueh_worse_vs_normal']}/{summary['total_types_tested']}")
    print(f"  Test FRUEH worse vs SPAET:   {summary['test_frueh_worse_vs_spaet']}/{summary['total_types_tested']}")
    print(f"  Test FRUEH worse vs NORMAL:  {summary['test_frueh_worse_vs_normal']}/{summary['total_types_tested']}")
    print(f"  Significant effects:         {summary['significant_effects']}")
    print(f"\n  Hypothesis status:           {summary['hypothesis_status']}")
    print(f"  Warning:                     {summary['statistical_power_warning']}")

    print("\n" + "=" * 70)
    print("REPRO COMMAND:")
    print("  python scripts/test_frueh_phase_isolated.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
