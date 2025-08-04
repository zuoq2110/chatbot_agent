@echo off
REM Script cài đặt KMA ChatBot Authentication System

echo ========================================
echo   KMA ChatBot Authentication Setup
echo ========================================
echo.

echo [1/5] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python không được tìm thấy!
    echo Vui lòng cài đặt Python 3.12+ từ https://python.org
    pause
    exit /b 1
) else (
    echo [OK] Python đã được cài đặt
)

echo.
echo [2/5] Kiểm tra MongoDB...
REM Kiểm tra MongoDB service
sc query MongoDB >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Không tìm thấy MongoDB service
    echo Vui lòng cài đặt MongoDB và đảm bảo service đang chạy
) else (
    echo [OK] MongoDB service được tìm thấy
)

echo.
echo [3/5] Cài đặt dependencies...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Sử dụng pip để cài đặt...
    pip install requests streamlit fastapi uvicorn pymongo pydantic motor
) else (
    echo [INFO] Sử dụng Poetry để cài đặt...
    poetry install
)

echo.
echo [4/5] Kiểm tra cấu trúc thư mục...
if not exist "src\streamlit_ui\auth.py" (
    echo [ERROR] File auth.py không tồn tại!
    echo Vui lòng đảm bảo tất cả files đã được tạo đúng cách
    pause
    exit /b 1
) else (
    echo [OK] Files authentication đã sẵn sàng
)

echo.
echo [5/5] Tạo file môi trường...
if not exist ".env" (
    echo Tạo file .env mẫu...
    echo # MongoDB Configuration > .env
    echo MONGODB_URL=mongodb://localhost:27017 >> .env
    echo MONGODB_DATABASE=kma_chatbot >> .env
    echo. >> .env
    echo # API Configuration >> .env
    echo API_HOST=localhost >> .env
    echo API_PORT=8000 >> .env
    echo. >> .env
    echo # Streamlit Configuration >> .env
    echo STREAMLIT_HOST=localhost >> .env
    echo STREAMLIT_PORT=8501 >> .env
    echo. >> .env
    echo [INFO] File .env đã được tạo. Vui lòng kiểm tra và cập nhật cấu hình.
) else (
    echo [OK] File .env đã tồn tại
)

echo.
echo ========================================
echo            SETUP HOÀN THÀNH!
echo ========================================
echo.
echo Các bước tiếp theo:
echo 1. Kiểm tra file .env và cập nhật cấu hình MongoDB
echo 2. Chạy: run.bat để khởi động ứng dụng
echo 3. Truy cập: http://localhost:8501
echo.
echo Tài liệu chi tiết: AUTHENTICATION.md
echo.
pause
