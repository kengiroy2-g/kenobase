# kenobase/scraper/converters.py
"""Converters to transform scraper records to analysis-compatible formats."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from kenobase.core.data_loader import DrawResult, GameType
from kenobase.core.regions import normalize_region
from kenobase.scraper.parsers import KenoWinnerRecord

logger = logging.getLogger(__name__)


def winner_record_to_draw_result(record: KenoWinnerRecord) -> Optional[DrawResult]:
    """Convert a KenoWinnerRecord to a DrawResult for analysis.

    The conversion maps:
    - bundesland -> metadata["bundesland"] (normalized)
    - city/region -> metadata["city"]/["region"]
    - numbers -> numbers (validated for KENO range 1-70)
    - keno_type -> metadata["keno_type"]
    - amount_eur -> metadata["amount_eur"]
    - draw_date -> date (or publish_date as fallback)

    Args:
        record: KenoWinnerRecord from press scraper

    Returns:
        DrawResult or None if conversion fails (invalid data)
    """
    # Validate numbers - must be valid KENO selection
    if not record.numbers:
        logger.debug(f"Skipping record without numbers: {record.source_url}")
        return None

    # Filter and validate numbers (1-70, unique)
    valid_numbers = sorted(set(n for n in record.numbers if 1 <= n <= 70))

    # Must have 2-10 unique valid numbers (valid KENO selection)
    if not (2 <= len(valid_numbers) <= 10):
        logger.debug(
            f"Skipping record with invalid number count ({len(valid_numbers)}): "
            f"{record.source_url}"
        )
        return None

    # Get date (prefer draw_date, fallback to publish_date or now)
    date = record.draw_date or record.publish_date or datetime.now()

    # Build metadata
    normalized_bundesland = normalize_region(record.bundesland)
    metadata = {
        "bundesland": normalized_bundesland or record.bundesland,
        "source_url": record.source_url,
        "extraction_confidence": record.extraction_confidence,
    }

    if record.city:
        metadata["city"] = record.city
    if record.region:
        metadata["region"] = record.region
    if record.keno_type:
        metadata["keno_type"] = record.keno_type
    if record.amount_eur:
        metadata["amount_eur"] = record.amount_eur

    try:
        return DrawResult(
            date=date,
            numbers=valid_numbers,
            bonus=[],
            game_type=GameType.KENO,
            metadata=metadata,
        )
    except Exception as e:
        logger.warning(f"Failed to create DrawResult: {e}")
        return None


def load_scraped_winners(
    input_path: Path | str,
    *,
    min_confidence: float = 0.3,
) -> list[DrawResult]:
    """Load scraped winners from JSON file and convert to DrawResults.

    Args:
        input_path: Path to JSON file from scrape_press.py
        min_confidence: Minimum extraction confidence threshold (0.0-1.0)

    Returns:
        List of DrawResult objects with bundesland in metadata
    """
    path = Path(input_path)
    if not path.exists():
        logger.error(f"File not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records_data = data.get("records", [])
    if not records_data:
        logger.warning(f"No records found in {path}")
        return []

    results: list[DrawResult] = []

    for rec_dict in records_data:
        # Skip low-confidence records
        confidence = rec_dict.get("extraction_confidence", 0.0)
        if confidence < min_confidence:
            continue

        # Parse dates
        draw_date = None
        if rec_dict.get("draw_date"):
            try:
                draw_date = datetime.fromisoformat(rec_dict["draw_date"])
            except ValueError:
                pass

        publish_date = None
        if rec_dict.get("publish_date"):
            try:
                publish_date = datetime.fromisoformat(rec_dict["publish_date"])
            except ValueError:
                pass

        record = KenoWinnerRecord(
            bundesland=rec_dict.get("bundesland", ""),
            source_url=rec_dict.get("source_url", ""),
            city=rec_dict.get("city"),
            region=rec_dict.get("region"),
            numbers=rec_dict.get("numbers"),
            keno_type=rec_dict.get("keno_type"),
            amount_eur=rec_dict.get("amount_eur"),
            draw_date=draw_date,
            publish_date=publish_date,
            article_title=rec_dict.get("article_title", ""),
            extraction_confidence=confidence,
        )

        draw_result = winner_record_to_draw_result(record)
        if draw_result:
            results.append(draw_result)

    logger.info(
        f"Loaded {len(results)} valid DrawResults from {len(records_data)} records "
        f"(min_confidence={min_confidence})"
    )
    return results


def load_all_scraped_winners(
    scraped_dir: Path | str,
    *,
    min_confidence: float = 0.3,
    deduplicate: bool = True,
) -> list[DrawResult]:
    """Load all scraped winner JSONs from a directory.

    Args:
        scraped_dir: Directory containing keno_winners_*.json files
        min_confidence: Minimum extraction confidence threshold
        deduplicate: Remove duplicate records (same source_url)

    Returns:
        Combined list of DrawResult objects
    """
    dir_path = Path(scraped_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory not found: {dir_path}")
        return []

    json_files = sorted(dir_path.glob("keno_winners_*.json"))
    if not json_files:
        logger.warning(f"No keno_winners_*.json files in {dir_path}")
        return []

    all_results: list[DrawResult] = []
    seen_urls: set[str] = set()

    for json_file in json_files:
        results = load_scraped_winners(json_file, min_confidence=min_confidence)

        if deduplicate:
            for r in results:
                url = r.metadata.get("source_url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(r)
                elif not url:
                    all_results.append(r)
        else:
            all_results.extend(results)

    logger.info(
        f"Loaded {len(all_results)} total DrawResults from {len(json_files)} files"
    )
    return all_results


__all__ = [
    "winner_record_to_draw_result",
    "load_scraped_winners",
    "load_all_scraped_winners",
]
