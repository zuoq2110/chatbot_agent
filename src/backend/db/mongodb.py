import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class MongoDBSettings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ai_chat"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = ""
    LANGCHAIN_PROJECT: str = ""
    RAG_MODEL: str = ""
    GEMINI_MODEL: str = ""
    GOOGLE_API_KEY: str = ""
    POSTGRES_URI: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: str = ""
    PORT: str = ""
    DEV_MODE: str = ""
    LOG_LEVEL: str = ""
    
    class Config:
        env_file = ".env"

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    
    @classmethod
    async def connect_to_mongodb(cls):
        settings = MongoDBSettings()
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.MONGODB_DB_NAME]
        logger.info("Connected to MongoDB")

        collections = await cls.db.list_collection_names()
        logger.info(f"Collections: {collections}")
        if 'user' in collections:
            logger.info(f"Collection user' now exists.")
        else:
            logger.info(f"Error: Collection user was not created as expected.")

        collection = cls.db.users
        if collection is None:
            logger.info("Error: Collection object is None!")

        logger.info(f"MONGO SETTED UP")
        
    @classmethod
    async def close_mongodb_connection(cls):
        if cls.client:
            logger.info("Closing MongoDB connection")
            cls.client.close()
            logger.info("MongoDB connection closed")

# Convenience properties to access collections
    @property
    def conversations(self):
        return self.db.conversations

    @property
    def user(self):
        return self.db.user
        
    @property
    def messages(self):
        return self.db.messages
        
mongodb = MongoDB() 