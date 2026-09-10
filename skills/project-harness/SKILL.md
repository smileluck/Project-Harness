---
name: project-harness
description: Initialize or improve a repository's agent collaboration harness — layered AGENTS.md + aiDoc/ documentation system, decision records, change plans, drift detection. Use for making a project agent-ready, generating/updating aiDoc docs, checking doc drift, or recording decisions/plans/handoffs.
whenToUse: When the user wants to onboard a project to agent-assisted development, generate or update AGENTS.md/aiDoc documentation, check documentation drift, or create decision notes, change plans, handoffs
arguments:
  - action
---

# Project Harness

Make any repository agent-ready: a layered `AGENTS.md` + `aiDoc/` documentation system, decision records, change plans, handoffs, and drift detection — adapted to the target project, never copied from another project's specifics.

## Route the action

Parse `$ARGUMENTS` (or `$action`) and dispatch:

| Action | Purpose | Read first |
|---|---|---|
| `init` | Non-destructive skeleton bootstrap of a new or lightly documented repo (AGENTS.md, aiDoc/ tree, tool adapters). Runs `scripts/init_project.py`. | [references/init-harness.md](references/init-harness.md) |
| `generate [--incremental \| --scope <area> \| --dry-run] [--lang zh\|en]` | Probe the codebase and generate/update `AGENTS.md` + the `aiDoc/` documentation system. | [references/generate-aidoc.md](references/generate-aidoc.md) |
| `sync` | Detect documentation drift (mechanical checks via `scripts/check_sync.py`, then agent-driven semantic drift handling) and resync incrementally. | [references/sync-aidoc.md](references/sync-aidoc.md) |
| `record [note \| plan \| handoff]` | Create a decision note, change plan, or handoff under the correct lifecycle/class discipline. | [references/change-docs.md](references/change-docs.md) |

Supporting references, loaded on demand:

- [references/harness-model.md](references/harness-model.md) — the five-layer model, ownership map, toolkit boundaries
- [references/aidoc-structure.md](references/aidoc-structure.md) — the aiDoc/ directory contract (single source for per-file content requirements)
- [references/tool-adapters.md](references/tool-adapters.md) — how each agent tool loads project rules
- [references/collaboration.md](references/collaboration.md) — multi-agent / multi-person coordination
- [references/quality-workflow.md](references/quality-workflow.md) — review, verification, and evidence discipline

No arguments: print a usage summary of the table above plus the script locations below, and ask which action to run. Unknown action: print the same summary and stop.

## Operating invariants

- One fact has one maintained home; every other document links to it.
- Standing rules live in `AGENTS.md`; current-state facts live in `aiDoc/`; decision rationale lives in `aiDoc/notes/`; execution state lives in `aiDoc/plans/active/`; reusable procedures live in skills.
- Conflict priority inside the target repo: `AGENTS.md` > `aiDoc/README.md` > aiDoc sub-documents > tool adapter files.
- Rule bodies never live in tool-private directories (`.claude/`, `.cursor/`, …); adapters carry entry pointers only.
- Initialization never overwrites existing files by default; `--overwrite` requires explicit user approval.
- Evidence must be proportional to the affected surface; never claim checks that were not run.
- Document content must come from real code probing — never invent stack, paths, or symbols.

## Scripts and templates

Scripts and templates ship inside this skill directory, next to this `SKILL.md`:

- `scripts/init_project.py` — skeleton bootstrap (supports `--dry-run`, `--overwrite`)
- `scripts/check_sync.py` — mechanical drift checks between docs and code
- `templates/<lang>/` — document skeletons, including `templates/<lang>/adapters/` for tool adapters and `templates/<lang>/aidoc/` for notes/plans templates

Resolve the skill directory via `${KIMI_SKILL_DIR}` when available, otherwise via the skill's install path. Example: `python3 ${KIMI_SKILL_DIR}/scripts/init_project.py <repo-root> --dry-run`.
