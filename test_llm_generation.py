#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to debug LLM generation with exact prompt
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_llm_generation():
    """Test LLM generation with exact context and prompt"""
    try:
        from llm.config import get_gemini_llm
        from rag.rag_graph import get_retriever
        from rag.retriever import smart_retrieve, MetadataEnhancedHybridRetriever
        
        query = "Nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        print(f"🔍 Testing LLM generation for query: {query}")
        
        # Get retriever and documents
        retriever = get_retriever()
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            docs = smart_retrieve(retriever, query, use_smart_filtering=True)
        else:
            docs = retriever.get_relevant_documents(query)
        
        # Combine content
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Load prompt template
        prompts_dir = os.path.join(os.path.dirname(__file__), 'src', 'rag', 'prompts')
        with open(os.path.join(prompts_dir, "generate.txt"), "r", encoding='utf-8') as f:
            generate_prompt = f.read().strip()
        
        # Create full prompt
        full_prompt = generate_prompt.format(question=query, context=context)
        
        print(f"\n📋 Full prompt preview (first 500 chars):")
        print(full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
        
        print(f"\n📋 Context contains 'Quân y': {'quân y' in context.lower()}")
        
        # Test with LLM
        llm = get_gemini_llm()
        print(f"\n🤖 Calling LLM...")
        
        response = llm.invoke([{"role": "user", "content": full_prompt}])
        
        print(f"\n✅ LLM Response:")
        print(response.content)
        
        print(f"\n📋 Response contains 'Quân y': {'quân y' in response.content.lower()}")
        
        # Check if response mentions all 3 sections
        sections = ["văn bản quy định", "đảm bảo cơ sở vật chất", "quân y"]
        for section in sections:
            found = section in response.content.lower()
            print(f"📋 Response mentions '{section}': {found}")
        
        return response.content
        
    except Exception as e:
        print(f"❌ Error testing LLM generation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_llm_generation()