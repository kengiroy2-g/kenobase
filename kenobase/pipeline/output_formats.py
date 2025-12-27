"""Output-Formate Modul - Formatierung von Pipeline-Ergebnissen.

Dieses Modul implementiert verschiedene Output-Formate fuer Kenobase V2.0:
- JSON: Vollstaendige Datenstruktur
- CSV: Tabellarische Frequenzdaten (erweitert mit Physics)
- HTML: Interaktiver Report
- Markdown: GFM-kompatibles Textformat
- YAML: Strukturierte Konfiguration/Daten

Usage:
    from kenobase.pipeline.output_formats import OutputFormatter, OutputFormat

    formatter = OutputFormatter()
    result = formatter.format(data, OutputFormat.MARKDOWN)
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional


class OutputFormat(Enum):
    """Unterstuetzte Ausgabeformate."""

    JSON = "json"
    CSV = "csv"
    HTML = "html"
    MARKDOWN = "markdown"
    YAML = "yaml"


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder fuer numpy und datetime Typen."""

    def default(self, obj: Any) -> Any:
        """Konvertiert spezielle Typen zu JSON-serialisierbaren Werten."""
        # Handle numpy types if numpy is available
        try:
            import numpy as np
            if isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            if isinstance(obj, (np.integer, int)):
                return int(obj)
            if isinstance(obj, (np.floating, float)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass

        # Handle datetime
        if isinstance(obj, datetime):
            return obj.isoformat()

        return super().default(obj)


@dataclass
class FormatterConfig:
    """Konfiguration fuer Output-Formatter.

    Attributes:
        indent: Einrueckung fuer JSON/YAML (default 2)
        include_physics: Physics-Ergebnisse einschliessen (default True)
        include_patterns: Pattern-Ergebnisse einschliessen (default True)
        top_n_frequencies: Anzahl Top-Frequenzen in Reports (default 20)
        top_n_pairs: Anzahl Top-Paare in Reports (default 10)
    """

    indent: int = 2
    include_physics: bool = True
    include_patterns: bool = True
    top_n_frequencies: int = 20
    top_n_pairs: int = 10


class OutputFormatter:
    """Formatiert Pipeline-Ergebnisse in verschiedene Ausgabeformate.

    Unterstuetzt JSON, CSV, HTML, Markdown und YAML.
    Verwendet Registry-Pattern fuer einfache Erweiterbarkeit.

    Example:
        >>> formatter = OutputFormatter()
        >>> json_output = formatter.format(data, OutputFormat.JSON)
        >>> md_output = formatter.format(data, OutputFormat.MARKDOWN)
    """

    def __init__(self, config: Optional[FormatterConfig] = None) -> None:
        """Initialisiert den Formatter.

        Args:
            config: Optionale Formatter-Konfiguration.
        """
        self.config = config or FormatterConfig()
        self._formatters: dict[OutputFormat, Callable[[dict], str]] = {
            OutputFormat.JSON: self._format_json,
            OutputFormat.CSV: self._format_csv,
            OutputFormat.HTML: self._format_html,
            OutputFormat.MARKDOWN: self._format_markdown,
            OutputFormat.YAML: self._format_yaml,
        }

    def format(self, data: dict, output_format: OutputFormat | str) -> str:
        """Formatiert Daten in das angegebene Format.

        Args:
            data: Pipeline-Ergebnisse als Dict.
            output_format: Zielformat (OutputFormat enum oder String).

        Returns:
            Formatierter String.

        Raises:
            ValueError: Bei unbekanntem Format.
        """
        # Convert string to enum if needed
        if isinstance(output_format, str):
            try:
                output_format = OutputFormat(output_format.lower())
            except ValueError:
                raise ValueError(
                    f"Unknown format: {output_format}. "
                    f"Supported: {[f.value for f in OutputFormat]}"
                )

        formatter = self._formatters.get(output_format)
        if formatter is None:
            raise ValueError(f"No formatter registered for {output_format}")

        return formatter(data)

    def register_formatter(
        self,
        output_format: OutputFormat,
        formatter: Callable[[dict], str],
    ) -> None:
        """Registriert einen benutzerdefinierten Formatter.

        Args:
            output_format: Zu registrierendes Format.
            formatter: Formatter-Funktion (dict -> str).
        """
        self._formatters[output_format] = formatter

    def _format_json(self, data: dict) -> str:
        """Formatiert als JSON."""
        return json.dumps(
            data,
            indent=self.config.indent,
            ensure_ascii=False,
            cls=CustomJSONEncoder,
        )

    def _format_csv(self, data: dict) -> str:
        """Formatiert als CSV (erweitert mit Physics-Daten).

        Erzeugt mehrere Sektionen:
        - frequency_results
        - pair_frequency_results (optional)
        - physics_summary (wenn vorhanden)
        """
        output = io.StringIO()

        # Section 1: Frequency Results
        freq_results = data.get("frequency_results", [])
        if freq_results:
            output.write("# Frequency Results\n")
            writer = csv.DictWriter(
                output,
                fieldnames=["number", "count", "relative_frequency", "classification"],
                extrasaction="ignore",
            )
            writer.writeheader()
            for r in freq_results:
                writer.writerow({
                    "number": r.get("number", ""),
                    "count": r.get("count", ""),
                    "relative_frequency": f"{r.get('relative_frequency', 0):.4f}",
                    "classification": r.get("classification", ""),
                })
            output.write("\n")

        # Section 2: Pair Frequency Results
        pair_results = data.get("pair_frequency_results", [])
        if pair_results and self.config.include_patterns:
            output.write("# Pair Frequency Results (Top {})\n".format(
                self.config.top_n_pairs
            ))
            writer = csv.DictWriter(
                output,
                fieldnames=["pair", "count", "relative_frequency", "classification"],
                extrasaction="ignore",
            )
            writer.writeheader()
            for r in pair_results[:self.config.top_n_pairs]:
                pair_str = "-".join(str(x) for x in r.get("pair", []))
                writer.writerow({
                    "pair": pair_str,
                    "count": r.get("count", ""),
                    "relative_frequency": f"{r.get('relative_frequency', 0):.4f}",
                    "classification": r.get("classification", ""),
                })
            output.write("\n")

        # Section 3: Physics Summary
        physics = data.get("physics_result")
        if physics and self.config.include_physics:
            output.write("# Physics Summary\n")
            output.write("metric,value\n")
            output.write(f"stability_score,{physics.get('stability_score', 0):.4f}\n")
            output.write(f"is_stable_law,{physics.get('is_stable_law', False)}\n")
            output.write(f"criticality_score,{physics.get('criticality_score', 0):.4f}\n")
            output.write(f"criticality_level,{physics.get('criticality_level', 'N/A')}\n")
            output.write(f"hurst_exponent,{physics.get('hurst_exponent', 0):.4f}\n")
            output.write(f"regime_complexity,{physics.get('regime_complexity', 0)}\n")
            output.write(f"recommended_max_picks,{physics.get('recommended_max_picks', 6)}\n")

            avalanche = physics.get("avalanche")
            if avalanche:
                output.write(f"avalanche_theta,{avalanche.get('theta', 0):.4f}\n")
                output.write(f"avalanche_state,{avalanche.get('state', 'N/A')}\n")
                output.write(f"is_safe_to_bet,{avalanche.get('is_safe_to_bet', False)}\n")

        return output.getvalue()

    def _format_html(self, data: dict) -> str:
        """Formatiert als HTML-Report."""
        timestamp = data.get("timestamp", "N/A")
        draws_count = data.get("draws_count", 0)

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kenobase Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #666; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 30px; }}
        .meta {{ color: #888; font-size: 0.9em; }}
        .warning {{ color: #c00; font-weight: bold; background: #fff0f0; padding: 10px; border-radius: 4px; margin: 5px 0; }}
        table {{ border-collapse: collapse; margin: 10px 0; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .hot {{ background-color: #ffe0e0 !important; }}
        .cold {{ background-color: #e0e0ff !important; }}
        .normal {{ background-color: #fff; }}
        .physics {{ background-color: #f0f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3; }}
        .physics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .physics-item {{ background: white; padding: 10px; border-radius: 4px; }}
        .physics-item strong {{ color: #333; }}
        .avalanche-safe {{ color: #4CAF50; }}
        .avalanche-moderate {{ color: #FF9800; }}
        .avalanche-warning {{ color: #f44336; }}
        .avalanche-critical {{ color: #9C27B0; font-weight: bold; }}
    </style>
</head>
<body>
<div class="container">
    <h1>Kenobase Analysis Report</h1>
    <p class="meta">Generated: {timestamp} | Draws analyzed: {draws_count}</p>
"""

        # Warnings
        warnings = data.get("warnings", [])
        if warnings:
            html += "<h2>Warnings</h2>\n"
            for w in warnings:
                html += f'<div class="warning">{w}</div>\n'

        # Physics Results
        physics = data.get("physics_result")
        if physics and self.config.include_physics:
            stability_status = "Stable" if physics.get("is_stable_law") else "Unstable"
            html += '<h2>Physics Analysis</h2>\n<div class="physics">\n'
            html += '<div class="physics-grid">\n'
            html += f'<div class="physics-item"><strong>Stability Score:</strong> {physics.get("stability_score", 0):.3f} ({stability_status})</div>\n'
            html += f'<div class="physics-item"><strong>Criticality:</strong> {physics.get("criticality_score", 0):.3f} ({physics.get("criticality_level", "N/A")})</div>\n'
            html += f'<div class="physics-item"><strong>Hurst Exponent:</strong> {physics.get("hurst_exponent", 0):.3f}</div>\n'
            html += f'<div class="physics-item"><strong>Regime Complexity:</strong> {physics.get("regime_complexity", 0)}</div>\n'
            html += f'<div class="physics-item"><strong>Recommended Max Picks:</strong> {physics.get("recommended_max_picks", 6)}</div>\n'

            avalanche = physics.get("avalanche")
            if avalanche:
                state = avalanche.get("state", "N/A")
                state_class = f"avalanche-{state.lower()}" if state != "N/A" else ""
                html += f'<div class="physics-item"><strong>Avalanche:</strong> theta={avalanche.get("theta", 0):.3f}, '
                html += f'<span class="{state_class}">state={state}</span>, safe={avalanche.get("is_safe_to_bet", False)}</div>\n'

            html += '</div>\n</div>\n'

        # Frequency Table
        freq_results = data.get("frequency_results", [])
        if freq_results:
            html += f"<h2>Number Frequencies (Top {self.config.top_n_frequencies})</h2>\n"
            html += "<table>\n<tr><th>Number</th><th>Count</th><th>Frequency</th><th>Classification</th></tr>\n"
            freq_sorted = sorted(
                freq_results,
                key=lambda x: x.get("count", 0),
                reverse=True,
            )[:self.config.top_n_frequencies]
            for r in freq_sorted:
                cls = r.get("classification", "normal")
                html += f'<tr class="{cls}"><td>{r.get("number", "")}</td>'
                html += f'<td>{r.get("count", 0)}</td>'
                html += f'<td>{r.get("relative_frequency", 0):.4f}</td>'
                html += f'<td>{cls}</td></tr>\n'
            html += "</table>\n"

        # Pair Frequency Table
        pair_results = data.get("pair_frequency_results", [])
        if pair_results and self.config.include_patterns:
            html += f"<h2>Pair Frequencies (Top {self.config.top_n_pairs})</h2>\n"
            html += "<table>\n<tr><th>Pair</th><th>Count</th><th>Frequency</th><th>Classification</th></tr>\n"
            for r in pair_results[:self.config.top_n_pairs]:
                pair_str = "-".join(str(x) for x in r.get("pair", []))
                cls = r.get("classification", "normal")
                html += f'<tr class="{cls}"><td>{pair_str}</td>'
                html += f'<td>{r.get("count", 0)}</td>'
                html += f'<td>{r.get("relative_frequency", 0):.4f}</td>'
                html += f'<td>{cls}</td></tr>\n'
            html += "</table>\n"

        # Pipeline Selection
        pipeline = data.get("pipeline_selection")
        if pipeline:
            html += "<h2>Pipeline Selection (Least-Action)</h2>\n"
            html += f"<p><strong>Selected:</strong> {pipeline.get('selected_name', 'N/A')} "
            html += f"(action={pipeline.get('selected_action', 0):.3f})</p>\n"

        html += "</div>\n</body>\n</html>"
        return html

    def _format_markdown(self, data: dict) -> str:
        """Formatiert als Markdown (GFM-kompatibel)."""
        timestamp = data.get("timestamp", "N/A")
        draws_count = data.get("draws_count", 0)

        lines = [
            "# Kenobase Analysis Report",
            "",
            f"**Generated:** {timestamp}  ",
            f"**Draws analyzed:** {draws_count}",
            "",
        ]

        # Warnings
        warnings = data.get("warnings", [])
        if warnings:
            lines.append("## Warnings")
            lines.append("")
            for w in warnings:
                lines.append(f"- :warning: {w}")
            lines.append("")

        # Physics Results
        physics = data.get("physics_result")
        if physics and self.config.include_physics:
            stability_status = "Stable" if physics.get("is_stable_law") else "Unstable"
            lines.append("## Physics Analysis")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| Stability Score | {physics.get('stability_score', 0):.3f} ({stability_status}) |")
            lines.append(f"| Criticality | {physics.get('criticality_score', 0):.3f} ({physics.get('criticality_level', 'N/A')}) |")
            lines.append(f"| Hurst Exponent | {physics.get('hurst_exponent', 0):.3f} |")
            lines.append(f"| Regime Complexity | {physics.get('regime_complexity', 0)} |")
            lines.append(f"| Recommended Max Picks | {physics.get('recommended_max_picks', 6)} |")

            avalanche = physics.get("avalanche")
            if avalanche:
                lines.append(f"| Avalanche Theta | {avalanche.get('theta', 0):.3f} |")
                lines.append(f"| Avalanche State | {avalanche.get('state', 'N/A')} |")
                lines.append(f"| Safe to Bet | {avalanche.get('is_safe_to_bet', False)} |")

            lines.append("")

        # Frequency Table
        freq_results = data.get("frequency_results", [])
        if freq_results:
            lines.append(f"## Number Frequencies (Top {self.config.top_n_frequencies})")
            lines.append("")
            lines.append("| Number | Count | Frequency | Classification |")
            lines.append("|--------|-------|-----------|----------------|")
            freq_sorted = sorted(
                freq_results,
                key=lambda x: x.get("count", 0),
                reverse=True,
            )[:self.config.top_n_frequencies]
            for r in freq_sorted:
                lines.append(
                    f"| {r.get('number', '')} | {r.get('count', 0)} | "
                    f"{r.get('relative_frequency', 0):.4f} | {r.get('classification', 'normal')} |"
                )
            lines.append("")

        # Pair Frequency Table
        pair_results = data.get("pair_frequency_results", [])
        if pair_results and self.config.include_patterns:
            lines.append(f"## Pair Frequencies (Top {self.config.top_n_pairs})")
            lines.append("")
            lines.append("| Pair | Count | Frequency | Classification |")
            lines.append("|------|-------|-----------|----------------|")
            for r in pair_results[:self.config.top_n_pairs]:
                pair_str = "-".join(str(x) for x in r.get("pair", []))
                lines.append(
                    f"| {pair_str} | {r.get('count', 0)} | "
                    f"{r.get('relative_frequency', 0):.4f} | {r.get('classification', 'normal')} |"
                )
            lines.append("")

        # Pipeline Selection
        pipeline = data.get("pipeline_selection")
        if pipeline:
            lines.append("## Pipeline Selection (Least-Action)")
            lines.append("")
            lines.append(f"**Selected:** {pipeline.get('selected_name', 'N/A')} "
                        f"(action={pipeline.get('selected_action', 0):.3f})")
            lines.append("")

        # Config Summary
        config = data.get("config_snapshot")
        if config:
            lines.append("## Configuration")
            lines.append("")
            lines.append(f"- **Version:** {config.get('version', 'N/A')}")
            lines.append(f"- **Active Game:** {config.get('active_game', 'N/A')}")
            physics_cfg = config.get("physics", {})
            if physics_cfg:
                lines.append(f"- **Physics Enabled:** {physics_cfg.get('enable_model_laws', False)}")
                lines.append(f"- **Avalanche Enabled:** {physics_cfg.get('enable_avalanche', False)}")
            lines.append("")

        lines.append("---")
        lines.append("*Generated by Kenobase V2.0*")

        return "\n".join(lines)

    def _format_yaml(self, data: dict) -> str:
        """Formatiert als YAML."""
        try:
            import yaml
            return yaml.dump(
                data,
                default_flow_style=False,
                allow_unicode=True,
                indent=self.config.indent,
                sort_keys=False,
            )
        except ImportError:
            # Fallback: Simple YAML-like formatting
            return self._simple_yaml_format(data)

    def _simple_yaml_format(self, data: dict, indent: int = 0) -> str:
        """Einfache YAML-Formatierung ohne pyyaml Abhaengigkeit."""
        lines = []
        prefix = "  " * indent

        for key, value in data.items():
            if value is None:
                lines.append(f"{prefix}{key}: null")
            elif isinstance(value, bool):
                lines.append(f"{prefix}{key}: {str(value).lower()}")
            elif isinstance(value, (int, float)):
                lines.append(f"{prefix}{key}: {value}")
            elif isinstance(value, str):
                # Escape quotes if needed
                if "\n" in value or ":" in value or value.startswith(" "):
                    lines.append(f'{prefix}{key}: "{value}"')
                else:
                    lines.append(f"{prefix}{key}: {value}")
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{prefix}  -")
                        nested = self._simple_yaml_format(item, indent + 2)
                        lines.append(nested)
                    else:
                        lines.append(f"{prefix}  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                nested = self._simple_yaml_format(value, indent + 1)
                lines.append(nested)
            else:
                lines.append(f"{prefix}{key}: {value}")

        return "\n".join(lines)


def format_output(data: dict, output_format: str) -> str:
    """Convenience-Funktion fuer Format-Konvertierung.

    Kompatibel mit der alten API aus scripts/analyze.py.

    Args:
        data: Pipeline-Ergebnisse als Dict.
        output_format: Zielformat ("json", "csv", "html", "markdown", "yaml").

    Returns:
        Formatierter String.
    """
    formatter = OutputFormatter()
    return formatter.format(data, output_format)


def get_supported_formats() -> list[str]:
    """Gibt Liste der unterstuetzten Formate zurueck."""
    return [f.value for f in OutputFormat]


__all__ = [
    "CustomJSONEncoder",
    "FormatterConfig",
    "OutputFormat",
    "OutputFormatter",
    "format_output",
    "get_supported_formats",
]
