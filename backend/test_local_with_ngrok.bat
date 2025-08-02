@echo off
echo Starting LINE Bot Backend with ngrok...

REM Activate virtual environment
echo Activating virtual environment...
call D:\genAI\line-agent-langchain\env\Scripts\activate

REM Change to backend directory
cd /d D:\genAI\line-agent-langchain\backend

REM Start backend in new window
echo Starting backend server...
start "LINE Bot Backend" cmd /k "D:\genAI\line-agent-langchain\env\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5

REM Start ngrok in new window
echo Starting ngrok tunnel...
start "ngrok" cmd /k "ngrok http 8000"

echo.
echo ================================
echo LINE Bot Testing Environment
echo ================================
echo.
echo 1. Backend is starting on http://localhost:8000
echo 2. API Documentation: http://localhost:8000/docs
echo 3. ngrok is creating a public tunnel...
echo.
echo Next steps:
echo 1. Wait for ngrok window to show the URL
echo 2. Copy the https URL (e.g., https://xxxx-xxx.ngrok.io)
echo 3. Go to LINE Developers Console
echo 4. Update Webhook URL to: https://xxxx-xxx.ngrok.io/webhook
echo 5. Click "Verify" to test the connection
echo.
echo ngrok Web Interface: http://localhost:4040
echo.
echo Press any key to exit this window (backend and ngrok will continue running)
pause
