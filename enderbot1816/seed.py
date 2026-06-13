import asyncio
import os
import logging
from database import db_manager
from dotenv import load_dotenv

# Setup minimal logging to align with the database manager's feedback stream
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Bot.Seeder")

load_dotenv()

async def seed_data():
    # 1. Corrected Method Call: Await the verified async infrastructure initialization
    try:
        logger.info("Initializing database manager handshake for seeding...")
        await db_manager.initialize()
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}")
        return

    # 2. Corrected Target Layer: Route data to 'guild_settings' to match dashboard configurations
    config_collection = db_manager.get_collection("guild_settings")
    
    # Replace with your actual test Discord server/guild ID
    sample_guild_id = 123456789012345678 
    
    logger.info(f"Writing security parameters for Guild ID: {sample_guild_id}...")
    
    await config_collection.update_one(
        {"guild_id": sample_guild_id},
        {
            "$set": {
                "automod_enabled": True,
                "mod_cmds_enabled": True,
                "transcript_enabled": True,
                "close_reason_enabled": True,
                "banned_words": ["scam", "nitro-free", "malware", "crypto-gift"],
                "logging_channel_id": None,
                "ticket_category_id": None,
                "ticket_banner_url": "",
                "autorole_id": None
            }
        },
        upsert=True
    )
    print("🚀 Database configuration seeded successfully into 'guild_settings'!")

if __name__ == "__main__":
    try:
        asyncio.run(seed_data())
    except (KeyboardInterrupt, SystemExit):
        print("\nSeeding routine terminated safely.")