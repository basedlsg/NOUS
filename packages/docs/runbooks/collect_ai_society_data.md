# Runbook: Collecting AI Society Data

## Purpose

This runbook provides instructions on how to collect data for the AI Society component.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   `gsutil` command-line tool available in your environment.
*   `bq` command-line tool available in your environment.
*   Authentication with Google Cloud.
*   The Google Cloud project ID.
*   The Google Cloud region.
*   The GCS bucket name.
*   The BigQuery dataset name.

## Steps

1.  **Collect Cloud Run logs for society API/observer:**

    ```bash
    gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="<SERVICE_NAME>"' --limit=200 --format='value(textPayload)' > results/ai_society_cloud_run_logs.txt
    ```

    Replace `<SERVICE_NAME>` with the actual service name.

2.  **Collect GCS snapshots:**

    ```bash
    gcloud storage objects list --bucket=${BUCKET} --prefix=society/ > results/ai_society_gcs_snapshots.txt
    gsutil cp -m gs://${BUCKET}/society/live_observations_*.json ./cloud_obs/
    ```

    Replace `${BUCKET}` with the name of your GCS bucket.

3.  **Collect BigQuery events:**

    ```bash
    bq ls ${DATASET} > results/ai_society_bigquery_datasets.txt
    bq show --format=prettyjson ${DATASET}.llm_events | jq > results/ai_society_bigquery_llm_events.json
    ```

    Replace `${DATASET}` with the name of your BigQuery dataset.

4.  **Run example query:**

    ```bash
    bq query --use_legacy_sql=false 'SELECT model, COUNT(*) n, AVG(latency_ms) avg_latency FROM \${PROJECT_ID}.${DATASET}.llm_events` GROUP BY model ORDER BY n DESC'` > results/ai_society_bigquery_query_results.txt
    ```

    Replace `${PROJECT_ID}` with your project ID and `${DATASET}` with the name of your BigQuery dataset.

## Troubleshooting

*   If you encounter an error message, ensure that the command-line tools are properly installed and configured.
*   Verify that you have the correct permissions to access the resources.
*   Ensure that you are authenticated with Google Cloud.
*   Ensure that you have set the correct project ID, region, GCS bucket name, and BigQuery dataset name.
