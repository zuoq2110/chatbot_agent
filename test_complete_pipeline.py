#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to debug the complete RAG pipeline
"""

import sys
import os
import asyncio

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_complete_pipeline():
    """Test the complete pipeline from RAG tool to final response"""
    try:
        from rag.tool import search_kma_regulations
        from rag.rag_graph import process_kma_query
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Testing complete pipeline with query: {query}")
        
        # Test 1: Direct RAG tool
        print("\n📋 Test 1: Using search_kma_regulations tool...")
        result1 = search_kma_regulations(query)
        print(f"Result length: {len(result1)}")
        print("Contains 'Quân y':", "quân y" in result1.lower())
        if "quân y" not in result1.lower():
            print("Result preview:", result1[:500] + "..." if len(result1) > 500 else result1)
        
        # Test 2: Direct process_kma_query
        print("\n📋 Test 2: Using process_kma_query function...")
        result2 = await process_kma_query(query)
        print(f"Answer length: {len(result2['answer'])}")
        print("Contains 'Quân y':", "quân y" in result2['answer'].lower())
        if "quân y" not in result2['answer'].lower():
            print("Answer preview:", result2['answer'][:500] + "..." if len(result2['answer']) > 500 else result2['answer'])
        
        # Test 3: Check sources
        print(f"\n📋 Test 3: Checking sources ({len(result2['sources'])} sources)...")
        for i, source in enumerate(result2['sources']):
            contains_quan_y = "quân y" in source.lower()
            print(f"Source {i+1} contains 'Quân y': {contains_quan_y}")
            if contains_quan_y:
                print(f"  Preview: {source[:200]}...")
        
        return result1, result2
        
    except Exception as e:
        print(f"❌ Error testing pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    asyncio.run(test_complete_pipeline())