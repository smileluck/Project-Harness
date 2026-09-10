<!-- last-updated: {{DATE}} -->
# aiDoc

`aiDoc/` is the structured AI documentation layer of this repository. It extracts long-lived project context out of tool-private directories and splits it into maintainable constraint documents by topic.

## How to Use

1. `AGENTS.md` is auto-loaded via the root `CLAUDE.md` (L0) and always in effect.
2. On receiving a task, consult the "Task → Must-Read Docs" routing table below first (L1).
3. When unsure what a document covers, look it up in the "Common Entries" dictionary (L1).
4. Open the concrete `aiDoc/` child documents the routing table points to for deep reading (L2).

Project-level rules are never copied into tool-private directories; Claude Code uses `@import`, other tools use thin adapter pointers (see "Tool Loading" in `../AGENTS.md`).

## Directory Guide

- `relations/` — repo structure, tech stack, dependencies, development workflow
- `modules/` — architecture rules, module development guide
- `contracts/` — contract layer: interface contract and responsibility split
- `frontend/` — frontend rules, utility reuse rules (generated only when a frontend exists)
- `examples/` — explanatory examples for each layer
- `memory/` — AI memory layer (long-term preferences, business requirement records)
- `notes/` — decision records (proposed / implemented / rejected)
- `plans/` — change plans and handoffs (active / completed)

## Ownership Map

One fact has one maintained home; other places only link.

| Information type | Maintained home |
|---|---|
| Rules needed in every task | `../AGENTS.md` |
| Doc index and task routing | this file |
| Repo structure, tech stack, workflow | `relations/` |
| Architecture and module rules | `modules/` |
| Contract layer | `contracts/` |
| Frontend rules | `frontend/` |
| Per-layer explanatory examples | `examples/` |
| Stable user preferences, business requirement records | `memory/` |
| Why a non-trivial decision won | `notes/<lifecycle>/<class>/` |
| Current execution checklist for a change | `plans/active/` |
| Reusable situational procedure | `../.agents/skills/<workflow>/SKILL.md` |

Never duplicate the same rule across tiers; put a short link at the point of use.

## Common Entries

TODO: one line per document — path + one-sentence purpose. This is the "look up by document" index. Keep it complete; an unlisted document is effectively not in the system.

| Document | Purpose |
|---|---|
| `relations/repo-profile.md` | Project positioning and tech stack |
| `relations/development-workflow.md` | Development order, branches, commits, commands |
| `relations/system-map.md` | Architecture and component relationships |
| `modules/architecture-rules.md` | Architecture and per-layer constraints |
| `modules/module-development.md` | Step-by-step module creation guide |
| `contracts/boundary.md` | Contract layer: interface contract and responsibility split |
| `frontend/frontend-rules.md` | Frontend development rules |
| `frontend/frontend-utils.md` | Utility reuse rules |
| `examples/README.md` | How to use the example layer |
| `memory/project-memory.md` | Memory index |
| `notes/README.md` | Decision-record lifecycle and naming rules |
| `plans/README.md` | Change-plan lifecycle rules |

TODO: adjust to the documents that actually exist in this project.

## Task → Must-Read Docs

Paths are relative to `aiDoc/`. TODO: complete for every task type that exists in this project.

| Task type | Must-read docs |
|---|---|
| New module / feature / command | `modules/module-development.md`, `modules/architecture-rules.md`, `examples/` |
| New frontend page / feature | `frontend/frontend-rules.md`, `frontend/frontend-utils.md`, `examples/` (frontend examples) |
| Contract / field alignment | `contracts/boundary.md` |
| Understand repo structure / stack / workflow | `relations/repo-profile.md`, `relations/system-map.md`, `relations/development-workflow.md` |
| New business requirement from user | `memory/business/TEMPLATE.md`, `memory/project-memory.md` (index must be updated) |
| Multi-step / cross-component change | `plans/README.md`, `plans/change-plan.TEMPLATE.md` |
| Recording a non-trivial decision | `notes/README.md`, `notes/TEMPLATE.md` |
| Code review | `../.agents/skills/project-code-review/SKILL.md` |
| Pre-push verification | `../.agents/skills/project-pre-push-checks/SKILL.md` |

## Maintenance Principles

- Stable rules live here, not in tool-private directories.
- Temporary session drafts are never committed.
- Project-level rules go into `../AGENTS.md` first; details split into `aiDoc/`.
- When a child doc is added or removed, update "Common Entries" and the routing table in the same change — otherwise the document is not in the system.
- Keep the ownership map honest: when a fact moves to a new home, update every link to it.
