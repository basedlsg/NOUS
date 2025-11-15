#!/usr/bin/env bash
set -euo pipefail

# This script deploys the spatial experiment to Google Cloud Run.

# Check if PROJECT_ID is set
if [ -z "${PROJECT_ID:-}" ]; then
    echo "Error: PROJECT_ID environment variable is not set"
    echo "Please set PROJECT_ID to your Google Cloud project ID"
    exit 1
fi

echo "Deploying spatial experiment to Google Cloud Run..."
echo "Project ID: $PROJECT_ID"

# 1. Build the Docker image
echo "Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/spatial-experiment:latest .

# 2. Push the image to Google Container Registry
echo "Pushing image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/spatial-experiment:latest

# 3. Deploy the image to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy spatial-experiment \
    --image gcr.io/$PROJECT_ID/spatial-experiment:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10

echo "✅ Deployment completed successfully!"
echo "The spatial experiment is now running on Google Cloud Run"