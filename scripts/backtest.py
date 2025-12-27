#!/usr/bin/env python3
"""Kenobase Backtest Script - Historisches Walk-Forward Backtesting.

Dieses Script implementiert das Backtest-System fuer Kenobase V2.0.
Es fuehrt Walk-Forward-Backtests durch und berechnet Precision, Recall, F1-Score.

Usage:
    python scripts/backtest.py --help
    python scripts/backtest.py -d data/raw/keno/KENO.csv -p 12 -o output/backtest.json

Gemaess CLAUDE.md Phase 5: Validation & Backtest.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Optional

import click

from kenobase.analysis.frequency import get_hot_numbers
from kenobase.core.config import KenobaseConfig, load_config
from kenobase.core.data_loader import DataLoader, DrawResult
from kenobase.pipeline.runner import PipelineRunner
from kenobase.pipeline.validation_metrics import (
    calculate_hits,
    calculate_metrics_dict as calculate_metrics,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class BacktestPeriodResult:
    """Ergebnis einer einzelnen Backtest-Periode.

    Attributes:
        period_id: Nummer der Periode (1-basiert)
        train_start: Start-Datum Trainingsperiode
        train_end: End-Datum Trainingsperiode
        test_start: Start-Datum Testperiode
        test_end: End-Datum Testperiode
        train_draws: Anzahl Trainings-Ziehungen
        test_draws: Anzahl Test-Ziehungen
        predicted_hot: Liste der vorhergesagten Hot-Numbers
        total_hits: Anzahl Treffer (predicted in actual)
        total_predictions: Anzahl Vorhersagen * Test-Ziehungen
        precision: hits / (len(predicted) * test_draws)
        recall: hits / (numbers_per_draw * test_draws)
        f1_score: 2 * P * R / (P + R)
        stability_score: Stability-Score aus Physics Layer
        criticality_level: Criticality-Level aus Physics Layer
    """

    period_id: int
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_draws: int
    test_draws: int
    predicted_hot: list[int]
    total_hits: int
    total_predictions: int
    precision: float
    recall: float
    f1_score: float
    stability_score: float
    criticality_level: str


@dataclass
class BacktestResult:
    """Gesamt-Ergebnis eines Backtests.

    Attributes:
        timestamp: Zeitpunkt der Ausfuehrung
        config_name: Name der verwendeten Konfiguration
        total_draws: Gesamtzahl Ziehungen
        n_periods: Anzahl Perioden
        period_results: Ergebnisse pro Periode
        summary: Aggregierte Metriken
    """

    timestamp: datetime
    config_name: str
    total_draws: int
    n_periods: int
    period_results: list[BacktestPeriodResult]
    summary: dict = field(default_factory=dict)


# =============================================================================
# Backtest Engine
# =============================================================================


class BacktestEngine:
    """Walk-Forward Backtest Engine.

    Fuehrt historische Backtests durch mit Train/Test-Split pro Periode.
    Nutzt PipelineRunner fuer Physics-Layer Integration.

    Example:
        >>> config = load_config("config/default.yaml")
        >>> engine = BacktestEngine(config)
        >>> draws = DataLoader().load("data/raw/keno/KENO.csv")
        >>> result = engine.run(draws, n_periods=12)
        >>> print(f"Avg F1: {result.summary['avg_f1']:.3f}")
    """

    def __init__(self, config: KenobaseConfig) -> None:
        """Initialisiert BacktestEngine.

        Args:
            config: Kenobase-Konfiguration
        """
        self.config = config
        self.runner = PipelineRunner(config)

    def run(
        self,
        draws: list[DrawResult],
        n_periods: int = 12,
        train_ratio: float = 0.8,
    ) -> BacktestResult:
        """Fuehrt Walk-Forward Backtest durch.

        Teilt Daten in n_periods auf. Fuer jede Periode:
        1. Train auf ersten train_ratio% der Periode
        2. Identifiziere Hot-Numbers aus Training
        3. Evaluiere auf restlichen (1-train_ratio)% als Test

        Args:
            draws: Chronologisch sortierte Ziehungen
            n_periods: Anzahl Backtest-Perioden
            train_ratio: Anteil Training pro Periode (default 0.8)

        Returns:
            BacktestResult mit allen Perioden-Ergebnissen

        Raises:
            ValueError: Wenn zu wenig Ziehungen fuer n_periods
        """
        min_draws = n_periods * 10
        if len(draws) < min_draws:
            raise ValueError(
                f"Not enough draws ({len(draws)}) for {n_periods} periods. "
                f"Need at least {min_draws}."
            )

        # Sort draws chronologically
        sorted_draws = sorted(draws, key=lambda d: d.date)

        # Calculate period size
        period_size = len(sorted_draws) // n_periods
        train_size = int(period_size * train_ratio)
        test_size = period_size - train_size

        # Get game config for numbers_per_draw
        game_config = self.config.get_active_game()
        numbers_per_draw = game_config.numbers_to_draw

        period_results: list[BacktestPeriodResult] = []

        for i in range(n_periods):
            start_idx = i * period_size
            train_end_idx = start_idx + train_size
            test_end_idx = start_idx + period_size

            train_draws = sorted_draws[start_idx:train_end_idx]
            test_draws = sorted_draws[train_end_idx:test_end_idx]

            if not train_draws or not test_draws:
                logger.warning(f"Period {i + 1}: Skipping due to empty train/test")
                continue

            # Get hot numbers from training period
            # Use game-specific thresholds (ADR-018 style: 1.3x/0.7x expected frequency)
            predicted_hot = get_hot_numbers(
                train_draws,
                hot_threshold=game_config.get_hot_threshold(),
                cold_threshold=game_config.get_cold_threshold(),
                number_range=game_config.numbers_range,
            )

            # Calculate metrics on test period
            metrics = calculate_metrics(
                predicted_hot,
                test_draws,
                numbers_per_draw=numbers_per_draw,
            )

            # Run pipeline on training for physics metrics
            pipeline_result = self.runner.run(train_draws)

            stability_score = 0.0
            criticality_level = "UNKNOWN"
            if pipeline_result.physics_result:
                stability_score = pipeline_result.physics_result.stability_score
                criticality_level = pipeline_result.physics_result.criticality_level

            period_result = BacktestPeriodResult(
                period_id=i + 1,
                train_start=train_draws[0].date,
                train_end=train_draws[-1].date,
                test_start=test_draws[0].date,
                test_end=test_draws[-1].date,
                train_draws=len(train_draws),
                test_draws=len(test_draws),
                predicted_hot=predicted_hot,
                total_hits=metrics["hits"],
                total_predictions=metrics["total_predictions"],
                precision=metrics["precision"],
                recall=metrics["recall"],
                f1_score=metrics["f1_score"],
                stability_score=stability_score,
                criticality_level=criticality_level,
            )
            period_results.append(period_result)

            logger.info(
                f"Period {i + 1}/{n_periods}: "
                f"P={metrics['precision']:.3f}, "
                f"R={metrics['recall']:.3f}, "
                f"F1={metrics['f1_score']:.3f}"
            )

        # Generate summary
        summary = self._generate_summary(period_results)

        return BacktestResult(
            timestamp=datetime.now(),
            config_name=self.config.version,
            total_draws=len(draws),
            n_periods=n_periods,
            period_results=period_results,
            summary=summary,
        )

    def _generate_summary(
        self,
        period_results: list[BacktestPeriodResult],
    ) -> dict:
        """Aggregiert Metriken ueber alle Perioden.

        Args:
            period_results: Liste der Perioden-Ergebnisse

        Returns:
            Dict mit aggregierten Metriken
        """
        if not period_results:
            return {
                "avg_precision": 0.0,
                "avg_recall": 0.0,
                "avg_f1": 0.0,
                "std_f1": 0.0,
                "avg_stability": 0.0,
                "critical_periods": 0,
                "best_period": None,
                "worst_period": None,
            }

        precisions = [r.precision for r in period_results]
        recalls = [r.recall for r in period_results]
        f1_scores = [r.f1_score for r in period_results]
        stability_scores = [r.stability_score for r in period_results]

        best_period = max(period_results, key=lambda r: r.f1_score)
        worst_period = min(period_results, key=lambda r: r.f1_score)

        return {
            "avg_precision": mean(precisions),
            "avg_recall": mean(recalls),
            "avg_f1": mean(f1_scores),
            "std_f1": stdev(f1_scores) if len(f1_scores) > 1 else 0.0,
            "avg_stability": mean(stability_scores),
            "critical_periods": sum(
                1 for r in period_results if r.criticality_level == "CRITICAL"
            ),
            "best_period": best_period.period_id,
            "worst_period": worst_period.period_id,
            "best_f1": best_period.f1_score,
            "worst_f1": worst_period.f1_score,
        }


# =============================================================================
# Output Formatting
# =============================================================================


def format_result_json(result: BacktestResult) -> str:
    """Formatiert BacktestResult als JSON.

    Args:
        result: BacktestResult

    Returns:
        JSON-String
    """
    data = {
        "backtest_timestamp": result.timestamp.isoformat(),
        "config_name": result.config_name,
        "total_draws": result.total_draws,
        "n_periods": result.n_periods,
        "period_results": [
            {
                "period_id": r.period_id,
                "train_start": r.train_start.isoformat(),
                "train_end": r.train_end.isoformat(),
                "test_start": r.test_start.isoformat(),
                "test_end": r.test_end.isoformat(),
                "train_draws": r.train_draws,
                "test_draws": r.test_draws,
                "predicted_hot": r.predicted_hot,
                "total_hits": r.total_hits,
                "total_predictions": r.total_predictions,
                "precision": round(r.precision, 4),
                "recall": round(r.recall, 4),
                "f1_score": round(r.f1_score, 4),
                "stability_score": round(r.stability_score, 4),
                "criticality_level": r.criticality_level,
            }
            for r in result.period_results
        ],
        "summary": {
            k: round(v, 4) if isinstance(v, float) else v
            for k, v in result.summary.items()
        },
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_result_markdown(result: BacktestResult) -> str:
    """Formatiert BacktestResult als Markdown-Report.

    Args:
        result: BacktestResult

    Returns:
        Markdown-String
    """
    lines = [
        "# Kenobase Backtest Report",
        "",
        f"**Timestamp:** {result.timestamp.isoformat()}",
        f"**Total Draws:** {result.total_draws}",
        f"**Periods:** {result.n_periods}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Avg Precision | {result.summary.get('avg_precision', 0):.4f} |",
        f"| Avg Recall | {result.summary.get('avg_recall', 0):.4f} |",
        f"| Avg F1 | {result.summary.get('avg_f1', 0):.4f} |",
        f"| F1 Std Dev | {result.summary.get('std_f1', 0):.4f} |",
        f"| Avg Stability | {result.summary.get('avg_stability', 0):.4f} |",
        f"| Critical Periods | {result.summary.get('critical_periods', 0)} |",
        f"| Best Period | #{result.summary.get('best_period', 'N/A')} (F1={result.summary.get('best_f1', 0):.4f}) |",
        f"| Worst Period | #{result.summary.get('worst_period', 'N/A')} (F1={result.summary.get('worst_f1', 0):.4f}) |",
        "",
        "## Period Details",
        "",
        "| Period | Train | Test | Predicted | Hits | Precision | Recall | F1 | Stability | Criticality |",
        "|--------|-------|------|-----------|------|-----------|--------|-----|-----------|-------------|",
    ]

    for r in result.period_results:
        lines.append(
            f"| {r.period_id} | {r.train_draws} | {r.test_draws} | "
            f"{len(r.predicted_hot)} | {r.total_hits} | "
            f"{r.precision:.4f} | {r.recall:.4f} | {r.f1_score:.4f} | "
            f"{r.stability_score:.4f} | {r.criticality_level} |"
        )

    lines.append("")
    return "\n".join(lines)


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
    default=12,
    help="Anzahl der Backtest-Perioden",
    type=int,
)
@click.option(
    "--train-ratio",
    "-t",
    default=0.8,
    help="Train/Test-Split Verhaeltnis (default 0.8)",
    type=float,
)
@click.option(
    "--output",
    "-o",
    help="Pfad zur Ausgabedatei",
    type=click.Path(),
)
@click.option(
    "--format",
    "-f",
    "output_format",
    default="json",
    type=click.Choice(["json", "markdown"]),
    help="Ausgabeformat (default: json)",
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def main(
    config: str,
    data: str,
    periods: int,
    train_ratio: float,
    output: Optional[str],
    output_format: str,
    verbose: int,
) -> None:
    """Fuehrt historischen Walk-Forward Backtest durch.

    Teilt Daten in Perioden, trainiert auf Trainingsperiode,
    evaluiert Vorhersage-Qualitaet auf Testperiode.

    \b
    Metriken:
    - Precision: Wie oft war eine vorhergesagte Hot-Number im Draw?
    - Recall: Wie viele der tatsaechlichen Zahlen wurden vorhergesagt?
    - F1-Score: Harmonisches Mittel aus Precision und Recall

    \b
    Example:
        python scripts/backtest.py -d data/raw/keno/KENO.csv -p 12
        python scripts/backtest.py -d data/raw/keno/KENO.csv -p 12 -o output/backtest.json
        python scripts/backtest.py -d data/raw/keno/KENO.csv -p 6 -f markdown -o report.md
    """
    setup_logging(verbose)

    # Validate train_ratio
    if not 0.1 <= train_ratio <= 0.95:
        click.echo("Error: train-ratio must be between 0.1 and 0.95", err=True)
        sys.exit(1)

    # Load config
    cfg = load_config(config)
    click.echo(f"Config loaded: {config}")

    # Load data
    loader = DataLoader()
    try:
        draws = loader.load(data)
    except FileNotFoundError:
        click.echo(f"Error: File not found: {data}", err=True)
        sys.exit(1)

    click.echo(f"Loaded {len(draws)} draws from {data}")

    # Validate enough data
    min_draws = periods * 10
    if len(draws) < min_draws:
        click.echo(
            f"Error: Not enough draws ({len(draws)}) for {periods} periods. "
            f"Need at least {min_draws}.",
            err=True,
        )
        sys.exit(1)

    # Run backtest
    engine = BacktestEngine(cfg)
    try:
        result = engine.run(draws, n_periods=periods, train_ratio=train_ratio)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Format output
    if output_format == "markdown":
        formatted = format_result_markdown(result)
    else:
        formatted = format_result_json(result)

    # Write or print output
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted, encoding="utf-8")
        click.echo(f"Results written to {output}")
    else:
        click.echo(formatted)

    # Print summary
    click.echo("\n--- Summary ---")
    click.echo(f"Avg F1-Score: {result.summary.get('avg_f1', 0):.4f}")
    click.echo(f"F1 Std Dev:   {result.summary.get('std_f1', 0):.4f}")
    click.echo(f"Best Period:  #{result.summary.get('best_period')} (F1={result.summary.get('best_f1', 0):.4f})")
    click.echo(f"Worst Period: #{result.summary.get('worst_period')} (F1={result.summary.get('worst_f1', 0):.4f})")


if __name__ == "__main__":
    main()
