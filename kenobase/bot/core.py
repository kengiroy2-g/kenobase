"""BotCore - Zentraler Bot-Service mit Caching.

Orchestriert Prediction-Abrufe und verwaltet Cache fuer Rate-Limiting.
Integriert mit kenobase.prediction.recommendation fuer Zahlenempfehlungen.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from kenobase.prediction.synthesizer import HypothesisSynthesizer
from kenobase.prediction.recommendation import (
    generate_recommendations,
    recommendations_to_dict,
    format_recommendations,
)

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Ergebnis einer Prediction-Anfrage."""

    numbers: list[int]
    tier_summary: dict[str, int]
    timestamp: datetime
    game_type: str
    confidence: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    cached: bool = False


class BotCore:
    """Zentraler Bot-Service mit Prediction-Cache.

    Verwaltet Prediction-Abrufe mit Caching und Rate-Limiting.
    Integriert mit kenobase.prediction.recommendation.

    Attributes:
        config: Bot-Konfiguration aus YAML.
        cache_ttl: Cache Time-to-Live in Sekunden (default 300).
        rate_limit_rpm: Max Requests pro Minute (default 10).
    """

    def __init__(
        self,
        config: dict,
        results_dir: str = "results",
    ):
        """Initialisiert BotCore.

        Args:
            config: Bot-Konfiguration (bot: Section aus YAML).
            results_dir: Pfad zum HYP-Ergebnis-Verzeichnis.
        """
        self.config = config
        self.results_dir = Path(results_dir)

        # Cache-Konfiguration
        cache_config = config.get("cache", {})
        self.cache_enabled = cache_config.get("enabled", True)
        self.cache_ttl = cache_config.get("ttl_seconds", 300)

        # Rate-Limiting
        rate_config = config.get("rate_limit", {})
        self.rate_limit_rpm = rate_config.get("requests_per_minute", 10)
        self.cooldown_seconds = rate_config.get("cooldown_seconds", 6)

        # Interner State
        self._cache: dict[str, tuple[PredictionResult, float]] = {}
        self._request_times: list[float] = []

        logger.info(
            f"BotCore initialized: cache_ttl={self.cache_ttl}s, "
            f"rate_limit={self.rate_limit_rpm}/min"
        )

    def _is_rate_limited(self) -> bool:
        """Prueft ob Rate-Limit erreicht ist.

        Returns:
            True wenn Limit erreicht, False sonst.
        """
        now = time.time()
        # Entferne alte Requests (aelter als 60s)
        self._request_times = [t for t in self._request_times if now - t < 60]

        if len(self._request_times) >= self.rate_limit_rpm:
            logger.warning(
                f"Rate limit reached: {len(self._request_times)}/{self.rate_limit_rpm} rpm"
            )
            return True
        return False

    def _record_request(self) -> None:
        """Zeichnet einen Request fuer Rate-Limiting auf."""
        self._request_times.append(time.time())

    def _get_from_cache(self, cache_key: str) -> Optional[PredictionResult]:
        """Holt Prediction aus Cache wenn gueltig.

        Args:
            cache_key: Cache-Schluessel (z.B. "keno").

        Returns:
            PredictionResult wenn im Cache und nicht abgelaufen, sonst None.
        """
        if not self.cache_enabled:
            return None

        if cache_key in self._cache:
            result, cached_time = self._cache[cache_key]
            age = time.time() - cached_time

            if age < self.cache_ttl:
                logger.debug(f"Cache hit for {cache_key} (age: {age:.1f}s)")
                result.cached = True
                return result
            else:
                logger.debug(f"Cache expired for {cache_key} (age: {age:.1f}s)")
                del self._cache[cache_key]

        return None

    def _put_to_cache(self, cache_key: str, result: PredictionResult) -> None:
        """Speichert Prediction im Cache.

        Args:
            cache_key: Cache-Schluessel.
            result: Zu cachende PredictionResult.
        """
        if self.cache_enabled:
            self._cache[cache_key] = (result, time.time())
            logger.debug(f"Cached prediction for {cache_key}")

    def get_prediction(
        self,
        game_type: str = "keno",
        top_n: int = 6,
        force_refresh: bool = False,
    ) -> PredictionResult:
        """Ruft Prediction ab (cached wenn moeglich).

        Args:
            game_type: Spieltyp ("keno", "eurojackpot", "lotto").
            top_n: Anzahl empfohlener Zahlen.
            force_refresh: Ignoriere Cache wenn True.

        Returns:
            PredictionResult mit Zahlenempfehlungen.

        Raises:
            RuntimeError: Bei Rate-Limiting oder Fehlern.
        """
        cache_key = f"{game_type}_{top_n}"
        start_time = time.time()

        # Cache-Check
        if not force_refresh:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        # Rate-Limiting
        if self._is_rate_limited():
            raise RuntimeError(
                f"Rate limit exceeded. Please wait {self.cooldown_seconds}s."
            )

        self._record_request()

        try:
            # Lade Synthesizer und generiere Recommendations
            synthesizer = HypothesisSynthesizer(
                results_dir=str(self.results_dir),
                numbers_range=self._get_numbers_range(game_type),
            )
            scores = synthesizer.synthesize()
            recommendations = generate_recommendations(
                scores,
                top_n=top_n,
                max_per_decade=2,
                anti_avalanche_limit=4,
            )

            # Erstelle Result
            rec_dict = recommendations_to_dict(recommendations)
            result = PredictionResult(
                numbers=rec_dict["numbers"],
                tier_summary=rec_dict["tier_summary"],
                timestamp=datetime.now(),
                game_type=game_type,
                confidence=self._calculate_confidence(recommendations),
                details=rec_dict,
                cached=False,
            )

            # Cache speichern
            self._put_to_cache(cache_key, result)

            elapsed = time.time() - start_time
            logger.info(
                f"Prediction generated for {game_type}: "
                f"{result.numbers} in {elapsed:.2f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Prediction failed for {game_type}: {e}")
            raise RuntimeError(f"Prediction failed: {e}") from e

    def _get_numbers_range(self, game_type: str) -> tuple[int, int]:
        """Gibt Zahlenbereich fuer Spieltyp zurueck.

        Args:
            game_type: Spieltyp.

        Returns:
            Tuple (min, max) fuer Zahlenbereich.
        """
        ranges = {
            "keno": (1, 70),
            "eurojackpot": (1, 50),
            "lotto": (1, 49),
        }
        return ranges.get(game_type, (1, 70))

    def _calculate_confidence(self, recommendations: list) -> float:
        """Berechnet Konfidenz basierend auf Tier-Verteilung.

        Args:
            recommendations: Liste von Recommendation.

        Returns:
            Konfidenz-Score (0.0-1.0).
        """
        if not recommendations:
            return 0.0

        tier_scores = {"A": 1.0, "B": 0.6, "C": 0.3}
        total = sum(tier_scores.get(r.tier.value, 0.3) for r in recommendations)
        return total / len(recommendations)

    def format_prediction(
        self,
        result: PredictionResult,
        style: str = "short",
    ) -> str:
        """Formatiert Prediction fuer Bot-Ausgabe.

        Args:
            result: PredictionResult zum Formatieren.
            style: Ausgabe-Stil ("short", "detailed", "telegram", "discord").

        Returns:
            Formatierter String.
        """
        from kenobase.bot.formatters import (
            format_short,
            format_detailed,
            format_telegram,
            format_discord,
        )

        formatters = {
            "short": format_short,
            "detailed": format_detailed,
            "telegram": format_telegram,
            "discord": format_discord,
        }

        formatter = formatters.get(style, format_short)
        return formatter(result)

    def get_status(self) -> dict:
        """Gibt Bot-Status zurueck.

        Returns:
            Dict mit Status-Informationen.
        """
        now = time.time()
        recent_requests = len([t for t in self._request_times if now - t < 60])

        return {
            "cache_enabled": self.cache_enabled,
            "cache_entries": len(self._cache),
            "cache_ttl_seconds": self.cache_ttl,
            "rate_limit_rpm": self.rate_limit_rpm,
            "requests_last_minute": recent_requests,
            "rate_limit_remaining": self.rate_limit_rpm - recent_requests,
            "results_dir": str(self.results_dir),
            "results_dir_exists": self.results_dir.exists(),
        }

    def clear_cache(self) -> int:
        """Leert den Prediction-Cache.

        Returns:
            Anzahl der geloeschten Cache-Eintraege.
        """
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared {count} cache entries")
        return count


def create_bot_core_from_config(config_path: str = "config/default.yaml") -> BotCore:
    """Erstellt BotCore aus YAML-Config.

    Args:
        config_path: Pfad zur YAML-Config.

    Returns:
        Konfigurierter BotCore.
    """
    import yaml

    with open(config_path, "r", encoding="utf-8") as f:
        full_config = yaml.safe_load(f)

    bot_config = full_config.get("bot", {})
    results_dir = full_config.get("paths", {}).get("output_dir", "results")

    return BotCore(config=bot_config, results_dir=results_dir)


__all__ = ["BotCore", "PredictionResult", "create_bot_core_from_config"]
