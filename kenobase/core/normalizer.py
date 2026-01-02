"""Zahlenraum-Normalisierung fuer Cross-Lottery Analyse.

Dieses Modul implementiert die Normalisierung von Lottozahlen aus verschiedenen
Spielen (KENO, Lotto, EuroJackpot) auf einen einheitlichen [0.0, 1.0] Bereich.

Die Normalisierung ermoeglicht:
- Cross-Lottery Korrelationsanalysen
- Vergleichbare Metriken ueber verschiedene Spiele
- Oekosystem-Analysen gemaess Axiom-First Ansatz

Formel: normalized = (n - min) / (max - min)

Usage:
    from kenobase.core.normalizer import (
        normalize_number, denormalize_number,
        normalize_numbers, normalize_draw
    )
    from kenobase.core.data_loader import GameType

    # Einzelne Zahl normalisieren
    norm = normalize_number(35, GameType.KENO)  # 35 aus 1-70 -> 0.493

    # Zurueck transformieren
    original = denormalize_number(0.493, GameType.KENO)  # -> 35

    # Batch-Normalisierung
    numbers = [7, 11, 23, 31, 42]
    normalized = normalize_numbers(numbers, GameType.LOTTO)

    # DrawResult normalisieren
    normalized_draw = normalize_draw(draw_result)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kenobase.core.data_loader import DrawResult, GameType

# Game-specific number ranges
# Source: config/default.yaml lines 131-158
GAME_RANGES: dict[str, tuple[int, int]] = {
    "keno": (1, 70),
    "eurojackpot": (1, 50),
    "lotto": (1, 49),
    "gk1_summary": (1, 70),  # GK1 uses KENO range
    "gk1_hit": (1, 70),  # GK1 uses KENO range
    "unknown": (1, 70),  # Default to KENO range
}

# EuroJackpot bonus (EuroZahlen) range
EUROJACKPOT_BONUS_RANGE: tuple[int, int] = (1, 12)

# Lotto bonus (Superzahl) range
LOTTO_BONUS_RANGE: tuple[int, int] = (0, 9)


def get_game_range(game_type: GameType | str) -> tuple[int, int]:
    """Gibt den Zahlenbereich fuer einen Spieltyp zurueck.

    Args:
        game_type: Spieltyp als GameType Enum oder String

    Returns:
        Tuple (min, max) des Zahlenbereichs

    Raises:
        ValueError: Wenn Spieltyp unbekannt ist
    """
    # Convert enum to string if needed
    if hasattr(game_type, "value"):
        game_key = game_type.value
    else:
        game_key = str(game_type).lower()

    if game_key not in GAME_RANGES:
        raise ValueError(f"Unknown game type: {game_type}")

    return GAME_RANGES[game_key]


def normalize_number(n: int, game_type: GameType | str) -> float:
    """Normalisiert eine einzelne Zahl auf [0.0, 1.0].

    Formel: (n - min) / (max - min)

    Args:
        n: Die zu normalisierende Zahl
        game_type: Spieltyp (keno, lotto, eurojackpot)

    Returns:
        Normalisierter Wert im Bereich [0.0, 1.0]

    Raises:
        ValueError: Wenn Zahl ausserhalb des gueltigen Bereichs liegt

    Example:
        >>> normalize_number(35, "keno")  # KENO: 1-70
        0.4927536231884058
        >>> normalize_number(25, "lotto")  # Lotto: 1-49
        0.5
    """
    min_val, max_val = get_game_range(game_type)

    if not min_val <= n <= max_val:
        raise ValueError(
            f"Number {n} out of range [{min_val}, {max_val}] for {game_type}"
        )

    # Avoid division by zero (shouldn't happen with valid ranges)
    range_size = max_val - min_val
    if range_size == 0:
        return 0.0

    return (n - min_val) / range_size


def denormalize_number(norm: float, game_type: GameType | str) -> int:
    """Transformiert normalisierten Wert zurueck zur Original-Zahl.

    Formel: round(norm * (max - min) + min)

    Args:
        norm: Normalisierter Wert [0.0, 1.0]
        game_type: Spieltyp (keno, lotto, eurojackpot)

    Returns:
        Original-Zahl als Integer

    Raises:
        ValueError: Wenn norm ausserhalb [0.0, 1.0] liegt

    Example:
        >>> denormalize_number(0.5, "keno")  # KENO: 1-70
        35
        >>> denormalize_number(0.5, "lotto")  # Lotto: 1-49
        25
    """
    if not 0.0 <= norm <= 1.0:
        raise ValueError(f"Normalized value {norm} out of range [0.0, 1.0]")

    min_val, max_val = get_game_range(game_type)
    range_size = max_val - min_val

    return round(norm * range_size + min_val)


def normalize_numbers(numbers: list[int], game_type: GameType | str) -> list[float]:
    """Normalisiert eine Liste von Zahlen.

    Args:
        numbers: Liste von Zahlen
        game_type: Spieltyp

    Returns:
        Liste von normalisierten Werten [0.0, 1.0]

    Example:
        >>> normalize_numbers([1, 35, 70], "keno")
        [0.0, 0.4927536231884058, 1.0]
    """
    return [normalize_number(n, game_type) for n in numbers]


def denormalize_numbers(
    normalized: list[float], game_type: GameType | str
) -> list[int]:
    """Transformiert Liste normalisierter Werte zurueck.

    Args:
        normalized: Liste von normalisierten Werten
        game_type: Spieltyp

    Returns:
        Liste von Original-Zahlen

    Example:
        >>> denormalize_numbers([0.0, 0.5, 1.0], "keno")
        [1, 35, 70]
    """
    return [denormalize_number(n, game_type) for n in normalized]


def normalize_draw(draw: DrawResult) -> dict:
    """Normalisiert ein DrawResult-Objekt.

    Args:
        draw: DrawResult mit numbers, bonus, game_type

    Returns:
        Dictionary mit normalisierten Werten:
        - date: Original-Datum
        - numbers: Normalisierte Hauptzahlen
        - bonus: Normalisierte Bonuszahlen (falls vorhanden)
        - game_type: Original-Spieltyp
        - original_numbers: Original-Zahlen (fuer Rueck-Referenz)
        - original_bonus: Original-Bonuszahlen

    Example:
        >>> from kenobase.core.data_loader import DrawResult, GameType
        >>> draw = DrawResult(
        ...     date=datetime.now(),
        ...     numbers=[7, 14, 21, 28, 35],
        ...     bonus=[],
        ...     game_type=GameType.EUROJACKPOT
        ... )
        >>> result = normalize_draw(draw)
        >>> result["numbers"]
        [0.122..., 0.265..., 0.408..., 0.551..., 0.693...]
    """
    game_type = draw.game_type

    # Normalize main numbers
    normalized_numbers = normalize_numbers(draw.numbers, game_type)

    # Normalize bonus numbers (game-specific ranges)
    normalized_bonus: list[float] = []
    if draw.bonus:
        if hasattr(game_type, "value"):
            game_key = game_type.value
        else:
            game_key = str(game_type).lower()

        if game_key == "eurojackpot":
            # EuroZahlen: 1-12
            min_b, max_b = EUROJACKPOT_BONUS_RANGE
            for b in draw.bonus:
                if min_b <= b <= max_b:
                    normalized_bonus.append((b - min_b) / (max_b - min_b))
        elif game_key == "lotto":
            # Superzahl: 0-9
            min_b, max_b = LOTTO_BONUS_RANGE
            for b in draw.bonus:
                if min_b <= b <= max_b:
                    normalized_bonus.append((b - min_b) / (max_b - min_b))
        else:
            # KENO Plus5 is a 5-digit number (lottery code), not a lottery number
            # It doesn't make sense to normalize it to [0, 1] in lottery space
            # Keep as empty or store raw value in metadata
            normalized_bonus = []

    return {
        "date": draw.date,
        "numbers": normalized_numbers,
        "bonus": normalized_bonus,
        "game_type": game_type,
        "original_numbers": draw.numbers,
        "original_bonus": draw.bonus,
        "metadata": draw.metadata,
    }


def normalize_draws(draws: list[DrawResult]) -> list[dict]:
    """Normalisiert eine Liste von DrawResult-Objekten.

    Args:
        draws: Liste von DrawResult-Objekten

    Returns:
        Liste von normalisierten Dictionaries
    """
    return [normalize_draw(d) for d in draws]


def cross_game_distance(
    numbers_a: list[int],
    game_a: GameType | str,
    numbers_b: list[int],
    game_b: GameType | str,
) -> float:
    """Berechnet die normalisierte Distanz zwischen Zahlen aus verschiedenen Spielen.

    Ermoeglicht Cross-Lottery Vergleiche durch Normalisierung auf [0.0, 1.0].
    Verwendet Mean Absolute Error (MAE) der normalisierten Werte.

    Args:
        numbers_a: Zahlen aus Spiel A
        game_a: Spieltyp A
        numbers_b: Zahlen aus Spiel B
        game_b: Spieltyp B

    Returns:
        Durchschnittliche absolute Distanz (0.0 = identisch, 1.0 = maximal verschieden)

    Note:
        Die Listen muessen nicht gleich lang sein. Bei unterschiedlicher Laenge
        wird die kuerzere Liste verwendet und die Distanz auf die gemeinsamen
        Positionen beschraenkt.

    Example:
        >>> # Vergleiche KENO [35] mit Lotto [25] (beide sind Mitte ihres Bereichs)
        >>> cross_game_distance([35], "keno", [25], "lotto")
        0.007...  # Sehr aehnlich (beide nahe 0.5)
    """
    norm_a = normalize_numbers(numbers_a, game_a)
    norm_b = normalize_numbers(numbers_b, game_b)

    # Use shorter list length
    min_len = min(len(norm_a), len(norm_b))
    if min_len == 0:
        return 0.0

    total_distance = sum(
        abs(norm_a[i] - norm_b[i]) for i in range(min_len)
    )

    return total_distance / min_len


__all__ = [
    "GAME_RANGES",
    "EUROJACKPOT_BONUS_RANGE",
    "LOTTO_BONUS_RANGE",
    "get_game_range",
    "normalize_number",
    "denormalize_number",
    "normalize_numbers",
    "denormalize_numbers",
    "normalize_draw",
    "normalize_draws",
    "cross_game_distance",
]
