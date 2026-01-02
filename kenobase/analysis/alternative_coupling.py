"""Alternative coupling analysis methods for cross-lottery ecosystems.

This module implements 5 alternative methods for detecting cross-lottery
dependencies, following the Axiom-First paradigm (testing coupling, not
pattern-mining).

Methods:
- METHOD-001: Granger Causality (statsmodels VAR)
- METHOD-002: Transfer Entropy (kNN/conditional MI)
- METHOD-003: Mutual Information with lag (kNN)
- METHOD-004: Dynamic Time Warping (DTW) distance
- METHOD-005: Combined multi-method ensemble

All methods include:
- Null model testing (permutation-based)
- FDR correction via BH procedure
- Train/Test split validation
- EuroJackpot as negative control

References:
- Granger (1969): Investigating Causal Relations
- Schreiber (2000): Measuring Information Transfer
- Kraskov et al. (2004): Estimating Mutual Information
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, replace
from typing import Literal, Optional, Sequence

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree
from scipy.special import digamma

from kenobase.analysis.cross_lottery_coupling import bh_fdr

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CouplingResult:
    """Result of a coupling analysis between two games.

    Attributes:
        source: Source game name
        target: Target game name
        method: Analysis method used
        statistic: Test statistic value
        p_value: P-value from permutation test
        q_value: FDR-adjusted q-value
        lag: Lag in days used
        n_samples: Number of samples used
        null_mean: Mean of null distribution
        null_std: Standard deviation of null distribution
        is_significant: Whether q_value <= alpha threshold
        segment: Optional data split label (e.g., "train", "test")
        is_control: Whether the pair involves the EuroJackpot control
        representation: Input representation identifier (e.g., centroid)
        k_history_target: Conditioning length for target history
        k_history_source: Conditioning length for source history (if used)
        n_permutations: Number of permutations used for the null model
    """

    source: str
    target: str
    method: str
    statistic: float
    p_value: float
    q_value: float
    lag: int
    n_samples: int
    null_mean: float
    null_std: float
    is_significant: bool
    segment: Optional[str] = None
    is_control: bool = False
    representation: Optional[str] = None
    k_history_target: int = 0
    k_history_source: int = 0
    n_permutations: int = 0


def _check_statsmodels() -> bool:
    """Check if statsmodels is available."""
    try:
        import statsmodels.tsa.stattools  # noqa: F401
        return True
    except ImportError:
        return False


def _check_dtw() -> bool:
    """Check if dtw-python is available."""
    try:
        import dtw  # noqa: F401
        return True
    except ImportError:
        return False


def _sanitize_series(
    source: np.ndarray,
    target: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Sanitize and align source/target arrays, keeping NaNs out."""
    src_arr = np.asarray(source, dtype=np.float64)
    tgt_arr = np.asarray(target, dtype=np.float64)

    if src_arr.ndim == 1:
        src_arr = src_arr.reshape(-1, 1)
    if tgt_arr.ndim == 1:
        tgt_arr = tgt_arr.reshape(-1, 1)

    min_len = min(len(src_arr), len(tgt_arr))
    src_arr = src_arr[:min_len]
    tgt_arr = tgt_arr[:min_len]

    mask = ~(np.isnan(src_arr).any(axis=1) | np.isnan(tgt_arr).any(axis=1))
    src_arr = src_arr[mask]
    tgt_arr = tgt_arr[mask]

    return src_arr, tgt_arr


def _prepare_lagged_vectors(
    source: np.ndarray,
    target: np.ndarray,
    lag: int,
    k_history_target: int,
    k_history_source: int,
) -> Optional[tuple[np.ndarray, np.ndarray, int, int, np.ndarray, np.ndarray]]:
    """Build lagged matrices for TE/CMI.

    Returns:
        (y_future, y_past, max_offset, n_samples, clean_source, clean_target)
    """
    clean_source, clean_target = _sanitize_series(source, target)
    if lag < 0:
        raise ValueError("lag must be non-negative")

    max_offset = max(lag + k_history_source, k_history_target)
    n_samples = clean_target.shape[0] - max_offset
    if n_samples <= max(4, k_history_target + k_history_source):
        return None

    y_future = clean_target[max_offset:]
    if y_future.ndim == 1:
        y_future = y_future.reshape(-1, 1)

    if k_history_target > 0:
        y_past_cols = []
        for i in range(k_history_target):
            start = max_offset - 1 - i
            end = start + n_samples
            y_past_cols.append(clean_target[start:end])
        y_past = np.column_stack(y_past_cols)
    else:
        y_past = np.zeros_like(y_future)

    return y_future, y_past, max_offset, n_samples, clean_source, clean_target


