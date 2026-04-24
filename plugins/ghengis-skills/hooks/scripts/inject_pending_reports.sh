#!/bin/bash
# Thin wrapper — Python does the real work (cross-platform paths)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"${SCRIPT_DIR}/run-python.sh" "${SCRIPT_DIR}/inject_pending_reports.py"
exit 0
