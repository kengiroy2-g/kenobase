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

from kenobase.core.regions import normalize_region

logger = logging.getLogger(__name__)


class GameType(str, Enum):
    """Unterstuetzte Spieltypen."""

    KENO = "keno"
    EUROJACKPOT = "eurojackpot"
    LOTTO = "lotto"
    GK1_SUMMARY = "gk1_summary"
    GK1_HIT = "gk1_hit"
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


class GK1Summary(BaseModel):
    """Gewinnklasse 1 Zusammenfassung.

    Modell fuer 10-9_KGDaten_gefiltert.csv.
    Enthaelt aggregierte GK1-Ereignisse ohne Zahlen.

    Attributes:
        datum: Datum der GK1-Ziehung
        keno_typ: Keno-Typ (9 oder 10)
        anzahl_gewinner: Anzahl der Gewinner
        vergangene_tage: Tage seit letztem GK1 Treffer
    """

    datum: datetime
    keno_typ: int
    anzahl_gewinner: int
    vergangene_tage: int

    @field_validator("keno_typ")
    @classmethod
    def validate_keno_typ(cls, v: int) -> int:
        """Validiert dass Keno-Typ 9 oder 10 ist."""
        if v not in (9, 10):
            raise ValueError(f"Keno-Typ must be 9 or 10, got {v}")
        return v

    @field_validator("anzahl_gewinner")
    @classmethod
    def validate_anzahl_gewinner(cls, v: int) -> int:
        """Validiert dass Anzahl Gewinner positiv ist."""
        if v < 1:
            raise ValueError(f"Anzahl Gewinner must be >= 1, got {v}")
        return v

    model_config = ConfigDict(use_enum_values=True)


