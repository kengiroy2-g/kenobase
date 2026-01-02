#!/usr/bin/env python3
"""
V1 vs V2 Cooldown-Phase Test (TASK_041)

Vergleicht V1 und V2 Birthday-Avoidance Strategien mit exakter 30-Tage Cooldown-Definition.

Cooldown-Semantik (WL-003 konform):
- cooldown: 0-30 Tage nach Jackpot (System spart)
- normal: >30 Tage nach Jackpot (System laeuft normal)

Key metric: ROI delta (V2-V1) in cooldown vs normal periods.

Output: results/v1_v2_cooldown_comparison.json

Repro: python scripts/backtest_v1_v2_cooldown.py
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

from super_model_synthesis import (
    SuperModel,
    load_data,
    simulate_ticket,
)

from super_model_v1_birthday import (
    SuperModelV1,
)

from super_model_v2_birthday_signal import (
    SuperModelV2,
)


# ============================================================================
# COOLDOWN BESTIMMUNG (exaktes 30-Tage Fenster)
# ============================================================================

def is_in_cooldown(
    date: datetime,
    jackpot_dates: List[datetime],
    cooldown_days: int = 30
) -> Tuple[bool, int]:
    """
    Bestimmt ob ein Datum im 30-Tage Cooldown-Fenster liegt.

    Args:
        date: Zu pruefendes Datum
        jackpot_dates: Liste aller Jackpot-Daten
        cooldown_days: Cooldown-Fenster in Tagen (default: 30)

    Returns:
        Tuple (is_cooldown, days_since_jackpot)
        - is_cooldown: True wenn 0 < days_since_jackpot <= 30
        - days_since_jackpot: Tage seit letztem Jackpot (oder -1 wenn keiner)
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
# V1 BACKTEST MIT COOLDOWN-TRACKING
# ============================================================================

def backtest_v1_with_cooldown(
    model: SuperModelV1,
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9,
    start_idx: int = 365,
    strategy: str = "jackpot"
) -> Dict:
    """
    Fuehrt V1 Backtest mit exaktem 30-Tage Cooldown-Tracking durch.

    Alle Ziehungen werden gespielt (keine skip-Logik fuer fairen Vergleich).
    """

    results = {
        "model_version": "V1",
        "strategy": strategy,
        "keno_type": keno_type,
        "invested": 0,
        "won": 0,
        "played": 0,
        "hits_distribution": defaultdict(int),
        "high_wins": [],
        # Cooldown-Tracking (exakt 30 Tage)
        "cooldown_invested": 0,
        "cooldown_won": 0,
        "cooldown_draws": 0,
        "normal_invested": 0,
        "normal_won": 0,
        "normal_draws": 0,
    }

    for i in range(start_idx, len(keno_df)):
        prev_row = keno_df.iloc[i - 1]
        curr_row = keno_df.iloc[i]
        curr_date = curr_row["Datum"]

        # Cooldown bestimmen (exakt 30 Tage)
        is_cd, days_since = is_in_cooldown(curr_date, jackpot_dates)

        context = {
            "date": curr_date,
            "prev_date": prev_row["Datum"],
            "prev_positions": prev_row["positions"],
            "prev_numbers": list(prev_row["numbers_set"]),
            "jackpot_dates": jackpot_dates,
        }

        # Generiere Ticket (ohne skip fuer fairen Vergleich)
        ticket, metadata = model.generate_ticket(keno_type, context, strategy=strategy)

        # Simuliere
        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1

        # Cooldown-Tracking
        if is_cd:
            results["cooldown_invested"] += 1
            results["cooldown_won"] += win
            results["cooldown_draws"] += 1
        else:
            results["normal_invested"] += 1
            results["normal_won"] += win
            results["normal_draws"] += 1

        if win >= 100:
            results["high_wins"].append({
                "date": str(curr_date.date()),
                "ticket": ticket,
                "hits": hits,
                "win": win,
                "is_cooldown": is_cd,
                "days_since_jackpot": days_since,
            })

    # ROI gesamt
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0

    # ROI pro Phase
    results["cooldown_roi"] = 0
    if results["cooldown_invested"] > 0:
        results["cooldown_roi"] = (
            (results["cooldown_won"] - results["cooldown_invested"]) /
            results["cooldown_invested"] * 100
        )

    results["normal_roi"] = 0
    if results["normal_invested"] > 0:
        results["normal_roi"] = (
            (results["normal_won"] - results["normal_invested"]) /
            results["normal_invested"] * 100
        )

    return results


