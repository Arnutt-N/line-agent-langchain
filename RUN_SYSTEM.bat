@echo off
cls
echo =====================================
echo    LINE Agent System Launcher
echo =====================================
echo.

:: Kill old processes
echo [1/4] Stopping old processes...
taskkill /F /IM python.exe 2>nul >nul
taskkill /F /IM node.exe 2>nul >nul
timeout /t 2 /nobreak > nul

:: Start Backend
echo [2/4] Starting Backend Server...
cd /d D:\genAI\line-agent-langchain
start "Backend - Port 8000" cmd /k "call env\Scripts\activate && python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend
echo [3/4] Waiting for backend to start...
timeout /t 5 /nobreak > nul

:: Start Frontend
echo [4/4] Starting Frontend Server...
cd /d D:\genAI\line-agent-langchain\frontend
start "Frontend - Port 5173" cmd /k "npx vite --host 0.0.0.0 --port 5173"

:: Wait and show status
timeout /t 5 /nobreak > nul
cls
echo =====================================
echo    ✅ LINE Agent System Started!
echo =====================================
echo.
echo 📍 Frontend Admin Panel:
echo    http://localhost:5173
echo.
echo 📍 Backend API Documentation:
echo    http://localhost:8000/docs
echo.
echo 📍 Health Check:
echo    http://localhost:8000/health
echo.
echo =====================================
echo.
echo ℹ️  Tips:
echo - Clear browser cache if you see errors
echo - Use Ctrl+C to stop servers
echo - Check console windows for logs
echo.
echo =====================================
pause