import discord
from discord.ext import commands
from database import db_manager

# --- SYSTEM BRANDING CONSTANTS ---
BOT_VERSION = "Ender Bot v2.0"
CREATOR_CREDIT = "System Automation Engine"
BRANDED_FOOTER = f"{BOT_VERSION} • {CREATOR_CREDIT} | Made by yaduvanshi1816_"

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Core collection connection for matrix settings
        self.config_collection = db_manager.get_collection("guild_settings")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Prevent loops from other bot entities or non-guild DM vectors
        if message.author.bot or not message.guild:
            return

        # Core Override: Administrative entities bypass structural auto-moderation filters
        if message.author.guild_permissions.administrator:
            return

        # Fetch active configuration map from database (assuming async motor configuration)
        # Fallback to default empty schema if guild document does not exist
        try:
            settings = await self.config_collection.find_one({"guild_id": message.guild.id}) or {}
        except TypeError:
            # Fallback if the underlying db connection engine requires thread pool execution
            settings = self.config_collection.find_one({"guild_id": message.guild.id}) or {}
        
        # Check if dashboard switch has deactivated automod systems
        if not settings.get("automod_enabled", True):
            return

        # Retrieve structural blacklist filters (Defaults protect against standard exploitation arrays)
        banned_words = settings.get("banned_words", ["scam", "nitro-free"])
        message_content = message.content.lower()

        # Scanning message payload array for restricted elements
        if any(word in message_content for word in banned_words):
            try:
                # Vaporize corrupted or malicious payload from channel stream
                await message.delete()
                
                # Emit warning notice with temporary lifecycle visibility
                await message.channel.send(
                    f"⚠️ **Security Warning:** {message.author.mention}, your message payload triggered our structural keyword filters and was purged.", 
                    delete_after=5
                )
            except discord.Forbidden:
                # Execution failed due to missing administrative hierarchy/permissions inside target guild
                pass  
            except discord.NotFound:
                # Message was already processed or removed concurrently by another security framework
                pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))