#!/usr/bin/env python3
"""
HZ-DELAY ISOLATED TEST (SYN_003)

Tests the Hot-Zone Delay (48-60d after 1st HZ-Jackpot) in isolation with proper statistical controls.

IMPORTANT SEMANTIC DIFFERENCE from FRUEH-Phase (SYN_002):
- FRUEH-Phase: Days since GLOBAL 10/10 Jackpot
- HZ-Delay: Days since 1st Jackpot of a SPECIFIC Hot-Zone (Top-7 numbers from 50-day window)

Axiom-First Approach:
- Axiom A7 (Reset-Zyklen): Hot-Zone cycles independently
- Hypothese: 2nd Jackpot of a Hot-Zone comes 48-120 days after 1st (optimal: 48-60d)

Delay Windows:
- EARLY: 0-47 Tage nach 1. HZ-Jackpot (zu frueh)
- OPTIMAL: 48-60 Tage nach 1. HZ-Jackpot (2. Jackpot erwartet)
- LATE: 61-120 Tage nach 1. HZ-Jackpot (noch moeglich)
- EXPIRED: >120 Tage nach 1. HZ-Jackpot (Hot-Zone abgelaufen)

Controls:
- Train/Test Split: 2022-2023 (Train) vs 2024 (Test)
- Negative Control: Random windows (ohne HZ-Jackpot-Bezug)
- Chi2-Test + Mann-Whitney U fuer statistische Signifikanz

Output: results/hz_delay_isolated_test.json

Repro: python scripts/test_hz_delay_isolated.py
"""

import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from kenobase.core.keno_quotes import KENO_FIXED_QUOTES_BY_TYPE


# ============================================================================
# HZ-DELAY PHASE CONSTANTS
# ============================================================================

HZ_EARLY_MAX_DAYS = 47      # 0-47 Tage: zu frueh fuer 2. Jackpot
HZ_OPTIMAL_MIN_DAYS = 48    # 48-60 Tage: optimales Fenster
HZ_OPTIMAL_MAX_DAYS = 60
HZ_LATE_MAX_DAYS = 120      # 61-120 Tage: noch moeglich
# >120 Tage: EXPIRED


class HZDelayPhase:
    """Hot-Zone Delay Phase after 1st Jackpot."""
    EARLY = "EARLY"       # 0-47 Tage
    OPTIMAL = "OPTIMAL"   # 48-60 Tage
    LATE = "LATE"         # 61-120 Tage
    EXPIRED = "EXPIRED"   # >120 Tage
    UNKNOWN = "UNKNOWN"   # Vor 1. Jackpot


def get_hz_delay_phase(days_since_first_jackpot: Optional[int]) -> str:
    """Determine HZ-Delay phase based on days since 1st Hot-Zone Jackpot."""
    if days_since_first_jackpot is None:
        return HZDelayPhase.UNKNOWN
    if days_since_first_jackpot < 0:
        return HZDelayPhase.UNKNOWN
    if days_since_first_jackpot <= HZ_EARLY_MAX_DAYS:
        return HZDelayPhase.EARLY
    if days_since_first_jackpot <= HZ_OPTIMAL_MAX_DAYS:
        return HZDelayPhase.OPTIMAL
    if days_since_first_jackpot <= HZ_LATE_MAX_DAYS:
        return HZDelayPhase.LATE
    return HZDelayPhase.EXPIRED


# ============================================================================
# KENO QUOTES
# ============================================================================

KENO_QUOTES = {
    int(keno_type): {int(hits): float(quote) for hits, quote in mapping.items()}
    for keno_type, mapping in KENO_FIXED_QUOTES_BY_TYPE.items()
}


# ============================================================================
# HOT-ZONE LOGIC (from find_ripe_hotzones.py)
# ============================================================================

def get_hot_zone(df: pd.DataFrame, end_date: datetime, window: int = 50) -> Tuple[int, ...]:
    """
    Get Top-7 most frequent numbers from the last `window` draws.

    This is the Hot-Zone definition from find_ripe_hotzones.py:42-59.
    """
    hist = df[df['datum'] <= end_date].tail(window)
    freq = Counter()
    for zahlen in hist['zahlen']:
        freq.update(zahlen)
    return tuple(sorted([n for n, _ in freq.most_common(7)]))


