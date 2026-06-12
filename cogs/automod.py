import discord
from discord.ext import commands
from database import db_manager

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Targeted non-blocking collection initialization
        self.config_collection = db_manager.get_collection("automod_configs")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Evade feedback loops by filtering out application profile identity
        if message.author.bot or not message.guild:
            return

        # Simple high-speed asynchronous cache placeholder implementation lookup logic
        try:
            # Check database config for the guild
            guild_config = await self.config_collection.find_one({"guild_id": message.guild.id})
            banned_words = guild_config.get("banned_words", ["scam", "nitro-free", "malware"]) if guild_config else ["scam", "nitro-free", "malware"]
        except Exception:
            # Fallback block configuration to maintain security continuity in network drops
            banned_words = ["scam", "nitro-free", "malware"]

        content_processed = message.content.lower()
        if any(bad_word in content_processed for bad_word in banned_words):
            try:
                await message.delete()
                # Issue warning directly targeting the infraction context
                await message.channel.send(f"⚠️ {message.author.mention}, your post contained prohibited material violating server security protocols.", delete_after=5)
            except discord.Forbidden:
                pass # Bot lacks permission hierarchy to delete messages

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
