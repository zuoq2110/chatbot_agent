@echo off
REM Start server in PRODUCTION mode (no reload, cache persists)
echo Starting KMA Chat Backend in PRODUCTION mode...
echo Cache will persist across requests for faster performance
echo.

set PRODUCTION=true
uvicorn src.backend.main:app --port 3434 --host 0.0.0.0 --workers 1

pause
