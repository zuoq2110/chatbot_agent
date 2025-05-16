import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv
from app.utils.log_config import setup_logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from src.agent import create_supervisor_agent
from src.agent.state import MyAgentState

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
    
    # Initialize agent
    supervisor_agent = create_supervisor_agent(model_name="gpt-3.5-turbo")
    
    # Store active conversations
    conversations: Dict[str, MyAgentState] = {}
    
    yield
    
    # Log application shutdown
    logger.info("Application shutting down")
    
    # Close the connection when the app shuts down
    client.close()

# Initialize the FastAPI app
app = FastAPI(
    title="KMA Chat Agent API",
    description="API for KMA's Student Assistant Agent",
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

# Initialize agent
supervisor_agent = create_supervisor_agent(model_name="gpt-3.5-turbo")

# Store active conversations
conversations: Dict[str, MyAgentState] = {}

class MessageRequest(BaseModel):
    """Request model for sending a message"""
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    message: str = Field(..., description="Message from the user")

class MessageResponse(BaseModel):
    """Response model for messages"""
    conversation_id: str = Field(..., description="Unique identifier for the conversation")
    messages: List[Dict[str, Any]] = Field(..., description="List of messages in the conversation")
    awaiting_human_input: bool = Field(False, description="Whether the agent is waiting for human input")
    human_input_prompt: Optional[str] = Field(None, description="Prompt for human input if awaiting_human_input is True")
    

@app.post("/api/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Send a message to the agent"""
    conversation_id = request.conversation_id
    message = request.message
    
    # Get or create conversation state
    if conversation_id not in conversations:
        conversations[conversation_id] = MyAgentState()
    
    state = conversations[conversation_id]
    
    # Check if we were waiting for human input
    if state.awaiting_human_input:
        # Process human input through the handle_human_input node
        human_message = HumanMessage(content=message)
        state.add_message(human_message)
        state.set_human_input_received()
    else:
        # Add user message
        state.add_message(HumanMessage(content=message))
    
    # Invoke agent
    result = supervisor_agent.invoke(state)
    
    # Update conversation state
    conversations[conversation_id] = result
    
    # Convert messages to serializable format
    serialized_messages = []
    for msg in result.messages:
        if isinstance(msg, HumanMessage):
            serialized_messages.append({
                "role": "human",
                "content": msg.content
            })
        elif isinstance(msg, AIMessage):
            serialized_messages.append({
                "role": "ai",
                "content": msg.content
            })
        elif isinstance(msg, ToolMessage):
            serialized_messages.append({
                "role": "tool",
                "name": msg.name,
                "content": msg.content
            })
    
    return MessageResponse(
        conversation_id=conversation_id,
        messages=serialized_messages,
        awaiting_human_input=result.awaiting_human_input,
        human_input_prompt=result.human_input_prompt
    )

@app.get("/api/conversations/{conversation_id}", response_model=MessageResponse)
async def get_conversation(conversation_id: str):
    """Get a conversation by ID"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    state = conversations[conversation_id]
    
    # Convert messages to serializable format
    serialized_messages = []
    for msg in state.messages:
        if isinstance(msg, HumanMessage):
            serialized_messages.append({
                "role": "human",
                "content": msg.content
            })
        elif isinstance(msg, AIMessage):
            serialized_messages.append({
                "role": "ai",
                "content": msg.content
            })
        elif isinstance(msg, ToolMessage):
            serialized_messages.append({
                "role": "tool",
                "name": msg.name,
                "content": msg.content
            })
    
    return MessageResponse(
        conversation_id=conversation_id,
        messages=serialized_messages,
        awaiting_human_input=state.awaiting_human_input,
        human_input_prompt=state.human_input_prompt
    )

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation by ID"""
    if conversation_id in conversations:
        del conversations[conversation_id]
    
    return {"message": "Conversation deleted successfully"}

# Add a simple health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

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