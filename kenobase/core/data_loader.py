"""Kenobase Data Loader - Multi-Format CSV Parser mit Auto-Erkennung.

Dieses Modul implementiert den Data Loader fuer Kenobase V2.0.
Unterstuetzte Formate:
- KENO: 22 Spalten, Semikolon, Zahlen in Keno_Z1-Keno_Z20
- EuroJackpot: Semikolon, 5 Hauptzahlen + 2 EuroZahlen in Spalten 1-7 nach Datum
- Lotto Alt (ab-1955): 7 Spalten, Komma, z1-z6
- Lotto Neu (ab-2018): Semikolon, Gewinnzahlen als separate Spalten

Usage:
    from kenobase.core.data_loader import DataLoader, DrawResult

    loader = DataLoader()
    results = loader.load("path/to/data.csv")
    df = loader.to_dataframe(results)
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class GameType(str, Enum):
    """Unterstuetzte Spieltypen."""

    KENO = "keno"
    EUROJACKPOT = "eurojackpot"
    LOTTO = "lotto"
    UNKNOWN = "unknown"


class DrawResult(BaseModel):
    """Ergebnis einer einzelnen Ziehung.

    Attributes:
        date: Datum der Ziehung
        numbers: Gezogene Hauptzahlen (sortiert)
        bonus: Bonuszahlen (EuroZahlen, Superzahl, Plus5)
        game_type: Spieltyp (keno, eurojackpot, lotto)
        metadata: Zusaetzliche Daten (Spieleinsatz, etc.)
    """

    date: datetime
    numbers: list[int]
    bonus: list[int] = Field(default_factory=list)
    game_type: GameType
    metadata: dict = Field(default_factory=dict)

    @field_validator("numbers")
    @classmethod
    def validate_numbers(cls, v: list[int]) -> list[int]:
        """Validiert dass Zahlen positiv sind."""
        if not all(n > 0 for n in v):
            raise ValueError("All numbers must be positive")
        return sorted(v)

    @field_validator("bonus")
    @classmethod
    def validate_bonus(cls, v: list[int]) -> list[int]:
        """Validiert dass Bonuszahlen nicht-negativ sind."""
        if not all(n >= 0 for n in v):
            raise ValueError("All bonus numbers must be non-negative")
        return v

    model_config = ConfigDict(use_enum_values=True)


@dataclass
class FormatInfo:
    """Erkannte Format-Informationen."""

    game_type: GameType
    delimiter: str
    date_format: str
    encoding: str


class DataLoader:
    """Multi-Format Data Loader fuer Lottozahlen-CSVs.

    Automatische Format-Erkennung basierend auf Header-Inspektion.
    Unterstuetzt KENO, EuroJackpot und Lotto in verschiedenen Formaten.

    Example:
        >>> loader = DataLoader()
        >>> results = loader.load("data/KENO_Stats_ab-2018.csv")
        >>> len(results)
        1234
        >>> results[0].game_type
        'keno'
    """

    # Known header patterns for format detection
    KENO_HEADERS = {"Datum", "Keno_Z1", "Keno_Z2", "Keno_Z20", "Keno_Plus5"}
    EUROJACKPOT_HEADERS = {"Datum", "5 aus 50", "EZ", "Spieleinsatz"}
    LOTTO_OLD_HEADERS = {"Datum", "z1", "z2", "z3", "z4", "z5", "z6"}
    LOTTO_NEW_HEADERS = {"Datum", "Gewinnzahlen", "ZZ", "Spiel77", "Super6"}

    def __init__(
        self,
        default_encoding: str = "utf-8",
        default_date_format: str = "%d.%m.%Y",
    ) -> None:
        """Initialisiert DataLoader.

        Args:
            default_encoding: Standard-Encoding fuer CSV-Dateien
            default_date_format: Standard-Datumsformat
        """
        self.default_encoding = default_encoding
        self.default_date_format = default_date_format

    def load(
        self,
        path: str | Path,
        game_type: Optional[GameType] = None,
        encoding: Optional[str] = None,
    ) -> list[DrawResult]:
        """Laedt Ziehungsdaten aus CSV-Datei.

        Args:
            path: Pfad zur CSV-Datei
            game_type: Optionaler Spieltyp (wird automatisch erkannt wenn None)
            encoding: Optionales Encoding (Standard: utf-8)

        Returns:
            Liste von DrawResult-Objekten

        Raises:
            FileNotFoundError: Wenn Datei nicht existiert
            ValueError: Wenn Format nicht erkannt werden kann
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        enc = encoding or self.default_encoding
        format_info = self._detect_format(file_path, enc)

        if game_type:
            format_info.game_type = game_type

        logger.info(
            f"Loading {file_path.name} as {format_info.game_type.value} "
            f"(delimiter='{format_info.delimiter}')"
        )

        parser_map = {
            GameType.KENO: self._parse_keno,
            GameType.EUROJACKPOT: self._parse_eurojackpot,
            GameType.LOTTO: self._parse_lotto,
        }

        parser = parser_map.get(format_info.game_type)
        if not parser:
            raise ValueError(f"Unknown game type: {format_info.game_type}")

        return parser(file_path, format_info)

    def _detect_format(self, path: Path, encoding: str) -> FormatInfo:
        """Erkennt CSV-Format anhand des Headers.

        Args:
            path: Pfad zur CSV-Datei
            encoding: Encoding fuer Datei-Lesen

        Returns:
            FormatInfo mit erkanntem Spieltyp und Delimiter
        """
        with open(path, "r", encoding=encoding) as f:
            first_line = f.readline().strip()

        # Detect delimiter
        if ";" in first_line:
            delimiter = ";"
        elif "," in first_line:
            delimiter = ","
        else:
            delimiter = ";"  # Default

        # Clean header and split
        header_parts = {h.strip() for h in first_line.split(delimiter)}

        # Detect game type based on header patterns
        if self.KENO_HEADERS.issubset(header_parts) or "Keno_Z1" in header_parts:
            game_type = GameType.KENO
        elif "5 aus 50" in first_line or "EZ" in header_parts:
            game_type = GameType.EUROJACKPOT
        elif "S1" in header_parts and "S2" in header_parts and "z1" in header_parts:
            # Bereinigt EuroJackpot format: Datum;S1;S2;z1;z2;z3;z4;z5
            game_type = GameType.EUROJACKPOT
        elif self.LOTTO_OLD_HEADERS.issubset(header_parts):
            game_type = GameType.LOTTO
        elif "Gewinnzahlen" in first_line:
            game_type = GameType.LOTTO
        else:
            logger.warning(f"Could not detect format for {path.name}, defaulting to LOTTO")
            game_type = GameType.LOTTO

        return FormatInfo(
            game_type=game_type,
            delimiter=delimiter,
            date_format=self.default_date_format,
            encoding=encoding,
        )

    def _parse_keno(self, path: Path, format_info: FormatInfo) -> list[DrawResult]:
        """Parst KENO CSV-Format.

        Format: Datum;Keno_Z1;...;Keno_Z20;Keno_Plus5;Keno_Spieleinsatz
        22 Spalten, Semikolon-Delimiter

        Args:
            path: Pfad zur CSV-Datei
            format_info: Format-Informationen

        Returns:
            Liste von DrawResult-Objekten
        """
        results: list[DrawResult] = []

        with open(path, "r", encoding=format_info.encoding) as f:
            reader = csv.DictReader(f, delimiter=format_info.delimiter)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Clean whitespace from keys and values
                    row = {k.strip(): v.strip() if v else "" for k, v in row.items() if k}

                    # Parse date
                    date_str = row.get("Datum", "")
                    if not date_str:
                        continue
                    date = datetime.strptime(date_str, format_info.date_format)

                    # Parse 20 KENO numbers
                    numbers = []
                    for i in range(1, 21):
                        key = f"Keno_Z{i}"
                        if key in row and row[key]:
                            numbers.append(int(row[key]))

                    if len(numbers) != 20:
                        logger.warning(
                            f"Row {row_num}: Expected 20 numbers, got {len(numbers)}"
                        )
                        continue

                    # Parse Plus5 as bonus
                    bonus = []
                    plus5 = row.get("Keno_Plus5", "")
                    if plus5:
                        bonus.append(int(plus5))

                    # Parse metadata
                    metadata = {}
                    spieleinsatz = row.get("Keno_Spieleinsatz", "")
                    if spieleinsatz:
                        metadata["spieleinsatz"] = spieleinsatz

                    results.append(
                        DrawResult(
                            date=date,
                            numbers=numbers,
                            bonus=bonus,
                            game_type=GameType.KENO,
                            metadata=metadata,
                        )
                    )

                except (ValueError, KeyError) as e:
                    logger.warning(f"Row {row_num}: Parse error - {e}")
                    continue

        logger.info(f"Loaded {len(results)} KENO draws from {path.name}")
        return results

    def _parse_eurojackpot(
        self, path: Path, format_info: FormatInfo
    ) -> list[DrawResult]:
        """Parst EuroJackpot CSV-Format.

        Zwei Formate werden unterstuetzt:
        - Standard: Datum;Z1;Z2;Z3;Z4;Z5;EZ1;EZ2;... (cols 1-5=main, 6-7=euro)
        - Bereinigt: Datum;S1;S2;z1;z2;z3;z4;z5 (cols 1-2=euro, 3-7=main)

        Args:
            path: Pfad zur CSV-Datei
            format_info: Format-Informationen

        Returns:
            Liste von DrawResult-Objekten
        """
        results: list[DrawResult] = []

        with open(path, "r", encoding=format_info.encoding) as f:
            # Read raw lines to handle the complex header
            lines = f.readlines()

        if not lines:
            return results

        # Parse header to understand column positions
        header_line = lines[0].strip()
        headers = [h.strip() for h in header_line.split(format_info.delimiter)]

        # Detect bereinigt format: Datum;S1;S2;z1;z2;z3;z4;z5
        # S1,S2 = EuroZahlen (bonus), z1-z5 = Hauptzahlen
        is_bereinigt = "S1" in headers and "z1" in headers

        for row_num, line in enumerate(lines[1:], start=2):
            try:
                values = [v.strip() for v in line.strip().split(format_info.delimiter)]

                min_cols = 8 if not is_bereinigt else 8
                if len(values) < min_cols:
                    continue

                # Parse date (first column)
                date_str = values[0]
                if not date_str:
                    continue
                date = datetime.strptime(date_str, format_info.date_format)

                if is_bereinigt:
                    # Bereinigt format: S1,S2 are EuroZahlen (cols 1-2), z1-z5 are main (cols 3-7)
                    bonus = []
                    for i in range(1, 3):
                        if values[i]:
                            bonus.append(int(values[i]))

                    numbers = []
                    for i in range(3, 8):
                        if values[i]:
                            numbers.append(int(values[i]))
                else:
                    # Standard format: cols 1-5 main, 6-7 euro
                    numbers = []
                    for i in range(1, 6):
                        if values[i]:
                            numbers.append(int(values[i]))

                    bonus = []
                    for i in range(6, 8):
                        if i < len(values) and values[i]:
                            bonus.append(int(values[i]))

                if len(numbers) != 5:
                    logger.warning(
                        f"Row {row_num}: Expected 5 main numbers, got {len(numbers)}"
                    )
                    continue

                if len(bonus) != 2:
                    logger.warning(
                        f"Row {row_num}: Expected 2 euro numbers, got {len(bonus)}"
                    )

                # Parse metadata
                metadata = {}
                if is_bereinigt:
                    metadata["format"] = "bereinigt"
                else:
                    if len(values) > 8 and values[8]:
                        metadata["spieleinsatz"] = values[8]

                results.append(
                    DrawResult(
                        date=date,
                        numbers=numbers,
                        bonus=bonus,
                        game_type=GameType.EUROJACKPOT,
                        metadata=metadata,
                    )
                )

            except (ValueError, IndexError) as e:
                logger.warning(f"Row {row_num}: Parse error - {e}")
                continue

        logger.info(f"Loaded {len(results)} EuroJackpot draws from {path.name}")
        return results

    def _parse_lotto(self, path: Path, format_info: FormatInfo) -> list[DrawResult]:
        """Parst Lotto CSV-Format (alt, neu, und archiv).

        Drei Formate werden unterstuetzt:
        - Alt (ab-1955): Datum,z1,z2,z3,z4,z5,z6 (Komma, 7 Spalten)
        - Neu (ab-2018): Datum;;Z1;Z2;Z3;Z4;Z5;Z6;ZZ;... (Semikolon, Gewinnzahlen separiert)
        - Archiv (bereinigt): "ISO8601,1-2-3-4-5-6" (Quoted, dash-separated numbers)

        Args:
            path: Pfad zur CSV-Datei
            format_info: Format-Informationen

        Returns:
            Liste von DrawResult-Objekten
        """
        # Detect which Lotto format
        with open(path, "r", encoding=format_info.encoding) as f:
            first_line = f.readline().strip()

        # Check for archiv format: quoted line with ISO8601 date and dash-separated numbers
        # Example: "2024-02-07T00:00:00Z,1-8-15-19-26-31"
        if first_line.startswith('"') and "T00:00:00Z" in first_line and "-" in first_line:
            return self._parse_lotto_archiv(path, format_info)
        elif "z1" in first_line.lower() and format_info.delimiter == ",":
            return self._parse_lotto_old(path, format_info)
        else:
            return self._parse_lotto_new(path, format_info)

    def _parse_lotto_old(self, path: Path, format_info: FormatInfo) -> list[DrawResult]:
        """Parst altes Lotto-Format (Lotto_Archiv_ab-1955.csv).

        Format: Datum,z1,z2,z3,z4,z5,z6
        7 Spalten, Komma-Delimiter

        Args:
            path: Pfad zur CSV-Datei
            format_info: Format-Informationen

        Returns:
            Liste von DrawResult-Objekten
        """
        results: list[DrawResult] = []

        with open(path, "r", encoding=format_info.encoding) as f:
            reader = csv.DictReader(f, delimiter=format_info.delimiter)

            for row_num, row in enumerate(reader, start=2):
                try:
                    row = {k.strip(): v.strip() if v else "" for k, v in row.items() if k}

                    date_str = row.get("Datum", "")
                    if not date_str:
                        continue
                    date = datetime.strptime(date_str, format_info.date_format)

                    numbers = []
                    for i in range(1, 7):
                        key = f"z{i}"
                        if key in row and row[key]:
                            numbers.append(int(row[key]))

                    if len(numbers) != 6:
                        logger.warning(
                            f"Row {row_num}: Expected 6 numbers, got {len(numbers)}"
                        )
                        continue

                    results.append(
                        DrawResult(
                            date=date,
                            numbers=numbers,
                            bonus=[],
                            game_type=GameType.LOTTO,
                            metadata={"format": "old"},
                        )
                    )

                except (ValueError, KeyError) as e:
                    logger.warning(f"Row {row_num}: Parse error - {e}")
                    continue

        logger.info(f"Loaded {len(results)} Lotto draws (old format) from {path.name}")
        return results

    def _parse_lotto_new(self, path: Path, format_info: FormatInfo) -> list[DrawResult]:
        """Parst neues Lotto-Format (lotto_Stats_ab-2018.csv).

        Format: Datum;;Z1;Z2;Z3;Z4;Z5;Z6;ZZ;S;Spiel77;Super6;...
        Zahlen in separaten Spalten nach Datum (mit Leerspalte)

        Args:
            path: Pfad zur CSV-Datei
            format_info: Format-Informationen

        Returns:
            Liste von DrawResult-Objekten
        """
        results: list[DrawResult] = []

        with open(path, "r", encoding=format_info.encoding) as f:
            lines = f.readlines()

        if not lines:
            return results

        for row_num, line in enumerate(lines[1:], start=2):
            try:
                values = [v.strip() for v in line.strip().split(format_info.delimiter)]

                if len(values) < 10:
                    continue

                # Parse date
                date_str = values[0]
                if not date_str:
                    continue
                date = datetime.strptime(date_str, format_info.date_format)

                # Values[1] is often empty, numbers start at index 2
                # Format: Datum;;Z1;Z2;Z3;Z4;Z5;Z6;ZZ;S;...
                # Find 6 consecutive integers starting from column 2
                numbers = []
                start_idx = 2  # Skip Datum and empty column

                for i in range(start_idx, min(start_idx + 6, len(values))):
                    if values[i] and values[i].isdigit():
                        numbers.append(int(values[i]))

                if len(numbers) != 6:
                    # Try alternative: Gewinnzahlen column might be a string
                    logger.warning(
                        f"Row {row_num}: Expected 6 numbers, got {len(numbers)} - skipping"
                    )
                    continue

                # Parse Zusatzzahl (ZZ) as bonus - column after the 6 numbers
                bonus = []
                zz_idx = start_idx + 6  # Index for ZZ
                if zz_idx < len(values):
                    zz_val = values[zz_idx]
                    if zz_val and zz_val != "--" and zz_val != "--;":
                        try:
                            bonus.append(int(zz_val))
                        except ValueError:
                            pass

                # Parse metadata
                metadata = {"format": "new"}
                # Spiel77, Super6 are at later positions
                for label, idx in [("spieleinsatz", 12), ("spiel77", 10), ("super6", 11)]:
                    if idx < len(values) and values[idx]:
                        metadata[label] = values[idx]

                results.append(
                    DrawResult(
                        date=date,
                        numbers=numbers,
                        bonus=bonus,
                        game_type=GameType.LOTTO,
                        metadata=metadata,
                    )
                )

            except (ValueError, IndexError) as e:
                logger.warning(f"Row {row_num}: Parse error - {e}")
                continue

        logger.info(f"Loaded {len(results)} Lotto draws (new format) from {path.name}")
        return results

    def _parse_lotto_archiv(
        self, path: Path, format_info: FormatInfo
    ) -> list[DrawResult]:
        """Parst Lotto Archiv-Format (Lotto_archiv_bereinigt.csv).

        Format: "2024-02-07T00:00:00Z,1-8-15-19-26-31"
        - Quoted line
        - ISO8601 date with T00:00:00Z suffix
        - Dash-separated numbers
        - No header row

        Args:
            path: Pfad zur CSV-Datei
            format_info: Format-Informationen

        Returns:
            Liste von DrawResult-Objekten
        """
        results: list[DrawResult] = []

        with open(path, "r", encoding=format_info.encoding) as f:
            lines = f.readlines()

        for row_num, line in enumerate(lines, start=1):
            try:
                # Remove quotes and whitespace
                line = line.strip().strip('"')
                if not line:
                    continue

                # Split by comma to separate date and numbers
                parts = line.split(",")
                if len(parts) != 2:
                    logger.warning(f"Row {row_num}: Invalid format - expected date,numbers")
                    continue

                date_str, numbers_str = parts

                # Parse ISO8601 date: 2024-02-07T00:00:00Z
                date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

                # Parse dash-separated numbers: 1-8-15-19-26-31
                numbers = [int(n) for n in numbers_str.split("-") if n.strip()]

                if len(numbers) != 6:
                    logger.warning(
                        f"Row {row_num}: Expected 6 numbers, got {len(numbers)}"
                    )
                    continue

                results.append(
                    DrawResult(
                        date=date,
                        numbers=numbers,
                        bonus=[],
                        game_type=GameType.LOTTO,
                        metadata={"format": "archiv"},
                    )
                )

            except (ValueError, IndexError) as e:
                logger.warning(f"Row {row_num}: Parse error - {e}")
                continue

        logger.info(f"Loaded {len(results)} Lotto draws (archiv format) from {path.name}")
        return results

    def to_dataframe(self, results: list[DrawResult]) -> pd.DataFrame:
        """Konvertiert DrawResult-Liste zu Pandas DataFrame.

        Args:
            results: Liste von DrawResult-Objekten

        Returns:
            DataFrame mit Spalten: date, numbers, bonus, game_type, plus metadata
        """
        if not results:
            return pd.DataFrame()

        data = []
        for r in results:
            row = {
                "date": r.date,
                "numbers": r.numbers,
                "bonus": r.bonus,
                "game_type": r.game_type,
            }
            row.update(r.metadata)
            data.append(row)

        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        return df

    def load_as_dataframe(
        self,
        path: str | Path,
        game_type: Optional[GameType] = None,
        encoding: Optional[str] = None,
    ) -> pd.DataFrame:
        """Laedt CSV und gibt direkt DataFrame zurueck.

        Convenience-Methode die load() und to_dataframe() kombiniert.

        Args:
            path: Pfad zur CSV-Datei
            game_type: Optionaler Spieltyp
            encoding: Optionales Encoding

        Returns:
            DataFrame mit Ziehungsdaten
        """
        results = self.load(path, game_type, encoding)
        return self.to_dataframe(results)


__all__ = [
    "DataLoader",
    "DrawResult",
    "GameType",
    "FormatInfo",
]
