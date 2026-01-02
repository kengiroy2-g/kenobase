"""Economic State Variables and Proxies for Lottery Analysis.

This module provides economic state variables/proxies that can be used for
bet-selection strategies based on Axiom A7 (Reset-Zyklen) and A1 (House-Edge).

Key Proxies:
- Spieleinsatz (betting volume) - from DrawResult.metadata
- Jackpot level - from DrawResult.metadata
- Rolling CV (coefficient of variation) - computed from hit distribution

Integration:
- DataLoader already parses spieleinsatz/jackpot into metadata
- Train/Test split from axioms.py is respected
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import numpy as np

from kenobase.core.data_loader import DrawResult


@dataclass
class EconomicState:
    """Economic state for a single draw or period.

    Attributes:
        date: Reference date for this state
        spieleinsatz: Total betting volume (from metadata, may be None)
        jackpot: Jackpot level (from metadata, may be None)
        rolling_cv: Coefficient of variation of hit distribution (computed)
        state_label: Classification label (NORMAL, COOLDOWN, RECOVERY, HOT)
    """

    date: datetime
    spieleinsatz: Optional[float]
    jackpot: Optional[float]
    rolling_cv: Optional[float]
    state_label: str = "NORMAL"


def _parse_numeric_value(raw: str) -> Optional[float]:
    """Parse locale-specific numeric strings like '1.234.567,89' or '€1,000'."""
    try:
        cleaned = (
            raw.replace("€", "")
            .replace(".", "")
            .replace(" ", "")
            .replace(",", ".")
            .strip()
        )
        return float(cleaned)
    except ValueError:
        return None


def parse_spieleinsatz(metadata: dict) -> Optional[float]:
    """Parse spieleinsatz from DrawResult metadata.

    Args:
        metadata: Metadata dict from DrawResult

    Returns:
        Parsed spieleinsatz as float, or None if not available
    """
    raw = metadata.get("spieleinsatz")
    if raw is None:
        return None

    if isinstance(raw, (int, float)):
        return float(raw)

    # Handle string format (e.g., "1.234.567,89" German format)
    if isinstance(raw, str):
        return _parse_numeric_value(raw)

    return None


def parse_jackpot(metadata: dict) -> Optional[float]:
    """Parse jackpot from DrawResult metadata.

    Args:
        metadata: Metadata dict from DrawResult

    Returns:
        Parsed jackpot as float, or None if not available
    """
    # Accept multiple keys to align with heterogeneous CSV sources.
    raw_keys = (
        "jackpot",
        "jackpot_kl1",
        "jackpot_klasse1",
        "jackpot_kl_1",
    )
    raw = None
    for key in raw_keys:
        if key in metadata:
            raw = metadata.get(key)
            break
    if raw is None:
        return None

    if isinstance(raw, (int, float)):
        return float(raw)

    # Handle string format
    if isinstance(raw, str):
        return _parse_numeric_value(raw)

    return None


def compute_rolling_cv(
    draws: list[DrawResult],
    window: int = 30,
    numbers_range: tuple[int, int] = (1, 70),
) -> list[Optional[float]]:
    """Compute rolling coefficient of variation of number frequencies.

    The CV measures how spread out the frequency distribution is. A higher CV
    indicates more uneven distribution (some numbers appearing much more/less).

    Args:
        draws: List of DrawResult objects (sorted by date ascending)
        window: Rolling window size (default 30 draws)
        numbers_range: Range of possible numbers (default KENO 1-70)

    Returns:
        List of CV values, one per draw. First (window-1) values are None.
    """
    if len(draws) < window:
        return [None] * len(draws)

    min_num, max_num = numbers_range
    n_numbers = max_num - min_num + 1

    cvs: list[Optional[float]] = [None] * (window - 1)

    for i in range(window - 1, len(draws)):
        # Count frequencies in window
        freq = np.zeros(n_numbers)
        for j in range(i - window + 1, i + 1):
            for num in draws[j].numbers:
                if min_num <= num <= max_num:
                    freq[num - min_num] += 1

        # Compute CV = std / mean
        mean_freq = np.mean(freq)
        if mean_freq > 0:
            cv = np.std(freq) / mean_freq
        else:
            cv = 0.0

        cvs.append(float(cv))

    return cvs


def classify_economic_state(
    spieleinsatz: Optional[float],
    jackpot: Optional[float],
    rolling_cv: Optional[float],
    spieleinsatz_baseline: Optional[float] = None,
    jackpot_high_threshold: float = 10_000_000.0,
    cv_high_threshold: float = 0.5,
) -> str:
    """Classify the economic state based on proxies.

    States (aligned with Axiom A7 Reset-Zyklen):
    - COOLDOWN: After jackpot hit, system needs to recover (low spieleinsatz, high CV)
    - HOT: High jackpot, high activity (good for players)
    - RECOVERY: Transitioning from cooldown
    - NORMAL: Standard operating state

    Args:
        spieleinsatz: Current betting volume
        jackpot: Current jackpot level
        rolling_cv: Current coefficient of variation
        spieleinsatz_baseline: Reference spieleinsatz for comparison
        jackpot_high_threshold: Threshold for "high" jackpot
        cv_high_threshold: Threshold for "high" CV

    Returns:
        State label: COOLDOWN, HOT, RECOVERY, or NORMAL
    """
    # If we don't have enough data, return NORMAL
    if all(x is None for x in [spieleinsatz, jackpot, rolling_cv]):
        return "NORMAL"

    # Check for COOLDOWN indicators
    cooldown_indicators = 0

    # Low spieleinsatz relative to baseline
    if spieleinsatz is not None and spieleinsatz_baseline is not None:
        if spieleinsatz < spieleinsatz_baseline * 0.7:
            cooldown_indicators += 1

    # Low jackpot (recently hit)
    if jackpot is not None and jackpot < jackpot_high_threshold * 0.3:
        cooldown_indicators += 1

    # High CV (uneven distribution after jackpot)
    if rolling_cv is not None and rolling_cv > cv_high_threshold:
        cooldown_indicators += 1

    if cooldown_indicators >= 2:
        return "COOLDOWN"

    # Check for HOT indicators
    hot_indicators = 0

    # High jackpot
    if jackpot is not None and jackpot >= jackpot_high_threshold:
        hot_indicators += 1

    # High spieleinsatz
    if spieleinsatz is not None and spieleinsatz_baseline is not None:
        if spieleinsatz > spieleinsatz_baseline * 1.3:
            hot_indicators += 1

    if hot_indicators >= 1 and jackpot is not None and jackpot >= jackpot_high_threshold:
        return "HOT"

    # Check for RECOVERY
    if cooldown_indicators == 1:
        return "RECOVERY"

    return "NORMAL"


def extract_economic_states(
    draws: list[DrawResult],
    window: int = 30,
    numbers_range: tuple[int, int] = (1, 70),
    jackpot_high_threshold: float = 10_000_000.0,
    cv_high_threshold: float = 0.5,
) -> list[EconomicState]:
    """Extract economic states from a list of draws.

    Args:
        draws: List of DrawResult objects (will be sorted by date)
        window: Rolling window for CV computation
        numbers_range: Range of possible numbers
        jackpot_high_threshold: Threshold for "high" jackpot
        cv_high_threshold: Threshold for "high" CV

    Returns:
        List of EconomicState objects, one per draw
    """
    # Sort by date
    sorted_draws = sorted(draws, key=lambda d: d.date)

    # Extract spieleinsatz values for baseline
    spieleinsatz_values = []
    for draw in sorted_draws:
        se = parse_spieleinsatz(draw.metadata)
        if se is not None:
            spieleinsatz_values.append(se)

    spieleinsatz_baseline = (
        float(np.median(spieleinsatz_values)) if spieleinsatz_values else None
    )

    # Compute rolling CVs
    rolling_cvs = compute_rolling_cv(sorted_draws, window, numbers_range)

    # Build economic states
    states = []
    for i, draw in enumerate(sorted_draws):
        spieleinsatz = parse_spieleinsatz(draw.metadata)
        jackpot = parse_jackpot(draw.metadata)
        rolling_cv = rolling_cvs[i]

        state_label = classify_economic_state(
            spieleinsatz=spieleinsatz,
            jackpot=jackpot,
            rolling_cv=rolling_cv,
            spieleinsatz_baseline=spieleinsatz_baseline,
            jackpot_high_threshold=jackpot_high_threshold,
            cv_high_threshold=cv_high_threshold,
        )

        states.append(
            EconomicState(
                date=draw.date,
                spieleinsatz=spieleinsatz,
                jackpot=jackpot,
                rolling_cv=rolling_cv,
                state_label=state_label,
            )
        )

    return states


def get_bet_recommendation(state: EconomicState) -> dict:
    """Get bet recommendation based on economic state.

    Based on Axiom A7 (Reset-Zyklen):
    - COOLDOWN: System is recovering, avoid betting
    - HOT: High jackpot, potentially good time to play
    - RECOVERY: Transitioning, play cautiously
    - NORMAL: Standard play

    Args:
        state: Current economic state

    Returns:
        Dict with recommendation and confidence
    """
    recommendations = {
        "COOLDOWN": {
            "action": "AVOID",
            "confidence": 0.7,
            "reason": "System in post-jackpot recovery phase (Axiom A7)",
        },
        "HOT": {
            "action": "CONSIDER",
            "confidence": 0.6,
            "reason": "High jackpot, increased player activity",
        },
        "RECOVERY": {
            "action": "CAUTIOUS",
            "confidence": 0.5,
            "reason": "Transitioning from cooldown, uncertain state",
        },
        "NORMAL": {
            "action": "NEUTRAL",
            "confidence": 0.5,
            "reason": "Standard operating conditions",
        },
    }

    return recommendations.get(
        state.state_label,
        {"action": "NEUTRAL", "confidence": 0.5, "reason": "Unknown state"},
    )


def compute_state_distribution(states: list[EconomicState]) -> dict:
    """Compute distribution of economic states.

    Args:
        states: List of EconomicState objects

    Returns:
        Dict with state counts and percentages
    """
    if not states:
        return {"total": 0, "counts": {}, "percentages": {}}

    counts: dict[str, int] = {}
    for state in states:
        counts[state.state_label] = counts.get(state.state_label, 0) + 1

    total = len(states)
    percentages = {k: v / total * 100 for k, v in counts.items()}

    return {
        "total": total,
        "counts": counts,
        "percentages": percentages,
    }
