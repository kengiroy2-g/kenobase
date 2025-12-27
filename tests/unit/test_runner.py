"""Unit Tests fuer Pipeline Runner mit Physics-Integration.

Tests fuer kenobase/pipeline/runner.py
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from kenobase.core.config import KenobaseConfig, PhysicsConfig
from kenobase.core.data_loader import DrawResult, GameType
from kenobase.physics.avalanche import AvalancheState
from kenobase.pipeline.runner import (
    PhysicsResult,
    PipelineResult,
    PipelineRunner,
    run_pipeline,
)


@pytest.fixture
def sample_draws() -> list[DrawResult]:
    """Erstellt Beispiel-Ziehungen fuer Tests."""
    from datetime import timedelta

    base_date = datetime(2024, 1, 1)
    draws = []
    for i in range(100):
        # Create draws with varying numbers
        numbers = [(i + j) % 70 + 1 for j in range(20)]
        draws.append(
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=numbers,
                bonus=[],
                game_type=GameType.KENO,
            )
        )
    return draws


@pytest.fixture
def default_config() -> KenobaseConfig:
    """Erstellt Standard-Konfiguration."""
    return KenobaseConfig()


@pytest.fixture
def physics_disabled_config() -> KenobaseConfig:
    """Konfiguration mit deaktivierter Physics-Layer."""
    config = KenobaseConfig()
    config.physics.enable_model_laws = False
    config.physics.enable_avalanche = False
    return config


class TestPipelineRunner:
    """Tests fuer PipelineRunner."""

    def test_init_with_config(self, default_config: KenobaseConfig) -> None:
        """Test: Runner kann mit Config initialisiert werden."""
        runner = PipelineRunner(default_config)
        assert runner.config == default_config

    def test_run_empty_draws(self, default_config: KenobaseConfig) -> None:
        """Test: Pipeline mit leerer Draw-Liste."""
        runner = PipelineRunner(default_config)
        result = runner.run([])

        assert result.draws_count == 0
        assert result.frequency_results == []
        assert result.pair_frequency_results == []
        assert "No draws provided" in result.warnings

    def test_run_with_draws(
        self, default_config: KenobaseConfig, sample_draws: list[DrawResult]
    ) -> None:
        """Test: Pipeline mit Ziehungen."""
        runner = PipelineRunner(default_config)
        result = runner.run(sample_draws)

        assert result.draws_count == 100
        assert len(result.frequency_results) > 0
        assert len(result.pair_frequency_results) > 0
        assert result.timestamp is not None

    def test_run_with_physics_layer(
        self, default_config: KenobaseConfig, sample_draws: list[DrawResult]
    ) -> None:
        """Test: Pipeline mit Physics-Layer."""
        runner = PipelineRunner(default_config)
        result = runner.run(sample_draws)

        assert result.physics_result is not None
        assert 0.0 <= result.physics_result.stability_score <= 1.0
        assert result.physics_result.criticality_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert result.physics_result.hurst_exponent >= 0.0

    def test_run_without_physics(
        self, physics_disabled_config: KenobaseConfig, sample_draws: list[DrawResult]
    ) -> None:
        """Test: Pipeline ohne Physics-Layer."""
        runner = PipelineRunner(physics_disabled_config)
        result = runner.run(sample_draws)

        assert result.physics_result is None

    def test_run_with_combination(
        self, default_config: KenobaseConfig, sample_draws: list[DrawResult]
    ) -> None:
        """Test: Pipeline mit Kombination fuer Pattern-Analyse."""
        runner = PipelineRunner(default_config)
        combination = [1, 5, 12, 23, 34, 45]
        result = runner.run(sample_draws, combination=combination)

        # Pattern analysis should have run
        assert result.aggregated_patterns is not None
        # Physics should have avalanche result
        if result.physics_result:
            assert result.physics_result.avalanche_result is not None

    def test_validate_combination_safe(self, default_config: KenobaseConfig) -> None:
        """Test: Kombinations-Validierung (sicher)."""
        runner = PipelineRunner(default_config)
        # 2 Picks mit 80% Precision = theta ~0.36 = SAFE
        result = runner.validate_combination([1, 2], precision_estimate=0.8)

        assert result["n_picks"] == 2
        assert result["state"] == "SAFE"
        assert result["theta"] < 0.5  # SAFE threshold

    def test_validate_combination_critical(self, default_config: KenobaseConfig) -> None:
        """Test: Kombinations-Validierung (kritisch)."""
        runner = PipelineRunner(default_config)
        # 6 Picks mit 70% Precision = theta ~0.88 = CRITICAL
        result = runner.validate_combination(
            [1, 2, 3, 4, 5, 6], precision_estimate=0.7
        )

        assert result["n_picks"] == 6
        assert result["state"] == "CRITICAL"
        assert result["theta"] > 0.85

    def test_config_snapshot(
        self, default_config: KenobaseConfig, sample_draws: list[DrawResult]
    ) -> None:
        """Test: Config-Snapshot wird korrekt erstellt."""
        runner = PipelineRunner(default_config)
        result = runner.run(sample_draws[:10])

        assert "version" in result.config_snapshot
        assert "physics" in result.config_snapshot
        assert "analysis" in result.config_snapshot
        assert result.config_snapshot["physics"]["enable_model_laws"] is True


class TestPhysicsResult:
    """Tests fuer PhysicsResult Dataclass."""

    def test_physics_result_creation(self) -> None:
        """Test: PhysicsResult kann erstellt werden."""
        result = PhysicsResult(
            stability_score=0.95,
            is_stable_law=True,
            criticality_score=0.3,
            criticality_level="LOW",
            avalanche_result=None,
            hurst_exponent=0.5,
            regime_complexity=2,
            recommended_max_picks=4,
        )

        assert result.stability_score == 0.95
        assert result.is_stable_law is True
        assert result.criticality_level == "LOW"


class TestPipelineResult:
    """Tests fuer PipelineResult Dataclass."""

    def test_pipeline_result_defaults(self) -> None:
        """Test: PipelineResult mit Default-Werten."""
        result = PipelineResult(
            timestamp=datetime.now(),
            draws_count=100,
            frequency_results=[],
            pair_frequency_results=[],
        )

        assert result.pattern_results == []
        assert result.aggregated_patterns == {}
        assert result.warnings == []
        assert result.physics_result is None


class TestRunPipeline:
    """Tests fuer run_pipeline Convenience-Funktion."""

    def test_run_pipeline_convenience(
        self, default_config: KenobaseConfig, sample_draws: list[DrawResult]
    ) -> None:
        """Test: run_pipeline Funktion."""
        result = run_pipeline(sample_draws[:10], default_config)

        assert isinstance(result, PipelineResult)
        assert result.draws_count == 10


class TestPhysicsIntegration:
    """Integration Tests fuer Physics-Layer in Pipeline."""

    def test_stability_below_threshold_adds_warning(
        self, sample_draws: list[DrawResult]
    ) -> None:
        """Test: Niedrige Stabilitaet erzeugt Warnung."""
        config = KenobaseConfig()
        config.physics.stability_threshold = 0.99  # Very high threshold
        runner = PipelineRunner(config)

        result = runner.run(sample_draws)

        # Should have stability warning since threshold is very high
        stability_warnings = [w for w in result.warnings if "stability" in w.lower()]
        assert len(stability_warnings) > 0

    def test_critical_avalanche_adds_warning(
        self, sample_draws: list[DrawResult]
    ) -> None:
        """Test: Kritischer Avalanche-State erzeugt Warnung."""
        config = KenobaseConfig()
        runner = PipelineRunner(config)

        # 6-pick combination with 70% precision = CRITICAL
        combination = [1, 5, 12, 23, 34, 45]
        result = runner.run(sample_draws, combination=combination, precision_estimate=0.7)

        avalanche_warnings = [w for w in result.warnings if "avalanche" in w.lower()]
        assert len(avalanche_warnings) > 0

    def test_recommended_max_picks_anti_avalanche(
        self, default_config: KenobaseConfig
    ) -> None:
        """Test: Anti-Avalanche empfiehlt reduzierte Picks."""
        runner = PipelineRunner(default_config)

        # At 70% precision, max 3 picks for theta <= 0.75
        max_picks = runner.validate_combination(
            [1, 2, 3, 4, 5, 6], precision_estimate=0.7
        )["recommended_max_picks"]

        assert max_picks <= 4  # Should recommend 3-4 picks
