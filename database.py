import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("Bot.Database")

class DatabaseManager:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.client = None
        self.db = None

    def connect(self):
        try:
            # Initialize the AsyncIO Motor Client
            self.client = AsyncIOMotorClient(self.mongo_uri)
            # Database name extracted or targeted (defaulting to 'bot_prod')
            self.db = self.client["bot_prod"]
            logger.info("Successfully initiated Motor MongoDB connection.")
        except Exception as e:
            logger.critical(f"Failed to connect to MongoDB: {e}")
            raise e

    def get_collection(self, name: str):
        if self.db is None:
            self.connect()
        return self.db[name]

# Global database manager instance
db_manager = DatabaseManager()