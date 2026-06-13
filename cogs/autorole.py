import discord
from discord.ext import commands
from database import db_manager
import logging

logger = logging.getLogger("Bot.Autorole")

class Autorole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_collection = db_manager.get_collection("guild_settings")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Ignore bot integrations joining the server
        if member.bot:
            return

        # 1. Fetch this server's specific configuration from MongoDB
        settings = await self.config_collection.find_one({"guild_id": member.guild.id}) or {}
        role_id = settings.get("autorole_id")

        if not role_id:
            return  # Autorole field is blank or unconfigured on the dashboard

        # 2. Locate the targeted role within the server cache
        role = member.guild.get_role(role_id)
        if not role:
            logger.warning(f"Autorole mismatch in {member.guild.name}: Role ID {role_id} no longer exists.")
            return

        # 3. Attempt role assignment
        try:
            await member.add_roles(role, reason="Ender Bot Autorole Integration Pipeline")
            logger.info(f"Successfully assigned autorole '{role.name}' to {member.name} in {member.guild.name}")
        except discord.Forbidden:
            logger.error(
                f"❌ Permission Error: Cannot assign role '{role.name}' in '{member.guild.name}'. "
                f"Fix this by opening Discord -> Server Settings -> Roles, and dragging the 'Ender Bot' "
                f"integration role ABOVE the '{role.name}' role in the hierarchy list."
            )
        except Exception as e:
            logger.error(f"Unexpected error executing autorole context: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Autorole(bot))
