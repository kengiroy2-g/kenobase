#!/usr/bin/env python3
"""
Dienstag x Cooldown Interaction Analysis (TASK_041b)

Tests 2x2 factorial design: (Dienstag vs andere Tage) x (cooldown vs normal).

Hypothesis: If both effects exist, do they interact?
- Di + normal = best cell?
- Di + cooldown = mitigated by WL-003?

Semantics:
- cooldown: 0-30 days post-jackpot (WL-003: System spart)
- normal: >30 days post-jackpot
- Dienstag: weekday == 1 (0=Mo in Python)

Output: results/dienstag_cooldown_interaction.json

Repro: python scripts/validate_dienstag_cooldown.py
"""

import json
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from kenobase.core.keno_quotes import get_fixed_quote


# V2 Birthday-Avoidance Ticket Type 9 (standard recommendation)
TICKET_V2_TYPE9 = [3, 7, 36, 43, 48, 51, 58, 61, 64]


def load_keno_data(base_path: Path) -> pd.DataFrame:
    """Load KENO data from CSV."""
    # Try multiple paths (consistent with super_model_synthesis.py)
    keno_paths = [
        base_path / "Keno_GPTs" / "Kenogpts_2" / "Basis_Tab" / "KENO_ab_2018.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2018.csv",
        base_path / "data" / "raw" / "keno" / "KENO_ab_2022_bereinigt.csv",
    ]

    df = None
    for p in keno_paths:
        if p.exists():
            df = pd.read_csv(p, sep=";", encoding="utf-8")
            df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
            break

    if df is None:
        raise FileNotFoundError("No KENO data file found")

    pos_cols = [f"Keno_Z{i}" for i in range(1, 21)]
    df["numbers_set"] = df[pos_cols].apply(
        lambda row: set(row.dropna().astype(int)), axis=1
    )
    df["weekday"] = df["Datum"].dt.dayofweek

    return df.dropna(subset=["Datum"]).sort_values("Datum").reset_index(drop=True)


def load_jackpot_dates(base_path: Path) -> List[datetime]:
    """Load jackpot dates from separate file (Typ-10 10/10 events)."""
    gk1_path = base_path / "Keno_GPTs" / "10-9_KGDaten_gefiltert.csv"

    jackpot_dates = []
    if gk1_path.exists():
        gk1_df = pd.read_csv(gk1_path, encoding="utf-8")
        gk1_df["Datum"] = pd.to_datetime(gk1_df["Datum"], format="%d.%m.%Y")
        jackpot_dates = sorted(gk1_df[gk1_df["Keno-Typ"] == 10]["Datum"].tolist())

    return [d.to_pydatetime() for d in jackpot_dates]


