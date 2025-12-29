"""Unit Tests for BotCore - kenobase/bot/core.py.

Tests:
- PredictionResult dataclass
- BotCore caching
- BotCore rate limiting
- BotCore formatting
"""

from __future__ import annotations

import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from kenobase.bot.core import BotCore, PredictionResult
from kenobase.bot.formatters import (
    format_short,
    format_detailed,
    format_telegram,
    format_discord,
)


class TestPredictionResult:
    """Tests fuer PredictionResult Dataclass."""

    def test_create_prediction_result(self):
        """Test Erstellung einer PredictionResult Instanz."""
        result = PredictionResult(
            numbers=[7, 14, 23, 35, 42, 56],
            tier_summary={"A": 2, "B": 3, "C": 1},
            timestamp=datetime.now(),
            game_type="keno",
            confidence=0.75,
        )

        assert result.numbers == [7, 14, 23, 35, 42, 56]
        assert result.tier_summary["A"] == 2
        assert result.game_type == "keno"
        assert result.confidence == 0.75
        assert result.cached is False

    def test_prediction_result_defaults(self):
        """Test Default-Werte von PredictionResult."""
        result = PredictionResult(
            numbers=[1, 2, 3],
            tier_summary={},
            timestamp=datetime.now(),
            game_type="keno",
        )

        assert result.confidence == 0.0
        assert result.cached is False
        assert result.details == {}


class TestBotCore:
    """Tests fuer BotCore Klasse."""

    @pytest.fixture
    def bot_config(self):
        """Standard-Config fuer Tests."""
        return {
            "cache": {
                "enabled": True,
                "ttl_seconds": 60,
            },
            "rate_limit": {
                "requests_per_minute": 5,
                "cooldown_seconds": 12,
            },
        }

    @pytest.fixture
    def bot_core(self, bot_config):
        """Erstellt BotCore Instanz."""
        return BotCore(config=bot_config, results_dir="results")

    def test_init(self, bot_core, bot_config):
        """Test BotCore Initialisierung."""
        assert bot_core.cache_enabled is True
        assert bot_core.cache_ttl == 60
        assert bot_core.rate_limit_rpm == 5
        assert bot_core.cooldown_seconds == 12

    def test_init_defaults(self):
        """Test BotCore mit leerer Config."""
        bot = BotCore(config={})

        assert bot.cache_enabled is True
        assert bot.cache_ttl == 300
        assert bot.rate_limit_rpm == 10

    def test_cache_put_and_get(self, bot_core):
        """Test Cache put/get Operationen."""
        result = PredictionResult(
            numbers=[1, 2, 3],
            tier_summary={"A": 1},
            timestamp=datetime.now(),
            game_type="keno",
        )

        # Put in cache
        bot_core._put_to_cache("test_key", result)

        # Get from cache
        cached = bot_core._get_from_cache("test_key")

        assert cached is not None
        assert cached.numbers == [1, 2, 3]
        assert cached.cached is True

    def test_cache_expiry(self, bot_config):
        """Test Cache Ablauf nach TTL."""
        # Kurzer TTL fuer Test
        bot_config["cache"]["ttl_seconds"] = 1
        bot = BotCore(config=bot_config)

        result = PredictionResult(
            numbers=[1, 2, 3],
            tier_summary={},
            timestamp=datetime.now(),
            game_type="keno",
        )

        bot._put_to_cache("test_key", result)

        # Sofort abrufen - sollte funktionieren
        assert bot._get_from_cache("test_key") is not None

        # Warten bis TTL abgelaufen
        time.sleep(1.1)

        # Jetzt sollte Cache leer sein
        assert bot._get_from_cache("test_key") is None

    def test_cache_disabled(self):
        """Test mit deaktiviertem Cache."""
        config = {
            "cache": {"enabled": False},
        }
        bot = BotCore(config=config)

        result = PredictionResult(
            numbers=[1, 2, 3],
            tier_summary={},
            timestamp=datetime.now(),
            game_type="keno",
        )

        bot._put_to_cache("test_key", result)

        # Cache disabled -> sollte None zurueckgeben
        assert bot._get_from_cache("test_key") is None

    def test_rate_limiting(self, bot_config):
        """Test Rate-Limiting Logik."""
        bot_config["rate_limit"]["requests_per_minute"] = 3
        bot = BotCore(config=bot_config)

        # Erste 3 Requests sollten durchgehen
        for _ in range(3):
            assert bot._is_rate_limited() is False
            bot._record_request()

        # 4. Request sollte blockiert werden
        assert bot._is_rate_limited() is True

    def test_rate_limit_reset(self, bot_config):
        """Test Rate-Limit Reset nach 60s."""
        bot_config["rate_limit"]["requests_per_minute"] = 1
        bot = BotCore(config=bot_config)

        # Ersten Request aufzeichnen
        bot._record_request()

        # Limit erreicht
        assert bot._is_rate_limited() is True

        # Simuliere 60s Wartezeit durch Manipulation
        bot._request_times = [time.time() - 61]

        # Limit sollte zurueckgesetzt sein
        assert bot._is_rate_limited() is False

    def test_get_numbers_range(self, bot_core):
        """Test Zahlenbereich-Lookup."""
        assert bot_core._get_numbers_range("keno") == (1, 70)
        assert bot_core._get_numbers_range("eurojackpot") == (1, 50)
        assert bot_core._get_numbers_range("lotto") == (1, 49)
        assert bot_core._get_numbers_range("unknown") == (1, 70)

    def test_get_status(self, bot_core):
        """Test Status-Report."""
        status = bot_core.get_status()

        assert "cache_enabled" in status
        assert "cache_entries" in status
        assert "rate_limit_rpm" in status
        assert "requests_last_minute" in status

    def test_clear_cache(self, bot_core):
        """Test Cache-Leerung."""
        # Fuege Eintraege hinzu
        for i in range(3):
            result = PredictionResult(
                numbers=[i],
                tier_summary={},
                timestamp=datetime.now(),
                game_type="keno",
            )
            bot_core._put_to_cache(f"key_{i}", result)

        assert len(bot_core._cache) == 3

        # Cache leeren
        count = bot_core.clear_cache()

        assert count == 3
        assert len(bot_core._cache) == 0