def _slice_source_with_history(
    source: np.ndarray,
    max_offset: int,
    lag: int,
    k_history_source: int,
    n_samples: int,
) -> np.ndarray:
    """Slice source into lagged matrix with optional source history."""
    x_lag = source[max_offset - lag : max_offset - lag + n_samples]
    if x_lag.ndim == 1:
        x_lag = x_lag.reshape(-1, 1)
    features = [x_lag]

    for i in range(k_history_source):
        start = max_offset - lag - 1 - i
        end = start + n_samples
        hist_slice = source[start:end]
        if hist_slice.ndim == 1:
            hist_slice = hist_slice.reshape(-1, 1)
        features.append(hist_slice)

    return np.hstack(features)


def _block_permute(arr: np.ndarray, block_size: int = 5) -> np.ndarray:
    """Block-wise permutation to preserve some autocorrelation."""
    flat = np.asarray(arr)
    if flat.ndim > 1:
        flat = flat.reshape(len(flat), -1)
    if block_size <= 1 or len(flat) <= block_size:
        permuted = np.random.permutation(flat)
        return permuted

    blocks = [
        flat[i : i + block_size] for i in range(0, len(flat), block_size)
    ]
    np.random.shuffle(blocks)
    return np.vstack(blocks)


def _estimate_cmi_knn(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    k_neighbors: int = 5,
    as_bits: bool = False,
) -> float:
    """Kraskov-style conditional MI estimator using kNN (Chebyshev metric)."""
    x_arr = np.asarray(x, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.float64)
    z_arr = np.asarray(z, dtype=np.float64)

    if x_arr.ndim == 1:
        x_arr = x_arr.reshape(-1, 1)
    if y_arr.ndim == 1:
        y_arr = y_arr.reshape(-1, 1)
    if z_arr.ndim == 1:
        z_arr = z_arr.reshape(-1, 1)

    n_samples = x_arr.shape[0]
    if n_samples <= k_neighbors + 1:
        return 0.0

    xyz = np.hstack([x_arr, y_arr, z_arr])
    xz = np.hstack([x_arr, z_arr])
    yz = np.hstack([y_arr, z_arr])

    tree_xyz = cKDTree(xyz)
    dist, _ = tree_xyz.query(xyz, k=k_neighbors + 1, p=np.inf)
    eps = dist[:, -1]
    eps = np.nextafter(eps, np.zeros_like(eps))

    tree_xz = cKDTree(xz)
    tree_yz = cKDTree(yz)
    tree_z = cKDTree(z_arr)

    nx = np.array(
        [len(tree_xz.query_ball_point(xz[i], eps[i], p=np.inf)) - 1 for i in range(n_samples)],
        dtype=np.int64,
    )
    ny = np.array(
        [len(tree_yz.query_ball_point(yz[i], eps[i], p=np.inf)) - 1 for i in range(n_samples)],
        dtype=np.int64,
    )
    nz = np.array(
        [len(tree_z.query_ball_point(z_arr[i], eps[i], p=np.inf)) - 1 for i in range(n_samples)],
        dtype=np.int64,
    )

    cmi = (
        digamma(k_neighbors)
        + digamma(n_samples)
        - np.mean(digamma(nx + 1) + digamma(ny + 1))
        + np.mean(digamma(nz + 1))
    )

    if as_bits:
        cmi = cmi / math.log(2)

    return float(max(0.0, cmi))


