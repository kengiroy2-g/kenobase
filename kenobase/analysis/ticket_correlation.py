"""Ticket Correlation Analysis for Portfolio Diversification.

This module analyzes correlations between different ticket types (Typ-2, Typ-6, Typ-8, Typ-10)
across three dimensions:
- Zahlen-Overlap (Jaccard similarity)
- ROI-Synchronization (Spearman correlation of ROI time series)
- Gewinn-Timing (win co-occurrence ratio)

The goal is NOT to find profitable tickets (all have negative ROI: -43% to -67%),
but to identify anti-correlated tickets for portfolio diversification.

Usage:
    from kenobase.analysis.ticket_correlation import (
        analyze_ticket_correlation,
        calculate_overlap,
        calculate_roi_sync,
    )

    result = analyze_ticket_correlation(tickets, backtest_results)

Author: EXECUTOR (TASK_034)
Date: 2025-12-30
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations
from typing import Optional, Sequence

import numpy as np
from scipy import stats

from kenobase.analysis.null_models import benjamini_hochberg_fdr, FDRResult

logger = logging.getLogger(__name__)


# --- Dataclasses ---

@dataclass(frozen=True)
class TicketPair:
    """Represents a pair of tickets for correlation analysis.

    Attributes:
        ticket_a_type: Keno type of first ticket (e.g., 2, 6, 8, 10)
        ticket_b_type: Keno type of second ticket
        ticket_a_numbers: Numbers in first ticket
        ticket_b_numbers: Numbers in second ticket
    """
    ticket_a_type: int
    ticket_b_type: int
    ticket_a_numbers: tuple[int, ...]
    ticket_b_numbers: tuple[int, ...]

    def __post_init__(self) -> None:
        """Validate ticket data."""
        if not self.ticket_a_numbers:
            raise ValueError("ticket_a_numbers cannot be empty")
        if not self.ticket_b_numbers:
            raise ValueError("ticket_b_numbers cannot be empty")


@dataclass(frozen=True)
class OverlapResult:
    """Result of Zahlen-Overlap (Jaccard similarity) analysis.

    Attributes:
        jaccard_index: Jaccard similarity (intersection / union), 0-1
        overlap_count: Number of shared numbers
        union_count: Total unique numbers across both tickets
    """
    jaccard_index: float
    overlap_count: int
    union_count: int


@dataclass(frozen=True)
class SyncResult:
    """Result of ROI-Synchronization analysis.

    Attributes:
        spearman_r: Spearman correlation coefficient
        spearman_p: Spearman p-value
        n_observations: Number of paired observations
        is_significant: True if p < 0.05
    """
    spearman_r: float
    spearman_p: float
    n_observations: int
    is_significant: bool


@dataclass(frozen=True)
class TimingResult:
    """Result of Gewinn-Timing (win co-occurrence) analysis.

    Attributes:
        cooccurrence_ratio: Fraction of draws where both tickets win
        ticket_a_win_rate: Win rate of ticket A
        ticket_b_win_rate: Win rate of ticket B
        expected_cooccurrence: Expected co-occurrence under independence
        lift: Actual / Expected co-occurrence (>1 = positive correlation)
        n_draws: Total number of draws analyzed
    """
    cooccurrence_ratio: float
    ticket_a_win_rate: float
    ticket_b_win_rate: float
    expected_cooccurrence: float
    lift: float
    n_draws: int


@dataclass
class PairCorrelation:
    """Complete correlation analysis for a ticket pair.

    Attributes:
        pair: The ticket pair being analyzed
        overlap: Zahlen-Overlap result
        sync: ROI-Synchronization result (None if insufficient data)
        timing: Gewinn-Timing result (None if insufficient data)
        diversification_score: 0-1 score for portfolio diversification
            (higher = more diversified, better for portfolio)
    """
    pair: TicketPair
    overlap: OverlapResult
    sync: Optional[SyncResult] = None
    timing: Optional[TimingResult] = None
    diversification_score: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "pair": {
                "ticket_a_type": self.pair.ticket_a_type,
                "ticket_b_type": self.pair.ticket_b_type,
                "ticket_a_numbers": list(self.pair.ticket_a_numbers),
                "ticket_b_numbers": list(self.pair.ticket_b_numbers),
            },
            "overlap": {
                "jaccard_index": self.overlap.jaccard_index,
                "overlap_count": self.overlap.overlap_count,
                "union_count": self.overlap.union_count,
            },
            "diversification_score": self.diversification_score,
        }
        if self.sync is not None:
            result["sync"] = {
                "spearman_r": self.sync.spearman_r,
                "spearman_p": self.sync.spearman_p,
                "n_observations": self.sync.n_observations,
                "is_significant": self.sync.is_significant,
            }
        if self.timing is not None:
            result["timing"] = {
                "cooccurrence_ratio": self.timing.cooccurrence_ratio,
                "ticket_a_win_rate": self.timing.ticket_a_win_rate,
                "ticket_b_win_rate": self.timing.ticket_b_win_rate,
                "expected_cooccurrence": self.timing.expected_cooccurrence,
                "lift": self.timing.lift,
                "n_draws": self.timing.n_draws,
            }
        return result


@dataclass
class TicketCorrelationResult:
    """Complete result of ticket correlation analysis.

    Attributes:
        pair_correlations: List of PairCorrelation results
        fdr_result: FDR correction result (if n_tests >= 5)
        n_tickets: Number of tickets analyzed
        n_pairs: Number of pairs analyzed
        best_diversification_pair: Pair with highest diversification score
        worst_diversification_pair: Pair with lowest diversification score
        generated_at: Timestamp of analysis
    """
    pair_correlations: list[PairCorrelation]
    fdr_result: Optional[FDRResult] = None
    n_tickets: int = 0
    n_pairs: int = 0
    best_diversification_pair: Optional[tuple[int, int]] = None
    worst_diversification_pair: Optional[tuple[int, int]] = None
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "generated_at": self.generated_at,
            "n_tickets": self.n_tickets,
            "n_pairs": self.n_pairs,
            "best_diversification_pair": list(self.best_diversification_pair)
            if self.best_diversification_pair else None,
            "worst_diversification_pair": list(self.worst_diversification_pair)
            if self.worst_diversification_pair else None,
            "pair_correlations": [pc.to_dict() for pc in self.pair_correlations],
        }
        if self.fdr_result is not None:
            result["fdr"] = self.fdr_result.to_dict()
        return result


# --- Analysis Functions ---

def calculate_overlap(
    numbers_a: Sequence[int],
    numbers_b: Sequence[int],
) -> OverlapResult:
    """Calculate Jaccard similarity between two tickets.

    Jaccard index = |A ∩ B| / |A ∪ B|

    Args:
        numbers_a: Numbers in first ticket
        numbers_b: Numbers in second ticket

    Returns:
        OverlapResult with Jaccard index and counts
    """
    set_a = set(numbers_a)
    set_b = set(numbers_b)

    intersection = set_a & set_b
    union = set_a | set_b

    overlap_count = len(intersection)
    union_count = len(union)

    if union_count == 0:
        jaccard = 0.0
    else:
        jaccard = overlap_count / union_count

    return OverlapResult(
        jaccard_index=float(jaccard),
        overlap_count=overlap_count,
        union_count=union_count,
    )


def calculate_roi_sync(
    roi_a: Sequence[float],
    roi_b: Sequence[float],
    min_observations: int = 10,
) -> Optional[SyncResult]:
    """Calculate Spearman correlation of ROI time series.

    Args:
        roi_a: ROI time series for ticket A
        roi_b: ROI time series for ticket B
        min_observations: Minimum paired observations required

    Returns:
        SyncResult or None if insufficient data
    """
    # Convert to arrays and filter NaN
    arr_a = np.asarray(roi_a, dtype=float)
    arr_b = np.asarray(roi_b, dtype=float)

    if len(arr_a) != len(arr_b):
        logger.warning(
            f"ROI series length mismatch: {len(arr_a)} vs {len(arr_b)}"
        )
        min_len = min(len(arr_a), len(arr_b))
        arr_a = arr_a[:min_len]
        arr_b = arr_b[:min_len]

    # Filter out NaN pairs
    mask = ~(np.isnan(arr_a) | np.isnan(arr_b))
    arr_a = arr_a[mask]
    arr_b = arr_b[mask]

    n_obs = len(arr_a)
    if n_obs < min_observations:
        logger.debug(
            f"Insufficient observations ({n_obs} < {min_observations})"
        )
        return None

    # Check for constant arrays
    if len(set(arr_a)) == 1 or len(set(arr_b)) == 1:
        logger.debug("Constant array detected, correlation undefined")
        return SyncResult(
            spearman_r=0.0,
            spearman_p=1.0,
            n_observations=n_obs,
            is_significant=False,
        )

    # Calculate Spearman correlation
    spearman_r, spearman_p = stats.spearmanr(arr_a, arr_b)

    # Handle NaN
    if np.isnan(spearman_r):
        spearman_r, spearman_p = 0.0, 1.0

    return SyncResult(
        spearman_r=float(spearman_r),
        spearman_p=float(spearman_p),
        n_observations=n_obs,
        is_significant=spearman_p < 0.05,
    )


def calculate_timing(
    wins_a: Sequence[bool],
    wins_b: Sequence[bool],
    min_draws: int = 10,
) -> Optional[TimingResult]:
    """Calculate win co-occurrence ratio and lift.

    Args:
        wins_a: Boolean array of wins for ticket A (per draw)
        wins_b: Boolean array of wins for ticket B (per draw)
        min_draws: Minimum number of draws required

    Returns:
        TimingResult or None if insufficient data
    """
    arr_a = np.asarray(wins_a, dtype=bool)
    arr_b = np.asarray(wins_b, dtype=bool)

    if len(arr_a) != len(arr_b):
        logger.warning(
            f"Wins series length mismatch: {len(arr_a)} vs {len(arr_b)}"
        )
        min_len = min(len(arr_a), len(arr_b))
        arr_a = arr_a[:min_len]
        arr_b = arr_b[:min_len]

    n_draws = len(arr_a)
    if n_draws < min_draws:
        logger.debug(f"Insufficient draws ({n_draws} < {min_draws})")
        return None

    # Calculate rates
    win_a_rate = float(np.mean(arr_a))
    win_b_rate = float(np.mean(arr_b))

    # Co-occurrence: both win on same draw
    cooccurrence = arr_a & arr_b
    cooccurrence_ratio = float(np.mean(cooccurrence))

    # Expected under independence
    expected_cooccurrence = win_a_rate * win_b_rate

    # Lift = actual / expected
    if expected_cooccurrence > 0:
        lift = cooccurrence_ratio / expected_cooccurrence
    else:
        lift = 1.0 if cooccurrence_ratio == 0 else float("inf")

    return TimingResult(
        cooccurrence_ratio=cooccurrence_ratio,
        ticket_a_win_rate=win_a_rate,
        ticket_b_win_rate=win_b_rate,
        expected_cooccurrence=expected_cooccurrence,
        lift=float(lift),
        n_draws=n_draws,
    )


def calculate_diversification_score(
    overlap: OverlapResult,
    sync: Optional[SyncResult],
    timing: Optional[TimingResult],
    overlap_weight: float = 0.3,
    sync_weight: float = 0.4,
    timing_weight: float = 0.3,
) -> float:
    """Calculate diversification score from individual components.

    Higher score = more diversified (better for portfolio).
    Score is inverted so that low correlation = high diversification.

    Components:
    - Overlap: 1 - jaccard_index (no overlap = good)
    - Sync: 1 - abs(spearman_r) if significant, else neutral (0.5)
    - Timing: 1 - min(lift, 2)/2 (lift < 1 = good, capped at 2)

    Args:
        overlap: OverlapResult
        sync: Optional SyncResult
        timing: Optional TimingResult
        overlap_weight: Weight for overlap component (default 0.3)
        sync_weight: Weight for sync component (default 0.4)
        timing_weight: Weight for timing component (default 0.3)

    Returns:
        Diversification score 0-1 (higher = more diversified)
    """
    # Overlap component: prefer no overlap
    overlap_score = 1.0 - overlap.jaccard_index

    # Sync component: prefer low or negative correlation
    if sync is not None and sync.is_significant:
        # Negative correlation is best, positive is worst
        # Map [-1, 1] to [1, 0]
        sync_score = (1.0 - sync.spearman_r) / 2.0
    else:
        # Neutral if not significant
        sync_score = 0.5

    # Timing component: prefer lift < 1 (anti-correlated timing)
    if timing is not None:
        # Cap lift at 2 for normalization
        capped_lift = min(timing.lift, 2.0)
        timing_score = 1.0 - (capped_lift / 2.0)
    else:
        # Neutral if no timing data
        timing_score = 0.5

    # Weighted average
    total_weight = overlap_weight + sync_weight + timing_weight
    score = (
        overlap_weight * overlap_score
        + sync_weight * sync_score
        + timing_weight * timing_score
    ) / total_weight

    return float(score)


def analyze_ticket_pair(
    pair: TicketPair,
    roi_a: Optional[Sequence[float]] = None,
    roi_b: Optional[Sequence[float]] = None,
    wins_a: Optional[Sequence[bool]] = None,
    wins_b: Optional[Sequence[bool]] = None,
) -> PairCorrelation:
    """Analyze correlation between a ticket pair.

    Args:
        pair: TicketPair to analyze
        roi_a: Optional ROI time series for ticket A
        roi_b: Optional ROI time series for ticket B
        wins_a: Optional win flags for ticket A
        wins_b: Optional win flags for ticket B

    Returns:
        PairCorrelation with all analysis results
    """
    # Calculate overlap (always possible)
    overlap = calculate_overlap(pair.ticket_a_numbers, pair.ticket_b_numbers)

    # Calculate ROI sync if data available
    sync = None
    if roi_a is not None and roi_b is not None:
        sync = calculate_roi_sync(roi_a, roi_b)

    # Calculate timing if data available
    timing = None
    if wins_a is not None and wins_b is not None:
        timing = calculate_timing(wins_a, wins_b)

    # Calculate diversification score
    div_score = calculate_diversification_score(overlap, sync, timing)

    return PairCorrelation(
        pair=pair,
        overlap=overlap,
        sync=sync,
        timing=timing,
        diversification_score=div_score,
    )


def analyze_ticket_correlation(
    tickets: dict[int, tuple[int, ...]],
    backtest_results: Optional[dict[int, dict]] = None,
    apply_fdr: bool = True,
    fdr_alpha: float = 0.05,
) -> TicketCorrelationResult:
    """Analyze correlations between all ticket pairs.

    Args:
        tickets: Dict mapping keno_type -> ticket numbers
            Example: {2: (9, 50), 6: (3, 24, 40, 49, 51, 64), ...}
        backtest_results: Optional dict with backtest data per keno_type
            Expected structure:
            {
                keno_type: {
                    "roi_series": [float, ...],  # ROI per period
                    "win_flags": [bool, ...],    # Win per draw
                }
            }
        apply_fdr: If True, apply BH-FDR correction when n_tests >= 5
        fdr_alpha: Alpha level for FDR correction

    Returns:
        TicketCorrelationResult with all pair correlations
    """
    if len(tickets) < 2:
        logger.warning("Need at least 2 tickets for correlation analysis")
        return TicketCorrelationResult(
            pair_correlations=[],
            n_tickets=len(tickets),
            n_pairs=0,
        )

    pair_correlations: list[PairCorrelation] = []

    # Generate all pairs
    for type_a, type_b in combinations(sorted(tickets.keys()), 2):
        numbers_a = tickets[type_a]
        numbers_b = tickets[type_b]

        pair = TicketPair(
            ticket_a_type=type_a,
            ticket_b_type=type_b,
            ticket_a_numbers=tuple(numbers_a),
            ticket_b_numbers=tuple(numbers_b),
        )

        # Get backtest data if available
        roi_a = roi_b = wins_a = wins_b = None
        if backtest_results:
            if type_a in backtest_results:
                roi_a = backtest_results[type_a].get("roi_series")
                wins_a = backtest_results[type_a].get("win_flags")
            if type_b in backtest_results:
                roi_b = backtest_results[type_b].get("roi_series")
                wins_b = backtest_results[type_b].get("win_flags")

        correlation = analyze_ticket_pair(pair, roi_a, roi_b, wins_a, wins_b)
        pair_correlations.append(correlation)

    # Apply FDR if we have sync results and enough tests
    fdr_result = None
    if apply_fdr:
        p_values = [
            pc.sync.spearman_p
            for pc in pair_correlations
            if pc.sync is not None
        ]
        if len(p_values) >= 5:
            fdr_result = benjamini_hochberg_fdr(p_values, alpha=fdr_alpha)
            logger.info(
                f"Applied BH-FDR correction to {len(p_values)} tests, "
                f"{fdr_result.n_significant} significant at alpha={fdr_alpha}"
            )

    # Find best/worst diversification pairs
    best_pair = worst_pair = None
    if pair_correlations:
        sorted_by_div = sorted(
            pair_correlations,
            key=lambda x: x.diversification_score,
            reverse=True,
        )
        best = sorted_by_div[0]
        worst = sorted_by_div[-1]
        best_pair = (best.pair.ticket_a_type, best.pair.ticket_b_type)
        worst_pair = (worst.pair.ticket_a_type, worst.pair.ticket_b_type)

    return TicketCorrelationResult(
        pair_correlations=pair_correlations,
        fdr_result=fdr_result,
        n_tickets=len(tickets),
        n_pairs=len(pair_correlations),
        best_diversification_pair=best_pair,
        worst_diversification_pair=worst_pair,
    )


__all__ = [
    # Dataclasses
    "TicketPair",
    "OverlapResult",
    "SyncResult",
    "TimingResult",
    "PairCorrelation",
    "TicketCorrelationResult",
    # Functions
    "calculate_overlap",
    "calculate_roi_sync",
    "calculate_timing",
    "calculate_diversification_score",
    "analyze_ticket_pair",
    "analyze_ticket_correlation",
]
