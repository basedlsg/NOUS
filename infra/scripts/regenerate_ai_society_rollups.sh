#!/bin/bash

# This script regenerates AI Society rollups.

python3 scripts/aggregate_live_observations.py --glob 'gcp_deployment/live_observations_*.json' --outdir results/rollups --report results/observations_report.html

echo "Regenerating AI Society rollups..."