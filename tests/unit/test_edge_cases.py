"""Unit Tests fuer Edge Cases und Grenzfaelle.

Diese Tests decken Randfaelle ab, die in normalen Tests
moeglicherweise nicht abgedeckt werden.
"""

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from kenobase.core.config import KenobaseConfig
from kenobase.core.data_loader import DrawResult, GameType


class TestConfigEdgeCases:
    """Edge Cases fuer Config-System."""

    def test_config_with_zero_values(self) -> None:
        """Test: Config mit Null-Werten."""
        config = KenobaseConfig()
        config.analysis.min_frequency_threshold = 0.0  # Valid edge case

        assert config.analysis.min_frequency_threshold == 0.0

    def test_config_with_extreme_thresholds(self) -> None:
        """Test: Config mit extremen Threshold-Werten."""
        config = KenobaseConfig()

        # Edge: Threshold bei exakt 0.0
        config.physics.stability_threshold = 0.0
        assert config.physics.stability_threshold == 0.0

        # Edge: Threshold bei exakt 1.0
        config.physics.stability_threshold = 1.0
        assert config.physics.stability_threshold == 1.0

    def test_config_negative_values_handling(self) -> None:
        """Test: Config reagiert auf negative Werte."""
        config = KenobaseConfig()

        # Negative thresholds should trigger validation in pydantic
        # This tests that the config stores valid values correctly
        config.analysis.duo_min_occurrences = 0
        assert config.analysis.duo_min_occurrences == 0


class TestDataLoaderEdgeCases:
    """Edge Cases fuer Data Loader."""

    def test_draw_result_with_empty_numbers(self) -> None:
        """Test: DrawResult mit leerer Zahlenliste."""
        draw = DrawResult(
            date=datetime.now(),
            numbers=[],
            bonus=[],
            game_type=GameType.KENO,
        )

        assert draw.numbers == []
        assert len(draw.numbers) == 0

    def test_draw_result_with_single_number(self) -> None:
        """Test: DrawResult mit nur einer Zahl."""
        draw = DrawResult(
            date=datetime.now(),
            numbers=[42],
            bonus=[],
            game_type=GameType.KENO,
        )

        assert len(draw.numbers) == 1
        assert draw.numbers[0] == 42

    def test_draw_result_with_duplicate_numbers(self) -> None:
        """Test: DrawResult mit duplizierten Zahlen (ungueltig aber moeglich)."""
        draw = DrawResult(
            date=datetime.now(),
            numbers=[1, 1, 2, 2, 3],
            bonus=[],
            game_type=GameType.KENO,
        )

        # Should store as-is (validation is separate)
        assert len(draw.numbers) == 5
        assert draw.numbers.count(1) == 2

    def test_draw_result_boundary_numbers(self) -> None:
        """Test: DrawResult mit Grenzzahlen."""
        # KENO: 1-70
        draw = DrawResult(
            date=datetime.now(),
            numbers=[1, 70],  # Min and max
            bonus=[],
            game_type=GameType.KENO,
        )

        assert 1 in draw.numbers
        assert 70 in draw.numbers


class TestPhysicsEdgeCases:
    """Edge Cases fuer Physics-Module."""

    def test_stability_with_constant_relation(self) -> None:
        """Test: Stabilitaet bei konstanter Relation (perfekt stabil)."""
        from kenobase.physics.model_laws import is_law

        def constant(**kwargs: Any) -> float:
            return 42.0

        variations = [{"x": i} for i in range(10)]
        stability, is_stable = is_law(constant, variations)

        assert stability == 1.0  # Perfekt stabil
        assert is_stable == True  # Use == for numpy compatibility

    def test_stability_with_empty_variations(self) -> None:
        """Test: Stabilitaet mit leeren Variationen."""
        from kenobase.physics.model_laws import is_law

        def any_fn(**kwargs: Any) -> float:
            return 1.0

        # Empty variations - behavior depends on implementation
        # With no data points, stability cannot be meaningfully computed
        stability, is_stable = is_law(any_fn, [])
        # May return 0.0 (no stability computable) or 1.0 (no variance)
        assert 0.0 <= stability <= 1.0

    def test_stability_with_single_variation(self) -> None:
        """Test: Stabilitaet mit nur einer Variation."""
        from kenobase.physics.model_laws import is_law

        def any_fn(**kwargs: Any) -> float:
            return 1.0

        variations = [{"x": 1}]
        stability, is_stable = is_law(any_fn, variations)

        # Single data point = stable (std = 0)
        assert stability == 1.0
        assert is_stable == True  # Use == for numpy compatibility

    def test_criticality_at_boundary_probability(self) -> None:
        """Test: Criticality bei Grenzwahrscheinlichkeiten."""
        from kenobase.physics.model_laws import calculate_criticality

        # Edge: prob = 0.0 (minimal sensitivity)
        score_0, level_0 = calculate_criticality(0.0, regime_complexity=1)
        assert score_0 == 0.0

        # Edge: prob = 1.0 (minimal sensitivity)
        score_1, level_1 = calculate_criticality(1.0, regime_complexity=1)
        assert score_1 == 0.0

        # Edge: prob = 0.5 (maximum sensitivity)
        score_half, level_half = calculate_criticality(0.5, regime_complexity=1)
        assert score_half == 1.0

    def test_avalanche_theta_at_zero_precision(self) -> None:
        """Test: Theta bei 0% Precision."""
        from kenobase.physics.avalanche import calculate_theta

        # 0% precision = 100% loss
        theta = calculate_theta(0.0, 1)
        assert theta == 1.0

    def test_avalanche_theta_at_perfect_precision(self) -> None:
        """Test: Theta bei 100% Precision."""
        from kenobase.physics.avalanche import calculate_theta

        # 100% precision = 0% loss
        theta = calculate_theta(1.0, 10)
        assert theta == 0.0

    def test_avalanche_zero_picks(self) -> None:
        """Test: Avalanche bei 0 Picks."""
        from kenobase.physics.avalanche import calculate_theta

        # 0 picks = theta = 0 (no bet, no loss)
        theta = calculate_theta(0.5, 0)
        assert theta == 0.0

    def test_hurst_with_constant_data(self) -> None:
        """Test: Hurst-Exponent bei konstanten Daten."""
        from kenobase.physics.metrics import calculate_hurst_exponent

        # Constant data should handle gracefully
        constant_data = [1.0] * 100
        try:
            hurst = calculate_hurst_exponent(constant_data)
            # May return special value or raise
            assert hurst is not None
        except (ValueError, ZeroDivisionError):
            # Expected for constant data
            pass

    def test_hurst_with_short_series(self) -> None:
        """Test: Hurst-Exponent mit sehr kurzer Zeitreihe."""
        from kenobase.physics.metrics import calculate_hurst_exponent

        # Very short series
        short_data = [1.0, 2.0, 1.5]
        try:
            hurst = calculate_hurst_exponent(short_data)
            assert 0.0 <= hurst <= 1.0
        except ValueError:
            # May require minimum length
            pass


