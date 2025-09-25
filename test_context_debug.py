#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to debug what context is being sent to LLM
"""

import sys
import os
import asyncio

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_context_content():
    """Test what context is actually being sent to the LLM"""
    try:
        from rag.rag_graph import get_retriever
        from rag.retriever import smart_retrieve, MetadataEnhancedHybridRetriever
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Testing context content for query: {query}")
        
        # Get retriever
        retriever = get_retriever()
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            docs = smart_retrieve(retriever, query, use_smart_filtering=True)
        else:
            docs = retriever.get_relevant_documents(query)
        
        print(f"📋 Retrieved {len(docs)} documents")
        
        # Check each document for Quân y
        quan_y_found = False
        for i, doc in enumerate(docs):
            content_lower = doc.page_content.lower()
            if "quân y" in content_lower:
                print(f"\n✅ Document {i+1} contains 'Quân y':")
                # Show a snippet around "quân y"
                quan_y_pos = content_lower.find("quân y")
                start = max(0, quan_y_pos - 100)
                end = min(len(doc.page_content), quan_y_pos + 100)
                snippet = doc.page_content[start:end]
                print(f"   Snippet: ...{snippet}...")
                quan_y_found = True
        
        if not quan_y_found:
            print("❌ No document contains 'Quân y'")
        
        # Combine content like in the actual system
        combined_content = "\n\n".join([doc.page_content for doc in docs])
        
        print(f"\n📋 Combined context length: {len(combined_content)} characters")
        print(f"📋 Combined context contains 'Quân y': {'quân y' in combined_content.lower()}")
        
        # Show first 1000 chars of combined content
        print(f"\n📋 First 1000 characters of combined context:")
        print(combined_content[:1000] + "..." if len(combined_content) > 1000 else combined_content)
        
        # Check if it has all 3 sections
        sections = ["văn bản quy định", "đảm bảo cơ sở vật chất", "quân y"]
        for section in sections:
            found = section in combined_content.lower()
            print(f"📋 Contains '{section}': {found}")
        
        return combined_content
        
    except Exception as e:
        print(f"❌ Error testing context: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_context_content()