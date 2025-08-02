@echo off
echo ========================================
echo  Deploying LINE Bot Backend to Cloud Run
echo  With Supabase Database
echo ========================================

REM Set project variables
set PROJECT_ID=line-agent-langchain
set REGION=asia-southeast1
set SERVICE_NAME=line-hr-bot-backend

REM Set Supabase credentials
set SUPABASE_URL=https://fedcstitvqoknmiouafn.supabase.co
set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlZGNzdGl0dnFva25taW91YWZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3NDgyNzcsImV4cCI6MjA2OTMyNDI3N30.BmBFqaOOcWuqOA6p-8QAyyf_MCek8mO1i3JzGpuyppI

echo.
echo Step 1: Building Docker image...
cd backend

REM Build using the Cloud Run specific Dockerfile
gcloud builds submit --tag gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest ^
  --file Dockerfile.cloudrun .

if errorlevel 1 (
    echo ERROR: Docker build failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 2: Deploying to Cloud Run with Supabase...
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
  --set-env-vars PORT=8080,ENVIRONMENT=production,SUPABASE_URL=%SUPABASE_URL%,SUPABASE_ANON_KEY=%SUPABASE_ANON_KEY%

if errorlevel 1 (
    echo ERROR: Cloud Run deployment failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 3: Setting sensitive environment variables via gcloud...
REM Update service with all environment variables
gcloud run services update %SERVICE_NAME% ^
  --region %REGION% ^
  --update-env-vars LINE_ACCESS_TOKEN=7SnsooFkLSB+1vz+XPuxNG9LNtHsB9GZzH2Zli0IWNhGumnQxrf0Qu0dz3u6AsihGDi0pmlaaLvwE6cuJZO2rsfA86PPDN0g2tnaatZMjvbmM3khoZEQsTHE++gfSJhjr7QrbOK9h3NUKRxw1oiEhgdB04t89/1O/w1cDnyilFU=,LINE_CHANNEL_SECRET=b3091cd8b818ab035b3a3f1006c2322a,GEMINI_API_KEY=AIzaSyAX3WH2gYTz_U_qOp5v3p1YoDHa1Yr0H7g,GEMINI_MODEL=gemini-2.5-flash,GEMINI_TEMPERATURE=0.7,GEMINI_MAX_TOKENS=500,GEMINI_ENABLE_SAFETY=false,SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlZGNzdGl0dnFva25taW91YWZuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzc0ODI3NywiZXhwIjoyMDY5MzI0Mjc3fQ.4jlDH5HhplSTau9hcs_blM2wQZXALAbcalsEUw2ap7I

echo.
echo Step 4: Getting service URL...
set SERVICE_URL=
for /f "delims=" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"') do set SERVICE_URL=%%i

echo Service URL: %SERVICE_URL%

echo.
echo ========================================
echo ✅ Deployment completed successfully!
echo ========================================
echo.
echo 🚀 Your LINE Bot backend is now live at:
echo    %SERVICE_URL%
echo.
echo 📊 Database: Using Supabase
echo    URL: %SUPABASE_URL%
echo.
echo 📌 Next steps:
echo    1. Update LINE Webhook URL to: %SERVICE_URL%/webhook
echo    2. Test the bot in LINE app
echo    3. Check logs: gcloud logs read --service=%SERVICE_NAME% --region=%REGION%
echo.
echo 🔐 Security Note: Consider using Secret Manager for API keys in production

cd ..
pause
