#!/bin/bash

# This script lists the BigQuery datasets.

bq ls --project_id=${PROJECT_ID}

echo "Listing BigQuery datasets..."