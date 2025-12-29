"""Discord Handler - discord.py Integration.

Stellt Discord-Bot-Funktionalitaet bereit:
- !predict: Aktuelle Zahlenempfehlungen
- !top6: Top-6 Zahlen (Alias)
- !status: Bot-Status und Cache-Info

Erfordert:
- discord.py>=2.3.0
- DISCORD_BOT_TOKEN Umgebungsvariable
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Optional

logger = logging.getLogger(__name__)

# Lazy imports fuer optionale Dependencies
try:
    import discord
    from discord.ext import commands

    HAS_DISCORD = True
except ImportError:
    HAS_DISCORD = False
    logger.warning(
        "discord.py not installed. Install with: pip install discord.py>=2.3.0"
    )

if TYPE_CHECKING:
    from kenobase.bot.core import BotCore


class PredictionCog(commands.Cog):
    """Discord Cog fuer Predictions."""

    def __init__(self, bot: "commands.Bot", bot_core: "BotCore"):
        """Initialisiert PredictionCog.

        Args:
            bot: Discord Bot Instanz.
            bot_core: Konfigurierter BotCore.
        """
        self.bot = bot
        self.bot_core = bot_core

    @commands.command(name="predict")
    async def predict(self, ctx: "commands.Context") -> None:
        """Zeigt aktuelle Zahlenempfehlungen.

        Args:
            ctx: Command Context.
        """
        try:
            result = self.bot_core.get_prediction(game_type="keno", top_n=6)
            message = self.bot_core.format_prediction(result, style="discord")

            await ctx.send(message)
            logger.info(f"Sent prediction to channel {ctx.channel.id}")

        except RuntimeError as e:
            await ctx.send(f"Fehler: {e}")
            logger.error(f"Prediction error: {e}")

    @commands.command(name="top6")
    async def top6(self, ctx: "commands.Context") -> None:
        """Alias fuer !predict.

        Args:
            ctx: Command Context.
        """
        await self.predict(ctx)

    @commands.command(name="status")
    async def status(self, ctx: "commands.Context") -> None:
        """Zeigt Bot-Status.

        Args:
            ctx: Command Context.
        """
        status = self.bot_core.get_status()

        lines = [
            "**KENOBASE Bot Status**",
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

        await ctx.send("\n".join(lines))

    @commands.command(name="clear_cache")
    @commands.has_permissions(administrator=True)
    async def clear_cache(self, ctx: "commands.Context") -> None:
        """Leert den Prediction-Cache (Admin-only).

        Args:
            ctx: Command Context.
        """
        count = self.bot_core.clear_cache()
        await ctx.send(f"Cache geleert: {count} Eintraege entfernt.")

    @commands.command(name="help_kenobase")
    async def help_kenobase(self, ctx: "commands.Context") -> None:
        """Zeigt KENOBASE-Hilfe.

        Args:
            ctx: Command Context.
        """
        help_text = """**KENOBASE Bot - Hilfe**

Verfuegbare Befehle:

`!predict` - Zeigt aktuelle Zahlenempfehlungen
`!top6` - Alias fuer !predict
`!status` - Zeigt Bot-Status
`!help_kenobase` - Diese Hilfe

Die Empfehlungen basieren auf:
- Hypothesen-Synthese (HYP-007 bis HYP-012)
- Zehnergruppen-Filter
- Anti-Avalanche-Theorie
"""
        await ctx.send(help_text)


class StatusCog(commands.Cog):
    """Discord Cog fuer Bot-Status und Events."""

    def __init__(self, bot: "commands.Bot"):
        """Initialisiert StatusCog.

        Args:
            bot: Discord Bot Instanz.
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Event Handler wenn Bot bereit ist."""
        logger.info(f"Discord bot ready: {self.bot.user}")
        print(f"KENOBASE Discord Bot eingeloggt als {self.bot.user}")

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: "commands.Context",
        error: "commands.CommandError",
    ) -> None:
        """Globaler Error Handler.

        Args:
            ctx: Command Context.
            error: Aufgetretener Fehler.
        """
        if isinstance(error, commands.CommandNotFound):
            return  # Ignoriere unbekannte Commands

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Keine Berechtigung fuer diesen Befehl.")
            return

        logger.error(f"Command error: {error}")
        await ctx.send(f"Ein Fehler ist aufgetreten: {error}")


def create_discord_bot(
    token: str,
    bot_core: "BotCore",
    command_prefix: str = "!",
    allowed_guild_ids: Optional[list[int]] = None,
) -> "commands.Bot":
    """Erstellt Discord Bot mit Cogs.

    Args:
        token: Discord Bot Token.
        bot_core: Konfigurierter BotCore.
        command_prefix: Command-Prefix (default "!").
        allowed_guild_ids: Optionale Whitelist fuer Guilds.

    Returns:
        Konfigurierter Discord Bot.

    Raises:
        ImportError: Wenn discord.py nicht installiert.
    """
    if not HAS_DISCORD:
        raise ImportError(
            "discord.py>=2.3.0 required. Install with: "
            "pip install discord.py>=2.3.0"
        )

    # Intents konfigurieren
    intents = discord.Intents.default()
    intents.message_content = True

    # Bot erstellen
    bot = commands.Bot(
        command_prefix=command_prefix,
        intents=intents,
        description="KENOBASE - Wissenschaftliche Lottozahlen-Analyse",
    )

    # Speichere Token und Config fuer run
    bot._token = token
    bot._bot_core = bot_core
    bot._allowed_guild_ids = allowed_guild_ids

    logger.info("Discord bot created")

    return bot


async def setup_cogs(bot: "commands.Bot", bot_core: "BotCore") -> None:
    """Registriert Cogs beim Bot.

    Args:
        bot: Discord Bot Instanz.
        bot_core: Konfigurierter BotCore.
    """
    await bot.add_cog(PredictionCog(bot, bot_core))
    await bot.add_cog(StatusCog(bot))
    logger.info("Cogs registered")


async def run_discord_bot(
    token: str,
    bot_core: "BotCore",
    command_prefix: str = "!",
    allowed_guild_ids: Optional[list[int]] = None,
) -> None:
    """Startet den Discord Bot (async).

    Args:
        token: Discord Bot Token.
        bot_core: Konfigurierter BotCore.
        command_prefix: Command-Prefix.
        allowed_guild_ids: Optionale Guild-Whitelist.
    """
    bot = create_discord_bot(token, bot_core, command_prefix, allowed_guild_ids)

    @bot.event
    async def on_ready():
        await setup_cogs(bot, bot_core)
        logger.info(f"Discord bot ready: {bot.user}")

    logger.info("Starting Discord bot...")
    await bot.start(token)


__all__ = [
    "HAS_DISCORD",
    "PredictionCog",
    "StatusCog",
    "create_discord_bot",
    "run_discord_bot",
    "setup_cogs",
]
