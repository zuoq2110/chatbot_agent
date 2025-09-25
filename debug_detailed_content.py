#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug detailed content of retrieved documents to identify cross-contamination
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.rag_graph import get_retriever

def debug_detailed_content():
    print("🔍 Analyzing detailed content of retrieved documents...")
    
    # Initialize retriever
    retriever = get_retriever()
    
    # Query that causes mixed content
    query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
    
    # Retrieve documents
    docs = retriever.invoke(query)
    
    print(f"📋 Retrieved {len(docs)} documents for analysis:")
    print()
    
    # Analyze first 5 docs in detail
    for i, doc in enumerate(docs[:5]):
        print(f"{'='*60}")
        print(f"📄 Document {i+1}:")
        print(f"{'='*60}")
        
        # Full content
        content = doc.page_content
        print(f"📝 Full Content ({len(content)} chars):")
        print(content)
        print()
        
        # Metadata
        metadata = doc.metadata
        print(f"📊 Metadata:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")
        print()
        
        # Check for department mentions
        departments = [
            "PHÒNG THIẾT BỊ", "phòng thiết bị",
            "PHÒNG HÀNH CHÍNH", "phòng hành chính", 
            "PHÒNG ĐÀO TẠO", "phòng đào tạo",
            "PHÒNG KẾ HOẠCH", "phòng kế hoạch"
        ]
        
        found_depts = []
        content_lower = content.lower()
        for dept in departments:
            if dept.lower() in content_lower:
                found_depts.append(dept)
        
        if found_depts:
            print(f"🏢 Departments mentioned: {', '.join(found_depts)}")
        else:
            print(f"🏢 No department headers found")
        print()
        
        # Check for specific confusing keywords
        confusing_keywords = ["văn thư", "PCCC", "giấy giới thiệu", "lưu trữ", "hành chính"]
        found_keywords = []
        for keyword in confusing_keywords:
            if keyword.lower() in content_lower:
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"⚠️  Confusing keywords found: {', '.join(found_keywords)}")
        print()

if __name__ == "__main__":
    debug_detailed_content()