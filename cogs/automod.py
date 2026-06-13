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

        # Check if the user has administrator permissions to bypass the system
        if message.author.guild_permissions.administrator:
            return

        settings = await self.config_collection.find_one({"guild_id": message.guild.id}) or {}
        if not settings.get("automod_enabled", True):
            return

        banned_words = settings.get("banned_words", ["scam", "nitro-free"])
        message_content = message.content.lower()

        if any(word in message_content for word in banned_words):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, that word is restricted in this server.", delete_after=5)
            except discord.Forbidden:
                pass  

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
