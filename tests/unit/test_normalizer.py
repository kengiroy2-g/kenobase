"""Unit tests for kenobase.core.normalizer module.

Tests Zahlenraum-Normalisierung for cross-lottery analysis.
"""

import pytest
from datetime import datetime

from kenobase.core.normalizer import (
    GAME_RANGES,
    EUROJACKPOT_BONUS_RANGE,
    LOTTO_BONUS_RANGE,
    get_game_range,
    normalize_number,
    denormalize_number,
    normalize_numbers,
    denormalize_numbers,
    normalize_draw,
    normalize_draws,
    cross_game_distance,
)
from kenobase.core.data_loader import DrawResult, GameType


class TestGameRanges:
    """Tests for game range constants and lookup."""

    def test_keno_range(self):
        """KENO uses 1-70."""
        assert GAME_RANGES["keno"] == (1, 70)

    def test_lotto_range(self):
        """Lotto 6aus49 uses 1-49."""
        assert GAME_RANGES["lotto"] == (1, 49)

    def test_eurojackpot_range(self):
        """EuroJackpot uses 1-50."""
        assert GAME_RANGES["eurojackpot"] == (1, 50)

    def test_eurojackpot_bonus_range(self):
        """EuroZahlen use 1-12."""
        assert EUROJACKPOT_BONUS_RANGE == (1, 12)

    def test_lotto_bonus_range(self):
        """Superzahl uses 0-9."""
        assert LOTTO_BONUS_RANGE == (0, 9)

    def test_get_game_range_with_string(self):
        """get_game_range works with string input."""
        assert get_game_range("keno") == (1, 70)
        assert get_game_range("lotto") == (1, 49)
        assert get_game_range("eurojackpot") == (1, 50)

    def test_get_game_range_with_enum(self):
        """get_game_range works with GameType enum."""
        assert get_game_range(GameType.KENO) == (1, 70)
        assert get_game_range(GameType.LOTTO) == (1, 49)
        assert get_game_range(GameType.EUROJACKPOT) == (1, 50)

    def test_get_game_range_unknown(self):
        """get_game_range raises ValueError for unknown game."""
        with pytest.raises(ValueError, match="Unknown game type"):
            get_game_range("invalid_game")


class TestNormalizeNumber:
    """Tests for normalize_number function."""

    def test_keno_min(self):
        """KENO min (1) normalizes to 0.0."""
        result = normalize_number(1, "keno")
        assert result == pytest.approx(0.0)

    def test_keno_max(self):
        """KENO max (70) normalizes to 1.0."""
        result = normalize_number(70, "keno")
        assert result == pytest.approx(1.0)

    def test_keno_mid(self):
        """KENO middle (35.5) normalizes to ~0.5."""
        # For range 1-70, midpoint is (1+70)/2 = 35.5
        # But we use integers, so 35 and 36 bracket 0.5
        result = normalize_number(35, "keno")
        assert result == pytest.approx((35 - 1) / (70 - 1))

    def test_lotto_min(self):
        """Lotto min (1) normalizes to 0.0."""
        result = normalize_number(1, "lotto")
        assert result == pytest.approx(0.0)

    def test_lotto_max(self):
        """Lotto max (49) normalizes to 1.0."""
        result = normalize_number(49, "lotto")
        assert result == pytest.approx(1.0)

    def test_eurojackpot_min(self):
        """EuroJackpot min (1) normalizes to 0.0."""
        result = normalize_number(1, "eurojackpot")
        assert result == pytest.approx(0.0)

    def test_eurojackpot_max(self):
        """EuroJackpot max (50) normalizes to 1.0."""
        result = normalize_number(50, "eurojackpot")
        assert result == pytest.approx(1.0)

    def test_with_game_type_enum(self):
        """Works with GameType enum."""
        result = normalize_number(35, GameType.KENO)
        assert result == pytest.approx((35 - 1) / (70 - 1))

    def test_out_of_range_below(self):
        """Raises ValueError for number below range."""
        with pytest.raises(ValueError, match="out of range"):
            normalize_number(0, "keno")

    def test_out_of_range_above(self):
        """Raises ValueError for number above range."""
        with pytest.raises(ValueError, match="out of range"):
            normalize_number(71, "keno")


