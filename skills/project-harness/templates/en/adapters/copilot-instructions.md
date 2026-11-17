---
tool: copilot
role: compatibility-adapter
canonical_source: /AGENTS.md
structured_context: /aiDoc
---

# Copilot Instructions Adapter

This file exists only to be compatible with GitHub Copilot's automatic instructions loading path.

## Real Rule Entry Points

1. `/AGENTS.md`
2. `/aiDoc/README.md` (look up guidance by change scope)
3. The affected `/aiDoc/` pages or sections

## Adapter Constraints

- Never expand project-level rules in this file.
- When project-level rules change, update `/AGENTS.md` and `/aiDoc/` first; this file does not change.
- Tool directories keep only thin-adapter responsibilities.
