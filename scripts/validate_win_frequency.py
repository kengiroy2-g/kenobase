#!/usr/bin/env python3
"""Validate A3 Axiom: 'Ein Gewinn treibt alles' (small wins keep players engaged).

This script validates that any reasonable ticket achieves at least one win per month
at the lowest GK tier (>=2 matches), supporting the A3 axiom that the system must
maintain player engagement through regular small wins.

Usage:
    python scripts/validate_win_frequency.py
    python scripts/validate_win_frequency.py --output results/win_frequency_validation.json
    python scripts/validate_win_frequency.py --types 2,6,8,10 --verbose

Axiom-First conformant:
- Validates A3 (Spiel muss attraktiv bleiben)
- Tests against random ticket baseline
- Per-ticket-type granularity
- Acceptance: >95% months with at least one win
"""

from __future__ import annotations

import json
import logging
import random
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import click
import pandas as pd

from kenobase.core.data_loader import DataLoader, DrawResult

logger = logging.getLogger(__name__)

DEFAULT_DATA_PATH = "data/raw/keno/KENO_ab_2022_bereinigt.csv"
DEFAULT_OUTPUT_PATH = "results/win_frequency_validation.json"
DEFAULT_KENO_TYPES = [2, 6, 8, 10]
ACCEPTANCE_THRESHOLD = 0.95  # >95% months must have wins


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


def count_matches(ticket: list[int], drawn: set[int]) -> int:
    """Count how many ticket numbers were drawn."""
    return len(set(ticket) & drawn)


def get_month_key(date: pd.Timestamp) -> str:
    """Extract YYYY-MM from date for monthly grouping."""
    return date.strftime("%Y-%m")


def analyze_ticket_win_frequency(
    draws: list[DrawResult],
    ticket: list[int],
    keno_type: int,
    min_matches: int = 2,
) -> dict[str, Any]:
    """Analyze win frequency for a single ticket.

    Args:
        draws: List of DrawResult objects
        ticket: List of ticket numbers
        keno_type: Keno type (2, 6, 8, 10)
        min_matches: Minimum matches to count as a win (default: 2)

    Returns:
        Dictionary with win frequency metrics per month
    """
    monthly_wins: dict[str, int] = defaultdict(int)
    monthly_draws: dict[str, int] = defaultdict(int)

    for draw in draws:
        date = draw.date
        drawn = set(draw.numbers)
        month_key = date.strftime("%Y-%m")

        monthly_draws[month_key] += 1
        matches = count_matches(ticket, drawn)
        if matches >= min_matches:
            monthly_wins[month_key] += 1

    # Calculate metrics
    total_months = len(monthly_draws)
    months_with_win = sum(1 for m in monthly_draws if monthly_wins[m] > 0)
    win_frequency = months_with_win / total_months if total_months > 0 else 0.0

    return {
        "keno_type": keno_type,
        "ticket": ticket,
        "total_months": total_months,
        "months_with_win": months_with_win,
        "win_frequency": win_frequency,
        "passes_threshold": win_frequency >= ACCEPTANCE_THRESHOLD,
        "monthly_details": {
            month: {"draws": monthly_draws[month], "wins": monthly_wins[month]}
            for month in sorted(monthly_draws.keys())
        },
    }


def generate_random_ticket(keno_type: int, seed: int | None = None) -> list[int]:
    """Generate a random ticket for given keno type."""
    if seed is not None:
        random.seed(seed)
    return sorted(random.sample(range(1, 71), keno_type))


