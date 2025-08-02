@echo off
echo ========================================
echo  Deploying LINE Bot Backend to Cloud Run
echo ========================================

REM Set project variables
set PROJECT_ID=line-agent-langchain
set REGION=asia-southeast1
set SERVICE_NAME=line-hr-bot-backend

echo.
echo Step 1: Building Docker image from root directory...
echo Current directory: %CD%

REM Build from root directory to include requirements-simplified.txt
gcloud builds submit --tag gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest .

if errorlevel 1 (
    echo ERROR: Docker build failed!
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
    pause
    exit /b 1
)

echo.
echo ✅ Deployment completed successfully!
echo.
echo Getting service URL...
gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"

echo.
echo 🚀 Your LINE Bot backend is now live!
pause
