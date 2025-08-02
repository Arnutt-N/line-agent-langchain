@echo off
cd /d D:\genAI\line-agent-langchain\backend

echo Current directory: %CD%
echo.
echo Python path:
python -c "import sys; print(sys.executable)"
echo.
echo Checking .env file:
if exist .env (
    echo .env file exists
    echo First 5 lines:
    type .env | find /n /v "" | findstr "^\[1\] ^\[2\] ^\[3\] ^\[4\] ^\[5\]"
) else (
    echo .env file NOT FOUND!
)
echo.
echo Starting server...
python -m uvicorn app.main:app --reload --port 8000
