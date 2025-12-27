"""Unit tests for least_action.py - Model Law B Pipeline Selection.

Tests the Least-Action pipeline selection mechanism:
- PipelineVariant creation and conversion
- PipelineSelector with different configurations
- SelectionResult structure
- Integration with model_laws.py functions
"""

import pytest

from kenobase.core.config import KenobaseConfig, PhysicsConfig
from kenobase.pipeline.least_action import (
    DEFAULT_PIPELINE_VARIANTS,
    PipelineSelector,
    PipelineVariant,
    SelectionResult,
    create_variant_from_analysis_config,
)
from kenobase.physics.model_laws import (
    PipelineConfig as PhysicsPipelineConfig,
    calculate_pipeline_action,
)


class TestPipelineVariant:
    """Tests for PipelineVariant dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        variant = PipelineVariant(name="test")
        assert variant.name == "test"
        assert variant.num_features == 10
        assert variant.num_rules == 5
        assert variant.num_special_cases == 0
        assert variant.performance_variance == 0.1
        assert variant.roi == 1.0
        assert variant.description == ""

    def test_custom_values(self) -> None:
        """Test custom values are preserved."""
        variant = PipelineVariant(
            name="custom",
            num_features=15,
            num_rules=8,
            num_special_cases=3,
            performance_variance=0.2,
            roi=1.5,
            description="Custom variant",
        )
        assert variant.name == "custom"
        assert variant.num_features == 15
        assert variant.num_rules == 8
        assert variant.num_special_cases == 3
        assert variant.performance_variance == 0.2
        assert variant.roi == 1.5
        assert variant.description == "Custom variant"

    def test_to_physics_config(self) -> None:
        """Test conversion to PhysicsPipelineConfig."""
        variant = PipelineVariant(
            name="test",
            num_features=10,
            num_rules=5,
            num_special_cases=2,
            performance_variance=0.15,
            roi=1.2,
        )
        physics_config = variant.to_physics_config()

        assert isinstance(physics_config, PhysicsPipelineConfig)
        assert physics_config.num_features == 10
        assert physics_config.num_rules == 5
        assert physics_config.num_special_cases == 2
        assert physics_config.performance_variance == 0.15
        assert physics_config.roi == 1.2


class TestDefaultPipelineVariants:
    """Tests for DEFAULT_PIPELINE_VARIANTS."""

    def test_default_variants_exist(self) -> None:
        """Test that default variants are defined."""
        assert len(DEFAULT_PIPELINE_VARIANTS) == 4

    def test_variant_names(self) -> None:
        """Test expected variant names."""
        names = [v.name for v in DEFAULT_PIPELINE_VARIANTS]
        assert "minimal" in names
        assert "standard" in names
        assert "extended" in names
        assert "full" in names

    def test_minimal_has_lowest_complexity(self) -> None:
        """Test minimal variant has lowest feature count."""
        minimal = next(v for v in DEFAULT_PIPELINE_VARIANTS if v.name == "minimal")
        for variant in DEFAULT_PIPELINE_VARIANTS:
            if variant.name != "minimal":
                assert minimal.num_features <= variant.num_features

    def test_all_have_descriptions(self) -> None:
        """Test all variants have descriptions."""
        for variant in DEFAULT_PIPELINE_VARIANTS:
            assert variant.description != ""


class TestPipelineSelector:
    """Tests for PipelineSelector class."""

    @pytest.fixture
    def config_enabled(self) -> KenobaseConfig:
        """Config with least-action enabled."""
        config = KenobaseConfig()
        config.physics = PhysicsConfig(enable_least_action=True)
        return config

    @pytest.fixture
    def config_disabled(self) -> KenobaseConfig:
        """Config with least-action disabled."""
        config = KenobaseConfig()
        config.physics = PhysicsConfig(enable_least_action=False)
        return config

    def test_enabled_property(
        self,
        config_enabled: KenobaseConfig,
        config_disabled: KenobaseConfig,
    ) -> None:
        """Test enabled property reflects config."""
        selector_on = PipelineSelector(config_enabled)
        selector_off = PipelineSelector(config_disabled)

        assert selector_on.enabled is True
        assert selector_off.enabled is False

    def test_select_empty_raises(self, config_enabled: KenobaseConfig) -> None:
        """Test select with empty list raises ValueError."""
        selector = PipelineSelector(config_enabled)
        with pytest.raises(ValueError, match="At least one pipeline variant required"):
            selector.select([])

    def test_select_single_variant(self, config_enabled: KenobaseConfig) -> None:
        """Test select with single variant returns it."""
        selector = PipelineSelector(config_enabled)
        variant = PipelineVariant(name="only_one", roi=1.5)

        result = selector.select([variant])

        assert result.selected_name == "only_one"
        assert len(result.all_actions) == 1

    def test_select_prefers_lower_action(self, config_enabled: KenobaseConfig) -> None:
        """Test selector prefers variant with lower action."""
        selector = PipelineSelector(config_enabled)

        # Same performance but different complexity
        simple = PipelineVariant(
            name="simple",
            num_features=5,
            num_rules=2,
            num_special_cases=0,
            roi=1.0,
        )
        complex_variant = PipelineVariant(
            name="complex",
            num_features=20,
            num_rules=10,
            num_special_cases=5,
            roi=1.0,
        )

        result = selector.select([complex_variant, simple])

        assert result.selected_name == "simple"
        assert result.all_actions["simple"] < result.all_actions["complex"]

    def test_select_with_performance_override(
        self, config_enabled: KenobaseConfig
    ) -> None:
        """Test performance overrides change selection."""
        selector = PipelineSelector(config_enabled)

        # Complex variant with better ROI after override should win
        simple = PipelineVariant(name="simple", num_features=5, roi=1.0)
        complex_variant = PipelineVariant(name="complex", num_features=15, roi=1.0)

        # Without override, simple wins
        result1 = selector.select([simple, complex_variant])
        assert result1.selected_name == "simple"

        # With override giving complex high ROI, complex might win
        result2 = selector.select(
            [simple, complex_variant],
            performance_overrides={"complex": 3.0},
        )
        # Complex should now win because high ROI compensates for complexity
        assert result2.selected_name == "complex"

    def test_select_disabled_returns_first(
        self, config_disabled: KenobaseConfig
    ) -> None:
        """Test disabled selector returns first variant."""
        selector = PipelineSelector(config_disabled)

        variants = [
            PipelineVariant(name="first", roi=0.5),
            PipelineVariant(name="second", roi=2.0),
        ]

        result = selector.select(variants)

        assert result.selected_name == "first"
        assert "disabled" in result.selection_reason.lower()

    def test_select_from_defaults(self, config_enabled: KenobaseConfig) -> None:
        """Test select_from_defaults uses DEFAULT_PIPELINE_VARIANTS."""
        selector = PipelineSelector(config_enabled)

        result = selector.select_from_defaults()

        assert result.selected_name in [v.name for v in DEFAULT_PIPELINE_VARIANTS]
        assert len(result.all_actions) == len(DEFAULT_PIPELINE_VARIANTS)

    def test_calculate_action(self, config_enabled: KenobaseConfig) -> None:
        """Test calculate_action returns correct value."""
        selector = PipelineSelector(config_enabled)
        variant = PipelineVariant(
            name="test",
            num_features=10,
            num_rules=5,
            num_special_cases=2,
            performance_variance=0.1,
            roi=1.5,
        )

        action = selector.calculate_action(variant)

        # complexity = 10*0.1 + 5*0.05 + 2*0.2 = 1.0 + 0.25 + 0.4 = 1.65
        # action = 1.65 + 0.1 - 1.5 = 0.25
        expected = 0.25
        assert abs(action - expected) < 0.001

    def test_compare_variants(self, config_enabled: KenobaseConfig) -> None:
        """Test compare_variants returns sorted list."""
        selector = PipelineSelector(config_enabled)

        variants = [
            PipelineVariant(name="high", num_features=20, roi=0.5),
            PipelineVariant(name="low", num_features=5, roi=1.5),
            PipelineVariant(name="medium", num_features=10, roi=1.0),
        ]

        ranking = selector.compare_variants(variants)

        assert len(ranking) == 3
        # Should be sorted by action (ascending)
        assert ranking[0][1] <= ranking[1][1] <= ranking[2][1]
        # First should be "low" (best action)
        assert ranking[0][0] == "low"


class TestSelectionResult:
    """Tests for SelectionResult dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        result = SelectionResult(
            selected_name="test",
            selected_action=0.5,
        )
        assert result.selected_name == "test"
        assert result.selected_action == 0.5
        assert result.all_actions == {}
        assert result.selection_reason == ""

    def test_all_values(self) -> None:
        """Test all values set correctly."""
        result = SelectionResult(
            selected_name="best",
            selected_action=0.3,
            all_actions={"best": 0.3, "other": 0.5},
            selection_reason="Lowest action",
        )
        assert result.selected_name == "best"
        assert result.all_actions["other"] == 0.5
        assert "Lowest" in result.selection_reason


