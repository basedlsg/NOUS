# Runbook: Regenerating AI Society Rollups

## Purpose

This runbook provides instructions on how to regenerate AI Society rollups.

## Prerequisites

*   Python 3 installed.
*   The `scripts/aggregate_live_observations.py` script available.
*   The `gcp_deployment/live_observations_*.json` files available.

## Steps

1.  **Open a terminal.**
2.  **Run the following command:**

    ```bash
    python3 scripts/aggregate_live_observations.py --glob 'gcp_deployment/live_observations_*.json' --outdir results/rollups --report results/observations_report.html
    ```

    This command will regenerate the AI Society rollups and output the results to the `results/rollups` directory.

## Troubleshooting

*   If you encounter an error message, ensure that Python 3 is properly installed.
*   Verify that the `scripts/aggregate_live_observations.py` script exists and is executable.
*   Ensure that the `gcp_deployment/live_observations_*.json` files are available.
