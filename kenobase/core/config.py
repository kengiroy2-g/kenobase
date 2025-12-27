"""Kenobase Config-System - YAML-basierte Konfiguration mit Pydantic-Validierung.

Dieses Modul implementiert das Config-System fuer Kenobase V2.0.
Basiert auf CLAUDE.md Architektur-Spezifikation.

Usage:
    from kenobase.core.config import load_config, get_config, set_config

    # Config laden
    config = load_config("config/default.yaml")

    # Globale Config setzen/abrufen
    set_config(config)
    current = get_config()
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

# Globale Config-Instanz
_global_config: Optional[KenobaseConfig] = None


class GameConfig(BaseModel):
    """Konfiguration fuer ein Lottospiel (KENO, EuroJackpot, Lotto)."""

    name: str
    numbers_range: tuple[int, int]
    numbers_to_draw: int
    bonus_range: Optional[tuple[int, int]] = None
    bonus_count: int = 0
    # Spielspezifische Hot/Cold Thresholds (basierend auf erwarteter Frequenz)
    hot_threshold: Optional[float] = None
    cold_threshold: Optional[float] = None

    def get_hot_threshold(self) -> float:
        """Gibt Hot-Threshold zurueck (berechnet wenn nicht gesetzt)."""
        if self.hot_threshold is not None:
            return self.hot_threshold
        # Default: 1.3x erwartete Frequenz
        expected = self.numbers_to_draw / (self.numbers_range[1] - self.numbers_range[0] + 1)
        return expected * 1.3

    def get_cold_threshold(self) -> float:
        """Gibt Cold-Threshold zurueck (berechnet wenn nicht gesetzt)."""
        if self.cold_threshold is not None:
            return self.cold_threshold
        # Default: 0.7x erwartete Frequenz
        expected = self.numbers_to_draw / (self.numbers_range[1] - self.numbers_range[0] + 1)
        return expected * 0.7

    @field_validator("numbers_range")
    @classmethod
    def validate_numbers_range(cls, v: tuple[int, int]) -> tuple[int, int]:
        """Validiert dass min < max."""
        if v[0] >= v[1]:
            raise ValueError(f"numbers_range min ({v[0]}) must be < max ({v[1]})")
        return v

    @model_validator(mode="after")
    def validate_numbers_to_draw(self) -> "GameConfig":
        """Validiert dass numbers_to_draw im Bereich liegt."""
        range_size = self.numbers_range[1] - self.numbers_range[0] + 1
        if self.numbers_to_draw > range_size:
            raise ValueError(
                f"numbers_to_draw ({self.numbers_to_draw}) exceeds range size ({range_size})"
            )
        return self


class PhysicsConfig(BaseModel):
    """Physics Layer Konfiguration (Model Laws A/B/C, Avalanche)."""

    enable_model_laws: bool = True
    stability_threshold: float = Field(default=0.90, ge=0.0, le=1.0)
    stability_variations: int = 100
    enable_least_action: bool = True
    criticality_warning_threshold: float = Field(default=0.70, ge=0.0, le=1.0)
    criticality_critical_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    enable_avalanche: bool = True
    anti_avalanche_mode: bool = True

    @field_validator("stability_threshold", "criticality_warning_threshold", "criticality_critical_threshold")
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        """Validiert Schwellenwerte im Bereich 0-1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Threshold must be between 0 and 1, got {v}")
        return v


class AnalysisConfig(BaseModel):
    """Analyse-Einstellungen."""

    min_frequency_threshold: float = 0.05
    max_frequency_threshold: float = 0.20
    duo_min_occurrences: int = 3
    trio_min_occurrences: int = 2
    quatro_min_occurrences: int = 2
    zehnergruppen_max_per_group: int = 3
    enable_111_principle: bool = True
    windows: list[int] = Field(default_factory=lambda: [5, 10, 20, 50])


class PipelineConfig(BaseModel):
    """Pipeline-Einstellungen."""

    n_workers: int = 4
    chunk_size: int = 10000
    enable_checkpoints: bool = True
    checkpoint_dir: str = "checkpoints"
    checkpoint_interval: int = 100000
    output_format: str = "json"
    output_dir: str = "output"


