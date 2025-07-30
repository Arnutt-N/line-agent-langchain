# Google Cloud Run Deployment Guide

This guide walks you through deploying the LINE HR Bot to Google Cloud Run.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Google Cloud SDK** installed and authenticated
3. **Docker** installed locally
4. **Required API Keys**:
   - LINE Channel Access Token & Secret
   - Google Gemini API Key
   - Supabase URL & Anon Key (optional)
   - Telegram Bot credentials (optional)

## Quick Start

### 1. Set Environment Variables

```bash
# Set your Google Cloud Project ID
export PROJECT_ID="your-project-id"
export REGION="asia-southeast1"  # Optional, defaults to asia-southeast1
```

### 2. Run Deployment Script

**For Linux/macOS:**
```bash
chmod +x deploy.sh
PROJECT_ID=your-project-id ./deploy.sh
```

**For Windows:**
```cmd
set PROJECT_ID=your-project-id
deploy.bat
```

### 3. Update Secrets

After deployment, update the secrets with actual values:

```bash
# Update each secret with actual values
echo "your_actual_line_token" | gcloud secrets versions add LINE_CHANNEL_ACCESS_TOKEN --data-file=-
echo "your_actual_line_secret" | gcloud secrets versions add LINE_CHANNEL_SECRET --data-file=-
echo "your_actual_gemini_key" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
echo "your_actual_supabase_url" | gcloud secrets versions add SUPABASE_URL --data-file=-
echo "your_actual_supabase_key" | gcloud secrets versions add SUPABASE_ANON_KEY --data-file=-
```
```cmd
REM Update each secret with actual values
echo your_actual_line_token | gcloud secrets versions add LINE_CHANNEL_ACCESS_TOKEN --data-file=-
echo your_actual_line_secret | gcloud secrets versions add LINE_CHANNEL_SECRET --data-file=-
echo your_actual_gemini_key | gcloud secrets versions add GEMINI_API_KEY --data-file=-
echo your_actual_supabase_url | gcloud secrets versions add SUPABASE_URL --data-file=-
echo your_actual_supabase_key | gcloud secrets versions add SUPABASE_ANON_KEY --data-file=-
```

### 4. Configure LINE Webhook

Update your LINE Bot webhook URL to:
```
https://line-hr-bot-backend-[HASH]-uc.a.run.app/webhook
```

## Manual Deployment Steps

### 1. Enable APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 2. Create Secrets

```bash
# Create secrets with placeholder values
echo "REPLACE_WITH_ACTUAL_VALUE" | gcloud secrets create LINE_CHANNEL_ACCESS_TOKEN --data-file=-
echo "REPLACE_WITH_ACTUAL_VALUE" | gcloud secrets create LINE_CHANNEL_SECRET --data-file=-
echo "REPLACE_WITH_ACTUAL_VALUE" | gcloud secrets create GEMINI_API_KEY --data-file=-
echo "REPLACE_WITH_ACTUAL_VALUE" | gcloud secrets create SUPABASE_URL --data-file=-
echo "REPLACE_WITH_ACTUAL_VALUE" | gcloud secrets create SUPABASE_ANON_KEY --data-file=-
echo "REPLACE_WITH_ACTUAL_VALUE" | gcloud secrets create TELEGRAM_BOT_TOKEN --data-file=-
echo "REPLACE_WITH_ACTUAL_VALUE" | gcloud secrets create TELEGRAM_CHAT_ID --data-file=-
```

### 3. Build and Deploy Backend

```bash
# Build Docker image
cd backend
docker build -f Dockerfile.cloudrun -t gcr.io/$PROJECT_ID/line-hr-bot-backend:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/line-hr-bot-backend:latest

# Deploy to Cloud Run
gcloud run deploy line-hr-bot-backend \
  --image gcr.io/$PROJECT_ID/line-hr-bot-backend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --concurrency 80 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars PORT=8080,ENVIRONMENT=production \
  --update-secrets \
  LINE_CHANNEL_ACCESS_TOKEN=LINE_CHANNEL_ACCESS_TOKEN:latest,\
LINE_CHANNEL_SECRET=LINE_CHANNEL_SECRET:latest,\
GEMINI_API_KEY=GEMINI_API_KEY:latest,\
SUPABASE_URL=SUPABASE_URL:latest,\
SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest,\
TELEGRAM_BOT_TOKEN=TELEGRAM_BOT_TOKEN:latest,\
TELEGRAM_CHAT_ID=TELEGRAM_CHAT_ID:latest
```

