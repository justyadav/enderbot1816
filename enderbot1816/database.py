import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConfigurationError  # Fixes NameError crash vector
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("Bot.Database")

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None

    async def initialize(self):
        """Establishes and verifies the async connection to the MongoDB Atlas cluster."""
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            logger.critical("MONGO_URI missing from environment configuration!")
            raise ValueError("MONGO_URI environment variable is not set.")
        
        # Initialize the Motor Async Client
        self.client = AsyncIOMotorClient(mongo_uri)
        
        try:
            # Enforce a non-blocking network ping test to verify credentials and IP whitelisting
            await self.client.admin.command('ping')
        except Exception as e:
            logger.critical(f"MongoDB network validation handshake failed: {e}")
            raise ConnectionError(f"Could not establish connection to MongoDB cluster: {e}")
        
        try:
            # Try to get the database defined directly in your connection URI string
            self.db = self.client.get_default_database()
        except ConfigurationError:
            # Fallback if your URI string doesn't end with a database name
            logger.warning("No default database found in MONGO_URI. Falling back to 'EnderBotDB'.")
            self.db = self.client["EnderBotDB"]
            
        logger.info("MongoDB Async infrastructure handshake verified and completed successfully.")

    def get_collection(self, name: str):
        """Helper to fetch a specific data collection."""
        if self.db is None:
            raise RuntimeError("DatabaseManager is not initialized! Call initialize() first.")
        return self.db[name]

# Export a single global instance to import across your project files
db_manager = DatabaseManager()