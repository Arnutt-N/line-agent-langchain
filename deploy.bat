@echo off
REM Google Cloud Run Deployment Script for Windows
REM Make sure to set these variables before running

setlocal enabledelayedexpansion

REM Configuration
if not defined PROJECT_ID set PROJECT_ID=your-project-id
if not defined REGION set REGION=asia-southeast1

echo [INFO] Starting Google Cloud Run deployment...
echo [INFO] Using PROJECT_ID: %PROJECT_ID%
echo [INFO] Using REGION: %REGION%

REM Check if required environment variables are set
if "%PROJECT_ID%"=="your-project-id" (
    echo [ERROR] Please set PROJECT_ID environment variable
    echo Example: set PROJECT_ID=my-project-id ^& deploy.bat
    exit /b 1
)

REM Authenticate with Google Cloud
echo [INFO] Authenticating with Google Cloud...
gcloud auth configure-docker gcr.io --quiet
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo [INFO] Enabling required Google Cloud APIs...
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com --project=%PROJECT_ID%

REM Create secrets (if they don't exist)
echo [INFO] Creating secrets in Secret Manager...

set secrets=LINE_CHANNEL_ACCESS_TOKEN LINE_CHANNEL_SECRET GEMINI_API_KEY SUPABASE_URL SUPABASE_ANON_KEY TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID

for %%s in (%secrets%) do (
    gcloud secrets describe %%s --project=%PROJECT_ID% >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Secret %%s does not exist. Creating with placeholder...
        echo REPLACE_WITH_ACTUAL_VALUE | gcloud secrets create %%s --data-file=- --project=%PROJECT_ID%
        echo [INFO] Created secret: %%s ^(remember to update with actual value^)
    ) else (
        echo [INFO] Secret already exists: %%s
    )
)

REM Build and push backend
echo [INFO] Building backend Docker image...
cd backend
docker build -f Dockerfile.cloudrun -t gcr.io/%PROJECT_ID%/line-hr-bot-backend:latest .
if errorlevel 1 (
    echo [ERROR] Backend build failed
    exit /b 1
)

echo [INFO] Pushing backend image to Container Registry...
docker push gcr.io/%PROJECT_ID%/line-hr-bot-backend:latest
if errorlevel 1 (
    echo [ERROR] Backend push failed
    exit /b 1
)
cd ..

REM Build and push frontend
echo [INFO] Building frontend Docker image...
cd frontend
docker build -f Dockerfile.cloudrun -t gcr.io/%PROJECT_ID%/line-hr-bot-frontend:latest .
if errorlevel 1 (
    echo [ERROR] Frontend build failed
    exit /b 1
)

echo [INFO] Pushing frontend image to Container Registry...
docker push gcr.io/%PROJECT_ID%/line-hr-bot-frontend:latest
if errorlevel 1 (
    echo [ERROR] Frontend push failed
    exit /b 1
)
cd ..

REM Deploy backend service
echo [INFO] Deploying backend to Cloud Run...
powershell -Command "(Get-Content cloudrun-backend.yaml) -replace 'PROJECT_ID', '%PROJECT_ID%' | Set-Content cloudrun-backend-temp.yaml"

gcloud run services replace cloudrun-backend-temp.yaml --region=%REGION% --project=%PROJECT_ID%
if errorlevel 1 (
    echo [ERROR] Backend deployment failed
    del cloudrun-backend-temp.yaml
    exit /b 1
)

del cloudrun-backend-temp.yaml
echo [INFO] Backend deployed successfully

REM Get backend service URL
for /f "tokens=*" %%i in ('gcloud run services describe line-hr-bot-backend --region=%REGION% --project=%PROJECT_ID% --format="value(status.url)"') do set BACKEND_URL=%%i

REM Deploy frontend service
echo [INFO] Deploying frontend to Cloud Run...
powershell -Command "(Get-Content cloudrun-frontend.yaml) -replace 'PROJECT_ID', '%PROJECT_ID%' -replace 'https://line-hr-bot-backend-HASH-uc.a.run.app', '%BACKEND_URL%' | Set-Content cloudrun-frontend-temp.yaml"

gcloud run services replace cloudrun-frontend-temp.yaml --region=%REGION% --project=%PROJECT_ID%
if errorlevel 1 (
    echo [ERROR] Frontend deployment failed
    del cloudrun-frontend-temp.yaml
    exit /b 1
)

del cloudrun-frontend-temp.yaml
echo [INFO] Frontend deployed successfully

REM Set IAM permissions
echo [INFO] Setting IAM permissions...
gcloud run services add-iam-policy-binding line-hr-bot-backend --region=%REGION% --member="allUsers" --role="roles/run.invoker" --project=%PROJECT_ID%
gcloud run services add-iam-policy-binding line-hr-bot-frontend --region=%REGION% --member="allUsers" --role="roles/run.invoker" --project=%PROJECT_ID%
echo [INFO] IAM permissions set

REM Get service URLs
for /f "tokens=*" %%i in ('gcloud run services describe line-hr-bot-frontend --region=%REGION% --project=%PROJECT_ID% --format="value(status.url)"') do set FRONTEND_URL=%%i

echo.
echo [INFO] ============================================
echo [INFO] 🎉 Deployment completed successfully!
echo [INFO] ============================================
echo.
echo [INFO] 📱 Backend URL:  %BACKEND_URL%
echo [INFO] 🌐 Frontend URL: %FRONTEND_URL%
echo.
echo [WARN] ⚠️  Don't forget to:
echo [WARN]    1. Update secrets in Secret Manager with actual values
echo [WARN]    2. Update LINE webhook URL to: %BACKEND_URL%/webhook
echo [WARN]    3. Configure CORS settings if needed
echo.

pause