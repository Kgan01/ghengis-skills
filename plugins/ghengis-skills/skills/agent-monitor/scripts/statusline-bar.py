#!/usr/bin/env python3
import sys
import json
import io

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def progress_bar(percentage, width=10):
    """Generate a colored progress bar string"""
    filled = int((percentage / 100) * width)
    empty = width - filled

    # ANSI color codes
    if percentage < 50:
        color = '\033[32m'  # Green
    elif percentage < 80:
        color = '\033[33m'  # Yellow
    else:
        color = '\033[31m'  # Red

    reset = '\033[0m'
    dim = '\033[2m'

    bar = color + '█' * filled + dim + '░' * empty + reset
    return bar

def abbreviate_path(path, max_len=30):
    """Shorten path, keeping first and last parts"""
    if len(path) <= max_len:
        return path

    # Normalize separators
    path = path.replace('\\', '/')
    parts = [p for p in path.split('/') if p]

    if len(parts) <= 2:
        return path

    # Keep first part (drive or ~) and last 2 parts
    first = parts[0]
    if first.endswith(':'):
        first = '/' + first[0].lower()  # C: -> /c

    return f"{first}/.../{'/'.join(parts[-2:])}"

try:
    data = json.load(sys.stdin)
    model = data.get('model', {}).get('display_name', 'Unknown')

    # Use pre-calculated percentage from Claude Code (tracks actual context window)
    ctx = data.get('context_window', {})
    used = ctx.get('used_percentage', 0)
    # Linear correction: calibrated from (18%, 18%) and (75%, 90%) data points
    corrected = (used * 1.26) - 4.7
    used = max(0, min(corrected, 100))

    # Get abbreviated directory
    cwd = data.get('workspace', {}).get('current_dir', '')
    short_path = abbreviate_path(cwd)

    # Colors
    orange = '\033[38;5;208m'
    cyan = '\033[36m'
    reset = '\033[0m'
    dim = '\033[2m'

    bar = progress_bar(used, width=10)

    print(f"{orange}{model}{reset} {bar} {dim}{used:.0f}%{reset}\n{cyan}{short_path}{reset}")
except:
    print("Error ░░░░░░░░░░ 0%")
