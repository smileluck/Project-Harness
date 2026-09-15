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
| `init [--no-generate]` | Non-destructive skeleton bootstrap of a new or lightly documented repo (AGENTS.md, CLAUDE.md, aiDoc/ tree, `.agents/skills/` helpers — tool adapters are written later by the generate workflow, not by the script). Runs `scripts/init_project.py`, then continues into the `generate` workflow by default; `--no-generate` stops at the skeleton. Script-level flags (`--dry-run`/`--overwrite`/`--no-scan`/`--lang`) are documented by the script's `--help`. | [references/init-harness.md](references/init-harness.md) |
| `generate [--incremental \| --scope <area> \| --dry-run] [--lang auto\|zh\|en]` | Probe the codebase and generate/update `AGENTS.md` + the `aiDoc/` documentation system. | [references/generate-aidoc.md](references/generate-aidoc.md) |
| `sync` | Detect documentation drift (mechanical checks via `scripts/check_sync.py`, then agent-driven semantic drift handling) and resync incrementally. | [references/sync-aidoc.md](references/sync-aidoc.md) |
| `record [note \| plan \| handoff \| lesson]` | Create a decision note, change plan, handoff, or lesson record under the correct lifecycle/class discipline. | [references/change-docs.md](references/change-docs.md) |
| `update` | Refresh a repo's harness-managed files to the current template version after a toolkit upgrade (mechanical refresh via `scripts/update_harness.py`, then semantic merge for project-modified files). | [references/update-harness.md](references/update-harness.md) |

Supporting references, loaded on demand:

- [references/harness-model.md](references/harness-model.md) — the five-layer model, ownership map, toolkit boundaries
- [references/aidoc-structure.md](references/aidoc-structure.md) — the aiDoc/ directory contract (single source for per-file content requirements)
- [references/tool-adapters.md](references/tool-adapters.md) — how each agent tool loads project rules
- [references/collaboration.md](references/collaboration.md) — multi-agent / multi-person coordination
- [references/quality-workflow.md](references/quality-workflow.md) — review, verification, and evidence discipline

No arguments: print a usage summary of the table above plus the script locations below, and ask which action to run. Unknown action: print the same summary and stop.

Flags inside the Action column are workflow-level (parsed by the agent, e.g. `--no-generate`, generate's `--dry-run`); flags like init's `--dry-run` belong to `init_project.py` and are listed by its `--help` — do not mix the two namespaces when invoking scripts.

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

- `scripts/init_project.py` — skeleton bootstrap; writes the `aiDoc/.harness-manifest.json` baseline
- `scripts/update_harness.py` — mechanical refresh of harness-managed files to the current template version
- `scripts/check_sync.py` — mechanical drift checks between docs and code
- `templates/<lang>/` — document skeletons, including `templates/<lang>/adapters/` for tool adapters and `templates/<lang>/aidoc/` for notes/plans templates

Resolve the skill directory from this file's location — references use the `<skill-dir>` placeholder for it (in Kimi Code, `${KIMI_SKILL_DIR}` holds this path). Example: `python3 <skill-dir>/scripts/init_project.py <repo-root> --dry-run`. Each script prints its full parameter surface with `--help`.
