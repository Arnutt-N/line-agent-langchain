@echo off
echo Starting LINE Agent Backend (Port 8000)...
cd /d D:\genAI\line-agent-langchain

echo Activating virtual environment...
call env\Scripts\activate

echo Starting FastAPI server...
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

pause