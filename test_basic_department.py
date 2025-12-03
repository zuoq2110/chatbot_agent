#!/usr/bin/env python3
"""
Simple test for department graph manager
Kiểm tra import và cấu trúc cơ bản
"""
import sys
import os

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print("🧪 Testing Department Graph Manager Import")
print("=" * 60)

try:
    print("1. Testing basic imports...")
    from graph_rag.department_graph_manager import DepartmentGraphManager
    print("   ✅ DepartmentGraphManager imported successfully")
    
    print("2. Testing manager creation...")
    output_dir = os.path.join(project_root, "test_department_graphs")
    manager = DepartmentGraphManager(output_dir)
    print("   ✅ Manager created successfully")
    
    print("3. Testing path detection...")
    test_paths = [
        "data/phongdaotao/daihoc/file.md",
        "data/phongkhaothi/quy_dinh.md",
        "data/khoa/attt/chuong_trinh.md",
        "data/Giao trinh _ Phần mềm mã nguồn mở.md"
    ]
    
    for path in test_paths:
        dept = manager.detect_department_from_path(path)
        print(f"   📁 {path} → {dept}")
    
    print("4. Testing query detection...")
    test_queries = [
        "Quy định về điểm TOEIC cần thiết để tốt nghiệp",
        "Chương trình đào tạo ngành ATTT",
        "Quy trình nghiên cứu khoa học"
    ]
    
    for query in test_queries:
        depts = manager.detect_department_from_query(query, top_k=2)
        print(f"   🔍 '{query}' → {depts}")
    
    print("\n✅ ALL BASIC TESTS PASSED!")
    print("DepartmentGraphManager is ready to use")
    
except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    print("Full traceback:")
    print(traceback.format_exc())