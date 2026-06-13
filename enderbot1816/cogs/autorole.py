import discord
from discord.ext import commands
from database import db_manager
import logging

# Set up logging channels specifically for the core framework
logger = logging.getLogger("Bot.Autorole")

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"

class Autorole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Core collection connection for matrix settings
        self.config_collection = db_manager.get_collection("guild_settings")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Ignore bot integrations joining the server frame
        if member.bot:
            return

        logger.info(f"👤 Detection: Member {member.name} successfully connected to {member.guild.name}. Querying database...")
        role = None  # FIXED: Initialize to None to prevent UnboundLocalError reference failures in error catchers

        try:
            # 1. Fetch this server's specific configuration from MongoDB 
            # (Checks both raw integer and string variants to prevent data type collisions from the dashboard web-hook)
            try:
                settings = await self.config_collection.find_one({
                    "$or": [
                        {"guild_id": member.guild.id},
                        {"guild_id": str(member.guild.id)}
                    ]
                })
            except TypeError:
                # Fallback handler if the underlying db manager engine uses thread pool execution
                settings = self.config_collection.find_one({
                    "$or": [
                        {"guild_id": member.guild.id},
                        {"guild_id": str(member.guild.id)}
                    ]
                })

            if not settings:
                logger.warning(f"⚠️ Autorole aborted: No database record payload found for guild: {member.guild.name} ({member.guild.id})")
                return

            raw_role_id = settings.get("autorole_id")
            if not raw_role_id:
                logger.info(f"ℹ️ Autorole skipped: Feature is currently unconfigured or left blank for {member.guild.name}.")
                return

            # Ensure the role ID is cast properly as a flat numerical integer
            try:
                role_id = int(raw_role_id)
            except ValueError:
                logger.error(f"❌ Database Validation Error: Stored role ID '{raw_role_id}' is not a valid number matrix link.")
                return

            # 2. Locate the targeted role within the server cache
            role = member.guild.get_role(role_id)
            if not role:
                logger.warning(f"❌ Autorole Mismatch in {member.guild.name}: Role ID {role_id} cannot be found in server cache.")
                return

            # 3. Attempt role assignment
            await member.add_roles(role, reason="Ender Bot Autorole Integration Pipeline")
            logger.info(f"✅ Success: Assigned autorole '{role.name}' to {member.name} inside {member.guild.name}")

        except discord.Forbidden:
            role_name_str = role.name if role else f"ID: {raw_role_id}"
            logger.error(
                f"❌ Permission Error: Cannot assign role '{role_name_str}' in '{member.guild.name}'. "
                f"Fix this by opening Discord -> Server Settings -> Roles, and dragging the 'Ender Bot' "
                f"integration role ABOVE the target role in the hierarchy list."
            )
        except Exception as e:
            logger.error(f"❌ Unexpected error executing autorole context: {e}", exc_info=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Autorole(bot))