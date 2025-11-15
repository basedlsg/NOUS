# Runbook: Listing Logging Sources

## Purpose

This runbook provides instructions on how to list Logging sources using the `gcloud` command-line tool.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   Authentication with Google Cloud.

## Steps

1.  **Open a terminal.**
2.  **Run the following command:**

    ```bash
    gcloud logging logs list --limit=50
    ```

    This command will output a list of Logging sources in your project.

## Troubleshooting

*   If you encounter an error message, ensure that the `gcloud` command-line tool is properly installed and configured.
*   Verify that you have the correct permissions to access Logging.
*   Ensure that you are authenticated with Google Cloud.
