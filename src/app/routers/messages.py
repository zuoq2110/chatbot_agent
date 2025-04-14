from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List
from bson import ObjectId
from app.models.message import MessageCreate, MessageUpdate, MessageInDB, MessageResponse
from app.db import Database, model_to_dict

router = APIRouter()

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(message: MessageCreate):
    try:
        # Validate that conversation exists
        conversation = await Database.find_one(
            "conversations", 
            {"_id": ObjectId(message.conversation_id)}
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Create message document
        message_db = MessageInDB(
            conversation_id=ObjectId(message.conversation_id),
            user_id=ObjectId(message.user_id),
            content=message.content,
            role=message.role,
            has_attachment=message.has_attachment,
            attachments=message.attachments
        )
        message_dict = model_to_dict(message_db)
        message_id = await Database.insert_one("messages", message_dict)
        
        # Update conversation's updated_at field
        await Database.update_one(
            "conversations", 
            {"_id": ObjectId(message.conversation_id)},
            {"updated_at": message_db.created_at}
        )
        
        # Return created message
        created_message = {**message_dict, "_id": message_id}
        return MessageResponse(**created_message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating message: {str(e)}"
        )

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str):
    try:
        message = await Database.find_one("messages", {"_id": ObjectId(message_id)})
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        return MessageResponse(**message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid message ID: {str(e)}"
        )

@router.get("/conversation/{conversation_id}", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str = Path(..., description="ID of the conversation to get messages for"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    try:
        # Check if conversation exists or is shared
        conversation = await Database.find_one("conversations", {"_id": ObjectId(conversation_id)})
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages for the conversation, sorted by creation time
        messages = await Database.find(
            "messages", 
            {"conversation_id": ObjectId(conversation_id)},
            skip=skip,
            limit=limit,
            sort=[("created_at", 1)]  # Sort by creation time, oldest first
        )
        return [MessageResponse(**message) for message in messages]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid conversation ID: {str(e)}"
        )

@router.get("/shared/{share_token}", response_model=List[MessageResponse])
async def get_shared_conversation_messages(
    share_token: str = Path(..., description="Share token of the conversation"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    # Find the shared conversation
    conversation = await Database.find_one("conversations", {
        "share_token": share_token,
        "is_shared": True
    })
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared conversation not found or not accessible"
        )
    
    # Get messages for the conversation
    try:
        messages = await Database.find(
            "messages", 
            {"conversation_id": conversation["_id"]},
            skip=skip,
            limit=limit,
            sort=[("created_at", 1)]
        )
        return [MessageResponse(**message) for message in messages]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching messages: {str(e)}"
        )

@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(message_id: str, message_update: MessageUpdate):
    try:
        # Check if message exists
        message = await Database.find_one("messages", {"_id": ObjectId(message_id)})
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Update message
        update_data = {k: v for k, v in message_update.model_dump().items() if v is not None}
        if not update_data:
            # No valid fields to update
            return MessageResponse(**message)
        
        success = await Database.update_one("messages", {"_id": ObjectId(message_id)}, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update message"
            )
        
        # Get updated message
        updated_message = await Database.find_one("messages", {"_id": ObjectId(message_id)})
        return MessageResponse(**updated_message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid message ID or data: {str(e)}"
        )

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: str):
    try:
        # Check if message exists
        message = await Database.find_one("messages", {"_id": ObjectId(message_id)})
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Soft delete the message
        success = await Database.delete_one("messages", {"_id": ObjectId(message_id)})
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete message"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid message ID: {str(e)}"
        ) 