#!/bin/bash

# This script sets the environment variables and runs all the other scripts.

export PROJECT_ID=my-project
export REGION=us-central1
export BUCKET=my-bucket
export DATASET=my_dataset
export PADRES_SERVICE=padres-service

gcloud config set project $PROJECT_ID

chmod +x infra/scripts/*.sh

#infra/scripts/authenticate.sh
#infra/scripts/set_project_id.sh
infra/scripts/list_gcs_buckets.sh
infra/scripts/list_bigquery_datasets.sh
infra/scripts/list_logging_sources.sh
infra/scripts/list_cloud_run_services.sh
infra/scripts/discover_firestore_export_targets.sh
infra/scripts/list_pubsub_topics_subscriptions.sh
infra/scripts/collect_ai_society_data.sh
infra/scripts/collect_spatial_ai_lab_data.sh
infra/scripts/collect_warehouse_padres_factory_data.sh
infra/scripts/collect_cloudvr_perfguard_data.sh
infra/scripts/collect_evolution_data.sh
infra/scripts/regenerate_ai_society_rollups.sh
infra/scripts/generate_reports.sh

#python3 scripts/summarize_components.py --outdir results/component_reports --html results/component_reports/index.html --pdf results/component_reports/overview.pdf

echo "All scripts have been executed."