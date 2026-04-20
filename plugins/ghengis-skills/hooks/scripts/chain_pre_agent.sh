#!/bin/bash
# Thin wrapper — Python does the real work (cross-platform path handling)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "${SCRIPT_DIR}/chain_pre_agent.py"
exit 0
