# kenobase/scraper/landeslotterien.py
"""Configuration for all 16 German Landeslotterien press pages."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LotterieConfig:
    """Configuration for a single Landeslotterie."""

    code: str
    name: str
    bundesland: str
    base_url: str
    press_path: str
    search_pattern: str  # URL pattern for KENO articles
    article_selector: str  # CSS selector for article links
    title_selector: str  # CSS selector for article title
    content_selector: str  # CSS selector for article content
    date_selector: Optional[str] = None  # CSS selector for date


# All 16 Landeslotterien configurations
LANDESLOTTERIEN: dict[str, LotterieConfig] = {
    "bayern": LotterieConfig(
        code="bayern",
        name="LOTTO Bayern",
        bundesland="Bayern",
        base_url="https://www.lotto-bayern.de",
        press_path="/unternehmen/nachrichten/unsere_gewinner",
        search_pattern="keno",
        article_selector="a.news-teaser__link",
        title_selector="h1.article__headline",
        content_selector="div.article__content",
        date_selector="time.article__date",
    ),
    "brandenburg": LotterieConfig(
        code="brandenburg",
        name="LOTTO Brandenburg",
        bundesland="Brandenburg",
        base_url="https://www.lotto-brandenburg.de",
        press_path="/newsroom/presse",
        search_pattern="KENO",
        article_selector="a.news-item__link",
        title_selector="h1.article-header__title",
        content_selector="div.article-content",
        date_selector="span.article-header__date",
    ),
    "nrw": LotterieConfig(
        code="nrw",
        name="WestLotto",
        bundesland="Nordrhein-Westfalen",
        base_url="https://www.westlotto.de",
        press_path="/newsroom",
        search_pattern="keno",
        article_selector="a.teaser__link",
        title_selector="h1.article__title",
        content_selector="div.article__body",
        date_selector="time.article__date",
    ),
    "niedersachsen": LotterieConfig(
        code="niedersachsen",
        name="LOTTO Niedersachsen",
        bundesland="Niedersachsen",
        base_url="https://www.lotto-niedersachsen.de",
        press_path="/unternehmen/presse",
        search_pattern="keno",
        article_selector="a.press-teaser__link",
        title_selector="h1.press-article__title",
        content_selector="div.press-article__content",
        date_selector="span.press-article__date",
    ),
    "hessen": LotterieConfig(
        code="hessen",
        name="LOTTO Hessen",
        bundesland="Hessen",
        base_url="https://www.lotto-hessen.de",
        press_path="/magazin/meldungen",
        search_pattern="keno",
        article_selector="a.teaser-list__link",
        title_selector="h1.article__headline",
        content_selector="div.article__text",
        date_selector="span.article__date",
    ),
    "sachsen": LotterieConfig(
        code="sachsen",
        name="Sachsenlotto",
        bundesland="Sachsen",
        base_url="https://www.sachsenlotto.de",
        press_path="/portal/ueber-uns/presse.jsp",
        search_pattern="KENO",
        article_selector="a.press-item",
        title_selector="h1.article-title",
        content_selector="div.article-body",
        date_selector="span.article-date",
    ),
    "bw": LotterieConfig(
        code="bw",
        name="Lotto Baden-Wuerttemberg",
        bundesland="Baden-Wuerttemberg",
        base_url="https://www.lotto-bw.de",
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.news-teaser",
        title_selector="h1.article__title",
        content_selector="div.article__content",
        date_selector="time.article__time",
    ),
    "berlin": LotterieConfig(
        code="berlin",
        name="LOTTO Berlin",
        bundesland="Berlin",
        base_url="https://www.lotto-berlin.de",
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.news-item",
        title_selector="h1.page-title",
        content_selector="div.content-main",
        date_selector="span.date",
    ),
    "bremen": LotterieConfig(
        code="bremen",
        name="LOTTO Bremen",
        bundesland="Bremen",
        base_url="https://www.lotto-bremen.de",
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.teaser__link",
        title_selector="h1.article__title",
        content_selector="div.article__body",
        date_selector="time",
    ),
    "hamburg": LotterieConfig(
        code="hamburg",
        name="LOTTO Hamburg",
        bundesland="Hamburg",
        base_url="https://www.lotto-hh.de",  # Korrigiert: lotto-hh.de
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.teaser-link",
        title_selector="h1.headline",
        content_selector="div.text-content",
        date_selector="span.date",
    ),
    "mv": LotterieConfig(
        code="mv",
        name="LOTTO Mecklenburg-Vorpommern",
        bundesland="Mecklenburg-Vorpommern",
        base_url="https://www.lottomv.de",  # Korrigiert: lottomv.de
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.news-link",
        title_selector="h1.article-headline",
        content_selector="div.article-text",
        date_selector="span.publish-date",
    ),
    "rlp": LotterieConfig(
        code="rlp",
        name="LOTTO Rheinland-Pfalz",
        bundesland="Rheinland-Pfalz",
        base_url="https://www.lotto-rlp.de",
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.press-teaser",
        title_selector="h1.press-title",
        content_selector="div.press-content",
        date_selector="span.press-date",
    ),
    "saarland": LotterieConfig(
        code="saarland",
        name="Saartoto",
        bundesland="Saarland",
        base_url="https://www.saartoto.de",
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.news-teaser",
        title_selector="h1.article-title",
        content_selector="div.article-body",
        date_selector="time.article-date",
    ),
    "sachsen_anhalt": LotterieConfig(
        code="sachsen_anhalt",
        name="LOTTO Sachsen-Anhalt",
        bundesland="Sachsen-Anhalt",
        base_url="https://www.lottosachsenanhalt.de",
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.press-item",
        title_selector="h1.press-headline",
        content_selector="div.press-text",
        date_selector="span.press-date",
    ),
    "sh": LotterieConfig(
        code="sh",
        name="Nordwestlotto Schleswig-Holstein",
        bundesland="Schleswig-Holstein",
        base_url="https://www.lotto-sh.de",
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.news-teaser-link",
        title_selector="h1.article-headline",
        content_selector="div.article-content",
        date_selector="span.article-date",
    ),
    "thueringen": LotterieConfig(
        code="thueringen",
        name="LOTTO Thueringen",
        bundesland="Thueringen",
        base_url="https://www.lotto-thueringen.de",
        press_path="/presse",
        search_pattern="keno",
        article_selector="a.press-teaser",
        title_selector="h1.press-title",
        content_selector="div.press-body",
        date_selector="span.press-date",
    ),
}


def get_scraper_config(code: str) -> LotterieConfig:
    """Get configuration for a specific Landeslotterie.

    Args:
        code: Landeslotterie code (e.g., 'bayern', 'nrw')

    Returns:
        LotterieConfig for the specified lottery

    Raises:
        KeyError: If code is not found
    """
    if code not in LANDESLOTTERIEN:
        valid_codes = ", ".join(sorted(LANDESLOTTERIEN.keys()))
        raise KeyError(f"Unknown Landeslotterie: {code}. Valid: {valid_codes}")
    return LANDESLOTTERIEN[code]


def get_all_bundeslaender() -> list[str]:
    """Return list of all Bundeslaender with lottery configs."""
    return sorted(set(cfg.bundesland for cfg in LANDESLOTTERIEN.values()))
