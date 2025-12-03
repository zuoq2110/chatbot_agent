#!/usr/bin/env python3
"""
Migration Script: From Single Graph to Department Graphs
Hướng dẫn và script migration từ hệ thống graph chung sang department graphs
"""
import sys
import os
import shutil
from pathlib import Path

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def backup_old_system():
    """Backup hệ thống cũ trước khi migration"""
    print("📦 BACKUP OLD SYSTEM")
    print("-" * 40)
    
    backup_items = [
        ("document_graph", "document_graph_backup"),
        ("vector_db", "vector_db_backup"),
        ("build_graph.py", "build_graph_old.py")
    ]
    
    for old_path, backup_path in backup_items:
        old_full = os.path.join(project_root, old_path)
        backup_full = os.path.join(project_root, backup_path)
        
        if os.path.exists(old_full):
            if os.path.exists(backup_full):
                print(f"   ⚠️  Backup exists: {backup_path}")
            else:
                try:
                    if os.path.isdir(old_full):
                        shutil.copytree(old_full, backup_full)
                    else:
                        shutil.copy2(old_full, backup_full)
                    print(f"   ✅ Backed up: {old_path} → {backup_path}")
                except Exception as e:
                    print(f"   ❌ Failed to backup {old_path}: {e}")
        else:
            print(f"   ⚠️  Not found: {old_path}")

