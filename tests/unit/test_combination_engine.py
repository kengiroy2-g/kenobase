"""Unit tests for CombinationEngine.

Tests fuer kenobase/core/combination_engine.py.
Prueft Kombinations-Generierung mit Filtern.
"""

from __future__ import annotations

import pytest

from kenobase.core.combination_engine import CombinationEngine, CombinationResult
from kenobase.core.config import KenobaseConfig


class TestCombinationResultDataclass:
    """Tests fuer CombinationResult Dataclass."""

    def test_creation_basic(self):
        """Test grundlegende Erstellung."""
        result = CombinationResult(numbers=(1, 2, 3), sum_value=6)

        assert result.numbers == (1, 2, 3)
        assert result.sum_value == 6

    def test_decade_distribution_auto_calculated(self):
        """Test automatische Berechnung der Dekaden-Verteilung."""
        # 1,2 in Dekade 0; 11,12 in Dekade 1; 21 in Dekade 2
        result = CombinationResult(numbers=(1, 2, 11, 12, 21), sum_value=47)

        assert result.decade_distribution == {0: 2, 1: 2, 2: 1}

    def test_decade_distribution_single_decade(self):
        """Test Verteilung wenn alle in einer Dekade."""
        result = CombinationResult(numbers=(1, 2, 3, 4, 5, 6), sum_value=21)

        assert result.decade_distribution == {0: 6}

    def test_decade_edge_cases(self):
        """Test Dekaden-Grenzen: 10 ist Dekade 0, 11 ist Dekade 1."""
        result = CombinationResult(numbers=(10, 11), sum_value=21)

        # 10: (10-1)//10 = 0
        # 11: (11-1)//10 = 1
        assert result.decade_distribution == {0: 1, 1: 1}

    def test_immutability(self):
        """Test dass CombinationResult immutable ist (frozen=True)."""
        result = CombinationResult(numbers=(1, 2, 3), sum_value=6)

        with pytest.raises(AttributeError):
            result.numbers = (4, 5, 6)


class TestCombinationEngineInit:
    """Tests fuer CombinationEngine Initialisierung."""

    def test_default_parameters(self):
        """Test Standard-Parameter."""
        pool = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
        engine = CombinationEngine(pool=pool)

        assert engine.combination_size == 6
        assert engine.max_per_decade == 3

    def test_custom_parameters(self):
        """Test benutzerdefinierte Parameter."""
        pool = {1, 2, 3, 4, 5}
        engine = CombinationEngine(
            pool=pool,
            combination_size=3,
            max_per_decade=2,
            min_sum=5,
            max_sum=10,
        )

        assert engine.combination_size == 3
        assert engine.max_per_decade == 2
        assert engine.min_sum == 5
        assert engine.max_sum == 10

    def test_empty_pool_raises(self):
        """Test ValueError bei leerem Pool."""
        with pytest.raises(ValueError, match="Pool cannot be empty"):
            CombinationEngine(pool=set())

    def test_pool_too_small_raises(self):
        """Test ValueError wenn Pool kleiner als combination_size."""
        pool = {1, 2, 3}
        with pytest.raises(ValueError, match="Pool size.*must be >= combination_size"):
            CombinationEngine(pool=pool, combination_size=6)

    def test_invalid_combination_size_raises(self):
        """Test ValueError bei combination_size < 1."""
        pool = {1, 2, 3}
        with pytest.raises(ValueError, match="combination_size must be >= 1"):
            CombinationEngine(pool=pool, combination_size=0)

    def test_invalid_max_per_decade_raises(self):
        """Test ValueError bei max_per_decade < 1."""
        pool = {1, 2, 3, 4, 5, 6}
        with pytest.raises(ValueError, match="max_per_decade must be >= 1"):
            CombinationEngine(pool=pool, combination_size=3, max_per_decade=0)


class TestCombinationEngineGenerate:
    """Tests fuer generate() Methode."""

    def test_generate_returns_iterator(self):
        """Test dass generate() einen Iterator zurueckgibt."""
        pool = {1, 2, 3}
        engine = CombinationEngine(pool=pool, combination_size=2, max_per_decade=3)

        result = engine.generate()

        # Iterator-Check
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_generate_yields_combination_results(self):
        """Test dass generate() CombinationResult-Objekte liefert."""
        pool = {1, 2, 3}
        engine = CombinationEngine(pool=pool, combination_size=2, max_per_decade=3)

        results = list(engine.generate())

        assert all(isinstance(r, CombinationResult) for r in results)

    def test_generate_correct_count(self):
        """Test korrekte Anzahl Kombinationen (3 choose 2 = 3)."""
        pool = {1, 2, 3}
        engine = CombinationEngine(pool=pool, combination_size=2, max_per_decade=3)

        results = list(engine.generate())

        assert len(results) == 3  # (1,2), (1,3), (2,3)

    def test_generate_sorted_numbers(self):
        """Test dass Zahlen in jedem Ergebnis sortiert sind."""
        pool = {5, 3, 1, 4, 2}
        engine = CombinationEngine(pool=pool, combination_size=3, max_per_decade=5)

        for result in engine.generate():
            assert result.numbers == tuple(sorted(result.numbers))

    def test_generate_correct_sum(self):
        """Test korrekte Summenberechnung."""
        pool = {1, 2, 3}
        engine = CombinationEngine(pool=pool, combination_size=2, max_per_decade=3)

        results = list(engine.generate())

        for result in results:
            assert result.sum_value == sum(result.numbers)


