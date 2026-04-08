---
name: file-organization
description: Use when helping organize files, clean up directories, or establish file naming and structure conventions — covers 18 manifest types, intelligent file categorization, naming conventions, and organizational patterns with audit trails
allowed-tools: Read Glob Bash(ls *) Bash(find *) Bash(mv *) Bash(mkdir *)
---

# File Organization

## When to Use
When organizing files into a coherent structure, cleaning up messy directories, establishing naming conventions, setting up project folder hierarchies, categorizing files by type or purpose, identifying duplicate or orphaned files, or helping someone establish a sustainable file organization system. Useful at project start (establish structure), mid-project (when things get messy), and project end (archive and clean up).

## 18 Project Manifest Types

These manifest files identify a project's root directory and its technology stack. Use them to auto-discover projects within a directory tree.

| Manifest File | Project Type | Ecosystem |
|--------------|-------------|-----------|
| `package.json` | node | JavaScript / TypeScript / Node.js |
| `pyproject.toml` | python | Modern Python (Poetry, Hatch, PDM) |
| `setup.py` | python | Legacy Python (setuptools) |
| `Cargo.toml` | rust | Rust (Cargo) |
| `go.mod` | go | Go modules |
| `pom.xml` | java-maven | Java (Maven) |
| `build.gradle` | java-gradle | Java / Android (Gradle) |
| `build.gradle.kts` | kotlin-gradle | Kotlin (Gradle KTS) |
| `Gemfile` | ruby | Ruby (Bundler) |
| `composer.json` | php | PHP (Composer) |
| `pubspec.yaml` | dart-flutter | Dart / Flutter |
| `platformio.ini` | embedded-pio | Embedded / ESP32 / Arduino |
| `CMakeLists.txt` | cpp-cmake | C++ (CMake) |
| `Makefile` | make | Make-based builds |
| `mix.exs` | elixir | Elixir (Mix) |
| `shard.yml` | crystal | Crystal |
| `deno.json` | deno | Deno |
| `bun.lockb` | bun | Bun runtime |

**Usage**: Scan a directory tree looking for these files. When found, the parent directory is a project root. Stop descending into that project's subdirectories to avoid false matches in nested dependencies.

**Skip directories during scanning**: `node_modules`, `__pycache__`, `target`, `build`, `dist`, `.git`, `venv`, `.venv`, `env`, `.tox` (these are build artifacts or dependency caches, never project roots).

## Canonical Client Folder Structure

For client/project-based work, use this four-folder structure per client:

```
clients/
  {client-name}/
    projects/           # Source code, build files, project assets
    contracts/          # Legal documents, SOWs, NDAs, agreements
    deliverables/       # Final outputs, reports, presentations, exports
    communications/     # Emails, meeting notes, chat logs, correspondence
```

This structure cleanly separates concerns and makes files findable by purpose rather than just date or type.

## Intelligent File Categorization

### Heuristic Classification Rules

When determining where a file belongs, apply these rules in order (first match wins):

**Contracts** (high confidence: 0.7)
```
Keywords in filename: contract, agreement, nda, sow, terms, legal, msa
File types: .docx, .doc (when combined with contract keywords)
```

**Communications** (high confidence: 0.7)
```
Keywords in filename: email, meeting, notes, chat, message, correspondence, minutes
```

**Deliverables** (medium confidence: 0.6)
```
Keywords in filename: report, presentation, deliverable, final, export, invoice
File types: .pdf, .pptx, .ppt, .xlsx, .xls, .csv
```

**Projects** (default, low confidence: 0.4)
```
Everything else — source code, config files, assets, documentation
This is the fallback when no other pattern matches
```

### LLM-Assisted Categorization

When heuristic rules produce low confidence (below 0.5) or the file is ambiguous, use Claude to analyze the file's name, extension, path context, and (if small enough) content to suggest placement.

**Prompt pattern for ambiguous files**:
```
For each file below, suggest which canonical folder it belongs in.
The folders are:
- projects/ (source code, build files, project assets)
- contracts/ (legal documents, SOWs, NDAs, agreements)
- deliverables/ (final outputs, reports, presentations, exports)
- communications/ (emails, meeting notes, chat logs, correspondence)

Files:
- path/to/ambiguous-file.ext
- path/to/another-file.ext

For each file provide: suggested_folder, reason, confidence (0.0-1.0)
```

## Naming Conventions

### File Naming Rules

**General principles**:
- Lowercase with hyphens: `project-proposal.md` not `Project Proposal.md`
- No spaces in filenames (use hyphens or underscores)
- Be descriptive: `2024-q2-revenue-report.pdf` not `report-final-v3.pdf`
- Include version only if multiple versions coexist; prefer a single source of truth

**Date-prefixed files** (use for time-series content):
```
YYYY-MM-DD-description.ext
2024-06-01-client-meeting-notes.md
2024-05-weekly-status-report.pdf
```

