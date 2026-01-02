"""Summen-Signatur Analyse (TRANS-001).

Berechnet pro Ziehung und KENO-Typ (Pick-Count) eine deterministische
Summen-Signatur mit:
- sum_total: Summe aller gezogenen Zahlen (20 Zahlen)
- sum_scaled: Auf KENO-Typ projizierte Summe (Mean-Skaling)
- sum_bucket: Typ-spezifische Bucket-Einordnung anhand Erwartung/Std
- parity_vector: Gerade/Ungerade Erwartungswerte fuer den KENO-Typ
- decade_hist: Erwartete Zehnergruppen-Verteilung fuer den KENO-Typ
- checksum: SHA-Hash ueber Kernfelder fuer Reproduzierbarkeit

Train/Test-Split gemaess ADR: train < 2024-01-01, test >= 2024-01-01.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from kenobase.analysis.decade_affinity import DECADES
from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)

# Konstanten
DEFAULT_NUMBER_RANGE = (1, 70)
SUMMEN_SIGNATUR_VERSION = "1.0"


def _mean_for_type(keno_type: int, number_range: tuple[int, int]) -> float:
    """Erwarteter Mittelwert fuer Summe einer KENO-Typ Auswahl."""
    min_num, max_num = number_range
    avg_number = (min_num + max_num) / 2
    return avg_number * keno_type


def _std_for_type(keno_type: int, population_size: int = 70) -> float:
    """Standardabweichung der Summe bei Ziehung ohne Zuruecklegen."""
    if keno_type <= 0 or population_size <= 1:
        return 0.0
    single_var = (population_size**2 - 1) / 12  # Varianz uniforme 1..N
    correction = (population_size - keno_type) / (population_size - 1)
    return math.sqrt(keno_type * single_var * correction)


def _scale_distribution(counts: Sequence[int], target_total: int) -> list[int]:
    """Skaliert eine Verteilung deterministisch auf target_total Elemente."""
    total = sum(counts)
    if target_total <= 0 or total <= 0:
        return [0 for _ in counts]

    scaled = [int((c / total) * target_total) for c in counts]
    remainder = target_total - sum(scaled)

    if remainder:
        fractions = [
            (((c / total) * target_total) - base, idx) for idx, (c, base) in enumerate(zip(counts, scaled))
        ]
        fractions.sort(key=lambda x: (-x[0], x[1]))
        for _, idx in fractions[:remainder]:
            scaled[idx] += 1

    return scaled


def _decade_counts(numbers: Sequence[int]) -> list[int]:
    """Zaehlt Zahlen pro Dekade."""
    counts = [0 for _ in range(len(DECADES))]
    for n in numbers:
        for idx, rng in DECADES.items():
            if n in rng:
                counts[idx] += 1
                break
    return counts


def _bucket_label(
    value: float,
    mean: float,
    std: float,
    low_mult: float,
    high_mult: float,
) -> str:
    """Mappt Wert auf typisierte Buckets."""
    if std <= 0:
        return "unknown"

    low_bound = mean - low_mult * std
    high_bound = mean + low_mult * std
    very_low_bound = mean - high_mult * std
    very_high_bound = mean + high_mult * std

    if value <= very_low_bound:
        return "very_low"
    if value <= low_bound:
        return "low"
    if value >= very_high_bound:
        return "very_high"
    if value >= high_bound:
        return "high"
    return "mid"


def _checksum(payload: dict, algorithm: str = "sha256") -> str:
    """Berechnet deterministischen Hash ueber Payload."""
    algo = algorithm if algorithm in hashlib.algorithms_available else "sha256"
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    h = hashlib.new(algo)
    h.update(serialized.encode("utf-8"))
    return h.hexdigest()


def _decade_label(decade_idx: int) -> str:
    """Gibt string label fuer Dekade zurueck, z.B. '01-10'."""
    rng = DECADES.get(decade_idx)
    if not rng:
        return f"decade_{decade_idx}"
    return f"{min(rng):02d}-{max(rng):02d}"


@dataclass
class SummenSignaturRecord:
    """Summen-Signatur fuer eine Ziehung und einen KENO-Typ."""

    draw_date: datetime
    draw_index: int
    keno_type: int
    sum_total: int
    sum_scaled: float
    sum_bucket: str
    parity_vector: dict[str, int]
    decade_hist: dict[str, int]
    checksum: str
    source: str = ""
    version: str = SUMMEN_SIGNATUR_VERSION
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialisiert Record fuer JSON-Export."""
        return {
            "draw_date": self.draw_date.isoformat(),
            "draw_index": self.draw_index,
            "keno_type": self.keno_type,
            "sum_total": self.sum_total,
            "sum_scaled": round(self.sum_scaled, 3),
            "sum_bucket": self.sum_bucket,
            "parity_vector": self.parity_vector,
            "decade_hist": self.decade_hist,
            "checksum": self.checksum,
            "source": self.source,
            "version": self.version,
            "metadata": self.metadata,
        }


