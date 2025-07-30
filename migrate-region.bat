@echo off
REM Migration script to move Cloud Run services from us-central1 to asia-southeast1
REM Make sure to set PROJECT_ID before running

setlocal enabledelayedexpansion

REM Configuration
if not defined PROJECT_ID set PROJECT_ID=your-project-id
set OLD_REGION=us-central1
set NEW_REGION=asia-southeast1

echo [INFO] Starting Cloud Run region migration...
echo [INFO] PROJECT_ID: %PROJECT_ID%
echo [INFO] Moving from: %OLD_REGION% to %NEW_REGION%

REM Check if required environment variables are set
if "%PROJECT_ID%"=="your-project-id" (
    echo [ERROR] Please set PROJECT_ID environment variable
    echo Example: set PROJECT_ID=my-project-id ^& migrate-region.bat
    exit /b 1
)

REM Set project
echo [INFO] Setting project...
gcloud config set project %PROJECT_ID%

REM Deploy to new region (reusing existing images)
echo [INFO] Deploying backend to %NEW_REGION%...
powershell -Command "(Get-Content cloudrun-backend.yaml) -replace 'PROJECT_ID', '%PROJECT_ID%' | Set-Content cloudrun-backend-temp.yaml"

gcloud run services replace cloudrun-backend-temp.yaml --region=%NEW_REGION% --project=%PROJECT_ID%
if errorlevel 1 (
    echo [ERROR] Backend deployment to %NEW_REGION% failed
    del cloudrun-backend-temp.yaml
    exit /b 1
)

del cloudrun-backend-temp.yaml
echo [INFO] Backend deployed to %NEW_REGION% successfully

REM Get new backend URL
for /f "tokens=*" %%i in ('gcloud run services describe line-hr-bot-backend --region=%NEW_REGION% --project=%PROJECT_ID% --format="value(status.url)"') do set NEW_BACKEND_URL=%%i

REM Deploy frontend to new region
echo [INFO] Deploying frontend to %NEW_REGION%...
powershell -Command "(Get-Content cloudrun-frontend.yaml) -replace 'PROJECT_ID', '%PROJECT_ID%' -replace 'https://line-hr-bot-backend-HASH-uc.a.run.app', '%NEW_BACKEND_URL%' | Set-Content cloudrun-frontend-temp.yaml"

gcloud run services replace cloudrun-frontend-temp.yaml --region=%NEW_REGION% --project=%PROJECT_ID%
if errorlevel 1 (
    echo [ERROR] Frontend deployment to %NEW_REGION% failed
    del cloudrun-frontend-temp.yaml
    exit /b 1
)

del cloudrun-frontend-temp.yaml
echo [INFO] Frontend deployed to %NEW_REGION% successfully

REM Set IAM permissions for new region
echo [INFO] Setting IAM permissions for %NEW_REGION%...
gcloud run services add-iam-policy-binding line-hr-bot-backend --region=%NEW_REGION% --member="allUsers" --role="roles/run.invoker" --project=%PROJECT_ID%
gcloud run services add-iam-policy-binding line-hr-bot-frontend --region=%NEW_REGION% --member="allUsers" --role="roles/run.invoker" --project=%PROJECT_ID%

REM Get new service URLs
for /f "tokens=*" %%i in ('gcloud run services describe line-hr-bot-frontend --region=%NEW_REGION% --project=%PROJECT_ID% --format="value(status.url)"') do set NEW_FRONTEND_URL=%%i

echo.
echo [INFO] ============================================
echo [INFO] 🎉 Migration completed successfully!
echo [INFO] ============================================
echo.
echo [INFO] NEW SERVICES (%NEW_REGION%):
echo [INFO] 📱 Backend URL:  %NEW_BACKEND_URL%
echo [INFO] 🌐 Frontend URL: %NEW_FRONTEND_URL%
echo.
echo [WARN] ⚠️  Important next steps:
echo [WARN]    1. Update LINE webhook URL to: %NEW_BACKEND_URL%/webhook
echo [WARN]    2. Test the new services to ensure they work correctly
echo [WARN]    3. Run cleanup script to remove old services from %OLD_REGION%
echo.

REM Ask if user wants to clean up old services
set /p cleanup="Do you want to delete the old services in %OLD_REGION%? (y/N): "
if /i "%cleanup%"=="y" (
    echo [INFO] Deleting old services from %OLD_REGION%...
    
    gcloud run services delete line-hr-bot-backend --region=%OLD_REGION% --project=%PROJECT_ID% --quiet
    if errorlevel 1 (
        echo [WARN] Failed to delete backend service from %OLD_REGION%
    ) else (
        echo [INFO] ✅ Deleted backend service from %OLD_REGION%
    )
    
    gcloud run services delete line-hr-bot-frontend --region=%OLD_REGION% --project=%PROJECT_ID% --quiet
    if errorlevel 1 (
        echo [WARN] Failed to delete frontend service from %OLD_REGION%
    ) else (
        echo [INFO] ✅ Deleted frontend service from %OLD_REGION%
    )
    
    echo [INFO] ✅ Cleanup completed
) else (
    echo [INFO] Old services kept in %OLD_REGION%. You can delete them manually later:
    echo [INFO]   gcloud run services delete line-hr-bot-backend --region=%OLD_REGION% --project=%PROJECT_ID%
    echo [INFO]   gcloud run services delete line-hr-bot-frontend --region=%OLD_REGION% --project=%PROJECT_ID%
)

echo.
pause