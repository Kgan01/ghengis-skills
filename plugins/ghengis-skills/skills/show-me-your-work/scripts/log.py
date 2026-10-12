#!/usr/bin/env python3
"""Append a well-formed row to a show-me-your-work decision log (TSV).

Stdlib-only port of log.sh (poteto/pstack, MIT) so the helper runs on
Windows without bash.

Usage: python log.py <logfile> <phase> <decision> <why> <evidence> <result>
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

HEADER = "ts\tphase\tdecision\twhy\tevidence\tresult\n"
USAGE = "usage: log.py <logfile> <phase> <decision> <why> <evidence> <result>\n"


def clean(value: str) -> str:
    """Keep a cell on one line and defuse spreadsheet formulas.

    Tabs, newlines, and CRs become spaces. A cell whose first char a
    spreadsheet would parse as a formula (=, +, -, @) gets a leading
    single quote, so attacker-controlled evidence (PR titles, filenames,
    generated text) cannot execute when a reviewer opens the file.
    """
    v = value.translate(str.maketrans("\t\n\r", "   "))
    if v[:1] in ("=", "+", "-", "@"):
        return "'" + v
    return v


def main(argv: list[str]) -> int:
    if len(argv) != 6:
        sys.stderr.write(USAGE)
        return 1
    logfile = Path(argv[0])
    logfile.parent.mkdir(parents=True, exist_ok=True)

    # Append mode only, never truncate. If the size test misfires on a
    # network mount, the cost is one stray header line, not the rows.
    needs_header = not logfile.exists() or logfile.stat().st_size == 0
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = "\t".join([ts, *(clean(c) for c in argv[1:])]) + "\n"
    with logfile.open("a", encoding="utf-8", newline="") as fh:
        if needs_header:
            fh.write(HEADER)
        fh.write(row)
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        sys.stdout.write(USAGE)
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
