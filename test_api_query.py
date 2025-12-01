"""
Test API query để so sánh với test file
"""
import requests
import json
import time

# API endpoint
API_URL = "http://localhost:3434/api/chat"

# Test queries
QUERIES = [
    "Cách tính điểm học phần",
    "Tôi được 7.0 IELTS thì điểm quy đổi là bao nhiêu?",
    "Điều kiện để được thi lại",
]

def test_query(query: str, token: str = None):
    """Test a single query"""
    print("=" * 80)
    print(f"📝 Query: {query}")
    print("=" * 80)
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "message": query,
        "conversationId": None
    }
    
    print(f"🔄 Sending request to {API_URL}...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        elapsed_time = time.time() - start_time
        
        print(f"✅ Response received in {elapsed_time:.2f}s")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("statusCode") == 200:
                answer = data.get("data", {}).get("response", "")
                print(f"\n💬 ANSWER:")
                print("-" * 80)
                print(answer)
                print("-" * 80)
                
                # Show metadata if available
                metadata = data.get("data", {})
                if "tokensUsed" in metadata:
                    print(f"\n📊 Tokens used: {metadata['tokensUsed']}")
                if "conversationId" in metadata:
                    print(f"🆔 Conversation ID: {metadata['conversationId']}")
            else:
                print(f"\n❌ API Error: {data.get('message')}")
                print(f"Full response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Không thể kết nối đến {API_URL}")
        print("Kiểm tra xem server có đang chạy không (uvicorn src.backend.main:app --port 3434)")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n")


def main():
    print("🚀 TESTING API QUERIES")
    print("=" * 80)
    print(f"API Endpoint: {API_URL}")
    print("=" * 80)
    print()
    
    # Get token if needed (optional)
    token = None
    use_auth = input("Bạn có cần dùng authentication token? (y/n): ").lower()
    if use_auth == 'y':
        token = input("Nhập token: ").strip()
        print()
    
    # Test each query
    for i, query in enumerate(QUERIES, 1):
        print(f"\n🔍 TEST {i}/{len(QUERIES)}")
        test_query(query, token)
        
        if i < len(QUERIES):
            # Wait a bit between requests
            time.sleep(2)
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
    print("\n💡 Tips:")
    print("- Kiểm tra logs server để thấy:")
    print("  📊 Retrieved X documents")
    print("  📄 First doc preview")
    print("  📝 Context length")
    print("  📋 Prompt length")
    print("\n- So sánh với kết quả test_graph_rag_with_llm.py")


if __name__ == "__main__":
    main()
