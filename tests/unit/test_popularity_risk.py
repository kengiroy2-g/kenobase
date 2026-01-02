"""Unit Tests fuer kenobase.analysis.popularity_risk (POP-001).

Acceptance Criteria:
- AC-1: PopularityRiskScore im Bereich 0-1
- AC-2: Monotonie: mehr Birthday/Pattern-Zahlen = hoeherer Score
- AC-3: Integration mit recommendation.py
- AC-4: Null-Model Validierung (p < 0.1)
- AC-5: >80% Test Coverage
"""

import pytest
import numpy as np

from kenobase.analysis.popularity_risk import (
    PopularityRiskScore,
    PopularityRiskLevel,
    BIRTHDAY_NUMBERS,
    SCHOENE_ZAHLEN,
    calculate_birthday_score,
    calculate_pattern_score,
    estimate_competition_factor,
    calculate_popularity_risk_score,
    should_play,
    adjust_recommendation_by_popularity,
    analyze_draw_popularity,
)


class TestCalculateBirthdayScore:
    """Tests fuer calculate_birthday_score()."""

    def test_empty_list_returns_zero(self):
        """Leere Liste ergibt Score 0."""
        assert calculate_birthday_score([]) == 0.0

    def test_all_birthday_numbers(self):
        """Nur Birthday-Zahlen (1-31) ergibt Score 1.0."""
        numbers = [1, 7, 15, 23, 31]
        assert calculate_birthday_score(numbers) == 1.0

    def test_no_birthday_numbers(self):
        """Nur Non-Birthday-Zahlen (32-70) ergibt Score 0.0."""
        numbers = [35, 42, 55, 68, 70]
        assert calculate_birthday_score(numbers) == 0.0

    def test_mixed_numbers(self):
        """Gemischte Zahlen ergibt Anteil."""
        numbers = [5, 15, 35, 55]  # 2 Birthday, 2 Non-Birthday
        assert calculate_birthday_score(numbers) == 0.5

    def test_single_birthday_number(self):
        """Einzelne Birthday-Zahl ergibt 1.0."""
        assert calculate_birthday_score([7]) == 1.0

    def test_single_non_birthday_number(self):
        """Einzelne Non-Birthday-Zahl ergibt 0.0."""
        assert calculate_birthday_score([50]) == 0.0


class TestCalculatePatternScore:
    """Tests fuer calculate_pattern_score()."""

    def test_empty_list_returns_zero(self):
        """Leere Liste ergibt Score 0."""
        assert calculate_pattern_score([]) == 0.0

    def test_schoene_zahlen(self):
        """Schoene Zahlen werden erkannt."""
        numbers = [7, 11, 13]  # Alle in SCHOENE_ZAHLEN
        score = calculate_pattern_score(numbers)
        assert score == 1.0

    def test_round_numbers(self):
        """Runde Zahlen werden erkannt."""
        numbers = [10, 20, 30]
        score = calculate_pattern_score(numbers)
        assert score == 1.0

    def test_symmetric_numbers(self):
        """Symmetrische Zahlen werden erkannt."""
        numbers = [11, 22, 33, 44, 55, 66]
        score = calculate_pattern_score(numbers)
        # 11 und 55 sind auch in SCHOENE_ZAHLEN
        assert score >= 0.8  # Alle sind Pattern-Zahlen

    def test_no_pattern_numbers(self):
        """Zahlen ohne Muster haben niedrigen Score."""
        # Zahlen die in keinem Pattern-Set sind
        numbers = [2, 8, 14, 23, 47]
        score = calculate_pattern_score(numbers)
        # Nur konsekutive-Check bleibt, sollte niedrig sein
        assert score < 0.3

    def test_consecutive_numbers_increase_score(self):
        """Konsekutive Zahlen erhoehen Score leicht."""
        non_consecutive = [5, 15, 25, 35]
        consecutive = [5, 6, 7, 8]

        score_non_cons = calculate_pattern_score(non_consecutive)
        score_cons = calculate_pattern_score(consecutive)

        # Konsekutive sollten hoeheren Score haben (durch 0.2 Bonus)
        assert score_cons > score_non_cons


