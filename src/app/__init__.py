"""
KMA Chat Agent API - FastAPI backend for the KMA Chat Agent system.

This package implements the REST API endpoints for chat functionality, user management,
and integration with the agent system.
"""

from fastapi import FastAPI
from app.routers import chat_router, user_router
from app.middleware import LoggingMiddleware

__all__ = ["create_app"]


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="KMA Chat Agent API",
        description="API for the KMA Chat Agent system",
        version="0.1.0"
    )
    
    # Add middleware
    app.add_middleware(LoggingMiddleware)
    
    # Register routers
    app.include_router(chat_router)
    app.include_router(user_router)
    
    return app 