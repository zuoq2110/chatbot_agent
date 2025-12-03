# Department-Specific Graph RAG System

## Tổng quan

Hệ thống mới xây dựng **graph riêng biệt cho từng phòng ban** thay vì sử dụng 1 graph chung. Điều này có những lợi ích:

1. **Tránh nhiễu thông tin**: User chỉ tìm kiếm trong phòng ban liên quan
2. **Tăng độ chính xác**: Kết quả tập trung vào domain cụ thể  
3. **Tốc độ nhanh hơn**: Graph nhỏ hơn, tìm kiếm nhanh hơn
4. **Dễ bảo trì**: Mỗi phòng ban quản lý data riêng

## Cấu trúc Phòng ban

### Phòng ban được hỗ trợ:
- `phongdaotao`: Phòng Đào tạo (đại học, thạc sĩ, tiến sĩ, chương trình học)
- `phongkhaothi`: Phòng Khảo thí & Đảm bảo chất lượng (quy định thi, đánh giá, quy đổi điểm)
- `khoa`: Các khoa (ATTT, CNTT, DTVT, chuyên ngành)
- `viennghiencuuvahoptacphattrien`: Viện Nghiên cứu (khoa học, đề tài, hợp tác)
- `thongtinhvktmm`: Thông tin Học viện (giới thiệu, lịch sử, tổ chức)
- `common`: Tài liệu chung (giáo trình, tài liệu không phân loại)

## Cách hoạt động

### 1. Department Detection (Tự động xác định phòng ban)

#### Từ đường dẫn file:
```python
manager = DepartmentGraphManager()

# Từ đường dẫn
dept = manager.detect_department_from_path("data/phongdaotao/daihoc/quy_che.md")
# Output: "phongdaotao"
```

#### Từ nội dung query:
```python
# Từ từ khóa trong câu hỏi
depts = manager.detect_department_from_query("Quy định về điểm TOEIC cần để tốt nghiệp")
# Output: ["phongkhaothi", "phongdaotao"]
```

### 2. Query Modes (Các chế độ truy vấn)

#### Smart Query (Tự động):
```python
# Tự động xác định phòng ban và tìm kiếm
results = manager.query_smart("Điều kiện tốt nghiệp là gì?", k=5)
```

#### Department-Specific Query:
```python
# Tìm kiếm trong phòng ban cụ thể
results = manager.query_department("Quy trình phúc khảo", "phongkhaothi", k=3)
```

#### Multi-Department Query:
```python
# Tìm kiếm trong nhiều phòng ban
results = manager.query_multi_department("Quy chế đào tạo", ["phongdaotao", "phongkhaothi"], k=6)
```

## Setup và Sử dụng

### 1. Xây dựng Department Graphs

```bash
# Cài đặt dependencies
pip install python-dotenv networkx python-louvain scikit-learn

# Xây dựng graphs (cần LLM/embedding model)
python build_department_graphs.py
```

### 2. Sử dụng trong Code

```python
from graph_rag import DepartmentGraphManager

# Khởi tạo manager
manager = DepartmentGraphManager("department_graphs")

# Load graphs đã xây dựng
success = manager.load_department_graphs()

if success:
    # Query thông minh
    results = manager.query_smart("Học phí đại học bao nhiêu?", k=4)
    
    for doc in results:
        print(f"[{doc.metadata.get('query_department')}] {doc.page_content[:200]}")
```

### 3. Tích hợp với RAG Tool

Tool `search_kma_regulations` đã được cập nhật để sử dụng department graphs:

```python
# Tool call với department filter
result = search_kma_regulations.invoke({
    "query": "Quy định về khảo thí", 
    "department": "phongkhaothi"  # Optional
})

# Tool call với auto-detection 
result = search_kma_regulations.invoke({
    "query": "Thủ tục tốt nghiệp như thế nào?"
    # department tự động được xác định là "phongdaotao"
})
```

## Keywords Mapping

### Phòng Đào tạo (`phongdaotao`):
- **Keywords**: đào tạo, học tập, sinh viên, giảng viên, khóa học, chương trình, đại học, thạc sĩ, tiến sĩ, tốt nghiệp, học phí, tuyển sinh

### Phòng Khảo thí (`phongkhaothi`):
- **Keywords**: khảo thí, thi, kiểm tra, đánh giá, chất lượng, điểm, quy đổi điểm, TOEIC, IELTS, TOEFL, Cambridge, tiếng Anh

### Khoa (`khoa`):
- **Keywords**: khoa, ngành, chuyên ngành, ATTT, CNTT, DTVT, an toàn thông tin, công nghệ thông tin, điện tử viễn thông

### Viện Nghiên cứu (`viennghiencuuvahoptacphattrien`):
- **Keywords**: nghiên cứu, khoa học, hợp tác, phát triển, đề tài, dự án, công bố, tạp chí, hội thảo

### Thông tin Học viện (`thongtinhvktmm`):
- **Keywords**: học viện, HVKTMM, cơ yếu, chuyển đổi số, sáng kiến, giới thiệu, lịch sử, tổ chức

## Cấu trúc Files

```
chatbot_agent/
├── department_graphs/           # Graphs cho từng phòng ban
│   ├── phongdaotao/
│   │   └── graph.pkl
│   ├── phongkhaothi/
│   │   └── graph.pkl
│   └── ...
├── src/graph_rag/
│   ├── department_graph_manager.py  # Class chính
│   └── ...
├── build_department_graphs.py      # Script xây dựng graphs
└── test_department_graphs.py       # Script test
```

## Ưu điểm so với Graph chung

| Aspect | Graph chung | Department Graphs |
|--------|-------------|------------------|
| **Độ chính xác** | Medium | High ⭐ |
| **Tốc độ** | Slow | Fast ⭐ |
| **Nhiễu thông tin** | High | Low ⭐ |
| **Maintenance** | Hard | Easy ⭐ |
| **Scalability** | Limited | Good ⭐ |

## Migration từ hệ thống cũ

1. **Backup** graph cũ: `mv document_graph document_graph_backup`
2. **Build** department graphs: `python build_department_graphs.py`  
3. **Update** code sử dụng `DepartmentGraphManager` thay vì `GraphRoutedRetriever`
4. **Test** với queries thường dùng

## Troubleshooting

### Graph không load được:
```bash
# Kiểm tra files
ls -la department_graphs/*/graph.pkl

# Rebuild nếu cần
python build_department_graphs.py
```

### Department detection sai:
- Kiểm tra keywords trong `department_keywords` (file department_graph_manager.py)
- Thêm từ khóa mới nếu cần

### Performance chậm:
- Giảm `k` (số documents trả về)
- Kiểm tra graph size: `manager.get_department_stats()`

## Logs & Monitoring

Hệ thống ghi log chi tiết cho debugging:

```
🔍 Smart query: 'Điều kiện tốt nghiệp là gì?'
🎯 Detected departments: ['phongdaotao']
📁 Searching in phongdaotao: 3 documents found
✅ Query completed: 3 results
```

Log levels:
- `INFO`: Workflow thông thường
- `WARNING`: Department không tìm thấy, fallback
- `ERROR`: Graph lỗi, cần rebuild