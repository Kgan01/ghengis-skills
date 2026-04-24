#!/bin/bash
# Thin wrapper — Python does the real work
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"${SCRIPT_DIR}/run-python.sh" "${SCRIPT_DIR}/track_session_activity.py"
exit 0
