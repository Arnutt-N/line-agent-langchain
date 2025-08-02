@echo off
echo Starting LINE Bot Backend...
start cmd /k "cd /d D:\genAI\line-agent-langchain\backend && python -m uvicorn app.main:app --reload --port 8000"

echo.
echo Waiting for backend to start...
timeout /t 5

echo.
echo Starting ngrok...
start cmd /k "ngrok http 8000"

echo.
echo ================================
echo LINE Bot is starting...
echo ================================
echo.
echo 1. Wait for ngrok to start
echo 2. Copy the https URL from ngrok
echo 3. Update webhook URL in LINE Developers Console
echo 4. Your webhook URL will be: https://[ngrok-url]/webhook
echo.
echo ngrok dashboard: http://localhost:4040
echo Backend API docs: http://localhost:8000/docs
echo.
pause
