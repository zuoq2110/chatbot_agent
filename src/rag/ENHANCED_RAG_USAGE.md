# Enhanced RAG System với Metadata Filtering

## Tổng quan

Enhanced RAG system sử dụng **single index + metadata** để cải thiện độ chính xác của chatbot bằng cách:

1. **Metadata-based filtering**: Lọc documents theo department, education level, source type
2. **Smart query analysis**: Tự động phân tích query để áp dụng filters phù hợp  
3. **Better chunking**: Preserved context với larger chunks và metadata
4. **Intelligent routing**: Định tuyến query đến đúng loại documents

## Ví dụ sử dụng

### 1. Migration từ hệ thống cũ

```python
# Cũ: Sử dụng basic retriever
from rag.retriever import create_hybrid_retriever

retriever, documents = create_hybrid_retriever("./vector_db", "./data")
results = retriever._get_relevant_documents("quy định đại học")

# Mới: Sử dụng enhanced retriever với metadata
from rag.retriever import create_enhanced_hybrid_retriever, smart_retrieve

enhanced_retriever, documents = create_enhanced_hybrid_retriever("./vector_db", "./data")
results = smart_retrieve(enhanced_retriever, "quy định đại học", use_smart_filtering=True)
```

### 2. Smart Query Filtering

```python
from rag.retriever import (
    create_enhanced_hybrid_retriever, 
    smart_retrieve,
    analyze_query_for_metadata_filter
)

# Tạo enhanced retriever
retriever, docs = create_enhanced_hybrid_retriever("./vector_db", "./data")

# Ví dụ các query sẽ được tự động filter:

# Query về đại học -> tự động filter education_level='daihoc'
query1 = "Quy định tốt nghiệp đại học"
results1 = smart_retrieve(retriever, query1)

# Query về thạc sĩ -> tự động filter education_level='thacsi' 
query2 = "Điều kiện nhập học cao học"
results2 = smart_retrieve(retriever, query2)

# Query về phòng đào tạo -> tự động filter department='phongdaotao'
query3 = "Quy trình xét tốt nghiệp phòng đào tạo"
results3 = smart_retrieve(retriever, query3)

# Query general -> không filter
query4 = "Thông tin chung về học viện"
results4 = smart_retrieve(retriever, query4)
```

### 3. Manual Filtering

```python
# Filter theo education level
metadata_filter = {'education_level': 'daihoc'}
results = retriever._get_relevant_documents(
    "quy định học tập", 
    metadata_filter=metadata_filter
)

# Filter theo department
metadata_filter = {'department': 'vanphong'}
results = retriever._get_relevant_documents(
    "quy trình hành chính", 
    metadata_filter=metadata_filter
)

# Multiple filters
metadata_filter = {
    'department': 'phongdaotao',
    'education_level': 'thacsi'
}
results = retriever._get_relevant_documents(
    "luận văn thạc sĩ", 
    metadata_filter=metadata_filter
)
```

## Metadata Structure

Mỗi document chunk được thêm các metadata sau:

```python
{
    'filename': 'quy-che-dao-tao.txt',
    'file_extension': '.txt', 
    'department': 'phongdaotao',  # phongdaotao | vanphong | general
    'source_type': 'education',   # education | administration | regulation
    'education_level': 'daihoc',  # daihoc | thacsi | tiensi | giangvien
    'education_level_vn': 'đại học',
    'source_path': 'phongdaotao/daihoc/quy-che-dao-tao.txt',
    'chunk_index': 0,
    'total_chunks': 15
}
```

## Cấu trúc thư mục được hỗ trợ

```
data/
├── regulation.txt                    # department='general'
├── phongdaotao/                     # department='phongdaotao' 
│   ├── daihoc/                      # education_level='daihoc'
│   │   └── quy-che-dao-tao.txt
│   ├── thacsi/                      # education_level='thacsi'
│   │   └── quy-che-cao-hoc.txt
│   ├── tiensi/                      # education_level='tiensi'
│   │   └── quy-che-nghien-cuu.txt
│   └── giangvien/                   # education_level='giangvien'
│       └── quy-che-giang-vien.txt
└── vanphong/                        # department='vanphong'
    └── quy-che-lam-viec.txt
```

## Query Pattern Recognition

Enhanced system tự động nhận diện các từ khóa:

### Education Levels:
- **Đại học**: 'đại học', 'sinh viên', 'cử nhân'
- **Thạc sĩ**: 'thạc sĩ', 'cao học'  
- **Tiến sĩ**: 'tiến sĩ', 'nghiên cứu sinh'
- **Giảng viên**: 'giảng viên', 'giáo viên'

### Departments:
- **Phòng đào tạo**: 'phòng đào tạo', 'đào tạo'
- **Văn phòng**: 'văn phòng', 'hành chính'

## Performance Benefits

1. **Reduced noise**: Lọc bỏ irrelevant documents từ other departments
2. **Better context**: Larger chunks (500 vs 400) with preserved structure
3. **Intelligent routing**: Automatic filtering giảm search space
4. **Metadata preservation**: Context headers help LLM understand source

## Backward Compatibility

Hệ thống mới vẫn hỗ trợ các functions cũ:

```python
# Old functions vẫn hoạt động
from rag.retriever import create_hybrid_retriever, load_vector_database

# Nhưng nên sử dụng enhanced versions
from rag.retriever import (
    create_enhanced_hybrid_retriever,
    load_enhanced_vector_database, 
    smart_retrieve
)
```

## Testing the Enhanced System

```python
# Test script để so sánh performance
def test_enhanced_vs_basic():
    # Basic retriever
    basic_retriever, _ = create_hybrid_retriever("./vector_db", "./data")
    basic_results = basic_retriever._get_relevant_documents("quy định đại học")
    
    # Enhanced retriever  
    enhanced_retriever, _ = create_enhanced_hybrid_retriever("./vector_db", "./data")
    enhanced_results = smart_retrieve(enhanced_retriever, "quy định đại học")
    
    print(f"Basic results: {len(basic_results)} documents")
    print(f"Enhanced results: {len(enhanced_results)} documents")
    
    # Check metadata
    for doc in enhanced_results[:3]:
        print(f"Department: {doc.metadata.get('department')}")
        print(f"Education Level: {doc.metadata.get('education_level_vn')}")
        print(f"Source: {doc.metadata.get('source_path')}")
        print("---")
```