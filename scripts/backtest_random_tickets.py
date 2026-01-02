#!/usr/bin/env python3
"""Random Ticket Null Model Backtest - Monte-Carlo baseline for ticket strategies.

This script runs a Monte-Carlo simulation with random tickets as the null model
baseline, comparing against the weighted-frequency strategy.

Usage:
    python scripts/backtest_random_tickets.py --seeds 100
    python scripts/backtest_random_tickets.py --seeds 100 --output results/random_ticket_null_model.json
    python scripts/backtest_random_tickets.py --seeds 200 --types 2,6,8,10 --jobs 4

Axiom-First conformant: Random baseline serves as null model for strategy validation.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import click

from kenobase.core.data_loader import DataLoader
from kenobase.prediction.ticket_backtester import (
    save_random_null_model_json,
    walk_forward_backtest_random_tickets,
    walk_forward_backtest_weighted_frequency,
)

logger = logging.getLogger(__name__)

DEFAULT_DATA_PATH = "data/raw/keno/KENO_ab_2022_bereinigt.csv"
DEFAULT_OUTPUT_PATH = "results/random_ticket_null_model.json"
DEFAULT_KENO_TYPES = [2, 6, 8, 10]


def setup_logging(verbose: int) -> None:
    """Configure logging based on verbosity level."""
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
    "--data",
    "-d",
    default=DEFAULT_DATA_PATH,
    help=f"Path to KENO draw data CSV (default: {DEFAULT_DATA_PATH})",
    type=click.Path(),
)
@click.option(
    "--output",
    "-o",
    default=DEFAULT_OUTPUT_PATH,
    help=f"Output JSON path (default: {DEFAULT_OUTPUT_PATH})",
    type=click.Path(),
)
@click.option(
    "--seeds",
    "-s",
    default=100,
    help="Number of Monte-Carlo seeds (default: 100)",
    type=int,
)
@click.option(
    "--types",
    "-t",
    default="2,6,8,10",
    help="Comma-separated keno types (default: 2,6,8,10)",
    type=str,
)
@click.option(
    "--start-index",
    default=365,
    help="Start index for walk-forward (default: 365)",
    type=int,
)
@click.option(
    "--jobs",
    "-j",
    default=-1,
    help="Number of parallel jobs (-1 = all CPUs, default: -1)",
    type=int,
)
@click.option(
    "--compare/--no-compare",
    default=True,
    help="Compare with weighted-frequency strategy (default: True)",
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def main(
    data: str,
    output: str,
    seeds: int,
    types: str,
    start_index: int,
    jobs: int,
    compare: bool,
    verbose: int,
) -> None:
    """Run Monte-Carlo random ticket null model backtest.

    This script generates random tickets for each draw and calculates
    the average hits across multiple seeds. The result serves as a
    baseline (null model) to compare against the weighted-frequency
    strategy.

    \b
    Output includes:
    - mean_hits_random: Average hits for random tickets
    - std_hits_random: Standard deviation across seeds
    - expected_mean_hits: Theoretical hypergeometric expectation
    - mean_hits_weighted_freq: Hits from weighted-frequency (if --compare)
    - random_vs_weighted_diff: Difference (weighted - random)

    \b
    Example:
        python scripts/backtest_random_tickets.py --seeds 100
        python scripts/backtest_random_tickets.py --seeds 200 --types 8,10 --jobs 4
    """
    setup_logging(verbose)

    # Parse keno types
    try:
        keno_types = [int(t.strip()) for t in types.split(",")]
    except ValueError:
        click.echo(f"Error: Invalid keno types format: {types}", err=True)
        sys.exit(1)

    # Validate keno types
    for kt in keno_types:
        if kt < 2 or kt > 10:
            click.echo(f"Error: Invalid keno type {kt}. Must be 2-10.", err=True)
            sys.exit(1)

    click.echo(f"Random Ticket Null Model Backtest")
    click.echo(f"  Seeds: {seeds}")
    click.echo(f"  Keno Types: {keno_types}")
    click.echo(f"  Start Index: {start_index}")
    click.echo(f"  Jobs: {jobs if jobs > 0 else 'all CPUs'}")
    click.echo(f"  Compare with weighted-freq: {compare}")
    click.echo()

    # Load data
    data_path = Path(data)
    if not data_path.exists():
        click.echo(f"Error: Data file not found: {data}", err=True)
        sys.exit(1)

    loader = DataLoader()
    try:
        draws = loader.load(str(data_path))
    except Exception as e:
        click.echo(f"Error loading data: {e}", err=True)
        sys.exit(1)

    click.echo(f"Loaded {len(draws)} draws from {data_path}")

    if start_index >= len(draws):
        click.echo(f"Error: start_index ({start_index}) >= number of draws ({len(draws)})", err=True)
        sys.exit(1)

    # Run weighted-frequency for comparison if requested
    weighted_freq_results = None
    if compare:
        click.echo("Running weighted-frequency backtest for comparison...")
        try:
            weighted_freq_results = walk_forward_backtest_weighted_frequency(
                draws,
                keno_types=keno_types,
                start_index=start_index,
            )
            click.echo(f"  Weighted-freq results: {len(weighted_freq_results)} types")
        except Exception as e:
            click.echo(f"Warning: Failed to run weighted-frequency: {e}", err=True)
            weighted_freq_results = None

    # Run random ticket Monte-Carlo
    click.echo(f"Running Monte-Carlo with {seeds} seeds...")
    try:
        result = walk_forward_backtest_random_tickets(
            draws,
            keno_types=keno_types,
            start_index=start_index,
            n_seeds=seeds,
            weighted_freq_results=weighted_freq_results,
            n_jobs=jobs,
        )
    except Exception as e:
        click.echo(f"Error running Monte-Carlo: {e}", err=True)
        sys.exit(1)

    # Save results
    output_path = Path(output)
    save_random_null_model_json(result, output_path=output_path, draws_path=str(data_path))
    click.echo(f"\nResults saved to: {output_path}")

    # Print summary
    click.echo("\n--- Results Summary ---")
    click.echo(f"{'Type':<6} {'Random':<10} {'Expected':<10} {'WF':<10} {'Diff (WF-Rand)':<15}")
    click.echo("-" * 55)

    for r in result.per_type_results:
        wf_str = f"{r.mean_hits_weighted_freq:.4f}" if r.mean_hits_weighted_freq is not None else "N/A"
        diff_str = f"{r.random_vs_weighted_diff:+.4f}" if r.random_vs_weighted_diff is not None else "N/A"
        click.echo(
            f"Typ-{r.keno_type:<2} {r.mean_hits_random:<10.4f} {r.expected_mean_hits:<10.4f} "
            f"{wf_str:<10} {diff_str:<15}"
        )

    click.echo()
    click.echo(f"Conclusion: {result.conclusion}")

    # Repro command
    click.echo("\n--- Repro Command ---")
    click.echo(f"python scripts/backtest_random_tickets.py --seeds {seeds} --types {types} --output {output}")


if __name__ == "__main__":
    main()
