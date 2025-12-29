#!/usr/bin/env python
"""run_bot.py - CLI Entry Point fuer KENOBASE Bot.

Startet Telegram oder Discord Bot.

Usage:
    python scripts/run_bot.py --platform telegram
    python scripts/run_bot.py --platform discord
    python scripts/run_bot.py --platform both

Environment Variables:
    TELEGRAM_BOT_TOKEN: Telegram Bot Token
    DISCORD_BOT_TOKEN: Discord Bot Token
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def setup_logging(level: str = "INFO") -> None:
    """Konfiguriert Logging.

    Args:
        level: Log-Level (DEBUG, INFO, WARNING, ERROR).
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )


def load_config(config_path: str) -> dict:
    """Laedt YAML-Config.

    Args:
        config_path: Pfad zur Config-Datei.

    Returns:
        Config-Dict.
    """
    import yaml

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_bot_core(config: dict) -> "BotCore":
    """Erstellt BotCore aus Config.

    Args:
        config: Vollstaendige Config.

    Returns:
        Konfigurierter BotCore.
    """
    from kenobase.bot.core import BotCore

    bot_config = config.get("bot", {})
    results_dir = config.get("paths", {}).get("output_dir", "results")

    return BotCore(config=bot_config, results_dir=results_dir)


async def run_telegram(bot_core: "BotCore", config: dict) -> None:
    """Startet Telegram Bot.

    Args:
        bot_core: Konfigurierter BotCore.
        config: Bot-Config.
    """
    from kenobase.bot.telegram_handler import run_telegram_bot, HAS_TELEGRAM

    if not HAS_TELEGRAM:
        print("ERROR: python-telegram-bot not installed.")
        print("Install with: pip install python-telegram-bot>=21.0")
        sys.exit(1)

    # Token aus Env oder Config
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        token = config.get("bot", {}).get("telegram", {}).get("token", "")
        # Resolve ${VAR} syntax
        if token.startswith("${") and token.endswith("}"):
            var_name = token[2:-1]
            token = os.environ.get(var_name, "")

    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set.")
        print("Set environment variable: export TELEGRAM_BOT_TOKEN=your_token")
        sys.exit(1)

    allowed_chats = config.get("bot", {}).get("telegram", {}).get("allowed_chat_ids", [])

    print("Starting Telegram bot...")
    await run_telegram_bot(token, bot_core, allowed_chats)


async def run_discord(bot_core: "BotCore", config: dict) -> None:
    """Startet Discord Bot.

    Args:
        bot_core: Konfigurierter BotCore.
        config: Bot-Config.
    """
    from kenobase.bot.discord_handler import run_discord_bot, HAS_DISCORD

    if not HAS_DISCORD:
        print("ERROR: discord.py not installed.")
        print("Install with: pip install discord.py>=2.3.0")
        sys.exit(1)

    # Token aus Env oder Config
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        token = config.get("bot", {}).get("discord", {}).get("token", "")
        # Resolve ${VAR} syntax
        if token.startswith("${") and token.endswith("}"):
            var_name = token[2:-1]
            token = os.environ.get(var_name, "")

    if not token:
        print("ERROR: DISCORD_BOT_TOKEN not set.")
        print("Set environment variable: export DISCORD_BOT_TOKEN=your_token")
        sys.exit(1)

    allowed_guilds = config.get("bot", {}).get("discord", {}).get("allowed_guild_ids", [])
    prefix = config.get("bot", {}).get("discord", {}).get("command_prefix", "!")

    print("Starting Discord bot...")
    await run_discord_bot(token, bot_core, prefix, allowed_guilds)


async def run_both(bot_core: "BotCore", config: dict) -> None:
    """Startet beide Bots parallel.

    Args:
        bot_core: Konfigurierter BotCore.
        config: Bot-Config.
    """
    tasks = [
        asyncio.create_task(run_telegram(bot_core, config)),
        asyncio.create_task(run_discord(bot_core, config)),
    ]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        for task in tasks:
            task.cancel()


def main() -> None:
    """CLI Entry Point."""
    parser = argparse.ArgumentParser(
        description="KENOBASE Bot - Telegram/Discord Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_bot.py --platform telegram
    python scripts/run_bot.py --platform discord
    python scripts/run_bot.py --platform both --config config/default.yaml

Environment Variables:
    TELEGRAM_BOT_TOKEN: Required for Telegram
    DISCORD_BOT_TOKEN: Required for Discord
        """,
    )

    parser.add_argument(
        "--platform",
        "-p",
        choices=["telegram", "discord", "both"],
        default="telegram",
        help="Bot platform (default: telegram)",
    )

    parser.add_argument(
        "--config",
        "-c",
        default="config/default.yaml",
        help="Path to config file (default: config/default.yaml)",
    )

    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Load config
    config_path = project_root / args.config
    if not config_path.exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)

    config = load_config(str(config_path))
    logger.info(f"Loaded config from {config_path}")

    # Create BotCore
    bot_core = get_bot_core(config)

    # Run bot(s)
    try:
        if args.platform == "telegram":
            asyncio.run(run_telegram(bot_core, config))
        elif args.platform == "discord":
            asyncio.run(run_discord(bot_core, config))
        else:  # both
            asyncio.run(run_both(bot_core, config))
    except KeyboardInterrupt:
        print("\nBot stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
