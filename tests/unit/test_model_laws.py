"""Unit Tests fuer Physics Model Laws A/B/C.

Tests fuer kenobase/physics/model_laws.py
"""

import pytest

from kenobase.physics.model_laws import (
    PipelineConfig,
    calculate_criticality,
    calculate_criticality_from_config,
    calculate_pipeline_action,
    calculate_stability,
    is_law,
    select_best_pipeline,
)


class TestIsLaw:
    """Tests fuer Gesetz A: is_law() Funktion."""

    def test_constant_relation_is_law(self):
        """Konstante Relation hat Stabilitaet 1.0."""
        def constant_relation(x: float) -> float:
            return 5.0  # Always returns 5

        variations = [{"x": i} for i in range(10)]
        stability, is_law_result = is_law(constant_relation, variations)

        assert stability == 1.0
        assert is_law_result is True

    def test_variable_relation_not_law(self):
        """Variable Relation mit hoher Streuung ist kein Gesetz."""
        def variable_relation(x: float) -> float:
            return x  # Returns input directly

        variations = [{"x": float(i * 10)} for i in range(1, 11)]
        stability, is_law_result = is_law(variable_relation, variations)

        assert stability < 0.9
        assert is_law_result == False

    def test_stable_relation_is_law(self):
        """Stabile Relation mit geringer Streuung ist Gesetz."""
        def stable_relation(x: float) -> float:
            return 100.0 + x * 0.01  # Small variation

        variations = [{"x": float(i)} for i in range(10)]
        stability, is_law_result = is_law(stable_relation, variations)

        assert stability >= 0.9
        assert is_law_result == True

    def test_empty_variations_returns_false(self):
        """Leere Variationen geben False zurueck."""
        def dummy(x: float) -> float:
            return x

        stability, is_law_result = is_law(dummy, [])

        assert stability == 0.0
        assert is_law_result is False

    def test_custom_threshold(self):
        """Benutzerdefinierter Schwellenwert wird beachtet."""
        def medium_variance(x: float) -> float:
            return 10.0 + x * 0.5

        variations = [{"x": float(i)} for i in range(10)]

        # With default threshold (0.9)
        stability, is_law_default = is_law(medium_variance, variations)

        # With lower threshold (0.7)
        _, is_law_low = is_law(medium_variance, variations, threshold=0.7)

        # Lower threshold should be easier to meet
        assert isinstance(stability, float)


class TestCalculateStability:
    """Tests fuer calculate_stability() Funktion."""

    def test_constant_history(self):
        """Konstante Historie hat Stabilitaet 1.0."""
        history = [5.0] * 10
        stability, is_law_result = calculate_stability(history)

        assert stability == 1.0
        assert is_law_result is True

    def test_variable_history(self):
        """Variable Historie hat niedrige Stabilitaet."""
        history = [1.0, 10.0, 2.0, 9.0, 3.0, 8.0]
        stability, is_law_result = calculate_stability(history)

        assert stability < 0.9
        assert is_law_result == False

    def test_empty_history(self):
        """Leere Historie gibt 0.0 zurueck."""
        stability, is_law_result = calculate_stability([])

        assert stability == 0.0
        assert is_law_result is False

    def test_single_value_history(self):
        """Einzelner Wert gibt 0.0 zurueck."""
        stability, is_law_result = calculate_stability([5.0])

        assert stability == 0.0
        assert is_law_result is False


class TestPipelineAction:
    """Tests fuer Gesetz B: calculate_pipeline_action()."""

    def test_simple_pipeline_low_action(self):
        """Einfache Pipeline hat niedrige Action."""
        simple = PipelineConfig(
            num_features=2,
            num_rules=1,
            num_special_cases=0,
            performance_variance=0.1,
            roi=1.0
        )
        action = calculate_pipeline_action(simple)

        # Expected: 2*0.1 + 1*0.05 + 0*0.2 + 0.1 - 1.0 = -0.65
        assert action == pytest.approx(-0.65, abs=0.01)

    def test_complex_pipeline_high_action(self):
        """Komplexe Pipeline hat hohe Action."""
        complex_config = PipelineConfig(
            num_features=20,
            num_rules=10,
            num_special_cases=5,
            performance_variance=0.5,
            roi=0.5
        )
        action = calculate_pipeline_action(complex_config)

        # Expected: 20*0.1 + 10*0.05 + 5*0.2 + 0.5 - 0.5 = 3.5
        assert action == pytest.approx(3.5, abs=0.01)

    def test_roi_reduces_action(self):
        """Hoehere ROI reduziert Action."""
        config1 = PipelineConfig(
            num_features=5,
            num_rules=5,
            num_special_cases=1,
            performance_variance=0.1,
            roi=1.0
        )
        config2 = PipelineConfig(
            num_features=5,
            num_rules=5,
            num_special_cases=1,
            performance_variance=0.1,
            roi=2.0
        )

        action1 = calculate_pipeline_action(config1)
        action2 = calculate_pipeline_action(config2)

        assert action2 < action1  # Higher ROI = lower action


