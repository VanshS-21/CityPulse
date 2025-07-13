#!/bin/bash

# This script removes unnecessary generated files, logs, and test artifacts
# to clean up the codebase and improve maintainability.

# --- Generated Reports & Logs ---
# These files are auto-generated and do not need to be version-controlled.
echo "Removing generated reports and logs..."
rm -f PROJECT_ANALYSIS_REPORT.md
rm -f TESTING_VALIDATION_REPORT.md
rm -f DOCUMENTATION_ENHANCEMENT_REPORT.md
rm -f TESTING_VERIFICATION_REPORT.md
rm -f FINAL_REVIEW_REPORT.md
rm -f DOCKER_MIGRATION_REPORT.md
rm -f STEP3_CODE_ENHANCEMENT_RESEARCH_REPORT.md
rm -f audit_report.json
rm -f pylint-report.txt
rm -f pylint-report.json
rm -f pylint-report-updated.txt

# --- Test Artifacts ---
# These files and directories are generated during test runs.
echo "Removing test artifacts..."
rm -rf test-results/
rm -f tests/test_output.json

echo "Cleanup complete."