"""Integration Tests fuer die Kenobase Pipeline.

End-to-End Tests die den gesamten Pipeline-Durchlauf testen,
von Data Loading bis Output-Generierung.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from kenobase.core.config import KenobaseConfig, load_config
from kenobase.core.data_loader import DataLoader, DrawResult, GameType
from kenobase.core.number_pool import NumberPoolGenerator
from kenobase.core.combination_engine import CombinationEngine
from kenobase.analysis.frequency import calculate_frequency, calculate_pair_frequency
from kenobase.analysis.pattern import extract_patterns, aggregate_patterns, PatternResult
from kenobase.physics.model_laws import is_law, calculate_criticality
from kenobase.physics.avalanche import calculate_theta, get_avalanche_state
from kenobase.pipeline.runner import PipelineRunner, run_pipeline


class TestEndToEndPipeline:
    """End-to-End Integration Tests fuer den gesamten Pipeline-Flow."""

    @pytest.fixture
    def realistic_draws(self) -> list[DrawResult]:
        """Erstellt realistische Ziehungsdaten fuer Integration Tests."""
        base_date = datetime(2024, 1, 1)
        draws = []

        # Erstelle 50 realistische KENO-Ziehungen mit variierenden Mustern
        for i in range(50):
            # Simuliere realistische Zahlenverteilung
            base_numbers = list(range(1, 71))
            # Rotate numbers to create variation
            offset = (i * 7) % 70
            numbers = [(n + offset) % 70 + 1 for n in range(20)]

            draws.append(
                DrawResult(
                    date=base_date + timedelta(days=i),
                    numbers=sorted(set(numbers)),
                    bonus=[],
                    game_type=GameType.KENO,
                )
            )
        return draws

    @pytest.fixture
    def default_config(self) -> KenobaseConfig:
        """Standard-Konfiguration fuer Tests."""
        return KenobaseConfig()

    def test_full_pipeline_execution(
        self, default_config: KenobaseConfig, realistic_draws: list[DrawResult]
    ) -> None:
        """Test: Vollstaendiger Pipeline-Durchlauf ohne Fehler."""
        runner = PipelineRunner(default_config)
        result = runner.run(realistic_draws)

        # Verify basic result structure
        assert result.draws_count == 50
        assert result.timestamp is not None
        assert isinstance(result.frequency_results, list)
        assert isinstance(result.pair_frequency_results, list)

    def test_pipeline_with_physics_layer(
        self, default_config: KenobaseConfig, realistic_draws: list[DrawResult]
    ) -> None:
        """Test: Pipeline mit Physics-Layer Integration."""
        runner = PipelineRunner(default_config)
        result = runner.run(realistic_draws)

        # Physics results should be present
        assert result.physics_result is not None
        assert 0.0 <= result.physics_result.stability_score <= 1.0
        assert result.physics_result.criticality_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert result.physics_result.hurst_exponent >= 0.0

    def test_pipeline_with_combination_validation(
        self, default_config: KenobaseConfig, realistic_draws: list[DrawResult]
    ) -> None:
        """Test: Pipeline mit Kombinations-Validierung."""
        runner = PipelineRunner(default_config)
        combination = [5, 12, 23, 34, 45, 56]

        result = runner.run(realistic_draws, combination=combination)

        # Should have pattern analysis results
        assert result.aggregated_patterns is not None

        # Physics should include avalanche assessment
        if result.physics_result:
            assert result.physics_result.avalanche_result is not None

    def test_frequency_to_pattern_flow(
        self, default_config: KenobaseConfig, realistic_draws: list[DrawResult]
    ) -> None:
        """Test: Datenfluss von Frequency Analysis zu Pattern Detection."""
        # Run pipeline
        runner = PipelineRunner(default_config)
        result = runner.run(realistic_draws)

        # Frequency results should inform pattern analysis
        # FrequencyResult objects have .number attribute
        freq_numbers = {r.number for r in result.frequency_results}

        # Patterns should use numbers from frequency analysis
        # PairFrequencyResult objects have .pair attribute (tuple of 2 numbers)
        for pattern in result.pair_frequency_results:
            if hasattr(pattern, 'pair'):
                for num in pattern.pair:
                    assert 1 <= num <= 70  # Valid KENO range

    def test_warnings_propagation(
        self, realistic_draws: list[DrawResult]
    ) -> None:
        """Test: Warnungen werden durch Pipeline propagiert."""
        config = KenobaseConfig()
        # Set very high stability threshold to trigger warning
        config.physics.stability_threshold = 0.999

        runner = PipelineRunner(config)
        result = runner.run(realistic_draws)

        # Should have warnings due to stability threshold
        assert len(result.warnings) > 0

    def test_config_snapshot_preserved(
        self, default_config: KenobaseConfig, realistic_draws: list[DrawResult]
    ) -> None:
        """Test: Config-Snapshot wird im Ergebnis korrekt erhalten."""
        runner = PipelineRunner(default_config)
        result = runner.run(realistic_draws)

        # Config snapshot should match input config
        assert "version" in result.config_snapshot
        assert result.config_snapshot["physics"]["enable_model_laws"] is True
        assert result.config_snapshot["physics"]["enable_avalanche"] is True


class TestDataLoaderToAnalysisFlow:
    """Tests fuer den Datenfluss von DataLoader zu Analysis-Modulen."""

    @pytest.fixture
    def sample_draws(self) -> list[DrawResult]:
        """Erstellt Test-Ziehungen direkt."""
        base_date = datetime(2024, 1, 1)
        return [
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=[1+i, 5+i, 12+i, 23+i, 34, 45, 56, 67, 2, 8, 15, 25, 36, 47, 58, 68, 3, 9, 16, 26],
                bonus=[],
                game_type=GameType.KENO,
            )
            for i in range(3)
        ]

    def test_draws_to_frequency_analysis(
        self, sample_draws: list[DrawResult]
    ) -> None:
        """Test: Ziehungen fliessen korrekt in Frequency Analysis."""
        assert len(sample_draws) == 3

        # Run frequency analysis
        results = calculate_frequency(sample_draws)

        assert len(results) > 0

    def test_number_pool_generation_from_draws(
        self, sample_draws: list[DrawResult]
    ) -> None:
        """Test: NumberPool wird korrekt aus Ziehungen generiert."""
        # NumberPoolGenerator needs enough draws for its periods
        # With 3 draws and n_periods=1, draws_per_period=3 should work
        generator = NumberPoolGenerator(n_periods=1, draws_per_period=3, top_n_per_period=10)
        pool = generator.generate(sample_draws)

        assert len(pool) > 0
        assert all(1 <= n <= 70 for n in pool)


class TestPhysicsLayerIntegration:
    """Tests fuer Physics-Layer Integration in Pipeline."""

    def test_stability_to_criticality_flow(self) -> None:
        """Test: Stability-Score fliesst in Criticality-Berechnung."""
        # Test data representing a stable pattern
        def stable_relation(**kwargs: Any) -> float:
            return 0.5  # Constant output = stable

        variations = [{"param": i} for i in range(10)]
        stability, is_stable = is_law(stable_relation, variations, threshold=0.9)

        assert stability >= 0.9
        assert is_stable == True  # Use == for numpy compatibility

        # Use stability in criticality calculation
        criticality, level = calculate_criticality(0.5, regime_complexity=2)
        assert level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_avalanche_state_integration(self) -> None:
        """Test: Avalanche-State wird korrekt berechnet und propagiert."""
        # Test different pick counts with same precision
        precision = 0.7

        for n_picks in [2, 4, 6, 8]:
            theta = calculate_theta(precision, n_picks)
            state = get_avalanche_state(theta)

            assert 0.0 <= theta <= 1.0
            assert state in ["SAFE", "MODERATE", "WARNING", "CRITICAL"]

            # More picks should lead to higher theta
            if n_picks >= 6:
                assert state in ["WARNING", "CRITICAL"]


class TestCombinationEngineIntegration:
    """Tests fuer Kombinations-Engine Integration."""

    def test_pool_to_combinations_flow(self) -> None:
        """Test: Number Pool fliesst korrekt in Kombinations-Generierung."""
        pool = {1, 5, 12, 23, 34, 45, 56, 67, 8, 15, 25}

        engine = CombinationEngine(
            pool=pool,
            combination_size=6,
            max_per_decade=3,
            min_sum=100,
        )

        combinations = list(engine.generate())

        assert len(combinations) > 0

        for combo in combinations:
            assert len(combo.numbers) == 6
            # Check decade filter
            decades = [(n - 1) // 10 for n in combo.numbers]
            from collections import Counter
            decade_counts = Counter(decades)
            assert all(count <= 3 for count in decade_counts.values())

    def test_combination_to_pattern_analysis_flow(self) -> None:
        """Test: Kombinationen fliessen korrekt in Pattern-Analyse."""
        combinations = [
            [1, 5, 12, 23, 34, 45],
            [2, 6, 13, 24, 35, 46],
            [3, 7, 14, 25, 36, 47],
        ]

        # Simulated draw that overlaps with some combinations
        draw = [1, 5, 12, 23, 7, 9, 14, 25, 22, 28, 33, 41, 48, 52, 55, 61, 64, 67, 69, 70]

        for combo in combinations:
            result = extract_patterns(combo, draw)
            assert isinstance(result, PatternResult)
            assert result.match_count >= 0


class TestConvenienceFunctionIntegration:
    """Tests fuer Convenience-Funktionen."""

    @pytest.fixture
    def sample_draws(self) -> list[DrawResult]:
        """Einfache Ziehungsdaten."""
        return [
            DrawResult(
                date=datetime(2024, 1, i),
                numbers=list(range(i, i + 20)),
                bonus=[],
                game_type=GameType.KENO,
            )
            for i in range(1, 11)
        ]

    def test_run_pipeline_convenience(
        self, sample_draws: list[DrawResult]
    ) -> None:
        """Test: run_pipeline Convenience-Funktion."""
        config = KenobaseConfig()
        result = run_pipeline(sample_draws, config)

        assert result.draws_count == 10
        assert result.timestamp is not None
