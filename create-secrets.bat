@echo off
echo ========================================
echo  Secure Deployment with Google Secret Manager
echo ========================================

set PROJECT_ID=line-agent-langchain
set REGION=asia-southeast1
set SERVICE_NAME=line-hr-bot-backend

echo.
echo Step 1: Creating secrets in Secret Manager...
echo.

REM Create secrets (run once)
echo Creating LINE_ACCESS_TOKEN secret...
echo 7SnsooFkLSB+1vz+XPuxNG9LNtHsB9GZzH2Zli0IWNhGumnQxrf0Qu0dz3u6AsihGDi0pmlaaLvwE6cuJZO2rsfA86PPDN0g2tnaatZMjvbmM3khoZEQsTHE++gfSJhjr7QrbOK9h3NUKRxw1oiEhgdB04t89/1O/w1cDnyilFU= | gcloud secrets create line-access-token --data-file=-

echo Creating LINE_CHANNEL_SECRET secret...
echo b3091cd8b818ab035b3a3f1006c2322a | gcloud secrets create line-channel-secret --data-file=-

echo Creating GEMINI_API_KEY secret...
echo AIzaSyAX3WH2gYTz_U_qOp5v3p1YoDHa1Yr0H7g | gcloud secrets create gemini-api-key --data-file=-

echo Creating SUPABASE_SERVICE_KEY secret...
echo eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlZGNzdGl0dnFva25taW91YWZuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzc0ODI3NywiZXhwIjoyMDY5MzI0Mjc3fQ.4jlDH5HhplSTau9hcs_blM2wQZXALAbcalsEUw2ap7I | gcloud secrets create supabase-service-key --data-file=-

echo Creating SUPABASE_ANON_KEY secret...
echo eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlZGNzdGl0dnFva25taW91YWZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3NDgyNzcsImV4cCI6MjA2OTMyNDI3N30.BmBFqaOOcWuqOA6p-8QAyyf_MCek8mO1i3JzGpuyppI | gcloud secrets create supabase-anon-key --data-file=-

echo.
echo Secrets created successfully!
echo.
pause