def find_hz_jackpots(
    df: pd.DataFrame,
    hz_numbers: Tuple[int, ...],
    start_date: datetime,
    end_date: datetime
) -> List[Dict]:
    """
    Find all Typ-6 Jackpots for a Hot-Zone (6/6 hits from 7 numbers).

    Based on find_ripe_hotzones.py:42-59.
    """
    numbers = sorted(hz_numbers)[:7]
    groups = list(combinations(numbers, 6))
    test_df = df[(df['datum'] >= start_date) & (df['datum'] <= end_date)]

    jackpots = []
    for _, row in test_df.iterrows():
        drawn = set(row['zahlen'])
        for group in groups:
            if len(drawn & set(group)) == 6:
                jackpots.append({
                    'datum': row['datum'],
                    'gruppe': tuple(sorted(group)),
                    'gezogen': tuple(sorted(drawn))
                })
                break  # Only one jackpot per draw
    return jackpots


# ============================================================================
# DATA LOADING
# ============================================================================

def load_data(base_path: Path) -> pd.DataFrame:
    """Load KENO data with standard columns."""

    # Try multiple data paths
    keno_paths = [
        base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv",
        base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv"
    ]

    keno_df = None
    for p in keno_paths:
        if p.exists():
            keno_df = pd.read_csv(p, sep=";", encoding="utf-8")
            keno_df["datum"] = pd.to_datetime(keno_df["Datum"], format="%d.%m.%Y", errors="coerce")
            break

    if keno_df is None:
        raise FileNotFoundError("Keine KENO-Datendatei gefunden")

    zahl_cols = [f'Keno_Z{i}' for i in range(1, 21)]
    keno_df['zahlen'] = keno_df[zahl_cols].apply(lambda row: [int(x) for x in row if pd.notna(x)], axis=1)
    keno_df['numbers_set'] = keno_df[zahl_cols].apply(lambda row: set(int(x) for x in row if pd.notna(x)), axis=1)
    keno_df = keno_df.dropna(subset=['datum']).sort_values('datum').reset_index(drop=True)

    return keno_df


# ============================================================================
# HOT-ZONE HISTORY BUILDER
# ============================================================================

def build_hz_history(df: pd.DataFrame) -> Dict:
    """
    Build Hot-Zone history with first jackpot dates.

    Returns:
        Dict mapping hot-zone tuple -> {
            'first_jackpot': datetime,
            'all_jackpots': List[datetime],
            'ermittlung_date': datetime
        }
    """
    hotzones = {}

    # Generate Hot-Zones for each month (same as find_ripe_hotzones.py)
    last_draw = df['datum'].max()
    test_dates = pd.date_range(start='2022-04-01', end=last_draw - timedelta(days=30), freq='MS')

    for ermittlung_date in test_dates:
        hz = get_hot_zone(df, ermittlung_date, 50)

        if hz not in hotzones:
            hotzones[hz] = {
                'ermittlung_date': ermittlung_date,
                'zahlen': hz,
                'jackpots': []
            }

    # Find jackpots for each Hot-Zone
    for hz, data in hotzones.items():
        jackpots = find_hz_jackpots(
            df, hz,
            data['ermittlung_date'],
            last_draw
        )

        if jackpots:
            data['jackpots'] = jackpots
            data['first_jackpot'] = min(jp['datum'] for jp in jackpots)
            data['jackpot_count'] = len(jackpots)
        else:
            data['first_jackpot'] = None
            data['jackpot_count'] = 0

    return hotzones


# ============================================================================
# HZ-DELAY PHASE TAGGING
# ============================================================================