def run_validation(
    data_path: str,
    keno_types: list[int],
    n_random_seeds: int = 100,
) -> dict[str, Any]:
    """Run full A3 axiom validation.

    Args:
        data_path: Path to KENO draw data
        keno_types: List of keno types to validate
        n_random_seeds: Number of random tickets to test per type

    Returns:
        Complete validation results dictionary
    """
    # Load data
    loader = DataLoader()
    draws = loader.load(data_path)
    n_draws = len(draws)

    logger.info(f"Loaded {n_draws} draws from {data_path}")

    # Get date range
    min_date = draws[0].date
    max_date = draws[-1].date

    results: dict[str, Any] = {
        "analysis": "a3_axiom_win_frequency_validation",
        "generated_at": datetime.now().isoformat(),
        "data_source": data_path,
        "n_draws": n_draws,
        "date_range": {"start": str(min_date.date()), "end": str(max_date.date())},
        "acceptance_threshold": ACCEPTANCE_THRESHOLD,
        "per_type_results": [],
        "random_baseline": [],
    }

    # Define structured tickets (from SYSTEM_STATUS.json)
    structured_tickets = {
        2: [9, 50],
        6: [3, 24, 40, 49, 51, 64],
        8: [2, 3, 20, 24, 36, 49, 51, 64],
        10: [2, 3, 9, 24, 33, 36, 49, 50, 51, 64],
    }

    # Validate structured tickets
    for keno_type in keno_types:
        if keno_type not in structured_tickets:
            logger.warning(f"No structured ticket defined for Typ-{keno_type}")
            continue

        ticket = structured_tickets[keno_type]
        result = analyze_ticket_win_frequency(draws, ticket, keno_type)
        results["per_type_results"].append(result)

        logger.info(
            f"Typ-{keno_type}: {result['months_with_win']}/{result['total_months']} "
            f"months with win ({result['win_frequency']:.1%})"
        )

    # Random baseline comparison
    logger.info(f"Running random baseline with {n_random_seeds} seeds...")
    for keno_type in keno_types:
        random_win_freqs = []
        for seed in range(n_random_seeds):
            random_ticket = generate_random_ticket(keno_type, seed=seed)
            random_result = analyze_ticket_win_frequency(
                draws, random_ticket, keno_type
            )
            random_win_freqs.append(random_result["win_frequency"])

        mean_freq = sum(random_win_freqs) / len(random_win_freqs)
        min_freq = min(random_win_freqs)
        max_freq = max(random_win_freqs)
        passes_count = sum(1 for f in random_win_freqs if f >= ACCEPTANCE_THRESHOLD)

        results["random_baseline"].append(
            {
                "keno_type": keno_type,
                "n_seeds": n_random_seeds,
                "mean_win_frequency": mean_freq,
                "min_win_frequency": min_freq,
                "max_win_frequency": max_freq,
                "passes_threshold_count": passes_count,
                "passes_threshold_pct": passes_count / n_random_seeds,
            }
        )

        logger.info(
            f"Typ-{keno_type} random baseline: mean={mean_freq:.1%}, "
            f"range=[{min_freq:.1%}, {max_freq:.1%}], "
            f"passes={passes_count}/{n_random_seeds}"
        )

    # Overall conclusion
    all_pass = all(r["passes_threshold"] for r in results["per_type_results"])
    results["conclusion"] = {
        "a3_axiom_validated": all_pass,
        "summary": (
            "A3 CONFIRMED: All ticket types achieve >95% months with wins"
            if all_pass
            else "A3 PARTIAL: Some ticket types below threshold"
        ),
    }

    return results


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
    "--types",
    "-t",
    default="2,6,8,10",
    help="Comma-separated keno types (default: 2,6,8,10)",
    type=str,
)
@click.option(
    "--seeds",
    "-s",
    default=100,
    help="Number of random seeds for baseline (default: 100)",
    type=int,
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (-v for INFO, -vv for DEBUG)",
)
def main(
    data: str,
    output: str,
    types: str,
    seeds: int,
    verbose: int,
) -> None:
    """Validate A3 Axiom: Small wins keep players engaged."""
    setup_logging(verbose)

    keno_types = [int(t.strip()) for t in types.split(",")]

    logger.info(f"Validating A3 axiom for types: {keno_types}")

    results = run_validation(
        data_path=data,
        keno_types=keno_types,
        n_random_seeds=seeds,
    )

    # Save results
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("A3 AXIOM VALIDATION: 'Ein Gewinn treibt alles'")
    print("=" * 60)

    for r in results["per_type_results"]:
        status = "PASS" if r["passes_threshold"] else "FAIL"
        print(
            f"Typ-{r['keno_type']}: {r['months_with_win']}/{r['total_months']} "
            f"months with win ({r['win_frequency']:.1%}) [{status}]"
        )

    print("-" * 60)
    print(f"Conclusion: {results['conclusion']['summary']}")
    print("=" * 60)

    # Exit code based on validation
    sys.exit(0 if results["conclusion"]["a3_axiom_validated"] else 1)


if __name__ == "__main__":
    main()
