"""Pipeline Runner - Main Analysis Pipeline with Physics Integration.

Dieses Modul implementiert die Haupt-Pipeline fuer Kenobase V2.0.
Integriert Physics Layer (Model Laws A/B/C, Avalanche) gemaess CLAUDE.md Section 4.2.

Usage:
    from kenobase.pipeline.runner import (
        PipelineRunner,
        PipelineResult,
        PhysicsResult,
    )
    from kenobase.core.config import load_config

    config = load_config("config/default.yaml")
    runner = PipelineRunner(config)
    result = runner.run(draws)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from kenobase.analysis.frequency import (
    FrequencyResult,
    PairFrequencyResult,
    calculate_frequency,
    calculate_pair_frequency,
    classify_numbers,
    classify_pairs,
)
from kenobase.analysis.pattern import (
    PatternResult,
    aggregate_patterns,
    extract_patterns,
    extract_patterns_from_draws,
)
from kenobase.physics.avalanche import (
    AvalancheResult,
    AvalancheState,
    analyze_combination,
    max_picks_for_theta,
)
from kenobase.physics.metrics import (
    calculate_hurst_exponent,
    calculate_stability_score,
    count_regime_peaks,
)
from kenobase.physics.model_laws import (
    calculate_criticality,
    calculate_criticality_from_config,
    calculate_stability,
    is_law,
)
from kenobase.pipeline.least_action import (
    DEFAULT_PIPELINE_VARIANTS,
    PipelineSelector,
    SelectionResult,
    create_variant_from_analysis_config,
)

if TYPE_CHECKING:
    from kenobase.core.config import KenobaseConfig
    from kenobase.core.data_loader import DrawResult

logger = logging.getLogger(__name__)


@dataclass
class PhysicsResult:
    """Ergebnis der Physics-Layer-Analyse.

    Attributes:
        stability_score: Stabilitaets-Score (Gesetz A) [0-1]
        is_stable_law: True wenn stability >= threshold
        criticality_score: Criticality-Score (Gesetz C)
        criticality_level: "LOW", "MEDIUM", "HIGH", "CRITICAL"
        avalanche_result: Avalanche-Analyse Ergebnis
        hurst_exponent: Hurst-Exponent der Frequenz-Zeitreihe
        regime_complexity: Anzahl erkannter Regime-Peaks
        recommended_max_picks: Empfohlene max Picks (Anti-Avalanche)
    """

    stability_score: float
    is_stable_law: bool
    criticality_score: float
    criticality_level: str
    avalanche_result: Optional[AvalancheResult]
    hurst_exponent: float
    regime_complexity: int
    recommended_max_picks: int


@dataclass
class PipelineResult:
    """Ergebnis der vollstaendigen Pipeline-Ausfuehrung.

    Attributes:
        timestamp: Zeitpunkt der Ausfuehrung
        draws_count: Anzahl analysierter Ziehungen
        frequency_results: Einzelzahlen-Frequenzen
        pair_frequency_results: Paar-Frequenzen (Duos)
        pattern_results: Muster-Ergebnisse (wenn combination angegeben)
        aggregated_patterns: Aggregierte Muster-Haeufigkeiten
        physics_result: Physics-Layer Ergebnisse
        warnings: Liste von Warnungen waehrend der Ausfuehrung
        config_snapshot: Verwendete Konfiguration (als Dict)
    """

    timestamp: datetime
    draws_count: int
    frequency_results: list[FrequencyResult]
    pair_frequency_results: list[PairFrequencyResult]
    pattern_results: list[PatternResult] = field(default_factory=list)
    aggregated_patterns: dict = field(default_factory=dict)
    physics_result: Optional[PhysicsResult] = None
    pipeline_selection: Optional[SelectionResult] = None
    warnings: list[str] = field(default_factory=list)
    config_snapshot: dict = field(default_factory=dict)


class PipelineRunner:
    """Haupt-Pipeline Runner mit Physics-Integration.

    Fuehrt die vollstaendige Analyse-Pipeline aus:
    1. Frequenzanalyse (Einzel + Paare)
    2. Pattern-Extraktion (optional, bei Kombination)
    3. Physics Layer (Stability, Criticality, Avalanche)
    4. Aggregation und Reporting

    Example:
        >>> from kenobase.core.config import load_config
        >>> from kenobase.core.data_loader import DataLoader
        >>>
        >>> config = load_config("config/default.yaml")
        >>> loader = DataLoader()
        >>> draws = loader.load("data/raw/keno/KENO_ab_2018.csv")
        >>>
        >>> runner = PipelineRunner(config)
        >>> result = runner.run(draws)
        >>> print(f"Analyzed {result.draws_count} draws")
    """

    def __init__(self, config: KenobaseConfig) -> None:
        """Initialisiert Pipeline Runner.

        Args:
            config: Kenobase-Konfiguration.
        """
        self.config = config
        self._pipeline_selector = PipelineSelector(config)
        self._validate_config()

    def _validate_config(self) -> None:
        """Validiert die Konfiguration."""
        if self.config.physics.criticality_critical_threshold <= self.config.physics.criticality_warning_threshold:
            logger.warning(
                "criticality_critical_threshold should be > criticality_warning_threshold"
            )

    def run(
        self,
        draws: list[DrawResult],
        combination: Optional[list[int]] = None,
        precision_estimate: float = 0.7,
    ) -> PipelineResult:
        """Fuehrt die vollstaendige Analyse-Pipeline aus.

        Args:
            draws: Liste von DrawResult-Objekten.
            combination: Optionale Spielkombination fuer Pattern-Analyse.
            precision_estimate: Geschaetzte Einzelzahl-Precision fuer Avalanche.

        Returns:
            PipelineResult mit allen Analyse-Ergebnissen.
        """
        logger.info(f"Starting pipeline with {len(draws)} draws")
        timestamp = datetime.now()
        warnings: list[str] = []

        if not draws:
            warnings.append("No draws provided")
            return PipelineResult(
                timestamp=timestamp,
                draws_count=0,
                frequency_results=[],
                pair_frequency_results=[],
                warnings=warnings,
                config_snapshot=self._get_config_snapshot(),
            )

        # Step 1: Frequenzanalyse
        logger.debug("Step 1: Frequency analysis")
        game_config = self.config.get_active_game()
        number_range = game_config.numbers_range

        frequency_results = calculate_frequency(draws, number_range)
        frequency_results = classify_numbers(
            frequency_results,
            hot_threshold=self.config.analysis.max_frequency_threshold,
            cold_threshold=self.config.analysis.min_frequency_threshold,
        )

        pair_frequency_results = calculate_pair_frequency(draws)
        pair_frequency_results = classify_pairs(pair_frequency_results)

        # Step 2: Pattern-Analyse (optional)
        logger.debug("Step 2: Pattern analysis")
        pattern_results: list[PatternResult] = []
        aggregated_patterns: dict = {}

        if combination:
            pattern_results = extract_patterns_from_draws(combination, draws)
            aggregated_patterns = aggregate_patterns(pattern_results)

        # Step 3: Physics Layer
        logger.debug("Step 3: Physics layer")
        physics_result = None

        if self.config.physics.enable_model_laws:
            physics_result = self._run_physics_layer(
                draws=draws,
                frequency_results=frequency_results,
                combination=combination,
                precision_estimate=precision_estimate,
            )

            # Add warnings based on physics results
            if physics_result.criticality_level == "CRITICAL":
                warnings.append(
                    f"CRITICAL criticality level ({physics_result.criticality_score:.2f})"
                )

            if physics_result.avalanche_result:
                if physics_result.avalanche_result.state == AvalancheState.CRITICAL:
                    warnings.append(
                        f"CRITICAL avalanche state (theta={physics_result.avalanche_result.theta:.2f})"
                    )

            if not physics_result.is_stable_law:
                warnings.append(
                    f"Pattern not stable (stability={physics_result.stability_score:.2f})"
                )

        # Step 4: Least-Action Pipeline Selection (Model Law B)
        pipeline_selection: Optional[SelectionResult] = None

        if self.config.physics.enable_least_action:
            logger.debug("Step 4: Least-action pipeline selection")
            pipeline_selection = self._run_least_action_selection()

        logger.info(f"Pipeline completed with {len(warnings)} warnings")

        return PipelineResult(
            timestamp=timestamp,
            draws_count=len(draws),
            frequency_results=frequency_results,
            pair_frequency_results=pair_frequency_results,
            pattern_results=pattern_results,
            aggregated_patterns=aggregated_patterns,
            physics_result=physics_result,
            pipeline_selection=pipeline_selection,
            warnings=warnings,
            config_snapshot=self._get_config_snapshot(),
        )

    def _run_physics_layer(
        self,
        draws: list[DrawResult],
        frequency_results: list[FrequencyResult],
        combination: Optional[list[int]],
        precision_estimate: float,
    ) -> PhysicsResult:
        """Fuehrt die Physics-Layer-Analyse aus.

        Args:
            draws: Liste von Ziehungen.
            frequency_results: Frequenz-Ergebnisse.
            combination: Optionale Spielkombination.
            precision_estimate: Geschaetzte Precision.

        Returns:
            PhysicsResult mit allen Physics-Metriken.
        """
        # Gesetz A: Stabilitaetstest
        # Teste ob Frequenzen ueber Zeit stabil sind
        freq_history = [r.relative_frequency for r in frequency_results]
        stability_score, is_stable = calculate_stability(
            freq_history,
            window=len(freq_history) // 4 if len(freq_history) >= 4 else 1,
        )

        # Threshold aus Config
        is_stable_law = stability_score >= self.config.physics.stability_threshold

        # Hurst-Exponent: Trendy vs Random?
        hurst = calculate_hurst_exponent(freq_history)

        # Regime-Complexity: Anzahl Peaks
        regime_complexity = count_regime_peaks(freq_history)

        # Gesetz C: Criticality
        # Probability-Estimate: Durchschnittliche Frequenz der Hot-Numbers
        hot_freqs = [r.relative_frequency for r in frequency_results if r.classification == "hot"]
        avg_prob = sum(hot_freqs) / len(hot_freqs) if hot_freqs else 0.5

        criticality_score, criticality_level = calculate_criticality_from_config(
            probability=avg_prob,
            regime_complexity=regime_complexity,
            warning_threshold=self.config.physics.criticality_warning_threshold,
            critical_threshold=self.config.physics.criticality_critical_threshold,
        )

        # Avalanche-Analyse
        avalanche_result: Optional[AvalancheResult] = None
        recommended_max_picks = 6  # Default

        if self.config.physics.enable_avalanche and combination:
            n_picks = len(combination)
            avalanche_result = analyze_combination(
                precision=precision_estimate,
                n_picks=n_picks,
                avg_odds=1.0,  # Conservative
            )

            if self.config.physics.anti_avalanche_mode:
                # Berechne empfohlene max Picks fuer theta <= 0.75
                recommended_max_picks = max_picks_for_theta(
                    precision=precision_estimate,
                    max_theta=0.75,
                )

        return PhysicsResult(
            stability_score=stability_score,
            is_stable_law=is_stable_law,
            criticality_score=criticality_score,
            criticality_level=criticality_level,
            avalanche_result=avalanche_result,
            hurst_exponent=hurst,
            regime_complexity=regime_complexity,
            recommended_max_picks=recommended_max_picks,
        )

    def _run_least_action_selection(
        self,
        performance_overrides: Optional[dict[str, float]] = None,
    ) -> SelectionResult:
        """Fuehrt Least-Action Pipeline-Auswahl aus (Gesetz B).

        Waehlt die optimale Pipeline basierend auf dem Least-Action-Prinzip:
        - Niedrigere Komplexitaet wird bevorzugt
        - Niedrigere Instabilitaet wird bevorzugt
        - Hoehere Performance wird bevorzugt

        Args:
            performance_overrides: Optionale ROI-Ueberschreibungen aus Backtests.

        Returns:
            SelectionResult mit der ausgewaehlten Pipeline.
        """
        return self._pipeline_selector.select_from_defaults(
            performance_overrides=performance_overrides,
        )

    def get_pipeline_selector(self) -> PipelineSelector:
        """Gibt den PipelineSelector fuer manuelle Nutzung zurueck."""
        return self._pipeline_selector

    def _get_config_snapshot(self) -> dict:
        """Erstellt einen Snapshot der relevanten Config-Werte."""
        return {
            "version": self.config.version,
            "active_game": self.config.active_game,
            "physics": {
                "enable_model_laws": self.config.physics.enable_model_laws,
                "enable_least_action": self.config.physics.enable_least_action,
                "stability_threshold": self.config.physics.stability_threshold,
                "criticality_warning": self.config.physics.criticality_warning_threshold,
                "criticality_critical": self.config.physics.criticality_critical_threshold,
                "enable_avalanche": self.config.physics.enable_avalanche,
                "anti_avalanche_mode": self.config.physics.anti_avalanche_mode,
            },
            "analysis": {
                "min_frequency_threshold": self.config.analysis.min_frequency_threshold,
                "max_frequency_threshold": self.config.analysis.max_frequency_threshold,
            },
        }

    def validate_combination(
        self,
        combination: list[int],
        precision_estimate: float = 0.7,
    ) -> dict:
        """Validiert eine Kombination gegen Physics-Constraints.

        Args:
            combination: Spielkombination.
            precision_estimate: Geschaetzte Precision.

        Returns:
            Dict mit Validierungs-Ergebnis und Empfehlungen.
        """
        n_picks = len(combination)
        avalanche_result = analyze_combination(
            precision=precision_estimate,
            n_picks=n_picks,
        )

        recommended_max = max_picks_for_theta(precision_estimate, max_theta=0.75)

        return {
            "combination": combination,
            "n_picks": n_picks,
            "theta": avalanche_result.theta,
            "state": avalanche_result.state.value,
            "is_safe_to_bet": avalanche_result.is_safe_to_bet,
            "recommended_max_picks": recommended_max,
            "warning": (
                f"Consider reducing to {recommended_max} picks"
                if n_picks > recommended_max
                else None
            ),
        }


def run_pipeline(
    draws: list[DrawResult],
    config: KenobaseConfig,
    combination: Optional[list[int]] = None,
) -> PipelineResult:
    """Convenience-Funktion fuer Pipeline-Ausfuehrung.

    Args:
        draws: Liste von DrawResult-Objekten.
        config: Kenobase-Konfiguration.
        combination: Optionale Spielkombination.

    Returns:
        PipelineResult.
    """
    runner = PipelineRunner(config)
    return runner.run(draws, combination)


__all__ = [
    "PhysicsResult",
    "PipelineResult",
    "PipelineRunner",
    "run_pipeline",
]
