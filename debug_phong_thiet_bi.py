#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug why the response includes content from PHÒNG HÀNH CHÍNH
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def debug_phong_thiet_bi():
    """Debug why response includes PHÒNG HÀNH CHÍNH content"""
    try:
        from rag.rag_graph import get_retriever
        from rag.retriever import smart_retrieve, MetadataEnhancedHybridRetriever
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Debugging mixed department content for: {query}")
        
        # Get retriever and documents
        retriever = get_retriever()
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            docs = smart_retrieve(retriever, query, use_smart_filtering=True)
        else:
            docs = retriever.get_relevant_documents(query)
        
        print(f"📋 Retrieved {len(docs)} documents")
        
        # Check each document to see which departments they mention
        phong_thiet_bi_docs = []
        phong_hanh_chinh_docs = []
        other_docs = []
        
        for i, doc in enumerate(docs):
            content_lower = doc.page_content.lower()
            
            has_thiet_bi = "phòng thiết bị" in content_lower or "xi. phòng thiết bị" in content_lower
            has_hanh_chinh = "phòng hành chính" in content_lower or "ix. phòng hành chính" in content_lower
            
            if has_thiet_bi:
                phong_thiet_bi_docs.append((i, doc))
                print(f"✅ Doc {i+1} - PHÒNG THIẾT BỊ content")
            elif has_hanh_chinh:
                phong_hanh_chinh_docs.append((i, doc))
                print(f"⚠️  Doc {i+1} - PHÒNG HÀNH CHÍNH content")
            else:
                other_docs.append((i, doc))
                # Check what department this might be
                if "phòng" in content_lower:
                    # Find department mentions
                    lines = content_lower.split('\n')
                    dept_mentions = []
                    for line in lines:
                        if 'phòng' in line and ('.') in line:
                            dept_mentions.append(line.strip())
                    if dept_mentions:
                        print(f"🔍 Doc {i+1} - Other department: {dept_mentions[0][:50]}...")
                    else:
                        print(f"❓ Doc {i+1} - Unknown content")
                else:
                    print(f"❓ Doc {i+1} - No department mention")
        
        print(f"\n📊 Summary:")
        print(f"   PHÒNG THIẾT BỊ docs: {len(phong_thiet_bi_docs)}")
        print(f"   PHÒNG HÀNH CHÍNH docs: {len(phong_hanh_chinh_docs)}")
        print(f"   Other docs: {len(other_docs)}")
        
        # Show content that mentions "văn thư" or "PCCC" that might be confusing
        print(f"\n🔍 Looking for confusing content (văn thư, PCCC):")
        for i, doc in enumerate(docs):
            content_lower = doc.page_content.lower()
            if "văn thư" in content_lower or "pccc" in content_lower:
                print(f"\nDoc {i+1} contains văn thư/PCCC:")
                # Show which department section this belongs to
                lines = doc.page_content.split('\n')
                for j, line in enumerate(lines):
                    if "ix." in line.lower() or "xi." in line.lower() or "xii." in line.lower():
                        print(f"   Department header: {line.strip()}")
                        break
                print(f"   Content preview: {doc.page_content[:200]}...")
        
        return docs
        
    except Exception as e:
        print(f"❌ Error debugging: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_phong_thiet_bi()