"""TimelineGrid - Multi-Game Daily Timeline Alignment.

Dieses Modul implementiert die Zeitachsen-Ausrichtung fuer verschiedene
Lotteriespiele auf ein einheitliches Tages-Grid.

Unterstuetzte Spiele:
- KENO: Taeglich (7/Woche)
- Lotto 6aus49: Mi + Sa (2/Woche)
- EuroJackpot: Di + Fr (2/Woche)

Usage:
    from kenobase.core.timeline import TimelineGrid

    grid = TimelineGrid()
    grid.add_game("keno", keno_draws)
    grid.add_game("lotto", lotto_draws)
    grid.add_game("eurojackpot", ej_draws)

    aligned_df = grid.to_dataframe()
    grid.to_parquet("data/processed/timeline_grid.parquet")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

import pandas as pd

from kenobase.core.data_loader import DrawResult, GameType

logger = logging.getLogger(__name__)


# Draw day patterns (0=Monday, 6=Sunday)
DRAW_PATTERNS: dict[str, set[int]] = {
    "keno": {0, 1, 2, 3, 4, 5, 6},  # Daily
    "lotto": {2, 5},  # Wednesday, Saturday
    "eurojackpot": {1, 4},  # Tuesday, Friday
}


@dataclass
class GameData:
    """Container for a single game's draw data.

    Attributes:
        game_type: Type of lottery game
        draws: List of DrawResult objects
        df: DataFrame representation of draws
    """
    game_type: GameType
    draws: list[DrawResult]
    df: Optional[pd.DataFrame] = None


@dataclass
class TimelineGrid:
    """Multi-Game Timeline Grid mit taeglicher Ausrichtung.

    Erstellt ein einheitliches Tages-Grid fuer mehrere Lotteriespiele,
    wobei nicht-Ziehungstage als NaN oder forward-fill behandelt werden.

    Attributes:
        games: Dictionary mit Spielname -> GameData
        start_date: Fruehestes Datum im Grid
        end_date: Spaetestes Datum im Grid
        fill_strategy: Strategie fuer nicht-Ziehungstage ('nan', 'ffill')

    Example:
        >>> grid = TimelineGrid(fill_strategy='nan')
        >>> grid.add_game('keno', keno_results)
        >>> grid.add_game('lotto', lotto_results)
        >>> df = grid.to_dataframe()
        >>> print(df.columns)
        Index(['keno_numbers', 'keno_has_draw', 'lotto_numbers', 'lotto_has_draw'])
    """

    games: dict[str, GameData] = field(default_factory=dict)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    fill_strategy: Literal["nan", "ffill"] = "nan"

    def add_game(
        self,
        game_name: str,
        draws: list[DrawResult],
        game_type: Optional[GameType] = None,
    ) -> None:
        """Fuegt ein Spiel zum Grid hinzu.

        Args:
            game_name: Eindeutiger Name des Spiels (z.B. 'keno', 'lotto')
            draws: Liste von DrawResult-Objekten
            game_type: Optionaler GameType (wird aus draws inferiert wenn None)

        Raises:
            ValueError: Wenn keine Ziehungen vorhanden sind
        """
        if not draws:
            raise ValueError(f"No draws provided for game '{game_name}'")

        # Infer game type from first draw if not provided
        if game_type is None:
            game_type = draws[0].game_type
            if isinstance(game_type, str):
                game_type = GameType(game_type)

        # Build DataFrame from draws
        data = []
        for draw in draws:
            row = {
                "date": draw.date.date() if isinstance(draw.date, datetime) else draw.date,
                "numbers": tuple(draw.numbers),
                "bonus": tuple(draw.bonus) if draw.bonus else (),
            }
            row.update(draw.metadata)
            data.append(row)

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
        df = df.set_index("date")

        # Update date range
        game_start = df.index.min()
        game_end = df.index.max()

        if self.start_date is None or game_start < self.start_date:
            self.start_date = game_start
        if self.end_date is None or game_end > self.end_date:
            self.end_date = game_end

        self.games[game_name] = GameData(
            game_type=game_type,
            draws=draws,
            df=df,
        )

        logger.info(
            f"Added game '{game_name}' with {len(draws)} draws "
            f"({game_start.date()} to {game_end.date()})"
        )

    def add_game_from_csv(
        self,
        game_name: str,
        path: str | Path,
        game_type: Optional[GameType] = None,
    ) -> None:
        """Laedt Spieldaten aus CSV und fuegt sie zum Grid hinzu.

        Args:
            game_name: Eindeutiger Name des Spiels
            path: Pfad zur CSV-Datei
            game_type: Optionaler GameType fuer explizite Format-Angabe
        """
        from kenobase.core.data_loader import DataLoader

        loader = DataLoader()
        draws = loader.load(path, game_type=game_type)
        self.add_game(game_name, draws, game_type)

    def _create_daily_index(self) -> pd.DatetimeIndex:
        """Erstellt den taeglichen DatetimeIndex.

        Returns:
            DatetimeIndex mit allen Tagen von start_date bis end_date
        """
        if self.start_date is None or self.end_date is None:
            raise ValueError("No games added yet - cannot create date range")

        return pd.date_range(start=self.start_date, end=self.end_date, freq="D")

    def to_dataframe(
        self,
        include_draw_mask: bool = True,
        include_numbers: bool = True,
        include_bonus: bool = True,
    ) -> pd.DataFrame:
        """Konvertiert das Grid zu einem einheitlichen DataFrame.

        Erstellt einen DataFrame mit taeglichem Index und Spalten fuer
        jedes Spiel. Nicht-Ziehungstage werden gemaess fill_strategy
        behandelt.

        Args:
            include_draw_mask: Wenn True, fuege '{game}_has_draw' Spalten hinzu
            include_numbers: Wenn True, fuege '{game}_numbers' Spalten hinzu
            include_bonus: Wenn True, fuege '{game}_bonus' Spalten hinzu

        Returns:
            DataFrame mit taeglichem Index und Spiel-spezifischen Spalten

        Raises:
            ValueError: Wenn keine Spiele hinzugefuegt wurden
        """
        if not self.games:
            raise ValueError("No games added to grid")

        daily_index = self._create_daily_index()
        result_df = pd.DataFrame(index=daily_index)
        result_df.index.name = "date"

        for game_name, game_data in self.games.items():
            source_df = game_data.df

            # Reindex to daily grid
            aligned = source_df.reindex(daily_index)

            # Create draw mask (True where we have a draw)
            has_draw = ~aligned["numbers"].isna()

            if include_draw_mask:
                result_df[f"{game_name}_has_draw"] = has_draw

            if include_numbers:
                if self.fill_strategy == "ffill":
                    result_df[f"{game_name}_numbers"] = aligned["numbers"].ffill()
                else:
                    result_df[f"{game_name}_numbers"] = aligned["numbers"]

            if include_bonus and "bonus" in aligned.columns:
                if self.fill_strategy == "ffill":
                    result_df[f"{game_name}_bonus"] = aligned["bonus"].ffill()
                else:
                    result_df[f"{game_name}_bonus"] = aligned["bonus"]

        logger.info(
            f"Created timeline grid: {len(result_df)} days, "
            f"{len(self.games)} games, "
            f"{len(result_df.columns)} columns"
        )

        return result_df

    def to_numbers_matrix(self) -> pd.DataFrame:
        """Erstellt Matrix mit Zahlenvektoren als separate Spalten.

        Fuer jedes Spiel werden die Zahlen in separate Spalten aufgeteilt:
        - keno_z1, keno_z2, ..., keno_z20
        - lotto_z1, ..., lotto_z6
        - eurojackpot_z1, ..., eurojackpot_z5, eurojackpot_euro1, eurojackpot_euro2

        Returns:
            DataFrame mit expandierten Zahlenspalten
        """
        if not self.games:
            raise ValueError("No games added to grid")

        daily_index = self._create_daily_index()
        result_df = pd.DataFrame(index=daily_index)
        result_df.index.name = "date"

        for game_name, game_data in self.games.items():
            source_df = game_data.df.copy()

            # Expand numbers tuple to separate columns
            if "numbers" in source_df.columns:
                # Get max length of numbers across all draws
                num_lengths = source_df["numbers"].dropna().apply(len)
                if len(num_lengths) > 0:
                    max_len = num_lengths.max()

                    for i in range(max_len):
                        col_name = f"{game_name}_z{i+1}"
                        source_df[col_name] = source_df["numbers"].apply(
                            lambda x: x[i] if isinstance(x, tuple) and len(x) > i else None
                        )

            # Expand bonus tuple to separate columns
            if "bonus" in source_df.columns:
                bonus_lengths = source_df["bonus"].dropna().apply(
                    lambda x: len(x) if isinstance(x, tuple) else 0
                )
                if len(bonus_lengths) > 0 and bonus_lengths.max() > 0:
                    max_bonus = bonus_lengths.max()

                    prefix = "euro" if game_name == "eurojackpot" else "bonus"
                    for i in range(max_bonus):
                        col_name = f"{game_name}_{prefix}{i+1}"
                        source_df[col_name] = source_df["bonus"].apply(
                            lambda x: x[i] if isinstance(x, tuple) and len(x) > i else None
                        )

            # Remove original tuple columns
            cols_to_keep = [c for c in source_df.columns if c not in ["numbers", "bonus"]]
            source_df = source_df[cols_to_keep]

            # Reindex to daily grid
            aligned = source_df.reindex(daily_index)

            # Add has_draw column
            first_num_col = f"{game_name}_z1"
            if first_num_col in aligned.columns:
                result_df[f"{game_name}_has_draw"] = ~aligned[first_num_col].isna()

            # Apply fill strategy and add columns
            for col in aligned.columns:
                if self.fill_strategy == "ffill":
                    result_df[col] = aligned[col].ffill()
                else:
                    result_df[col] = aligned[col]

        logger.info(
            f"Created numbers matrix: {len(result_df)} days, "
            f"{len(result_df.columns)} columns"
        )

        return result_df

    def to_parquet(
        self,
        path: str | Path,
        mode: Literal["tuple", "matrix"] = "tuple",
    ) -> Path:
        """Exportiert das Grid als Parquet-Datei.

        Args:
            path: Ziel-Pfad fuer Parquet-Datei
            mode: 'tuple' fuer Zahlen als Tupel, 'matrix' fuer expandierte Spalten

        Returns:
            Pfad zur erstellten Datei
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if mode == "matrix":
            df = self.to_numbers_matrix()
        else:
            df = self.to_dataframe()
            # Convert tuples to strings for parquet compatibility
            for col in df.columns:
                if df[col].dtype == "object":
                    df[col] = df[col].apply(
                        lambda x: str(x) if isinstance(x, tuple) else x
                    )

        df.to_parquet(path)
        logger.info(f"Exported timeline grid to {path}")
        return path

    def get_draw_coverage(self) -> pd.DataFrame:
        """Berechnet die Ziehungs-Abdeckung pro Spiel.

        Returns:
            DataFrame mit Statistiken pro Spiel:
            - total_days: Anzahl Tage im Grid
            - draw_days: Anzahl Ziehungstage
            - coverage: Anteil Ziehungstage (0-1)
            - expected_weekly: Erwartete Ziehungen pro Woche
            - actual_weekly: Tatsaechliche Ziehungen pro Woche
        """
        if not self.games:
            raise ValueError("No games added to grid")

        daily_index = self._create_daily_index()
        total_days = len(daily_index)
        total_weeks = total_days / 7

        stats = []
        for game_name, game_data in self.games.items():
            source_df = game_data.df

            # Count draws within the grid date range
            draw_days = len(source_df)

            # Expected draws based on pattern
            pattern_key = game_name.lower()
            if pattern_key in DRAW_PATTERNS:
                expected_weekly = len(DRAW_PATTERNS[pattern_key])
            else:
                expected_weekly = 7  # Assume daily if unknown

            stats.append({
                "game": game_name,
                "total_days": total_days,
                "draw_days": draw_days,
                "coverage": draw_days / total_days if total_days > 0 else 0,
                "expected_weekly": expected_weekly,
                "actual_weekly": draw_days / total_weeks if total_weeks > 0 else 0,
            })

        return pd.DataFrame(stats)

    def get_joint_draw_days(self, games: Optional[list[str]] = None) -> pd.DatetimeIndex:
        """Findet Tage an denen alle angegebenen Spiele Ziehungen haben.

        Args:
            games: Liste von Spielnamen (default: alle Spiele)

        Returns:
            DatetimeIndex mit gemeinsamen Ziehungstagen
        """
        if games is None:
            games = list(self.games.keys())

        if not games:
            return pd.DatetimeIndex([])

        # Start with first game's draw dates
        joint_dates = set(self.games[games[0]].df.index)

        # Intersect with remaining games
        for game_name in games[1:]:
            if game_name in self.games:
                game_dates = set(self.games[game_name].df.index)
                joint_dates &= game_dates

        return pd.DatetimeIndex(sorted(joint_dates))

    def summary(self) -> dict:
        """Gibt eine Zusammenfassung des Grids zurueck.

        Returns:
            Dictionary mit Grid-Statistiken
        """
        coverage_df = self.get_draw_coverage()

        return {
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "total_days": len(self._create_daily_index()) if self.start_date else 0,
            "games": list(self.games.keys()),
            "fill_strategy": self.fill_strategy,
            "coverage": coverage_df.to_dict(orient="records") if len(coverage_df) > 0 else [],
        }


