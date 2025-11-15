#!/bin/bash
set -e

echo "🚀 Deploying AMIEN to Google Cloud Platform (without Cloud Scheduler)"
echo "Project ID: amien-research-pipeline"
echo "Region: us-central1"

# Set project
gcloud config set project amien-research-pipeline

# Enable required APIs (excluding scheduler for now)
echo "📡 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable monitoring.googleapis.com

# Create secrets (you'll need to add the actual API keys)
echo "🔐 Creating secrets..."
echo "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- || echo "Secret already exists, updating..."
echo "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=- || echo "Failed to update secret"
echo "$PERPLEXITY_API_KEY" | gcloud secrets create perplexity-api-key --data-file=- || echo "Secret already exists, updating..."
echo "$PERPLEXITY_API_KEY" | gcloud secrets versions add perplexity-api-key --data-file=- || echo "Failed to update secret"

# Build and deploy container images
echo "🏗️ Building container images..."
cd gcp_deployment

# Prepare deployment files
echo "📁 Preparing deployment files..."

# Copy necessary files if they don't exist
if [ ! -f "requirements.txt" ]; then
    cp ../requirements_production.txt requirements.txt
fi

if [ ! -f "production_demo.py" ]; then
    cp ../production_demo.py .
fi

# Copy research modules
cp -r ../ai_research . 2>/dev/null || echo "ai_research directory not found, skipping"
cp -r ../evolution . 2>/dev/null || echo "evolution directory not found, skipping"
cp -r ../funsearch . 2>/dev/null || echo "funsearch directory not found, skipping"
cp -r ../AI-Scientist . 2>/dev/null || echo "AI-Scientist directory not found, skipping"

# Use the existing Dockerfile.api
if [ -f "Dockerfile.api" ]; then
    cp Dockerfile.api Dockerfile
else
    echo "❌ Dockerfile.api not found, creating basic Dockerfile"
    cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main_api.py"]
EOF
fi

# Build API service using the new Dockerfile
gcloud builds submit --tag gcr.io/amien-research-pipeline/padres-app --file padres_container/Dockerfile .

# Deploy Cloud Run services
echo "☁️ Deploying Cloud Run services..."
gcloud run deploy padres-app \
    --image gcr.io/amien-research-pipeline/padres-app \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 100 \
    --set-env-vars="GCP_PROJECT_ID=amien-research-pipeline,AMIEN_ENV=production"

cd ..

echo "✅ PADRES core deployment complete!"
echo "🌐 API URL: $(gcloud run services describe padres-app --region us-central1 --format='value(status.url)')"
echo "📊 Monitor at: https://console.cloud.google.com/monitoring"

echo ""
echo "⚠️  Note: Cloud Scheduler was skipped due to permission issues."
echo "   You can enable it manually in the GCP Console:"
echo "   1. Go to https://console.cloud.google.com/cloudscheduler"
echo "   2. Enable the API if prompted"
echo "   3. Create jobs manually or run the scheduler setup script"

echo ""
echo "🔧 Next steps:"
echo "   1. Update API keys in secrets: gcloud secrets versions add gemini-api-key --data-file=<your-key-file>"
echo "   2. Test the deployment: curl \$(gcloud run services describe padres-app --region us-central1 --format='value(status.url)')/health"
echo "   3. Set up Cloud Scheduler manually if needed"
