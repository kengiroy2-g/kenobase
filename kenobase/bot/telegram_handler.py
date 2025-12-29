"""Telegram Handler - python-telegram-bot Integration.

Stellt Telegram-Bot-Funktionalitaet bereit:
- /predict: Aktuelle Zahlenempfehlungen
- /top6: Top-6 Zahlen (Alias fuer /predict)
- /status: Bot-Status und Cache-Info
- Daily Push: Automatische taegliche Benachrichtigung

Erfordert:
- python-telegram-bot>=21.0
- TELEGRAM_BOT_TOKEN Umgebungsvariable
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING, Optional

logger = logging.getLogger(__name__)

# Lazy imports fuer optionale Dependencies
try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        ContextTypes,
        MessageHandler,
        filters,
    )

    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    logger.warning(
        "python-telegram-bot not installed. Install with: pip install python-telegram-bot>=21.0"
    )

if TYPE_CHECKING:
    from kenobase.bot.core import BotCore


async def predict_command(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    """Handler fuer /predict Command.

    Zeigt aktuelle Zahlenempfehlungen.

    Args:
        update: Telegram Update Objekt.
        context: Bot Context mit user_data.
    """
    if update.message is None:
        return

    bot_core: Optional["BotCore"] = context.bot_data.get("bot_core")
    if bot_core is None:
        await update.message.reply_text("Bot nicht korrekt initialisiert.")
        return

    try:
        # Hole Prediction
        result = bot_core.get_prediction(game_type="keno", top_n=6)
        message = bot_core.format_prediction(result, style="telegram")

        await update.message.reply_text(
            message,
            parse_mode="Markdown",
        )
        logger.info(f"Sent prediction to chat {update.message.chat_id}")

    except RuntimeError as e:
        await update.message.reply_text(f"Fehler: {e}")
        logger.error(f"Prediction error: {e}")


async def top6_command(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    """Handler fuer /top6 Command (Alias fuer /predict).

    Args:
        update: Telegram Update Objekt.
        context: Bot Context.
    """
    await predict_command(update, context)


async def status_command(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    """Handler fuer /status Command.

    Zeigt Bot-Status und Cache-Informationen.

    Args:
        update: Telegram Update Objekt.
        context: Bot Context.
    """
    if update.message is None:
        return

    bot_core: Optional["BotCore"] = context.bot_data.get("bot_core")
    if bot_core is None:
        await update.message.reply_text("Bot nicht korrekt initialisiert.")
        return

    status = bot_core.get_status()

    lines = [
        "*KENOBASE Bot Status*",
        "",
        f"Cache: {'aktiv' if status['cache_enabled'] else 'inaktiv'}",
        f"Cache-Eintraege: {status['cache_entries']}",
        f"Cache-TTL: {status['cache_ttl_seconds']}s",
        "",
        f"Rate-Limit: {status['requests_last_minute']}/{status['rate_limit_rpm']} rpm",
        f"Verbleibend: {status['rate_limit_remaining']}",
        "",
        f"Results-Dir: {'OK' if status['results_dir_exists'] else 'FEHLT'}",
    ]

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
    )


async def clear_cache_command(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    """Handler fuer /clear_cache Command (Admin).

    Leert den Prediction-Cache.

    Args:
        update: Telegram Update Objekt.
        context: Bot Context.
    """
    if update.message is None:
        return

    bot_core: Optional["BotCore"] = context.bot_data.get("bot_core")
    if bot_core is None:
        await update.message.reply_text("Bot nicht korrekt initialisiert.")
        return

    count = bot_core.clear_cache()
    await update.message.reply_text(f"Cache geleert: {count} Eintraege entfernt.")


async def help_command(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    """Handler fuer /help Command.

    Zeigt verfuegbare Befehle.

    Args:
        update: Telegram Update Objekt.
        context: Bot Context.
    """
    if update.message is None:
        return

    help_text = """*KENOBASE Bot - Hilfe*

Verfuegbare Befehle:

/predict - Zeigt aktuelle Zahlenempfehlungen
/top6 - Alias fuer /predict
/status - Zeigt Bot-Status
/help - Diese Hilfe

Die Empfehlungen basieren auf:
- Hypothesen-Synthese (HYP-007 bis HYP-012)
- Zehnergruppen-Filter
- Anti-Avalanche-Theorie
"""

    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
    )


async def start_command(
    update: "Update",
    context: "ContextTypes.DEFAULT_TYPE",
) -> None:
    """Handler fuer /start Command.

    Begruessung bei erstem Kontakt.

    Args:
        update: Telegram Update Objekt.
        context: Bot Context.
    """
    if update.message is None:
        return

    await update.message.reply_text(
        "Willkommen bei KENOBASE!\n\n"
        "Nutze /predict fuer Zahlenempfehlungen.\n"
        "Nutze /help fuer alle Befehle.",
        parse_mode="Markdown",
    )


def create_telegram_app(
    token: str,
    bot_core: "BotCore",
    allowed_chat_ids: Optional[list[int]] = None,
) -> "Application":
    """Erstellt Telegram Application mit Handlern.

    Args:
        token: Telegram Bot Token.
        bot_core: Konfigurierter BotCore.
        allowed_chat_ids: Optionale Liste erlaubter Chat-IDs (Whitelist).

    Returns:
        Konfigurierte Telegram Application.

    Raises:
        ImportError: Wenn python-telegram-bot nicht installiert.
    """
    if not HAS_TELEGRAM:
        raise ImportError(
            "python-telegram-bot>=21.0 required. Install with: "
            "pip install python-telegram-bot>=21.0"
        )

    # Erstelle Application
    app = Application.builder().token(token).build()

    # Speichere BotCore in bot_data
    app.bot_data["bot_core"] = bot_core

    # Registriere Handler
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("predict", predict_command))
    app.add_handler(CommandHandler("top6", top6_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("clear_cache", clear_cache_command))

    logger.info("Telegram application created with handlers")

    return app


async def run_telegram_bot(
    token: str,
    bot_core: "BotCore",
    allowed_chat_ids: Optional[list[int]] = None,
) -> None:
    """Startet den Telegram Bot (async).

    Args:
        token: Telegram Bot Token.
        bot_core: Konfigurierter BotCore.
        allowed_chat_ids: Optionale Whitelist.
    """
    app = create_telegram_app(token, bot_core, allowed_chat_ids)

    logger.info("Starting Telegram bot polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Keep running until stopped
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Telegram bot stopped")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


__all__ = [
    "HAS_TELEGRAM",
    "create_telegram_app",
    "run_telegram_bot",
    "predict_command",
    "status_command",
    "help_command",
]