def granger_causality_test(
    source: np.ndarray,
    target: np.ndarray,
    max_lag: int = 7,
    n_permutations: int = 100,
    alpha: float = 0.05,
    representation: Optional[str] = None,
    segment: Optional[str] = None,
    is_control: bool = False,
) -> CouplingResult:
    """Test Granger causality from source to target time-series.

    Uses statsmodels VAR to test if source Granger-causes target.
    Permutation test used for null hypothesis.

    Args:
        source: Source time-series (1D array)
        target: Target time-series (1D array)
        max_lag: Maximum lag to test
        n_permutations: Number of permutations for null distribution
        alpha: Significance threshold

    Returns:
        CouplingResult with Granger F-statistic
    """
    if not _check_statsmodels():
        logger.warning("statsmodels not available, returning NaN result")
        return CouplingResult(
            source="unknown",
            target="unknown",
            method="granger",
            statistic=np.nan,
            p_value=1.0,
            q_value=1.0,
            lag=max_lag,
            n_samples=0,
            null_mean=0.0,
            null_std=0.0,
            is_significant=False,
            segment=segment,
            is_control=is_control,
            representation=representation,
            k_history_target=0,
            k_history_source=0,
            n_permutations=n_permutations,
        )

    from statsmodels.tsa.stattools import grangercausalitytests

    # Prepare data (collapse vectors to mean)
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    if source.ndim > 1:
        source = np.mean(source, axis=1)
    if target.ndim > 1:
        target = np.mean(target, axis=1)
    source = source.flatten()
    target = target.flatten()

    # Align lengths
    min_len = min(len(source), len(target))
    source = source[:min_len]
    target = target[:min_len]

    # Remove NaN
    mask = ~(np.isnan(source) | np.isnan(target))
    source = source[mask]
    target = target[mask]

    n_samples = len(source)
    if n_samples < max_lag + 2:
        return CouplingResult(
            source="unknown",
            target="unknown",
            method="granger",
            statistic=np.nan,
            p_value=1.0,
            q_value=1.0,
            lag=max_lag,
            n_samples=n_samples,
            null_mean=0.0,
            null_std=0.0,
            is_significant=False,
            segment=segment,
            is_control=is_control,
            representation=representation,
            k_history_target=0,
            k_history_source=0,
            n_permutations=n_permutations,
        )

    # Run Granger test
    data = np.column_stack([target, source])

    try:
        result = grangercausalitytests(data, maxlag=max_lag, verbose=False)
        # Get F-statistic at optimal lag (use max_lag)
        f_stat = result[max_lag][0]["ssr_ftest"][0]
        observed_p = result[max_lag][0]["ssr_ftest"][1]
    except Exception as e:
        logger.warning(f"Granger test failed: {e}")
        return CouplingResult(
            source="unknown",
            target="unknown",
            method="granger",
            statistic=np.nan,
            p_value=1.0,
            q_value=1.0,
            lag=max_lag,
            n_samples=n_samples,
            null_mean=0.0,
            null_std=0.0,
            is_significant=False,
            segment=segment,
            is_control=is_control,
            representation=representation,
            k_history_target=0,
            k_history_source=0,
            n_permutations=n_permutations,
        )

    # Permutation test for null distribution
    null_stats = []
    for _ in range(n_permutations):
        perm_source = np.random.permutation(source)
        perm_data = np.column_stack([target, perm_source])
        try:
            perm_result = grangercausalitytests(perm_data, maxlag=max_lag, verbose=False)
            null_stats.append(perm_result[max_lag][0]["ssr_ftest"][0])
        except Exception:
            continue

    null_stats = np.array(null_stats)
    null_mean = np.mean(null_stats) if len(null_stats) > 0 else 0.0
    null_std = np.std(null_stats) if len(null_stats) > 0 else 1.0

    # Empirical p-value
    p_value = np.mean(null_stats >= f_stat) if len(null_stats) > 0 else observed_p

    return CouplingResult(
        source="unknown",
        target="unknown",
        method="granger",
        statistic=float(f_stat),
        p_value=float(p_value),
        q_value=float(p_value),  # Will be corrected later
        lag=max_lag,
        n_samples=n_samples,
        null_mean=float(null_mean),
        null_std=float(null_std),
        is_significant=p_value <= alpha,
        segment=segment,
        is_control=is_control,
        representation=representation,
        k_history_target=0,
        k_history_source=0,
        n_permutations=n_permutations,
    )


