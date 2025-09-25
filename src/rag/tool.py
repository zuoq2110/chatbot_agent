"""
RAG (Retrieval Augmented Generation) tool for accessing all documents in KMA's knowledge base.

This tool allows querying information from all documents in the system, including KMA's regulations, 
rules, policies, and any other uploaded documents in the data directory.
"""

import asyncio
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from rag.rag_graph import process_kma_query_sync


class KMARegulationInput(BaseModel):
    query: str = Field(description="The query to search for in all available documents")


@tool("search_kma_regulations", args_schema=KMARegulationInput,
      description=("Search for information in all training documents including KMA's regulations, "
                   "rules, policies, and any other uploaded documents in the data directory. "
                   "Uses enhanced RAG system with smart retrieval and context boosting. "
                   "The query must be provided."))
def search_kma_regulations(query: str) -> str:
    """
    Search for information in all training documents in the knowledge base.
    Uses enhanced RAG system with smart retrieval, sliding window and context boosting.

    Args:
        query: The question or search query about any content in the knowledge base

    Returns:
        A string containing the retrieved information
    """
    try:
        # Use the improved process_kma_query_sync function
        result = process_kma_query_sync(query)
        return result['answer']

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in search_kma_regulations: {error_details}")
        return f"Error searching KMA regulations: {str(e)}"


def create_rag_tool():
    """Create a configured instance of the RAG tool."""
    return search_kma_regulations
