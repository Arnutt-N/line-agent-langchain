@echo off
echo LINE Agent Troubleshooting
echo ==========================

echo [1] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2] Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js
    pause
    exit /b 1
)

echo.
echo [3] Checking ports...
netstat -ano | findstr :8000 > nul
if not errorlevel 1 (
    echo WARNING: Port 8000 is already in use!
    echo Please close the application using port 8000
)

netstat -ano | findstr :5173 > nul
if not errorlevel 1 (
    echo WARNING: Port 5173 is already in use!
    echo Please close the application using port 5173
)

echo.
echo [4] Installing Backend dependencies...
cd /d D:\genAI\line-agent-langchain\backend
call ..\env\Scripts\activate
pip install -r requirements.txt

echo.
echo [5] Installing Frontend dependencies...
cd ..\frontend
call npm install

echo.
echo ==========================
echo Setup complete! You can now run:
echo - run_backend.bat (for backend only)
echo - run_frontend.bat (for frontend only)  
echo - run_all.bat (for both)
echo ==========================
pause