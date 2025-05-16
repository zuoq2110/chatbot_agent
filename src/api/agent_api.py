from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uvicorn
import logging
import time
from typing import Optional, Dict, Any
import os
import sys

# Add the parent directory to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our agent functionality
from agent.supervisor_agent import run_agent_no_human_loop

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the FastAPI app
app = FastAPI(
    title="KMA Agent API",
    description="API for interacting with the KMA Agent - no authentication, no chat history",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request model
class QueryRequest(BaseModel):
    query: str

# Define the response model
class QueryResponse(BaseModel):
    response: str
    processing_time_ms: Optional[float] = None

@app.get("/")
async def root():
    return {"message": "KMA Agent API is running. Use /query endpoint to interact with the agent."}

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        start_time = time.time()
        logger.info(f"Received query: {request.query}")
        
        # Run the agent with the query
        response_text = await run_agent_no_human_loop(request.query)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # convert to milliseconds
        logger.info(f"Query processed in {processing_time:.2f}ms")
        
        # Check if the response was the fallback
        if response_text == "I couldn't generate a response. Please try a different query.":
            logger.warning(f"Agent returned fallback response for query: {request.query}")
        
        # Return the response
        return {
            "response": response_text,
            "processing_time_ms": round(processing_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

def run_api():
    """Run the API server"""
    uvicorn.run("api.agent_api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    uvicorn.run("agent_api:app", host="0.0.0.0", port=8000, reload=True) 