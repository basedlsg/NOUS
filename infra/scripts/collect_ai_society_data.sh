#!/bin/bash

# This script collects data for the AI Society component.

# 1. Cloud Run logs for society API/observer:
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="<SERVICE_NAME>"' --limit=200 --format='value(textPayload)' > results/ai_society_cloud_run_logs.txt

# 2. GCS snapshots (look for prefixes like live_observations_*.json):
gsutil ls gs://${BUCKET}/society/ > results/ai_society_gcs_snapshots.txt
gsutil cp -m gs://${BUCKET}/society/live_observations_*.json ./cloud_obs/

# 3. BigQuery events (if wired): enumerate datasets and look for tables with names like llm_events, trial_results, observations:
bq ls ${DATASET} > results/ai_society_bigquery_datasets.txt
bq show --format=prettyjson ${DATASET}.llm_events | jq > results/ai_society_bigquery_llm_events.json

# Example query:
bq query --use_legacy_sql=false "SELECT model, COUNT(*) n, AVG(latency_ms) avg_latency FROM \`${PROJECT_ID}.${DATASET}.llm_events\` GROUP BY model ORDER BY n DESC" > results/ai_society_bigquery_query_results.txt

echo "Collecting AI Society data..."