**When to date-prefix**:
- Communication logs and meeting notes
- Reports and deliverables with temporal relevance
- Invoices and financial documents
- Anything where chronological sorting matters

**When NOT to date-prefix**:
- Source code files
- Configuration files
- Templates and reusable documents
- READMEs and documentation

### Directory Naming

- Lowercase with hyphens: `meeting-notes/` not `Meeting Notes/`
- Singular nouns for categories: `contract/` or `contracts/` (pick one convention and stick with it)
- No abbreviations unless universally understood: `docs/` is fine, `comms/` should be `communications/`

## Directory Structure Patterns

### Pattern 1: By Project (Best for client work)
```
workspace/
  client-alpha/
    projects/
    contracts/
    deliverables/
    communications/
  client-beta/
    projects/
    contracts/
    deliverables/
    communications/
```

### Pattern 2: By Type (Best for personal files)
```
documents/
  contracts/
  invoices/
  reports/
  notes/
code/
  project-one/
  project-two/
media/
  images/
  videos/
  audio/
```

### Pattern 3: By Date (Best for archives, logs)
```
archive/
  2024/
    q1/
    q2/
    q3/
    q4/
  2023/
    ...
```

### Pattern 4: Hybrid (Recommended for most workflows)
```
workspace/
  active/                    # Current projects (by client or project)
    client-alpha/
    personal-site/
  archive/                   # Completed work (by year)
    2024/
    2023/
  templates/                 # Reusable templates
  reference/                 # Reference material, docs, guides
```

## Audit Trail

Every file move or organization action should be logged. This creates an undo-able history and helps track what changed.

### Audit Entry Format

```yaml
id: mv_a1b2c3d4e5f6
action: move                 # move | create_structure | discover | suggest
src: /old/path/to/file.pdf
dst: /new/path/to/file.pdf
client_id: acme-corp         # or "__manual__" for ad-hoc moves
timestamp: 2024-06-01T14:30:00Z
metadata:
  size_bytes: 245760
  reason: "Matched contract keywords, moved to contracts/"
```

### Audit Actions

| Action | Description |
|--------|------------|
| `move` | File relocated from src to dst |
| `create_structure` | Directory structure created (e.g., client folders) |
| `discover` | Project auto-discovery scan completed |
| `suggest` | LLM or heuristic classification generated |

### Audit Log Storage

Store as an append-only file (JSONL format, one JSON object per line):

```
audit-log.jsonl
```

Each line is a self-contained JSON record. Easy to grep, parse, and review. Never edit existing entries -- only append new ones.

### Safe File Moves

When moving files:
1. Verify source exists and is a file (not a directory)
2. Resolve to absolute paths (avoid relative path confusion)
3. Check destination does not already exist (refuse to overwrite)
4. Create parent directories as needed
5. Perform the move
6. Log the audit entry with source, destination, and timestamp
7. Verify the destination file exists after the move

## Cleanup Patterns

### Identifying Duplicates

**By filename**: Find files with identical names in different locations
```
Look for: same filename + same size = likely duplicate
Verify with: content hash (SHA-256) for certainty
```

**By content hash**: Compute hash of file contents, group by hash
```
Same hash = identical content regardless of filename
```

**Action**: Keep the copy in the canonical location, remove others (or move to a `duplicates/` staging directory for review).

### Identifying Orphaned Files

Orphaned files are those that:
- Live outside any project or client directory
- Have no clear categorization
- Were created as temporary files and never cleaned up
- Are old versions superseded by newer files

**Common orphan patterns**:
```
*.tmp, *.bak, *.old, *.swp       # Temporary/backup files
*-copy.*, *-Copy.*, * (1).*      # Accidental duplicates
~$*                                # Office temp files
.DS_Store, Thumbs.db, desktop.ini # OS metadata
```

### Identifying Outdated Versions

Look for patterns like:
```
report-v1.pdf
report-v2.pdf
report-v3.pdf          # Only this one matters
report-final.pdf       # Or this one
report-final-final.pdf # The naming tells you there's a problem
```

**Fix**: Keep only the latest version in the working directory. Move older versions to `archive/` with date prefix.

## Organization Workflows

### Project Start: Establish Structure
```
1. Decide on structure pattern (by-project, by-type, hybrid)
2. Create top-level directories
3. For client work: create per-client folder structure
4. Create README.md documenting the conventions
5. Set up audit log file
6. Move any existing loose files into the structure
7. Log all moves in the audit trail
```

### Mid-Project: Clean Up the Mess
```
1. Scan for project roots using the 18 manifest types
2. Identify files outside any project directory (orphans)
3. Run heuristic classification on orphaned files
4. For low-confidence files, use LLM-assisted categorization
5. Review suggested moves before executing
6. Execute moves with audit trail
7. Scan for duplicates and remove/archive
8. Remove OS metadata files (.DS_Store, Thumbs.db)
9. Update README if conventions changed
```

