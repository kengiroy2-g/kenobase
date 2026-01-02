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
from kenobase.analysis.decade_distribution import (
    DecadeDistributionResult,
    analyze_decade_distribution,
)
from kenobase.analysis.pattern import (
    PatternResult,
    aggregate_patterns,
    extract_patterns,
    extract_patterns_from_draws,
)
from kenobase.analysis.sum_distribution import (
    SumDistributionResult,
    analyze_sum_distribution,
)
from kenobase.analysis.summen_signatur import (
    aggregate_bucket_counts,
    compute_summen_signatur,
    export_signatures as export_summen_signatur,
)
from kenobase.analysis.regional_affinity import (
    RegionalAffinityAnalysis,
    analyze_regional_affinity,
)
from kenobase.core.combination_filter import SumBounds, derive_sum_bounds_from_result
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
        sum_distribution_result: Summen-Verteilungs-Analyse (TASK-P05)
        sum_bounds: Abgeleitete Summen-Grenzen fuer Kombinations-Filter
        physics_result: Physics-Layer Ergebnisse
        warnings: Liste von Warnungen waehrend der Ausfuehrung
        config_snapshot: Verwendete Konfiguration (als Dict)
        regional_affinity: Regionale Affinitaetsanalyse (optional)
    """

    timestamp: datetime
    draws_count: int
    frequency_results: list[FrequencyResult]
    pair_frequency_results: list[PairFrequencyResult]
    pattern_results: list[PatternResult] = field(default_factory=list)
    aggregated_patterns: dict = field(default_factory=dict)
    sum_distribution_result: Optional[SumDistributionResult] = None
    sum_bounds: Optional[SumBounds] = None
    physics_result: Optional[PhysicsResult] = None
    pipeline_selection: Optional[SelectionResult] = None
    regional_affinity: Optional[RegionalAffinityAnalysis] = None
    decade_distribution: Optional[DecadeDistributionResult] = None
    summen_signatur_buckets: Optional[dict[int, dict[str, int]]] = None
    summen_signatur_path: Optional[str] = None
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
        source_path: Optional[str] = None,
    ) -> PipelineResult:
        """Fuehrt die vollstaendige Analyse-Pipeline aus.

        Args:
            draws: Liste von DrawResult-Objekten.
            combination: Optionale Spielkombination fuer Pattern-Analyse.
            precision_estimate: Geschaetzte Einzelzahl-Precision fuer Avalanche.
            source_path: Optionaler Pfad zur Datenquelle (fuer Artefakt-Metadaten).

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

        # Step 1.5: Dekaden-Verteilung (TRANS-002)
        max_number = max(number_range) if number_range else 70
        decade_distribution = analyze_decade_distribution(
            draws,
            max_number=max_number,
            numbers_per_draw=game_config.numbers_to_draw,
            guardrail_ratio=0.20,
        )
        if decade_distribution.guardrail_breached:
            warnings.append(
                f"decade_distribution guardrail exceeded (max deviation "
                f"{decade_distribution.max_deviation_ratio:.2f} > 0.20)"
            )
        if decade_distribution.warnings:
            warnings.extend(f"decade_distribution: {w}" for w in decade_distribution.warnings)

        # Step 2: Pattern-Analyse (optional)
        logger.debug("Step 2: Pattern analysis")
        pattern_results: list[PatternResult] = []
        aggregated_patterns: dict = {}

        if combination:
            pattern_results = extract_patterns_from_draws(combination, draws)
            aggregated_patterns = aggregate_patterns(pattern_results)

        # Step 2.5: Sum Distribution Analysis (TASK-P05)
        sum_distribution_result: Optional[SumDistributionResult] = None
        sum_bounds: Optional[SumBounds] = None

        sum_cfg = self.config.analysis.sum_windows
        if sum_cfg.enabled:
            logger.debug("Step 2.5: Sum distribution analysis")
            sum_distribution_result, sum_bounds = self._run_sum_analysis(draws)

            if sum_bounds and sum_bounds.is_active():
                logger.info(
                    f"Sum bounds derived: [{sum_bounds.min_sum}, {sum_bounds.max_sum}] "
                    f"(source={sum_bounds.source})"
                )

        # Step 2.6: Regionale Affinitaet (Bundesland)
        regional_affinity: Optional[RegionalAffinityAnalysis] = None
        regional_cfg = self.config.analysis.regional_affinity
        if regional_cfg.enabled:
            regional_affinity = analyze_regional_affinity(
                draws,
                number_range=number_range,
                numbers_per_draw=regional_cfg.numbers_per_draw_override
                or game_config.numbers_to_draw,
                min_draws_per_region=regional_cfg.min_draws_per_region,
                smoothing_alpha=regional_cfg.smoothing_alpha,
                z_threshold=regional_cfg.z_threshold,
                game=self.config.active_game,
            )
            if regional_affinity.warnings:
                warnings.extend(
                    f"regional_affinity: {w}" for w in regional_affinity.warnings
                )

        # Step 2.7: Summen-Signatur (TRANS-001)
        summen_signatur_buckets: Optional[dict[int, dict[str, int]]] = None
        summen_signatur_path: Optional[str] = None
        summen_cfg = self.config.analysis.summen_signatur
        if summen_cfg.enabled:
            summen_signatur_buckets, summen_signatur_path = self._run_summen_signatur(
                draws=draws,
                source_path=source_path,
            )

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
            sum_distribution_result=sum_distribution_result,
            sum_bounds=sum_bounds,
            physics_result=physics_result,
            pipeline_selection=pipeline_selection,
            regional_affinity=regional_affinity,
            decade_distribution=decade_distribution,
            summen_signatur_buckets=summen_signatur_buckets,
            summen_signatur_path=summen_signatur_path,
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

    def _run_sum_analysis(
        self,
        draws: list[DrawResult],
    ) -> tuple[Optional[SumDistributionResult], Optional[SumBounds]]:
        """Fuehrt Summen-Verteilungsanalyse durch (TASK-P05).

        Analysiert die Summen der gezogenen Zahlen und erkennt Cluster.
        Leitet daraus min_sum/max_sum Grenzen fuer den Kombinations-Filter ab.

        Args:
            draws: Liste von Ziehungen.

        Returns:
            Tuple (SumDistributionResult, SumBounds)
        """
        sum_cfg = self.config.analysis.sum_windows

        # Check for manual overrides first
        if sum_cfg.manual_min_sum is not None or sum_cfg.manual_max_sum is not None:
            logger.info("Using manual sum bounds from config")
            return None, SumBounds(
                min_sum=sum_cfg.manual_min_sum,
                max_sum=sum_cfg.manual_max_sum,
                source="config",
            )

        if not draws:
            return None, None

        # Calculate sums from draws
        sums = [sum(d.numbers) for d in draws]

        # Compute expected_mean dynamically from active game config
        game_config = self.config.get_active_game()
        expected_mean = game_config.get_expected_sum_mean()

        logger.debug(
            f"Sum analysis using game={self.config.active_game}, "
            f"expected_mean={expected_mean:.1f} (dynamic)"
        )

        # Run analysis
        result = analyze_sum_distribution(
            sums=sums,
            expected_mean=expected_mean,
            bin_width=sum_cfg.bin_width,
        )

        # Derive bounds from detected clusters
        sum_bounds = derive_sum_bounds_from_result(result, use_union=True)

        logger.info(
            f"Sum analysis: n={result.total_draws}, mean={result.sum_mean:.1f}, "
            f"std={result.sum_std:.1f}, clusters={len(result.clusters)}"
        )

        return result, sum_bounds

    def _run_summen_signatur(
        self,
        draws: list[DrawResult],
        source_path: Optional[str],
    ) -> tuple[Optional[dict[int, dict[str, int]]], Optional[str]]:
        """Berechnet Summen-Signatur und exportiert optional Artefakt."""
        cfg = self.config.analysis.summen_signatur
        if not draws:
            return None, None

        records = compute_summen_signatur(
            draws=draws,
            keno_types=cfg.keno_types,
            bucket_std_low=cfg.bucket_std_low,
            bucket_std_high=cfg.bucket_std_high,
            checksum_algorithm=cfg.checksum_algorithm,
            number_range=self.config.get_active_game().numbers_range,
            source=source_path or "",
        )
        if not records:
            return None, None

        bucket_counts = aggregate_bucket_counts(records)
        metadata = {
            "source": source_path or "",
            "keno_types": cfg.keno_types,
            "numbers_per_draw": len(draws[0].numbers) if draws and draws[0].numbers else 0,
            "bucket_std_low": cfg.bucket_std_low,
            "bucket_std_high": cfg.bucket_std_high,
            "generated_by": "pipeline_runner",
        }
        export_summen_signatur(records, cfg.latest_output, metadata)
        return bucket_counts, cfg.latest_output

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
        sum_cfg = self.config.analysis.sum_windows
        regional_cfg = self.config.analysis.regional_affinity
        summen_cfg = self.config.analysis.summen_signatur
        game_config = self.config.get_active_game()
        return {
            "version": self.config.version,
            "active_game": self.config.active_game,
            "game": {
                "name": game_config.name,
                "numbers_range": list(game_config.numbers_range),
                "numbers_to_draw": game_config.numbers_to_draw,
                "expected_sum_mean": game_config.get_expected_sum_mean(),
            },
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
                "sum_windows": {
                    "enabled": sum_cfg.enabled,
                    "bin_width": sum_cfg.bin_width,
                    "expected_mean_dynamic": game_config.get_expected_sum_mean(),
                    "manual_min_sum": sum_cfg.manual_min_sum,
                    "manual_max_sum": sum_cfg.manual_max_sum,
                },
                "regional_affinity": {
                    "enabled": regional_cfg.enabled,
                    "min_draws_per_region": regional_cfg.min_draws_per_region,
                    "smoothing_alpha": regional_cfg.smoothing_alpha,
                    "z_threshold": regional_cfg.z_threshold,
                    "numbers_per_draw_override": regional_cfg.numbers_per_draw_override,
                },
                "summen_signatur": {
                    "enabled": summen_cfg.enabled,
                    "keno_types": summen_cfg.keno_types,
                    "split_date": summen_cfg.split_date,
                    "bucket_std_low": summen_cfg.bucket_std_low,
                    "bucket_std_high": summen_cfg.bucket_std_high,
                    "latest_output": summen_cfg.latest_output,
                    "train_output": summen_cfg.train_output,
                    "test_output": summen_cfg.test_output,
                },
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
    source_path: Optional[str] = None,
) -> PipelineResult:
    """Convenience-Funktion fuer Pipeline-Ausfuehrung.

    Args:
        draws: Liste von DrawResult-Objekten.
        config: Kenobase-Konfiguration.
        combination: Optionale Spielkombination.
        source_path: Optionale Quelle fuer Artefakt-Metadaten.

    Returns:
        PipelineResult.
    """
    runner = PipelineRunner(config)
    return runner.run(draws, combination, source_path=source_path)


__all__ = [
    "PhysicsResult",
    "PipelineResult",
    "PipelineRunner",
    "SumBounds",
    "run_pipeline",
]
