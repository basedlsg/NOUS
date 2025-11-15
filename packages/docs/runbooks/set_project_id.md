# Runbook: Setting the Google Cloud Project ID

## Purpose

This runbook provides instructions on how to set the Google Cloud project ID using the `gcloud` command-line tool.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   The desired Google Cloud project ID.

## Steps

1.  **Open a terminal.**
2.  **Run the following command, replacing `<PROJECT_ID>` with the actual project ID:**

    ```bash
    gcloud config set project <PROJECT_ID>
    ```

    For example:

    ```bash
    gcloud config set project my-gcp-project
    ```

3.  **Verify the project ID:**

    ```bash
    gcloud config get-value project
    ```

    This command should output the project ID you set in the previous step.

## Troubleshooting

*   If you encounter an error message, ensure that the `gcloud` command-line tool is properly installed and configured.
*   Verify that you have the correct permissions to access the specified project.
