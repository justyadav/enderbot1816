import discord
from discord import app_commands
from discord.ext import commands

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"

# --- REUSABLE HIGH-CONTRAST PALETTE ---
COLOR_MAIN_PANEL = discord.Color.from_rgb(47, 49, 54)     # Sleek Obsidian Grey
COLOR_ACTIVE_BLUE = discord.Color.from_rgb(114, 137, 218) # Discord Blurple Accent
COLOR_CONFIRM_GREEN = discord.Color.from_rgb(67, 181, 129) # Safe Mint Emerald


# --- HELP CATEGORY DROPDOWN ---
class HelpDropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        options = [
            discord.SelectOption(label="Utility Module", description="Core metrics, ping, uptime, and server statistics.", emoji="⚙️", value="utility"),
            discord.SelectOption(label="Ticket System", description="Commands to manage public ticket rooms and channels.", emoji="🎫", value="tickets"),
            discord.SelectOption(label="Automation Tools", description="Interactive polls, secure calculator, and reminders.", emoji="🛠️", value="tools"),
            discord.SelectOption(label="Support Hub", description="Official invitations and routing system help.", emoji="🆘", value="support")
        ]
        super().__init__(
            placeholder="📂 Choose a command category to display...", 
            min_values=1, 
            max_values=1, 
            custom_id="help_select_menu", 
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        embed = discord.Embed(color=COLOR_ACTIVE_BLUE, timestamp=discord.utils.utcnow())
        embed.set_footer(text=BRANDED_FOOTER)
        
        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        if selection == "utility":
            embed.title = "⚙️ Module: Utility Arrays"
            embed.description = "Essential systemic check tools for measuring runtime stability:"
            embed.add_field(name="`/ping`", value="`└─` Calculates system gateway ping and WebSocket communication delays.", inline=False)
            embed.add_field(name="`/stats`", value="`└─` Compiles local host architecture info, memory footprints, and guild counts.", inline=False)
            embed.add_field(name="`/uptime`", value="`└─` Checks elapsed intervals since the last hard process deployment.", inline=False)

        elif selection == "tickets":
            embed.title = "🎫 Module: Support Line Management"
            embed.description = "Publicly exposed controller paths for routing active incidents:"
            embed.add_field(name="`/ticket_add` [member]", value="`└─` Authorizes a profile token to access an active ticket stream.", inline=False)
            embed.add_field(name="`/ticket_remove` [member]", value="`└─` Drops a user access path entirely from the local channel array.", inline=False)
            embed.add_field(name="`/ticket_rename` [name]", value="`└─` Modifies the trailing metadata string label of a channel safely.", inline=False)
            embed.add_field(name="📌 Persistent Dashboard Panel", value="Use `/ticket_setup` via admin clearance to deploy the automated dropdown interface inside your operational zones.", inline=False)

        elif selection == "tools":
            embed.title = "🛠️ Module: Automation Engineering Tools"
            embed.description = "Ancillary data interaction features engineered for general server members:"
            embed.add_field(name="`/poll` [question]", value="`└─` Generates a clean feedback interaction stack for community metrics.", inline=False)
            embed.add_field(name="`/calculator`", value="`└─` Opens a secure visual calculator grid for simple floating math operations.", inline=False)
            embed.add_field(name="`/remind` [time] [text]", value="`└─` Places a back-end worker background task to ping you on custom intervals.", inline=False)

        elif selection == "support":
            embed.title = "🆘 Module: Centralized Support Infrastructure"
            embed.description = "Direct routing assistance arrays to link with development nodes:"
            embed.add_field(name="`/about`", value="`└─` Displays details about the framework, framework version, and software attributes.", inline=False)
            embed.add_field(name="`/invite`", value="`└─` Generates a clean URL redirection path to link the bot to other remote clusters.", inline=False)
            embed.add_field(name="🌐 System Terminal Links", value="[Developer Profile](https://discord.com/users/915121966562095144) • [Control Panel Network](https://discord.gg/)", inline=False)

        await interaction.response.edit_message(embed=embed, view=self.view)


# --- HELP VIEW CONTAINER ---
class HelpLauncher(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=180)
        self.add_item(HelpDropdown(bot))


# --- CENTRAL COMMAND COG ---
class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Queries the central control interface matrix directory")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✦ ━━━━━━━ Mainframe System Diagnostics ━━━━━━━ ✦",
            description=(
                f"Welcome to the **{BOT_VERSION}** Central Command Hub.\n"
                f"This environment provides links directly to your public module endpoints.\n\n"
                f"Use the drop-down selector matrix below to query active operational commands."
            ),
            color=COLOR_MAIN_PANEL,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="🌐 Network Node", value="`Render Cloud Platform`", inline=True)
        embed.add_field(name="⚡ Gateway Latency", value=f"`{round(self.bot.latency * 1000)}ms`", inline=True)
        embed.add_field(name="🔒 Core Security", value="`AES-Encrypted Streams`", inline=True)
        
        if interaction.guild and interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
            
        embed.set_footer(text=BRANDED_FOOTER)
        
        await interaction.response.send_message(embed=embed, view=HelpLauncher(self.bot))


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))