class TestCreateVariantFromAnalysisConfig:
    """Tests for create_variant_from_analysis_config function."""

    def test_creates_variant_with_name(self) -> None:
        """Test variant is created with given name."""
        config = KenobaseConfig()
        variant = create_variant_from_analysis_config(
            name="from_config",
            config=config,
        )
        assert variant.name == "from_config"

    def test_counts_windows_as_features(self) -> None:
        """Test rolling windows are counted as features."""
        config = KenobaseConfig()
        # Default windows are [5, 10, 20, 50]
        variant = create_variant_from_analysis_config(
            name="test",
            config=config,
        )
        # 4 windows + 1 for 111 principle = 5
        assert variant.num_features >= 4

    def test_counts_analysis_rules(self) -> None:
        """Test analysis rules are counted."""
        config = KenobaseConfig()
        variant = create_variant_from_analysis_config(
            name="test",
            config=config,
        )
        # Should have rules for duo, trio, quatro, zehnergruppen
        assert variant.num_rules >= 1

    def test_counts_physics_special_cases(self) -> None:
        """Test physics special cases are counted."""
        config = KenobaseConfig()
        # enable_avalanche and anti_avalanche_mode are true by default
        variant = create_variant_from_analysis_config(
            name="test",
            config=config,
        )
        assert variant.num_special_cases >= 2

    def test_uses_measured_values(self) -> None:
        """Test measured ROI and variance are used."""
        config = KenobaseConfig()
        variant = create_variant_from_analysis_config(
            name="test",
            config=config,
            measured_roi=1.25,
            measured_variance=0.08,
        )
        assert variant.roi == 1.25
        assert variant.performance_variance == 0.08


