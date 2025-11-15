# Runbook: Deploy Spatial Experiment to Cloud Run using Cloud Build

This runbook provides instructions on how to deploy the spatial experiment to Google Cloud Run using Cloud Build.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   Cloud Build API enabled.
*   Project ID configured in the environment.

## Deployment Steps

1.  **Create a Cloud Build YAML file (cloudbuild.yaml):**

    ```yaml
    steps:
      - name: 'gcr.io/cloud-builders/docker'
        args: ['build', '-t', 'gcr.io/$PROJECT_ID/spatial-experiment:latest', '.']
      - name: 'gcr.io/cloud-builders/docker'
        args: ['push', 'gcr.io/$PROJECT_ID/spatial-experiment:latest']
      - name: 'gcr.io/google-cloud-sdk'
        args:
          - 'gcloud'
          - 'run'
          - 'deploy'
          - 'spatial-experiment'
          - '--image'
          - 'gcr.io/$PROJECT_ID/spatial-experiment:latest'
          - '--platform'
          - 'managed'
          - '--region'
          - 'us-central1'
    ```

2.  **Submit the Cloud Build job:**

    ```bash
    gcloud builds submit --config cloudbuild.yaml .
    ```

    *   This command will build the Docker image, push it to Google Container Registry, and deploy it to Cloud Run.
    *   Follow the prompts in the terminal to configure the Cloud Run service.
    *   Ensure that the service is publicly accessible.

## Running Experiments

1.  **Access the Cloud Run service:**

    *   Obtain the URL of the deployed Cloud Run service.

2.  **Send requests to the service:**

    *   Use a tool like `curl` or a Python script to send requests to the service's API endpoint to generate new tasks and collect trajectories.

## Analyzing Results

1.  **Collect the experiment data:**

    *   Download the generated trajectory data from Google Cloud Storage.

2.  **Analyze the data:**

    *   Use the analysis scripts in the `src/spatial_lab/evaluation` directory to analyze the data and determine if the LLM prioritizes shape recognition or metadata.

## Troubleshooting

*   **Deployment fails:**

    *   Check the Cloud Build logs for errors.
    *   Verify that the Docker image was built and pushed successfully.
    *   Ensure that the Cloud Run service is properly configured.

*   **Experiments are not running:**

    *   Check the Cloud Run service logs for errors.
    *   Verify that the API endpoint is accessible.

*   **Data analysis fails:**

    *   Check the data format and ensure that it is compatible with the analysis scripts.