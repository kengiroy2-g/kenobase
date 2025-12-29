#!/usr/bin/env python3
"""Zehnergruppen-Regel Validierung - A/B-Test und Grid-Search.

Dieses Script validiert die Zehnergruppen-Regel (max_per_decade Filter):
1. A/B-Test: Vergleich mit/ohne Zehnergruppen-Filter
2. Grid-Search: Optimierung von max_per_decade (1-5)
3. Signifikanztest: Paired t-test fuer F1-Score Unterschiede

Usage:
    python scripts/validate_zehnergruppen.py --data data/raw/keno/KENO_ab_2018.csv
    python scripts/validate_zehnergruppen.py --data data/raw/keno/KENO_ab_2018.csv -o results/zehnergruppen_validation.json

Gemaess TASK-M02: Zehnergruppen-Regel Validierung.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev
from typing import Optional

import click

# Import scipy for statistical tests
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from kenobase.analysis.frequency import get_hot_numbers
from kenobase.core.config import load_config
from kenobase.core.data_loader import DataLoader, DrawResult
from kenobase.pipeline.validation_metrics import (
    calculate_metrics_dict as calculate_metrics,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class VariantResult:
    """Ergebnis einer einzelnen Variante (max_per_decade Einstellung).

    Attributes:
        variant_name: Name der Variante (z.B. "no_filter" oder "max_2")
        max_per_decade: Wert (None = kein Filter)
        f1_scores: F1-Scores pro Backtest-Periode
        avg_f1: Durchschnittlicher F1-Score
        std_f1: Standardabweichung F1-Score
        avg_precision: Durchschnittliche Precision
        avg_recall: Durchschnittlicher Recall
        n_combinations_avg: Durchschnittliche Anzahl Kombinationen pro Periode
    """

    variant_name: str
    max_per_decade: Optional[int]
    f1_scores: list[float]
    avg_f1: float
    std_f1: float
    avg_precision: float
    avg_recall: float
    n_combinations_avg: float


@dataclass
class ValidationResult:
    """Gesamt-Ergebnis der Zehnergruppen-Validierung.

    Attributes:
        timestamp: Zeitpunkt der Ausfuehrung
        data_file: Pfad zur Datendatei
        n_draws: Anzahl Ziehungen
        n_periods: Anzahl Backtest-Perioden
        variants: Ergebnisse pro Variante
        ab_test: A/B-Test Ergebnis (filter vs no_filter)
        grid_search: Grid-Search Ergebnis (beste max_per_decade)
    """

    timestamp: datetime
    data_file: str
    n_draws: int
    n_periods: int
    variants: list[VariantResult]
    ab_test: dict
    grid_search: dict


# =============================================================================
# Core Logic
# =============================================================================


def run_backtest_for_variant(
    draws: list[DrawResult],
    max_per_decade: Optional[int],
    n_periods: int = 12,
    train_ratio: float = 0.8,
    hot_threshold: float = 0.37,
    cold_threshold: float = 0.20,
    numbers_range: tuple[int, int] = (1, 70),
    numbers_per_draw: int = 20,
) -> VariantResult:
    """Fuehrt Backtest fuer eine max_per_decade Variante durch.

    Args:
        draws: Liste der Ziehungen
        max_per_decade: Max Zahlen pro Dekade (None = kein Filter)
        n_periods: Anzahl Backtest-Perioden
        train_ratio: Train/Test Split
        hot_threshold: Schwelle fuer Hot-Numbers
        cold_threshold: Schwelle fuer Cold-Numbers
        numbers_range: Zahlenbereich des Spiels
        numbers_per_draw: Anzahl gezogener Zahlen

    Returns:
        VariantResult mit F1-Scores und Statistiken
    """
    sorted_draws = sorted(draws, key=lambda d: d.date)
    period_size = len(sorted_draws) // n_periods
    train_size = int(period_size * train_ratio)

    f1_scores = []
    precisions = []
    recalls = []
    combinations_counts = []

    for i in range(n_periods):
        start_idx = i * period_size
        train_end_idx = start_idx + train_size
        test_end_idx = start_idx + period_size

        train_draws = sorted_draws[start_idx:train_end_idx]
        test_draws = sorted_draws[train_end_idx:test_end_idx]

        if not train_draws or not test_draws:
            continue

        # Get hot numbers from training period
        predicted_hot = get_hot_numbers(
            train_draws,
            hot_threshold=hot_threshold,
            cold_threshold=cold_threshold,
            number_range=numbers_range,
        )

        # Apply decade filter if max_per_decade is set
        if max_per_decade is not None:
            filtered_combos = filter_by_decade(predicted_hot, max_per_decade)
            # Count valid combinations (for reporting)
            combinations_counts.append(len(filtered_combos))
        else:
            filtered_combos = predicted_hot
            combinations_counts.append(len(predicted_hot))

        # Calculate metrics on test period
        metrics = calculate_metrics(
            filtered_combos,
            test_draws,
            numbers_per_draw=numbers_per_draw,
        )

        f1_scores.append(metrics["f1_score"])
        precisions.append(metrics["precision"])
        recalls.append(metrics["recall"])

    variant_name = f"max_{max_per_decade}" if max_per_decade else "no_filter"

    return VariantResult(
        variant_name=variant_name,
        max_per_decade=max_per_decade,
        f1_scores=f1_scores,
        avg_f1=mean(f1_scores) if f1_scores else 0.0,
        std_f1=stdev(f1_scores) if len(f1_scores) > 1 else 0.0,
        avg_precision=mean(precisions) if precisions else 0.0,
        avg_recall=mean(recalls) if recalls else 0.0,
        n_combinations_avg=mean(combinations_counts) if combinations_counts else 0.0,
    )


def filter_by_decade(numbers: list[int], max_per_decade: int) -> list[int]:
    """Filtert Zahlen nach Dekaden-Regel.

    Die Regel: Max max_per_decade Zahlen pro Dekade.
    Dekaden: 1-10=0, 11-20=1, 21-30=2, etc.
    Formel: decade = (number - 1) // 10

    Args:
        numbers: Liste der Zahlen
        max_per_decade: Max Zahlen pro Dekade

    Returns:
        Gefilterte Liste (erste max_per_decade Zahlen pro Dekade)
    """
    decade_counts: dict[int, int] = {}
    result = []

    for num in sorted(numbers):
        decade = (num - 1) // 10
        current_count = decade_counts.get(decade, 0)
        if current_count < max_per_decade:
            result.append(num)
            decade_counts[decade] = current_count + 1

    return result


def run_ab_test(
    baseline: VariantResult,
    treatment: VariantResult,
) -> dict:
    """Fuehrt A/B-Test durch (paired t-test auf F1-Scores).

    Args:
        baseline: Baseline-Variante (ohne Filter)
        treatment: Treatment-Variante (mit Filter)

    Returns:
        Dict mit:
        - delta_f1: Durchschnittliche F1-Differenz
        - p_value: p-Wert des t-tests
        - significant: True wenn p < 0.05
        - recommendation: Empfehlung basierend auf Ergebnis
    """
    if not SCIPY_AVAILABLE:
        return {
            "delta_f1": treatment.avg_f1 - baseline.avg_f1,
            "p_value": None,
            "significant": None,
            "recommendation": "scipy nicht installiert - keine Signifikanzpruefung moeglich",
            "error": "scipy not available",
        }

    if len(baseline.f1_scores) != len(treatment.f1_scores):
        return {
            "delta_f1": treatment.avg_f1 - baseline.avg_f1,
            "p_value": None,
            "significant": None,
            "recommendation": "Ungleiche Periodenanzahl - kein paired t-test moeglich",
            "error": "unequal period counts",
        }

    if len(baseline.f1_scores) < 2:
        return {
            "delta_f1": treatment.avg_f1 - baseline.avg_f1,
            "p_value": None,
            "significant": None,
            "recommendation": "Zu wenige Perioden - kein t-test moeglich",
            "error": "insufficient periods",
        }

    # Paired t-test
    t_stat, p_value = stats.ttest_rel(treatment.f1_scores, baseline.f1_scores)

    delta_f1 = treatment.avg_f1 - baseline.avg_f1
    significant = p_value < 0.05

    if significant:
        if delta_f1 > 0:
            recommendation = f"Filter VERBESSERT F1 signifikant (delta={delta_f1:.4f}, p={p_value:.4f})"
        else:
            recommendation = f"Filter VERSCHLECHTERT F1 signifikant (delta={delta_f1:.4f}, p={p_value:.4f})"
    else:
        recommendation = f"Kein signifikanter Unterschied (delta={delta_f1:.4f}, p={p_value:.4f})"

    return {
        "delta_f1": delta_f1,
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": significant,
        "recommendation": recommendation,
    }


def run_grid_search(variants: list[VariantResult]) -> dict:
    """Findet beste max_per_decade Einstellung via Grid-Search.

    Args:
        variants: Liste aller Varianten (inkl. no_filter)

    Returns:
        Dict mit:
        - best_variant: Name der besten Variante
        - best_max_per_decade: Beste Einstellung
        - best_avg_f1: Bester F1-Score
        - ranking: Sortierte Liste aller Varianten
    """
    # Filter nur Varianten mit Filter (keine no_filter)
    filtered_variants = [v for v in variants if v.max_per_decade is not None]

    if not filtered_variants:
        return {
            "best_variant": None,
            "best_max_per_decade": None,
            "best_avg_f1": None,
            "ranking": [],
            "error": "No filtered variants available",
        }

    # Sortiere nach avg_f1 (absteigend)
    sorted_variants = sorted(filtered_variants, key=lambda v: v.avg_f1, reverse=True)
    best = sorted_variants[0]

    ranking = [
        {
            "variant": v.variant_name,
            "max_per_decade": v.max_per_decade,
            "avg_f1": round(v.avg_f1, 4),
            "std_f1": round(v.std_f1, 4),
        }
        for v in sorted_variants
    ]

    return {
        "best_variant": best.variant_name,
        "best_max_per_decade": best.max_per_decade,
        "best_avg_f1": best.avg_f1,
        "ranking": ranking,
    }


# =============================================================================
# Output Formatting
# =============================================================================


def _safe_value(value):
    """Konvertiert Wert zu JSON-kompatiblem Typ."""
    import math
    if value is None:
        return None
    # Handle numpy types
    if hasattr(value, 'item'):  # numpy scalar
        value = value.item()
    # Handle float nan/inf
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    # Round floats
    if isinstance(value, float):
        return round(value, 4)
    return value


def _safe_float(value: float) -> Optional[float]:
    """Konvertiert float zu JSON-kompatiblem Wert (None fuer nan/inf)."""
    return _safe_value(value)


def format_result_json(result: ValidationResult) -> str:
    """Formatiert ValidationResult als JSON.

    Args:
        result: ValidationResult

    Returns:
        JSON-String
    """
    data = {
        "validation_timestamp": result.timestamp.isoformat(),
        "data_file": result.data_file,
        "n_draws": result.n_draws,
        "n_periods": result.n_periods,
        "variants": [
            {
                "variant_name": v.variant_name,
                "max_per_decade": v.max_per_decade,
                "avg_f1": _safe_float(v.avg_f1),
                "std_f1": _safe_float(v.std_f1),
                "avg_precision": _safe_float(v.avg_precision),
                "avg_recall": _safe_float(v.avg_recall),
                "n_combinations_avg": round(v.n_combinations_avg, 2) if v.n_combinations_avg else 0.0,
                "f1_scores": [_safe_float(f) for f in v.f1_scores],
            }
            for v in result.variants
        ],
        "ab_test": {
            k: _safe_value(v) for k, v in result.ab_test.items()
        },
        "grid_search": {
            k: _safe_value(v) if not isinstance(v, list) else v
            for k, v in result.grid_search.items()
        },
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


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
    "--output",
    "-o",
    help="Pfad zur Ausgabedatei (JSON)",
    type=click.Path(),
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def main(
    config: str,
    data: str,
    periods: int,
    output: Optional[str],
    verbose: int,
) -> None:
    """Validiert die Zehnergruppen-Regel via A/B-Test und Grid-Search.

    Fuehrt Walk-Forward Backtest mit verschiedenen max_per_decade Werten durch:
    - no_filter: Keine Zehnergruppen-Filterung
    - max_1: Max 1 Zahl pro Dekade
    - max_2: Max 2 Zahlen pro Dekade
    - max_3: Max 3 Zahlen pro Dekade (default)
    - max_4: Max 4 Zahlen pro Dekade
    - max_5: Max 5 Zahlen pro Dekade

    A/B-Test: Vergleicht default (max_3) mit no_filter.
    Grid-Search: Findet beste max_per_decade Einstellung.

    \b
    Example:
        python scripts/validate_zehnergruppen.py -d data/raw/keno/KENO_ab_2018.csv
        python scripts/validate_zehnergruppen.py -d data/raw/keno/KENO_ab_2018.csv -o results/zehnergruppen.json
    """
    setup_logging(verbose)

    # Load config
    cfg = load_config(config)
    game_config = cfg.get_active_game()

    click.echo(f"Config: {config} (active_game: {cfg.active_game})")

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

    # Game parameters
    hot_threshold = game_config.get_hot_threshold()
    cold_threshold = game_config.get_cold_threshold()
    numbers_range = game_config.numbers_range
    numbers_per_draw = game_config.numbers_to_draw

    click.echo(f"Game: {game_config.name}")
    click.echo(f"Hot threshold: {hot_threshold}, Cold threshold: {cold_threshold}")

    # Run variants
    click.echo("\n--- Running Variants ---")
    variants: list[VariantResult] = []

    # Variant 0: No filter (baseline)
    click.echo("Running: no_filter...")
    baseline = run_backtest_for_variant(
        draws=draws,
        max_per_decade=None,
        n_periods=periods,
        hot_threshold=hot_threshold,
        cold_threshold=cold_threshold,
        numbers_range=numbers_range,
        numbers_per_draw=numbers_per_draw,
    )
    variants.append(baseline)
    click.echo(f"  no_filter: F1={baseline.avg_f1:.4f} +/- {baseline.std_f1:.4f}")

    # Variants 1-5: max_per_decade = 1, 2, 3, 4, 5
    for max_val in range(1, 6):
        click.echo(f"Running: max_{max_val}...")
        variant = run_backtest_for_variant(
            draws=draws,
            max_per_decade=max_val,
            n_periods=periods,
            hot_threshold=hot_threshold,
            cold_threshold=cold_threshold,
            numbers_range=numbers_range,
            numbers_per_draw=numbers_per_draw,
        )
        variants.append(variant)
        click.echo(f"  max_{max_val}: F1={variant.avg_f1:.4f} +/- {variant.std_f1:.4f}")

    # A/B Test: default (max_3) vs no_filter
    click.echo("\n--- A/B Test (max_3 vs no_filter) ---")
    default_variant = next((v for v in variants if v.max_per_decade == 3), None)
    if default_variant:
        ab_test_result = run_ab_test(baseline, default_variant)
    else:
        ab_test_result = {"error": "max_3 variant not found"}

    click.echo(f"Delta F1: {ab_test_result.get('delta_f1', 'N/A')}")
    click.echo(f"p-value: {ab_test_result.get('p_value', 'N/A')}")
    click.echo(f"Recommendation: {ab_test_result.get('recommendation', 'N/A')}")

    # Grid Search
    click.echo("\n--- Grid Search ---")
    grid_search_result = run_grid_search(variants)
    click.echo(f"Best variant: {grid_search_result.get('best_variant', 'N/A')}")
    click.echo(f"Best avg F1: {grid_search_result.get('best_avg_f1', 'N/A')}")

    if grid_search_result.get("ranking"):
        click.echo("\nRanking:")
        for rank in grid_search_result["ranking"]:
            click.echo(
                f"  {rank['variant']}: F1={rank['avg_f1']:.4f} +/- {rank['std_f1']:.4f}"
            )

    # Create result
    result = ValidationResult(
        timestamp=datetime.now(),
        data_file=str(data),
        n_draws=len(draws),
        n_periods=periods,
        variants=variants,
        ab_test=ab_test_result,
        grid_search=grid_search_result,
    )

    # Output
    formatted = format_result_json(result)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted, encoding="utf-8")
        click.echo(f"\nResults written to {output}")
    else:
        click.echo("\n--- Full JSON Result ---")
        click.echo(formatted)


if __name__ == "__main__":
    main()
