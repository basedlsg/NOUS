# Runbook: Authenticating with Google Cloud

## Purpose

This runbook provides instructions on how to authenticate with Google Cloud using a service account key.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   A Google Cloud service account key in JSON format.

## Steps

1.  **Open a terminal.**
2.  **Run the following command, replacing `<KEY.json>` with the actual path to the key file:**

    ```bash
    gcloud auth activate-service-account --key-file <KEY.json>
    ```

    For example:

    ```bash
    gcloud auth activate-service-account --key-file /path/to/key.json
    ```

3.  **Verify the authentication:**

    ```bash
    gcloud auth list
    ```

    This command should output the service account you authenticated with.

## Troubleshooting

*   If you encounter an error message, ensure that the `gcloud` command-line tool is properly installed and configured.
*   Verify that the key file exists and is accessible.
*   Verify that the service account has the correct permissions to access the resources you need.