class TestDecadeFilter:
    """Tests fuer Zehnergruppen-Filter."""

    def test_decade_filter_allows_valid(self):
        """Test dass gueltige Kombinationen durchgelassen werden."""
        # Pool mit max 2 pro Dekade
        pool = {1, 2, 11, 12, 21, 22}
        engine = CombinationEngine(
            pool=pool, combination_size=4, max_per_decade=2
        )

        results = list(engine.generate())

        # Jede Kombination sollte max 2 Zahlen pro Dekade haben
        for result in results:
            for count in result.decade_distribution.values():
                assert count <= 2

    def test_decade_filter_blocks_invalid(self):
        """Test dass ungueltige Kombinationen gefiltert werden."""
        # Pool mit 4 Zahlen in Dekade 0, aber max_per_decade=2
        pool = {1, 2, 3, 4}
        engine = CombinationEngine(
            pool=pool, combination_size=3, max_per_decade=2
        )

        results = list(engine.generate())

        # Nur Kombinationen mit max 2 Zahlen sollten durchkommen
        # Moeglich: (1,2,x) wobei x nicht existiert -> keine Kombis moeglich
        # (1,2,3), (1,2,4), (1,3,4), (2,3,4) - alle haben 3 in Dekade 0
        assert len(results) == 0

    def test_decade_filter_edge_at_boundary(self):
        """Test Dekaden-Grenze: 10 und 11."""
        pool = {9, 10, 11, 12}
        engine = CombinationEngine(
            pool=pool, combination_size=2, max_per_decade=1
        )

        results = list(engine.generate())

        # Gueltige Kombinationen: (9,11), (9,12), (10,11), (10,12)
        # Ungueltig: (9,10) - beide Dekade 0; (11,12) - beide Dekade 1
        assert len(results) == 4
        valid_combos = [(9, 11), (9, 12), (10, 11), (10, 12)]
        result_numbers = [r.numbers for r in results]
        for combo in valid_combos:
            assert combo in result_numbers

    def test_decade_definition_formula(self):
        """Test Dekaden-Formel: (n-1)//10."""
        # Dekade 0: 1-10, Dekade 1: 11-20, Dekade 6: 61-70
        test_cases = [
            (1, 0),
            (10, 0),
            (11, 1),
            (20, 1),
            (21, 2),
            (61, 6),
            (70, 6),
        ]
        for number, expected_decade in test_cases:
            calculated = (number - 1) // 10
            assert calculated == expected_decade, f"Zahl {number}: erwartet Dekade {expected_decade}, got {calculated}"


class TestSumFilter:
    """Tests fuer Summen-Filter."""

    def test_sum_filter_min_only(self):
        """Test Filter mit nur min_sum."""
        pool = {1, 2, 3, 4, 5}
        engine = CombinationEngine(
            pool=pool, combination_size=2, max_per_decade=5, min_sum=6
        )

        results = list(engine.generate())

        for result in results:
            assert result.sum_value >= 6

    def test_sum_filter_max_only(self):
        """Test Filter mit nur max_sum."""
        pool = {1, 2, 3, 4, 5}
        engine = CombinationEngine(
            pool=pool, combination_size=2, max_per_decade=5, max_sum=5
        )

        results = list(engine.generate())

        for result in results:
            assert result.sum_value <= 5

    def test_sum_filter_both_bounds(self):
        """Test Filter mit min_sum und max_sum."""
        pool = {1, 2, 3, 4, 5}
        engine = CombinationEngine(
            pool=pool, combination_size=2, max_per_decade=5, min_sum=4, max_sum=6
        )

        results = list(engine.generate())

        for result in results:
            assert 4 <= result.sum_value <= 6

    def test_sum_filter_no_matches(self):
        """Test wenn keine Kombination die Summen-Schwelle erfuellt."""
        pool = {1, 2, 3}  # Max Summe = 5
        engine = CombinationEngine(
            pool=pool, combination_size=2, max_per_decade=5, min_sum=100
        )

        results = list(engine.generate())

        assert len(results) == 0


class TestCombinedFilters:
    """Tests fuer kombinierte Filter."""

    def test_both_filters_applied(self):
        """Test dass beide Filter zusammen angewendet werden."""
        # Pool: Dekade 0 (1-10) und Dekade 1 (11-20)
        pool = {1, 2, 3, 11, 12, 13}
        engine = CombinationEngine(
            pool=pool,
            combination_size=3,
            max_per_decade=2,  # Max 2 pro Dekade
            min_sum=20,  # Min Summe 20
        )

        results = list(engine.generate())

        for result in results:
            # Dekaden-Check
            for count in result.decade_distribution.values():
                assert count <= 2
            # Summen-Check
            assert result.sum_value >= 20


