"""
RAG (Retrieval Augmented Generation) tool for accessing KMA regulations.

This tool allows querying information about KMA's regulations, rules, and policies.
"""

import asyncio
from typing import Dict, List, Any, Optional
import json
from pydantic import BaseModel, Field

from langchain_core.tools import tool

from rag.graph import KMAChatAgent


class KMARegulationInput(BaseModel):
    query: str = Field(description="The query about KMA regulations to search for")


# Initialize the KMAChatAgent as a singleton
_chat_agent = None

def get_chat_agent():
    """Get or create a singleton instance of KMAChatAgent"""
    global _chat_agent
    if _chat_agent is None:
        _chat_agent = KMAChatAgent()
    return _chat_agent


@tool("search_kma_regulations", args_schema=KMARegulationInput, description=(
    "Search for information in KMA's regulations, rules, and policies. "
    "Uses a LangGraph-based RAG system to retrieve and process information. "
    "The query must be provided."
))
async def search_kma_regulations(query: str) -> str:
    """
    Search for information in KMA's regulations, rules, and policies.
    Uses a LangGraph-based RAG system to retrieve and process information.

    Args:
        query: The question or search query about KMA regulations

    Returns:
        A JSON string containing the retrieved information and sources
    """
    try:
        # Get the KMAChatAgent instance
        agent = get_chat_agent()
        
        # Use the agent's chat method to process the query
        response = agent.chat(query)
        #
        # # Get relevant sources from the retriever
        # retriever = agent.retriever
        # docs = retriever.get_relevant_documents(query)
        # sources = [doc.page_content for doc in docs[:3]]  # Top 3 sources
        
        # Format response
        result = {
            "answer": response,
            "message": "KMA regulation information retrieved successfully"
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "answer": "",
            "message": f"Error searching KMA regulations: {str(e)}"
        })


def create_rag_tool():
    """Create a configured instance of the RAG tool."""
    # Initialize the agent so it's ready when needed
    get_chat_agent()
    return search_kma_regulations