# kenobase/scraper/base.py
"""Base scraper for fetching press releases from Landeslotterien websites."""

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from kenobase.scraper.landeslotterien import LANDESLOTTERIEN, LotterieConfig
from kenobase.scraper.parsers import KenoWinnerParser, KenoWinnerRecord, is_keno_article

logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    """Configuration for the press release scraper."""

    # Rate limiting
    delay_between_requests: float = 2.0  # seconds
    delay_between_sites: float = 5.0  # seconds

    # Request settings
    timeout: int = 30
    max_retries: int = 3
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Scraping limits
    max_articles_per_site: int = 50
    min_confidence: float = 0.3  # Minimum confidence to include record

    # Output
    output_dir: Path = field(default_factory=lambda: Path("data/scraped"))


@dataclass
class ScrapeResult:
    """Result of a scraping operation."""

    records: list[KenoWinnerRecord]
    errors: list[str]
    sites_scraped: int
    articles_found: int
    articles_parsed: int
    duration_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "sites_scraped": self.sites_scraped,
            "articles_found": self.articles_found,
            "articles_parsed": self.articles_parsed,
            "records_extracted": len(self.records),
            "errors_count": len(self.errors),
            "duration_seconds": round(self.duration_seconds, 2),
            "records": [r.to_dict() for r in self.records],
            "errors": self.errors,
        }


