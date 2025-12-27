#!/usr/bin/env python
"""Kenobase CLI - Command-Line Interface fuer Analyse-Pipeline.

Usage:
    python scripts/analyze.py --help
    python scripts/analyze.py analyze --config config/default.yaml
    python scripts/analyze.py validate --combination 1,2,3,4,5,6
    python scripts/analyze.py info --config config/default.yaml
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.core.config import KenobaseConfig, load_config
from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.pipeline.output_formats import (
    OutputFormat,
    OutputFormatter,
    format_output,
    get_supported_formats,
)
from kenobase.pipeline.runner import PipelineResult, PipelineRunner


def setup_logging(verbosity: int) -> None:
    """Konfiguriert Logging basierend auf Verbosity-Level.

    Args:
        verbosity: 0=WARNING, 1=INFO, 2+=DEBUG
    """
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def filter_draws_by_date(
    draws: list[DrawResult],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> list[DrawResult]:
    """Filtert Ziehungen nach Datum.

    Args:
        draws: Liste von DrawResult-Objekten
        start_date: Startdatum (inklusive)
        end_date: Enddatum (inklusive)

    Returns:
        Gefilterte Liste von DrawResult-Objekten
    """
    filtered = draws
    if start_date:
        filtered = [d for d in filtered if d.date >= start_date]
    if end_date:
        filtered = [d for d in filtered if d.date <= end_date]
    return filtered


def parse_combination(combo_str: str) -> list[int]:
    """Parst Kombinations-String zu Integer-Liste.

    Args:
        combo_str: Komma-separierte Zahlen, z.B. "1,2,3,4,5,6"

    Returns:
        Liste von Integers
    """
    return [int(x.strip()) for x in combo_str.split(",")]


def result_to_dict(result: PipelineResult) -> dict:
    """Konvertiert PipelineResult zu serialisierbarem Dict.

    Args:
        result: PipelineResult-Objekt

    Returns:
        Dict fuer JSON-Serialisierung
    """
    output = {
        "timestamp": result.timestamp.isoformat(),
        "draws_count": result.draws_count,
        "warnings": result.warnings,
        "config_snapshot": result.config_snapshot,
    }

    # Frequency results
    output["frequency_results"] = [
        {
            "number": r.number,
            "count": r.absolute_frequency,
            "relative_frequency": r.relative_frequency,
            "classification": r.classification,
        }
        for r in result.frequency_results
    ]

    # Pair frequency results (top 20)
    output["pair_frequency_results"] = [
        {
            "pair": list(r.pair),
            "count": r.absolute_frequency,
            "relative_frequency": r.relative_frequency,
            "classification": r.classification,
        }
        for r in sorted(
            result.pair_frequency_results, key=lambda x: x.absolute_frequency, reverse=True
        )[:20]
    ]

    # Physics results
    if result.physics_result:
        pr = result.physics_result
        output["physics_result"] = {
            "stability_score": pr.stability_score,
            "is_stable_law": pr.is_stable_law,
            "criticality_score": pr.criticality_score,
            "criticality_level": pr.criticality_level,
            "hurst_exponent": pr.hurst_exponent,
            "regime_complexity": pr.regime_complexity,
            "recommended_max_picks": pr.recommended_max_picks,
        }
        if pr.avalanche_result:
            output["physics_result"]["avalanche"] = {
                "theta": pr.avalanche_result.theta,
                "state": pr.avalanche_result.state.value,
                "is_safe_to_bet": pr.avalanche_result.is_safe_to_bet,
            }

    # Pipeline selection
    if result.pipeline_selection:
        ps = result.pipeline_selection
        output["pipeline_selection"] = {
            "selected_name": ps.selected_name,
            "selected_action": ps.selected_action,
            "comparison_count": len(ps.all_actions),
        }

    # Pattern results (aggregated)
    if result.aggregated_patterns:
        output["aggregated_patterns"] = result.aggregated_patterns

    return output


# Legacy format_output removed - now using kenobase.pipeline.output_formats


# Main CLI Group
@click.group()
@click.version_option(version="2.0.0", prog_name="kenobase")
def cli():
    """Kenobase V2.0 - Lottozahlen-Analysesystem mit Physics-Integration."""
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    default="config/default.yaml",
    help="Pfad zur Konfigurationsdatei",
    type=click.Path(exists=False),
)
@click.option(
    "--data",
    "-d",
    required=True,
    help="Pfad zur Eingabe-CSV-Datei",
    type=click.Path(exists=True),
)
@click.option(
    "--output",
    "-o",
    help="Pfad zur Ausgabedatei (stdout wenn nicht angegeben)",
    type=click.Path(),
)
@click.option(
    "--format",
    "-f",
    "output_format",
    default="json",
    type=click.Choice(["json", "csv", "html", "markdown", "yaml"]),
    help="Ausgabeformat (json, csv, html, markdown, yaml)",
)
@click.option(
    "--start-date",
    "-s",
    help="Startdatum (YYYY-MM-DD)",
    type=click.DateTime(formats=["%Y-%m-%d"]),
)
@click.option(
    "--end-date",
    "-e",
    help="Enddatum (YYYY-MM-DD)",
    type=click.DateTime(formats=["%Y-%m-%d"]),
)
@click.option(
    "--combination",
    help="Spielkombination fuer Pattern-Analyse (z.B. 1,2,3,4,5,6)",
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def analyze(
    config: str,
    data: str,
    output: Optional[str],
    output_format: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    combination: Optional[str],
    verbose: int,
):
    """Fuehrt vollstaendige Analyse-Pipeline aus.

    Example:
        python scripts/analyze.py analyze -d data/raw/keno/KENO.csv -f json
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    # Load config
    logger.info(f"Loading config from {config}")
    cfg = load_config(config)

    # Load data
    logger.info(f"Loading data from {data}")
    loader = DataLoader()
    draws = loader.load(data)

    # Filter by date
    if start_date or end_date:
        original_count = len(draws)
        draws = filter_draws_by_date(draws, start_date, end_date)
        logger.info(f"Filtered draws: {original_count} -> {len(draws)}")

    if not draws:
        click.echo("Error: No draws found after filtering", err=True)
        sys.exit(1)

    # Parse combination if provided
    combo = None
    if combination:
        try:
            combo = parse_combination(combination)
            logger.info(f"Using combination: {combo}")
        except ValueError as e:
            click.echo(f"Error parsing combination: {e}", err=True)
            sys.exit(1)

    # Run pipeline
    logger.info("Running pipeline...")
    runner = PipelineRunner(cfg)
    result = runner.run(draws, combination=combo)

    # Format output using new output_formats module
    result_dict = result_to_dict(result)
    formatter = OutputFormatter()
    formatted = formatter.format(result_dict, output_format)

    # Write output
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted, encoding="utf-8")
        click.echo(f"Results written to {output}")
    else:
        click.echo(formatted)

    # Show warnings summary
    if result.warnings:
        click.echo(f"\n{len(result.warnings)} warning(s):", err=True)
        for w in result.warnings:
            click.echo(f"  - {w}", err=True)


