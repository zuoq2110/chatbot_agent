#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug sliding window for PHÒNG THIẾT BỊ - QUẢN TRỊ query
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.rag_graph import get_retriever
from rag.retriever import smart_retrieve

def debug_sliding_window():
    print("🔍 Debugging sliding window for PHÒNG THIẾT BỊ - QUẢN TRỊ...")
    
    # Initialize retriever
    retriever = get_retriever()
    print(f"📊 Retriever window size: {retriever.window_size}")
    print(f"📊 Total documents: {len(retriever.all_documents) if retriever.all_documents else 0}")
    print()
    
    # Test query
    query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
    
    # Get initial results without smart filtering
    print("🔍 Getting initial results...")
    initial_docs = retriever._get_relevant_documents(query)
    
    print(f"📋 Initial retrieval found: {len(initial_docs)} documents")
    
    # Check which docs contain PHÒNG THIẾT BỊ
    relevant_docs = []
    for i, doc in enumerate(initial_docs):
        content_lower = doc.page_content.lower()
        if "phòng thiết bị" in content_lower and "quản trị" in content_lower:
            chunk_idx = doc.metadata.get('chunk_index', -1)
            filename = doc.metadata.get('filename', 'unknown')
            relevant_docs.append((i, chunk_idx, filename, doc))
            print(f"   ✅ Doc {i+1}: Chunk #{chunk_idx} from {filename}")
        elif "quân y" in content_lower:
            chunk_idx = doc.metadata.get('chunk_index', -1)
            filename = doc.metadata.get('filename', 'unknown')
            print(f"   🔍 Doc {i+1}: Chunk #{chunk_idx} from {filename} (contains 'Quân y')")
    
    print(f"\n📋 Found {len(relevant_docs)} documents with PHÒNG THIẾT BỊ content")
    
    # Test sliding window manually
    if relevant_docs and retriever.all_documents:
        print("\n🔄 Testing sliding window expansion...")
        
        for i, (doc_idx, chunk_idx, filename, doc) in enumerate(relevant_docs):
            print(f"\n📄 Processing Doc {doc_idx+1} (Chunk #{chunk_idx}):")
            
            # Find neighbors manually
            neighbors = []
            for window_doc in retriever.all_documents:
                if (window_doc.metadata.get('filename') == filename):
                    window_chunk_idx = window_doc.metadata.get('chunk_index', -1)
                    distance = abs(window_chunk_idx - chunk_idx)
                    if distance <= retriever.window_size:
                        neighbors.append((window_chunk_idx, distance, window_doc))
            
            # Sort by chunk index
            neighbors.sort(key=lambda x: x[0])
            
            print(f"   🔍 Found {len(neighbors)} neighbors within window size {retriever.window_size}:")
            for neighbor_idx, distance, neighbor_doc in neighbors:
                has_quan_y = "quân y" in neighbor_doc.page_content.lower()
                marker = "🎯" if has_quan_y else "📄"
                print(f"      {marker} Chunk #{neighbor_idx} (distance: {distance}) {' - Contains Quân y!' if has_quan_y else ''}")
    
    # Test with smart_retrieve
    print(f"\n{'='*60}")
    print("🧠 Testing smart_retrieve function...")
    smart_docs = smart_retrieve(retriever, query, use_smart_filtering=True)
    
    print(f"📋 Smart retrieve returned: {len(smart_docs)} documents")
    
    # Check if Quân y is included
    quan_y_found = False
    for i, doc in enumerate(smart_docs[:10]):  # Check first 10
        if "quân y" in doc.page_content.lower():
            quan_y_found = True
            chunk_idx = doc.metadata.get('chunk_index', -1)
            filename = doc.metadata.get('filename', 'unknown')
            print(f"   ✅ Doc {i+1}: Chunk #{chunk_idx} from {filename} - Contains 'Quân y'!")
    
    if not quan_y_found:
        print("   ❌ No document with 'Quân y' found in smart_retrieve results!")
        print("   🔍 Checking all smart_retrieve results...")
        for i, doc in enumerate(smart_docs):
            if "quân y" in doc.page_content.lower():
                chunk_idx = doc.metadata.get('chunk_index', -1)
                filename = doc.metadata.get('filename', 'unknown')
                print(f"      Found at position {i+1}: Chunk #{chunk_idx} from {filename}")
                break

if __name__ == "__main__":
    debug_sliding_window()