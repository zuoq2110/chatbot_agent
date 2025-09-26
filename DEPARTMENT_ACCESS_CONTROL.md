# Department-Based Access Control System

## Tổng quan

Hệ thống phân quyền theo phòng ban cho phép kiểm soát quyền truy cập nội dung dựa trên vai trò của người dùng:

- **Phòng Đào tạo**: Chỉ được truy cập thông tin liên quan đến đào tạo, học tập
- **Phòng Khảo thí**: Chỉ được truy cập thông tin liên quan đến thi cử, khảo thí  
- **Chung**: Được truy cập tất cả thông tin

## Cách hoạt động

### 1. Backend API Validation

```python
# Trong /api/chat/quick-messages endpoint
user_department = message.department or current_user.get("department")
is_allowed, reason = DepartmentFilterService.validate_query(message.content, user_department)

if not is_allowed:
    raise HTTPException(status_code=403, detail=f"Query not allowed: {reason}")
```

### 2. Department Filter Service

```python
class DepartmentFilterService:
    DEPARTMENT_MAPPINGS = {
        'phongdaotao': {
            'allowed_keywords': ['đào tạo', 'tốt nghiệp', 'học tập', ...],
            'blocked_keywords': ['khảo thí', 'thi', 'kiểm tra', ...],
            'metadata_filter': {'department': 'phongdaotao'}
        },
        'phongkhaothi': {
            'allowed_keywords': ['khảo thí', 'thi', 'kiểm tra', ...],
            'blocked_keywords': ['đào tạo', 'tốt nghiệp', ...],
            'metadata_filter': {'department': 'phongkhaothi'}
        }
    }
```

### 3. Frontend Department Selector

```jsx
// ChatInput component
<div className="flex gap-2">
  <button onClick={() => handleDepartmentChange('chung')}>Tất cả</button>
  <button onClick={() => handleDepartmentChange('phongdaotao')}>Đào tạo</button>  
  <button onClick={() => handleDepartmentChange('phongkhaothi')}>Khảo thí</button>
</div>
```

### 4. RAG System Integration

```python
# Trong RAG tool
def search_kma_regulations(query: str, department: str = None) -> str:
    result = process_kma_query_sync(query, department_filter=department)
    return result['answer']
```

## API Changes

### Models

```python
class MessageQuickChat(BaseModel):
    content: str
    department: Optional[str] = None  # 'phongdaotao', 'phongkhaothi', or None

class MessageCreate(BaseModel):
    content: str
    is_user: bool = True
    department: Optional[str] = None
```

### Endpoints

- `POST /api/chat/quick-messages` - Với department filtering
- `POST /api/chat/{conversation_id}/messages` - Với department filtering

## Frontend Changes

### ChatInput Component

- Thêm department selector UI
- Gửi department parameter kèm message

### Chat Service

```javascript
sendQuickMessage: async (message, department = null) => {
  return await httpClient.post(API_ENDPOINTS.QUICK_CHAT, {
    content: message,
    department: department
  });
}
```

## Test Cases

Chạy test để kiểm tra:

```bash
cd chatbot_agent
python test_department_filter.py
```

### Test Scenarios:

1. **Phòng Đào tạo queries:**
   - ✅ "quy định tốt nghiệp đại học" 
   - ❌ "lịch thi cuối kỳ" (blocked)

2. **Phòng Khảo thí queries:**
   - ✅ "lịch thi cuối kỳ"
   - ❌ "quy định tốt nghiệp đại học" (blocked)

3. **General access:**
   - ✅ Tất cả queries đều được phép

## Deployment

### 1. Backend Restart
```bash
cd chatbot_agent
# Restart API server để load DepartmentFilterService
```

### 2. Frontend Build
```bash
cd chatbot_FE
npm run build
```

### 3. Verification
- Test department selector UI
- Verify API responses với department filtering
- Check error messages cho blocked queries

## Error Handling

### HTTP 403 Forbidden
```json
{
  "detail": "Query not allowed: Query contains restricted content for phongdaotao: 'khảo thí'"
}
```

### Frontend Error Display
```jsx
// Show user-friendly error message
if (response.statusCode === 403) {
  setError("Bạn không có quyền truy cập nội dung này với vai trò hiện tại.");
}
```

## Configuration

### Thêm department keywords:

```python
# Trong DepartmentFilterService.DEPARTMENT_MAPPINGS
'phongdaotao': {
    'allowed_keywords': [
        'đào tạo', 'tốt nghiệp', 'học tập', 'điểm', 'tín chỉ',
        # Thêm keywords mới ở đây
    ]
}
```

### Thêm department mới:

```python
'phongmoi': {
    'allowed_keywords': ['keyword1', 'keyword2'],
    'blocked_keywords': ['blocked1', 'blocked2'],
    'metadata_filter': {'department': 'phongmoi'}
}
```

## Security Notes

1. **Server-side validation**: Tất cả filtering logic ở backend
2. **Department persistence**: Department được lưu trong user session
3. **Metadata filtering**: RAG system chỉ trả về documents phù hợp
4. **Error masking**: Không expose sensitive information trong error messages