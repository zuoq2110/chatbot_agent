# Hướng dẫn sử dụng API Backend

## 🚀 Khởi động Backend

### Cách 1: Sử dụng script có sẵn
```bash
# Từ thư mục gốc dự án
./start_backend.bat
```

### Cách 2: Khởi động thủ công
```bash
# Chuyển đến thư mục src
cd d:/KMA_ChatBot_Frontend_System/chatbot_agent/src

# Khởi động FastAPI server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 Danh sách API có sẵn

### 🔐 User API (Authentication)

#### 1. Đăng ký người dùng
- **URL**: `POST /api/users`
- **Mô tả**: Tạo tài khoản người dùng mới
- **Body**:
```json
{
    "student_code": "CT030101",
    "student_name": "Nguyễn Văn A",
    "student_class": "CT301",
    "password_hash": "hashed_password",
    "salt": "random_salt"
}
```

#### 2. Lấy thông tin người dùng (Login)
- **URL**: `GET /api/users/{student_code}`
- **Mô tả**: Lấy thông tin user để đăng nhập
- **Response**: Trả về thông tin user bao gồm password_hash và salt

### 💬 Chat API

#### 3. Lấy tất cả cuộc hội thoại
- **URL**: `GET /api/chat/conversations/all`
- **Mô tả**: Lấy danh sách tất cả cuộc hội thoại

#### 4. Lấy cuộc hội thoại của user
- **URL**: `GET /api/chat/conversations?student_code={student_code}`
- **Mô tả**: Lấy danh sách cuộc hội thoại của một user cụ thể

#### 5. Tạo cuộc hội thoại mới
- **URL**: `POST /api/chat/conversations`
- **Body**:
```json
{
    "student_code": "CT030101",
    "title": "Hỏi về môn học"
}
```

#### 6. Cập nhật cuộc hội thoại
- **URL**: `PUT /api/chat/conversations/{conversation_id}`
- **Body**:
```json
{
    "title": "Tiêu đề mới",
    "is_active": true
}
```

#### 7. Xóa cuộc hội thoại
- **URL**: `DELETE /api/chat/conversations/{conversation_id}`

#### 8. Lấy tin nhắn trong cuộc hội thoại
- **URL**: `GET /api/chat/messages/{conversation_id}`
- **Mô tả**: Lấy tất cả tin nhắn trong một cuộc hội thoại

#### 9. Gửi tin nhắn mới
- **URL**: `POST /api/chat/{conversation_id}/messages`
- **Body**:
```json
{
    "content": "Xin chào, tôi muốn hỏi về..."
}
```

#### 10. Chat nhanh (không cần conversation)
- **URL**: `POST /api/chat/quick-messages`
- **Body**:
```json
{
    "message": "Câu hỏi của tôi",
    "student_code": "CT030101"
}
```

## 🔗 Health Check
- **URL**: `GET /health`
- **Mô tả**: Kiểm tra trạng thái server

## 📖 API Documentation
Sau khi khởi động backend, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Cách sử dụng trong code Python

```python
import requests
import json

# Base URL
API_BASE = "http://localhost:8000"

# 1. Đăng ký user
def register_user(student_code, student_name, student_class, password_hash, salt):
    url = f"{API_BASE}/api/users"
    data = {
        "student_code": student_code,
        "student_name": student_name,
        "student_class": student_class,
        "password_hash": password_hash,
        "salt": salt
    }
    response = requests.post(url, json=data)
    return response.json()

# 2. Lấy thông tin user
def get_user(student_code):
    url = f"{API_BASE}/api/users/{student_code}"
    response = requests.get(url)
    return response.json()

# 3. Tạo cuộc hội thoại
def create_conversation(student_code, title):
    url = f"{API_BASE}/api/chat/conversations"
    data = {
        "student_code": student_code,
        "title": title
    }
    response = requests.post(url, json=data)
    return response.json()

# 4. Gửi tin nhắn
def send_message(conversation_id, content):
    url = f"{API_BASE}/api/chat/{conversation_id}/messages"
    data = {
        "content": content
    }
    response = requests.post(url, json=data)
    return response.json()

# 5. Chat nhanh
def quick_chat(message, student_code):
    url = f"{API_BASE}/api/chat/quick-messages"
    data = {
        "message": message,
        "student_code": student_code
    }
    response = requests.post(url, json=data)
    return response.json()
```

## 🔧 Troubleshooting

### Lỗi Connection Refused
- Đảm bảo backend đang chạy trên port 8000
- Kiểm tra MongoDB đang chạy trên port 27017

### Kiểm tra MongoDB
```bash
# Khởi động MongoDB (nếu cần)
mongod --dbpath="C:\data\db"
```

### Kiểm tra Backend
```bash
# Test health endpoint
curl http://localhost:8000/health
```
