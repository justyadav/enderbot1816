import discord
from discord.ext import commands
from discord import app_commands

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"
BANNER_URL = "https://media.discordapp.net/attachments/1503357008722530377/1505483556959293628/11.png"

COLOR_DARK = discord.Color.from_rgb(34, 36, 41)


class HelpDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="System Overview", description="Ender Bot v2.0 specifications & general instructions.", emoji="🤖", value="overview"),
            discord.SelectOption(label="Public Utilities", description="Everyday commands available to all users.", emoji="⚙️", value="utility"),
            discord.SelectOption(label="Support Desk Help", description="How to initialize private assistance channels.", emoji="📂", value="support")
        ]
        super().__init__(
            placeholder="📚 Select a directory to view commands...",
            min_values=1,
            max_values=1,
            custom_id="ender_help_dropdown",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        # 1. OVERVIEW SCREEN
        if selection == "overview":
            embed = discord.Embed(
                title=f"🤖 {BOT_VERSION} Mainframe Help Menu",
                description=(
                    f"Welcome to the user operations manual for **{BOT_VERSION}**.\n"
                    f"This bot features modular high-performance systems optimized for community scaling.\n\n"
                    f"Use the selection dropdown menu below to navigate through the available instruction sets."
                ),
                color=COLOR_DARK
            )
            embed.add_field(name="🌐 Host Matrix", value="Running on dedicated high-speed cloud infrastructure arrays.", inline=False)

        # 2. PUBLIC UTILITIES
        elif selection == "utility":
            embed = discord.Embed(
                title="⚙️ Public Utility Matrix",
                description="These baseline data utilities are fully un-restricted and accessible to all server members globally.",
                color=discord.Color.blurple()
            )
            embed.add_field(name="📊 `/dashboard`", value="Launches the central system monitoring analytics and link arrays.", inline=False)
            embed.add_field(name="🛰️ `/botinfo`", value="Exposes real-time scaling counts, global population numbers, and specifications.", inline=False)
            embed.add_field(name="⏳ `/uptime`", value="Displays the duration the core engine has been continuously running online.", inline=False)
            embed.add_field(name="👤 `/userinfo`", value="Inspects profile parameters and account data stamps for any user.", inline=False)
            embed.add_field(name="🌐 `/serverinfo`", value="Compiles explicit operational data and demographic logs for this guild.", inline=False)
            embed.add_field(name="🚀 `/invite`", value="Generates the secure network authorization link to add the bot elsewhere.", inline=False)

        # 3. SUPPORT DESK HELP
        elif selection == "support":
            embed = discord.Embed(
                title="📂 Support & Ticket Operations",
                description="How to interact with the enterprise assistance grid inside this environment.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="🛠️ Initializing a Ticket Room",
                value="Locate the server's designated support hub, look for our custom dropdown selector panel, and pick your case category. The bot will automatically split-clone a private room for you.",
                inline=False
            )
            embed.add_field(
                name="🔒 Private Channel Safety",
                value="All internal conversation modules remain heavily locked away from standard members. Only you and authorized administration staff have clearance.",
                inline=False
            )

        # Apply persistent styling parameters across changes
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=BRANDED_FOOTER)
        
        # Edit the message with the newly pulled embed page data
        await interaction.message.edit(embed=embed, view=self.view)
        await interaction.response.defer()


class HelpMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Infinite UI persistence across cluster reboots
        self.add_item(HelpDropdown())


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Automatically attach the persistent UI view object to the background thread pool
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(HelpMenuView())

    # =====================================================
    # GLOBAL HELP COMMAND
    # =====================================================
    @app_commands.command(
        name="help",
        description="View the interactive public instruction matrix for Ender Bot v2.0"
    )
    async def help_command(self, interaction: discord.Interaction):
        # Default landing splash page configuration
        embed = discord.Embed(
            title=f"🤖 {BOT_VERSION} Mainframe Help Menu",
            description=(
                f"Welcome to the user operations manual for **{BOT_VERSION}**.\n"
                f"This bot features modular high-performance systems optimized for community scaling.\n\n"
                f"Use the selection dropdown menu below to navigate through the available instruction sets."
            ),
            color=COLOR_DARK
        )
        embed.add_field(name="🌐 Host Matrix", value="Running on dedicated high-speed cloud infrastructure arrays.", inline=False)
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=BRANDED_FOOTER)

        # Deploy directly as a visible, non-ephemeral stream so multiple users can read it
        await interaction.response.send_message(embed=embed, view=HelpMenuView())


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
