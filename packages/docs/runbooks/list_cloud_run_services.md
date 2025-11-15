# Runbook: Listing Cloud Run Services

## Purpose

This runbook provides instructions on how to list Cloud Run services using the `gcloud` command-line tool.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   Authentication with Google Cloud.
*   The Google Cloud region.

## Steps

1.  **Open a terminal.**
2.  **Run the following command, replacing `<REGION>` with the actual region:**

    ```bash
    gcloud run services list --region=<REGION> --platform=managed
    ```

    For example:

    ```bash
    gcloud run services list --region=us-central1 --platform=managed
    ```

    This command will output a list of Cloud Run services in your project and region.

## Troubleshooting

*   If you encounter an error message, ensure that the `gcloud` command-line tool is properly installed and configured.
*   Verify that you have the correct permissions to access Cloud Run.
*   Ensure that you are authenticated with Google Cloud.
*   Ensure that you have set the correct region.
