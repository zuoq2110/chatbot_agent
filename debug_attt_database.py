#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug to check if ATTT file is in vector database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.retriever import load_enhanced_vector_database

def check_attt_in_database():
    print("🔍 Checking if ATTT file exists in vector database...")
    
    # Load vector database
    vector_db_path = os.path.join(os.path.dirname(__file__), "vector_db")
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    try:
        vectorstore, documents = load_enhanced_vector_database(vector_db_path, data_dir)
        
        print(f"📊 Total documents in database: {len(documents)}")
        
        # Look for ATTT related documents
        attt_docs = []
        for i, doc in enumerate(documents):
            if any(keyword in doc.page_content.lower() for keyword in ["an toàn thông tin", "attt", "165 tc", "khối lượng kiến thức toàn khóa"]):
                attt_docs.append((i, doc))
        
        print(f"📋 Found {len(attt_docs)} documents containing ATTT keywords")
        
        for i, (doc_idx, doc) in enumerate(attt_docs[:5]):  # Show first 5
            print(f"\nDoc {i+1} (index {doc_idx}):")
            print(f"Metadata: {doc.metadata}")
            print(f"Content preview: {doc.page_content[:200]}...")
        
        # Check specifically for "165" and "135"
        docs_165 = [doc for doc in documents if "165" in doc.page_content]
        docs_135 = [doc for doc in documents if "135" in doc.page_content]
        
        print(f"\n📊 Documents containing '165': {len(docs_165)}")
        print(f"📊 Documents containing '135': {len(docs_135)}")
        
        if docs_165:
            print("\nFirst doc with '165':")
            print(f"Metadata: {docs_165[0].metadata}")
            print(f"Content: {docs_165[0].page_content[:300]}...")
            
        if docs_135:
            print("\nFirst doc with '135':")
            print(f"Metadata: {docs_135[0].metadata}")
            print(f"Content: {docs_135[0].page_content[:300]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_attt_in_database()