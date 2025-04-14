import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv
from app.utils.log_config import setup_logging

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    mongodb_url: str = os.getenv("MONGODB_URL", "")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "kma_chat")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
db = None

# Configure logging
setup_logging()
logger = logging.getLogger("kma_chat_api")
logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the MongoDB database
    global db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    # Set the db reference in the db module
    from app.db import _db as db_module_reference
    db_module_reference = db
    
    # Log application startup
    from app.utils.logger import logger
    logger.info("Application starting up", {
        "mongodb_db": settings.mongodb_db_name,
        "log_level": settings.log_level
    })
    
    yield
    
    # Log application shutdown
    logger.info("Application shutting down")
    
    # Close the connection when the app shuts down
    client.close()

# Initialize the FastAPI app
app = FastAPI(
    title="KMA Chat Agent API",
    description="API for the KMA Chat Agent",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
from app.middleware.logging_middleware import LoggingMiddleware
app.add_middleware(LoggingMiddleware)

# Import and include routers
from app.routers import users, conversations, messages, chat

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to KMA Chat Agent API"}

def run_backend():
    """Run the backend in production mode"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )

def run_backend_dev():
    """Run the backend in development mode"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )

def run_backend_prod():
    """Run the backend in production mode"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )

if __name__ == "__main__":
    run_backend_dev() 