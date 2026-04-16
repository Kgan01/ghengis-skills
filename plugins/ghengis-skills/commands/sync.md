# Sync project documentation to current state

Invoke the `ghengis-skills:auto-project-sync` skill to update CLAUDE.md, MEMORY.md, project indexes, and documentation to reflect the current state of the codebase.

This is the manual override for the auto-sync system. Run this when:
- You just finished a major feature/plan and want docs current
- You want to verify project state matches reality before starting new work
- The auto-trigger didn't fire and you want to force it

The skill will:
1. Detect changes since last sync (commits, new files)
2. Update CLAUDE.md with current phase/decisions
3. Update MEMORY.md with new lessons learned
4. Regenerate spec/plan indexes
5. Capture sync timestamp in `.claude/last_sync`

If nothing has changed since last sync, the skill will exit quickly with no changes.