def check_dependencies():
    """Kiểm tra dependencies cần thiết"""
    print("\n🔍 CHECK DEPENDENCIES")
    print("-" * 40)
    
    required_packages = [
        "python-dotenv",
        "networkx", 
        "python-louvain",
        "scikit-learn",
        "langchain",
        "langchain-core"
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == "python-dotenv":
                import dotenv
            elif package == "networkx":
                import networkx
            elif package == "python-louvain":
                import community
            elif package == "scikit-learn":
                import sklearn
            elif package == "langchain":
                import langchain
            elif package == "langchain-core":
                import langchain_core
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n   📦 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True

def analyze_current_data():
    """Phân tích cấu trúc data hiện tại"""
    print("\n📊 ANALYZE CURRENT DATA")
    print("-" * 40)
    
    data_folder = os.path.join(project_root, "data")
    if not os.path.exists(data_folder):
        print(f"   ❌ Data folder not found: {data_folder}")
        return False
    
    # Count files by department
    dept_counts = {}
    total_files = 0
    
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith('.md'):
                total_files += 1
                rel_path = os.path.relpath(os.path.join(root, file), data_folder)
                
                # Detect department from path
                if 'phongdaotao' in rel_path.lower():
                    dept = 'phongdaotao'
                elif 'phongkhaothi' in rel_path.lower():
                    dept = 'phongkhaothi'
                elif 'khoa' in rel_path.lower():
                    dept = 'khoa'
                elif 'viennghiencuu' in rel_path.lower():
                    dept = 'viennghiencuuvahoptacphattrien'
                elif 'thongtin' in rel_path.lower() or 'hvktmm' in rel_path.lower():
                    dept = 'thongtinhvktmm'
                else:
                    dept = 'common'
                
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    print(f"   📄 Total markdown files: {total_files}")
    print(f"   📁 Files by department:")
    
    for dept, count in sorted(dept_counts.items()):
        percentage = (count / total_files * 100) if total_files > 0 else 0
        print(f"      {dept}: {count} files ({percentage:.1f}%)")
    
    return dept_counts

def migration_plan():
    """Hiển thị migration plan"""
    print("\n🗺️  MIGRATION PLAN")
    print("-" * 40)
    print("Phase 1: Preparation")
    print("   1. ✅ Backup old system")
    print("   2. ✅ Check dependencies")
    print("   3. ✅ Analyze current data")
    print()
    print("Phase 2: Build Department Graphs")
    print("   4. 🔄 Run: python build_department_graphs.py")
    print("   5. 🔄 Verify: department_graphs/ created")
    print()
    print("Phase 3: Update Code")
    print("   6. 🔄 Update imports: DepartmentGraphManager")
    print("   7. 🔄 Update rag_graph.py: use department routing")
    print("   8. 🔄 Update tool.py: department parameter")
    print()
    print("Phase 4: Testing")
    print("   9. 🔄 Test: python test_department_graphs.py")
    print("   10. 🔄 Verify query routing works")
    print("   11. 🔄 Test end-to-end with chatbot")

def generate_test_queries():
    """Tạo test queries cho migration testing"""
    print("\n🧪 TEST QUERIES FOR MIGRATION")
    print("-" * 40)
    
    test_queries = {
        'phongdaotao': [
            "Điều kiện tốt nghiệp đại học là gì?",
            "Quy trình đăng ký học phần như thế nào?", 
            "Học phí các khóa học bao nhiêu?"
        ],
        'phongkhaothi': [
            "Quy định về điểm TOEIC cần để tốt nghiệp",
            "Thủ tục phúc khảo bài thi ra sao?",
            "Quy trình đánh giá chất lượng giáo dục"
        ],
        'khoa': [
            "Chương trình đào tạo ngành ATTT",
            "Các môn học chuyên ngành CNTT",
            "Giáo trình môn An toàn thông tin"
        ],
        'viennghiencuuvahoptacphattrien': [
            "Quy trình đăng ký đề tài nghiên cứu",
            "Tiêu chuẩn công bố khoa học quốc tế",
            "Chính sách hợp tác nghiên cứu"
        ],
        'thongtinhvktmm': [
            "Lịch sử Học viện Kỹ thuật mật mã",
            "Cơ cấu tổ chức của HVKTMM",
            "Thông tin ban giám hiệu"
        ]
    }
    
    for dept, queries in test_queries.items():
        print(f"   🏢 {dept}:")
        for i, query in enumerate(queries, 1):
            print(f"      {i}. {query}")
        print()

def create_migration_checklist():
    """Tạo checklist migration"""
    checklist_content = """# Migration Checklist: Single Graph → Department Graphs

## Pre-Migration
- [ ] ✅ Backup completed (document_graph_backup, vector_db_backup)
- [ ] ✅ Dependencies checked and installed
- [ ] ✅ Data analysis completed
- [ ] 📊 Department distribution analyzed

## Migration Steps
- [ ] 🔄 Run `python build_department_graphs.py`
- [ ] 📁 Verify department_graphs/ folder created
- [ ] 📊 Check all departments have graph.pkl files
- [ ] 🧪 Run `python test_department_graphs.py`

## Code Updates  
- [ ] 🔄 Update imports to use DepartmentGraphManager
- [ ] 🔄 Update rag_graph.py get_retriever() function
- [ ] 🔄 Update agent code to use department routing
- [ ] 🔄 Update tool descriptions

## Testing
- [ ] 🧪 Test department detection from queries
- [ ] 🧪 Test department-specific retrieval
- [ ] 🧪 Test smart query routing
- [ ] 🧪 Test end-to-end chatbot functionality

## Performance Comparison
- [ ] ⏱️  Compare query response times (old vs new)
- [ ] 📊 Compare retrieval accuracy
- [ ] 🎯 Verify reduced noise in results
- [ ] 📈 Monitor memory usage

## Rollback Plan (if needed)
- [ ] 🔄 Restore from backup: document_graph_backup → document_graph
- [ ] 🔄 Revert code changes
- [ ] 🔄 Update imports back to GraphRoutedRetriever
- [ ] ✅ Verify old system works

## Post-Migration
- [ ] 📚 Update documentation
- [ ] 🎓 Train team on new department system
- [ ] 🗑️  Clean up backup files (after verification)
- [ ] 📊 Monitor production performance

## Test Queries Success Criteria
### phongdaotao queries should return:
- [ ] Đào tạo, sinh viên, chương trình học content
- [ ] NO khảo thí or nghiên cứu content

### phongkhaothi queries should return:
- [ ] Khảo thí, điểm số, quy đổi content  
- [ ] NO đào tạo curriculum content

### Cross-department queries should return:
- [ ] Results from multiple relevant departments
- [ ] Proper department attribution in metadata
"""
    
    checklist_path = os.path.join(project_root, "MIGRATION_CHECKLIST.md")
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(checklist_content)
    
    print(f"\n📋 MIGRATION CHECKLIST CREATED")
    print(f"   📄 File: {checklist_path}")
    print("   Use this checklist to track migration progress")

def main():
    """Main migration workflow"""
    print("=" * 80)
    print("🔄 MIGRATION: SINGLE GRAPH → DEPARTMENT GRAPHS")  
    print("=" * 80)
    print()
    print("This script will help you migrate from the old single-graph system")
    print("to the new department-specific graph system.")
    print()
    
    # Phase 1: Preparation
    backup_old_system()
    
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n❌ Please install missing dependencies before continuing")
        return
    
    dept_counts = analyze_current_data()
    if not dept_counts:
        print("\n❌ No data found to migrate")
        return
    
    # Show plan
    migration_plan()
    generate_test_queries() 
    create_migration_checklist()
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION PREPARATION COMPLETE!")
    print("=" * 80)
    print()
    print("🚀 NEXT STEPS:")
    print("1. Review the migration checklist: MIGRATION_CHECKLIST.md")
    print("2. Run: python build_department_graphs.py")
    print("3. Test: python test_department_graphs.py") 
    print("4. Update your code to use DepartmentGraphManager")
    print("5. Verify end-to-end functionality")
    print()
    print("📞 Support: Check DEPARTMENT_GRAPHS_README.md for detailed docs")

if __name__ == "__main__":
    main()