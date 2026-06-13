import asyncio
import os
from database import db_manager
from dotenv import load_dotenv

load_dotenv()

async def seed_data():
    db_manager.connect()
    config_collection = db_manager.get_collection("automod_configs")
    
    # Replace with your actual test Discord server/guild ID
    sample_guild_id = 123456789012345678 
    
    await config_collection.update_one(
        {"guild_id": sample_guild_id},
        {"$set": {"banned_words": ["scam", "nitro-free", "malware", "crypto-gift"]}},
        upsert=True
    )
    print("Database configuration seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())