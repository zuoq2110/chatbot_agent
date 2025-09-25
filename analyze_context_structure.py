#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyze the exact context structure to understand the Quân y issue
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def analyze_context_structure():
    """Analyze the exact structure of context around Quân y"""
    try:
        from rag.rag_graph import get_retriever
        from rag.retriever import smart_retrieve, MetadataEnhancedHybridRetriever
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Analyzing context structure for: {query}")
        
        # Get retriever and documents
        retriever = get_retriever()
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            docs = smart_retrieve(retriever, query, use_smart_filtering=True)
        else:
            docs = retriever.get_relevant_documents(query)
        
        # Find the exact sequence around Quân y
        context = "\n\n".join([doc.page_content for doc in docs])
        
        print(f"📋 Full context structure:")
        print("="*80)
        print(context)
        print("="*80)
        
        # Find where "XI. PHÒNG THIẾT BỊ" appears
        lines = context.split('\n')
        phong_thiet_bi_index = -1
        quan_y_index = -1
        
        for i, line in enumerate(lines):
            if "xi. phòng thiết bị" in line.lower():
                phong_thiet_bi_index = i
                print(f"📋 Found 'XI. PHÒNG THIẾT BỊ' at line {i}: {line}")
            if "3. quân y" in line.lower():
                quan_y_index = i
                print(f"📋 Found '3. Quân y' at line {i}: {line}")
        
        if phong_thiet_bi_index >= 0 and quan_y_index >= 0:
            print(f"\n📋 Distance between headers: {quan_y_index - phong_thiet_bi_index} lines")
            
            # Show the structure between them
            start = max(0, phong_thiet_bi_index - 2)
            end = min(len(lines), quan_y_index + 5)
            
            print(f"\n📋 Context from line {start} to {end}:")
            for i in range(start, end):
                marker = ">>>" if i == phong_thiet_bi_index or i == quan_y_index else "   "
                print(f"{marker} {i:3d}: {lines[i]}")
        
        # Check what appears between XI. PHÒNG THIẾT BỊ and XII. PHÒNG CHÍNH TRỊ
        print(f"\n📋 Looking for section boundaries...")
        for i, line in enumerate(lines):
            if "xii." in line.lower() and "phòng chính trị" in line.lower():
                print(f"📋 Found 'XII. PHÒNG CHÍNH TRỊ' at line {i}: {line}")
                break
        
        return context
        
    except Exception as e:
        print(f"❌ Error analyzing context: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    analyze_context_structure()