#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test improved prompt with strict department filtering
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.rag_graph import process_kma_query
import asyncio

async def test_improved_prompt():
    print("🧪 Testing improved prompt with strict department filtering...")
    
    # Test query
    query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
    print(f"📝 Query: {query}")
    print()
    
    try:
        # Get response
        result = await process_kma_query(query)
        
        print("🤖 LLM Response:")
        print("-" * 60)
        print(result['answer'])
        print("-" * 60)
        print()
        
        # Check for contamination keywords
        response_lower = result['answer'].lower()
        contamination_keywords = [
            "văn thư", "lưu trữ", "pccc", "giấy giới thiệu", 
            "hành chính", "an ninh", "an toàn", "công đoàn",
            "đào tạo", "khảo thí", "chính trị"
        ]
        
        found_contamination = []
        for keyword in contamination_keywords:
            if keyword in response_lower:
                found_contamination.append(keyword)
        
        if found_contamination:
            print(f"⚠️  CONTAMINATION DETECTED: {', '.join(found_contamination)}")
            print("❌ Response still contains content from other departments")
        else:
            print("✅ No contamination detected - response focused on PHÒNG THIẾT BỊ only")
        
        print()
        print("📊 Response Analysis:")
        print(f"   Length: {len(result['answer'])} chars")
        print(f"   Sources: {len(result.get('sources', []))}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_improved_prompt())