@cli.command()
@click.option(
    "--config",
    "-c",
    default="config/default.yaml",
    help="Pfad zur Konfigurationsdatei",
    type=click.Path(exists=False),
)
@click.option(
    "--data",
    "-d",
    required=True,
    help="Pfad zur Eingabe-CSV-Datei",
    type=click.Path(exists=True),
)
@click.option(
    "--periods",
    "-p",
    default=10,
    help="Anzahl der Backtest-Perioden",
    type=int,
)
@click.option(
    "--output",
    "-o",
    help="Pfad zur Ausgabedatei",
    type=click.Path(),
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def backtest(
    config: str,
    data: str,
    periods: int,
    output: Optional[str],
    verbose: int,
):
    """Fuehrt historischen Backtest durch.

    Teilt Daten in Perioden und evaluiert Vorhersage-Qualitaet.

    Example:
        python scripts/analyze.py backtest -d data/raw/keno/KENO.csv -p 12
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    # Load config and data
    cfg = load_config(config)
    loader = DataLoader()
    draws = loader.load(data)

    if len(draws) < periods * 10:
        click.echo(
            f"Error: Not enough draws ({len(draws)}) for {periods} periods", err=True
        )
        sys.exit(1)

    # Split into periods
    period_size = len(draws) // periods
    results = []

    runner = PipelineRunner(cfg)

    for i in range(periods):
        start_idx = i * period_size
        end_idx = start_idx + period_size
        period_draws = draws[start_idx:end_idx]

        logger.info(f"Running period {i + 1}/{periods} ({len(period_draws)} draws)")
        result = runner.run(period_draws)

        period_result = {
            "period": i + 1,
            "start_date": period_draws[0].date.isoformat() if period_draws else None,
            "end_date": period_draws[-1].date.isoformat() if period_draws else None,
            "draws_count": result.draws_count,
            "warnings_count": len(result.warnings),
        }

        if result.physics_result:
            period_result["stability_score"] = result.physics_result.stability_score
            period_result["criticality_level"] = result.physics_result.criticality_level

        results.append(period_result)

    # Aggregate
    output_data = {
        "backtest_timestamp": datetime.now().isoformat(),
        "total_draws": len(draws),
        "periods": periods,
        "period_results": results,
        "summary": {
            "avg_stability": sum(
                r.get("stability_score", 0) for r in results if "stability_score" in r
            )
            / max(1, sum(1 for r in results if "stability_score" in r)),
            "critical_periods": sum(
                1 for r in results if r.get("criticality_level") == "CRITICAL"
            ),
        },
    }

    formatted = json.dumps(output_data, indent=2, ensure_ascii=False)

    if output:
        Path(output).write_text(formatted, encoding="utf-8")
        click.echo(f"Backtest results written to {output}")
    else:
        click.echo(formatted)


@cli.command()
@click.option(
    "--config",
    "-c",
    default="config/default.yaml",
    help="Pfad zur Konfigurationsdatei",
    type=click.Path(exists=False),
)
@click.option(
    "--combination",
    required=True,
    help="Spielkombination (z.B. 1,2,3,4,5,6)",
)
@click.option(
    "--precision",
    "-p",
    default=0.7,
    help="Geschaetzte Precision pro Zahl",
    type=float,
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def validate(
    config: str,
    combination: str,
    precision: float,
    verbose: int,
):
    """Validiert eine Kombination gegen Physics-Constraints.

    Berechnet Avalanche-Risiko und gibt Empfehlungen.

    Example:
        python scripts/analyze.py validate --combination 1,2,3,4,5,6
    """
    setup_logging(verbose)

    # Load config
    cfg = load_config(config)

    # Parse combination
    try:
        combo = parse_combination(combination)
    except ValueError as e:
        click.echo(f"Error parsing combination: {e}", err=True)
        sys.exit(1)

    # Validate
    runner = PipelineRunner(cfg)
    result = runner.validate_combination(combo, precision_estimate=precision)

    # Output
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))

    # Exit code based on safety
    if not result["is_safe_to_bet"]:
        click.echo(
            f"\nWarning: Combination is in {result['state']} state!", err=True
        )
        sys.exit(2)


@cli.command()
@click.option(
    "--config",
    "-c",
    default="config/default.yaml",
    help="Pfad zur Konfigurationsdatei",
    type=click.Path(exists=False),
)
def info(config: str):
    """Zeigt Konfigurationsinformationen an.

    Example:
        python scripts/analyze.py info --config config/keno.yaml
    """
    cfg = load_config(config)

    info_data = {
        "version": cfg.version,
        "active_game": cfg.active_game,
        "game_config": {
            "name": cfg.get_active_game().name,
            "numbers_range": list(cfg.get_active_game().numbers_range),
            "numbers_to_draw": cfg.get_active_game().numbers_to_draw,
        },
        "physics": {
            "enable_model_laws": cfg.physics.enable_model_laws,
            "stability_threshold": cfg.physics.stability_threshold,
            "criticality_warning": cfg.physics.criticality_warning_threshold,
            "criticality_critical": cfg.physics.criticality_critical_threshold,
            "enable_avalanche": cfg.physics.enable_avalanche,
            "anti_avalanche_mode": cfg.physics.anti_avalanche_mode,
        },
        "paths": {
            "data_dir": cfg.paths.data_dir,
            "output_dir": cfg.paths.output_dir,
        },
    }

    click.echo(json.dumps(info_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    cli()
