"""Unit tests for TimelineGrid module.

Tests the multi-game timeline alignment functionality.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.core.timeline import (
    DRAW_PATTERNS,
    GameData,
    TimelineGrid,
    load_multi_game_grid,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_keno_draws() -> list[DrawResult]:
    """Create sample KENO draws (daily)."""
    dates = pd.date_range("2024-01-01", "2024-01-07", freq="D")
    draws = []
    for i, date in enumerate(dates):
        draws.append(
            DrawResult(
                date=date.to_pydatetime(),
                numbers=list(range(1, 21)),  # 20 numbers
                bonus=[10000 + i],
                game_type=GameType.KENO,
                metadata={"spieleinsatz": f"{100+i}"},
            )
        )
    return draws


@pytest.fixture
def sample_lotto_draws() -> list[DrawResult]:
    """Create sample Lotto draws (Wed + Sat)."""
    # Jan 2024: Wed=3rd, Sat=6th
    draws = [
        DrawResult(
            date=datetime(2024, 1, 3),  # Wednesday
            numbers=[1, 2, 3, 4, 5, 6],
            bonus=[7],
            game_type=GameType.LOTTO,
            metadata={"format": "test"},
        ),
        DrawResult(
            date=datetime(2024, 1, 6),  # Saturday
            numbers=[10, 20, 30, 40, 41, 42],
            bonus=[9],
            game_type=GameType.LOTTO,
            metadata={"format": "test"},
        ),
    ]
    return draws


@pytest.fixture
def sample_eurojackpot_draws() -> list[DrawResult]:
    """Create sample EuroJackpot draws (Tue + Fri)."""
    # Jan 2024: Tue=2nd, Fri=5th
    draws = [
        DrawResult(
            date=datetime(2024, 1, 2),  # Tuesday
            numbers=[1, 2, 3, 4, 5],
            bonus=[1, 2],
            game_type=GameType.EUROJACKPOT,
            metadata={"format": "test"},
        ),
        DrawResult(
            date=datetime(2024, 1, 5),  # Friday
            numbers=[10, 20, 30, 40, 50],
            bonus=[3, 4],
            game_type=GameType.EUROJACKPOT,
            metadata={"format": "test"},
        ),
    ]
    return draws


# ============================================================================
# Draw Pattern Tests
# ============================================================================


class TestDrawPatterns:
    """Tests for draw pattern constants."""

    def test_keno_daily(self):
        """KENO should have draws every day."""
        assert DRAW_PATTERNS["keno"] == {0, 1, 2, 3, 4, 5, 6}
        assert len(DRAW_PATTERNS["keno"]) == 7

    def test_lotto_wed_sat(self):
        """Lotto should have draws on Wednesday (2) and Saturday (5)."""
        assert DRAW_PATTERNS["lotto"] == {2, 5}

    def test_eurojackpot_tue_fri(self):
        """EuroJackpot should have draws on Tuesday (1) and Friday (4)."""
        assert DRAW_PATTERNS["eurojackpot"] == {1, 4}


# ============================================================================
# TimelineGrid Tests
# ============================================================================


class TestTimelineGridBasic:
    """Basic TimelineGrid functionality tests."""

    def test_init_empty(self):
        """Empty grid should initialize with default values."""
        grid = TimelineGrid()
        assert grid.games == {}
        assert grid.start_date is None
        assert grid.end_date is None
        assert grid.fill_strategy == "nan"

    def test_init_with_fill_strategy(self):
        """Grid should accept fill_strategy parameter."""
        grid = TimelineGrid(fill_strategy="ffill")
        assert grid.fill_strategy == "ffill"

    def test_add_game_empty_raises(self):
        """Adding empty draws should raise ValueError."""
        grid = TimelineGrid()
        with pytest.raises(ValueError, match="No draws provided"):
            grid.add_game("test", [])

    def test_add_game_single(self, sample_keno_draws):
        """Adding a single game should work."""
        grid = TimelineGrid()
        grid.add_game("keno", sample_keno_draws)

        assert "keno" in grid.games
        assert grid.games["keno"].game_type == GameType.KENO
        assert len(grid.games["keno"].draws) == 7
        assert grid.start_date == datetime(2024, 1, 1)
        assert grid.end_date == datetime(2024, 1, 7)

    def test_add_game_multiple(
        self, sample_keno_draws, sample_lotto_draws, sample_eurojackpot_draws
    ):
        """Adding multiple games should merge date ranges."""
        grid = TimelineGrid()
        grid.add_game("keno", sample_keno_draws)
        grid.add_game("lotto", sample_lotto_draws)
        grid.add_game("eurojackpot", sample_eurojackpot_draws)

        assert len(grid.games) == 3
        assert grid.start_date == datetime(2024, 1, 1)
        assert grid.end_date == datetime(2024, 1, 7)


class TestTimelineGridDataFrame:
    """Tests for DataFrame conversion."""

    def test_to_dataframe_empty_raises(self):
        """Empty grid should raise ValueError."""
        grid = TimelineGrid()
        with pytest.raises(ValueError, match="No games added"):
            grid.to_dataframe()

    def test_to_dataframe_single_game(self, sample_keno_draws):
        """Single game DataFrame should have correct structure."""
        grid = TimelineGrid()
        grid.add_game("keno", sample_keno_draws)
        df = grid.to_dataframe()

        assert len(df) == 7  # 7 days
        assert "keno_has_draw" in df.columns
        assert "keno_numbers" in df.columns
        assert "keno_bonus" in df.columns
        assert df["keno_has_draw"].all()  # All days have draws

    def test_to_dataframe_multiple_games(
        self, sample_keno_draws, sample_lotto_draws
    ):
        """Multiple games should have correct columns."""
        grid = TimelineGrid()
        grid.add_game("keno", sample_keno_draws)
        grid.add_game("lotto", sample_lotto_draws)
        df = grid.to_dataframe()

        assert len(df) == 7  # 7 days
        assert "keno_has_draw" in df.columns
        assert "lotto_has_draw" in df.columns

        # KENO has draws every day
        assert df["keno_has_draw"].sum() == 7

        # Lotto has draws on Wed (3rd) and Sat (6th)
        assert df["lotto_has_draw"].sum() == 2

    def test_to_dataframe_nan_strategy(self, sample_lotto_draws):
        """NaN strategy should leave non-draw days as NaN."""
        grid = TimelineGrid(fill_strategy="nan")
        grid.add_game("lotto", sample_lotto_draws)
        df = grid.to_dataframe()

        # Non-draw days should be NaN (Jan 4th is between Wed 3rd and Sat 6th)
        assert pd.isna(df.loc["2024-01-04", "lotto_numbers"])

        # Draw day should have value
        assert df.loc["2024-01-03", "lotto_numbers"] is not None

    def test_to_dataframe_ffill_strategy(self, sample_lotto_draws):
        """Forward-fill strategy should propagate last value."""
        grid = TimelineGrid(fill_strategy="ffill")
        grid.add_game("lotto", sample_lotto_draws)
        df = grid.to_dataframe()

        # After Wed (3rd), Thu (4th) should have Wed's value
        wed_numbers = df.loc["2024-01-03", "lotto_numbers"]
        thu_numbers = df.loc["2024-01-04", "lotto_numbers"]
        assert thu_numbers == wed_numbers


class TestTimelineGridMatrix:
    """Tests for numbers matrix export."""

    def test_to_numbers_matrix_single(self, sample_lotto_draws):
        """Matrix should expand numbers to separate columns."""
        grid = TimelineGrid()
        grid.add_game("lotto", sample_lotto_draws)
        df = grid.to_numbers_matrix()

        # Should have individual number columns
        assert "lotto_z1" in df.columns
        assert "lotto_z6" in df.columns
        assert "lotto_has_draw" in df.columns

        # Check values on draw day
        assert df.loc["2024-01-03", "lotto_z1"] == 1
        assert df.loc["2024-01-03", "lotto_z6"] == 6

    def test_to_numbers_matrix_bonus(self, sample_eurojackpot_draws):
        """Matrix should include bonus numbers."""
        grid = TimelineGrid()
        grid.add_game("eurojackpot", sample_eurojackpot_draws)
        df = grid.to_numbers_matrix()

        # EuroJackpot has euro1, euro2 for bonus
        assert "eurojackpot_euro1" in df.columns
        assert "eurojackpot_euro2" in df.columns

        # Check values
        assert df.loc["2024-01-02", "eurojackpot_euro1"] == 1
        assert df.loc["2024-01-02", "eurojackpot_euro2"] == 2


class TestTimelineGridCoverage:
    """Tests for draw coverage statistics."""

    def test_get_draw_coverage(
        self, sample_keno_draws, sample_lotto_draws
    ):
        """Coverage should calculate correctly."""
        grid = TimelineGrid()
        grid.add_game("keno", sample_keno_draws)
        grid.add_game("lotto", sample_lotto_draws)
        coverage = grid.get_draw_coverage()

        assert len(coverage) == 2

        keno_cov = coverage[coverage["game"] == "keno"].iloc[0]
        assert keno_cov["draw_days"] == 7
        assert keno_cov["coverage"] == 1.0
        assert keno_cov["expected_weekly"] == 7

        lotto_cov = coverage[coverage["game"] == "lotto"].iloc[0]
        assert lotto_cov["draw_days"] == 2
        assert lotto_cov["expected_weekly"] == 2


class TestTimelineGridJointDays:
    """Tests for joint draw day detection."""

    def test_get_joint_draw_days(
        self, sample_keno_draws, sample_lotto_draws
    ):
        """Joint days should be intersection of draw dates."""
        grid = TimelineGrid()
        grid.add_game("keno", sample_keno_draws)
        grid.add_game("lotto", sample_lotto_draws)

        # KENO is daily, Lotto is Wed+Sat
        # Joint days = Lotto draw days (subset of KENO)
        joint = grid.get_joint_draw_days()
        assert len(joint) == 2
        assert datetime(2024, 1, 3) in joint
        assert datetime(2024, 1, 6) in joint

    def test_get_joint_draw_days_specific_games(
        self, sample_keno_draws, sample_lotto_draws, sample_eurojackpot_draws
    ):
        """Joint days for specific games only."""
        grid = TimelineGrid()
        grid.add_game("keno", sample_keno_draws)
        grid.add_game("lotto", sample_lotto_draws)
        grid.add_game("eurojackpot", sample_eurojackpot_draws)

        # Only Lotto + EuroJackpot
        # Lotto: Wed(3), Sat(6)
        # EJ: Tue(2), Fri(5)
        # No overlap!
        joint = grid.get_joint_draw_days(["lotto", "eurojackpot"])
        assert len(joint) == 0


class TestTimelineGridSummary:
    """Tests for summary method."""

    def test_summary(self, sample_keno_draws):
        """Summary should contain expected fields."""
        grid = TimelineGrid()
        grid.add_game("keno", sample_keno_draws)
        summary = grid.summary()

        assert summary["start_date"] == "2024-01-01"
        assert summary["end_date"] == "2024-01-07"
        assert summary["total_days"] == 7
        assert "keno" in summary["games"]
        assert summary["fill_strategy"] == "nan"
        assert len(summary["coverage"]) == 1


class TestTimelineGridParquet:
    """Tests for Parquet export."""

    def test_to_parquet_tuple_mode(self, sample_lotto_draws, tmp_path):
        """Parquet export in tuple mode."""
        grid = TimelineGrid()
        grid.add_game("lotto", sample_lotto_draws)

        output_path = tmp_path / "timeline.parquet"
        result_path = grid.to_parquet(output_path, mode="tuple")

        assert result_path.exists()

        # Read back and verify
        df = pd.read_parquet(result_path)
        assert len(df) == 4  # 4 days (Jan 3-6, range from lotto draws)
        assert "lotto_numbers" in df.columns

    def test_to_parquet_matrix_mode(self, sample_lotto_draws, tmp_path):
        """Parquet export in matrix mode."""
        grid = TimelineGrid()
        grid.add_game("lotto", sample_lotto_draws)

        output_path = tmp_path / "timeline_matrix.parquet"
        result_path = grid.to_parquet(output_path, mode="matrix")

        assert result_path.exists()

        # Read back and verify
        df = pd.read_parquet(result_path)
        assert "lotto_z1" in df.columns


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestLoadMultiGameGrid:
    """Tests for load_multi_game_grid function."""

    def test_load_no_games_empty_grid(self):
        """No paths should return empty grid."""
        grid = load_multi_game_grid()
        assert len(grid.games) == 0

    def test_load_function_returns_timeline_grid(self):
        """Function should return TimelineGrid instance."""
        grid = load_multi_game_grid(fill_strategy="ffill")
        assert isinstance(grid, TimelineGrid)
        assert grid.fill_strategy == "ffill"

    @patch("kenobase.core.data_loader.DataLoader.load")
    def test_load_with_keno_mock(self, mock_load, sample_keno_draws):
        """Should call DataLoader.load for KENO path."""
        mock_load.return_value = sample_keno_draws

        grid = load_multi_game_grid(
            keno_path="data/keno.csv",
            fill_strategy="nan",
        )

        assert "keno" in grid.games
        mock_load.assert_called_once()
