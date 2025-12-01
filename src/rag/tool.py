"""
RAG (Retrieval Augmented Generation) tool for accessing all documents in KMA's knowledge base.

This tool allows querying information from all documents in the system, including KMA's regulations, 
rules, policies, and any other uploaded documents in the data directory.
"""

import asyncio
from typing import Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from rag.rag_graph import process_kma_query_sync

class KMARegulationInput(BaseModel):
    query: str = Field(description="The query to search for in all available documents")
    department: Optional[str] = Field(default=None, description="User's department for filtering (phongdaotao/phongkhaothi/chung)")


@tool("search_kma_regulations", args_schema=KMARegulationInput,
      description=("Search for information in all training documents including KMA's regulations, "
                   "rules, policies, and any other uploaded documents in the data directory. "
                   "Uses enhanced RAG system with smart retrieval and context boosting. "
                   "The query must be provided."))
def search_kma_regulations(query: str, department: str = None) -> str:
    """
    Search for information in all training documents in the knowledge base.
    Uses enhanced RAG system with smart retrieval, sliding window and context boosting.

    Args:
        query: The question or search query about any content in the knowledge base
        department: User's department for content filtering (phongdaotao/phongkhaothi/chung)

    Returns:
        A string containing the retrieved information
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔍 search_kma_regulations called with query: {query[:100]}...")
        logger.info(f"📁 Department filter: {department}")
        
        # Use the improved process_kma_query_sync function with department filter
        result = process_kma_query_sync(query, department_filter=department)
        
        answer = result.get('answer', '')
        logger.info(f"✅ RAG query completed, answer length: {len(answer)}")
        logger.info(f"📝 Answer preview: {answer[:200]}...")
        
        if not answer or len(answer.strip()) == 0:
            logger.error("❌ Empty answer returned from RAG!")
            return "Xin lỗi, tôi không tìm thấy thông tin phù hợp với câu hỏi của bạn."
        
        return answer

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"❌ Error in search_kma_regulations: {error_details}")
        return f"Xin lỗi, đã xảy ra lỗi khi tìm kiếm thông tin: {str(e)}"


def create_rag_tool():
    """Create a configured instance of the RAG tool."""
    return search_kma_regulations