class PressReleaseScraper:
    """Scraper for Landeslotterien press releases about KENO winners."""

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize the scraper.

        Args:
            config: Scraper configuration (uses defaults if None)
        """
        self.config = config or ScraperConfig()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a configured requests session."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        })
        return session

    def scrape_all(
        self,
        codes: Optional[list[str]] = None,
        progress_callback: Optional[callable] = None,
    ) -> ScrapeResult:
        """Scrape press releases from all (or specified) Landeslotterien.

        Args:
            codes: List of lottery codes to scrape (None = all)
            progress_callback: Optional callback(code, status) for progress updates

        Returns:
            ScrapeResult with all extracted records
        """
        start_time = time.time()
        all_records: list[KenoWinnerRecord] = []
        all_errors: list[str] = []
        sites_scraped = 0
        total_articles_found = 0
        total_articles_parsed = 0

        target_codes = codes if codes else list(LANDESLOTTERIEN.keys())

        for code in target_codes:
            if progress_callback:
                progress_callback(code, "starting")

            try:
                records, articles_found, articles_parsed, errors = self._scrape_site(code)
                all_records.extend(records)
                all_errors.extend(errors)
                total_articles_found += articles_found
                total_articles_parsed += articles_parsed
                sites_scraped += 1

                if progress_callback:
                    progress_callback(code, f"done: {len(records)} records")

            except Exception as e:
                error_msg = f"[{code}] Site scrape failed: {str(e)}"
                logger.error(error_msg)
                all_errors.append(error_msg)

                if progress_callback:
                    progress_callback(code, f"error: {str(e)}")

            # Delay between sites
            time.sleep(self.config.delay_between_sites)

        duration = time.time() - start_time

        return ScrapeResult(
            records=all_records,
            errors=all_errors,
            sites_scraped=sites_scraped,
            articles_found=total_articles_found,
            articles_parsed=total_articles_parsed,
            duration_seconds=duration,
        )

    def scrape_site(self, code: str) -> ScrapeResult:
        """Scrape a single Landeslotterie site.

        Args:
            code: Lottery code (e.g., 'bayern', 'nrw')

        Returns:
            ScrapeResult for this site
        """
        start_time = time.time()
        records, articles_found, articles_parsed, errors = self._scrape_site(code)
        duration = time.time() - start_time

        return ScrapeResult(
            records=records,
            errors=errors,
            sites_scraped=1,
            articles_found=articles_found,
            articles_parsed=articles_parsed,
            duration_seconds=duration,
        )

    def _scrape_site(
        self, code: str
    ) -> tuple[list[KenoWinnerRecord], int, int, list[str]]:
        """Internal method to scrape a single site.

        Returns:
            Tuple of (records, articles_found, articles_parsed, errors)
        """
        config = LANDESLOTTERIEN.get(code)
        if not config:
            return [], 0, 0, [f"Unknown lottery code: {code}"]

        records: list[KenoWinnerRecord] = []
        errors: list[str] = []
        articles_found = 0
        articles_parsed = 0

        parser = KenoWinnerParser(config.bundesland)

        # Fetch press page
        press_url = urljoin(config.base_url, config.press_path)
        logger.info(f"[{code}] Fetching press page: {press_url}")

        try:
            response = self._fetch_url(press_url)
            if not response:
                return [], 0, 0, [f"[{code}] Failed to fetch press page"]

            soup = BeautifulSoup(response.text, "html.parser")

            # Find article links
            article_links = self._find_article_links(soup, config, press_url)
            articles_found = len(article_links)
            logger.info(f"[{code}] Found {articles_found} article links")

            # Process each article
            for url, title in article_links[: self.config.max_articles_per_site]:
                time.sleep(self.config.delay_between_requests)

                try:
                    record = self._process_article(url, title, parser, config)
                    if record:
                        articles_parsed += 1
                        if record.extraction_confidence >= self.config.min_confidence:
                            records.append(record)
                            logger.debug(
                                f"[{code}] Extracted record: {record.city or record.region} "
                                f"(confidence: {record.extraction_confidence})"
                            )
                except Exception as e:
                    error_msg = f"[{code}] Article parse error ({url}): {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)

        except Exception as e:
            errors.append(f"[{code}] Scrape error: {str(e)}")

        logger.info(
            f"[{code}] Completed: {len(records)} records from {articles_parsed} articles"
        )
        return records, articles_found, articles_parsed, errors

    def _fetch_url(self, url: str) -> Optional[requests.Response]:
        """Fetch a URL with retries."""
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(url, timeout=self.config.timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Fetch attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def _find_article_links(
        self, soup: BeautifulSoup, config: LotterieConfig, base_url: str
    ) -> list[tuple[str, str]]:
        """Find KENO-related article links on a press page.

        Returns:
            List of (url, title) tuples
        """
        links: list[tuple[str, str]] = []

        # Try multiple selectors to find article links
        selectors_to_try = [
            config.article_selector,
            "a[href*='keno']",  # Links containing 'keno' in URL
            "a[href*='KENO']",
            ".news-item a",
            ".teaser a",
            ".article-teaser a",
            ".press-item a",
            "article a",
            ".content a",
        ]

        elements = []
        for selector in selectors_to_try:
            try:
                found = soup.select(selector)
                if found:
                    elements.extend(found)
            except Exception:
                continue

        # Also search all links for KENO mentions
        all_links = soup.find_all("a", href=True)
        for link in all_links:
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if "keno" in (href + text).lower():
                if link not in elements:
                    elements.append(link)

        for element in elements:
            href = element.get("href", "")
            title = element.get_text(strip=True)

            # Skip empty links
            if not href:
                continue

            # Skip navigation/footer links
            skip_patterns = [
                "spielschein", "quoten", "statistik", "gewinnzahlen",
                "spielanleitung", "login", "registr", "javascript",
                "#", "mailto:", "tel:"
            ]
            if any(p in href.lower() for p in skip_patterns):
                continue

            # Build absolute URL
            full_url = urljoin(base_url, href)

            # Skip if not same domain
            if not full_url.startswith(config.base_url):
                continue

            # Use URL as title fallback
            if not title or len(title) < 5:
                title = href.split("/")[-1].replace("-", " ").title()

            # Avoid duplicates
            if full_url not in [l[0] for l in links]:
                links.append((full_url, title))

        return links

    def _process_article(
        self,
        url: str,
        title: str,
        parser: KenoWinnerParser,
        config: LotterieConfig,
    ) -> Optional[KenoWinnerRecord]:
        """Process a single article and extract KENO winner data."""
        response = self._fetch_url(url)
        if not response:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove navigation, footer, sidebar elements
        for tag in soup.select("nav, footer, aside, .sidebar, .navigation, .footer, .menu"):
            tag.decompose()

        # Try multiple selectors for content
        content_selectors = [
            config.content_selector,
            "article",
            ".article",
            ".article-content",
            ".article__content",
            ".press-article",
            ".news-article",
            ".content-main",
            "main",
            ".main-content",
        ]

        content_element = None
        for selector in content_selectors:
            try:
                content_element = soup.select_one(selector)
                if content_element:
                    break
            except Exception:
                continue

        if not content_element:
            content_element = soup.body

        if not content_element:
            return None

        text = content_element.get_text(separator=" ", strip=True)

        # Check if this is actually a KENO winner article
        if not is_keno_article(title, text):
            return None

        # Parse and return record
        return parser.parse(text, url, title)

    def save_results(self, result: ScrapeResult, filename: Optional[str] = None) -> Path:
        """Save scrape results to JSON file.

        Args:
            result: ScrapeResult to save
            filename: Optional filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"keno_winners_{timestamp}.json"

        output_path = self.config.output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

        logger.info(f"Results saved to: {output_path}")
        return output_path
