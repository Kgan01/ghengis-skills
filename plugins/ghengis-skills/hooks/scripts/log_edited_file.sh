#!/bin/bash
# Thin wrapper — Python does the real work (UTF-8 / unicode path handling)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "${SCRIPT_DIR}/log_edited_file.py"
exit 0
