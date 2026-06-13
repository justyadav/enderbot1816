import discord
from discord.ext import commands
from database import db_manager

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # 1. Fetch live toggle status from database
        settings = await self.config_collection.find_one({"guild_id": message.guild.id}) or {}
        is_automod_on = settings.get("automod_enabled", True) # Default to true if not set

        # 2. If it's turned off on the dashboard, abort!
        if not is_automod_on:
            return

        # Run filtering checks if turned on
        banned_words = ["scam", "nitro-free", "malware"]
        if any(word in message.content.lower() for word in banned_words):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, bad words are restricted here.", delete_after=5)
            except discord.Forbidden:
                pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
