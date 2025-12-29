"""Unit tests for GK1 data loader functionality.

Tests for GK1Summary and GK1Hit parsing from CSV files.
"""

from datetime import datetime
from pathlib import Path

import pytest

from kenobase.core.data_loader import (
    DataLoader,
    GameType,
    GK1Hit,
    GK1Summary,
)


@pytest.fixture
def loader() -> DataLoader:
    """Create a DataLoader instance."""
    return DataLoader()


@pytest.fixture
def gk1_summary_path() -> Path:
    """Path to GK1Summary test CSV."""
    return Path("Keno_GPTs/10-9_KGDaten_gefiltert.csv")


@pytest.fixture
def gk1_hit_path() -> Path:
    """Path to GK1Hit test CSV."""
    return Path("Keno_GPTs/10-9_Liste_GK1_Treffer.csv")


class TestGK1Summary:
    """Tests for GK1Summary model and parsing."""

    def test_load_gk1_summary_auto_detect(
        self, loader: DataLoader, gk1_summary_path: Path
    ) -> None:
        """Test that GK1Summary format is auto-detected."""
        if not gk1_summary_path.exists():
            pytest.skip("Test CSV not found")

        results = loader.load(gk1_summary_path)
        assert len(results) > 0
        assert all(isinstance(r, GK1Summary) for r in results)

    def test_load_gk1_summary_count(
        self, loader: DataLoader, gk1_summary_path: Path
    ) -> None:
        """Test that correct number of records are loaded."""
        if not gk1_summary_path.exists():
            pytest.skip("Test CSV not found")

        results = loader.load(gk1_summary_path)
        # CSV has 20 data rows (21 lines including header, last line is empty)
        assert len(results) == 20

    def test_gk1_summary_fields(
        self, loader: DataLoader, gk1_summary_path: Path
    ) -> None:
        """Test that GK1Summary fields are correctly parsed."""
        if not gk1_summary_path.exists():
            pytest.skip("Test CSV not found")

        results = loader.load(gk1_summary_path)
        first = results[0]

        assert first.datum == datetime(2022, 1, 31)
        assert first.keno_typ == 10
        assert first.anzahl_gewinner == 10
        assert first.vergangene_tage == 0

    def test_gk1_summary_keno_typ_validation(self) -> None:
        """Test that Keno-Typ validation works."""
        # Valid types
        GK1Summary(
            datum=datetime.now(),
            keno_typ=9,
            anzahl_gewinner=1,
            vergangene_tage=0,
        )
        GK1Summary(
            datum=datetime.now(),
            keno_typ=10,
            anzahl_gewinner=1,
            vergangene_tage=0,
        )

        # Invalid type
        with pytest.raises(ValueError, match="Keno-Typ must be 9 or 10"):
            GK1Summary(
                datum=datetime.now(),
                keno_typ=8,
                anzahl_gewinner=1,
                vergangene_tage=0,
            )


class TestGK1Hit:
    """Tests for GK1Hit model and parsing."""

    def test_load_gk1_hit_auto_detect(
        self, loader: DataLoader, gk1_hit_path: Path
    ) -> None:
        """Test that GK1Hit format is auto-detected."""
        if not gk1_hit_path.exists():
            pytest.skip("Test CSV not found")

        results = loader.load(gk1_hit_path)
        assert len(results) > 0
        assert all(isinstance(r, GK1Hit) for r in results)

    def test_load_gk1_hit_count(
        self, loader: DataLoader, gk1_hit_path: Path
    ) -> None:
        """Test that correct number of records are loaded."""
        if not gk1_hit_path.exists():
            pytest.skip("Test CSV not found")

        results = loader.load(gk1_hit_path)
        # CSV has 4 data rows
        assert len(results) == 4

    def test_gk1_hit_fields(
        self, loader: DataLoader, gk1_hit_path: Path
    ) -> None:
        """Test that GK1Hit fields are correctly parsed."""
        if not gk1_hit_path.exists():
            pytest.skip("Test CSV not found")

        results = loader.load(gk1_hit_path)
        first = results[0]

        assert first.datum == datetime(2022, 7, 24)
        assert first.keno_typ == 9
        assert first.anzahl_gewinner == 5
        assert first.vergangene_tage == 57
        assert first.date_check == datetime(2023, 10, 10)
        assert first.anzahl_treffer == 6
        # Numbers are sorted
        assert first.numbers == [3, 9, 26, 33, 51, 58]

    def test_gk1_hit_numbers_validation(self) -> None:
        """Test that numbers validation works."""
        # Valid numbers
        hit = GK1Hit(
            datum=datetime.now(),
            keno_typ=10,
            anzahl_gewinner=1,
            vergangene_tage=0,
            date_check=datetime.now(),
            anzahl_treffer=6,
            numbers=[1, 2, 3, 4, 5, 6],
        )
        assert hit.numbers == [1, 2, 3, 4, 5, 6]

        # Wrong count
        with pytest.raises(ValueError, match="Expected 6 numbers"):
            GK1Hit(
                datum=datetime.now(),
                keno_typ=10,
                anzahl_gewinner=1,
                vergangene_tage=0,
                date_check=datetime.now(),
                anzahl_treffer=5,
                numbers=[1, 2, 3, 4, 5],
            )

        # Number out of range
        with pytest.raises(ValueError, match="between 1 and 70"):
            GK1Hit(
                datum=datetime.now(),
                keno_typ=10,
                anzahl_gewinner=1,
                vergangene_tage=0,
                date_check=datetime.now(),
                anzahl_treffer=6,
                numbers=[0, 2, 3, 4, 5, 6],
            )


class TestFormatDetection:
    """Tests for format auto-detection."""

    def test_detect_gk1_summary(
        self, loader: DataLoader, gk1_summary_path: Path
    ) -> None:
        """Test GK1Summary format detection."""
        if not gk1_summary_path.exists():
            pytest.skip("Test CSV not found")

        format_info = loader._detect_format(gk1_summary_path, "utf-8")
        assert format_info.game_type == GameType.GK1_SUMMARY
        assert format_info.delimiter == ","

    def test_detect_gk1_hit(
        self, loader: DataLoader, gk1_hit_path: Path
    ) -> None:
        """Test GK1Hit format detection."""
        if not gk1_hit_path.exists():
            pytest.skip("Test CSV not found")

        format_info = loader._detect_format(gk1_hit_path, "utf-8")
        assert format_info.game_type == GameType.GK1_HIT
        assert format_info.delimiter == ","
