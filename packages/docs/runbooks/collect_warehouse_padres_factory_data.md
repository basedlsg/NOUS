# Runbook: Collecting Warehouse/Padres/Factory Data

## Purpose

This runbook provides instructions on how to collect data for the Warehouse/Padres/Factory component.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   `bq` command-line tool available in your environment.
*   Authentication with Google Cloud.
*   The Google Cloud project ID.
*   The Google Cloud region.
*   The BigQuery dataset name.
*   The Padres Cloud Run service name.

## Steps

1.  **Describe the Padres Cloud Run service:**

    ```bash
    gcloud run services describe <PADRES_SERVICE> --region=${REGION} --format=json > results/warehouse_padres_factory_cloud_run_service.json
    ```

    Replace `<PADRES_SERVICE>` with the name of your Padres Cloud Run service and `${REGION}` with the Google Cloud region.

2.  **Collect Cloud Run logs:**

    ```bash
    gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="<PADRES_SERVICE>" AND severity>=ERROR' --limit=200 --format='value(textPayload)' > results/warehouse_padres_factory_cloud_run_logs.txt
    ```

    Replace `<PADRES_SERVICE>` with the name of your Padres Cloud Run service.

3.  **Get the first 20 rows of the coordination_runs table:**

    ```bash
    bq head -n 20 ${DATASET}.coordination_runs > results/warehouse_padres_factory_bigquery_coordination_runs.txt
    ```

    Replace `${DATASET}` with the name of your BigQuery dataset.

4.  **Run query to get KPIs:**

    ```bash
    bq query --use_legacy_sql=false 'SELECT strategy, AVG(avg_efficiency) eff, AVG(avg_collision_count) collisions FROM \${PROJECT_ID}.${DATASET}.coordination_runs` GROUP BY strategy'` > results/warehouse_padres_factory_bigquery_kpis.txt
    ```

    Replace `${PROJECT_ID}` with your project ID and `${DATASET}` with the name of your BigQuery dataset.

## Troubleshooting

*   If you encounter an error message, ensure that the command-line tools are properly installed and configured.
*   Verify that you have the correct permissions to access Cloud Run and BigQuery.
*   Ensure that you are authenticated with Google Cloud.
*   Ensure that you have set the correct project ID, region, BigQuery dataset name, and Padres Cloud Run service name.
