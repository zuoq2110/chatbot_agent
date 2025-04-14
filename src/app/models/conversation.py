from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId

class ConversationBase(BaseModel):
    name: str = Field(..., description="Conversation name")
    user_id: PyObjectId = Field(..., description="User ID who owns this conversation")
    is_active: bool = Field(default=True, description="Whether the conversation is active")
    is_shared: bool = Field(default=False, description="Whether the conversation is shared with others")
    share_token: Optional[str] = Field(default=None, description="Token for sharing the conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

class ConversationCreate(BaseModel):
    name: str
    user_id: str

class ConversationUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    is_shared: Optional[bool] = None
    share_token: Optional[str] = None

class ConversationInDB(ConversationBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True
    }

class ConversationResponse(BaseModel):
    id: str
    name: str
    user_id: str
    is_active: bool
    is_shared: bool
    share_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "populate_by_name": True
    } 