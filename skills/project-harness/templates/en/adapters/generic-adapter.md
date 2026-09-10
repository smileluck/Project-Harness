---
tool: generic
role: compatibility-adapter
canonical_source: /AGENTS.md
structured_context: /aiDoc
---

# Tool Rules Adapter (Generic)

TODO(init): set `tool:` in the frontmatter and the title to the actual tool name (codex / windsurf / aider / ...), and place this file at that tool's native rules path. Create it only for tools whose rules directory actually exists in the project — never scaffold adapter files for absent tools.

This file exists only to be compatible with the tool's automatic rules loading path.

## Real Rule Entry Points

1. `/AGENTS.md`
2. `/aiDoc/README.md` (holds the "task → must-read docs" routing table — consult the table first, then deep-read)
3. The `/aiDoc/` child documents the routing table points to

## Adapter Constraints

- Never expand project-level rules in this file.
- When project-level rules change, update `/AGENTS.md` and `/aiDoc/` first; this file does not change.
- Tool directories keep only thin-adapter responsibilities.
