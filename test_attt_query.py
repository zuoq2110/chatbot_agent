#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test ATTT query to check if RAG retrieves correct data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from rag.rag_graph import process_kma_query

async def test_attt_queries():
    print("🧪 Testing ATTT queries for correct data retrieval...")
    
    queries = [
        "KHỐI LƯỢNG KIẾN THỨC TOÀN KHÓA ngành an toàn thông tin",
        "ĐỐI TƯỢNG TUYỂN SINH ngành an toàn thông tin", 
        "THỜI GIAN ĐÀO TẠO ngành an toàn thông tin"
    ]
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        print("=" * 60)
        
        try:
            result = await process_kma_query(query)
            
            print("🤖 LLM Response:")
            print("-" * 40)
            print(result['answer'])
            print("-" * 40)
            
            print("\n📊 Sources used:")
            for i, source in enumerate(result.get('sources', [])[:3], 1):
                print(f"Source {i}: {source[:200]}...")
                
            # Check for specific keywords from the ATTT file
            response_lower = result['answer'].lower()
            
            if "135 tc" in response_lower or "135 tín chỉ" in response_lower:
                print("❌ WRONG DATA: Shows 135 TC instead of 165 TC")
            elif "165 tc" in response_lower or "165 tín chỉ" in response_lower:
                print("✅ CORRECT DATA: Shows 165 TC")
            else:
                print("⚠️  No clear TC information found")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_attt_queries())
