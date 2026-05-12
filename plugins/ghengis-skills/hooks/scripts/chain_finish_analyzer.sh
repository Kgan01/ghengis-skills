#!/bin/bash
# Thin wrapper — Python does the real work (json parsing + system-reminder injection)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"${SCRIPT_DIR}/run-python.sh" "${SCRIPT_DIR}/chain_finish_analyzer.py"
exit 0
