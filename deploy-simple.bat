@echo off
echo ========================================
echo  Simple LINE Bot Deployment
echo ========================================

set PROJECT_ID=line-agent-langchain
set REGION=asia-southeast1
set SERVICE_NAME=line-hr-bot-backend

echo.
echo Preparing for deployment...
cd backend

REM Ensure we're using the right Dockerfile
echo Step 1: Using Dockerfile.cloudrun as main Dockerfile...
copy /Y Dockerfile.cloudrun Dockerfile

echo.
echo Step 2: Building Docker image...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest .

if errorlevel 1 (
    echo ERROR: Docker build failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 3: Deploying to Cloud Run...
echo Setting up with Supabase connection...

gcloud run deploy %SERVICE_NAME% ^
  --image gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest ^
  --region %REGION% ^
  --platform managed ^
  --allow-unauthenticated ^
  --memory 1Gi ^
  --cpu 1 ^
  --concurrency 80 ^
  --max-instances 10 ^
  --timeout 300 ^
  --set-env-vars ^
PORT=8080,^
ENVIRONMENT=production,^
SUPABASE_URL=https://fedcstitvqoknmiouafn.supabase.co,^
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlZGNzdGl0dnFva25taW91YWZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3NDgyNzcsImV4cCI6MjA2OTMyNDI3N30.BmBFqaOOcWuqOA6p-8QAyyf_MCek8mO1i3JzGpuyppI,^
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlZGNzdGl0dnFva25taW91YWZuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzc0ODI3NywiZXhwIjoyMDY5MzI0Mjc3fQ.4jlDH5HhplSTau9hcs_blM2wQZXALAbcalsEUw2ap7I,^
LINE_ACCESS_TOKEN=7SnsooFkLSB+1vz+XPuxNG9LNtHsB9GZzH2Zli0IWNhGumnQxrf0Qu0dz3u6AsihGDi0pmlaaLvwE6cuJZO2rsfA86PPDN0g2tnaatZMjvbmM3khoZEQsTHE++gfSJhjr7QrbOK9h3NUKRxw1oiEhgdB04t89/1O/w1cDnyilFU=,^
LINE_CHANNEL_SECRET=b3091cd8b818ab035b3a3f1006c2322a,^
GEMINI_API_KEY=AIzaSyAX3WH2gYTz_U_qOp5v3p1YoDHa1Yr0H7g,^
GEMINI_MODEL=gemini-2.5-flash,^
GEMINI_TEMPERATURE=0.7,^
GEMINI_MAX_TOKENS=500,^
GEMINI_ENABLE_SAFETY=false

if errorlevel 1 (
    echo ERROR: Cloud Run deployment failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 4: Getting service URL...
set SERVICE_URL=
for /f "delims=" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"') do set SERVICE_URL=%%i

echo.
echo ========================================
echo ✅ Deployment completed successfully!
echo ========================================
echo.
echo 🚀 Your LINE Bot is live at: %SERVICE_URL%
echo.
echo 📌 Next steps:
echo    1. Update LINE Webhook URL to: %SERVICE_URL%/webhook
echo    2. Enable webhook in LINE Developers Console
echo    3. Test the bot in LINE app
echo.
echo 📊 Database: Supabase
echo 📝 View logs: gcloud logs tail --service=%SERVICE_NAME%
echo.
echo ⚠️  Note: For production, use Secret Manager instead of env vars

cd ..
pause
