@echo off
echo ========================================
echo  Deploying LINE Bot Backend to Cloud Run
echo ========================================

REM Set project variables
set PROJECT_ID=line-agent-langchain
set REGION=asia-southeast1
set SERVICE_NAME=line-hr-bot-backend

echo.
echo Step 1: Building Docker image...
echo Current directory: %CD%

REM Navigate to backend directory
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
echo Step 2: Deploying to Cloud Run...
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
  --set-env-vars PORT=8080,ENVIRONMENT=production

if errorlevel 1 (
    echo ERROR: Cloud Run deployment failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 3: Getting service URL...
set SERVICE_URL=
for /f "delims=" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"') do set SERVICE_URL=%%i

echo Service URL: %SERVICE_URL%

echo.
echo ✅ Deployment completed successfully!
echo.
echo 🚀 Your LINE Bot backend is now live at:
echo    %SERVICE_URL%
echo.
echo 📌 Don't forget to:
echo    1. Update your LINE Webhook URL to: %SERVICE_URL%/webhook
echo    2. Set environment variables in Cloud Run console
echo    3. Check logs with: gcloud logs read --service=%SERVICE_NAME% --region=%REGION%

cd ..
pause
