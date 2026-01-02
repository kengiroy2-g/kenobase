"""Cross-spectrum and phase coupling analysis between lottery games.

Goal
----
Detect inverse/periodic coupling between lottery games using spectral methods:
- Cross-Power Spectral Density (CPSD) via Welch's method
- Coherence analysis per frequency band
- Phase difference and Phase-Locking Value (PLV)

This is an exploratory analysis layer with BH/FDR correction for multiple comparisons.

Important
---------
Many tests are run in parallel (multiple frequency bands, representations).
Always rely on FDR-adjusted q-values to avoid false discoveries.
EuroJackpot is treated as a negative control (should not show spurious coupling).
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Literal, Optional, Sequence

import numpy as np
from scipy import signal, stats

from kenobase.analysis.cross_lottery_coupling import GameDraws, bh_fdr
from kenobase.analysis.number_representations import (
    GameTimeSeries,
    RepresentationType,
    game_to_time_series,
)


@dataclass(frozen=True)
class FrequencyBand:
    """Frequency band specification."""

    name: str
    low_freq: float  # cycles per sample
    high_freq: float  # cycles per sample


# Default frequency bands (in cycles per sample, assuming daily sampling)
DEFAULT_BANDS: list[FrequencyBand] = [
    FrequencyBand(name="weekly", low_freq=1 / 10, high_freq=1 / 5),
    FrequencyBand(name="biweekly", low_freq=1 / 20, high_freq=1 / 10),
    FrequencyBand(name="monthly", low_freq=1 / 40, high_freq=1 / 20),
]


@dataclass
class CoherenceResult:
    """Coherence analysis result for a frequency band."""

    band_name: str
    low_freq: float
    high_freq: float
    mean_coherence: float
    max_coherence: float
    peak_frequency: float
    p_value: float
    q_value: float = 0.0


@dataclass
class PhaseResult:
    """Phase coupling result for a frequency band."""

    band_name: str
    mean_phase_diff: float  # radians
    phase_std: float  # radians
    plv: float  # Phase-Locking Value [0, 1]
    circular_mean_direction: float  # radians
    p_value: float
    q_value: float = 0.0


@dataclass
class SpectralCouplingResult:
    """Full spectral coupling result between two games."""

    source_game: str
    target_game: str
    representation: str
    n_samples: int
    segment_length: int
    overlap: int
    coherence_results: list[CoherenceResult]
    phase_results: list[PhaseResult]
    dominant_frequency: Optional[float]
    dominant_coherence: Optional[float]
    is_significant: bool
    negative_control: bool = False


@dataclass
class CrossSpectrumSummary:
    """Summary of cross-spectrum analysis across all pairs and representations."""

    timestamp: str
    n_pairs: int
    n_representations: int
    n_bands: int
    n_surrogates: int
    alpha_fdr: float
    results: list[SpectralCouplingResult]
    significant_count: int
    negative_control_significant: int


def _ensure_1d(values: np.ndarray) -> np.ndarray:
    """Ensure values are 1D, taking mean across columns if needed."""
    if values.ndim == 1:
        return values.astype(np.float64)
    elif values.ndim == 2:
        # For vector representations, take the mean across dimensions
        return np.mean(values, axis=1).astype(np.float64)
    else:
        raise ValueError(f"Unsupported array dimension: {values.ndim}")


def align_series_by_date(
    series1: GameTimeSeries,
    series2: GameTimeSeries,
) -> tuple[np.ndarray, np.ndarray, list[date]]:
    """Align two time series by date intersection.

    Args:
        series1: First time series
        series2: Second time series

    Returns:
        Tuple of (aligned_values1, aligned_values2, common_dates)
    """
    dates1 = set(series1.dates)
    dates2 = set(series2.dates)
    common = sorted(dates1.intersection(dates2))

    if not common:
        return np.array([]), np.array([]), []

    idx1 = {d: i for i, d in enumerate(series1.dates)}
    idx2 = {d: i for i, d in enumerate(series2.dates)}

    vals1 = _ensure_1d(series1.values)
    vals2 = _ensure_1d(series2.values)

    aligned1 = np.array([vals1[idx1[d]] for d in common], dtype=np.float64)
    aligned2 = np.array([vals2[idx2[d]] for d in common], dtype=np.float64)

    return aligned1, aligned2, common


def compute_cpsd_coherence(
    x: np.ndarray,
    y: np.ndarray,
    fs: float = 1.0,
    nperseg: Optional[int] = None,
    noverlap: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute cross-power spectral density and coherence.

    Args:
        x: First signal
        y: Second signal
        fs: Sampling frequency (default 1.0 for normalized frequency)
        nperseg: Segment length for Welch's method
        noverlap: Overlap between segments

    Returns:
        Tuple of (frequencies, cpsd, coherence, phase)
    """
    n = len(x)
    if nperseg is None:
        nperseg = min(256, n // 4)
    if noverlap is None:
        noverlap = nperseg // 2

    # Ensure minimum segment length
    nperseg = max(16, min(nperseg, n))
    noverlap = min(noverlap, nperseg - 1)

    # Cross-power spectral density
    freqs, cpsd = signal.csd(x, y, fs=fs, nperseg=nperseg, noverlap=noverlap)

    # Coherence
    _, coh = signal.coherence(x, y, fs=fs, nperseg=nperseg, noverlap=noverlap)

    # Phase from CPSD
    phase = np.angle(cpsd)

    return freqs, np.abs(cpsd), coh, phase


def compute_plv(phases: np.ndarray) -> float:
    """Compute Phase-Locking Value from phase differences.

    PLV = |mean(exp(i * phases))|

    Args:
        phases: Array of phase differences in radians

    Returns:
        PLV in [0, 1], where 1 indicates perfect phase locking
    """
    if len(phases) == 0:
        return 0.0
    complex_phases = np.exp(1j * phases)
    return float(np.abs(np.mean(complex_phases)))


def circular_mean(phases: np.ndarray) -> tuple[float, float]:
    """Compute circular mean and resultant length.

    Args:
        phases: Array of angles in radians

    Returns:
        Tuple of (mean_direction, resultant_length)
    """
    if len(phases) == 0:
        return 0.0, 0.0
    s = np.sin(phases)
    c = np.cos(phases)
    mean_dir = np.arctan2(np.mean(s), np.mean(c))
    resultant = np.sqrt(np.mean(s) ** 2 + np.mean(c) ** 2)
    return float(mean_dir), float(resultant)


def extract_band_metrics(
    freqs: np.ndarray,
    coherence: np.ndarray,
    phase: np.ndarray,
    band: FrequencyBand,
) -> tuple[CoherenceResult, PhaseResult]:
    """Extract metrics for a specific frequency band.

    Args:
        freqs: Frequency array
        coherence: Coherence values
        phase: Phase values
        band: Frequency band specification

    Returns:
        Tuple of (CoherenceResult, PhaseResult)
    """
    # Find indices within band
    mask = (freqs >= band.low_freq) & (freqs <= band.high_freq)
    band_freqs = freqs[mask]
    band_coh = coherence[mask]
    band_phase = phase[mask]

    if len(band_coh) == 0:
        coh_result = CoherenceResult(
            band_name=band.name,
            low_freq=band.low_freq,
            high_freq=band.high_freq,
            mean_coherence=0.0,
            max_coherence=0.0,
            peak_frequency=0.0,
            p_value=1.0,
        )
        phase_result = PhaseResult(
            band_name=band.name,
            mean_phase_diff=0.0,
            phase_std=0.0,
            plv=0.0,
            circular_mean_direction=0.0,
            p_value=1.0,
        )
        return coh_result, phase_result

    mean_coh = float(np.mean(band_coh))
    max_coh = float(np.max(band_coh))
    peak_idx = int(np.argmax(band_coh))
    peak_freq = float(band_freqs[peak_idx])

    # Phase metrics
    plv = compute_plv(band_phase)
    circ_mean, _ = circular_mean(band_phase)
    phase_std = float(np.std(band_phase))
    mean_phase = float(np.mean(band_phase))

    coh_result = CoherenceResult(
        band_name=band.name,
        low_freq=band.low_freq,
        high_freq=band.high_freq,
        mean_coherence=mean_coh,
        max_coherence=max_coh,
        peak_frequency=peak_freq,
        p_value=1.0,  # Will be set by surrogate testing
    )

    phase_result = PhaseResult(
        band_name=band.name,
        mean_phase_diff=mean_phase,
        phase_std=phase_std,
        plv=plv,
        circular_mean_direction=circ_mean,
        p_value=1.0,  # Will be set by surrogate testing
    )

    return coh_result, phase_result


def generate_phase_surrogate(x: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
    """Generate phase-randomized surrogate preserving amplitude spectrum.

    Args:
        x: Input signal
        seed: Random seed for reproducibility

    Returns:
        Surrogate signal with randomized phase
    """
    rng = np.random.default_rng(seed)
    n = len(x)

    # FFT
    fft_x = np.fft.rfft(x)

    # Randomize phases (preserve DC and Nyquist)
    random_phases = rng.uniform(0, 2 * np.pi, len(fft_x))
    random_phases[0] = 0  # Preserve DC
    if n % 2 == 0:
        random_phases[-1] = 0  # Preserve Nyquist for even n

    # Apply random phase shift
    surrogate_fft = np.abs(fft_x) * np.exp(1j * random_phases)

    # Inverse FFT
    return np.fft.irfft(surrogate_fft, n=n)


def generate_block_surrogate(
    x: np.ndarray,
    block_size: int = 7,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Generate block-permuted surrogate preserving local structure.

    Args:
        x: Input signal
        block_size: Size of blocks to permute (default 7 for weekly)
        seed: Random seed for reproducibility

    Returns:
        Block-permuted surrogate
    """
    rng = np.random.default_rng(seed)
    n = len(x)

    # Create blocks
    n_blocks = n // block_size
    remainder = n % block_size

    blocks = [x[i * block_size : (i + 1) * block_size] for i in range(n_blocks)]
    if remainder > 0:
        blocks.append(x[n_blocks * block_size :])

    # Shuffle blocks
    rng.shuffle(blocks)

    return np.concatenate(blocks)


def surrogate_significance_test(
    x: np.ndarray,
    y: np.ndarray,
    observed_coherence: np.ndarray,
    observed_plv: float,
    band: FrequencyBand,
    freqs: np.ndarray,
    n_surrogates: int = 199,
    surrogate_type: Literal["phase", "block"] = "phase",
    nperseg: Optional[int] = None,
    noverlap: Optional[int] = None,
    seed: Optional[int] = None,
) -> tuple[float, float]:
    """Compute p-values via surrogate testing.

    Args:
        x, y: Original signals
        observed_coherence: Observed coherence values
        observed_plv: Observed PLV
        band: Frequency band
        freqs: Frequency array
        n_surrogates: Number of surrogates
        surrogate_type: Type of surrogate ("phase" or "block")
        nperseg: Segment length for spectral estimation
        noverlap: Overlap for spectral estimation
        seed: Base random seed

    Returns:
        Tuple of (coherence_p_value, plv_p_value)
    """
    rng = np.random.default_rng(seed)

    mask = (freqs >= band.low_freq) & (freqs <= band.high_freq)
    observed_mean_coh = float(np.mean(observed_coherence[mask])) if mask.any() else 0.0

    coh_count = 0
    plv_count = 0

    for i in range(n_surrogates):
        s = rng.integers(0, 2**31) if seed is not None else None

        if surrogate_type == "phase":
            y_surr = generate_phase_surrogate(y, seed=s)
        else:
            y_surr = generate_block_surrogate(y, seed=s)

        _, _, surr_coh, surr_phase = compute_cpsd_coherence(
            x, y_surr, nperseg=nperseg, noverlap=noverlap
        )

        surr_mean_coh = float(np.mean(surr_coh[mask])) if mask.any() else 0.0
        surr_plv = compute_plv(surr_phase[mask]) if mask.any() else 0.0

        if surr_mean_coh >= observed_mean_coh:
            coh_count += 1
        if surr_plv >= observed_plv:
            plv_count += 1

    # Add 1 to both numerator and denominator for conservative estimate
    coh_p = (coh_count + 1) / (n_surrogates + 1)
    plv_p = (plv_count + 1) / (n_surrogates + 1)

    return coh_p, plv_p


def analyze_spectral_coupling(
    game1: GameDraws,
    game2: GameDraws,
    representation: RepresentationType = "centroid",
    bands: Optional[list[FrequencyBand]] = None,
    nperseg: Optional[int] = None,
    noverlap: Optional[int] = None,
    n_surrogates: int = 199,
    surrogate_type: Literal["phase", "block"] = "phase",
    alpha_fdr: float = 0.05,
    negative_control: bool = False,
    seed: Optional[int] = None,
) -> SpectralCouplingResult:
    """Analyze spectral coupling between two lottery games.

    Args:
        game1: First game draws
        game2: Second game draws
        representation: Time series representation type
        bands: Frequency bands to analyze (default: weekly, biweekly, monthly)
        nperseg: Segment length for Welch's method
        noverlap: Overlap between segments
        n_surrogates: Number of surrogates for significance testing
        surrogate_type: Type of surrogate ("phase" or "block")
        alpha_fdr: FDR threshold for significance
        negative_control: Flag if this is a negative control pair
        seed: Random seed for reproducibility

    Returns:
        SpectralCouplingResult with coherence and phase metrics per band
    """
    if bands is None:
        bands = DEFAULT_BANDS

    # Convert to time series
    ts1 = game_to_time_series(game1, representation)
    ts2 = game_to_time_series(game2, representation)

    # Align by date
    x, y, common_dates = align_series_by_date(ts1, ts2)

    if len(x) < 32:
        return SpectralCouplingResult(
            source_game=game1.name,
            target_game=game2.name,
            representation=representation,
            n_samples=len(x),
            segment_length=0,
            overlap=0,
            coherence_results=[],
            phase_results=[],
            dominant_frequency=None,
            dominant_coherence=None,
            is_significant=False,
            negative_control=negative_control,
        )

    # Normalize
    x = (x - np.mean(x)) / (np.std(x) + 1e-10)
    y = (y - np.mean(y)) / (np.std(y) + 1e-10)

    # Set default segment parameters
    n = len(x)
    if nperseg is None:
        nperseg = min(64, n // 4)
    if noverlap is None:
        noverlap = nperseg // 2

    # Compute spectral metrics
    freqs, cpsd, coherence, phase = compute_cpsd_coherence(
        x, y, nperseg=nperseg, noverlap=noverlap
    )

    coherence_results: list[CoherenceResult] = []
    phase_results: list[PhaseResult] = []
    all_p_values: list[float] = []

    for band in bands:
        coh_res, phase_res = extract_band_metrics(freqs, coherence, phase, band)

        # Surrogate significance testing
        mask = (freqs >= band.low_freq) & (freqs <= band.high_freq)
        if mask.any():
            coh_p, plv_p = surrogate_significance_test(
                x,
                y,
                coherence,
                phase_res.plv,
                band,
                freqs,
                n_surrogates=n_surrogates,
                surrogate_type=surrogate_type,
                nperseg=nperseg,
                noverlap=noverlap,
                seed=seed,
            )
            coh_res = CoherenceResult(
                band_name=coh_res.band_name,
                low_freq=coh_res.low_freq,
                high_freq=coh_res.high_freq,
                mean_coherence=coh_res.mean_coherence,
                max_coherence=coh_res.max_coherence,
                peak_frequency=coh_res.peak_frequency,
                p_value=coh_p,
            )
            phase_res = PhaseResult(
                band_name=phase_res.band_name,
                mean_phase_diff=phase_res.mean_phase_diff,
                phase_std=phase_res.phase_std,
                plv=phase_res.plv,
                circular_mean_direction=phase_res.circular_mean_direction,
                p_value=plv_p,
            )
            all_p_values.extend([coh_p, plv_p])

        coherence_results.append(coh_res)
        phase_results.append(phase_res)

    # Apply BH/FDR correction
    if all_p_values:
        q_values = bh_fdr(np.array(all_p_values))
        q_idx = 0
        updated_coh_results = []
        updated_phase_results = []
        for coh_res, phase_res in zip(coherence_results, phase_results):
            if coh_res.p_value < 1.0:
                updated_coh_results.append(
                    CoherenceResult(
                        band_name=coh_res.band_name,
                        low_freq=coh_res.low_freq,
                        high_freq=coh_res.high_freq,
                        mean_coherence=coh_res.mean_coherence,
                        max_coherence=coh_res.max_coherence,
                        peak_frequency=coh_res.peak_frequency,
                        p_value=coh_res.p_value,
                        q_value=float(q_values[q_idx]),
                    )
                )
                updated_phase_results.append(
                    PhaseResult(
                        band_name=phase_res.band_name,
                        mean_phase_diff=phase_res.mean_phase_diff,
                        phase_std=phase_res.phase_std,
                        plv=phase_res.plv,
                        circular_mean_direction=phase_res.circular_mean_direction,
                        p_value=phase_res.p_value,
                        q_value=float(q_values[q_idx + 1]),
                    )
                )
                q_idx += 2
            else:
                updated_coh_results.append(coh_res)
                updated_phase_results.append(phase_res)
        coherence_results = updated_coh_results
        phase_results = updated_phase_results

    # Find dominant frequency
    dom_freq = None
    dom_coh = None
    if coherence_results:
        best = max(coherence_results, key=lambda r: r.max_coherence)
        dom_freq = best.peak_frequency
        dom_coh = best.max_coherence

    # Check significance
    is_significant = any(r.q_value <= alpha_fdr for r in coherence_results if r.q_value > 0)

    return SpectralCouplingResult(
        source_game=game1.name,
        target_game=game2.name,
        representation=representation,
        n_samples=len(x),
        segment_length=nperseg,
        overlap=noverlap,
        coherence_results=coherence_results,
        phase_results=phase_results,
        dominant_frequency=dom_freq,
        dominant_coherence=dom_coh,
        is_significant=is_significant,
        negative_control=negative_control,
    )


def run_cross_spectrum_analysis(
    games: list[GameDraws],
    representations: Optional[list[RepresentationType]] = None,
    bands: Optional[list[FrequencyBand]] = None,
    n_surrogates: int = 199,
    surrogate_type: Literal["phase", "block"] = "phase",
    alpha_fdr: float = 0.05,
    negative_control_games: Optional[list[str]] = None,
    seed: Optional[int] = None,
) -> CrossSpectrumSummary:
    """Run cross-spectrum analysis across all game pairs and representations.

    Args:
        games: List of GameDraws objects
        representations: List of representation types to analyze
        bands: Frequency bands to analyze
        n_surrogates: Number of surrogates for significance testing
        surrogate_type: Type of surrogate ("phase" or "block")
        alpha_fdr: FDR threshold for significance
        negative_control_games: List of game names to treat as negative controls
        seed: Random seed for reproducibility

    Returns:
        CrossSpectrumSummary with all results
    """
    from datetime import datetime

    if representations is None:
        representations = ["centroid", "sum", "mean"]
    if bands is None:
        bands = DEFAULT_BANDS
    if negative_control_games is None:
        negative_control_games = ["EuroJackpot", "eurojackpot", "EJ"]

    results: list[SpectralCouplingResult] = []
    n_pairs = 0

    for i, game1 in enumerate(games):
        for game2 in games[i + 1 :]:
            n_pairs += 1
            is_negative = (
                game1.name in negative_control_games or game2.name in negative_control_games
            )

            for rep in representations:
                result = analyze_spectral_coupling(
                    game1,
                    game2,
                    representation=rep,
                    bands=bands,
                    n_surrogates=n_surrogates,
                    surrogate_type=surrogate_type,
                    alpha_fdr=alpha_fdr,
                    negative_control=is_negative,
                    seed=seed,
                )
                results.append(result)

    significant_count = sum(1 for r in results if r.is_significant and not r.negative_control)
    negative_significant = sum(1 for r in results if r.is_significant and r.negative_control)

    return CrossSpectrumSummary(
        timestamp=datetime.now().isoformat(),
        n_pairs=n_pairs,
        n_representations=len(representations),
        n_bands=len(bands),
        n_surrogates=n_surrogates,
        alpha_fdr=alpha_fdr,
        results=results,
        significant_count=significant_count,
        negative_control_significant=negative_significant,
    )


def to_jsonable(obj) -> dict:
    """Convert dataclasses / nested structures to JSON-serializable dict."""
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    return obj


__all__ = [
    "FrequencyBand",
    "CoherenceResult",
    "PhaseResult",
    "SpectralCouplingResult",
    "CrossSpectrumSummary",
    "DEFAULT_BANDS",
    "align_series_by_date",
    "compute_cpsd_coherence",
    "compute_plv",
    "circular_mean",
    "extract_band_metrics",
    "generate_phase_surrogate",
    "generate_block_surrogate",
    "surrogate_significance_test",
    "analyze_spectral_coupling",
    "run_cross_spectrum_analysis",
    "to_jsonable",
]
