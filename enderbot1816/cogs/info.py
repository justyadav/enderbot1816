import discord
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="info", description="Check the running operational statistics of the bot application.")
    async def info_cmd(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000, 2)
        embed = discord.Embed(
            title="⚙️ Application Core Status", 
            color=discord.Color.blue()
        )
        embed.add_field(name="Gateway Latency", value=f"`{latency}ms`", inline=True)
        embed.add_field(name="Guild Standby Count", value=f"`{len(self.bot.guilds)}` servers", inline=True)
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Displays an organized layout of accessible utility systems.")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛠️ System Infrastructure Directory",
            description="Use the slash command platform to interface with active background subsystems.",
            color=discord.Color.green()
        )
        embed.add_field(name="📊 System Core", value="`/info` - Application health data\n`/help` - Operational manual", inline=False)
        embed.add_field(name="🛡️ Moderation Suite", value="`/kick` - Evict target\n`/ban` - Restrict target permanently\n`/timeout` - Temporary voice & chat isolation", inline=False)
        embed.add_field(name="🎫 Ticket Engine", value="`/setup` - Initialize interactive persistent support matrix", inline=False)
        
        # Send ephemeral to ensure clean user experience without channel cluttering
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))