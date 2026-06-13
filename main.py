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
        logger.info("Initializing system background operations...")

        # Connection to the MongoDB Atlas cluster
        try:
            await db_manager.initialize() 
            logger.info("Successfully established connection to MongoDB Cluster.")
        except Exception as e:
            logger.critical(f"Database handshake crash: {e}")
            return

        # Dynamic Extension Cogs registry
        cogs_to_load = [
            "cogs.automod",
            "cogs.logging",
            "cogs.tickets",
            "cogs.aitorole"
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"Extension cog loaded successfully: {cog}")
            except Exception as e:
                logger.error(f"Failed to load extension {cog}: {e}")

        # Bind web dashboard natively inside bot's execution event loop
        self.loop.create_task(run_dashboard(self, PORT))
        logger.info(f"Dashboard thread deployed targeting production port: {PORT}")

    async def on_ready(self):
        logger.info(f"🤖 Bot Connection Secured | Logged in as: {self.user.name} ({self.user.id})")
        try:
            synced = await self.tree.sync()
            logger.info(f"Successfully synced {len(synced)} application slash commands globally.")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="GladByte Panel"))

async def main():
    if not TOKEN:
        logger.critical("Initialization aborted: 'DISCORD_TOKEN' environment key missing.")
        return

    bot = EnderBot()
    app.bot = bot

    try:
        await bot.start(TOKEN)
    except Exception as e:
        logger.critical(f"Fatal crash encountered during launch sequencing: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System process terminated safely.")
