@echo off
echo Checking and clearing ports...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Killing process %%a on port 8000...
    taskkill /F /PID %%a 2>nul
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    echo Killing process %%a on port 5173...
    taskkill /F /PID %%a 2>nul
)

echo Waiting for ports to clear...
timeout /t 2 /nobreak > nul

echo ==============================
echo Starting LINE Agent System
echo ==============================

cd /d D:\genAI\line-agent-langchain\backend
start "Backend Server" cmd /k "call ..\env\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak > nul

cd /d D:\genAI\line-agent-langchain\frontend
start "Frontend Server" cmd /k "npm run dev"

echo ==============================
echo ✅ System Started!
echo ==============================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ==============================

timeout /t 5 /nobreak > nul

echo Testing endpoints...
echo.
echo Root endpoint:
curl -s http://localhost:8000/
echo.
echo.
echo Health endpoint:
curl -s http://localhost:8000/health
echo.
echo ==============================
pause