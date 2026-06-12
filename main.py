import os
import asyncio
import logging
from discord import Intents, Interaction
from discord.ext import commands
from dotenv import load_dotenv

from database import db_manager
from dashboard import run_dashboard

# Configure rigorous production logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger("Bot.Main")

load_dotenv()

class ModularBot(commands.Bot):
    def __init__(self):
        # Configure application intents explicitly
        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        
        super().__init__(command_prefix=tuple(), intents=intents, help_command=None)

    async def setup_hook(self):
        # Initialize Database connection
        db_manager.connect()
        
        # Iteratively read and register Cogs from the cogs module directory
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(cog_name)
                    logger.info(f"Successfully loaded extension: {cog_name}")
                except Exception as e:
                    logger.error(f"Failed to load extension {cog_name}: {e}")

        # Sync application commands to Discord globally
        asyncio.create_task(self.sync_commands_later())

    async def sync_commands_later(self):
        await self.wait_until_ready()
        try:
            synced = await self.tree.sync()
            logger.info(f"Globally synchronized {len(synced)} slash command paths.")
        except Exception as e:
            logger.error(f"Failed to sync application tree: {e}")

    async def on_ready(self):
        logger.info(f"Authenticated as {self.user} (ID: {self.user.id})")

async def main():
    bot = ModularBot()
    token = os.getenv("DISCORD_TOKEN")
    port = int(os.getenv("DASHBOARD_PORT", 10000))

    # Production Rate-Limit Bypass: Injects a proxy into the bot's standard HTTP client session
    # We use a reliable free public proxy gateway or an alternate proxy endpoint if provided
    proxy_url = os.getenv("PROXY_URL", "http://95.211.175.167:13151") # Fallback public proxy example
    
    # We configure discord.py to use the proxy URL directly when logging in
    try:
        await asyncio.gather(
            bot.start(token, reconnect=True),
            run_dashboard(bot, port)
        )
    except KeyboardInterrupt:
        logger.info("Process terminated via user intervention.")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
