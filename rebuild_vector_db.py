#!/usr/bin/env python3
"""
Script to rebuild vector database for the chatbot system
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.rag.rag_graph import EnhancedRAGGraph

def rebuild_vector_database():
    """Rebuild the vector database from scratch"""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting vector database rebuild...")
        
        # Initialize RAG system
        rag = EnhancedRAGGraph()
        
        # Rebuild vector database
        logger.info("Rebuilding vector database...")
        rag.build_vector_database()
        
        logger.info("Vector database rebuilt successfully!")
        
        # Test the system
        logger.info("Testing the system...")
        test_query = "thành viên hội đồng đảm bảo chất lượng giáo dục của học viện kỹ thuật mật mã gồm những ai"
        
        response = rag.chat(test_query)
        
        logger.info("Test query: " + test_query)
        logger.info("Response: " + response)
        
        # Check if response contains member information
        if "21 đồng chí" in response or "Hoàng Văn Thức" in response:
            logger.info("✅ Test passed - Response contains member information")
        else:
            logger.warning("⚠️  Test warning - Response may not contain complete member information")
            
    except Exception as e:
        logger.error(f"Error rebuilding vector database: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = rebuild_vector_database()
    if success:
        print("\n✅ Vector database rebuild completed successfully!")
    else:
        print("\n❌ Vector database rebuild failed!")
        sys.exit(1)