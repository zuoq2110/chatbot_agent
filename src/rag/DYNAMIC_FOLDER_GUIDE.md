# Dynamic Folder Management Guide

## Tổng quan

Enhanced RAG system giờ đây **hoàn toàn flexible** với folder structure bất kỳ! Thay vì hardcode metadata mappings, hệ thống sử dụng:

1. **Configuration file** để define metadata mappings
2. **Auto-detection** cho folders chưa được config  
3. **Dynamic query analysis** dựa trên config
4. **Folder management utilities** để dễ dàng thêm folders mới

## 🔧 Cách thêm folders mới

### Method 1: Auto Scan & Configure

```python
from rag.folder_manager import scan_and_suggest, auto_configure

# Scan data directory để tìm folders mới
suggestions = scan_and_suggest("./data")
print(suggestions)

# Auto-configure tất cả folders tìm được
auto_configure("./data", confirm=True)
```

### Method 2: Manual Configuration

```python
from rag.folder_manager import FolderManager

manager = FolderManager()

# Thêm department mới với subfolders
manager.add_new_department(
    folder_name="phongkhcn",
    department_vn="Phòng KHCN", 
    source_type="research",
    subfolders={
        "detai": {
            "research_type": "project",
            "research_type_vn": "đề tài"
        },
        "baibao": {
            "research_type": "publication", 
            "research_type_vn": "bài báo"
        }
    }
)

# Thêm subfolder vào department existing
manager.add_subfolder_to_department(
    department="phongdaotao",
    subfolder_name="lienkethuc",
    subfolder_vn="Liên kết thúc",
    metadata_type="program_type"
)

# Save changes
manager.save_config()
```

### Method 3: Edit JSON Config

Chỉnh sửa trực tiếp file `metadata_config.json`:

```json
{
  "folder_mappings": {
    "your_new_folder": {
      "department": "your_new_folder",
      "department_vn": "Tên Tiếng Việt",
      "source_type": "custom",
      "subfolders": {
        "subfolder1": {
          "custom_type": "subfolder1",
          "custom_type_vn": "Subfolder 1"
        }
      }
    }
  },
  "query_keywords": {
    "departments": {
      "your_new_folder": ["từ khóa 1", "từ khóa 2"]
    }
  }
}
```

## 📁 Supported Folder Structures

Hệ thống support bất kỳ structure nào:

```
data/
├── regulation.txt                    # Auto: department="general"
├── phongdaotao/                     # Configured
│   ├── daihoc/                      # education_level="daihoc"
│   ├── thacsi/                      # education_level="thacsi"  
│   └── new_program/                 # Auto: custom_level="new_program"
├── your_custom_dept/                # Auto-detected
│   ├── type1/                       # Auto: custom_level="type1"
│   └── type2/                       # Auto: custom_level="type2"
└── any_folder_name/                 # Auto-detected với dynamic metadata
    └── any_subfolder/
```

## 🎯 Query Intelligence

System tự động nhận diện queries dựa trên config:

```python
# Configured keywords
"Quy định đại học" → filter: education_level="daihoc"
"Phòng KHCN đề tài" → filter: department="phongkhcn", research_type="project"

# Auto-detected folders
"Your custom dept policy" → filter: department="your_custom_dept"
"New program requirements" → filter: custom_level="new_program"
```

## 🔄 Migration Examples

### Existing Structure
```
data/
├── department_a/
│   ├── level_x/
│   └── level_y/
└── department_b/
    └── level_z/
```

### Auto-Configure
```python
from rag.folder_manager import auto_configure

# Scan và auto-config
auto_configure("./data", confirm=True)

# Kết quả: 
# - department_a → Department_A (department)
# - level_x → Level_X (custom_level)  
# - level_y → Level_Y (custom_level)
# - department_b → Department_B (department)
# - level_z → Level_Z (custom_level)
```

### Custom Configuration
```python
from rag.folder_manager import FolderManager

manager = FolderManager()

# Rename và thêm meaningful metadata
manager.add_new_department(
    "department_a", 
    "Phòng A",
    "administration",
    {
        "level_x": {
            "process_type": "level_x",
            "process_type_vn": "Quy trình X"
        },
        "level_y": {
            "process_type": "level_y", 
            "process_type_vn": "Quy trình Y"
        }
    }
)

manager.save_config()
```

## 🛠️ Utilities

### Check Current Config
```python
from rag.folder_manager import print_config

print_config()
# Output:
# 📊 Current Configuration:
# ==================================================
# 📁 phongdaotao (Phòng Đào Tạo) - Type: education
#   📂 daihoc (đại học)
#   📂 thacsi (thạc sĩ)
# 📁 your_folder (Your Folder) - Type: custom
#   📂 subfolder1 (Subfolder 1)
```

### Scan for New Folders
```python
from rag.folder_manager import scan_and_suggest

suggestions = scan_and_suggest("./data")
# Returns dict with new_folders, missing_subfolders
```

### Backup & Restore
```python
manager = FolderManager()

# Save với backup
manager.save_config(backup=True)  # Tạo .backup file

# Reload config
manager.reload_config()
```

## 📊 Metadata Structure

Dynamic metadata cho mỗi document:

```python
{
    # File info
    'filename': 'document.txt',
    'file_extension': '.txt',
    'source_path': 'dept/subfolder/document.txt',
    'folder_depth': 2,
    
    # Department info (from config hoặc auto-detected)
    'department': 'dept',
    'department_vn': 'Department Name',
    'source_type': 'custom',
    
    # Level info (flexible)
    'education_level': 'daihoc',           # If configured
    'education_level_vn': 'đại học',
    'custom_level': 'subfolder',           # If auto-detected
    'custom_level_vn': 'Subfolder Name',
    'research_type': 'project',            # Custom types
    
    # Chunking info
    'chunk_index': 0,
    'total_chunks': 10
}
```

## 🚀 Performance Benefits

1. **Zero hardcoding**: Hoàn toàn flexible với folder structure
2. **Auto-adaptation**: Tự động adapt với folders mới
3. **Smart filtering**: Query intelligence dựa trên metadata
4. **Easy maintenance**: Config file dễ update
5. **Backup safety**: Auto backup khi save config

## 📋 Best Practices

1. **Luôn backup** trước khi thay đổi config
2. **Sử dụng auto-scan** cho folders structure lớn
3. **Add meaningful Vietnamese names** cho better query recognition
4. **Group similar metadata types** (education_level, research_type, etc.)
5. **Test query keywords** sau khi thêm folders mới

## 🔍 Troubleshooting

### Folder không được nhận diện
```python
# Check current config
print_config()

# Scan for missing folders
suggestions = scan_and_suggest("./data")
print(suggestions)

# Auto-configure missing folders
auto_configure("./data", confirm=True)
```

### Query không filter đúng
```python
# Check query keywords trong config
config = get_metadata_config()
keywords = config.get_query_keywords()
print(keywords)

# Add more keywords
manager = FolderManager()
manager.config.add_query_keywords("departments", "your_dept", ["keyword1", "keyword2"])
manager.save_config()
```

### Reset về default
```python
# Delete config file để use default
import os
config_path = "src/rag/metadata_config.json"
if os.path.exists(config_path):
    os.remove(config_path)

# Reload sẽ dùng default config
from rag.metadata_config import reload_metadata_config
reload_metadata_config()
```

Với hệ thống này, bạn có thể thêm **bất kỳ folder structure nào** mà không cần modify code! 🎉