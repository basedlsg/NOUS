# Runbook: Generating Per-Component and Consolidated Reports

## Purpose

This runbook provides instructions on how to generate per-component and consolidated reports.

## Prerequisites

*   Python 3 installed.
*   The `scripts/summarize_components.py` script available.
*   The data collected for each component.

## Steps

1.  **Open a terminal.**
2.  **Run the following command:**

    ```bash
    python3 scripts/summarize_components.py --outdir results/component_reports --html results/component_reports/index.html --pdf results/component_reports/overview.pdf
    ```

    This command will generate per-component JSON summaries, a combined summary JSON, a combined HTML report, and a combined PDF overview.

## Troubleshooting

*   If you encounter an error message, ensure that Python 3 is properly installed.
*   Verify that the `scripts/summarize_components.py` script exists and is executable.
*   Ensure that the data collected for each component is available in the expected locations.