class TestDenormalizeNumber:
    """Tests for denormalize_number function."""

    def test_keno_min(self):
        """0.0 denormalizes to KENO min (1)."""
        result = denormalize_number(0.0, "keno")
        assert result == 1

    def test_keno_max(self):
        """1.0 denormalizes to KENO max (70)."""
        result = denormalize_number(1.0, "keno")
        assert result == 70

    def test_lotto_mid(self):
        """0.5 denormalizes to Lotto middle (25)."""
        result = denormalize_number(0.5, "lotto")
        assert result == 25  # (49-1)*0.5 + 1 = 25

    def test_roundtrip_keno(self):
        """normalize -> denormalize roundtrip works for KENO."""
        for n in [1, 20, 35, 50, 70]:
            norm = normalize_number(n, "keno")
            back = denormalize_number(norm, "keno")
            assert back == n

    def test_roundtrip_lotto(self):
        """normalize -> denormalize roundtrip works for Lotto."""
        for n in [1, 10, 25, 40, 49]:
            norm = normalize_number(n, "lotto")
            back = denormalize_number(norm, "lotto")
            assert back == n

    def test_out_of_range_below(self):
        """Raises ValueError for norm < 0."""
        with pytest.raises(ValueError, match="out of range"):
            denormalize_number(-0.1, "keno")

    def test_out_of_range_above(self):
        """Raises ValueError for norm > 1."""
        with pytest.raises(ValueError, match="out of range"):
            denormalize_number(1.1, "keno")


class TestNormalizeNumbers:
    """Tests for normalize_numbers batch function."""

    def test_empty_list(self):
        """Empty list returns empty list."""
        result = normalize_numbers([], "keno")
        assert result == []

    def test_single_number(self):
        """Single number works."""
        result = normalize_numbers([35], "keno")
        assert len(result) == 1
        assert result[0] == pytest.approx((35 - 1) / (70 - 1))

    def test_multiple_numbers(self):
        """Multiple numbers work."""
        result = normalize_numbers([1, 35, 70], "keno")
        assert len(result) == 3
        assert result[0] == pytest.approx(0.0)
        assert result[2] == pytest.approx(1.0)

    def test_preserves_order(self):
        """Order is preserved."""
        numbers = [50, 10, 30, 20]
        result = normalize_numbers(numbers, "keno")
        # 50 should be > 30 in normalized space too
        assert result[0] > result[2]
        assert result[1] < result[3]  # 10 < 20


class TestDenormalizeNumbers:
    """Tests for denormalize_numbers batch function."""

    def test_empty_list(self):
        """Empty list returns empty list."""
        result = denormalize_numbers([], "keno")
        assert result == []

    def test_roundtrip(self):
        """normalize -> denormalize roundtrip works for lists."""
        original = [7, 14, 28, 42, 56]
        normalized = normalize_numbers(original, "keno")
        back = denormalize_numbers(normalized, "keno")
        assert back == original


class TestNormalizeDraw:
    """Tests for normalize_draw function."""

    def test_keno_draw(self):
        """KENO draw normalization works."""
        draw = DrawResult(
            date=datetime(2024, 1, 15),
            numbers=[1, 20, 35, 50, 70],
            bonus=[],  # KENO Plus5 is a 5-digit number, not normalized as lottery number
            game_type=GameType.KENO,
            metadata={"test": "value"},
        )

        result = normalize_draw(draw)

        assert result["date"] == datetime(2024, 1, 15)
        assert result["game_type"] == GameType.KENO
        assert len(result["numbers"]) == 5
        assert result["numbers"][0] == pytest.approx(0.0)  # 1 -> 0.0
        assert result["numbers"][4] == pytest.approx(1.0)  # 70 -> 1.0
        assert result["original_numbers"] == [1, 20, 35, 50, 70]
        assert result["metadata"] == {"test": "value"}

    def test_eurojackpot_draw(self):
        """EuroJackpot draw with bonus normalization works."""
        draw = DrawResult(
            date=datetime(2024, 1, 15),
            numbers=[1, 13, 25, 38, 50],  # 5 main numbers
            bonus=[1, 12],  # EuroZahlen
            game_type=GameType.EUROJACKPOT,
        )

        result = normalize_draw(draw)

        assert len(result["numbers"]) == 5
        assert result["numbers"][0] == pytest.approx(0.0)  # 1 -> 0.0
        assert result["numbers"][4] == pytest.approx(1.0)  # 50 -> 1.0
        # Bonus: EuroZahlen 1-12
        assert len(result["bonus"]) == 2
        assert result["bonus"][0] == pytest.approx(0.0)  # 1 -> 0.0
        assert result["bonus"][1] == pytest.approx(1.0)  # 12 -> 1.0

    def test_lotto_draw(self):
        """Lotto draw with Superzahl normalization works."""
        draw = DrawResult(
            date=datetime(2024, 1, 15),
            numbers=[1, 10, 25, 40, 49, 6],  # 6 main numbers
            bonus=[5],  # Superzahl 0-9
            game_type=GameType.LOTTO,
        )

        result = normalize_draw(draw)

        # Numbers are sorted by DrawResult validator
        assert len(result["numbers"]) == 6
        # Bonus: Superzahl 0-9, so 5 -> 0.5 (middle)
        assert len(result["bonus"]) == 1
        assert result["bonus"][0] == pytest.approx(0.5555555555555556)  # (5-0)/(9-0)


