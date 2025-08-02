#!/bin/bash

echo "========================================"
echo " Deploying LINE Bot Backend to Cloud Run"
echo "========================================"

# Set project variables
PROJECT_ID=${1:-your-project-id}
REGION="asia-southeast1"
SERVICE_NAME="line-hr-bot-backend"

echo ""
echo "Step 1: Building Docker image..."
cd backend

gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed!"
    exit 1
fi

echo ""
echo "Step 2: Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --concurrency 80 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars PORT=8080,ENVIRONMENT=production

if [ $? -ne 0 ]; then
    echo "ERROR: Cloud Run deployment failed!"
    exit 1
fi

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "Getting service URL..."
gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)"

echo ""
echo "🚀 Your LINE Bot backend is now live!"
