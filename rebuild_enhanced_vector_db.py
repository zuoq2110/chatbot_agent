#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild vector database with enhanced metadata and sliding window support
"""
import os
import sys
import shutil
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent.absolute()
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

from rag.retriever import create_enhanced_vector_database

def rebuild_enhanced_vector_db():
    """Rebuild vector database with enhanced features"""
    print("🔄 Rebuilding Enhanced Vector Database")
    print("=" * 50)
    
    # Paths
    vector_db_path = os.path.join(current_dir, "vector_db")
    data_dir = os.path.join(current_dir, "data")
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    # Remove existing vector database
    if os.path.exists(vector_db_path):
        print(f"🗑️  Removing existing vector database...")
        shutil.rmtree(vector_db_path)
    
    try:
        print(f"📊 Processing data from: {data_dir}")
        print(f"💾 Creating vector database at: {vector_db_path}")
        
        # Create enhanced vector database
        documents = create_enhanced_vector_database(vector_db_path, data_dir)
        
        print(f"✅ Successfully created vector database with {len(documents)} documents")
        
        # Show some statistics
        file_stats = {}
        chunk_types = {'text': 0, 'table': 0}
        
        for doc in documents:
            if hasattr(doc, 'metadata'):
                filename = doc.metadata.get('filename', 'Unknown')
                chunk_type = doc.metadata.get('chunk_type', 'text')
                
                if filename not in file_stats:
                    file_stats[filename] = 0
                file_stats[filename] += 1
                
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        print("\n📈 Database Statistics:")
        print(f"  Total documents: {len(documents)}")
        print(f"  Text chunks: {chunk_types.get('text', 0)}")
        print(f"  Table chunks: {chunk_types.get('table', 0)}")
        print("\n📁 Files processed:")
        
        for filename, count in file_stats.items():
            print(f"  {filename}: {count} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error rebuilding vector database: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sliding_window_retrieval():
    """Test sliding window retrieval after rebuilding"""
    print("\n🔍 Testing Sliding Window Retrieval")
    print("=" * 50)
    
    try:
        from rag.retriever import create_enhanced_hybrid_retriever, smart_retrieve
        
        vector_db_path = os.path.join(current_dir, "vector_db")
        data_dir = os.path.join(current_dir, "data")
        
        # Test with different window sizes
        test_queries = [
            "quy định về thi cử và khảo thí",
            "thành phần hội đồng",
            "điều kiện tốt nghiệp",
            "nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        ]
        
        for window_size in [0, 1, 2]:
            print(f"\n📋 Window Size: {window_size}")
            print("-" * 30)
            
            retriever, _ = create_enhanced_hybrid_retriever(
                vector_db_path=vector_db_path,
                data_dir=data_dir,
                window_size=window_size
            )
            
            for query in test_queries:
                results = smart_retrieve(retriever, query, use_smart_filtering=True)
                print(f"Query: '{query}' -> {len(results)} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sliding window: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced Vector Database Rebuild")
    print("=" * 60)
    
    success = rebuild_enhanced_vector_db()
    
    if success:
        print("\n🧪 Running sliding window test...")
        test_sliding_window_retrieval()
        print("\n✅ All operations completed successfully!")
    else:
        print("\n❌ Failed to rebuild vector database")
        sys.exit(1)