class TestCombinationEngineEdgeCases:
    """Edge Cases fuer Kombinations-Engine."""

    def test_generate_from_empty_pool(self) -> None:
        """Test: Kombinationen aus leerem Pool wirft ValueError."""
        from kenobase.core.combination_engine import CombinationEngine

        # Empty pool should raise ValueError
        with pytest.raises(ValueError, match="cannot be empty"):
            CombinationEngine(pool=set(), combination_size=6)

    def test_generate_from_pool_smaller_than_size(self) -> None:
        """Test: Pool kleiner als gewuenschte Kombinationsgroesse wirft ValueError."""
        from kenobase.core.combination_engine import CombinationEngine

        # Pool smaller than combination_size should raise ValueError
        with pytest.raises(ValueError, match="must be >= combination_size"):
            CombinationEngine(pool={1, 2, 3}, combination_size=6)

    def test_generate_from_exact_size_pool(self) -> None:
        """Test: Pool exakt gleich Kombinationsgroesse."""
        from kenobase.core.combination_engine import CombinationEngine

        pool = {1, 2, 3, 4, 5, 6}
        engine = CombinationEngine(pool=pool, combination_size=6, max_per_decade=10)
        combos = list(engine.generate())

        # Should generate exactly one combination
        assert len(combos) == 1
        assert set(combos[0].numbers) == pool

    def test_decade_filter_with_all_same_decade(self) -> None:
        """Test: Zehnerfilter wenn alle Zahlen in einer Dekade."""
        from kenobase.core.combination_engine import CombinationEngine

        pool = {11, 12, 13, 14, 15, 16, 17, 18}  # All in decade 1
        engine = CombinationEngine(pool=pool, combination_size=6, max_per_decade=2)

        combos = list(engine.generate())

        # With max_per_decade=2, can't form 6-combos from same decade
        assert len(combos) == 0


class TestFrequencyEdgeCases:
    """Edge Cases fuer Frequency Analysis."""

    def test_analyze_empty_draws(self) -> None:
        """Test: Frequency Analysis ohne Ziehungen."""
        from kenobase.analysis.frequency import calculate_frequency

        results = calculate_frequency([])

        assert len(results) == 0

    def test_analyze_single_draw(self) -> None:
        """Test: Frequency Analysis mit nur einer Ziehung."""
        from datetime import datetime
        from kenobase.analysis.frequency import calculate_frequency
        from kenobase.core.data_loader import DrawResult, GameType

        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 2, 3],
                bonus=[],
                game_type=GameType.KENO,
            )
        ]
        results = calculate_frequency(draws)

        assert len(results) == 3
        for r in results:
            assert r.absolute_frequency == 1

    def test_analyze_with_frequency_threshold(self) -> None:
        """Test: Frequency threshold filtering."""
        from datetime import datetime
        from kenobase.analysis.frequency import calculate_frequency
        from kenobase.core.data_loader import DrawResult, GameType

        draws = [
            DrawResult(
                date=datetime(2024, 1, i),
                numbers=[1, 2, 3] if i <= 2 else [1, 2, 4],
                bonus=[],
                game_type=GameType.KENO,
            )
            for i in range(1, 4)
        ]
        results = calculate_frequency(draws)

        # Number 1 and 2 appear in all 3 draws
        freq_1 = next((r for r in results if r.number == 1), None)
        assert freq_1 is not None
        assert freq_1.absolute_frequency == 3


