#!/bin/bash

# Migration script to move Cloud Run services from us-central1 to asia-southeast1
# Make sure to set PROJECT_ID before running

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
OLD_REGION="us-central1"
NEW_REGION="asia-southeast1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo_info "🚀 Starting Cloud Run region migration..."
echo_info "PROJECT_ID: $PROJECT_ID"
echo_info "Moving from: $OLD_REGION to $NEW_REGION"

# Check if required environment variables are set
if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "your-project-id" ]]; then
    echo_error "Please set PROJECT_ID environment variable"
    echo "Example: PROJECT_ID=my-project-id ./migrate-region.sh"
    exit 1
fi

# Set project
echo_info "Setting project..."
gcloud config set project $PROJECT_ID

# Deploy to new region (reusing existing images)
echo_info "Deploying backend to $NEW_REGION..."

# Replace PROJECT_ID in config file
sed "s/PROJECT_ID/$PROJECT_ID/g" cloudrun-backend.yaml > cloudrun-backend-temp.yaml

gcloud run services replace cloudrun-backend-temp.yaml \
    --region=$NEW_REGION \
    --project=$PROJECT_ID

# Clean up temp file
rm cloudrun-backend-temp.yaml

echo_info "✅ Backend deployed to $NEW_REGION successfully"

# Get new backend URL
NEW_BACKEND_URL=$(gcloud run services describe line-hr-bot-backend \
    --region=$NEW_REGION \
    --project=$PROJECT_ID \
    --format="value(status.url)")

# Deploy frontend to new region
echo_info "Deploying frontend to $NEW_REGION..."

# Replace variables in config file
sed -e "s/PROJECT_ID/$PROJECT_ID/g" \
    -e "s|https://line-hr-bot-backend-HASH-uc.a.run.app|$NEW_BACKEND_URL|g" \
    cloudrun-frontend.yaml > cloudrun-frontend-temp.yaml

gcloud run services replace cloudrun-frontend-temp.yaml \
    --region=$NEW_REGION \
    --project=$PROJECT_ID

# Clean up temp file
rm cloudrun-frontend-temp.yaml

echo_info "✅ Frontend deployed to $NEW_REGION successfully"

# Set IAM permissions for new region
echo_info "Setting IAM permissions for $NEW_REGION..."

gcloud run services add-iam-policy-binding line-hr-bot-backend \
    --region=$NEW_REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project=$PROJECT_ID

gcloud run services add-iam-policy-binding line-hr-bot-frontend \
    --region=$NEW_REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --project=$PROJECT_ID

# Get new service URLs
NEW_FRONTEND_URL=$(gcloud run services describe line-hr-bot-frontend \
    --region=$NEW_REGION \
    --project=$PROJECT_ID \
    --format="value(status.url)")

echo ""
echo_info "============================================"
echo_info "🎉 Migration completed successfully!"
echo_info "============================================"
echo ""
echo_info "NEW SERVICES ($NEW_REGION):"
echo_info "📱 Backend URL:  $NEW_BACKEND_URL"
echo_info "🌐 Frontend URL: $NEW_FRONTEND_URL"
echo ""
echo_warn "⚠️  Important next steps:"
echo_warn "   1. Update LINE webhook URL to: $NEW_BACKEND_URL/webhook"
echo_warn "   2. Test the new services to ensure they work correctly"
echo_warn "   3. Run cleanup to remove old services from $OLD_REGION"
echo ""

# Ask if user wants to clean up old services
read -p "Do you want to delete the old services in $OLD_REGION? (y/N): " cleanup

if [[ "$cleanup" == "y" || "$cleanup" == "Y" ]]; then
    echo_info "Deleting old services from $OLD_REGION..."
    
    if gcloud run services delete line-hr-bot-backend \
        --region=$OLD_REGION \
        --project=$PROJECT_ID \
        --quiet; then
        echo_info "✅ Deleted backend service from $OLD_REGION"
    else
        echo_warn "Failed to delete backend service from $OLD_REGION"
    fi
    
    if gcloud run services delete line-hr-bot-frontend \
        --region=$OLD_REGION \
        --project=$PROJECT_ID \
        --quiet; then
        echo_info "✅ Deleted frontend service from $OLD_REGION"
    else
        echo_warn "Failed to delete frontend service from $OLD_REGION"
    fi
    
    echo_info "✅ Cleanup completed"
else
    echo_info "Old services kept in $OLD_REGION. You can delete them manually later:"
    echo_info "  gcloud run services delete line-hr-bot-backend --region=$OLD_REGION --project=$PROJECT_ID"
    echo_info "  gcloud run services delete line-hr-bot-frontend --region=$OLD_REGION --project=$PROJECT_ID"
fi

echo ""
echo_info "Migration complete! 🎉"