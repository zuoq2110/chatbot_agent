#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug metadata filtering for ATTT queries
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.retriever import load_enhanced_vector_database, smart_retrieve, analyze_query_for_metadata_filter

def debug_attt_retrieval():
    print("🔍 Debug ATTT retrieval process...")
    
    # Load vector database
    vector_db_path = os.path.join(os.path.dirname(__file__), "vector_db")
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    try:
        vectorstore, documents = load_enhanced_vector_database(vector_db_path, data_dir)
        
        from rag.retriever import MetadataEnhancedHybridRetriever
        from langchain_community.retrievers import BM25Retriever
        
        # Create retriever
        texts = [doc.page_content for doc in documents]
        bm25_retriever = BM25Retriever.from_texts(texts=texts, k=15)
        bm25_retriever.docs = documents
        
        retriever = MetadataEnhancedHybridRetriever(
            vectorstore=vectorstore,
            bm25_retriever=bm25_retriever,
            k=8,
            window_size=2,
            all_documents=documents
        )
        
        # Test query
        query = "KHỐI LƯỢNG KIẾN THỨC TOÀN KHÓA ngành an toàn thông tin"
        
        print(f"📝 Query: {query}")
        
        # Check metadata filtering
        metadata_filter = analyze_query_for_metadata_filter(query)
        print(f"🏷️  Metadata filter: {metadata_filter}")
        
        # Get documents with smart retrieve
        docs = smart_retrieve(retriever, query, use_smart_filtering=True)
        
        print(f"\n📊 Retrieved {len(docs)} documents:")
        
        for i, doc in enumerate(docs[:5]):
            print(f"\nDoc {i+1}:")
            print(f"  Metadata: {doc.metadata}")
            content = doc.page_content.replace('\n', ' ')[:200]
            print(f"  Content: {content}...")
            
            # Check if it contains the right info
            if "165 tc" in doc.page_content.lower() or "165 tín chỉ" in doc.page_content.lower():
                print(f"  ✅ Contains 165 TC")
            elif "135 tc" in doc.page_content.lower() or "135 tín chỉ" in doc.page_content.lower():
                print(f"  ❌ Contains 135 TC (wrong)")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_attt_retrieval()