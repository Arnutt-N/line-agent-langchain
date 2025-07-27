@echo off
echo Stopping old processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul

echo Waiting for ports to be released...
timeout /t 3 /nobreak > nul

echo Starting LINE Agent System...
echo ==============================

echo [1/2] Starting Backend (Port 8000)...
start cmd /k "cd /d D:\genAI\line-agent-langchain\backend && call ..\env\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo [2/2] Starting Frontend (Port 5173)...
start cmd /k "cd /d D:\genAI\line-agent-langchain\frontend && npm run dev"

echo ==============================
echo System is starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ==============================
timeout /t 5

echo Testing backend endpoints...
curl -s http://localhost:8000/
echo.
curl -s http://localhost:8000/health
echo.
echo ==============================
pause