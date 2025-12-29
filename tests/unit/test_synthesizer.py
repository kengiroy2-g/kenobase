"""Unit Tests fuer HypothesisSynthesizer und Recommendation Engine.

Tests fuer:
- Score-Extraktion aus HYP-Ergebnissen
- Kombination heterogener Scores
- Zehnergruppen-Filter
- Tier-Klassifikation
"""

import json
import tempfile
from pathlib import Path

import pytest

from kenobase.prediction.synthesizer import (
    HypothesisSynthesizer,
    NumberScore,
    HypothesisScore,
)
from kenobase.prediction.recommendation import (
    generate_recommendations,
    get_decade,
    apply_decade_filter,
    RecommendationTier,
)


# Test fixtures
@pytest.fixture
def mock_hyp010_data():
    """Mock HYP-010 (Odds Correlation) Daten."""
    return {
        "hypothesis": "HYP-010",
        "classification": {
            "safe_numbers": [1, 35, 36, 51, 52, 53, 56, 57],
            "popular_numbers": [2, 3, 4, 5, 7, 8, 9, 11, 12, 17, 23, 25, 33],
        },
        "correlation": {"is_significant": False},
    }


@pytest.fixture
def mock_hyp012_data():
    """Mock HYP-012 (Stake Correlation) Daten."""
    return {
        "hypothesis": "HYP-012",
        "classification": {
            "low_stake_numbers": [6, 14, 22, 24, 36, 42, 60, 64],
            "high_stake_numbers": [4, 11, 12, 13, 20, 28, 41, 44, 49, 52, 56, 58, 59, 66, 68],
        },
        "correlation": {
            "total_auszahlung": {"is_significant": True},
        },
    }


@pytest.fixture
def temp_results_dir(mock_hyp010_data, mock_hyp012_data):
    """Erstellt temporaeres Verzeichnis mit Mock-Ergebnissen."""
    with tempfile.TemporaryDirectory() as tmpdir:
        results_dir = Path(tmpdir)

        with open(results_dir / "hyp010_test.json", "w") as f:
            json.dump(mock_hyp010_data, f)

        with open(results_dir / "hyp012_test.json", "w") as f:
            json.dump(mock_hyp012_data, f)

        yield results_dir


class TestGetDecade:
    """Tests fuer Zehnergruppen-Berechnung."""

    def test_decade_1(self):
        """Zahlen 1-10 gehoeren zu Zehnergruppe 1."""
        assert get_decade(1) == 1
        assert get_decade(5) == 1
        assert get_decade(10) == 1

    def test_decade_2(self):
        """Zahlen 11-20 gehoeren zu Zehnergruppe 2."""
        assert get_decade(11) == 2
        assert get_decade(15) == 2
        assert get_decade(20) == 2

    def test_decade_7(self):
        """Zahlen 61-70 gehoeren zu Zehnergruppe 7."""
        assert get_decade(61) == 7
        assert get_decade(65) == 7
        assert get_decade(70) == 7


class TestSynthesizer:
    """Tests fuer HypothesisSynthesizer."""

    def test_load_results(self, temp_results_dir):
        """Test: Ergebnisse werden korrekt geladen."""
        synth = HypothesisSynthesizer(results_dir=str(temp_results_dir))
        loaded = synth.load_results()

        assert "HYP-010" in loaded
        assert "HYP-012" in loaded

    def test_synthesize_returns_all_numbers(self, temp_results_dir):
        """Test: Synthese liefert Scores fuer alle 70 Zahlen."""
        synth = HypothesisSynthesizer(results_dir=str(temp_results_dir))
        scores = synth.synthesize()

        assert len(scores) == 70
        assert 1 in scores
        assert 70 in scores

    def test_safe_number_high_score(self, temp_results_dir):
        """Test: Safe numbers haben hoeheren Score."""
        synth = HypothesisSynthesizer(results_dir=str(temp_results_dir))
        scores = synth.synthesize()

        # Zahl 1 ist safe in HYP-010
        safe_score = scores[1].combined_score
        # Zahl 2 ist popular in HYP-010
        popular_score = scores[2].combined_score

        assert safe_score > popular_score

    def test_tier_classification(self, temp_results_dir):
        """Test: Tier wird korrekt basierend auf Score gesetzt."""
        synth = HypothesisSynthesizer(results_dir=str(temp_results_dir))
        scores = synth.synthesize()

        for num, ns in scores.items():
            if ns.combined_score >= 0.7:
                assert ns.tier == "A"
            elif ns.combined_score >= 0.5:
                assert ns.tier == "B"
            else:
                assert ns.tier == "C"

    def test_get_top_numbers(self, temp_results_dir):
        """Test: Top-N Zahlen sind absteigend sortiert."""
        synth = HypothesisSynthesizer(results_dir=str(temp_results_dir))
        top_10 = synth.get_top_numbers(10)

        assert len(top_10) == 10
        # Verifiziere absteigende Sortierung
        for i in range(len(top_10) - 1):
            assert top_10[i].combined_score >= top_10[i + 1].combined_score


