#!/usr/bin/env python3
"""Kenobase Report Generator - Generiert HTML/Markdown Reports aus Backtest-Ergebnissen.

Dieses Script konsumiert BacktestResult JSON-Dateien und generiert
formatierte Reports in HTML oder Markdown.

Usage:
    python scripts/report.py --help
    python scripts/report.py --input output/backtest.json --format html --output reports/report.html
    python scripts/report.py --input output/backtest.json --format markdown --output reports/report.md

Gemaess CLAUDE.md Phase 5 Task 5.3: Report-Generator.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import click

logger = logging.getLogger(__name__)


# =============================================================================
# Report Generation
# =============================================================================


def generate_html_report(data: dict, title: str) -> str:
    """Generiert einen HTML-Report aus BacktestResult JSON.

    Args:
        data: BacktestResult als Dict (aus JSON geladen)
        title: Titel fuer den Report

    Returns:
        HTML-String
    """
    timestamp = data.get("backtest_timestamp", "N/A")
    config_name = data.get("config_name", "N/A")
    total_draws = data.get("total_draws", 0)
    n_periods = data.get("n_periods", 0)
    summary = data.get("summary", {})
    period_results = data.get("period_results", [])

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #666; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 30px; }}
        .meta {{ color: #888; font-size: 0.9em; margin-bottom: 20px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .summary-item {{ background: #f0f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3; }}
        .summary-item strong {{ color: #333; display: block; margin-bottom: 5px; }}
        .summary-item .value {{ font-size: 1.5em; color: #2196F3; }}
        table {{ border-collapse: collapse; margin: 10px 0; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .good {{ color: #4CAF50; font-weight: bold; }}
        .warning {{ color: #FF9800; font-weight: bold; }}
        .critical {{ color: #f44336; font-weight: bold; }}
        .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #ddd; color: #888; font-size: 0.8em; }}
    </style>
</head>
<body>
<div class="container">
    <h1>{title}</h1>
    <p class="meta">
        <strong>Timestamp:</strong> {timestamp}<br>
        <strong>Config:</strong> {config_name}<br>
        <strong>Total Draws:</strong> {total_draws}<br>
        <strong>Periods:</strong> {n_periods}
    </p>

    <h2>Summary</h2>
    <div class="summary-grid">
        <div class="summary-item">
            <strong>Avg Precision</strong>
            <span class="value">{summary.get('avg_precision', 0):.4f}</span>
        </div>
        <div class="summary-item">
            <strong>Avg Recall</strong>
            <span class="value">{summary.get('avg_recall', 0):.4f}</span>
        </div>
        <div class="summary-item">
            <strong>Avg F1-Score</strong>
            <span class="value">{summary.get('avg_f1', 0):.4f}</span>
        </div>
        <div class="summary-item">
            <strong>F1 Std Dev</strong>
            <span class="value">{summary.get('std_f1', 0):.4f}</span>
        </div>
        <div class="summary-item">
            <strong>Avg Stability</strong>
            <span class="value">{summary.get('avg_stability', 0):.4f}</span>
        </div>
        <div class="summary-item">
            <strong>Critical Periods</strong>
            <span class="value">{summary.get('critical_periods', 0)}</span>
        </div>
    </div>

    <p>
        <strong>Best Period:</strong> #{summary.get('best_period', 'N/A')}
        (F1={summary.get('best_f1', 0):.4f})<br>
        <strong>Worst Period:</strong> #{summary.get('worst_period', 'N/A')}
        (F1={summary.get('worst_f1', 0):.4f})
    </p>

    <h2>Period Details</h2>
    <table>
        <tr>
            <th>Period</th>
            <th>Train</th>
            <th>Test</th>
            <th>Predicted</th>
            <th>Hits</th>
            <th>Precision</th>
            <th>Recall</th>
            <th>F1</th>
            <th>Stability</th>
            <th>Criticality</th>
        </tr>
"""

    for r in period_results:
        criticality = r.get("criticality_level", "UNKNOWN")
        crit_class = "critical" if criticality == "CRITICAL" else ""
        f1_class = "good" if r.get("f1_score", 0) >= 0.3 else ""

        html += f"""        <tr>
            <td>{r.get('period_id', '')}</td>
            <td>{r.get('train_draws', '')}</td>
            <td>{r.get('test_draws', '')}</td>
            <td>{len(r.get('predicted_hot', []))}</td>
            <td>{r.get('total_hits', '')}</td>
            <td>{r.get('precision', 0):.4f}</td>
            <td>{r.get('recall', 0):.4f}</td>
            <td class="{f1_class}">{r.get('f1_score', 0):.4f}</td>
            <td>{r.get('stability_score', 0):.4f}</td>
            <td class="{crit_class}">{criticality}</td>
        </tr>
"""

    html += """    </table>

    <div class="footer">
        <p>Generated by Kenobase V2.0 Report Generator</p>
    </div>
</div>
</body>
</html>"""

    return html