def is_in_cooldown(
    date: datetime,
    jackpot_dates: List[datetime],
    cooldown_days: int = 30
) -> Tuple[bool, int]:
    """
    Determine if a date is in 30-day cooldown window.

    Returns:
        Tuple (is_cooldown, days_since_jackpot)
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


def simulate_ticket(ticket: list[int], keno_type: int, draw_set: set) -> float:
    """Simulate payout for a ticket against a draw."""
    hits = sum(1 for n in ticket if n in draw_set)
    return get_fixed_quote(keno_type, hits)


def compute_2x2_roi(
    df: pd.DataFrame,
    jackpot_dates: List[datetime],
    ticket: List[int],
    keno_type: int
) -> Dict[str, Dict[str, Any]]:
    """
    Compute ROI for 2x2 factorial design: (Di vs other) x (cooldown vs normal).

    Returns dict with 4 cells:
    - di_cooldown: Dienstag + cooldown phase
    - di_normal: Dienstag + normal phase
    - other_cooldown: Other weekdays + cooldown phase
    - other_normal: Other weekdays + normal phase
    """
    cells = {
        "di_cooldown": {"n": 0, "invested": 0, "winnings": 0.0},
        "di_normal": {"n": 0, "invested": 0, "winnings": 0.0},
        "other_cooldown": {"n": 0, "invested": 0, "winnings": 0.0},
        "other_normal": {"n": 0, "invested": 0, "winnings": 0.0},
    }

    for _, row in df.iterrows():
        date = row["Datum"]
        weekday = row["weekday"]
        draw_set = row["numbers_set"]

        is_cd, _ = is_in_cooldown(date.to_pydatetime(), jackpot_dates)
        is_di = weekday == 1  # 0=Mo, 1=Di

        # Determine cell
        if is_di and is_cd:
            cell_key = "di_cooldown"
        elif is_di and not is_cd:
            cell_key = "di_normal"
        elif not is_di and is_cd:
            cell_key = "other_cooldown"
        else:
            cell_key = "other_normal"

        # Simulate
        win = simulate_ticket(ticket, keno_type, draw_set)

        cells[cell_key]["n"] += 1
        cells[cell_key]["invested"] += 1
        cells[cell_key]["winnings"] += win

    # Calculate ROI per cell
    for key, data in cells.items():
        if data["invested"] > 0:
            data["roi_pct"] = round(
                ((data["winnings"] - data["invested"]) / data["invested"]) * 100,
                2
            )
            data["winnings"] = round(data["winnings"], 2)
        else:
            data["roi_pct"] = None

    return cells


def compute_interaction_effect(cells: Dict) -> Dict[str, Any]:
    """
    Compute interaction effect for 2x2 design.

    Interaction = (Di_cooldown - Di_normal) - (Other_cooldown - Other_normal)

    Interpretation:
    - If interaction > 0: Di benefits more in cooldown (or other benefits more in normal)
    - If interaction < 0: Di benefits more in normal (or other benefits more in cooldown)
    - If interaction ~ 0: No interaction (effects are additive)
    """
    roi_di_cd = cells["di_cooldown"]["roi_pct"]
    roi_di_nm = cells["di_normal"]["roi_pct"]
    roi_ot_cd = cells["other_cooldown"]["roi_pct"]
    roi_ot_nm = cells["other_normal"]["roi_pct"]

    if None in [roi_di_cd, roi_di_nm, roi_ot_cd, roi_ot_nm]:
        return {
            "interaction_effect": None,
            "interpretation": "Insufficient data in one or more cells"
        }

    # Main effects
    di_effect = (roi_di_cd + roi_di_nm) / 2 - (roi_ot_cd + roi_ot_nm) / 2
    cooldown_effect = (roi_di_cd + roi_ot_cd) / 2 - (roi_di_nm + roi_ot_nm) / 2

    # Interaction effect
    interaction = (roi_di_cd - roi_di_nm) - (roi_ot_cd - roi_ot_nm)

    # Best/worst cell
    all_cells = {
        "di_cooldown": roi_di_cd,
        "di_normal": roi_di_nm,
        "other_cooldown": roi_ot_cd,
        "other_normal": roi_ot_nm,
    }
    best_cell = max(all_cells.keys(), key=lambda k: all_cells[k])
    worst_cell = min(all_cells.keys(), key=lambda k: all_cells[k])

    return {
        "main_effect_dienstag": round(di_effect, 2),
        "main_effect_cooldown": round(cooldown_effect, 2),
        "interaction_effect": round(interaction, 2),
        "best_cell": best_cell,
        "best_roi": all_cells[best_cell],
        "worst_cell": worst_cell,
        "worst_roi": all_cells[worst_cell],
        "roi_spread_pct": round(all_cells[best_cell] - all_cells[worst_cell], 2),
    }


def permutation_test_interaction(
    df: pd.DataFrame,
    jackpot_dates: List[datetime],
    ticket: List[int],
    keno_type: int,
    n_permutations: int = 1000,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Permutation test for interaction effect significance.

    Null hypothesis: weekday assignment is independent of ROI conditional on cooldown.

    Procedure:
    1. Compute observed interaction effect
    2. Shuffle weekday labels (preserving cooldown structure)
    3. Recompute interaction effect for shuffled data
    4. P-value = proportion of shuffled interactions >= observed
    """
    random.seed(seed)
    np.random.seed(seed)

    # Observed
    observed_cells = compute_2x2_roi(df, jackpot_dates, ticket, keno_type)
    observed_effects = compute_interaction_effect(observed_cells)
    observed_interaction = observed_effects.get("interaction_effect")

    if observed_interaction is None:
        return {
            "p_value": 1.0,
            "observed_interaction": None,
            "null_mean": None,
            "null_std": None,
            "n_permutations": n_permutations,
        }

    # Permutation test
    null_interactions = []

    for _ in range(n_permutations):
        # Shuffle weekday assignments
        shuffled_df = df.copy()
        shuffled_weekdays = shuffled_df["weekday"].tolist()
        random.shuffle(shuffled_weekdays)
        shuffled_df["weekday"] = shuffled_weekdays

        # Recompute
        shuffled_cells = compute_2x2_roi(shuffled_df, jackpot_dates, ticket, keno_type)
        shuffled_effects = compute_interaction_effect(shuffled_cells)
        shuffled_int = shuffled_effects.get("interaction_effect")

        if shuffled_int is not None:
            null_interactions.append(shuffled_int)

    if not null_interactions:
        return {
            "p_value": 1.0,
            "observed_interaction": observed_interaction,
            "null_mean": None,
            "null_std": None,
            "n_permutations": n_permutations,
        }

    # Two-tailed p-value
    p_value = sum(
        1 for ni in null_interactions if abs(ni) >= abs(observed_interaction)
    ) / len(null_interactions)

    return {
        "p_value": round(p_value, 4),
        "observed_interaction": observed_interaction,
        "null_mean": round(np.mean(null_interactions), 2),
        "null_std": round(np.std(null_interactions), 2),
        "n_permutations": n_permutations,
    }


