#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to check the exact position and content of Quân y section
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_quan_y_position():
    """Test where exactly Quân y section appears in context"""
    try:
        from rag.rag_graph import get_retriever
        from rag.retriever import smart_retrieve, MetadataEnhancedHybridRetriever
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Analyzing Quân y position for query: {query}")
        
        # Get retriever and documents
        retriever = get_retriever()
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            docs = smart_retrieve(retriever, query, use_smart_filtering=True)
        else:
            docs = retriever.get_relevant_documents(query)
        
        print(f"📋 Retrieved {len(docs)} documents")
        
        # Check each document for Quân y and PHÒNG THIẾT BỊ content
        for i, doc in enumerate(docs):
            content = doc.page_content
            content_lower = content.lower()
            
            if "quân y" in content_lower:
                print(f"\n✅ Document {i+1} contains 'Quân y':")
                print(f"   Full content:\n{content}")
                print(f"   Length: {len(content)} characters")
            
            if "phòng thiết bị" in content_lower:
                print(f"\n🏢 Document {i+1} contains 'PHÒNG THIẾT BỊ':")
                print(f"   Full content:\n{content}")
                print(f"   Length: {len(content)} characters")
        
        # Check combined context
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Find all sections related to PHÒNG THIẾT BỊ - QUẢN TRỊ
        print(f"\n🔍 Looking for complete PHÒNG THIẾT BỊ - QUẢN TRỊ structure in context:")
        
        # Split by sections and check
        lines = context.split('\n')
        in_phong_thiet_bi_section = False
        phong_thiet_bi_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if "xi. phòng thiết bị" in line_lower or "phòng thiết bị - quản trị" in line_lower:
                in_phong_thiet_bi_section = True
                phong_thiet_bi_content.append(line)
                print(f"📋 Found PHÒNG THIẾT BỊ header: {line}")
            elif in_phong_thiet_bi_section:
                if line.strip().startswith("XII.") or line.strip().startswith("XIII.") or "PHÒNG" in line.upper() and not "phòng làm việc" in line.lower():
                    # We've moved to next section
                    break
                else:
                    phong_thiet_bi_content.append(line)
        
        print(f"\n📋 Complete PHÒNG THIẾT BỊ - QUẢN TRỊ section content:")
        complete_section = '\n'.join(phong_thiet_bi_content)
        print(complete_section)
        
        print(f"\n📋 Complete section contains 'Quân y': {'quân y' in complete_section.lower()}")
        
    except Exception as e:
        print(f"❌ Error analyzing Quân y position: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quan_y_position()