def get_hz_delay_for_date(
    target_date: datetime,
    hotzones: Dict
) -> Tuple[str, Optional[int], Optional[Tuple[int, ...]]]:
    """
    Determine HZ-Delay phase for a specific date.

    Looks at ALL Hot-Zones that have exactly 1 jackpot before target_date,
    and returns the phase based on the most recent 1st jackpot.

    Returns:
        (phase, days_since_first_jackpot, hot_zone_numbers)
    """
    best_hz = None
    best_days = None

    for hz, data in hotzones.items():
        if data['first_jackpot'] is None:
            continue

        # Only consider Hot-Zones with exactly 1 jackpot BEFORE target_date
        past_jackpots = [jp for jp in data['jackpots'] if jp['datum'] < target_date]

        if len(past_jackpots) == 1:
            first_jp = data['first_jackpot']
            if first_jp < target_date:
                days = (target_date - first_jp).days

                # Prefer the most recent 1st jackpot (smallest days)
                if best_days is None or days < best_days:
                    best_days = days
                    best_hz = hz

    if best_hz is None:
        return HZDelayPhase.UNKNOWN, None, None

    phase = get_hz_delay_phase(best_days)
    return phase, best_days, best_hz


# ============================================================================
# TICKET SIMULATION
# ============================================================================

def simulate_ticket(ticket: List[int], keno_type: int, draw_set: set) -> Tuple[int, int]:
    """Simulate a ticket against a draw."""
    hits = sum(1 for n in ticket if n in draw_set)
    win = KENO_QUOTES.get(keno_type, {}).get(hits, 0)
    return win, hits


# ============================================================================
# BACKTEST FUNCTION
# ============================================================================

def backtest_hz_delay_isolated(
    keno_df: pd.DataFrame,
    hotzones: Dict,
    keno_type: int,
    ticket: List[int],
    date_filter: Tuple[datetime, datetime] = None
) -> Dict:
    """
    Runs isolated HZ-Delay backtest.

    Returns separate ROI for EARLY (0-47d) vs OPTIMAL (48-60d) vs LATE (61-120d) vs EXPIRED (>120d).
    """
    results = {
        "early": {"invested": 0, "won": 0, "draws": [], "rois": []},
        "optimal": {"invested": 0, "won": 0, "draws": [], "rois": []},
        "late": {"invested": 0, "won": 0, "draws": [], "rois": []},
        "expired": {"invested": 0, "won": 0, "draws": [], "rois": []},
    }

    phase_map = {
        HZDelayPhase.EARLY: "early",
        HZDelayPhase.OPTIMAL: "optimal",
        HZDelayPhase.LATE: "late",
        HZDelayPhase.EXPIRED: "expired",
    }

    for i in range(1, len(keno_df)):
        row = keno_df.iloc[i]
        curr_date = row["datum"]

        # Apply date filter if specified
        if date_filter:
            start_date, end_date = date_filter
            if curr_date < start_date or curr_date > end_date:
                continue

        hz_phase, days_since, hz_numbers = get_hz_delay_for_date(curr_date, hotzones)

        # Skip UNKNOWN
        if hz_phase == HZDelayPhase.UNKNOWN:
            continue

        # Simulate ticket
        draw_set = row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        phase_key = phase_map[hz_phase]
        results[phase_key]["invested"] += 1
        results[phase_key]["won"] += win
        results[phase_key]["draws"].append({
            "date": str(curr_date.date()),
            "hits": hits,
            "win": win,
            "days_since_hz_jackpot": days_since,
            "hot_zone": list(hz_numbers) if hz_numbers else None
        })

        # Per-draw ROI for Mann-Whitney
        draw_roi = (win - 1) / 1 * 100  # ROI per 1 EUR
        results[phase_key]["rois"].append(draw_roi)

    # Calculate aggregate ROI
    for phase in ["early", "optimal", "late", "expired"]:
        inv = results[phase]["invested"]
        won = results[phase]["won"]
        if inv > 0:
            results[phase]["roi"] = (won - inv) / inv * 100
        else:
            results[phase]["roi"] = 0.0

    return results


# ============================================================================
# NEGATIVE CONTROL: Random Windows
# ============================================================================