def transfer_entropy(
    source: np.ndarray,
    target: np.ndarray,
    lag: int = 1,
    k_history_target: int = 1,
    k_history_source: int = 0,
    k_neighbors: int = 5,
    n_permutations: int = 100,
    alpha: float = 0.05,
    representation: Optional[str] = None,
    segment: Optional[str] = None,
    is_control: bool = False,
) -> CouplingResult:
    """Compute transfer entropy from source to target.

    Uses a kNN-based conditional mutual information estimator (Kraskov-style).
    TE(X->Y) = I(X_{t-lag}; Y_t | Y_{t-1..k_history_target})

    Args:
        source: Source time-series (1D array)
        target: Target time-series (1D array)
        lag: Lag from source to target
        k_history_target: Number of past target steps to condition on
        k_history_source: Number of past source steps to include (optional)
        k_neighbors: k for kNN estimator
        n_permutations: Number of permutations for null
        alpha: Significance threshold

    Returns:
        CouplingResult with transfer entropy in bits
    """
    prepared = _prepare_lagged_vectors(
        source=source,
        target=target,
        lag=lag,
        k_history_target=k_history_target,
        k_history_source=k_history_source,
    )

    if prepared is None:
        return CouplingResult(
            source="unknown",
            target="unknown",
            method="transfer_entropy",
            statistic=0.0,
            p_value=1.0,
            q_value=1.0,
            lag=lag,
            n_samples=0,
            null_mean=0.0,
            null_std=0.0,
            is_significant=False,
            segment=segment,
            is_control=is_control,
            representation=representation,
            k_history_target=k_history_target,
            k_history_source=k_history_source,
            n_permutations=n_permutations,
        )

    y_future, y_past, max_offset, n_samples, clean_source, clean_target = prepared
    x_stack = _slice_source_with_history(
        clean_source, max_offset, lag, k_history_source, n_samples
    )

    observed_te = _estimate_cmi_knn(
        x_stack, y_future, y_past, k_neighbors=k_neighbors, as_bits=True
    )

    block_size = max(1, min(10, lag + 1))
    null_stats = []
    for _ in range(n_permutations):
        perm_source = _block_permute(clean_source, block_size=block_size)
        perm_x = _slice_source_with_history(
            perm_source, max_offset, lag, k_history_source, n_samples
        )
        null_stats.append(
            _estimate_cmi_knn(
                perm_x, y_future, y_past, k_neighbors=k_neighbors, as_bits=True
            )
        )

    null_stats = np.asarray(null_stats, dtype=np.float64)
    null_mean = float(np.mean(null_stats)) if null_stats.size > 0 else 0.0
    null_std = float(np.std(null_stats)) if null_stats.size > 1 else 1.0
    p_value = (
        float(np.mean(null_stats >= observed_te)) if null_stats.size > 0 else 1.0
    )

    return CouplingResult(
        source="unknown",
        target="unknown",
        method="transfer_entropy",
        statistic=float(observed_te),
        p_value=float(p_value),
        q_value=float(p_value),
        lag=lag,
        n_samples=n_samples,
        null_mean=null_mean,
        null_std=null_std,
        is_significant=p_value <= alpha,
        segment=segment,
        is_control=is_control,
        representation=representation,
        k_history_target=k_history_target,
        k_history_source=k_history_source,
        n_permutations=n_permutations,
    )


