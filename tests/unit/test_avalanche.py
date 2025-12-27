"""Unit Tests fuer Physics Avalanche Module.

Tests fuer kenobase/physics/avalanche.py
"""

import pytest

from kenobase.physics.avalanche import (
    THETA_MODERATE,
    THETA_SAFE,
    THETA_WARNING,
    AvalancheResult,
    AvalancheState,
    analyze_combination,
    calculate_expected_value,
    calculate_theta,
    get_avalanche_state,
    get_avalanche_state_with_thresholds,
    is_profitable,
    max_picks_for_theta,
)


class TestCalculateTheta:
    """Tests fuer calculate_theta() Funktion."""

    def test_theta_formula(self):
        """theta = 1 - p^n."""
        # 70% precision, 6 picks
        theta = calculate_theta(0.7, 6)
        expected = 1 - (0.7 ** 6)
        assert theta == pytest.approx(expected, abs=0.0001)

    def test_perfect_precision(self):
        """100% Precision gibt theta=0."""
        theta = calculate_theta(1.0, 10)
        assert theta == 0.0

    def test_zero_precision(self):
        """0% Precision gibt theta=1."""
        theta = calculate_theta(0.0, 5)
        assert theta == 1.0

    def test_zero_picks(self):
        """0 Picks gibt theta=0."""
        theta = calculate_theta(0.7, 0)
        assert theta == 0.0

    def test_single_pick(self):
        """1 Pick: theta = 1 - p."""
        theta = calculate_theta(0.8, 1)
        assert theta == pytest.approx(0.2, abs=0.0001)

    def test_six_picks_at_70_percent(self):
        """CLAUDE.md Beispiel: 6er-Kombi bei 70% = 0.88 (CRITICAL)."""
        theta = calculate_theta(0.7, 6)
        # 1 - 0.7^6 = 1 - 0.117649 = 0.882351
        assert theta == pytest.approx(0.882351, abs=0.001)
        assert theta >= 0.85  # Should be CRITICAL


class TestGetAvalancheState:
    """Tests fuer get_avalanche_state() Funktion."""

    def test_safe_state(self):
        """theta < 0.50 ist SAFE."""
        assert get_avalanche_state(0.0) == AvalancheState.SAFE
        assert get_avalanche_state(0.3) == AvalancheState.SAFE
        assert get_avalanche_state(0.49) == AvalancheState.SAFE

    def test_moderate_state(self):
        """0.50 <= theta < 0.75 ist MODERATE."""
        assert get_avalanche_state(0.50) == AvalancheState.MODERATE
        assert get_avalanche_state(0.6) == AvalancheState.MODERATE
        assert get_avalanche_state(0.74) == AvalancheState.MODERATE

    def test_warning_state(self):
        """0.75 <= theta < 0.85 ist WARNING."""
        assert get_avalanche_state(0.75) == AvalancheState.WARNING
        assert get_avalanche_state(0.8) == AvalancheState.WARNING
        assert get_avalanche_state(0.84) == AvalancheState.WARNING

    def test_critical_state(self):
        """theta >= 0.85 ist CRITICAL."""
        assert get_avalanche_state(0.85) == AvalancheState.CRITICAL
        assert get_avalanche_state(0.9) == AvalancheState.CRITICAL
        assert get_avalanche_state(1.0) == AvalancheState.CRITICAL

    def test_threshold_constants(self):
        """Konstanten haben korrekte Werte."""
        assert THETA_SAFE == 0.50
        assert THETA_MODERATE == 0.75
        assert THETA_WARNING == 0.85


class TestGetAvalancheStateWithThresholds:
    """Tests fuer get_avalanche_state_with_thresholds()."""

    def test_custom_thresholds(self):
        """Benutzerdefinierte Schwellenwerte funktionieren."""
        # Very strict thresholds
        state = get_avalanche_state_with_thresholds(
            0.3, safe_threshold=0.2, moderate_threshold=0.4, warning_threshold=0.5
        )
        assert state == AvalancheState.MODERATE

    def test_lenient_thresholds(self):
        """Lockere Schwellenwerte erlauben hoehere theta."""
        state = get_avalanche_state_with_thresholds(
            0.9, safe_threshold=0.95, moderate_threshold=0.97, warning_threshold=0.99
        )
        assert state == AvalancheState.SAFE


