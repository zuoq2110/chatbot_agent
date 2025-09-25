#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test just the search_kma_regulations tool to debug retriever type
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_search_tool_only():
    """Test just the search_kma_regulations tool"""
    try:
        from rag.tool import search_kma_regulations
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Testing search_kma_regulations for: {query}")
        
        # Test 1: Direct tool call
        result = search_kma_regulations(query)
        print(f"✅ Result length: {len(result)}")
        print(f"📋 Contains 'Quân y': {'quân y' in result.lower()}")
        
        if "quân y" in result.lower():
            print(f"🎉 SUCCESS: Found 'Quân y' in result!")
        else:
            print(f"❌ FAILED: 'Quân y' not found in result")
            print(f"Result preview: {result[:500]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing search tool: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_search_tool_only()