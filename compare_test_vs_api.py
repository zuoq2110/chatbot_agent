"""
So sánh kết quả giữa test file và API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import time
import requests
from src.rag.rag_graph import process_kma_query_sync
from src.llm.config import get_gemini_llm

def test_direct_rag(query: str):
    """Test direct RAG (giống test file)"""
    print("=" * 80)
    print("🔬 DIRECT RAG TEST (giống test_graph_rag_with_llm.py)")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    start_time = time.time()
    
    try:
        result = process_kma_query_sync(query)
        elapsed = time.time() - start_time
        
        print(f"✅ Completed in {elapsed:.2f}s")
        print(f"\n💬 ANSWER:")
        print("-" * 80)
        print(result['answer'])
        print("-" * 80)
        
        return result['answer']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_api(query: str, token: str = None):
    """Test qua API"""
    print("\n" + "=" * 80)
    print("🌐 API TEST")
    print("=" * 80)
    print(f"Query: {query}\n")
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "message": query,
        "conversationId": None
    }
    
    start_time = time.time()
    
    try:
        response = requests.post("http://localhost:3434/api/chat", json=payload, headers=headers)
        elapsed = time.time() - start_time
        
        print(f"✅ Completed in {elapsed:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("statusCode") == 200:
                answer = data.get("data", {}).get("response", "")
                print(f"\n💬 ANSWER:")
                print("-" * 80)
                print(answer)
                print("-" * 80)
                return answer
            else:
                print(f"❌ API Error: {data.get('message')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def compare_answers(direct_answer: str, api_answer: str):
    """So sánh 2 câu trả lời"""
    print("\n" + "=" * 80)
    print("📊 COMPARISON")
    print("=" * 80)
    
    if not direct_answer or not api_answer:
        print("⚠️  Cannot compare - one or both answers are missing")
        return
    
    direct_len = len(direct_answer)
    api_len = len(api_answer)
    
    print(f"\n📏 Length comparison:")
    print(f"  Direct RAG: {direct_len} characters")
    print(f"  API:        {api_len} characters")
    print(f"  Difference: {abs(direct_len - api_len)} characters")
    
    # Check if answers are similar
    direct_words = set(direct_answer.lower().split())
    api_words = set(api_answer.lower().split())
    
    common_words = direct_words.intersection(api_words)
    similarity = len(common_words) / max(len(direct_words), len(api_words)) * 100
    
    print(f"\n📝 Word similarity: {similarity:.1f}%")
    
    if similarity > 80:
        print("✅ Answers are very similar")
    elif similarity > 50:
        print("⚠️  Answers are somewhat similar")
    else:
        print("❌ Answers are quite different")
    
    # Check for common patterns
    print(f"\n🔍 Pattern check:")
    patterns = ["không có thông tin", "không biết", "không tìm thấy", "sorry"]
    
    direct_negative = any(p in direct_answer.lower() for p in patterns)
    api_negative = any(p in api_answer.lower() for p in patterns)
    
    if direct_negative and api_negative:
        print("  ⚠️  Both answers indicate missing information")
    elif api_negative and not direct_negative:
        print("  ❌ API says 'no info' but Direct RAG has answer → PROBLEM!")
    elif not direct_negative and not api_negative:
        print("  ✅ Both answers provide information")
    else:
        print("  ⚠️  Inconsistent - Direct RAG says 'no info' but API has answer")


def main():
    print("🔬 COMPARING DIRECT RAG vs API")
    print("=" * 80)
    print()
    
    # Test query
    query = input("Nhập query để test (Enter = 'Cách tính điểm học phần'): ").strip()
    if not query:
        query = "Cách tính điểm học phần"
    
    print()
    
    # Test direct
    direct_answer = test_direct_rag(query)
    
    # Wait a bit
    time.sleep(1)
    
    # Test API
    token = None
    use_auth = input("\nCần authentication? (y/n, Enter = n): ").lower()
    if use_auth == 'y':
        token = input("Token: ").strip()
    
    api_answer = test_api(query, token)
    
    # Compare
    compare_answers(direct_answer, api_answer)
    
    print("\n" + "=" * 80)
    print("💡 DEBUGGING TIPS")
    print("=" * 80)
    print("""
Nếu API trả lời khác Direct RAG:

1. Kiểm tra server logs:
   - 📊 Retrieved X documents
   - 📝 Context length
   - 📋 Prompt length

2. Nếu context length khác nhau:
   → Vấn đề: Retrieval khác nhau (cache? filter?)

3. Nếu context giống nhưng answer khác:
   → Vấn đề: Prompt khác nhau hoặc LLM inconsistent

4. Nếu API nói "không có thông tin":
   → Kiểm tra prompt có tone tiêu cực không?
   → Thử đổi "Nếu không có thông tin..." thành 
     "Hãy trả lời dựa trên thông tin..."
""")


if __name__ == "__main__":
    main()
