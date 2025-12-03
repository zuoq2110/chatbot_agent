#!/usr/bin/env python3
"""
Test Department Graph Manager
Kiểm tra hoạt động của hệ thống graph riêng theo phòng ban
"""
import sys
import os

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from graph_rag.department_graph_manager import DepartmentGraphManager

def test_department_detection():
    """Test xác định phòng ban từ path và query"""
    print("=" * 60)
    print("🧪 TESTING DEPARTMENT DETECTION")
    print("=" * 60)
    
    manager = DepartmentGraphManager()
    
    # Test path detection
    test_paths = [
        "D:\\KMA_ChatBot_Frontend_System\\chatbot_agent\\data\\phongdaotao\\daihoc\\file.md",
        "D:\\KMA_ChatBot_Frontend_System\\chatbot_agent\\data\\phongkhaothi\\quy_dinh.md",
        "D:\\KMA_ChatBot_Frontend_System\\chatbot_agent\\data\\khoa\\attt\\chuong_trinh.md",
        "D:\\KMA_ChatBot_Frontend_System\\chatbot_agent\\data\\viennghiencuuvahoptacphattrien\\quy_che.md",
        "D:\\KMA_ChatBot_Frontend_System\\chatbot_agent\\data\\Giao trinh _ Phần mềm mã nguồn mở.md"
    ]
    
    print("\n📁 Path → Department detection:")
    for path in test_paths:
        dept = manager.detect_department_from_path(path)
        print(f"   {os.path.basename(path)} → {dept}")
    
    # Test query detection
    test_queries = [
        "Quy định về điểm TOEIC cần thiết để tốt nghiệp",
        "Chương trình đào tạo ngành An toàn thông tin",
        "Quy trình đánh giá chất lượng giáo dục",
        "Quy chế nghiên cứu khoa học tại học viện",
        "Giới thiệu về Học viện Kỹ thuật mật mã",
        "Làm thế nào để nộp luận văn thạc sĩ?"
    ]
    
    print("\n🔍 Query → Department detection:")
    for query in test_queries:
        depts = manager.detect_department_from_query(query, top_k=3)
        print(f"   '{query[:50]}...' → {depts}")

def test_graph_loading_and_querying():
    """Test load graphs và query"""
    print("\n" + "=" * 60)
    print("🔍 TESTING GRAPH LOADING & QUERYING")
    print("=" * 60)
    
    output_folder = os.path.join(project_root, "department_graphs")
    
    if not os.path.exists(output_folder):
        print(f"❌ Department graphs folder not found: {output_folder}")
        print("   Please run 'python build_department_graphs.py' first")
        return
    
    # Load graphs
    manager = DepartmentGraphManager(output_folder)
    success = manager.load_department_graphs()
    
    if not success:
        print("❌ Failed to load department graphs")
        return
    
    print("✅ Successfully loaded department graphs")
    
    # Show available departments
    departments = manager.list_available_departments()
    print(f"\n📊 Available departments: {departments}")
    
    # Show statistics
    stats = manager.get_department_stats()
    print(f"\n📈 Department statistics:")
    for dept, stat in stats.items():
        print(f"   {dept}: {stat['nodes']} nodes, {stat['edges']} edges, {stat['communities']} communities")
    
    # Test queries for each department
    test_cases = [
        {
            'query': "Quy định về điểm TOEIC cần thiết để tốt nghiệp",
            'expected_dept': 'phongkhaothi',
            'description': 'Câu hỏi về quy đổi điểm tiếng Anh'
        },
        {
            'query': "Chương trình đào tạo ngành ATTT",
            'expected_dept': 'phongdaotao',
            'description': 'Câu hỏi về chương trình đào tạo'
        },
        {
            'query': "Quy trình nghiên cứu khoa học",
            'expected_dept': 'viennghiencuuvahoptacphattrien',
            'description': 'Câu hỏi về nghiên cứu khoa học'
        },
        {
            'query': "Giới thiệu về Học viện Kỹ thuật mật mã",
            'expected_dept': 'thongtinhvktmm', 
            'description': 'Câu hỏi về thông tin học viện'
        }
    ]
    
    print(f"\n🧪 Testing queries:")
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Query: '{case['query']}'")
        print(f"   Expected dept: {case['expected_dept']}")
        
        # Test department detection
        detected_depts = manager.detect_department_from_query(case['query'], top_k=2)
        print(f"   Detected depts: {detected_depts}")
        
        # Test smart query
        results = manager.query_smart(case['query'], k=3)
        print(f"   Smart query results: {len(results)} documents")
        
        for j, doc in enumerate(results):
            source = os.path.basename(doc.metadata.get('source', 'unknown'))
            dept = doc.metadata.get('query_department', 'unknown')
            score = doc.metadata.get('combined_score', 0)
            print(f"      {j+1}. [{dept}] {source} (score: {score:.3f})")
        
        # Test specific department query
        if case['expected_dept'] in departments:
            dept_results = manager.query_department(case['query'], case['expected_dept'], k=2)
            print(f"   Specific {case['expected_dept']} query: {len(dept_results)} documents")
            for j, doc in enumerate(dept_results):
                source = os.path.basename(doc.metadata.get('source', 'unknown'))
                score = doc.metadata.get('combined_score', 0)
                print(f"      {j+1}. {source} (score: {score:.3f})")

def main():
    """Main test function"""
    print("🧪 DEPARTMENT GRAPH MANAGER TESTS")
    print("Testing hệ thống graph riêng biệt cho từng phòng ban")
    
    # Test 1: Department detection
    test_department_detection()
    
    # Test 2: Graph loading and querying
    test_graph_loading_and_querying()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()