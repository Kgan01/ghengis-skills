#!/bin/bash
# Thin wrapper — Python does the real work (cross-platform path handling)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"${SCRIPT_DIR}/run-python.sh" "${SCRIPT_DIR}/chain_subagent_stop.py"
exit 0
