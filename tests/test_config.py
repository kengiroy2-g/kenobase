"""Tests für das Kenobase Config-System."""

import pytest
import tempfile
from pathlib import Path
import yaml

from kenobase.core.config import (
    KenobaseConfig,
    GameConfig,
    PhysicsConfig,
    AnalysisConfig,
    PipelineConfig,
    PathsConfig,
    load_config,
    save_config,
    get_config,
    set_config,
)


class TestGameConfig:
    """Tests für GameConfig Dataclass."""

    def test_keno_config(self):
        """Test KENO Spielkonfiguration."""
        config = GameConfig(
            name="KENO",
            numbers_range=(1, 70),
            numbers_to_draw=20
        )
        assert config.name == "KENO"
        assert config.numbers_range == (1, 70)
        assert config.numbers_to_draw == 20
        assert config.bonus_range is None
        assert config.bonus_count == 0

    def test_eurojackpot_config(self):
        """Test EuroJackpot Spielkonfiguration."""
        config = GameConfig(
            name="EuroJackpot",
            numbers_range=(1, 50),
            numbers_to_draw=5,
            bonus_range=(1, 12),
            bonus_count=2
        )
        assert config.name == "EuroJackpot"
        assert config.numbers_to_draw == 5
        assert config.bonus_range == (1, 12)
        assert config.bonus_count == 2

    def test_invalid_numbers_range(self):
        """Test ungültige Zahlenbereich-Konfiguration."""
        with pytest.raises(ValueError):
            GameConfig(
                name="Invalid",
                numbers_range=(70, 1),  # min > max
                numbers_to_draw=6
            )

    def test_numbers_to_draw_exceeds_range(self):
        """Test wenn numbers_to_draw größer als Bereich ist."""
        with pytest.raises(ValueError):
            GameConfig(
                name="Invalid",
                numbers_range=(1, 10),
                numbers_to_draw=15  # > 10 Zahlen im Bereich
            )


class TestPhysicsConfig:
    """Tests für PhysicsConfig Dataclass."""

    def test_default_values(self):
        """Test Standard-Physics-Konfiguration."""
        config = PhysicsConfig()
        assert config.enable_model_laws is True
        assert config.stability_threshold == 0.90
        assert config.criticality_warning_threshold == 0.70
        assert config.enable_avalanche is True

    def test_custom_thresholds(self):
        """Test benutzerdefinierte Schwellenwerte."""
        config = PhysicsConfig(
            stability_threshold=0.95,
            criticality_warning_threshold=0.80
        )
        assert config.stability_threshold == 0.95
        assert config.criticality_warning_threshold == 0.80

    def test_invalid_stability_threshold(self):
        """Test ungültiger Stabilitätsschwellenwert."""
        with pytest.raises(ValueError):
            PhysicsConfig(stability_threshold=1.5)  # > 1.0


class TestKenobaseConfig:
    """Tests für Haupt-Konfigurationsklasse."""

    def test_default_games(self):
        """Test Standard-Spielkonfigurationen."""
        config = KenobaseConfig()
        assert "keno" in config.games
        assert "eurojackpot" in config.games
        assert "lotto" in config.games

    def test_get_active_game(self):
        """Test Abruf des aktiven Spiels."""
        config = KenobaseConfig()
        config.active_game = "keno"
        game = config.get_active_game()
        assert game.name == "KENO"
        assert game.numbers_range == (1, 70)

    def test_unknown_active_game(self):
        """Test unbekanntes aktives Spiel."""
        config = KenobaseConfig()
        config.active_game = "unknown_game"
        with pytest.raises(ValueError):
            config.get_active_game()


class TestConfigIO:
    """Tests für Konfiguration Laden/Speichern."""

    def test_save_and_load_config(self):
        """Test Speichern und Laden einer Konfiguration."""
        config = KenobaseConfig()
        config.debug = True
        config.physics.stability_threshold = 0.85
        config.active_game = "eurojackpot"

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            save_config(config, str(config_path))

            # Datei existiert
            assert config_path.exists()

            # Laden und prüfen
            loaded_config = load_config(str(config_path))
            assert loaded_config.debug is True
            assert loaded_config.physics.stability_threshold == 0.85
            assert loaded_config.active_game == "eurojackpot"

    def test_load_nonexistent_config(self):
        """Test Laden nicht existierender Konfiguration (Fallback)."""
        config = load_config("/nonexistent/path/config.yaml")
        # Sollte Default-Config zurückgeben
        assert isinstance(config, KenobaseConfig)
        assert config.version == "2.0.0"

    def test_yaml_format(self):
        """Test YAML-Format der gespeicherten Konfiguration."""
        config = KenobaseConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test.yaml"
            save_config(config, str(config_path))

            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)

            assert 'version' in yaml_data
            assert 'physics' in yaml_data
            assert 'games' in yaml_data
            assert yaml_data['physics']['enable_model_laws'] is True


class TestGlobalConfig:
    """Tests für globale Konfiguration."""

    def test_get_set_config(self):
        """Test globale Config get/set."""
        custom_config = KenobaseConfig()
        custom_config.debug = True

        set_config(custom_config)
        retrieved = get_config()

        assert retrieved.debug is True


class TestAnalysisConfig:
    """Tests für AnalysisConfig."""

    def test_default_windows(self):
        """Test Standard-Windows."""
        config = AnalysisConfig()
        assert config.windows == [5, 10, 20, 50]

    def test_111_principle_enabled(self):
        """Test 111-Prinzip standardmäßig aktiviert."""
        config = AnalysisConfig()
        assert config.enable_111_principle is True


class TestPipelineConfig:
    """Tests für PipelineConfig."""

    def test_default_workers(self):
        """Test Standard-Worker-Anzahl."""
        config = PipelineConfig()
        assert config.n_workers == 4

    def test_checkpoint_settings(self):
        """Test Checkpoint-Einstellungen."""
        config = PipelineConfig()
        assert config.enable_checkpoints is True
        assert config.checkpoint_interval == 100000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