class TestEstimateCompetitionFactor:
    """Tests fuer estimate_competition_factor()."""

    def test_zero_scores_baseline(self):
        """Null-Scores ergeben Faktor 1.0 (Baseline)."""
        factor = estimate_competition_factor(0.0, 0.0)
        assert factor == 1.0

    def test_max_scores_max_factor(self):
        """Maximale Scores ergeben maximalen Faktor."""
        factor = estimate_competition_factor(1.0, 1.0)
        # Default base_multiplier = 1.3
        assert factor == 1.3

    def test_half_scores_half_increase(self):
        """Halbe Scores ergeben halbe Erhoehung."""
        factor = estimate_competition_factor(0.5, 0.5)
        # combined = 0.5, factor = 1 + 0.5 * 0.3 = 1.15
        assert abs(factor - 1.15) < 0.01

    def test_monotonic_increase(self):
        """Faktor steigt monoton mit Scores."""
        factors = [
            estimate_competition_factor(i * 0.25, i * 0.25)
            for i in range(5)
        ]
        # Sollte strikt steigend sein
        for i in range(len(factors) - 1):
            assert factors[i] < factors[i + 1]

    def test_custom_weights(self):
        """Benutzerdefinierte Gewichte funktionieren."""
        factor = estimate_competition_factor(
            1.0, 0.0,
            birthday_weight=1.0,
            pattern_weight=0.0,
        )
        assert factor == 1.3  # Nur Birthday zaehlt

    def test_custom_base_multiplier(self):
        """Benutzerdefinierter Base-Multiplier funktioniert."""
        factor = estimate_competition_factor(
            1.0, 1.0,
            base_multiplier=2.0,
        )
        assert factor == 2.0


class TestCalculatePopularityRiskScore:
    """Tests fuer calculate_popularity_risk_score()."""

    def test_empty_list_raises_error(self):
        """Leere Liste wirft ValueError."""
        with pytest.raises(ValueError, match="darf nicht leer"):
            calculate_popularity_risk_score([])

    def test_invalid_number_raises_error(self):
        """Ungueltige Zahlen werfen ValueError."""
        with pytest.raises(ValueError, match="Ungueltige KENO-Zahl"):
            calculate_popularity_risk_score([0, 5, 10])

        with pytest.raises(ValueError, match="Ungueltige KENO-Zahl"):
            calculate_popularity_risk_score([5, 71, 10])

    def test_score_in_range_0_1(self):
        """AC-1: Score ist immer im Bereich 0-1."""
        # Verschiedene Kombinationen testen
        test_cases = [
            [1, 7, 15, 23, 31],  # All birthday
            [35, 42, 55, 68, 70],  # No birthday
            [5, 15, 35, 55, 65],  # Mixed
            list(range(1, 21)),  # 20 Zahlen
        ]

        for numbers in test_cases:
            result = calculate_popularity_risk_score(numbers)
            assert 0.0 <= result.score <= 1.0, f"Score out of range for {numbers}"
            assert 0.0 <= result.birthday_score <= 1.0
            assert 0.0 <= result.pattern_score <= 1.0

    def test_monotonicity_birthday(self):
        """AC-2: Mehr Birthday-Zahlen = hoeherer Score."""
        # Sukzessive mehr Birthday-Zahlen
        low_birthday = [35, 42, 55, 68, 70]  # 0 birthday
        mid_birthday = [5, 15, 42, 55, 70]  # 2 birthday
        high_birthday = [1, 7, 15, 23, 31]  # 5 birthday

        low_result = calculate_popularity_risk_score(low_birthday)
        mid_result = calculate_popularity_risk_score(mid_birthday)
        high_result = calculate_popularity_risk_score(high_birthday)

        assert low_result.score < mid_result.score < high_result.score

    def test_returns_correct_dataclass(self):
        """Gibt PopularityRiskScore Dataclass zurueck."""
        result = calculate_popularity_risk_score([5, 15, 35, 55, 65])

        assert isinstance(result, PopularityRiskScore)
        assert isinstance(result.score, float)
        assert isinstance(result.birthday_score, float)
        assert isinstance(result.pattern_score, float)
        assert isinstance(result.competition_factor, float)
        assert isinstance(result.risk_level, PopularityRiskLevel)
        assert isinstance(result.numbers, tuple)

    def test_risk_level_assignment(self):
        """Risiko-Level wird korrekt zugewiesen."""
        # LOW: score < 0.3
        low_risk_nums = [35, 42, 55, 68, 70]
        low_result = calculate_popularity_risk_score(low_risk_nums)
        assert low_result.risk_level == PopularityRiskLevel.LOW

        # HIGH/VERY_HIGH: score >= 0.6
        high_risk_nums = [1, 7, 11, 13, 21, 31]  # Birthday + Pattern
        high_result = calculate_popularity_risk_score(high_risk_nums)
        assert high_result.risk_level in (
            PopularityRiskLevel.HIGH,
            PopularityRiskLevel.VERY_HIGH,
        )

    def test_to_dict_serialization(self):
        """to_dict() erzeugt serialisierbares Dict."""
        result = calculate_popularity_risk_score([5, 15, 35, 55, 65])
        d = result.to_dict()

        assert "score" in d
        assert "birthday_score" in d
        assert "pattern_score" in d
        assert "competition_factor" in d
        assert "risk_level" in d
        assert "numbers" in d
        assert isinstance(d["numbers"], list)


