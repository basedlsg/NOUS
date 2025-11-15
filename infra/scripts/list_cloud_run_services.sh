#!/bin/bash

# This script lists the Cloud Run services.

gcloud run services list --region=${REGION} --platform=managed

echo "Listing Cloud Run services..."