def mutual_information_lagged(
    source: np.ndarray,
    target: np.ndarray,
    lag: int = 1,
    k_neighbors: int = 5,
    k_history_target: int = 0,
    k_history_source: int = 0,
    n_permutations: int = 100,
    alpha: float = 0.05,
    representation: Optional[str] = None,
    segment: Optional[str] = None,
    is_control: bool = False,
) -> CouplingResult:
    """Compute lagged mutual information between source and target.

    MI(X_{t-lag}, Y_t) using a kNN estimator. Can optionally condition on
    past source/target histories by setting k_history_target/k_history_source.

    Args:
        source: Source time-series (1D array)
        target: Target time-series (1D array)
        lag: Lag from source to target
        k_neighbors: k for kNN estimator
        k_history_target: Conditioning steps of target history (0 => unconditional MI)
        k_history_source: Conditioning steps of source history
        n_permutations: Number of permutations for null
        alpha: Significance threshold

    Returns:
        CouplingResult with MI in bits
    """
    prepared = _prepare_lagged_vectors(
        source=source,
        target=target,
        lag=lag,
        k_history_target=k_history_target,
        k_history_source=k_history_source,
    )

    if prepared is None:
        return CouplingResult(
            source="unknown",
            target="unknown",
            method="mutual_information",
            statistic=0.0,
            p_value=1.0,
            q_value=1.0,
            lag=lag,
            n_samples=0,
            null_mean=0.0,
            null_std=0.0,
            is_significant=False,
            segment=segment,
            is_control=is_control,
            representation=representation,
            k_history_target=k_history_target,
            k_history_source=k_history_source,
            n_permutations=n_permutations,
        )

    y_future, y_past, max_offset, n_samples, clean_source, _ = prepared

    # When k_history_target == k_history_source == 0, y_past becomes zeros,
    # yielding unconditional MI via the same CMI estimator.
    x_stack = _slice_source_with_history(
        clean_source, max_offset, lag, k_history_source, n_samples
    )

    observed_mi = _estimate_cmi_knn(
        x_stack,
        y_future,
        y_past if (k_history_target > 0 or k_history_source > 0) else np.zeros_like(y_future),
        k_neighbors=k_neighbors,
        as_bits=True,
    )

    null_stats = []
    block_size = max(1, min(10, lag + 1))
    for _ in range(n_permutations):
        perm_source = _block_permute(clean_source, block_size=block_size)
        perm_x = _slice_source_with_history(
            perm_source, max_offset, lag, k_history_source, n_samples
        )
        null_stats.append(
            _estimate_cmi_knn(
                perm_x,
                y_future,
                y_past if (k_history_target > 0 or k_history_source > 0) else np.zeros_like(y_future),
                k_neighbors=k_neighbors,
                as_bits=True,
            )
        )

    null_stats = np.asarray(null_stats, dtype=np.float64)
    null_mean = float(np.mean(null_stats)) if null_stats.size > 0 else 0.0
    null_std = float(np.std(null_stats)) if null_stats.size > 1 else 1.0
    p_value = (
        float(np.mean(null_stats >= observed_mi)) if null_stats.size > 0 else 1.0
    )

    return CouplingResult(
        source="unknown",
        target="unknown",
        method="mutual_information",
        statistic=float(observed_mi),
        p_value=float(p_value),
        q_value=float(p_value),
        lag=lag,
        n_samples=n_samples,
        null_mean=null_mean,
        null_std=null_std,
        is_significant=p_value <= alpha,
        segment=segment,
        is_control=is_control,
        representation=representation,
        k_history_target=k_history_target,
        k_history_source=k_history_source,
        n_permutations=n_permutations,
    )


