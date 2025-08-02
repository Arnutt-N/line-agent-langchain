@echo off
echo ========================================
echo  Secure LINE Bot Deployment with Supabase
echo ========================================

set PROJECT_ID=line-agent-langchain
set REGION=asia-southeast1
set SERVICE_NAME=line-hr-bot-backend
set SERVICE_ACCOUNT=%SERVICE_NAME%@%PROJECT_ID%.iam.gserviceaccount.com

echo.
echo Step 1: Building Docker image...
cd backend

gcloud builds submit --config=cloudbuild-production.yaml .

if errorlevel 1 (
    echo ERROR: Docker build failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 2: Creating service account (if not exists)...
gcloud iam service-accounts create %SERVICE_NAME% ^
  --display-name="LINE Bot Service Account" 2>nul

echo.
echo Step 3: Granting secret access permissions...
REM Grant access to secrets
gcloud secrets add-iam-policy-binding line-access-token ^
  --member="serviceAccount:%SERVICE_ACCOUNT%" ^
  --role="roles/secretmanager.secretAccessor" --quiet

gcloud secrets add-iam-policy-binding line-channel-secret ^
  --member="serviceAccount:%SERVICE_ACCOUNT%" ^
  --role="roles/secretmanager.secretAccessor" --quiet

gcloud secrets add-iam-policy-binding gemini-api-key ^
  --member="serviceAccount:%SERVICE_ACCOUNT%" ^
  --role="roles/secretmanager.secretAccessor" --quiet

gcloud secrets add-iam-policy-binding supabase-service-key ^
  --member="serviceAccount:%SERVICE_ACCOUNT%" ^
  --role="roles/secretmanager.secretAccessor" --quiet

gcloud secrets add-iam-policy-binding supabase-anon-key ^
  --member="serviceAccount:%SERVICE_ACCOUNT%" ^
  --role="roles/secretmanager.secretAccessor" --quiet

echo.
echo Step 4: Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
  --image gcr.io/%PROJECT_ID%/%SERVICE_NAME%:latest ^
  --region %REGION% ^
  --platform managed ^
  --allow-unauthenticated ^
  --service-account %SERVICE_ACCOUNT% ^
  --memory 1Gi ^
  --cpu 1 ^
  --concurrency 80 ^
  --max-instances 10 ^
  --timeout 300 ^
  --set-env-vars PORT=8080,ENVIRONMENT=production,SUPABASE_URL=https://fedcstitvqoknmiouafn.supabase.co,GEMINI_MODEL=gemini-2.5-flash,GEMINI_TEMPERATURE=0.7,GEMINI_MAX_TOKENS=500 ^
  --set-secrets LINE_ACCESS_TOKEN=line-access-token:latest,LINE_CHANNEL_SECRET=line-channel-secret:latest,GEMINI_API_KEY=gemini-api-key:latest,SUPABASE_SERVICE_KEY=supabase-service-key:latest,SUPABASE_ANON_KEY=supabase-anon-key:latest

if errorlevel 1 (
    echo ERROR: Cloud Run deployment failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo Step 5: Getting service URL...
set SERVICE_URL=
for /f "delims=" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"') do set SERVICE_URL=%%i

echo.
echo ========================================
echo ✅ Deployment completed successfully!
echo ========================================
echo.
echo 🚀 Your LINE Bot is live at: %SERVICE_URL%
echo 📊 Database: Supabase (fedcstitvqoknmiouafn)
echo 🔐 Secrets: Stored in Google Secret Manager
echo.
echo 📌 Next steps:
echo    1. Update LINE Webhook: %SERVICE_URL%/webhook
echo    2. Test in LINE app
echo    3. Monitor logs: gcloud logs tail --service=%SERVICE_NAME%
echo.

cd ..
pause
