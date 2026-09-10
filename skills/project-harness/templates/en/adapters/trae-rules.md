---
tool: trae
role: compatibility-adapter
canonical_source: /AGENTS.md
structured_context: /aiDoc
---

# Trae Rules Adapter

This file exists only to be compatible with Trae's automatic rules loading path.

## Real Rule Entry Points

1. `/AGENTS.md`
2. `/aiDoc/README.md` (holds the "task → must-read docs" routing table — consult the table first, then deep-read)
3. The `/aiDoc/` child documents the routing table points to

## Adapter Constraints

- Never expand project-level rules in this file.
- When project-level rules change, update `/AGENTS.md` and `/aiDoc/` first; this file does not change.
- Tool directories keep only thin-adapter responsibilities.