class TestCountCombinations:
    """Tests fuer count_combinations() Methode."""

    def test_count_matches_list_length(self):
        """Test dass count_combinations() gleich len(list(generate()))."""
        pool = {1, 2, 3, 11, 12, 21}
        engine = CombinationEngine(pool=pool, combination_size=3, max_per_decade=2)

        count = engine.count_combinations()
        results = list(engine.generate())

        assert count == len(results)


class TestGetStatistics:
    """Tests fuer get_statistics() Methode."""

    def test_statistics_structure(self):
        """Test dass get_statistics() korrekte Struktur zurueckgibt."""
        pool = {1, 2, 11, 12, 21, 22}
        engine = CombinationEngine(
            pool=pool, combination_size=3, max_per_decade=2, min_sum=10, max_sum=50
        )

        stats = engine.get_statistics()

        assert "pool_size" in stats
        assert "combination_size" in stats
        assert "theoretical_max" in stats
        assert "max_per_decade" in stats
        assert "min_sum" in stats
        assert "max_sum" in stats
        assert "pool_decade_distribution" in stats

    def test_statistics_values(self):
        """Test korrekte Werte in Statistiken."""
        pool = {1, 2, 11, 12}
        engine = CombinationEngine(pool=pool, combination_size=2, max_per_decade=2)

        stats = engine.get_statistics()

        assert stats["pool_size"] == 4
        assert stats["combination_size"] == 2
        assert stats["theoretical_max"] == 6  # 4 choose 2
        assert stats["pool_decade_distribution"] == {0: 2, 1: 2}


class TestFromConfig:
    """Tests fuer from_config() Factory-Methode."""

    def test_from_config_uses_analysis_settings(self):
        """Test dass from_config() Werte aus Config liest."""
        config = KenobaseConfig()
        # Default: zehnergruppen_max_per_group = 3
        pool = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

        engine = CombinationEngine.from_config(pool=pool, config=config)

        assert engine.max_per_decade == 3  # From config.analysis
        assert engine.combination_size == 6  # Default 6er-Kombi

    def test_from_config_with_sum_overrides(self):
        """Test dass min_sum/max_sum Parameter ueberschreiben."""
        config = KenobaseConfig()
        pool = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

        engine = CombinationEngine.from_config(
            pool=pool, config=config, min_sum=100, max_sum=200
        )

        assert engine.min_sum == 100
        assert engine.max_sum == 200


class TestMemoryEfficiency:
    """Tests fuer Memory-Effizienz (Generator-Pattern)."""

    def test_generator_is_lazy(self):
        """Test dass Generator lazy evaluiert wird."""
        pool = set(range(1, 21))  # 20 Zahlen
        engine = CombinationEngine(pool=pool, combination_size=6, max_per_decade=3)

        gen = engine.generate()

        # Generator sollte noch nichts berechnet haben
        # Wir koennen nur testen dass wir schrittweise iterieren koennen
        first = next(gen)
        assert isinstance(first, CombinationResult)

        second = next(gen)
        assert isinstance(second, CombinationResult)
        assert first.numbers != second.numbers

    def test_large_pool_does_not_explode_memory(self):
        """Test dass grosse Pools nicht sofort Speicher allokieren."""
        # 40 Zahlen, 6er-Kombi -> 3.838.380 theoretische Kombinationen
        pool = set(range(1, 41))
        engine = CombinationEngine(pool=pool, combination_size=6, max_per_decade=2)

        gen = engine.generate()

        # Nur erste 10 abrufen, nicht alle
        for _ in range(10):
            result = next(gen)
            assert isinstance(result, CombinationResult)

        # Test bestanden wenn kein MemoryError


class TestEdgeCases:
    """Tests fuer Randfaelle."""

    def test_single_number_pool(self):
        """Test Pool mit nur einer Zahl."""
        pool = {42}
        engine = CombinationEngine(pool=pool, combination_size=1, max_per_decade=1)

        results = list(engine.generate())

        assert len(results) == 1
        assert results[0].numbers == (42,)

    def test_combination_size_equals_pool_size(self):
        """Test wenn combination_size == pool_size."""
        pool = {1, 2, 3}
        engine = CombinationEngine(pool=pool, combination_size=3, max_per_decade=3)

        results = list(engine.generate())

        assert len(results) == 1
        assert results[0].numbers == (1, 2, 3)

    def test_high_decade_numbers(self):
        """Test mit hohen Zahlen (Dekade 6 fuer KENO 61-70)."""
        pool = {61, 62, 63, 64, 65, 70}
        engine = CombinationEngine(pool=pool, combination_size=3, max_per_decade=2)

        results = list(engine.generate())

        # Alle Zahlen in Dekade 6, max 2 erlaubt
        # -> keine 3er-Kombi moeglich
        assert len(results) == 0