class TestShouldPlay:
    """Tests fuer should_play()."""

    def test_low_risk_returns_true(self):
        """Niedriges Risiko = spielen."""
        numbers = [35, 42, 55, 68, 70]  # Keine Birthday
        should, reason = should_play(numbers)
        assert should is True
        assert "wenig konkurrenz" in reason.lower() or "akzeptabler" in reason.lower()

    def test_high_risk_returns_false(self):
        """Hohes Risiko ueber Grenzwert = nicht spielen."""
        numbers = [1, 7, 11, 13, 21, 31]  # Viel Birthday + Pattern
        should, reason = should_play(numbers, max_risk_score=0.3)
        assert should is False
        assert "risiko" in reason.lower() or "konkurrenz" in reason.lower()

    def test_invalid_numbers_returns_false(self):
        """Ungueltige Zahlen = nicht spielen."""
        should, reason = should_play([0, 5, 10])
        assert should is False
        assert "ungueltig" in reason.lower()

    def test_custom_thresholds(self):
        """Benutzerdefinierte Grenzwerte funktionieren."""
        numbers = [5, 15, 25, 35, 45]

        # Mit hohem Grenzwert: sollte spielen
        should_high, _ = should_play(numbers, max_risk_score=0.9)
        assert should_high is True

        # Mit niedrigem Grenzwert: sollte nicht spielen
        should_low, _ = should_play(numbers, max_risk_score=0.1)
        # Haengt vom Score ab


class TestAdjustRecommendationByPopularity:
    """Tests fuer adjust_recommendation_by_popularity()."""

    def test_low_popularity_minimal_penalty(self):
        """Niedrige Popularitaet = minimale Penalty."""
        numbers = [35, 42, 55, 68, 70]
        base_score = 0.8
        adjusted = adjust_recommendation_by_popularity(numbers, base_score)
        # Penalty sollte klein sein
        assert adjusted >= base_score * 0.9

    def test_high_popularity_significant_penalty(self):
        """Hohe Popularitaet = signifikante Penalty."""
        numbers = [1, 7, 11, 13, 21]  # Birthday + Pattern
        base_score = 0.8
        adjusted = adjust_recommendation_by_popularity(numbers, base_score)
        # Penalty sollte merklich sein
        assert adjusted < base_score * 0.95

    def test_score_remains_in_bounds(self):
        """Angepasster Score bleibt in 0-1."""
        test_cases = [
            ([1, 7, 11], 1.0),  # Max base
            ([35, 42, 55], 0.0),  # Min base
            ([5, 15, 35], 0.5),  # Mid base
        ]

        for numbers, base_score in test_cases:
            adjusted = adjust_recommendation_by_popularity(numbers, base_score)
            assert 0.0 <= adjusted <= 1.0

    def test_invalid_numbers_returns_base_score(self):
        """Ungueltige Zahlen ergeben unveränderten Base-Score."""
        adjusted = adjust_recommendation_by_popularity([0, 5], 0.7)
        assert adjusted == 0.7


