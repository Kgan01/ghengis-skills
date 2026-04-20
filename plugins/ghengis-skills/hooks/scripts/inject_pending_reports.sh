#!/bin/bash
# Thin wrapper — Python does the real work (cross-platform paths)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "${SCRIPT_DIR}/inject_pending_reports.py"
exit 0
