#!/usr/bin/env python
"""CLI: Berechnet Summen-Signatur Artefakte (Train/Test Split)."""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

# Add project root for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kenobase.analysis.summen_signatur import (  # noqa: E402
    aggregate_bucket_counts,
    compute_summen_signatur,
    export_signatures,
    split_signatures_by_date,
)
from kenobase.core.config import KenobaseConfig, load_config  # noqa: E402
from kenobase.core.data_loader import DataLoader  # noqa: E402


def setup_logging(verbosity: int) -> None:
    """Konfiguriert Logging-Level."""
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


def _parse_keno_types(raw: Optional[str], cfg: KenobaseConfig) -> list[int]:
    """Parst Keno-Typen aus CLI oder Config."""
    if raw:
        parsed = [int(x.strip()) for x in raw.split(",") if x.strip()]
    else:
        parsed = cfg.analysis.summen_signatur.keno_types
    return sorted({k for k in parsed if 2 <= k <= 10})


def _resolve_paths(
    cfg: KenobaseConfig,
    output_dir: Optional[str],
    train_output: Optional[str],
    test_output: Optional[str],
) -> tuple[Path, Path]:
    """Bestimmt Artefaktpfade."""
    base_dir = Path(output_dir) if output_dir else None

    if base_dir:
        base_dir.mkdir(parents=True, exist_ok=True)
        train_path = base_dir / "summen_signatur_train.json"
        test_path = base_dir / "summen_signatur_test.json"
    else:
        train_path = Path(train_output) if train_output else Path(cfg.analysis.summen_signatur.train_output)
        test_path = Path(test_output) if test_output else Path(cfg.analysis.summen_signatur.test_output)

    train_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)
    return train_path, test_path


@click.command()
@click.option(
    "--config",
    "-c",
    default="config/default.yaml",
    help="Pfad zur Konfigurationsdatei.",
    type=click.Path(exists=False),
)
@click.option(
    "--data",
    "-d",
    required=True,
    help="Pfad zur KENO CSV-Datei.",
    type=click.Path(exists=True),
)
@click.option(
    "--keno-types",
    "-k",
    default=None,
    help="Kommagetrennte KENO-Typen (2-10). Default aus config.",
)
@click.option(
    "--split-date",
    default=None,
    help="Train/Test Split (YYYY-MM-DD). Default aus config.",
)
@click.option(
    "--train-output",
    default=None,
    help="Pfad fuer Train-Artefakt (ueberschreibt config).",
    type=click.Path(),
)
@click.option(
    "--test-output",
    default=None,
    help="Pfad fuer Test-Artefakt (ueberschreibt config).",
    type=click.Path(),
)
@click.option(
    "--output-dir",
    default=None,
    help="Basisverzeichnis fuer Artefakte (setzt train/test Pfade).",
    type=click.Path(),
)
@click.option("-v", "--verbose", count=True, help="Verbosity (-v INFO, -vv DEBUG)")
def main(
    config: str,
    data: str,
    keno_types: Optional[str],
    split_date: Optional[str],
    train_output: Optional[str],
    test_output: Optional[str],
    output_dir: Optional[str],
    verbose: int,
) -> None:
    """Berechnet Summen-Signaturen und exportiert Train/Test JSON."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    cfg = load_config(config)
    logger.info("Loaded config from %s", config)

    split_str = split_date or cfg.analysis.summen_signatur.split_date
    try:
        split_dt = datetime.fromisoformat(split_str)
    except ValueError as exc:
        raise click.BadParameter(f"Invalid split-date: {split_str}") from exc

    keno_types_list = _parse_keno_types(keno_types, cfg)
    if not keno_types_list:
        raise click.BadParameter("No valid keno types provided (expected 2..10)")

    train_path, test_path = _resolve_paths(cfg, output_dir, train_output, test_output)

    data_path = Path(data)
    loader = DataLoader()
    draws = loader.load(data_path)
    if not draws:
        raise click.ClickException(f"No draws found in {data_path}")

    logger.info("Loaded %s draws from %s", len(draws), data_path)

    records = compute_summen_signatur(
        draws=draws,
        keno_types=keno_types_list,
        bucket_std_low=cfg.analysis.summen_signatur.bucket_std_low,
        bucket_std_high=cfg.analysis.summen_signatur.bucket_std_high,
        checksum_algorithm=cfg.analysis.summen_signatur.checksum_algorithm,
        number_range=cfg.get_active_game().numbers_range,
        source=str(data_path),
    )

    train_records, test_records = split_signatures_by_date(records, split_dt)

    metadata = {
        "source": str(data_path),
        "keno_types": keno_types_list,
        "split_date": split_dt.isoformat(),
        "numbers_per_draw": len(draws[0].numbers) if draws and draws[0].numbers else 0,
        "checksum_algorithm": cfg.analysis.summen_signatur.checksum_algorithm,
    }

    export_signatures(train_records, train_path, metadata | {"split": "train"})
    export_signatures(test_records, test_path, metadata | {"split": "test"})

    bucket_summary = {
        "train": aggregate_bucket_counts(train_records),
        "test": aggregate_bucket_counts(test_records),
    }

    logger.info(
        "Summen-Signatur train=%s test=%s (split %s)",
        len(train_records),
        len(test_records),
        split_dt.date(),
    )
    click.echo(
        f"Train -> {train_path} ({len(train_records)} records)\n"
        f"Test  -> {test_path} ({len(test_records)} records)\n"
        f"Buckets: {bucket_summary}"
    )


if __name__ == "__main__":
    main()