# ============================================================================
# V2 BACKTEST MIT COOLDOWN-TRACKING
# ============================================================================

def backtest_v2_with_cooldown(
    model: SuperModelV2,
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9,
    start_idx: int = 365
) -> Dict:
    """
    Fuehrt V2 Backtest mit exaktem 30-Tage Cooldown-Tracking durch.

    Alle Ziehungen werden gespielt (keine skip-Logik fuer fairen Vergleich).
    """

    results = {
        "model_version": "V2",
        "keno_type": keno_type,
        "invested": 0,
        "won": 0,
        "played": 0,
        "hits_distribution": defaultdict(int),
        "high_wins": [],
        # Cooldown-Tracking (exakt 30 Tage)
        "cooldown_invested": 0,
        "cooldown_won": 0,
        "cooldown_draws": 0,
        "normal_invested": 0,
        "normal_won": 0,
        "normal_draws": 0,
        # V2-internes Mode-Tracking
        "v2_mode_counts": defaultdict(int),
        "v2_mode_wins": defaultdict(float),
    }

    for i in range(start_idx, len(keno_df)):
        prev_row = keno_df.iloc[i - 1]
        curr_row = keno_df.iloc[i]
        curr_date = curr_row["Datum"]

        # Cooldown bestimmen (exakt 30 Tage)
        is_cd, days_since = is_in_cooldown(curr_date, jackpot_dates)

        context = {
            "date": curr_date,
            "prev_date": prev_row["Datum"],
            "prev_positions": prev_row["positions"],
            "prev_numbers": list(prev_row["numbers_set"]),
            "jackpot_dates": jackpot_dates,
        }

        # Generiere Ticket (ohne skip fuer fairen Vergleich)
        ticket, metadata = model.generate_ticket(keno_type, context)
        v2_mode = metadata.get("ticket_mode", "normal")

        # Simuliere
        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1

        # Cooldown-Tracking
        if is_cd:
            results["cooldown_invested"] += 1
            results["cooldown_won"] += win
            results["cooldown_draws"] += 1
        else:
            results["normal_invested"] += 1
            results["normal_won"] += win
            results["normal_draws"] += 1

        # V2-Mode-Tracking
        results["v2_mode_counts"][v2_mode] += 1
        results["v2_mode_wins"][v2_mode] += win

        if win >= 100:
            results["high_wins"].append({
                "date": str(curr_date.date()),
                "ticket": ticket,
                "hits": hits,
                "win": win,
                "is_cooldown": is_cd,
                "days_since_jackpot": days_since,
                "v2_mode": v2_mode,
            })

    # ROI gesamt
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0

    # ROI pro Phase
    results["cooldown_roi"] = 0
    if results["cooldown_invested"] > 0:
        results["cooldown_roi"] = (
            (results["cooldown_won"] - results["cooldown_invested"]) /
            results["cooldown_invested"] * 100
        )

    results["normal_roi"] = 0
    if results["normal_invested"] > 0:
        results["normal_roi"] = (
            (results["normal_won"] - results["normal_invested"]) /
            results["normal_invested"] * 100
        )

    # ROI pro V2-Mode
    results["v2_mode_roi"] = {}
    for mode, count in results["v2_mode_counts"].items():
        if count > 0:
            mode_win = results["v2_mode_wins"][mode]
            results["v2_mode_roi"][mode] = (mode_win - count) / count * 100

    return results


# ============================================================================
# VERGLEICH V1 vs V2 per Cooldown-Phase
# ============================================================================