def generate_markdown_report(data: dict, title: str) -> str:
    """Generiert einen Markdown-Report aus BacktestResult JSON.

    Args:
        data: BacktestResult als Dict (aus JSON geladen)
        title: Titel fuer den Report

    Returns:
        Markdown-String (GFM-kompatibel)
    """
    timestamp = data.get("backtest_timestamp", "N/A")
    config_name = data.get("config_name", "N/A")
    total_draws = data.get("total_draws", 0)
    n_periods = data.get("n_periods", 0)
    summary = data.get("summary", {})
    period_results = data.get("period_results", [])

    lines = [
        f"# {title}",
        "",
        f"**Timestamp:** {timestamp}  ",
        f"**Config:** {config_name}  ",
        f"**Total Draws:** {total_draws}  ",
        f"**Periods:** {n_periods}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Avg Precision | {summary.get('avg_precision', 0):.4f} |",
        f"| Avg Recall | {summary.get('avg_recall', 0):.4f} |",
        f"| Avg F1 | {summary.get('avg_f1', 0):.4f} |",
        f"| F1 Std Dev | {summary.get('std_f1', 0):.4f} |",
        f"| Avg Stability | {summary.get('avg_stability', 0):.4f} |",
        f"| Critical Periods | {summary.get('critical_periods', 0)} |",
        f"| Best Period | #{summary.get('best_period', 'N/A')} (F1={summary.get('best_f1', 0):.4f}) |",
        f"| Worst Period | #{summary.get('worst_period', 'N/A')} (F1={summary.get('worst_f1', 0):.4f}) |",
        "",
        "## Period Details",
        "",
        "| Period | Train | Test | Predicted | Hits | Precision | Recall | F1 | Stability | Criticality |",
        "|--------|-------|------|-----------|------|-----------|--------|-----|-----------|-------------|",
    ]

    for r in period_results:
        lines.append(
            f"| {r.get('period_id', '')} | {r.get('train_draws', '')} | "
            f"{r.get('test_draws', '')} | {len(r.get('predicted_hot', []))} | "
            f"{r.get('total_hits', '')} | {r.get('precision', 0):.4f} | "
            f"{r.get('recall', 0):.4f} | {r.get('f1_score', 0):.4f} | "
            f"{r.get('stability_score', 0):.4f} | {r.get('criticality_level', 'UNKNOWN')} |"
        )

    lines.extend([
        "",
        "---",
        "*Generated by Kenobase V2.0 Report Generator*",
    ])

    return "\n".join(lines)


def load_backtest_json(path: Path) -> dict:
    """Laedt BacktestResult JSON-Datei.

    Args:
        path: Pfad zur JSON-Datei

    Returns:
        Dict mit BacktestResult Daten

    Raises:
        FileNotFoundError: Wenn Datei nicht existiert
        json.JSONDecodeError: Wenn JSON ungueltig
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# CLI
# =============================================================================


def setup_logging(verbose: int) -> None:
    """Konfiguriert Logging basierend auf Verbosity."""
    if verbose >= 2:
        level = logging.DEBUG
    elif verbose >= 1:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


@click.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    help="Pfad zur Eingabe-JSON-Datei (BacktestResult)",
    type=click.Path(exists=True),
)
@click.option(
    "--format",
    "-f",
    "output_format",
    default="html",
    type=click.Choice(["html", "markdown"]),
    help="Ausgabeformat (default: html)",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    help="Pfad zur Ausgabedatei (optional, sonst stdout)",
    type=click.Path(),
)
@click.option(
    "--title",
    "-t",
    default="Kenobase Backtest Report",
    help="Titel fuer den Report",
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def main(
    input_file: str,
    output_format: str,
    output_file: Optional[str],
    title: str,
    verbose: int,
) -> None:
    """Generiert HTML/Markdown Reports aus BacktestResult JSON-Dateien.

    Liest eine JSON-Datei, die von scripts/backtest.py erzeugt wurde,
    und generiert einen formatierten Report.

    \b
    Unterstuetzte Formate:
    - html: Interaktiver HTML-Report mit Styling
    - markdown: GFM-kompatibles Markdown

    \b
    Beispiele:
        python scripts/report.py -i output/backtest.json -f html -o reports/report.html
        python scripts/report.py -i output/backtest.json -f markdown -o reports/report.md
        python scripts/report.py -i output/backtest.json -f html -t "KENO Analysis Q4 2024"
    """
    setup_logging(verbose)

    input_path = Path(input_file)

    # Load JSON
    try:
        data = load_backtest_json(input_path)
        logger.info(f"Loaded backtest data from {input_path}")
    except FileNotFoundError:
        click.echo(f"Error: File not found: {input_file}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in {input_file}: {e}", err=True)
        sys.exit(1)

    # Validate required fields
    required_fields = ["backtest_timestamp", "summary", "period_results"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        click.echo(
            f"Error: Missing required fields in JSON: {missing}",
            err=True,
        )
        sys.exit(1)

    # Generate report
    if output_format == "html":
        report = generate_html_report(data, title)
        logger.info("Generated HTML report")
    else:
        report = generate_markdown_report(data, title)
        logger.info("Generated Markdown report")

    # Write or print output
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        click.echo(f"Report written to {output_file}")
    else:
        click.echo(report)

    # Summary stats
    summary = data.get("summary", {})
    n_periods = data.get("n_periods", 0)
    click.echo(f"\n--- Report Generated ---", err=True)
    click.echo(f"Periods: {n_periods}", err=True)
    click.echo(f"Avg F1: {summary.get('avg_f1', 0):.4f}", err=True)


if __name__ == "__main__":
    main()
