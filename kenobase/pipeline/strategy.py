"""Strategy Pattern fuer Walk-Forward Backtest.

Dieses Modul implementiert das Strategy-Pattern fuer austauschbare
Vorhersage-Strategien im Backtest-Framework (TASK-P03).

Strategien koennen verschiedene Ansaetze zur Zahlenvorhersage implementieren:
- HotNumberStrategy: Basiert auf Frequenzanalyse (Standard)
- PhysicsStrategy: Basiert auf Model Laws A/B/C
- MLStrategy: Basiert auf Machine Learning (zukuenftig)

Usage:
    from kenobase.pipeline.strategy import StrategyFactory, HotNumberStrategy

    # Explizit
    strategy = HotNumberStrategy(config)
    hot_numbers = strategy.predict(train_draws)

    # Via Factory (empfohlen)
    strategy = StrategyFactory.create("hot_number", config)
    hot_numbers = strategy.predict(train_draws)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kenobase.core.config import GameConfig, KenobaseConfig
    from kenobase.core.data_loader import DrawResult


class BacktestStrategy(ABC):
    """Abstrakte Basisklasse fuer Backtest-Strategien.

    Definiert das Interface fuer alle Vorhersage-Strategien.
    Jede Strategy muss predict() implementieren.

    Attributes:
        name: Eindeutiger Name der Strategie
        config: Kenobase-Konfiguration
    """

    name: str = "base"

    def __init__(self, config: KenobaseConfig) -> None:
        """Initialisiert Strategy mit Konfiguration.

        Args:
            config: Kenobase-Konfiguration
        """
        self.config = config

    @abstractmethod
    def predict(
        self,
        train_draws: list[DrawResult],
        game_config: GameConfig,
    ) -> list[int]:
        """Generiert Vorhersage basierend auf Trainingsdaten.

        Args:
            train_draws: Historische Ziehungen fuer Training
            game_config: Spielspezifische Konfiguration

        Returns:
            Liste der vorhergesagten Zahlen (sortiert)
        """
        ...

    def get_metadata(self) -> dict[str, Any]:
        """Gibt Metadaten der Strategie zurueck.

        Kann von Subklassen ueberschrieben werden um
        strategie-spezifische Informationen zu liefern.

        Returns:
            Dict mit Metadaten (z.B. Parameter, Version)
        """
        return {
            "strategy_name": self.name,
            "strategy_version": "1.0.0",
        }


class HotNumberStrategy(BacktestStrategy):
    """Frequenz-basierte Hot-Number Strategie.

    Standard-Strategie: Identifiziert "heisse" Zahlen basierend
    auf ihrer Erscheinungshaeufigkeit im Trainingszeitraum.

    Verwendet game-specific thresholds aus config/default.yaml
    (hot_threshold, cold_threshold pro Spiel).
    """

    name: str = "hot_number"

    def predict(
        self,
        train_draws: list[DrawResult],
        game_config: GameConfig,
    ) -> list[int]:
        """Identifiziert Hot-Numbers aus Trainingsdaten.

        Args:
            train_draws: Historische Ziehungen
            game_config: Spielspezifische Konfiguration

        Returns:
            Liste der Hot-Numbers (sortiert)
        """
        from kenobase.analysis.frequency import get_hot_numbers

        return get_hot_numbers(
            train_draws,
            hot_threshold=game_config.get_hot_threshold(),
            cold_threshold=game_config.get_cold_threshold(),
            number_range=game_config.numbers_range,
        )

    def get_metadata(self) -> dict[str, Any]:
        """Gibt Hot-Number spezifische Metadaten zurueck."""
        game_config = self.config.get_active_game()
        return {
            "strategy_name": self.name,
            "strategy_version": "1.0.0",
            "hot_threshold": game_config.get_hot_threshold(),
            "cold_threshold": game_config.get_cold_threshold(),
        }


class ColdNumberStrategy(BacktestStrategy):
    """Cold-Number Strategie (Gegenteil von Hot).

    Identifiziert "kalte" Zahlen die selten erscheinen.
    Basiert auf der Annahme dass seltene Zahlen
    "ueberfaellig" sind (Gamblers Fallacy - nur fuer Tests).
    """

    name: str = "cold_number"

    def predict(
        self,
        train_draws: list[DrawResult],
        game_config: GameConfig,
    ) -> list[int]:
        """Identifiziert Cold-Numbers aus Trainingsdaten.

        Args:
            train_draws: Historische Ziehungen
            game_config: Spielspezifische Konfiguration

        Returns:
            Liste der Cold-Numbers (sortiert)
        """
        from kenobase.analysis.frequency import get_cold_numbers

        return get_cold_numbers(
            train_draws,
            hot_threshold=game_config.get_hot_threshold(),
            cold_threshold=game_config.get_cold_threshold(),
            number_range=game_config.numbers_range,
        )


class RandomStrategy(BacktestStrategy):
    """Zufalls-Strategie (Baseline).

    Waehlt zufaellige Zahlen aus dem erlaubten Bereich.
    Dient als Baseline zum Vergleich mit anderen Strategien.
    """

    name: str = "random"

    def __init__(
        self,
        config: KenobaseConfig,
        n_predictions: int = 20,
        seed: int | None = None,
    ) -> None:
        """Initialisiert Random-Strategy.

        Args:
            config: Kenobase-Konfiguration
            n_predictions: Anzahl zu generierende Zahlen
            seed: Random Seed fuer Reproduzierbarkeit
        """
        super().__init__(config)
        self.n_predictions = n_predictions
        self.seed = seed

    def predict(
        self,
        train_draws: list[DrawResult],
        game_config: GameConfig,
    ) -> list[int]:
        """Generiert zufaellige Zahlen.

        Args:
            train_draws: Wird ignoriert
            game_config: Fuer Zahlenbereich

        Returns:
            Liste zufaelliger Zahlen (sortiert)
        """
        import random

        if self.seed is not None:
            random.seed(self.seed)

        min_num, max_num = game_config.numbers_range
        all_numbers = list(range(min_num, max_num + 1))
        n_to_pick = min(self.n_predictions, len(all_numbers))

        return sorted(random.sample(all_numbers, n_to_pick))


class AntiClusterStrategy(BacktestStrategy):
    """Anti-Cluster Strategy (TASK-P04).

    Filtert Zahlen mit aktiven Clustern aus den Vorhersagen.
    Basiert auf cluster_reset.py: Zahlen mit NO_BET Signal
    werden aus den Predictions entfernt.

    Ein Cluster ist eine Serie von >= threshold aufeinanderfolgenden
    Ziehungen, in denen eine Zahl erscheint. Nach der Reset-Hypothese
    (HYP-003) haben solche Zahlen eine erhoehte Wahrscheinlichkeit
    nicht mehr zu erscheinen.
    """

    name: str = "anti_cluster"

    def __init__(
        self,
        config: KenobaseConfig,
        cluster_threshold: int = 5,
    ) -> None:
        """Initialisiert AntiCluster-Strategy.

        Args:
            config: Kenobase-Konfiguration
            cluster_threshold: Mindest-Laenge fuer Cluster (default: 5)
        """
        super().__init__(config)
        self.cluster_threshold = cluster_threshold

    def predict(
        self,
        train_draws: list[DrawResult],
        game_config: GameConfig,
    ) -> list[int]:
        """Generiert Vorhersage: Alle Zahlen ausser NO_BET Signale.

        Args:
            train_draws: Historische Ziehungen
            game_config: Spielspezifische Konfiguration

        Returns:
            Liste der vorhergesagten Zahlen (ohne Cluster-Zahlen)
        """
        from kenobase.analysis.cluster_reset import generate_trading_signals

        # Get NO_BET signals
        signals = generate_trading_signals(train_draws, threshold=self.cluster_threshold)
        no_bet_numbers = {s.number for s in signals if s.signal_type == "NO_BET"}

        # Return all numbers except NO_BET
        min_num, max_num = game_config.numbers_range
        all_numbers = set(range(min_num, max_num + 1))
        allowed_numbers = all_numbers - no_bet_numbers

        return sorted(allowed_numbers)

    def get_metadata(self) -> dict[str, Any]:
        """Gibt AntiCluster spezifische Metadaten zurueck."""
        return {
            "strategy_name": self.name,
            "strategy_version": "1.0.0",
            "cluster_threshold": self.cluster_threshold,
        }

    def get_no_bet_numbers(
        self,
        train_draws: list[DrawResult],
    ) -> set[int]:
        """Gibt alle NO_BET Zahlen zurueck (fuer Composite-Strategien).

        Args:
            train_draws: Historische Ziehungen

        Returns:
            Set der NO_BET Zahlen
        """
        from kenobase.analysis.cluster_reset import generate_trading_signals

        signals = generate_trading_signals(train_draws, threshold=self.cluster_threshold)
        return {s.number for s in signals if s.signal_type == "NO_BET"}


class CompositeStrategy(BacktestStrategy):
    """Composite Strategy - kombiniert mehrere Strategien (TASK-P04).

    Beispiel: HotNumber + AntiCluster = Hot-Numbers ohne Cluster-Zahlen.

    Die erste Strategie generiert Kandidaten, nachfolgende Strategien
    koennen diese filtern (bei FilterStrategy) oder erweitern.
    """

    name: str = "composite"

    def __init__(
        self,
        config: KenobaseConfig,
        strategies: list[BacktestStrategy] | None = None,
    ) -> None:
        """Initialisiert Composite-Strategy.

        Args:
            config: Kenobase-Konfiguration
            strategies: Liste von Strategien (erste = Basis, rest = Filter)
        """
        super().__init__(config)
        self.strategies = strategies or []

    def add_strategy(self, strategy: BacktestStrategy) -> None:
        """Fuegt Strategie zur Kette hinzu.

        Args:
            strategy: Zu ergaenzende Strategie
        """
        self.strategies.append(strategy)

    def predict(
        self,
        train_draws: list[DrawResult],
        game_config: GameConfig,
    ) -> list[int]:
        """Generiert Vorhersage durch Kombination aller Strategien.

        Logik:
        1. Erste Strategie generiert Basis-Kandidaten
        2. AntiClusterStrategy filtert NO_BET Zahlen raus
        3. Andere Strategien: Intersection mit Kandidaten

        Args:
            train_draws: Historische Ziehungen
            game_config: Spielspezifische Konfiguration

        Returns:
            Liste der kombinierten Vorhersagen
        """
        if not self.strategies:
            return []

        # Start with first strategy
        candidates = set(self.strategies[0].predict(train_draws, game_config))

        # Apply filters from remaining strategies
        for strategy in self.strategies[1:]:
            if isinstance(strategy, AntiClusterStrategy):
                # AntiCluster: Remove NO_BET numbers
                no_bet = strategy.get_no_bet_numbers(train_draws)
                candidates = candidates - no_bet
            else:
                # Other strategies: Intersection
                strategy_result = set(strategy.predict(train_draws, game_config))
                candidates = candidates & strategy_result

        return sorted(candidates)

    def get_metadata(self) -> dict[str, Any]:
        """Gibt Composite spezifische Metadaten zurueck."""
        return {
            "strategy_name": self.name,
            "strategy_version": "1.0.0",
            "sub_strategies": [s.name for s in self.strategies],
            "n_strategies": len(self.strategies),
        }


class HotNumberAntiClusterStrategy(BacktestStrategy):
    """Hot-Number + Anti-Cluster kombinierte Strategie (TASK-P04).

    Convenience-Strategie: Kombiniert HotNumber mit AntiCluster.
    Gibt Hot-Numbers zurueck, aber filtert Zahlen mit aktiven Clustern.
    """

    name: str = "hot_number_anti_cluster"

    def __init__(
        self,
        config: KenobaseConfig,
        cluster_threshold: int = 5,
    ) -> None:
        """Initialisiert kombinierte Strategie.

        Args:
            config: Kenobase-Konfiguration
            cluster_threshold: Mindest-Laenge fuer Cluster (default: 5)
        """
        super().__init__(config)
        self.cluster_threshold = cluster_threshold
        self._hot_strategy = HotNumberStrategy(config)
        self._anti_cluster = AntiClusterStrategy(config, cluster_threshold)

    def predict(
        self,
        train_draws: list[DrawResult],
        game_config: GameConfig,
    ) -> list[int]:
        """Hot-Numbers ohne Cluster-Zahlen.

        Args:
            train_draws: Historische Ziehungen
            game_config: Spielspezifische Konfiguration

        Returns:
            Liste der Hot-Numbers ohne NO_BET Signale
        """
        hot_numbers = set(self._hot_strategy.predict(train_draws, game_config))
        no_bet = self._anti_cluster.get_no_bet_numbers(train_draws)

        return sorted(hot_numbers - no_bet)

    def get_metadata(self) -> dict[str, Any]:
        """Gibt Metadaten zurueck."""
        game_config = self.config.get_active_game()
        return {
            "strategy_name": self.name,
            "strategy_version": "1.0.0",
            "hot_threshold": game_config.get_hot_threshold(),
            "cold_threshold": game_config.get_cold_threshold(),
            "cluster_threshold": self.cluster_threshold,
        }


class StrategyFactory:
    """Factory fuer Strategy-Instanzen.

    Zentrale Stelle zum Erstellen von Strategien.
    Unterstuetzt dynamische Registrierung neuer Strategien.

    Example:
        >>> strategy = StrategyFactory.create("hot_number", config)
        >>> StrategyFactory.register("my_strategy", MyStrategy)
        >>> custom = StrategyFactory.create("my_strategy", config)
    """

    _registry: dict[str, type[BacktestStrategy]] = {
        "hot_number": HotNumberStrategy,
        "cold_number": ColdNumberStrategy,
        "random": RandomStrategy,
        "anti_cluster": AntiClusterStrategy,
        "composite": CompositeStrategy,
        "hot_number_anti_cluster": HotNumberAntiClusterStrategy,
    }

    @classmethod
    def create(
        cls,
        strategy_name: str,
        config: KenobaseConfig,
        **kwargs: Any,
    ) -> BacktestStrategy:
        """Erstellt Strategy-Instanz nach Name.

        Args:
            strategy_name: Registrierter Name der Strategie
            config: Kenobase-Konfiguration
            **kwargs: Zusaetzliche Parameter fuer Strategy

        Returns:
            Initialisierte Strategy-Instanz

        Raises:
            ValueError: Wenn strategy_name nicht registriert
        """
        if strategy_name not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Unknown strategy: '{strategy_name}'. "
                f"Available: {available}"
            )

        strategy_class = cls._registry[strategy_name]
        return strategy_class(config, **kwargs)

    @classmethod
    def register(
        cls,
        name: str,
        strategy_class: type[BacktestStrategy],
    ) -> None:
        """Registriert neue Strategy.

        Args:
            name: Eindeutiger Name fuer die Strategie
            strategy_class: Strategy-Klasse (muss BacktestStrategy erben)

        Raises:
            ValueError: Wenn Name bereits registriert oder Klasse ungueltig
        """
        if name in cls._registry:
            raise ValueError(f"Strategy '{name}' already registered")

        if not issubclass(strategy_class, BacktestStrategy):
            raise ValueError(
                f"Strategy class must inherit from BacktestStrategy, "
                f"got {strategy_class}"
            )

        cls._registry[name] = strategy_class

    @classmethod
    def list_strategies(cls) -> list[str]:
        """Listet alle registrierten Strategien.

        Returns:
            Liste der Strategie-Namen
        """
        return list(cls._registry.keys())

    @classmethod
    def get_default(cls, config: KenobaseConfig) -> BacktestStrategy:
        """Gibt Standard-Strategie zurueck.

        Args:
            config: Kenobase-Konfiguration

        Returns:
            HotNumberStrategy als Standard
        """
        return cls.create("hot_number", config)


__all__ = [
    "AntiClusterStrategy",
    "BacktestStrategy",
    "ColdNumberStrategy",
    "CompositeStrategy",
    "HotNumberAntiClusterStrategy",
    "HotNumberStrategy",
    "RandomStrategy",
    "StrategyFactory",
]
