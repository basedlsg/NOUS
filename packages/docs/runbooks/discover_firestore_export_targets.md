# Runbook: Discovering Firestore Export Targets

## Purpose

This runbook provides instructions on how to discover Firestore export targets.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   `gsutil` command-line tool available in your environment.
*   Authentication with Google Cloud.
*   A GCS bucket to export Firestore data to.

## Steps

1.  **Export Firestore data to a GCS bucket:**

    ```bash
    gcloud firestore export gs://${BUCKET}/firestore-exports/$(date +%F)/ --collection-ids=experiment_configs,run_status,job_queue
    ```

    Replace `${BUCKET}` with the name of your GCS bucket.

2.  **List objects in the GCS bucket:**

    ```bash
    gsutil ls -r gs://${BUCKET}/firestore-exports/ | sort
    ```

    Replace `${BUCKET}` with the name of your GCS bucket.

    This command will output a list of objects in the GCS bucket, which will include the Firestore export targets.

## Troubleshooting

*   If you encounter an error message, ensure that the `gcloud` and `gsutil` command-line tools are properly installed and configured.
*   Verify that you have the correct permissions to access Firestore and GCS.
*   Ensure that you are authenticated with Google Cloud.
*   Ensure that you have a GCS bucket to export Firestore data to.
