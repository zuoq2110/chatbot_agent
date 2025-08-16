import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class MongoDBSettings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ai_chat"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

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
        
        # Kiểm tra danh sách collections
        collections = await cls.db.list_collection_names()
        logger.info(f"Collections in DB: {collections}")
        
        if 'users' in collections:
            logger.info("Collection 'users' exists.")
        else:
            logger.warning("Collection 'users' not found. It will be created on first insert.")
    
    @classmethod
    async def close_mongodb_connection(cls):
        if cls.client:
            logger.info("Closing MongoDB connection")
            cls.client.close()
            logger.info("MongoDB connection closed")

    # Convenience properties
    @property
    def conversations(self):
        return self.db.conversations

    @property
    def users(self):
        return self.db.users
        
    @property
    def messages(self):
        return self.db.messages

mongodb = MongoDB()
