@echo off
echo ========================================
echo Starting LINE Bot Local Development
echo ========================================

REM Check if ngrok is installed
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: ngrok not found!
    echo Please download from https://ngrok.com/download
    pause
    exit /b 1
)

REM Start backend
echo Starting Backend on port 8000...
start "Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

REM Wait for backend to start
timeout /t 5

REM Start ngrok
echo Starting ngrok tunnel...
start "ngrok" cmd /k "ngrok http 8000"

REM Start frontend (optional)
echo Starting Frontend on port 5173...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo 1. Copy ngrok URL from the ngrok window
echo 2. Update LINE Webhook to: https://YOUR-NGROK-URL.ngrok-free.app/webhook
echo 3. Backend logs: Check Backend window
echo 4. ngrok dashboard: http://localhost:4040
echo.
pause
