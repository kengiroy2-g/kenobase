"""Unit-Tests fuer kenobase.pipeline.output_formats."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from kenobase.pipeline.output_formats import (
    CustomJSONEncoder,
    FormatterConfig,
    OutputFormat,
    OutputFormatter,
    format_output,
    get_supported_formats,
)


# ============================================================
# Test Fixtures
# ============================================================


@pytest.fixture
def sample_pipeline_result() -> dict:
    """Erzeugt ein Sample-PipelineResult als Dict."""
    return {
        "timestamp": "2025-12-26T22:30:00",
        "draws_count": 100,
        "warnings": ["Test warning 1", "Test warning 2"],
        "config_snapshot": {
            "version": "2.0.0",
            "active_game": "keno",
            "physics": {
                "enable_model_laws": True,
                "enable_avalanche": True,
            },
        },
        "frequency_results": [
            {"number": 17, "count": 45, "relative_frequency": 0.45, "classification": "hot"},
            {"number": 23, "count": 40, "relative_frequency": 0.40, "classification": "hot"},
            {"number": 5, "count": 15, "relative_frequency": 0.15, "classification": "cold"},
            {"number": 42, "count": 25, "relative_frequency": 0.25, "classification": "normal"},
        ],
        "pair_frequency_results": [
            {"pair": [17, 23], "count": 20, "relative_frequency": 0.20, "classification": "hot"},
            {"pair": [5, 42], "count": 5, "relative_frequency": 0.05, "classification": "cold"},
        ],
        "physics_result": {
            "stability_score": 0.92,
            "is_stable_law": True,
            "criticality_score": 0.45,
            "criticality_level": "MEDIUM",
            "hurst_exponent": 0.55,
            "regime_complexity": 3,
            "recommended_max_picks": 4,
            "avalanche": {
                "theta": 0.65,
                "state": "MODERATE",
                "is_safe_to_bet": True,
            },
        },
        "pipeline_selection": {
            "selected_name": "balanced",
            "selected_action": 0.25,
            "comparison_count": 3,
        },
    }


@pytest.fixture
def minimal_result() -> dict:
    """Minimales Ergebnis ohne optionale Felder."""
    return {
        "timestamp": "2025-12-26T22:30:00",
        "draws_count": 10,
        "warnings": [],
        "frequency_results": [
            {"number": 1, "count": 5, "relative_frequency": 0.50, "classification": "normal"},
        ],
    }


# ============================================================
# Test OutputFormat Enum
# ============================================================


class TestOutputFormat:
    """Tests fuer OutputFormat Enum."""

    def test_all_formats_defined(self):
        """Alle erwarteten Formate sind definiert."""
        expected = {"json", "csv", "html", "markdown", "yaml"}
        actual = {f.value for f in OutputFormat}
        assert actual == expected

    def test_format_values_lowercase(self):
        """Alle Format-Werte sind lowercase."""
        for fmt in OutputFormat:
            assert fmt.value == fmt.value.lower()


# ============================================================
# Test get_supported_formats
# ============================================================


class TestGetSupportedFormats:
    """Tests fuer get_supported_formats()."""

    def test_returns_list_of_strings(self):
        """Gibt Liste von Strings zurueck."""
        formats = get_supported_formats()
        assert isinstance(formats, list)
        assert all(isinstance(f, str) for f in formats)

    def test_contains_all_formats(self):
        """Enthaelt alle definierten Formate."""
        formats = get_supported_formats()
        assert "json" in formats
        assert "csv" in formats
        assert "html" in formats
        assert "markdown" in formats
        assert "yaml" in formats


# ============================================================
# Test FormatterConfig
# ============================================================


class TestFormatterConfig:
    """Tests fuer FormatterConfig."""

    def test_default_values(self):
        """Standardwerte sind korrekt."""
        config = FormatterConfig()
        assert config.indent == 2
        assert config.include_physics is True
        assert config.include_patterns is True
        assert config.top_n_frequencies == 20
        assert config.top_n_pairs == 10

    def test_custom_values(self):
        """Benutzerdefinierte Werte werden akzeptiert."""
        config = FormatterConfig(
            indent=4,
            include_physics=False,
            top_n_frequencies=10,
        )
        assert config.indent == 4
        assert config.include_physics is False
        assert config.top_n_frequencies == 10


# ============================================================
# Test CustomJSONEncoder
# ============================================================


class TestCustomJSONEncoder:
    """Tests fuer CustomJSONEncoder."""

    def test_datetime_encoding(self):
        """datetime wird zu ISO-String konvertiert."""
        dt = datetime(2025, 12, 26, 22, 30, 0)
        result = json.dumps({"ts": dt}, cls=CustomJSONEncoder)
        assert "2025-12-26T22:30:00" in result

    def test_bool_encoding(self):
        """bool wird korrekt kodiert."""
        result = json.dumps({"flag": True}, cls=CustomJSONEncoder)
        parsed = json.loads(result)
        assert parsed["flag"] is True


# ============================================================
# Test OutputFormatter
# ============================================================


class TestOutputFormatter:
    """Tests fuer OutputFormatter Klasse."""

    def test_init_default_config(self):
        """Initialisierung mit Default-Config."""
        formatter = OutputFormatter()
        assert formatter.config is not None
        assert isinstance(formatter.config, FormatterConfig)

    def test_init_custom_config(self):
        """Initialisierung mit benutzerdefinierter Config."""
        config = FormatterConfig(indent=4)
        formatter = OutputFormatter(config)
        assert formatter.config.indent == 4

    def test_format_accepts_string(self, sample_pipeline_result):
        """format() akzeptiert String als Format."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "json")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_accepts_enum(self, sample_pipeline_result):
        """format() akzeptiert OutputFormat Enum."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, OutputFormat.JSON)
        assert isinstance(result, str)

    def test_format_unknown_raises(self, sample_pipeline_result):
        """format() wirft ValueError bei unbekanntem Format."""
        formatter = OutputFormatter()
        with pytest.raises(ValueError, match="Unknown format"):
            formatter.format(sample_pipeline_result, "unknown_format")


# ============================================================
# Test JSON Format
# ============================================================


class TestJsonFormat:
    """Tests fuer JSON-Formatierung."""

    def test_valid_json_output(self, sample_pipeline_result):
        """Output ist valides JSON."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "json")
        parsed = json.loads(result)
        assert parsed["draws_count"] == 100

    def test_contains_frequency_results(self, sample_pipeline_result):
        """Frequenz-Ergebnisse sind enthalten."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "json")
        parsed = json.loads(result)
        assert "frequency_results" in parsed
        assert len(parsed["frequency_results"]) == 4

    def test_contains_physics_result(self, sample_pipeline_result):
        """Physics-Ergebnisse sind enthalten."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "json")
        parsed = json.loads(result)
        assert "physics_result" in parsed
        assert parsed["physics_result"]["stability_score"] == 0.92