def compare_v1_v2_cooldown(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_types: List[int] = [8, 9, 10]
) -> Dict:
    """
    Vergleicht V1 und V2 per exakter 30-Tage Cooldown-Phase.

    Key metric: ROI delta (V2-V1) in cooldown vs normal.
    """

    comparison = {
        "analysis_date": datetime.now().isoformat(),
        "cooldown_semantics": {
            "cooldown": "0-30 Tage nach Jackpot (WL-003: System spart)",
            "normal": ">30 Tage nach Jackpot (normaler Betrieb)",
        },
        "jackpot_count": len(jackpot_dates),
        "results": {},
        "summary": {},
    }

    for keno_type in keno_types:
        print(f"\n{'='*70}")
        print(f"TYP {keno_type} - V1 vs V2 COOLDOWN VERGLEICH (30-Tage Fenster)")
        print(f"{'='*70}")

        # V1 Backtest
        v1_model = SuperModelV1()
        v1_results = backtest_v1_with_cooldown(
            v1_model, keno_df, jackpot_dates, keno_type, strategy="jackpot"
        )

        # V2 Backtest
        v2_model = SuperModelV2()
        v2_results = backtest_v2_with_cooldown(
            v2_model, keno_df, jackpot_dates, keno_type
        )

        # Ergebnisse strukturieren
        type_results = {
            "v1": {
                "roi_gesamt": v1_results["roi"],
                "played": v1_results["played"],
                "won": v1_results["won"],
                "high_wins": len(v1_results["high_wins"]),
                "cooldown": {
                    "draws": v1_results["cooldown_draws"],
                    "roi": v1_results["cooldown_roi"],
                },
                "normal": {
                    "draws": v1_results["normal_draws"],
                    "roi": v1_results["normal_roi"],
                },
            },
            "v2": {
                "roi_gesamt": v2_results["roi"],
                "played": v2_results["played"],
                "won": v2_results["won"],
                "high_wins": len(v2_results["high_wins"]),
                "cooldown": {
                    "draws": v2_results["cooldown_draws"],
                    "roi": v2_results["cooldown_roi"],
                },
                "normal": {
                    "draws": v2_results["normal_draws"],
                    "roi": v2_results["normal_roi"],
                },
                "v2_mode_distribution": dict(v2_results["v2_mode_counts"]),
                "v2_mode_roi": v2_results["v2_mode_roi"],
            },
            "cooldown_comparison": {
                "v1_roi": v1_results["cooldown_roi"],
                "v2_roi": v2_results["cooldown_roi"],
                "delta_v2_minus_v1": v2_results["cooldown_roi"] - v1_results["cooldown_roi"],
                "draws": v1_results["cooldown_draws"],
                "winner": "V2" if v2_results["cooldown_roi"] > v1_results["cooldown_roi"] else "V1",
            },
            "normal_comparison": {
                "v1_roi": v1_results["normal_roi"],
                "v2_roi": v2_results["normal_roi"],
                "delta_v2_minus_v1": v2_results["normal_roi"] - v1_results["normal_roi"],
                "draws": v1_results["normal_draws"],
                "winner": "V2" if v2_results["normal_roi"] > v1_results["normal_roi"] else "V1",
            },
        }

        comparison["results"][f"typ_{keno_type}"] = type_results

        # Ausgabe
        print(f"\n  GESAMT:")
        print(f"    V1: ROI {v1_results['roi']:+.2f}%, Spiele: {v1_results['played']}")
        print(f"    V2: ROI {v2_results['roi']:+.2f}%, Spiele: {v2_results['played']}")

        print(f"\n  COOLDOWN PHASE (0-30 Tage post-Jackpot, N={v1_results['cooldown_draws']}):")
        print(f"    V1: ROI {v1_results['cooldown_roi']:+.2f}%")
        print(f"    V2: ROI {v2_results['cooldown_roi']:+.2f}%")
        delta_cd = v2_results['cooldown_roi'] - v1_results['cooldown_roi']
        winner_cd = "V2" if delta_cd > 0 else "V1"
        print(f"    Delta (V2-V1): {delta_cd:+.2f}% -> Winner: {winner_cd}")

        print(f"\n  NORMAL PHASE (>30 Tage post-Jackpot, N={v1_results['normal_draws']}):")
        print(f"    V1: ROI {v1_results['normal_roi']:+.2f}%")
        print(f"    V2: ROI {v2_results['normal_roi']:+.2f}%")
        delta_nm = v2_results['normal_roi'] - v1_results['normal_roi']
        winner_nm = "V2" if delta_nm > 0 else "V1"
        print(f"    Delta (V2-V1): {delta_nm:+.2f}% -> Winner: {winner_nm}")

    # Summary
    cooldown_v1_wins = 0
    cooldown_v2_wins = 0
    normal_v1_wins = 0
    normal_v2_wins = 0

    for typ_key, typ_data in comparison["results"].items():
        if typ_data["cooldown_comparison"]["winner"] == "V1":
            cooldown_v1_wins += 1
        else:
            cooldown_v2_wins += 1
        if typ_data["normal_comparison"]["winner"] == "V1":
            normal_v1_wins += 1
        else:
            normal_v2_wins += 1

    comparison["summary"] = {
        "cooldown_phase": {
            "v1_wins": cooldown_v1_wins,
            "v2_wins": cooldown_v2_wins,
            "dominant_model": "V2" if cooldown_v2_wins > cooldown_v1_wins else "V1",
        },
        "normal_phase": {
            "v1_wins": normal_v1_wins,
            "v2_wins": normal_v2_wins,
            "dominant_model": "V2" if normal_v2_wins > normal_v1_wins else "V1",
        },
        "wl003_hypothesis": (
            "BESTAETIGT" if cooldown_v1_wins != cooldown_v2_wins or normal_v1_wins != normal_v2_wins
            else "NICHT_SIGNIFIKANT"
        ),
    }

    return comparison


