<!-- last-updated: {{DATE}} -->
# aiDoc

## Look Up by Change Scope

Start with `AGENTS.md` and the code involved in the task. Use the matching rows below when locating code, confirming a constraint, or recording a change. In long files, find the relevant passage by heading, path, or symbol. Consult additional constraints as the scope expands.

| Change scope | Open when needed |
|---|---|
| Local fix / copy change / internal refactor | Start with the relevant code and nearest tests. Use the rows below when the change touches those constraints |
| New module, layer change, or dependency change | Relevant layer or component in `modules/architecture-rules.md`; use `modules/module-development.md` for integration steps |
| New frontend page or feature | Relevant rules in `frontend/frontend-rules.md`; use `frontend/frontend-utils.md` when reusing utilities |
| Example for one layer | Find the example for that layer via `examples/README.md` |
| API, public type, CLI, or cross-component behavior change | Find the affected contract via `contracts/boundary.md` and trace its producer and consumer. Repeat for each affected boundary |
| Locate an entry point, component, or command | Search `relations/code-index.md`; use `relations/system-map.md` for component relationships |
| Project purpose / tech stack | `relations/repo-profile.md` |
| Build / deploy / commit | Relevant section of `relations/development-workflow.md` |
| Record a business requirement or lesson | See `memory/business/README.md` for requirements or `memory/lessons/README.md` for lessons. Search the memory index by topic and update the matching section |
| Non-trivial decision / complex change / handoff | Open `notes/README.md`, `plans/README.md`, or `plans/handoff.TEMPLATE.md` as applicable |
| Code review | `../.agents/skills/project-code-review/SKILL.md` |
| Pre-push checks | `../.agents/skills/project-pre-push-checks/SKILL.md` |

## Common Entries

| Document | Purpose |
|---|---|
| `relations/repo-profile.md` | Project positioning and tech stack quick reference |
| `relations/development-workflow.md` | Development process, commit conventions, environment commands |
| `relations/system-map.md` | System architecture and component relationships |
| `relations/code-index.md` | Component inventory, language composition, entry points, command index (machine-generated, never hand-edited) |
| `modules/architecture-rules.md` | Constraints each architecture layer must obey |
| `modules/module-development.md` | Complete steps for creating a module / feature / command |
| `contracts/boundary.md` | Shared conventions and entry point for contract surfaces |
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

## Maintenance Principles

- Maintain routes by code entry point, component, or contract surface. Register top-level entries here, contract pages in `contracts/boundary.md`, and records in the index owned by their area.
- Update the owning index when adding, removing, or moving a document. Update facts in the document that owns them.
