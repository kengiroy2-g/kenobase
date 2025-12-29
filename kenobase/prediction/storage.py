"""Prediction Storage - Speichert und vergleicht Vorhersagen mit Ist-Ergebnissen.

Dieses Modul ermoeglicht:
- Persistierung von Vorhersagen in results/predictions/
- Vergleich mit tatsaechlichen Ziehungen
- Berechnung von Metriken (hit_rate, precision, tier_accuracy)
- Historische Tracking-Daten

Storage Format (JSON):
{
    "draw_id": "KENO-2025-12-28",
    "prediction_time": "2025-12-28T12:00:00",
    "predictions": [1, 5, 17, 23, 45, 67],
    "tier_predictions": {"A": [17, 23], "B": [1, 45], "C": [5, 67]},
    "actuals": [3, 5, 17, ...],  # Nach Ziehung
    "metrics": {
        "hits": 2,
        "hit_rate": 0.333,
        "tier_accuracy": {"A": 0.5, "B": 0.0, "C": 0.5}
    }
}

Usage:
    from kenobase.prediction.storage import PredictionStorage, Prediction

    storage = PredictionStorage()
    pred = Prediction(
        draw_id="KENO-2025-12-28",
        numbers=[1, 5, 17, 23, 45, 67],
        tier_predictions={"A": [17, 23], "B": [1, 45], "C": [5, 67]},
    )
    storage.save_prediction(pred)

    # Nach Ziehung
    actuals = [3, 5, 17, 22, 28, ...]
    metrics = storage.compare_and_update(pred.draw_id, actuals)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class PredictionMetrics:
    """Metriken fuer eine einzelne Vorhersage."""

    hits: int = 0
    hit_rate: float = 0.0
    precision: float = 0.0  # hits / len(predictions)
    tier_accuracy: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Konvertiert zu Dict fuer JSON-Serialisierung."""
        return {
            "hits": self.hits,
            "hit_rate": round(self.hit_rate, 4),
            "precision": round(self.precision, 4),
            "tier_accuracy": {
                k: round(v, 4) for k, v in self.tier_accuracy.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PredictionMetrics":
        """Erstellt PredictionMetrics aus Dict."""
        return cls(
            hits=data.get("hits", 0),
            hit_rate=data.get("hit_rate", 0.0),
            precision=data.get("precision", 0.0),
            tier_accuracy=data.get("tier_accuracy", {}),
        )


@dataclass
class Prediction:
    """Repraesentation einer Vorhersage."""

    draw_id: str  # Format: KENO-YYYY-MM-DD oder KENO-YYYY-MM-DD-N
    numbers: list[int]
    prediction_time: datetime = field(default_factory=datetime.now)
    tier_predictions: dict[str, list[int]] = field(default_factory=dict)
    mode: str = "rule_based"  # rule_based, ensemble
    config: dict = field(default_factory=dict)
    actuals: list[int] = field(default_factory=list)
    metrics: Optional[PredictionMetrics] = None

    def to_dict(self) -> dict:
        """Konvertiert zu Dict fuer JSON-Serialisierung."""
        result = {
            "draw_id": self.draw_id,
            "prediction_time": self.prediction_time.isoformat(),
            "numbers": self.numbers,
            "tier_predictions": self.tier_predictions,
            "mode": self.mode,
            "config": self.config,
        }
        if self.actuals:
            result["actuals"] = self.actuals
        if self.metrics:
            result["metrics"] = self.metrics.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Prediction":
        """Erstellt Prediction aus Dict."""
        pred = cls(
            draw_id=data["draw_id"],
            numbers=data["numbers"],
            prediction_time=datetime.fromisoformat(data["prediction_time"]),
            tier_predictions=data.get("tier_predictions", {}),
            mode=data.get("mode", "rule_based"),
            config=data.get("config", {}),
            actuals=data.get("actuals", []),
        )
        if "metrics" in data:
            pred.metrics = PredictionMetrics.from_dict(data["metrics"])
        return pred


def generate_draw_id(game_type: str = "KENO", date: Optional[datetime] = None) -> str:
    """Generiert eine eindeutige draw_id.

    Format: {GAME_TYPE}-{YYYY}-{MM}-{DD}
    Bei mehreren Ziehungen am Tag: {GAME_TYPE}-{YYYY}-{MM}-{DD}-{N}

    Args:
        game_type: Spieltyp (KENO, LOTTO, EUROJACKPOT)
        date: Datum der Ziehung (default: heute)

    Returns:
        Eindeutige draw_id
    """
    if date is None:
        date = datetime.now()
    return f"{game_type.upper()}-{date.strftime('%Y-%m-%d')}"


class PredictionStorage:
    """Speichert und verwaltet Vorhersagen."""

    def __init__(
        self,
        storage_dir: str = "results/predictions",
        create_dir: bool = True,
    ):
        """Initialisiert den PredictionStorage.

        Args:
            storage_dir: Pfad zum Speicherverzeichnis
            create_dir: Erstellt Verzeichnis wenn nicht vorhanden
        """
        self.storage_dir = Path(storage_dir)
        if create_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_prediction_path(self, draw_id: str) -> Path:
        """Gibt den Dateipfad fuer eine Vorhersage zurueck."""
        safe_id = draw_id.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe_id}.json"

    def save_prediction(self, prediction: Prediction) -> Path:
        """Speichert eine Vorhersage.

        Args:
            prediction: Vorhersage zum Speichern

        Returns:
            Pfad zur gespeicherten Datei
        """
        path = self._get_prediction_path(prediction.draw_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(prediction.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Prediction saved: {path}")
        return path

    def load_prediction(self, draw_id: str) -> Optional[Prediction]:
        """Laedt eine Vorhersage.

        Args:
            draw_id: ID der Ziehung

        Returns:
            Prediction oder None wenn nicht gefunden
        """
        path = self._get_prediction_path(draw_id)
        if not path.exists():
            logger.warning(f"Prediction not found: {path}")
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Prediction.from_dict(data)

    def list_predictions(self, pattern: str = "*.json") -> list[str]:
        """Listet alle gespeicherten Vorhersagen.

        Args:
            pattern: Glob-Pattern fuer Dateien

        Returns:
            Liste von draw_ids
        """
        draw_ids = []
        for path in self.storage_dir.glob(pattern):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    draw_ids.append(data["draw_id"])
            except (json.JSONDecodeError, KeyError):
                continue
        return sorted(draw_ids)

    def calculate_metrics(
        self,
        predictions: list[int],
        actuals: list[int],
        tier_predictions: Optional[dict[str, list[int]]] = None,
    ) -> PredictionMetrics:
        """Berechnet Metriken fuer eine Vorhersage.

        Args:
            predictions: Vorhergesagte Zahlen
            actuals: Tatsaechliche Zahlen
            tier_predictions: Optional: Zahlen pro Tier

        Returns:
            PredictionMetrics mit berechneten Werten
        """
        actuals_set = set(actuals)
        predictions_set = set(predictions)

        hits = len(predictions_set & actuals_set)
        hit_rate = hits / len(actuals_set) if actuals_set else 0.0
        precision = hits / len(predictions_set) if predictions_set else 0.0

        tier_accuracy = {}
        if tier_predictions:
            for tier, tier_nums in tier_predictions.items():
                tier_set = set(tier_nums)
                tier_hits = len(tier_set & actuals_set)
                tier_accuracy[tier] = tier_hits / len(tier_set) if tier_set else 0.0

        return PredictionMetrics(
            hits=hits,
            hit_rate=hit_rate,
            precision=precision,
            tier_accuracy=tier_accuracy,
        )

    def compare_and_update(
        self,
        draw_id: str,
        actuals: list[int],
    ) -> Optional[PredictionMetrics]:
        """Vergleicht Vorhersage mit Ist-Ergebnis und aktualisiert.

        Args:
            draw_id: ID der Ziehung
            actuals: Tatsaechliche Zahlen

        Returns:
            Berechnete Metriken oder None wenn Vorhersage nicht gefunden
        """
        prediction = self.load_prediction(draw_id)
        if not prediction:
            logger.error(f"Prediction not found for draw_id: {draw_id}")
            return None

        # Berechne Metriken
        metrics = self.calculate_metrics(
            predictions=prediction.numbers,
            actuals=actuals,
            tier_predictions=prediction.tier_predictions,
        )

        # Update prediction
        prediction.actuals = actuals
        prediction.metrics = metrics

        # Speichern
        self.save_prediction(prediction)
        logger.info(f"Updated prediction {draw_id} with {metrics.hits} hits")

        return metrics

    def get_aggregate_metrics(
        self,
        only_evaluated: bool = True,
    ) -> dict:
        """Berechnet aggregierte Metriken ueber alle Vorhersagen.

        Args:
            only_evaluated: Nur Vorhersagen mit Ist-Ergebnissen

        Returns:
            Dict mit aggregierten Metriken
        """
        predictions = []
        for draw_id in self.list_predictions():
            pred = self.load_prediction(draw_id)
            if pred and (not only_evaluated or pred.metrics):
                predictions.append(pred)

        if not predictions:
            return {"count": 0, "message": "No evaluated predictions found"}

        total_hits = 0
        total_predictions = 0
        total_actuals = 0
        tier_hits: dict[str, int] = {}
        tier_counts: dict[str, int] = {}

        for pred in predictions:
            if pred.metrics:
                total_hits += pred.metrics.hits
                total_predictions += len(pred.numbers)
                total_actuals += len(pred.actuals)

                for tier, accuracy in pred.metrics.tier_accuracy.items():
                    tier_nums = pred.tier_predictions.get(tier, [])
                    tier_hit_count = int(accuracy * len(tier_nums))
                    tier_hits[tier] = tier_hits.get(tier, 0) + tier_hit_count
                    tier_counts[tier] = tier_counts.get(tier, 0) + len(tier_nums)

        return {
            "count": len(predictions),
            "evaluated": len([p for p in predictions if p.metrics]),
            "total_hits": total_hits,
            "avg_hits": round(total_hits / len(predictions), 2) if predictions else 0,
            "avg_precision": round(
                total_hits / total_predictions, 4
            ) if total_predictions else 0,
            "avg_hit_rate": round(
                total_hits / total_actuals, 4
            ) if total_actuals else 0,
            "tier_precision": {
                tier: round(tier_hits.get(tier, 0) / tier_counts.get(tier, 1), 4)
                for tier in tier_counts
            },
        }


__all__ = [
    "Prediction",
    "PredictionMetrics",
    "PredictionStorage",
    "generate_draw_id",
]
