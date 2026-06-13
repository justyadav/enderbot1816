import discord
from discord.ext import commands
from database import db_manager

class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        settings = await self.config_collection.find_one({"guild_id": message.guild.id}) or {}
        channel_id = settings.get("logging_channel_id")
        
        if not channel_id:
            return  

        log_channel = message.guild.get_channel(channel_id)
        if not log_channel:
            return  

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red(),
            timestamp=message.created_at
        )
        embed.add_field(name="Sender Profile", value=f"{message.author.mention} (`{message.author.id}`)", inline=True)
        embed.add_field(name="Origin Location", value=message.channel.mention, inline=True)
        
        content_fallback = message.content if message.content else "*[No text payload present]*"
        embed.add_field(name="Message Material Content", value=content_fallback, inline=False)

        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))
