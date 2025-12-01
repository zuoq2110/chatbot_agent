@echo off
REM Quick test API without authentication
echo Testing API query: "Cach tinh diem hoc phan"
echo.

curl -X POST http://localhost:3434/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Cach tinh diem hoc phan\", \"conversationId\": null}"

echo.
echo.
echo ===================================================
echo Check server logs for:
echo   - Retrieved X documents
echo   - Context length
echo   - Prompt length
echo ===================================================
pause