class GK1Hit(BaseModel):
    """Gewinnklasse 1 Treffer mit Zahlen.

    Modell fuer 10-9_Liste_GK1_Treffer.csv.
    Enthaelt GK1-Ereignis mit gepruefter Kombination.

    Attributes:
        datum: Datum der Original-GK1-Ziehung
        keno_typ: Keno-Typ (9 oder 10)
        anzahl_gewinner: Anzahl der Gewinner
        vergangene_tage: Tage seit letztem GK1 Treffer
        date_check: Datum an dem die Kombination erneut geprueft wurde
        anzahl_treffer: Anzahl Treffer bei date_check
        numbers: Die 6 geprueften Zahlen (z1-z6)
    """

    datum: datetime
    keno_typ: int
    anzahl_gewinner: int
    vergangene_tage: int
    date_check: datetime
    anzahl_treffer: int
    numbers: list[int]

    @field_validator("keno_typ")
    @classmethod
    def validate_keno_typ(cls, v: int) -> int:
        """Validiert dass Keno-Typ 9 oder 10 ist."""
        if v not in (9, 10):
            raise ValueError(f"Keno-Typ must be 9 or 10, got {v}")
        return v

    @field_validator("numbers")
    @classmethod
    def validate_numbers(cls, v: list[int]) -> list[int]:
        """Validiert dass genau 6 positive Zahlen vorhanden sind."""
        if len(v) != 6:
            raise ValueError(f"Expected 6 numbers, got {len(v)}")
        if not all(1 <= n <= 70 for n in v):
            raise ValueError("All numbers must be between 1 and 70")
        return sorted(v)

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
    LOTTO_BEREINIGT_HEADERS = {"Datum", "L1", "L2", "L3", "L4", "L5", "L6"}
    GK1_SUMMARY_HEADERS = {"Datum", "Keno-Typ", "Anzahl der Gewinner"}
    GK1_HIT_HEADERS = {"Datum", "Keno-Typ", "Date_Check", "z1", "z2"}

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
            GameType.GK1_SUMMARY: self._parse_gk1_summary,
            GameType.GK1_HIT: self._parse_gk1_hit,
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
        # GK1 formats must be checked before LOTTO (both have z1-z6)
        if self.GK1_HIT_HEADERS.issubset(header_parts):
            # GK1Hit has Date_Check column (differentiator)
            game_type = GameType.GK1_HIT
        elif self.GK1_SUMMARY_HEADERS.issubset(header_parts) and "Date_Check" not in header_parts:
            # GK1Summary: has Keno-Typ but NOT Date_Check
            game_type = GameType.GK1_SUMMARY
        elif self.KENO_HEADERS.issubset(header_parts) or "Keno_Z1" in header_parts:
            game_type = GameType.KENO
        elif "5 aus 50" in first_line or "EZ" in header_parts:
            game_type = GameType.EUROJACKPOT
        elif "S1" in header_parts and "S2" in header_parts and "z1" in header_parts:
            # Bereinigt EuroJackpot format: Datum;S1;S2;z1;z2;z3;z4;z5
            game_type = GameType.EUROJACKPOT
        elif "E1" in header_parts and "Euro1" in header_parts:
            # EuroJackpot E-format: Datum;E1;E2;E3;E4;E5;Euro1;Euro2;...
            game_type = GameType.EUROJACKPOT
        elif self.LOTTO_BEREINIGT_HEADERS.issubset(header_parts):
            # Bereinigt Lotto format: Datum;L1;L2;L3;L4;L5;L6;...
            game_type = GameType.LOTTO
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

    @staticmethod
    def _extract_region_from_row(row: dict[str, str]) -> Optional[str]:
        """Extrahiert und normalisiert Region/Bundesland aus einer CSV-Zeile."""
        for key, value in row.items():
            key_lower = key.strip().lower()
            if key_lower in {"bundesland", "region", "state"} or "bundesland" in key_lower:
                region = normalize_region(value)
                if region:
                    return region
        return None

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

                    jackpot_candidates = [
                        row.get("Keno_Jackpot", ""),
                        row.get("Jackpot", ""),
                        row.get("Jackpot_Kl1", ""),
                    ]
                    for candidate in jackpot_candidates:
                        if candidate:
                            metadata["jackpot"] = candidate
                            break

                    # Preserve original draw order for position-based analyses.
                    metadata["numbers_ordered"] = list(numbers)

                    region = self._extract_region_from_row(row)
                    if region:
                        metadata["region"] = region

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

        Drei Formate werden unterstuetzt:
        - Standard: Datum;Z1;Z2;Z3;Z4;Z5;EZ1;EZ2;... (cols 1-5=main, 6-7=euro)
        - Bereinigt S: Datum;S1;S2;z1;z2;z3;z4;z5 (cols 1-2=euro, 3-7=main)
        - Bereinigt E: Datum;E1;E2;E3;E4;E5;Euro1;Euro2;... (cols 1-5=main, 6-7=euro)

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

        # Detect format variant
        # S-bereinigt: Datum;S1;S2;z1;z2;z3;z4;z5 (S1,S2 = EuroZahlen, z1-z5 = Hauptzahlen)
        is_s_bereinigt = "S1" in headers and "z1" in headers
        # E-bereinigt: Datum;E1;E2;E3;E4;E5;Euro1;Euro2;... (E1-E5 = Hauptzahlen, Euro1-2 = EuroZahlen)
        is_e_bereinigt = "E1" in headers and "Euro1" in headers

        for row_num, line in enumerate(lines[1:], start=2):
            try:
                values = [v.strip() for v in line.strip().split(format_info.delimiter)]

                if len(values) < 8:
                    continue

                # Parse date (first column)
                date_str = values[0]
                if not date_str:
                    continue
                date = datetime.strptime(date_str, format_info.date_format)

                if is_s_bereinigt:
                    # S-Bereinigt format: S1,S2 are EuroZahlen (cols 1-2), z1-z5 are main (cols 3-7)
                    bonus = []
                    for i in range(1, 3):
                        if values[i]:
                            bonus.append(int(values[i]))

                    numbers = []
                    for i in range(3, 8):
                        if values[i]:
                            numbers.append(int(values[i]))
                    metadata = {"format": "bereinigt_s"}

                elif is_e_bereinigt:
                    # E-Bereinigt format: E1-E5 are main (cols 1-5), Euro1-Euro2 are euro (cols 6-7)
                    numbers = []
                    for i in range(1, 6):
                        if values[i]:
                            numbers.append(int(values[i]))

                    bonus = []
                    for i in range(6, 8):
                        if i < len(values) and values[i]:
                            bonus.append(int(values[i]))
                    metadata = {"format": "bereinigt_e"}

                    # Capture additional metadata
                    if len(values) > 8 and values[8]:
                        metadata["spieleinsatz"] = values[8]
                    if len(values) > 9 and values[9]:
                        metadata["jackpot"] = values[9]

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

                    metadata = {}
                    if len(values) > 8 and values[8]:
                        metadata["spieleinsatz"] = values[8]

                if len(numbers) != 5:
                    logger.warning(
                        f"Row {row_num}: Expected 5 main numbers, got {len(numbers)}"
                    )
                    continue

                if len(bonus) != 2:
                    logger.warning(
                        f"Row {row_num}: Expected 2 euro numbers, got {len(bonus)}"
                    )

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
        """Parst Lotto CSV-Format (alt, neu, bereinigt, und archiv).

        Vier Formate werden unterstuetzt:
        - Alt (ab-1955): Datum,z1,z2,z3,z4,z5,z6 (Komma, 7 Spalten)
        - Neu (ab-2018): Datum;;Z1;Z2;Z3;Z4;Z5;Z6;ZZ;... (Semikolon, Gewinnzahlen separiert)
        - Bereinigt: Datum;L1;L2;L3;L4;L5;L6;Zusatzzahl;Superzahl;... (Semikolon)
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
        elif "L1" in first_line and "L6" in first_line:
            # Bereinigt format: Datum;L1;L2;L3;L4;L5;L6;...
            return self._parse_lotto_bereinigt(path, format_info)
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

    def _parse_lotto_bereinigt(
        self, path: Path, format_info: FormatInfo
    ) -> list[DrawResult]:
        """Parst Lotto Bereinigt-Format (LOTTO_ab_2022_bereinigt.csv).

        Format: Datum;L1;L2;L3;L4;L5;L6;Zusatzzahl;Superzahl;Spiel77;Super6;Spieleinsatz;Jackpot_Kl1
        L1-L6 sind die Hauptzahlen, Semikolon-Delimiter

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

                    # Parse L1-L6
                    numbers = []
                    for i in range(1, 7):
                        key = f"L{i}"
                        if key in row and row[key]:
                            numbers.append(int(row[key]))

                    if len(numbers) != 6:
                        logger.warning(
                            f"Row {row_num}: Expected 6 numbers, got {len(numbers)}"
                        )
                        continue

                    # Parse Zusatzzahl and Superzahl as bonus
                    bonus = []
                    zusatzzahl = row.get("Zusatzzahl", "")
                    if zusatzzahl and zusatzzahl.isdigit():
                        zz = int(zusatzzahl)
                        if zz > 0:  # Only add if non-zero
                            bonus.append(zz)

                    superzahl = row.get("Superzahl", "")
                    if superzahl and superzahl.isdigit():
                        sz = int(superzahl)
                        if sz > 0:  # Only add if non-zero
                            bonus.append(sz)

                    # Parse metadata
                    metadata = {"format": "bereinigt"}
                    for key in ["Spieleinsatz", "Jackpot_Kl1", "Spiel77", "Super6"]:
                        if key in row and row[key]:
                            metadata[key.lower()] = row[key]

                    results.append(
                        DrawResult(
                            date=date,
                            numbers=numbers,
                            bonus=bonus,
                            game_type=GameType.LOTTO,
                            metadata=metadata,
                        )
                    )

                except (ValueError, KeyError) as e:
                    logger.warning(f"Row {row_num}: Parse error - {e}")
                    continue

        logger.info(f"Loaded {len(results)} Lotto draws (bereinigt format) from {path.name}")
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

    def _parse_gk1_summary(
        self, path: Path, format_info: FormatInfo
    ) -> list[GK1Summary]:
        """Parst GK1Summary CSV-Format (10-9_KGDaten_gefiltert.csv).

        Format: Datum,Keno-Typ,Anzahl der Gewinner,Vergangene Tage seit dem letzten Gewinnklasse 1
        4 Spalten, Komma-Delimiter, deutsches Datumsformat

        Args:
            path: Pfad zur CSV-Datei
            format_info: Format-Informationen

        Returns:
            Liste von GK1Summary-Objekten
        """
        results: list[GK1Summary] = []

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
                    datum = datetime.strptime(date_str, format_info.date_format)

                    # Parse Keno-Typ
                    keno_typ_str = row.get("Keno-Typ", "")
                    if not keno_typ_str:
                        continue
                    keno_typ = int(keno_typ_str)

                    # Parse Anzahl der Gewinner (float in CSV, but we want int)
                    anzahl_str = row.get("Anzahl der Gewinner", "")
                    if not anzahl_str:
                        continue
                    anzahl_gewinner = int(float(anzahl_str))

                    # Parse Vergangene Tage
                    tage_str = row.get("Vergangene Tage seit dem letzten Gewinnklasse 1", "")
                    if not tage_str:
                        continue
                    vergangene_tage = int(float(tage_str))

                    results.append(
                        GK1Summary(
                            datum=datum,
                            keno_typ=keno_typ,
                            anzahl_gewinner=anzahl_gewinner,
                            vergangene_tage=vergangene_tage,
                        )
                    )

                except (ValueError, KeyError) as e:
                    logger.warning(f"Row {row_num}: Parse error - {e}")
                    continue

        logger.info(f"Loaded {len(results)} GK1Summary records from {path.name}")
        return results

    def _parse_gk1_hit(
        self, path: Path, format_info: FormatInfo
    ) -> list[GK1Hit]:
        """Parst GK1Hit CSV-Format (10-9_Liste_GK1_Treffer.csv).

        Format: Datum,Keno-Typ,Anzahl der Gewinner,Vergangene Tage...,Date_Check,Anzahl Treffer,z1,z2,z3,z4,z5,z6
        12 Spalten, Komma-Delimiter, deutsches Datumsformat

        Args:
            path: Pfad zur CSV-Datei
            format_info: Format-Informationen

        Returns:
            Liste von GK1Hit-Objekten
        """
        results: list[GK1Hit] = []

        with open(path, "r", encoding=format_info.encoding) as f:
            reader = csv.DictReader(f, delimiter=format_info.delimiter)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Clean whitespace from keys and values
                    row = {k.strip(): v.strip() if v else "" for k, v in row.items() if k}

                    # Parse datum
                    date_str = row.get("Datum", "")
                    if not date_str:
                        continue
                    datum = datetime.strptime(date_str, format_info.date_format)

                    # Parse Keno-Typ
                    keno_typ_str = row.get("Keno-Typ", "")
                    if not keno_typ_str:
                        continue
                    keno_typ = int(keno_typ_str)

                    # Parse Anzahl der Gewinner
                    anzahl_str = row.get("Anzahl der Gewinner", "")
                    if not anzahl_str:
                        continue
                    anzahl_gewinner = int(float(anzahl_str))

                    # Parse Vergangene Tage
                    tage_str = row.get("Vergangene Tage seit dem letzten Gewinnklasse 1", "")
                    if not tage_str:
                        continue
                    vergangene_tage = int(float(tage_str))

                    # Parse Date_Check
                    date_check_str = row.get("Date_Check", "")
                    if not date_check_str:
                        continue
                    date_check = datetime.strptime(date_check_str, format_info.date_format)

                    # Parse Anzahl Treffer
                    treffer_str = row.get("Anzahl Treffer", "")
                    if not treffer_str:
                        continue
                    anzahl_treffer = int(treffer_str)

                    # Parse z1-z6
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
                        GK1Hit(
                            datum=datum,
                            keno_typ=keno_typ,
                            anzahl_gewinner=anzahl_gewinner,
                            vergangene_tage=vergangene_tage,
                            date_check=date_check,
                            anzahl_treffer=anzahl_treffer,
                            numbers=numbers,
                        )
                    )

                except (ValueError, KeyError) as e:
                    logger.warning(f"Row {row_num}: Parse error - {e}")
                    continue

        logger.info(f"Loaded {len(results)} GK1Hit records from {path.name}")
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
    "GK1Summary",
    "GK1Hit",
]
