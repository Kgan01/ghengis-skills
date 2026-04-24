#!/bin/bash
# Pick whichever Python interpreter is actually functional.
#
# On Unix (macOS, Linux): python3 is the standard name.
# On Windows: `python3` often resolves to the Microsoft Store shim that
# prints "Python was not found..." and exits non-zero. Fall back to `python`.
#
# If both are missing we emit a single clear stderr line and exit 127 so
# Claude Code's hook runner sees the failure without a cryptic JSON error.

if python3 --version >/dev/null 2>&1; then
    exec python3 "$@"
elif python --version >/dev/null 2>&1; then
    exec python "$@"
else
    echo "[ghengis-skills] No working Python interpreter found on PATH (tried python3 and python). Install Python 3.x to enable hook scripts." >&2
    exit 127
fi