class TestApplyDecadeFilter:
    """Tests fuer Zehnergruppen-Filter."""

    def test_filter_limits_per_decade(self):
        """Test: Filter begrenzt Zahlen pro Zehnergruppe."""
        # Erstelle Mock NumberScores fuer Zahlen 1-5 (alle Zehnergruppe 1)
        scores = [
            NumberScore(number=i, combined_score=1.0 - i * 0.1, tier="A")
            for i in range(1, 6)
        ]

        filtered = apply_decade_filter(scores, max_per_decade=2)

        assert len(filtered) == 2
        assert filtered[0].number == 1  # Hoechster Score
        assert filtered[1].number == 2

    def test_filter_allows_multiple_decades(self):
        """Test: Filter erlaubt max_per_decade aus verschiedenen Gruppen."""
        scores = [
            NumberScore(number=1, combined_score=0.9, tier="A"),   # Decade 1
            NumberScore(number=11, combined_score=0.85, tier="A"), # Decade 2
            NumberScore(number=2, combined_score=0.8, tier="A"),   # Decade 1
            NumberScore(number=12, combined_score=0.75, tier="A"), # Decade 2
            NumberScore(number=3, combined_score=0.7, tier="A"),   # Decade 1 (wird gefiltert)
        ]

        filtered = apply_decade_filter(scores, max_per_decade=2)

        assert len(filtered) == 4
        assert 3 not in [ns.number for ns in filtered]


class TestGenerateRecommendations:
    """Tests fuer Empfehlungs-Generierung."""

    def test_recommendations_sorted_by_score(self, temp_results_dir):
        """Test: Empfehlungen sind nach Score sortiert."""
        synth = HypothesisSynthesizer(results_dir=str(temp_results_dir))
        scores = synth.synthesize()

        recs = generate_recommendations(scores, top_n=6)

        for i in range(len(recs) - 1):
            assert recs[i].combined_score >= recs[i + 1].combined_score

    def test_recommendations_have_tier(self, temp_results_dir):
        """Test: Empfehlungen haben korrektes Tier."""
        synth = HypothesisSynthesizer(results_dir=str(temp_results_dir))
        scores = synth.synthesize()

        recs = generate_recommendations(scores, top_n=6)

        for rec in recs:
            assert rec.tier in [RecommendationTier.A, RecommendationTier.B, RecommendationTier.C]

    def test_decade_filter_applied(self, temp_results_dir):
        """Test: Zehnergruppen-Filter wird angewendet."""
        synth = HypothesisSynthesizer(results_dir=str(temp_results_dir))
        scores = synth.synthesize()

        recs = generate_recommendations(scores, top_n=20, max_per_decade=2)

        # Zaehle Zahlen pro Zehnergruppe
        decade_counts: dict[int, int] = {}
        for rec in recs:
            decade = rec.decade
            decade_counts[decade] = decade_counts.get(decade, 0) + 1

        # Keine Zehnergruppe sollte mehr als 2 haben
        for decade, count in decade_counts.items():
            assert count <= 2, f"Decade {decade} has {count} numbers, expected <= 2"
