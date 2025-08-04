@echo off
REM Script khởi động Backend API

echo =====================================
echo     KMA ChatBot Backend Starter
echo =====================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python không được tìm thấy!
    echo Vui lòng cài đặt Python từ https://python.org
    pause
    exit /b 1
)

echo [INFO] Đang khởi động Backend API...
echo [INFO] URL: http://localhost:8000
echo [INFO] Docs: http://localhost:8000/docs
echo [INFO] Nhấn Ctrl+C để dừng
echo.

REM Chuyển đến thư mục src
cd src

REM Khởi động FastAPI server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo [INFO] Backend đã dừng.
pause
