"""
treefile-organizer: project analyzer.

Walks a project directory, extracts the import graph, classifies each file into
an architectural layer, identifies anchor files that should never move, and
emits a JSON analysis suitable for downstream PROPOSE/PLAN stages.

This is stage 1 of the 7-stage pipeline. It does NOT propose moves and it does
NOT execute anything. It produces a deterministic analysis that humans and
validators can audit.

Usage:
    python analyzer.py <project_root> [--output <path>] [--include-external]

Output:
    JSON to stdout (or to --output path) matching the schema documented at
    `<skill_dir>/plan-format.md` (analysis section).

v1 scope: Python (via stdlib ast) and TypeScript/JavaScript (via regex).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import warnings
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ANALYZER_VERSION = "1"

PYTHON_EXTS = {".py"}
TYPESCRIPT_EXTS = {".ts", ".tsx", ".mts", ".cts"}
JAVASCRIPT_EXTS = {".js", ".jsx", ".mjs", ".cjs"}
SUPPORTED_EXTS = PYTHON_EXTS | TYPESCRIPT_EXTS | JAVASCRIPT_EXTS

# Directories never scanned. Compared against any path component, not just root.
EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", ".venv", "venv", "env", "node_modules", "dist",
    "build", ".next", ".nuxt", "out", "target", ".gradle", ".idea", ".vscode",
    "coverage", ".coverage", "htmlcov", ".DS_Store",
}

# Files at any path that mark themselves as anchors — never proposed for moves.
# Match by exact basename or by glob fragment.
ANCHOR_BASENAMES = {
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
    "Pipfile", "Pipfile.lock", "poetry.lock", "uv.lock",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "tsconfig.json", "tsconfig.base.json", "jsconfig.json",
    ".gitignore", ".gitattributes", ".editorconfig", ".dockerignore",
    "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "next.config.js", "next.config.ts", "next.config.mjs",
    "vite.config.js", "vite.config.ts", "vite.config.mjs",
    "webpack.config.js", "rollup.config.js", "esbuild.config.js",
    "tailwind.config.js", "tailwind.config.ts",
    "postcss.config.js", "postcss.config.mjs",
    "jest.config.js", "jest.config.ts", "vitest.config.js", "vitest.config.ts",
    "babel.config.js", ".babelrc", ".babelrc.js",
    ".prettierrc", ".prettierrc.json", ".prettierrc.js",
    ".eslintrc", ".eslintrc.json", ".eslintrc.js", ".eslintrc.cjs",
    "Procfile", "Procfile.dev",
}
ANCHOR_DIR_PATTERNS = {
    ".github", ".gitlab", ".circleci", ".husky",
    "scripts",  # commonly scripts/ contains build/deploy scripts; treated as anchor *directory*
}

# Layer classification: a directory NAME (an exact path-component, not a substring)
# maps to a layer. Order matters — first match wins. Avoids substring traps like
# "contests" matching "tests" or "domains_handler" matching "domain".
LAYER_DIR_NAMES: list[tuple[str, str]] = [
    ("routes", "api"),
    ("api", "api"),
    ("controllers", "api"),
    ("endpoints", "api"),
    ("handlers", "api"),
    ("services", "service"),
    ("service", "service"),
    ("business", "service"),
    ("domain", "service"),
    ("models", "data"),
    ("schemas", "data"),
    ("schema", "data"),
    ("entities", "data"),
    ("repositories", "data"),
    ("db", "data"),
    ("database", "data"),
    ("components", "ui"),
    ("views", "ui"),
    ("pages", "ui"),
    ("widgets", "ui"),
    ("screens", "ui"),
    ("ui", "ui"),
    ("scripts", "infrastructure"),
    ("deploy", "infrastructure"),
    ("config", "infrastructure"),
    ("infra", "infrastructure"),
    ("middleware", "infrastructure"),
    ("utils", "utility"),
    ("util", "utility"),
    ("helpers", "utility"),
    ("common", "utility"),
    ("lib", "utility"),
    ("shared", "utility"),
]

# Test detection: directory names AND file-name suffixes. Both checked exactly
# (no substring matching) so `contests.py` doesn't collide with the `tests` rule.
TEST_DIR_NAMES = {"tests", "test", "__tests__", "__test__"}
TEST_FILE_SUFFIXES = (".test.py", ".spec.py", ".test.ts", ".test.tsx", ".test.js",
                      ".test.jsx", ".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx",
                      "_test.py", "_test.go", "_test.rs")

# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass
class ImportRef:
    line: int
    module: str            # the dotted/path string as written
    kind: str              # "internal" | "external" | "relative"
    resolves_to: str | None = None  # relative path within project_root, if internal


@dataclass
class FileEntry:
    path: str              # relative to project_root, forward slashes
    language: str          # "python" | "typescript" | "javascript"
    layer: str             # "api" | "service" | "data" | "ui" | "infrastructure" | "utility" | "test" | "unknown"
    loc: int               # line count (cheap proxy)
    imports: list[ImportRef] = field(default_factory=list)


@dataclass
class Edge:
    src: str               # file path (relative)
    dst: str               # file path (relative)
    line: int


@dataclass
class Stats:
    files_total: int
    files_by_language: dict[str, int]
    imports_total: int
    internal_edges: int
    external_imports: int
    cycles_detected: int


# ---------------------------------------------------------------------------
# Walking
# ---------------------------------------------------------------------------


def is_excluded_dir(p: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in p.parts)


def detect_language(path: Path) -> str | None:
    suf = path.suffix.lower()
    if suf in PYTHON_EXTS:
        return "python"
    if suf in TYPESCRIPT_EXTS:
        return "typescript"
    if suf in JAVASCRIPT_EXTS:
        return "javascript"
    return None


def walk_source_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if is_excluded_dir(path.relative_to(root)):
            continue
        if detect_language(path) is None:
            continue
        yield path


# ---------------------------------------------------------------------------
# Anchors
# ---------------------------------------------------------------------------


def is_anchor(rel_path: Path) -> bool:
    if rel_path.name in ANCHOR_BASENAMES:
        return True
    parts = rel_path.parts
    for pat in ANCHOR_DIR_PATTERNS:
        if pat.rstrip("/") in parts:
            return True
    return False


def collect_anchors(root: Path) -> list[str]:
    anchors: list[str] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if is_excluded_dir(rel):
            continue
        if is_anchor(rel):
            anchors.append(str(rel).replace("\\", "/"))
    return sorted(anchors)


# ---------------------------------------------------------------------------
# Layer classification
# ---------------------------------------------------------------------------


def classify_layer(rel_path: str) -> str:
    """Classify a file path to an architectural layer.

    Uses exact path-component matching (not substring) to avoid traps like
    `contests.py` matching the `tests` directory rule.
    """
    norm = rel_path.replace("\\", "/").lower()
    parts = norm.split("/")
    parts_set = set(parts)
    file_name = parts[-1] if parts else ""

    # Test detection: file-name suffix OR exact directory-name match.
    if file_name.endswith(TEST_FILE_SUFFIXES):
        return "test"
    if parts_set & TEST_DIR_NAMES:
        return "test"

    # Layer detection: walk path components from leaf to root, first match wins.
    # Walking leaf-first means a deeply-nested file in `services/auth/handlers/`
    # gets classified as `api` (handlers, the closest hint) over `service`.
    for component in reversed(parts):
        for dir_name, layer in LAYER_DIR_NAMES:
            if component == dir_name:
                return layer

    # File-name based fallbacks (.tsx with JSX → ui).
    if file_name.endswith((".tsx", ".jsx")):
        return "ui"

    return "unknown"


# ---------------------------------------------------------------------------
# Python import extraction (via ast)
# ---------------------------------------------------------------------------


def extract_python_imports(source: str) -> list[tuple[int, str, bool]]:
    """Return list of (line, module_string, is_relative).

    SyntaxWarning is suppressed: ast.parse() emits warnings for valid-but-
    legacy code (e.g., `"\\d"` literals) and we don't want analyzer stderr
    to pollute the consumer's output for projects with old regex strings.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            tree = ast.parse(source)
    except SyntaxError:
        return []
    out: list[tuple[int, str, bool]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((node.lineno, alias.name, False))
        elif isinstance(node, ast.ImportFrom):
            level = node.level or 0
            mod = node.module or ""
            module_str = ("." * level) + mod
            out.append((node.lineno, module_str, level > 0))
    return out


def resolve_python_import(
    module_str: str,
    is_relative: bool,
    source_rel: str,
    project_root: Path,
    all_files: set[str],
) -> str | None:
    """Try to resolve a Python import to an actual file in the project."""
    if is_relative:
        # Relative import: `..` strip from module_str, walk up from source dir
        leading_dots = len(module_str) - len(module_str.lstrip("."))
        rest = module_str[leading_dots:]
        src_parts = Path(source_rel).parent.parts
        # leading_dots=1 means same package (no walk-up). leading_dots=2 means parent.
        up = leading_dots - 1
        if up > len(src_parts):
            return None
        base_parts = src_parts[: len(src_parts) - up] if up > 0 else src_parts
        rest_parts = tuple(rest.split(".")) if rest else ()
        candidate_parts = tuple(p for p in base_parts + rest_parts if p)
    else:
        candidate_parts = tuple(module_str.split("."))

    # Try `<parts>.py` then `<parts>/__init__.py`
    if not candidate_parts:
        return None
    as_module = "/".join(candidate_parts) + ".py"
    as_package = "/".join(candidate_parts) + "/__init__.py"
    if as_module in all_files:
        return as_module
    if as_package in all_files:
        return as_package
    return None


# ---------------------------------------------------------------------------
# TypeScript / JavaScript import extraction (regex-based)
# ---------------------------------------------------------------------------

# Captures the path string from:
#   import X from 'path';  import {a,b} from "path";  import 'path';
#   import type X from 'path';  export {a} from 'path';  export * from 'path';
#   require('path')
#   import('path')   (only when path is a string literal)
TS_IMPORT_PATTERNS = [
    re.compile(r"""(?m)^[ \t]*import(?:\s+type)?[^'"\n]*?\s+from\s+['"]([^'"\n]+)['"]"""),
    re.compile(r"""(?m)^[ \t]*import\s+['"]([^'"\n]+)['"]"""),
    re.compile(r"""(?m)^[ \t]*export(?:\s+type)?[^'"\n]*?\s+from\s+['"]([^'"\n]+)['"]"""),
    re.compile(r"""\brequire\s*\(\s*['"]([^'"\n]+)['"]\s*\)"""),
    re.compile(r"""\bimport\s*\(\s*['"]([^'"\n]+)['"]\s*\)"""),
]


def extract_ts_imports(source: str) -> list[tuple[int, str]]:
    """Return list of (line, module_string) for TS/JS source."""
    seen: set[tuple[int, str]] = set()
    for pat in TS_IMPORT_PATTERNS:
        for m in pat.finditer(source):
            line = source[: m.start()].count("\n") + 1
            mod = m.group(1)
            seen.add((line, mod))
    return sorted(seen)


def resolve_ts_import(
    module_str: str,
    source_rel: str,
    all_files: set[str],
) -> str | None:
    """Resolve a TS/JS import to a project file. Only handles relative paths."""
    if not (module_str.startswith("./") or module_str.startswith("../")):
        return None  # External package or unresolved alias — leave for proposer to handle.
    src_dir = Path(source_rel).parent
    candidate = (src_dir / module_str).as_posix()
    # Normalize ./ and ../
    candidate = str(Path(candidate)).replace("\\", "/")
    # Try direct, then with extensions, then index.
    direct_attempts = [candidate]
    direct_attempts += [f"{candidate}{ext}" for ext in (".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs", ".cjs")]
    direct_attempts += [f"{candidate}/index{ext}" for ext in (".ts", ".tsx", ".js", ".jsx")]
    for c in direct_attempts:
        if c in all_files:
            return c
    return None


# ---------------------------------------------------------------------------
# Cycle detection (Tarjan / iterative DFS)
# ---------------------------------------------------------------------------


def count_cycles(edges: list[Edge]) -> int:
    adj: dict[str, list[str]] = {}
    for e in edges:
        adj.setdefault(e.src, []).append(e.dst)
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {}
    cycles = 0

    def dfs_iter(start: str) -> int:
        local = 0
        stack: list[tuple[str, int]] = [(start, 0)]
        path_set: set[str] = set()
        while stack:
            node, idx = stack[-1]
            if idx == 0:
                if color.get(node, WHITE) == BLACK:
                    stack.pop()
                    continue
                color[node] = GRAY
                path_set.add(node)
            children = adj.get(node, [])
            if idx < len(children):
                stack[-1] = (node, idx + 1)
                child = children[idx]
                c = color.get(child, WHITE)
                if c == GRAY:
                    local += 1
                elif c == WHITE:
                    stack.append((child, 0))
            else:
                color[node] = BLACK
                path_set.discard(node)
                stack.pop()
        return local

    for src in list(adj.keys()):
        if color.get(src, WHITE) == WHITE:
            cycles += dfs_iter(src)
    return cycles


# ---------------------------------------------------------------------------
# Main analyze
# ---------------------------------------------------------------------------


def analyze(project_root: Path, include_external: bool = False) -> dict:
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise SystemExit(f"Not a directory: {project_root}")

    source_paths = list(walk_source_files(project_root))
    all_rel: set[str] = {str(p.relative_to(project_root)).replace("\\", "/") for p in source_paths}

    files: list[FileEntry] = []
    edges: list[Edge] = []
    lang_counts: dict[str, int] = {}
    imports_total = 0
    internal_edges = 0
    external_imports = 0

    for path in source_paths:
        rel = str(path.relative_to(project_root)).replace("\\", "/")
        lang = detect_language(path) or "unknown"
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        layer = classify_layer(rel)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text = ""
        loc = text.count("\n") + (1 if text and not text.endswith("\n") else 0)

        imports: list[ImportRef] = []
        if lang == "python":
            for line, module, is_rel in extract_python_imports(text):
                resolved = resolve_python_import(module, is_rel, rel, project_root, all_rel)
                # kind:
                #   - "internal" if the import points at a project file
                #   - "relative" if it's a `.` / `..` import that didn't resolve
                #   - "external" otherwise
                if resolved:
                    kind = "internal"
                elif is_rel:
                    kind = "relative"
                else:
                    kind = "external"
                imports_total += 1
                if kind == "external":
                    external_imports += 1
                # Edges are ONLY emitted when the import resolves to a real file.
                # Never produce {dst: None} entries — schema requires a string.
                if resolved is not None:
                    edges.append(Edge(src=rel, dst=resolved, line=line))
                    internal_edges += 1
                # External imports are kept out of per-file imports list unless
                # the caller opts in via --include-external. Internal/relative
                # imports always get recorded.
                if kind == "external" and not include_external:
                    continue
                imports.append(ImportRef(line=line, module=module, kind=kind, resolves_to=resolved))
        elif lang in ("typescript", "javascript"):
            for line, module in extract_ts_imports(text):
                resolved = resolve_ts_import(module, rel, all_rel)
                is_rel = module.startswith("./") or module.startswith("../")
                if resolved:
                    kind = "internal"
                elif is_rel:
                    kind = "relative"
                else:
                    kind = "external"
                imports_total += 1
                if kind == "external":
                    external_imports += 1
                if resolved is not None:
                    edges.append(Edge(src=rel, dst=resolved, line=line))
                    internal_edges += 1
                if kind == "external" and not include_external:
                    continue
                imports.append(ImportRef(line=line, module=module, kind=kind, resolves_to=resolved))

        files.append(FileEntry(path=rel, language=lang, layer=layer, loc=loc, imports=imports))

    files.sort(key=lambda f: f.path)
    edges.sort(key=lambda e: (e.src, e.line, e.dst))

    cycles = count_cycles(edges)

    stats = Stats(
        files_total=len(files),
        files_by_language=lang_counts,
        imports_total=imports_total,
        internal_edges=internal_edges,
        external_imports=external_imports,
        cycles_detected=cycles,
    )

    anchors = collect_anchors(project_root)

    return {
        "version": ANALYZER_VERSION,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "files": [asdict(f) for f in files],
        "edges": [asdict(e) for e in edges],
        "anchors": anchors,
        "stats": asdict(stats),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="treefile-organizer analyzer (stage 1)")
    p.add_argument("project_root", help="Path to the project to analyze")
    p.add_argument("--output", "-o", help="Write JSON to this path instead of stdout")
    p.add_argument(
        "--include-external",
        action="store_true",
        help="Include external (non-project) imports in per-file imports list",
    )
    args = p.parse_args(argv)

    result = analyze(Path(args.project_root), include_external=args.include_external)
    payload = json.dumps(result, indent=2, sort_keys=False)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
