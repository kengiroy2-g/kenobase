"""
Null Models for Statistical Testing in Kenobase V2.0

This module implements permutation-based null models for robust statistical testing
of axiom predictions. Supports schedule-preserving and block permutation methods.

Implements:
- schedule_permutation(): Preserves weekday structure of draws
- block_permutation(): Preserves weekly blocks (temporal autocorrelation)
- NullModelRunner: Unified interface for all null model types
- FDR correction via Benjamini-Hochberg procedure

Used by predictions: P1.3, P4.3, P6.3, P7.3

Author: EXECUTOR (TASK NULL-001)
Date: 2025-12-30
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional, Sequence, TypeVar

import numpy as np
from numpy.random import Generator, default_rng

# Import NullModelType from axioms to maintain consistency
from kenobase.core.axioms import NullModelType


# Type variable for generic data
T = TypeVar("T")


@dataclass
class PermutationResult:
    """Result of a single permutation test."""

    observed_statistic: float
    null_distribution: np.ndarray
    p_value: float
    n_permutations: int
    null_model_type: NullModelType
    direction: str = "two-sided"  # "less", "greater", "two-sided"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "observed_statistic": float(self.observed_statistic),
            "null_mean": float(np.mean(self.null_distribution)),
            "null_std": float(np.std(self.null_distribution)),
            "null_median": float(np.median(self.null_distribution)),
            "null_percentile_5": float(np.percentile(self.null_distribution, 5)),
            "null_percentile_95": float(np.percentile(self.null_distribution, 95)),
            "p_value": float(self.p_value),
            "n_permutations": self.n_permutations,
            "null_model_type": self.null_model_type.value,
            "direction": self.direction,
        }


@dataclass
class FDRResult:
    """Result of FDR correction across multiple tests."""

    original_p_values: list[float]
    q_values: list[float]  # FDR-adjusted p-values
    significant_indices: list[int]  # Indices of tests significant at alpha
    alpha: float
    n_tests: int
    n_significant: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "original_p_values": self.original_p_values,
            "q_values": self.q_values,
            "significant_indices": self.significant_indices,
            "alpha": self.alpha,
            "n_tests": self.n_tests,
            "n_significant": self.n_significant,
        }


@dataclass
class NullModelTestResult:
    """Complete result of a null model test with FDR correction."""

    prediction_id: str
    permutation_result: PermutationResult
    fdr_result: Optional[FDRResult] = None
    is_significant: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "prediction_id": self.prediction_id,
            "permutation": self.permutation_result.to_dict(),
            "is_significant": self.is_significant,
        }
        if self.fdr_result:
            result["fdr"] = self.fdr_result.to_dict()
        return result


def schedule_permutation(
    data: np.ndarray,
    dates: Sequence[datetime],
    rng: Optional[Generator] = None,
) -> np.ndarray:
    """
    Permute data while preserving the weekday schedule structure.

    This ensures that draws remain on the same weekdays as the original data,
    preserving any day-of-week effects while shuffling the actual values.

    Args:
        data: Array of values to permute (e.g., draw results, metrics)
        dates: Sequence of datetime objects corresponding to each data point
        rng: Optional numpy random generator for reproducibility

    Returns:
        Permuted array with same weekday distribution as original

    Example:
        If original data has Mon draws at indices [0,3,6] and Wed at [1,4,7],
        the permutation will only shuffle within each weekday group.
    """
    if rng is None:
        rng = default_rng()

    data = np.asarray(data)
    if len(data) != len(dates):
        raise ValueError(f"Data length ({len(data)}) != dates length ({len(dates)})")

    # Group indices by weekday (0=Mon, 6=Sun)
    weekday_groups: dict[int, list[int]] = {i: [] for i in range(7)}
    for idx, dt in enumerate(dates):
        weekday_groups[dt.weekday()].append(idx)

    # Permute within each weekday group
    permuted = data.copy()
    for weekday, indices in weekday_groups.items():
        if len(indices) > 1:
            group_values = data[indices].copy()
            rng.shuffle(group_values)
            permuted[indices] = group_values

    return permuted


def block_permutation(
    data: np.ndarray,
    block_size: int = 7,
    rng: Optional[Generator] = None,
) -> np.ndarray:
    """
    Permute data by shuffling entire blocks while preserving within-block structure.

    This preserves weekly autocorrelation patterns by keeping weekly blocks
    intact but shuffling their order.

    Args:
        data: Array of values to permute
        block_size: Size of each block (default 7 for weekly blocks)
        rng: Optional numpy random generator for reproducibility

    Returns:
        Permuted array with blocks shuffled but internal structure preserved

    Example:
        For block_size=7, weeks are shuffled but the pattern within
        each week (Mon-Sun) remains intact.
    """
    if rng is None:
        rng = default_rng()

    data = np.asarray(data)
    n = len(data)
    n_complete_blocks = n // block_size
    remainder = n % block_size

    # Split into complete blocks
    blocks = [
        data[i * block_size : (i + 1) * block_size].copy()
        for i in range(n_complete_blocks)
    ]

    # Handle remainder (incomplete last block)
    if remainder > 0:
        remainder_data = data[n_complete_blocks * block_size :].copy()
    else:
        remainder_data = None

    # Shuffle blocks
    block_order = np.arange(n_complete_blocks)
    rng.shuffle(block_order)
    shuffled_blocks = [blocks[i] for i in block_order]

    # Reassemble
    if shuffled_blocks:
        permuted = np.concatenate(shuffled_blocks)
    else:
        permuted = np.array([])

    # Append remainder (not shuffled - it stays at end)
    if remainder_data is not None:
        permuted = np.concatenate([permuted, remainder_data])

    return permuted


def iid_permutation(
    data: np.ndarray,
    rng: Optional[Generator] = None,
) -> np.ndarray:
    """
    Simple IID permutation (complete shuffle).

    Args:
        data: Array of values to permute
        rng: Optional numpy random generator for reproducibility

    Returns:
        Randomly shuffled array
    """
    if rng is None:
        rng = default_rng()

    permuted = np.asarray(data).copy()
    rng.shuffle(permuted)
    return permuted


def calculate_empirical_p_value(
    observed: float,
    null_distribution: np.ndarray,
    direction: str = "two-sided",
) -> float:
    """
    Calculate empirical p-value from null distribution.

    Args:
        observed: Observed test statistic
        null_distribution: Array of null distribution values
        direction: "less", "greater", or "two-sided"

    Returns:
        Empirical p-value
    """
    n = len(null_distribution)

    if direction == "less":
        # P(X <= observed) under null
        p_value = (np.sum(null_distribution <= observed) + 1) / (n + 1)
    elif direction == "greater":
        # P(X >= observed) under null
        p_value = (np.sum(null_distribution >= observed) + 1) / (n + 1)
    else:  # two-sided
        # P(|X| >= |observed|) under null
        abs_obs = abs(observed - np.mean(null_distribution))
        abs_null = np.abs(null_distribution - np.mean(null_distribution))
        p_value = (np.sum(abs_null >= abs_obs) + 1) / (n + 1)

    return float(p_value)


def benjamini_hochberg_fdr(
    p_values: Sequence[float],
    alpha: float = 0.05,
) -> FDRResult:
    """
    Apply Benjamini-Hochberg FDR correction to multiple p-values.

    Args:
        p_values: List of p-values from multiple tests
        alpha: Significance level (default 0.05)

    Returns:
        FDRResult with q-values and significant indices
    """
    p_values = np.asarray(p_values)
    n = len(p_values)

    if n == 0:
        return FDRResult(
            original_p_values=[],
            q_values=[],
            significant_indices=[],
            alpha=alpha,
            n_tests=0,
            n_significant=0,
        )

    # Sort p-values and keep track of original indices
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    # Calculate BH critical values
    # BH threshold: p_i <= (i/n) * alpha
    ranks = np.arange(1, n + 1)
    bh_thresholds = (ranks / n) * alpha

    # Find largest i where p_i <= threshold
    significant_mask = sorted_p <= bh_thresholds
    if np.any(significant_mask):
        max_significant_rank = np.max(np.where(significant_mask)[0]) + 1
    else:
        max_significant_rank = 0

    # Calculate q-values (adjusted p-values)
    q_values = np.zeros(n)
    q_values[sorted_indices[-1]] = sorted_p[-1]  # Last p-value stays same

    for i in range(n - 2, -1, -1):
        q_values[sorted_indices[i]] = min(
            sorted_p[i] * n / (i + 1),
            q_values[sorted_indices[i + 1]]
        )

    # Determine significant indices
    significant_indices = [
        int(sorted_indices[i]) for i in range(max_significant_rank)
    ]

    return FDRResult(
        original_p_values=[float(p) for p in p_values],
        q_values=[float(q) for q in q_values],
        significant_indices=significant_indices,
        alpha=alpha,
        n_tests=n,
        n_significant=len(significant_indices),
    )


class NullModelRunner:
    """
    Unified runner for null model permutation tests.

    Integrates with NullModelType enum from axioms.py and provides
    a consistent interface for running permutation tests.

    Example:
        runner = NullModelRunner(n_permutations=1000, seed=42)
        result = runner.run_test(
            data=draw_values,
            statistic_fn=lambda x: np.mean(x),
            null_model_type=NullModelType.BLOCK_PERMUTATION,
            dates=draw_dates,
            direction="greater"
        )
    """

    def __init__(
        self,
        n_permutations: int = 1000,
        seed: Optional[int] = None,
    ):
        """
        Initialize the null model runner.

        Args:
            n_permutations: Number of permutations to run (default 1000)
            seed: Random seed for reproducibility
        """
        self.n_permutations = n_permutations
        self.rng = default_rng(seed)

    def run_test(
        self,
        data: np.ndarray,
        statistic_fn: Callable[[np.ndarray], float],
        null_model_type: NullModelType,
        dates: Optional[Sequence[datetime]] = None,
        block_size: int = 7,
        direction: str = "two-sided",
    ) -> PermutationResult:
        """
        Run a permutation test using the specified null model.

        Args:
            data: Input data array
            statistic_fn: Function that computes test statistic from data
            null_model_type: Type of null model to use
            dates: Required for SCHEDULE_PRESERVING, optional otherwise
            block_size: Block size for BLOCK_PERMUTATION (default 7)
            direction: "less", "greater", or "two-sided"

        Returns:
            PermutationResult with observed statistic, null distribution, and p-value

        Raises:
            ValueError: If dates not provided for SCHEDULE_PRESERVING
        """
        data = np.asarray(data)

        # Calculate observed statistic
        observed = statistic_fn(data)

        # Select permutation function
        if null_model_type == NullModelType.SCHEDULE_PRESERVING:
            if dates is None:
                raise ValueError(
                    "dates parameter required for SCHEDULE_PRESERVING null model"
                )
            permute_fn = lambda d: schedule_permutation(d, dates, self.rng)
        elif null_model_type == NullModelType.BLOCK_PERMUTATION:
            permute_fn = lambda d: block_permutation(d, block_size, self.rng)
        elif null_model_type == NullModelType.PERMUTATION:
            permute_fn = lambda d: iid_permutation(d, self.rng)
        elif null_model_type == NullModelType.IID:
            permute_fn = lambda d: iid_permutation(d, self.rng)
        else:
            # For other null model types, fall back to IID permutation
            permute_fn = lambda d: iid_permutation(d, self.rng)

        # Generate null distribution
        null_distribution = np.zeros(self.n_permutations)
        for i in range(self.n_permutations):
            permuted = permute_fn(data)
            null_distribution[i] = statistic_fn(permuted)

        # Calculate p-value
        p_value = calculate_empirical_p_value(observed, null_distribution, direction)

        return PermutationResult(
            observed_statistic=observed,
            null_distribution=null_distribution,
            p_value=p_value,
            n_permutations=self.n_permutations,
            null_model_type=null_model_type,
            direction=direction,
        )

    def run_multiple_tests(
        self,
        tests: list[dict],
        alpha: float = 0.05,
    ) -> tuple[list[PermutationResult], FDRResult]:
        """
        Run multiple tests and apply FDR correction.

        Args:
            tests: List of test configurations, each a dict with:
                - data: np.ndarray
                - statistic_fn: Callable
                - null_model_type: NullModelType
                - dates: Optional[Sequence[datetime]]
                - block_size: int (optional, default 7)
                - direction: str (optional, default "two-sided")
            alpha: Significance level for FDR correction

        Returns:
            Tuple of (list of PermutationResults, FDRResult)
        """
        results = []
        for test in tests:
            result = self.run_test(
                data=test["data"],
                statistic_fn=test["statistic_fn"],
                null_model_type=test["null_model_type"],
                dates=test.get("dates"),
                block_size=test.get("block_size", 7),
                direction=test.get("direction", "two-sided"),
            )
            results.append(result)

        # Apply FDR correction
        p_values = [r.p_value for r in results]
        fdr_result = benjamini_hochberg_fdr(p_values, alpha)

        return results, fdr_result


def run_axiom_prediction_test(
    prediction_id: str,
    data: np.ndarray,
    statistic_fn: Callable[[np.ndarray], float],
    null_model_type: NullModelType,
    dates: Optional[Sequence[datetime]] = None,
    block_size: int = 7,
    direction: str = "two-sided",
    n_permutations: int = 1000,
    seed: Optional[int] = None,
) -> NullModelTestResult:
    """
    Convenience function to run a null model test for a specific axiom prediction.

    Args:
        prediction_id: Prediction identifier (e.g., "P1.3", "P4.3")
        data: Input data array
        statistic_fn: Function that computes test statistic
        null_model_type: Type of null model (from axioms.py)
        dates: Required for SCHEDULE_PRESERVING
        block_size: Block size for BLOCK_PERMUTATION
        direction: "less", "greater", or "two-sided"
        n_permutations: Number of permutations
        seed: Random seed

    Returns:
        NullModelTestResult with all test information
    """
    runner = NullModelRunner(n_permutations=n_permutations, seed=seed)

    perm_result = runner.run_test(
        data=data,
        statistic_fn=statistic_fn,
        null_model_type=null_model_type,
        dates=dates,
        block_size=block_size,
        direction=direction,
    )

    # Single test - no FDR needed, just check p < 0.05
    is_significant = perm_result.p_value < 0.05

    return NullModelTestResult(
        prediction_id=prediction_id,
        permutation_result=perm_result,
        fdr_result=None,
        is_significant=is_significant,
    )
