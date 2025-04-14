from typing import Dict, Any, Optional
import asyncio
import sys
import os
import traceback
from datetime import datetime
from app.models.message import MessageCreate, MessageInDB
from app.db import Database, model_to_dict

# Import agent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agent.agent import initialize_rag

# Global conversation instance
_conversation = None

async def get_conversation():
    """Get or initialize the conversation instance"""
    global _conversation
    if _conversation is None:
        # Initialize in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        _conversation = await loop.run_in_executor(None, initialize_rag)
    return _conversation

async def send_query_to_agent(query: str) -> str:
    """Send a query to the agent and get a response"""
    try:
        conversation = await get_conversation()
        # Call the agent in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: conversation({"question": query})
        )
        return response.get('answer', 'I apologize, but I could not process your query.')
    except Exception as e:
        print(f"Error in chatbot agent: {e}")
        traceback.print_exc()
        return "I apologize, but I encountered an error while processing your query."

async def process_chat_request(conversation_id: str, user_id: str, query: str, 
                               attachments: list = None) -> Dict[str, Any]:
    """Process a chat request and store messages in the database"""
    try:
        # Save user message
        user_message = MessageCreate(
            conversation_id=conversation_id,
            user_id=user_id,
            content=query,
            role="human",
            has_attachment=bool(attachments),
            attachments=attachments or []
        )
        user_message_dict = model_to_dict(MessageInDB(**user_message.model_dump()))
        user_message_id = await Database.insert_one("messages", user_message_dict)
        
        # Get response from agent
        response_text = await send_query_to_agent(query)
        
        # Save bot response
        bot_message = MessageCreate(
            conversation_id=conversation_id,
            user_id=user_id,  # Using the same user_id to associate the response 
            content=response_text,
            role="bot",
            has_attachment=False
        )
        bot_message_dict = model_to_dict(MessageInDB(**bot_message.model_dump()))
        bot_message_id = await Database.insert_one("messages", bot_message_dict)
        
        # Update conversation's updated_at timestamp
        await Database.update_one(
            "conversations", 
            {"_id": Database.get_object_id(conversation_id)},
            {"updated_at": datetime.utcnow()}
        )
        
        # Return both messages
        return {
            "user_message": {**user_message_dict, "_id": user_message_id},
            "bot_message": {**bot_message_dict, "_id": bot_message_id}
        }
    except Exception as e:
        print(f"Error processing chat request: {e}")
        traceback.print_exc()
        raise 