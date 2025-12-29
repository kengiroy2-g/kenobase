"""Parsing helpers for mixed-format numeric fields.

Kenobase ingests data from multiple sources (Excel/CSV exports) where integer-like
fields may appear in inconsistent formats, e.g.:

- ``275.0`` (float string for an integer)
- ``3.462`` (German thousands separator -> 3462)
- ``2.91`` (often intended as ``2.910`` with a dropped trailing zero -> 2910)
- ``1.234,56`` (German float -> 1234.56)

These helpers provide robust parsing with conservative heuristics.
"""

from __future__ import annotations

import math
import re
from typing import Any

_THOUSAND_GROUPS_DOT = re.compile(r"^\d{1,3}(?:\.\d{3})+$")
_TWO_DECIMALS_DOT = re.compile(r"^\d+\.\d{2}$")


def parse_float_mixed_german(value: Any, *, default: float = 0.0) -> float:
    """Parse a mixed-format numeric value into a float.

    This function treats comma as decimal separator when present. Dot-grouped
    thousands (e.g. ``3.462``) are normalized to ``3462``.
    """
    if value is None:
        return default

    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return default
        return float(value)

    text = str(value).strip().replace("\u00a0", "")
    if not text:
        return default

    # German style: 1.234,56
    if "," in text:
        normalized = text.replace(".", "").replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return default

    # Thousand groups with dot: 3.462 -> 3462
    if _THOUSAND_GROUPS_DOT.match(text):
        try:
            return float(text.replace(".", ""))
        except ValueError:
            return default

    try:
        return float(text)
    except ValueError:
        return default


def parse_int_mixed_german(value: Any, *, default: int = 0) -> int:
    """Parse a mixed-format integer-like field into an int.

    Heuristics:
    - Thousand groups with dot are treated as thousands separators.
    - Values with exactly two digits after the dot (e.g. ``2.91``) are treated as
      a thousands-group with a dropped trailing zero (=> ``2910``).
    - Plain numeric values are rounded to the nearest int if they are integral.
    """
    if value is None:
        return default

    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        if math.isnan(value):
            return default
        return int(round(value))

    text = str(value).strip().replace("\u00a0", "")
    if not text:
        return default

    if _THOUSAND_GROUPS_DOT.match(text):
        try:
            return int(text.replace(".", ""))
        except ValueError:
            return default

    if _TWO_DECIMALS_DOT.match(text):
        left, right = text.split(".")
        # Interpret 2.91 as 2.910 (common when a trailing 0 is dropped)
        try:
            return int(f"{left}{right}0")
        except ValueError:
            return default

    parsed = parse_float_mixed_german(text, default=float(default))
    if abs(parsed - round(parsed)) < 1e-9:
        return int(round(parsed))

    # Last resort: strip non-digits
    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else default


__all__ = [
    "parse_float_mixed_german",
    "parse_int_mixed_german",
]

