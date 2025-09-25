#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test with an explicit prompt that asks LLM to find all numbered sections
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_explicit_prompt():
    """Test with explicit prompt asking for all sections"""
    try:
        from llm.config import get_gemini_llm
        from rag.rag_graph import get_retriever
        from rag.retriever import smart_retrieve, MetadataEnhancedHybridRetriever
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Testing with explicit prompt for query: {query}")
        
        # Get retriever and documents
        retriever = get_retriever()
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            docs = smart_retrieve(retriever, query, use_smart_filtering=True)
        else:
            docs = retriever.get_relevant_documents(query)
        
        # Combine content
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create explicit prompt
        explicit_prompt = f"""Dựa trên tài liệu được cung cấp, hãy liệt kê TẤT CẢ các nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ.

QUAN TRỌNG: 
- Hãy đọc kỹ TOÀN BỘ tài liệu dưới đây
- Tìm tất cả các phần được đánh số (1., 2., 3., ...) liên quan đến PHÒNG THIẾT BỊ - QUẢN TRỊ
- Ngay cả khi các phần này xuất hiện ở những vị trí khác nhau trong tài liệu, hãy tổng hợp chúng lại
- Đừng bỏ sót bất kỳ phần nào

Câu hỏi: {query}

Tài liệu:
{context}

Hãy trả lời bằng cách liệt kê đầy đủ tất cả các nhiệm vụ, bao gồm cả các phần có thể nằm rời rạc trong tài liệu."""
        
        print(f"\n📋 Context contains 'Quân y': {'quân y' in context.lower()}")
        
        # Test with LLM
        llm = get_gemini_llm()
        print(f"\n🤖 Calling LLM with explicit prompt...")
        
        response = llm.invoke([{"role": "user", "content": explicit_prompt}])
        
        print(f"\n✅ LLM Response:")
        print(response.content)
        
        print(f"\n📋 Response contains 'Quân y': {'quân y' in response.content.lower()}")
        
        return response.content
        
    except Exception as e:
        print(f"❌ Error testing explicit prompt: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_explicit_prompt()