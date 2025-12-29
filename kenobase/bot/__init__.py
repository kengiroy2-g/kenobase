"""Kenobase Bot Module - Telegram & Discord Integration.

Dieses Modul stellt Bot-Interfaces fuer Telegram und Discord bereit,
um Predictions abzurufen und Daily Pushes zu senden.

Hauptkomponenten:
- BotCore: Zentraler Bot-Service mit Caching
- TelegramHandler: python-telegram-bot Integration
- DiscordHandler: discord.py Integration
- Formatters: Message-Formatierung fuer verschiedene Stile

Usage:
    from kenobase.bot import BotCore

    bot = BotCore(config)
    result = bot.get_prediction(game_type="keno")
    message = bot.format_prediction(result, style="short")
"""

from kenobase.bot.core import BotCore, PredictionResult
from kenobase.bot.formatters import (
    format_short,
    format_detailed,
    format_telegram,
    format_discord,
)

__all__ = [
    "BotCore",
    "PredictionResult",
    "format_short",
    "format_detailed",
    "format_telegram",
    "format_discord",
]
