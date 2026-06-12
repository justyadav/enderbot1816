import discord
from discord.ext import commands
from database import db_manager

class AutoRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.role_collection = db_manager.get_collection("autorole_configs")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        try:
            config = await self.role_collection.find_one({"guild_id": guild.id})
            role_id = config["role_id"] if config else None
        except Exception:
            role_id = None

        # Fallback structure looks for a text-matched fallback entity if database reference is missing
        if role_id:
            role = guild.get_role(role_id)
        else:
            role = discord.utils.get(guild.roles, name="Member")

        if role:
            try:
                await member.add_roles(role, reason="Auto-assigned onboarding security policy validation role.")
            except discord.Forbidden:
                pass # Check hierarchical positions relative to target execution tree

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoRole(bot))