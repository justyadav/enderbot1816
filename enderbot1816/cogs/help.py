import discord
from discord import app_commands
from discord.ext import commands
from database import db_manager

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot, guild_id: int, user_perms: discord.Permissions, mod_enabled: bool):
        self.bot = bot
        self.guild_id = guild_id
        self.user_perms = user_perms
        self.mod_enabled = mod_enabled

        options = [
            discord.SelectOption(label="General Subsystem", description="Core utility and information commands.", emoji="🤖", value="general"),
            discord.SelectOption(label="Ticket Matrix", description="Interactive user support pipeline tools.", emoji="🎫", value="tickets")
        ]

        # Only expose the moderation cluster choice if it's active and user has administrative scope
        if self.mod_enabled and self.user_perms.kick_members:
            options.append(discord.SelectOption(label="Staff Directives", description="Server enforcement and restriction utilities.", emoji="🔨", value="moderation"))

        super().__init__(placeholder="Select operational mainframe directory...", min_values=1, max_values=1, options=options, custom_id="ender_help_select")

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        embed = discord.Embed(color=discord.Color.from_rgb(88, 101, 242))
        
        if selection == "general":
            embed.title = "🤖 Mainframe Core • General Subsystem"
            embed.description = (
                "`/about` - Displays bot system telemetry, latency logs, and cluster runtimes.\n"
                "`/ping` - Test network packet connection round-trip delays.\n"
                "`/invite` - Generates secure OAuth application gateway authorization parameters."
            )
        elif selection == "tickets":
            embed.title = "🎫 Mainframe Core • Ticket Support Matrix"
            embed.description = (
                "`/ticket setup` - Deploys the automated persistent panel launcher layout inside a channel.\n"
                "`/ticket close` - Archives the current active communication secure line down to database.\n"
                "`/ticket add` - Append a specific profile entity into an isolated channel map target."
            )
        elif selection == "moderation":
            embed.title = "🔨 Mainframe Core • Staff Directives"
            embed.description = (
                "`/kick` - Sever a disruptive user entity out from the active server cluster.\n"
                "`/ban` - Permban malicious actors and register identity to the server network barrier.\n"
                "`/clear` - Purge a targeted index volume of message payloads out from channel history maps."
            )

        embed.set_footer(text="Ender Control Matrix Framework V2.0")
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot, guild_id: int, user_perms: discord.Permissions, mod_enabled: bool):
        super().__init__(timeout=180) # Form stays alive for 3 minutes
        self.add_item(HelpDropdown(bot, guild_id, user_perms, mod_enabled))


class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    @app_commands.command(name="help", description="Access the interactive system command directory blueprint.")
    async def help_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        if not guild:
            return await interaction.followup.send("❌ Mainframe directories can only be queried inside functional server clusters.", ephemeral=True)

        # Query database configuration settings to adjust command availability maps
        settings = await self.config_collection.find_one({"guild_id": guild.id}) or {}
        mod_cmds_enabled = settings.get("mod_cmds_enabled", True)

        # Construct primary entry map layout
        embed = discord.Embed(
            title="⚙️ Ender System Mainframe Directory",
            description=(
                "Welcome to the central automation terminal hub. Access specific cluster commands "
                "by interacting with the secure matrix directory dropdown selector below.\n\n"
                "**Operational Status Lines:**\n"
                f"🛡️ Core AutoMod: `{ 'ONLINE' if settings.get('automod_enabled', True) else 'OFFLINE' }`\n"
                f"🔨 Staff Directives: `{ 'ONLINE' if mod_cmds_enabled else 'DISABLED_VIA_DASHBOARD' }`"
            ),
            color=discord.Color.from_rgb(15, 17, 21)
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.name} • Security Level Verified", icon_url=interaction.user.display_avatar.url)

        view = HelpView(self.bot, guild.id, interaction.user.guild_permissions, mod_cmds_enabled)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))