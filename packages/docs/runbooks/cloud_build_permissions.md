# Granting Cloud Build Service Account Permissions

The `gcp_all_in_one.sh` script uses Cloud Build to perform several tasks, including exporting Cloud Asset Inventory, creating BigQuery datasets, and copying data to Cloud Storage. The Cloud Build service account must have the necessary permissions to perform these tasks.

## Identifying the Service Account

The service account used by Cloud Build is specified in the `cloudbuild.yaml` file:

```yaml
serviceAccount: projects/seven-l-prod/serviceAccounts/central-inventory-sa@seven-l-prod.iam.gserviceaccount.com
```

In this case, the service account is `central-inventory-sa@seven-l-prod.iam.gserviceaccount.com` in the `seven-l-prod` project.

## Granting Permissions

You can grant the necessary permissions to the service account using the Google Cloud Console or the `gcloud` command-line tool.

### Using the Google Cloud Console

1.  Go to the [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) page in the Google Cloud Console.
2.  Select the project containing the service account (e.g., `seven-l-prod`).
3.  Find the `central-inventory-sa@seven-l-prod.iam.gserviceaccount.com` service account.
4.  Click the pencil icon to edit the service account.
5.  Click "Add Role" and grant the following roles:
    *   **Cloud Asset Owner** (`roles/cloudasset.owner`): Required to export Cloud Asset Inventory.
    *   **BigQuery Data Editor** (`roles/bigquery.dataEditor`): Required to write data to BigQuery tables.
    *   **BigQuery Admin** (`roles/bigquery.admin`): Required to create BigQuery datasets.
    *   **Storage Admin** (`roles/storage.admin`): Required to create and manage Cloud Storage buckets and objects.
    *   **Service Usage Admin** (`roles/serviceusage.serviceUsageAdmin`): Required to enable APIs.
6.  Click "Save".

### Using the `gcloud` Command-Line Tool

You can use the following `gcloud` commands to grant the necessary roles to the service account:

```bash
PROJECT_ID="seven-l-prod"
SERVICE_ACCOUNT="central-inventory-sa@seven-l-prod.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudasset.owner"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/serviceusage.serviceUsageAdmin"
```

Replace `seven-l-prod` with the actual project ID.

## Verifying Permissions

After granting the permissions, you can verify that the service account has the necessary roles by running the following command:

```bash
gcloud projects get-iam-policy "$PROJECT_ID" \
  --format="yaml" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT"
```

This command will output the IAM policy for the project, filtered to show the roles granted to the specified service account.
