# kenobase/scraper/__init__.py
"""Scraper modules for KENO data from various sources."""

from kenobase.scraper.base import PressReleaseScraper
from kenobase.scraper.converters import (
    load_all_scraped_winners,
    load_scraped_winners,
    winner_record_to_draw_result,
)
from kenobase.scraper.landeslotterien import LANDESLOTTERIEN, get_scraper_config
from kenobase.scraper.lotto_de import (
    KenoDrawResult,
    LottoDeScraper,
    analyze_birthday_correlation,
)
from kenobase.scraper.parsers import KenoWinnerParser, KenoWinnerRecord

__all__ = [
    # Press release scraper
    "PressReleaseScraper",
    "KenoWinnerParser",
    "KenoWinnerRecord",
    "LANDESLOTTERIEN",
    "get_scraper_config",
    # Converters
    "winner_record_to_draw_result",
    "load_scraped_winners",
    "load_all_scraped_winners",
    # lotto.de archive scraper
    "LottoDeScraper",
    "KenoDrawResult",
    "analyze_birthday_correlation",
]
