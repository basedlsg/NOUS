# Runbook: Deploy Spatial Experiment to Cloud Run

This runbook provides instructions on how to deploy the spatial experiment to Google Cloud Run.

## Prerequisites

*   Google Cloud SDK installed and configured.
*   Docker installed.
*   Project ID configured in the environment.

## Deployment Steps

1.  **Build the Docker image:**

    ```bash
    docker build -t gcr.io/$PROJECT_ID/spatial-experiment:latest .
    ```

2.  **Push the image to Google Container Registry:**

    ```bash
    docker push gcr.io/$PROJECT_ID/spatial-experiment:latest
    ```

3.  **Deploy the image to Cloud Run:**

    ```bash
    gcloud run deploy spatial-experiment --image gcr.io/$PROJECT_ID/spatial-experiment:latest --platform managed --region us-central1
    ```

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

    *   Check the Google Cloud SDK configuration.
    *   Verify that the Docker image was built and pushed successfully.
    *   Ensure that the Cloud Run service is properly configured.

*   **Experiments are not running:**

    *   Check the Cloud Run service logs for errors.
    *   Verify that the API endpoint is accessible.

*   **Data analysis fails:**

    *   Check the data format and ensure that it is compatible with the analysis scripts.