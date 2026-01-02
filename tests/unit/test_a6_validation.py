# tests/unit/test_a6_validation.py
"""Unit tests for A6 Axiom validation."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kenobase.core.data_loader import DrawResult, GameType


class TestA6Validation:
    """Tests for A6 regional distribution validation."""

    def test_count_wins_by_bundesland(self):
        """Test counting wins per Bundesland."""
        # Import here to avoid import errors in other tests
        from scripts.validate_a6_regional import count_wins_by_bundesland

        # Create mock DrawResults
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 2, 3],
                bonus=[],
                game_type=GameType.KENO,
                metadata={"bundesland": "Bayern"},
            ),
            DrawResult(
                date=datetime(2024, 1, 2),
                numbers=[4, 5, 6],
                bonus=[],
                game_type=GameType.KENO,
                metadata={"bundesland": "bayern"},  # lowercase
            ),
            DrawResult(
                date=datetime(2024, 1, 3),
                numbers=[7, 8, 9],
                bonus=[],
                game_type=GameType.KENO,
                metadata={"bundesland": "NRW"},  # alias
            ),
        ]

        counts = count_wins_by_bundesland(draws)

        assert counts["bayern"] == 2
        assert counts["nordrhein-westfalen"] == 1
        assert counts["berlin"] == 0

    def test_population_data_complete(self):
        """Test that all 16 Bundeslaender have population data."""
        from scripts.validate_a6_regional import BUNDESLAND_POPULATION
        from kenobase.core.regions import GERMAN_REGIONS

        # All GERMAN_REGIONS should have population data
        for region in GERMAN_REGIONS:
            assert region in BUNDESLAND_POPULATION, f"Missing population for {region}"

        # Population should be positive
        for region, pop in BUNDESLAND_POPULATION.items():
            assert pop > 0, f"Invalid population for {region}: {pop}"

        # Should be 16 Bundeslaender
        assert len(BUNDESLAND_POPULATION) == 16

    def test_validate_p61_with_correlated_data(self):
        """Test P6.1 with data that correlates with population."""
        from scripts.validate_a6_regional import (
            validate_p61_population_correlation,
            BUNDESLAND_POPULATION,
        )

        # Create wins proportional to population
        wins = {
            bl: int(pop * 10)  # Scale up for integer counts
            for bl, pop in BUNDESLAND_POPULATION.items()
        }

        result = validate_p61_population_correlation(wins)

        # Should pass with high correlation
        assert result["passed"]  # numpy bool comparison
        assert result["observed_value"] > 0.9  # Should be near 1.0

    def test_validate_p61_with_random_data(self):
        """Test P6.1 with random distribution (should fail)."""
        from scripts.validate_a6_regional import validate_p61_population_correlation

        # Random wins - not correlated with population
        wins = {
            "nordrhein-westfalen": 1,  # Largest but only 1 win
            "bremen": 10,  # Smallest but 10 wins
            "bayern": 0,
            "baden-wuerttemberg": 0,
            "niedersachsen": 0,
            "hessen": 0,
            "rheinland-pfalz": 0,
            "sachsen": 0,
            "berlin": 0,
            "schleswig-holstein": 0,
            "brandenburg": 0,
            "sachsen-anhalt": 0,
            "thueringen": 0,
            "hamburg": 0,
            "mecklenburg-vorpommern": 0,
            "saarland": 0,
        }

        result = validate_p61_population_correlation(wins)

        # Should fail (r < 0.5)
        assert result["observed_value"] < 0.5


class TestLottoHessenAPI:
    """Tests for Lotto Hessen API client."""

    def test_api_config_defaults(self):
        """Test default API configuration."""
        from kenobase.scraper.lotto_hessen_api import LottoHessenConfig

        config = LottoHessenConfig()

        assert config.base_url == "https://www.lotto-hessen.de"
        assert config.api_path == "/api/magazin/meldungen"
        assert config.timeout == 30
        assert config.max_articles == 100

    def test_is_keno_article_positive(self):
        """Test KENO article detection - positive case."""
        from kenobase.scraper.lotto_hessen_api import LottoHessenAPI

        api = LottoHessenAPI()

        article = {
            "title": "KENO-Spieler aus Frankfurt gewinnt 100.000 Euro",
            "content": "Ein Tipper hat beim KENO den Hauptgewinn abgeraumt.",
        }

        assert api.is_keno_article(article) is True

    def test_is_keno_article_negative(self):
        """Test KENO article detection - negative case."""
        from kenobase.scraper.lotto_hessen_api import LottoHessenAPI

        api = LottoHessenAPI()

        article = {
            "title": "Lotto 6aus49 Ziehung vom Samstag",
            "content": "Die Gewinnzahlen sind: 5, 12, 23, 34, 45, 49",
        }

        assert api.is_keno_article(article) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
