#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple solution: Turn off smart filtering by default and rely on context boosting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from rag.rag_graph import process_kma_query

async def test_simple_approach():
    print("🧪 Testing simplified approach (no smart filtering)...")
    
    queries = [
        "KHỐI LƯỢNG KIẾN THỨC TOÀN KHÓA ngành an toàn thông tin",
        "ĐỐI TƯỢNG TUYỂN SINH ngành an toàn thông tin", 
        "THỜI GIAN ĐÀO TẠO ngành an toàn thông tin",
        "nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"📝 Query {i}: {query}")
        print("=" * 80)
        
        try:
            result = await process_kma_query(query)
            
            print("🤖 Response:")
            print("-" * 50)
            print(result['answer'])
            print("-" * 50)
            
            # Quick validation
            response_lower = result['answer'].lower()
            if "165 tc" in response_lower or "165 tín chỉ" in response_lower:
                print("✅ Contains correct 165 TC")
            elif "135 tc" in response_lower or "135 tín chỉ" in response_lower:
                print("❌ Contains incorrect 135 TC")
                
            if "phòng thiết bị" in response_lower and "quân y" in response_lower:
                print("✅ Contains complete PHÒNG THIẾT BỊ info including Quân y")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_approach())