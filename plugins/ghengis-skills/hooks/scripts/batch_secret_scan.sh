#!/bin/bash
# Thin shell wrapper — Python does the real work
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "${SCRIPT_DIR}/batch_secret_scan.py" 2>&1
exit 0
