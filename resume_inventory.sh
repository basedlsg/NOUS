#!/bin/bash
# Navigate to your project directory
cd /Users/carlos/NOUS

# Set up environment
export PROJECT_IDS="seven-l-prod"
export BILLING_QUOTA_PROJECT="seven-l-prod"
export BQ_PROJECT="seven-l-prod"
export SA_NAME="central-inventory-sa"
export SA_EMAIL="${SA_NAME}@${BQ_PROJECT}.iam.gserviceaccount.com"

# Ensure ADC is configured
unset GOOGLE_APPLICATION_CREDENTIALS
gcloud auth application-default print-access-token >/dev/null 2>&1 || gcloud auth application-default login --quiet

# Check Current Status
gsutil ls -r gs://central-inventory-20251012-17126/ | head -20

# Check if script is still running
ps aux | grep gcp_all_in_one.sh

# Continue/Resume the Inventory Script
unset GOOGLE_APPLICATION_CREDENTIALS
./gcp_all_in_one.sh 2>&1 | tee -a inventory_output_$(date +%Y%m%d_%H%M%S).log

# Alternative: Check Cloud Build Status
gcloud builds log ab310395-e31d-46a6-93e5-4d5027aaa4e4 --project=seven-l-prod

# Or check all recent builds
gcloud builds list --project=seven-l-prod --limit=5

# If Script Completed - Access Results
grep -A 5 "===== FINAL RESULT =====" inventory_output_*.log

# If found, extract the signed URL and SQL
grep "SIGNED_URL=" inventory_output_*.log
grep "SQL=" inventory_output_*.log

exit 0