"""Gemeinsame Pytest-Fixtures fuer Kenobase Tests.

Dieses Modul stellt projektweite Fixtures bereit, die in allen
Test-Modulen automatisch verfuegbar sind.
"""

from pathlib import Path
from typing import Generator

import pytest


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def fixtures_dir() -> Path:
    """Pfad zum fixtures Verzeichnis.

    Returns:
        Path zum tests/fixtures/ Verzeichnis
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def project_root() -> Path:
    """Pfad zum Projekt-Root.

    Returns:
        Path zum Kenobase Projekt-Root
    """
    return Path(__file__).parent.parent


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_numbers() -> list[int]:
    """Beispiel-Zahlen fuer Tests.

    Returns:
        Liste mit 20 KENO-typischen Zahlen (1-70)
    """
    return [1, 6, 11, 19, 21, 26, 27, 28, 29, 32,
            34, 42, 48, 50, 51, 61, 63, 64, 65, 68]


@pytest.fixture
def sample_lotto_numbers() -> list[int]:
    """Beispiel Lotto-Zahlen (6 aus 49).

    Returns:
        Liste mit 6 Lotto-Zahlen
    """
    return [7, 14, 21, 28, 35, 42]


@pytest.fixture
def sample_eurojackpot_numbers() -> tuple[list[int], list[int]]:
    """Beispiel EuroJackpot-Zahlen (5+2).

    Returns:
        Tuple aus (Hauptzahlen, Eurozahlen)
    """
    return ([2, 7, 38, 40, 45], [7, 10])


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Temporaeres Datenverzeichnis fuer Tests.

    Args:
        tmp_path: Pytest-internes tmp_path Fixture

    Returns:
        Path zum temporaeren Verzeichnis
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


# ============================================================================
# Config Fixtures
# ============================================================================

@pytest.fixture
def default_config_path(project_root: Path) -> Path:
    """Pfad zur Standard-Konfiguration.

    Args:
        project_root: Projekt-Root Fixture

    Returns:
        Path zur default.yaml Config
    """
    return project_root / "config" / "default.yaml"
