# Runbook: Debugging gcloud and gsutil Issues

This runbook provides steps to debug common issues with the `gcloud` CLI and `gsutil`.

## Prerequisites

- Ensure you have the `gcloud` CLI installed and configured.
- Ensure you have network connectivity to Google Cloud.

## Debugging Steps

1.  **Verify gcloud CLI Installation:**

    -   Run `gcloud version` to check the installed version and components.
    -   If the version is outdated, update the components by running `gcloud components update`.

2.  **Check Account and Project Settings:**

    -   Run `gcloud config list` to view the current account and project settings.
    -   Ensure the correct account is active. If not, activate the correct account using `gcloud config set account ACCOUNT_NAME`.
    -   Ensure the correct project is set. If not, set the correct project using `gcloud config set project PROJECT_ID`.

3.  **Troubleshoot "file://" URL Error:**

    -   The `gcloud storage ls` and `gsutil ls` commands are used to list the contents of Google Cloud Storage buckets, and should be used with `gs://` URLs.
    -   If you are trying to list a local file, use the standard `ls` command in your terminal.
    -   Example:
        -   To list a GCS bucket: `gsutil ls gs://your-bucket-name`
        -   To list a local directory: `ls /path/to/your/local/directory`

4.  **Troubleshoot Timeout Issues:**

    -   Timeout issues can occur due to network connectivity problems or large bucket sizes.
    -   Check your network connection to ensure it is stable.
    -   Try increasing the timeout value using the `--timeout` flag.
        -   Example: `gsutil ls gs://your-bucket-name --timeout=30`
    -   If the bucket is very large, consider using pagination to list the contents in smaller chunks.

5.  **Check for System-Level gsutil Installation (Likely Cause):**

    -   Run `which gsutil` to determine the location of the `gsutil` executable.
    -   If the path is `/usr/bin/gsutil` or another system-level directory, it is *highly likely* that this is conflicting with the `gcloud` CLI's managed version.
    -   **Solution:**
        -   *Recommended:* Always use the full path to `gsutil` within the `gcloud` CLI's installation directory (e.g., `/opt/google-cloud-sdk/bin/gsutil ls gs://your-bucket-name`).
        -   *Alternative:* Ensure that the `gcloud` CLI's bin directory is ahead of `/usr/bin` in your `PATH` environment variable. You can add the following line to your `.bashrc` or `.zshrc` file:
            `export PATH="/opt/google-cloud-sdk/bin:$PATH"` (adjust the path if your SDK is installed elsewhere). After modifying the file, restart your terminal or run `source ~/.bashrc` or `source ~/.zshrc` to apply the changes.

6.  **Check Permissions:**

    -   Ensure that the active account has the necessary permissions to access the GCS bucket.
    -   Verify that the account has the `storage.buckets.list` permission on the bucket.
    -   You can check the permissions using the Cloud Console or the `gcloud` CLI.

7.  **Search for Known Issues:**

    -   Check the Google Cloud documentation and Stack Overflow for known issues and solutions related to `gcloud` and `gsutil`.

## If the issue persists

-   Contact Google Cloud Support for further assistance.