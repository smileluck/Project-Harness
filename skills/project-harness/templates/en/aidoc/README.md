<!-- last-updated: {{DATE}} -->
# aiDoc

`aiDoc/` is the structured AI documentation layer of this repository. It extracts long-lived project context out of tool-private directories and splits it into maintainable constraint documents by topic.

## How to Use

1. `AGENTS.md` is auto-loaded via the root `CLAUDE.md` (L0) and always in effect.
2. On receiving a task, consult the "Task → Must-Read Docs" routing table below first (L1).
3. When unsure what a document covers, look it up in the "Common Entries" dictionary (L1).
4. Open the concrete `aiDoc/` child documents the routing table points to for deep reading (L2).

Project-level rules are never copied into tool-private directories; Claude Code uses `@import`, other tools use thin adapter pointers (see "Tool Loading" in `../AGENTS.md`).

## Ownership Map

One fact has one maintained home; other places only link.

| Information type | Maintained home |
|---|---|
| Rules needed in every task | `../AGENTS.md` |
| Doc index and task routing | this file |
| Repo structure, tech stack, workflow | `relations/` (incl. machine-generated `code-index.md`, never hand-edited) |
| Architecture and module rules | `modules/` |
| Contract layer | `contracts/` |
| Frontend rules | `frontend/` |
| Per-layer explanatory examples | `examples/` |
| Stable user preferences, business requirement records | `memory/` |
| Pitfalls and recurring patterns pending promotion | `memory/lessons/` |
| Why a non-trivial decision won | `notes/<lifecycle>/<class>/` |
| Current execution checklist for a change | `plans/active/` |
| Reusable situational procedure | `../.agents/skills/<workflow>/SKILL.md` |

Never duplicate the same rule across tiers; put a short link at the point of use.

## Common Entries

| Document | Purpose |
|---|---|
| `relations/repo-profile.md` | Project positioning and tech stack |
| `relations/development-workflow.md` | Development order, branches, commits, commands |
| `relations/system-map.md` | Architecture and component relationships |
| `relations/code-index.md` | Component inventory, language composition, entry points, command index (machine-generated, never hand-edited) |
| `modules/architecture-rules.md` | Architecture and per-layer constraints |
| `modules/module-development.md` | Step-by-step module creation guide |
| `contracts/boundary.md` | Contract layer: interface contract and responsibility split |
| `frontend/frontend-rules.md` | Frontend development rules |
| `frontend/frontend-utils.md` | Utility reuse rules |
| `examples/README.md` | How to use the example layer |
| `memory/README.md` | Memory-layer overview and usage rules |
| `memory/long-term/README.md` | Rules for stable long-term preferences |
| `memory/business/README.md` | Business-requirement record rules (index solely in project-memory.md) |
| `memory/project-memory.md` | Memory index |
| `memory/lessons/README.md` | Lesson capture and promotion discipline |
| `notes/README.md` | Decision-record lifecycle and naming rules |
| `plans/README.md` | Change-plan lifecycle rules |

## Task → Must-Read Docs

Paths are relative to `aiDoc/`. TODO: complete for every task type that exists in this project.

| Task type | Must-read docs |
|---|---|
| New module / feature / command | `modules/module-development.md`, `modules/architecture-rules.md`, `examples/` |
| New frontend page / feature | `frontend/frontend-rules.md`, `frontend/frontend-utils.md`, `examples/` (frontend examples) |
| Contract / field alignment | `contracts/boundary.md` |
| Understand repo structure / stack / workflow | `relations/repo-profile.md`, `relations/system-map.md`, `relations/development-workflow.md` |
| Look up components / entry points / command index | `relations/code-index.md` (machine-generated, never hand-edited) |
| New business requirement from user | `memory/business/TEMPLATE.md`, `memory/project-memory.md` (index must be updated) |
| Recording a pitfall / recurring pattern | `memory/lessons/README.md`, `memory/lessons/TEMPLATE.md` (index must be updated) |
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
