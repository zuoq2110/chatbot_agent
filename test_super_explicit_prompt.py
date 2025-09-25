#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test with super explicit prompt using specific example
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_super_explicit_prompt():
    """Test with super explicit prompt using specific example"""
    try:
        from llm.config import get_gemini_llm
        from rag.rag_graph import get_retriever
        from rag.retriever import smart_retrieve, MetadataEnhancedHybridRetriever
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Testing with super explicit prompt for query: {query}")
        
        # Get retriever and documents
        retriever = get_retriever()
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            docs = smart_retrieve(retriever, query, use_smart_filtering=True)
        else:
            docs = retriever.get_relevant_documents(query)
        
        # Combine content
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create super explicit prompt with example
        super_explicit_prompt = f"""Tôi sẽ cung cấp cho bạn một tài liệu và bạn cần liệt kê TẤT CẢ các nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ.

HƯỚNG DẪN QUAN TRỌNG:
1. Tìm phần "XI. PHÒNG THIẾT BỊ - QUẢN TRỊ" trong tài liệu
2. Tất cả các section được đánh số (1., 2., 3., ...) sau "XI. PHÒNG THIẾT BỊ - QUẢN TRỊ" đều thuộc về phòng này
3. Ngay cả khi có ngắt trang như "[TRANG 15]" ở giữa, section vẫn thuộc về PHÒNG THIẾT BỊ cho đến khi gặp phòng mới (XII. PHÒNG CHÍNH TRỊ)

VÍ DỤ: 
Nếu bạn thấy:
"XI. PHÒNG THIẾT BỊ - QUẢN TRỊ
1. Văn bản quy định
2. Đảm bảo cơ sở vật chất
[TRANG 15]
3. Quân y
XII. PHÒNG CHÍNH TRỊ"

Thì cả 3 section (1. Văn bản quy định, 2. Đảm bảo cơ sở vật chất, 3. Quân y) đều thuộc về PHÒNG THIẾT BỊ - QUẢN TRỊ.

BÂY GIỜ HÃY ÁP DỤNG QUY TẮC NÀY VÀO TÀI LIỆU DƯỚI ĐÂY:

Tài liệu:
{context}

Hãy liệt kê TẤT CẢ các nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ theo đúng cấu trúc được đánh số trong tài liệu."""
        
        print(f"\n📋 Context contains 'Quân y': {'quân y' in context.lower()}")
        
        # Test with LLM
        llm = get_gemini_llm()
        print(f"\n🤖 Calling LLM with super explicit prompt...")
        
        response = llm.invoke([{"role": "user", "content": super_explicit_prompt}])
        
        print(f"\n✅ LLM Response:")
        print(response.content)
        
        print(f"\n📋 Response contains 'Quân y': {'quân y' in response.content.lower()}")
        
        return response.content
        
    except Exception as e:
        print(f"❌ Error testing super explicit prompt: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_super_explicit_prompt()