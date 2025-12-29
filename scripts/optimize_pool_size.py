#!/usr/bin/env python3
"""Kenobase Pool Size Optimization Script.

Dieses Script optimiert die Top-Pool-Size (top_n_per_period) fuer NumberPoolGenerator.
Es vergleicht verschiedene Pool-Sizes [5, 11, 15, 20] via Walk-Forward Backtest
und ermittelt die optimale Groesse basierend auf F1-Score.

Usage:
    python scripts/optimize_pool_size.py --help
    python scripts/optimize_pool_size.py -d data/raw/keno/KENO_ab_2018.csv
    python scripts/optimize_pool_size.py -d data/raw/keno/KENO.csv -o results/pool_optimization.json

Gemaess CLAUDE.md TASK-M01: Top-Pool Size Optimierung.
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

from kenobase.core.config import load_config
from kenobase.core.data_loader import DataLoader, DrawResult
from kenobase.core.number_pool import NumberPoolGenerator

logger = logging.getLogger(__name__)


# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class PoolSizePeriodResult:
    """Ergebnis einer Backtest-Periode fuer eine Pool-Size.

    Attributes:
        period_id: Nummer der Periode (1-basiert)
        pool_size: Anzahl Pool-Zahlen
        predicted_numbers: Generierte Pool-Zahlen
        hits: Treffer in der Test-Ziehung
        precision: hits / pool_size
        recall: hits / numbers_per_draw
        f1_score: 2 * P * R / (P + R)
    """

    period_id: int
    pool_size: int
    predicted_numbers: list[int]
    hits: int
    precision: float
    recall: float
    f1_score: float


@dataclass
class PoolSizeResult:
    """Aggregiertes Ergebnis fuer eine Pool-Size.

    Attributes:
        top_n_per_period: Getestete Pool-Size
        period_results: Ergebnisse pro Periode
        avg_precision: Durchschnittliche Precision
        avg_recall: Durchschnittlicher Recall
        avg_f1: Durchschnittlicher F1-Score
        std_f1: Standardabweichung des F1-Score
        avg_pool_size: Durchschnittliche generierte Pool-Groesse
    """

    top_n_per_period: int
    period_results: list[PoolSizePeriodResult]
    avg_precision: float
    avg_recall: float
    avg_f1: float
    std_f1: float
    avg_pool_size: float


@dataclass
class OptimizationResult:
    """Gesamtergebnis der Pool-Size-Optimierung.

    Attributes:
        timestamp: Zeitpunkt der Ausfuehrung
        total_draws: Gesamtzahl Ziehungen
        n_periods: Anzahl Backtest-Perioden
        pool_sizes_tested: Liste getesteter Pool-Sizes
        results: Ergebnisse pro Pool-Size
        optimal_pool_size: Beste Pool-Size basierend auf F1-Score
        summary: Aggregierte Zusammenfassung
    """

    timestamp: datetime
    total_draws: int
    n_periods: int
    pool_sizes_tested: list[int]
    results: list[PoolSizeResult]
    optimal_pool_size: int
    summary: dict = field(default_factory=dict)


# =============================================================================
# Optimization Engine
# =============================================================================


class PoolSizeOptimizer:
    """Optimizer fuer Top-Pool Size via Walk-Forward Backtest.

    Testet verschiedene Pool-Sizes und ermittelt die optimale Groesse
    basierend auf durchschnittlichem F1-Score.

    Example:
        >>> optimizer = PoolSizeOptimizer(numbers_per_draw=20)
        >>> draws = DataLoader().load("data/raw/keno/KENO.csv")
        >>> result = optimizer.optimize(draws, pool_sizes=[5, 11, 15, 20])
        >>> print(f"Optimal: {result.optimal_pool_size}")
    """

    def __init__(
        self,
        numbers_per_draw: int = 20,
        n_periods: int = 3,
        draws_per_period: int = 10,
    ) -> None:
        """Initialisiert PoolSizeOptimizer.

        Args:
            numbers_per_draw: Anzahl Zahlen pro Ziehung (KENO: 20)
            n_periods: Anzahl Zeitraeume fuer NumberPoolGenerator
            draws_per_period: Ziehungen pro Zeitraum
        """
        self.numbers_per_draw = numbers_per_draw
        self.n_periods = n_periods
        self.draws_per_period = draws_per_period

    def optimize(
        self,
        draws: list[DrawResult],
        pool_sizes: list[int],
        n_test_periods: int = 12,
        train_ratio: float = 0.8,
    ) -> OptimizationResult:
        """Fuehrt Pool-Size-Optimierung durch.

        Fuer jede Pool-Size wird ein Walk-Forward Backtest durchgefuehrt:
        1. Training: Generiere Pool mit NumberPoolGenerator
        2. Test: Evaluiere Pool gegen naechste Ziehung

        Args:
            draws: Chronologisch sortierte Ziehungen
            pool_sizes: Liste der zu testenden Pool-Sizes
            n_test_periods: Anzahl Backtest-Perioden
            train_ratio: Train/Test-Split

        Returns:
            OptimizationResult mit allen Ergebnissen
        """
        # Mindestanforderung fuer Walk-Forward
        min_train_draws = self.n_periods * self.draws_per_period
        min_draws = n_test_periods * (min_train_draws + 1)

        if len(draws) < min_draws:
            raise ValueError(
                f"Not enough draws ({len(draws)}) for optimization. "
                f"Need at least {min_draws}."
            )

        # Sort draws chronologically
        sorted_draws = sorted(draws, key=lambda d: d.date)

        results: list[PoolSizeResult] = []

        for top_n in pool_sizes:
            logger.info(f"Testing top_n_per_period={top_n}")
            pool_result = self._evaluate_pool_size(
                sorted_draws, top_n, n_test_periods
            )
            results.append(pool_result)
            logger.info(
                f"  -> Avg F1: {pool_result.avg_f1:.4f}, "
                f"Avg Pool Size: {pool_result.avg_pool_size:.1f}"
            )

        # Find optimal pool size
        best_result = max(results, key=lambda r: r.avg_f1)
        optimal_pool_size = best_result.top_n_per_period

        # Generate summary
        summary = {
            "optimal_top_n_per_period": optimal_pool_size,
            "optimal_avg_f1": best_result.avg_f1,
            "optimal_std_f1": best_result.std_f1,
            "all_results": [
                {
                    "top_n_per_period": r.top_n_per_period,
                    "avg_f1": round(r.avg_f1, 4),
                    "std_f1": round(r.std_f1, 4),
                    "avg_pool_size": round(r.avg_pool_size, 1),
                }
                for r in results
            ],
        }

        return OptimizationResult(
            timestamp=datetime.now(),
            total_draws=len(draws),
            n_periods=n_test_periods,
            pool_sizes_tested=pool_sizes,
            results=results,
            optimal_pool_size=optimal_pool_size,
            summary=summary,
        )

    def _evaluate_pool_size(
        self,
        sorted_draws: list[DrawResult],
        top_n_per_period: int,
        n_test_periods: int,
    ) -> PoolSizeResult:
        """Evaluiert eine einzelne Pool-Size.

        Args:
            sorted_draws: Chronologisch sortierte Ziehungen
            top_n_per_period: Pool-Size zum Testen
            n_test_periods: Anzahl Testperioden

        Returns:
            PoolSizeResult mit aggregierten Metriken
        """
        min_train = self.n_periods * self.draws_per_period
        period_results: list[PoolSizePeriodResult] = []

        # Walk-Forward: Fuer jede Periode
        for i in range(n_test_periods):
            # Training startet bei Index i, Test ist direkt danach
            train_start = i
            train_end = train_start + min_train

            if train_end >= len(sorted_draws):
                break

            train_draws = sorted_draws[train_start:train_end]
            test_draw = sorted_draws[train_end]

            # Generate pool
            generator = NumberPoolGenerator(
                n_periods=self.n_periods,
                draws_per_period=self.draws_per_period,
                top_n_per_period=top_n_per_period,
                top_n_total=20,  # Standard
            )

            try:
                pool = generator.generate(train_draws)
            except ValueError as e:
                logger.warning(f"Period {i + 1}: {e}")
                continue

            # Calculate metrics
            predicted = list(pool)
            actual = set(test_draw.numbers)
            hits = len(set(predicted) & actual)

            precision = hits / len(predicted) if predicted else 0.0
            recall = hits / self.numbers_per_draw if self.numbers_per_draw > 0 else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )

            period_results.append(
                PoolSizePeriodResult(
                    period_id=i + 1,
                    pool_size=len(predicted),
                    predicted_numbers=predicted,
                    hits=hits,
                    precision=precision,
                    recall=recall,
                    f1_score=f1,
                )
            )

        # Aggregate results
        if not period_results:
            return PoolSizeResult(
                top_n_per_period=top_n_per_period,
                period_results=[],
                avg_precision=0.0,
                avg_recall=0.0,
                avg_f1=0.0,
                std_f1=0.0,
                avg_pool_size=0.0,
            )

        precisions = [r.precision for r in period_results]
        recalls = [r.recall for r in period_results]
        f1_scores = [r.f1_score for r in period_results]
        pool_sizes = [r.pool_size for r in period_results]

        return PoolSizeResult(
            top_n_per_period=top_n_per_period,
            period_results=period_results,
            avg_precision=mean(precisions),
            avg_recall=mean(recalls),
            avg_f1=mean(f1_scores),
            std_f1=stdev(f1_scores) if len(f1_scores) > 1 else 0.0,
            avg_pool_size=mean(pool_sizes),
        )


# =============================================================================
# Output Formatting
# =============================================================================


def format_result_json(result: OptimizationResult) -> str:
    """Formatiert OptimizationResult als JSON.

    Args:
        result: OptimizationResult

    Returns:
        JSON-String
    """
    data = {
        "optimization_timestamp": result.timestamp.isoformat(),
        "total_draws": result.total_draws,
        "n_periods": result.n_periods,
        "pool_sizes_tested": result.pool_sizes_tested,
        "optimal_pool_size": result.optimal_pool_size,
        "results": [
            {
                "top_n_per_period": r.top_n_per_period,
                "avg_precision": round(r.avg_precision, 4),
                "avg_recall": round(r.avg_recall, 4),
                "avg_f1": round(r.avg_f1, 4),
                "std_f1": round(r.std_f1, 4),
                "avg_pool_size": round(r.avg_pool_size, 1),
                "n_periods_evaluated": len(r.period_results),
            }
            for r in result.results
        ],
        "summary": result.summary,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_result_table(result: OptimizationResult) -> str:
    """Formatiert OptimizationResult als ASCII-Tabelle.

    Args:
        result: OptimizationResult

    Returns:
        Tabellen-String
    """
    lines = [
        "=" * 70,
        "Pool Size Optimization Results",
        "=" * 70,
        f"Total Draws: {result.total_draws}",
        f"Test Periods: {result.n_periods}",
        "",
        "| top_n | Avg Precision | Avg Recall | Avg F1  | Std F1  | Pool Size |",
        "|-------|---------------|------------|---------|---------|-----------|",
    ]

    for r in result.results:
        marker = " *" if r.top_n_per_period == result.optimal_pool_size else "  "
        lines.append(
            f"|{marker}{r.top_n_per_period:4} |"
            f"      {r.avg_precision:.4f}  |"
            f"   {r.avg_recall:.4f}  |"
            f" {r.avg_f1:.4f} |"
            f" {r.std_f1:.4f} |"
            f"   {r.avg_pool_size:5.1f}   |"
        )

    lines.append("")
    lines.append(f"* Optimal: top_n_per_period = {result.optimal_pool_size}")
    lines.append(f"  Avg F1: {result.summary.get('optimal_avg_f1', 0):.4f}")
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
    "--pool-sizes",
    "-s",
    default="5,11,15,20",
    help="Komma-separierte Liste der Pool-Sizes (default: 5,11,15,20)",
)
@click.option(
    "--periods",
    "-p",
    default=12,
    help="Anzahl der Backtest-Perioden (default: 12)",
    type=int,
)
@click.option(
    "--output",
    "-o",
    help="Pfad zur Ausgabedatei (JSON)",
    type=click.Path(),
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def main(
    config: str,
    data: str,
    pool_sizes: str,
    periods: int,
    output: Optional[str],
    verbose: int,
) -> None:
    """Optimiert Top-Pool Size (top_n_per_period) via Walk-Forward Backtest.

    Testet verschiedene Pool-Sizes und ermittelt die optimale Groesse
    basierend auf durchschnittlichem F1-Score.

    \b
    Metriken:
    - Precision: Wie viele Pool-Zahlen waren im Draw?
    - Recall: Wie viele Draw-Zahlen waren im Pool?
    - F1-Score: Harmonisches Mittel aus Precision und Recall

    \b
    Example:
        python scripts/optimize_pool_size.py -d data/raw/keno/KENO.csv
        python scripts/optimize_pool_size.py -d data/raw/keno/KENO.csv -s "5,10,15,20,25"
        python scripts/optimize_pool_size.py -d data/raw/keno/KENO.csv -o results/pool_opt.json
    """
    setup_logging(verbose)

    # Parse pool sizes
    try:
        sizes = [int(s.strip()) for s in pool_sizes.split(",")]
    except ValueError:
        click.echo(f"Error: Invalid pool-sizes format: {pool_sizes}", err=True)
        sys.exit(1)

    if not sizes:
        click.echo("Error: At least one pool size required", err=True)
        sys.exit(1)

    click.echo(f"Testing pool sizes: {sizes}")

    # Load config
    cfg = load_config(config)
    game_config = cfg.get_active_game()
    numbers_per_draw = game_config.numbers_to_draw

    click.echo(f"Game: {game_config.name}, numbers_per_draw: {numbers_per_draw}")

    # Load data
    loader = DataLoader()
    try:
        draws = loader.load(data)
    except FileNotFoundError:
        click.echo(f"Error: File not found: {data}", err=True)
        sys.exit(1)

    click.echo(f"Loaded {len(draws)} draws from {data}")

    # Run optimization
    optimizer = PoolSizeOptimizer(numbers_per_draw=numbers_per_draw)

    try:
        result = optimizer.optimize(
            draws,
            pool_sizes=sizes,
            n_test_periods=periods,
        )
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Output
    click.echo(format_result_table(result))

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(format_result_json(result), encoding="utf-8")
        click.echo(f"Results written to {output}")

    # Summary
    click.echo(f"\nOptimal top_n_per_period: {result.optimal_pool_size}")
    click.echo(
        f"Recommendation: Update config/default.yaml with "
        f"top_n_per_period: {result.optimal_pool_size}"
    )


if __name__ == "__main__":
    main()
