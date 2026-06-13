import discord
from discord.ext import commands
from discord import app_commands
import time
import platform

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"
BANNER_URL = "https://media.discordapp.net/attachments/1503357008722530377/1505483556959293628/11.png"

SUPPORT_SERVER_URL = "https://discord.gg/your-invite-link"
BOT_INVITE_URL = "https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID_HERE&permissions=8&scope=bot%20applications.commands"


class DashboardInteractiveButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Direct URL Link Navigation Row
        self.add_item(discord.ui.Button(label="Support Desk", url=SUPPORT_SERVER_URL, style=discord.ButtonStyle.link, emoji="📡"))
        self.add_item(discord.ui.Button(label="Invite v2.0 Core", url=BOT_INVITE_URL, style=discord.ButtonStyle.link, emoji="🚀"))


class DashboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()  # Track initialization time for uptime calculations

    # =====================================================
    # DASHBOARD SLASH COMMAND
    # =====================================================
    @app_commands.command(
        name="dashboard",
        description="Launch the primary Ender Bot system diagnostics and control dashboard"
    )
    async def launch_dashboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # 1. Calculate Uptime metrics dynamically
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_string = f"`{days}d {hours}h {minutes}m {seconds}s`"

        # 2. Extract Shard, Gateway and API Latency mappings
        gateway_ping = round(self.bot.latency * 1000)
        total_guilds = len(self.bot.guilds)
        total_members = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)

        # 3. Construct Premium Grid Matrix Embed
        embed = discord.Embed(
            title=f"⚡ {BOT_VERSION} • Operational Control Dashboard",
            description=(
                f"Welcome to the mainframe dashboard for **{BOT_VERSION}**.\n"
                f"All cluster tasks are performing within target optimization parameters.\n\n"
                f"📊 **System Status Matrix Overview:**"
            ),
            color=discord.Color.from_rgb(34, 36, 41) # Dark High-Contrast Panel
        )

        # Row 1: Core Performance Metrics
        embed.add_field(name="🛰️ Gateway Connection", value=f"`{gateway_ping}ms Latency`", inline=True)
        embed.add_field(name="⏳ Engine Uptime", value=uptime_string, inline=True)
        embed.add_field(name="🧬 Shard Clusters", value="`Cluster 01 / Active`", inline=True)

        # Row 2: Infrastructure Scale Data
        embed.add_field(name="🌐 Host Guilds", value=f"`{total_guilds} Clusters`", inline=True)
        embed.add_field(name="👥 Monitored Terminals", value=f"`{total_members:,} Users`", inline=True)
        embed.add_field(name="⚙️ Software Array", value=f"`Python {platform.python_version()}`", inline=True)

        # Design and asset injection
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=BRANDED_FOOTER)

        # Deploy response package with web buttons attached
        await interaction.followup.send(embed=embed, view=DashboardInteractiveButtons())


async def setup(bot):
    await bot.add_cog(DashboardCog(bot))