class TestIntegrationWithModelLaws:
    """Integration tests with kenobase.physics.model_laws."""

    def test_action_matches_model_laws(self) -> None:
        """Test PipelineVariant action matches model_laws calculation."""
        variant = PipelineVariant(
            name="test",
            num_features=10,
            num_rules=5,
            num_special_cases=2,
            performance_variance=0.15,
            roi=1.2,
        )

        physics_config = variant.to_physics_config()
        expected_action = calculate_pipeline_action(physics_config)

        config = KenobaseConfig()
        selector = PipelineSelector(config)
        actual_action = selector.calculate_action(variant)

        assert abs(actual_action - expected_action) < 0.0001

    def test_selection_uses_model_laws_select(self) -> None:
        """Test selection result matches model_laws.select_best_pipeline."""
        from kenobase.physics.model_laws import select_best_pipeline

        variants = [
            PipelineVariant(name="a", num_features=5, roi=1.0),
            PipelineVariant(name="b", num_features=10, roi=1.0),
        ]

        physics_configs = [
            (v.name, v.to_physics_config()) for v in variants
        ]
        expected_name, expected_action = select_best_pipeline(physics_configs)

        config = KenobaseConfig()
        selector = PipelineSelector(config)
        result = selector.select(variants)

        assert result.selected_name == expected_name
        assert abs(result.selected_action - expected_action) < 0.0001
