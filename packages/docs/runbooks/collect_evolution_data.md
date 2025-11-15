# Runbook: Collecting Evolution Data

## Purpose

This runbook provides instructions on how to collect data for the Evolution component.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gsutil` command-line tool available in your environment.
*   `bq` command-line tool available in your environment.
*   Authentication with Google Cloud.
*   The Google Cloud project ID.
*   The BigQuery dataset name.
*   The GCS bucket name.

## Steps

1.  **Collect GCS objects:**

    ```bash
    gsutil ls gs://${BUCKET}/evolution/ > results/evolution_gcs_objects.txt
    ```

    Replace `${BUCKET}` with the name of your GCS bucket.

2.  **List BigQuery datasets:**

    ```bash
    bq ls ${DATASET} > results/evolution_bigquery_datasets.txt
    ```

    Replace `${DATASET}` with the name of your BigQuery dataset.

3.  **Run query to get KPIs:**

    ```bash
    bq query --use_legacy_sql=false 'SELECT segment, AVG(cues.glow) avg_glow FROM \${PROJECT_ID}.${DATASET}.pareto_fronts`, UNNEST(cues) cues GROUP BY segment'` > results/evolution_bigquery_kpis.txt
    ```

    Replace `${PROJECT_ID}` with your project ID and `${DATASET}` with the name of your BigQuery dataset.

## Troubleshooting

*   If you encounter an error message, ensure that the command-line tools are properly installed and configured.
*   Verify that you have the correct permissions to access GCS and BigQuery.
*   Ensure that you are authenticated with Google Cloud.
*   Ensure that you have set the correct project ID, BigQuery dataset name, and GCS bucket name.
