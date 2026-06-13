import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Component attachments
from database import db_manager
from dashboard import run_dashboard, app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Bot.Main")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 10000))

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True          

class EnderBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        logger.info("Loading extensions...")

      # Dynamic Extension Cogs registry
        cogs_to_load = [
            "cogs.automod",
            "cogs.autorole",
            "cogs.info",
            "cogs.logging",
            "cogs.moderation",
            "cogs.gladbyte_ticket",
            "cogs.kitecloud_tickets",
            "cogs.botinfo",
            "cogs.invite",
            "cogs.dashboard",
            "cogs.admin_utils",
            "cogs.error_handler",
            "cogs.onboard",
            "cogs.help"  # <-- Added your new public help menu matrix!
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"Extension cog loaded successfully: {cog}")
            except Exception as e:
                logger.error(f"Failed to load extension {cog}: {e}")

    async def on_ready(self):
        logger.info(f"🤖 Bot Connection Secured | Logged in as: {self.user.name} ({self.user.id})")
        try:
            synced = await self.tree.sync()
            logger.info(f"Successfully synced {len(synced)} application slash commands globally.")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="GladByte Panel"))

sync def on_ready(self):
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Ender Bot V2.0"
        )
        await self.change_presence(
            status=discord.Status.do_not_disturb,
            activity=activity
        )
async def main():
    if not TOKEN:
        logger.critical("Initialization aborted: 'DISCORD_TOKEN' environment key missing.")
        return

    # Run database handshake FIRST and block everything until it succeeds.
    try:
        logger.info("Establishing connection to MongoDB Cluster...")
        await db_manager.initialize() 
        logger.info("Successfully established connection to MongoDB Cluster.")
    except Exception as e:
        logger.critical(f"Database handshake crash: {e}")
        return

    bot = EnderBot()
    app.bot = bot

    # Launch web traffic and bot socket gateways concurrently
    async with asyncio.TaskGroup() as tg:
        logger.info(f"Deploying dashboard webserver framework targeting port: {PORT}")
        tg.create_task(run_dashboard(bot, PORT))
        
        logger.info("Launching Discord bot client connection gateway...")
        tg.create_task(bot.start(TOKEN))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("System processes terminated safely.")
