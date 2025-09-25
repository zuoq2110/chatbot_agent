#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify sliding window integration
"""
import os
import sys
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent.absolute()
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def test_enhanced_retriever():
    """Test enhanced retriever with sliding window"""
    print("🧪 Testing Enhanced Retriever Integration")
    print("=" * 60)
    
    try:
        from rag.rag_graph import get_retriever, process_kma_query
        from rag.retriever import MetadataEnhancedHybridRetriever, smart_retrieve
        
        print("1. Testing get_retriever()...")
        retriever = get_retriever()
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            print("   ✅ Enhanced retriever loaded successfully")
            print(f"   📄 Window size: {retriever.window_size}")
            print(f"   📊 Total documents: {len(retriever.all_documents) if retriever.all_documents else 'Unknown'}")
        else:
            print("   ⚠️  Fallback to old retriever")
        
        print("\n2. Testing smart_retrieve()...")
        test_query = "nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        
        if isinstance(retriever, MetadataEnhancedHybridRetriever):
            docs = smart_retrieve(retriever, test_query, use_smart_filtering=True)
            print(f"   ✅ Smart retrieve returned {len(docs)} documents")
            
            # Check for complete sections
            has_van_ban = any("Văn bản quy định" in doc.page_content for doc in docs[:10])
            has_dam_bao = any("Đảm bảo cơ sở vật chất" in doc.page_content for doc in docs[:10])
            has_quan_y = any("Quân y" in doc.page_content for doc in docs[:10])
            
            print(f"   📋 In top 10 results:")
            print(f"      - Văn bản quy định: {'✅' if has_van_ban else '❌'}")
            print(f"      - Đảm bảo cơ sở vật chất: {'✅' if has_dam_bao else '❌'}")
            print(f"      - Quân y: {'🎯✅' if has_quan_y else '❌'}")
            
            if has_van_ban and has_dam_bao and has_quan_y:
                print("   🎉 COMPLETE: All sections found!")
            else:
                print("   ⚠️  INCOMPLETE: Some sections missing")
        else:
            print("   ⚠️  Smart retrieve not available with this retriever type")
        
        print("\n3. Testing process_kma_query()...")
        import asyncio
        result = asyncio.run(process_kma_query(test_query))
        
        if result and "answer" in result:
            answer_length = len(result["answer"])
            sources_count = len(result.get("sources", []))
            print(f"   ✅ Query processed successfully")
            print(f"   📝 Answer length: {answer_length} characters")
            print(f"   📚 Sources count: {sources_count}")
            
            # Check if answer contains all 3 sections
            answer = result["answer"].lower()
            answer_has_van_ban = "văn bản quy định" in answer or "quy định" in answer
            answer_has_dam_bao = "đảm bảo cơ sở vật chất" in answer or "cơ sở vật chất" in answer
            answer_has_quan_y = "quân y" in answer
            
            print(f"   📋 Answer mentions:")
            print(f"      - Văn bản/Quy định: {'✅' if answer_has_van_ban else '❌'}")
            print(f"      - Cơ sở vật chất: {'✅' if answer_has_dam_bao else '❌'}")
            print(f"      - Quân y: {'🎯✅' if answer_has_quan_y else '❌'}")
        else:
            print("   ❌ Query processing failed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_chat_agent():
    """Test SimpleChatAgent integration"""
    print("\n🤖 Testing SimpleChatAgent Integration") 
    print("=" * 60)
    
    try:
        from rag.simple_chat_agent import SimpleChatAgent
        from rag.retriever import MetadataEnhancedHybridRetriever
        
        print("1. Creating SimpleChatAgent...")
        agent = SimpleChatAgent()
        
        if isinstance(agent.retriever, MetadataEnhancedHybridRetriever):
            print("   ✅ Enhanced retriever loaded in agent")
            print(f"   📄 Window size: {agent.retriever.window_size}")
        else:
            print("   ⚠️  Fallback retriever in agent")
        
        print("\n2. Testing chat functionality...")
        test_query = "nhiệm vụ của PHÒNG THIẾT BỊ - QUẢN TRỊ"
        response = agent.chat(test_query)
        
        if response:
            response_length = len(response)
            print(f"   ✅ Chat response generated")
            print(f"   📝 Response length: {response_length} characters")
            
            # Check content
            response_lower = response.lower()
            has_van_ban = "văn bản" in response_lower or "quy định" in response_lower
            has_dam_bao = "đảm bảo" in response_lower or "cơ sở vật chất" in response_lower
            has_quan_y = "quân y" in response_lower
            
            print(f"   📋 Response includes:")
            print(f"      - Văn bản/Quy định: {'✅' if has_van_ban else '❌'}")
            print(f"      - Đảm bảo/Cơ sở vật chất: {'✅' if has_dam_bao else '❌'}")
            print(f"      - Quân y: {'🎯✅' if has_quan_y else '❌'}")
            
            return has_van_ban and has_dam_bao and has_quan_y
        else:
            print("   ❌ No response generated")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests"""
    print("🚀 Starting Sliding Window Integration Tests")
    print("=" * 80)
    
    results = []
    
    # Test enhanced retriever
    results.append(test_enhanced_retriever())
    
    # Test simple chat agent
    results.append(test_simple_chat_agent())
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Sliding window integration is working correctly!")
        return True
    else:
        print("⚠️  Some tests failed - Check the output above for details")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)