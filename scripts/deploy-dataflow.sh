#!/bin/bash

# CityPulse Dataflow Deployment Script
# Deploys Apache Beam pipelines to Google Cloud Dataflow

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
DATASET="citypulse_analytics"
CONTAINER_IMAGE="gcr.io/citypulse-21/citypulse-secure:latest"
TEMP_BUCKET="citypulse-21-temp-inspired-rodent"
STAGING_BUCKET="citypulse-21-staging-inspired-rodent"

print_status "🚀 CITYPULSE DATAFLOW DEPLOYMENT"
echo "=================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Container: $CONTAINER_IMAGE"
echo ""

# Step 1: Verify prerequisites
print_status "Step 1: Verifying prerequisites..."

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not authenticated with gcloud. Please run 'gcloud auth login'"
    exit 1
fi

# Check if container exists
if ! gcloud container images describe "$CONTAINER_IMAGE" &> /dev/null; then
    print_error "Container image not found: $CONTAINER_IMAGE"
    exit 1
fi

print_success "Prerequisites verified"

# Step 2: Create Pub/Sub subscriptions
print_status "Step 2: Creating Pub/Sub subscriptions..."

TOPICS=("citypulse-iot_sensors-ingestion" "citypulse-citizen_reports-ingestion" "citypulse-twitter-ingestion" "citypulse-official_feeds-ingestion")

for topic in "${TOPICS[@]}"; do
    subscription="${topic}-subscription"
    
    # Check if subscription exists
    if gcloud pubsub subscriptions describe "$subscription" --project="$PROJECT_ID" &> /dev/null; then
        print_warning "Subscription $subscription already exists"
    else
        print_status "Creating subscription: $subscription"
        gcloud pubsub subscriptions create "$subscription" \
            --topic="$topic" \
            --project="$PROJECT_ID" \
            --ack-deadline=600
        print_success "Created subscription: $subscription"
    fi
done

# Step 3: Deploy IoT Pipeline
print_status "Step 3: Deploying IoT Data Pipeline..."

JOB_NAME="citypulse-iot-pipeline-$(date +%Y%m%d-%H%M%S)"

gcloud dataflow jobs run "$JOB_NAME" \
    --gcs-location="gs://dataflow-templates-$REGION/latest/flex/Python_Streaming_Template" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --parameters="^|^sdk_container_image=$CONTAINER_IMAGE|input_subscription=projects/$PROJECT_ID/subscriptions/citypulse-iot_sensors-ingestion-subscription|output_table=$PROJECT_ID:$DATASET.iot_data|temp_location=gs://$TEMP_BUCKET/temp|staging_location=gs://$STAGING_BUCKET/staging|setup_file=./setup.py|requirements_file=./requirements.txt|python_file_path=data_models/data_ingestion/iot_pipeline.py" \
    --max-workers=3 \
    --num-workers=1

print_success "IoT Pipeline deployed: $JOB_NAME"

# Step 4: Deploy Citizen Reports Pipeline
print_status "Step 4: Deploying Citizen Reports Pipeline..."

JOB_NAME="citypulse-citizen-reports-$(date +%Y%m%d-%H%M%S)"

gcloud dataflow jobs run "$JOB_NAME" \
    --gcs-location="gs://dataflow-templates-$REGION/latest/flex/Python_Streaming_Template" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --parameters="^|^sdk_container_image=$CONTAINER_IMAGE|input_subscription=projects/$PROJECT_ID/subscriptions/citypulse-citizen_reports-ingestion-subscription|output_table=$PROJECT_ID:$DATASET.events|temp_location=gs://$TEMP_BUCKET/temp|staging_location=gs://$STAGING_BUCKET/staging|setup_file=./setup.py|requirements_file=./requirements.txt|python_file_path=data_models/data_ingestion/citizen_report_pipeline.py" \
    --max-workers=3 \
    --num-workers=1

print_success "Citizen Reports Pipeline deployed: $JOB_NAME"

# Step 5: Display deployment status
print_status "Step 5: Checking deployment status..."

echo ""
print_success "🎉 DATAFLOW DEPLOYMENT COMPLETED!"
echo ""
echo "📋 DEPLOYED PIPELINES:"
echo "======================"
gcloud dataflow jobs list --region="$REGION" --project="$PROJECT_ID" --filter="state=Running" --format="table(name,type,state,createTime)"

echo ""
echo "🔍 MONITORING COMMANDS:"
echo "======================="
echo "# View running jobs"
echo "gcloud dataflow jobs list --region=$REGION --filter='state=Running'"
echo ""
echo "# Monitor job logs"
echo "gcloud dataflow jobs show JOB_ID --region=$REGION"
echo ""
echo "# Check BigQuery data"
echo "bq query --use_legacy_sql=false 'SELECT COUNT(*) as total_records FROM \`$PROJECT_ID.$DATASET.iot_data\`'"
echo ""
echo "📊 NEXT STEPS:"
echo "=============="
echo "1. Test data ingestion by publishing to Pub/Sub topics"
echo "2. Monitor job performance in Cloud Console"
echo "3. Verify data appears in BigQuery tables"

print_success "Dataflow deployment script completed! 🚀"
