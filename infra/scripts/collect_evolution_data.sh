#!/bin/bash

# This script collects data for the Evolution component.

# 1. GCS:
gsutil ls gs://${BUCKET}/evolution/ > results/evolution_gcs_objects.txt

# 2. BigQuery:
bq ls ${DATASET} > results/evolution_bigquery_datasets.txt

# KPIs:
bq query --use_legacy_sql=false "SELECT segment, AVG(cues.glow) avg_glow FROM `${PROJECT_ID}.${DATASET}.pareto_fronts`, UNNEST(cues) cues GROUP BY segment" > results/evolution_bigquery_kpis.txt

echo "Collecting Evolution data..."