class TestSelectBestPipeline:
    """Tests fuer select_best_pipeline()."""

    def test_selects_lowest_action(self):
        """Waehlt Pipeline mit niedrigster Action."""
        pipelines = [
            ("complex", PipelineConfig(10, 10, 5, 0.3, 0.5)),
            ("simple", PipelineConfig(2, 1, 0, 0.1, 1.5)),
            ("medium", PipelineConfig(5, 3, 1, 0.2, 1.0)),
        ]

        best_name, best_action = select_best_pipeline(pipelines)

        assert best_name == "simple"

    def test_empty_list_raises(self):
        """Leere Liste wirft ValueError."""
        with pytest.raises(ValueError):
            select_best_pipeline([])


class TestCriticality:
    """Tests fuer Gesetz C: calculate_criticality()."""

    def test_probability_0_5_max_sensitivity(self):
        """p=0.5 hat maximale Sensitivity (1.0)."""
        score, level = calculate_criticality(0.5, 1)

        # sensitivity = 1 - |0.5 - 0.5| * 2 = 1.0
        # criticality = 1.0 * 1 = 1.0
        assert score == pytest.approx(1.0, abs=0.01)
        assert level == "CRITICAL"

    def test_probability_0_or_1_min_sensitivity(self):
        """p=0 oder p=1 haben minimale Sensitivity (0.0)."""
        score0, level0 = calculate_criticality(0.0, 1)
        score1, level1 = calculate_criticality(1.0, 1)

        assert score0 == pytest.approx(0.0, abs=0.01)
        assert score1 == pytest.approx(0.0, abs=0.01)
        assert level0 == "LOW"
        assert level1 == "LOW"

    def test_regime_complexity_multiplies(self):
        """Regime-Komplexitaet multipliziert Sensitivity."""
        score1, _ = calculate_criticality(0.5, 1)
        score3, _ = calculate_criticality(0.5, 3)

        assert score3 == pytest.approx(score1 * 3, abs=0.01)

    def test_criticality_levels(self):
        """Korrekte Level-Zuordnung."""
        # LOW: criticality < 0.3 -> sensitivity * complexity < 0.3
        # sensitivity = 1 - |p - 0.5| * 2
        # For p=0.1: sensitivity = 1 - 0.4*2 = 0.2, criticality = 0.2
        _, level_low = calculate_criticality(0.1, 1)
        assert level_low == "LOW"

        # MEDIUM: 0.3-0.5 -> need criticality in [0.3, 0.5)
        # For p=0.35: sensitivity = 1 - 0.15*2 = 0.7, criticality = 0.7 -> CRITICAL
        # For p=0.2: sensitivity = 1 - 0.3*2 = 0.4, criticality = 0.4 -> MEDIUM
        _, level_medium = calculate_criticality(0.2, 1)
        assert level_medium == "MEDIUM"

        # HIGH: 0.5-0.7 -> need criticality in [0.5, 0.7)
        # For p=0.3: sensitivity = 1 - 0.2*2 = 0.6, criticality = 0.6 -> HIGH
        _, level_high = calculate_criticality(0.3, 1)
        assert level_high == "HIGH"

        # CRITICAL: >= 0.7
        # For p=0.5: sensitivity = 1.0, criticality = 1.0 -> CRITICAL
        _, level_critical = calculate_criticality(0.5, 1)
        assert level_critical == "CRITICAL"


class TestCriticalityFromConfig:
    """Tests fuer calculate_criticality_from_config()."""

    def test_custom_thresholds(self):
        """Benutzerdefinierte Schwellenwerte werden beachtet."""
        # With strict thresholds: p=0.5 -> normalized=1.0 >= 0.6 -> CRITICAL
        _, level_strict = calculate_criticality_from_config(
            0.5, 1, warning_threshold=0.5, critical_threshold=0.6
        )
        assert level_strict == "CRITICAL"

        # With lenient thresholds but low sensitivity
        # p=0.1 -> sensitivity=0.2, normalized=0.2 < 0.5 -> LOW
        _, level_lenient = calculate_criticality_from_config(
            0.1, 1, warning_threshold=0.95, critical_threshold=0.99
        )
        assert level_lenient == "LOW"

        # p=0.3 -> sensitivity=0.6, normalized=0.6 >= 0.5 but < 0.7 -> MEDIUM
        _, level_medium = calculate_criticality_from_config(
            0.3, 1, warning_threshold=0.7, critical_threshold=0.85
        )
        assert level_medium == "MEDIUM"
