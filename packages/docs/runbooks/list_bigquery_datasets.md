# Runbook: Listing BigQuery Datasets

## Purpose

This runbook provides instructions on how to list BigQuery datasets using the `bq` command-line tool.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `bq` command-line tool available in your environment.
*   Authentication with Google Cloud.
*   The Google Cloud project ID.

## Steps

1.  **Open a terminal.**
2.  **Run the following command, replacing `<PROJECT_ID>` with the actual project ID:**

    ```bash
    bq ls --project_id=<PROJECT_ID>
    ```

    For example:

    ```bash
    bq ls --project_id=my-gcp-project
    ```

    This command will output a list of BigQuery datasets in your project.

## Troubleshooting

*   If you encounter an error message, ensure that the `bq` command-line tool is properly installed and configured.
*   Verify that you have the correct permissions to access BigQuery.
*   Ensure that you are authenticated with Google Cloud.
*   Ensure that you have set the correct project ID.
