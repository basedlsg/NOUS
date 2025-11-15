# Runbook: Resuming the Inventory Script

This runbook documents the steps taken to resume the inventory script.

## Prerequisites

*   Ensure that the Google Cloud SDK is installed and configured.
*   Ensure that the necessary environment variables are set.

## Steps

1.  Set up the environment variables:

    ```bash
    export PROJECT_IDS="seven-l-prod"
    export BILLING_QUOTA_PROJECT="seven-l-prod"
    export BQ_PROJECT="seven-l-prod"
    export SA_NAME="central-inventory-sa"
    export SA_EMAIL="${SA_NAME}@${BQ_PROJECT}.iam.gserviceaccount.com"
    ```

2.  Run the resume inventory script:

    ```bash
    ./infra/scripts/resume_inventory.sh
    ```

3.  Monitor the script's output for any errors.

4.  Once the script completes, check the results in the log file.

5.  If the script completed successfully, copy the results to Google Drive.