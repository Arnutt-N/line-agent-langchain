@echo off
echo 🚀 Starting LINE Agent System...
echo ==================================

start cmd /k "cd /d D:\genAI\line-agent-langchain\backend && call ..\env\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

start cmd /k "cd /d D:\genAI\line-agent-langchain\frontend && npm run dev"

echo ==================================
echo ✅ ระบบเริ่มทำงานแล้ว!
echo.
echo 📍 Backend API: http://localhost:8000/docs
echo 📍 Frontend Admin: http://localhost:5173
echo ==================================
timeout /t 5