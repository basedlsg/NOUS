#!/bin/bash

# This script collects data for the Spatial AI Lab component.

# 1. BigQuery dataset may include tables like spatial_tasks, task_results:
bq ls ${DATASET} > results/spatial_ai_lab_bigquery_datasets.txt
bq head -n 20 ${DATASET}.spatial_tasks > results/spatial_ai_lab_bigquery_spatial_tasks.txt

# KPIs:
bq query --use_legacy_sql=false "SELECT category, COUNT(*) total, AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) acc FROM `${PROJECT_ID}.${DATASET}.spatial_tasks` GROUP BY category" > results/spatial_ai_lab_bigquery_category_accuracy.txt

# Latency/cost:
bq query --use_legacy_sql=false "SELECT provider, AVG(latency_ms) avg_latency, AVG(cost_estimate) avg_cost FROM `${PROJECT_ID}.${DATASET}.spatial_tasks` GROUP BY provider" > results/spatial_ai_lab_bigquery_latency_cost.txt

echo "Collecting Spatial AI Lab data..."