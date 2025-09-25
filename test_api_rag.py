#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test API RAG functionality directly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.tool import search_kma_regulations
import asyncio

def test_api_rag():
    print("🧪 Testing API RAG tool...")
    
    # Test query
    query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
    print(f"📝 Query: {query}")
    print()
    
    try:
        # Get response using the same tool that API uses
        response = search_kma_regulations(query)
        
        print("🤖 RAG Tool Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        print()
        
        # Check for contamination keywords
        response_lower = response.lower()
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
        print(f"   Length: {len(response)} chars")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_rag()