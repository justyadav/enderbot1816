import discord
from discord import app_commands
from discord.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Evict an abusive user from the current guild.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No explicit reason specified."):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Command execution denied: Target user possesses equal or higher role hierarchy.", ephemeral=True)
            
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ **{member.tag}** has been successfully kicked. Reason: {reason}")

    @app_commands.command(name="ban", description="Permanently bar an abusive user from the guild.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No explicit reason specified."):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Command execution denied: Target user possesses equal or higher role hierarchy.", ephemeral=True)
            
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ **{member.tag}** has been permanently banned. Reason: {reason}")

    @app_commands.command(name="timeout", description="Isolate a user temporarily, suspending voice and text transmission permissions.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No explicit reason specified."):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Command execution denied: Target user possesses equal or higher role hierarchy.", ephemeral=True)
            
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout(duration, reason=reason)
        await interaction.response.send_message(f"✅ **{member.tag}** has been placed in isolation for {minutes} minutes. Reason: {reason}")

    # Cog-local handler for modern slash command exceptions
    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ Access Denied: You lack the requisite administrative permissions (`{missing_perms}`) to issue this instruction.", ephemeral=True)
        else:
            if not interaction.response.is_done():
                await interaction.response.send_message("⚠️ An unexpected application exception disrupted this transaction.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))