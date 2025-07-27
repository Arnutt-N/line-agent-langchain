@echo off
echo Starting LINE Agent System (Port 8001)...
echo =====================================

echo [1/2] Starting Backend Server (Port 8001)...
start cmd /k "cd /d D:\genAI\line-agent-langchain && run_backend_port8001.bat"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo [2/2] Starting Frontend Server (Port 5173)...
start cmd /k "cd /d D:\genAI\line-agent-langchain && run_frontend.bat"

echo =====================================
echo Both servers are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:5173
echo =====================================
echo.
echo ⚠️  หมายเหตุ: 
echo - Backend ทำงานที่ Port 8001 (แทน 8000)
echo - Frontend จะเชื่อมต่อผ่าน Proxy อัตโนมัติ
echo =====================================
echo Press any key to exit...
pause > nul