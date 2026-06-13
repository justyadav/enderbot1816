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
        
        # Define the categories matching your public cogs
        options = [
            discord.SelectOption(label="Utility Module", description="Core metrics, ping, uptime, and server statistics.", emoji="⚙️", value="utility"),
            discord.SelectOption(label="Ticket System", description="Commands to manage public ticket rooms and channels.", emoji="🎫", value="tickets"),
            discord.SelectOption(label="Automation Tools", description="Interactive polls, secure calculator, and reminders.", emoji="🛠️", value="tools"),
            discord.SelectOption(label="Support Hub", description="Official invitations and routing system help.", emoji="🆘", value="support")
        ]
        super().__init__(placeholder="📂 Choose a command category...", min_values=1, max_values=1, custom_id="help_select_menu", options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        embed = discord.Embed(color=COLOR_PRIMARY, timestamp=discord.utils.utcnow())
        embed.set_footer(text=f"Requested by {interaction.user.display_name} • {CREATOR_CREDIT}")

        # Map your select dropdown values directly to your Cog class names
        cog_mapping = {
            "utility": ("Utility", "⚙️ General Utility Commands"),
            "tickets": ("Tickets", "🎫 Public Ticket Controls"),
            "tools": ("Tools", "🛠️ Advanced Tool Engines"),
            "support": ("Support", "🆘 Support & Routing")
        }
        
        cog_name, title = cog_mapping.get(selection, (None, None))
        cog = self.bot.get_cog(cog_name)

        embed.title = title
        
        # fallback manual commands array showoff if a specific cog hasn't fully registered yet on startup
        if not cog:
            embed.description = f"Here are the active, public application commands available inside **{cog_name or selection.capitalize()}**:\n\n"
            if selection == "tickets":
                embed.add_field(name="/ticket_setup", value="└ Deploys the highly aesthetic ticket launcher dropdown configuration", inline=False)
                embed.add_field(name="/ticket_add", value="└ Grant a user access to the ticket channel", inline=False)
                embed.add_field(name="/ticket_remove", value="└ Revoke a user's access from the ticket channel", inline=False)
                embed.add_field(name="/ticket_rename", value="└ Quick-rename the channel tag prefix", inline=False)
            elif selection == "utility":
                embed.add_field(name="/ping", value="└ Calculates system gateway ping and response latency.", inline=False)
                embed.add_field(name="/stats", value="└ Compiles host system performance metrics.", inline=False)
            elif selection == "tools":
                embed.add_field(name="/poll", value="└ Generates an interactive feedback binary poll option array.", inline=False)
                embed.add_field(name="/calculator", value="└ Opens a secure ui calculations matrix.", inline=False)
            else:
                embed.add_field(name="/invite", value="└ Generates secondary connection routing links for the cluster.", inline=False)
        else:
            embed.description = f"Here are the active, public application commands available inside **{cog_name}**:\n\n"
            commands_found = False
            for cmd in cog.get_app_commands():
                # EXCLUSION RULE: Skip commands containing private server IDs
                if cmd.guild_ids:
                    continue
                    
                embed.add_field(
                    name=f"/{cmd.name}",
                    value=f"└ {cmd.description or 'No structural description provided.'}",
                    inline=False
                )
                commands_found = True

            if not commands_found:
                embed.description += "*No public global commands found in this module.*"

        # Safe update modification pattern utilizing direct execution blocks
        await interaction.response.edit_message(embed=embed)


# --- HELP VIEW LAUNCHER ---
class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=180)  # Timeout after 3 minutes of inactivity
        self.add_item(HelpDropdown(bot))


# =========================================================
# SYSTEM HELP COG MODULE
# =========================================================
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="📖 Open the central command catalog directory and help documentation")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✦ ━━━━━━━ System Directory Hub ━━━━━━━ ✦",
            description=(
                f"Welcome to the interactive system guide manual.\n\n"
                f"Use the drop-down selection menu element down below to parse through "
                f"available public commands sorted by their respective framework layers."
            ),
            color=COLOR_DARK
        )
        
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
        embed.add_field(name="🛡️ Privacy Layer Active", value="`Private / Guild-Locked commands are filtered natively.`", inline=False)
        embed.set_footer(text=f"System Framework Core • {CREATOR_CREDIT}")

        view = HelpView(self.bot)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
