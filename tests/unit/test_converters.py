"""Tests for kenobase.scraper.converters module."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from kenobase.scraper.converters import (
    load_all_scraped_winners,
    load_scraped_winners,
    winner_record_to_draw_result,
)
from kenobase.scraper.parsers import KenoWinnerRecord


class TestWinnerRecordToDrawResult:
    """Tests for winner_record_to_draw_result conversion."""

    def test_valid_record_converts(self):
        """Valid record should convert successfully."""
        record = KenoWinnerRecord(
            bundesland="Bayern",
            source_url="https://example.com",
            numbers=[5, 12, 20, 26, 34, 41, 48, 55, 62, 68],
            keno_type=10,
            amount_eur=100000.0,
            draw_date=datetime(2024, 1, 15),
        )

        result = winner_record_to_draw_result(record)

        assert result is not None
        assert result.numbers == [5, 12, 20, 26, 34, 41, 48, 55, 62, 68]
        assert result.metadata["bundesland"] == "bayern"
        assert result.metadata["keno_type"] == 10
        assert result.metadata["amount_eur"] == 100000.0

    def test_no_numbers_returns_none(self):
        """Record without numbers should return None."""
        record = KenoWinnerRecord(
            bundesland="Bayern",
            source_url="https://example.com",
            numbers=None,
        )

        result = winner_record_to_draw_result(record)
        assert result is None

    def test_too_many_numbers_returns_none(self):
        """Record with > 10 numbers should return None."""
        record = KenoWinnerRecord(
            bundesland="Bayern",
            source_url="https://example.com",
            numbers=list(range(1, 71)),  # All 70 numbers
        )

        result = winner_record_to_draw_result(record)
        assert result is None

    def test_invalid_numbers_filtered(self):
        """Numbers outside 1-70 should be filtered."""
        record = KenoWinnerRecord(
            bundesland="Bayern",
            source_url="https://example.com",
            numbers=[0, 5, 10, 71, 100, 15, 20, 25],  # 0, 71, 100 invalid
        )

        result = winner_record_to_draw_result(record)

        assert result is not None
        assert result.numbers == [5, 10, 15, 20, 25]  # Only valid, sorted

    def test_bundesland_normalized(self):
        """Bundesland should be normalized to ASCII key."""
        record = KenoWinnerRecord(
            bundesland="Baden-Württemberg",
            source_url="https://example.com",
            numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        )

        result = winner_record_to_draw_result(record)

        assert result is not None
        assert result.metadata["bundesland"] == "baden-wuerttemberg"


class TestLoadScrapedWinners:
    """Tests for load_scraped_winners function."""

    def test_load_valid_json(self, tmp_path):
        """Valid JSON should load correctly."""
        data = {
            "records": [
                {
                    "bundesland": "Bayern",
                    "source_url": "https://example.com/1",
                    "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "keno_type": 10,
                    "extraction_confidence": 0.9,
                },
                {
                    "bundesland": "Hessen",
                    "source_url": "https://example.com/2",
                    "numbers": [11, 12, 13, 14, 15],
                    "keno_type": 5,
                    "extraction_confidence": 0.85,
                },
            ]
        }

        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data))

        results = load_scraped_winners(json_file)

        assert len(results) == 2
        assert results[0].metadata["bundesland"] == "bayern"
        assert results[1].metadata["bundesland"] == "hessen"

    def test_confidence_filter(self, tmp_path):
        """Low confidence records should be filtered."""
        data = {
            "records": [
                {
                    "bundesland": "Bayern",
                    "source_url": "https://example.com/1",
                    "numbers": [1, 2, 3, 4, 5],
                    "extraction_confidence": 0.8,
                },
                {
                    "bundesland": "Hessen",
                    "source_url": "https://example.com/2",
                    "numbers": [11, 12, 13, 14, 15],
                    "extraction_confidence": 0.2,  # Below default 0.3
                },
            ]
        }

        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data))

        results = load_scraped_winners(json_file, min_confidence=0.5)

        assert len(results) == 1
        assert results[0].metadata["bundesland"] == "bayern"

    def test_missing_file_returns_empty(self):
        """Missing file should return empty list."""
        results = load_scraped_winners(Path("/nonexistent/file.json"))
        assert results == []

    def test_empty_records_returns_empty(self, tmp_path):
        """Empty records array should return empty list."""
        data = {"records": []}

        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data))

        results = load_scraped_winners(json_file)
        assert results == []


class TestLoadAllScrapedWinners:
    """Tests for load_all_scraped_winners function."""

    def test_load_multiple_files(self, tmp_path):
        """Should load from multiple keno_winners_*.json files."""
        # Create multiple JSON files
        for i in range(3):
            data = {
                "records": [
                    {
                        "bundesland": f"Region{i}",
                        "source_url": f"https://example.com/{i}",
                        "numbers": [1, 2, 3, 4, 5],
                        "extraction_confidence": 0.9,
                    }
                ]
            }
            (tmp_path / f"keno_winners_2024010{i}.json").write_text(json.dumps(data))

        results = load_all_scraped_winners(tmp_path)
        assert len(results) == 3

    def test_deduplication(self, tmp_path):
        """Duplicate source_urls should be deduplicated."""
        # Same record in two files
        for i in range(2):
            data = {
                "records": [
                    {
                        "bundesland": "Bayern",
                        "source_url": "https://example.com/same",  # Same URL
                        "numbers": [1, 2, 3, 4, 5],
                        "extraction_confidence": 0.9,
                    }
                ]
            }
            (tmp_path / f"keno_winners_2024010{i}.json").write_text(json.dumps(data))

        results = load_all_scraped_winners(tmp_path, deduplicate=True)
        assert len(results) == 1

    def test_no_deduplication(self, tmp_path):
        """Without deduplication, all records should be kept."""
        for i in range(2):
            data = {
                "records": [
                    {
                        "bundesland": "Bayern",
                        "source_url": "https://example.com/same",
                        "numbers": [1, 2, 3, 4, 5],
                        "extraction_confidence": 0.9,
                    }
                ]
            }
            (tmp_path / f"keno_winners_2024010{i}.json").write_text(json.dumps(data))

        results = load_all_scraped_winners(tmp_path, deduplicate=False)
        assert len(results) == 2

    def test_missing_directory_returns_empty(self):
        """Missing directory should return empty list."""
        results = load_all_scraped_winners(Path("/nonexistent/dir"))
        assert results == []
