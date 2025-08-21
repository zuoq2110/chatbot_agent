"""
RAG (Retrieval Augmented Generation) tool for accessing all documents in KMA's knowledge base.

This tool allows querying information from all documents in the system, including KMA's regulations, 
rules, policies, and any other uploaded documents in the data directory.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from rag.rag_graph import KMAChatAgent


class KMARegulationInput(BaseModel):
    query: str = Field(description="The query to search for in all available documents")


# Initialize the KMAChatAgent as a singleton
_chat_agent = None


def get_chat_agent():
    """Get or create a singleton instance of KMAChatAgent"""
    global _chat_agent
    if _chat_agent is None:
        _chat_agent = KMAChatAgent()
    return _chat_agent


@tool("search_kma_regulations", args_schema=KMARegulationInput,
      description=("Search for information in all training documents including KMA's regulations, "
                   "rules, policies, and any other uploaded documents in the data directory. "
                   "Uses a LangGraph-based RAG system to retrieve and process information. "
                   "The query must be provided."))
async def search_kma_regulations(query: str) -> str:
    """
    Search for information in all training documents in the knowledge base.
    Uses a LangGraph-based RAG system to retrieve and process information.

    Args:
        query: The question or search query about any content in the knowledge base

    Returns:
        A JSON string containing the retrieved information and sources
    """
    try:
        # Get the KMAChatAgent instance
        agent = get_chat_agent()

        # Use the agent's chat method to process the query
        response = agent.chat(query)

        # Format response
        result = {"answer": response, "message": "KMA regulation information retrieved successfully"}

        return response

    except Exception as e:
        # return json.dumps({
        #     "answer": "",
        #     "message": f"Error searching KMA regulations: {str(e)}"
        # })

        return "Error searching KMA regulations"


def create_rag_tool():
    """Create a configured instance of the RAG tool."""
    # Initialize the agent so it's ready when needed
    get_chat_agent()
    return search_kma_regulations
