@echo off
echo Starting LINE Agent Backend on Port 8001...
cd /d D:\genAI\line-agent-langchain\backend

echo Activating virtual environment...
call ..\env\Scripts\activate

echo Starting FastAPI server on port 8001...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

pause