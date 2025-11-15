# Runbook: Listing Google Cloud Storage Buckets

## Purpose

This runbook provides instructions on how to list Google Cloud Storage buckets using the `gcloud` command-line tool.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   Authentication with Google Cloud.

## Steps

1.  **Open a terminal.**
2.  **Run the following command:**

    ```bash
    gcloud storage buckets list
    ```

    This command will output a list of GCS buckets in your project.

## Troubleshooting

*   If you encounter an error message, ensure that the `gcloud` command-line tool is properly installed and configured.
*   Verify that you have the correct permissions to access the GCS buckets.
*   Ensure that you are authenticated with Google Cloud.
