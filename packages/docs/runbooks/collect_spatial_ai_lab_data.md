# Runbook: Collecting Spatial AI Lab Data

## Purpose

This runbook provides instructions on how to collect data for the Spatial AI Lab component.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `bq` command-line tool available in your environment.
*   Authentication with Google Cloud.
*   The Google Cloud project ID.
*   The BigQuery dataset name.

## Steps

1.  **List BigQuery datasets:**

    ```bash
    bq ls ${DATASET} > results/spatial_ai_lab_bigquery_datasets.txt
    ```

    Replace `${DATASET}` with the name of your BigQuery dataset.

2.  **Get the first 20 rows of the spatial_tasks table:**

    ```bash
    bq head -n 20 ${DATASET}.spatial_tasks > results/spatial_ai_lab_bigquery_spatial_tasks.txt
    ```

    Replace `${DATASET}` with the name of your BigQuery dataset.

3.  **Run query to get per-category accuracy:**

    ```bash
    bq query --use_legacy_sql=false 'SELECT category, COUNT(*) total, AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) acc FROM \${PROJECT_ID}.${DATASET}.spatial_tasks` GROUP BY category'` > results/spatial_ai_lab_bigquery_category_accuracy.txt
    ```

    Replace `${PROJECT_ID}` with your project ID and `${DATASET}` with the name of your BigQuery dataset.

4.  **Run query to get latency/cost:**

    ```bash
    bq query --use_legacy_sql=false 'SELECT provider, AVG(latency_ms) avg_latency, AVG(cost_estimate) avg_cost FROM \${PROJECT_ID}.${DATASET}.spatial_tasks` GROUP BY provider'` > results/spatial_ai_lab_bigquery_latency_cost.txt
    ```

    Replace `${PROJECT_ID}` with your project ID and `${DATASET}` with the name of your BigQuery dataset.

## Troubleshooting

*   If you encounter an error message, ensure that the command-line tools are properly installed and configured.
*   Verify that you have the correct permissions to access BigQuery.
*   Ensure that you are authenticated with Google Cloud.
*   Ensure that you have set the correct project ID and BigQuery dataset name.
