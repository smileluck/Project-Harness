# Tool adapters

Rule bodies live only in `AGENTS.md` and `aiDoc/`. Tool-private directories carry nothing but the tool's native loading entry and its own commands. Adapter templates ship in `templates/<lang>/adapters/` (relative to this skill directory).

## Loading matrix

| Tool | Native mechanism | What the harness writes |
|---|---|---|
| Claude Code | `CLAUDE.md` supports `@import` natively | Ensure root `CLAUDE.md` contains exactly `@AGENTS.md`. `.claude/` holds only `commands/` — **no** rule adapter file |
| Kimi Code | `AGENTS.md` auto-loaded; project skills scanned from `.agents/skills/` and `.kimi-code/skills/` | Nothing extra. Project-local workflow skills go in `.agents/skills/` |
| Codex | `AGENTS.md` native | Nothing extra |
| Trae | `.trae/rules/project_rules.md` auto-loaded | Thin adapter (only if `.trae/` exists) |
| Cursor | `.cursor/rules/` | Thin adapter (only if `.cursor/` exists) |
| GitHub Copilot | `.github/copilot-instructions.md` | Thin adapter (only if `.github/` exists) |
| Windsurf / Aider / others | tool-specific file | Thin adapter, same pattern (only if the directory exists) |

## Thin adapter pattern (tools without `@import`)

- Probe which tool directories **actually exist** in the target repo; generate adapters only for those. Never create tool directories the project does not use.
- Do **not** scan all dot-directories (e.g. `ls -d .*/`) and write an adapter into each — that manufactures redundant copies and violates the single-source rule.
- Adapter content is an entry pointer only. It must contain: the canonical rule source (`/AGENTS.md`), the structured context root (`/aiDoc`, routing via `/aiDoc/README.md`), and the constraint that no project rule bodies may be added here and that rule changes require no adapter edits.
- Suggested frontmatter:

```yaml
---
tool: <trae|cursor|copilot|windsurf|aider|...>
role: compatibility-adapter
canonical_source: /AGENTS.md
structured_context: /aiDoc
---
```

- Generate adapters from `templates/<lang>/adapters/<tool>.md`, filling only the tool name; do not expand project rules into the template.

## Adapter state registry

After generating or updating adapters, register every tool's loading method in the `AGENTS.md` tool loading table (path + mechanism). That table is the **sole index** of adapter state — when an adapter is added or removed, update the table in the same change.

## Invariants

- Rule bodies never appear in tool-private directories — no exceptions for "convenience".
- Tools with native `@import` get exactly one line (`@AGENTS.md`), nothing more.
- An adapter that has drifted to contain rule text must be cut back to the pointer pattern; move any real rules it accumulated into `AGENTS.md` or `aiDoc/` first.
- Project-level workflow skills (e.g. the two generated under `.agents/skills/`) are procedures, not rule copies — they may reference rules but must not restate them.
