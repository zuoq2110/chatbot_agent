#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to debug which retriever is being used in the system
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_retriever_loading():
    """Test which retriever is actually being loaded"""
    try:
        from rag.rag_graph import get_retriever
        from rag.retriever import MetadataEnhancedHybridRetriever
        
        print("📋 Testing retriever loading...")
        
        # Get the retriever
        retriever = get_retriever()
        
        print(f"✅ Retriever loaded successfully")
        print(f"📝 Retriever type: {type(retriever).__name__}")
        print(f"📝 Is enhanced retriever: {isinstance(retriever, MetadataEnhancedHybridRetriever)}")
        
        if hasattr(retriever, 'window_size'):
            print(f"📝 Window size: {retriever.window_size}")
        
        if hasattr(retriever, 'all_documents') and retriever.all_documents:
            print(f"📝 Total documents: {len(retriever.all_documents)}")
        
        # Test the PHÒNG THIẾT BỊ query
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"\n🔍 Testing query: {query}")
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            from rag.retriever import smart_retrieve
            docs = smart_retrieve(retriever, query, use_smart_filtering=True)
            print(f"📋 Using smart_retrieve - found {len(docs)} documents")
        else:
            docs = retriever.get_relevant_documents(query)
            print(f"📋 Using regular retrieve - found {len(docs)} documents")
        
        # Check if we have the Quân y section
        found_quan_y = False
        for i, doc in enumerate(docs[:10]):  # Check top 10
            content_lower = doc.page_content.lower()
            if "quân y" in content_lower:
                print(f"✅ Found 'Quân y' in document {i+1}")
                found_quan_y = True
                break
        
        if not found_quan_y:
            print("❌ 'Quân y' section not found in top 10 results")
        
        return retriever
        
    except Exception as e:
        print(f"❌ Error testing retriever: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_retriever_loading()