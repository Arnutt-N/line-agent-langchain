@echo off
echo Starting LINE Bot Testing Environment...

REM Start Backend
start "Backend" cmd /k "cd /d D:\genAI\line-agent-langchain\backend && D:\genAI\line-agent-langchain\env\Scripts\python -m uvicorn app.main:app --reload --port 8000"

timeout /t 5

REM Start ngrok
start "ngrok" cmd /k "ngrok http 8000"

echo.
echo ========================================
echo LINE Bot Testing Started!
echo ========================================
echo 1. Backend: http://localhost:8000
echo 2. API Docs: http://localhost:8000/docs
echo 3. ngrok Dashboard: http://localhost:4040
echo.
echo Next: Copy ngrok URL and update LINE webhook
echo ========================================
pause