# ============================================================
# Test CSV Format
# ============================================================


class TestCsvFormat:
    """Tests fuer CSV-Formatierung."""

    def test_contains_header(self, sample_pipeline_result):
        """CSV enthaelt Header-Zeile."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "csv")
        lines = result.strip().split("\n")
        # Find header line (skip section comments)
        header_line = next(l for l in lines if not l.startswith("#") and l)
        assert "number" in header_line.lower()
        assert "count" in header_line.lower()

    def test_contains_physics_section(self, sample_pipeline_result):
        """CSV enthaelt Physics-Section."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "csv")
        assert "# Physics Summary" in result
        assert "stability_score" in result

    def test_contains_pair_section_when_enabled(self, sample_pipeline_result):
        """CSV enthaelt Pair-Section wenn aktiviert."""
        config = FormatterConfig(include_patterns=True)
        formatter = OutputFormatter(config)
        result = formatter.format(sample_pipeline_result, "csv")
        assert "# Pair Frequency Results" in result

    def test_excludes_pair_section_when_disabled(self, sample_pipeline_result):
        """CSV enthaelt keine Pair-Section wenn deaktiviert."""
        config = FormatterConfig(include_patterns=False)
        formatter = OutputFormatter(config)
        result = formatter.format(sample_pipeline_result, "csv")
        assert "# Pair Frequency Results" not in result


# ============================================================
# Test HTML Format
# ============================================================


