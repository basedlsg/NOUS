#!/bin/bash

# A script to automate the deployment of the PADRES application to Google Cloud Platform.
# This script builds the Docker image, pushes it to GCR, and submits a job to AI Platform.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# The name of the application/image.
APP_NAME="padres-app"

# --- Argument Parsing ---
# Check if all required arguments are provided.
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <PROJECT_ID> <IMAGE_TAG> <NUM_TURNS> <GCS_OUTPUT_PATH>"
    echo "Example: ./deploy_to_gcp.sh my-gcp-project v1.0 100 gs://my-bucket/padres/results"
    exit 1
fi

PROJECT_ID="$1"
IMAGE_TAG="$2"
NUM_TURNS="$3"
GCS_OUTPUT_PATH="$4"
IMAGE_URI="gcr.io/${PROJECT_ID}/${APP_NAME}:${IMAGE_TAG}"

# --- Script Execution ---
echo "Starting PADRES deployment process..."
echo "  Project ID:        ${PROJECT_ID}"
echo "  Image Tag:         ${IMAGE_TAG}"
echo "  Image URI:         ${IMAGE_URI}"
echo "  Number of Turns:   ${NUM_TURNS}"
echo "  GCS Output Path:   ${GCS_OUTPUT_PATH}"

# 1. Build the Docker image
echo ""
echo "--> Building Docker image..."
docker build -t "${IMAGE_URI}" .
if [ $? -ne 0 ]; then
    echo "ERROR: Docker image build failed."
    exit 1
fi
echo "Docker image built successfully."

# 2. Push the image to Google Container Registry (GCR)
echo ""
echo "--> Pushing image to GCR..."
# Ensure you have authenticated with gcloud and configured Docker:
# gcloud auth configure-docker
docker push "${IMAGE_URI}"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to push image to GCR."
    exit 1
fi
echo "Image pushed to GCR successfully."

# 3. Submit the job to Google AI Platform
echo ""
echo "--> Submitting job to Google AI Platform..."
# A unique job name is required for each run.
# Sanitize the image tag for the job name: remove all non-alphanumeric characters.
CLEANED_IMAGE_TAG=$(echo "${IMAGE_TAG}" | sed 's/[^a-zA-Z0-9]/_/g')
JOB_NAME="padres_${CLEANED_IMAGE_TAG}_$(date +%Y%m%d_%H%M%S)"
# The output file for the job, located in the specified GCS bucket.
OUTPUT_FILE="${GCS_OUTPUT_PATH}/${JOB_NAME}/trajectories.jsonl"

# The --region can be changed to any region that supports Vertex AI Jobs.
# Arguments are passed to the container's entrypoint.
gcloud ai custom-jobs create \
    --display-name="${JOB_NAME}" \
    --worker-pool-spec=machine-type=n1-standard-4,replica-count=1,container-image-uri="${IMAGE_URI}" \
    --region="us-central1" \
    --args="--num_turns=${NUM_TURNS}" \
    --args="--output_file=${OUTPUT_FILE}"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to submit job to AI Platform."
    exit 1
fi

echo ""
echo "----------------------------------------------------"
echo "Deployment script finished successfully!"
echo "  Job '${JOB_NAME}' submitted to Google AI Platform."
echo "  Results will be saved to: ${OUTPUT_FILE}"
echo "  Monitor job status with: gcloud ai custom-jobs describe ${JOB_NAME} --region=us-central1"
echo "  View logs with: gcloud ai custom-jobs stream-logs ${JOB_NAME} --region=us-central1"
echo "----------------------------------------------------"