"""
Axiom-First Framework for Kenobase V2.0

This module defines the 7 economic axioms and their 21 falsifiable predictions
for lottery analysis. Based on the principle that lotteries are ECONOMIC systems
with hard constraints, not pure random number generators.

Author: EXECUTOR (TASK AXIOM-001)
Date: 2025-12-30
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class NullModelType(Enum):
    """Types of null models for statistical testing."""
    IID = "iid"                          # Independent and identically distributed
    POISSON = "poisson"                  # Poisson process
    BINOMIAL = "binomial"                # Binomial distribution
    PERMUTATION = "permutation"          # Random permutation
    BLOCK_PERMUTATION = "block_permutation"  # Block-preserving permutation
    SCHEDULE_PRESERVING = "schedule_preserving"  # Preserves temporal schedule
    FAKE_LAG = "fake_lag"                # Fake lag control for post-event tests


class Direction(Enum):
    """Direction of hypothesis test."""
    LESS = "less"          # Observed < threshold
    GREATER = "greater"    # Observed > threshold
    BETWEEN = "between"    # threshold_low < Observed < threshold_high
    NOT_EQUAL = "not_equal"  # Observed != expected


@dataclass
class Prediction:
    """A falsifiable prediction derived from an axiom."""
    id: str
    description: str
    metric: str
    threshold: float
    threshold_high: Optional[float] = None  # For BETWEEN direction
    direction: Direction = Direction.LESS
    null_model: NullModelType = NullModelType.IID
    requires_data: Optional[str] = None  # Data requirement flag (e.g., "DATAREQ-001")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "description": self.description,
            "metric": self.metric,
            "threshold": self.threshold,
            "threshold_high": self.threshold_high,
            "direction": self.direction.value,
            "null_model": self.null_model.value,
            "requires_data": self.requires_data,
        }


@dataclass
class Axiom:
    """An economic axiom about the lottery system."""
    id: str
    name: str
    description: str
    economic_rationale: str
    predictions: list[Prediction] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "economic_rationale": self.economic_rationale,
            "predictions": [p.to_dict() for p in self.predictions],
        }


# =============================================================================
# AXIOM DEFINITIONS
# =============================================================================

AXIOM_A1 = Axiom(
    id="A1",
    name="House-Edge",
    description="50% redistribution is legally guaranteed",
    economic_rationale=(
        "The lottery must maintain profitability. German law requires approximately "
        "50% of stakes to be redistributed as prizes. This creates a hard constraint "
        "on expected ROI for any playing strategy."
    ),
    predictions=[
        Prediction(
            id="P1.1",
            description="12-month ROI between -45% and -55% (median ~-50%)",
            metric="roi_12m",
            threshold=-0.55,
            threshold_high=-0.45,
            direction=Direction.BETWEEN,
            null_model=NullModelType.BINOMIAL,
        ),
        Prediction(
            id="P1.2",
            description="No player-type achieves sustained > 0% ROI",
            metric="max_roi_by_type",
            threshold=0.0,
            direction=Direction.LESS,
            null_model=NullModelType.PERMUTATION,
        ),
        Prediction(
            id="P1.3",
            description="House-Edge variance < 5% between quarters",
            metric="roi_quarterly_std",
            threshold=0.05,
            direction=Direction.LESS,
            null_model=NullModelType.BLOCK_PERMUTATION,
        ),
    ],
)

AXIOM_A2 = Axiom(
    id="A2",
    name="Dauerscheine",
    description="Players use fixed combinations (subscription tickets)",
    economic_rationale=(
        "Many players use 'Dauerscheine' (subscription tickets) with the same "
        "numbers over extended periods. This creates predictable patterns in "
        "ticket distributions that the system must account for."
    ),
    predictions=[
        Prediction(
            id="P2.1",
            description="Certain combinations appear more frequently in tickets",
            metric="combination_frequency_variance",
            threshold=1.0,  # > 1.0 indicates non-uniform distribution
            direction=Direction.GREATER,
            null_model=NullModelType.IID,
        ),
        Prediction(
            id="P2.2",
            description="Birthday numbers (1-31) are overrepresented in tips",
            metric="birthday_ratio",
            threshold=0.44,  # 31/70 = 0.44 would be uniform
            direction=Direction.GREATER,
            null_model=NullModelType.BINOMIAL,
        ),
        Prediction(
            id="P2.3",
            description="Win quotes for popular combinations are lower",
            metric="popular_vs_unpopular_quote_ratio",
            threshold=1.0,
            direction=Direction.LESS,
            null_model=NullModelType.PERMUTATION,
        ),
    ],
)

AXIOM_A3 = Axiom(
    id="A3",
    name="Attraktivitaet",
    description="Small wins MUST occur regularly",
    economic_rationale=(
        "To maintain player engagement, the system must ensure regular small wins. "
        "This creates 'near-miss' experiences that keep players returning. "
        "Without regular small wins, players would abandon the game."
    ),
    predictions=[
        Prediction(
            id="P3.1",
            description="Small wins (Type 6-8) occur regularly",
            metric="small_win_frequency",
            threshold=0.1,  # At least 10% of plays should yield small wins
            direction=Direction.GREATER,
            null_model=NullModelType.POISSON,
        ),
        Prediction(
            id="P3.2",
            description="Near-misses (5 of 6) more frequent than IID predicts",
            metric="near_miss_ratio_vs_iid",
            threshold=1.0,
            direction=Direction.GREATER,
            null_model=NullModelType.IID,
        ),
        Prediction(
            id="P3.3",
            description="At least 1 winner per week in each prize class",
            metric="weekly_winner_coverage",
            threshold=1.0,
            direction=Direction.GREATER,
            null_model=NullModelType.POISSON,
        ),
    ],
)

AXIOM_A4 = Axiom(
    id="A4",
    name="Paar-Garantie",
    description="Number pairs ensure player retention",
    economic_rationale=(
        "Players often play specific number pairs (birthdays, anniversaries). "
        "The system may ensure these pairs appear together more often than "
        "pure randomness would suggest, maintaining player loyalty."
    ),
    predictions=[
        Prediction(
            id="P4.1",
            description="Certain number pairs appear significantly more often together",
            metric="pair_coupling_chi2",
            threshold=0.05,  # p-value < 0.05
            direction=Direction.LESS,
            null_model=NullModelType.IID,
        ),
        Prediction(
            id="P4.2",
            description="Popular pairs (7-11, 3-7) have increased coupling",
            metric="popular_pair_coupling_ratio",
            threshold=1.0,
            direction=Direction.GREATER,
            null_model=NullModelType.PERMUTATION,
        ),
        Prediction(
            id="P4.3",
            description="Pair frequency correlates with Dauerschein popularity",
            metric="pair_dauerschein_correlation",
            threshold=0.1,  # r > 0.1
            direction=Direction.GREATER,
            null_model=NullModelType.SCHEDULE_PRESERVING,
        ),
    ],
)

AXIOM_A5 = Axiom(
    id="A5",
    name="Pseudo-Zufall",
    description="Every number must appear within a period",
    economic_rationale=(
        "To maintain perceived fairness, no number should be absent for too long. "
        "The system ensures all numbers appear within reasonable periods, "
        "preventing player perception of 'cold' or 'dead' numbers."
    ),
    predictions=[
        Prediction(
            id="P5.1",
            description="Every number appears at least once in N drawings (N~20)",
            metric="max_absence_period",
            threshold=20,  # Max 20 drawings without appearance
            direction=Direction.LESS,
            null_model=NullModelType.POISSON,
        ),
        Prediction(
            id="P5.2",
            description="Maximum gap of a number is bounded (< 50 drawings)",
            metric="max_gap",
            threshold=50,
            direction=Direction.LESS,
            null_model=NullModelType.IID,
        ),
        Prediction(
            id="P5.3",
            description="Frequency distribution is tighter than IID Poisson",
            metric="frequency_variance_ratio",
            threshold=1.0,  # < 1.0 means tighter than Poisson
            direction=Direction.LESS,
            null_model=NullModelType.POISSON,
        ),
    ],
)

AXIOM_A6 = Axiom(
    id="A6",
    name="Regionale Verteilung",
    description="Wins distributed per federal state",
    economic_rationale=(
        "German lottery operates federally. Each Bundesland expects proportional "
        "wins to maintain political support. Large wins should correlate with "
        "population distribution."
    ),
    predictions=[
        Prediction(
            id="P6.1",
            description="Wins per Bundesland correlate with population",
            metric="regional_population_correlation",
            threshold=0.5,  # r > 0.5
            direction=Direction.GREATER,
            null_model=NullModelType.PERMUTATION,
            requires_data="DATAREQ-001",
        ),
        Prediction(
            id="P6.2",
            description="No region has significantly more jackpots per capita",
            metric="regional_jackpot_per_capita_chi2",
            threshold=0.05,  # p-value > 0.05 (not significant)
            direction=Direction.GREATER,
            null_model=NullModelType.BINOMIAL,
            requires_data="DATAREQ-001",
        ),
        Prediction(
            id="P6.3",
            description="Large wins are evenly distributed over time",
            metric="regional_temporal_uniformity",
            threshold=0.1,  # Kolmogorov-Smirnov p > 0.1
            direction=Direction.GREATER,
            null_model=NullModelType.SCHEDULE_PRESERVING,
            requires_data="DATAREQ-001",
        ),
    ],
)

AXIOM_A7 = Axiom(
    id="A7",
    name="Reset-Zyklen",
    description="System 'saves' after jackpots",
    economic_rationale=(
        "After a large jackpot payout, the system must rebuild its prize pool. "
        "This creates 'cooldown' periods where overall win rates decrease. "
        "Smart players should avoid playing during these reset cycles."
    ),
    predictions=[
        Prediction(
            id="P7.1",
            description="ROI drops by > 20% in 30 days after jackpot",
            metric="post_jackpot_roi_change",
            threshold=-0.20,
            direction=Direction.LESS,
            null_model=NullModelType.FAKE_LAG,
        ),
        Prediction(
            id="P7.2",
            description="Hot numbers before jackpot become cold after",
            metric="hot_cold_transition_rate",
            threshold=0.5,  # > 50% of hot numbers become cold
            direction=Direction.GREATER,
            null_model=NullModelType.PERMUTATION,
        ),
        Prediction(
            id="P7.3",
            description="System-wide win quote drops post-jackpot",
            metric="post_jackpot_quote_change",
            threshold=0.0,
            direction=Direction.LESS,
            null_model=NullModelType.SCHEDULE_PRESERVING,
        ),
    ],
)

# All axioms as a dictionary
ALL_AXIOMS: dict[str, Axiom] = {
    "A1": AXIOM_A1,
    "A2": AXIOM_A2,
    "A3": AXIOM_A3,
    "A4": AXIOM_A4,
    "A5": AXIOM_A5,
    "A6": AXIOM_A6,
    "A7": AXIOM_A7,
}

# All predictions as a flat dictionary
ALL_PREDICTIONS: dict[str, Prediction] = {}
for axiom in ALL_AXIOMS.values():
    for pred in axiom.predictions:
        ALL_PREDICTIONS[pred.id] = pred


def get_axiom(axiom_id: str) -> Axiom:
    """Get an axiom by ID.

    Args:
        axiom_id: Axiom identifier (A1-A7)

    Returns:
        The requested Axiom

    Raises:
        KeyError: If axiom_id is not found
    """
    if axiom_id not in ALL_AXIOMS:
        raise KeyError(f"Unknown axiom: {axiom_id}. Valid IDs: {list(ALL_AXIOMS.keys())}")
    return ALL_AXIOMS[axiom_id]


def get_prediction(prediction_id: str) -> Prediction:
    """Get a prediction by ID.

    Args:
        prediction_id: Prediction identifier (P1.1, P1.2, etc.)

    Returns:
        The requested Prediction

    Raises:
        KeyError: If prediction_id is not found
    """
    if prediction_id not in ALL_PREDICTIONS:
        raise KeyError(
            f"Unknown prediction: {prediction_id}. "
            f"Valid IDs: {list(ALL_PREDICTIONS.keys())}"
        )
    return ALL_PREDICTIONS[prediction_id]


def get_predictions_for_axiom(axiom_id: str) -> list[Prediction]:
    """Get all predictions for a specific axiom.

    Args:
        axiom_id: Axiom identifier (A1-A7)

    Returns:
        List of predictions for the axiom
    """
    axiom = get_axiom(axiom_id)
    return axiom.predictions


def get_predictions_requiring_data() -> list[Prediction]:
    """Get all predictions that require external data.

    Returns:
        List of predictions with requires_data set
    """
    return [p for p in ALL_PREDICTIONS.values() if p.requires_data is not None]


def get_predictions_by_null_model(null_model: NullModelType) -> list[Prediction]:
    """Get all predictions using a specific null model type.

    Args:
        null_model: The null model type to filter by

    Returns:
        List of predictions using that null model
    """
    return [p for p in ALL_PREDICTIONS.values() if p.null_model == null_model]


def export_all_axioms() -> dict:
    """Export all axioms and predictions as a dictionary.

    Returns:
        Dictionary with all axiom definitions
    """
    return {
        "axioms": {aid: ax.to_dict() for aid, ax in ALL_AXIOMS.items()},
        "total_axioms": len(ALL_AXIOMS),
        "total_predictions": len(ALL_PREDICTIONS),
        "predictions_requiring_data": [
            p.id for p in get_predictions_requiring_data()
        ],
    }


# =============================================================================
# TRAIN/TEST SPLIT CONFIGURATION
# =============================================================================

TRAIN_TEST_SPLIT = {
    "train_end": "2023-12-31",
    "test_start": "2024-01-01",
    "rule": "Rules are mined in train and FROZEN for test evaluation",
}


def get_train_test_split() -> dict:
    """Get the train/test split configuration.

    Returns:
        Dictionary with train_end, test_start, and rule
    """
    return TRAIN_TEST_SPLIT.copy()


# =============================================================================
# EUROJACKPOT NEGATIVE CONTROL
# =============================================================================

EUROJACKPOT_CONTROL = {
    "is_german_ecosystem": False,
    "rationale": (
        "EuroJackpot is NOT part of the German lottery ecosystem. "
        "It has international control, different player base, and own economics. "
        "Use as negative control: German axioms A2, A4, A6 should NOT apply."
    ),
    "excluded_axioms": ["A2", "A4", "A6"],
}


def get_eurojackpot_control_config() -> dict:
    """Get EuroJackpot negative control configuration.

    Returns:
        Dictionary with control configuration
    """
    return EUROJACKPOT_CONTROL.copy()
