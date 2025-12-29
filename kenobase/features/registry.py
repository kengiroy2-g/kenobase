"""Feature Registry - Zentrale Registrierung aller Feature-Extraktoren.

Dieses Modul definiert:
- FeatureDefinition: Metadata fuer einen Feature-Typ
- FeatureRegistry: Singleton fuer Feature-Registrierung
- register_feature: Decorator fuer Feature-Funktionen

Alle 18+ Feature-Kategorien werden hier registriert:
1. Frequency: freq_raw, freq_rolling, freq_hot, freq_cold
2. Pattern: duo_score, trio_score, quatro_score
3. Temporal: weekday_bias, month_bias, holiday_proximity
4. Popularity: is_birthday, is_schoene, is_safe
5. Stake: einsatz_score, auszahlung_score
6. Recurrence: streak_length, stability_score
7. Stability: law_a_score, window_stability
8. Cluster: reset_probability, cluster_signal
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class FeatureCategory(str, Enum):
    """Kategorien fuer Features."""

    FREQUENCY = "frequency"
    PATTERN = "pattern"
    TEMPORAL = "temporal"
    POPULARITY = "popularity"
    STAKE = "stake"
    RECURRENCE = "recurrence"
    STABILITY = "stability"
    CLUSTER = "cluster"


@dataclass
class FeatureDefinition:
    """Definition eines Feature-Typs.

    Attributes:
        name: Eindeutiger Feature-Name (z.B. "freq_raw")
        category: Feature-Kategorie
        description: Kurze Beschreibung
        extractor: Funktion die das Feature berechnet
        dependencies: Andere Features die benoetigt werden
        normalize: Ob das Feature auf 0-1 normalisiert werden soll
        weight: Default-Gewicht fuer Combined Score
    """

    name: str
    category: FeatureCategory
    description: str
    extractor: Optional[Callable[..., dict[int, float]]] = None
    dependencies: list[str] = field(default_factory=list)
    normalize: bool = True
    weight: float = 1.0


class FeatureRegistry:
    """Singleton-Registry fuer alle Feature-Definitionen.

    Verwendung:
        registry = FeatureRegistry()
        registry.register(FeatureDefinition(...))

        # Oder via Decorator:
        @register_feature("freq_raw", FeatureCategory.FREQUENCY)
        def extract_freq_raw(draws, numbers_range):
            ...
    """

    _instance: Optional[FeatureRegistry] = None
    _features: dict[str, FeatureDefinition]

    def __new__(cls) -> FeatureRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._features = {}
            cls._instance._register_default_features()
        return cls._instance

    def _register_default_features(self) -> None:
        """Registriert alle Standard-Features."""
        # Frequency Features (4)
        self._features["freq_raw"] = FeatureDefinition(
            name="freq_raw",
            category=FeatureCategory.FREQUENCY,
            description="Rohe Haeufigkeit der Zahl in allen Ziehungen",
            weight=1.0,
        )
        self._features["freq_rolling"] = FeatureDefinition(
            name="freq_rolling",
            category=FeatureCategory.FREQUENCY,
            description="Rolling-Haeufigkeit (letzte N Ziehungen)",
            weight=1.2,
        )
        self._features["freq_hot"] = FeatureDefinition(
            name="freq_hot",
            category=FeatureCategory.FREQUENCY,
            description="1.0 wenn ueber Hot-Threshold, sonst proportional",
            weight=0.8,
        )
        self._features["freq_cold"] = FeatureDefinition(
            name="freq_cold",
            category=FeatureCategory.FREQUENCY,
            description="1.0 wenn unter Cold-Threshold, sonst proportional",
            weight=0.8,
        )

        # Pattern Features (3)
        self._features["duo_score"] = FeatureDefinition(
            name="duo_score",
            category=FeatureCategory.PATTERN,
            description="Score basierend auf Duo-Pattern-Vorkommen",
            weight=0.5,
        )
        self._features["trio_score"] = FeatureDefinition(
            name="trio_score",
            category=FeatureCategory.PATTERN,
            description="Score basierend auf Trio-Pattern-Vorkommen",
            weight=0.5,
        )
        self._features["quatro_score"] = FeatureDefinition(
            name="quatro_score",
            category=FeatureCategory.PATTERN,
            description="Score basierend auf Quatro-Pattern-Vorkommen",
            weight=0.3,
        )

        # Temporal Features (3)
        self._features["weekday_bias"] = FeatureDefinition(
            name="weekday_bias",
            category=FeatureCategory.TEMPORAL,
            description="Bias der Zahl fuer bestimmte Wochentage",
            weight=0.4,
        )
        self._features["month_bias"] = FeatureDefinition(
            name="month_bias",
            category=FeatureCategory.TEMPORAL,
            description="Bias der Zahl fuer bestimmte Monate",
            weight=0.3,
        )
        self._features["holiday_proximity"] = FeatureDefinition(
            name="holiday_proximity",
            category=FeatureCategory.TEMPORAL,
            description="Haeufigkeit nahe Feiertagen (signifikant!)",
            weight=0.8,
        )

        # Popularity Features (3)
        self._features["is_birthday"] = FeatureDefinition(
            name="is_birthday",
            category=FeatureCategory.POPULARITY,
            description="1.0 wenn Geburtstagszahl (1-31), sonst 0",
            normalize=False,
            weight=0.6,
        )
        self._features["is_schoene"] = FeatureDefinition(
            name="is_schoene",
            category=FeatureCategory.POPULARITY,
            description="1.0 wenn 'schoene' Zahl, sonst 0",
            normalize=False,
            weight=0.5,
        )
        self._features["is_safe"] = FeatureDefinition(
            name="is_safe",
            category=FeatureCategory.POPULARITY,
            description="1.0 wenn wenige Mitspieler (safe), sonst 0",
            normalize=False,
            weight=0.9,
        )

        # Stake Features (2)
        self._features["einsatz_score"] = FeatureDefinition(
            name="einsatz_score",
            category=FeatureCategory.STAKE,
            description="Invertierter Einsatz-Score (weniger = besser)",
            weight=0.7,
        )
        self._features["auszahlung_score"] = FeatureDefinition(
            name="auszahlung_score",
            category=FeatureCategory.STAKE,
            description="Auszahlungs-Korrelation (signifikant!)",
            weight=0.9,
        )

        # Recurrence Features (2)
        self._features["streak_length"] = FeatureDefinition(
            name="streak_length",
            category=FeatureCategory.RECURRENCE,
            description="Normalisierte aktuelle Streak-Laenge",
            weight=0.6,
        )
        self._features["stability_score"] = FeatureDefinition(
            name="stability_score",
            category=FeatureCategory.RECURRENCE,
            description="Stabilitaet der Wiederholungs-Muster",
            weight=0.7,
        )

        # Stability Features (Model Law A) (1)
        self._features["law_a_score"] = FeatureDefinition(
            name="law_a_score",
            category=FeatureCategory.STABILITY,
            description="Model Law A Score (>= 0.9 = Gesetz)",
            weight=1.0,
        )

        # Cluster Features (2)
        self._features["reset_probability"] = FeatureDefinition(
            name="reset_probability",
            category=FeatureCategory.CLUSTER,
            description="Wahrscheinlichkeit eines Cluster-Resets",
            weight=0.8,
        )
        self._features["cluster_signal"] = FeatureDefinition(
            name="cluster_signal",
            category=FeatureCategory.CLUSTER,
            description="Trading-Signal (1=BUY, 0=HOLD, -1=SELL)",
            normalize=False,
            weight=0.7,
        )

        logger.info(f"Registered {len(self._features)} default features")

    def register(self, definition: FeatureDefinition) -> None:
        """Registriert eine Feature-Definition.

        Args:
            definition: Feature-Definition
        """
        if definition.name in self._features:
            logger.warning(f"Overwriting existing feature: {definition.name}")
        self._features[definition.name] = definition
        logger.debug(f"Registered feature: {definition.name}")

    def get(self, name: str) -> Optional[FeatureDefinition]:
        """Gibt Feature-Definition zurueck.

        Args:
            name: Feature-Name

        Returns:
            FeatureDefinition oder None
        """
        return self._features.get(name)

    def get_all(self) -> dict[str, FeatureDefinition]:
        """Gibt alle Feature-Definitionen zurueck."""
        return self._features.copy()

    def get_by_category(self, category: FeatureCategory) -> list[FeatureDefinition]:
        """Gibt alle Features einer Kategorie zurueck.

        Args:
            category: Feature-Kategorie

        Returns:
            Liste von FeatureDefinitions
        """
        return [f for f in self._features.values() if f.category == category]

    def count(self) -> int:
        """Gibt Anzahl registrierter Features zurueck."""
        return len(self._features)

    @property
    def feature_names(self) -> list[str]:
        """Liste aller Feature-Namen."""
        return list(self._features.keys())


def register_feature(
    name: str,
    category: FeatureCategory,
    description: str = "",
    weight: float = 1.0,
    normalize: bool = True,
) -> Callable:
    """Decorator zum Registrieren einer Feature-Extraktor-Funktion.

    Verwendung:
        @register_feature("my_feature", FeatureCategory.FREQUENCY)
        def extract_my_feature(draws, numbers_range):
            return {num: score for num in range(1, 71)}

    Args:
        name: Feature-Name
        category: Feature-Kategorie
        description: Beschreibung
        weight: Gewicht fuer Combined Score
        normalize: Normalisierung auf 0-1

    Returns:
        Decorator-Funktion
    """

    def decorator(func: Callable[..., dict[int, float]]) -> Callable:
        registry = FeatureRegistry()
        registry.register(
            FeatureDefinition(
                name=name,
                category=category,
                description=description or func.__doc__ or "",
                extractor=func,
                weight=weight,
                normalize=normalize,
            )
        )
        return func

    return decorator


__all__ = [
    "FeatureCategory",
    "FeatureDefinition",
    "FeatureRegistry",
    "register_feature",
]
