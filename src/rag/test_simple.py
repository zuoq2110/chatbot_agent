#!/usr/bin/env python
"""
Simple test script for the RAG tool.

This script directly calls the RAG tool without mocking to test its functionality.
"""

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Import the tool directly
from tool import search_kma_regulations, create_rag_tool
from rag_graph import KMAChatAgent


async def test_search_regulations():
    """Test searching KMA regulations with a simple query."""
    print("\n===== Testing RAG Search =====")
    
    # Create the tool
    rag_tool = create_rag_tool()
    
    # Define test queries
    test_queries = [
        "Quy định về học cải thiện?",
        "Cách quy đổi điểm hệ 4 sang hệ chữ",
    ]
    
    # Test each query
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            response = await rag_tool.ainvoke(query)
            result = json.loads(response)
            
            print(f"Answer: {result['answer']}")
            print("Sources:")
            for i, source in enumerate(result['sources']):
                print(f"  Source {i+1}: {source[:100]}..." if len(source) > 100 else f"  Source {i+1}: {source}")
            
            print(f"Status: {result['message']}")
        except Exception as e:
            print(f"Error: {str(e)}")


async def run_tests():
    """Run all simple tests."""
    print("Starting simple RAG tool tests...")
    
    await test_search_regulations()
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(run_tests()) 