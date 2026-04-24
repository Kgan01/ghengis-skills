#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"${SCRIPT_DIR}/run-python.sh" "${SCRIPT_DIR}/inject_update_notice.py"
exit 0
