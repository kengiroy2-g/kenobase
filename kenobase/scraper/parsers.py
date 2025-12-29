# kenobase/scraper/parsers.py
"""Parsers for extracting KENO winner information from press releases."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class KenoWinnerRecord:
    """Represents a KENO winner extracted from a press release."""

    # Required fields
    bundesland: str
    source_url: str

    # Extracted fields (may be None if not found)
    city: Optional[str] = None
    region: Optional[str] = None  # Landkreis, Oberbayern, etc.
    numbers: Optional[list[int]] = None
    keno_type: Optional[int] = None
    amount_eur: Optional[float] = None
    draw_date: Optional[datetime] = None
    publish_date: Optional[datetime] = None

    # Metadata
    article_title: str = ""
    extraction_confidence: float = 0.0
    raw_text: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "bundesland": self.bundesland,
            "city": self.city,
            "region": self.region,
            "numbers": self.numbers,
            "keno_type": self.keno_type,
            "amount_eur": self.amount_eur,
            "draw_date": self.draw_date.isoformat() if self.draw_date else None,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "source_url": self.source_url,
            "article_title": self.article_title,
            "extraction_confidence": self.extraction_confidence,
        }


class KenoWinnerParser:
    """Parser for extracting KENO winner data from article text."""

    # Regex patterns for number extraction
    # Pattern 1: Dash-separated numbers (5 – 12 – 20 – 26...)
    NUMBERS_DASH_PATTERN = re.compile(
        r"(\d{1,2})\s*[\u2013\u2014-]\s*"  # First number + dash
        r"(\d{1,2})\s*[\u2013\u2014-]\s*"  # Second + dash
        r"(\d{1,2})\s*[\u2013\u2014-]\s*"  # Third + dash
        r"(\d{1,2})\s*[\u2013\u2014-]\s*"  # Fourth + dash
        r"(\d{1,2})\s*[\u2013\u2014-]\s*"  # Fifth + dash
        r"(\d{1,2})"  # Sixth
        r"(?:\s*[\u2013\u2014-]\s*(\d{1,2}))?"  # Optional 7th
        r"(?:\s*[\u2013\u2014-]\s*(\d{1,2}))?"  # Optional 8th
        r"(?:\s*[\u2013\u2014-]\s*(\d{1,2}))?"  # Optional 9th
        r"(?:\s*[\u2013\u2014-]\s*(\d{1,2}))?",  # Optional 10th
    )

    # Pattern 2: Comma-separated numbers in a row (6-10 numbers)
    NUMBERS_COMMA_PATTERN = re.compile(
        r"\b(\d{1,2}),\s*(\d{1,2}),\s*(\d{1,2}),\s*(\d{1,2}),\s*"
        r"(\d{1,2}),\s*(\d{1,2})(?:,\s*(\d{1,2}))?(?:,\s*(\d{1,2}))?"
        r"(?:,\s*(\d{1,2}))?(?:,\s*(\d{1,2}))?\b",
    )

    # Pattern 3: Explicit list after "Zahlen:" or "Glueckszahlen:"
    NUMBERS_EXPLICIT_PATTERN = re.compile(
        r"(?:Glueckszahlen|Zahlen)[:\s]+"
        r"((?:\d{1,2}[\s,;\u2013\u2014-]+)+\d{1,2})",
        re.IGNORECASE,
    )

    # Pattern 4: Numbers after specific context
    NUMBERS_CONTEXT_PATTERN = re.compile(
        r"(?:angekreuzt|getippt|gespielt)[^.]*?"
        r"((?:\d{1,2}[\s,;\u2013\u2014-]+){4,9}\d{1,2})",
        re.IGNORECASE,
    )

    # KENO type pattern
    KENO_TYPE_PATTERN = re.compile(
        r"KENO[- ]?(?:Typ|Type)?[:\s]*(\d{1,2})", re.IGNORECASE
    )

    # Amount patterns (German number format)
    # Order matters: more specific patterns first
    AMOUNT_PATTERNS = [
        # 100.000 Euro, 1.000.000 EUR (large amounts with dots)
        re.compile(
            r"(\d{1,3}\.\d{3}(?:\.\d{3})?(?:,\d{2})?)\s*(?:Euro|EUR|\u20ac)",
            re.IGNORECASE,
        ),
        # Million(en) / Mio
        re.compile(r"(\d+(?:,\d+)?)\s*(?:Million(?:en)?|Mio)", re.IGNORECASE),
        # Context: "gewinnt 100.000 Euro"
        re.compile(
            r"(?:gewinnt|gewonnen|Gewinn(?:summe)?)[:\s]+(\d{1,3}(?:\.\d{3})+)\s*(?:Euro|EUR)?",
            re.IGNORECASE,
        ),
    ]

    # KENO type patterns (more flexible)
    KENO_TYPE_PATTERNS = [
        re.compile(r"KENO[- ]?Typ\s*(\d{1,2})", re.IGNORECASE),
        re.compile(r"Typ[- ]?(\d{1,2})[- ]?KENO", re.IGNORECASE),
        re.compile(r"KENO[- ]?(\d{1,2})\b", re.IGNORECASE),
        re.compile(r"(\d{1,2})\s*(?:Zahlen|Kreuzchen)\s*(?:bei|im)\s*KENO", re.IGNORECASE),
    ]

    # City/Region patterns
    CITY_PATTERNS = [
        re.compile(r"(?:aus|in|nach)\s+([A-Z\u00c4\u00d6\u00dc][a-z\u00e4\u00f6\u00fc\u00df]+(?:\s+[A-Z\u00c4\u00d6\u00dc][a-z\u00e4\u00f6\u00fc\u00df]+)?)", re.UNICODE),
        re.compile(r"(?:Landkreis|Region|Kreis)\s+([A-Z\u00c4\u00d6\u00dc][a-z\u00e4\u00f6\u00fc\u00df\-]+)", re.UNICODE),
        re.compile(r"([A-Z\u00c4\u00d6\u00dc][a-z\u00e4\u00f6\u00fc\u00df]+(?:er|erin))\s+(?:gewinnt|holt|sahnt)", re.UNICODE),
    ]

    # Date patterns
    DATE_PATTERNS = [
        re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})"),
        re.compile(r"(\d{1,2})\.\s*([A-Za-z\u00e4\u00f6\u00fc]+)\s*(\d{4})"),
    ]

    MONTH_MAP = {
        "januar": 1, "februar": 2, "m\u00e4rz": 3, "april": 4,
        "mai": 5, "juni": 6, "juli": 7, "august": 8,
        "september": 9, "oktober": 10, "november": 11, "dezember": 12,
    }

    def __init__(self, bundesland: str):
        """Initialize parser for a specific Bundesland.

        Args:
            bundesland: Name of the German federal state
        """
        self.bundesland = bundesland

    def parse(self, text: str, url: str, title: str = "") -> KenoWinnerRecord:
        """Parse article text to extract KENO winner information.

        Args:
            text: Full article text
            url: Source URL of the article
            title: Article title

        Returns:
            KenoWinnerRecord with extracted data
        """
        record = KenoWinnerRecord(
            bundesland=self.bundesland,
            source_url=url,
            article_title=title,
            raw_text=text[:2000],  # Store first 2000 chars for debugging
        )

        # Extract all fields
        record.numbers = self._extract_numbers(text)
        record.keno_type = self._extract_keno_type(text)
        record.amount_eur = self._extract_amount(text)
        record.city, record.region = self._extract_location(text, title)
        record.draw_date = self._extract_date(text)

        # Calculate confidence based on how many fields were extracted
        record.extraction_confidence = self._calculate_confidence(record)

        return record

    def _extract_numbers(self, text: str) -> Optional[list[int]]:
        """Extract KENO numbers from text.

        Returns numbers only if they look like a valid KENO selection
        (2-10 unique numbers between 1-70).
        """
        candidates: list[list[int]] = []

        # Try dash-separated pattern (5 – 12 – 20 – 26...)
        match = self.NUMBERS_DASH_PATTERN.search(text)
        if match:
            numbers = [
                int(g) for g in match.groups()
                if g is not None and 1 <= int(g) <= 70
            ]
            if self._is_valid_keno_selection(numbers):
                candidates.append(numbers)

        # Try comma-separated list pattern
        match = self.NUMBERS_COMMA_PATTERN.search(text)
        if match:
            numbers = [
                int(g) for g in match.groups()
                if g is not None and g.isdigit() and 1 <= int(g) <= 70
            ]
            if self._is_valid_keno_selection(numbers):
                candidates.append(numbers)

        # Try explicit pattern ("Glueckszahlen: ...")
        match = self.NUMBERS_EXPLICIT_PATTERN.search(text)
        if match:
            numbers_str = match.group(1)
            numbers = [
                int(n) for n in re.findall(r"\d{1,2}", numbers_str)
                if 1 <= int(n) <= 70
            ]
            if self._is_valid_keno_selection(numbers):
                candidates.append(numbers)

        # Try context pattern (angekreuzt/getippt/gespielt)
        match = self.NUMBERS_CONTEXT_PATTERN.search(text)
        if match:
            numbers_str = match.group(1)
            numbers = [
                int(n) for n in re.findall(r"\d{1,2}", numbers_str)
                if 1 <= int(n) <= 70
            ]
            if self._is_valid_keno_selection(numbers):
                candidates.append(numbers)

        # Return best candidate (prefer longer lists)
        if candidates:
            best = max(candidates, key=len)
            return sorted(set(best))  # Remove duplicates and sort

        return None

    def _is_valid_keno_selection(self, numbers: list[int]) -> bool:
        """Check if numbers look like a valid KENO selection."""
        if not numbers:
            return False

        unique_numbers = set(numbers)

        # Must have 2-10 unique numbers
        if not (2 <= len(unique_numbers) <= 10):
            return False

        # All numbers must be 1-70
        if not all(1 <= n <= 70 for n in unique_numbers):
            return False

        # Reject if it looks like a range (1,2,3,4,5... or 60,61,62...)
        sorted_nums = sorted(unique_numbers)
        consecutive_count = sum(
            1 for i in range(len(sorted_nums) - 1)
            if sorted_nums[i + 1] - sorted_nums[i] == 1
        )
        if consecutive_count >= len(sorted_nums) - 1 and len(sorted_nums) > 3:
            return False

        return True

    def _extract_keno_type(self, text: str) -> Optional[int]:
        """Extract KENO type (2-10) from text."""
        # Try each pattern in order
        for pattern in self.KENO_TYPE_PATTERNS:
            match = pattern.search(text)
            if match:
                keno_type = int(match.group(1))
                if 2 <= keno_type <= 10:
                    return keno_type

        # Fallback: if we found numbers, infer type from count
        # (This is a heuristic - 10 numbers = KENO-10)
        return None

    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract win amount in EUR from text.

        German number format:
        - 100.000 = 100,000 (hundred thousand)
        - 1.000.000 = 1,000,000 (one million)
        - 100.000,00 = 100,000.00
        """
        amounts_found: list[float] = []

        # Only look in KENO-related context (avoid EuroJackpot ads etc.)
        # Find paragraphs/sentences containing KENO
        keno_context = self._extract_keno_context(text)

        for pattern in self.AMOUNT_PATTERNS:
            for match in pattern.finditer(keno_context):
                amount_str = match.group(1)

                try:
                    # Check if this is a million pattern
                    if pattern == self.AMOUNT_PATTERNS[1]:  # Million pattern
                        base = float(amount_str.replace(",", "."))
                        amount = base * 1_000_000
                    else:
                        # German format: dots are thousands separators, comma is decimal
                        normalized = amount_str.replace(".", "")  # Remove thousand separators
                        normalized = normalized.replace(",", ".")  # Convert decimal comma
                        amount = float(normalized)

                    # Sanity check: KENO amounts are typically 100 - 1,000,000
                    if 100 <= amount <= 1_000_000:
                        amounts_found.append(amount)
                except ValueError:
                    continue

        # Return largest plausible amount
        if amounts_found:
            return max(amounts_found)
        return None

    def _extract_keno_context(self, text: str) -> str:
        """Extract text portions that are related to KENO.

        This filters out navigation, ads, and other game mentions.
        Returns a window of text around KENO mentions.
        """
        # Find all positions where KENO is mentioned
        keno_positions = [m.start() for m in re.finditer(r"keno", text, re.IGNORECASE)]

        if not keno_positions:
            return text  # Fallback to full text

        # Extract windows around each KENO mention (500 chars before/after)
        windows = []
        for pos in keno_positions:
            start = max(0, pos - 500)
            end = min(len(text), pos + 500)
            window = text[start:end]
            # Skip if this window contains EuroJackpot (probably an ad)
            if "eurojackpot" not in window.lower():
                windows.append(window)

        return " ".join(windows) if windows else text

    def _extract_location(self, text: str, title: str) -> tuple[Optional[str], Optional[str]]:
        """Extract city and/or region from text and title."""
        city = None
        region = None

        # Check title first (often contains location)
        combined_text = f"{title} {text}"

        for pattern in self.CITY_PATTERNS:
            match = pattern.search(combined_text)
            if match:
                location = match.group(1).strip()
                # Filter out common false positives
                false_positives = {
                    "Euro", "KENO", "Lotto", "Gewinn", "Spieler",
                    "Tipper", "Million", "Ziehung", "Zahlen",
                }
                if location not in false_positives and len(location) > 2:
                    # Determine if city or region
                    if "landkreis" in combined_text.lower() or "region" in combined_text.lower():
                        region = location
                    else:
                        city = location
                    break

        # Check for specific region patterns
        region_match = re.search(
            r"(Ober|Unter|Mittel)?(bayern|franken|sachsen|pfalz)",
            combined_text,
            re.IGNORECASE,
        )
        if region_match and not region:
            region = region_match.group(0)

        return city, region

    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract draw date from text."""
        for pattern in self.DATE_PATTERNS:
            match = pattern.search(text)
            if match:
                try:
                    groups = match.groups()
                    day = int(groups[0])
                    year = int(groups[2])

                    # Month can be number or name
                    if groups[1].isdigit():
                        month = int(groups[1])
                    else:
                        month = self.MONTH_MAP.get(groups[1].lower(), 0)

                    if month and 1 <= day <= 31 and 2000 <= year <= 2030:
                        return datetime(year, month, day)
                except (ValueError, IndexError):
                    continue
        return None

    def _calculate_confidence(self, record: KenoWinnerRecord) -> float:
        """Calculate extraction confidence score (0.0 - 1.0)."""
        score = 0.0
        weights = {
            "numbers": 0.35,
            "keno_type": 0.15,
            "amount_eur": 0.20,
            "city_or_region": 0.20,
            "draw_date": 0.10,
        }

        if record.numbers:
            score += weights["numbers"]
        if record.keno_type:
            score += weights["keno_type"]
        if record.amount_eur:
            score += weights["amount_eur"]
        if record.city or record.region:
            score += weights["city_or_region"]
        if record.draw_date:
            score += weights["draw_date"]

        return round(score, 2)


def is_keno_article(title: str, text: str) -> bool:
    """Check if an article is about KENO winners.

    Args:
        title: Article title
        text: Article text

    Returns:
        True if article appears to be about KENO winners
    """
    combined = f"{title} {text}".lower()

    # Must contain KENO
    if "keno" not in combined:
        return False

    # Exclude non-article pages (play pages, info pages)
    exclude_keywords = [
        "spielschein", "jetzt spielen", "online spielen",
        "spielanleitung", "spielregeln", "gewinnwahrscheinlichkeit",
        "quoten", "gewinnplan", "wie funktioniert",
    ]
    if any(kw in combined for kw in exclude_keywords):
        # But allow if it also has winner keywords
        has_winner = any(
            kw in combined
            for kw in ["gewonnen", "gewinner", "volltreffer", "hauptgewinn"]
        )
        if not has_winner:
            return False

    # Should contain winner-related keywords
    winner_keywords = [
        "gewinn", "gewinner", "gewinnt", "gewonnen",
        "hauptgewinn", "volltreffer", "jackpot",
        "glueckspilz", "tipper", "tipperin", "millionaer",
    ]

    # Require at least one winner keyword
    if not any(kw in combined for kw in winner_keywords):
        return False

    # Require an amount (Euro/EUR)
    if "euro" not in combined and "eur" not in combined:
        return False

    return True
