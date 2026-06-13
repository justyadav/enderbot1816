import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger("Bot.ErrorHandler")

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"

class GlobalErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Register the app command error tree hook
        bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # FIXED: Extract the true root cause if the exception is wrapped inside a generic CheckFailure container
        if isinstance(error, app_commands.CheckFailure) and error.__cause__:
            error = error.__cause__

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
            # Clean up the console telemetry log for backend debugging
            logger.error(f"❌ Core Exception Failure caught by handler: {error}", exc_info=error)
            
            # FIXED: Repaired the broken multiline string SyntaxError loop
            embed = discord.Embed(
                title="🚨 Internal Engineering Error",
                description="An unhandled execution fault occurred inside the v2.0 runtime logic pipeline.\n\nThe administration logs have been generated for debugging review.",
                color=discord.Color.red()
            )
            embed.set_footer(text=BRANDED_FOOTER)
            
            try:
                if interaction.response.is_done():
                    return await interaction.followup.send(embed=embed, ephemeral=True)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(GlobalErrorHandler(bot))