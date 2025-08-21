import logging
import os
import sys
from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, status, Header, Depends
from langchain_core.messages import HumanMessage, AIMessage

# Add the parent directory to sys.path to import our agent
print(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent.supervisor_agent import ReActGraph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

agent = ReActGraph()
agent.create_graph()
agent.print_mermaid()

from ..db.mongodb import MongoDB, mongodb


from backend.models.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageResponse, QuickMessageResponse, MessageQuickChat
)
from backend.models.user import UserResponse
from backend.models.responses import BaseResponse
from backend.auth.dependencies import require_auth
from backend.api.rate_limit import check_rate_limit

router = APIRouter()

agent = ReActGraph()
agent.create_graph()
agent.print_mermaid()

# Helper function to check if ObjectId is valid
def validate_object_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {id}")
    return ObjectId(id)


# Helper function to estimate token count for rate limiting
def estimate_token_count(prompt_text: str, response_text: str) -> int:
    """
    Ước tính số token được sử dụng trong một cuộc hội thoại
    
    Args:
        prompt_text: Nội dung tin nhắn của người dùng
        response_text: Nội dung phản hồi của AI
        
    Returns:
        Ước tính tổng số token
    """
    # Một cách ước tính đơn giản: ~4 ký tự = 1 token (thực tế phụ thuộc vào tokenizer)
    prompt_tokens = len(prompt_text) // 4
    response_tokens = len(response_text) // 4
    
    # Thêm một overhead cho các token đặc biệt và context
    overhead = 100
    
    return prompt_tokens + response_tokens + overhead


@router.get("/conversations/all", response_model=BaseResponse[List[ConversationResponse]])
async def get_all_conversations(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user = Depends(require_auth)
):
    cursor = mongodb.db.conversations.find(
        {}
    ).sort("updated_at", -1).skip(skip).limit(limit)

    conversations = []
    async for conv in cursor:
        # Count messages for this conversation
        response_data = ConversationResponse(
            _id=str(conv["_id"]),
            user_id=str(conv["user_id"]),
            title=conv["title"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
        )
        conversations.append(response_data)

    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Conversations retrieved successfully",
        data=conversations
    )

@router.get("/conversations", response_model=BaseResponse[List[ConversationResponse]])
async def get_conversations_of_user(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(require_auth)
):
    """Get all conversations for a user"""
    # Kiểm tra nếu current_user là dict hoặc UserResponse
    if isinstance(current_user, dict):
        user_id = current_user.get("_id") or current_user.get("user_id")
    else:
        user_id = current_user._id
        
    user_id_obj = validate_object_id(user_id)

    conversations = []

    if user_id_obj is None:
        return BaseResponse(
            statusCode=status.HTTP_200_OK,
            message="Conversations retrieved successfully",
            data=conversations
        )
    
    cursor = mongodb.db.conversations.find(
        {"user_id": user_id_obj}
    ).sort("updated_at", -1).skip(skip).limit(limit)

    async for conv in cursor:
        # Count messages for this conversation
        response_data = ConversationResponse(
            _id = str(conv["_id"]),
            user_id = str(conv["user_id"]),
            title = conv["title"],
            created_at = conv["created_at"],
            updated_at = conv["updated_at"],
        )
        conversations.append(response_data)
    
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Conversations retrieved successfully",
        data=conversations
    )

@router.post("/conversations", response_model=BaseResponse[ConversationResponse])
async def create_conversation(
    conversation: ConversationCreate,
    current_user = Depends(require_auth)
):
    logger.info(f"Creating conversation: {conversation.title}")
    """Create a new conversation"""
    user_id_obj = validate_object_id(conversation.user_id)
    
    now = datetime.utcnow()
    new_conversation = {
        "user_id": user_id_obj,
        "title": conversation.title,
        "created_at": now,
        "updated_at": now
    }

    collection = mongodb.db.conversations
    if collection is None:
        logger.info("Error: Collection object is None!")
    else:
        logger.info(f"Collection object: {collection}")

    result = await mongodb.db.conversations.insert_one(new_conversation)
    logger.info("conv id: ", result)

    conversation_id = result.inserted_id
    
    created_conversation = await mongodb.db.conversations.find_one({"_id": conversation_id})

    logger.info("Created conv")
    logger.info(created_conversation)

    response_data = ConversationResponse(
        _id=str(created_conversation["_id"]),
        user_id=str(created_conversation["user_id"]),
        title= created_conversation["title"],
        created_at = created_conversation["created_at"],
        updated_at = created_conversation["updated_at"],
    )
    
    return BaseResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Conversation created successfully",
        data=response_data
    )

