# Runbook: Collecting CloudVR-PerfGuard Data

## Purpose

This runbook provides instructions on how to collect data for the CloudVR-PerfGuard component.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   `gsutil` command-line tool available in your environment.
*   `bq` command-line tool available in your environment.
*   Authentication with Google Cloud.
*   The Google Cloud project ID.
*   The BigQuery dataset name.
*   The GCS bucket name.

## Steps

1.  **Collect GCS objects:**

    ```bash
    gcloud storage objects list --bucket=${BUCKET} --prefix=cloudvr/ > results/cloudvr_perfguard_gcs_objects.txt
    gsutil cp -m gs://${BUCKET}/cloudvr/research_outputs/* ./research_outputs/
    ```

    Replace `${BUCKET}` with the name of your GCS bucket.

2.  **Collect BigQuery data:**

    ```bash
    bq ls ${DATASET} > results/cloudvr_perfguard_bigquery_datasets.txt
    bq show --format=prettyjson ${DATASET}.vr_runs | jq > results/cloudvr_perfguard_bigquery_vr_runs.json
    ```

    Replace `${DATASET}` with the name of your BigQuery dataset.

3.  **Run query to get KPIs:**

    ```bash
    bq query --use_legacy_sql=false 'SELECT app, COUNT(*) runs, AVG(fps) avg_fps, AVG(frame_time_ms) avg_ft, AVG(comfort_score) avg_comfort FROM \${PROJECT_ID}.${DATASET}.vr_runs` GROUP BY app'` > results/cloudvr_perfguard_bigquery_kpis.txt
    ```

    Replace `${PROJECT_ID}` with your project ID and `${DATASET}` with the name of your BigQuery dataset.

4.  **Collect Cloud Run logs:**

    ```bash
    gcloud logging read 'resource.type="cloud_run_revision" AND textPayload:CloudVR' --limit=200 --format=json | jq '.[].textPayload' > results/cloudvr_perfguard_cloud_run_logs.json
    ```

## Troubleshooting

*   If you encounter an error message, ensure that the command-line tools are properly installed and configured.
*   Verify that you have the correct permissions to access GCS, BigQuery, and Cloud Logging.
*   Ensure that you are authenticated with Google Cloud.
*   Ensure that you have set the correct project ID, BigQuery dataset name, and GCS bucket name.