def generate_random_windows(
    keno_df: pd.DataFrame,
    hotzones: Dict,
    n_windows: int,
    window_days: int = 13,  # 48-60d = 13 days
    seed: int = 42
) -> List[Tuple[datetime, datetime]]:
    """
    Generate random 13-day windows that do NOT overlap with HZ-Jackpot windows.

    Used as negative control to compare with actual OPTIMAL windows.
    """
    random.seed(seed)

    min_date = keno_df["datum"].min()
    max_date = keno_df["datum"].max() - timedelta(days=window_days)

    # Exclude dates near HZ jackpots (48-120 days after each)
    exclude_set = set()
    for hz, data in hotzones.items():
        if data['first_jackpot']:
            first_jp = data['first_jackpot']
            for d in range(48, 121):  # Exclude the OPTIMAL and LATE windows
                exclude_set.add((first_jp + timedelta(days=d)).date())

    all_dates = keno_df[keno_df["datum"] <= max_date]["datum"].tolist()
    eligible_dates = [d for d in all_dates if d.date() not in exclude_set]

    if len(eligible_dates) < n_windows:
        n_windows = len(eligible_dates)

    selected_dates = random.sample(eligible_dates, n_windows)

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
            curr_date = row["datum"]

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

def chi2_test_jackpot_rate(
    phase_a_draws: List[Dict],
    phase_b_draws: List[Dict],
    jackpot_threshold: int = 500  # Typ-6 6/6 = 500 EUR
) -> Dict:
    """
    Chi2-Test for jackpot rate difference between two phases.

    H0: Jackpot rate is equal in both phases.
    """
    a_n = len(phase_a_draws)
    b_n = len(phase_b_draws)

    a_jackpots = sum(1 for d in phase_a_draws if d["win"] >= jackpot_threshold)
    b_jackpots = sum(1 for d in phase_b_draws if d["win"] >= jackpot_threshold)

    # Contingency table
    observed = np.array([
        [a_jackpots, a_n - a_jackpots],
        [b_jackpots, b_n - b_jackpots]
    ])

    # Chi2 test
    try:
        if observed.sum() > 0 and (a_jackpots + b_jackpots) > 0:
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
        "phase_a_jackpots": a_jackpots,
        "phase_a_total": a_n,
        "phase_a_rate": a_jackpots / a_n * 100 if a_n > 0 else 0,
        "phase_b_jackpots": b_jackpots,
        "phase_b_total": b_n,
        "phase_b_rate": b_jackpots / b_n * 100 if b_n > 0 else 0,
        "chi2": chi2,
        "p_value": p_value,
        "significant": p_value < 0.05
    }


