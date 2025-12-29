# kenobase/scraper/lotto_de.py
"""Scraper for official KENO data from lotto.de (DLTB central source)."""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class KenoDrawResult:
    """Single KENO draw result from lotto.de."""

    date: datetime
    numbers: list[int]  # 20 winning numbers
    plus5: Optional[str] = None  # Plus5 winning number

    # Winner counts per KENO type (available since 2017-12-29)
    winners_by_type: Optional[dict[int, dict[int, int]]] = None
    # Format: {keno_type: {matches: winner_count}}
    # e.g., {10: {10: 0, 9: 5, 8: 42, ...}, 9: {...}, ...}

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "numbers": self.numbers,
            "plus5": self.plus5,
            "winners_by_type": self.winners_by_type,
        }

    @property
    def birthday_score(self) -> float:
        """Calculate percentage of birthday numbers (1-31)."""
        birthday_count = sum(1 for n in self.numbers if 1 <= n <= 31)
        return birthday_count / len(self.numbers)

    @property
    def total_winners(self) -> Optional[int]:
        """Calculate total number of winners across all types."""
        if not self.winners_by_type:
            return None
        total = 0
        for type_winners in self.winners_by_type.values():
            total += sum(type_winners.values())
        return total


@dataclass
class LottoDeScraper:
    """Scraper for official KENO data via Lotto Hessen API.

    API Base: https://services.lotto-hessen.de/spielinformationen/

    Endpoints:
        - /gewinnzahlen/keno - Current KENO numbers (20 Zahlen)
        - /quoten/keno - Current KENO quotes
        - /gewinnzahlen/lotto - Lotto 6aus49
        - /gewinnzahlen/eurojackpot - EuroJackpot
    """

    # Lotto Hessen API (official JSON source)
    api_base: str = "https://services.lotto-hessen.de/spielinformationen"
    keno_numbers_url: str = "https://services.lotto-hessen.de/spielinformationen/gewinnzahlen/keno"
    keno_quoten_url: str = "https://services.lotto-hessen.de/spielinformationen/quoten/keno"

    # Fallback: lotto.de website
    web_base_url: str = "https://www.lotto.de"
    keno_archive_url: str = "https://www.lotto.de/keno/zahlen"

    # Rate limiting
    delay_between_requests: float = 1.0
    timeout: int = 30

    # Session
    session: requests.Session = field(default_factory=requests.Session)

    def __post_init__(self):
        """Configure session."""
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        })

    def fetch_current(self) -> Optional[KenoDrawResult]:
        """Fetch current KENO draw from API.

        Returns:
            KenoDrawResult with today's numbers
        """
        try:
            resp = self.session.get(self.keno_numbers_url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            # Parse response
            # Format: {"Datum": "27.12.2025", "Ziehung": "Samstag", "Zahl": [9, 61, ...]}
            date_str = data.get("Datum", "")
            numbers = data.get("Zahl", [])

            if not date_str or len(numbers) != 20:
                logger.warning(f"Invalid API response: {data}")
                return None

            # Parse date
            date = datetime.strptime(date_str, "%d.%m.%Y")

            return KenoDrawResult(
                date=date,
                numbers=sorted(numbers),
                plus5=None,  # Not in this API
                winners_by_type=None,  # Not in this API
            )

        except Exception as e:
            logger.error(f"API fetch failed: {e}")
            return None

    def fetch_draw(self, date: datetime) -> Optional[KenoDrawResult]:
        """Fetch KENO draw result for a specific date.

        Args:
            date: Date to fetch (KENO draws happen daily)

        Returns:
            KenoDrawResult or None if not found
        """
        # Format date for URL
        date_str = date.strftime("%d.%m.%Y")
        url = f"{self.keno_archive_url}?datum={date_str}"

        logger.debug(f"Fetching KENO draw for {date_str}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

        return self._parse_draw_page(response.text, date)

    def fetch_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        progress_callback: Optional[callable] = None,
    ) -> list[KenoDrawResult]:
        """Fetch KENO draws for a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            progress_callback: Optional callback(current_date, total_days)

        Returns:
            List of KenoDrawResult
        """
        results: list[KenoDrawResult] = []
        current = start_date
        total_days = (end_date - start_date).days + 1

        while current <= end_date:
            if progress_callback:
                days_done = (current - start_date).days + 1
                progress_callback(current, days_done, total_days)

            result = self.fetch_draw(current)
            if result:
                results.append(result)
                logger.info(
                    f"[{current.strftime('%Y-%m-%d')}] "
                    f"Numbers: {len(result.numbers)}, "
                    f"Winners: {result.total_winners or 'N/A'}"
                )

            current += timedelta(days=1)
            time.sleep(self.delay_between_requests)

        return results

    def fetch_recent(self, days: int = 30) -> list[KenoDrawResult]:
        """Fetch recent KENO draws.

        Args:
            days: Number of days to fetch (default: 30)

        Returns:
            List of KenoDrawResult
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return self.fetch_date_range(start_date, end_date)

    def _parse_draw_page(
        self, html: str, expected_date: datetime
    ) -> Optional[KenoDrawResult]:
        """Parse KENO draw page HTML.

        Args:
            html: Page HTML content
            expected_date: Expected draw date

        Returns:
            KenoDrawResult or None
        """
        soup = BeautifulSoup(html, "html.parser")

        # Extract winning numbers
        numbers = self._extract_numbers(soup)
        if not numbers or len(numbers) != 20:
            logger.warning(f"Could not extract 20 numbers for {expected_date}")
            return None

        # Extract Plus5
        plus5 = self._extract_plus5(soup)

        # Extract winner counts (available since 2017-12-29)
        winners = self._extract_winners(soup)

        return KenoDrawResult(
            date=expected_date,
            numbers=numbers,
            plus5=plus5,
            winners_by_type=winners,
        )

    def _extract_numbers(self, soup: BeautifulSoup) -> list[int]:
        """Extract 20 KENO winning numbers from page."""
        numbers = []

        # Try various selectors for number elements
        selectors = [
            ".keno-numbers .number",
            ".gewinnzahlen .zahl",
            ".winning-numbers span",
            "[class*='keno'] [class*='number']",
            ".zahlen .zahl",
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for el in elements:
                    text = el.get_text(strip=True)
                    if text.isdigit():
                        num = int(text)
                        if 1 <= num <= 70:
                            numbers.append(num)
                if len(numbers) == 20:
                    return sorted(numbers)
                numbers = []

        # Fallback: search for pattern in text
        text = soup.get_text()
        # Look for 20 consecutive 1-2 digit numbers
        pattern = r"\b([1-9]|[1-6][0-9]|70)\b"
        matches = re.findall(pattern, text)

        # Filter to plausible KENO numbers and take first 20 unique
        seen = set()
        for m in matches:
            num = int(m)
            if 1 <= num <= 70 and num not in seen:
                numbers.append(num)
                seen.add(num)
            if len(numbers) == 20:
                break

        return sorted(numbers) if len(numbers) == 20 else []

    def _extract_plus5(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract Plus5 winning number."""
        selectors = [
            ".plus5 .number",
            ".plus-5 .zahl",
            "[class*='plus5']",
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if re.match(r"^\d{5}$", text):
                    return text

        # Fallback: search for 5-digit number after "plus 5" text
        text = soup.get_text()
        match = re.search(r"plus\s*5[:\s]*(\d{5})", text, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def _extract_winners(
        self, soup: BeautifulSoup
    ) -> Optional[dict[int, dict[int, int]]]:
        """Extract winner counts per KENO type and match count.

        Returns:
            Dict mapping keno_type -> {matches -> winner_count}
            e.g., {10: {10: 0, 9: 5, 8: 42}, 9: {9: 2, 8: 15}, ...}
        """
        winners: dict[int, dict[int, int]] = {}

        # Look for winner tables
        tables = soup.select("table")

        for table in tables:
            rows = table.select("tr")
            for row in rows:
                cells = row.select("td, th")
                if len(cells) >= 3:
                    # Try to parse: Type, Richtige, Gewinner
                    try:
                        type_text = cells[0].get_text(strip=True)
                        matches_text = cells[1].get_text(strip=True)
                        winners_text = cells[2].get_text(strip=True)

                        # Parse keno type
                        type_match = re.search(r"\d+", type_text)
                        if not type_match:
                            continue
                        keno_type = int(type_match.group())
                        if not (2 <= keno_type <= 10):
                            continue

                        # Parse matches
                        matches_match = re.search(r"\d+", matches_text)
                        if not matches_match:
                            continue
                        matches = int(matches_match.group())

                        # Parse winner count
                        winners_clean = winners_text.replace(".", "").replace(",", "")
                        winner_match = re.search(r"\d+", winners_clean)
                        if not winner_match:
                            continue
                        winner_count = int(winner_match.group())

                        if keno_type not in winners:
                            winners[keno_type] = {}
                        winners[keno_type][matches] = winner_count

                    except (ValueError, IndexError):
                        continue

        return winners if winners else None

    def save_results(
        self,
        results: list[KenoDrawResult],
        output_path: Path,
    ) -> None:
        """Save results to JSON file.

        Args:
            results: List of draw results
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "source": "lotto.de",
            "generated_at": datetime.now().isoformat(),
            "count": len(results),
            "draws": [r.to_dict() for r in results],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(results)} draws to {output_path}")


def analyze_birthday_correlation(results: list[KenoDrawResult]) -> dict:
    """Analyze correlation between birthday numbers and winner counts.

    Hypothesis: More birthday numbers (1-31) = more winners
    (because people often pick birth dates)

    Args:
        results: List of draw results with winner counts

    Returns:
        Analysis results
    """
    # Filter to draws with winner data
    draws_with_winners = [r for r in results if r.total_winners is not None]

    if not draws_with_winners:
        return {"error": "No winner data available"}

    # Calculate correlation
    birthday_scores = [r.birthday_score for r in draws_with_winners]
    winner_counts = [r.total_winners for r in draws_with_winners]

    # Simple correlation calculation
    n = len(birthday_scores)
    mean_bs = sum(birthday_scores) / n
    mean_wc = sum(winner_counts) / n

    numerator = sum(
        (bs - mean_bs) * (wc - mean_wc)
        for bs, wc in zip(birthday_scores, winner_counts)
    )
    denominator_bs = sum((bs - mean_bs) ** 2 for bs in birthday_scores) ** 0.5
    denominator_wc = sum((wc - mean_wc) ** 2 for wc in winner_counts) ** 0.5

    if denominator_bs * denominator_wc == 0:
        correlation = 0.0
    else:
        correlation = numerator / (denominator_bs * denominator_wc)

    # Categorize draws
    high_birthday = [r for r in draws_with_winners if r.birthday_score > 0.5]
    low_birthday = [r for r in draws_with_winners if r.birthday_score < 0.35]

    avg_winners_high = (
        sum(r.total_winners for r in high_birthday) / len(high_birthday)
        if high_birthday
        else 0
    )
    avg_winners_low = (
        sum(r.total_winners for r in low_birthday) / len(low_birthday)
        if low_birthday
        else 0
    )

    return {
        "total_draws_analyzed": len(draws_with_winners),
        "correlation_birthday_vs_winners": round(correlation, 4),
        "interpretation": (
            "BESTAETIGT: Mehr Birthday-Zahlen = mehr Gewinner"
            if correlation > 0.1
            else "NICHT SIGNIFIKANT"
            if -0.1 <= correlation <= 0.1
            else "INVERS: Weniger Birthday-Zahlen = mehr Gewinner"
        ),
        "high_birthday_draws": len(high_birthday),
        "low_birthday_draws": len(low_birthday),
        "avg_winners_high_birthday": round(avg_winners_high, 1),
        "avg_winners_low_birthday": round(avg_winners_low, 1),
        "winner_ratio": (
            round(avg_winners_high / avg_winners_low, 2)
            if avg_winners_low > 0
            else None
        ),
    }
