#!/bin/bash

# CityPulse API Deployment Script for Google Cloud Run
# This script builds and deploys the FastAPI application to Cloud Run

set -e  # Exit on any error

# Configuration
PROJECT_ID=${PROJECT_ID:-"citypulse-21"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="citypulse-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if logged into gcloud
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not logged into gcloud. Please run 'gcloud auth login' first."
        exit 1
    fi
    
    print_status "Prerequisites check passed!"
}

# Set up gcloud configuration
setup_gcloud() {
    print_status "Setting up gcloud configuration..."
    
    gcloud config set project $PROJECT_ID
    gcloud config set run/region $REGION
    
    # Enable required APIs
    print_status "Enabling required APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    
    print_status "gcloud configuration complete!"
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    
    # Build the image using Cloud Build for better performance
    gcloud builds submit --tag $IMAGE_NAME .
    
    print_status "Docker image built successfully!"
}

# Deploy to Cloud Run
deploy_service() {
    print_status "Deploying to Cloud Run..."
    
    # Deploy the service
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --concurrency 80 \
        --max-instances 10 \
        --min-instances 0 \
        --timeout 300 \
        --set-env-vars "PROJECT_ID=${PROJECT_ID}" \
        --set-env-vars "GCP_REGION=${REGION}" \
        --port 8080
    
    print_status "Deployment complete!"
}

# Get service URL
get_service_url() {
    print_status "Getting service URL..."
    
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    print_status "Service deployed successfully!"
    print_status "Service URL: $SERVICE_URL"
    print_status "Health check: $SERVICE_URL/health"
    print_status "API docs: $SERVICE_URL/docs"
}

# Test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    
    # Test health endpoint
    if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
        print_status "Health check passed!"
    else
        print_warning "Health check failed. Service might still be starting up."
    fi
    
    # Test root endpoint
    if curl -f "$SERVICE_URL/" > /dev/null 2>&1; then
        print_status "Root endpoint test passed!"
    else
        print_warning "Root endpoint test failed."
    fi
}

# Main deployment function
main() {
    print_status "Starting CityPulse API deployment..."
    
    check_prerequisites
    setup_gcloud
    build_image
    deploy_service
    get_service_url
    test_deployment
    
    print_status "Deployment completed successfully!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Update your frontend configuration to use the new API URL"
    print_status "2. Configure Firebase Authentication"
    print_status "3. Set up API keys for public endpoints"
    print_status "4. Configure monitoring and alerting"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "build")
        check_prerequisites
        setup_gcloud
        build_image
        ;;
    "test")
        test_deployment
        ;;
    "url")
        get_service_url
        ;;
    *)
        echo "Usage: $0 [deploy|build|test|url]"
        echo "  deploy: Full deployment (default)"
        echo "  build:  Build Docker image only"
        echo "  test:   Test existing deployment"
        echo "  url:    Get service URL"
        exit 1
        ;;
esac
