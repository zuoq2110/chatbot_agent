@echo off
REM Script chạy ứng dụng KMA ChatBot

echo ===================================
echo    KMA ChatBot System Launcher
echo ===================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python không được tìm thấy. Vui lòng cài đặt Python.
    pause
    exit /b 1
)

REM Kiểm tra Poetry
poetry --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Poetry không được tìm thấy. Đang cài đặt dependencies bằng pip...
    pip install -r requirements.txt
) else (
    echo [INFO] Đang cài đặt dependencies bằng Poetry...
    poetry install
)

echo.
echo Chọn chế độ chạy:
echo 1. Chạy Backend API (Port 8000)
echo 2. Chạy Frontend Streamlit (Port 8501)
echo 3. Chạy cả Backend và Frontend
echo 4. Chạy trang đăng nhập riêng (Port 8502)
echo.

set /p choice="Nhập lựa chọn (1-4): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto both
if "%choice%"=="4" goto login_page

echo [ERROR] Lựa chọn không hợp lệ!
pause
exit /b 1

:backend
echo [INFO] Đang khởi động Backend API...
cd src
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
goto end

:frontend
echo [INFO] Đang khởi động Frontend Streamlit...
cd src/streamlit_ui
streamlit run streamlit_app.py --server.port 8501
goto end

:login_page
echo [INFO] Đang khởi động trang đăng nhập...
cd src/streamlit_ui
streamlit run login_page.py --server.port 8502
goto end

:both
echo [INFO] Đang khởi động cả Backend và Frontend...
echo [INFO] Backend sẽ chạy ở port 8000
echo [INFO] Frontend sẽ chạy ở port 8501
echo.
start /b cmd /c "cd src && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 >nul
cd src/streamlit_ui
streamlit run streamlit_app.py --server.port 8501
goto end

:end
echo.
echo [INFO] Ứng dụng đã dừng.
pause
