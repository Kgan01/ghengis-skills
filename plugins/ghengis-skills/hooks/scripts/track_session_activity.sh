#!/bin/bash
# Thin wrapper — Python does the real work
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "${SCRIPT_DIR}/track_session_activity.py"
exit 0
