import discord
from discord import app_commands
from discord.ext import commands
from database import db_manager

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    # Helper function to check if moderation commands are active
    async def check_mod_status(self, interaction: discord.Interaction) -> bool:
        settings = await self.config_collection.find_one({"guild_id": interaction.guild_id}) or {}
        is_enabled = settings.get("mod_cmds_enabled", True)
        
        if not is_enabled:
            await interaction.response.send_message("❌ Moderation commands are currently disabled via the web dashboard.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="kick", description="Kick a disruptive user from the server.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason specified"):
        # Run the dashboard toggle check
        if not await self.check_mod_status(interaction):
            return

        await member.kick(reason=reason)
        await interaction.response.send_message(f"🔨 **{member.name}** has been kicked. Reason: {reason}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
