#!/usr/bin/env bash
set -euo pipefail

# Autonomous Spatial Experiment Cloud Deployment Script
# This script deploys the spatial experiment to run autonomously in Google Cloud

echo "🚀 AUTONOMOUS SPATIAL EXPERIMENT CLOUD DEPLOYMENT"
echo "=================================================="

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
docker build -t gcr.io/$PROJECT_ID/autonomous-spatial-experiment:latest .

echo "📤 Pushing image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/autonomous-spatial-experiment:latest

echo "✅ Image pushed successfully"

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy autonomous-spatial-experiment \
    --image gcr.io/$PROJECT_ID/autonomous-spatial-experiment:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 5 \
    --set-env-vars "EXPERIMENT_MODE=autonomous,NUM_TRIALS=1000,OUTPUT_BUCKET=gs://$PROJECT_ID-spatial-experiment-results"

echo "✅ Deployment completed!"

# Get the service URL
SERVICE_URL=$(gcloud run services describe autonomous-spatial-experiment \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)')

echo ""
echo "🎉 AUTONOMOUS EXPERIMENT DEPLOYED SUCCESSFULLY!"
echo "=============================================="
echo "📊 Service URL: $SERVICE_URL"
echo "📁 Results will be saved to: gs://$PROJECT_ID-spatial-experiment-results"
echo ""
echo "🧪 The experiment will run autonomously and generate results"
echo "📈 You can monitor progress via the Cloud Run logs"
echo ""
echo "To view logs: gcloud run logs tail autonomous-spatial-experiment --region us-central1"
echo "To trigger experiment: curl $SERVICE_URL"





