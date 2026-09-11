#!/bin/bash
# run_pipeline.sh
# Triggers the pipeline for cron (macOS/Linux).
#
# Set up with cron:
#   crontab -e
#   Add a line like (runs daily at 2am):
#   0 2 * * * /path/to/educational-data-pipeline/scripts/run_pipeline.sh

cd "$(dirname "$0")/../src" || exit 1
python3 pipeline.py
