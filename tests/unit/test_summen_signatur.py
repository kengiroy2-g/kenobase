from __future__ import annotations

import json
from datetime import datetime

from kenobase.analysis.summen_signatur import (
    aggregate_bucket_counts,
    compute_summen_signatur,
    export_signatures,
    split_signatures_by_date,
)
from kenobase.core.config import KenobaseConfig
from kenobase.core.data_loader import DrawResult, GameType
from kenobase.pipeline.runner import PipelineRunner


def _make_draw(date_str: str, start: int) -> DrawResult:
    numbers = list(range(start, start + 20))
    return DrawResult(
        date=datetime.fromisoformat(date_str),
        numbers=numbers,
        bonus=[],
        game_type=GameType.KENO,
        metadata={},
    )


def test_summen_signatur_buckets_and_scaling(tmp_path) -> None:
    draws = [
        _make_draw("2023-12-31", 1),   # very low after scaling
        _make_draw("2024-01-02", 51),  # very high after scaling
    ]

    records = compute_summen_signatur(
        draws=draws,
        keno_types=[6],
        bucket_std_low=0.5,
        bucket_std_high=1.5,
        checksum_algorithm="sha256",
    )

    assert len(records) == 2
    assert records[0].sum_bucket == "very_low"
    assert records[1].sum_bucket == "very_high"

    for rec in records:
        assert rec.parity_vector["even"] + rec.parity_vector["odd"] == rec.keno_type
        assert sum(rec.decade_hist.values()) == rec.keno_type

    # Deterministic checksum
    repeat = compute_summen_signatur(
        draws=draws,
        keno_types=[6],
        bucket_std_low=0.5,
        bucket_std_high=1.5,
        checksum_algorithm="sha256",
    )
    assert repeat[0].checksum == records[0].checksum

    # Split by date
    train, test = split_signatures_by_date(records, datetime(2024, 1, 1))
    assert [r.draw_date.year for r in train] == [2023]
    assert [r.draw_date.year for r in test] == [2024]

    # Export and aggregate buckets
    export_path = tmp_path / "train_signaturen.json"
    export_signatures(train, export_path, {"source": "unit-test"})
    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["record_count"] == len(train)
    assert payload["metadata"]["source"] == "unit-test"

    bucket_counts = aggregate_bucket_counts(records)
    assert bucket_counts[6]["very_low"] == 1
    assert bucket_counts[6]["very_high"] == 1


def test_pipeline_runner_skips_summen_signatur_when_disabled() -> None:
    config = KenobaseConfig()
    config.analysis.summen_signatur.enabled = False

    runner = PipelineRunner(config)
    draws = [
        _make_draw("2024-01-05", 1),
        _make_draw("2024-01-06", 11),
    ]

    result = runner.run(draws)

    assert result.summen_signatur_buckets is None
    assert result.summen_signatur_path is None
