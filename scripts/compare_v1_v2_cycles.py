#!/usr/bin/env python3
"""
V1 vs V2 Per-28-Day-Cycle Vergleich

TASK_039c: Vergleicht V1 und V2 Birthday-Avoidance Strategien per 28-Tage-Zyklus.

Cycle-Semantik:
- Nicht-ueberlappende 28-Tage-Fenster (stride=28)
- ~28 Draws pro Zyklus (1 Draw/Tag)
- Rolling ab erstem verfuegbaren Datum

Output: results/v1_v2_cycle_comparison.json

Repro: python scripts/compare_v1_v2_cycles.py
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
# CYCLE SEGMENTATION (28-Tage nicht-ueberlappend)
# ============================================================================

def segment_into_cycles(
    keno_df: pd.DataFrame,
    cycle_days: int = 28,
    start_idx: int = 365
) -> List[Dict]:
    """
    Segmentiert DataFrame in nicht-ueberlappende 28-Tage-Zyklen.

    Args:
        keno_df: DataFrame mit KENO-Ziehungen
        cycle_days: Tage pro Zyklus (default: 28)
        start_idx: Start-Index fuer Backtest (Training-Periode)

    Returns:
        Liste von Zyklen mit cycle_idx, start_date, end_date, indices
    """
    cycles = []

    # Nutze nur Daten ab start_idx
    df_subset = keno_df.iloc[start_idx:].copy()

    if len(df_subset) == 0:
        return cycles

    first_date = df_subset.iloc[0]["Datum"]
    last_date = df_subset.iloc[-1]["Datum"]

    cycle_idx = 0
    cycle_start = first_date

    while cycle_start <= last_date:
        cycle_end = cycle_start + timedelta(days=cycle_days - 1)

        # Finde alle Draws in diesem Zyklus
        mask = (df_subset["Datum"] >= cycle_start) & (df_subset["Datum"] <= cycle_end)
        cycle_draws = df_subset[mask]

        if len(cycle_draws) > 0:
            # Hole die originalen DataFrame-Indizes
            indices = cycle_draws.index.tolist()

            cycles.append({
                "cycle_idx": cycle_idx,
                "cycle_start_date": cycle_start,
                "cycle_end_date": cycle_end,
                "num_draws": len(cycle_draws),
                "indices": indices,
            })
            cycle_idx += 1

        cycle_start = cycle_end + timedelta(days=1)

    return cycles


# ============================================================================
# BACKTEST FUER EINZELNEN ZYKLUS
# ============================================================================

def backtest_cycle(
    model,
    keno_df: pd.DataFrame,
    cycle_indices: List[int],
    jackpot_dates: List[datetime],
    keno_type: int,
    is_v1: bool = True,
    strategy: str = "jackpot"
) -> Dict:
    """
    Fuehrt Backtest fuer einen einzelnen Zyklus durch.

    Args:
        model: SuperModelV1 oder SuperModelV2 Instanz
        keno_df: DataFrame mit KENO-Ziehungen
        cycle_indices: DataFrame-Indizes fuer diesen Zyklus
        jackpot_dates: Liste aller Jackpot-Daten
        keno_type: KENO-Typ (8, 9, 10)
        is_v1: True fuer V1, False fuer V2
        strategy: Strategie fuer V1 (default: "jackpot")

    Returns:
        Dict mit ROI, invested, won, hits_distribution, high_wins
    """
    results = {
        "invested": 0,
        "won": 0,
        "played": 0,
        "hits_distribution": defaultdict(int),
        "high_wins": [],
    }

    for idx in cycle_indices:
        # Sicherstellen, dass prev_row existiert
        if idx - 1 < 0:
            continue

        prev_row = keno_df.iloc[idx - 1]
        curr_row = keno_df.iloc[idx]
        curr_date = curr_row["Datum"]

        context = {
            "date": curr_date,
            "prev_date": prev_row["Datum"],
            "prev_positions": prev_row["positions"],
            "prev_numbers": list(prev_row["numbers_set"]),
            "jackpot_dates": jackpot_dates,
        }

        # Generiere Ticket
        if is_v1:
            ticket, metadata = model.generate_ticket(keno_type, context, strategy=strategy)
        else:
            ticket, metadata = model.generate_ticket(keno_type, context)

        # Simuliere
        draw_set = curr_row["numbers_set"]
        win, hits = simulate_ticket(ticket, keno_type, draw_set)

        results["invested"] += 1
        results["won"] += win
        results["played"] += 1
        results["hits_distribution"][hits] += 1

        if win >= 100:
            results["high_wins"].append({
                "date": str(curr_date.date()),
                "ticket": ticket,
                "hits": hits,
                "win": win,
            })

    # ROI berechnen
    if results["invested"] > 0:
        results["roi"] = (results["won"] - results["invested"]) / results["invested"] * 100
    else:
        results["roi"] = 0.0

    return results


# ============================================================================
# V1 vs V2 PER-CYCLE VERGLEICH
# ============================================================================

def compare_v1_v2_per_cycle(
    keno_df: pd.DataFrame,
    jackpot_dates: List[datetime],
    keno_types: List[int] = [8, 9, 10],
    cycle_days: int = 28,
    start_idx: int = 365
) -> Dict:
    """
    Vergleicht V1 und V2 per 28-Tage-Zyklus.

    Args:
        keno_df: DataFrame mit KENO-Ziehungen
        jackpot_dates: Liste aller Jackpot-Daten
        keno_types: Liste der KENO-Typen
        cycle_days: Tage pro Zyklus
        start_idx: Start-Index (Training-Periode)

    Returns:
        Dict mit per-cycle Vergleich
    """
    # Segmentiere in Zyklen
    cycles = segment_into_cycles(keno_df, cycle_days, start_idx)

    comparison = {
        "analysis_date": datetime.now().isoformat(),
        "cycle_semantics": {
            "cycle_days": cycle_days,
            "non_overlapping": True,
            "start_idx": start_idx,
            "total_cycles": len(cycles),
        },
        "results": {},
        "per_cycle_detail": {},
        "summary": {},
    }

    print(f"\nZyklen segmentiert: {len(cycles)} x {cycle_days} Tage")

    for keno_type in keno_types:
        print(f"\n{'='*70}")
        print(f"TYP {keno_type} - V1 vs V2 PER-CYCLE VERGLEICH")
        print(f"{'='*70}")

        v1_model = SuperModelV1()
        v2_model = SuperModelV2()

        # Aggregierte Ergebnisse
        v1_total = {"invested": 0, "won": 0, "high_wins": 0}
        v2_total = {"invested": 0, "won": 0, "high_wins": 0}

        # Per-Cycle Ergebnisse
        cycle_comparisons = []

        for cycle in cycles:
            cycle_idx = cycle["cycle_idx"]
            indices = cycle["indices"]

            # V1 Backtest fuer diesen Zyklus
            v1_result = backtest_cycle(
                v1_model, keno_df, indices, jackpot_dates, keno_type, is_v1=True
            )

            # V2 Backtest fuer diesen Zyklus
            v2_result = backtest_cycle(
                v2_model, keno_df, indices, jackpot_dates, keno_type, is_v1=False
            )

            # Aggregiere
            v1_total["invested"] += v1_result["invested"]
            v1_total["won"] += v1_result["won"]
            v1_total["high_wins"] += len(v1_result["high_wins"])

            v2_total["invested"] += v2_result["invested"]
            v2_total["won"] += v2_result["won"]
            v2_total["high_wins"] += len(v2_result["high_wins"])

            # Delta und Winner
            v1_roi = v1_result["roi"]
            v2_roi = v2_result["roi"]
            delta = v2_roi - v1_roi

            if v2_roi > v1_roi:
                winner = "V2"
            elif v1_roi > v2_roi:
                winner = "V1"
            else:
                winner = "TIE"

            cycle_comp = {
                "cycle_idx": cycle_idx,
                "cycle_start_date": str(cycle["cycle_start_date"].date()),
                "cycle_end_date": str(cycle["cycle_end_date"].date()),
                "num_draws": cycle["num_draws"],
                "v1_roi": round(v1_roi, 2),
                "v1_won": round(v1_result["won"], 2),
                "v1_invested": v1_result["invested"],
                "v1_high_wins": len(v1_result["high_wins"]),
                "v2_roi": round(v2_roi, 2),
                "v2_won": round(v2_result["won"], 2),
                "v2_invested": v2_result["invested"],
                "v2_high_wins": len(v2_result["high_wins"]),
                "delta": round(delta, 2),
                "winner": winner,
            }
            cycle_comparisons.append(cycle_comp)

        # Gesamt-ROI
        v1_roi_total = (v1_total["won"] - v1_total["invested"]) / v1_total["invested"] * 100 if v1_total["invested"] > 0 else 0
        v2_roi_total = (v2_total["won"] - v2_total["invested"]) / v2_total["invested"] * 100 if v2_total["invested"] > 0 else 0

        # Count Wins per Model
        v1_cycle_wins = sum(1 for c in cycle_comparisons if c["winner"] == "V1")
        v2_cycle_wins = sum(1 for c in cycle_comparisons if c["winner"] == "V2")
        ties = sum(1 for c in cycle_comparisons if c["winner"] == "TIE")

        type_results = {
            "v1_roi_total": round(v1_roi_total, 2),
            "v1_total_invested": v1_total["invested"],
            "v1_total_won": round(v1_total["won"], 2),
            "v1_total_high_wins": v1_total["high_wins"],
            "v2_roi_total": round(v2_roi_total, 2),
            "v2_total_invested": v2_total["invested"],
            "v2_total_won": round(v2_total["won"], 2),
            "v2_total_high_wins": v2_total["high_wins"],
            "delta_total": round(v2_roi_total - v1_roi_total, 2),
            "v1_cycle_wins": v1_cycle_wins,
            "v2_cycle_wins": v2_cycle_wins,
            "ties": ties,
            "total_cycles": len(cycle_comparisons),
        }

        comparison["results"][f"typ_{keno_type}"] = type_results
        comparison["per_cycle_detail"][f"typ_{keno_type}"] = cycle_comparisons

        # Ausgabe
        print(f"\n  GESAMT:")
        print(f"    V1: ROI {v1_roi_total:+.2f}%, Invested: {v1_total['invested']}, High Wins: {v1_total['high_wins']}")
        print(f"    V2: ROI {v2_roi_total:+.2f}%, Invested: {v2_total['invested']}, High Wins: {v2_total['high_wins']}")
        print(f"    Delta: {v2_roi_total - v1_roi_total:+.2f}%")

        print(f"\n  CYCLE WINS (wer hat mehr Zyklen gewonnen):")
        print(f"    V1 gewinnt: {v1_cycle_wins} / {len(cycle_comparisons)} Zyklen")
        print(f"    V2 gewinnt: {v2_cycle_wins} / {len(cycle_comparisons)} Zyklen")
        print(f"    Ties: {ties}")

        # Top 3 beste Zyklen fuer V1 und V2
        sorted_by_v1 = sorted(cycle_comparisons, key=lambda x: x["v1_roi"], reverse=True)[:3]
        sorted_by_v2 = sorted(cycle_comparisons, key=lambda x: x["v2_roi"], reverse=True)[:3]

        print(f"\n  TOP 3 ZYKLEN V1 (bestes ROI):")
        for c in sorted_by_v1:
            print(f"    Zyklus {c['cycle_idx']}: {c['cycle_start_date']} - {c['cycle_end_date']}, ROI: {c['v1_roi']:+.2f}%")

        print(f"\n  TOP 3 ZYKLEN V2 (bestes ROI):")
        for c in sorted_by_v2:
            print(f"    Zyklus {c['cycle_idx']}: {c['cycle_start_date']} - {c['cycle_end_date']}, ROI: {c['v2_roi']:+.2f}%")

    # Summary ueber alle Typen
    total_v1_wins = sum(comparison["results"][f"typ_{t}"]["v1_cycle_wins"] for t in keno_types)
    total_v2_wins = sum(comparison["results"][f"typ_{t}"]["v2_cycle_wins"] for t in keno_types)
    total_ties = sum(comparison["results"][f"typ_{t}"]["ties"] for t in keno_types)
    total_cycles_all = sum(comparison["results"][f"typ_{t}"]["total_cycles"] for t in keno_types)

    comparison["summary"] = {
        "total_comparisons": total_cycles_all,
        "v1_cycle_wins_all_types": total_v1_wins,
        "v2_cycle_wins_all_types": total_v2_wins,
        "ties_all_types": total_ties,
        "overall_winner": "V2" if total_v2_wins > total_v1_wins else "V1" if total_v1_wins > total_v2_wins else "TIE",
    }

    return comparison


def main():
    """Hauptfunktion: V1 vs V2 Per-Cycle Vergleich."""
    print("=" * 70)
    print("V1 vs V2 PER-28-DAY-CYCLE VERGLEICH")
    print("=" * 70)
    print()
    print("Cycle-Semantik:")
    print("  - 28 Tage pro Zyklus (nicht-ueberlappend)")
    print("  - ~28 Draws pro Zyklus")
    print("  - Rolling ab start_idx=365")
    print()

    base_path = Path(__file__).parent.parent

    print("Lade Daten...")
    keno_df, jackpot_dates = load_data(base_path)
    print(f"  KENO Ziehungen: {len(keno_df)}")
    print(f"  Jackpots: {len(jackpot_dates)}")

    # Vergleich durchfuehren
    comparison = compare_v1_v2_per_cycle(
        keno_df, jackpot_dates,
        keno_types=[8, 9, 10],
        cycle_days=28,
        start_idx=365
    )

    # Speichern
    output_path = base_path / "results" / "v1_v2_cycle_comparison.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n\nErgebnisse gespeichert: {output_path}")

    # Summary ausgeben
    print("\n" + "=" * 70)
    print("SUMMARY (ALLE TYPEN)")
    print("=" * 70)
    summary = comparison["summary"]
    print(f"\n  Vergleiche gesamt: {summary['total_comparisons']}")
    print(f"  V1 Zyklen gewonnen: {summary['v1_cycle_wins_all_types']}")
    print(f"  V2 Zyklen gewonnen: {summary['v2_cycle_wins_all_types']}")
    print(f"  Ties: {summary['ties_all_types']}")
    print(f"\n  OVERALL WINNER: {summary['overall_winner']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
