import discord
from discord.ext import commands
from database import db_manager

class Logging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        # Gracefully handle instances where message is missing or completely uncached
        if not message.guild or (message.author and message.author.bot):
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
            timestamp=message.created_at if message.created_at else discord.utils.utcnow()
        )
        
        # Safe fallback initialization for profiles outside active memory cache lines
        author_mention = message.author.mention if message.author else "Unknown User"
        author_id = message.author.id if message.author else "Unknown ID"
        channel_mention = message.channel.mention if hasattr(message.channel, 'mention') else f"#{message.channel}"
        
        embed.add_field(name="Sender Profile", value=f"{author_mention} (`{author_id}`)", inline=True)
        embed.add_field(name="Origin Location", value=channel_mention, inline=True)
        
        # Hardened character slicing prevents API crashes on long text arrays/Nitro inputs
        if message.content:
            if len(message.content) > 1024:
                content_fallback = f"{message.content[:1020]}..."
            else:
                content_fallback = message.content
        else:
            content_fallback = "*[No text payload or attachment data present]*"
            
        embed.add_field(name="Message Material Content", value=content_fallback, inline=False)

        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))