def mann_whitney_test(rois_a: List[float], rois_b: List[float]) -> Dict:
    """
    Mann-Whitney U test for ROI distribution difference.
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
# REFERENCE TICKETS
# ============================================================================

REFERENCE_TICKETS = {
    6: [3, 9, 10, 32, 49, 64],
    7: [3, 24, 30, 49, 51, 59, 64],
    8: [3, 20, 24, 27, 36, 49, 51, 64],
    9: [3, 9, 10, 20, 24, 36, 49, 51, 64],
    10: [2, 3, 9, 10, 20, 24, 36, 49, 51, 64],
}


# ============================================================================
# MAIN TEST FUNCTION
# ============================================================================

def run_hz_delay_isolated_test(
    keno_df: pd.DataFrame,
    hotzones: Dict,
    keno_types: List[int] = [6, 7, 8, 9, 10]
) -> Dict:
    """
    Runs the isolated HZ-Delay test with all controls.

    Returns:
    - Train/Test split results
    - Negative control comparison
    - Statistical tests for OPTIMAL vs EARLY vs LATE vs EXPIRED
    """

    # Date splits
    train_end = datetime(2023, 12, 31)
    test_start = datetime(2024, 1, 1)

    # Count HZ with exactly 1 jackpot per period
    train_hz_count = sum(
        1 for hz, d in hotzones.items()
        if d['first_jackpot'] and d['first_jackpot'] <= train_end and d['jackpot_count'] == 1
    )
    test_hz_count = sum(
        1 for hz, d in hotzones.items()
        if d['first_jackpot'] and d['first_jackpot'] > train_end and d['jackpot_count'] == 1
    )

    results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "hz_delay_semantics": {
                "early": f"0-{HZ_EARLY_MAX_DAYS} Tage nach 1. HZ-Jackpot",
                "optimal": f"{HZ_OPTIMAL_MIN_DAYS}-{HZ_OPTIMAL_MAX_DAYS} Tage nach 1. HZ-Jackpot",
                "late": f"{HZ_OPTIMAL_MAX_DAYS+1}-{HZ_LATE_MAX_DAYS} Tage nach 1. HZ-Jackpot",
                "expired": f">{HZ_LATE_MAX_DAYS} Tage nach 1. HZ-Jackpot"
            },
            "train_period": "2022-2023",
            "test_period": "2024",
            "total_hotzones": len(hotzones),
            "train_hz_with_1_jackpot": train_hz_count,
            "test_hz_with_1_jackpot": test_hz_count
        },
        "by_type": {},
        "negative_control": {},
        "summary": {}
    }

    for keno_type in keno_types:
        ticket = REFERENCE_TICKETS[keno_type]

        # TRAIN: 2022-2023
        train_min = keno_df["datum"].min()
        train_results = backtest_hz_delay_isolated(
            keno_df, hotzones, keno_type, ticket,
            date_filter=(train_min, train_end)
        )

        # TEST: 2024
        test_max = keno_df["datum"].max()
        test_results = backtest_hz_delay_isolated(
            keno_df, hotzones, keno_type, ticket,
            date_filter=(test_start, test_max)
        )

        # NEGATIVE CONTROL: Random 13d windows
        n_hz_with_1jp = sum(1 for d in hotzones.values() if d['jackpot_count'] == 1)
        random_windows = generate_random_windows(
            keno_df, hotzones, n_windows=n_hz_with_1jp * 2, window_days=13, seed=42
        )
        negative_control = backtest_random_windows(
            keno_df, random_windows, keno_type, ticket
        )

        # Statistical tests: OPTIMAL vs EARLY
        train_chi2_optimal_vs_early = chi2_test_jackpot_rate(
            train_results["optimal"]["draws"],
            train_results["early"]["draws"]
        )

        test_chi2_optimal_vs_early = chi2_test_jackpot_rate(
            test_results["optimal"]["draws"],
            test_results["early"]["draws"]
        )

        train_mw_optimal_vs_early = mann_whitney_test(
            train_results["optimal"]["rois"],
            train_results["early"]["rois"]
        )

        test_mw_optimal_vs_early = mann_whitney_test(
            test_results["optimal"]["rois"],
            test_results["early"]["rois"]
        )

        # Compare OPTIMAL vs LATE
        train_mw_optimal_vs_late = mann_whitney_test(
            train_results["optimal"]["rois"],
            train_results["late"]["rois"]
        )

        test_mw_optimal_vs_late = mann_whitney_test(
            test_results["optimal"]["rois"],
            test_results["late"]["rois"]
        )

        # Compare OPTIMAL vs negative control
        optimal_all_rois = train_results["optimal"]["rois"] + test_results["optimal"]["rois"]
        optimal_vs_control_mw = mann_whitney_test(
            optimal_all_rois,
            negative_control["all_draw_rois"]
        )

        # Build results for this type
        type_result = {
            "ticket": ticket,
            "train": {
                "early_draws": train_results["early"]["invested"],
                "early_roi": train_results["early"]["roi"],
                "optimal_draws": train_results["optimal"]["invested"],
                "optimal_roi": train_results["optimal"]["roi"],
                "late_draws": train_results["late"]["invested"],
                "late_roi": train_results["late"]["roi"],
                "expired_draws": train_results["expired"]["invested"],
                "expired_roi": train_results["expired"]["roi"],
                "delta_optimal_vs_early": train_results["optimal"]["roi"] - train_results["early"]["roi"],
                "delta_optimal_vs_late": train_results["optimal"]["roi"] - train_results["late"]["roi"],
                "chi2_optimal_vs_early": train_chi2_optimal_vs_early,
                "mann_whitney_optimal_vs_early": train_mw_optimal_vs_early,
                "mann_whitney_optimal_vs_late": train_mw_optimal_vs_late
            },
            "test": {
                "early_draws": test_results["early"]["invested"],
                "early_roi": test_results["early"]["roi"],
                "optimal_draws": test_results["optimal"]["invested"],
                "optimal_roi": test_results["optimal"]["roi"],
                "late_draws": test_results["late"]["invested"],
                "late_roi": test_results["late"]["roi"],
                "expired_draws": test_results["expired"]["invested"],
                "expired_roi": test_results["expired"]["roi"],
                "delta_optimal_vs_early": test_results["optimal"]["roi"] - test_results["early"]["roi"],
                "delta_optimal_vs_late": test_results["optimal"]["roi"] - test_results["late"]["roi"],
                "chi2_optimal_vs_early": test_chi2_optimal_vs_early,
                "mann_whitney_optimal_vs_early": test_mw_optimal_vs_early,
                "mann_whitney_optimal_vs_late": test_mw_optimal_vs_late
            },
            "negative_control": {
                "n_windows": len(random_windows),
                "total_draws": negative_control["total_invested"],
                "avg_roi": negative_control["avg_roi"],
                "optimal_vs_control": optimal_vs_control_mw
            }
        }

        results["by_type"][f"typ_{keno_type}"] = type_result
        results["negative_control"][f"typ_{keno_type}"] = {
            "window_rois": negative_control["window_rois"][:5],
            "avg_roi": negative_control["avg_roi"]
        }

    # Summary
    train_optimal_better_vs_early = 0
    train_optimal_better_vs_late = 0
    test_optimal_better_vs_early = 0
    test_optimal_better_vs_late = 0
    significant_count = 0

    for typ_key, typ_data in results["by_type"].items():
        if typ_data["train"]["delta_optimal_vs_early"] > 0:
            train_optimal_better_vs_early += 1
        if typ_data["train"]["delta_optimal_vs_late"] > 0:
            train_optimal_better_vs_late += 1
        if typ_data["test"]["delta_optimal_vs_early"] > 0:
            test_optimal_better_vs_early += 1
        if typ_data["test"]["delta_optimal_vs_late"] > 0:
            test_optimal_better_vs_late += 1
        if (typ_data["train"]["mann_whitney_optimal_vs_early"].get("significant", False) or
            typ_data["test"]["mann_whitney_optimal_vs_early"].get("significant", False)):
            significant_count += 1

    n_types = len(keno_types)

    # Hypothesis status: OPTIMAL should be better than EARLY in most cases
    hypothesis_status = "NOT_CONFIRMED"
    if train_optimal_better_vs_early >= 3 and test_optimal_better_vs_early >= 1:
        hypothesis_status = "CONFIRMED"
    elif train_optimal_better_vs_early >= 2:
        hypothesis_status = "WEAK"

    results["summary"] = {
        "total_types_tested": n_types,
        "train_optimal_better_vs_early": train_optimal_better_vs_early,
        "train_optimal_better_vs_late": train_optimal_better_vs_late,
        "test_optimal_better_vs_early": test_optimal_better_vs_early,
        "test_optimal_better_vs_late": test_optimal_better_vs_late,
        "significant_effects": significant_count,
        "hypothesis_status": hypothesis_status,
        "statistical_power_warning": (
            f"LOW - Only {len([d for d in hotzones.values() if d['jackpot_count'] == 1])} "
            "Hot-Zones with exactly 1 jackpot, tests may lack power"
        )
    }

    return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function for isolated HZ-Delay test."""
    print("=" * 70)
    print("HZ-DELAY ISOLATED TEST (SYN_003)")
    print("=" * 70)
    print()
    print("HZ-Delay-Semantik (nach 1. Hot-Zone-Jackpot, NICHT globalem 10/10):")
    print(f"  - EARLY:   0-{HZ_EARLY_MAX_DAYS} Tage (zu frueh)")
    print(f"  - OPTIMAL: {HZ_OPTIMAL_MIN_DAYS}-{HZ_OPTIMAL_MAX_DAYS} Tage (2. Jackpot erwartet)")
    print(f"  - LATE:    {HZ_OPTIMAL_MAX_DAYS+1}-{HZ_LATE_MAX_DAYS} Tage (noch moeglich)")
    print(f"  - EXPIRED: >{HZ_LATE_MAX_DAYS} Tage (abgelaufen)")
    print()
    print("Hypothese: OPTIMAL-Phase hat bessere ROI als EARLY und LATE.")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")

    # Filter for test period (2022+)
    keno_df = keno_df[keno_df["datum"] >= datetime(2022, 1, 1)]
    keno_df = keno_df.reset_index(drop=True)
    print(f"  Gefiltert (2022+): {len(keno_df)} Ziehungen")

    print("\nBaue Hot-Zone-Historie...")
    hotzones = build_hz_history(keno_df)
    print(f"  Unique Hot-Zones: {len(hotzones)}")

    hz_with_1_jackpot = sum(1 for d in hotzones.values() if d['jackpot_count'] == 1)
    hz_with_2plus_jackpots = sum(1 for d in hotzones.values() if d['jackpot_count'] >= 2)
    print(f"  Hot-Zones mit 1 Jackpot: {hz_with_1_jackpot}")
    print(f"  Hot-Zones mit 2+ Jackpots: {hz_with_2plus_jackpots}")

    # Run test
    print("\n" + "=" * 70)
    print("RUNNING ISOLATED HZ-DELAY TEST...")
    print("=" * 70)

    results = run_hz_delay_isolated_test(keno_df, hotzones)

    # Output results
    for typ_key, typ_data in results["by_type"].items():
        print(f"\n  {typ_key.upper()}:")
        print(f"    TRAIN (2022-2023):")
        print(f"      EARLY:   {typ_data['train']['early_draws']} draws, ROI: {typ_data['train']['early_roi']:+.2f}%")
        print(f"      OPTIMAL: {typ_data['train']['optimal_draws']} draws, ROI: {typ_data['train']['optimal_roi']:+.2f}%")
        print(f"      LATE:    {typ_data['train']['late_draws']} draws, ROI: {typ_data['train']['late_roi']:+.2f}%")
        print(f"      EXPIRED: {typ_data['train']['expired_draws']} draws, ROI: {typ_data['train']['expired_roi']:+.2f}%")
        print(f"      Delta (OPTIMAL-EARLY): {typ_data['train']['delta_optimal_vs_early']:+.2f}%")
        print(f"      Delta (OPTIMAL-LATE):  {typ_data['train']['delta_optimal_vs_late']:+.2f}%")

        print(f"    TEST (2024):")
        print(f"      EARLY:   {typ_data['test']['early_draws']} draws, ROI: {typ_data['test']['early_roi']:+.2f}%")
        print(f"      OPTIMAL: {typ_data['test']['optimal_draws']} draws, ROI: {typ_data['test']['optimal_roi']:+.2f}%")
        print(f"      LATE:    {typ_data['test']['late_draws']} draws, ROI: {typ_data['test']['late_roi']:+.2f}%")
        print(f"      EXPIRED: {typ_data['test']['expired_draws']} draws, ROI: {typ_data['test']['expired_roi']:+.2f}%")
        print(f"      Delta (OPTIMAL-EARLY): {typ_data['test']['delta_optimal_vs_early']:+.2f}%")
        print(f"      Delta (OPTIMAL-LATE):  {typ_data['test']['delta_optimal_vs_late']:+.2f}%")

        print(f"    NEGATIVE CONTROL:")
        print(f"      Random windows ROI: {typ_data['negative_control']['avg_roi']:+.2f}%")

    # Save results
    output_path = base_path / "results" / "hz_delay_isolated_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    summary = results["summary"]
    print(f"\n  Types tested:                  {summary['total_types_tested']}")
    print(f"  Train OPTIMAL better vs EARLY: {summary['train_optimal_better_vs_early']}/{summary['total_types_tested']}")
    print(f"  Train OPTIMAL better vs LATE:  {summary['train_optimal_better_vs_late']}/{summary['total_types_tested']}")
    print(f"  Test OPTIMAL better vs EARLY:  {summary['test_optimal_better_vs_early']}/{summary['total_types_tested']}")
    print(f"  Test OPTIMAL better vs LATE:   {summary['test_optimal_better_vs_late']}/{summary['total_types_tested']}")
    print(f"  Significant effects:           {summary['significant_effects']}")
    print(f"\n  Hypothesis status:             {summary['hypothesis_status']}")
    print(f"  Warning:                       {summary['statistical_power_warning']}")

    print("\n" + "=" * 70)
    print("REPRO COMMAND:")
    print("  python scripts/test_hz_delay_isolated.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
