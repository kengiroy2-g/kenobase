"""Unit Tests fuer kenobase.core.data_loader.

Testet alle Parser-Funktionen und Format-Erkennung fuer:
- KENO (22 Spalten, Semikolon)
- EuroJackpot (Spalten 1-7 nach Datum)
- Lotto Alt (7 Spalten, Komma)
- Lotto Neu (Semikolon, separate Zahlen-Spalten)
"""

from datetime import datetime
from pathlib import Path

import pytest

from kenobase.core.data_loader import (
    DataLoader,
    DrawResult,
    GameType,
    FormatInfo,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def loader() -> DataLoader:
    """Standard DataLoader Instanz."""
    return DataLoader()


@pytest.fixture
def fixtures_dir() -> Path:
    """Pfad zum fixtures Verzeichnis."""
    return Path(__file__).parent.parent / "fixtures"


# ============================================================================
# DrawResult Tests
# ============================================================================

class TestDrawResult:
    """Tests fuer DrawResult Pydantic Model."""

    def test_create_valid_result(self):
        """Test: Valides DrawResult erstellen."""
        result = DrawResult(
            date=datetime(2024, 1, 1),
            numbers=[1, 2, 3, 4, 5, 6],
            bonus=[7],
            game_type=GameType.LOTTO,
        )
        assert result.date == datetime(2024, 1, 1)
        assert result.numbers == [1, 2, 3, 4, 5, 6]  # sorted
        assert result.bonus == [7]
        assert result.game_type == GameType.LOTTO

    def test_numbers_are_sorted(self):
        """Test: Zahlen werden automatisch sortiert."""
        result = DrawResult(
            date=datetime(2024, 1, 1),
            numbers=[6, 3, 1, 4, 2, 5],
            game_type=GameType.LOTTO,
        )
        assert result.numbers == [1, 2, 3, 4, 5, 6]

    def test_invalid_negative_number(self):
        """Test: Negative Zahlen werden abgelehnt."""
        with pytest.raises(ValueError, match="positive"):
            DrawResult(
                date=datetime(2024, 1, 1),
                numbers=[1, 2, -3, 4, 5, 6],
                game_type=GameType.LOTTO,
            )

    def test_empty_bonus_default(self):
        """Test: Leerer Bonus ist Standard."""
        result = DrawResult(
            date=datetime(2024, 1, 1),
            numbers=[1, 2, 3],
            game_type=GameType.KENO,
        )
        assert result.bonus == []

    def test_metadata_default(self):
        """Test: Leeres Metadata ist Standard."""
        result = DrawResult(
            date=datetime(2024, 1, 1),
            numbers=[1, 2, 3],
            game_type=GameType.KENO,
        )
        assert result.metadata == {}


# ============================================================================
# Format Detection Tests
# ============================================================================

class TestFormatDetection:
    """Tests fuer automatische Format-Erkennung."""

    def test_detect_keno_format(self, loader: DataLoader, fixtures_dir: Path):
        """Test: KENO Format wird korrekt erkannt."""
        path = fixtures_dir / "keno_sample.csv"
        format_info = loader._detect_format(path, "utf-8")

        assert format_info.game_type == GameType.KENO
        assert format_info.delimiter == ";"

    def test_detect_eurojackpot_format(self, loader: DataLoader, fixtures_dir: Path):
        """Test: EuroJackpot Format wird korrekt erkannt."""
        path = fixtures_dir / "eurojackpot_sample.csv"
        format_info = loader._detect_format(path, "utf-8")

        assert format_info.game_type == GameType.EUROJACKPOT
        assert format_info.delimiter == ";"

    def test_detect_lotto_old_format(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Altes Lotto Format wird korrekt erkannt."""
        path = fixtures_dir / "lotto_old_sample.csv"
        format_info = loader._detect_format(path, "utf-8")

        assert format_info.game_type == GameType.LOTTO
        assert format_info.delimiter == ","

    def test_detect_lotto_new_format(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Neues Lotto Format wird korrekt erkannt."""
        path = fixtures_dir / "lotto_new_sample.csv"
        format_info = loader._detect_format(path, "utf-8")

        assert format_info.game_type == GameType.LOTTO
        assert format_info.delimiter == ";"


# ============================================================================
# KENO Parser Tests
# ============================================================================

class TestKenoParser:
    """Tests fuer KENO CSV Parser."""

    def test_load_keno_sample(self, loader: DataLoader, fixtures_dir: Path):
        """Test: KENO Sample wird korrekt geladen."""
        path = fixtures_dir / "keno_sample.csv"
        results = loader.load(path)

        assert len(results) == 3
        assert all(r.game_type == GameType.KENO for r in results)

    def test_keno_has_20_numbers(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Jede KENO Ziehung hat 20 Zahlen."""
        path = fixtures_dir / "keno_sample.csv"
        results = loader.load(path)

        for r in results:
            assert len(r.numbers) == 20

    def test_keno_first_draw(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Erste KENO Ziehung hat korrekte Werte."""
        path = fixtures_dir / "keno_sample.csv"
        results = loader.load(path)

        first = results[0]
        assert first.date == datetime(2018, 1, 1)
        # Numbers are sorted, original: 29,51,28,1,50,27,34,32,21,63,61,26,42,68,48,65,6,19,64,11
        assert 1 in first.numbers
        assert 68 in first.numbers
        assert first.bonus == [32646]  # Plus5

    def test_keno_metadata(self, loader: DataLoader, fixtures_dir: Path):
        """Test: KENO Metadata wird korrekt geparsed."""
        path = fixtures_dir / "keno_sample.csv"
        results = loader.load(path)

        assert "spieleinsatz" in results[0].metadata
        assert results[0].metadata["spieleinsatz"] == "304.198,00"

    def test_keno_preserves_numbers_ordered(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Original-Reihenfolge (Positionen) wird in metadata gespeichert."""
        path = fixtures_dir / "keno_sample.csv"
        results = loader.load(path)

        first = results[0]
        assert first.metadata.get("numbers_ordered") == [
            29,
            51,
            28,
            1,
            50,
            27,
            34,
            32,
            21,
            63,
            61,
            26,
            42,
            68,
            48,
            65,
            6,
            19,
            64,
            11,
        ]
        # DrawResult.numbers bleibt absichtlich sortiert (legacy behavior).
        assert first.numbers == sorted(first.metadata["numbers_ordered"])


# ============================================================================
# EuroJackpot Parser Tests
# ============================================================================

class TestEuroJackpotParser:
    """Tests fuer EuroJackpot CSV Parser."""

    def test_load_eurojackpot_sample(self, loader: DataLoader, fixtures_dir: Path):
        """Test: EuroJackpot Sample wird korrekt geladen."""
        path = fixtures_dir / "eurojackpot_sample.csv"
        results = loader.load(path)

        assert len(results) == 3
        assert all(r.game_type == GameType.EUROJACKPOT for r in results)

    def test_eurojackpot_has_5_numbers(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Jede EuroJackpot Ziehung hat 5 Hauptzahlen."""
        path = fixtures_dir / "eurojackpot_sample.csv"
        results = loader.load(path)

        for r in results:
            assert len(r.numbers) == 5

    def test_eurojackpot_has_2_eurozahlen(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Jede EuroJackpot Ziehung hat 2 EuroZahlen."""
        path = fixtures_dir / "eurojackpot_sample.csv"
        results = loader.load(path)

        for r in results:
            assert len(r.bonus) == 2

    def test_eurojackpot_first_draw(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Erste EuroJackpot Ziehung hat korrekte Werte."""
        path = fixtures_dir / "eurojackpot_sample.csv"
        results = loader.load(path)

        first = results[0]
        assert first.date == datetime(2018, 1, 5)
        # Numbers: 40,2,38,45,7 -> sorted: 2,7,38,40,45
        assert first.numbers == [2, 7, 38, 40, 45]
        # EuroZahlen: 10,7
        assert first.bonus == [10, 7]


# ============================================================================
# Lotto Parser Tests
# ============================================================================

class TestLottoOldParser:
    """Tests fuer altes Lotto CSV Format (ab-1955)."""

    def test_load_lotto_old_sample(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Altes Lotto Sample wird korrekt geladen."""
        path = fixtures_dir / "lotto_old_sample.csv"
        results = loader.load(path)

        assert len(results) == 3
        assert all(r.game_type == GameType.LOTTO for r in results)

    def test_lotto_old_has_6_numbers(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Jede Lotto Ziehung hat 6 Zahlen."""
        path = fixtures_dir / "lotto_old_sample.csv"
        results = loader.load(path)

        for r in results:
            assert len(r.numbers) == 6

    def test_lotto_old_first_draw(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Erste Lotto Ziehung (alt) hat korrekte Werte."""
        path = fixtures_dir / "lotto_old_sample.csv"
        results = loader.load(path)

        first = results[0]
        assert first.date == datetime(2024, 2, 7)
        assert first.numbers == [1, 8, 15, 19, 26, 31]
        assert first.bonus == []


class TestLottoNewParser:
    """Tests fuer neues Lotto CSV Format (ab-2018)."""

    def test_load_lotto_new_sample(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Neues Lotto Sample wird korrekt geladen."""
        path = fixtures_dir / "lotto_new_sample.csv"
        results = loader.load(path)

        assert len(results) == 3
        assert all(r.game_type == GameType.LOTTO for r in results)

    def test_lotto_new_has_6_numbers(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Jede Lotto Ziehung (neu) hat 6 Zahlen."""
        path = fixtures_dir / "lotto_new_sample.csv"
        results = loader.load(path)

        for r in results:
            assert len(r.numbers) == 6

    def test_lotto_new_first_draw(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Erste Lotto Ziehung (neu) hat korrekte Werte."""
        path = fixtures_dir / "lotto_new_sample.csv"
        results = loader.load(path)

        first = results[0]
        assert first.date == datetime(2018, 1, 3)
        # Numbers: 45,10,34,31,15,35 -> sorted: 10,15,31,34,35,45
        assert first.numbers == [10, 15, 31, 34, 35, 45]


class TestLottoArchivParser:
    """Tests fuer Lotto Archiv Format (bereinigt, ISO8601 + dash-separated)."""

    def test_load_lotto_archiv_sample(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Lotto Archiv Sample wird korrekt geladen."""
        path = fixtures_dir / "lotto_archiv_sample.csv"
        results = loader.load(path)

        assert len(results) == 3
        assert all(r.game_type == GameType.LOTTO for r in results)

    def test_lotto_archiv_has_6_numbers(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Jede Lotto Archiv Ziehung hat 6 Zahlen."""
        path = fixtures_dir / "lotto_archiv_sample.csv"
        results = loader.load(path)

        for r in results:
            assert len(r.numbers) == 6

    def test_lotto_archiv_first_draw(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Erste Lotto Archiv Ziehung hat korrekte Werte."""
        path = fixtures_dir / "lotto_archiv_sample.csv"
        results = loader.load(path)

        first = results[0]
        # ISO8601: 2024-02-07T00:00:00Z
        assert first.date == datetime(2024, 2, 7)
        # Numbers: 1-8-15-19-26-31 -> sorted: 1,8,15,19,26,31
        assert first.numbers == [1, 8, 15, 19, 26, 31]
        assert first.bonus == []
        assert first.metadata.get("format") == "archiv"

    def test_lotto_archiv_iso8601_parsing(self, loader: DataLoader, fixtures_dir: Path):
        """Test: ISO8601 Datum wird korrekt geparsed."""
        path = fixtures_dir / "lotto_archiv_sample.csv"
        results = loader.load(path)

        # Check all dates are parsed correctly
        expected_dates = [
            datetime(2024, 2, 7),
            datetime(2024, 1, 31),
            datetime(2024, 1, 24),
        ]
        actual_dates = [r.date for r in results]
        assert actual_dates == expected_dates


# ============================================================================
# DataFrame Conversion Tests
# ============================================================================

class TestDataFrameConversion:
    """Tests fuer DataFrame Konvertierung."""

    def test_to_dataframe(self, loader: DataLoader, fixtures_dir: Path):
        """Test: DrawResults werden korrekt zu DataFrame konvertiert."""
        path = fixtures_dir / "keno_sample.csv"
        results = loader.load(path)
        df = loader.to_dataframe(results)

        assert len(df) == 3
        assert "numbers" in df.columns
        assert "bonus" in df.columns
        assert "game_type" in df.columns
        assert df.index.name == "date"

    def test_to_dataframe_sorted_by_date(self, loader: DataLoader, fixtures_dir: Path):
        """Test: DataFrame ist nach Datum sortiert."""
        path = fixtures_dir / "keno_sample.csv"
        results = loader.load(path)
        df = loader.to_dataframe(results)

        dates = list(df.index)
        assert dates == sorted(dates)

    def test_load_as_dataframe(self, loader: DataLoader, fixtures_dir: Path):
        """Test: load_as_dataframe() Convenience-Methode."""
        path = fixtures_dir / "keno_sample.csv"
        df = loader.load_as_dataframe(path)

        assert len(df) == 3
        assert "numbers" in df.columns

    def test_empty_results_to_dataframe(self, loader: DataLoader):
        """Test: Leere Resultate ergeben leeren DataFrame."""
        df = loader.to_dataframe([])
        assert df.empty


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests fuer Edge Cases."""

    def test_file_not_found(self, loader: DataLoader):
        """Test: FileNotFoundError bei fehlender Datei."""
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent_file.csv")

    def test_force_game_type(self, loader: DataLoader, fixtures_dir: Path):
        """Test: Game Type kann erzwungen werden."""
        path = fixtures_dir / "lotto_old_sample.csv"
        results = loader.load(path, game_type=GameType.LOTTO)

        assert all(r.game_type == GameType.LOTTO for r in results)


# ============================================================================
# Integration with Real Data (optional)
# ============================================================================

class TestRealDataIntegration:
    """Integration Tests mit echten Daten (wenn verfuegbar)."""

    @pytest.fixture
    def real_data_dir(self) -> Path:
        """Pfad zu echten Daten."""
        return Path("Keno_GPTs/Daten")

    def test_load_real_keno_data(self, loader: DataLoader, real_data_dir: Path):
        """Test: Echte KENO Daten laden (wenn verfuegbar)."""
        path = real_data_dir / "KENO_Stats_ab-2018.csv"
        if not path.exists():
            pytest.skip("Real KENO data not available")

        results = loader.load(path)
        assert len(results) > 100  # Mindestens 100 Ziehungen erwartet
        assert all(len(r.numbers) == 20 for r in results)

    def test_load_real_eurojackpot_data(self, loader: DataLoader, real_data_dir: Path):
        """Test: Echte EuroJackpot Daten laden (wenn verfuegbar)."""
        path = real_data_dir / "EuroJackpot_Stats_ab-2018.csv"
        if not path.exists():
            pytest.skip("Real EuroJackpot data not available")

        results = loader.load(path)
        assert len(results) > 50  # Mindestens 50 Ziehungen erwartet
        assert all(len(r.numbers) == 5 for r in results)
        assert all(len(r.bonus) == 2 for r in results)

    def test_load_real_lotto_old_data(self, loader: DataLoader, real_data_dir: Path):
        """Test: Echte Lotto Archiv Daten laden (wenn verfuegbar)."""
        path = real_data_dir / "Lotto_Archiv_ab-1955.csv"
        if not path.exists():
            pytest.skip("Real Lotto archive data not available")

        results = loader.load(path)
        assert len(results) > 100
        assert all(len(r.numbers) == 6 for r in results)

    def test_load_real_lotto_new_data(self, loader: DataLoader, real_data_dir: Path):
        """Test: Echte Lotto Stats Daten laden (wenn verfuegbar)."""
        path = real_data_dir / "lotto_Stats_ab-2018.csv"
        if not path.exists():
            pytest.skip("Real Lotto stats data not available")

        results = loader.load(path)
        assert len(results) > 50
        assert all(len(r.numbers) == 6 for r in results)

    def test_load_real_lotto_archiv_data(self, loader: DataLoader):
        """Test: Echte Lotto Archiv Daten laden (wenn verfuegbar)."""
        path = Path("data/raw/lotto/Lotto_archiv_bereinigt.csv")
        if not path.exists():
            pytest.skip("Real Lotto archiv data not available")

        results = loader.load(path)
        assert len(results) > 100
        assert all(len(r.numbers) == 6 for r in results)
        assert all(r.metadata.get("format") == "archiv" for r in results)
