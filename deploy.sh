#!/bin/bash

# Google Cloud Run Deployment Script for LINE HR Bot
# Make sure to set these variables before running

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"asia-southeast1"}
SERVICE_ACCOUNT=${SERVICE_ACCOUNT:-"cloudrun-service@${PROJECT_ID}.iam.gserviceaccount.com"}

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

# Check if required environment variables are set
check_env() {
    if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "your-project-id" ]]; then
        echo_error "Please set PROJECT_ID environment variable"
        exit 1
    fi
    
    echo_info "Using PROJECT_ID: $PROJECT_ID"
    echo_info "Using REGION: $REGION"
}

# Authenticate with Google Cloud
authenticate() {
    echo_info "Authenticating with Google Cloud..."
    gcloud auth configure-docker gcr.io --quiet
    gcloud config set project $PROJECT_ID
}

# Enable required APIs
enable_apis() {
    echo_info "Enabling required Google Cloud APIs..."
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        containerregistry.googleapis.com \
        secretmanager.googleapis.com \
        --project=$PROJECT_ID
}

# Create secrets (if they don't exist)
create_secrets() {
    echo_info "Creating secrets in Secret Manager..."
    
    secrets=(
        "LINE_CHANNEL_ACCESS_TOKEN"
        "LINE_CHANNEL_SECRET"
        "GEMINI_API_KEY"
        "SUPABASE_URL"
        "SUPABASE_ANON_KEY"
        "TELEGRAM_BOT_TOKEN"
        "TELEGRAM_CHAT_ID"
    )
    
    for secret in "${secrets[@]}"; do
        if ! gcloud secrets describe $secret --project=$PROJECT_ID >/dev/null 2>&1; then
            echo_warn "Secret $secret does not exist. Creating with placeholder..."
            echo "REPLACE_WITH_ACTUAL_VALUE" | gcloud secrets create $secret --data-file=- --project=$PROJECT_ID
            echo_info "✓ Created secret: $secret (remember to update with actual value)"
        else
            echo_info "✓ Secret already exists: $secret"
        fi
    done
}

# Build and push backend
build_backend() {
    echo_info "Building backend Docker image..."
    cd backend
    
    docker build \
        -f Dockerfile.cloudrun \
        -t gcr.io/$PROJECT_ID/line-hr-bot-backend:latest \
        .
    
    echo_info "Pushing backend image to Container Registry..."
    docker push gcr.io/$PROJECT_ID/line-hr-bot-backend:latest
    
    cd ..
}

# Build and push frontend
build_frontend() {
    echo_info "Building frontend Docker image..."
    cd frontend
    
    docker build \
        -f Dockerfile.cloudrun \
        -t gcr.io/$PROJECT_ID/line-hr-bot-frontend:latest \
        .
    
    echo_info "Pushing frontend image to Container Registry..."
    docker push gcr.io/$PROJECT_ID/line-hr-bot-frontend:latest
    
    cd ..
}

# Deploy backend service
deploy_backend() {
    echo_info "Deploying backend to Cloud Run..."
    
    # Replace PROJECT_ID in config file
    sed "s/PROJECT_ID/$PROJECT_ID/g" cloudrun-backend.yaml > cloudrun-backend-temp.yaml
    
    gcloud run services replace cloudrun-backend-temp.yaml \
        --region=$REGION \
        --project=$PROJECT_ID
    
    # Clean up temp file
    rm cloudrun-backend-temp.yaml
    
    echo_info "✅ Backend deployed successfully"
}

# Deploy frontend service
deploy_frontend() {
    echo_info "Deploying frontend to Cloud Run..."
    
    # Get backend service URL
    BACKEND_URL=$(gcloud run services describe line-hr-bot-backend \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.url)")
    
    # Replace variables in config file
    sed -e "s/PROJECT_ID/$PROJECT_ID/g" \
        -e "s|https://line-hr-bot-backend-HASH-uc.a.run.app|$BACKEND_URL|g" \
        cloudrun-frontend.yaml > cloudrun-frontend-temp.yaml
    
    gcloud run services replace cloudrun-frontend-temp.yaml \
        --region=$REGION \
        --project=$PROJECT_ID
    
    # Clean up temp file
    rm cloudrun-frontend-temp.yaml
    
    echo_info "✅ Frontend deployed successfully"
}

# Set IAM permissions
set_permissions() {
    echo_info "Setting IAM permissions..."
    
    # Allow public access to services
    gcloud run services add-iam-policy-binding line-hr-bot-backend \
        --region=$REGION \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --project=$PROJECT_ID
    
    gcloud run services add-iam-policy-binding line-hr-bot-frontend \
        --region=$REGION \
        --member="allUsers" \
        --role="roles/run.invoker" \
        --project=$PROJECT_ID
    
    echo_info "✅ IAM permissions set"
}

# Get service URLs
get_urls() {
    echo_info "Getting service URLs..."
    
    BACKEND_URL=$(gcloud run services describe line-hr-bot-backend \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.url)")
    
    FRONTEND_URL=$(gcloud run services describe line-hr-bot-frontend \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.url)")
    
    echo_info "🎉 Deployment completed successfully!"
    echo ""
    echo_info "📱 Backend URL:  $BACKEND_URL"
    echo_info "🌐 Frontend URL: $FRONTEND_URL"
    echo ""
    echo_warn "⚠️  Don't forget to:"
    echo_warn "   1. Update secrets in Secret Manager with actual values"
    echo_warn "   2. Update LINE webhook URL to: $BACKEND_URL/webhook"
    echo_warn "   3. Configure CORS settings if needed"
}

# Main deployment function
main() {
    echo_info "🚀 Starting Google Cloud Run deployment..."
    
    check_env
    authenticate
    enable_apis
    create_secrets
    build_backend
    build_frontend
    deploy_backend
    deploy_frontend
    set_permissions
    get_urls
}

# Help function
show_help() {
    echo "Google Cloud Run Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [OPTIONS]"
    echo ""
    echo "Environment Variables:"
    echo "  PROJECT_ID    - Google Cloud Project ID (required)"
    echo "  REGION        - Deployment region (default: asia-southeast1)"
    echo ""
    echo "Examples:"
    echo "  PROJECT_ID=my-project ./deploy.sh"
    echo "  PROJECT_ID=my-project REGION=asia-southeast1 ./deploy.sh"
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main
        ;;
esac