@echo off
echo ========================================================
echo Phase 1.6: Test HR Bot System
echo ========================================================
echo.

echo Checking if backend is running...
curl -s http://localhost:8000 > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Backend not running. Please run RUN_SYSTEM.bat first
    echo.
    pause
    exit /b 1
)

echo [OK] Backend is running
echo.

echo Running system tests...
cd /d D:\genAI\line-agent-langchain
call env\Scripts\activate
python backend\test_system_phase16.py

echo.
echo ========================================================
echo Testing complete! Check results above.
echo ========================================================
pause
