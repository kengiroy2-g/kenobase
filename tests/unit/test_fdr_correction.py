"""
Unit tests for FDR correction script.

Tests the apply_fdr_correction.py script functionality:
- p_value extraction from nested JSON
- FDR correction application
- Report generation

Author: EXECUTOR (TASK_031)
Date: 2025-12-30
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from scripts.apply_fdr_correction import (
    PValueEntry,
    apply_fdr_correction,
    extract_p_values_recursive,
    generate_markdown_report,
    scan_results_directory,
)


class TestPValueExtraction:
    """Tests for p_value extraction from JSON structures."""

    def test_extract_top_level_p_value(self):
        """Extract p_value at top level."""
        data = {"p_value": 0.05, "observed_value": 1.5}
        entries = extract_p_values_recursive(data, source_file="test.json")
        assert len(entries) == 1
        assert entries[0].p_value == 0.05

    def test_extract_nested_p_value(self):
        """Extract p_value from nested structure."""
        data = {
            "by_type": {
                "typ_6": {"p_value": 0.03, "observed_statistic": 2.1},
                "typ_7": {"p_value": 0.08, "observed_statistic": 1.2},
            }
        }
        entries = extract_p_values_recursive(data, source_file="nested.json")
        assert len(entries) == 2
        p_values = sorted([e.p_value for e in entries])
        assert p_values == [0.03, 0.08]

    def test_extract_p_value_variants(self):
        """Extract various p_value naming conventions."""
        data = {
            "test1": {"p_value": 0.01},
            "test2": {"p-value": 0.02},
            "test3": {"pvalue": 0.03},
            "test4": {"P_VALUE": 0.04},
        }
        entries = extract_p_values_recursive(data, source_file="variants.json")
        # Should find all 4 variants
        assert len(entries) == 4

    def test_extract_from_array(self):
        """Extract p_values from array of results."""
        data = {
            "results": [
                {"test_name": "A", "p_value": 0.01},
                {"test_name": "B", "p_value": 0.02},
                {"test_name": "C", "p_value": 0.03},
            ]
        }
        entries = extract_p_values_recursive(data, source_file="array.json")
        assert len(entries) == 3

    def test_skip_null_p_values(self):
        """Skip null p_value entries."""
        data = {
            "test1": {"p_value": 0.05},
            "test2": {"p_value": None},
        }
        entries = extract_p_values_recursive(data, source_file="null.json")
        assert len(entries) == 1

    def test_infer_hypothesis_id(self):
        """Infer hypothesis ID from context."""
        data = {"hypothesis_id": "HYP-007", "p_value": 0.05}
        entries = extract_p_values_recursive(data, source_file="test.json")
        assert entries[0].hypothesis_id == "HYP-007"

    def test_infer_hypothesis_id_from_filename(self):
        """Infer hypothesis ID from filename when not in data."""
        data = {"p_value": 0.05}
        entries = extract_p_values_recursive(data, source_file="hyp011_regularity.json")
        assert "HYP011" in entries[0].hypothesis_id.upper()


class TestFDRCorrection:
    """Tests for FDR correction functionality."""

    def test_fdr_correction_basic(self):
        """Test basic FDR correction."""
        entries = [
            PValueEntry("f1.json", "H1", "test1", 0.01, "p_value"),
            PValueEntry("f2.json", "H2", "test2", 0.04, "p_value"),  # < 0.05
            PValueEntry("f3.json", "H3", "test3", 0.10, "p_value"),
        ]
        result = apply_fdr_correction(entries, alpha=0.05)

        assert result["n_tests"] == 3
        assert result["n_significant_before_correction"] == 2  # p < 0.05 (0.01, 0.04)
        assert "entries" in result
        assert len(result["entries"]) == 3

    def test_fdr_correction_empty(self):
        """Test FDR correction with empty input."""
        result = apply_fdr_correction([], alpha=0.05)
        assert result["n_tests"] == 0
        assert result["n_significant_after_fdr"] == 0

    def test_fdr_q_values_ordering(self):
        """Test that q-values maintain proper ordering."""
        entries = [
            PValueEntry("f1.json", "H1", "test1", 0.001, "p_value"),
            PValueEntry("f2.json", "H2", "test2", 0.01, "p_value"),
            PValueEntry("f3.json", "H3", "test3", 0.05, "p_value"),
        ]
        result = apply_fdr_correction(entries, alpha=0.05)

        q_values = [e["q_value"] for e in result["entries"]]
        # q-values should be monotonically increasing with original order
        assert q_values[0] <= q_values[1] <= q_values[2]

    def test_fdr_significant_indices(self):
        """Test correct significant indices after FDR."""
        # With 3 tests and p-values [0.001, 0.02, 0.1]
        # BH threshold at rank 1: 0.05 * (1/3) = 0.0167
        # BH threshold at rank 2: 0.05 * (2/3) = 0.0333
        # p[0]=0.001 < 0.0167 -> significant
        # p[1]=0.02 < 0.0333 -> significant
        # p[2]=0.1 > 0.05 -> not significant
        entries = [
            PValueEntry("f1.json", "H1", "test1", 0.001, "p_value"),
            PValueEntry("f2.json", "H2", "test2", 0.02, "p_value"),
            PValueEntry("f3.json", "H3", "test3", 0.1, "p_value"),
        ]
        result = apply_fdr_correction(entries, alpha=0.05)

        assert result["n_significant_after_fdr"] == 2


class TestScanResultsDirectory:
    """Tests for scanning results directory."""

    def test_scan_empty_directory(self):
        """Test scanning empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            entries = scan_results_directory(Path(tmpdir))
            assert len(entries) == 0

    def test_scan_with_json_files(self):
        """Test scanning directory with JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test JSON files
            (tmppath / "test1.json").write_text(
                json.dumps({"p_value": 0.05}), encoding="utf-8"
            )
            (tmppath / "test2.json").write_text(
                json.dumps({"results": {"p_value": 0.01}}), encoding="utf-8"
            )

            entries = scan_results_directory(tmppath)
            assert len(entries) == 2

    def test_scan_ignores_invalid_json(self):
        """Test that invalid JSON files are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            (tmppath / "valid.json").write_text(
                json.dumps({"p_value": 0.05}), encoding="utf-8"
            )
            (tmppath / "invalid.json").write_text("not valid json{}", encoding="utf-8")

            entries = scan_results_directory(tmppath)
            assert len(entries) == 1


class TestMarkdownReport:
    """Tests for Markdown report generation."""

    def test_generate_report(self):
        """Test basic report generation."""
        fdr_results = {
            "timestamp": "2025-12-30T12:00:00",
            "alpha": 0.05,
            "n_tests": 3,
            "n_significant_before_correction": 2,
            "n_significant_after_fdr": 1,
            "significant_indices": [0],
            "entries": [
                {
                    "source_file": "test.json",
                    "hypothesis_id": "H1",
                    "test_name": "Test One",
                    "original_p_value": 0.001,
                    "q_value": 0.003,
                    "is_significant_after_fdr": True,
                    "json_path": "p_value",
                    "context": {},
                }
            ],
            "summary": {
                "files_scanned": 1,
                "unique_hypotheses": 1,
                "p_values_extracted": 1,
                "min_p_value": 0.001,
                "max_p_value": 0.001,
                "median_p_value": 0.001,
            },
        }

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            output_path = Path(f.name)

        try:
            generate_markdown_report(fdr_results, output_path)
            content = output_path.read_text(encoding="utf-8")

            assert "# FDR Correction Report" in content
            assert "H1" in content
            assert "0.001" in content
            assert "0.003" in content
        finally:
            output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