def load_multi_game_grid(
    keno_path: Optional[str | Path] = None,
    lotto_path: Optional[str | Path] = None,
    eurojackpot_path: Optional[str | Path] = None,
    fill_strategy: Literal["nan", "ffill"] = "nan",
) -> TimelineGrid:
    """Convenience-Funktion zum Laden mehrerer Spiele.

    Args:
        keno_path: Pfad zu KENO CSV (optional)
        lotto_path: Pfad zu Lotto CSV (optional)
        eurojackpot_path: Pfad zu EuroJackpot CSV (optional)
        fill_strategy: Strategie fuer nicht-Ziehungstage

    Returns:
        Konfiguriertes TimelineGrid

    Example:
        >>> grid = load_multi_game_grid(
        ...     keno_path="data/raw/keno/KENO_ab_2022_bereinigt.csv",
        ...     lotto_path="data/raw/lotto/LOTTO_ab_2022_bereinigt.csv",
        ...     fill_strategy="nan"
        ... )
        >>> df = grid.to_dataframe()
    """
    grid = TimelineGrid(fill_strategy=fill_strategy)

    if keno_path:
        grid.add_game_from_csv("keno", keno_path, GameType.KENO)

    if lotto_path:
        grid.add_game_from_csv("lotto", lotto_path, GameType.LOTTO)

    if eurojackpot_path:
        grid.add_game_from_csv("eurojackpot", eurojackpot_path, GameType.EUROJACKPOT)

    return grid


__all__ = [
    "TimelineGrid",
    "GameData",
    "DRAW_PATTERNS",
    "load_multi_game_grid",
]