class TestIsProfitable:
    """Tests fuer is_profitable() Funktion."""

    def test_profitable_bet(self):
        """p * q > 1 ist profitabel."""
        # 60% * 2.0 = 1.2 > 1
        assert is_profitable(0.6, 2.0) is True

    def test_unprofitable_bet(self):
        """p * q < 1 ist nicht profitabel."""
        # 40% * 2.0 = 0.8 < 1
        assert is_profitable(0.4, 2.0) is False

    def test_break_even(self):
        """p * q = 1 ist nicht profitabel (strict >)."""
        # 50% * 2.0 = 1.0 = 1
        assert is_profitable(0.5, 2.0) is False

    def test_high_odds_compensate(self):
        """Hohe Quoten kompensieren niedrige Precision."""
        # 20% * 6.0 = 1.2 > 1
        assert is_profitable(0.2, 6.0) is True


class TestCalculateExpectedValue:
    """Tests fuer calculate_expected_value()."""

    def test_positive_ev(self):
        """Positiver EV bei profitabler Wette."""
        # EV = 1 * (0.6 * 2.0 - 1) = 0.2
        ev = calculate_expected_value(0.6, 2.0, stake=1.0)
        assert ev == pytest.approx(0.2, abs=0.01)

    def test_negative_ev(self):
        """Negativer EV bei unprofitabler Wette."""
        # EV = 1 * (0.4 * 2.0 - 1) = -0.2
        ev = calculate_expected_value(0.4, 2.0, stake=1.0)
        assert ev == pytest.approx(-0.2, abs=0.01)

    def test_stake_multiplier(self):
        """Stake multipliziert EV."""
        ev1 = calculate_expected_value(0.6, 2.0, stake=1.0)
        ev10 = calculate_expected_value(0.6, 2.0, stake=10.0)
        assert ev10 == pytest.approx(ev1 * 10, abs=0.01)


class TestAnalyzeCombination:
    """Tests fuer analyze_combination()."""

    def test_safe_combination(self):
        """Sichere Kombination mit niedrigem theta."""
        result = analyze_combination(0.9, 2, avg_odds=2.0)

        assert isinstance(result, AvalancheResult)
        assert result.theta == pytest.approx(1 - 0.9**2, abs=0.001)
        assert result.state == AvalancheState.SAFE
        assert result.is_safe_to_bet is True

    def test_critical_combination(self):
        """Kritische Kombination mit hohem theta."""
        result = analyze_combination(0.7, 6, avg_odds=2.0)

        assert result.theta >= 0.85
        assert result.state == AvalancheState.CRITICAL
        assert result.is_safe_to_bet is False


class TestMaxPicksForTheta:
    """Tests fuer max_picks_for_theta()."""

    def test_70_percent_precision(self):
        """Bei 70% Precision: max 3 Picks fuer theta <= 0.75."""
        max_n = max_picks_for_theta(0.7, max_theta=0.75)

        # Check: 0.7^3 = 0.343, theta = 0.657 <= 0.75 OK
        # Check: 0.7^4 = 0.2401, theta = 0.7599 > 0.75 NOT OK
        assert max_n == 3

    def test_high_precision_allows_more(self):
        """Hohe Precision erlaubt mehr Picks."""
        max_n_90 = max_picks_for_theta(0.9, max_theta=0.75)
        max_n_70 = max_picks_for_theta(0.7, max_theta=0.75)

        assert max_n_90 > max_n_70

    def test_zero_precision_returns_zero(self):
        """0% Precision gibt 0 Picks."""
        assert max_picks_for_theta(0.0, 0.5) == 0

    def test_perfect_precision_returns_large(self):
        """100% Precision gibt grosse Anzahl."""
        max_n = max_picks_for_theta(1.0, 0.5)
        assert max_n == 0  # Edge case: log(1.0) = 0


class TestAvalancheStateEnum:
    """Tests fuer AvalancheState Enum."""

    def test_enum_values(self):
        """Enum hat korrekte String-Werte."""
        assert AvalancheState.SAFE.value == "SAFE"
        assert AvalancheState.MODERATE.value == "MODERATE"
        assert AvalancheState.WARNING.value == "WARNING"
        assert AvalancheState.CRITICAL.value == "CRITICAL"

    def test_enum_is_string(self):
        """Enum erbt von str."""
        assert isinstance(AvalancheState.SAFE, str)
        assert AvalancheState.SAFE == "SAFE"
