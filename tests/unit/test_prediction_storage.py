"""Unit Tests fuer PredictionStorage."""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from kenobase.prediction.storage import (
    Prediction,
    PredictionMetrics,
    PredictionStorage,
    generate_draw_id,
)


class TestGenerateDrawId:
    """Tests fuer generate_draw_id."""

    def test_generate_draw_id_default(self):
        """Test: Generiert ID mit heutigem Datum."""
        draw_id = generate_draw_id()
        today = datetime.now().strftime("%Y-%m-%d")
        assert draw_id == f"KENO-{today}"

    def test_generate_draw_id_custom_game(self):
        """Test: Generiert ID fuer anderen Spieltyp."""
        draw_id = generate_draw_id("LOTTO")
        today = datetime.now().strftime("%Y-%m-%d")
        assert draw_id == f"LOTTO-{today}"

    def test_generate_draw_id_custom_date(self):
        """Test: Generiert ID mit spezifischem Datum."""
        date = datetime(2025, 12, 25)
        draw_id = generate_draw_id("KENO", date)
        assert draw_id == "KENO-2025-12-25"


class TestPredictionMetrics:
    """Tests fuer PredictionMetrics."""

    def test_to_dict(self):
        """Test: Serialisierung zu Dict."""
        metrics = PredictionMetrics(
            hits=3,
            hit_rate=0.15,
            precision=0.5,
            tier_accuracy={"A": 0.5, "B": 0.25},
        )
        d = metrics.to_dict()
        assert d["hits"] == 3
        assert d["hit_rate"] == 0.15
        assert d["precision"] == 0.5
        assert d["tier_accuracy"]["A"] == 0.5

    def test_from_dict(self):
        """Test: Deserialisierung von Dict."""
        data = {
            "hits": 2,
            "hit_rate": 0.1,
            "precision": 0.33,
            "tier_accuracy": {"A": 1.0},
        }
        metrics = PredictionMetrics.from_dict(data)
        assert metrics.hits == 2
        assert metrics.hit_rate == 0.1
        assert metrics.tier_accuracy["A"] == 1.0


class TestPrediction:
    """Tests fuer Prediction."""

    def test_to_dict_minimal(self):
        """Test: Serialisierung minimal."""
        pred = Prediction(
            draw_id="KENO-2025-12-28",
            numbers=[1, 5, 17],
        )
        d = pred.to_dict()
        assert d["draw_id"] == "KENO-2025-12-28"
        assert d["numbers"] == [1, 5, 17]
        assert "actuals" not in d  # Nicht gesetzt

    def test_to_dict_full(self):
        """Test: Serialisierung mit allen Feldern."""
        pred = Prediction(
            draw_id="KENO-2025-12-28",
            numbers=[1, 5, 17],
            tier_predictions={"A": [17], "B": [1, 5]},
            actuals=[1, 3, 5, 7, 9],
            metrics=PredictionMetrics(hits=2, hit_rate=0.4),
        )
        d = pred.to_dict()
        assert d["tier_predictions"]["A"] == [17]
        assert d["actuals"] == [1, 3, 5, 7, 9]
        assert d["metrics"]["hits"] == 2

    def test_from_dict(self):
        """Test: Deserialisierung."""
        data = {
            "draw_id": "KENO-2025-12-28",
            "prediction_time": "2025-12-28T12:00:00",
            "numbers": [1, 5, 17],
            "tier_predictions": {"A": [17]},
            "mode": "ensemble",
            "config": {},
            "actuals": [1, 3],
            "metrics": {"hits": 1, "hit_rate": 0.5, "precision": 0.33, "tier_accuracy": {}},
        }
        pred = Prediction.from_dict(data)
        assert pred.draw_id == "KENO-2025-12-28"
        assert pred.numbers == [1, 5, 17]
        assert pred.mode == "ensemble"
        assert pred.metrics.hits == 1


