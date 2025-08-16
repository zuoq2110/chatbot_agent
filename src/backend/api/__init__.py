from fastapi import APIRouter
from .chat import router as chat_router
from .file import router as file_router
from .user import router as user_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(file_router, prefix="/chat", tags=["file"])
router.include_router(user_router, prefix="/users", tags=["users"])

__all__ = ["router"]