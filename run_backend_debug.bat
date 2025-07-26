@echo off
echo Starting LINE Agent Backend (Debug Mode)...
cd /d D:\genAI\line-agent-langchain\backend

echo Activating virtual environment...
call ..\env\Scripts\activate

echo Testing Python import...
python -c "from app.main import app; print('Import successful!')"

if errorlevel 1 (
    echo.
    echo Import failed! Checking detailed error...
    python app\main.py
    pause
    exit /b 1
)

echo.
echo Starting server without reload...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause