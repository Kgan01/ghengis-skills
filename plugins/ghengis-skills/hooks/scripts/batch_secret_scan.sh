#!/bin/bash
# Thin shell wrapper — Python does the real work
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"${SCRIPT_DIR}/run-python.sh" "${SCRIPT_DIR}/batch_secret_scan.py"
exit 0