def compute_summen_signatur(
    draws: Sequence[DrawResult],
    keno_types: Iterable[int],
    bucket_std_low: float = 0.5,
    bucket_std_high: float = 1.5,
    checksum_algorithm: str = "sha256",
    number_range: tuple[int, int] = DEFAULT_NUMBER_RANGE,
    source: str = "",
) -> list[SummenSignaturRecord]:
    """Berechnet Summen-Signaturen fuer alle Ziehungen/KENO-Typen."""
    if not draws:
        return []

    sorted_draws = sorted(draws, key=lambda d: d.date)
    keno_types_unique = sorted({int(k) for k in keno_types if 2 <= int(k) <= 10})
    if not keno_types_unique:
        logger.warning("No valid keno_types provided; skipping computation")
        return []

    numbers_per_draw = len(sorted_draws[0].numbers) if sorted_draws[0].numbers else 0
    records: list[SummenSignaturRecord] = []

    for draw_idx, draw in enumerate(sorted_draws):
        if not draw.numbers:
            logger.warning("Skipping draw without numbers at index %s", draw_idx)
            continue

        sum_total = sum(draw.numbers)
        even_count = sum(1 for n in draw.numbers if n % 2 == 0)
        odd_count = len(draw.numbers) - even_count
        decade_counts = _decade_counts(draw.numbers)

        for keno_type in keno_types_unique:
            scaled_sum = (sum_total / numbers_per_draw) * keno_type if numbers_per_draw else float(sum_total)
            mean_expected = _mean_for_type(keno_type, number_range)
            std_expected = _std_for_type(keno_type, population_size=number_range[1])

            parity_scaled = _scale_distribution([even_count, odd_count], keno_type)
            decade_scaled = _scale_distribution(decade_counts, keno_type)

            decade_hist = {
                _decade_label(idx): count for idx, count in enumerate(decade_scaled)
            }

            payload = {
                "date": draw.date.isoformat(),
                "draw_index": draw_idx,
                "keno_type": keno_type,
                "sum_total": sum_total,
                "sum_scaled": round(scaled_sum, 6),
                "sum_bucket": _bucket_label(
                    scaled_sum,
                    mean_expected,
                    std_expected,
                    bucket_std_low,
                    bucket_std_high,
                ),
                "parity_vector": {"even": parity_scaled[0], "odd": parity_scaled[1]},
                "decade_hist": decade_hist,
            }

            record = SummenSignaturRecord(
                draw_date=draw.date,
                draw_index=draw_idx,
                keno_type=keno_type,
                sum_total=sum_total,
                sum_scaled=scaled_sum,
                sum_bucket=payload["sum_bucket"],
                parity_vector=payload["parity_vector"],
                decade_hist=decade_hist,
                checksum=_checksum(payload, checksum_algorithm),
                source=source,
            )
            records.append(record)

    return records


def split_signatures_by_date(
    records: Sequence[SummenSignaturRecord],
    split_date: datetime,
) -> tuple[list[SummenSignaturRecord], list[SummenSignaturRecord]]:
    """Teilt Signaturen in Train/Test anhand split_date."""
    train = [r for r in records if r.draw_date < split_date]
    test = [r for r in records if r.draw_date >= split_date]
    return train, test


def export_signatures(
    records: Sequence[SummenSignaturRecord],
    output_path: str | Path,
    metadata: dict | None = None,
) -> None:
    """Exportiert Signaturen als JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "metadata": metadata or {},
        "records": [r.to_dict() for r in records],
    }

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote %s summen_signatur records to %s", len(records), path)


def aggregate_bucket_counts(
    records: Sequence[SummenSignaturRecord],
) -> dict[int, dict[str, int]]:
    """Aggregiert Bucket-Haeufigkeiten pro KENO-Typ."""
    aggregated: dict[int, dict[str, int]] = {}
    for rec in records:
        type_buckets = aggregated.setdefault(rec.keno_type, {})
        type_buckets[rec.sum_bucket] = type_buckets.get(rec.sum_bucket, 0) + 1
    return aggregated


__all__ = [
    "SummenSignaturRecord",
    "compute_summen_signatur",
    "split_signatures_by_date",
    "export_signatures",
    "aggregate_bucket_counts",
]
