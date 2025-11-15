# Runbook: Listing Pub/Sub Topics and Subscriptions

## Purpose

This runbook provides instructions on how to list Pub/Sub topics and subscriptions using the `gcloud` command-line tool.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   `gcloud` command-line tool available in your environment.
*   Authentication with Google Cloud.

## Steps

1.  **Open a terminal.**
2.  **Run the following commands:**

    ```bash
    gcloud pubsub topics list
    gcloud pubsub subscriptions list
    ```

    These commands will output a list of Pub/Sub topics and subscriptions in your project.

## Troubleshooting

*   If you encounter an error message, ensure that the `gcloud` command-line tool is properly installed and configured.
*   Verify that you have the correct permissions to access Pub/Sub.
*   Ensure that you are authenticated with Google Cloud.
