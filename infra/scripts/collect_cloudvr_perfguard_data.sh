#!/bin/bash

# This script collects data for the CloudVR-PerfGuard component.

# 1. GCS:
gsutil ls gs://${BUCKET}/cloudvr/ > results/cloudvr_perfguard_gcs_objects.txt
gsutil cp -m gs://${BUCKET}/cloudvr/research_outputs/* ./research_outputs/

# 2. BigQuery:
bq ls ${DATASET} > results/cloudvr_perfguard_bigquery_datasets.txt
bq show --format=prettyjson ${DATASET}.vr_runs | jq > results/cloudvr_perfguard_bigquery_vr_runs.json

# KPIs:
bq query --use_legacy_sql=false "SELECT app, COUNT(*) runs, AVG(fps) avg_fps, AVG(frame_time_ms) avg_ft, AVG(comfort_score) avg_comfort FROM `${PROJECT_ID}.${DATASET}.vr_runs` GROUP BY app" > results/cloudvr_perfguard_bigquery_kpis.txt

# 3. Logging:
gcloud logging read 'resource.type="cloud_run_revision" AND textPayload:CloudVR' --limit=200 --format=json | jq '.[].textPayload' > results/cloudvr_perfguard_cloud_run_logs.json

echo "Collecting CloudVR-PerfGuard data..."