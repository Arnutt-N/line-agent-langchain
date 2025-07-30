#!/bin/bash

# Deployment Validation Script for Google Cloud Run
# This script validates the deployment and performs basic health checks

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"asia-southeast1"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

echo_header() {
    echo -e "${BLUE}[====== $1 ======]${NC}"
}

# Check if required tools are installed
check_prerequisites() {
    echo_header "Checking Prerequisites"
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        echo_error "gcloud CLI is not installed or not in PATH"
        exit 1
    fi
    echo_info "✅ gcloud CLI is available"
    
    # Check docker
    if ! command -v docker &> /dev/null; then
        echo_error "Docker is not installed or not in PATH"
        exit 1
    fi
    echo_info "✅ Docker is available"
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        echo_error "curl is not installed or not in PATH"
        exit 1
    fi
    echo_info "✅ curl is available"
    
    # Check project ID
    if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "your-project-id" ]]; then
        echo_error "Please set PROJECT_ID environment variable"
        exit 1
    fi
    echo_info "✅ PROJECT_ID is set: $PROJECT_ID"
}

# Validate Google Cloud configuration
validate_gcloud_config() {
    echo_header "Validating Google Cloud Configuration"
    
    # Check authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
        echo_error "Not authenticated with Google Cloud. Run: gcloud auth login"
        exit 1
    fi
    echo_info "✅ Authenticated with Google Cloud"
    
    # Check project access
    if ! gcloud projects describe $PROJECT_ID > /dev/null 2>&1; then
        echo_error "Cannot access project $PROJECT_ID. Check project ID and permissions."
        exit 1
    fi
    echo_info "✅ Project $PROJECT_ID is accessible"
    
    # Check enabled APIs
    required_apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "containerregistry.googleapis.com"
        "secretmanager.googleapis.com"
    )
    
    for api in "${required_apis[@]}"; do
        if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
            echo_info "✅ API enabled: $api"
        else
            echo_warn "❌ API not enabled: $api"
        fi
    done
}

# Check secrets
validate_secrets() {
    echo_header "Validating Secrets"
    
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
        if gcloud secrets describe $secret --project=$PROJECT_ID > /dev/null 2>&1; then
            # Check if secret has actual value (not placeholder)
            secret_value=$(gcloud secrets versions access latest --secret="$secret" --project=$PROJECT_ID)
            if [[ "$secret_value" == "REPLACE_WITH_ACTUAL_VALUE" ]]; then
                echo_warn "⚠️  Secret $secret has placeholder value"
            else
                echo_info "✅ Secret $secret is configured"
            fi
        else
            echo_warn "❌ Secret $secret does not exist"
        fi
    done
}

# Check Cloud Run services
validate_services() {
    echo_header "Validating Cloud Run Services"
    
    services=("line-hr-bot-backend" "line-hr-bot-frontend")
    
    for service in "${services[@]}"; do
        if gcloud run services describe $service --region=$REGION --project=$PROJECT_ID > /dev/null 2>&1; then
            echo_info "✅ Service deployed: $service"
            
            # Get service URL
            service_url=$(gcloud run services describe $service \
                --region=$REGION \
                --project=$PROJECT_ID \
                --format="value(status.url)")
            
            echo_info "   URL: $service_url"
            
            # Test health endpoint
            if curl -s -f -m 10 "$service_url/health" > /dev/null; then
                echo_info "   ✅ Health check passed"
            else
                echo_warn "   ❌ Health check failed"
            fi
        else
            echo_error "❌ Service not found: $service"
        fi
    done
}

# Test API endpoints
test_api_endpoints() {
    echo_header "Testing API Endpoints"
    
    # Get backend URL
    backend_url=$(gcloud run services describe line-hr-bot-backend \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.url)" 2>/dev/null || echo "")
    
    if [[ -z "$backend_url" ]]; then
        echo_error "Backend service URL not found"
        return 1
    fi
    
    echo_info "Testing backend at: $backend_url"
    
    # Test root endpoint
    if curl -s -f -m 10 "$backend_url/" > /dev/null; then
        echo_info "✅ Root endpoint responds"
    else
        echo_warn "❌ Root endpoint failed"
    fi
    
    # Test health endpoint with detailed response
    health_response=$(curl -s -m 10 "$backend_url/health")
    if [[ $? -eq 0 ]]; then
        echo_info "✅ Health endpoint responds"
        
        # Parse health status if JSON
        if echo "$health_response" | jq -e '.status' > /dev/null 2>&1; then
            status=$(echo "$health_response" | jq -r '.status')
            echo_info "   Status: $status"
            
            # Show component health
            if echo "$health_response" | jq -e '.components' > /dev/null 2>&1; then
                echo "$health_response" | jq -r '.components | to_entries[] | "   \(.key): \(.value.status // "unknown")"'
            fi
        fi
    else
        echo_warn "❌ Health endpoint failed"
    fi
    
    # Test users endpoint
    if curl -s -f -m 10 "$backend_url/api/users" > /dev/null; then
        echo_info "✅ Users API endpoint responds"
    else
        echo_warn "❌ Users API endpoint failed"
    fi
}