### Project End: Archive
```
1. Verify all deliverables are in deliverables/
2. Verify all contracts are in contracts/
3. Move project directory to archive/{year}/
4. Create a project summary file (what was done, key dates, outcome)
5. Remove build artifacts and temporary files:
   - node_modules/, __pycache__/, target/, build/, dist/
   - .env files (never archive secrets)
   - IDE-specific files (.idea/, .vscode/ settings)
6. Compress the archive directory if space is a concern
7. Log the archive action in the audit trail
```

## Project Discovery

### Auto-Discovering Projects in a Directory

Scan a directory tree (up to 5 levels deep by default) looking for the 18 manifest files. For each found:

**Collected information**:
```yaml
path: /Users/me/code/my-app
name: my-app                    # Directory name
project_type: node              # From manifest lookup
manifest_file: package.json     # Which manifest was found
size_bytes: 15728640            # Total size of all files
file_count: 342                 # Number of files in project
```

**Why this matters**: Before organizing, you must know what projects exist and where they live. Discovery prevents accidentally breaking a project by moving its files.

## Common Pitfalls

### Organizing Without a Plan
- **Symptom**: Moving files around randomly, no consistent structure
- **Impact**: Files become harder to find, not easier
- **Fix**: Choose a structure pattern first, document it in a README, then organize

### No Audit Trail
- **Symptom**: "Where did that file go?" / "I moved it somewhere..."
- **Impact**: Lost files, no ability to undo, others can't find things
- **Fix**: Log every move. An append-only JSONL file takes seconds to write

### Overorganizing
- **Symptom**: 10 levels of nested directories with 1 file each
- **Impact**: More time navigating than working, path names become unwieldy
- **Fix**: Max 3-4 levels deep. If a directory has fewer than 3 files, it probably doesn't need to exist

### Ignoring Build Artifacts
- **Symptom**: `node_modules/` and `__pycache__/` mixed in with project files
- **Impact**: Bloated directories, slow searches, confusing file counts
- **Fix**: Never organize into build artifact directories. Exclude them from scans

### Not Archiving Completed Work
- **Symptom**: Active workspace has 50+ directories, most for completed projects
- **Impact**: Hard to find current work, overwhelming directory listings
- **Fix**: Move completed projects to `archive/{year}/` within 2 weeks of completion

### Spaces and Special Characters in Filenames
- **Symptom**: `My Final Report (v3) - Copy.pdf`
- **Impact**: Shell commands break, scripts fail, URLs get mangled
- **Fix**: Lowercase, hyphens, no spaces: `2024-06-final-report.pdf`

## Checklists

### Initial Organization Setup
- [ ] Choose structure pattern (by-project, by-type, or hybrid)
- [ ] Create top-level directories
- [ ] Create per-client folder structure (if client work)
- [ ] Write README.md with naming conventions and structure rules
- [ ] Set up audit log (audit-log.jsonl)
- [ ] Run project discovery scan (18 manifest types)
- [ ] Categorize and move loose files
- [ ] Remove OS metadata files (.DS_Store, Thumbs.db)

### Weekly Maintenance
- [ ] Check for files in root/inbox that need categorizing
- [ ] Move any new deliverables to proper client directories
- [ ] Log communications to the right locations
- [ ] Check for duplicate files (same name, different locations)
- [ ] Remove temporary files (*.tmp, *.bak, ~$*)

### Monthly Cleanup
- [ ] Run full project discovery scan (any new projects?)
- [ ] Identify orphaned files (outside any project)
- [ ] Review and move or delete orphans
- [ ] Archive completed projects (move to archive/{year}/)
- [ ] Check directory depth (any > 4 levels deep?)
- [ ] Verify naming conventions are being followed
- [ ] Review audit log for patterns (recurring disorganization?)

### Project Archival
- [ ] All deliverables confirmed in deliverables/
- [ ] All contracts confirmed in contracts/
- [ ] Build artifacts removed (node_modules, __pycache__, dist, etc.)
- [ ] Environment files removed (.env, secrets)
- [ ] IDE-specific files removed (.idea, .vscode settings)
- [ ] Project summary written (scope, dates, outcome)
- [ ] Moved to archive/{year}/{project-name}/
- [ ] Audit entry logged
- [ ] Verified archive is complete (spot check key files)

### Emergency "Desk is on Fire" Triage
- [ ] Create inbox/ directory for unsorted files
- [ ] Move everything loose into inbox/
- [ ] Sort inbox/ by file type (extension) into rough buckets
- [ ] Apply heuristic classification to each bucket
- [ ] Move high-confidence matches to canonical locations
- [ ] Flag low-confidence files for manual review
- [ ] Log all moves in audit trail
- [ ] Schedule time for proper organization (this was triage, not a solution)
