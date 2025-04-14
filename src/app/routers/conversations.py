from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from bson import ObjectId
import uuid
from datetime import datetime
from app.models.conversation import ConversationCreate, ConversationUpdate, ConversationInDB, ConversationResponse
from app.db import Database, model_to_dict

router = APIRouter()

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(conversation: ConversationCreate):
    try:
        # Create conversation document
        conversation_db = ConversationInDB(
            name=conversation.name,
            user_id=ObjectId(conversation.user_id)
        )
        conversation_dict = model_to_dict(conversation_db)
        conversation_id = await Database.insert_one("conversations", conversation_dict)
        
        # Return created conversation
        created_conversation = {**conversation_dict, "_id": conversation_id}
        return ConversationResponse(**created_conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating conversation: {str(e)}"
        )

@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: str = Query(..., description="ID of the user to get conversations for"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        conversations = await Database.find(
            "conversations", 
            {"user_id": ObjectId(user_id)},
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)]  # Sort by most recently updated
        )
        return [ConversationResponse(**conversation) for conversation in conversations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching conversations: {str(e)}"
        )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    try:
        conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return ConversationResponse(**conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID: {str(e)}"
        )

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(conversation_id: str, conversation_update: ConversationUpdate):
    try:
        # Check if conversation exists
        conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Update conversation
        update_data = {k: v for k, v in conversation_update.model_dump().items() if v is not None}
        if not update_data:
            # No valid fields to update
            return ConversationResponse(**conversation)
        
        success = await Database.update_one("conversations", {"_id": ObjectId(conversation_id)}, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update conversation"
            )
        
        # Get updated conversation
        updated_conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        return ConversationResponse(**updated_conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID or data: {str(e)}"
        )

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str):
    try:
        # Check if conversation exists
        conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Soft delete the conversation
        success = await Database.delete_one("conversations", {"_id": ObjectId(conversation_id)})
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID: {str(e)}"
        )

@router.post("/{conversation_id}/share", response_model=ConversationResponse)
async def share_conversation(conversation_id: str):
    try:
        # Check if conversation exists
        conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Generate a unique share token if not present
        share_token = conversation.get("share_token")
        if not share_token:
            share_token = str(uuid.uuid4())
        
        # Update the conversation with share info
        update_data = {
            "is_shared": True,
            "share_token": share_token
        }
        
        success = await Database.update_one("conversations", {"_id": ObjectId(conversation_id)}, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to share conversation"
            )
        
        # Get updated conversation
        updated_conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        return ConversationResponse(**updated_conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID: {str(e)}"
        )

@router.post("/{conversation_id}/unshare", response_model=ConversationResponse)
async def unshare_conversation(conversation_id: str):
    try:
        # Check if conversation exists
        conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Update the conversation to remove sharing
        update_data = {
            "is_shared": False,
            "share_token": None
        }
        
        success = await Database.update_one("conversations", {"_id": ObjectId(conversation_id)}, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unshare conversation"
            )
        
        # Get updated conversation
        updated_conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        return ConversationResponse(**updated_conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID: {str(e)}"
        )

@router.get("/shared/{share_token}", response_model=ConversationResponse)
async def get_shared_conversation(share_token: str):
    conversation = await Database.find_one("conversations", {
        "share_token": share_token,
        "is_shared": True
    })
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared conversation not found or no longer shared"
        )
    return ConversationResponse(**conversation) 