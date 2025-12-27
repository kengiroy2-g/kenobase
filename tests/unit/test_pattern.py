"""Unit-Tests fuer kenobase.analysis.pattern.

Diese Tests verifizieren den BUG-FIX fuer die exklusive elif-Kette
aus V9:130-135. Die korrigierte Implementierung extrahiert ALLE
Sub-Kombinationen statt nur die groesste.

Mathematische Grundlage:
- 4 Treffer: C(4,4) + C(4,3) + C(4,2) = 1 + 4 + 6 = 11 Muster
- 3 Treffer: C(3,3) + C(3,2) = 1 + 3 = 4 Muster
- 2 Treffer: C(2,2) = 1 Muster
- 1 Treffer: 0 Muster (min. 2 fuer Duo)
- 0 Treffer: 0 Muster
"""

from datetime import datetime

import pytest

from kenobase.analysis.pattern import (
    PatternResult,
    aggregate_patterns,
    extract_patterns,
    extract_patterns_from_draws,
)
from kenobase.core.data_loader import DrawResult, GameType


# ============================================================================
# Test: extract_patterns - Core BUG-FIX Verification
# ============================================================================


class TestExtractPatterns:
    """Tests fuer extract_patterns Funktion."""

    def test_four_matches_extracts_all_subpatterns(self) -> None:
        """BUG-FIX: 4 Treffer muessen 11 Muster erzeugen (1 quatro + 4 trios + 6 duos).

        Dies ist der Kern-Test fuer den Bug-Fix. V9 extrahierte nur 1 Muster.
        """
        combination = [1, 5, 12, 23, 34, 45]
        draw_numbers = [1, 5, 12, 23, 7, 9, 14, 18, 22, 28,
                        33, 41, 48, 52, 55, 61, 64, 67, 69, 70]

        result = extract_patterns(combination, draw_numbers)

        assert result.match_count == 4
        assert result.matched_numbers == frozenset({1, 5, 12, 23})

        # C(4,4) = 1 quatro
        assert len(result.quatros) == 1
        assert result.quatros[0] == (1, 5, 12, 23)

        # C(4,3) = 4 trios
        assert len(result.trios) == 4
        expected_trios = {(1, 5, 12), (1, 5, 23), (1, 12, 23), (5, 12, 23)}
        assert set(result.trios) == expected_trios

        # C(4,2) = 6 duos
        assert len(result.duos) == 6
        expected_duos = {(1, 5), (1, 12), (1, 23), (5, 12), (5, 23), (12, 23)}
        assert set(result.duos) == expected_duos

        # Total: 1 + 4 + 6 = 11
        assert result.total_patterns == 11

    def test_three_matches_extracts_all_subpatterns(self) -> None:
        """BUG-FIX: 3 Treffer muessen 4 Muster erzeugen (1 trio + 3 duos).

        V9 extrahierte nur 1 Muster.
        """
        combination = [10, 20, 30, 40, 50, 60]
        draw_numbers = [10, 20, 30, 1, 2, 3, 4, 5, 6, 7,
                        8, 9, 11, 12, 13, 14, 15, 16, 17, 18]

        result = extract_patterns(combination, draw_numbers)

        assert result.match_count == 3
        assert result.matched_numbers == frozenset({10, 20, 30})

        # Keine quatros bei 3 Treffern
        assert len(result.quatros) == 0

        # C(3,3) = 1 trio
        assert len(result.trios) == 1
        assert result.trios[0] == (10, 20, 30)

        # C(3,2) = 3 duos
        assert len(result.duos) == 3
        expected_duos = {(10, 20), (10, 30), (20, 30)}
        assert set(result.duos) == expected_duos

        # Total: 0 + 1 + 3 = 4
        assert result.total_patterns == 4

    def test_two_matches_extracts_one_duo(self) -> None:
        """2 Treffer erzeugen genau 1 Duo."""
        combination = [7, 14, 21, 28, 35, 42]
        draw_numbers = [7, 14, 1, 2, 3, 4, 5, 6, 8, 9,
                        10, 11, 12, 13, 15, 16, 17, 18, 19, 20]

        result = extract_patterns(combination, draw_numbers)

        assert result.match_count == 2
        assert result.matched_numbers == frozenset({7, 14})
        assert len(result.quatros) == 0
        assert len(result.trios) == 0
        assert len(result.duos) == 1
        assert result.duos[0] == (7, 14)
        assert result.total_patterns == 1

    def test_one_match_extracts_no_patterns(self) -> None:
        """1 Treffer erzeugt keine Muster (min. 2 fuer Duo)."""
        combination = [1, 2, 3, 4, 5, 6]
        draw_numbers = [1, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                        19, 20, 21, 22, 23, 24, 25, 26, 27, 28]

        result = extract_patterns(combination, draw_numbers)

        assert result.match_count == 1
        assert result.matched_numbers == frozenset({1})
        assert len(result.quatros) == 0
        assert len(result.trios) == 0
        assert len(result.duos) == 0
        assert result.total_patterns == 0

    def test_zero_matches_extracts_no_patterns(self) -> None:
        """0 Treffer erzeugen keine Muster."""
        combination = [1, 2, 3, 4, 5, 6]
        draw_numbers = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                        20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

        result = extract_patterns(combination, draw_numbers)

        assert result.match_count == 0
        assert result.matched_numbers == frozenset()
        assert len(result.quatros) == 0
        assert len(result.trios) == 0
        assert len(result.duos) == 0
        assert result.total_patterns == 0

    def test_five_matches_extracts_correctly(self) -> None:
        """5 Treffer: C(5,4)=5 quatros + C(5,3)=10 trios + C(5,2)=10 duos = 25."""
        combination = [1, 2, 3, 4, 5, 6]
        draw_numbers = [1, 2, 3, 4, 5, 10, 11, 12, 13, 14,
                        15, 16, 17, 18, 19, 20, 21, 22, 23, 24]

        result = extract_patterns(combination, draw_numbers)

        assert result.match_count == 5
        assert result.matched_numbers == frozenset({1, 2, 3, 4, 5})

        # C(5,4) = 5 quatros
        assert len(result.quatros) == 5

        # C(5,3) = 10 trios
        assert len(result.trios) == 10

        # C(5,2) = 10 duos
        assert len(result.duos) == 10

        # Total: 5 + 10 + 10 = 25
        assert result.total_patterns == 25

    def test_six_matches_full_hit(self) -> None:
        """6 Treffer (Volltreff): C(6,4)=15 + C(6,3)=20 + C(6,2)=15 = 50."""
        combination = [1, 2, 3, 4, 5, 6]
        draw_numbers = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13,
                        14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

        result = extract_patterns(combination, draw_numbers)

        assert result.match_count == 6
        assert result.matched_numbers == frozenset({1, 2, 3, 4, 5, 6})

        # C(6,4) = 15 quatros
        assert len(result.quatros) == 15

        # C(6,3) = 20 trios
        assert len(result.trios) == 20

        # C(6,2) = 15 duos
        assert len(result.duos) == 15

        # Total: 15 + 20 + 15 = 50
        assert result.total_patterns == 50

    def test_patterns_are_sorted(self) -> None:
        """Alle Muster-Tupel sollten sortiert sein."""
        combination = [50, 10, 30, 20, 40, 60]  # Unsortiert
        draw_numbers = [50, 10, 30, 20, 1, 2, 3, 4, 5, 6,
                        7, 8, 9, 11, 12, 13, 14, 15, 16, 17]

        result = extract_patterns(combination, draw_numbers)

        # Kombination sollte sortiert sein
        assert result.combination == (10, 20, 30, 40, 50, 60)

        # Alle Duos sortiert
        for duo in result.duos:
            assert duo == tuple(sorted(duo))

        # Alle Trios sortiert
        for trio in result.trios:
            assert trio == tuple(sorted(trio))

        # Quatro sortiert
        for quatro in result.quatros:
            assert quatro == tuple(sorted(quatro))

    def test_accepts_set_input(self) -> None:
        """Funktion akzeptiert auch Sets als Input."""
        combination = [1, 2, 3, 4, 5, 6]
        draw_numbers = {1, 2, 3, 10, 11, 12, 13, 14, 15, 16,
                        17, 18, 19, 20, 21, 22, 23, 24, 25, 26}

        result = extract_patterns(combination, draw_numbers)

        assert result.match_count == 3
        assert result.total_patterns == 4  # 1 trio + 3 duos