class TestPredictionStorage:
    """Tests fuer PredictionStorage."""

    @pytest.fixture
    def temp_storage(self):
        """Erstellt temporaeren Storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield PredictionStorage(storage_dir=tmpdir)

    def test_save_and_load(self, temp_storage):
        """Test: Speichern und Laden einer Vorhersage."""
        pred = Prediction(
            draw_id="KENO-2025-12-28",
            numbers=[1, 5, 17, 23, 45, 67],
            tier_predictions={"A": [17, 23], "B": [1, 45]},
        )

        path = temp_storage.save_prediction(pred)
        assert path.exists()

        loaded = temp_storage.load_prediction("KENO-2025-12-28")
        assert loaded is not None
        assert loaded.draw_id == "KENO-2025-12-28"
        assert loaded.numbers == [1, 5, 17, 23, 45, 67]

    def test_list_predictions(self, temp_storage):
        """Test: Auflisten aller Vorhersagen."""
        for i in range(3):
            pred = Prediction(
                draw_id=f"KENO-2025-12-{28-i:02d}",
                numbers=[1, 2, 3],
            )
            temp_storage.save_prediction(pred)

        draw_ids = temp_storage.list_predictions()
        assert len(draw_ids) == 3
        assert "KENO-2025-12-28" in draw_ids

    def test_calculate_metrics(self, temp_storage):
        """Test: Metrik-Berechnung."""
        predictions = [1, 5, 17, 23, 45, 67]
        actuals = [5, 17, 22, 28, 35, 41, 45, 48, 52, 55, 58, 61, 64, 67, 68, 69, 70, 11, 19, 3]
        tier_predictions = {"A": [17, 23], "B": [1, 45]}

        metrics = temp_storage.calculate_metrics(
            predictions=predictions,
            actuals=actuals,
            tier_predictions=tier_predictions,
        )

        # Treffer: 5, 17, 45, 67 = 4
        assert metrics.hits == 4
        assert metrics.precision == 4 / 6  # 4 Treffer von 6 Vorhersagen
        assert metrics.hit_rate == 4 / 20  # 4 Treffer von 20 Ist-Zahlen
        assert metrics.tier_accuracy["A"] == 0.5  # 17 trifft, 23 nicht
        assert metrics.tier_accuracy["B"] == 0.5  # 45 trifft, 1 nicht

    def test_compare_and_update(self, temp_storage):
        """Test: Vergleich und Update."""
        pred = Prediction(
            draw_id="KENO-2025-12-28",
            numbers=[1, 5, 17],
            tier_predictions={"A": [17]},
        )
        temp_storage.save_prediction(pred)

        actuals = [5, 17, 22, 28, 35]
        metrics = temp_storage.compare_and_update("KENO-2025-12-28", actuals)

        assert metrics is not None
        assert metrics.hits == 2  # 5, 17

        # Reload and verify update persisted
        loaded = temp_storage.load_prediction("KENO-2025-12-28")
        assert loaded.actuals == actuals
        assert loaded.metrics.hits == 2

    def test_get_aggregate_metrics(self, temp_storage):
        """Test: Aggregierte Metriken."""
        # Speichere zwei ausgewertete Vorhersagen
        for i, (nums, acts, tier_a) in enumerate([
            ([1, 5, 17], [5, 17, 22], [17]),
            ([2, 6, 18], [6, 18, 23], [18]),
        ]):
            pred = Prediction(
                draw_id=f"KENO-2025-12-{28-i:02d}",
                numbers=nums,
                tier_predictions={"A": tier_a},
            )
            temp_storage.save_prediction(pred)
            temp_storage.compare_and_update(pred.draw_id, acts)

        stats = temp_storage.get_aggregate_metrics()
        assert stats["count"] == 2
        assert stats["evaluated"] == 2
        assert stats["total_hits"] == 4  # 2 + 2
        assert stats["avg_hits"] == 2.0

    def test_load_nonexistent(self, temp_storage):
        """Test: Laden nicht-existenter Vorhersage."""
        loaded = temp_storage.load_prediction("NONEXISTENT")
        assert loaded is None
