#!/usr/bin/env python3
"""
Script để kiểm tra metadata của các chunk trong vector database
"""
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from rag.retriever import load_enhanced_vector_database
from pprint import pprint

def check_chunk_metadata():
    """Kiểm tra metadata của các chunk"""
    
    print("🔍 KIỂM TRA METADATA CỦA CÁC CHUNK")
    print("="*60)
    
    try:
        # Load vector database
        vector_db_path = "./vector_db"
        data_dir = "./data"
        
        vectorstore, documents = load_enhanced_vector_database(vector_db_path, data_dir)
        
        print(f"📊 Tổng số documents: {len(documents)}")
        print("="*60)
        
        # Phân loại documents theo department
        dept_counts = {}
        phongkhaothi_docs = []
        
        for i, doc in enumerate(documents):
            metadata = doc.metadata
            dept = metadata.get('department', 'unknown')
            
            if dept not in dept_counts:
                dept_counts[dept] = 0
            dept_counts[dept] += 1
            
            # Lưu documents của phòng khảo thí
            if dept == 'phongkhaothi':
                phongkhaothi_docs.append((i, doc))
        
        # Hiển thị thống kê theo phòng ban
        print("📈 THỐNG KÊ THEO PHÒNG BAN:")
        for dept, count in dept_counts.items():
            dept_vn = "Không xác định" if dept == 'unknown' else dept
            if dept == 'phongkhaothi':
                dept_vn = "Phòng Khảo thí"
            elif dept == 'phongdaotao':
                dept_vn = "Phòng Đào tạo"
            elif dept == 'vanphong':
                dept_vn = "Văn phòng"
            print(f"   {dept_vn}: {count} chunks")
        
        print("\n" + "="*60)
        print(f"🎯 KIỂM TRA CỤ THỂ PHÒNG KHẢO THÍ ({len(phongkhaothi_docs)} chunks)")
        print("="*60)
        
        if not phongkhaothi_docs:
            print("❌ KHÔNG TÌM THẤY CHUNK NÀO CỦA PHÒNG KHẢO THÍ!")
            print("   Có thể vector database chưa được rebuild sau khi cập nhật config")
            return
        
        # Hiển thị chi tiết 5 chunk đầu tiên của phòng khảo thí
        for idx, (doc_idx, doc) in enumerate(phongkhaothi_docs[:5]):
            print(f"\n📄 CHUNK {idx+1}/{len(phongkhaothi_docs)} (Document index: {doc_idx})")
            print("-" * 40)
            print("METADATA:")
            for key, value in doc.metadata.items():
                print(f"   {key}: {value}")
            
            print("\nNỘI DUNG (100 ký tự đầu):")
            content_preview = doc.page_content[:100].replace('\n', ' ')
            print(f"   {content_preview}...")
            print("-" * 40)
        
        # Tìm chunk có chứa thông tin về hội đồng đảm bảo chất lượng
        print(f"\n🔎 TÌM CHUNK CHỨA THÔNG TIN VỀ HỘI ĐỒNG")
        print("="*60)
        
        council_chunks = []
        search_keywords = ['hội đồng', 'thành viên', 'chất lượng', 'hoàng văn thức']
        
        for i, doc in enumerate(documents):
            content_lower = doc.page_content.lower()
            if any(keyword in content_lower for keyword in search_keywords):
                if doc.metadata.get('department') == 'phongkhaothi':
                    council_chunks.append((i, doc))
        
        print(f"📋 Tìm thấy {len(council_chunks)} chunks có thông tin hội đồng từ phòng khảo thí")
        
        for idx, (doc_idx, doc) in enumerate(council_chunks[:3]):
            print(f"\n🎯 HỘI ĐỒNG CHUNK {idx+1}/{len(council_chunks)}")
            print("-" * 40)
            print("METADATA:")
            pprint(doc.metadata, width=60)
            
            print("\nNỘI DUNG:")
            lines = doc.page_content.split('\n')
            for line_idx, line in enumerate(lines[:10]):  # Hiển thị 10 dòng đầu
                if line.strip():
                    print(f"   {line}")
                if line_idx >= 10:
                    print("   [...]")
                    break
            print("-" * 40)
        
        if not council_chunks:
            print("❌ KHÔNG TÌM THẤY CHUNK NÀO CHỨA THÔNG TIN HỘI ĐỒNG TỪ PHÒNG KHẢO THÍ!")
            
            # Kiểm tra xem có chunk nào chứa thông tin hội đồng từ phòng khác không
            other_council_chunks = []
            for i, doc in enumerate(documents):
                content_lower = doc.page_content.lower()
                if any(keyword in content_lower for keyword in search_keywords):
                    other_council_chunks.append((i, doc))
            
            if other_council_chunks:
                print(f"\n⚠️  Tìm thấy {len(other_council_chunks)} chunks có thông tin hội đồng từ các nguồn khác:")
                for idx, (doc_idx, doc) in enumerate(other_council_chunks[:3]):
                    print(f"   Chunk {doc_idx}: department='{doc.metadata.get('department', 'unknown')}', source_path='{doc.metadata.get('source_path', 'unknown')}'")
        
    except Exception as e:
        print(f"❌ LỖI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_chunk_metadata()