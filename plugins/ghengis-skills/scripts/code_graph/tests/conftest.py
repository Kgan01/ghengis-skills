"""Shared pytest config — adds parent dir (scripts/code_graph) to sys.path so
the helper modules can be imported as top-level (matching how run.py imports
them).
"""
from __future__ import annotations

import sys
from pathlib import Path

_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))