class TestNormalizeDraws:
    """Tests for normalize_draws batch function."""

    def test_empty_list(self):
        """Empty list returns empty list."""
        result = normalize_draws([])
        assert result == []

    def test_multiple_draws(self):
        """Multiple draws work."""
        draws = [
            DrawResult(
                date=datetime(2024, 1, 15),
                numbers=[1, 20, 35, 50, 70] + list(range(2, 17)),  # 20 numbers
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2024, 1, 16),
                numbers=[5, 15, 25, 35, 45] + list(range(6, 21)),  # 20 numbers
                game_type=GameType.KENO,
            ),
        ]

        result = normalize_draws(draws)

        assert len(result) == 2
        assert result[0]["date"] == datetime(2024, 1, 15)
        assert result[1]["date"] == datetime(2024, 1, 16)


class TestCrossGameDistance:
    """Tests for cross_game_distance function."""

    def test_identical_normalized_values(self):
        """Numbers at same relative position have zero distance."""
        # KENO 35.5 is middle of 1-70, Lotto 25 is middle of 1-49
        # But since we use integers, we need to be careful
        # KENO 35 -> (35-1)/(70-1) = 0.4927...
        # Lotto 25 -> (25-1)/(49-1) = 0.5
        # These are close but not identical
        distance = cross_game_distance([35], "keno", [25], "lotto")
        assert distance < 0.01  # Very close

    def test_max_distance(self):
        """Min vs max has distance ~1.0."""
        # KENO 1 (0.0) vs Lotto 49 (1.0)
        distance = cross_game_distance([1], "keno", [49], "lotto")
        assert distance == pytest.approx(1.0)

    def test_empty_lists(self):
        """Empty lists return 0.0."""
        distance = cross_game_distance([], "keno", [], "lotto")
        assert distance == 0.0

    def test_unequal_lengths(self):
        """Uses shorter list length."""
        # [1, 70] vs [1] -> only compares first element
        distance = cross_game_distance([1, 70], "keno", [1], "lotto")
        # 1/70 range vs 1/49 range: both are 0.0
        assert distance == pytest.approx(0.0)

    def test_symmetric(self):
        """Distance is symmetric."""
        d1 = cross_game_distance([35], "keno", [25], "lotto")
        d2 = cross_game_distance([25], "lotto", [35], "keno")
        assert d1 == pytest.approx(d2)

    def test_with_game_type_enum(self):
        """Works with GameType enum."""
        distance = cross_game_distance(
            [35], GameType.KENO, [25], GameType.LOTTO
        )
        assert distance < 0.01


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_cross_game_comparison_workflow(self):
        """Full workflow: load draws, normalize, compare."""
        # Simulate KENO draw
        keno_draw = DrawResult(
            date=datetime(2024, 1, 15),
            numbers=[7, 14, 21, 28, 35, 42, 49, 56, 63, 70] + list(range(1, 11)),
            game_type=GameType.KENO,
        )

        # Simulate Lotto draw
        lotto_draw = DrawResult(
            date=datetime(2024, 1, 15),
            numbers=[7, 14, 21, 28, 35, 42],
            game_type=GameType.LOTTO,
        )

        # Normalize both
        keno_norm = normalize_draw(keno_draw)
        lotto_norm = normalize_draw(lotto_draw)

        # Both have numbers in normalized space
        assert 0.0 <= keno_norm["numbers"][0] <= 1.0
        assert 0.0 <= lotto_norm["numbers"][0] <= 1.0

        # Compare first 6 numbers
        distance = cross_game_distance(
            keno_draw.numbers[:6],
            GameType.KENO,
            lotto_draw.numbers,
            GameType.LOTTO,
        )

        # Distance should be reasonable (not 0, not 1)
        assert 0.0 < distance < 1.0
