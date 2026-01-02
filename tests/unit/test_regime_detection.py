from datetime import datetime, timedelta

from kenobase.analysis.regime_detection import (
    RegimeDetectionConfig,
    detect_regimes,
)
from kenobase.core.data_loader import DrawResult, GameType


def _make_draw(date: datetime, spieleinsatz: float, jackpot: float) -> DrawResult:
    return DrawResult(
        date=date,
        numbers=list(range(1, 21)),
        bonus=[],
        game_type=GameType.KENO,
        metadata={
            "spieleinsatz": spieleinsatz,
            "jackpot": jackpot,
        },
    )


def test_detect_regimes_pipeline_runs_and_maps_states() -> None:
    base_date = datetime(2023, 6, 1)

    # Train segment 1: cooldown regime (low jackpot/einsatz)
    draws = [
        _make_draw(base_date + timedelta(days=i), 500_000, 1_000_000) for i in range(6)
    ]
    # Train segment 2: hot regime (high jackpot/einsatz)
    draws.extend(
        _make_draw(base_date + timedelta(days=6 + i), 1_500_000, 20_000_000) for i in range(6)
    )
    # Test segment: extends hot regime into 2024
    draws.extend(
        _make_draw(datetime(2024, 1, 1) + timedelta(days=i), 1_600_000, 22_000_000)
        for i in range(4)
    )

    config = RegimeDetectionConfig(
        train_split_date=datetime(2024, 1, 1),
        cv_window=2,
        numbers_range=(1, 70),
        change_point_penalty=1.0,
        change_point_min_size=2,
        boundary_tolerance=1,
        n_states=4,
        random_state=7,
    )

    result = detect_regimes(draws, config)

    assert len(result.latent_states) == len(draws)
    assert len(result.state_labels) == len(draws)
    assert result.train_size == 12
    assert result.boundaries, "Change-point detection should identify at least one boundary"
    assert result.boundary_f1 >= 0.0
    # Test accuracy on the held-out portion (hot regime continues)
    assert result.accuracy >= 0.5
    # Log-likelihood should be finite on test data
    assert result.log_likelihood != 0.0