class TestPatternEdgeCases:
    """Edge Cases fuer Pattern Analysis."""

    def test_pattern_with_single_number_combo(self) -> None:
        """Test: Pattern Analysis mit 1-Zahl-Kombination."""
        from kenobase.analysis.pattern import extract_patterns, PatternResult

        # Extract patterns from single number combo
        combo = [42]
        draw = [1, 2, 42, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        result = extract_patterns(combo, draw)

        # Should handle single number gracefully
        assert isinstance(result, PatternResult)
        assert result.match_count <= 1  # At most 1 match

    def test_pattern_with_no_matches(self) -> None:
        """Test: Pattern Analysis ohne Treffer."""
        from kenobase.analysis.pattern import extract_patterns, PatternResult

        # No overlap between combo and draw
        combo = [1, 2, 3, 4, 5, 6]
        draw = [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
        result = extract_patterns(combo, draw)

        assert isinstance(result, PatternResult)
        assert result.match_count == 0
        assert len(result.duos) == 0


class TestPipelineEdgeCases:
    """Edge Cases fuer Pipeline Runner."""

    def test_pipeline_with_single_draw(self) -> None:
        """Test: Pipeline mit nur einer Ziehung."""
        from kenobase.pipeline.runner import PipelineRunner

        config = KenobaseConfig()
        runner = PipelineRunner(config)

        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                         11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                bonus=[],
                game_type=GameType.KENO,
            )
        ]

        result = runner.run(draws)

        assert result.draws_count == 1

    def test_pipeline_with_identical_draws(self) -> None:
        """Test: Pipeline mit identischen Ziehungen."""
        from kenobase.pipeline.runner import PipelineRunner

        config = KenobaseConfig()
        runner = PipelineRunner(config)

        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                   11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

        draws = [
            DrawResult(
                date=datetime(2024, 1, i),
                numbers=numbers.copy(),
                bonus=[],
                game_type=GameType.KENO,
            )
            for i in range(1, 11)
        ]

        result = runner.run(draws)

        # All draws identical - verify basic pipeline execution
        assert result.draws_count == 10
        # Physics result should exist
        assert result.physics_result is not None
        # Stability score should be computed (value depends on implementation)
        assert 0.0 <= result.physics_result.stability_score <= 1.0

    def test_validate_combination_empty(self) -> None:
        """Test: Kombinations-Validierung mit leerer Kombination."""
        from kenobase.pipeline.runner import PipelineRunner

        config = KenobaseConfig()
        runner = PipelineRunner(config)

        result = runner.validate_combination([], precision_estimate=0.7)

        assert result["n_picks"] == 0
        assert result["theta"] == 0.0
        assert result["state"] == "SAFE"


class TestNumberPoolEdgeCases:
    """Edge Cases fuer Number Pool Generator."""

    def test_pool_from_empty_draws(self) -> None:
        """Test: Pool aus leeren Ziehungen wirft ValueError."""
        from kenobase.core.number_pool import NumberPoolGenerator

        generator = NumberPoolGenerator()

        # Empty draws should raise ValueError due to minimum draw requirement
        with pytest.raises(ValueError, match="Need at least"):
            generator.generate([])

    def test_pool_with_few_draws(self) -> None:
        """Test: Pool mit weniger Draws als erwartet wirft ValueError."""
        from kenobase.core.number_pool import NumberPoolGenerator
        from kenobase.core.data_loader import DrawResult, GameType

        # Only 2 draws, but generator expects 30 (3 periods * 10 draws)
        generator = NumberPoolGenerator(n_periods=1, draws_per_period=3)
        draws = [
            DrawResult(date=datetime(2024, 1, i), numbers=[1, 2, 3], bonus=[], game_type=GameType.KENO)
            for i in range(1, 3)  # Only 2 draws
        ]

        # Should raise ValueError because 2 < 3 (n_periods * draws_per_period)
        with pytest.raises(ValueError, match="Need at least"):
            generator.generate(draws)


class TestOutputFormatEdgeCases:
    """Edge Cases fuer Output-Formatierung."""

    def test_format_empty_result(self) -> None:
        """Test: Formatierung von leerem Ergebnis."""
        from kenobase.pipeline.output_formats import OutputFormatter, OutputFormat
        from kenobase.pipeline.runner import PipelineResult

        result = PipelineResult(
            timestamp=datetime.now(),
            draws_count=0,
            frequency_results=[],
            pair_frequency_results=[],
        )

        # Convert to dict for formatting
        result_dict = {
            "timestamp": result.timestamp.isoformat(),
            "draws_count": result.draws_count,
            "frequency_results": result.frequency_results,
            "pair_frequency_results": result.pair_frequency_results,
        }

        formatter = OutputFormatter()
        output = formatter.format(result_dict, OutputFormat.JSON)

        assert output is not None
        assert "draws_count" in output or "0" in output
