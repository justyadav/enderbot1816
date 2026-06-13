import discord
from discord.ext import commands
from discord import app_commands

# =========================================================
# CONSTANTS & CONFIGURATION
# =========================================================
GUILD_ID = 1503037186034110595  # Hard-locked to your development tree
CREATOR_CREDIT = "Ender Bot X Kitecloud • Reliable Cloud Solutions | Made by yaduvanshi1816_"
BANNER_URL = "https://media.discordapp.net/attachments/1503357008722530377/1505483556959293628/11.png"

class BotInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # BOT INFO SLASH COMMAND
    # =====================================================
    @app_commands.command(
        name="botinfo",
        description="Display information and performance statistics for Ender Bot"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def bot_info(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Dynamic footprint calculation across all joined shards/guilds
        total_guilds = len(self.bot.guilds)
        total_members = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)

        # Premium structural Embed design
        embed = discord.Embed(
            title="🤖 Ender Bot X Stats & Specifications",
            description="Reliable systems administration and enterprise management solutions.",
            color=discord.Color.purple()
        )
        
        # Grid layout fields
        embed.add_field(name="✨ Bot Version", value="`Ender Bot v2.0`", inline=True)
        embed.add_field(name="👑 Developer", value="`yaduvanshi1816_`", inline=True)
        embed.add_field(name="📡 Support Server", value="[Join Support Server](https://discord.gg/your-invite-link)", inline=True)
        
        embed.add_field(name="🌐 Infrastructure Guilds", value=f"`{total_guilds} Servers`", inline=True)
        embed.add_field(name="👥 Total Members", value=f"`{total_members:,} Users`", inline=True)
        embed.add_field(name="⚡ Processing Core", value="`Discord.py v2.4.0`", inline=True)

        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=CREATOR_CREDIT)

        await interaction.followup.send(embed=embed)


# =========================================================
# COG REGISTRATION COROUTINE
# =========================================================
async def setup(bot):
    await bot.add_cog(BotInfoCog(bot))
