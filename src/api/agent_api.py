import logging
import os
import sys
import time
from typing import Optional, Dict, Any, List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our agent functionality
from agent.supervisor_agent import ReActGraph

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

agent = ReActGraph()
agent.create_graph()
agent.print_mermaid()

# Define the FastAPI app
app = FastAPI(title="KMA Agent API",
    description="API for interacting with the KMA Agent - no authentication, no chat history", version="1.0.0", )

# Enable CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"],  # In production, you should specify the allowed origins
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"], )

class MessageHistory(BaseModel):
    content: str
    is_user: bool

    class Config:
        schema_extra = {
            "example": {
                "content": "Hello, how are you?",
                "is_user": True
            }
        }

# Define the request model
class QueryRequest(BaseModel):
    query: str

class ConversationRequest(BaseModel):
    query: str
    history: Optional[List[MessageHistory]] = None


# Define the response model
class QueryResponse(BaseModel):
    response: str
    processing_time_ms: Optional[float] = None


class BaseResponse(BaseModel):
    statusCode: int
    message: str
    data: Optional[Dict[str, Any]] = None



@app.get("/")
async def root():
    return {"message": "KMA Agent API is running. Use /query endpoint to interact with the agent."}


@app.post("/conversation", response_model=BaseResponse)
async def conversation_agent(request: ConversationRequest):
    try:
        start_time = time.time()
        logger.info(f"Received conversation query: {request.query}")

        # Convert DB messages to langchain message format
        conversation_history = []
        async for msg in request.history:
            if msg.is_user:
                conversation_history.append(HumanMessage(content=msg.content))
            else:
                conversation_history.append(AIMessage(content=msg.content))

        # Use the chat_with_memory method to get a response with context
        logger.info(f"Processing query with memory: {request.query}")

        response_text = await agent.chat_with_memory(conversation_history, request.query)

        logger.info(f"Response from conversation: {response_text}")

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # convert to milliseconds
        logger.info(f"Conversation processed in {processing_time:.2f}ms")

        content = response_text[-1].content
        # Check if the response was the fallback
        if content == "I couldn't generate a response. Please try a different query.":
            logger.warning(f"Agent returned fallback response for query: {request.query}")

            ## raise http 400 with data base response
            raise HTTPException(statusCode=400,
                                detail="Agent returned fallback response. Please try a different query.")

        # Return the response with base response
        return BaseResponse(statusCode=200, message="Query processed successfully",
                            data={"response": content, "processing_time_ms": processing_time})

    except Exception as e:
        logger.error(f"Error processing conversation: {str(e)}")
        raise HTTPException(statusCode=500, detail=f"Error processing conversation: {str(e)}")

@app.post("/query", response_model=BaseResponse)
async def query_agent(request: QueryRequest):
    try:
        start_time = time.time()
        logger.info(f"Received query: {request.query}")

        # Run the agent with the query
        response_text = await agent.chat(request.query)

        logger.info(f"Response from query: {response_text}")

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # convert to milliseconds
        logger.info(f"Query processed in {processing_time:.2f}ms")

        content = response_text[-1].content
        # Check if the response was the fallback
        if content == "I couldn't generate a response. Please try a different query.":
            logger.warning(f"Agent returned fallback response for query: {request.query}")

            ## raise http 400 with data base response
            raise HTTPException(statusCode=400,
                                detail="Agent returned fallback response. Please try a different query.")

        # Return the response with base response
        return BaseResponse(statusCode=200, message="Query processed successfully",
                            data={"response": content, "processing_time_ms": processing_time})

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(statusCode=500, detail=f"Error processing query: {str(e)}")

def run_api():
    """Run the API server"""
    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()
    port = os.environ.get("PORT")
    if port is None:
        port = 3434
    else:
        port = int(port)
    uvicorn.run("api.agent_api:app", host="0.0.0.0", port=3435, reload=True)


if __name__ == "__main__":
    run_api()
