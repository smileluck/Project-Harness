<!-- last-updated: {{DATE}} -->
# aiDoc

`aiDoc/` is this repository's structured AI documentation layer (the L1 routing layer): it extracts long-lived project context out of tool directories and splits it into maintainable constraint documents by topic.

## How to Use

1. `AGENTS.md` is auto-loaded via the root `CLAUDE.md @AGENTS.md` (L0) and always in effect
2. On receiving a task, consult the "Task → Must-Read Docs" routing table below first to decide the must-read docs (L1)
3. When unsure what a document covers, look it up in the "Common Entries" dictionary (L1)
4. Open the concrete `aiDoc/` child documents the routing table points to for deep reading (L2)
5. The record layer (`memory/`, `notes/`, `plans/`) body text is not auto-loaded with the session; read or write it on demand only when the routing table hits or a record is needed

Project-level rules are never copied into tool-private directories; tools supporting `@import` use `@AGENTS.md`, the rest use thin adapter pointers (see "Tool Loading" in `AGENTS.md`).

## Ownership Map

One fact has one maintained home; other places only link.

| Information type | Sole maintained home |
|---|---|
| High-level rules and invariants every task needs | `/AGENTS.md` |
| Doc index and "task → must-read docs" routing table | `aiDoc/README.md` (this file) |
| Project positioning, tech stack, directory responsibilities | `relations/repo-profile.md`, `relations/system-map.md` |
| Component inventory, language composition, module list, entry points, command index | `relations/code-index.md` (machine-generated, never hand-edited) |
| Development process, branch and commit conventions, environment commands | `relations/development-workflow.md` |
| Architecture and module organization constraints | `modules/architecture-rules.md` |
| Steps for creating a module / feature / command | `modules/module-development.md` |
| Shared contracts, field naming, type bridging | `contracts/boundary.md` |
| Frontend development rules | `frontend/frontend-rules.md` |
| Frontend utility reuse | `frontend/frontend-utils.md` |
| Per-layer code organization standards (explanatory) | `examples/` |
| Long-term stable collaboration preferences | `memory/long-term/` |
| One record per business requirement | `memory/business/` |
| Lessons from pitfalls and recurring patterns (pending promotion) | `memory/lessons/` |
| Why a non-trivial decision was made | `notes/<proposed\|implemented\|rejected>/<class>/` |
| Execution checklist for in-progress changes | `plans/active/` |
| Reusable situational workflows | `.agents/skills/<workflow>/SKILL.md` |
| Work handoff and resuming interrupted work | handoff documents under `plans/` |

## Common Entries

| Document | Purpose |
|---|---|
| `relations/repo-profile.md` | Project positioning and tech stack quick reference |
| `relations/development-workflow.md` | Development process, commit conventions, environment commands |
| `relations/system-map.md` | System architecture and component relationships |
| `relations/code-index.md` | Component inventory, language composition, entry points, command index (machine-generated, never hand-edited) |
| `modules/architecture-rules.md` | Constraints each architecture layer must obey |
| `modules/module-development.md` | Complete steps for creating a module / feature / command |
| `contracts/boundary.md` | Shared contracts between producer and consumer |
| `frontend/frontend-rules.md` | Frontend development rules |
| `frontend/frontend-utils.md` | Frontend utility reuse list |
| `examples/README.md` | Entry to the explanatory examples |
| `memory/README.md` | Memory-layer overview and usage rules |
| `memory/long-term/README.md` | Rules for settling long-term stable preferences |
| `memory/business/README.md` | Business-requirement record rules (index solely maintained in project-memory.md) |
| `memory/project-memory.md` | Memory-layer index |
| `memory/lessons/README.md` | Capture and promotion discipline for lessons |
| `notes/README.md` | Classification and maintenance discipline for decision records |
| `plans/README.md` | Change-plan lifecycle and when a plan is needed |

## Task → Must-Read Docs

<!-- TODO: the generate workflow completes every task type for the aiDoc child docs this project actually has. Paths are relative to aiDoc/ -->

| Task type | Must-read docs |
|---|---|
| New module / feature / command | `modules/module-development.md`, `modules/architecture-rules.md`, `examples/README.md` |
| Modify existing logic | `modules/architecture-rules.md`, `relations/system-map.md` |
| New frontend page / feature | `frontend/frontend-rules.md`, `frontend/frontend-utils.md`, `examples/README.md` |
| Contract / interface alignment | `contracts/boundary.md` |
| Understand repo structure / stack / workflow | `relations/repo-profile.md`, `relations/system-map.md`, `relations/development-workflow.md` |
| Look up components / entry points / command index | `relations/code-index.md` (machine-generated, never hand-edited) |
| New business requirement from user | `memory/business/TEMPLATE.md`, `memory/project-memory.md` (index must be updated) |
| Recording a pitfall / recurring pattern | `memory/lessons/README.md`, `memory/lessons/TEMPLATE.md` (index must be updated) |
| Non-trivial decision (behavior / architecture / contract / process change) | `notes/README.md`, `notes/TEMPLATE.md` |
| Multi-step / cross-component / risky change | `plans/README.md`, `plans/change-plan.TEMPLATE.md` |
| Interrupted work or handoff | `plans/handoff.TEMPLATE.md` |
| Code review | `../.agents/skills/project-code-review/SKILL.md` |
| Pre-push checks | `../.agents/skills/project-pre-push-checks/SKILL.md` |

## Maintenance Principles

- Stable rules live here, not in tool-private directories
- Temporary session drafts are never committed
- Project-level rules go into `/AGENTS.md` first; details split into `aiDoc/`
- When an `aiDoc/` child doc is added or removed, update this file's "Common Entries" and routing table in the same change — otherwise the document is not in the system
- When facts change, update the owning document's body in place; never append a changelog at the tail
- Conflict priority: `/AGENTS.md` > this file > aiDoc child docs > tool adapter files
