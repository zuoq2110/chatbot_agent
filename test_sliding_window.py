#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for sliding window functionality in RAG retriever
"""
import os
import sys
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent.absolute()
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

from rag.retriever import create_enhanced_hybrid_retriever, smart_retrieve

def test_sliding_window():
    """Test sliding window retrieval functionality"""
    print("🔍 Testing Sliding Window Functionality")
    print("=" * 50)
    
    # Paths
    vector_db_path = os.path.join(current_dir, "vector_db")
    data_dir = os.path.join(current_dir, "data")
    
    try:
        # Test with different window sizes
        window_sizes = [0, 1, 2]
        test_query = "quy định về thi cử"
        
        for window_size in window_sizes:
            print(f"\n📋 Testing with window_size={window_size}")
            print("-" * 30)
            
            # Create retriever with specified window size
            retriever, all_docs = create_enhanced_hybrid_retriever(
                vector_db_path=vector_db_path,
                data_dir=data_dir,
                window_size=window_size
            )
            
            print(f"Total documents in database: {len(all_docs)}")
            
            # Perform retrieval
            results = smart_retrieve(retriever, test_query, use_smart_filtering=True)
            
            print(f"Retrieved {len(results)} documents")
            
            # Show results with metadata
            for i, doc in enumerate(results[:5]):  # Show top 5 results
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                chunk_idx = metadata.get('chunk_index', 'N/A')
                source = metadata.get('filename', 'Unknown')
                chunk_type = metadata.get('chunk_type', 'text')
                
                print(f"  [{i+1}] Source: {source}")
                print(f"      Chunk Index: {chunk_idx}")
                print(f"      Type: {chunk_type}")
                print(f"      Content Preview: {doc.page_content[:100]}...")
                print()
        
        # Test with specific query that might benefit from sliding window
        print("\n🎯 Testing specific scenario")
        print("=" * 50)
        
        # Test query that might have related info in adjacent chunks
        specific_queries = [
            "thành phần hội đồng khảo thí",
            "quy trình nộp hồ sơ tốt nghiệp", 
            "điều kiện xét tốt nghiệp đại học"
        ]
        
        for query in specific_queries:
            print(f"\n Query: '{query}'")
            print("-" * 40)
            
            # Compare window_size=0 vs window_size=2
            for ws in [0, 2]:
                retriever, _ = create_enhanced_hybrid_retriever(
                    vector_db_path=vector_db_path,
                    data_dir=data_dir,
                    window_size=ws
                )
                
                results = smart_retrieve(retriever, query, use_smart_filtering=True)
                print(f"  Window Size {ws}: {len(results)} chunks retrieved")
                
                # Show chunk indices to see if adjacent chunks are included
                chunk_indices = []
                for doc in results[:10]:
                    if hasattr(doc, 'metadata'):
                        idx = doc.metadata.get('chunk_index', -1)
                        source = doc.metadata.get('filename', 'Unknown')
                        chunk_indices.append(f"{source}:{idx}")
                
                print(f"    Chunk indices: {chunk_indices}")
            print()
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def analyze_chunk_distribution():
    """Analyze how chunks are distributed in the database"""
    print("\n📊 Analyzing Chunk Distribution")
    print("=" * 50)
    
    vector_db_path = os.path.join(current_dir, "vector_db")
    data_dir = os.path.join(current_dir, "data")
    
    try:
        retriever, all_docs = create_enhanced_hybrid_retriever(
            vector_db_path=vector_db_path,
            data_dir=data_dir,
            window_size=0  # No window for analysis
        )
        
        # Group documents by source file
        file_chunks = {}
        for doc in all_docs:
            if hasattr(doc, 'metadata'):
                filename = doc.metadata.get('filename', 'Unknown')
                chunk_idx = doc.metadata.get('chunk_index', 0)
                
                if filename not in file_chunks:
                    file_chunks[filename] = []
                file_chunks[filename].append(chunk_idx)
        
        print(f"Files and their chunk counts:")
        for filename, chunks in file_chunks.items():
            chunks.sort()
            print(f"  {filename}: {len(chunks)} chunks (indices: {min(chunks)}-{max(chunks)})")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    print("🚀 Starting Sliding Window Tests")
    print("=" * 60)
    
    # Check if vector database exists
    vector_db_path = os.path.join(current_dir, "vector_db")
    if not os.path.exists(vector_db_path):
        print("❌ Vector database not found. Please run rebuild_vector_db.py first!")
        sys.exit(1)
    
    # Run tests
    analyze_chunk_distribution()
    test_sliding_window()
    
    print("\n✅ Testing completed!")