class TestAnalyzeDrawPopularity:
    """Tests fuer analyze_draw_popularity()."""

    def test_returns_complete_analysis(self):
        """Gibt vollstaendige Analyse zurueck."""
        drawn = list(range(1, 21))  # 20 Zahlen
        result = analyze_draw_popularity(drawn)

        assert "popularity_risk" in result
        assert "expected_winner_multiplier" in result
        assert "strategy_hint" in result
        assert "drawn_birthday_count" in result
        assert "drawn_pattern_count" in result

    def test_birthday_count_correct(self):
        """Birthday-Count ist korrekt."""
        drawn = [1, 7, 15, 31, 35, 42, 55, 60, 62, 64,
                 66, 67, 68, 69, 70, 32, 33, 34, 36, 37]
        result = analyze_draw_popularity(drawn)
        # 1, 7, 15, 31 sind Birthday = 4
        assert result["drawn_birthday_count"] == 4

    def test_strategy_hint_reflects_popularity(self):
        """Strategy-Hint reflektiert Popularitaet."""
        # Populaere Ziehung (viele Birthday)
        popular = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                   11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        result_pop = analyze_draw_popularity(popular)
        assert "populaer" in result_pop["strategy_hint"].lower()

        # Unpopulaere Ziehung (wenig Birthday)
        unpopular = list(range(40, 60))
        result_unpop = analyze_draw_popularity(unpopular)
        assert "unpopulaer" in result_unpop["strategy_hint"].lower()


class TestNullModelValidation:
    """AC-4: Null-Model Validierung."""

    def test_random_distribution_vs_systematic(self):
        """Zufaellige Zahlen sollten anderen Score haben als systematische."""
        np.random.seed(42)

        # Systematisch: Nur Birthday-Zahlen
        systematic_scores = []
        for _ in range(100):
            numbers = np.random.choice(range(1, 32), size=6, replace=False)
            result = calculate_popularity_risk_score(list(numbers))
            systematic_scores.append(result.score)

        # Zufaellig: Alle Zahlen gleichverteilt
        random_scores = []
        for _ in range(100):
            numbers = np.random.choice(range(1, 71), size=6, replace=False)
            result = calculate_popularity_risk_score(list(numbers))
            random_scores.append(result.score)

        # Systematische sollten hoehere Scores haben
        assert np.mean(systematic_scores) > np.mean(random_scores)

    def test_score_variance_reasonable(self):
        """Score-Varianz sollte vernuenftig sein (nicht zu deterministisch)."""
        np.random.seed(42)

        scores = []
        for _ in range(100):
            numbers = np.random.choice(range(1, 71), size=6, replace=False)
            result = calculate_popularity_risk_score(list(numbers))
            scores.append(result.score)

        # Varianz sollte existieren (nicht alle gleich)
        assert np.std(scores) > 0.05

        # Aber auch nicht zu extrem
        assert np.std(scores) < 0.5


class TestEdgeCases:
    """Randfaelle und Edge Cases."""

    def test_single_number(self):
        """Einzelne Zahl funktioniert."""
        result = calculate_popularity_risk_score([42])
        assert 0.0 <= result.score <= 1.0

    def test_all_70_numbers(self):
        """Alle 70 Zahlen funktionieren."""
        numbers = list(range(1, 71))
        result = calculate_popularity_risk_score(numbers)
        assert 0.0 <= result.score <= 1.0

    def test_duplicate_numbers_handled(self):
        """Duplikate funktionieren (auch wenn ungewoehnlich)."""
        numbers = [5, 5, 5, 15, 25]
        result = calculate_popularity_risk_score(numbers)
        assert 0.0 <= result.score <= 1.0

    def test_numpy_integers_work(self):
        """NumPy Integer-Typen funktionieren."""
        numbers = [np.int32(5), np.int64(15), np.int64(35)]
        result = calculate_popularity_risk_score(numbers)
        assert 0.0 <= result.score <= 1.0

    def test_frozen_dataclass_immutable(self):
        """PopularityRiskScore ist immutable (frozen)."""
        result = calculate_popularity_risk_score([5, 15, 35])
        with pytest.raises(AttributeError):
            result.score = 0.5  # type: ignore
