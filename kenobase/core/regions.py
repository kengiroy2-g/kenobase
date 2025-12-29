"""Utility helpers for regional metadata (Bundesland) normalization."""

from __future__ import annotations

from typing import Optional

# Canonical ASCII names for German Bundeslaender
GERMAN_REGIONS = {
    "baden-wuerttemberg",
    "bayern",
    "berlin",
    "brandenburg",
    "bremen",
    "hamburg",
    "hessen",
    "mecklenburg-vorpommern",
    "niedersachsen",
    "nordrhein-westfalen",
    "rheinland-pfalz",
    "saarland",
    "sachsen",
    "sachsen-anhalt",
    "schleswig-holstein",
    "thueringen",
}

# Common aliases and abbreviations mapped to canonical names
REGION_ALIASES = {
    "baden-wuerttemberg": "baden-wuerttemberg",
    "baden-württemberg": "baden-wuerttemberg",
    "bw": "baden-wuerttemberg",
    "bawue": "baden-wuerttemberg",
    "bayern": "bayern",
    "bay": "bayern",
    "by": "bayern",
    "berlin": "berlin",
    "brandenburg": "brandenburg",
    "bb": "brandenburg",
    "bremen": "bremen",
    "hb": "bremen",
    "hamburg": "hamburg",
    "hh": "hamburg",
    "hessen": "hessen",
    "he": "hessen",
    "mecklenburg-vorpommern": "mecklenburg-vorpommern",
    "meck-pomm": "mecklenburg-vorpommern",
    "mvp": "mecklenburg-vorpommern",
    "niedersachsen": "niedersachsen",
    "nds": "niedersachsen",
    "nordrhein-westfalen": "nordrhein-westfalen",
    "nrw": "nordrhein-westfalen",
    "rheinland-pfalz": "rheinland-pfalz",
    "rlp": "rheinland-pfalz",
    "saarland": "saarland",
    "sl": "saarland",
    "sachsen": "sachsen",
    "sn": "sachsen",
    "sachsen-anhalt": "sachsen-anhalt",
    "lsa": "sachsen-anhalt",
    "schleswig-holstein": "schleswig-holstein",
    "sh": "schleswig-holstein",
    "thueringen": "thueringen",
    "thüringen": "thueringen",
    "th": "thueringen",
}


def normalize_region(value: Optional[str]) -> Optional[str]:
    """Normalize Bundesland strings to a canonical ASCII key.

    Args:
        value: Raw region string from CSV/metadata.

    Returns:
        Normalized region key (e.g., "nordrhein-westfalen") or None if empty.
    """
    if value is None:
        return None

    cleaned = value.strip().lower()
    if not cleaned:
        return None

    # Normalize umlauts and separators for ASCII-safe keys
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
    }
    for src, target in replacements.items():
        cleaned = cleaned.replace(src, target)

    cleaned = cleaned.replace("_", "-").replace(" ", "-")
    cleaned = cleaned.strip("-")

    canonical = REGION_ALIASES.get(cleaned, cleaned)
    return canonical


__all__ = [
    "GERMAN_REGIONS",
    "REGION_ALIASES",
    "normalize_region",
]
