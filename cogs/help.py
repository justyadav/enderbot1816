import discord
from discord import app_commands
from discord.ext import commands

# --- SYSTEM PALETTE ---
COLOR_PRIMARY = discord.Color.blurple()
COLOR_DARK = discord.Color.from_rgb(34, 36, 41)
CREATOR_CREDIT = "System Automation Engine"


# --- HELP CATEGORY DROPDOWN ---
class HelpDropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        options = [
            discord.SelectOption(label="System Core", description="Core application metrics, health info, and manuals.", emoji="📊", value="core"),
            discord.SelectOption(label="Moderation Suite", description="Administrative commands to manage server members.", emoji="🛡️", value="moderation"),
            discord.SelectOption(label="Ticket Engine", description="Commands to deploy and configure persistent support spaces.", emoji="🎫", value="tickets"),
        ]
        super().__init__(placeholder="📂 Choose a system engine to inspect...", min_values=1, max_values=1, custom_id="help_select_menu", options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        embed = discord.Embed(color=COLOR_PRIMARY, timestamp=discord.utils.utcnow())
        embed.set_footer(text=f"Requested by {interaction.user.display_name} • {CREATOR_CREDIT}")

        if selection == "core":
            embed.title = "📊 System Core Module"
            embed.description = "Active background metrics and application configuration utilities:\n\n"
            embed.add_field(name="`/info`", value="`└─` Pulls system performance charts, latency states, and application health data.", inline=False)
            embed.add_field(name="`/help`", value="`└─` Displays this interactive system guide manual database.", inline=False)

        elif selection == "moderation":
            embed.title = "🛡️ Moderation Security Suite"
            embed.description = "Privileged network access commands used to protect operations rooms:\n\n"
            embed.add_field(name="`/kick` [member] [reason]", value="`└─` Evicts target connection instantly from the current server cluster.", inline=False)
            embed.add_field(name="`/ban` [member] [reason]", value="`└─` Restricts target identifier permanently from re-authenticating access.", inline=False)
            embed.add_field(name="`/timeout` [member] [duration] [reason]", value="`└─` Temporary voice & text chat stream isolation restriction.", inline=False)

        elif selection == "tickets":
            embed.title = "🎫 Public Support Ticket Engine"
            embed.description = "Operational command lines for configuring help desks:\n\n"
            embed.add_field(name="`/ticket-setup` [channel] [category]", value="`└─` Initialize interactive persistent support dropdown matrices.", inline=False)
            embed.add_field(name="`/ticket_add` [member]", value="`└─` Forces a member profile permission overwrite into an open thread.", inline=False)
            embed.add_field(name="`/ticket_remove` [member]", value="`└─` Strips a profile's connection parameters from a restricted thread.", inline=False)
            embed.add_field(name="`/ticket_rename` [string]", value="`└─` Rewrites the local tag designator suffix index safely.", inline=False)

        await interaction.response.edit_message(embed=embed)


# --- HELP VIEW LAUNCHER ---
class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=180)
        self.add_item(HelpDropdown(bot))


# =========================================================
# SYSTEM HELP COG MODULE
# =========================================================
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Central command catalog directory and help documentation")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛠️ System Infrastructure Directory",
            description=(
                f"Use the slash command platform drop-down selection menu down "
                f"below to interface with active background subsystems."
            ),
            color=COLOR_DARK
        )
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
        embed.set_footer(text=f"System Framework Core • {CREATOR_CREDIT}")

        view = HelpView(self.bot)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
