import discord
from discord import app_commands
from discord.ext import commands

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"

COLOR_MAIN_PANEL = discord.Color.from_rgb(22, 25, 32)      # Deep Cyber Charcoal
COLOR_ACTIVE_BLUE = discord.Color.from_rgb(168, 85, 247)   # Ender Purple Accent


class HelpDropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label="Mainframe Overview", 
                description="View system status, version modules, and operational load.", 
                emoji="🛰️", 
                value="overview"
            ),
            discord.SelectOption(
                label="Ticket Management", 
                description="Public operational commands for controlling active support lines.", 
                emoji="📥", 
                value="tickets"
            ),
            discord.SelectOption(
                label="System Security", 
                description="Overview of integrated security protocols and real-time filters.", 
                emoji="🛡️", 
                value="security"
            )
        ]
        super().__init__(
            placeholder="🛰️ Navigate the core database modules...",
            min_values=1,
            max_values=1,
            custom_id="ender_help_select_menu",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        
        if value == "overview":
            embed = discord.Embed(
                title="✦ ━━━━━━━ Mainframe Diagnostics ━━━━━━━ ✦",
                description=(
                    f"Welcome to the **{BOT_VERSION}** Central Command Hub.\n"
                    f"This environment links directly to your web control panel interface.\n\n"
                    f"Use the drop-down selector matrix below to query active operational files."
                ),
                color=COLOR_ACTIVE_BLUE
            )
            embed.add_field(name="🌐 Network Node", value="`Render Cloud Platform`", inline=True)
            embed.add_field(name="⚡ Gateway Latency", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
            embed.add_field(name="🔒 Core Security", value="`AES-Encrypted Streams`", inline=True)
            embed.set_footer(text=BRANDED_FOOTER)
            
        elif value == "tickets":
            embed = discord.Embed(
                title="📥 Module: Support Channel Controllers",
                description="Publicly exposed slash commands for monitoring and routing customer operations threads:",
                color=COLOR_ACTIVE_BLUE
            )
            embed.add_field(
                name="`/ticket_add` [member]", 
                value="`└─` Grants a secure user permission profile access inside an active operational room.", 
                inline=False
            )
            embed.add_field(
                name="`/ticket_remove` [member]", 
                value="`└─` Drops a user connection completely from the local thread array.", 
                inline=False
            )
            embed.add_field(
                name="`/ticket_rename` [name]", 
                value="`└─` Modifies the metadata textual label trailing index string safely.", 
                inline=False
            )
            embed.set_footer(text=f"Ticket Controls Module | {BRANDED_FOOTER}")
            
        elif value == "security":
            embed = discord.Embed(
                title="🛡️ Module: Integrated Automation Firewalls",
                description="Core automated modules configured directly via your web dashboard platform:",
                color=COLOR_ACTIVE_BLUE
            )
            embed.add_field(
                name="🔒 AutoMod Filters", 
                value="`└─ Status: Active` • Blocks custom lexicon spam strings and automated invite tracking objects.", 
                inline=False
            )
            embed.add_field(
                name="👥 Automated Clearance Roles", 
                value="`└─ Status: Active` • Automatically injects background structural access verification metrics to new arrivals.", 
                inline=False
            )
            embed.add_field(
                name="📝 Secure Incident Logging", 
                value="`└─ Status: Connected` • Forwards deep transcript logs directly onto designated cloud channels.", 
                inline=False
            )
            embed.set_footer(text=f"Security Cluster Framework | {BRANDED_FOOTER}")

        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
            
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpLauncher(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=180)
        self.add_item(HelpDropdown(bot))


class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Queries the central control interface matrix directory")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✦ ━━━━━━━ Mainframe Diagnostics ━━━━━━━ ✦",
            description=(
                f"Welcome to the **{BOT_VERSION}** Central Command Hub.\n"
                f"This environment links directly to your web control panel interface.\n\n"
                f"Use the drop-down selector matrix below to query active operational files."
            ),
            color=COLOR_ACTIVE_BLUE
        )
        embed.add_field(name="🌐 Network Node", value="`Render Cloud Platform`", inline=True)
        embed.add_field(name="⚡ Gateway Latency", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
        embed.add_field(name="🔒 Core Security", value="`AES-Encrypted Streams`", inline=True)
        
        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
            
        embed.set_footer(text=BRANDED_FOOTER)
        
        await interaction.response.send_message(embed=embed, view=HelpLauncher(self.bot))


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))                    f"Welcome to the user operations manual for **{BOT_VERSION}**.\n"
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
