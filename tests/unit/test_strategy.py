"""Unit-Tests fuer das Strategy-Pattern (TASK-P03).

Testet:
- BacktestStrategy ABC
- HotNumberStrategy
- ColdNumberStrategy
- RandomStrategy
- StrategyFactory

Gemaess CLAUDE.md Phase 5 Test-Strategie.
"""

from datetime import datetime, timedelta

import pytest

from kenobase.core.config import GameConfig, KenobaseConfig
from kenobase.core.data_loader import DrawResult, GameType
from kenobase.pipeline.strategy import (
    AntiClusterStrategy,
    BacktestStrategy,
    ColdNumberStrategy,
    CompositeStrategy,
    HotNumberAntiClusterStrategy,
    HotNumberStrategy,
    RandomStrategy,
    StrategyFactory,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def default_config() -> KenobaseConfig:
    """Standard-Konfiguration fuer Tests."""
    return KenobaseConfig()


@pytest.fixture
def keno_game_config() -> GameConfig:
    """KENO-spezifische Spielkonfiguration."""
    return GameConfig(
        name="KENO",
        numbers_range=(1, 70),
        numbers_to_draw=20,
        hot_threshold=0.37,
        cold_threshold=0.20,
    )


@pytest.fixture
def sample_draws_hot() -> list[DrawResult]:
    """Ziehungen mit klaren Hot-Numbers (1-10 erscheinen oft)."""
    base_date = datetime(2023, 1, 1)
    draws = []

    # 100 Ziehungen: 1-10 erscheinen in 70%, 11-20 in 30%
    for i in range(100):
        if i % 10 < 7:  # 70% - Hot numbers dominant
            numbers = list(range(1, 11)) + list(range(51, 61))
        else:  # 30% - Mixed
            numbers = list(range(11, 21)) + list(range(41, 51))

        draws.append(
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=numbers,
                game_type=GameType.KENO,
            )
        )
    return draws


@pytest.fixture
def uniform_draws() -> list[DrawResult]:
    """Ziehungen mit gleichmaessiger Verteilung."""
    base_date = datetime(2023, 1, 1)
    draws = []

    for i in range(100):
        # Shift numbers to create uniform distribution
        start = (i * 20) % 70 + 1
        numbers = [(start + j - 1) % 70 + 1 for j in range(20)]
        draws.append(
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=numbers,
                game_type=GameType.KENO,
            )
        )
    return draws


@pytest.fixture
def cluster_draws() -> list[DrawResult]:
    """Ziehungen mit Cluster-Mustern fuer Anti-Cluster Tests.

    Zahl 5 erscheint in den letzten 6 Ziehungen (Cluster aktiv).
    Zahl 10 erscheint in den letzten 3 Ziehungen (kein Cluster bei threshold=5).
    """
    base_date = datetime(2023, 1, 1)
    draws = []

    for i in range(20):
        # Base numbers (vary slightly)
        base_nums = list(range(21, 41))

        if i >= 14:  # Last 6 draws: 5 appears (cluster)
            base_nums[0] = 5
        if i >= 17:  # Last 3 draws: 10 appears (no cluster at threshold=5)
            base_nums[1] = 10

        draws.append(
            DrawResult(
                date=base_date + timedelta(days=i),
                numbers=base_nums,
                game_type=GameType.KENO,
            )
        )
    return draws


# =============================================================================
# Test BacktestStrategy ABC
# =============================================================================


class TestBacktestStrategyABC:
    """Tests fuer abstrakte Basisklasse."""

    def test_cannot_instantiate_abc(self, default_config: KenobaseConfig) -> None:
        """ABC kann nicht direkt instantiiert werden."""
        with pytest.raises(TypeError):
            BacktestStrategy(default_config)

    def test_subclass_must_implement_predict(
        self, default_config: KenobaseConfig
    ) -> None:
        """Subklassen muessen predict() implementieren."""

        class IncompleteStrategy(BacktestStrategy):
            name = "incomplete"

        with pytest.raises(TypeError):
            IncompleteStrategy(default_config)


# =============================================================================
# Test HotNumberStrategy
# =============================================================================


