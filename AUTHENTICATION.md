# 🔐 Hệ thống Đăng ký & Đăng nhập KMA ChatBot

## Tổng quan

Hệ thống authentication hoàn chỉnh cho KMA ChatBot với các tính năng:

- ✅ Đăng ký tài khoản mới
- ✅ Đăng nhập bảo mật
- ✅ Quản lý phiên đăng nhập
- ✅ Hash mật khẩu an toàn
- ✅ Giao diện người dùng thân thiện
- ✅ Tích hợp với MongoDB

## Cấu trúc Files

```
src/streamlit_ui/
├── auth.py           # Lớp AuthManager chính
├── login_page.py     # Trang đăng nhập độc lập
├── chat_ui.py        # Giao diện chat (đã cập nhật)
├── appbar.py         # App bar với thông tin user
└── streamlit_app.py  # App chính

src/backend/
├── models/user.py    # Models cho User (đã cập nhật)
└── api/user.py       # API endpoints (đã cập nhật)
```

## Cách sử dụng

### 1. Khởi động hệ thống

```bash
# Sử dụng script tự động
./run.bat

# Hoặc chạy thủ công
# Backend (Terminal 1)
cd src
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (Terminal 2)
cd src/streamlit_ui
streamlit run streamlit_app.py --server.port 8501
```

### 2. Truy cập ứng dụng

- **App chính**: http://localhost:8501
- **Trang đăng nhập riêng**: http://localhost:8502 (tùy chọn)
- **Backend API**: http://localhost:8000

### 3. Đăng ký tài khoản mới

1. Truy cập ứng dụng
2. Chọn tab "Đăng ký"
3. Nhập thông tin:
   - Mã sinh viên (ví dụ: CT030101)
   - Họ và tên đầy đủ
   - Lớp (ví dụ: CT301)
   - Mật khẩu (tối thiểu 6 ký tự)
   - Xác nhận mật khẩu
4. Nhấn "Đăng ký"

### 4. Đăng nhập

1. Chọn tab "Đăng nhập"
2. Nhập mã sinh viên và mật khẩu
3. Nhấn "Đăng nhập"

## Tính năng bảo mật

### Hash mật khẩu
- Sử dụng `PBKDF2` với SHA-256
- 100,000 iterations
- Salt ngẫu nhiên cho mỗi mật khẩu
- So sánh timing-safe với `hmac.compare_digest`

### Quản lý phiên
- Session được lưu trong `st.session_state`
- Thông tin session bao gồm:
  - student_code
  - student_name
  - student_class
  - login_time

### Validation
- Kiểm tra độ dài mật khẩu
- Xác nhận mật khẩu khớp
- Validation mã sinh viên và thông tin bắt buộc

## API Endpoints

### Đăng ký user mới
```http
POST /users
Content-Type: application/json

{
    "student_code": "CT030101",
    "student_name": "Nguyễn Văn A", 
    "student_class": "CT301",
    "password_hash": "...",
    "salt": "..."
}
```

### Lấy thông tin user (cho đăng nhập)
```http
GET /users/{student_code}
```

## Database Schema

### Collection: users
```javascript
{
    "_id": ObjectId,
    "student_code": String,     // Mã sinh viên (unique)
    "student_name": String,     // Họ tên
    "student_class": String,    // Lớp
    "password_hash": String,    // Hash của mật khẩu
    "salt": String,            // Salt để hash
    "created_at": DateTime,
    "updated_at": DateTime
}
```

## Customization

### Thay đổi API URL
```python
# Trong auth.py
auth_manager = AuthManager(api_base_url="http://your-api-server:8000")
```

### Tùy chỉnh validation
```python
# Trong auth.py, method show_register_form()
if len(password) < 8:  # Thay đổi độ dài tối thiểu
    errors.append("Mật khẩu phải có ít nhất 8 ký tự")
```

### Thay đổi hash algorithm
```python
# Trong auth.py, method hash_password()
password_hash = hashlib.pbkdf2_hmac('sha512',  # Thay đổi từ sha256
                                  password.encode('utf-8'),
                                  salt.encode('utf-8'),
                                  200000)  # Tăng iterations
```

## Troubleshooting

### Lỗi kết nối API
- Kiểm tra backend đã chạy chưa
- Kiểm tra port và URL trong `AuthManager`
- Kiểm tra firewall/network

### Lỗi database
- Kiểm tra MongoDB đã chạy chưa
- Kiểm tra connection string
- Kiểm tra permissions

### Lỗi dependencies
```bash
# Cài đặt lại dependencies
poetry install
# hoặc
pip install -r requirements.txt
```

## Development

### Thêm tính năng mới
1. Cập nhật `UserCreate` model trong `models/user.py`
2. Cập nhật API endpoints trong `api/user.py` 
3. Cập nhật frontend trong `auth.py`

### Testing
```bash
# Test API
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"student_code":"TEST001","student_name":"Test User"}'
```

## Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs trong terminal
2. Kiểm tra network connectivity
3. Kiểm tra database connection
4. Liên hệ KMA AI Lab để được hỗ trợ

---

**© 2025 Học viện Kỹ thuật Mật mã - KMA AI Lab**
