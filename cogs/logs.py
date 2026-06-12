import discord
from discord.ext import commands
from database import db_manager

class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logs_collection = db_manager.get_collection("log_channels")

    async def _get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        try:
            config = await self.logs_collection.find_one({"guild_id": guild.id})
            if config:
                return guild.get_channel(config["channel_id"])
        except Exception:
            pass
        # Fallback layout looks for a text channel named 'server-logs'
        return discord.utils.get(guild.text_channels, name="server-logs")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        log_channel = await self._get_log_channel(message.guild)
        if not log_channel:
            return

        embed = discord.Embed(title="🗑️ Text Message Cleared", color=discord.Color.red(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Author Information", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
        embed.add_field(name="Channel Target Context", value=message.channel.mention, inline=False)
        embed.add_field(name="Purged Context Material", value=message.content or "*No text material present (Attachment or Embed)*", inline=False)
        
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content or not before.guild:
            return
        log_channel = await self._get_log_channel(before.guild)
        if not log_channel:
            return

        embed = discord.Embed(title="📝 Content Revision Tracked", color=discord.Color.orange(), timestamp=discord.utils.utcnow())
        embed.add_field(name="Author Profile", value=f"{before.author.mention} (`{before.author.id}`)", inline=False)
        embed.add_field(name="Location Context", value=before.channel.mention, inline=False)
        embed.add_field(name="Original State", value=before.content, inline=True)
        embed.add_field(name="Revised State", value=after.content, inline=True)
        
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        log_channel = await self._get_log_channel(member.guild)
        if not log_channel:
            return

        embed = discord.Embed(title="🔊 Voice Connectivity Lifecycle Event", color=discord.Color.purple(), timestamp=discord.utils.utcnow())
        embed.set_author(name=f"{member.name} Status Evolution", icon_url=member.display_avatar.url)

        if before.channel is None and after.channel is not None:
            embed.description = f"➡️ Member connected to channel: **{after.channel.name}**"
        elif before.channel is not None and after.channel is None:
            embed.description = f"⬅️ Member disconnected from channel: **{before.channel.name}**"
        elif before.channel != after.channel:
            embed.description = f"🔀 Member migrated from channel **{before.channel.name}** to **{after.channel.name}**"
        else:
            return # Ignore minor state modifications like individual local mute/deafen updates

        await log_channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))