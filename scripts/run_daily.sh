#!/bin/bash
# ==============================================================================
# run_daily.sh - Wrapper script for cron
# ==============================================================================
# This script:
# 1. Sets up the correct directory
# 2. Activates the virtual environment
# 3. Runs the Python script
# 4. Logs everything to a file
# ==============================================================================

# CONFIGURATION - Update this path if different!
PROJECT_DIR="/Users/daadi/paper-discovery-engine"

# Derived paths
VENV_PYTHON="${PROJECT_DIR}/venv/bin/python"
SCRIPT="${PROJECT_DIR}/src/daily_run.py"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/daily_$(date +%Y%m%d).log"

# Create log directory if needed
mkdir -p "${LOG_DIR}"

# Log start
echo "" >> "${LOG_FILE}"
echo "========================================" >> "${LOG_FILE}"
echo "Started: $(date)" >> "${LOG_FILE}"
echo "========================================" >> "${LOG_FILE}"

# Change to project directory
cd "${PROJECT_DIR}"

# Run the script and log output
"${VENV_PYTHON}" "${SCRIPT}" >> "${LOG_FILE}" 2>&1

# Log end
echo "" >> "${LOG_FILE}"
echo "Finished: $(date)" >> "${LOG_FILE}"
echo "========================================" >> "${LOG_FILE}"
