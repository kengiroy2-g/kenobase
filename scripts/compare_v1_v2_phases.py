#!/usr/bin/env python3
"""
V1 vs V2 Per-Phase Vergleich

TASK_039: Vergleicht V1 und V2 Birthday-Avoidance Strategien per Phase.

Phasen-Semantik (basierend auf GK1-Cooldown Events):
- normal: Kein Cooldown aktiv (>30 Tage seit letztem Jackpot)
- conservative: Leichter Cooldown (7-30 Tage seit Jackpot)
- jackpot: Starker Cooldown (<7 Tage seit Jackpot)

Output: results/v1_v2_phase_comparison.json

Repro: python scripts/compare_v1_v2_phases.py
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
    KENO_QUOTES,
    load_data,
    simulate_ticket,
)

from super_model_v1_birthday import (
    SuperModelV1,
    BIRTHDAY_NUMBERS,
    HIGH_NUMBERS,
)

from super_model_v2_birthday_signal import (
    SuperModelV2,
    BIRTHDAY_NUMBERS as V2_BIRTHDAY_NUMBERS,
)


# ============================================================================
# PHASE BESTIMMUNG (basierend auf GK1-Cooldown)
# ============================================================================

def determine_phase(
    date: datetime,
    jackpot_dates: List[datetime],
    cooldown_severe: int = 7,
    cooldown_moderate: int = 30
) -> str:
    """
    Bestimmt die aktuelle Phase basierend auf Jackpot-Cooldown.

    Phasen:
    - "jackpot": <7 Tage seit letztem Jackpot (starker Cooldown)
    - "conservative": 7-30 Tage seit Jackpot (leichter Cooldown)
    - "normal": >30 Tage seit Jackpot (kein Cooldown)
    """
    if not jackpot_dates:
        return "normal"

    # Finde letzten Jackpot vor dem aktuellen Datum
    past_jackpots = [jp for jp in jackpot_dates if jp < date]

    if not past_jackpots:
        return "normal"

    last_jackpot = max(past_jackpots)
    days_since = (date - last_jackpot).days

    if days_since < cooldown_severe:
        return "jackpot"
    elif days_since < cooldown_moderate:
        return "conservative"
    else:
        return "normal"


# ============================================================================
# V1 BACKTEST MIT PHASE-TRACKING
# ============================================================================

def backtest_v1_with_phases(
    model: SuperModelV1,
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9,
    start_idx: int = 365,
    strategy: str = "jackpot",
    include_all_phases: bool = True
) -> Dict:
    """Fuehrt V1 Backtest mit Phase-Tracking durch.

    Args:
        include_all_phases: Wenn True, werden auch Draws in Cooldown-Phasen
                           mitgezaehlt (skip-Logik ignoriert fuer Phase-Vergleich).
    """

    results = {
        "model_version": "V1",
        "strategy": strategy,
        "keno_type": keno_type,
        "invested": 0,
        "won": 0,
        "skipped": 0,
        "played": 0,
        "hits_distribution": defaultdict(int),
        "high_wins": [],
        # Phase-Tracking (neu fuer V1)
        "mode_counts": defaultdict(int),
        "mode_wins": defaultdict(float),
        "mode_played": defaultdict(int),
    }

    for i in range(start_idx, len(keno_df)):
        prev_row = keno_df.iloc[i - 1]
        curr_row = keno_df.iloc[i]
        curr_date = curr_row["Datum"]

        # Phase bestimmen
        phase = determine_phase(curr_date, jackpot_dates)

        context = {
            "date": curr_date,
            "prev_date": prev_row["Datum"],
            "prev_positions": prev_row["positions"],
            "prev_numbers": list(prev_row["numbers_set"]),
            "jackpot_dates": jackpot_dates,
        }

        # Skip-Check - OPTIONAL fuer Phase-Vergleich
        if not include_all_phases:
            should_skip, reason = model.should_skip(context)
            if should_skip:
                results["skipped"] += 1
                continue

        # Generiere Ticket
        ticket, metadata = model.generate_ticket(keno_type, context, strategy=strategy)

        # Simuliere
        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1

        # Phase-Tracking
        results["mode_counts"][phase] += 1
        results["mode_wins"][phase] += win
        results["mode_played"][phase] += 1

        if win >= 100:
            results["high_wins"].append({
                "date": str(curr_date.date()),
                "ticket": ticket,
                "hits": hits,
                "win": win,
                "phase": phase,
            })

    # ROI gesamt
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0

    # ROI pro Phase
    results["mode_roi"] = {}
    for phase, count in results["mode_counts"].items():
        if count > 0:
            phase_win = results["mode_wins"][phase]
            results["mode_roi"][phase] = (phase_win - count) / count * 100

    return results


# ============================================================================
# V2 BACKTEST MIT PHASE-TRACKING (erweitert)
# ============================================================================

def backtest_v2_with_phases(
    model: SuperModelV2,
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_type: int = 9,
    start_idx: int = 365,
    include_all_phases: bool = True
) -> Dict:
    """Fuehrt V2 Backtest mit GK1-Cooldown Phase-Tracking durch.

    Args:
        include_all_phases: Wenn True, werden auch Draws in Cooldown-Phasen
                           mitgezaehlt (skip-Logik ignoriert fuer Phase-Vergleich).
    """

    results = {
        "model_version": "V2",
        "keno_type": keno_type,
        "invested": 0,
        "won": 0,
        "skipped": 0,
        "played": 0,
        "hits_distribution": defaultdict(int),
        "high_wins": [],
        # Phase-Tracking (GK1-basiert, nicht V2-internes Mode)
        "mode_counts": defaultdict(int),
        "mode_wins": defaultdict(float),
        "mode_played": defaultdict(int),
        # V2-internes Mode-Tracking (Birthday-Signal basiert)
        "v2_mode_counts": defaultdict(int),
        "v2_mode_wins": defaultdict(float),
    }

    for i in range(start_idx, len(keno_df)):
        prev_row = keno_df.iloc[i - 1]
        curr_row = keno_df.iloc[i]
        curr_date = curr_row["Datum"]

        # GK1-Cooldown Phase bestimmen
        phase = determine_phase(curr_date, jackpot_dates)

        context = {
            "date": curr_date,
            "prev_date": prev_row["Datum"],
            "prev_positions": prev_row["positions"],
            "prev_numbers": list(prev_row["numbers_set"]),
            "jackpot_dates": jackpot_dates,
        }

        # Skip-Check - OPTIONAL fuer Phase-Vergleich
        if not include_all_phases:
            should_skip, reason = model.should_skip(context)
            if should_skip:
                results["skipped"] += 1
                continue

        # Generiere Ticket
        ticket, metadata = model.generate_ticket(keno_type, context)
        v2_mode = metadata.get("ticket_mode", "normal")

        # Simuliere
        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1

        # GK1-Cooldown Phase-Tracking
        results["mode_counts"][phase] += 1
        results["mode_wins"][phase] += win
        results["mode_played"][phase] += 1

        # V2-internes Mode-Tracking
        results["v2_mode_counts"][v2_mode] += 1
        results["v2_mode_wins"][v2_mode] += win

        if win >= 100:
            results["high_wins"].append({
                "date": str(curr_date.date()),
                "ticket": ticket,
                "hits": hits,
                "win": win,
                "phase": phase,
                "v2_mode": v2_mode,
            })

    # ROI gesamt
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0

    # ROI pro GK1-Phase
    results["mode_roi"] = {}
    for phase, count in results["mode_counts"].items():
        if count > 0:
            phase_win = results["mode_wins"][phase]
            results["mode_roi"][phase] = (phase_win - count) / count * 100

    # ROI pro V2-Mode
    results["v2_mode_roi"] = {}
    for mode, count in results["v2_mode_counts"].items():
        if count > 0:
            mode_win = results["v2_mode_wins"][mode]
            results["v2_mode_roi"][mode] = (mode_win - count) / count * 100

    return results


# ============================================================================
# VERGLEICH
# ============================================================================

def compare_v1_v2_per_phase(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_types: List[int] = [8, 9, 10]
) -> Dict:
    """Vergleicht V1 und V2 per GK1-Cooldown Phase."""

    comparison = {
        "analysis_date": datetime.now().isoformat(),
        "phase_semantics": {
            "normal": ">30 Tage seit letztem Jackpot (kein Cooldown)",
            "conservative": "7-30 Tage seit Jackpot (leichter Cooldown)",
            "jackpot": "<7 Tage seit Jackpot (starker Cooldown)",
        },
        "results": {},
        "summary": {},
    }

    for keno_type in keno_types:
        print(f"\n{'='*70}")
        print(f"TYP {keno_type} - V1 vs V2 PER-PHASE VERGLEICH")
        print(f"{'='*70}")

        # V1 Backtest
        v1_model = SuperModelV1()
        v1_results = backtest_v1_with_phases(
            v1_model, keno_df, jackpot_dates, keno_type, strategy="jackpot"
        )

        # V2 Backtest
        v2_model = SuperModelV2()
        v2_results = backtest_v2_with_phases(
            v2_model, keno_df, jackpot_dates, keno_type
        )

        # Ergebnisse strukturieren
        type_results = {
            "v1": {
                "roi_gesamt": v1_results["roi"],
                "played": v1_results["played"],
                "won": v1_results["won"],
                "high_wins": len(v1_results["high_wins"]),
                "mode_distribution": dict(v1_results["mode_counts"]),
                "mode_roi": v1_results["mode_roi"],
            },
            "v2": {
                "roi_gesamt": v2_results["roi"],
                "played": v2_results["played"],
                "won": v2_results["won"],
                "high_wins": len(v2_results["high_wins"]),
                "mode_distribution": dict(v2_results["mode_counts"]),
                "mode_roi": v2_results["mode_roi"],
                "v2_internal_mode_distribution": dict(v2_results["v2_mode_counts"]),
                "v2_internal_mode_roi": v2_results["v2_mode_roi"],
            },
            "per_phase_comparison": {},
        }

        # Per-Phase Delta
        for phase in ["normal", "conservative", "jackpot"]:
            v1_roi = v1_results["mode_roi"].get(phase, 0)
            v2_roi = v2_results["mode_roi"].get(phase, 0)
            v1_count = v1_results["mode_counts"].get(phase, 0)
            v2_count = v2_results["mode_counts"].get(phase, 0)

            type_results["per_phase_comparison"][phase] = {
                "v1_roi": v1_roi,
                "v2_roi": v2_roi,
                "delta": v2_roi - v1_roi,
                "v1_games": v1_count,
                "v2_games": v2_count,
                "winner": "V2" if v2_roi > v1_roi else "V1" if v1_roi > v2_roi else "TIE",
            }

        comparison["results"][f"typ_{keno_type}"] = type_results

        # Ausgabe
        print(f"\n  GESAMT:")
        print(f"    V1: ROI {v1_results['roi']:+.2f}%, Spiele: {v1_results['played']}")
        print(f"    V2: ROI {v2_results['roi']:+.2f}%, Spiele: {v2_results['played']}")

        print(f"\n  PER-PHASE VERGLEICH (GK1-Cooldown):")
        for phase in ["normal", "conservative", "jackpot"]:
            v1_roi = v1_results["mode_roi"].get(phase, 0)
            v2_roi = v2_results["mode_roi"].get(phase, 0)
            v1_count = v1_results["mode_counts"].get(phase, 0)
            v2_count = v2_results["mode_counts"].get(phase, 0)
            delta = v2_roi - v1_roi
            winner = "V2" if v2_roi > v1_roi else "V1" if v1_roi > v2_roi else "TIE"

            print(f"\n    {phase.upper():12s}:")
            print(f"      V1: ROI {v1_roi:+.2f}% ({v1_count} Spiele)")
            print(f"      V2: ROI {v2_roi:+.2f}% ({v2_count} Spiele)")
            print(f"      Delta: {delta:+.2f}% -> Winner: {winner}")

    # Summary: Welches Modell in welcher Phase besser
    summary_wins = {"V1": 0, "V2": 0, "TIE": 0}
    best_phase_model = {}

    for typ_key, typ_data in comparison["results"].items():
        for phase, phase_data in typ_data["per_phase_comparison"].items():
            winner = phase_data["winner"]
            summary_wins[winner] += 1
            key = f"{typ_key}_{phase}"
            best_phase_model[key] = winner

    comparison["summary"] = {
        "total_comparisons": sum(summary_wins.values()),
        "v1_wins": summary_wins["V1"],
        "v2_wins": summary_wins["V2"],
        "ties": summary_wins["TIE"],
        "best_per_scenario": best_phase_model,
    }

    return comparison


def main():
    """Hauptfunktion: V1 vs V2 Per-Phase Vergleich."""
    print("=" * 70)
    print("V1 vs V2 PER-PHASE VERGLEICH")
    print("=" * 70)
    print()
    print("Phasen-Semantik (GK1-Cooldown basiert):")
    print("  - normal:       >30 Tage seit letztem Jackpot")
    print("  - conservative: 7-30 Tage seit Jackpot")
    print("  - jackpot:      <7 Tage seit Jackpot")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Vergleich durchfuehren
    comparison = compare_v1_v2_per_phase(keno_df, jackpot_dates, keno_types=[8, 9, 10])

    # Speichern
    output_path = base_path / "results" / "v1_v2_phase_comparison.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Summary ausgeben
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    summary = comparison["summary"]
    print(f"\n  Vergleiche gesamt: {summary['total_comparisons']}")
    print(f"  V1 gewinnt: {summary['v1_wins']}")
    print(f"  V2 gewinnt: {summary['v2_wins']}")
    print(f"  Unentschieden: {summary['ties']}")

    print("\n  Best Model per Scenario:")
    for scenario, winner in summary["best_per_scenario"].items():
        print(f"    {scenario:20s}: {winner}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
