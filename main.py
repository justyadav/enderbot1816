import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Import components from your repository files
from database import db_manager
from dashboard import run_dashboard, app

# 1. System Logging Configurations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Bot.Main")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 10000))  # Render assigns port dynamically via environment variables

# 2. Configure Gateway Intents
intents = discord.Intents.default()
intents.message_content = True  # Required for AutoMod word scanning processing
intents.members = True          # Required to view profiles inside moderation commands

class EnderBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        logger.info("Initializing system background operations...")

        # A. Connect to the authenticated MongoDB Cluster securely
        try:
            # db_manager relies internally on the MONGO_URI environment string variable
            await db_manager.initialize() 
            logger.info("Successfully established connection to MongoDB Cluster.")
        except Exception as e:
            logger.critical(f"Database handshake crash: {e}")
            return

        # B. Load Extension Cogs dynamically on startup execution
        cogs_to_load = [
            "cogs.automod",
            "cogs.moderation",
            "cogs.logging",
            "cogs.tickets"
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"Extension cog loaded successfully: {cog}")
            except Exception as e:
                logger.error(f"Failed to load extension {cog}: {e}")

        # C. Bind the interactive web engine and run parallel to the Discord process loop
        self.loop.create_task(run_dashboard(self, PORT))
        logger.info(f"Dashboard thread deployed targeting production port: {PORT}")

    async def on_ready(self):
        logger.info(f"🤖 Bot Connection Secured | Logged in as: {self.user.name} ({self.user.id})")
        
        # Sync application slash commands globally across server caches
        try:
            synced = await self.tree.sync()
            logger.info(f"Successfully synced {len(synced)} application slash commands globally.")
        except Exception as e:
            logger.error(f"Failed to sync slash commands with Discord API: {e}")

        # Set standard activity appearance 
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="GladByte Panel"))

# 3. Safe Execution Context Hook 
async def main():
    if not TOKEN:
        logger.critical("Initialization aborted: 'DISCORD_TOKEN' environment key missing.")
        return

    bot = EnderBot()
    
    # Context anchor binding so dashboard routes can pull live bot instance data cache safely
    app.bot = bot

    try:
        await bot.start(TOKEN)
    except discord.LoginFailure:
        logger.critical("Authentication failed: Invalid Discord token provided.")
    except Exception as e:
        logger.critical(f"Fatal crash encountered during launch sequencing: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System process terminated safely via manual interruption.")
