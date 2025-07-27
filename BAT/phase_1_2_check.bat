@echo off
echo ========================================================
echo Phase 1.2: Check Environment Variables
echo ========================================================
echo.

cd /d D:\genAI\line-agent-langchain\backend
call ..\env\Scripts\activate

echo Running environment check...
python check_env_phase12.py

echo.
echo ========================================================
pause
