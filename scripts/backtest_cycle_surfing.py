#!/usr/bin/env python3
"""STRAT-004: Cycle Surfing Backtest.

Combines regime_detection.py (HMM-based regime states) with temporal_cycles.py
(weekday/month/holiday patterns) for a periodically-adaptive KENO strategy.

Core Logic:
- Regime Detection: HMM decodes latent states, mapped to economic_state labels
- Temporal Cycles: Weekday chi2, month chi2, holiday proximity effects
- Decision: PLAY if regime is favorable AND temporal signals align; else AVOID

Train/Test Split: 2024-01-01 (as per RegimeDetectionConfig.train_split_date)

Acceptance Criteria:
- ROI_strategy > ROI_baseline
- Mann-Whitney U test p < 0.05

Usage:
    python scripts/backtest_cycle_surfing.py
    python scripts/backtest_cycle_surfing.py --data data/raw/keno/KENO_ab_2018.csv
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

try:
    from scipy import stats
except ImportError:
    stats = None

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kenobase.core.data_loader import DataLoader, DrawResult
from kenobase.analysis.regime_detection import (
    RegimeDetectionConfig,
    RegimeDetectionResult,
    detect_regimes,
)
from kenobase.analysis.temporal_cycles import (
    analyze_dimension,
    analyze_holiday_proximity,
    GERMAN_HOLIDAYS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Favorable regimes for playing (avoid COOLDOWN and CRISIS)
FAVORABLE_REGIMES = {"NORMAL", "GROWTH", "UNKNOWN"}
AVOID_REGIMES = {"COOLDOWN", "CRISIS"}

# Favorable weekdays (from HYP-011 analysis - empirically determined)
# NOTE: These should be derived from train set only
DEFAULT_FAVORABLE_WEEKDAYS = {0, 1, 2, 3, 4}  # Mon-Fri (avoid weekends by default)

# Holiday proximity window (days)
HOLIDAY_WINDOW_DAYS = 3


@dataclass
class CycleSurfingConfig:
    """Configuration for cycle surfing strategy."""

    train_split_date: datetime = field(default_factory=lambda: datetime(2024, 1, 1))
    favorable_regimes: set[str] = field(default_factory=lambda: FAVORABLE_REGIMES.copy())
    avoid_regimes: set[str] = field(default_factory=lambda: AVOID_REGIMES.copy())
    use_weekday_filter: bool = True
    use_holiday_filter: bool = True
    holiday_window_days: int = HOLIDAY_WINDOW_DAYS
    # Weekday filter: if weekday chi2 p < 0.05 in train, use top weekdays
    weekday_alpha: float = 0.05


@dataclass
class BacktestResult:
    """Result container for cycle surfing backtest."""

    n_train: int = 0
    n_test: int = 0
    n_play_decisions: int = 0
    n_avoid_decisions: int = 0
    play_rate: float = 0.0

    # ROI metrics (simulated)
    # ROI = (total_return - total_stake) / total_stake
    # For KENO: we use hit rate as proxy since actual payouts vary by type
    baseline_hit_rate: float = 0.0  # All draws
    strategy_hit_rate: float = 0.0  # Only PLAY draws

    # Statistical significance
    mann_whitney_u: float = 0.0
    mann_whitney_p: float = 1.0
    is_significant: bool = False

    # Regime breakdown
    regime_counts: dict[str, int] = field(default_factory=dict)
    regime_play_counts: dict[str, int] = field(default_factory=dict)

    # Temporal breakdown
    weekday_play_counts: dict[str, int] = field(default_factory=dict)
    holiday_avoided: int = 0

    # Summary
    verdict: str = ""
    confidence: float = 0.0


def is_near_holiday(date: datetime, window_days: int = HOLIDAY_WINDOW_DAYS) -> bool:
    """Check if date is within window_days of a German holiday."""
    for h_month, h_day in GERMAN_HOLIDAYS:
        try:
            holiday = datetime(date.year, h_month, h_day)
            if abs((date - holiday).days) <= window_days:
                return True
        except ValueError:
            continue
    return False


def compute_hit_metric(draw: DrawResult) -> float:
    """Compute a simple hit metric for a draw.

    Since we don't have actual player bets, we use a proxy:
    - Count how many "popular" numbers appeared
    - Popular = numbers 1-31 (birthday numbers)

    Higher = more hits on popular numbers = potentially more payouts needed
    Lower = fewer hits on popular = better for house (worse ROI for strategy)

    For cycle surfing, we want to play when expected hits are HIGHER.
    """
    popular_count = sum(1 for n in draw.numbers if 1 <= n <= 31)
    return popular_count / 20.0  # Normalize by 20 numbers drawn


def derive_weekday_filter_from_train(
    draws: list[DrawResult],
    config: CycleSurfingConfig,
) -> set[int]:
    """Derive favorable weekdays from train data.

    If weekday distribution is significantly non-uniform (p < alpha),
    return top 4 weekdays by frequency. Otherwise return all weekdays.
    """
    train_dates = [d.date for d in draws if d.date < config.train_split_date]

    if len(train_dates) < 100:
        logger.warning("Insufficient train data for weekday analysis, using all weekdays")
        return set(range(7))

    result = analyze_dimension(train_dates, "weekday", config.weekday_alpha)

    if result.is_significant:
        # Sort weekdays by observed count, take top 4
        weekday_counts = list(zip(range(7), result.observed_counts))
        weekday_counts.sort(key=lambda x: x[1], reverse=True)
        favorable = {wc[0] for wc in weekday_counts[:4]}
        logger.info(f"Weekday filter derived from train: {favorable} (p={result.p_value:.4f})")
        return favorable
    else:
        logger.info(f"No significant weekday bias (p={result.p_value:.4f}), using all weekdays")
        return set(range(7))


def run_backtest(
    draws: list[DrawResult],
    regime_result: RegimeDetectionResult,
    config: Optional[CycleSurfingConfig] = None,
) -> BacktestResult:
    """Run cycle surfing backtest.

    Args:
        draws: List of DrawResult (sorted by date)
        regime_result: Result from detect_regimes()
        config: Optional configuration

    Returns:
        BacktestResult with metrics
    """
    cfg = config or CycleSurfingConfig()
    result = BacktestResult()

    if not draws or not regime_result.dates:
        result.verdict = "INSUFFICIENT_DATA"
        return result

    # Build date -> regime label mapping
    date_to_regime = dict(zip(regime_result.dates, regime_result.state_labels))

    # Derive weekday filter from train data
    if cfg.use_weekday_filter:
        favorable_weekdays = derive_weekday_filter_from_train(draws, cfg)
    else:
        favorable_weekdays = set(range(7))

    # Separate train/test
    train_draws = [d for d in draws if d.date < cfg.train_split_date]
    test_draws = [d for d in draws if d.date >= cfg.train_split_date]

    result.n_train = len(train_draws)
    result.n_test = len(test_draws)

    if result.n_test == 0:
        result.verdict = "NO_TEST_DATA"
        return result

    # Run backtest on test set
    play_decisions = []
    avoid_decisions = []
    baseline_metrics = []

    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_play_counts = {name: 0 for name in weekday_names}
    regime_counts: dict[str, int] = {}
    regime_play_counts: dict[str, int] = {}
    holiday_avoided = 0

    for draw in test_draws:
        regime = date_to_regime.get(draw.date, "UNKNOWN")
        weekday = draw.date.weekday()
        near_holiday = is_near_holiday(draw.date, cfg.holiday_window_days)

        # Track regime counts
        regime_counts[regime] = regime_counts.get(regime, 0) + 1

        # Decision logic: PLAY if conditions met, else AVOID
        should_play = True

        # Check regime
        if regime in cfg.avoid_regimes:
            should_play = False

        # Check weekday
        if cfg.use_weekday_filter and weekday not in favorable_weekdays:
            should_play = False

        # Check holiday
        if cfg.use_holiday_filter and near_holiday:
            should_play = False
            holiday_avoided += 1

        # Compute hit metric
        metric = compute_hit_metric(draw)
        baseline_metrics.append(metric)

        if should_play:
            play_decisions.append((draw, metric))
            regime_play_counts[regime] = regime_play_counts.get(regime, 0) + 1
            weekday_play_counts[weekday_names[weekday]] += 1
        else:
            avoid_decisions.append((draw, metric))

    result.n_play_decisions = len(play_decisions)
    result.n_avoid_decisions = len(avoid_decisions)
    result.play_rate = result.n_play_decisions / result.n_test if result.n_test > 0 else 0.0
    result.regime_counts = regime_counts
    result.regime_play_counts = regime_play_counts
    result.weekday_play_counts = weekday_play_counts
    result.holiday_avoided = holiday_avoided

    # Compute metrics
    if baseline_metrics:
        result.baseline_hit_rate = float(np.mean(baseline_metrics))

    if play_decisions:
        play_metrics = [m for _, m in play_decisions]
        result.strategy_hit_rate = float(np.mean(play_metrics))

        # Mann-Whitney U test: play_metrics vs avoid_metrics
        if stats is not None and len(avoid_decisions) > 0:
            avoid_metrics = [m for _, m in avoid_decisions]
            # Test if play_metrics > avoid_metrics (one-sided)
            try:
                stat, p_value = stats.mannwhitneyu(
                    play_metrics, avoid_metrics, alternative="greater"
                )
                result.mann_whitney_u = float(stat)
                result.mann_whitney_p = float(p_value)
                result.is_significant = p_value < 0.05
            except Exception as e:
                logger.warning(f"Mann-Whitney U test failed: {e}")
    else:
        result.strategy_hit_rate = 0.0

    # Verdict
    roi_improvement = result.strategy_hit_rate - result.baseline_hit_rate
    if result.n_play_decisions < 10:
        result.verdict = "INSUFFICIENT_PLAY_DECISIONS"
        result.confidence = 0.0
    elif result.is_significant and roi_improvement > 0:
        result.verdict = "STRATEGY_OUTPERFORMS"
        result.confidence = 1.0 - result.mann_whitney_p
    elif roi_improvement > 0:
        result.verdict = "POSITIVE_BUT_NOT_SIGNIFICANT"
        result.confidence = 0.5
    else:
        result.verdict = "NO_IMPROVEMENT"
        result.confidence = 0.0

    return result


def main() -> int:
    """Run STRAT-004 cycle surfing backtest."""
    parser = argparse.ArgumentParser(
        description="STRAT-004: Cycle Surfing Backtest"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="data/raw/keno/KENO_ab_2018.csv",
        help="Path to KENO data CSV",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/cycle_surfing_backtest.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--train-split",
        type=str,
        default="2024-01-01",
        help="Train/Test split date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--no-weekday-filter",
        action="store_true",
        help="Disable weekday filtering",
    )
    parser.add_argument(
        "--no-holiday-filter",
        action="store_true",
        help="Disable holiday proximity filtering",
    )

    args = parser.parse_args()

    # Load data
    data_path = Path(args.data)
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        return 1

    logger.info(f"Loading KENO data from {data_path}")
    loader = DataLoader()
    draws = loader.load(data_path)

    if not draws:
        logger.error("No draws loaded from data file")
        return 1

    # Sort draws by date
    draws = sorted(draws, key=lambda d: d.date)
    logger.info(f"Loaded {len(draws)} KENO draws")

    # Parse train split date
    try:
        train_split = datetime.strptime(args.train_split, "%Y-%m-%d")
    except ValueError:
        logger.error(f"Invalid train split date format: {args.train_split}")
        return 1

    # Run regime detection
    logger.info("Running regime detection (HMM)...")
    regime_config = RegimeDetectionConfig(train_split_date=train_split)
    regime_result = detect_regimes(draws, regime_config)
    logger.info(
        f"Regime detection: train={regime_result.train_size}, "
        f"accuracy={regime_result.accuracy:.2%}, mapping={regime_result.mapping}"
    )

    # Configure backtest
    backtest_config = CycleSurfingConfig(
        train_split_date=train_split,
        use_weekday_filter=not args.no_weekday_filter,
        use_holiday_filter=not args.no_holiday_filter,
    )

    # Run backtest
    logger.info("Running cycle surfing backtest...")
    result = run_backtest(draws, regime_result, backtest_config)

    # Prepare output (ensure all values are JSON-serializable)
    output = {
        "strategy_id": "STRAT-004",
        "strategy_name": "Cycle Surfing",
        "description": "Combines HMM regime detection with temporal cycle analysis",
        "timestamp": datetime.now().isoformat(),
        "data_source": str(data_path),
        "config": {
            "train_split_date": train_split.isoformat(),
            "use_weekday_filter": bool(backtest_config.use_weekday_filter),
            "use_holiday_filter": bool(backtest_config.use_holiday_filter),
            "holiday_window_days": int(backtest_config.holiday_window_days),
            "favorable_regimes": list(backtest_config.favorable_regimes),
            "avoid_regimes": list(backtest_config.avoid_regimes),
        },
        "regime_detection": {
            "train_size": int(regime_result.train_size),
            "accuracy": float(regime_result.accuracy),
            "boundary_f1": float(regime_result.boundary_f1),
            "mapping": {int(k): str(v) for k, v in regime_result.mapping.items()},
        },
        "backtest_results": {
            "n_train": int(result.n_train),
            "n_test": int(result.n_test),
            "n_play_decisions": int(result.n_play_decisions),
            "n_avoid_decisions": int(result.n_avoid_decisions),
            "play_rate": float(result.play_rate),
            "baseline_hit_rate": float(result.baseline_hit_rate),
            "strategy_hit_rate": float(result.strategy_hit_rate),
            "hit_rate_improvement": float(result.strategy_hit_rate - result.baseline_hit_rate),
            "mann_whitney_u": float(result.mann_whitney_u),
            "mann_whitney_p": float(result.mann_whitney_p),
            "is_significant": bool(result.is_significant),
            "regime_counts": {str(k): int(v) for k, v in result.regime_counts.items()},
            "regime_play_counts": {str(k): int(v) for k, v in result.regime_play_counts.items()},
            "weekday_play_counts": {str(k): int(v) for k, v in result.weekday_play_counts.items()},
            "holiday_avoided": int(result.holiday_avoided),
        },
        "verdict": str(result.verdict),
        "confidence": float(result.confidence),
        "acceptance_criteria": {
            "roi_improvement": bool(result.strategy_hit_rate > result.baseline_hit_rate),
            "statistical_significance": bool(result.is_significant),
            "passed": bool(result.verdict == "STRATEGY_OUTPERFORMS"),
        },
    }

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Results written to {output_path}")

    # Print summary
    print("\n" + "=" * 70)
    print("STRAT-004: CYCLE SURFING BACKTEST - SUMMARY")
    print("=" * 70)
    print(f"Data: {data_path.name}")
    print(f"Train/Test Split: {train_split.date()}")
    print(f"Train draws: {result.n_train}, Test draws: {result.n_test}")
    print()

    print("REGIME DETECTION:")
    print(f"  HMM Accuracy: {regime_result.accuracy:.2%}")
    print(f"  State Mapping: {regime_result.mapping}")
    print(f"  Regime Counts (test): {result.regime_counts}")
    print()

    print("STRATEGY DECISIONS:")
    print(f"  PLAY decisions: {result.n_play_decisions} ({result.play_rate:.1%})")
    print(f"  AVOID decisions: {result.n_avoid_decisions}")
    print(f"  Holiday avoided: {result.holiday_avoided}")
    print(f"  Weekday play distribution: {result.weekday_play_counts}")
    print()

    print("PERFORMANCE:")
    print(f"  Baseline hit rate: {result.baseline_hit_rate:.4f}")
    print(f"  Strategy hit rate: {result.strategy_hit_rate:.4f}")
    improvement = result.strategy_hit_rate - result.baseline_hit_rate
    print(f"  Improvement: {improvement:+.4f}")
    print()

    print("STATISTICAL TEST:")
    print(f"  Mann-Whitney U: {result.mann_whitney_u:.2f}")
    print(f"  p-value: {result.mann_whitney_p:.4f}")
    print(f"  Significant (p < 0.05): {'YES' if result.is_significant else 'NO'}")
    print()

    print("=" * 70)
    print(f"VERDICT: {result.verdict}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Acceptance Criteria PASSED: {result.verdict == 'STRATEGY_OUTPERFORMS'}")
    print("=" * 70)

    return 0 if result.verdict == "STRATEGY_OUTPERFORMS" else 1


if __name__ == "__main__":
    sys.exit(main())