def main():
    print("=" * 70)
    print("DIENSTAG x COOLDOWN INTERACTION ANALYSIS (TASK_041b)")
    print("=" * 70)
    print()
    print("Semantics:")
    print("  - Dienstag: weekday == 1 (Tuesday)")
    print("  - Cooldown: 0-30 days post-jackpot (WL-003)")
    print("  - Normal: >30 days post-jackpot")
    print()

    base_path = Path(__file__).parent.parent

    # Load data
    print("Loading data...")
    df = load_keno_data(base_path)
    jackpot_dates = load_jackpot_dates(base_path)

    n_draws = len(df)
    n_jackpots = len(jackpot_dates)

    print(f"  KENO draws: {n_draws}")
    print(f"  Jackpots: {n_jackpots}")
    print(f"  Date range: {df['Datum'].min().date()} to {df['Datum'].max().date()}")

    # 2x2 Analysis
    print("\n" + "=" * 70)
    print("2x2 FACTORIAL ANALYSIS")
    print("=" * 70)

    cells = compute_2x2_roi(df, jackpot_dates, TICKET_V2_TYPE9, keno_type=9)

    print("\n  CELL COUNTS AND ROI:")
    print("-" * 50)
    print(f"{'Cell':<20} {'N':>8} {'Invested':>10} {'Winnings':>10} {'ROI':>10}")
    print("-" * 50)

    for cell_name, cell_data in cells.items():
        roi_str = f"{cell_data['roi_pct']:+.1f}%" if cell_data['roi_pct'] is not None else "N/A"
        print(
            f"{cell_name:<20} {cell_data['n']:>8} "
            f"{cell_data['invested']:>10} {cell_data['winnings']:>10.2f} "
            f"{roi_str:>10}"
        )

    # Interaction effect
    effects = compute_interaction_effect(cells)

    print("\n  EFFECTS:")
    print("-" * 50)
    print(f"  Main effect (Dienstag):  {effects['main_effect_dienstag']:+.2f}%")
    print(f"  Main effect (Cooldown):  {effects['main_effect_cooldown']:+.2f}%")
    print(f"  Interaction effect:      {effects['interaction_effect']:+.2f}%")
    print()
    print(f"  Best cell:  {effects['best_cell']} ({effects['best_roi']:+.1f}%)")
    print(f"  Worst cell: {effects['worst_cell']} ({effects['worst_roi']:+.1f}%)")
    print(f"  ROI spread: {effects['roi_spread_pct']:.1f}%")

    # Permutation test
    print("\n" + "=" * 70)
    print("PERMUTATION TEST (1000 iterations)")
    print("=" * 70)

    perm_result = permutation_test_interaction(
        df, jackpot_dates, TICKET_V2_TYPE9, keno_type=9
    )

    print(f"\n  Observed interaction: {perm_result['observed_interaction']:+.2f}%")
    print(f"  Null mean: {perm_result['null_mean']:+.2f}%")
    print(f"  Null std: {perm_result['null_std']:.2f}%")
    print(f"  P-value (two-tailed): {perm_result['p_value']:.4f}")

    is_significant = perm_result["p_value"] < 0.05

    print(f"\n  Interaction significant (p < 0.05): {'YES' if is_significant else 'NO'}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if effects["interaction_effect"] is not None:
        if abs(effects["interaction_effect"]) < 10:
            interpretation = "KEINE relevante Interaktion: Effekte sind nahezu additiv"
        elif effects["interaction_effect"] > 0:
            interpretation = "POSITIVE Interaktion: Dienstag-Effekt ist in Cooldown-Phase STAERKER"
        else:
            interpretation = "NEGATIVE Interaktion: Dienstag-Effekt ist in Normal-Phase STAERKER"
    else:
        interpretation = "Interaktion nicht berechenbar (fehlende Daten)"

    print(f"\n  {interpretation}")

    # Sample size warning
    di_cooldown_n = cells["di_cooldown"]["n"]
    if di_cooldown_n < 50:
        print(f"\n  WARNUNG: Di+Cooldown hat nur N={di_cooldown_n} Ziehungen (geringe Power)")

    # Build result
    result = {
        "task": "TASK_041b",
        "analysis": "Dienstag x Cooldown Interaction",
        "data": {
            "n_draws": n_draws,
            "n_jackpots": n_jackpots,
            "date_range": {
                "start": str(df["Datum"].min().date()),
                "end": str(df["Datum"].max().date()),
            },
            "ticket": TICKET_V2_TYPE9,
            "keno_type": 9,
        },
        "semantics": {
            "dienstag": "weekday == 1 (0=Mo, 1=Di, ...)",
            "cooldown": "0-30 days post-jackpot (WL-003)",
            "normal": ">30 days post-jackpot",
        },
        "cells_2x2": cells,
        "effects": effects,
        "permutation_test": perm_result,
        "acceptance": {
            "interaction_significant": is_significant,
            "p_value_threshold": 0.05,
            "sample_size_di_cooldown": di_cooldown_n,
            "sample_size_warning": di_cooldown_n < 50,
        },
        "verdict": {
            "interaction_present": is_significant,
            "interpretation": interpretation,
            "best_strategy": f"Play {effects['best_cell'].replace('_', ' ')} for best ROI" if effects['best_roi'] is not None else "Insufficient data",
        },
        "timestamp": datetime.now().isoformat(),
    }

    # Save
    output_path = base_path / "results" / "dienstag_cooldown_interaction.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {output_path}")
    print("=" * 70)
    print("REPRO COMMAND:")
    print("  python scripts/validate_dienstag_cooldown.py")
    print("=" * 70)

    return result


if __name__ == "__main__":
    main()
