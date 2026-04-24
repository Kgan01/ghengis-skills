#!/bin/bash
# Thin wrapper — picks python3/python via run-python.sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"${SCRIPT_DIR}/run-python.sh" "${SCRIPT_DIR}/on_task_stop.py"
exit 0
