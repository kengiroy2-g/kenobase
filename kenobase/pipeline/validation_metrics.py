"""Validation Metrics - Precision, Recall, F1-Score Berechnung.

Dieses Modul extrahiert die Validierungs-Metriken aus backtest.py
fuer Wiederverwendbarkeit (z.B. Report-Generator P5-03).

Semantik (gemaess ARCHITECT Handoff):
- Precision = hits / total_predictions
  Wie oft war eine Vorhersage richtig?
- Recall = hits / total_actual
  Wie viele der tatsaechlichen Zahlen wurden vorhergesagt?
- F1 = 2 * P * R / (P + R)
  Harmonisches Mittel aus Precision und Recall

Gemaess CLAUDE.md Phase 5: Validation & Backtest.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult


@dataclass
class ValidationMetrics:
    """Container fuer Validierungs-Metriken.

    Attributes:
        hits: Anzahl Treffer (predicted in actual)
        total_predictions: Gesamtzahl Vorhersagen (len(predicted) * n_draws)
        total_actual: Gesamtzahl tatsaechliche Zahlen (numbers_per_draw * n_draws)
        precision: hits / total_predictions
        recall: hits / total_actual
        f1_score: 2 * P * R / (P + R)
    """

    hits: int
    total_predictions: int
    total_actual: int
    precision: float
    recall: float
    f1_score: float

    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary.

        Returns:
            Dict mit allen Metriken
        """
        return {
            "hits": self.hits,
            "total_predictions": self.total_predictions,
            "total_actual": self.total_actual,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
        }


def calculate_hits(
    predicted: list[int],
    draws: list[DrawResult],
) -> int:
    """Zaehlt wie oft predicted in draws erscheinen.

    Args:
        predicted: Liste der vorhergesagten Zahlen
        draws: Liste der Ziehungen

    Returns:
        Anzahl Treffer (Summe ueber alle Ziehungen)

    Example:
        >>> from kenobase.core.data_loader import DrawResult
        >>> from datetime import datetime
        >>> draws = [
        ...     DrawResult(id=1, date=datetime.now(), numbers=[1, 2, 3, 4, 5]),
        ...     DrawResult(id=2, date=datetime.now(), numbers=[2, 3, 4, 5, 6]),
        ... ]
        >>> calculate_hits([1, 2, 3], draws)
        5
    """
    hits = 0
    predicted_set = set(predicted)
    for draw in draws:
        hits += len(predicted_set.intersection(draw.numbers))
    return hits


def calculate_precision(
    hits: int,
    total_predictions: int,
) -> float:
    """Berechnet Precision.

    Precision = hits / total_predictions
    Wie oft war eine Vorhersage richtig?

    Args:
        hits: Anzahl Treffer
        total_predictions: Gesamtzahl Vorhersagen

    Returns:
        Precision (0.0 - 1.0)
    """
    return hits / total_predictions if total_predictions > 0 else 0.0


def calculate_recall(
    hits: int,
    total_actual: int,
) -> float:
    """Berechnet Recall.

    Recall = hits / total_actual
    Wie viele der tatsaechlichen Zahlen wurden vorhergesagt?

    Args:
        hits: Anzahl Treffer
        total_actual: Gesamtzahl tatsaechliche Zahlen

    Returns:
        Recall (0.0 - 1.0)
    """
    return hits / total_actual if total_actual > 0 else 0.0


def calculate_f1(
    precision: float,
    recall: float,
) -> float:
    """Berechnet F1-Score.

    F1 = 2 * P * R / (P + R)
    Harmonisches Mittel aus Precision und Recall

    Args:
        precision: Precision-Wert
        recall: Recall-Wert

    Returns:
        F1-Score (0.0 - 1.0)
    """
    if precision + recall > 0:
        return 2 * precision * recall / (precision + recall)
    return 0.0


def calculate_metrics(
    predicted: list[int],
    draws: list[DrawResult],
    numbers_per_draw: int = 20,
) -> ValidationMetrics:
    """Berechnet alle Validierungs-Metriken.

    Args:
        predicted: Liste der vorhergesagten Zahlen
        draws: Liste der Ziehungen zur Validierung
        numbers_per_draw: Zahlen pro Ziehung (default 20 fuer KENO)

    Returns:
        ValidationMetrics mit allen berechneten Metriken

    Example:
        >>> from kenobase.core.data_loader import DrawResult
        >>> from datetime import datetime
        >>> draws = [
        ...     DrawResult(id=1, date=datetime.now(), numbers=list(range(1, 21))),
        ...     DrawResult(id=2, date=datetime.now(), numbers=list(range(5, 25))),
        ... ]
        >>> metrics = calculate_metrics([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], draws, 20)
        >>> metrics.precision > 0
        True
    """
    hits = calculate_hits(predicted, draws)

    total_predictions = len(predicted) * len(draws)
    total_actual = numbers_per_draw * len(draws)

    precision = calculate_precision(hits, total_predictions)
    recall = calculate_recall(hits, total_actual)
    f1_score = calculate_f1(precision, recall)

    return ValidationMetrics(
        hits=hits,
        total_predictions=total_predictions,
        total_actual=total_actual,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
    )


def calculate_metrics_dict(
    predicted: list[int],
    draws: list[DrawResult],
    numbers_per_draw: int = 20,
) -> dict:
    """Berechnet Metriken und gibt Dict zurueck.

    Convenience-Wrapper um calculate_metrics() fuer direkte
    Dict-Rueckgabe. Kompatibilitaet mit altem backtest.py Interface.

    Args:
        predicted: Liste der vorhergesagten Zahlen
        draws: Liste der Ziehungen
        numbers_per_draw: Zahlen pro Ziehung (default 20)

    Returns:
        Dict mit hits, total_predictions, precision, recall, f1_score
    """
    metrics = calculate_metrics(predicted, draws, numbers_per_draw)
    return {
        "hits": metrics.hits,
        "total_predictions": metrics.total_predictions,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "f1_score": metrics.f1_score,
    }
