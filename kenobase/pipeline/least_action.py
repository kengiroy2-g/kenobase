"""Least-Action Pipeline Selector - Model Law B Implementation.

Dieses Modul implementiert die Pipeline-Auswahl nach dem Least-Action-Prinzip
(Gesetz B) gemaess CLAUDE.md Section 6.2 und 4.1.

Das Least-Action-Prinzip bevorzugt einfachere Pipelines bei gleicher Performance,
um Overfitting zu vermeiden.

Usage:
    from kenobase.pipeline.least_action import PipelineSelector, PipelineVariant
    from kenobase.core.config import load_config

    config = load_config("config/default.yaml")
    selector = PipelineSelector(config)

    variants = [
        PipelineVariant(name="simple", features=5, rules=2, special_cases=0),
        PipelineVariant(name="complex", features=15, rules=8, special_cases=3),
    ]

    best_name, best_action = selector.select(variants, performance_data)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from kenobase.physics.model_laws import (
    PipelineConfig as PhysicsPipelineConfig,
    calculate_pipeline_action,
    select_best_pipeline,
)

if TYPE_CHECKING:
    from kenobase.core.config import KenobaseConfig

logger = logging.getLogger(__name__)


@dataclass
class PipelineVariant:
    """Definition einer Pipeline-Variante fuer Least-Action-Vergleich.

    Attributes:
        name: Eindeutiger Name der Variante.
        num_features: Anzahl verwendeter Features.
        num_rules: Anzahl harter Regeln.
        num_special_cases: Anzahl Sonderfaelle/Ausnahmen.
        performance_variance: Varianz der Performance (Instabilitaet).
        roi: Return on Investment (historisch gemessen).
        description: Optionale Beschreibung der Variante.
    """

    name: str
    num_features: int = 10
    num_rules: int = 5
    num_special_cases: int = 0
    performance_variance: float = 0.1
    roi: float = 1.0
    description: str = ""

    def to_physics_config(self) -> PhysicsPipelineConfig:
        """Konvertiert zu PhysicsPipelineConfig fuer model_laws.py."""
        return PhysicsPipelineConfig(
            num_features=self.num_features,
            num_rules=self.num_rules,
            num_special_cases=self.num_special_cases,
            performance_variance=self.performance_variance,
            roi=self.roi,
        )


@dataclass
class SelectionResult:
    """Ergebnis der Pipeline-Auswahl.

    Attributes:
        selected_name: Name der ausgewaehlten Pipeline.
        selected_action: Action-Wert der ausgewaehlten Pipeline.
        all_actions: Dict aller Pipelines mit ihren Action-Werten.
        selection_reason: Begruendung der Auswahl.
    """

    selected_name: str
    selected_action: float
    all_actions: dict[str, float] = field(default_factory=dict)
    selection_reason: str = ""


# Vordefinierte Pipeline-Varianten fuer Kenobase
DEFAULT_PIPELINE_VARIANTS: list[PipelineVariant] = [
    PipelineVariant(
        name="minimal",
        num_features=5,
        num_rules=2,
        num_special_cases=0,
        performance_variance=0.15,
        roi=0.95,
        description="Minimale Pipeline: nur Frequenzanalyse",
    ),
    PipelineVariant(
        name="standard",
        num_features=10,
        num_rules=5,
        num_special_cases=1,
        performance_variance=0.10,
        roi=1.0,
        description="Standard Pipeline: Frequenz + Duos",
    ),
    PipelineVariant(
        name="extended",
        num_features=15,
        num_rules=8,
        num_special_cases=2,
        performance_variance=0.08,
        roi=1.05,
        description="Erweiterte Pipeline: Frequenz + Duos + Trios",
    ),
    PipelineVariant(
        name="full",
        num_features=20,
        num_rules=12,
        num_special_cases=4,
        performance_variance=0.12,
        roi=1.02,
        description="Volle Pipeline: alle Analysen inkl. 111-Prinzip",
    ),
]


class PipelineSelector:
    """Waehlt optimale Pipeline nach Least-Action-Prinzip (Gesetz B).

    Der Selector bewertet Pipeline-Varianten nach der Formel:
        action = complexity + instability - performance

    Wobei:
        - complexity = num_features * 0.1 + num_rules * 0.05 + num_special_cases * 0.2
        - instability = performance_variance
        - performance = roi

    Die Pipeline mit der niedrigsten Action wird ausgewaehlt.

    Example:
        >>> from kenobase.core.config import load_config
        >>> config = load_config("config/default.yaml")
        >>> selector = PipelineSelector(config)
        >>> result = selector.select_from_defaults()
        >>> print(f"Selected: {result.selected_name}")
    """

    def __init__(self, config: KenobaseConfig) -> None:
        """Initialisiert Pipeline Selector.

        Args:
            config: Kenobase-Konfiguration.
        """
        self.config = config
        self._enabled = config.physics.enable_least_action

    @property
    def enabled(self) -> bool:
        """Gibt zurueck ob Least-Action aktiviert ist."""
        return self._enabled

    def select(
        self,
        variants: list[PipelineVariant],
        performance_overrides: Optional[dict[str, float]] = None,
    ) -> SelectionResult:
        """Waehlt die beste Pipeline aus den Varianten.

        Args:
            variants: Liste von Pipeline-Varianten.
            performance_overrides: Optionale ROI-Ueberschreibungen pro Variante.

        Returns:
            SelectionResult mit ausgewaehlter Pipeline.

        Raises:
            ValueError: Wenn keine Varianten uebergeben werden.
        """
        if not variants:
            raise ValueError("At least one pipeline variant required")

        if not self._enabled:
            logger.info("Least-action selection disabled, using first variant")
            first = variants[0]
            action = calculate_pipeline_action(first.to_physics_config())
            return SelectionResult(
                selected_name=first.name,
                selected_action=action,
                all_actions={first.name: action},
                selection_reason="Least-action disabled, default selection",
            )

        # Build list of (name, PhysicsPipelineConfig) tuples
        pipeline_configs: list[tuple[str, PhysicsPipelineConfig]] = []
        all_actions: dict[str, float] = {}

        for variant in variants:
            config = variant.to_physics_config()

            # Apply performance overrides if provided
            if performance_overrides and variant.name in performance_overrides:
                config = PhysicsPipelineConfig(
                    num_features=config.num_features,
                    num_rules=config.num_rules,
                    num_special_cases=config.num_special_cases,
                    performance_variance=config.performance_variance,
                    roi=performance_overrides[variant.name],
                )

            pipeline_configs.append((variant.name, config))
            all_actions[variant.name] = calculate_pipeline_action(config)

        # Use model_laws.select_best_pipeline
        best_name, best_action = select_best_pipeline(pipeline_configs)

        # Build reason
        sorted_actions = sorted(all_actions.items(), key=lambda x: x[1])
        reason_parts = [f"{name}: {action:.3f}" for name, action in sorted_actions]
        reason = f"Lowest action ({best_action:.3f}). Ranking: {', '.join(reason_parts)}"

        logger.info(f"Least-action selected pipeline '{best_name}' with action={best_action:.3f}")

        return SelectionResult(
            selected_name=best_name,
            selected_action=best_action,
            all_actions=all_actions,
            selection_reason=reason,
        )

    def select_from_defaults(
        self,
        performance_overrides: Optional[dict[str, float]] = None,
    ) -> SelectionResult:
        """Waehlt aus den vordefinierten Standard-Varianten.

        Args:
            performance_overrides: Optionale ROI-Ueberschreibungen.

        Returns:
            SelectionResult mit ausgewaehlter Pipeline.
        """
        return self.select(DEFAULT_PIPELINE_VARIANTS, performance_overrides)

    def calculate_action(self, variant: PipelineVariant) -> float:
        """Berechnet Action fuer eine einzelne Variante.

        Args:
            variant: Pipeline-Variante.

        Returns:
            Action-Wert.
        """
        return calculate_pipeline_action(variant.to_physics_config())

    def compare_variants(
        self,
        variants: list[PipelineVariant],
    ) -> list[tuple[str, float, str]]:
        """Vergleicht Varianten und gibt Ranking zurueck.

        Args:
            variants: Liste von Varianten.

        Returns:
            Liste von (name, action, description) sortiert nach action.
        """
        results: list[tuple[str, float, str]] = []

        for variant in variants:
            action = self.calculate_action(variant)
            results.append((variant.name, action, variant.description))

        return sorted(results, key=lambda x: x[1])


def create_variant_from_analysis_config(
    name: str,
    config: KenobaseConfig,
    measured_roi: float = 1.0,
    measured_variance: float = 0.1,
) -> PipelineVariant:
    """Erstellt Variante basierend auf aktueller Config.

    Zaehlt Features und Regeln aus der Konfiguration.

    Args:
        name: Name der Variante.
        config: Kenobase-Konfiguration.
        measured_roi: Gemessener ROI aus Backtest.
        measured_variance: Gemessene Performance-Varianz.

    Returns:
        PipelineVariant mit abgeleiteten Werten.
    """
    # Count features from analysis config
    num_features = len(config.analysis.windows)  # Rolling windows
    if config.analysis.enable_111_principle:
        num_features += 1

    # Count rules
    num_rules = 0
    if config.analysis.duo_min_occurrences > 0:
        num_rules += 1
    if config.analysis.trio_min_occurrences > 0:
        num_rules += 1
    if config.analysis.quatro_min_occurrences > 0:
        num_rules += 1
    if config.analysis.zehnergruppen_max_per_group > 0:
        num_rules += 1

    # Count special cases from physics
    num_special_cases = 0
    if config.physics.enable_avalanche:
        num_special_cases += 1
    if config.physics.anti_avalanche_mode:
        num_special_cases += 1

    return PipelineVariant(
        name=name,
        num_features=num_features,
        num_rules=num_rules,
        num_special_cases=num_special_cases,
        performance_variance=measured_variance,
        roi=measured_roi,
        description=f"Auto-generated from config (game={config.active_game})",
    )


__all__ = [
    "PipelineVariant",
    "SelectionResult",
    "PipelineSelector",
    "DEFAULT_PIPELINE_VARIANTS",
    "create_variant_from_analysis_config",
]