class TestHotNumberStrategy:
    """Tests fuer Hot-Number Strategie."""

    def test_init(self, default_config: KenobaseConfig) -> None:
        """Initialisierung funktioniert."""
        strategy = HotNumberStrategy(default_config)
        assert strategy.name == "hot_number"
        assert strategy.config == default_config

    def test_predict_returns_list(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """predict() gibt Liste zurueck."""
        strategy = HotNumberStrategy(default_config)
        result = strategy.predict(sample_draws_hot, keno_game_config)

        assert isinstance(result, list)
        assert all(isinstance(n, int) for n in result)

    def test_predict_identifies_hot_numbers(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Identifiziert Hot-Numbers korrekt."""
        strategy = HotNumberStrategy(default_config)
        result = strategy.predict(sample_draws_hot, keno_game_config)

        # Numbers 1-10 and 51-60 should be hot (appear 70% of time)
        # Expected frequency for hot: 0.7, threshold is 0.37
        hot_candidates = set(range(1, 11)) | set(range(51, 61))

        # At least some of the predicted should be in hot_candidates
        overlap = set(result) & hot_candidates
        assert len(overlap) > 0, f"Expected overlap with {hot_candidates}, got {result}"

    def test_predict_returns_sorted_list(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Ergebnis ist sortiert."""
        strategy = HotNumberStrategy(default_config)
        result = strategy.predict(sample_draws_hot, keno_game_config)

        assert result == sorted(result)

    def test_metadata(self, default_config: KenobaseConfig) -> None:
        """get_metadata() liefert korrektes Format."""
        strategy = HotNumberStrategy(default_config)
        meta = strategy.get_metadata()

        assert "strategy_name" in meta
        assert meta["strategy_name"] == "hot_number"
        assert "hot_threshold" in meta
        assert "cold_threshold" in meta


# =============================================================================
# Test ColdNumberStrategy
# =============================================================================


class TestColdNumberStrategy:
    """Tests fuer Cold-Number Strategie."""

    def test_init(self, default_config: KenobaseConfig) -> None:
        """Initialisierung funktioniert."""
        strategy = ColdNumberStrategy(default_config)
        assert strategy.name == "cold_number"

    def test_predict_returns_list(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """predict() gibt Liste zurueck."""
        strategy = ColdNumberStrategy(default_config)
        result = strategy.predict(sample_draws_hot, keno_game_config)

        assert isinstance(result, list)

    def test_cold_numbers_different_from_hot(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Cold-Numbers sollten sich von Hot-Numbers unterscheiden."""
        hot_strategy = HotNumberStrategy(default_config)
        cold_strategy = ColdNumberStrategy(default_config)

        hot_result = set(hot_strategy.predict(sample_draws_hot, keno_game_config))
        cold_result = set(cold_strategy.predict(sample_draws_hot, keno_game_config))

        # Should have minimal overlap (ideally none)
        overlap = hot_result & cold_result
        # Note: With some distributions there might be edge cases
        assert len(overlap) < min(len(hot_result), len(cold_result))


# =============================================================================
# Test RandomStrategy
# =============================================================================


class TestRandomStrategy:
    """Tests fuer Random Strategie."""

    def test_init(self, default_config: KenobaseConfig) -> None:
        """Initialisierung funktioniert."""
        strategy = RandomStrategy(default_config)
        assert strategy.name == "random"
        assert strategy.n_predictions == 20

    def test_init_with_params(self, default_config: KenobaseConfig) -> None:
        """Initialisierung mit Parametern."""
        strategy = RandomStrategy(default_config, n_predictions=10, seed=42)
        assert strategy.n_predictions == 10
        assert strategy.seed == 42

    def test_predict_returns_correct_count(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """predict() gibt korrekte Anzahl zurueck."""
        strategy = RandomStrategy(default_config, n_predictions=15)
        result = strategy.predict(sample_draws_hot, keno_game_config)

        assert len(result) == 15

    def test_predict_in_range(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Alle Zahlen im erlaubten Bereich."""
        strategy = RandomStrategy(default_config, n_predictions=20)
        result = strategy.predict(sample_draws_hot, keno_game_config)

        min_num, max_num = keno_game_config.numbers_range
        assert all(min_num <= n <= max_num for n in result)

    def test_reproducibility_with_seed(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Gleicher Seed = gleiches Ergebnis."""
        strategy1 = RandomStrategy(default_config, seed=42)
        strategy2 = RandomStrategy(default_config, seed=42)

        result1 = strategy1.predict(sample_draws_hot, keno_game_config)
        result2 = strategy2.predict(sample_draws_hot, keno_game_config)

        assert result1 == result2

    def test_different_results_without_seed(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Ohne Seed unterschiedliche Ergebnisse (meist)."""
        strategy = RandomStrategy(default_config)

        # Run multiple times - should have different results eventually
        results = []
        for _ in range(5):
            results.append(tuple(strategy.predict(sample_draws_hot, keno_game_config)))

        # At least 2 different results in 5 tries (very high probability)
        unique_results = set(results)
        assert len(unique_results) >= 2


# =============================================================================
# Test StrategyFactory
# =============================================================================


class TestStrategyFactory:
    """Tests fuer Strategy Factory."""

    def test_create_hot_number(self, default_config: KenobaseConfig) -> None:
        """Factory erstellt HotNumberStrategy."""
        strategy = StrategyFactory.create("hot_number", default_config)
        assert isinstance(strategy, HotNumberStrategy)
        assert strategy.name == "hot_number"

    def test_create_cold_number(self, default_config: KenobaseConfig) -> None:
        """Factory erstellt ColdNumberStrategy."""
        strategy = StrategyFactory.create("cold_number", default_config)
        assert isinstance(strategy, ColdNumberStrategy)

    def test_create_random(self, default_config: KenobaseConfig) -> None:
        """Factory erstellt RandomStrategy."""
        strategy = StrategyFactory.create("random", default_config)
        assert isinstance(strategy, RandomStrategy)

    def test_create_with_kwargs(self, default_config: KenobaseConfig) -> None:
        """Factory leitet kwargs weiter."""
        strategy = StrategyFactory.create(
            "random", default_config, n_predictions=10, seed=42
        )
        assert isinstance(strategy, RandomStrategy)
        assert strategy.n_predictions == 10
        assert strategy.seed == 42

    def test_unknown_strategy_raises(self, default_config: KenobaseConfig) -> None:
        """Unbekannte Strategie wirft Fehler."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            StrategyFactory.create("nonexistent", default_config)

    def test_list_strategies(self) -> None:
        """list_strategies() gibt alle registrierten zurueck."""
        strategies = StrategyFactory.list_strategies()
        assert "hot_number" in strategies
        assert "cold_number" in strategies
        assert "random" in strategies

    def test_get_default(self, default_config: KenobaseConfig) -> None:
        """get_default() gibt HotNumberStrategy zurueck."""
        strategy = StrategyFactory.get_default(default_config)
        assert isinstance(strategy, HotNumberStrategy)

    def test_register_custom_strategy(self, default_config: KenobaseConfig) -> None:
        """Eigene Strategie kann registriert werden."""

        class CustomStrategy(BacktestStrategy):
            name = "custom"

            def predict(self, train_draws, game_config):
                return [1, 2, 3]

        # Register (might already be registered from other tests)
        try:
            StrategyFactory.register("custom_test", CustomStrategy)
        except ValueError:
            pass  # Already registered

        # Should be in list now
        assert "custom_test" in StrategyFactory.list_strategies()

    def test_register_duplicate_raises(self, default_config: KenobaseConfig) -> None:
        """Doppelte Registrierung wirft Fehler."""
        with pytest.raises(ValueError, match="already registered"):
            StrategyFactory.register("hot_number", HotNumberStrategy)

    def test_register_invalid_class_raises(self, default_config: KenobaseConfig) -> None:
        """Nicht-Strategy Klasse wirft Fehler."""

        class NotAStrategy:
            pass

        with pytest.raises(ValueError, match="must inherit from BacktestStrategy"):
            StrategyFactory.register("invalid", NotAStrategy)


# =============================================================================
# Integration Tests
# =============================================================================


# =============================================================================
# Test AntiClusterStrategy (TASK-P04)
# =============================================================================


class TestAntiClusterStrategy:
    """Tests fuer Anti-Cluster Strategie (TASK-P04)."""

    def test_init(self, default_config: KenobaseConfig) -> None:
        """Initialisierung funktioniert."""
        strategy = AntiClusterStrategy(default_config)
        assert strategy.name == "anti_cluster"
        assert strategy.cluster_threshold == 5

    def test_init_with_threshold(self, default_config: KenobaseConfig) -> None:
        """Initialisierung mit custom threshold."""
        strategy = AntiClusterStrategy(default_config, cluster_threshold=3)
        assert strategy.cluster_threshold == 3

    def test_predict_returns_list(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """predict() gibt Liste zurueck."""
        strategy = AntiClusterStrategy(default_config)
        result = strategy.predict(sample_draws_hot, keno_game_config)

        assert isinstance(result, list)
        assert all(isinstance(n, int) for n in result)

    def test_predict_excludes_cluster_numbers(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        cluster_draws: list[DrawResult],
    ) -> None:
        """Cluster-Zahlen werden ausgeschlossen."""
        strategy = AntiClusterStrategy(default_config, cluster_threshold=5)
        result = strategy.predict(cluster_draws, keno_game_config)

        # Zahl 5 hat Cluster (6 consecutive) -> should be excluded
        assert 5 not in result
        # Zahl 10 hat nur 3 consecutive -> should be included
        assert 10 in result

    def test_get_no_bet_numbers(
        self,
        default_config: KenobaseConfig,
        cluster_draws: list[DrawResult],
    ) -> None:
        """get_no_bet_numbers() gibt korrekte Menge zurueck."""
        strategy = AntiClusterStrategy(default_config, cluster_threshold=5)
        no_bet = strategy.get_no_bet_numbers(cluster_draws)

        assert isinstance(no_bet, set)
        assert 5 in no_bet  # Has cluster
        assert 10 not in no_bet  # No cluster

    def test_metadata(self, default_config: KenobaseConfig) -> None:
        """get_metadata() liefert korrektes Format."""
        strategy = AntiClusterStrategy(default_config, cluster_threshold=4)
        meta = strategy.get_metadata()

        assert meta["strategy_name"] == "anti_cluster"
        assert meta["cluster_threshold"] == 4


# =============================================================================
# Test CompositeStrategy (TASK-P04)
# =============================================================================


class TestCompositeStrategy:
    """Tests fuer Composite Strategie (TASK-P04)."""

    def test_init(self, default_config: KenobaseConfig) -> None:
        """Initialisierung funktioniert."""
        strategy = CompositeStrategy(default_config)
        assert strategy.name == "composite"
        assert strategy.strategies == []

    def test_add_strategy(self, default_config: KenobaseConfig) -> None:
        """add_strategy() fuegt Strategie hinzu."""
        composite = CompositeStrategy(default_config)
        hot = HotNumberStrategy(default_config)

        composite.add_strategy(hot)
        assert len(composite.strategies) == 1
        assert composite.strategies[0] == hot

    def test_predict_empty_returns_empty(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Leere Composite gibt leere Liste."""
        strategy = CompositeStrategy(default_config)
        result = strategy.predict(sample_draws_hot, keno_game_config)
        assert result == []

    def test_predict_with_single_strategy(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Single-Strategy Composite gibt Strategy-Ergebnis."""
        hot = HotNumberStrategy(default_config)
        composite = CompositeStrategy(default_config, strategies=[hot])

        composite_result = composite.predict(sample_draws_hot, keno_game_config)
        hot_result = hot.predict(sample_draws_hot, keno_game_config)

        assert composite_result == hot_result

    def test_predict_with_anti_cluster_filter(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        cluster_draws: list[DrawResult],
    ) -> None:
        """AntiCluster filtert Zahlen aus Basis-Strategie."""
        # Use RandomStrategy with seed for reproducibility
        random_strategy = RandomStrategy(default_config, n_predictions=70, seed=42)
        anti_cluster = AntiClusterStrategy(default_config, cluster_threshold=5)

        composite = CompositeStrategy(
            default_config, strategies=[random_strategy, anti_cluster]
        )
        result = composite.predict(cluster_draws, keno_game_config)

        # Zahl 5 hat Cluster -> should be filtered out
        assert 5 not in result

    def test_metadata(self, default_config: KenobaseConfig) -> None:
        """get_metadata() liefert korrektes Format."""
        hot = HotNumberStrategy(default_config)
        anti = AntiClusterStrategy(default_config)
        composite = CompositeStrategy(default_config, strategies=[hot, anti])

        meta = composite.get_metadata()
        assert meta["strategy_name"] == "composite"
        assert meta["n_strategies"] == 2
        assert "hot_number" in meta["sub_strategies"]
        assert "anti_cluster" in meta["sub_strategies"]


# =============================================================================
# Test HotNumberAntiClusterStrategy (TASK-P04)
# =============================================================================


class TestHotNumberAntiClusterStrategy:
    """Tests fuer kombinierte Hot-Number + Anti-Cluster Strategie."""

    def test_init(self, default_config: KenobaseConfig) -> None:
        """Initialisierung funktioniert."""
        strategy = HotNumberAntiClusterStrategy(default_config)
        assert strategy.name == "hot_number_anti_cluster"
        assert strategy.cluster_threshold == 5

    def test_init_with_threshold(self, default_config: KenobaseConfig) -> None:
        """Initialisierung mit custom threshold."""
        strategy = HotNumberAntiClusterStrategy(default_config, cluster_threshold=3)
        assert strategy.cluster_threshold == 3

    def test_predict_filters_clusters_from_hot(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        cluster_draws: list[DrawResult],
    ) -> None:
        """Hot-Numbers ohne Cluster-Zahlen."""
        strategy = HotNumberAntiClusterStrategy(default_config, cluster_threshold=5)
        result = strategy.predict(cluster_draws, keno_game_config)

        # Zahl 5 hat Cluster -> should not be in result even if hot
        assert 5 not in result

    def test_predict_returns_sorted_list(
        self,
        default_config: KenobaseConfig,
        keno_game_config: GameConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Ergebnis ist sortiert."""
        strategy = HotNumberAntiClusterStrategy(default_config)
        result = strategy.predict(sample_draws_hot, keno_game_config)

        assert result == sorted(result)

    def test_metadata(self, default_config: KenobaseConfig) -> None:
        """get_metadata() liefert korrektes Format."""
        strategy = HotNumberAntiClusterStrategy(default_config, cluster_threshold=4)
        meta = strategy.get_metadata()

        assert meta["strategy_name"] == "hot_number_anti_cluster"
        assert "hot_threshold" in meta
        assert "cold_threshold" in meta
        assert meta["cluster_threshold"] == 4


# =============================================================================
# Test StrategyFactory with new strategies (TASK-P04)
# =============================================================================


class TestStrategyFactoryAntiCluster:
    """Tests fuer Factory mit neuen Anti-Cluster Strategien."""

    def test_create_anti_cluster(self, default_config: KenobaseConfig) -> None:
        """Factory erstellt AntiClusterStrategy."""
        strategy = StrategyFactory.create("anti_cluster", default_config)
        assert isinstance(strategy, AntiClusterStrategy)

    def test_create_anti_cluster_with_threshold(
        self, default_config: KenobaseConfig
    ) -> None:
        """Factory leitet cluster_threshold weiter."""
        strategy = StrategyFactory.create(
            "anti_cluster", default_config, cluster_threshold=3
        )
        assert isinstance(strategy, AntiClusterStrategy)
        assert strategy.cluster_threshold == 3

    def test_create_composite(self, default_config: KenobaseConfig) -> None:
        """Factory erstellt CompositeStrategy."""
        strategy = StrategyFactory.create("composite", default_config)
        assert isinstance(strategy, CompositeStrategy)

    def test_create_hot_number_anti_cluster(
        self, default_config: KenobaseConfig
    ) -> None:
        """Factory erstellt HotNumberAntiClusterStrategy."""
        strategy = StrategyFactory.create("hot_number_anti_cluster", default_config)
        assert isinstance(strategy, HotNumberAntiClusterStrategy)

    def test_list_includes_new_strategies(self) -> None:
        """list_strategies() enthaelt neue Strategien."""
        strategies = StrategyFactory.list_strategies()
        assert "anti_cluster" in strategies
        assert "composite" in strategies
        assert "hot_number_anti_cluster" in strategies


# =============================================================================
# Integration Tests
# =============================================================================


class TestStrategyIntegration:
    """Integration Tests fuer Strategien im Backtest-Kontext."""

    def test_all_strategies_work_with_backtest_engine(
        self,
        default_config: KenobaseConfig,
        sample_draws_hot: list[DrawResult],
    ) -> None:
        """Alle Strategien funktionieren mit BacktestEngine."""
        from scripts.backtest import BacktestEngine

        for strategy_name in StrategyFactory.list_strategies():
            if strategy_name.startswith("custom"):
                continue  # Skip custom test strategies

            strategy = StrategyFactory.create(strategy_name, default_config)
            engine = BacktestEngine(default_config, strategy=strategy)

            # Should run without error (need 120+ draws for 12 periods)
            large_draws = sample_draws_hot * 2  # 200 draws
            result = engine.run(large_draws, n_periods=6, train_ratio=0.8)

            assert result is not None
            assert len(result.period_results) == 6
            assert all(
                r.strategy_name == strategy_name for r in result.period_results
            )
