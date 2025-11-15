#!/bin/bash

# This script collects data for the Warehouse/Padres/Factory component.

# 1. Cloud Run service for Padres API:
gcloud run services describe ${PADRES_SERVICE} --region=${REGION} --format=json > results/warehouse_padres_factory_cloud_run_service.json

# 2. Logs:
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="<PADRES_SERVICE>" AND severity>=ERROR' --limit=200 --format='value(textPayload)' > results/warehouse_padres_factory_cloud_run_logs.txt

# 3. BigQuery trial tables (if present) like padres_trials, coordination_runs:
bq head -n 20 ${DATASET}.coordination_runs > results/warehouse_padres_factory_bigquery_coordination_runs.txt

# KPIs:
bq query --use_legacy_sql=false 'SELECT strategy, AVG(avg_efficiency) eff, AVG(avg_collision_count) collisions FROM \${PROJECT_ID}.${DATASET}.coordination_runs` GROUP BY strategy'` > results/warehouse_padres_factory_bigquery_kpis.txt

echo "Collecting Warehouse/Padres/Factory data..."