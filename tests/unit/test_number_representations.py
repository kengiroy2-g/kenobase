"""Unit tests for number_representations module."""

from datetime import date

import numpy as np
import pytest

from kenobase.analysis.cross_lottery_coupling import GameDraws
from kenobase.analysis.number_representations import (
    GameTimeSeries,
    align_time_series,
    draws_to_centroid_series,
    draws_to_mean_series,
    draws_to_presence_vector_series,
    draws_to_sum_series,
    game_to_time_series,
    get_train_test_split,
)


@pytest.fixture
def sample_game_draws() -> GameDraws:
    """Create sample GameDraws for testing."""
    # 5 draws with numbers in range 1-70
    dates = [
        date(2023, 1, 1),
        date(2023, 1, 2),
        date(2023, 1, 3),
        date(2023, 1, 4),
        date(2023, 1, 5),
    ]

    # presence[i, n] = 1 if number n was drawn on day i
    presence = np.zeros((5, 71), dtype=np.int8)

    # Day 1: numbers 1, 10, 20, 30, 40, 50
    for n in [1, 10, 20, 30, 40, 50]:
        presence[0, n] = 1

    # Day 2: numbers 5, 15, 25, 35, 45, 55
    for n in [5, 15, 25, 35, 45, 55]:
        presence[1, n] = 1

    # Day 3: numbers 10, 20, 30, 40, 50, 60
    for n in [10, 20, 30, 40, 50, 60]:
        presence[2, n] = 1

    # Day 4: numbers 1, 2, 3, 4, 5, 6
    for n in [1, 2, 3, 4, 5, 6]:
        presence[3, n] = 1

    # Day 5: numbers 65, 66, 67, 68, 69, 70
    for n in [65, 66, 67, 68, 69, 70]:
        presence[4, n] = 1

    return GameDraws(
        name="KENO",
        pool_max=70,
        draw_size=6,
        dates=dates,
        presence=presence,
        ordered_numbers=None,
        jackpot_winners=None,
    )


class TestDrawsToSumSeries:
    """Tests for draws_to_sum_series."""

    def test_basic_sum_calculation(self, sample_game_draws: GameDraws) -> None:
        """Test that sum series is calculated correctly."""
        ts = draws_to_sum_series(sample_game_draws)

        assert ts.name == "KENO"
        assert ts.representation == "sum"
        assert len(ts.dates) == 5
        assert ts.values.shape == (5,)

        # Day 1: 1+10+20+30+40+50 = 151
        assert ts.values[0] == 151

        # Day 2: 5+15+25+35+45+55 = 180
        assert ts.values[1] == 180

        # Day 4: 1+2+3+4+5+6 = 21
        assert ts.values[3] == 21

    def test_output_type(self, sample_game_draws: GameDraws) -> None:
        """Test that output is a GameTimeSeries."""
        ts = draws_to_sum_series(sample_game_draws)
        assert isinstance(ts, GameTimeSeries)


class TestDrawsToMeanSeries:
    """Tests for draws_to_mean_series."""

    def test_basic_mean_calculation(self, sample_game_draws: GameDraws) -> None:
        """Test that mean series is calculated correctly."""
        ts = draws_to_mean_series(sample_game_draws)

        assert ts.representation == "mean"

        # Day 1: mean(1,10,20,30,40,50) = 25.166...
        assert np.isclose(ts.values[0], 25.166666, rtol=0.01)

        # Day 4: mean(1,2,3,4,5,6) = 3.5
        assert np.isclose(ts.values[3], 3.5)

        # Day 5: mean(65,66,67,68,69,70) = 67.5
        assert np.isclose(ts.values[4], 67.5)


class TestDrawsToCentroidSeries:
    """Tests for draws_to_centroid_series."""

    def test_centroid_normalization(self, sample_game_draws: GameDraws) -> None:
        """Test that centroid is normalized to [0, 1]."""
        ts = draws_to_centroid_series(sample_game_draws)

        assert ts.representation == "centroid"

        # All values should be in [0, 1]
        assert all(0 <= v <= 1 for v in ts.values)

        # Day 4 has low numbers -> centroid should be low
        assert ts.values[3] < 0.3

        # Day 5 has high numbers -> centroid should be high
        assert ts.values[4] > 0.9