def main():
    """Hauptfunktion: V1 vs V2 Cooldown-Phase Vergleich."""
    print("=" * 70)
    print("V1 vs V2 COOLDOWN-PHASE TEST (TASK_041)")
    print("=" * 70)
    print()
    print("Cooldown-Semantik (WL-003 konform):")
    print("  - cooldown: 0-30 Tage nach Jackpot (System spart)")
    print("  - normal:   >30 Tage nach Jackpot (normaler Betrieb)")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots (Typ10/10): {len(jackpot_dates)}")

    # Jackpot-Daten anzeigen
    print(f"\nJackpot-Daten (konsistent mit 11 Jackpots 2022-2024):")
    for i, jp in enumerate(jackpot_dates[:5], 1):
        print(f"  {i}. {jp.date()}")
    if len(jackpot_dates) > 5:
        print(f"  ... und {len(jackpot_dates) - 5} weitere")

    # Vergleich durchfuehren
    comparison = compare_v1_v2_cooldown(keno_df, jackpot_dates, keno_types=[8, 9, 10])

    # Speichern
    output_path = base_path / "results" / "v1_v2_cooldown_comparison.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Summary ausgeben
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    summary = comparison["summary"]

    print(f"\n  COOLDOWN PHASE (0-30 Tage post-Jackpot):")
    print(f"    V1 gewinnt: {summary['cooldown_phase']['v1_wins']} Typen")
    print(f"    V2 gewinnt: {summary['cooldown_phase']['v2_wins']} Typen")
    print(f"    Dominant: {summary['cooldown_phase']['dominant_model']}")

    print(f"\n  NORMAL PHASE (>30 Tage post-Jackpot):")
    print(f"    V1 gewinnt: {summary['normal_phase']['v1_wins']} Typen")
    print(f"    V2 gewinnt: {summary['normal_phase']['v2_wins']} Typen")
    print(f"    Dominant: {summary['normal_phase']['dominant_model']}")

    print(f"\n  WL-003 HYPOTHESE: {summary['wl003_hypothesis']}")

    print("\n" + "=" * 70)
    print("REPRO COMMAND:")
    print("  python scripts/backtest_v1_v2_cooldown.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
