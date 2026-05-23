"""Shared pytest config — adds skill-chain-supervisor/scripts to sys.path so
the scratchpad module can be imported by tests as a top-level module.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Point at <plugin_root>/skills/skill-chain-supervisor/scripts so `import scratchpad` works.
_PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRATCHPAD_DIR = _PLUGIN_ROOT / "skills" / "skill-chain-supervisor" / "scripts"
if str(_SCRATCHPAD_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRATCHPAD_DIR))