# Check container images
validate_images() {
    echo_header "Validating Container Images"
    
    images=("line-hr-bot-backend" "line-hr-bot-frontend")
    
    for image in "${images[@]}"; do
        if gcloud container images list-tags "gcr.io/$PROJECT_ID/$image" --limit=1 --format="value(digest)" > /dev/null 2>&1; then
            echo_info "✅ Container image exists: $image"
            
            # Get latest tag info
            latest_info=$(gcloud container images list-tags "gcr.io/$PROJECT_ID/$image" --limit=1 --format="table(digest[0:12],timestamp)")
            echo_info "   Latest: $(echo "$latest_info" | tail -1)"
        else
            echo_warn "❌ Container image not found: $image"
        fi
    done
}

# Check logs for errors
check_logs() {
    echo_header "Checking Recent Logs"
    
    services=("line-hr-bot-backend" "line-hr-bot-frontend")
    
    for service in "${services[@]}"; do
        echo_info "Checking logs for: $service"
        
        # Get recent error logs
        error_count=$(gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=$service AND severity>=ERROR" \
            --limit=10 \
            --format="value(timestamp)" \
            --project=$PROJECT_ID 2>/dev/null | wc -l)
        
        if [[ $error_count -gt 0 ]]; then
            echo_warn "   ⚠️  Found $error_count recent error(s)"
        else
            echo_info "   ✅ No recent errors"
        fi
    done
}

# Performance and resource check
check_performance() {
    echo_header "Performance and Resource Check"
    
    services=("line-hr-bot-backend" "line-hr-bot-frontend")
    
    for service in "${services[@]}"; do
        echo_info "Checking $service performance..."
        
        # Get service configuration
        config=$(gcloud run services describe $service --region=$REGION --project=$PROJECT_ID --format=json 2>/dev/null)
        
        if [[ -n "$config" ]]; then
            memory=$(echo "$config" | jq -r '.spec.template.spec.containers[0].resources.limits.memory // "unknown"')
            cpu=$(echo "$config" | jq -r '.spec.template.spec.containers[0].resources.limits.cpu // "unknown"')
            concurrency=$(echo "$config" | jq -r '.spec.template.spec.containerConcurrency // "unknown"')
            
            echo_info "   Memory: $memory"
            echo_info "   CPU: $cpu"
            echo_info "   Concurrency: $concurrency"
        fi
    done
}

# Generate deployment report
generate_report() {
    echo_header "Deployment Validation Report"
    
    # Get service URLs
    backend_url=$(gcloud run services describe line-hr-bot-backend \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.url)" 2>/dev/null || echo "Not deployed")
    
    frontend_url=$(gcloud run services describe line-hr-bot-frontend \
        --region=$REGION \
        --project=$PROJECT_ID \
        --format="value(status.url)" 2>/dev/null || echo "Not deployed")
    
    echo ""
    echo_info "🎉 Validation completed!"
    echo ""
    echo_info "📱 Backend URL:   $backend_url"
    echo_info "🌐 Frontend URL:  $frontend_url"
    echo ""
    echo_info "📋 Next steps:"
    echo_info "   1. Update LINE webhook URL to: $backend_url/webhook"
    echo_info "   2. Update secrets with actual values if needed"
    echo_info "   3. Test LINE Bot functionality"
    echo_info "   4. Monitor logs and metrics in Cloud Console"
    echo ""
    echo_info "🔧 Useful commands:"
    echo_info "   View logs: gcloud logs read 'resource.type=cloud_run_revision' --limit=50"
    echo_info "   Update service: gcloud run services update SERVICE_NAME --region=$REGION"
    echo_info "   Delete service: gcloud run services delete SERVICE_NAME --region=$REGION"
}

# Main validation function
main() {
    echo_info "🚀 Starting deployment validation..."
    echo_info "Project: $PROJECT_ID"
    echo_info "Region: $REGION"
    echo ""
    
    check_prerequisites
    echo ""
    
    validate_gcloud_config
    echo ""
    
    validate_secrets
    echo ""
    
    validate_images
    echo ""
    
    validate_services
    echo ""
    
    test_api_endpoints
    echo ""
    
    check_logs
    echo ""
    
    check_performance
    echo ""
    
    generate_report
}

# Help function
show_help() {
    echo "Deployment Validation Script"
    echo ""
    echo "Usage: ./validate-deployment.sh [OPTIONS]"
    echo ""
    echo "Environment Variables:"
    echo "  PROJECT_ID    - Google Cloud Project ID (required)"
    echo "  REGION        - Deployment region (default: asia-southeast1)"
    echo ""
    echo "Examples:"
    echo "  PROJECT_ID=my-project ./validate-deployment.sh"
    echo "  PROJECT_ID=my-project REGION=asia-southeast1 ./validate-deployment.sh"
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