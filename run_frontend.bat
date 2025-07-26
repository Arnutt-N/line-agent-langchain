@echo off
echo Starting LINE Agent Frontend...
cd /d D:\genAI\line-agent-langchain\frontend

echo Installing dependencies...
call npm install

echo Starting Vite dev server...
call npm run dev

pause