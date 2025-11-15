#!/bin/bash

# This script generates per-component and consolidated reports.

python3 scripts/summarize_components.py --outdir results/component_reports --html results/component_reports/index.html --pdf results/component_reports/overview.pdf

echo "Generating per-component and consolidated reports..."