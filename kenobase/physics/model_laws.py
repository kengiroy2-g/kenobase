"""Model Laws A/B/C Implementation.

Dieses Modul implementiert die drei physik-inspirierten Gesetze
fuer Kenobase V2.0 gemaess CLAUDE.md Section 6.

Gesetz A: Stabilitaetstest - Prueft ob eine Relation stabil ist
Gesetz B: Least-Action - Waehlt optimale Pipeline nach Einfachheit
Gesetz C: Criticality - Berechnet Instabilitaets-Score
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np


def is_law(
    relation: Callable[..., float],
    variations: list[dict[str, Any]],
    threshold: float = 0.9,
) -> tuple[float, bool]:
    """Testet ob eine Relation ein 'Gesetz' ist (ADR-018).

    Eine Relation gilt als Gesetz wenn sie ueber Variationen
    (Zeit, Datenquellen, Parameter) stabil bleibt.

    Args:
        relation: Auswertbare Funktion die einen float zurueckgibt.
        variations: Liste von Parametervarianten (dicts).
        threshold: Mindest-Stabilitaet (default 0.9).

    Returns:
        Tuple aus (stability_score, is_law).
        - stability_score: 0.0-1.0
        - is_law: True wenn score >= threshold

    Example:
        >>> def my_relation(x: float) -> float:
        ...     return x * 2
        >>> variations = [{"x": 1.0}, {"x": 2.0}, {"x": 3.0}]
        >>> score, is_law_result = is_law(my_relation, variations)
    """
    if not variations:
        return 0.0, False

    results = [relation(**var) for var in variations]
    results_array = np.array(results, dtype=float)

    mean_val = np.mean(results_array)
    std_val = np.std(results_array)

    # Avoid division by zero
    if abs(mean_val) < 1e-10:
        stability = 0.0 if std_val > 1e-10 else 1.0
    else:
        stability = 1.0 - (std_val / abs(mean_val))

    # Clamp to [0, 1]
    stability = max(0.0, min(1.0, stability))

    return stability, stability >= threshold


def calculate_stability(
    history: list[float],
    window: int = 4,
) -> tuple[float, bool]:
    """Berechnet die Stabilitaet einer Zahlenreihe (Gesetz A).

    Args:
        history: Liste von historischen Werten.
        window: Fenstergroesse fuer Rolling-Berechnung (nicht verwendet,
                fuer Kompatibilitaet).

    Returns:
        Tuple aus (stability_score, is_law).
        - stability_score: 0.0-1.0
        - is_law: True wenn score >= 0.9
    """
    if not history or len(history) < 2:
        return 0.0, False

    history_array = np.array(history, dtype=float)
    mean_val = np.mean(history_array)
    std_val = np.std(history_array)

    if abs(mean_val) < 1e-10:
        stability = 0.0 if std_val > 1e-10 else 1.0
    else:
        stability = 1.0 - (std_val / abs(mean_val))

    stability = max(0.0, min(1.0, stability))

    return stability, stability >= 0.9


@dataclass
class PipelineConfig:
    """Konfiguration fuer Pipeline-Action-Berechnung (Gesetz B)."""

    num_features: int
    num_rules: int
    num_special_cases: int
    performance_variance: float
    roi: float


def calculate_pipeline_action(config: PipelineConfig) -> float:
    """Berechnet die 'Action' einer Pipeline (ADR-018).

    Niedrigere Action = bessere Pipeline bei gleicher Performance.
    Formel: action = complexity + instability - performance

    Args:
        config: Pipeline-Konfiguration mit Komplexitaets- und
                Performance-Metriken.

    Returns:
        Action-Wert (niedriger ist besser).

    Example:
        >>> config = PipelineConfig(
        ...     num_features=10,
        ...     num_rules=5,
        ...     num_special_cases=2,
        ...     performance_variance=0.1,
        ...     roi=1.5
        ... )
        >>> action = calculate_pipeline_action(config)
    """
    complexity = (
        config.num_features * 0.1
        + config.num_rules * 0.05
        + config.num_special_cases * 0.2
    )
    instability = config.performance_variance
    performance = config.roi

    return complexity + instability - performance


def select_best_pipeline(
    pipeline_configs: list[tuple[str, PipelineConfig]],
) -> tuple[str, float]:
    """Waehlt die beste Pipeline nach Least-Action-Prinzip.

    Args:
        pipeline_configs: Liste von (name, config) Tupeln.

    Returns:
        Tuple aus (best_name, best_action).

    Raises:
        ValueError: Wenn keine Pipelines uebergeben werden.
    """
    if not pipeline_configs:
        raise ValueError("At least one pipeline config required")

    best_name = ""
    best_action = float("inf")

    for name, config in pipeline_configs:
        action = calculate_pipeline_action(config)
        if action < best_action:
            best_action = action
            best_name = name

    return best_name, best_action


def calculate_criticality(
    probability: float,
    regime_complexity: int,
) -> tuple[float, str]:
    """Berechnet Criticality-Score (ADR-018/020).

    Criticality misst wie instabil/riskant eine Vorhersage ist.
    Hohe Sensitivity (nahe 50%) + komplexe Regimes = hohes Risiko.

    Args:
        probability: Vorhersage-Wahrscheinlichkeit (0-1).
        regime_complexity: Anzahl Peaks in historischer Verteilung.

    Returns:
        Tuple aus (criticality_score, warning_level).
        - criticality_score: >= 0
        - warning_level: "LOW", "MEDIUM", "HIGH", "CRITICAL"

    Example:
        >>> score, level = calculate_criticality(0.5, 3)
        >>> level
        'CRITICAL'
    """
    # Sensitivity: maximal bei p=0.5, minimal bei p=0 oder p=1
    sensitivity = 1.0 - abs(probability - 0.5) * 2.0
    sensitivity = max(0.0, min(1.0, sensitivity))

    # Criticality = sensitivity * regime_complexity
    criticality = sensitivity * regime_complexity

    # Determine warning level
    if criticality < 0.3:
        level = "LOW"
    elif criticality < 0.5:
        level = "MEDIUM"
    elif criticality < 0.7:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return criticality, level


def calculate_criticality_from_config(
    probability: float,
    regime_complexity: int,
    warning_threshold: float = 0.7,
    critical_threshold: float = 0.85,
) -> tuple[float, str]:
    """Berechnet Criticality mit konfigurierbaren Schwellenwerten.

    Args:
        probability: Vorhersage-Wahrscheinlichkeit (0-1).
        regime_complexity: Anzahl Peaks in historischer Verteilung.
        warning_threshold: Schwelle fuer HIGH level.
        critical_threshold: Schwelle fuer CRITICAL level.

    Returns:
        Tuple aus (criticality_score, warning_level).
    """
    sensitivity = 1.0 - abs(probability - 0.5) * 2.0
    sensitivity = max(0.0, min(1.0, sensitivity))

    criticality = sensitivity * regime_complexity

    # Normalize to 0-1 range for threshold comparison
    normalized = criticality / max(regime_complexity, 1)

    if normalized >= critical_threshold:
        level = "CRITICAL"
    elif normalized >= warning_threshold:
        level = "HIGH"
    elif normalized >= 0.5:
        level = "MEDIUM"
    else:
        level = "LOW"

    return criticality, level


__all__ = [
    "is_law",
    "calculate_stability",
    "PipelineConfig",
    "calculate_pipeline_action",
    "select_best_pipeline",
    "calculate_criticality",
    "calculate_criticality_from_config",
]
