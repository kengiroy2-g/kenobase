# kenobase/scraper/lotto_hessen_api.py
"""Lotto Hessen API client for KENO winner data.

Lotto Hessen provides a JSON API for press releases and winner data.
This is an automated alternative to web scraping.

API Endpoints discovered:
- https://www.lotto-hessen.de/api/magazin/meldungen (press releases)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional

import requests

from kenobase.core.regions import normalize_region
from kenobase.scraper.parsers import KenoWinnerParser, KenoWinnerRecord

logger = logging.getLogger(__name__)


@dataclass
class LottoHessenConfig:
    """Configuration for Lotto Hessen API client."""

    base_url: str = "https://www.lotto-hessen.de"
    api_path: str = "/api/magazin/meldungen"
    timeout: int = 30
    max_articles: int = 100
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )


class LottoHessenAPI:
    """Client for Lotto Hessen API.

    Provides programmatic access to KENO winner press releases
    via JSON API (more reliable than HTML scraping).
    """

    def __init__(self, config: Optional[LottoHessenConfig] = None):
        """Initialize the API client.

        Args:
            config: API configuration (uses defaults if None)
        """
        self.config = config or LottoHessenConfig()
        self.session = self._create_session()
        self.parser = KenoWinnerParser("Hessen")

    def _create_session(self) -> requests.Session:
        """Create a configured requests session."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "application/json",
            "Accept-Language": "de-DE,de;q=0.9",
        })
        return session

    def fetch_articles(self) -> list[dict]:
        """Fetch article list from API.

        Returns:
            List of article metadata dicts
        """
        url = f"{self.config.base_url}{self.config.api_path}"
        logger.info(f"Fetching articles from {url}")

        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()

            data = response.json()

            # API may return different structures - adapt as needed
            if isinstance(data, list):
                articles = data
            elif isinstance(data, dict):
                articles = data.get("items", data.get("articles", []))
            else:
                logger.warning(f"Unexpected API response type: {type(data)}")
                articles = []

            logger.info(f"Found {len(articles)} articles")
            return articles[: self.config.max_articles]

        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            return []

    def is_keno_article(self, article: dict) -> bool:
        """Check if an article is about KENO winners.

        Args:
            article: Article metadata dict

        Returns:
            True if article is KENO-related
        """
        # Check title and content for KENO keywords
        title = article.get("title", "").lower()
        content = article.get("content", article.get("teaser", "")).lower()

        keno_keywords = ["keno", "keno-gewinn", "keno-spieler"]
        winner_keywords = ["gewinn", "gewinner", "volltreffer", "hauptgewinn"]

        has_keno = any(kw in title or kw in content for kw in keno_keywords)
        has_winner = any(kw in title or kw in content for kw in winner_keywords)

        return has_keno and has_winner

    def parse_article(self, article: dict) -> Optional[KenoWinnerRecord]:
        """Parse a KENO winner article.

        Args:
            article: Article metadata dict

        Returns:
            KenoWinnerRecord or None if parsing fails
        """
        title = article.get("title", "")
        content = article.get("content", article.get("teaser", ""))
        url = article.get("url", article.get("link", ""))

        if not url.startswith("http"):
            url = f"{self.config.base_url}{url}"

        # Use existing parser
        text = f"{title}\n\n{content}"
        record = self.parser.parse(text, url, title)

        # Parse publish date if available
        if article.get("date"):
            try:
                record.publish_date = datetime.fromisoformat(
                    article["date"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        return record if record.extraction_confidence >= 0.3 else None

    def fetch_keno_winners(self) -> list[KenoWinnerRecord]:
        """Fetch and parse all KENO winner articles.

        Returns:
            List of KenoWinnerRecord objects
        """
        articles = self.fetch_articles()
        records: list[KenoWinnerRecord] = []

        for article in articles:
            if self.is_keno_article(article):
                record = self.parse_article(article)
                if record:
                    records.append(record)
                    logger.debug(
                        f"Extracted: {record.city or record.region} "
                        f"(confidence: {record.extraction_confidence})"
                    )

        logger.info(f"Extracted {len(records)} KENO winner records")
        return records


def fetch_hessen_winners() -> list[KenoWinnerRecord]:
    """Convenience function to fetch Hessen winners.

    Returns:
        List of KenoWinnerRecord objects from Hessen
    """
    client = LottoHessenAPI()
    return client.fetch_keno_winners()


__all__ = [
    "LottoHessenConfig",
    "LottoHessenAPI",
    "fetch_hessen_winners",
]