class PathsConfig(BaseModel):
    """Pfad-Konfiguration."""

    data_dir: str = "data"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"
    models_dir: str = "models"
    output_dir: str = "output"
    logs_dir: str = "logs"


class LegacyConfig(BaseModel):
    """Legacy-Kompatibilitaet fuer alte CSV-Dateien."""

    keno_file: str = "keno/KENO_ab_2018.csv"
    eurojackpot_file: str = "eurojackpot/eurojackpot_archiv_bereinigt.csv"
    lotto_file: str = "lotto/Lotto_archiv_bereinigt.csv"
    csv_delimiter: str = ";"
    csv_date_format: str = "%d.%m.%Y"
    csv_encoding: str = "utf-8"


class LoggingConfig(BaseModel):
    """Logging-Konfiguration."""

    level: str = "INFO"
    file: str = "logs/kenobase.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class KenobaseConfig(BaseModel):
    """Haupt-Konfigurationsklasse fuer Kenobase V2.0."""

    version: str = "2.0.0"
    debug: bool = False
    active_game: str = "keno"

    paths: PathsConfig = Field(default_factory=PathsConfig)
    physics: PhysicsConfig = Field(default_factory=PhysicsConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    legacy: LegacyConfig = Field(default_factory=LegacyConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    games: dict[str, GameConfig] = Field(default_factory=dict)

    def __init__(self, **data):
        """Initialisiert Config mit Standard-Spielen wenn nicht vorhanden."""
        super().__init__(**data)
        if not self.games:
            self.games = self._default_games()

    @staticmethod
    def _default_games() -> dict[str, GameConfig]:
        """Erstellt Standard-Spielkonfigurationen."""
        return {
            "keno": GameConfig(
                name="KENO",
                numbers_range=(1, 70),
                numbers_to_draw=20
            ),
            "eurojackpot": GameConfig(
                name="EuroJackpot",
                numbers_range=(1, 50),
                numbers_to_draw=5,
                bonus_range=(1, 12),
                bonus_count=2
            ),
            "lotto": GameConfig(
                name="Lotto 6aus49",
                numbers_range=(1, 49),
                numbers_to_draw=6,
                bonus_range=(0, 9),
                bonus_count=1
            )
        }

    def get_active_game(self) -> GameConfig:
        """Gibt die Konfiguration des aktiven Spiels zurueck.

        Returns:
            GameConfig fuer das aktive Spiel.

        Raises:
            ValueError: Wenn active_game nicht in games definiert ist.
        """
        if self.active_game not in self.games:
            raise ValueError(f"Unknown active game: {self.active_game}")
        return self.games[self.active_game]


def load_config(path: str) -> KenobaseConfig:
    """Laedt Konfiguration aus YAML-Datei.

    Args:
        path: Pfad zur YAML-Konfigurationsdatei.

    Returns:
        KenobaseConfig-Instanz. Falls Datei nicht existiert,
        wird eine Standard-Konfiguration zurueckgegeben.
    """
    config_path = Path(path)

    if not config_path.exists():
        logger.warning(f"Config file not found: {path}. Using defaults.")
        return KenobaseConfig()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        if yaml_data is None:
            yaml_data = {}

        return _parse_yaml_to_config(yaml_data)

    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config: {e}")
        return KenobaseConfig()


def _parse_yaml_to_config(data: dict) -> KenobaseConfig:
    """Parst YAML-Dict zu KenobaseConfig.

    Args:
        data: Dict aus YAML-Datei.

    Returns:
        KenobaseConfig-Instanz.
    """
    config_data = {}

    # Einfache Felder
    if "version" in data:
        config_data["version"] = data["version"]
    if "debug" in data:
        config_data["debug"] = data["debug"]
    if "active_game" in data:
        config_data["active_game"] = data["active_game"]

    # Paths
    if "paths" in data:
        config_data["paths"] = PathsConfig(**data["paths"])

    # Physics - Map YAML keys to model field names
    if "physics" in data:
        physics_data = data["physics"].copy()
        # Map YAML field names to model field names
        if "criticality_warning" in physics_data:
            physics_data["criticality_warning_threshold"] = physics_data.pop("criticality_warning")
        if "criticality_critical" in physics_data:
            physics_data["criticality_critical_threshold"] = physics_data.pop("criticality_critical")
        config_data["physics"] = PhysicsConfig(**physics_data)

    # Analysis
    if "analysis" in data:
        config_data["analysis"] = AnalysisConfig(**data["analysis"])

    # Pipeline
    if "pipeline" in data:
        config_data["pipeline"] = PipelineConfig(**data["pipeline"])

    # Legacy
    if "legacy" in data:
        config_data["legacy"] = LegacyConfig(**data["legacy"])

    # Logging
    if "logging" in data:
        config_data["logging"] = LoggingConfig(**data["logging"])

    # Games
    if "games" in data:
        games = {}
        for game_key, game_data in data["games"].items():
            # Convert list to tuple for numbers_range
            if "numbers_range" in game_data and isinstance(game_data["numbers_range"], list):
                game_data["numbers_range"] = tuple(game_data["numbers_range"])
            if "bonus_range" in game_data and isinstance(game_data["bonus_range"], list):
                game_data["bonus_range"] = tuple(game_data["bonus_range"])
            games[game_key] = GameConfig(**game_data)
        config_data["games"] = games

    return KenobaseConfig(**config_data)


def save_config(config: KenobaseConfig, path: str) -> None:
    """Speichert Konfiguration als YAML-Datei.

    Args:
        config: KenobaseConfig-Instanz.
        path: Zielpfad fuer YAML-Datei.
    """
    config_path = Path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    yaml_data = _config_to_yaml_dict(config)

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _config_to_yaml_dict(config: KenobaseConfig) -> dict:
    """Konvertiert KenobaseConfig zu YAML-kompatiblem Dict.

    Args:
        config: KenobaseConfig-Instanz.

    Returns:
        Dict fuer YAML-Serialisierung.
    """
    data = {
        "version": config.version,
        "debug": config.debug,
        "active_game": config.active_game,
        "paths": config.paths.model_dump(),
        "physics": {
            "enable_model_laws": config.physics.enable_model_laws,
            "stability_threshold": config.physics.stability_threshold,
            "stability_variations": config.physics.stability_variations,
            "enable_least_action": config.physics.enable_least_action,
            "criticality_warning": config.physics.criticality_warning_threshold,
            "criticality_critical": config.physics.criticality_critical_threshold,
            "enable_avalanche": config.physics.enable_avalanche,
            "anti_avalanche_mode": config.physics.anti_avalanche_mode,
        },
        "analysis": config.analysis.model_dump(),
        "pipeline": config.pipeline.model_dump(),
        "legacy": config.legacy.model_dump(),
        "logging": config.logging.model_dump(),
        "games": {}
    }

    for game_key, game_config in config.games.items():
        game_data = {
            "name": game_config.name,
            "numbers_range": list(game_config.numbers_range),
            "numbers_to_draw": game_config.numbers_to_draw,
        }
        if game_config.bonus_range:
            game_data["bonus_range"] = list(game_config.bonus_range)
            game_data["bonus_count"] = game_config.bonus_count
        data["games"][game_key] = game_data

    return data


def get_config() -> KenobaseConfig:
    """Gibt die globale Konfiguration zurueck.

    Returns:
        Aktuelle globale KenobaseConfig-Instanz.
        Falls keine gesetzt, wird Standard-Config zurueckgegeben.
    """
    global _global_config
    if _global_config is None:
        _global_config = KenobaseConfig()
    return _global_config


def set_config(config: KenobaseConfig) -> None:
    """Setzt die globale Konfiguration.

    Args:
        config: KenobaseConfig-Instanz.
    """
    global _global_config
    _global_config = config


__all__ = [
    "KenobaseConfig",
    "GameConfig",
    "PhysicsConfig",
    "AnalysisConfig",
    "PipelineConfig",
    "PathsConfig",
    "LegacyConfig",
    "LoggingConfig",
    "load_config",
    "save_config",
    "get_config",
    "set_config",
]