class TestFormatters:
    """Tests fuer Message-Formatierung."""

    @pytest.fixture
    def sample_result(self):
        """Sample PredictionResult fuer Tests."""
        return PredictionResult(
            numbers=[7, 14, 23, 35, 42, 56],
            tier_summary={"A": 2, "B": 3, "C": 1},
            timestamp=datetime(2025, 12, 28, 10, 30, 0),
            game_type="keno",
            confidence=0.75,
            cached=False,
        )

    def test_format_short(self, sample_result):
        """Test Short-Format."""
        output = format_short(sample_result)

        assert "KENO" in output
        assert "7" in output
        assert "56" in output
        assert "(cached)" not in output

    def test_format_short_cached(self, sample_result):
        """Test Short-Format mit Cache-Marker."""
        sample_result.cached = True
        output = format_short(sample_result)

        assert "(cached)" in output

    def test_format_detailed(self, sample_result):
        """Test Detailed-Format."""
        output = format_detailed(sample_result)

        assert "KENOBASE" in output
        assert "Tier-Verteilung" in output
        assert "Konfidenz: 75" in output
        assert "A (stark):   2" in output

    def test_format_telegram(self, sample_result):
        """Test Telegram-Format mit Markdown."""
        output = format_telegram(sample_result)

        # Markdown Syntax
        assert "*KENOBASE KENO*" in output
        assert "*7*" in output  # Bold numbers
        assert "Tiers:" in output
        assert "75%" in output  # Confidence

    def test_format_discord(self, sample_result):
        """Test Discord-Format."""
        output = format_discord(sample_result)

        # Discord Markdown
        assert "**KENOBASE KENO**" in output
        assert "`7`" in output  # Code blocks for numbers
        assert "```" in output  # Code block for details

    def test_all_formatters_return_string(self, sample_result):
        """Test dass alle Formatter Strings zurueckgeben."""
        formatters = [
            format_short,
            format_detailed,
            format_telegram,
            format_discord,
        ]

        for formatter in formatters:
            output = formatter(sample_result)
            assert isinstance(output, str)
            assert len(output) > 0


