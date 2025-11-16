@echo off
REM Startup script for KMA ChatBot Agent with OpenMP fix

echo ========================================
echo KMA ChatBot Agent - Starting Server
echo ========================================
echo.

REM Set environment variable to fix OpenMP library conflict
set KMP_DUPLICATE_LIB_OK=TRUE
echo [OK] OpenMP conflict fix enabled

REM Navigate to project directory
cd /d "%~dp0"
echo [OK] Changed to project directory

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] No virtual environment found, using system Python
)

REM Start the server
echo.
echo [INFO] Starting Uvicorn server...
echo ========================================
echo.

uvicorn src.backend.main:app --reload --host 127.0.0.1 --port 8000

REM If the server exits, pause to see any error messages
echo.
echo ========================================
echo Server stopped
echo ========================================
pause
