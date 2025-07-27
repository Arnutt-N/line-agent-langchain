@echo off
echo Fixing LINE Agent Backend Dependencies...
cd /d D:\genAI\line-agent-langchain\backend

echo Activating virtual environment...
call ..\env\Scripts\activate

echo Installing/Updating langgraph components...
pip install --upgrade langgraph langgraph-checkpoint

echo Installing SQLite async support...
pip install aiosqlite

echo Verifying installations...
pip show langgraph
pip show langgraph-checkpoint

echo.
echo Dependencies fixed! Try running the backend again.
pause