class TestBotCoreIntegration:
    """Integration Tests mit Mock-Synthesizer."""

    @pytest.fixture
    def mock_synthesizer(self):
        """Mock fuer HypothesisSynthesizer."""
        with patch("kenobase.bot.core.HypothesisSynthesizer") as mock:
            instance = mock.return_value
            instance.synthesize.return_value = {
                1: MagicMock(
                    number=1,
                    combined_score=0.8,
                    tier="A",
                    hypothesis_scores={},
                ),
                2: MagicMock(
                    number=2,
                    combined_score=0.6,
                    tier="B",
                    hypothesis_scores={},
                ),
            }
            yield mock

    @pytest.fixture
    def mock_recommendations(self):
        """Mock fuer generate_recommendations."""
        with patch("kenobase.bot.core.generate_recommendations") as mock:
            mock.return_value = [
                MagicMock(
                    number=1,
                    combined_score=0.8,
                    tier=MagicMock(value="A"),
                    reasons=["Test"],
                    decade=1,
                ),
                MagicMock(
                    number=2,
                    combined_score=0.6,
                    tier=MagicMock(value="B"),
                    reasons=[],
                    decade=1,
                ),
            ]
            yield mock

    @pytest.fixture
    def mock_recommendations_to_dict(self):
        """Mock fuer recommendations_to_dict."""
        with patch("kenobase.bot.core.recommendations_to_dict") as mock:
            mock.return_value = {
                "numbers": [1, 2],
                "tier_summary": {"A": 1, "B": 1, "C": 0},
                "count": 2,
                "recommendations": [],
            }
            yield mock

    def test_get_prediction_success(
        self,
        mock_synthesizer,
        mock_recommendations,
        mock_recommendations_to_dict,
    ):
        """Test erfolgreicher Prediction-Abruf."""
        bot = BotCore(config={}, results_dir="results")

        result = bot.get_prediction(game_type="keno", top_n=6)

        assert result.numbers == [1, 2]
        assert result.tier_summary["A"] == 1
        assert result.game_type == "keno"
        assert result.cached is False

    def test_get_prediction_cached(
        self,
        mock_synthesizer,
        mock_recommendations,
        mock_recommendations_to_dict,
    ):
        """Test Prediction aus Cache."""
        bot = BotCore(config={}, results_dir="results")

        # Erster Abruf
        result1 = bot.get_prediction(game_type="keno", top_n=6)
        assert result1.cached is False

        # Zweiter Abruf (sollte aus Cache kommen)
        result2 = bot.get_prediction(game_type="keno", top_n=6)
        assert result2.cached is True

        # Synthesizer sollte nur einmal aufgerufen worden sein
        assert mock_synthesizer.call_count == 1

    def test_get_prediction_force_refresh(
        self,
        mock_synthesizer,
        mock_recommendations,
        mock_recommendations_to_dict,
    ):
        """Test Force-Refresh ignoriert Cache."""
        bot = BotCore(config={}, results_dir="results")

        # Erster Abruf
        bot.get_prediction(game_type="keno", top_n=6)

        # Force-Refresh
        result = bot.get_prediction(game_type="keno", top_n=6, force_refresh=True)
        assert result.cached is False

        # Synthesizer sollte zweimal aufgerufen worden sein
        assert mock_synthesizer.call_count == 2
