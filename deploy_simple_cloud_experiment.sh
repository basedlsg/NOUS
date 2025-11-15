#!/usr/bin/env bash
set -euo pipefail

# Simple Cloud Experiment Deployment Script
# This script deploys the spatial experiment to run in Google Cloud Run

echo "🚀 SIMPLE CLOUD SPATIAL EXPERIMENT DEPLOYMENT"
echo "============================================="

# Check if PROJECT_ID is set
if [ -z "${PROJECT_ID:-}" ]; then
    echo "❌ Error: PROJECT_ID environment variable is not set"
    echo "Please set PROJECT_ID to your Google Cloud project ID"
    echo "Example: export PROJECT_ID=your-project-id"
    exit 1
fi

echo "📋 Project ID: $PROJECT_ID"

# Check if gcloud is authenticated
echo "🔐 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null; then
    echo "❌ Not authenticated with gcloud. Please run: gcloud auth login"
    exit 1
fi

echo "✅ Authentication verified"

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo "✅ APIs enabled"

# Build and push Docker image
echo "🐳 Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/simple-spatial-experiment:latest .

echo "📤 Pushing image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/simple-spatial-experiment:latest

echo "✅ Image pushed successfully"

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy simple-spatial-experiment \
    --image gcr.io/$PROJECT_ID/simple-spatial-experiment:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 3600 \
    --max-instances 3 \
    --set-env-vars "EXPERIMENT_MODE=cloud,NUM_TRIALS=1000,LLM_PROVIDER=simulation"

echo "✅ Deployment completed!"

# Get the service URL
SERVICE_URL=$(gcloud run services describe simple-spatial-experiment \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)')

echo ""
echo "🎉 CLOUD EXPERIMENT DEPLOYED SUCCESSFULLY!"
echo "=========================================="
echo "📊 Service URL: $SERVICE_URL"
echo ""
echo "🧪 The experiment is now running autonomously in the cloud"
echo "📈 You can monitor progress via the Cloud Run logs"
echo ""
echo "To view logs: gcloud run logs tail simple-spatial-experiment --region us-central1"
echo "To trigger experiment: curl $SERVICE_URL"
echo "To run experiment locally: NUM_TRIALS=1000 python autonomous_spatial_experiment.py"





