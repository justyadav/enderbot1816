import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("Bot.Database")

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None

    async def initialize(self):
        """Establishes the async connection to the MongoDB Atlas cluster."""
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            logger.critical("MONGO_URI missing from environment configuration!")
            raise ValueError("MONGO_URI environment variable is not set.")
        
        # Initialize the Motor Async Client
        self.client = AsyncIOMotorClient(mongo_uri)
        
        # Automatically extracts the database name from your connection string or defaults to 'EnderBotDB'
        self.db = self.client.get_default_database(default_database='EnderBotDB')
        logger.info("MongoDB Async handshake completed successfully.")

    def get_collection(self, name: str):
        """Helper to fetch a specific data collection."""
        if self.db is None:
            raise RuntimeError("DatabaseManager is not initialized! Call initialize() first.")
        return self.db[name]

# Export a single global instance to import across your project files
db_manager = DatabaseManager()
