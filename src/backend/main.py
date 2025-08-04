import logging
import os

import typer
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .db.mongodb import MongoDB, mongodb
# from db.mongodb import MongoDB, mongodb
from .models.responses import BaseResponse
from .api.chat import router as chat_router
from .api.user import router as user_router
# from models.responses import BaseResponse
# from api.chat import router as chat_router
# from api.user import router as user_router

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI backend
app = FastAPI(
    title="AI Chat API",
    description="API for managing AI chat conversations",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(user_router, prefix="/api", tags=["user"])

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            statusCode=exc.status_code,
            message=exc.detail,
            data=None
        ).model_dump(),
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=BaseResponse(
            statusCode=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            data=None
        ).model_dump(),
    )

@app.on_event("startup")
async def startup_db_client():
    await mongodb.connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_db_client():
    await mongodb.close_mongodb_connection()

@app.get("/", response_model=BaseResponse)
async def root():
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="AI Chat API is running",
        data=None
    )

@app.get("/health", response_model=BaseResponse)
async def health_check():
    """Health check endpoint for monitoring backend status"""
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Backend is healthy",
        data={
            "status": "online",
            "timestamp": "2025-08-03",
            "version": "1.0.0"
        }
    )

def run_backend(port: int = 8000, host: str = "0.0.0.0", reload: bool = True):
    """
    Run the FastAPI backend with the specified configuration.
    
    Args:
        port: The port to run the server on
        host: The host address to bind to
        reload: Whether to reload the server on code changes
    """
    logger.info(f"Starting KMA Chat Agent backend on {host}:{port}")
    uvicorn.run("src.backend.main:app", host=host, port=port, reload=reload)

# Command line interface using Typer
cli = typer.Typer()

@cli.command()
def start(port: int = 8000, host: str = "0.0.0.0", reload: bool = True):
    """Run the KMA Chat Agent backend"""
    port = os.environ.get("PORT")
    if port is None:
        port = 3434
    else:
        port = int(port)

    run_backend(port=port, host=host, reload=reload)

if __name__ == "__main__":
    cli() 