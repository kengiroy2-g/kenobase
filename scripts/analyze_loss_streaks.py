#!/usr/bin/env python
"""Verlust-Serien (Loss Streak) Analyse fuer KENO-Backtests.

Berechnet loss streak, drawdown und recovery Metriken pro Ticket-Typ.
Vergleicht gegen Null-Model (random tickets) zur Validierung.

Axiom-First Verknuepfung:
- A1 (House-Edge): Erwartete Verluste, max_drawdown
- A7 (Reset-Zyklen): Recovery-Zeiten nach Verlust-Serien

Usage:
    python scripts/analyze_loss_streaks.py \\
        --data data/raw/keno/KENO_ab_2022_bereinigt.csv \\
        --types 2,6,8,10 \\
        --output results/loss_streak_analysis.json

Author: EXECUTOR (TASK_033)
Date: 2025-12-30
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.analysis.near_miss import KENO_PROBABILITIES


@dataclass(frozen=True)
class LossStreakMetrics:
    """Loss streak metrics for a single ticket-type."""

    keno_type: int
    n_draws: int
    ticket: list[int]

    # Streak metrics
    total_losses: int  # Draws with 0 or 1 hits (no payout for most types)
    max_loss_streak: int  # Longest consecutive draws without payout
    mean_loss_streak: float  # Average length of loss streaks
    loss_streak_count: int  # Number of distinct loss streaks

    # Drawdown metrics (cumulative losses before recovery)
    max_drawdown_pct: float  # Max percentage drop from peak
    max_drawdown_draws: int  # Number of draws in max drawdown

    # Recovery metrics
    mean_recovery_draws: float  # Average draws to recover from loss streak
    max_recovery_draws: int  # Maximum draws to recover

    # Win frequency
    win_rate: float  # Fraction of draws with payout (>=2 hits or special)


@dataclass(frozen=True)
class NullModelComparison:
    """Comparison of observed loss streaks vs random ticket null model."""

    keno_type: int
    observed_max_loss_streak: int
    null_mean_max_loss_streak: float
    null_std_max_loss_streak: float
    null_percentile_95: float
    z_score: float
    is_within_null: bool  # True if observed <= 95th percentile
    conclusion: str


@dataclass(frozen=True)
class LossStreakAnalysisResult:
    """Complete analysis result."""

    generated_at: str
    draws_path: str
    n_draws: int
    keno_types: list[int]
    per_type_metrics: list[LossStreakMetrics]
    null_model_comparison: list[NullModelComparison]
    axiom_notes: dict[str, str]


def is_payout(keno_type: int, hits: int) -> bool:
    """Check if the number of hits results in a payout for given keno_type.

    Payout rules (simplified):
    - Typ-2: 2 hits
    - Typ-3: 2+ hits
    - Typ-4 to Typ-10: 0 hits (special payout) or 3+ hits
    """
    if keno_type == 2:
        return hits >= 2
    elif keno_type == 3:
        return hits >= 2
    elif keno_type >= 4:
        # 0 hits is a special payout for Typ-4+
        # 3+ hits is regular payout
        return hits == 0 or hits >= 3
    return False


def compute_loss_streaks(hits_list: list[int], keno_type: int) -> tuple[list[int], int]:
    """Compute all loss streak lengths and the maximum.

    Returns:
        Tuple of (list of streak lengths, max streak length)
    """
    streaks: list[int] = []
    current_streak = 0

    for hits in hits_list:
        if not is_payout(keno_type, hits):
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
            current_streak = 0

    # Handle trailing streak
    if current_streak > 0:
        streaks.append(current_streak)

    max_streak = max(streaks) if streaks else 0
    return streaks, max_streak


def compute_drawdown(hits_list: list[int], keno_type: int) -> tuple[float, int]:
    """Compute max drawdown (percentage) and its duration.

    Drawdown = (peak - current) / peak, tracking cumulative win count.

    Returns:
        Tuple of (max_drawdown_pct, max_drawdown_draws)
    """
    if not hits_list:
        return 0.0, 0

    cumulative_wins = 0
    peak_wins = 0
    max_drawdown_pct = 0.0
    max_drawdown_draws = 0

    current_drawdown_start = 0
    in_drawdown = False

    for i, hits in enumerate(hits_list):
        if is_payout(keno_type, hits):
            cumulative_wins += 1

        if cumulative_wins > peak_wins:
            peak_wins = cumulative_wins
            in_drawdown = False
        elif peak_wins > 0:
            current_dd = (peak_wins - cumulative_wins) / peak_wins
            if current_dd > 0 and not in_drawdown:
                current_drawdown_start = i
                in_drawdown = True

            if current_dd > max_drawdown_pct:
                max_drawdown_pct = current_dd
                max_drawdown_draws = i - current_drawdown_start + 1

    return round(max_drawdown_pct * 100, 2), max_drawdown_draws


def compute_recovery_times(hits_list: list[int], keno_type: int) -> tuple[float, int]:
    """Compute mean and max recovery times after loss streaks.

    Recovery time = draws from end of loss streak until next win.

    Returns:
        Tuple of (mean_recovery_draws, max_recovery_draws)
    """
    recovery_times: list[int] = []
    current_streak = 0
    waiting_for_recovery = False
    recovery_count = 0

    for hits in hits_list:
        is_win = is_payout(keno_type, hits)

        if not is_win:
            current_streak += 1
        else:
            if current_streak >= 3:  # Only track recovery after significant streaks
                recovery_times.append(recovery_count)
            current_streak = 0
            waiting_for_recovery = False
            recovery_count = 0

        if current_streak > 0:
            waiting_for_recovery = True

        if waiting_for_recovery and current_streak == 0:
            recovery_count += 1

    if not recovery_times:
        return 0.0, 0

    return round(float(np.mean(recovery_times)), 2), max(recovery_times)


def analyze_ticket(
    draws: list[DrawResult],
    ticket: list[int],
    keno_type: int,
) -> LossStreakMetrics:
    """Analyze loss streaks for a specific ticket."""
    sorted_draws = sorted(draws, key=lambda d: d.date)
    ticket_set = set(ticket)

    # Compute hits per draw
    hits_list = []
    for draw in sorted_draws:
        draw_set = set(draw.numbers)
        hits = len(ticket_set & draw_set)
        hits_list.append(hits)

    # Compute streak metrics
    streaks, max_loss_streak = compute_loss_streaks(hits_list, keno_type)
    total_losses = sum(1 for h in hits_list if not is_payout(keno_type, h))
    mean_loss_streak = float(np.mean(streaks)) if streaks else 0.0

    # Compute drawdown
    max_drawdown_pct, max_drawdown_draws = compute_drawdown(hits_list, keno_type)

    # Compute recovery times
    mean_recovery, max_recovery = compute_recovery_times(hits_list, keno_type)

    # Win rate
    wins = sum(1 for h in hits_list if is_payout(keno_type, h))
    win_rate = wins / len(hits_list) if hits_list else 0.0

    return LossStreakMetrics(
        keno_type=keno_type,
        n_draws=len(hits_list),
        ticket=list(ticket),
        total_losses=total_losses,
        max_loss_streak=max_loss_streak,
        mean_loss_streak=round(mean_loss_streak, 2),
        loss_streak_count=len(streaks),
        max_drawdown_pct=max_drawdown_pct,
        max_drawdown_draws=max_drawdown_draws,
        mean_recovery_draws=mean_recovery,
        max_recovery_draws=max_recovery,
        win_rate=round(win_rate, 4),
    )


def run_null_model(
    draws: list[DrawResult],
    keno_type: int,
    n_seeds: int = 100,
) -> tuple[float, float, float]:
    """Run random ticket null model to get expected max_loss_streak distribution.

    Returns:
        Tuple of (mean, std, percentile_95) for max_loss_streak
    """
    sorted_draws = sorted(draws, key=lambda d: d.date)
    max_streaks: list[int] = []

    for seed in range(n_seeds):
        random.seed(seed)
        ticket = random.sample(range(1, 71), keno_type)
        ticket_set = set(ticket)

        hits_list = []
        for draw in sorted_draws:
            draw_set = set(draw.numbers)
            hits = len(ticket_set & draw_set)
            hits_list.append(hits)

        _, max_streak = compute_loss_streaks(hits_list, keno_type)
        max_streaks.append(max_streak)

    arr = np.array(max_streaks)
    return float(np.mean(arr)), float(np.std(arr)), float(np.percentile(arr, 95))


def get_best_ticket(keno_type: int) -> list[int]:
    """Get the best known ticket for a keno type from SYSTEM_STATUS."""
    # Based on SYSTEM_STATUS.json pair_based_tickets
    tickets = {
        2: [9, 50],
        6: [3, 24, 40, 49, 51, 64],
        8: [2, 3, 20, 24, 36, 49, 51, 64],
        10: [2, 3, 9, 24, 33, 36, 49, 50, 51, 64],
    }
    if keno_type in tickets:
        return tickets[keno_type]

    # Fallback: generate from high-frequency pairs
    base = [9, 50, 20, 36, 32, 64, 33, 49, 24, 40]
    return base[:keno_type]


def analyze_loss_streaks(
    draws: list[DrawResult],
    keno_types: list[int],
    n_null_seeds: int = 100,
) -> LossStreakAnalysisResult:
    """Full loss streak analysis for all requested keno types."""
    per_type_metrics: list[LossStreakMetrics] = []
    null_comparisons: list[NullModelComparison] = []

    for keno_type in keno_types:
        ticket = get_best_ticket(keno_type)
        metrics = analyze_ticket(draws, ticket, keno_type)
        per_type_metrics.append(metrics)

        # Run null model comparison
        null_mean, null_std, null_p95 = run_null_model(draws, keno_type, n_null_seeds)

        z_score = 0.0
        if null_std > 0:
            z_score = (metrics.max_loss_streak - null_mean) / null_std

        is_within = metrics.max_loss_streak <= null_p95

        if is_within:
            conclusion = f"max_loss_streak={metrics.max_loss_streak} within null 95th pct ({null_p95:.1f})"
        else:
            conclusion = f"max_loss_streak={metrics.max_loss_streak} EXCEEDS null 95th pct ({null_p95:.1f})"

        null_comparisons.append(
            NullModelComparison(
                keno_type=keno_type,
                observed_max_loss_streak=metrics.max_loss_streak,
                null_mean_max_loss_streak=round(null_mean, 2),
                null_std_max_loss_streak=round(null_std, 2),
                null_percentile_95=round(null_p95, 2),
                z_score=round(z_score, 2),
                is_within_null=is_within,
                conclusion=conclusion,
            )
        )

    axiom_notes = {
        "A1_house_edge": "max_drawdown_pct reflects cumulative house edge impact",
        "A7_reset_cycles": "mean_recovery_draws indicates system reset behavior after loss streaks",
    }

    return LossStreakAnalysisResult(
        generated_at=datetime.now().isoformat(),
        draws_path="",  # Will be set by caller
        n_draws=len(draws),
        keno_types=keno_types,
        per_type_metrics=per_type_metrics,
        null_model_comparison=null_comparisons,
        axiom_notes=axiom_notes,
    )


def save_analysis_json(
    result: LossStreakAnalysisResult,
    output_path: Path,
    draws_path: str,
) -> None:
    """Save analysis result to JSON."""
    payload = {
        "analysis": "loss_streak_analysis",
        "generated_at": result.generated_at,
        "draws_path": draws_path,
        "n_draws": result.n_draws,
        "keno_types": result.keno_types,
        "per_type_metrics": [asdict(m) for m in result.per_type_metrics],
        "null_model_comparison": [asdict(c) for c in result.null_model_comparison],
        "axiom_notes": result.axiom_notes,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verlust-Serien (Loss Streak) Analyse fuer KENO-Backtests"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/raw/keno/KENO_ab_2022_bereinigt.csv",
        help="Path to KENO CSV data file",
    )
    parser.add_argument(
        "--types",
        type=str,
        default="2,6,8,10",
        help="Comma-separated list of keno types to analyze",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/loss_streak_analysis.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--null-seeds",
        type=int,
        default=100,
        help="Number of random seeds for null model",
    )

    args = parser.parse_args()

    # Parse keno types
    keno_types = [int(t.strip()) for t in args.types.split(",")]

    # Load data
    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    loader = DataLoader()
    draws = loader.load(data_path, game_type=GameType.KENO)
    print(f"Loaded {len(draws)} draws from {data_path}")

    # Run analysis
    result = analyze_loss_streaks(draws, keno_types, n_null_seeds=args.null_seeds)

    # Save output
    output_path = Path(args.output)
    save_analysis_json(result, output_path, str(data_path))
    print(f"Analysis saved to {output_path}")

    # Print summary
    print("\n=== Loss Streak Analysis Summary ===")
    for m in result.per_type_metrics:
        print(f"\nTyp-{m.keno_type} (ticket={m.ticket}):")
        print(f"  max_loss_streak: {m.max_loss_streak}")
        print(f"  mean_loss_streak: {m.mean_loss_streak}")
        print(f"  max_drawdown_pct: {m.max_drawdown_pct}%")
        print(f"  win_rate: {m.win_rate:.2%}")

    print("\n=== Null Model Comparison ===")
    for c in result.null_model_comparison:
        status = "OK" if c.is_within_null else "EXCEEDS"
        print(f"Typ-{c.keno_type}: {status} | {c.conclusion}")


if __name__ == "__main__":
    main()
