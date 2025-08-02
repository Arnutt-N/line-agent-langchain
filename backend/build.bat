@echo off
cd /d D:\genAI\line-agent-langchain\backend
echo Building Docker image...
call gcloud builds submit --tag gcr.io/line-agent-langchain/line-hr-bot-backend:v3
echo Done!
