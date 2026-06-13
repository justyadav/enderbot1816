import discord
from discord import app_commands
from discord.ext import commands

BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"

class GlobalErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Register the app command error tree hook
        bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # Handle Missing Permissions
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="🔒 Security Clearance Access Denied",
                description=f"Your profile lacks the explicit permissions required to execute this operations array.\n\n**Required:** `{', '.join(error.missing_permissions)}`",
                color=discord.Color.red()
            )
            embed.set_footer(text=BRANDED_FOOTER)
            if interaction.response.is_done():
                return await interaction.followup.send(embed=embed, ephemeral=True)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Handle Cooldown Restrictions
        elif isinstance(error, app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏳ Rate Limit Lockdown Active",
                description=f"Mainframe protection throttling active. Please hold alignment operations.\n\n**Retry In:** `{error.retry_after:.2f} seconds`",
                color=discord.Color.from_rgb(255, 191, 0)
            )
            embed.set_footer(text=BRANDED_FOOTER)
            if interaction.response.is_done():
                return await interaction.followup.send(embed=embed, ephemeral=True)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Fallback handling for sudden unhandled fatal runtime breakages
        else:
            embed = discord.Embed(
                title="🚨 Internal Engineering Error",
                description=f"An unhandled execution fault occurred inside the v2.0 runtime logic pipeline.\n
http://googleusercontent.com/immersive_entry_chip/0