@router.put("/conversations/{conversation_id}", response_model=BaseResponse[ConversationResponse])
async def update_conversation(
    conversation_id: str,
    conversation: ConversationUpdate,
    current_user = Depends(require_auth)
):
    """Update a conversation's title"""
    conv_id = validate_object_id(conversation_id)

    result = await mongodb.db.conversations.update_one(
        {"_id": conv_id},
        {"$set": {"title": conversation.title, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    updated_conversation = await mongodb.db.conversations.find_one({"_id": conv_id})

    response_data = ConversationResponse(
        _id=str(updated_conversation["_id"]),
        user_id=str(updated_conversation["user_id"]),
        title=updated_conversation["title"],
        created_at=updated_conversation["created_at"],
        updated_at=updated_conversation["updated_at"],
    )
    
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Conversation updated successfully",
        data=response_data
    )

@router.delete("/conversations/{conversation_id}", response_model=BaseResponse)
async def delete_conversation(
    conversation_id: str,
    current_user = Depends(require_auth)
):
    """Delete a conversation and all its messages"""
    conv_id = validate_object_id(conversation_id)

    # First check if conversation exists
    conversation = await mongodb.db.conversations.find_one(
        {"_id": conv_id}
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete all messages in the conversation
    await mongodb.db.messages.delete_many({"conversation_id": conv_id})
    
    # Delete the conversation
    await mongodb.db.conversations.delete_one({"_id": conv_id})
    
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Conversation deleted successfully",
        data=None
    )

@router.get("/messages/{conversation_id}", response_model=BaseResponse[List[MessageResponse]])
async def get_messages_of_conversation(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get messages for a specific conversation"""
    conv_id = validate_object_id(conversation_id)

    # Check if conversation exists and belongs to the user
    conversation = await mongodb.db.conversations.find_one(
        {"_id": conv_id}
    )

    print("Conv:")
    print(conversation)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    cursor = mongodb.db.messages.find(
        {"conversation_id": conv_id}
    ).sort("created_at", 1).skip(skip).limit(limit)
    
    messages = []
    async for msg in cursor:
        response_msg = MessageResponse(
            _id = str(msg["_id"]),
            content = msg["content"],
            is_user = msg["is_user"],
            created_at = msg["created_at"],
        )
        messages.append(response_msg)

    print("all messages")
    print(messages)
    
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Messages retrieved successfully",
        data=messages
    )

@router.post("/{conversation_id}/messages", response_model=BaseResponse[MessageResponse])
async def query_ai(
    conversation_id: str,
    message: MessageCreate,
    student_code: str = Header(None),
    current_user = Depends(require_auth)
):
    """Add a new message to a conversation and get AI response using memory-aware chat"""
    conv_id = validate_object_id(conversation_id)

    # Check if conversation exists and belongs to the user
    conversation = await mongodb.db.conversations.find_one(
        {"_id": conv_id}
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Lấy user_id của người dùng hiện tại để kiểm tra rate limit
    user_id = str(current_user.get("_id"))
    if not user_id:
        logger.error("User ID not found in current_user object")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID not found")
    
    # Kiểm tra rate limit trước khi xử lý tin nhắn - không tính request ở đây
    # vì mỗi cặp câu hỏi và câu trả lời chỉ tính là 1 request
    allowed, error_message = await check_rate_limit(user_id, 0, count_as_request=False)  
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_message)
    
    now = datetime.utcnow()

    if student_code:
        logger.info(f"Student code: {student_code}")
        content = f"My student code is {student_code}" + message.content
    else:
        content = message.content

    # Create the user message
    new_message = {
        "conversation_id": conv_id,
        "content": content,
        "is_user": message.is_user,
        "created_at": now
    }

    await mongodb.db.messages.insert_one(new_message)

    # Update the conversation's updated_at timestamp
    await mongodb.db.conversations.update_one(
        {"_id": conv_id},
        {"$set": {"updated_at": now}}
    )

    # Get all previous messages from this conversation
    cursor = mongodb.db.messages.find(
        {"conversation_id": conv_id}
    ).sort("created_at", 1)
    
    # Convert DB messages to langchain message format
    conversation_history = []
    async for msg in cursor:
        if msg["is_user"]:
            conversation_history.append(HumanMessage(content=msg["content"]))
        else:
            conversation_history.append(AIMessage(content=msg["content"]))

    # Use the chat_with_memory method to get a response with context
    logger.info(f"Processing query with memory: {content}")
    updated_history = await agent.chat_with_memory(conversation_history[:-1], content)
    
    # The last message in the updated history is the AI's response
    ai_response = updated_history[-1].content
    logger.info(f"Agent response: {ai_response}")

    now = datetime.utcnow()

    # Create the bot message in the database
    new_ai_message = {
        "conversation_id": conv_id,
        "content": ai_response,
        "is_user": False,
        "created_at": now
    }

    result = await mongodb.db.messages.insert_one(new_ai_message)

    # Update the conversation's updated_at timestamp
    await mongodb.db.conversations.update_one(
        {"_id": conv_id},
        {"$set": {"updated_at": now}}
    )

    created_message = await mongodb.db.messages.find_one({"_id": result.inserted_id})

    response_data = MessageResponse(
        _id=str(created_message["_id"]),
        content=created_message["content"],
        is_user=created_message["is_user"],
        created_at=created_message["created_at"],
    )
    
    # Tính toán số token đã sử dụng và cập nhật rate limit
    estimated_tokens = estimate_token_count(content, ai_response)
    logger.info(f"Estimated token usage: {estimated_tokens}")
    logger.info(f"Updating rate limit for user ID: {user_id}")
    
    # Tính là một request khi hoàn thành cả cặp câu hỏi-trả lời
    token_result, token_error = await check_rate_limit(user_id, estimated_tokens, count_as_request=True)
    if not token_result:
        logger.warning(f"Token limit reached but continuing as request already processed: {token_error}")
    
    logger.info(f"Rate limit updated successfully")

    return BaseResponse(
        statusCode=status.HTTP_201_CREATED,
        message="Message created successfully",
        data=response_data
    )


@router.post("/quick-messages", response_model=BaseResponse[QuickMessageResponse])
async def quick_chat(
    message: MessageQuickChat,
    student_code: str = Header(None),
    current_user = Depends(require_auth)
):
    """Get a quick response without saving conversation history"""
    
    # Lấy user_id của người dùng hiện tại để kiểm tra rate limit
    user_id = str(current_user.get("_id"))
    if not user_id:
        logger.error("User ID not found in current_user object")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User ID not found")
    
    # Kiểm tra rate limit trước khi xử lý tin nhắn - không tính request ở đây
    # vì mỗi cặp câu hỏi và câu trả lời chỉ tính là 1 request
    allowed, error_message = await check_rate_limit(user_id, 0, count_as_request=False)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_message)
    
    # Create a single message for this quick chat
    conversation_history = [HumanMessage(content=message.content)]
    
    # Use the chat_with_memory method consistently with other endpoint
    logger.info(f"Processing quick query: {message.content}")
    logger.info(f"Student code: {student_code}")

    if student_code:
        logger.info(f"Student code: {student_code}")
        content = f"My student code is {student_code}" + message.content
    else:
        content = message.content

    response = await agent.chat_with_memory([], content)
    
    # The last message in the response is the AI's answer
    ai_response = response[-1].content
    logger.info(f"Agent quick response: {ai_response}")
    
    now = datetime.utcnow()
    
    response_data = QuickMessageResponse(
        content=ai_response,
        created_at=now,
    )
    
    # Tính toán số token đã sử dụng và cập nhật rate limit
    estimated_tokens = estimate_token_count(content, ai_response)
    logger.info(f"Estimated token usage: {estimated_tokens}")
    logger.info(f"Updating rate limit for user ID: {user_id}")
    
    # Tính là một request khi hoàn thành cả cặp câu hỏi-trả lời
    token_result, token_error = await check_rate_limit(user_id, estimated_tokens, count_as_request=True)
    if not token_result:
        logger.warning(f"Token limit reached but continuing as request already processed: {token_error}")
    
    logger.info(f"Rate limit updated successfully")
    
    return BaseResponse(
        statusCode=status.HTTP_200_OK,
        message="Quick chat response generated successfully",
        data=response_data
    )