# ============================================================================
# Test: extract_patterns_from_draws
# ============================================================================


class TestExtractPatternsFromDraws:
    """Tests fuer extract_patterns_from_draws Funktion."""

    def test_filters_draws_with_less_than_two_matches(self) -> None:
        """Nur Ziehungen mit mindestens 2 Treffern werden inkludiert."""
        combination = [1, 2, 3, 4, 5, 6]
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 2, 10, 11, 12, 13, 14, 15, 16, 17,
                         18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2024, 1, 2),
                numbers=[1, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                         19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
                game_type=GameType.KENO,
            ),
            DrawResult(
                date=datetime(2024, 1, 3),
                numbers=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                         20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
                game_type=GameType.KENO,
            ),
        ]

        results = extract_patterns_from_draws(combination, draws)

        # Nur erste Ziehung hat >= 2 Treffer
        assert len(results) == 1
        assert results[0].match_count == 2

    def test_returns_empty_for_no_matches(self) -> None:
        """Leere Liste wenn keine Ziehung mindestens 2 Treffer hat."""
        combination = [1, 2, 3, 4, 5, 6]
        draws = [
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                         20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
                game_type=GameType.KENO,
            ),
        ]

        results = extract_patterns_from_draws(combination, draws)

        assert len(results) == 0

    def test_multiple_draws_with_varying_matches(self) -> None:
        """Mehrere Ziehungen mit verschiedener Anzahl Treffer."""
        combination = [1, 2, 3, 4, 5, 6]
        draws = [
            DrawResult(  # 4 Treffer
                date=datetime(2024, 1, 1),
                numbers=[1, 2, 3, 4, 10, 11, 12, 13, 14, 15,
                         16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                game_type=GameType.KENO,
            ),
            DrawResult(  # 2 Treffer
                date=datetime(2024, 1, 2),
                numbers=[1, 2, 10, 11, 12, 13, 14, 15, 16, 17,
                         18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
                game_type=GameType.KENO,
            ),
            DrawResult(  # 3 Treffer
                date=datetime(2024, 1, 3),
                numbers=[4, 5, 6, 10, 11, 12, 13, 14, 15, 16,
                         17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
                game_type=GameType.KENO,
            ),
        ]

        results = extract_patterns_from_draws(combination, draws)

        assert len(results) == 3

        # Verifiziere Treffer-Anzahlen
        match_counts = sorted([r.match_count for r in results])
        assert match_counts == [2, 3, 4]


# ============================================================================
# Test: aggregate_patterns
# ============================================================================


class TestAggregatePatterns:
    """Tests fuer aggregate_patterns Funktion."""

    def test_aggregates_pattern_frequencies(self) -> None:
        """Aggregiert Haeufigkeiten korrekt ueber mehrere Ergebnisse."""
        results = [
            PatternResult(
                combination=(1, 2, 3, 4, 5, 6),
                match_count=2,
                matched_numbers=frozenset({1, 2}),
                duos=[(1, 2)],
                trios=[],
                quatros=[],
            ),
            PatternResult(
                combination=(1, 2, 3, 4, 5, 6),
                match_count=2,
                matched_numbers=frozenset({1, 2}),
                duos=[(1, 2)],  # Same duo again
                trios=[],
                quatros=[],
            ),
            PatternResult(
                combination=(1, 2, 3, 4, 5, 6),
                match_count=3,
                matched_numbers=frozenset({1, 2, 3}),
                duos=[(1, 2), (1, 3), (2, 3)],
                trios=[(1, 2, 3)],
                quatros=[],
            ),
        ]

        aggregated = aggregate_patterns(results)

        # (1, 2) appears 3 times (2 + 1)
        assert aggregated["duos"][(1, 2)] == 3
        # (1, 3) and (2, 3) appear 1 time each
        assert aggregated["duos"][(1, 3)] == 1
        assert aggregated["duos"][(2, 3)] == 1
        # (1, 2, 3) trio appears 1 time
        assert aggregated["trios"][(1, 2, 3)] == 1
        # No quatros
        assert len(aggregated["quatros"]) == 0

    def test_empty_results_returns_empty_dicts(self) -> None:
        """Leere Eingabe ergibt leere Dictionaries."""
        aggregated = aggregate_patterns([])

        assert aggregated["duos"] == {}
        assert aggregated["trios"] == {}
        assert aggregated["quatros"] == {}


# ============================================================================
# Test: PatternResult dataclass
# ============================================================================


class TestPatternResult:
    """Tests fuer PatternResult Datenklasse."""

    def test_total_patterns_property(self) -> None:
        """total_patterns gibt korrekte Summe zurueck."""
        result = PatternResult(
            combination=(1, 2, 3, 4, 5, 6),
            match_count=4,
            matched_numbers=frozenset({1, 2, 3, 4}),
            duos=[(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)],
            trios=[(1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)],
            quatros=[(1, 2, 3, 4)],
        )

        assert result.total_patterns == 11  # 6 + 4 + 1

    def test_default_empty_lists(self) -> None:
        """Default-Werte sind leere Listen."""
        result = PatternResult(
            combination=(1, 2, 3, 4, 5, 6),
            match_count=0,
            matched_numbers=frozenset(),
        )

        assert result.duos == []
        assert result.trios == []
        assert result.quatros == []
        assert result.total_patterns == 0
