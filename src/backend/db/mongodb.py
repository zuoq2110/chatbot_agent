import logging
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor

from pymongo import MongoClient
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
    HF_TOKEN: str = ""
    class Config:
        env_file = ".env"

def run_in_threadpool(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            ThreadPoolExecutor(), 
            lambda: func(*args, **kwargs)
        )
    return wrapper

class MongoDB:
    client: MongoClient = None
    db = None
    
    @classmethod
    async def connect_to_mongodb(self):
        settings = MongoDBSettings()
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        logger.info("Connected to MongoDB")

        # Run in thread to avoid blocking
        @run_in_threadpool
        def check_collections():
            collections = self.db.list_collection_names()
            return collections
        
        collections = await check_collections()
        logger.info(f"Collections: {collections}")
        if 'user' in collections:
            logger.info(f"Collection 'user' now exists.")
        else:
            logger.info(f"Error: Collection user was not created as expected.")

        collection = self.db.user
        if collection is None:
            logger.info("Error: Collection object is None!")
        else:
            logger.info(f"Collection object: {collection}")

        logger.info(f"MONGO SETTED UP")

        # created_conversation = await mongodb.db.conversations.find_one({"_id": "abcd"})
        created_conversation =  mongodb.db.conversations.find_one({"_id": "abcd"})

        logger.info("Test")
        logger.info(created_conversation)
        
    @classmethod
    async def close_mongodb_connection(cls):
        if cls.client:
            logger.info("Closing MongoDB connection")
            cls.client.close()
            logger.info("MongoDB connection closed")

    # Helper method to execute database operations in a thread pool
    @classmethod
    async def execute(cls, collection_name, operation, *args, **kwargs):
        collection = cls.db[collection_name]
        method = getattr(collection, operation)
        
        @run_in_threadpool
        def run_operation():
            return method(*args, **kwargs)
        
        return await run_operation()

    # Convenience methods to perform common operations
    @classmethod
    async def find_one(cls, collection_name, query, *args, **kwargs):
        return await cls.execute(collection_name, "find_one", query, *args, **kwargs)
    
    @classmethod
    async def find(cls, collection_name, query, *args, **kwargs):
        @run_in_threadpool
        def run_find():
            return list(cls.db[collection_name].find(query, *args, **kwargs))
        
        return await run_find()
    
    @classmethod
    async def insert_one(cls, collection_name, document, *args, **kwargs):
        return await cls.execute(collection_name, "insert_one", document, *args, **kwargs)
    
    @classmethod
    async def insert_many(cls, collection_name, documents, *args, **kwargs):
        return await cls.execute(collection_name, "insert_many", documents, *args, **kwargs)
    
    @classmethod
    async def update_one(cls, collection_name, filter, update, *args, **kwargs):
        return await cls.execute(collection_name, "update_one", filter, update, *args, **kwargs)
    
    @classmethod
    async def delete_one(cls, collection_name, filter, *args, **kwargs):
        return await cls.execute(collection_name, "delete_one", filter, *args, **kwargs)

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