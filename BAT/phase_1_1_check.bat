@echo off
echo ========================================================
echo Phase 1.1: Check Project Structure and Dependencies
echo ========================================================
echo.

echo [1] Checking Project Structure:
echo --------------------------------
if exist backend (
    echo [OK] backend/ - Backend API folder
) else (
    echo [X] backend/ - Missing!
)

if exist frontend (
    echo [OK] frontend/ - Frontend UI folder
) else (
    echo [X] frontend/ - Missing!
)

if exist env (
    echo [OK] env/ - Virtual Environment
) else (
    echo [X] env/ - Missing! Run: python -m venv env
)

if exist backend\app (
    echo [OK] backend/app/ - Main application
) else (
    echo [X] backend/app/ - Missing!
)

if not exist backend\data (
    echo [!] backend/data/ - Not found, creating...
    mkdir backend\data
    mkdir backend\data\text
    mkdir backend\data\csv
    echo [OK] Created data folders for RAG system
) else (
    echo [OK] backend/data/ - Data folder exists
)

echo.
echo [2] Checking Key Files:
echo --------------------------------
if exist backend\.env (
    echo [OK] backend/.env - Environment variables
    echo [!] Please verify API keys are not placeholders!
) else (
    echo [X] backend/.env - Missing!
    if exist backend\.env.example (
        echo [!] Found .env.example - copying...
        copy backend\.env.example backend\.env
        echo [!] Please edit backend/.env with your API keys!
    )
)

if exist backend\requirements.txt (
    echo [OK] backend/requirements.txt - Python packages list
) else (
    echo [X] backend/requirements.txt - Missing!
)

if exist backend\app\main.py (
    echo [OK] backend/app/main.py - Main FastAPI file
) else (
    echo [X] backend/app/main.py - Missing!
)

if exist backend\line_agent.db (
    echo [OK] backend/line_agent.db - SQLite database
) else (
    echo [!] backend/line_agent.db - Not found
    echo [!] Will be created on first run
)

echo.
echo [3] Checking Python Dependencies:
echo --------------------------------
echo Activating virtual environment...
call env\Scripts\activate

echo.
echo Checking installed packages...
pip list | findstr /i "fastapi uvicorn line-bot-sdk sqlalchemy langchain websockets"

echo.
echo ========================================================
echo Phase 1.1 Summary:
echo ========================================================
echo.
echo [READY] Core structure exists
echo [TODO] Check .env file for real API keys
echo [TODO] Verify all dependencies installed
echo.
echo Next: Run Phase 1.2 to configure .env file
echo ========================================================
pause
