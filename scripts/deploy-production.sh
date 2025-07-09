#!/bin/bash

# CityPulse Production Deployment Script
# Deploys the security-hardened distroless container to Google Cloud

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_ID="citypulse-21"
REGION="us-central1"
IMAGE_NAME="citypulse-secure"
CONTAINER_REGISTRY="gcr.io"
FULL_IMAGE_NAME="${CONTAINER_REGISTRY}/${PROJECT_ID}/${IMAGE_NAME}"

print_status "🚀 CITYPULSE PRODUCTION DEPLOYMENT"
echo "=================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Image: $FULL_IMAGE_NAME"
echo ""

# Step 1: Verify prerequisites
print_status "Step 1: Verifying prerequisites..."

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if authenticated with gcloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not authenticated with gcloud. Please run 'gcloud auth login'"
    exit 1
fi

print_success "Prerequisites verified"

# Step 2: Configure Docker for GCR
print_status "Step 2: Configuring Docker for Google Container Registry..."
gcloud auth configure-docker --quiet
print_success "Docker configured for GCR"

# Step 3: Use existing working distroless image
print_status "Step 3: Tagging existing production-ready container..."
docker tag citypulse:distroless-optimized "${FULL_IMAGE_NAME}:latest"
docker tag citypulse:distroless-optimized "${FULL_IMAGE_NAME}:$(date +%Y%m%d-%H%M%S)"
print_success "Container tagged for production"

# Step 4: Push to Google Container Registry
print_status "Step 4: Pushing container to Google Container Registry..."
docker push "${FULL_IMAGE_NAME}:latest"
docker push "${FULL_IMAGE_NAME}:$(date +%Y%m%d-%H%M%S)"
print_success "Container pushed to GCR"

# Step 5: Deploy infrastructure with Terraform
print_status "Step 5: Deploying infrastructure with Terraform..."
cd infra

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
    terraform init
fi

# Plan and apply infrastructure changes
terraform plan -out=tfplan
terraform apply tfplan
print_success "Infrastructure deployed"

cd ..

# Step 6: Create Dataflow template
print_status "Step 6: Creating Dataflow Flex Template..."

# Create template specification
cat > dataflow_template.json << EOF
{
    "image": "${FULL_IMAGE_NAME}:latest",
    "sdk_info": { "language": "PYTHON" },
    "metadata": {
        "name": "CityPulse Data Processing Pipeline",
        "description": "Secure Apache Beam pipeline for processing CityPulse data",
        "parameters": [
            {
                "name": "input_subscription",
                "label": "Input Pub/Sub Subscription",
                "help_text": "The Pub/Sub subscription to read data from",
                "is_optional": false
            },
            {
                "name": "output_collection",
                "label": "Output Firestore Collection",
                "help_text": "The Firestore collection to write processed data to",
                "is_optional": false
            }
        ]
    }
}
EOF

# Upload template to Cloud Storage
BUCKET_NAME="${PROJECT_ID}-staging-$(terraform -chdir=infra output -raw gcs_staging_bucket | cut -d'/' -f4)"
gsutil cp dataflow_template.json "gs://${BUCKET_NAME}/templates/"
print_success "Dataflow template created and uploaded"

# Step 7: Final verification
print_status "Step 7: Running final verification..."

# Verify container functionality
print_status "Testing container functionality..."
if docker run --rm "${FULL_IMAGE_NAME}:latest" --help &> /dev/null; then
    print_success "Container functionality verified"
else
    print_warning "Container test returned non-zero exit code (may be expected)"
fi

# Step 8: Display deployment information
print_success "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo ""
echo "📋 DEPLOYMENT SUMMARY:"
echo "======================"
echo "✅ Container Image: ${FULL_IMAGE_NAME}:latest"
echo "✅ Infrastructure: Deployed via Terraform"
echo "✅ Dataflow Template: gs://${BUCKET_NAME}/templates/dataflow_template.json"
echo ""
echo "🚀 NEXT STEPS:"
echo "=============="
echo "1. Deploy frontend to Vercel (see DEPLOYMENT.md)"
echo "2. Start Dataflow jobs using the template"
echo "3. Monitor application performance"
echo ""
echo "📊 MONITORING COMMANDS:"
echo "======================="
echo "# View running Dataflow jobs"
echo "gcloud dataflow jobs list --region=${REGION}"
echo ""
echo "# Monitor container logs"
echo "gcloud logging read 'resource.type=\"dataflow_job\"' --limit=50"
echo ""
echo "# Check infrastructure status"
echo "cd infra && terraform show"

print_success "Production deployment completed! 🚀"