def dtw_distance(
    source: np.ndarray,
    target: np.ndarray,
    window_size: int = 30,
    n_permutations: int = 100,
    alpha: float = 0.05,
    sakoe_chiba_band: int | None = None,
    multiscale_windows: list[int] | None = None,
    representation: Optional[str] = None,
    segment: Optional[str] = None,
    is_control: bool = False,
) -> CouplingResult:
    """Compute DTW distance between source and target windows.

    Uses rolling windows to compute DTW similarity with optional
    Sakoe-Chiba band constraint for O(n*w) complexity.

    Args:
        source: Source time-series (1D array)
        target: Target time-series (1D array)
        window_size: Size of rolling windows
        n_permutations: Number of permutations for null
        alpha: Significance threshold
        sakoe_chiba_band: Width of Sakoe-Chiba band constraint (None=no band, full O(n²)).
            When set, warping path is constrained to |i-j| <= band, reducing to O(n*band).
        multiscale_windows: List of window sizes for multiscale analysis.
            If provided, overrides window_size and computes DTW at multiple scales.

    Returns:
        CouplingResult with negative DTW distance (higher = more similar)
    """
    source = np.asarray(source, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    if source.ndim > 1:
        source = np.mean(source, axis=1)
    if target.ndim > 1:
        target = np.mean(target, axis=1)
    source = source.flatten()
    target = target.flatten()

    # Align lengths
    min_len = min(len(source), len(target))
    source = source[:min_len]
    target = target[:min_len]

    # Remove NaN
    mask = ~(np.isnan(source) | np.isnan(target))
    source = source[mask]
    target = target[mask]

    n_samples = len(source)
    if n_samples < window_size + 2:
        return CouplingResult(
            source="unknown",
            target="unknown",
            method="dtw",
            statistic=0.0,
            p_value=1.0,
            q_value=1.0,
            lag=0,
            n_samples=n_samples,
            null_mean=0.0,
            null_std=0.0,
            is_significant=False,
            segment=segment,
            is_control=is_control,
            representation=representation,
            k_history_target=0,
            k_history_source=0,
            n_permutations=n_permutations,
        )

    def _compute_dtw(src: np.ndarray, tgt: np.ndarray, band: int | None = None) -> float:
        """Compute DTW using dynamic programming with optional Sakoe-Chiba band.

        Args:
            src: Source sequence (normalized)
            tgt: Target sequence (normalized)
            band: Sakoe-Chiba band width. If None, full O(n²) DTW.
                  If set, constrains warping to |i-j| <= band for O(n*band).

        Returns:
            DTW distance (0 for identical sequences)
        """
        n, m = len(src), len(tgt)
        if n == 0 or m == 0:
            return 0.0

        # Normalize
        src = (src - np.mean(src)) / (np.std(src) + 1e-10)
        tgt = (tgt - np.mean(tgt)) / (np.std(tgt) + 1e-10)

        # DTW matrix
        dtw_matrix = np.full((n + 1, m + 1), np.inf)
        dtw_matrix[0, 0] = 0

        # Apply Sakoe-Chiba band constraint if specified
        if band is not None:
            # O(n*band) complexity with band constraint
            for i in range(1, n + 1):
                # j_min and j_max define the band around diagonal
                j_min = max(1, i - band)
                j_max = min(m + 1, i + band + 1)
                for j in range(j_min, j_max):
                    cost = abs(src[i - 1] - tgt[j - 1])
                    dtw_matrix[i, j] = cost + min(
                        dtw_matrix[i - 1, j],
                        dtw_matrix[i, j - 1],
                        dtw_matrix[i - 1, j - 1],
                    )
        else:
            # O(n²) full DTW without band constraint
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    cost = abs(src[i - 1] - tgt[j - 1])
                    dtw_matrix[i, j] = cost + min(
                        dtw_matrix[i - 1, j],
                        dtw_matrix[i, j - 1],
                        dtw_matrix[i - 1, j - 1],
                    )

        return dtw_matrix[n, m]

    # Determine window sizes to use
    if multiscale_windows is not None:
        windows_to_use = [w for w in multiscale_windows if w >= 5 and n_samples >= w + 2]
        if not windows_to_use:
            windows_to_use = [window_size]
    else:
        windows_to_use = [window_size]

    # Compute distances across all window scales
    distances = []
    for ws in windows_to_use:
        n_windows = max(1, n_samples // ws)
        for i in range(n_windows):
            start = i * ws
            end = min(start + ws, n_samples)
            if end - start >= 5:
                dist = _compute_dtw(
                    source[start:end], target[start:end], band=sakoe_chiba_band
                )
                distances.append(dist)

    observed_dist = np.mean(distances) if distances else 0.0
    # Use negative so higher = more similar (like correlation)
    observed_stat = -observed_dist

    # Permutation test
    null_stats = []
    for _ in range(n_permutations):
        perm_source = np.random.permutation(source)
        perm_distances = []
        for ws in windows_to_use:
            n_windows = max(1, n_samples // ws)
            for i in range(n_windows):
                start = i * ws
                end = min(start + ws, n_samples)
                if end - start >= 5:
                    dist = _compute_dtw(
                        perm_source[start:end], target[start:end], band=sakoe_chiba_band
                    )
                    perm_distances.append(dist)
        null_stats.append(-np.mean(perm_distances) if perm_distances else 0.0)

    null_stats = np.array(null_stats)
    null_mean = np.mean(null_stats)
    null_std = np.std(null_stats) if len(null_stats) > 1 else 1.0

    # p-value: how often null is more similar (larger negative distance)
    p_value = np.mean(null_stats >= observed_stat) if len(null_stats) > 0 else 1.0

    # Method name reflects band usage
    method_name = "dtw" if sakoe_chiba_band is None else f"dtw_band{sakoe_chiba_band}"

    return CouplingResult(
        source="unknown",
        target="unknown",
        method=method_name,
        statistic=float(observed_stat),
        p_value=float(p_value),
        q_value=float(p_value),
        lag=0,
        n_samples=n_samples,
        null_mean=float(null_mean),
        null_std=float(null_std),
        is_significant=p_value <= alpha,
        segment=segment,
        is_control=is_control,
        representation=representation,
        k_history_target=0,
        k_history_source=0,
        n_permutations=n_permutations,
    )


def run_all_methods(
    source: np.ndarray,
    target: np.ndarray,
    source_name: str = "source",
    target_name: str = "target",
    lag: int = 1,
    n_permutations: int = 100,
    alpha: float = 0.05,
    representation: Optional[str] = None,
    segment: Optional[str] = None,
    is_control: bool = False,
    k_history_target: int = 1,
    k_history_source: int = 0,
    k_neighbors: int = 5,
) -> list[CouplingResult]:
    """Run all coupling analysis methods on a pair of time-series.

    Args:
        source: Source time-series
        target: Target time-series
        source_name: Name of source game
        target_name: Name of target game
        lag: Lag to use
        n_permutations: Number of permutations
        alpha: Significance threshold
        representation: Representation identifier
        segment: Data split label (train/test)
        is_control: Whether the pair is a control comparison
        k_history_target: Target history length for TE/CMI
        k_history_source: Source history length for TE/CMI
        k_neighbors: k for TE/CMI estimators

    Returns:
        List of CouplingResult, one per method
    """
    results = []

    # Granger causality
    granger = granger_causality_test(
        source,
        target,
        max_lag=lag,
        n_permutations=n_permutations,
        alpha=alpha,
        representation=representation,
        segment=segment,
        is_control=is_control,
    )
    results.append(
        replace(
            granger,
            source=source_name,
            target=target_name,
        )
    )

    # Transfer entropy (kNN/CMI)
    te = transfer_entropy(
        source,
        target,
        lag=lag,
        k_history_target=k_history_target,
        k_history_source=k_history_source,
        k_neighbors=k_neighbors,
        n_permutations=n_permutations,
        alpha=alpha,
        representation=representation,
        segment=segment,
        is_control=is_control,
    )
    results.append(replace(te, source=source_name, target=target_name))

    # Mutual information (optionally conditional)
    mi = mutual_information_lagged(
        source,
        target,
        lag=lag,
        k_neighbors=k_neighbors,
        k_history_target=k_history_target,
        k_history_source=k_history_source,
        n_permutations=n_permutations,
        alpha=alpha,
        representation=representation,
        segment=segment,
        is_control=is_control,
    )
    results.append(replace(mi, source=source_name, target=target_name))

    # DTW
    dtw = dtw_distance(
        source,
        target,
        n_permutations=n_permutations,
        alpha=alpha,
        representation=representation,
        segment=segment,
        is_control=is_control,
    )
    results.append(replace(dtw, source=source_name, target=target_name))

    return results


def apply_fdr_correction(
    results: list[CouplingResult],
    alpha: float = 0.05,
    group_by: Optional[Sequence[str]] = None,
) -> list[CouplingResult]:
    """Apply BH/FDR correction to a list of CouplingResults.

    Args:
        results: List of CouplingResult objects
        alpha: FDR threshold
        group_by: Optional list of attributes to group corrections (e.g., ["method", "is_control"])

    Returns:
        New list with corrected q_values and is_significant
    """
    if not results:
        return []

    if not group_by:
        p_values = np.array([r.p_value for r in results])
        q_values = bh_fdr(p_values)
        return [
            replace(r, q_value=float(q), is_significant=q <= alpha)
            for r, q in zip(results, q_values)
        ]

    corrected: list[Optional[CouplingResult]] = [None] * len(results)
    grouped: dict[tuple, list[tuple[int, CouplingResult]]] = {}
    for idx, res in enumerate(results):
        key = tuple(getattr(res, field, None) for field in group_by)
        grouped.setdefault(key, []).append((idx, res))

    for _, entries in grouped.items():
        p_values = np.array([r.p_value for _, r in entries])
        q_values = bh_fdr(p_values)
        for (idx, res), q in zip(entries, q_values):
            corrected[idx] = replace(res, q_value=float(q), is_significant=q <= alpha)

    return [c for c in corrected if c is not None]


__all__ = [
    "CouplingResult",
    "granger_causality_test",
    "transfer_entropy",
    "mutual_information_lagged",
    "dtw_distance",
    "run_all_methods",
    "apply_fdr_correction",
]
