"""Message Formatters - Formatiert Predictions fuer verschiedene Plattformen.

Stellt verschiedene Ausgabe-Stile bereit:
- short: Kompakte Einzeiler
- detailed: Ausfuehrliche Ausgabe mit Tier-Details
- telegram: Telegram-optimiert mit Markdown
- discord: Discord-optimiert mit Embeds-Syntax
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kenobase.bot.core import PredictionResult


def format_short(result: "PredictionResult") -> str:
    """Formatiert Prediction als kompakten Einzeiler.

    Args:
        result: PredictionResult zum Formatieren.

    Returns:
        Einzeiliger String.
    """
    numbers_str = ", ".join(str(n) for n in result.numbers)
    cached_marker = " (cached)" if result.cached else ""
    return f"{result.game_type.upper()}: {numbers_str}{cached_marker}"


def format_detailed(result: "PredictionResult") -> str:
    """Formatiert Prediction mit allen Details.

    Args:
        result: PredictionResult zum Formatieren.

    Returns:
        Mehrzeiliger String mit Details.
    """
    lines = [
        "=" * 50,
        f"KENOBASE {result.game_type.upper()} PREDICTION",
        "=" * 50,
        "",
        f"Zahlen: {', '.join(str(n) for n in result.numbers)}",
        "",
        "Tier-Verteilung:",
        f"  A (stark):   {result.tier_summary.get('A', 0)}",
        f"  B (moderat): {result.tier_summary.get('B', 0)}",
        f"  C (neutral): {result.tier_summary.get('C', 0)}",
        "",
        f"Konfidenz: {result.confidence:.1%}",
        f"Zeitstempel: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if result.cached:
        lines.append("(aus Cache)")

    lines.extend(["", "=" * 50])

    return "\n".join(lines)


def format_telegram(result: "PredictionResult") -> str:
    """Formatiert Prediction fuer Telegram mit Markdown.

    Args:
        result: PredictionResult zum Formatieren.

    Returns:
        Telegram-Markdown-String.
    """
    numbers_bold = " ".join(f"*{n}*" for n in result.numbers)

    tier_a = result.tier_summary.get("A", 0)
    tier_b = result.tier_summary.get("B", 0)
    tier_c = result.tier_summary.get("C", 0)

    lines = [
        f"*KENOBASE {result.game_type.upper()}*",
        "",
        f"Empfohlene Zahlen:",
        numbers_bold,
        "",
        f"Tiers: A={tier_a} | B={tier_b} | C={tier_c}",
        f"Konfidenz: {result.confidence:.0%}",
    ]

    if result.cached:
        lines.append("_(cached)_")

    timestamp = result.timestamp.strftime("%H:%M")
    lines.append(f"\n_{timestamp}_")

    return "\n".join(lines)


def format_discord(result: "PredictionResult") -> str:
    """Formatiert Prediction fuer Discord mit Markdown.

    Args:
        result: PredictionResult zum Formatieren.

    Returns:
        Discord-Markdown-String.
    """
    numbers_code = " ".join(f"`{n}`" for n in result.numbers)

    tier_a = result.tier_summary.get("A", 0)
    tier_b = result.tier_summary.get("B", 0)
    tier_c = result.tier_summary.get("C", 0)

    lines = [
        f"**KENOBASE {result.game_type.upper()}**",
        "",
        f"Empfohlene Zahlen:",
        numbers_code,
        "",
        f"```",
        f"Tier A (stark):   {tier_a}",
        f"Tier B (moderat): {tier_b}",
        f"Tier C (neutral): {tier_c}",
        f"Konfidenz: {result.confidence:.0%}",
        f"```",
    ]

    if result.cached:
        lines.append("*(cached)*")

    timestamp = result.timestamp.strftime("%H:%M")
    lines.append(f"\n*{timestamp}*")

    return "\n".join(lines)


def format_json(result: "PredictionResult") -> dict:
    """Formatiert Prediction als JSON-Dict.

    Args:
        result: PredictionResult zum Formatieren.

    Returns:
        JSON-serialisierbares Dict.
    """
    return {
        "game_type": result.game_type,
        "numbers": result.numbers,
        "tier_summary": result.tier_summary,
        "confidence": round(result.confidence, 4),
        "timestamp": result.timestamp.isoformat(),
        "cached": result.cached,
        "details": result.details,
    }


__all__ = [
    "format_short",
    "format_detailed",
    "format_telegram",
    "format_discord",
    "format_json",
]
