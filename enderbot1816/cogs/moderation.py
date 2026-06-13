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
    async def kick_cmd(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason specified"):
        # 1. Run the dashboard toggle check
        if not await self.check_mod_status(interaction):
            return

        guild = interaction.guild

        # 2. Protection Layer: Prevent kicking the server owner
        if member.id == guild.owner_id:
            return await interaction.response.send_message("❌ Security Exception: You cannot kick the server owner.", ephemeral=True)

        # 3. Protection Layer: Verify Moderator role hierarchy position
        if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
            return await interaction.response.send_message("❌ Hierarchy Exception: Your highest role must be above the target's highest role.", ephemeral=True)

        # 4. Protection Layer: Verify Bot role hierarchy position
        if guild.me.top_role <= member.top_role:
            return await interaction.response.send_message("❌ Hierarchy Exception: My highest role is too low to kick this member. Move my role higher in settings.", ephemeral=True)

        # 5. Execution Layer: Safe wrapping prevents unhandled API crashes
        try:
            await member.kick(reason=f"Executed by {interaction.user.name} | Reason: {reason}")
            await interaction.response.send_message(f"🔨 **{member.name}** has been kicked. Reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Execution Failed: Missing permissions to perform this action.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Execution Failed: An unexpected network error occurred:\n```{e}```", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))