### 4. Build and Deploy Frontend

```bash
# Build Docker image
cd ../frontend
docker build -f Dockerfile.cloudrun -t gcr.io/$PROJECT_ID/line-hr-bot-frontend:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/line-hr-bot-frontend:latest

# Deploy to Cloud Run
gcloud run deploy line-hr-bot-frontend \
  --image gcr.io/$PROJECT_ID/line-hr-bot-frontend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 0.5 \
  --concurrency 100 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars PORT=8080
```

## Configuration

### Environment Variables

The following environment variables are automatically configured:

- `PORT=8080` (required by Cloud Run)
- `ENVIRONMENT=production`

### Secrets

Secrets are managed through Google Secret Manager:

- `LINE_CHANNEL_ACCESS_TOKEN` - LINE Bot channel access token
- `LINE_CHANNEL_SECRET` - LINE Bot channel secret
- `GEMINI_API_KEY` - Google Gemini API key
- `SUPABASE_URL` - Supabase project URL (optional)
- `SUPABASE_ANON_KEY` - Supabase anonymous key (optional)
- `TELEGRAM_BOT_TOKEN` - Telegram bot token (optional)
- `TELEGRAM_CHAT_ID` - Telegram chat ID (optional)

### Resource Limits

**Backend:**
- Memory: 1GB
- CPU: 1 vCPU
- Concurrency: 80 requests
- Max instances: 10
- Timeout: 300 seconds

**Frontend:**
- Memory: 512MB
- CPU: 0.5 vCPU
- Concurrency: 100 requests
- Max instances: 10
- Timeout: 300 seconds

## Health Checks

Both services include health check endpoints:

- Backend: `https://your-backend-url/health`
- Frontend: `https://your-frontend-url/health`

## Monitoring

### Logs

View logs using Cloud Console or gcloud:

```bash
# Backend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=line-hr-bot-backend" --limit 50

# Frontend logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=line-hr-bot-frontend" --limit 50
```

### Metrics

Monitor your services in the Cloud Console:
- Go to Cloud Run → Select your service → Metrics tab

## Troubleshooting

### Common Issues

1. **Secret Access Denied**
   ```bash
   # Grant secret access to compute service account
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

2. **Build Failures**
   - Check Docker build context and file paths
   - Verify all dependencies are included
   - Check Cloud Build logs for detailed errors

3. **Service Startup Issues**
   - Check health endpoint: `/health`
   - Review service logs
   - Verify environment variables and secrets

4. **LINE Webhook Issues**
   - Ensure webhook URL is publicly accessible
   - Verify SSL certificate is valid
   - Check LINE channel configuration

### Useful Commands

```bash
# Check service status
gcloud run services describe line-hr-bot-backend --region $REGION

# Update service
gcloud run services update line-hr-bot-backend --region $REGION

# Delete service
gcloud run services delete line-hr-bot-backend --region $REGION

# List secrets
gcloud secrets list

# Update secret
echo "new_value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

## Security

- All sensitive data is stored in Google Secret Manager
- Services run with minimal required permissions
- HTTPS is enforced by Cloud Run
- CORS is configured for frontend access only

## Cost Optimization

- Services scale to zero when not in use
- CPU throttling is enabled
- Memory and CPU limits are optimized
- Request-based pricing model

## CI/CD Pipeline

For automated deployments, use the included `cloudbuild.yaml`:

```bash
# Trigger build from GitHub
gcloud builds submit --config cloudbuild.yaml

# Set up automatic triggers
gcloud builds triggers create github \
  --repo-name=your-repo \
  --repo-owner=your-username \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## Next Steps

1. Configure custom domain (optional)
2. Set up monitoring and alerting
3. Configure backup and disaster recovery
4. Implement rate limiting
5. Set up staging environment