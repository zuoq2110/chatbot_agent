#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug sliding window retrieval
"""
import os
import sys
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent.absolute()
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def debug_sliding_window():
    """Debug sliding window functionality"""
    print("🔍 Debugging Sliding Window Retrieval")
    print("=" * 60)
    
    try:
        from rag.retriever import create_enhanced_hybrid_retriever, smart_retrieve, MetadataEnhancedHybridRetriever
        
        vector_db_path = os.path.join(current_dir, "vector_db")
        data_dir = os.path.join(current_dir, "data")
        
        # Test query about PHÒNG THIẾT BỊ - QUẢN TRỊ
        query = "nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        
        print(f"🔍 Query: {query}")
        print("\n" + "="*50)
        
        # Test with different window sizes
        for window_size in [0, 1, 2]:
            print(f"\n📋 Testing with Window Size: {window_size}")
            print("-" * 40)
            
            retriever, all_docs = create_enhanced_hybrid_retriever(
                vector_db_path=vector_db_path,
                data_dir=data_dir,
                window_size=window_size
            )
            
            # Check if retriever has the sliding window functionality
            if isinstance(retriever, MetadataEnhancedHybridRetriever):
                print(f"✅ Using MetadataEnhancedHybridRetriever with window_size={retriever.window_size}")
                print(f"📄 Total documents loaded: {len(retriever.all_documents) if retriever.all_documents else 0}")
            else:
                print("❌ Not using MetadataEnhancedHybridRetriever!")
                continue
            
            # Get results
            results = smart_retrieve(retriever, query, use_smart_filtering=True)
            
            print(f"📊 Retrieved {len(results)} documents")
            
            # Analyze the first 10 results in detail
            phong_thiet_bi_docs = []
            quan_y_found = False
            van_ban_found = False
            dam_bao_found = False
            
            for i, doc in enumerate(results[:15]):  # Check first 15 results
                content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                filename = doc.metadata.get('filename', 'Unknown')
                chunk_index = doc.metadata.get('chunk_index', 'No index')
                
                # Check if this is about PHÒNG THIẾT BỊ - QUẢN TRỊ or contains Quân y
                is_phong_thiet_bi = "PHÒNG THIẾT BỊ" in doc.page_content
                contains_quan_y = "Quân y" in doc.page_content
                contains_van_ban = "Văn bản quy định" in doc.page_content
                contains_dam_bao = "Đảm bảo cơ sở vật chất" in doc.page_content
                
                # Track what we've found
                if contains_quan_y:
                    quan_y_found = True
                if contains_van_ban:
                    van_ban_found = True
                if contains_dam_bao:
                    dam_bao_found = True
                
                if is_phong_thiet_bi or contains_quan_y or (contains_van_ban and contains_dam_bao):
                    phong_thiet_bi_docs.append((i, doc))
                    print(f"\n📄 Document {i+1} ({'PHÒNG THIẾT BỊ' if is_phong_thiet_bi else 'RELATED'}):")
                    print(f"   File: {filename}")
                    print(f"   Chunk Index: {chunk_index}")
                    print(f"   Content: {content}")
                    
                    # Check specific sections
                    if contains_van_ban:
                        print("     ✅ Contains 'Văn bản quy định'")
                    if contains_dam_bao:
                        print("     ✅ Contains 'Đảm bảo cơ sở vật chất'")
                    if contains_quan_y:
                        print("     🎯✅ Contains 'Quân y' section - FOUND!")
                elif i < 5:  # Show first 5 non-related docs
                    print(f"\n📄 Document {i+1}:")
                    print(f"   File: {filename}")  
                    print(f"   Chunk Index: {chunk_index}")
                    print(f"   Content: {content}")
            
            print(f"\n📋 Summary for Window Size {window_size}:")
            print(f"   - Found {len(phong_thiet_bi_docs)} PHÒNG THIẾT BỊ related docs in top 15 results")
            
            print(f"   - Has 'Văn bản quy định': {'✅' if van_ban_found else '❌'}")
            print(f"   - Has 'Đảm bảo cơ sở vật chất': {'✅' if dam_bao_found else '❌'}")
            print(f"   - Has 'Quân y': {'🎯✅' if quan_y_found else '❌'}")
            
            if van_ban_found and dam_bao_found and quan_y_found:
                print(f"   🎉 COMPLETE: All 3 sections found in top 15 results!")
            else:
                print(f"   ⚠️  INCOMPLETE: Missing sections in top 15 results")
        
        # Let's also check the raw document structure
        print(f"\n📊 Analyzing document structure...")
        print("-" * 40)
        
        if all_docs:
            # Find documents about PHÒNG THIẾT BỊ
            relevant_docs = []
            for i, doc in enumerate(all_docs):
                if "PHÒNG THIẾT BỊ" in doc.page_content:
                    relevant_docs.append((i, doc))
            
            print(f"📄 Found {len(relevant_docs)} documents containing 'PHÒNG THIẾT BỊ':")
            
            for idx, (doc_index, doc) in enumerate(relevant_docs):
                chunk_index = doc.metadata.get('chunk_index', 'No index')
                content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                
                print(f"\n  {idx+1}. Document index in all_docs: {doc_index}")
                print(f"     Chunk index: {chunk_index}")
                print(f"     Content preview: {content_preview}")
                
                # Check specific sections
                sections = []
                if "Văn bản quy định" in doc.page_content:
                    sections.append("Văn bản quy định")
                if "Đảm bảo cơ sở vật chất" in doc.page_content:
                    sections.append("Đảm bảo cơ sở vật chất")
                if "Quân y" in doc.page_content:
                    sections.append("Quân y")
                    print("     🎯 Contains 'Quân y' - THIS IS THE MISSING PIECE!")
                
                if sections:
                    print(f"     ✅ Contains: {', '.join(sections)}")
                    
            # Check if chunk 62 was in retrieval results
            print(f"\n🔍 Checking if chunk 62 (with Quân y) was retrieved...")
            chunk_62_found = False
            for i, doc in enumerate(results):
                if doc.metadata.get('chunk_index') == 62:
                    print(f"   ✅ Chunk 62 found at position {i+1} in results")
                    chunk_62_found = True
                    break
            
            if not chunk_62_found:
                print(f"   ❌ Chunk 62 NOT found in retrieval results!")
                print(f"   💡 This explains why context boosting didn't help")
                
                # Let's find what chunks were retrieved from the same file
                same_file_chunks = []
                target_filename = "02. Hoạt động đảm bảo chất lượng giáo dục tại HVKTMM.txt"
                for i, doc in enumerate(results):
                    if doc.metadata.get('filename') == target_filename:
                        chunk_idx = doc.metadata.get('chunk_index', 'No index')
                        same_file_chunks.append((i+1, chunk_idx))
                
                print(f"   📄 Chunks from same file in results: {same_file_chunks[:10]}...")
                
                # Check similarity scores for chunk 62 directly
                print(f"\n🔬 Let's manually check why chunk 62 wasn't retrieved...")
                chunk_62 = None
                for doc in all_docs:
                    if (doc.metadata.get('chunk_index') == 62 and 
                        doc.metadata.get('filename') == target_filename):
                        chunk_62 = doc
                        break
                        
                if chunk_62:
                    print(f"   📝 Chunk 62 content: {chunk_62.page_content[:200]}...")
                    print(f"   🤔 Query: '{query}'")
                    print(f"   💭 Chunk 62 might have low semantic similarity with the query")
                    
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sliding_window()