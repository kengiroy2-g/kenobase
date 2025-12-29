"""Fixed KENO payout table (Gewinnquoten) helpers.

Kenobase uses the per-1 EUR fixed KENO quotes as seen in
`Keno_GPTs/Keno_GQ_2022_2023-2024.csv` (column: "1 Euro Gewinn").

This module is the single source of truth for those quotes to avoid
divergent hardcoded tables across scripts.
"""

from __future__ import annotations

from typing import Mapping

# Fixed quotes per 1 EUR Einsatz (payouts in EUR) for Keno-Typ 2..10.
# Missing hit classes imply 0 EUR payout.
KENO_FIXED_QUOTES_BY_TYPE: dict[int, dict[int, float]] = {
    2: {2: 6.0},
    3: {2: 1.0, 3: 16.0},
    4: {2: 1.0, 3: 2.0, 4: 22.0},
    5: {3: 2.0, 4: 7.0, 5: 100.0},
    6: {3: 1.0, 4: 2.0, 5: 15.0, 6: 500.0},
    7: {3: 1.0, 4: 1.0, 5: 12.0, 6: 100.0, 7: 1000.0},
    8: {0: 1.0, 4: 1.0, 5: 2.0, 6: 15.0, 7: 100.0, 8: 10000.0},
    9: {0: 2.0, 4: 1.0, 5: 2.0, 6: 5.0, 7: 20.0, 8: 1000.0, 9: 50000.0},
    10: {0: 2.0, 5: 2.0, 6: 5.0, 7: 15.0, 8: 100.0, 9: 1000.0, 10: 100000.0},
}

# Convenience mapping (keno_type, hits) -> quote.
KENO_FIXED_ODDS: dict[tuple[int, int], float] = {
    (keno_type, hits): float(quote)
    for keno_type, mapping in KENO_FIXED_QUOTES_BY_TYPE.items()
    for hits, quote in mapping.items()
}


def get_fixed_quote(keno_type: int, hits: int) -> float:
    """Return the fixed quote (payout in EUR) for 1 EUR Einsatz.

    Args:
        keno_type: Keno-Typ (2..10)
        hits: Number of correct numbers (0..keno_type)

    Returns:
        Quote in EUR (0.0 if there is no payout for that hit class).
    """
    return float(KENO_FIXED_QUOTES_BY_TYPE.get(int(keno_type), {}).get(int(hits), 0.0))


def get_fixed_quotes_for_type(keno_type: int) -> Mapping[int, float]:
    """Return the payout mapping hits -> EUR for a given Keno-Typ."""
    return KENO_FIXED_QUOTES_BY_TYPE.get(int(keno_type), {})


__all__ = [
    "KENO_FIXED_ODDS",
    "KENO_FIXED_QUOTES_BY_TYPE",
    "get_fixed_quote",
    "get_fixed_quotes_for_type",
]