class TestDrawsToPresenceVectorSeries:
    """Tests for draws_to_presence_vector_series."""

    def test_presence_vector_shape(self, sample_game_draws: GameDraws) -> None:
        """Test that presence vector has correct shape."""
        ts = draws_to_presence_vector_series(sample_game_draws)

        assert ts.representation == "presence_vector"
        assert ts.values.shape == (5, 71)

    def test_presence_values_match(self, sample_game_draws: GameDraws) -> None:
        """Test that presence values match original."""
        ts = draws_to_presence_vector_series(sample_game_draws)

        # Check day 1 presence
        assert ts.values[0, 1] == 1  # number 1 present
        assert ts.values[0, 10] == 1  # number 10 present
        assert ts.values[0, 5] == 0  # number 5 not present


class TestGameToTimeSeries:
    """Tests for game_to_time_series factory function."""

    def test_factory_sum(self, sample_game_draws: GameDraws) -> None:
        """Test factory with sum representation."""
        ts = game_to_time_series(sample_game_draws, representation="sum")
        assert ts.representation == "sum"

    def test_factory_mean(self, sample_game_draws: GameDraws) -> None:
        """Test factory with mean representation."""
        ts = game_to_time_series(sample_game_draws, representation="mean")
        assert ts.representation == "mean"

    def test_factory_centroid(self, sample_game_draws: GameDraws) -> None:
        """Test factory with centroid representation."""
        ts = game_to_time_series(sample_game_draws, representation="centroid")
        assert ts.representation == "centroid"

    def test_factory_invalid_representation(self, sample_game_draws: GameDraws) -> None:
        """Test factory with invalid representation raises error."""
        with pytest.raises(ValueError):
            game_to_time_series(sample_game_draws, representation="invalid")


class TestAlignTimeSeries:
    """Tests for align_time_series."""

    def test_single_series_alignment(self, sample_game_draws: GameDraws) -> None:
        """Test alignment with single series."""
        ts = draws_to_centroid_series(sample_game_draws)
        df = align_time_series([ts])

        assert len(df) == 5
        assert "KENO" in df.columns

    def test_multiple_series_alignment(self, sample_game_draws: GameDraws) -> None:
        """Test alignment with multiple series."""
        ts1 = draws_to_centroid_series(sample_game_draws)

        # Create second game with different dates
        dates2 = [
            date(2023, 1, 2),  # Overlaps with ts1
            date(2023, 1, 3),  # Overlaps with ts1
            date(2023, 1, 6),  # After ts1
        ]
        presence2 = np.zeros((3, 50), dtype=np.int8)
        for n in [1, 2, 3, 4, 5, 6]:
            presence2[0, n] = 1
            presence2[1, n] = 1
            presence2[2, n] = 1

        game2 = GameDraws(
            name="LOTTO",
            pool_max=49,
            draw_size=6,
            dates=dates2,
            presence=presence2,
            ordered_numbers=None,
            jackpot_winners=None,
        )
        ts2 = draws_to_centroid_series(game2)

        df = align_time_series([ts1, ts2])

        assert "KENO" in df.columns
        assert "LOTTO" in df.columns
        # Should have union of dates: 6 unique dates
        assert len(df) == 6

    def test_date_filter(self, sample_game_draws: GameDraws) -> None:
        """Test date filtering in alignment."""
        ts = draws_to_centroid_series(sample_game_draws)
        df = align_time_series([ts], start_date=date(2023, 1, 2), end_date=date(2023, 1, 4))

        assert len(df) == 3


class TestTrainTestSplit:
    """Tests for get_train_test_split."""

    def test_basic_split(self, sample_game_draws: GameDraws) -> None:
        """Test basic train/test split."""
        ts = draws_to_centroid_series(sample_game_draws)
        df = align_time_series([ts])

        train, test = get_train_test_split(df, split_date="2023-01-04")

        # Days 1-3 in train, days 4-5 in test
        assert len(train) == 3
        assert len(test) == 2

    def test_empty_train_set(self, sample_game_draws: GameDraws) -> None:
        """Test split with empty train set."""
        ts = draws_to_centroid_series(sample_game_draws)
        df = align_time_series([ts])

        train, test = get_train_test_split(df, split_date="2023-01-01")

        assert len(train) == 0
        assert len(test) == 5

    def test_empty_test_set(self, sample_game_draws: GameDraws) -> None:
        """Test split with empty test set."""
        ts = draws_to_centroid_series(sample_game_draws)
        df = align_time_series([ts])

        train, test = get_train_test_split(df, split_date="2023-01-06")

        assert len(train) == 5
        assert len(test) == 0
