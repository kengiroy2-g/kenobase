"""Tests fuer kenobase.analysis.regional_affinity."""

from __future__ import annotations

from datetime import datetime

import pytest

from kenobase.analysis.regional_affinity import (
    BUNDESLAND_POPULATION_SHARE,
    _chi2_p_value,
    analyze_regional_affinity,
    calculate_distribution_chi2,
    get_top_affinities,
)
from kenobase.core.data_loader import DrawResult, GameType


def _make_draw(numbers: list[int], region: str | None, day: int) -> DrawResult:
    """Helper zum Erstellen eines DrawResult mit Region."""
    metadata = {"region": region} if region else {}
    return DrawResult(
        date=datetime(2024, 1, day),
        numbers=numbers,
        game_type=GameType.KENO,
        metadata=metadata,
    )


def test_no_draws_returns_warning():
    """Leere Eingabe liefert Warnung und keine Ergebnisse."""
    analysis = analyze_regional_affinity([], numbers_per_draw=20)
    assert analysis.warnings
    assert analysis.n_draws_total == 0
    assert analysis.regions == []


def test_missing_region_metadata_skips_analysis():
    """Ohne Region-Metadaten wird Analyse uebersprungen."""
    draws = [_make_draw([1, 2, 3], None, 1)]
    analysis = analyze_regional_affinity(draws, numbers_per_draw=3)
    assert analysis.regions == []
    assert any("No region metadata" in w for w in analysis.warnings)


def test_insufficient_draws_skipped_region():
    """Regionen unter Minimum werden als skipped markiert."""
    draws = [_make_draw([1, 2, 3], "berlin", 1)]
    analysis = analyze_regional_affinity(
        draws,
        numbers_per_draw=3,
        min_draws_per_region=2,
        number_range=(1, 6),
    )
    assert "berlin" in analysis.skipped_regions
    assert analysis.regions == []


def test_affinity_computation_and_top_selection():
    """Berechnet Lift pro Region und liefert Top-Affinitaeten."""
    draws = [
        _make_draw([1, 2, 3], "berlin", 1),
        _make_draw([1, 2, 4], "berlin", 2),
        _make_draw([1, 5, 6], "bayern", 3),
        _make_draw([1, 5, 6], "bayern", 4),
    ]

    analysis = analyze_regional_affinity(
        draws,
        number_range=(1, 6),
        numbers_per_draw=3,
        min_draws_per_region=2,
        smoothing_alpha=0.0,
        z_threshold=0.5,
    )

    berlin = next(r for r in analysis.regions if r.region == "berlin")
    stat_two = next(s for s in berlin.stats if s.number == 2)

    assert stat_two.relative_frequency == pytest.approx(2 / 6)
    assert stat_two.lift > 1.5
    assert stat_two.is_significant

    top = get_top_affinities(analysis, region="berlin", n=1, significance_only=True)
    assert top
    assert top[0].number == 2


# --- Tests for Chi-Quadrat distribution test ---


def _make_bundesland_draw(bundesland: str) -> DrawResult:
    """Create DrawResult with bundesland in metadata."""
    return DrawResult(
        date=datetime.now(),
        numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        game_type=GameType.KENO,
        metadata={"bundesland": bundesland},
    )


class TestCalculateDistributionChi2:
    """Tests for calculate_distribution_chi2 function."""

    def test_empty_draws(self):
        """Empty draws should return zero statistics."""
        result = calculate_distribution_chi2([])
        assert result.chi2_statistic == 0.0
        assert result.p_value == 1.0
        assert result.n_total == 0

    def test_single_region_not_testable(self):
        """Single region cannot be tested (df=0)."""
        draws = [_make_bundesland_draw("bayern") for _ in range(10)]
        result = calculate_distribution_chi2(draws)
        assert result.n_total == 10
        assert result.degrees_of_freedom == 0

    def test_multiple_regions(self):
        """Test with multiple regions."""
        draws = (
            [_make_bundesland_draw("nordrhein-westfalen") for _ in range(20)]
            + [_make_bundesland_draw("bayern") for _ in range(15)]
            + [_make_bundesland_draw("hessen") for _ in range(10)]
        )
        result = calculate_distribution_chi2(draws)
        assert result.n_total == 45
        assert result.degrees_of_freedom >= 1

    def test_population_shares_valid(self):
        """Population shares should sum to ~1.0."""
        total = sum(BUNDESLAND_POPULATION_SHARE.values())
        assert 0.99 <= total <= 1.01

    def test_all_bundeslaender_defined(self):
        """All 16 Bundeslaender should be defined."""
        assert len(BUNDESLAND_POPULATION_SHARE) == 16

    def test_result_serialization(self):
        """Result should serialize to dict."""
        draws = [
            _make_bundesland_draw("bayern"),
            _make_bundesland_draw("berlin"),
        ]
        result = calculate_distribution_chi2(draws, min_expected=0.1)
        d = result.to_dict()
        assert "chi2_statistic" in d
        assert "p_value" in d
        assert "observed" in d


class TestChi2PValue:
    """Tests for chi-square p-value approximation."""

    def test_chi2_zero_gives_p_one(self):
        """Chi2=0 should give p=1."""
        assert _chi2_p_value(0.0, 5) == 1.0

    def test_known_critical_values(self):
        """Test against known chi2 critical values at p=0.05."""
        # df=1, chi2=3.84 -> p~0.05
        p = _chi2_p_value(3.84, 1)
        assert 0.04 <= p <= 0.06

        # df=5, chi2=11.07 -> p~0.05
        p = _chi2_p_value(11.07, 5)
        assert 0.04 <= p <= 0.06

    def test_large_chi2_small_p(self):
        """Large chi2 should give very small p."""
        p = _chi2_p_value(100.0, 5)
        assert p < 0.0001