class TestHtmlFormat:
    """Tests fuer HTML-Formatierung."""

    def test_valid_html_structure(self, sample_pipeline_result):
        """Output hat gueltige HTML-Struktur."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "html")
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result
        assert "<head>" in result
        assert "<body>" in result

    def test_contains_title(self, sample_pipeline_result):
        """HTML enthaelt Titel."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "html")
        assert "<title>Kenobase Analysis Report</title>" in result

    def test_contains_css_styles(self, sample_pipeline_result):
        """HTML enthaelt CSS-Styles."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "html")
        assert "<style>" in result
        assert ".hot" in result
        assert ".cold" in result

    def test_contains_physics_section(self, sample_pipeline_result):
        """HTML enthaelt Physics-Section."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "html")
        assert "Physics Analysis" in result
        assert "Stability Score" in result

    def test_contains_frequency_table(self, sample_pipeline_result):
        """HTML enthaelt Frequenz-Tabelle."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "html")
        assert "<table>" in result
        assert "Number Frequencies" in result


# ============================================================
# Test Markdown Format
# ============================================================


class TestMarkdownFormat:
    """Tests fuer Markdown-Formatierung."""

    def test_starts_with_header(self, sample_pipeline_result):
        """Markdown beginnt mit H1-Header."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "markdown")
        assert result.startswith("# Kenobase Analysis Report")

    def test_contains_metadata(self, sample_pipeline_result):
        """Markdown enthaelt Metadaten."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "markdown")
        assert "**Generated:**" in result
        assert "**Draws analyzed:**" in result

    def test_contains_physics_table(self, sample_pipeline_result):
        """Markdown enthaelt Physics-Tabelle."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "markdown")
        assert "## Physics Analysis" in result
        assert "| Metric | Value |" in result
        assert "Stability Score" in result

    def test_contains_frequency_table(self, sample_pipeline_result):
        """Markdown enthaelt Frequenz-Tabelle."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "markdown")
        assert "## Number Frequencies" in result
        assert "| Number | Count | Frequency | Classification |" in result

    def test_contains_warnings(self, sample_pipeline_result):
        """Markdown enthaelt Warnings."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "markdown")
        assert "## Warnings" in result
        assert "Test warning 1" in result

    def test_gfm_table_format(self, sample_pipeline_result):
        """Tabellen sind GFM-kompatibel."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "markdown")
        # GFM tables have |---|---| separator
        assert "|--------|" in result


# ============================================================
# Test YAML Format
# ============================================================


class TestYamlFormat:
    """Tests fuer YAML-Formatierung."""

    def test_contains_top_level_keys(self, sample_pipeline_result):
        """YAML enthaelt Top-Level-Keys."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "yaml")
        assert "timestamp:" in result
        assert "draws_count:" in result
        assert "frequency_results:" in result

    def test_contains_physics_result(self, sample_pipeline_result):
        """YAML enthaelt Physics-Result."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "yaml")
        assert "physics_result:" in result
        assert "stability_score:" in result

    def test_handles_nested_structures(self, sample_pipeline_result):
        """YAML behandelt verschachtelte Strukturen korrekt."""
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "yaml")
        # Should have proper indentation for nested keys
        assert "avalanche:" in result


# ============================================================
# Test Convenience Function format_output
# ============================================================


class TestFormatOutputFunction:
    """Tests fuer die format_output() Convenience-Funktion."""

    def test_json_format(self, sample_pipeline_result):
        """format_output() funktioniert mit JSON."""
        result = format_output(sample_pipeline_result, "json")
        parsed = json.loads(result)
        assert parsed["draws_count"] == 100

    def test_markdown_format(self, sample_pipeline_result):
        """format_output() funktioniert mit Markdown."""
        result = format_output(sample_pipeline_result, "markdown")
        assert "# Kenobase Analysis Report" in result


# ============================================================
# Test Edge Cases
# ============================================================


class TestEdgeCases:
    """Tests fuer Edge Cases."""

    def test_empty_frequency_results(self, minimal_result):
        """Behandelt leere Frequenz-Ergebnisse."""
        minimal_result["frequency_results"] = []
        formatter = OutputFormatter()
        # Should not raise
        result = formatter.format(minimal_result, "json")
        parsed = json.loads(result)
        assert parsed["frequency_results"] == []

    def test_missing_physics_result(self, minimal_result):
        """Behandelt fehlendes physics_result."""
        formatter = OutputFormatter()
        result = formatter.format(minimal_result, "html")
        # Should not contain physics section
        assert "Physics Analysis" not in result

    def test_missing_avalanche(self, sample_pipeline_result):
        """Behandelt fehlendes avalanche in physics_result."""
        del sample_pipeline_result["physics_result"]["avalanche"]
        formatter = OutputFormatter()
        result = formatter.format(sample_pipeline_result, "markdown")
        assert "Avalanche Theta" not in result

    def test_top_n_limiting(self, sample_pipeline_result):
        """top_n_frequencies begrenzt Ausgabe korrekt."""
        # Add more frequency results
        for i in range(30):
            sample_pipeline_result["frequency_results"].append({
                "number": 50 + i,
                "count": i,
                "relative_frequency": i / 100,
                "classification": "normal",
            })

        config = FormatterConfig(top_n_frequencies=5)
        formatter = OutputFormatter(config)
        result = formatter.format(sample_pipeline_result, "markdown")

        # Count table rows (excluding header and separator)
        lines = result.split("\n")
        freq_section = False
        row_count = 0
        for line in lines:
            if "## Number Frequencies" in line:
                freq_section = True
            elif freq_section and line.startswith("| ") and "|---" not in line:
                if "Number" not in line:  # Skip header
                    row_count += 1
            elif freq_section and line.startswith("##"):
                break

        assert row_count == 5
