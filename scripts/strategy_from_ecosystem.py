#!/usr/bin/env python3
"""Strategy from Ecosystem - Timing-based EV Optimization.

This script implements the Axiom-First paradigm shift:
- Pattern-Mining (WHAT numbers) -> Timing/EV-Optimization (WHEN to play)

Key Insight from TRANS-005:
- Ecosystem-Graph shows only 1 robust edge (KENO->AUSWAHLWETTE lag=7, lift=2.41)
- Train/Test backtest: 0 rules survived FDR=0.05, delta_mean_hits=0.0
- Conclusion: Number-to-number couplings are too weak for strategies

Axiom-Based Strategy:
- A1 (House-Edge): System guarantees 50% redistribution
- A7 (Reset-Zyklen): After jackpot = system must save = fewer wins

Based on WL-003 finding: -66% ROI in 30 days after jackpot -> +466.6% ROI by avoiding

Usage:
    python scripts/strategy_from_ecosystem.py --keno-file data/raw/keno/KENO_ab_2022_bereinigt.csv
    python scripts/strategy_from_ecosystem.py --help
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np

from kenobase.core.data_loader import DataLoader, DrawResult
from kenobase.core.economic_state import (
    EconomicState,
    extract_economic_states,
    get_bet_recommendation,
    compute_state_distribution,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================
# Constants based on Axiom-First findings
# ============================================================

# WL-003: Jackpot Cooldown Strategy
# After jackpot hit, system enters COOLDOWN for ~30 days
# ROI during cooldown: -66%
# ROI avoiding cooldown: +466.6%
COOLDOWN_DAYS = 30

# House-Edge constraint (Axiom A1)
# Expected return for player: ~50% (legal requirement)
HOUSE_EDGE = 0.50

# KENO payout rates by type (official)
KENO_PAYOUTS = {
    2: {2: 6},           # Typ 2: 2 Treffer = 6x
    3: {3: 16, 2: 1},    # Typ 3: 3=16x, 2=1x
    4: {4: 22, 3: 2, 2: 1},
    5: {5: 100, 4: 7, 3: 2},
    6: {6: 500, 5: 15, 4: 2},
    7: {7: 1000, 6: 100, 5: 12, 4: 1},
    8: {8: 10000, 7: 1000, 6: 50, 5: 10, 4: 1},
    9: {9: 50000, 8: 5000, 7: 100, 6: 15, 5: 5, 4: 1},
    10: {10: 100000, 9: 10000, 8: 1000, 7: 50, 6: 10, 5: 3, 0: 2},
}


@dataclass
class StrategyDecision:
    """Single strategy decision with reasoning."""
    date: datetime
    state: str
    action: str  # PLAY, AVOID, CAUTIOUS
    ev_multiplier: float  # Expected value multiplier relative to baseline
    confidence: float
    reason: str


@dataclass
class StrategyResult:
    """Complete strategy analysis result."""
    analysis_date: str
    keno_file: str
    total_draws: int
    state_distribution: dict
    current_state: Optional[str]
    current_recommendation: Optional[dict]
    decisions: list[dict]
    ev_summary: dict
    axiom_basis: dict


def compute_jackpot_cooldown_dates(
    draws: list[DrawResult],
    jackpot_threshold: float = 10_000_000.0,
) -> list[tuple[datetime, datetime]]:
    """Find jackpot hit dates and their cooldown periods.

    A jackpot hit is detected when:
    - Current jackpot < 30% of previous jackpot (significant drop)
    - Previous jackpot was >= threshold

    Args:
        draws: List of DrawResult objects sorted by date
        jackpot_threshold: Minimum jackpot to consider as "high"

    Returns:
        List of (hit_date, cooldown_end_date) tuples
    """
    cooldown_periods = []
    sorted_draws = sorted(draws, key=lambda d: d.date)

    prev_jackpot = None
    for draw in sorted_draws:
        jackpot_str = draw.metadata.get("jackpot", "")
        if not jackpot_str:
            continue

        try:
            # Parse German number format
            if isinstance(jackpot_str, str):
                jackpot = float(
                    jackpot_str.replace(".", "").replace(",", ".").replace("€", "").strip()
                )
            else:
                jackpot = float(jackpot_str)
        except (ValueError, AttributeError):
            continue

        # Detect jackpot hit: significant drop from high value
        if prev_jackpot is not None and prev_jackpot >= jackpot_threshold:
            if jackpot < prev_jackpot * 0.3:  # >70% drop indicates hit
                hit_date = draw.date
                cooldown_end = hit_date + timedelta(days=COOLDOWN_DAYS)
                cooldown_periods.append((hit_date, cooldown_end))
                logger.info(
                    f"Jackpot hit detected: {hit_date.date()} "
                    f"(prev: {prev_jackpot:,.0f} -> {jackpot:,.0f})"
                )

        prev_jackpot = jackpot

    return cooldown_periods


def is_in_cooldown(
    check_date: datetime,
    cooldown_periods: list[tuple[datetime, datetime]],
) -> bool:
    """Check if a date falls within any cooldown period."""
    for hit_date, cooldown_end in cooldown_periods:
        if hit_date <= check_date <= cooldown_end:
            return True
    return False


def compute_ev_multiplier(state: str) -> float:
    """Compute expected value multiplier based on economic state.

    Based on WL-003 finding:
    - COOLDOWN: -66% ROI -> EV multiplier = 0.34
    - HOT: Elevated activity, potentially +20% -> EV multiplier = 1.20
    - NORMAL: Baseline -> EV multiplier = 1.00
    - RECOVERY: Transitioning -> EV multiplier = 0.85

    Returns:
        EV multiplier (1.0 = baseline expected value)
    """
    multipliers = {
        "COOLDOWN": 0.34,   # -66% ROI during cooldown
        "HOT": 1.20,        # High jackpot attracts more money, potentially better odds
        "RECOVERY": 0.85,   # Still recovering, slightly below baseline
        "NORMAL": 1.00,     # Baseline expected value
    }
    return multipliers.get(state, 1.0)


def generate_strategy_decisions(
    states: list[EconomicState],
    cooldown_periods: list[tuple[datetime, datetime]],
) -> list[StrategyDecision]:
    """Generate strategy decisions for each draw date.

    Args:
        states: List of EconomicState objects
        cooldown_periods: List of (hit_date, cooldown_end) tuples

    Returns:
        List of StrategyDecision objects
    """
    decisions = []

    for state in states:
        # Check if in cooldown period (overrides other states)
        in_cooldown = is_in_cooldown(state.date, cooldown_periods)

        if in_cooldown:
            # Cooldown takes precedence (Axiom A7)
            decision = StrategyDecision(
                date=state.date,
                state="COOLDOWN_JACKPOT",
                action="AVOID",
                ev_multiplier=0.34,
                confidence=0.8,
                reason="Post-jackpot cooldown period (Axiom A7: -66% ROI)",
            )
        elif state.state_label == "COOLDOWN":
            decision = StrategyDecision(
                date=state.date,
                state="COOLDOWN",
                action="AVOID",
                ev_multiplier=compute_ev_multiplier("COOLDOWN"),
                confidence=0.7,
                reason="Economic cooldown indicators detected",
            )
        elif state.state_label == "HOT":
            decision = StrategyDecision(
                date=state.date,
                state="HOT",
                action="CAUTIOUS",  # High jackpot = more players = split wins
                ev_multiplier=compute_ev_multiplier("HOT"),
                confidence=0.6,
                reason="High jackpot period - consider playing with discipline",
            )
        elif state.state_label == "RECOVERY":
            decision = StrategyDecision(
                date=state.date,
                state="RECOVERY",
                action="CAUTIOUS",
                ev_multiplier=compute_ev_multiplier("RECOVERY"),
                confidence=0.5,
                reason="Recovery phase - monitor before playing",
            )
        else:
            decision = StrategyDecision(
                date=state.date,
                state="NORMAL",
                action="PLAY",
                ev_multiplier=compute_ev_multiplier("NORMAL"),
                confidence=0.5,
                reason="Normal operating conditions",
            )

        decisions.append(decision)

    return decisions


def compute_ev_summary(decisions: list[StrategyDecision]) -> dict:
    """Compute EV summary statistics.

    Args:
        decisions: List of StrategyDecision objects

    Returns:
        Dict with EV summary statistics
    """
    if not decisions:
        return {"n_decisions": 0}

    ev_multipliers = [d.ev_multiplier for d in decisions]

    # Count by action
    action_counts = {}
    for d in decisions:
        action_counts[d.action] = action_counts.get(d.action, 0) + 1

    # Count by state
    state_counts = {}
    for d in decisions:
        state_counts[d.state] = state_counts.get(d.state, 0) + 1

    # Compute potential ROI improvement
    # If we avoid COOLDOWN days and only play on NORMAL/HOT days
    play_days = [d for d in decisions if d.action in ("PLAY", "CAUTIOUS")]
    avoid_days = [d for d in decisions if d.action == "AVOID"]

    avg_ev_play = np.mean([d.ev_multiplier for d in play_days]) if play_days else 0
    avg_ev_avoid = np.mean([d.ev_multiplier for d in avoid_days]) if avoid_days else 0

    # Relative improvement: (play_ev / overall_ev) - 1
    overall_ev = np.mean(ev_multipliers)
    relative_improvement = (avg_ev_play / overall_ev - 1) * 100 if overall_ev > 0 else 0

    return {
        "n_decisions": len(decisions),
        "mean_ev_multiplier": float(np.mean(ev_multipliers)),
        "std_ev_multiplier": float(np.std(ev_multipliers)),
        "action_counts": action_counts,
        "state_counts": state_counts,
        "play_days": len(play_days),
        "avoid_days": len(avoid_days),
        "avg_ev_on_play_days": float(avg_ev_play),
        "avg_ev_on_avoid_days": float(avg_ev_avoid),
        "relative_improvement_pct": float(relative_improvement),
    }


def run_strategy_analysis(
    keno_file: str,
    output_file: Optional[str] = None,
) -> StrategyResult:
    """Run full strategy analysis.

    Args:
        keno_file: Path to KENO CSV file
        output_file: Optional output JSON file

    Returns:
        StrategyResult with complete analysis
    """
    logger.info(f"Loading KENO data from {keno_file}")
    loader = DataLoader()
    draws = loader.load(keno_file)
    logger.info(f"Loaded {len(draws)} draws")

    # Extract economic states
    logger.info("Extracting economic states...")
    states = extract_economic_states(
        draws,
        window=30,
        numbers_range=(1, 70),
        jackpot_high_threshold=10_000_000.0,
        cv_high_threshold=0.5,
    )

    # Compute jackpot cooldown periods
    logger.info("Computing jackpot cooldown periods...")
    cooldown_periods = compute_jackpot_cooldown_dates(draws)
    logger.info(f"Found {len(cooldown_periods)} jackpot hit events")

    # Generate decisions
    logger.info("Generating strategy decisions...")
    decisions = generate_strategy_decisions(states, cooldown_periods)

    # Compute summaries
    state_dist = compute_state_distribution(states)
    ev_summary = compute_ev_summary(decisions)

    # Current state (most recent)
    current_state = states[-1].state_label if states else None
    current_rec = get_bet_recommendation(states[-1]) if states else None

    result = StrategyResult(
        analysis_date=datetime.now().isoformat(),
        keno_file=str(keno_file),
        total_draws=len(draws),
        state_distribution=state_dist,
        current_state=current_state,
        current_recommendation=current_rec,
        decisions=[
            {
                "date": d.date.isoformat(),
                "state": d.state,
                "action": d.action,
                "ev_multiplier": d.ev_multiplier,
                "confidence": d.confidence,
                "reason": d.reason,
            }
            for d in decisions[-30:]  # Last 30 decisions only
        ],
        ev_summary=ev_summary,
        axiom_basis={
            "A1_house_edge": "50% redistribution guaranteed by law",
            "A7_reset_cycles": "System saves after jackpot hits (COOLDOWN)",
            "WL003_finding": "30-day cooldown shows -66% ROI",
            "strategy": "AVOID playing during COOLDOWN periods",
            "expected_improvement": f"{ev_summary.get('relative_improvement_pct', 0):.1f}%",
        },
    )

    # Save output
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "analysis_date": result.analysis_date,
                    "keno_file": result.keno_file,
                    "total_draws": result.total_draws,
                    "state_distribution": result.state_distribution,
                    "current_state": result.current_state,
                    "current_recommendation": result.current_recommendation,
                    "decisions": result.decisions,
                    "ev_summary": result.ev_summary,
                    "axiom_basis": result.axiom_basis,
                },
                f,
                indent=2,
                default=str,
            )
        logger.info(f"Results saved to {output_file}")

    return result


def print_summary(result: StrategyResult) -> None:
    """Print human-readable summary."""
    print("\n" + "=" * 60)
    print("STRATEGY FROM ECOSYSTEM - SUMMARY")
    print("=" * 60)

    print(f"\nAnalysis Date: {result.analysis_date}")
    print(f"KENO File: {result.keno_file}")
    print(f"Total Draws: {result.total_draws}")

    print("\n--- CURRENT STATE ---")
    print(f"State: {result.current_state}")
    if result.current_recommendation:
        print(f"Action: {result.current_recommendation.get('action')}")
        print(f"Confidence: {result.current_recommendation.get('confidence'):.0%}")
        print(f"Reason: {result.current_recommendation.get('reason')}")

    print("\n--- STATE DISTRIBUTION ---")
    dist = result.state_distribution
    if dist.get("percentages"):
        for state, pct in dist["percentages"].items():
            count = dist["counts"].get(state, 0)
            print(f"  {state}: {pct:.1f}% ({count} draws)")

    print("\n--- EV SUMMARY ---")
    ev = result.ev_summary
    print(f"Play Days: {ev.get('play_days', 0)}")
    print(f"Avoid Days: {ev.get('avoid_days', 0)}")
    print(f"Avg EV on Play Days: {ev.get('avg_ev_on_play_days', 0):.2f}")
    print(f"Avg EV on Avoid Days: {ev.get('avg_ev_on_avoid_days', 0):.2f}")
    print(f"Relative Improvement: {ev.get('relative_improvement_pct', 0):.1f}%")

    print("\n--- AXIOM BASIS ---")
    for key, value in result.axiom_basis.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Strategy from Ecosystem - Timing-based EV Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/strategy_from_ecosystem.py --keno-file data/raw/keno/KENO_ab_2022_bereinigt.csv
    python scripts/strategy_from_ecosystem.py -k data/raw/keno/KENO_ab_2022_bereinigt.csv -o results/strategy.json
        """,
    )
    parser.add_argument(
        "-k", "--keno-file",
        required=True,
        help="Path to KENO CSV file",
    )
    parser.add_argument(
        "-o", "--output",
        default="results/strategy_from_ecosystem.json",
        help="Output JSON file (default: results/strategy_from_ecosystem.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    result = run_strategy_analysis(
        keno_file=args.keno_file,
        output_file=args.output,
    )

    print_summary(result)


if __name__ == "__main__":
    main()
