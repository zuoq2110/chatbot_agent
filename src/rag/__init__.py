"""
KMA Regulations Assistant - A chatbot for answering questions about 
regulations at the Academy of Cryptographic Techniques (KMA).
"""

# Fix OpenMP library conflict - MUST BE AT THE TOP
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from .tool import create_rag_tool, search_kma_regulations
from .rag_graph import process_kma_query, process_kma_query_sync, get_retriever

__version__ = "0.1.0"
__all__ = ["create_rag_tool", "search_kma_regulations", "process_kma_query", "process_kma_query_sync", "get_retriever"]
